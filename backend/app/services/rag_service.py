from typing import List, Dict
from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service
from app.services.vectorstore_service import vectorstore_service
import logging

logger = logging.getLogger(__name__)

class RAGService:
    """RAG orchestration for chat and doc generation"""
    
    async def generate_documentation(
        self,
        chunks: List[Dict],
        project_name: str
    ) -> str:
        """Generate README from chunks"""
        
        # Combine chunks
        context = "\n\n".join([c["content"] for c in chunks[:20]])
        
        # Use prompt from prompts/readme_prompt.py
        from app.prompts.readme_prompt import get_readme_prompt
        
        system_prompt = get_readme_prompt()
        user_prompt = f"""Project: {project_name}

Content to document:
{context}

Generate a comprehensive, kid-friendly README with examples."""
        
        readme = await llm_service.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=3000,
            temperature=0.7
        )
        
        return readme
    
    async def chat(
        self,
        project_id: str,
        query: str,
        chat_history: List[Dict] = None
    ) -> Dict:
        """RAG-based chat with proper context"""
        
        # Get embeddings for query
        query_embedding = await embedding_service.generate_embeddings(query)
        
        # Search vector store
        results = await vectorstore_service.search(
            project_id=project_id,
            query_embedding=query_embedding,
            top_k=5  # Get top 5 most relevant chunks
        )
        
        if not results:
            return {
                "response": "I don't have any context about this project yet. Please make sure the files were processed correctly.",
                "sources": [],
                "model": "none"
            }
        
        # Build context from results
        context = "\n\n".join([r["content"] for r in results])
        
        # Import and use the chat prompt
        from app.prompts.readme_prompt import get_chat_system_prompt
        system_prompt = get_chat_system_prompt(context)
        
        # Generate response
        response = await llm_service.generate_text(
            prompt=query,
            system_prompt=system_prompt,
            max_tokens=500,
            temperature=0.7
        )
        
        return {
            "response": response,
            "sources": results,
            "model": "llm"
        }

rag_service = RAGService()
