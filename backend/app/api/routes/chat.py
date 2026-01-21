from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.project import Project
from app.models.chat import ChatMessage
from app.schemas.chat import ChatRequest, ChatMessageResponse, ChatHistoryResponse
from app.services.rag_service import rag_service
from app.core.config import settings
import json

router = APIRouter()

@router.post("/projects/{slug}/chat")
async def chat_with_project(
    slug: str,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Chat with project using RAG"""
    
    # Get project
    project = db.query(Project).filter(Project.slug == slug).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get chat history
    history = db.query(ChatMessage).filter(
        ChatMessage.project_id == project.id
    ).order_by(ChatMessage.created_at.desc()).limit(settings.MAX_CHAT_HISTORY).all()
    
    history.reverse()  # Oldest first
    
    # Save user message
    user_message = ChatMessage(
        project_id=project.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()
    
    # Generate response
    result = await rag_service.chat(
        project_id=project.id,
        query=request.message,
        chat_history=[{"role": m.role, "content": m.content} for m in history]
    )
    
    # Save assistant message
    assistant_message = ChatMessage(
        project_id=project.id,
        role="assistant",
        content=result["response"],
        retrieved_chunks=[
            {"id": chunk["id"], "content": chunk["content"][:200]}
            for chunk in result["sources"]
        ],
        llm_provider=result.get("model")
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    
    return {
        "message": assistant_message,
        "sources": result["sources"]
    }

@router.get("/projects/{slug}/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    slug: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat history for project"""
    
    project = db.query(Project).filter(Project.slug == slug).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.project_id == project.id
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    messages.reverse()
    
    return {
        "messages": messages,
        "total": len(messages)
    }
