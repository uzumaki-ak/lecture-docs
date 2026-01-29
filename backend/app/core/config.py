import http
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses pydantic for validation and type safety.
    """
    
    # App Info
    APP_NAME: str = "LectureDocs"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Chroma Vector DB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    VECTOR_DB: str = "chroma"  # Options: chroma, qdrant
    
    # Application Mode
    MODE: str = "local"  # Options: local, cloud
    PRIVACY_MODE: Optional[str] = None
    DEV_AUTH: bool = True
    LOG_LEVEL: str = "info"
    
    # LLM Providers (with fallback chain)
    LLM_PROVIDER: str = "euron"
    LOCAL_LLM_URL: str = "http://localhost:11434"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    EURON_API_KEY: Optional[str] = None
    EURON_BASE_URL: str = "https://api.euron.one/api/v1/euri"
    EURON_CHAT_MODEL: str = "gpt-4.1-nano"
    EURON_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-haiku-20241022"
    
    # Multiple API keys for fallback/load balancing
    GEMINI_API_KEY_2: Optional[str] = None
    GEMINI_API_KEY_3: Optional[str] = None
    EURON_API_KEY_2: Optional[str] = None
    EURON_API_KEY_3: Optional[str] = None
    OPENAI_API_KEY_2: Optional[str] = None
    
    # Local LLM
    LOCAL_LLM_PATH: Optional[str] = "/app/models/llama-3.2-3b-instruct.gguf"
    LOCAL_LLM_URL: str = "http://localhost:11434"
    USE_LOCAL_LLM: bool = True
    
    # Embeddings
    EMBEDDINGS_PROVIDER: str = "sentence-transformers"
    EMBEDDING_MODEL: str = "paraphrase-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # OCR Configuration
    OCR_PROVIDER: str = "tesseract"  # Options: tesseract, trocr, paddle
    TROCR_MODEL: str = "microsoft/trocr-base-handwritten"
    USE_GPU: bool = False
    TESSERACT_LANG: str = "eng"
    
    # Speech-to-Text
    STT_PROVIDER: str = "whisper"
    WHISPER_MODEL: str = "base"
    WHISPER_DEVICE: str = "cpu"
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 50
    MAX_FILE_COUNT: int = 20
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,pdf,mp3,mp4,wav,m4a,zip,py,js,ts,sol,md,txt"
    
    # Rate Limiting
    RATE_LIMIT_UPLOADS_PER_HOUR: int = 10
    RATE_LIMIT_CHAT_PER_MINUTE: int = 20
    RATE_LIMIT_ENABLED: bool = True
    
    # Job Queue
    WORKER_CONCURRENCY: int = 2
    JOB_TIMEOUT_SECONDS: int = 600
    RETRY_ATTEMPTS: int = 3
    
    # Auth
    CLERK_SECRET_KEY: Optional[str] = None
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    JWT_SECRET: str = "change-this-to-a-random-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # Chunking
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MIN_CHUNK_SIZE: int = 100
    PRESERVE_CODE_BLOCKS: bool = True
    
    # RAG
    RAG_TOP_K: int = 10
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    CONTEXT_WINDOW: int = 8000
    MAX_CHAT_HISTORY: int = 10
    
    # Storage
    UPLOAD_DIR: str = "/app/uploads"
    MODELS_DIR: str = "/app/models"
    TEMP_DIR: str = "/tmp/lecture-docs"
    
    # Scaling
    WORKERS: int = 4
    KEEP_ALIVE: int = 65
    MAX_CONNECTIONS: int = 1000
    BACKLOG: int = 2048
    
    # Cache
    REDIS_MAX_MEMORY: str = "512mb"
    CACHE_TTL_SECONDS: int = 3600
    ENABLE_RESULT_CACHE: bool = True
    
    # Features
    ENABLE_YOUTUBE_UPLOAD: bool = True
    ENABLE_AUDIO_UPLOAD: bool = True
    ENABLE_VIDEO_UPLOAD: bool = True
    ENABLE_ZIP_UPLOAD: bool = True
    ENABLE_GITHUB_SYNC: bool = True
    ENABLE_EXPORT_PDF: bool = False
    
    # Documentation Generation
    GENERATE_EXAMPLES: bool = True
    GENERATE_MERMAID: bool = True
    CHILD_FRIENDLY_MODE: bool = True
    INCLUDE_TODOS: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_allowed_extensions(self) -> List[str]:
        """Get list of allowed file extensions"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(',')]
    
    def get_gemini_keys(self) -> List[str]:
        """Get all available Gemini API keys"""
        keys = []
        if self.GEMINI_API_KEY:
            keys.append(self.GEMINI_API_KEY)
        if self.GEMINI_API_KEY_2:
            keys.append(self.GEMINI_API_KEY_2)
        if self.GEMINI_API_KEY_3:
            keys.append(self.GEMINI_API_KEY_3)
        return keys
    
    def get_euron_keys(self) -> List[str]:
        """Get all available Euron API keys"""
        keys = []
        if self.EURON_API_KEY:
            keys.append(self.EURON_API_KEY)
        if self.EURON_API_KEY_2:
            keys.append(self.EURON_API_KEY_2)
        if self.EURON_API_KEY_3:
            keys.append(self.EURON_API_KEY_3)
        return keys
    
    def get_openai_keys(self) -> List[str]:
        """Get all available OpenAI API keys"""
        keys = []
        if self.OPENAI_API_KEY:
            keys.append(self.OPENAI_API_KEY)
        if self.OPENAI_API_KEY_2:
            keys.append(self.OPENAI_API_KEY_2)
        return keys

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    This ensures we only load environment variables once.
    """
    return Settings()

settings = get_settings()