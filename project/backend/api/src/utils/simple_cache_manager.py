"""
Simple Cache Manager - ZmartBot
Simplified high-performance caching using existing Redis client
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from functools import wraps

from src.utils.database import get_redis_client, redis_get, redis_set, redis_delete, redis_exists, redis_incr

logger = logging.getLogger(__name__)

class SimpleCacheManager:
    """
    Simple Cache Manager using existing Redis client
    """
    
    def __init__(self):
        self.default_ttl = 300  # 5 minutes default
        
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with automatic deserialization"""
        try:
            value = await redis_get(key)
            if value is None:
                return default
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                    
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with automatic serialization"""
        try:
            # Serialize value to JSON
            if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                serialized = json.dumps(value)
            else:
                serialized = str(value)
            
            # Set with TTL
            ttl = ttl or self.default_ttl
            return await redis_set(key, serialized, ttl)
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            result = await redis_delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return await redis_exists(key)
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment counter in cache"""
        try:
            return await redis_incr(key, amount)
        except Exception as e:
            logger.error(f"Cache incr error for key {key}: {e}")
            return 0
    
    async def warm_cache(self, symbols: List[str]):
        """Preload frequently accessed data for symbols"""
        logger.info(f"Warming cache for {len(symbols)} symbols")
        
        # Create tasks for parallel preloading
        tasks = []
        for symbol in symbols:
            tasks.extend([
                self._preload_symbol_data(symbol),
                self._preload_market_data(symbol),
                self._preload_ai_predictions(symbol)
            ])
        
        # Execute all tasks in parallel
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("Cache warming completed")
        except Exception as e:
            logger.error(f"Cache warming error: {e}")
    
    async def _preload_symbol_data(self, symbol: str):
        """Preload symbol-specific data"""
        cache_key = f"symbol:{symbol}:data"
        await self.set(cache_key, {"symbol": symbol, "status": "active"}, ttl=3600)
    
    async def _preload_market_data(self, symbol: str):
        """Preload market data for symbol"""
        cache_key = f"market:{symbol}:data"
        await self.set(cache_key, {"symbol": symbol, "price": 0, "volume": 0}, ttl=60)
    
    async def _preload_ai_predictions(self, symbol: str):
        """Preload AI predictions for symbol"""
        cache_key = f"ai:{symbol}:predictions"
        await self.set(cache_key, {"symbol": symbol, "win_rate": 0, "confidence": 0}, ttl=300)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            client = await get_redis_client()
            info = await client.info()
            return {
                "status": "available",
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"status": "error", "error": str(e)}

# Global cache manager instance
cache_manager = SimpleCacheManager()

# Cache decorator for functions
def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

# Initialize cache manager
async def init_cache():
    """Initialize the cache manager"""
    logger.info("Simple cache manager initialized")

# Close cache manager
async def close_cache():
    """Close the cache manager"""
    logger.info("Simple cache manager closed") 