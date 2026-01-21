from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.redis_client import redis_client
import httpx

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    Verifies: Database, Redis, Chroma connections
    """
    status = {"status": "healthy", "services": {}}
    
    # Check database
    try:
        db.execute("SELECT 1")
        status["services"]["database"] = "connected"
    except Exception as e:
        status["services"]["database"] = f"error: {str(e)}"
        status["status"] = "unhealthy"
    
    # Check Redis
    try:
        await redis_client.redis.ping()
        status["services"]["redis"] = "connected"
    except Exception as e:
        status["services"]["redis"] = f"error: {str(e)}"
        status["status"] = "unhealthy"
    
    # Check Chroma
    try:
        from app.core.config import settings
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{settings.CHROMA_HOST}:{settings.CHROMA_PORT}/api/v1/heartbeat",
                timeout=5
            )
            status["services"]["chroma"] = "connected"
    except Exception as e:
        status["services"]["chroma"] = f"error: {str(e)}"
        status["status"] = "unhealthy"
    
    return status
