from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import logging
from pathlib import Path
import sys
import os
from typing import Dict, Any, List, Optional

# Ensure the root directory is on the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import backend modules
from backend.models.schemas import FilterRequest, FilterResponse, ErrorResponse, FileUploadResponse
from backend.services.csv_service import CSVService
from backend.services.ai_service import AIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LinkReach",
    description="AI-powered LinkedIn connections filtering tool",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for uploaded data (in production, use Redis or database)
_uploaded_data: Dict[str, Any] = {}

def get_csv_service() -> CSVService:
    """Dependency injection for CSV service"""
    return CSVService()

def get_ai_service() -> AIService:
    """Dependency injection for AI service"""
    return AIService()

@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    csv_service: CSVService = Depends(get_csv_service)
):
    """Upload and validate CSV file"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        file_content = await file.read()
        is_valid, error_message, df = csv_service.validate_csv(file_content)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Store the dataframe (in production, use proper storage)
        file_id = f"file_{len(_uploaded_data) + 1}"
        _uploaded_data[file_id] = {
            'df': df,
            'filename': file.filename
        }
        
        preview_data = csv_service.get_preview_data(df)
        
        return FileUploadResponse(
            success=True,
            message=f"Successfully uploaded {file.filename}",
            total_rows=len(df),
            columns=df.columns.tolist(),
            preview_data=preview_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/filter", response_model=FilterResponse)
async def filter_connections(
    request: FilterRequest,
    csv_service: CSVService = Depends(get_csv_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """Filter connections using AI-generated code"""
    try:
        # Get the uploaded dataframe (in production, use proper storage)
        if not _uploaded_data:
            raise HTTPException(status_code=400, detail="No CSV file uploaded. Please upload a file first.")
        
        # Use the first uploaded file
        file_data = list(_uploaded_data.values())[0]
        df = file_data['df']
        
        # Generate sample data for AI
        sample_df = df.head(5).to_string(index=False)
        
        # Generate filter code using AI
        filter_code = ai_service.generate_filter_code(request.prompt, sample_df)
        
        # Validate the generated code
        if not ai_service.validate_filter_code(filter_code):
            raise HTTPException(status_code=500, detail="Generated filter code is invalid")
        
        # Execute the filter code
        local_vars = {'df': df.copy()}
        exec(filter_code, {}, local_vars)
        filtered_df = local_vars['df']
        
        # Save filtered results
        download_path = csv_service.save_filtered_results(filtered_df)
        
        # Get preview of filtered results
        preview_data = csv_service.get_preview_data(filtered_df)
        
        return FilterResponse(
            success=True,
            message=f"Successfully filtered {len(filtered_df)} connections from {len(df)} total",
            filtered_count=len(filtered_df),
            total_count=len(df),
            preview_data=preview_data,
            download_url=f"/api/download/{download_path.split('/')[-1]}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filtering connections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error filtering connections: {str(e)}")

@app.get("/api/download/{filename}")
async def download_results(filename: str):
    """Download filtered results"""
    try:
        csv_service = CSVService()
        file_path = csv_service.temp_dir / filename
        
        logger.info(f"Looking for file: {file_path}")
        logger.info(f"File exists: {file_path.exists()}")
        logger.info(f"Temp dir contents: {list(csv_service.temp_dir.glob('*'))}")
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='text/csv'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading file")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "LinkedIn Connections Filter API is running"}

# Serve static files from frontend
frontend_path = Path("frontend/static")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Serve frontend HTML
@app.get("/")
async def serve_frontend():
    """Serve the main frontend page"""
    try:
        return FileResponse("frontend/templates/index.html")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend not found")

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "message": "The requested resource was not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "Something went wrong"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 