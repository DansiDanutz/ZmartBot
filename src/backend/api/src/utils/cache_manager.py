#!/usr/bin/env python3
"""
Cache Manager
Centralized caching system for the ZmartBot platform
"""

import json
import time
import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import hashlib
import os

logger = logging.getLogger(__name__)

class CacheManager:
    """Centralized cache manager for ZmartBot"""
    
    def __init__(self, cache_dir: str = "unified_cache", default_ttl: int = 3600):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self._ensure_cache_dir()
        logger.info(f"Cache Manager initialized: {cache_dir}")
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_path(self, key: str) -> str:
        """Get cache file path for a key"""
        # Create a safe filename from the key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.cache")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with TTL"""
        try:
            ttl = ttl or self.default_ttl
            expiry = time.time() + ttl
            
            cache_data = {
                'value': value,
                'expiry': expiry,
                'created': time.time(),
                'key': key
            }
            
            cache_path = self._get_cache_path(key)
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, default=str)
            
            return True
        except Exception as e:
            logger.error(f"Error setting cache for {key}: {str(e)}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        try:
            cache_path = self._get_cache_path(key)
            
            if not os.path.exists(cache_path):
                return None
            
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Check if expired
            if time.time() > cache_data['expiry']:
                self.delete(key)
                return None
            
            return cache_data['value']
        except Exception as e:
            logger.error(f"Error getting cache for {key}: {str(e)}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache"""
        try:
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache for {key}: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists and is not expired"""
        return self.get(key) is not None
    
    def clear_expired(self) -> int:
        """Clear all expired cache entries"""
        cleared = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    cache_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(cache_path, 'r') as f:
                            cache_data = json.load(f)
                        
                        if time.time() > cache_data['expiry']:
                            os.remove(cache_path)
                            cleared += 1
                    except:
                        # If we can't read the file, remove it
                        os.remove(cache_path)
                        cleared += 1
        except Exception as e:
            logger.error(f"Error clearing expired cache: {str(e)}")
        
        return cleared
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            total_files = 0
            total_size = 0
            expired_count = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    cache_path = os.path.join(self.cache_dir, filename)
                    total_files += 1
                    total_size += os.path.getsize(cache_path)
                    
                    try:
                        with open(cache_path, 'r') as f:
                            cache_data = json.load(f)
                        
                        if time.time() > cache_data['expiry']:
                            expired_count += 1
                    except:
                        expired_count += 1
            
            return {
                'total_entries': total_files,
                'total_size_bytes': total_size,
                'expired_entries': expired_count,
                'active_entries': total_files - expired_count,
                'cache_directory': self.cache_dir
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}

# Global cache manager instance
_global_cache = None

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache