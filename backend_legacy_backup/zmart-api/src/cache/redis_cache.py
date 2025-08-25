"""
Redis Caching Layer
Provides intelligent caching for Enhanced Alerts System
"""

import redis
import json
import pickle
import os
from typing import Any, Optional, Dict, List, Union, Iterable
from datetime import datetime, timedelta
import logging
import hashlib

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis caching manager with intelligent invalidation"""
    
    def __init__(self):
        self.redis_client = None
        self.connect()
        
    def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=int(os.getenv("REDIS_CACHE_DB", "0")),
                decode_responses=False,  # For binary data
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis cache connection established")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis cache not available: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self.redis_client is not None
    
    def _serialize_key(self, key: str) -> str:
        """Create standardized cache key"""
        return f"alerts_cache:{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for Redis storage"""
        if isinstance(value, (dict, list)):
            return json.dumps(value, default=str).encode('utf-8')
        elif isinstance(value, (str, int, float, bool)):
            return json.dumps(value).encode('utf-8')
        else:
            return pickle.dumps(value)
    
    def _deserialize_value(self, value: bytes) -> Any:
        """Deserialize value from Redis"""
        try:
            # Try JSON first (most common)
            return json.loads(value.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            try:
                return pickle.loads(value)
            except Exception:
                return value.decode('utf-8') if isinstance(value, bytes) else value
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.is_available():
            return None
            
        try:
            cache_key = self._serialize_key(key)
            cached_value = self.redis_client.get(cache_key) if self.redis_client else None
            
            if cached_value is not None:
                # Ensure we have bytes for deserialization
                if isinstance(cached_value, str):
                    cached_value = cached_value.encode('utf-8')
                elif not isinstance(cached_value, bytes):
                    # Handle Redis response types safely
                    cached_value = str(cached_value).encode('utf-8')
                return self._deserialize_value(cached_value)
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL (default 5 minutes)"""
        if not self.is_available():
            return False
            
        try:
            cache_key = self._serialize_key(key)
            serialized_value = self._serialize_value(value)
            
            result = self.redis_client.setex(cache_key, ttl, serialized_value) if self.redis_client else False
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.is_available():
            return False
            
        try:
            cache_key = self._serialize_key(key)
            if self.redis_client:
                self.redis_client.delete(cache_key)
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.is_available():
            return 0
            
        try:
            cache_pattern = self._serialize_key(pattern)
            keys = self.redis_client.keys(cache_pattern) if self.redis_client else []
            if keys and self.redis_client:
                # Ensure keys is a proper list for unpacking
                if hasattr(keys, '__iter__') and not hasattr(keys, '__await__'):
                    try:
                        # Type-safe conversion: ensure keys is iterable before converting to list
                        if hasattr(keys, '__iter__') and not hasattr(keys, '__await__'):
                            # Cast to Iterable to satisfy type checker
                            keys_iterable: Iterable = keys  # type: ignore
                            keys_list = list(keys_iterable) if not isinstance(keys, list) else keys
                        else:
                            # If it's not iterable or is awaitable, return 0
                            return 0
                    except (TypeError, ValueError):
                        return 0
                    if keys_list:
                        result = self.redis_client.delete(*keys_list)
                        return int(str(result)) if result is not None else 0
                return 0
            return 0
            
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    def get_or_set(self, key: str, callable_func, ttl: int = 300) -> Any:
        """Get from cache or set if not exists"""
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Generate new value
        new_value = callable_func()
        self.set(key, new_value, ttl)
        return new_value
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache"""
        if not self.is_available():
            return None
            
        try:
            cache_key = self._serialize_key(key)
            result = self.redis_client.incrby(cache_key, amount) if self.redis_client else None
            # Handle Redis response type safely
            if result is not None:
                try:
                    return int(str(result))
                except (ValueError, TypeError):
                    return None
            return None
            
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    def set_hash(self, key: str, mapping: Dict[str, Any], ttl: int = 300) -> bool:
        """Set hash in Redis"""
        if not self.is_available():
            return False
            
        try:
            cache_key = self._serialize_key(key)
            
            # Serialize all values in the mapping
            serialized_mapping = {}
            for k, v in mapping.items():
                serialized_mapping[k] = self._serialize_value(v)
            
            if self.redis_client:
                self.redis_client.hset(cache_key, mapping=serialized_mapping)
                self.redis_client.expire(cache_key, ttl)
            return True
            
        except Exception as e:
            logger.error(f"Cache set hash error for key {key}: {e}")
            return False
    
    def get_hash(self, key: str) -> Optional[Dict[str, Any]]:
        """Get hash from Redis"""
        if not self.is_available():
            return None
            
        try:
            cache_key = self._serialize_key(key)
            hash_data = self.redis_client.hgetall(cache_key) if self.redis_client else None
            
            if hash_data:
                # Handle Redis response types safely
                result = {}
                
                # Check if it's an awaitable object first
                if hasattr(hash_data, '__await__'):
                    # This is an awaitable, we can't use it directly
                    return None
                
                # Type guard: ensure we have a synchronous dict-like object
                items = None
                if isinstance(hash_data, dict):
                    items = hash_data.items()
                else:
                    # For non-dict Redis responses, try to safely convert
                    try:
                        # Only try if it looks like a dict and is not awaitable
                        if (hasattr(hash_data, 'items') and 
                            callable(getattr(hash_data, 'items', None))):
                            items_method = getattr(hash_data, 'items')
                            items = items_method()
                    except Exception:
                        return None
                
                if items is None:
                    return None
                
                for k, v in items:
                    # Handle key conversion
                    if isinstance(k, bytes):
                        k = k.decode('utf-8')
                    elif not isinstance(k, str):
                        k = str(k)
                    
                    # Handle value conversion
                    if isinstance(v, str):
                        v = v.encode('utf-8')
                    elif not isinstance(v, bytes):
                        v = str(v).encode('utf-8')
                    
                    result[k] = self._deserialize_value(v)
                return result
            return None
            
        except Exception as e:
            logger.error(f"Cache get hash error for key {key}: {e}")
            return None

# Cache instance
cache = RedisCache()

# Cache decorators and utilities
def cache_key_for_symbol(symbol: str, data_type: str = "price") -> str:
    """Generate standardized cache key for symbol data"""
    return f"symbol:{symbol}:{data_type}"

def cache_key_for_technical_analysis(symbol: str, timeframe: str = "1h") -> str:
    """Generate cache key for technical analysis"""
    return f"technical:{symbol}:{timeframe}"

def cache_key_for_alerts(user_id: str = "system") -> str:
    """Generate cache key for alerts"""
    return f"alerts:{user_id}"

def invalidate_symbol_cache(symbol: str):
    """Invalidate all cache entries for a symbol"""
    patterns = [
        f"symbol:{symbol}:*",
        f"technical:{symbol}:*",
        f"alerts:*:{symbol}:*"
    ]
    
    for pattern in patterns:
        cache.delete_pattern(pattern)

# Market data caching
class MarketDataCache:
    """Specialized caching for market data"""
    
    @staticmethod
    def get_price_data(symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached price data for symbol"""
        key = cache_key_for_symbol(symbol, "price")
        return cache.get(key)
    
    @staticmethod
    def set_price_data(symbol: str, price_data: Dict[str, Any], ttl: int = 60):
        """Cache price data for symbol (1 minute default)"""
        key = cache_key_for_symbol(symbol, "price")
        return cache.set(key, price_data, ttl)
    
    @staticmethod
    def get_technical_analysis(symbol: str, timeframe: str = "1h") -> Optional[Dict[str, Any]]:
        """Get cached technical analysis"""
        key = cache_key_for_technical_analysis(symbol, timeframe)
        return cache.get(key)
    
    @staticmethod
    def set_technical_analysis(symbol: str, analysis_data: Dict[str, Any], 
                             timeframe: str = "1h", ttl: int = 300):
        """Cache technical analysis (5 minutes default)"""
        key = cache_key_for_technical_analysis(symbol, timeframe)
        return cache.set(key, analysis_data, ttl)
    
    @staticmethod
    def get_volume_data(symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached volume data"""
        key = cache_key_for_symbol(symbol, "volume")
        return cache.get(key)
    
    @staticmethod
    def set_volume_data(symbol: str, volume_data: Dict[str, Any], ttl: int = 120):
        """Cache volume data (2 minutes default)"""
        key = cache_key_for_symbol(symbol, "volume")
        return cache.set(key, volume_data, ttl)

# Alerts caching
class AlertsCache:
    """Specialized caching for alerts"""
    
    @staticmethod
    def get_user_alerts(user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached user alerts"""
        key = cache_key_for_alerts(user_id)
        return cache.get(key)
    
    @staticmethod
    def set_user_alerts(user_id: str, alerts: List[Dict[str, Any]], ttl: int = 300):
        """Cache user alerts (5 minutes default)"""
        key = cache_key_for_alerts(user_id)
        return cache.set(key, alerts, ttl)
    
    @staticmethod
    def invalidate_user_alerts(user_id: str):
        """Invalidate user alerts cache"""
        key = cache_key_for_alerts(user_id)
        cache.delete(key)
    
    @staticmethod
    def get_system_status() -> Optional[Dict[str, Any]]:
        """Get cached system status"""
        return cache.get("system:status")
    
    @staticmethod
    def set_system_status(status: Dict[str, Any], ttl: int = 60):
        """Cache system status (1 minute default)"""
        return cache.set("system:status", status, ttl)

# Export instances
market_cache = MarketDataCache()
alerts_cache = AlertsCache()