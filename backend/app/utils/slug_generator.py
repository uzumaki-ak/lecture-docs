import re
from sqlalchemy.orm import Session
from app.models.project import Project

def generate_slug(name: str, db: Session) -> str:
    """
    Generate unique URL-safe slug from project name
    
    Args:
        name: Project name
        db: Database session
    
    Returns:
        Unique slug
    """
    # Convert to lowercase
    slug = name.lower()
    
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Limit length
    slug = slug[:100]
    
    # Check for uniqueness
    base_slug = slug
    counter = 1
    
    while db.query(Project).filter(Project.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug