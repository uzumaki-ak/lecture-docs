from typing import Optional
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.core.security import decode_access_token, verify_clerk_token
from app.core.redis_client import redis_client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current authenticated user from token
    Supports both dev auth (JWT) and Clerk tokens
    """
    token = credentials.credentials
    
    try:
        # Try dev auth first
        if settings.DEV_AUTH:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            return user
        
        # Try Clerk auth
        if settings.CLERK_SECRET_KEY:
            payload = verify_clerk_token(token)
            clerk_id = payload.get("sub")
            
            # Find or create user
            user = db.query(User).filter(User.clerk_id == clerk_id).first()
            if not user:
                # Auto-create user from Clerk data
                user = User(
                    clerk_id=clerk_id,
                    email=payload.get("email"),
                    name=payload.get("name")
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            return user
        
        raise HTTPException(status_code=401, detail="Authentication not configured")
        
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user but don't require authentication
    Returns None if no valid token
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except:
        return None


async def check_rate_limit(
    request: Request,
    max_requests: int = 100,
    window_seconds: int = 3600
) -> bool:
    """
    Check rate limit for endpoint
    Uses IP address as identifier
    """
    if not settings.RATE_LIMIT_ENABLED:
        return True
    
    # Get client IP
    client_ip = request.client.host
    
    # Check rate limit
    identifier = f"ip:{client_ip}"
    allowed = await redis_client.rate_limit(
        identifier=identifier,
        max_requests=max_requests,
        window_seconds=window_seconds
    )
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {max_requests} requests per {window_seconds} seconds."
        )
    
    return True


async def check_upload_rate_limit(request: Request):
    """Rate limit for uploads"""
    return await check_rate_limit(
        request,
        max_requests=settings.RATE_LIMIT_UPLOADS_PER_HOUR,
        window_seconds=3600
    )


async def check_chat_rate_limit(request: Request):
    """Rate limit for chat"""
    return await check_rate_limit(
        request,
        max_requests=settings.RATE_LIMIT_CHAT_PER_MINUTE,
        window_seconds=60
    )
