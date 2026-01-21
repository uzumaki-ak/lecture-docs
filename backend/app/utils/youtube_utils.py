import yt_dlp
from typing import Dict, Optional
import logging
import re
import os
import tempfile

logger = logging.getLogger(__name__)

class YouTubeService:
    """YouTube video/transcript extraction"""
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def get_video_info(self, url: str) -> Dict:
        """Get video metadata"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    "title": info.get("title", "Unknown"),
                    "description": info.get("description", ""),
                    "duration": info.get("duration", 0),
                    "thumbnail": info.get("thumbnail"),
                    "uploader": info.get("uploader"),
                }
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return {"title": "YouTube Video", "description": ""}
    
    async def get_transcript(self, url: str) -> Optional[str]:
        """Get video transcript - try subtitles first, then audio"""
        logger.info(f"🎥 Getting transcript for: {url}")
        
        # Try 1: Get auto-generated subtitles
        try:
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en'],
                'skip_download': True,
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Check for subtitles
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                subtitle_text = None
                if 'en' in subtitles:
                    logger.info("✅ Found manual subtitles")
                    subtitle_text = await self._download_and_parse_subtitles(subtitles['en'][0]['url'])
                elif 'en' in automatic_captions:
                    logger.info("✅ Found auto-generated captions")
                    subtitle_text = await self._download_and_parse_subtitles(automatic_captions['en'][0]['url'])

                # If subtitles were fetched but are empty, fallback to audio transcription
                if subtitle_text:
                    return subtitle_text
                elif subtitle_text == "":
                    logger.warning("⚠️ Subtitle content empty, falling back to audio transcription")
                
        except Exception as e:
            logger.warning(f"⚠️ Subtitle extraction failed: {e}")
        
        # Try 2: Download audio and transcribe with Whisper
        logger.info("🔄 Downloading audio for transcription...")
        return await self._transcribe_audio(url)
    
    async def _download_and_parse_subtitles(self, subtitle_url: str) -> str:
        """Download and parse VTT/SRT subtitles"""
        import requests
        
        response = requests.get(subtitle_url, timeout=30)
        subtitle_text = response.text
        
        # Parse VTT/SRT and extract text
        lines = subtitle_text.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip timestamps, numbers, empty lines, headers
            if not line or '-->' in line or line.isdigit():
                continue
            if line.startswith('WEBVTT') or line.startswith('Kind:'):
                continue
            
            # Clean HTML tags
            line = re.sub(r'<[^>]+>', '', line)
            
            if line:
                text_lines.append(line)
        
        result = ' '.join(text_lines)
        logger.info(f"✅ Extracted {len(result)} chars from subtitles")
        return result
    
    async def _transcribe_audio(self, url: str) -> str:
        """Download audio and transcribe"""
        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp()
            audio_file = os.path.join(temp_dir, 'audio.mp3')
            
            # Download audio
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': audio_file.replace('.mp3', ''),
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            from app.services.stt_service import stt_service
            result = await stt_service.transcribe(audio_file + '.mp3')
            
            text = result.get("text", "")
            
            # FIX: If transcription empty, use video info
            if not text or text.strip() == "" or "unavailable" in text.lower():
                logger.warning("⚠️ Transcription empty, using video info")
                info = await self.get_video_info(url)
                title = info.get("title", "YouTube Video")
                desc = info.get("description", "")
                text = f"YouTube Video: {title}\n\nDescription: {desc}"
            
            logger.info(f"✅ Final text length: {len(text)} chars")
            return text
            
        except Exception as e:
            logger.error(f"❌ Audio transcription failed: {e}")
            # Fallback to video info
            info = await self.get_video_info(url)
            title = info.get("title", "YouTube Video")
            desc = info.get("description", "No description available")
            return f"YouTube Video: {title}\n\n{desc}"

youtube_service = YouTubeService()
