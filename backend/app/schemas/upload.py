from pydantic import BaseModel, Field, AnyHttpUrl
from typing import Optional, List
from datetime import datetime 
from enum import Enum

class UploadType(str, Enum):
    """Supported upload types"""
    FILE = "file"
    URL = "url"
    YOUTUBE = "youtube"
    GITHUB = "github"

class UploadRequest(BaseModel):
    """Schema for upload request"""
    project_name: Optional[str] = None
    course_name: Optional[str] = None
    module_name: Optional[str] = None
    lecture_name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    type: UploadType = UploadType.FILE

class UploadResponse(BaseModel):
    """Schema for upload response"""
    job_id: str
    project_id: Optional[str] = None
    message: str
    status: str

class JobStatusResponse(BaseModel):
    """Schema for job status"""
    job_id: str
    project_id: Optional[str] = None
    type: str
    status: str
    progress: int
    current_step: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True