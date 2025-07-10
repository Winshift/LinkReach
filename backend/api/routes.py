from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
import pandas as pd
from typing import Dict, Any
import logging

from backend.models.schemas import FilterRequest, FilterResponse, ErrorResponse, FileUploadResponse
from backend.services.csv_service import CSVService
from backend.services.ai_service import AIService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global storage for uploaded data (in production, use Redis or database)
_uploaded_data: Dict[str, Any] = {}

def get_csv_service() -> CSVService:
    """Dependency injection for CSV service"""
    return CSVService()

def get_ai_service() -> AIService:
    """Dependency injection for AI service"""
    return AIService()

@router.post("/upload", response_model=FileUploadResponse)
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

@router.post("/filter", response_model=FilterResponse)
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

@router.get("/download/{filename}")
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

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "LinkedIn Connections Filter API is running"} 