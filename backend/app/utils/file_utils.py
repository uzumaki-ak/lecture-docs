import os
import shutil
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings
import uuid

async def save_upload_file(upload_file: UploadFile, project_id: str) -> str:
    """
    Save uploaded file to disk
    
    Args:
        upload_file: FastAPI UploadFile
        project_id: Project ID
    
    Returns:
        File path
    """
    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR) / project_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(upload_file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return str(file_path)