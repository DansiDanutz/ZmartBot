#!/usr/bin/env python3
"""
Advanced Rate Limiting Protection Module
Provides comprehensive rate limiting for API calls and trading operations
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)

class RateLimitType(Enum):
    """Types of rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"

class RateLimiter:
    """
    Advanced rate limiter with multiple strategies
    Supports per-endpoint and per-user rate limiting
    """
    
    def __init__(
        self,
        max_requests: int = 100,
        time_window: int = 60,
        strategy: RateLimitType = RateLimitType.SLIDING_WINDOW
    ):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
            strategy: Rate limiting strategy to use
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.strategy = strategy
        
        # Storage for different strategies
        self.request_times = defaultdict(deque)  # For sliding window
        self.request_counts = defaultdict(int)   # For fixed window
        self.window_start = defaultdict(float)   # For fixed window
        self.tokens = defaultdict(lambda: max_requests)  # For token bucket
        self.last_refill = defaultdict(float)    # For token bucket
        
        # Semaphore for concurrent request limiting
        self.semaphore = asyncio.Semaphore(max_requests)
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'allowed_requests': 0,
            'last_reset': datetime.now()
        }
        
        logger.info(f"Rate limiter initialized: {max_requests} requests per {time_window}s using {strategy.value}")
    
    async def check_rate_limit(self, identifier: str = "global") -> bool:
        """
        Check if request is within rate limit
        
        Args:
            identifier: Unique identifier (API endpoint, user ID, etc.)
            
        Returns:
            True if request is allowed, False if rate limited
        """
        if self.strategy == RateLimitType.SLIDING_WINDOW:
            return await self._check_sliding_window(identifier)
        elif self.strategy == RateLimitType.FIXED_WINDOW:
            return await self._check_fixed_window(identifier)
        elif self.strategy == RateLimitType.TOKEN_BUCKET:
            return await self._check_token_bucket(identifier)
        elif self.strategy == RateLimitType.LEAKY_BUCKET:
            return await self._check_leaky_bucket(identifier)
        else:
            return True
    
    async def _check_sliding_window(self, identifier: str) -> bool:
        """Sliding window rate limiting"""
        current_time = time.time()
        request_queue = self.request_times[identifier]
        
        # Remove old requests outside the window
        while request_queue and request_queue[0] <= current_time - self.time_window:
            request_queue.popleft()
        
        # Check if we can make a new request
        if len(request_queue) < self.max_requests:
            request_queue.append(current_time)
            self.stats['allowed_requests'] += 1
            return True
        else:
            self.stats['blocked_requests'] += 1
            logger.warning(f"Rate limit exceeded for {identifier}: {len(request_queue)}/{self.max_requests}")
            return False
    
    async def _check_fixed_window(self, identifier: str) -> bool:
        """Fixed window rate limiting"""
        current_time = time.time()
        
        # Check if we need to reset the window
        if current_time - self.window_start[identifier] >= self.time_window:
            self.window_start[identifier] = current_time
            self.request_counts[identifier] = 0
        
        # Check if we can make a new request
        if self.request_counts[identifier] < self.max_requests:
            self.request_counts[identifier] += 1
            self.stats['allowed_requests'] += 1
            return True
        else:
            self.stats['blocked_requests'] += 1
            logger.warning(f"Rate limit exceeded for {identifier}: {self.request_counts[identifier]}/{self.max_requests}")
            return False
    
    async def _check_token_bucket(self, identifier: str) -> bool:
        """Token bucket rate limiting"""
        current_time = time.time()
        
        # Refill tokens based on time passed
        time_passed = current_time - self.last_refill[identifier]
        tokens_to_add = time_passed * (self.max_requests / self.time_window)
        
        self.tokens[identifier] = int(min(
            self.max_requests,
            self.tokens[identifier] + tokens_to_add
        ))
        self.last_refill[identifier] = current_time
        
        # Check if we have tokens available
        if self.tokens[identifier] >= 1:
            self.tokens[identifier] -= 1
            self.stats['allowed_requests'] += 1
            return True
        else:
            self.stats['blocked_requests'] += 1
            logger.warning(f"Rate limit exceeded for {identifier}: No tokens available")
            return False
    
    async def _check_leaky_bucket(self, identifier: str) -> bool:
        """Leaky bucket rate limiting"""
        # Similar to token bucket but with constant drain rate
        return await self._check_token_bucket(identifier)
    
    async def wait_if_needed(self, identifier: str = "global") -> None:
        """
        Wait if rate limit is exceeded
        
        Args:
            identifier: Unique identifier
        """
        while not await self.check_rate_limit(identifier):
            wait_time = self.get_retry_after(identifier)
            logger.info(f"Rate limited for {identifier}. Waiting {wait_time:.2f}s...")
            await asyncio.sleep(wait_time)
    
    def get_retry_after(self, identifier: str = "global") -> float:
        """
        Get time to wait before retry
        
        Args:
            identifier: Unique identifier
            
        Returns:
            Seconds to wait before retry
        """
        if self.strategy == RateLimitType.SLIDING_WINDOW:
            request_queue = self.request_times[identifier]
            if request_queue:
                oldest_request = request_queue[0]
                return max(0, self.time_window - (time.time() - oldest_request))
        elif self.strategy == RateLimitType.FIXED_WINDOW:
            time_until_reset = self.time_window - (time.time() - self.window_start[identifier])
            return max(0, time_until_reset)
        elif self.strategy == RateLimitType.TOKEN_BUCKET:
            # Calculate time to get 1 token
            return self.time_window / self.max_requests
        
        return 1.0  # Default wait time
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        self.stats['total_requests'] = self.stats['allowed_requests'] + self.stats['blocked_requests']
        self.stats['block_rate'] = (
            self.stats['blocked_requests'] / self.stats['total_requests']
            if self.stats['total_requests'] > 0 else 0
        )
        return self.stats
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'allowed_requests': 0,
            'last_reset': datetime.now()
        }

