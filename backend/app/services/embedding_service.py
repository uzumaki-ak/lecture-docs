import hashlib
import numpy as np
from typing import List, Union, Optional
import logging

logger = logging.getLogger(__name__)
print("✅ EmbeddingService module loaded")

class EmbeddingService:
    """Simple deterministic embedding service"""
    
    def __init__(self):
        self.embedding_dim = 384
        print("✅ EmbeddingService instance created")
    
    async def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        provider: Optional[str] = None
    ) -> Union[List[float], List[List[float]]]:
        """Generate embeddings with proper validation"""
        
        # Handle None or empty
        if texts is None or texts == "":
            logger.warning("⚠️ Received None/empty text, using default")
            return [0.1] * self.embedding_dim
        
        # Convert to list
        single_input = isinstance(texts, str)
        if single_input:
            texts = [texts] if texts else [""]
        
        # Filter out empty strings
        texts = [t if t and t.strip() else "empty" for t in texts]
        
        logger.info(f"🔍 Generating embeddings for {len(texts)} texts")
        
        embeddings = [self._text_to_embedding(text) for text in texts]
        
        return embeddings[0] if single_input else embeddings
    
    def _text_to_embedding(self, text: str) -> List[float]:
        """Convert text to deterministic embedding using SHA-256"""
        print(f"🔍 _text_to_embedding called for text length: {len(text)}")
        
        # Create hash from text
        hash_obj = hashlib.sha256(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # Generate 384-dimensional vector
        embedding = []
        for i in range(self.embedding_dim):
            # Use hash bytes cyclically with mixing
            byte_idx = i % len(hash_bytes)
            next_byte = (i + 1) % len(hash_bytes)
            # Mix bytes for better distribution
            val = (hash_bytes[byte_idx] ^ hash_bytes[next_byte]) / 255.0
            embedding.append(float(val))
        
        print(f"🔍 Final embedding length: {len(embedding)}")
        return embedding


# Create global instance
print("🔄 Creating embedding_service instance...")
embedding_service = EmbeddingService()
print("✅ embedding_service ready")
