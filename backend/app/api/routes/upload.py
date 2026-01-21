from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.job import Job
from app.models.project import Project
from app.schemas.upload import UploadResponse
from app.utils.file_utils import save_upload_file
from app.utils.slug_generator import generate_slug
from app.core.config import settings
import uuid
import os
import re
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=UploadResponse)
async def upload_files(
    files: list[UploadFile] = File(default=[]),  # Optional
    project_name: str = Form(None),
    course_name: str = Form(None),
    module_name: str = Form(None),
    lecture_name: str = Form(None),
    description: str = Form(None),
    url: str = Form(None),  # YouTube URL
    db: Session = Depends(get_db)
):
    """Upload files OR YouTube URL"""
    
    # Must have either files or URL
    if not files and not url:
        raise HTTPException(
            status_code=400,
            detail="Please provide files or YouTube URL"
        )
    
    # Generate project name
    if not project_name:
        if url:
            from app.utils.youtube_utils import youtube_service
            video_info = await youtube_service.get_video_info(url)
            project_name = video_info.get("title", "youtube-video")
        else:
            project_name = f"{course_name or 'course'}-{module_name or 'module'}-{lecture_name or 'lecture'}"
    
    slug = generate_slug(project_name, db)
    
    project = Project(
        name=project_name,
        slug=slug,
        description=description,
        course_name=course_name,
        module_name=module_name,
        lecture_name=lecture_name
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    file_paths = []
    
    # Handle YouTube URL
    if url:
        from app.utils.youtube_utils import youtube_service
        
        # Get transcript
        transcript = await youtube_service.get_transcript(url)

        logger.info(f"🔍 Transcript length: {len(transcript) if transcript else 0}")
        
        if not transcript or len(transcript.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract meaningful content from YouTube video. The video might not have captions/audio."
            )
        
        # Save transcript as text file
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        transcript_path = f"{settings.UPLOAD_DIR}/{project.id}_youtube.txt"
        
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcript)

        logger.info(f"✅ Saved transcript to {transcript_path}")
        
        file_paths.append(transcript_path)
    
    # Handle uploaded files
    for file in files:
        file_path = await save_upload_file(file, project.id)
        file_paths.append(file_path)
    
    # Create job
    job = Job(
        project_id=project.id,
        type="upload",
        input_data={
            "files": file_paths,
            "project_name": project_name
        }
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return {
        "job_id": job.id,
        "project_id": project.id,
        "message": "Upload successful. Processing started.",
        "status": "pending"
    }

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Get job status"""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.id,
        "project_id": job.project_id,
        "type": job.type,
        "status": job.status,
        "progress": job.progress,
        "current_step": job.current_step,
        "result": job.result,
        "error": job.error,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at
    }
