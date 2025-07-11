from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class FilterRequest(BaseModel):
    """Request model for filtering connections"""
    prompt: str = Field(..., description="Natural language prompt for filtering", min_length=1, max_length=500)
    file_id: Optional[str] = None  # Add file_id for stateless operation

class FilterResponse(BaseModel):
    """Response model for filtered results"""
    success: bool
    message: str
    filtered_count: int
    total_count: int
    preview_data: List[dict] = Field(default_factory=list, description="Preview of filtered results")
    download_url: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    details: Optional[str] = None

class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    success: bool
    message: str
    total_rows: int
    columns: List[str]
    preview_data: List[dict]
    file_id: Optional[str] = None  # Add file_id to upload response

class ProcessingStatus(str, Enum):
    """Enum for processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed" 