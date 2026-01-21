from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.database import get_db
from app.models.project import Project, ProjectVersion
from app.models.job import Job
from app.schemas.project import (
    ProjectResponse,
    ProjectListResponse,
    ProjectCreate,
    ProjectUpdate
)
from typing import Optional

router = APIRouter()

@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    course: Optional[str] = None,
    module: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List projects with pagination and filters"""
    
    query = db.query(Project)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Project.name.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%")
            )
        )
    
    if course:
        query = query.filter(Project.course_name == course)
    
    if module:
        query = query.filter(Project.module_name == module)
    
    # Get total count
    total = query.count()
    
    # Paginate
    projects = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "projects": projects,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/{slug}", response_model=ProjectResponse)
async def get_project(slug: str, db: Session = Depends(get_db)):
    """Get project by slug"""
    project = db.query(Project).filter(Project.slug == slug).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update last accessed
    from datetime import datetime
    project.last_accessed_at = datetime.utcnow()
    db.commit()
    
    return project

@router.post("/{slug}/regenerate")
async def regenerate_readme(slug: str, db: Session = Depends(get_db)):
    """Regenerate project README"""
    project = db.query(Project).filter(Project.slug == slug).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create job
    job = Job(
        project_id=project.id,
        type="regenerate"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return {
        "job_id": job.id,
        "message": "Regeneration started",
        "status": "pending"
    }

@router.delete("/{slug}")
async def delete_project(slug: str, db: Session = Depends(get_db)):
    """Delete project"""
    project = db.query(Project).filter(Project.slug == slug).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}