import PyPDF2
import pdfplumber
from pathlib import Path
import mimetypes
import ast
from typing import Dict, Optional
import logging
from app.services.ocr_service import OCRService
from app.services.stt_service import STTService  
from app.services.chunker_service import ChunkerService

logger = logging.getLogger(__name__)

class ParserService:
    """
    Multi-format file parser.
    Supports: PDF, code files, markdown, text
    """
    
    async def parse_file(
        self,
        file_path: str,
        file_type: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Parse file and extract content
        
        Args:
            file_path: Path to file
            file_type: Optional file type hint
        
        Returns:
            Dict with extracted content and metadata
        """
        path = Path(file_path)
        
        # Detect file type
        if not file_type:
            mime_type, _ = mimetypes.guess_type(str(path))
            file_type = path.suffix.lower()
        
        # Route to appropriate parser
        if file_type == '.pdf':
            return await self._parse_pdf(file_path)
        elif file_type in ['.py', '.js', '.ts', '.sol', '.java', '.cpp', '.go']:
            return await self._parse_code(file_path, file_type)
        elif file_type in ['.md', '.txt']:
            return await self._parse_text(file_path)
        else:
            # Default to text parsing
            return await self._parse_text(file_path)
    
    async def _parse_pdf(self, file_path: str) -> Dict[str, any]:
        """Parse PDF and extract text"""
        try:
            # Try pdfplumber first (better for tables)
            with pdfplumber.open(file_path) as pdf:
                text = '\n\n'.join(page.extract_text() or '' for page in pdf.pages)
            
            return {
                "content": text,
                "type": "pdf",
                "pages": len(pdf.pages),
                "method": "pdfplumber"
            }
        except:
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = '\n\n'.join(page.extract_text() for page in reader.pages)
            
            return {
                "content": text,
                "type": "pdf",
                "pages": len(reader.pages),
                "method": "pypdf2"
            }
    
    async def _parse_code(self, file_path: str, file_type: str) -> Dict[str, any]:
        """Parse code file and extract structure"""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        metadata = {
            "content": code,
            "type": "code",
            "language": file_type.replace('.', ''),
            "lines": len(code.split('\n'))
        }
        
        # Extract top-level info for Python
        if file_type == '.py':
            try:
                tree = ast.parse(code)
                functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                
                metadata["functions"] = functions
                metadata["classes"] = classes
            except:
                pass
        
        return metadata
    
    async def _parse_text(self, file_path: str) -> Dict[str, any]:
        """Parse plain text or markdown"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "content": content,
            "type": "text",
            "lines": len(content.split('\n')),
            "words": len(content.split())
        }


# Create global instances
ocr_service = OCRService()
stt_service = STTService()
chunker_service = ChunkerService()
parser_service = ParserService()
