import redis.asyncio as redis
from typing import Optional, Any
import json
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    """
    Redis client wrapper for caching and pub/sub
    """
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis.ping()
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis disconnected")
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """
        Set value in Redis
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON encoded if dict/list)
            expire: Optional expiration time in seconds
        
        Returns:
            True if successful
        """
        try:
            # Serialize complex objects to JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.redis.set(key, value, ex=expire or settings.CACHE_TTL_SECONDS)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get and deserialize JSON value from Redis"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def increment(self, key: str) -> int:
        """Increment a counter"""
        try:
            return await self.redis.incr(key)
        except Exception as e:
            logger.error(f"Redis INCR error for key {key}: {e}")
            return 0
    
    async def rate_limit(
        self, 
        identifier: str, 
        max_requests: int, 
        window_seconds: int
    ) -> bool:
        """
        Check rate limit using sliding window
        
        Args:
            identifier: Unique identifier (e.g., user_id, IP)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        key = f"rate_limit:{identifier}"
        
        try:
            current = await self.redis.incr(key)
            
            if current == 1:
                # First request, set expiration
                await self.redis.expire(key, window_seconds)
            
            return current <= max_requests
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # On error, allow the request (fail open)
            return True

# Global Redis client instance
redis_client = RedisClient()