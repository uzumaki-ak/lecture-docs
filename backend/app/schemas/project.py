

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    course_name: Optional[str] = None
    module_name: Optional[str] = None
    lecture_name: Optional[str] = None
    tags: List[str] = []

class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    pass

class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    course_name: Optional[str] = None
    module_name: Optional[str] = None
    lecture_name: Optional[str] = None
    tags: Optional[List[str]] = None

class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: str
    slug: str
    readme_content: Optional[str] = None
    folder_tree: Optional[Dict[str, Any]] = None
    language: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime
    
    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    """Schema for list of projects"""
    projects: List[ProjectResponse]
    total: int
    page: int
    page_size: int




