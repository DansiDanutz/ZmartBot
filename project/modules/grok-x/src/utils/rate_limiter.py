"""
Rate Limiter Utility
Advanced rate limiting for API requests with multiple time windows
"""

import asyncio
import time
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from collections import deque
import threading


@dataclass
class RateLimit:
    """Rate limit configuration"""
    requests: int
    window_seconds: int
    
    def __post_init__(self):
        if self.requests <= 0:
            raise ValueError("Requests must be positive")
        if self.window_seconds <= 0:
            raise ValueError("Window seconds must be positive")


class RateLimiter:
    """
    Advanced rate limiter supporting multiple time windows
    Thread-safe and async-compatible
    """
    
    def __init__(
        self,
        requests_per_minute: Optional[int] = None,
        requests_per_hour: Optional[int] = None,
        requests_per_day: Optional[int] = None,
        burst_limit: Optional[int] = None
    ):
        """
        Initialize rate limiter with multiple time windows
        
        Args:
            requests_per_minute: Maximum requests per minute
            requests_per_hour: Maximum requests per hour
            requests_per_day: Maximum requests per day
            burst_limit: Maximum burst requests (short-term limit)
        """
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        
        # Configure rate limits
        self.limits = []
        
        if burst_limit:
            self.limits.append(RateLimit(burst_limit, 10))  # 10 second burst window
        
        if requests_per_minute:
            self.limits.append(RateLimit(requests_per_minute, 60))
        
        if requests_per_hour:
            self.limits.append(RateLimit(requests_per_hour, 3600))
        
        if requests_per_day:
            self.limits.append(RateLimit(requests_per_day, 86400))
        
        if not self.limits:
            # Default rate limit if none specified
            self.limits.append(RateLimit(100, 60))  # 100 requests per minute
        
        # Request tracking for each limit
        self.request_times: Dict[int, deque] = {}
        for i, limit in enumerate(self.limits):
            self.request_times[i] = deque()
        
        # Statistics
        self.total_requests = 0
        self.total_waits = 0
        self.total_wait_time = 0.0
    
    def _cleanup_old_requests(self, limit_index: int, current_time: float):
        """Remove old requests outside the time window"""
        limit = self.limits[limit_index]
        request_times = self.request_times[limit_index]
        
        cutoff_time = current_time - limit.window_seconds
        
        while request_times and request_times[0] <= cutoff_time:
            request_times.popleft()
    
    def _can_make_request(self, current_time: float) -> tuple[bool, float]:
        """
        Check if a request can be made now
        
        Returns:
            (can_make_request, wait_time_seconds)
        """
        max_wait_time = 0.0
        
        for i, limit in enumerate(self.limits):
            self._cleanup_old_requests(i, current_time)
            request_times = self.request_times[i]
            
            if len(request_times) >= limit.requests:
                # Rate limit exceeded, calculate wait time
                oldest_request = request_times[0]
                wait_time = oldest_request + limit.window_seconds - current_time
                max_wait_time = max(max_wait_time, wait_time)
        
        return max_wait_time <= 0, max_wait_time
    
    def _record_request(self, current_time: float):
        """Record a new request"""
        for i in range(len(self.limits)):
            self.request_times[i].append(current_time)
        
        self.total_requests += 1
    
    async def acquire(self) -> None:
        """
        Acquire permission to make a request
        Will wait if necessary to respect rate limits
        """
        while True:
            current_time = time.time()
            
            with self.lock:
                can_proceed, wait_time = self._can_make_request(current_time)
                
                if can_proceed:
                    self._record_request(current_time)
                    return
            
            # Need to wait
            if wait_time > 0:
                self.logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                self.total_waits += 1
                self.total_wait_time += wait_time
                
                await asyncio.sleep(wait_time)
            else:
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.01)
    
    def try_acquire(self) -> bool:
        """
        Try to acquire permission without waiting
        
        Returns:
            True if request can be made immediately, False otherwise
        """
        current_time = time.time()
        
        with self.lock:
            can_proceed, _ = self._can_make_request(current_time)
            
            if can_proceed:
                self._record_request(current_time)
                return True
            
            return False
    
    def get_stats(self) -> Dict[str, any]:
        """Get rate limiter statistics"""
        current_time = time.time()
        
        with self.lock:
            # Clean up old requests for accurate current usage
            for i in range(len(self.limits)):
                self._cleanup_old_requests(i, current_time)
            
            # Calculate current usage for each limit
            current_usage = []
            for i, limit in enumerate(self.limits):
                usage = len(self.request_times[i])
                percentage = (usage / limit.requests) * 100
                current_usage.append({
                    'window_seconds': limit.window_seconds,
                    'limit': limit.requests,
                    'current': usage,
                    'percentage': percentage
                })
            
            return {
                'total_requests': self.total_requests,
                'total_waits': self.total_waits,
                'total_wait_time': self.total_wait_time,
                'average_wait_time': self.total_wait_time / max(self.total_waits, 1),
                'current_usage': current_usage
            }
    
    def reset(self):
        """Reset all rate limit counters"""
        with self.lock:
            for i in range(len(self.limits)):
                self.request_times[i].clear()
            
            self.total_requests = 0
            self.total_waits = 0
            self.total_wait_time = 0.0


