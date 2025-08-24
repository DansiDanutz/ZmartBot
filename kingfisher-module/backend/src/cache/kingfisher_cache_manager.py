#!/usr/bin/env python3
"""
KingFisher Intelligent Cache Manager
Provides caching for image analysis to avoid repeated processing
Implements smart TTL and update strategies to prevent API limitations
"""

import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import pickle
import aiofiles
import os
from enum import Enum

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """Cache priority levels"""
    HOT = "hot"        # Frequently accessed, short TTL (5 mins)
    WARM = "warm"      # Regular access, medium TTL (15 mins)
    COLD = "cold"      # Infrequent access, long TTL (1 hour)
    FROZEN = "frozen"  # Rarely changes, very long TTL (6 hours)

class KingFisherCacheManager:
    """
    Intelligent cache manager for KingFisher module
    Supports both Redis and local file caching
    """
    
    def __init__(self, redis_url: Optional[str] = None, cache_dir: str = "cache/kingfisher"):
        """
        Initialize cache manager
        
        Args:
            redis_url: Optional Redis connection URL
            cache_dir: Directory for file-based cache
        """
        self.redis_client = None
        self.redis_url = redis_url or os.getenv('REDIS_URL')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # TTL configurations (in seconds)
        self.ttl_config = {
            CacheLevel.HOT: 300,      # 5 minutes
            CacheLevel.WARM: 900,     # 15 minutes
            CacheLevel.COLD: 3600,    # 1 hour
            CacheLevel.FROZEN: 21600  # 6 hours
        }
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'updates': 0,
            'evictions': 0
        }
        
        # Update scheduler tracking
        self.update_schedule = {}
        self.last_api_call = {}
        
        # Rate limiting configuration
        self.rate_limits = {
            'image_analysis': {'calls': 10, 'period': 60},  # 10 calls per minute
            'airtable_update': {'calls': 5, 'period': 10},  # 5 calls per 10 seconds
            'telegram_send': {'calls': 30, 'period': 60}    # 30 calls per minute
        }
        
        logger.info("KingFisher Cache Manager initialized")
    
    async def connect(self):
        """Connect to Redis if available"""
        if redis and self.redis_url:
            try:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=False
                )
                await self.redis_client.ping()
                logger.info("Connected to Redis cache")
            except Exception as e:
                logger.warning(f"Redis connection failed, using file cache: {e}")
                self.redis_client = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _generate_cache_key(self, module: str, symbol: str, data_type: str, 
                          params: Optional[Dict] = None) -> str:
        """Generate unique cache key"""
        key_parts = ["kingfisher", module, symbol, data_type]
        
        if params:
            # Sort params for consistent key generation
            sorted_params = sorted(params.items())
            param_str = "_".join([f"{k}:{v}" for k, v in sorted_params])
            key_parts.append(hashlib.md5(param_str.encode()).hexdigest()[:8])
        
        return ":".join(key_parts)
    
    def _determine_cache_level(self, data_type: str, symbol: str) -> CacheLevel:
        """Determine appropriate cache level based on data type"""
        # High-frequency data gets shorter TTL
        if data_type in ['liquidation_map', 'rapid_movements']:
            return CacheLevel.HOT
        # Medium frequency data
        elif data_type in ['rsi_heatmap', 'liq_heatmap']:
            return CacheLevel.WARM
        # Low frequency data
        elif data_type in ['liq_ratio_longterm', 'support_resistance']:
            return CacheLevel.COLD
        # Very stable data
        elif data_type in ['professional_report', 'historical_analysis']:
            return CacheLevel.FROZEN
        else:
            return CacheLevel.WARM
    
    async def get(self, module: str, symbol: str, data_type: str, 
                  params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Get data from cache
        
        Args:
            module: Module name (e.g., 'image_analysis')
            symbol: Trading symbol
            data_type: Type of data
            params: Optional parameters
            
        Returns:
            Cached data if available and valid, None otherwise
        """
        cache_key = self._generate_cache_key(module, symbol, data_type, params)
        
        # Try Redis first
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    
                    # Check if data is still valid
                    if self._is_cache_valid(data):
                        self.stats['hits'] += 1
                        logger.debug(f"Cache hit for {cache_key}")
                        return data['value']
                    else:
                        # Data expired, remove it
                        await self.redis_client.delete(cache_key)
                        self.stats['evictions'] += 1
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        # Fallback to file cache
        cache_file = self.cache_dir / f"{cache_key.replace(':', '_')}.pkl"
        if cache_file.exists():
            try:
                async with aiofiles.open(cache_file, 'rb') as f:
                    content = await f.read()
                    data = pickle.loads(content)
                    
                    if self._is_cache_valid(data):
                        self.stats['hits'] += 1
                        logger.debug(f"File cache hit for {cache_key}")
                        return data['value']
                    else:
                        # Data expired, remove it
                        cache_file.unlink()
                        self.stats['evictions'] += 1
            except Exception as e:
                logger.error(f"File cache read error: {e}")
        
        self.stats['misses'] += 1
        logger.debug(f"Cache miss for {cache_key}")
        return None
    
    async def set(self, module: str, symbol: str, data_type: str, 
                  value: Any, params: Optional[Dict] = None, 
                  cache_level: Optional[CacheLevel] = None) -> bool:
        """
        Store data in cache
        
        Args:
            module: Module name
            symbol: Trading symbol
            data_type: Type of data
            value: Data to cache
            params: Optional parameters
            cache_level: Optional cache level override
            
        Returns:
            True if successful
        """
        cache_key = self._generate_cache_key(module, symbol, data_type, params)
        
        # Determine cache level if not provided
        if cache_level is None:
            cache_level = self._determine_cache_level(data_type, symbol)
        
        ttl = self.ttl_config[cache_level]
        expiry = datetime.now() + timedelta(seconds=ttl)
        
        cache_data = {
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'expiry': expiry.isoformat(),
            'cache_level': cache_level.value,
            'symbol': symbol,
            'data_type': data_type
        }
        
        # Store in Redis if available
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(cache_data, default=str)
                )
                logger.debug(f"Cached to Redis: {cache_key} (TTL: {ttl}s)")
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        
        # Also store in file cache as backup
        cache_file = self.cache_dir / f"{cache_key.replace(':', '_')}.pkl"
        try:
            async with aiofiles.open(cache_file, 'wb') as f:
                await f.write(pickle.dumps(cache_data))
            logger.debug(f"Cached to file: {cache_key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"File cache write error: {e}")
            return False
        
        self.stats['updates'] += 1
        return True
    
    def _is_cache_valid(self, cache_data: Dict) -> bool:
        """Check if cached data is still valid"""
        if 'expiry' not in cache_data:
            return False
        
        expiry = datetime.fromisoformat(cache_data['expiry'])
        return datetime.now() < expiry
    
    async def invalidate(self, module: str, symbol: Optional[str] = None, 
                         data_type: Optional[str] = None):
        """
        Invalidate cache entries
        
        Args:
            module: Module name
            symbol: Optional symbol filter
            data_type: Optional data type filter
        """
        pattern = f"kingfisher:{module}"
        if symbol:
            pattern += f":{symbol}"
        if data_type:
            pattern += f":{data_type}"
        pattern += "*"
        
        # Clear from Redis
        if self.redis_client:
            try:
                cursor = 0
                while True:
                    cursor, keys = await self.redis_client.scan(
                        cursor, match=pattern, count=100
                    )
                    if keys:
                        await self.redis_client.delete(*keys)
                        self.stats['evictions'] += len(keys)
                    if cursor == 0:
                        break
            except Exception as e:
                logger.error(f"Redis invalidate error: {e}")
        
        # Clear from file cache
        pattern_file = pattern.replace(':', '_').replace('*', '')
        for cache_file in self.cache_dir.glob(f"{pattern_file}*.pkl"):
            try:
                cache_file.unlink()
                self.stats['evictions'] += 1
            except Exception as e:
                logger.error(f"File cache delete error: {e}")
    
    async def can_make_api_call(self, api_type: str, symbol: str) -> bool:
        """
        Check if we can make an API call without hitting rate limits
        
        Args:
            api_type: Type of API call
            symbol: Trading symbol
            
        Returns:
            True if API call is allowed
        """
        if api_type not in self.rate_limits:
            return True
        
        limit_config = self.rate_limits[api_type]
        key = f"{api_type}:{symbol}"
        
        now = datetime.now()
        if key in self.last_api_call:
            last_calls = self.last_api_call[key]
            
            # Remove calls outside the period window
            cutoff = now - timedelta(seconds=limit_config['period'])
            last_calls = [call_time for call_time in last_calls if call_time > cutoff]
            
            # Check if we've hit the limit
            if len(last_calls) >= limit_config['calls']:
                # Calculate wait time
                oldest_call = min(last_calls)
                wait_time = (oldest_call + timedelta(seconds=limit_config['period']) - now).total_seconds()
                
                if wait_time > 0:
                    logger.warning(f"Rate limit reached for {api_type}:{symbol}, wait {wait_time:.1f}s")
                    return False
            
            self.last_api_call[key] = last_calls
        else:
            self.last_api_call[key] = []
        
        # Record this call
        self.last_api_call[key].append(now)
        return True
    
    async def schedule_update(self, module: str, symbol: str, data_type: str, 
                            update_func, interval_minutes: int = 15):
        """
        Schedule periodic cache updates to keep data fresh
        
        Args:
            module: Module name
            symbol: Trading symbol
            data_type: Type of data
            update_func: Async function to call for updates
            interval_minutes: Update interval in minutes
        """
        key = f"{module}:{symbol}:{data_type}"
        
        if key in self.update_schedule:
            # Cancel existing schedule
            self.update_schedule[key]['task'].cancel()
        
        async def update_loop():
            while True:
                try:
                    # Wait for the interval
                    await asyncio.sleep(interval_minutes * 60)
                    
                    # Check if we can make the API call
                    if await self.can_make_api_call('image_analysis', symbol):
                        # Call the update function
                        result = await update_func(symbol)
                        
                        if result:
                            # Cache the new data
                            await self.set(module, symbol, data_type, result)
                            logger.info(f"Scheduled update completed for {key}")
                        else:
                            logger.warning(f"Scheduled update failed for {key}")
                    else:
                        logger.info(f"Skipping scheduled update for {key} due to rate limits")
                        # Try again in 1 minute
                        await asyncio.sleep(60)
                        
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in scheduled update for {key}: {e}")
                    await asyncio.sleep(60)  # Wait before retrying
        
        # Start the update task
        task = asyncio.create_task(update_loop())
        self.update_schedule[key] = {
            'task': task,
            'interval': interval_minutes,
            'started': datetime.now()
        }
        
        logger.info(f"Scheduled updates for {key} every {interval_minutes} minutes")
    
    async def get_or_fetch(self, module: str, symbol: str, data_type: str,
                          fetch_func, params: Optional[Dict] = None,
                          force_refresh: bool = False) -> Optional[Any]:
        """
        Get data from cache or fetch if not available
        
        Args:
            module: Module name
            symbol: Trading symbol
            data_type: Type of data
            fetch_func: Async function to fetch data if not cached
            params: Optional parameters
            force_refresh: Force fetch new data
            
        Returns:
            Data from cache or freshly fetched
        """
        # Check cache first unless force refresh
        if not force_refresh:
            cached_data = await self.get(module, symbol, data_type, params)
            if cached_data is not None:
                return cached_data
        
        # Check if we can make the API call
        if not await self.can_make_api_call('image_analysis', symbol):
            # If we can't make the call, return stale cache if available
            logger.warning(f"Rate limited, returning stale cache for {symbol}:{data_type}")
            return await self._get_stale_cache(module, symbol, data_type, params)
        
        # Fetch fresh data
        try:
            logger.info(f"Fetching fresh data for {symbol}:{data_type}")
            fresh_data = await fetch_func(symbol, **(params or {}))
            
            if fresh_data:
                # Cache the fresh data
                await self.set(module, symbol, data_type, fresh_data, params)
                return fresh_data
            else:
                logger.warning(f"Failed to fetch data for {symbol}:{data_type}")
                # Return stale cache as fallback
                return await self._get_stale_cache(module, symbol, data_type, params)
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}:{data_type}: {e}")
            # Return stale cache as fallback
            return await self._get_stale_cache(module, symbol, data_type, params)
    
    async def _get_stale_cache(self, module: str, symbol: str, data_type: str,
                              params: Optional[Dict] = None) -> Optional[Any]:
        """Get stale cache data (expired but still stored)"""
        cache_key = self._generate_cache_key(module, symbol, data_type, params)
        
        # Try file cache (doesn't check expiry)
        cache_file = self.cache_dir / f"{cache_key.replace(':', '_')}.pkl"
        if cache_file.exists():
            try:
                async with aiofiles.open(cache_file, 'rb') as f:
                    content = await f.read()
                    data = pickle.loads(content)
                    logger.info(f"Returning stale cache for {cache_key}")
                    return data.get('value')
            except Exception as e:
                logger.error(f"Error reading stale cache: {e}")
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'updates': self.stats['updates'],
            'evictions': self.stats['evictions'],
            'hit_rate': f"{hit_rate:.1f}%",
            'total_requests': total_requests,
            'active_schedules': len(self.update_schedule),
            'cache_directory': str(self.cache_dir),
            'redis_connected': self.redis_client is not None
        }
    
    async def cleanup_expired(self):
        """Clean up expired cache entries"""
        logger.info("Starting cache cleanup")
        cleaned = 0
        
        # Clean file cache
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                async with aiofiles.open(cache_file, 'rb') as f:
                    content = await f.read()
                    data = pickle.loads(content)
                    
                    if not self._is_cache_valid(data):
                        cache_file.unlink()
                        cleaned += 1
            except Exception as e:
                logger.error(f"Error cleaning cache file {cache_file}: {e}")
        
        logger.info(f"Cleaned {cleaned} expired cache entries")
        self.stats['evictions'] += cleaned
        return cleaned

# Create global instance
kingfisher_cache = KingFisherCacheManager()