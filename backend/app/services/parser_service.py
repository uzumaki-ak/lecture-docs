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
from app.services.llm_service import llm_service

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
        
        logger.info(f"📂 Parsing {path.name} (type: {file_type})")
        
        # Route to appropriate parser
        if file_type == '.pdf':
            return await self._parse_pdf(file_path)
        elif file_type in ['.py', '.js', '.ts', '.sol', '.java', '.cpp', '.go']:
            return await self._parse_code(file_path, file_type)
        elif file_type in ['.md', '.txt']:
            return await self._parse_text(file_path)
        elif file_type in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            # Image files - use LLM Vision to extract text
            logger.info(f"🖼️ Image detected, using LLM Vision")
            return await self._parse_image(file_path)
        else:
            # Try text parsing, but handle binary files gracefully
            logger.info(f"⚠️ Unknown type, attempting text parsing")
            return await self._parse_text(file_path)
    
    async def _parse_pdf(self, file_path: str) -> Dict[str, any]:
        """Parse PDF: text extraction → OCR for handwritten → LLM Vision as last resort"""
        try:
            ocr_service = OCRService()
            extracted_text = []
            
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    # Step 1: Try normal text extraction
                    page_text = page.extract_text()
                    
                    if page_text and page_text.strip() and len(page_text.strip()) > 20:
                        extracted_text.append(page_text)
                        logger.info(f"✅ Text extracted from page {page_num + 1}")
                    else:
                        # Step 2: No text → try OCR (Tesseract + TrOCR)
                        logger.info(f"📄 Page {page_num + 1} has no text, trying OCR...")
                        ocr_success = False
                        
                        try:
                            # Get page as image using pdfplumber's built-in method
                            im = page.to_image(resolution=150)
                            
                            import tempfile
                            import os
                            from PIL import Image
                            
                            # Save to temp file
                            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                                if hasattr(im, 'original'):
                                    # pdfplumber image object
                                    im.original.save(tmp.name, 'PNG')
                                else:
                                    # PIL image
                                    im.save(tmp.name, 'PNG')
                                temp_path = tmp.name
                            
                            # Try OCR (TrOCR for handwritten)
                            ocr_result = await ocr_service.extract_text(temp_path, is_handwritten=True)
                            
                            if ocr_result.get("text", "").strip():
                                extracted_text.append(ocr_result["text"])
                                logger.info(f"✅ OCR extracted text from page {page_num + 1} using {ocr_result.get('method', 'unknown')}")
                                ocr_success = True
                            
                            # Cleanup
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                        except Exception as e:
                            logger.warning(f"⚠️ OCR failed for page {page_num + 1}: {e}")
                        
                        # Step 3: OCR failed → fallback to LLM Vision (last resort)
                        if not ocr_success:
                            try:
                                logger.info(f"🔍 Page {page_num + 1} OCR failed, using LLM Vision...")
                                
                                im = page.to_image(resolution=150)
                                
                                prompt = """Extract ALL text from this handwritten/image document. 
                                Preserve structure, highlighting, and annotations. Be thorough."""
                                
                                llm_text = await llm_service.extract_text_from_image(im, prompt)
                                
                                if llm_text and llm_text.strip():
                                    extracted_text.append(llm_text)
                                    logger.info(f"✅ LLM Vision extracted text from page {page_num + 1}")
                                
                            except Exception as e:
                                logger.warning(f"⚠️ LLM Vision failed for page {page_num + 1}: {e}")
                
                text = '\n\n'.join(extracted_text)
            
            if not text.strip():
                logger.warning(f"⚠️ No text extracted from PDF")
            
            return {
                "content": text,
                "type": "pdf",
                "pages": total_pages,
                "method": "text→ocr→llm"
            }
        except Exception as e:
            logger.error(f"❌ PDF parsing failed: {e}")
            try:
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = '\n\n'.join(page.extract_text() for page in reader.pages if page.extract_text())
                
                return {
                    "content": text,
                    "type": "pdf",
                    "pages": len(reader.pages),
                    "method": "pypdf2"
                }
            except Exception as fallback_e:
                logger.error(f"❌ All PDF parsing failed: {fallback_e}")
                return {
                    "content": "",
                    "type": "pdf",
                    "pages": 0,
                    "method": "failed"
                }
    
    async def _parse_image(self, file_path: str) -> Dict[str, any]:
        """Extract text from image using LLM Vision"""
        try:
            from PIL import Image
            
            logger.info(f"🖼️ Processing image: {file_path}")
            
            # Open image
            image = Image.open(file_path)
            
            # Use LLM Vision to extract text
            prompt = """Extract ALL text from this image. 
            If it's handwritten notes, preserve the structure and formatting.
            Include all visible text, annotations, and important information."""
            
            text = await llm_service.extract_text_from_image(image, prompt)
            
            if text and text.strip():
                logger.info(f"✅ LLM Vision extracted text from image")
                return {
                    "content": text,
                    "type": "image",
                    "method": "llm_vision"
                }
            else:
                logger.warning(f"⚠️ LLM Vision returned empty for image")
                return {
                    "content": "",
                    "type": "image",
                    "method": "llm_vision_empty"
                }
        except Exception as e:
            logger.error(f"❌ Image parsing failed: {e}")
            return {
                "content": "",
                "type": "image",
                "method": "failed"
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
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Binary file - skip
            logger.warning(f"⚠️ Binary file detected: {file_path} - skipping")
            return {
                "content": "",
                "type": "text",
                "lines": 0,
                "words": 0
            }
        
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
