from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
import pandas as pd
from typing import Dict, Any
import logging
import tempfile
import os
import uuid
import pickle

from backend.models.schemas import FilterRequest, FilterResponse, ErrorResponse, FileUploadResponse
from backend.services.csv_service import CSVService
from backend.services.ai_service import AIService

logger = logging.getLogger(__name__)

router = APIRouter()

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
    logger.info(f"/upload called with filename: {file.filename}")
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        file_content = await file.read()
        is_valid, error_message, df = csv_service.validate_csv(file_content)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Check for empty data (only headers, no rows)
        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded CSV contains only headers and no data rows.")
        
        # Store the dataframe in a temp file, return file_id
        file_id = str(uuid.uuid4())
        temp_path = os.path.join(tempfile.gettempdir(), f"linkedin_upload_{file_id}.pkl")
        with open(temp_path, "wb") as f:
            pickle.dump(df, f)
        
        preview_data = csv_service.get_preview_data(df)
        logger.info(f"/upload success: file_id={file_id}, rows={len(df)}")
        
        return FileUploadResponse(
            success=True,
            message=f"Successfully uploaded {file.filename}",
            total_rows=len(df),
            columns=df.columns.tolist(),
            preview_data=preview_data,
            file_id=file_id
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
    logger.info(f"/filter called with prompt: {request.prompt}, file_id: {request.file_id}")
    try:
        # Load the uploaded dataframe from temp file using file_id
        if not request.file_id:
            logger.warning("/filter: No file_id provided")
            raise HTTPException(status_code=400, detail="No file_id provided. Please upload a file first.")
        temp_path = os.path.join(tempfile.gettempdir(), f"linkedin_upload_{request.file_id}.pkl")
        if not os.path.exists(temp_path):
            logger.warning(f"/filter: Uploaded file not found for file_id={request.file_id}")
            raise HTTPException(status_code=400, detail="Uploaded file not found. Please upload again.")
        with open(temp_path, "rb") as f:
            df = pickle.load(f)
        logger.info(f"/filter: Loaded DataFrame for file_id={request.file_id}, rows={len(df)}")
        
        # Generate sample data for AI
        sample_df = df.head(5).to_string(index=False)
        
        # Generate filter code using AI
        filter_code = ai_service.generate_filter_code(request.prompt, sample_df)
        
        # Validate the generated code
        if not ai_service.validate_filter_code(filter_code):
            logger.error("/filter: Generated filter code is invalid")
            raise HTTPException(status_code=500, detail="Generated filter code is invalid")
        
        # Execute the filter code
        local_vars = {'df': df.copy()}
        exec(filter_code, {}, local_vars)
        filtered_df = local_vars['df']
        logger.info(f"/filter: Filtered DataFrame, result rows={len(filtered_df)}")
        
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
    logger.info(f"/download called for filename: {filename}")
    try:
        csv_service = CSVService()
        file_path = csv_service.temp_dir / filename
        
        logger.info(f"Looking for file: {file_path}")
        logger.info(f"File exists: {file_path.exists()}")
        logger.info(f"Temp dir contents: {list(csv_service.temp_dir.glob('*'))}")
        
        if not file_path.exists():
            logger.warning(f"/download: File not found: {filename}")
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
    logger.info("/health check called")
    return {"status": "healthy", "message": "LinkedIn Connections Filter API is running"} 