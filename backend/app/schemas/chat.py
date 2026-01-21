from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessageBase(BaseModel):
    """Base chat message schema"""
    content: str = Field(..., min_length=1, max_length=10000)

class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a chat message"""
    project_id: str

class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: str
    project_id: str
    user_id: Optional[str] = None
    role: str
    content: str
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    tokens: Optional[int] = None
    latency_ms: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    """Schema for chat request"""
    message: str = Field(..., min_length=1, max_length=10000)
    stream: bool = False

class ChatHistoryResponse(BaseModel):
    """Schema for chat history"""
    messages: List[ChatMessageResponse]
    total: int




