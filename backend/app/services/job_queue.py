import uuid
import asyncio
from app.db.database import SessionLocal
from app.models.job import Job
from app.services.ocr_service import ocr_service
from app.services.parser_service import parser_service
from app.services.chunker_service import chunker_service
from app.services.vectorstore_service import vectorstore_service
from app.services.rag_service import rag_service
from app.core.config import settings
import logging
from app.models.project import Chunk 
logger = logging.getLogger(__name__)

async def process_job(job_id: str):
    """Process a single job"""
    db = SessionLocal()
    
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            return
        
        # Update status
        job.status = "processing"
        job.progress = 10
        db.commit()
        
        if job.type == "upload":
            await process_upload_job(job, db)
        elif job.type == "regenerate":
            await process_regenerate_job(job, db)
        
        # Mark complete
        job.status = "completed"
        job.progress = 100
        db.commit()
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        job.status = "failed"
        job.error = str(e)
        db.commit()
    finally:
        db.close()



async def process_upload_job(job: Job, db):
    """Process file upload with better error handling"""
    from app.models.project import Project, File, Chunk
    from app.services.parser_service import parser_service
    from app.services.chunker_service import chunker_service
    from app.services.vectorstore_service import vectorstore_service
    from app.services.rag_service import rag_service
    import uuid
    import logging
    import os
    
    logger = logging.getLogger(__name__)
    
    files = job.input_data.get("files", [])
    project_id = job.project_id
    
    logger.info(f"📦 Processing {len(files)} files for project {project_id}")
    
    all_chunks = []
    
    for file_path in files:
        try:
            logger.info(f"📄 Processing file: {file_path}")
            
            job.current_step = f"Processing {os.path.basename(file_path)}"
            job.progress = 30
            db.commit()
            
            # Read file directly for YouTube transcripts
            if "_youtube.txt" in file_path:
                logger.info("🎥 Processing YouTube transcript")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if not content or len(content.strip()) < 50:
                        logger.error(f"❌ YouTube transcript too short: {len(content)} chars")
                        continue
                    
                    logger.info(f"✅ YouTube content: {len(content)} chars")
                    parsed = {"content": content, "type": "text"}
                    
                except Exception as e:
                    logger.error(f"❌ Failed to read YouTube file: {e}")
                    continue
            else:
                # Normal file parsing
                parsed = await parser_service.parse_file(file_path)
                content = parsed.get("content", "")
                
                if not content or len(content.strip()) < 10:
                    logger.warning(f"⚠️ Empty content from {file_path}")
                    continue
            
            content = parsed["content"]
            logger.info(f"📄 Content length: {len(content)} chars")
            
            # Save file record
            file_record = File(
                project_id=project_id,
                filename=os.path.basename(file_path),
                original_name=os.path.basename(file_path),
                file_type=parsed.get("type", "text"),
                file_path=file_path,
                file_size=len(content),
                is_processed=True,
                extracted_text=content
            )
            db.add(file_record)
            db.commit()
            
            # Chunk content
            logger.info(f"✂️ Chunking {len(content)} chars...")
            chunks = chunker_service.chunk_text(
                text=content,
                source_type=parsed.get("type", "text"),
                source_file=os.path.basename(file_path)
            )
            
            logger.info(f"✂️ Generated {len(chunks)} chunks")
            
            if not chunks:
                logger.error(f"❌ No chunks generated from {file_path}")
                continue
            
            # Save chunks
            for i, chunk_data in enumerate(chunks):
                chunk_id = str(uuid.uuid4())
                
                # Validate chunk content
                if not chunk_data.get("content") or len(chunk_data["content"].strip()) < 5:
                    logger.warning(f"⚠️ Skipping empty chunk {i}")
                    continue
                
                chunk = Chunk(
                    id=chunk_id,
                    project_id=project_id,
                    content=chunk_data["content"],
                    chunk_index=i,
                    source_file=chunk_data.get("source_file"),
                    source_type=chunk_data.get("source_type"),
                    is_code_block=chunk_data.get("is_code_block", False)
                )
                db.add(chunk)
                
                chunk_data["id"] = chunk_id
                all_chunks.append(chunk_data)
            
            db.commit()
            logger.info(f"✅ Saved {len(all_chunks)} chunks to DB")
            
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}", exc_info=True)
            continue
    
    # Validate we have chunks
    if not all_chunks:
        logger.error("❌ NO CHUNKS GENERATED")
        job.status = "failed"
        job.error = "Failed to extract any content from uploaded files"
        db.commit()
        return
    
    logger.info(f"📊 Total valid chunks: {len(all_chunks)}")
    
    # Add to vectorstore
    job.current_step = "Creating embeddings"
    job.progress = 60
    db.commit()
    
    try:
        await vectorstore_service.add_chunks(project_id, all_chunks)
        logger.info(f"✅ Added to vectorstore")
    except Exception as e:
        logger.error(f"❌ Vectorstore error: {e}")
        job.status = "failed"
        job.error = str(e)
        db.commit()
        return
    
    # Generate README
    job.current_step = "Generating documentation"
    job.progress = 80
    db.commit()
    
    try:
        readme = await rag_service.generate_documentation(
            chunks=all_chunks,
            project_name=job.input_data.get("project_name", "Project")
        )
        logger.info(f"✅ README: {len(readme)} chars")
    except Exception as e:
        logger.error(f"❌ README failed: {e}")
        readme = f"# {job.input_data.get('project_name')}\n\nContent processed but documentation generation failed."
    
    project = db.query(Project).filter(Project.id == project_id).first()
    project.readme_content = readme
    db.commit()

async def process_regenerate_job(job: Job, db):
    """Regenerate README for existing project"""
    from app.models.project import Project
    
    project = db.query(Project).filter(Project.id == job.project_id).first()
    chunks = db.query(Chunk).filter(Chunk.project_id == job.project_id).all()
    
    readme = await rag_service.generate_documentation(
        chunks=[{"content": c.content} for c in chunks],
        project_name=project.name
    )
    
    project.readme_content = readme
    db.commit()

async def worker_loop():
    """Main worker loop"""
    logger.info("🚀 Worker started")
    
    while True:
        db = SessionLocal()
        
        try:
            # Get pending jobs
            jobs = db.query(Job).filter(
                Job.status == "pending"
            ).limit(settings.WORKER_CONCURRENCY).all()
            
            for job in jobs:
                await process_job(job.id)
            
        except Exception as e:
            logger.error(f"Worker error: {e}")
        finally:
            db.close()
        
        await asyncio.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":
    asyncio.run(worker_loop())
