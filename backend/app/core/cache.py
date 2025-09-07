"""
Redis cache configuration and utilities.
"""
import redis.asyncio as redis
import pickle
import json
from typing import Any, Optional, Union
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Redis client instance
redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get Redis client instance."""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            await redis_client.ping()
            logger.info("Redis client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            redis_client = None
    return redis_client


async def cache_set(
    key: str, 
    value: Any, 
    ttl: int = None,
    serialize: str = "json"
) -> bool:
    """
    Set value in cache.
    
    Args:
        key: Cache key
        value: Value to cache
        ttl: Time to live in seconds
        serialize: Serialization method ('json' or 'pickle')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = await get_redis_client()
        if client is None:
            return False
            
        if serialize == "json":
            serialized_value = json.dumps(value)
        else:
            serialized_value = pickle.dumps(value)
        
        ttl = ttl or settings.CACHE_TTL
        await client.setex(key, ttl, serialized_value)
        return True
        
    except Exception as e:
        logger.error(f"Cache set error for key {key}: {e}")
        return False


async def cache_get(
    key: str, 
    serialize: str = "json"
) -> Optional[Any]:
    """
    Get value from cache.
    
    Args:
        key: Cache key
        serialize: Serialization method ('json' or 'pickle')
    
    Returns:
        Cached value or None if not found
    """
    try:
        client = await get_redis_client()
        if client is None:
            return None
            
        cached_value = await client.get(key)
        if cached_value is None:
            return None
            
        if serialize == "json":
            return json.loads(cached_value)
        else:
            return pickle.loads(cached_value)
            
    except Exception as e:
        logger.error(f"Cache get error for key {key}: {e}")
        return None


async def cache_delete(key: str) -> bool:
    """
    Delete value from cache.
    
    Args:
        key: Cache key
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = await get_redis_client()
        if client is None:
            return False
            
        await client.delete(key)
        return True
        
    except Exception as e:
        logger.error(f"Cache delete error for key {key}: {e}")
        return False


async def cache_exists(key: str) -> bool:
    """
    Check if key exists in cache.
    
    Args:
        key: Cache key
    
    Returns:
        bool: True if key exists, False otherwise
    """
    try:
        client = await get_redis_client()
        if client is None:
            return False
            
        return await client.exists(key) > 0
        
    except Exception as e:
        logger.error(f"Cache exists error for key {key}: {e}")
        return False


async def cache_flush() -> bool:
    """
    Flush all cache.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = await get_redis_client()
        if client is None:
            return False
            
        await client.flushdb()
        return True
        
    except Exception as e:
        logger.error(f"Cache flush error: {e}")
        return False
