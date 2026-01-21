import chromadb
from typing import List, Dict
from app.core.config import settings
from app.services.embedding_service import embedding_service
import logging

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Chroma vector database wrapper"""
    
    def __init__(self):
        # Use HTTP client to connect to Docker Chroma
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
        )
        logger.info("✅ Chroma HTTP client initialized")
    
    async def create_collection(self, project_id: str):
        collection_name = f"project_{project_id}"

        try:
            return self.client.create_collection(
                name=collection_name,
                metadata={"description": f"Collection for project {project_id}"},
            )
        except Exception as e:
            # Collection might already exist
            logger.info(f"ℹ️ Collection {collection_name} already exists or error: {e}")
            return self.client.get_collection(name=collection_name)

    async def add_chunks(self, project_id: str, chunks: List[Dict]):
        """Add chunks with validation"""
        
        # FIX: Validate chunks
        if not chunks or len(chunks) == 0:
            logger.error("❌ No chunks provided to add_chunks")
            raise ValueError("Cannot add empty chunks to vector store")
        
        collection = await self.create_collection(project_id)
        
        # Extract data
        texts = [chunk["content"] for chunk in chunks]
        
        # FIX: Validate texts
        if not texts or all(not t or t.strip() == "" for t in texts):
            logger.error("❌ All chunk texts are empty")
            raise ValueError("Cannot add chunks with empty content")
        
        logger.info(f"🔍 Generating embeddings for {len(texts)} texts")
        embeddings = await embedding_service.generate_embeddings(texts)
        
        # FIX: Validate embeddings
        if not embeddings or len(embeddings) == 0:
            logger.error("❌ Embedding generation returned empty")
            raise ValueError("Failed to generate embeddings")
        
        ids = [chunk["id"] for chunk in chunks]
        metadatas = [
            {
                "source_file": chunk.get("source_file", "unknown"),
                "chunk_index": chunk.get("chunk_index", 0),
                "is_code": chunk.get("is_code_block", False),
            }
            for chunk in chunks
        ]
        
        logger.info(f"🔍 Adding to Chroma: {len(ids)} ids, {len(texts)} docs, {len(embeddings)} embeddings")
        
        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        
        logger.info(f"✅ Successfully added {len(chunks)} chunks to {project_id}")

    async def search(
        self,
        project_id: str,
        query_embedding: List[float],
        top_k: int = 10,
    ) -> List[Dict]:
        try:
            collection = self.client.get_collection(
                name=f"project_{project_id}"
            )
        except Exception as e:
            logger.error(f"❌ Collection not found for project {project_id}: {e}")
            return []

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        # Handle empty results
        if not results["ids"][0]:
            return []

        return [
            {
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results.get("distances", [[None]])[0][i],
            }
            for i in range(len(results["ids"][0]))
        ]


# ⚠️ still okay for now, but better moved to FastAPI startup later
vectorstore_service = VectorStoreService()
