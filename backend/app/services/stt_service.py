from typing import Dict, List, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class STTService:
    """Speech-to-Text with Whisper"""
    
    def __init__(self):
        self.whisper_model = None
        
        # Try to load Whisper (optional)
        try:
            import whisper
            self.whisper_model = whisper.load_model(
                settings.WHISPER_MODEL,
                device=settings.WHISPER_DEVICE
            )
            logger.info(f"✅ Whisper initialized: {settings.WHISPER_MODEL}")
        except Exception as e:
            logger.warning(f"⚠️ Whisper unavailable: {e}")
    
    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict:
        """Transcribe audio to text"""
        if not self.whisper_model:
            return {
                "text": "[Audio transcription unavailable - Whisper not loaded]",
                "segments": [],
                "language": language or "unknown",
                "method": "disabled"
            }
        
        try:
            result = self.whisper_model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                fp16=False
            )
            
            return {
                "text": result["text"],
                "segments": result.get("segments", []),
                "language": result.get("language"),
                "method": "whisper"
            }
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                "text": f"[Transcription failed: {str(e)}]",
                "segments": [],
                "language": language or "unknown",
                "method": "error"
            }


# Add this function for YouTube service
async def transcribe_audio(audio_path: str) -> str:
    """Simple wrapper for YouTube service"""
    service = STTService()
    result = await service.transcribe(audio_path)
    return result["text"]


stt_service = STTService()