class MultiTierRateLimiter:
    """
    Multi-tier rate limiter for different API tiers
    """
    
    def __init__(self):
        """Initialize multi-tier rate limiter"""
        # Different tiers for different services
        self.tiers = {
            'cryptometer': RateLimiter(100, 60),  # 100 requests per minute
            'kucoin': RateLimiter(30, 10),        # 30 requests per 10 seconds
            'binance': RateLimiter(1200, 60),     # 1200 requests per minute
            'openai': RateLimiter(60, 60),        # 60 requests per minute
            'database': RateLimiter(1000, 60),    # 1000 requests per minute
            'trading': RateLimiter(10, 60),       # 10 trades per minute
        }
        
        logger.info("Multi-tier rate limiter initialized")
    
    async def check_limit(self, service: str, identifier: str = "global") -> bool:
        """Check rate limit for specific service"""
        if service in self.tiers:
            return await self.tiers[service].check_rate_limit(identifier)
        return True
    
    async def wait_if_needed(self, service: str, identifier: str = "global"):
        """Wait if rate limited for specific service"""
        if service in self.tiers:
            await self.tiers[service].wait_if_needed(identifier)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all tiers"""
        return {
            service: limiter.get_stats()
            for service, limiter in self.tiers.items()
        }

# Decorator for rate limiting
def rate_limit(max_calls: int = 10, time_window: int = 60, service: Optional[str] = None):
    """
    Decorator for rate limiting functions
    
    Args:
        max_calls: Maximum number of calls allowed
        time_window: Time window in seconds
        service: Service name for multi-tier limiting
    """
    def decorator(func: Callable):
        # Create limiter for this function
        limiter = RateLimiter(max_calls, time_window)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get identifier from function name or arguments
            identifier = f"{func.__name__}"
            
            # Wait if rate limited
            await limiter.wait_if_needed(identifier)
            
            # Execute function
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For synchronous functions
            identifier = f"{func.__name__}"
            
            # Simple check without async
            if not asyncio.run(limiter.check_rate_limit(identifier)):
                retry_after = limiter.get_retry_after(identifier)
                raise Exception(f"Rate limit exceeded. Retry after {retry_after:.2f}s")
            
            return func(*args, **kwargs)
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Global rate limiter instance
global_rate_limiter = MultiTierRateLimiter()