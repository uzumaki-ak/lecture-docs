from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List
from app.db.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/search")
async def search_projects(
    q: str = Query(..., min_length=1, description="Search query"),
    course: Optional[str] = None,
    module: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Full-text search across projects
    Searches: name, description, readme content, tags
    """
    
    query = db.query(Project)
    
    # Full-text search
    search_term = f"%{q}%"
    query = query.filter(
        or_(
            Project.name.ilike(search_term),
            Project.description.ilike(search_term),
            Project.readme_content.ilike(search_term),
            Project.tags.contains([q])  # Array contains search
        )
    )
    
    # Apply filters
    if course:
        query = query.filter(Project.course_name == course)
    
    if module:
        query = query.filter(Project.module_name == module)
    
    # Get results
    projects = query.limit(limit).all()
    
    logger.info(f"Search for '{q}' returned {len(projects)} results")
    
    return {
        "query": q,
        "results": projects,
        "total": len(projects)
    }


@router.get("/filters")
async def get_filters(db: Session = Depends(get_db)):
    """
    Get available filter options
    Returns unique values for courses, modules, tags
    """
    
    # Get unique courses
    courses = db.query(Project.course_name).distinct().filter(
        Project.course_name.isnot(None)
    ).all()
    
    # Get unique modules
    modules = db.query(Project.module_name).distinct().filter(
        Project.module_name.isnot(None)
    ).all()
    
    # Get unique tags
    tags_query = db.query(Project.tags).filter(
        Project.tags.isnot(None)
    ).all()
    
    # Flatten tags
    all_tags = set()
    for (tags,) in tags_query:
        if tags:
            all_tags.update(tags)
    
    return {
        "courses": [c[0] for c in courses],
        "modules": [m[0] for m in modules],
        "tags": sorted(list(all_tags))
    }
