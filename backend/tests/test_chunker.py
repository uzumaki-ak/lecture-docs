import pytest
from app.services.chunker_service import ChunkerService

def test_text_chunking():
    """Test basic text chunking"""
    chunker = ChunkerService()
    
    text = "This is a sentence. " * 100  # Long text
    chunks = chunker.chunk_text(text, source_type="text")
    
    assert len(chunks) > 1
    assert all("content" in chunk for chunk in chunks)
    assert all("chunk_index" in chunk for chunk in chunks)

def test_code_preservation():
    """Test code block preservation"""
    chunker = ChunkerService()
    
    code = """
def function1():
    pass

def function2():
    pass
    """ * 20
    
    chunks = chunker.chunk_text(code, source_type="code")
    
    assert len(chunks) > 0
    assert all(chunk["is_code_block"] for chunk in chunks)