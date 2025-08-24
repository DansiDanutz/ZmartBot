#!/usr/bin/env python3
"""
Cryptometer Intelligent Cache Manager
Provides caching for all 17 Cryptometer endpoints to avoid API limitations
Implements smart TTL, batch updates, and rate limit management
"""

import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
import logging
from pathlib import Path
import pickle
import os

try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    aiofiles = None
    AIOFILES_AVAILABLE = False
from enum import Enum
from collections import defaultdict
import heapq

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

logger = logging.getLogger(__name__)

class EndpointPriority(Enum):
    """Priority levels for different endpoints"""
    CRITICAL = 1     # Real-time critical data (ticker, rapid_movements)
    HIGH = 2         # Important frequently changing (ls_ratio, liquidation)
    MEDIUM = 3       # Regular updates (trend_indicator, ai_screener)
    LOW = 4          # Stable data (coin_info, forex_rates)

class CryptometerCacheManager:
    """
    Intelligent cache manager for Cryptometer module
    Manages caching for all 17 endpoints with rate limit awareness
    """
    
    def __init__(self, redis_url: Optional[str] = None, cache_dir: str = "cache/cryptometer"):
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
        
        # Endpoint configurations with TTL and priority
        self.endpoint_config = {
            # CRITICAL - Very short TTL (2-5 mins)
            'ticker': {'ttl': 120, 'priority': EndpointPriority.CRITICAL, 'weight': 8},
            'rapid_movements': {'ttl': 180, 'priority': EndpointPriority.CRITICAL, 'weight': 7},
            
            # HIGH - Short TTL (5-10 mins)
            'ls_ratio': {'ttl': 300, 'priority': EndpointPriority.HIGH, 'weight': 12},
            'liquidation_data_v2': {'ttl': 300, 'priority': EndpointPriority.HIGH, 'weight': 14},
            'open_interest': {'ttl': 600, 'priority': EndpointPriority.HIGH, 'weight': 9},
            
            # MEDIUM - Medium TTL (15-30 mins)
            'trend_indicator_v3': {'ttl': 900, 'priority': EndpointPriority.MEDIUM, 'weight': 15},
            'ai_screener': {'ttl': 1800, 'priority': EndpointPriority.MEDIUM, 'weight': 16},
            'ai_screener_analysis': {'ttl': 1800, 'priority': EndpointPriority.MEDIUM, 'weight': 18},
            'tickerlist': {'ttl': 900, 'priority': EndpointPriority.MEDIUM, 'weight': 5},
            'tickerlist_pro': {'ttl': 900, 'priority': EndpointPriority.MEDIUM, 'weight': 10},
            
            # LOW - Long TTL (1-6 hours)
            'coinlist': {'ttl': 21600, 'priority': EndpointPriority.LOW, 'weight': 2},
            'cryptocurrency_info': {'ttl': 3600, 'priority': EndpointPriority.LOW, 'weight': 6},
            'coin_info': {'ttl': 3600, 'priority': EndpointPriority.LOW, 'weight': 4},
            'forex_rates': {'ttl': 7200, 'priority': EndpointPriority.LOW, 'weight': 3}
        }
        
        # Rate limiting configuration (Cryptometer API limits)
        self.rate_limits = {
            'global': {'calls': 100, 'period': 60},         # 100 calls per minute global
            'per_endpoint': {'calls': 10, 'period': 60},    # 10 calls per endpoint per minute
            'burst': {'calls': 20, 'period': 10}            # 20 calls in 10 seconds burst
        }
        
        # API call tracking
        self.api_calls = defaultdict(list)  # Track calls per endpoint
        self.global_api_calls = []          # Track all API calls
        
        # Cache statistics
        self.stats = {
            'hits': defaultdict(int),
            'misses': defaultdict(int),
            'updates': defaultdict(int),
            'api_calls_saved': 0,
            'rate_limit_blocks': 0
        }
        
        # Update queue for batch processing
        self.update_queue = []  # Priority queue
        self.update_tasks = {}  # Active update tasks
        
        # Symbols being monitored
        self.monitored_symbols = set()
        
        logger.info("Cryptometer Cache Manager initialized")
    
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
    
    def _generate_cache_key(self, endpoint: str, symbol: str, 
                          params: Optional[Dict] = None) -> str:
        """Generate unique cache key for endpoint data"""
        key_parts = ["cryptometer", endpoint, symbol]
        
        if params:
            # Filter out API key from params
            filtered_params = {k: v for k, v in params.items() 
                             if k not in ['api_key', 'key', 'secret']}
            if filtered_params:
                sorted_params = sorted(filtered_params.items())
                param_str = "_".join([f"{k}:{v}" for k, v in sorted_params])
                key_parts.append(hashlib.md5(param_str.encode()).hexdigest()[:8])
        
        return ":".join(key_parts)
    
    async def get(self, endpoint: str, symbol: str, 
                  params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Get data from cache
        
        Args:
            endpoint: Endpoint name
            symbol: Trading symbol
            params: Optional parameters
            
        Returns:
            Cached data if available and valid
        """
        cache_key = self._generate_cache_key(endpoint, symbol, params)
        
        # Try Redis first
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    
                    if self._is_cache_valid(data):
                        self.stats['hits'][endpoint] += 1
                        self.stats['api_calls_saved'] += 1
                        logger.debug(f"Cache hit for {endpoint}:{symbol}")
                        return data['value']
                    else:
                        await self.redis_client.delete(cache_key)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        # Fallback to file cache
        cache_file = self.cache_dir / f"{cache_key.replace(':', '_')}.json"
        if cache_file.exists():
            try:
                if AIOFILES_AVAILABLE:
                    async with aiofiles.open(cache_file, 'r') as f:  # type: ignore
                        content = await f.read()  # type: ignore
                        data = json.loads(content)
                else:
                    with open(cache_file, 'r') as f:
                        content = f.read()
                        data = json.loads(content)
                    
                if self._is_cache_valid(data):
                    self.stats['hits'][endpoint] += 1
                    self.stats['api_calls_saved'] += 1
                    logger.debug(f"File cache hit for {endpoint}:{symbol}")
                    return data['value']
                else:
                    cache_file.unlink()
            except Exception as e:
                logger.error(f"File cache read error: {e}")
        
        self.stats['misses'][endpoint] += 1
        logger.debug(f"Cache miss for {endpoint}:{symbol}")
        return None
    
    async def set(self, endpoint: str, symbol: str, value: Any,
                  params: Optional[Dict] = None) -> bool:
        """
        Store data in cache with appropriate TTL
        
        Args:
            endpoint: Endpoint name
            symbol: Trading symbol
            value: Data to cache
            params: Optional parameters
            
        Returns:
            True if successful
        """
        cache_key = self._generate_cache_key(endpoint, symbol, params)
        
        # Get endpoint configuration
        config = self.endpoint_config.get(endpoint, 
                                         {'ttl': 900, 'priority': EndpointPriority.MEDIUM})
        ttl = config['ttl']
        
        expiry = datetime.now() + timedelta(seconds=ttl)
        
        cache_data = {
            'value': value,
            'endpoint': endpoint,
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'expiry': expiry.isoformat(),
            'ttl': ttl,
            'priority': config['priority'].value
        }
        
        # Store in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(cache_data, default=str)
                )
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        
        # Store in file cache
        cache_file = self.cache_dir / f"{cache_key.replace(':', '_')}.json"
        try:
            if AIOFILES_AVAILABLE:
                async with aiofiles.open(cache_file, 'w') as f:  # type: ignore
                    await f.write(json.dumps(cache_data, default=str, indent=2))  # type: ignore
            else:
                with open(cache_file, 'w') as f:
                    f.write(json.dumps(cache_data, default=str, indent=2))
        except Exception as e:
            logger.error(f"File cache write error: {e}")
            return False
        
        self.stats['updates'][endpoint] += 1
        
        # Add symbol to monitored set
        self.monitored_symbols.add(symbol)
        
        logger.debug(f"Cached {endpoint}:{symbol} with TTL {ttl}s")
        return True
    
    def _is_cache_valid(self, cache_data: Dict) -> bool:
        """Check if cached data is still valid"""
        if 'expiry' not in cache_data:
            return False
        
        expiry = datetime.fromisoformat(cache_data['expiry'])
        return datetime.now() < expiry
    
    async def can_make_api_call(self, endpoint: str) -> Tuple[bool, float]:
        """
        Check if we can make an API call without hitting rate limits
        
        Args:
            endpoint: Endpoint name
            
        Returns:
            Tuple of (can_call, wait_time_seconds)
        """
        now = datetime.now()
        
        # Check global rate limit
        global_limit = self.rate_limits['global']
        cutoff = now - timedelta(seconds=global_limit['period'])
        self.global_api_calls = [t for t in self.global_api_calls if t > cutoff]
        
        if len(self.global_api_calls) >= global_limit['calls']:
            wait_time = (min(self.global_api_calls) + 
                        timedelta(seconds=global_limit['period']) - now).total_seconds()
            if wait_time > 0:
                logger.warning(f"Global rate limit reached, wait {wait_time:.1f}s")
                self.stats['rate_limit_blocks'] += 1
                return False, wait_time
        
        # Check per-endpoint rate limit
        endpoint_limit = self.rate_limits['per_endpoint']
        endpoint_calls = self.api_calls[endpoint]
        cutoff = now - timedelta(seconds=endpoint_limit['period'])
        endpoint_calls = [t for t in endpoint_calls if t > cutoff]
        self.api_calls[endpoint] = endpoint_calls
        
        if len(endpoint_calls) >= endpoint_limit['calls']:
            wait_time = (min(endpoint_calls) + 
                        timedelta(seconds=endpoint_limit['period']) - now).total_seconds()
            if wait_time > 0:
                logger.warning(f"Endpoint {endpoint} rate limit reached, wait {wait_time:.1f}s")
                self.stats['rate_limit_blocks'] += 1
                return False, wait_time
        
        # Check burst limit
        burst_limit = self.rate_limits['burst']
        burst_cutoff = now - timedelta(seconds=burst_limit['period'])
        recent_calls = [t for t in self.global_api_calls if t > burst_cutoff]
        
        if len(recent_calls) >= burst_limit['calls']:
            wait_time = (min(recent_calls) + 
                        timedelta(seconds=burst_limit['period']) - now).total_seconds()
            if wait_time > 0:
                logger.warning(f"Burst limit reached, wait {wait_time:.1f}s")
                self.stats['rate_limit_blocks'] += 1
                return False, wait_time
        
        return True, 0
    
    def record_api_call(self, endpoint: str):
        """Record that an API call was made"""
        now = datetime.now()
        self.api_calls[endpoint].append(now)
        self.global_api_calls.append(now)
    
    async def get_or_fetch(self, endpoint: str, symbol: str, fetch_func,
                          params: Optional[Dict] = None,
                          force_refresh: bool = False) -> Optional[Any]:
        """
        Get data from cache or fetch if not available
        
        Args:
            endpoint: Endpoint name
            symbol: Trading symbol
            fetch_func: Async function to fetch data
            params: Optional parameters
            force_refresh: Force fetch new data
            
        Returns:
            Data from cache or freshly fetched
        """
        # Check cache first
        if not force_refresh:
            cached_data = await self.get(endpoint, symbol, params)
            if cached_data is not None:
                return cached_data
        
        # Check rate limits
        can_call, wait_time = await self.can_make_api_call(endpoint)
        
        if not can_call:
            # Return stale cache if available
            logger.info(f"Rate limited for {endpoint}, returning stale cache")
            stale_data = await self._get_stale_cache(endpoint, symbol, params)
            if stale_data:
                return stale_data
            
            # If no stale cache, wait and retry
            if wait_time > 0 and wait_time < 10:
                await asyncio.sleep(wait_time)
                can_call, _ = await self.can_make_api_call(endpoint)
            
            if not can_call:
                return None
        
        # Make the API call
        try:
            logger.info(f"Fetching fresh data for {endpoint}:{symbol}")
            self.record_api_call(endpoint)
            
            fresh_data = await fetch_func()
            
            if fresh_data:
                # Cache the fresh data
                await self.set(endpoint, symbol, fresh_data, params)
                return fresh_data
            else:
                # Return stale cache as fallback
                return await self._get_stale_cache(endpoint, symbol, params)
                
        except Exception as e:
            logger.error(f"Error fetching {endpoint}:{symbol}: {e}")
            # Return stale cache as fallback
            return await self._get_stale_cache(endpoint, symbol, params)
    
    async def _get_stale_cache(self, endpoint: str, symbol: str,
                              params: Optional[Dict] = None) -> Optional[Any]:
        """Get stale cache data (expired but still available)"""
        cache_key = self._generate_cache_key(endpoint, symbol, params)
        cache_file = self.cache_dir / f"{cache_key.replace(':', '_')}.json"
        
        if cache_file.exists():
            try:
                if AIOFILES_AVAILABLE:
                    async with aiofiles.open(cache_file, 'r') as f:  # type: ignore
                        content = await f.read()  # type: ignore
                        data = json.loads(content)
                else:
                    with open(cache_file, 'r') as f:
                        content = f.read()
                        data = json.loads(content)
                logger.info(f"Returning stale cache for {endpoint}:{symbol}")
                return data.get('value')
            except Exception as e:
                logger.error(f"Error reading stale cache: {e}")
        
        return None
    
    async def batch_update_symbols(self, symbols: List[str], endpoints: List[str],
                                  fetch_funcs: Dict[str, Any]):
        """
        Batch update multiple symbols and endpoints efficiently
        
        Args:
            symbols: List of symbols to update
            endpoints: List of endpoints to update
            fetch_funcs: Dictionary of fetch functions per endpoint
        """
        logger.info(f"Starting batch update for {len(symbols)} symbols, {len(endpoints)} endpoints")
        
        # Create update tasks prioritized by endpoint importance
        tasks = []
        for endpoint in endpoints:
            config = self.endpoint_config.get(endpoint, {})
            priority = config.get('priority', EndpointPriority.MEDIUM).value
            
            for symbol in symbols:
                # Check if update is needed
                cached = await self.get(endpoint, symbol)
                if cached is None:
                    # Add to priority queue
                    heapq.heappush(self.update_queue, 
                                 (priority, endpoint, symbol, fetch_funcs.get(endpoint)))
        
        # Process queue with rate limiting
        while self.update_queue:
            priority, endpoint, symbol, fetch_func = heapq.heappop(self.update_queue)
            
            # Check rate limits
            can_call, wait_time = await self.can_make_api_call(endpoint)
            
            if not can_call:
                if wait_time > 0 and wait_time < 60:
                    logger.info(f"Rate limited, waiting {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                else:
                    # Re-queue for later
                    heapq.heappush(self.update_queue, 
                                 (priority, endpoint, symbol, fetch_func))
                    await asyncio.sleep(1)
                    continue
            
            # Make the API call
            if fetch_func:
                try:
                    self.record_api_call(endpoint)
                    data = await fetch_func(symbol)
                    if data:
                        await self.set(endpoint, symbol, data)
                        logger.debug(f"Updated {endpoint}:{symbol}")
                except Exception as e:
                    logger.error(f"Error updating {endpoint}:{symbol}: {e}")
            
            # Small delay between calls
            await asyncio.sleep(0.1)
        
        logger.info("Batch update completed")
    
    async def start_smart_scheduler(self):
        """
        Start intelligent cache update scheduler
        Updates cache based on TTL and priority without hitting rate limits
        """
        logger.info("Starting smart cache scheduler")
        
        async def scheduler_loop():
            while True:
                try:
                    now = datetime.now()
                    updates_needed = []
                    
                    # Check all monitored symbols for needed updates
                    for symbol in self.monitored_symbols:
                        for endpoint, config in self.endpoint_config.items():
                            cache_key = self._generate_cache_key(endpoint, symbol)
                            cache_file = self.cache_dir / f"{cache_key.replace(':', '_')}.json"
                            
                            if cache_file.exists():
                                try:
                                    if AIOFILES_AVAILABLE:
                                        async with aiofiles.open(cache_file, 'r') as f:  # type: ignore
                                            content = await f.read()  # type: ignore
                                            data = json.loads(content)
                                    else:
                                        with open(cache_file, 'r') as f:
                                            content = f.read()
                                            data = json.loads(content)
                                        
                                    # Check if update is needed (80% of TTL)
                                    timestamp = datetime.fromisoformat(data['timestamp'])
                                    age = (now - timestamp).total_seconds()
                                    ttl = config['ttl']
                                    
                                    if age > ttl * 0.8:
                                        priority = config['priority'].value
                                        updates_needed.append((priority, endpoint, symbol, age))
                                except Exception:
                                    pass
                    
                    # Sort by priority and age
                    updates_needed.sort(key=lambda x: (x[0], -x[3]))
                    
                    # Process updates respecting rate limits
                    for priority, endpoint, symbol, age in updates_needed[:10]:  # Limit batch size
                        can_call, wait_time = await self.can_make_api_call(endpoint)
                        
                        if can_call:
                            logger.debug(f"Scheduling update for {endpoint}:{symbol} (age: {age:.0f}s)")
                            # Queue for update (would need actual fetch function)
                            heapq.heappush(self.update_queue, (priority, endpoint, symbol, None))
                        else:
                            logger.debug(f"Rate limited, postponing {endpoint}:{symbol}")
                    
                    # Wait before next check
                    await asyncio.sleep(30)  # Check every 30 seconds
                    
                except Exception as e:
                    logger.error(f"Error in scheduler: {e}")
                    await asyncio.sleep(60)
        
        # Start scheduler task
        asyncio.create_task(scheduler_loop())
        logger.info("Smart scheduler started")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_hits = sum(self.stats['hits'].values())
        total_misses = sum(self.stats['misses'].values())
        total_requests = total_hits + total_misses
        
        hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate per-endpoint statistics
        endpoint_stats = {}
        for endpoint in self.endpoint_config.keys():
            endpoint_requests = self.stats['hits'][endpoint] + self.stats['misses'][endpoint]
            if endpoint_requests > 0:
                endpoint_hit_rate = (self.stats['hits'][endpoint] / endpoint_requests * 100)
                endpoint_stats[endpoint] = {
                    'hits': self.stats['hits'][endpoint],
                    'misses': self.stats['misses'][endpoint],
                    'updates': self.stats['updates'][endpoint],
                    'hit_rate': f"{endpoint_hit_rate:.1f}%"
                }
        
        return {
            'total_hits': total_hits,
            'total_misses': total_misses,
            'total_requests': total_requests,
            'overall_hit_rate': f"{hit_rate:.1f}%",
            'api_calls_saved': self.stats['api_calls_saved'],
            'rate_limit_blocks': self.stats['rate_limit_blocks'],
            'monitored_symbols': len(self.monitored_symbols),
            'symbols': list(self.monitored_symbols),
            'endpoint_statistics': endpoint_stats,
            'cache_directory': str(self.cache_dir),
            'redis_connected': self.redis_client is not None
        }
    
    async def clear_cache(self, endpoint: Optional[str] = None, 
                         symbol: Optional[str] = None):
        """
        Clear cache entries
        
        Args:
            endpoint: Optional endpoint filter
            symbol: Optional symbol filter
        """
        pattern = "cryptometer"
        if endpoint:
            pattern += f":{endpoint}"
        if symbol:
            pattern += f":{symbol}"
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
                    if cursor == 0:
                        break
            except Exception as e:
                logger.error(f"Redis clear error: {e}")
        
        # Clear from file cache
        pattern_file = pattern.replace(':', '_').replace('*', '')
        for cache_file in self.cache_dir.glob(f"{pattern_file}*.json"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.error(f"File cache delete error: {e}")
        
        logger.info(f"Cleared cache for pattern: {pattern}")

# Create global instance
cryptometer_cache = CryptometerCacheManager()