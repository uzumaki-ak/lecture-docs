import logging
import sys
from pathlib import Path
from app.core.config import settings

def setup_logging():
    """
    Configure application-wide logging
    Creates both console and file handlers
    """
    
    # Create logs directory
    log_dir = Path("/app/logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(log_dir / "app.log", mode='a')
        ]
    )
    
    # Set levels for specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"✅ Logging configured at {settings.LOG_LEVEL.upper()} level")