class AdaptiveRateLimiter(RateLimiter):
    """
    Adaptive rate limiter that adjusts limits based on API responses
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_count = 0
        self.success_count = 0
        self.last_error_time = 0
        self.backoff_factor = 1.0
        self.max_backoff = 10.0
        self.recovery_threshold = 10  # Successful requests before reducing backoff
    
    def report_success(self):
        """Report a successful API request"""
        self.success_count += 1
        
        # Gradually reduce backoff after successful requests
        if self.success_count >= self.recovery_threshold and self.backoff_factor > 1.0:
            self.backoff_factor = max(1.0, self.backoff_factor * 0.9)
            self.success_count = 0
            self.logger.info(f"Reducing rate limit backoff to {self.backoff_factor:.2f}")
    
    def report_error(self, error_type: str = "unknown"):
        """Report an API error"""
        self.error_count += 1
        self.last_error_time = time.time()
        self.success_count = 0
        
        # Increase backoff for rate limit errors
        if "rate" in error_type.lower() or "429" in error_type:
            self.backoff_factor = min(self.max_backoff, self.backoff_factor * 2.0)
            self.logger.warning(f"Rate limit error detected, increasing backoff to {self.backoff_factor:.2f}")
    
    async def acquire(self) -> None:
        """Acquire with adaptive backoff"""
        # Apply backoff delay
        if self.backoff_factor > 1.0:
            base_delay = 1.0 / max(limit.requests / limit.window_seconds for limit in self.limits)
            adaptive_delay = base_delay * (self.backoff_factor - 1.0)
            
            if adaptive_delay > 0.1:  # Only apply significant delays
                await asyncio.sleep(adaptive_delay)
        
        await super().acquire()


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for smooth rate limiting
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize token bucket rate limiter
        
        Args:
            rate: Tokens per second
            capacity: Maximum tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def _update_tokens(self):
        """Update token count based on elapsed time"""
        current_time = time.time()
        elapsed = current_time - self.last_update
        
        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_update = current_time
    
    async def acquire(self, tokens: int = 1) -> None:
        """Acquire tokens from the bucket"""
        while True:
            with self.lock:
                self._update_tokens()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Calculate wait time for required tokens
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate
            
            self.logger.debug(f"Token bucket empty, waiting {wait_time:.2f} seconds")
            await asyncio.sleep(wait_time)
    
    def try_acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens without waiting"""
        with self.lock:
            self._update_tokens()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def get_available_tokens(self) -> int:
        """Get current number of available tokens"""
        with self.lock:
            self._update_tokens()
            return int(self.tokens)


# Factory function for creating appropriate rate limiters
def create_rate_limiter(
    limiter_type: str = "standard",
    **kwargs
) -> RateLimiter:
    """
    Factory function to create rate limiters
    
    Args:
        limiter_type: Type of rate limiter ("standard", "adaptive", "token_bucket")
        **kwargs: Rate limiter configuration
    
    Returns:
        Configured rate limiter instance
    """
    if limiter_type == "adaptive":
        return AdaptiveRateLimiter(**kwargs)
    elif limiter_type == "token_bucket":
        rate = kwargs.get('rate', 1.0)
        capacity = kwargs.get('capacity', 10)
        return TokenBucketRateLimiter(rate, capacity)
    else:
        return RateLimiter(**kwargs)

