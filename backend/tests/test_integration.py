import pytest
import asyncio
from pathlib import Path
from app.services.ocr_service import ocr_service
from app.services.chunker_service import chunker_service
from app.services.embedding_service import embedding_service
from app.services.rag_service import rag_service

@pytest.mark.asyncio
async def test_full_pipeline():
    """
    Test complete pipeline: file → parse → chunk → embed → RAG
    This is a smoke test that validates the entire flow
    """
    
    # Create test file
    test_content = """
    # Blockchain Basics
    
    A blockchain is a distributed ledger that records transactions across many computers.
    
    ## Smart Contracts
    
    Smart contracts are self-executing contracts with the terms written in code.
    
    ```python
    def transfer(from_address, to_address, amount):
        if balance[from_address] >= amount:
            balance[from_address] -= amount
            balance[to_address] += amount
            return True
        return False
    ```
    """
    
    # 1. Chunk the content
    chunks = chunker_service.chunk_text(
        text=test_content,
        source_type="markdown",
        source_file="test.md"
    )
    
    assert len(chunks) > 0, "Chunking failed"
    
    # 2. Generate embeddings
    chunk_texts = [c["content"] for c in chunks]
    embeddings = await embedding_service.generate_embeddings(chunk_texts)
    
    assert len(embeddings) == len(chunks), "Embedding generation failed"
    assert all(isinstance(e, list) for e in embeddings), "Invalid embedding format"
    
    # 3. Test RAG doc generation
    readme = await rag_service.generate_documentation(
        chunks=chunks,
        project_name="Blockchain Basics Test"
    )
    
    assert readme is not None, "README generation failed"
    assert len(readme) > 100, "README too short"
    assert "blockchain" in readme.lower(), "README missing key content"
    
    print("✅ Full pipeline test passed!")
    print(f"Generated README length: {len(readme)} chars")


@pytest.mark.asyncio
async def test_ocr_extraction():
    """Test OCR extraction (if test image exists)"""
    
    # This test requires a test image
    test_image = Path("tests/fixtures/test_note.png")
    
    if not test_image.exists():
        pytest.skip("Test image not found")
    
    result = await ocr_service.extract_text(str(test_image))
    
    assert result is not None
    assert "text" in result
    assert len(result["text"]) > 0


@pytest.mark.asyncio
async def test_multiple_llm_fallback():
    """Test LLM fallback chain"""
    
    from app.services.llm_service import llm_service
    
    # Simple test prompt
    response = await llm_service.generate_text(
        prompt="What is 2+2?",
        max_tokens=50
    )
    
    assert response is not None
    assert len(response) > 0
    print(f"✅ LLM fallback test passed. Response: {response[:100]}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])