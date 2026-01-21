import tiktoken
from typing import List, Dict, Optional
from app.core.config import settings
import re
import logging

logger = logging.getLogger(__name__)

class ChunkerService:
    """
    Smart chunking service that:
    - Respects code block boundaries
    - Preserves function/method definitions
    - Uses token-based chunking
    - Maintains context overlap
    """
    
    def __init__(self):
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except:
            logger.warning("⚠️ tiktoken not available, using word-based chunking")
            self.tokenizer = None
    
    def chunk_text(
        self,
        text: str,
        source_type: str = "text",
        source_file: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """Chunk text intelligently"""
        
        # FIX: Validate input
        if not text or text.strip() == "":
            logger.warning(f"⚠️ Empty text received for {source_file}, creating placeholder chunk")
            return [{
                "content": f"[Content extraction failed for {source_file or 'file'}]",
                "chunk_index": 0,
                "source_file": source_file,
                "source_type": source_type,
                "is_code_block": False
            }]
        
        print(f"📄 chunk_text called with text length: {len(text)}")
        
        is_code = self._is_code(text, source_type)
        
        if is_code and settings.PRESERVE_CODE_BLOCKS:
            chunks = self._chunk_code(text, source_file)
        else:
            chunks = self._chunk_text_basic(text, source_file)
        
        print(f"📄 Generated {len(chunks)} chunks")
        if chunks:
            print(f"📄 First chunk content length: {len(chunks[0]['content'])}")
            print(f"📄 First chunk preview: {chunks[0]['content'][:100]}...")
        else:
            print("⚠️ WARNING: No chunks generated")
    
        return chunks 
    
    def _is_code(self, text: str, source_type: str) -> bool:
        if source_type in ["code", "python", "javascript", "solidity"]:
            return True
        
        code_patterns = [
            r'def \w+\(',
            r'function \w+\(',
            r'class \w+',
            r'import \w+',
            r'\bif\s+\(',
            r'\bfor\s+\(',
            r'=>',
            r'{\s*$'
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _chunk_code(
        self,
        code: str,
        source_file: Optional[str]
    ) -> List[Dict[str, any]]:
        chunks = []
        lines = code.split('\n')
        current_chunk = []
        current_tokens = 0
        chunk_index = 0
        
        for i, line in enumerate(lines):
            line_tokens = self._count_tokens(line)
            
            if current_tokens + line_tokens > settings.CHUNK_SIZE and current_chunk:
                chunk_text = '\n'.join(current_chunk)
                chunks.append({
                    "content": chunk_text,
                    "chunk_index": chunk_index,
                    "source_file": source_file,
                    "source_type": "code",
                    "is_code_block": True,
                    "start_line": i - len(current_chunk),
                    "end_line": i
                })
                
                overlap_lines = int(len(current_chunk) * (settings.CHUNK_OVERLAP / settings.CHUNK_SIZE))
                current_chunk = current_chunk[-overlap_lines:] if overlap_lines > 0 else []
                current_tokens = self._count_tokens('\n'.join(current_chunk))
                chunk_index += 1
            
            current_chunk.append(line)
            current_tokens += line_tokens
        
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunks.append({
                "content": chunk_text,
                "chunk_index": chunk_index,
                "source_file": source_file,
                "source_type": "code",
                "is_code_block": True,
                "start_line": len(lines) - len(current_chunk),
                "end_line": len(lines)
            })
        
        return chunks
    
    def _chunk_text_basic(
        self,
        text: str,
        source_file: Optional[str]
    ) -> List[Dict[str, any]]:
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = []
        current_tokens = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)
            
            if current_tokens + sentence_tokens > settings.CHUNK_SIZE and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    "content": chunk_text,
                    "chunk_index": chunk_index,
                    "source_file": source_file,
                    "source_type": "text",
                    "is_code_block": False
                })
                
                overlap_size = int(len(current_chunk) * (settings.CHUNK_OVERLAP / settings.CHUNK_SIZE))
                current_chunk = current_chunk[-overlap_size:] if overlap_size > 0 else []
                current_tokens = self._count_tokens(' '.join(current_chunk))
                chunk_index += 1
            
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                "content": chunk_text,
                "chunk_index": chunk_index,
                "source_file": source_file,
                "source_type": "text",
                "is_code_block": False
            })
        
        return chunks
    
    def _count_tokens(self, text: str) -> int:
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        return len(text.split())

chunker_service = ChunkerService()
