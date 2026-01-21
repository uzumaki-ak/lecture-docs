import pytesseract
from PIL import Image
from typing import Dict, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class OCRService:
    """OCR service - Tesseract only (TrOCR optional)"""
    
    def __init__(self):
        self.trocr_processor = None
        self.trocr_model = None
        
        # Try to load TrOCR (optional)
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            import torch
            
            self.trocr_processor = TrOCRProcessor.from_pretrained(settings.TROCR_MODEL)
            self.trocr_model = VisionEncoderDecoderModel.from_pretrained(settings.TROCR_MODEL)
            
            if settings.USE_GPU and torch.cuda.is_available():
                self.trocr_model = self.trocr_model.to("cuda")
            
            logger.info("✅ TrOCR initialized for handwritten text")
        except Exception as e:
            logger.warning(f"⚠️ TrOCR unavailable, using Tesseract only: {e}")
    
    async def extract_text(self, image_path: str, is_handwritten: bool = False) -> Dict:
        """Extract text from image"""
        try:
            if is_handwritten and self.trocr_model:
                return await self._extract_trocr(image_path)
            else:
                return await self._extract_tesseract(image_path)
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return await self._extract_tesseract(image_path)
    
    async def _extract_trocr(self, image_path: str) -> Dict:
        """TrOCR for handwritten"""
        import torch
        from PIL import Image
        
        image = Image.open(image_path).convert("RGB")
        pixel_values = self.trocr_processor(image, return_tensors="pt").pixel_values
        
        if settings.USE_GPU and torch.cuda.is_available():
            pixel_values = pixel_values.to("cuda")
        
        generated_ids = self.trocr_model.generate(pixel_values)
        text = self.trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return {
            "text": text,
            "confidence": 0.9,
            "method": "trocr"
        }
    
    async def _extract_tesseract(self, image_path: str) -> Dict:
        """Tesseract OCR - fast & reliable"""
        image = Image.open(image_path)
        
        data = pytesseract.image_to_data(
            image,
            lang=settings.TESSERACT_LANG,
            output_type=pytesseract.Output.DICT
        )
        
        text_parts = []
        confidences = []
        
        for i, conf in enumerate(data['conf']):
            if conf > 0:
                text_parts.append(data['text'][i])
                confidences.append(float(conf))
        
        text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "text": text,
            "confidence": avg_confidence / 100.0,
            "method": "tesseract"
        }

ocr_service = OCRService()