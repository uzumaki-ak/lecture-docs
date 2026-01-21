from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token bearer
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional expiration time delta
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Dependency to get the current authenticated user
    
    Args:
        credentials: HTTP Authorization credentials
    
    Returns:
        User data from token payload
    
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        return {
            "id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role", "user")
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to get the current active user
    Extends get_current_user with additional checks
    """
    # Add additional checks here (e.g., user is active, not banned, etc.)
    return current_user

def verify_clerk_token(token: str) -> dict:
    """
    Verify a Clerk JWT token
    
    Args:
        token: Clerk JWT token
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token verification fails
    """
    if not settings.CLERK_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Clerk not configured")
    
    try:
        # Clerk uses RS256 algorithm
        # In production, you should fetch the public key from Clerk's JWKS endpoint
        payload = jwt.decode(
            token,
            settings.CLERK_SECRET_KEY,
            algorithms=["RS256"],
            options={"verify_signature": False}  # For dev; enable in production
        )
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Clerk token validation failed: {str(e)}")
