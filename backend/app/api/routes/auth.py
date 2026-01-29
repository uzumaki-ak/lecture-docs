from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash
)
from app.core.config import settings
from datetime import timedelta
import httpx

router = APIRouter()
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

async def get_supabase_client():
    """Get Supabase client for authentication"""
    try:
        from supabase import create_client
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise HTTPException(status_code=500, detail="Supabase not configured")
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    except ImportError:
        raise HTTPException(status_code=500, detail="Supabase client not available")

@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Create new user account via Supabase"""
    
    try:
        supabase = await get_supabase_client()
        
        # Sign up user in Supabase
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {"full_name": request.name}
            }
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Failed to create user")
        
        # Create user in local database
        existing_user = db.query(User).filter(User.email == request.email).first()
        if not existing_user:
            user = User(
                email=request.email,
                name=request.name,
                password_hash=get_password_hash(request.password)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user = existing_user
        
        # Create local JWT token
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        }
    except Exception as e:
        print(f"Signup error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password via Supabase"""
    
    try:
        supabase = await get_supabase_client()
        
        # Authenticate user with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get or create user in local database
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            user = User(
                email=request.email,
                name=request.email.split("@")[0],
                password_hash=get_password_hash(request.password)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create local JWT token
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        }
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
