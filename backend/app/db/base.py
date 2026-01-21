from app.db.database import Base
from app.models.user import User
from app.models.project import Project, ProjectVersion, File, Chunk
from app.models.chat import ChatMessage
from app.models.job import Job

# This ensures all models are registered with SQLAlchemy
__all__ = [
    "Base",
    "User",
    "Project",
    "ProjectVersion",
    "File",
    "Chunk",
    "ChatMessage",
    "Job"
]