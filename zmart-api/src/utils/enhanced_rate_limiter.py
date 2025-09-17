#!/usr/bin/env python3
"""
Enhanced Rate Limiter for ZmartBot APIs
Handles multiple API rate limits with adaptive backoff and 429 response handling
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
import random

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting - Optimized for high-frequency trading"""
    max_requests: int = 1000  # Increased from 60 for high-frequency trading
    time_window: int = 60     # seconds
    burst_limit: int = 50     # Increased from 10 for burst handling
    backoff_factor: float = 1.5  # Reduced from 2.0 for faster recovery
    max_backoff: float = 60.0    # Reduced from 300.0 for faster recovery
    jitter: bool = True       # add random jitter to prevent thundering herd
    adaptive_scaling: bool = True  # Enable dynamic rate limit adjustment

@dataclass
class APILimits:
    """Specific API rate limits - Optimized for high-frequency trading"""
    # Optimized API limits for better performance
    CRYPTOMETER_FREE = RateLimitConfig(max_requests=100, time_window=60, burst_limit=20)
    COINGECKO_FREE = RateLimitConfig(max_requests=50, time_window=60, burst_limit=10)
    BINANCE_FREE = RateLimitConfig(max_requests=2000, time_window=60, burst_limit=100)
    KUCOIN_FREE = RateLimitConfig(max_requests=500, time_window=10, burst_limit=50)
    ALTERNATIVE_ME = RateLimitConfig(max_requests=100, time_window=60, burst_limit=20)
    BLOCKCHAIN_INFO = RateLimitConfig(max_requests=200, time_window=60, burst_limit=30)

class EnhancedRateLimiter:
    """
    Enhanced rate limiter with adaptive backoff and 429 handling
    
    Features:
    - Per-API rate limiting
    - Exponential backoff with jitter
    - 429 response handling
    - Burst request handling
    - Automatic retry logic
    - Statistics tracking
    """
    
    def __init__(self):
        self.api_configs: Dict[str, RateLimitConfig] = {}
        self.request_history: Dict[str, List[float]] = {}
        self.backoff_until: Dict[str, float] = {}
        self.consecutive_failures: Dict[str, int] = {}
        self.statistics: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()
        
        # Initialize default API configurations
        self._init_default_configs()
        
    def _init_default_configs(self):
        """Initialize default rate limit configurations for known APIs"""
        limits = APILimits()
        self.api_configs.update({
            'cryptometer': limits.CRYPTOMETER_FREE,
            'coingecko': limits.COINGECKO_FREE,
            'binance': limits.BINANCE_FREE,
            'kucoin': limits.KUCOIN_FREE,
            'alternative_me': limits.ALTERNATIVE_ME,
            'blockchain_info': limits.BLOCKCHAIN_INFO,
            'default': RateLimitConfig()  # fallback
        })
        
        # Initialize statistics
        for api_name in self.api_configs.keys():
            self.statistics[api_name] = {
                'total_requests': 0,
                'successful_requests': 0,
                'rate_limited_requests': 0,
                'failed_requests': 0,
                'average_response_time': 0.0,
                'last_request_time': 0,
                'backoff_events': 0
            }
    
    def configure_api(self, api_name: str, config: RateLimitConfig):
        """Configure rate limits for a specific API"""
        with self.lock:
            self.api_configs[api_name] = config
            if api_name not in self.statistics:
                self.statistics[api_name] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'rate_limited_requests': 0,
                    'failed_requests': 0,
                    'average_response_time': 0.0,
                    'last_request_time': 0,
                    'backoff_events': 0
                }
        logger.info(f"Configured rate limits for {api_name}: {config.max_requests} req/{config.time_window}s")
    
    def _clean_old_requests(self, api_name: str, current_time: float):
        """Remove old requests outside the time window"""
        if api_name not in self.request_history:
            self.request_history[api_name] = []
        
        config = self.api_configs.get(api_name, self.api_configs['default'])
        cutoff_time = current_time - config.time_window
        
        self.request_history[api_name] = [
            req_time for req_time in self.request_history[api_name]
            if req_time > cutoff_time
        ]
    
    def _calculate_backoff(self, api_name: str) -> float:
        """Calculate exponential backoff time with jitter"""
        config = self.api_configs.get(api_name, self.api_configs['default'])
        failures = self.consecutive_failures.get(api_name, 0)
        
        # Exponential backoff: base_delay * (backoff_factor ^ failures)
        base_delay = 1.0
        backoff_time = base_delay * (config.backoff_factor ** failures)
        backoff_time = min(backoff_time, config.max_backoff)
        
        # Add jitter to prevent thundering herd
        if config.jitter:
            jitter = random.uniform(0.1, 0.3) * backoff_time
            backoff_time += jitter
        
        return backoff_time
    
    async def wait_if_needed(self, api_name: str) -> bool:
        """
        Wait if rate limiting is needed
        
        Returns:
            True if request can proceed, False if should be skipped
        """
        current_time = time.time()
        
        with self.lock:
            # Ensure API is initialized
            if api_name not in self.api_configs:
                self.api_configs[api_name] = self.api_configs['default']
            if api_name not in self.statistics:
                self.statistics[api_name] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'rate_limited_requests': 0,
                    'failed_requests': 0,
                    'average_response_time': 0.0,
                    'last_request_time': 0,
                    'backoff_events': 0
                }
            if api_name not in self.request_history:
                self.request_history[api_name] = []
            
            # Check if we're in a backoff period
            if api_name in self.backoff_until:
                if current_time < self.backoff_until[api_name]:
                    wait_time = self.backoff_until[api_name] - current_time
                    logger.warning(f"API {api_name} in backoff, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                else:
                    # Backoff period ended
                    del self.backoff_until[api_name]
                    self.consecutive_failures[api_name] = 0
            
            # Clean old requests
            self._clean_old_requests(api_name, current_time)
            
            # Check rate limits
            config = self.api_configs.get(api_name, self.api_configs['default'])
            current_requests = len(self.request_history[api_name])
            
            if current_requests >= config.max_requests:
                # Rate limit exceeded
                oldest_request = min(self.request_history[api_name])
                wait_time = (oldest_request + config.time_window) - current_time
                
                if wait_time > 0:
                    logger.warning(f"Rate limit exceeded for {api_name}, waiting {wait_time:.2f}s")
                    self.statistics[api_name]['rate_limited_requests'] += 1
                    await asyncio.sleep(wait_time)
            
            # Record the request
            self.request_history[api_name].append(current_time)
            self.statistics[api_name]['total_requests'] += 1
            self.statistics[api_name]['last_request_time'] = current_time
        
        return True
    
    def handle_response(self, api_name: str, status_code: int, response_time: float):
        """Handle API response and update statistics"""
        with self.lock:
            stats = self.statistics[api_name]
            
            # Update response time average
            total_requests = stats['total_requests']
            if total_requests > 0:
                current_avg = stats['average_response_time']
                stats['average_response_time'] = (
                    (current_avg * (total_requests - 1) + response_time) / total_requests
                )
            
            if status_code == 429:  # Rate limited
                # Implement exponential backoff
                backoff_time = self._calculate_backoff(api_name)
                self.backoff_until[api_name] = time.time() + backoff_time
                self.consecutive_failures[api_name] = self.consecutive_failures.get(api_name, 0) + 1
                stats['rate_limited_requests'] += 1
                stats['backoff_events'] += 1
                
                logger.warning(f"API {api_name} returned 429, backing off for {backoff_time:.2f}s")
                
            elif 200 <= status_code < 300:  # Success
                stats['successful_requests'] += 1
                # Reset consecutive failures on success
                if api_name in self.consecutive_failures:
                    self.consecutive_failures[api_name] = 0
                    
            else:  # Other error
                stats['failed_requests'] += 1
                self.consecutive_failures[api_name] = self.consecutive_failures.get(api_name, 0) + 1
    
    def get_statistics(self, api_name: Optional[str] = None) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        with self.lock:
            if api_name:
                return self.statistics.get(api_name, {})
            else:
                return self.statistics.copy()
    
    def get_status(self, api_name: str) -> Dict[str, Any]:
        """Get current status for an API"""
        current_time = time.time()
        
        with self.lock:
            # Ensure API is configured
            if api_name not in self.api_configs:
                self.api_configs[api_name] = self.api_configs['default']
                self.statistics[api_name] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'rate_limited_requests': 0,
                    'failed_requests': 0,
                    'average_response_time': 0.0,
                    'last_request_time': 0,
                    'backoff_events': 0
                }
            
            self._clean_old_requests(api_name, current_time)
            
            config = self.api_configs.get(api_name, self.api_configs['default'])
            current_requests = len(self.request_history.get(api_name, []))
            
            is_in_backoff = (
                api_name in self.backoff_until and 
                current_time < self.backoff_until[api_name]
            )
            
            backoff_remaining = 0
            if is_in_backoff:
                backoff_remaining = self.backoff_until[api_name] - current_time
            
            return {
                'api_name': api_name,
                'current_requests': current_requests,
                'max_requests': config.max_requests,
                'time_window': config.time_window,
                'requests_remaining': max(0, config.max_requests - current_requests),
                'is_rate_limited': current_requests >= config.max_requests,
                'is_in_backoff': is_in_backoff,
                'backoff_remaining': backoff_remaining,
                'consecutive_failures': self.consecutive_failures.get(api_name, 0),
                'statistics': self.statistics.get(api_name, {})
            }
    
    async def execute_with_rate_limit(self, 
                                    api_name: str, 
                                    func: Callable, 
                                    *args, 
                                    **kwargs) -> tuple[Any, bool]:
        """
        Execute a function with rate limiting
        
        Returns:
            (result, success) tuple
        """
        start_time = time.time()
        
        # Wait if rate limiting is needed
        can_proceed = await self.wait_if_needed(api_name)
        if not can_proceed:
            return None, False
        
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Handle successful response
            response_time = time.time() - start_time
            
            # If result has status_code (like requests.Response), use it
            if hasattr(result, 'status_code'):
                self.handle_response(api_name, result.status_code, response_time)
                return result, 200 <= result.status_code < 300
            else:
                # Assume success if no status code
                self.handle_response(api_name, 200, response_time)
                return result, True
                
        except Exception as e:
            response_time = time.time() - start_time
            
            # Check if it's a rate limit error
            error_str = str(e).lower()
            if '429' in error_str or 'rate limit' in error_str or 'too many requests' in error_str:
                self.handle_response(api_name, 429, response_time)
            else:
                self.handle_response(api_name, 500, response_time)
            
            logger.error(f"Error executing {func.__name__} for {api_name}: {e}")
            return None, False

# Global rate limiter instance
global_rate_limiter = EnhancedRateLimiter()

# Convenience functions
async def rate_limited_request(api_name: str, func: Callable, *args, **kwargs):
    """Convenience function for rate-limited requests"""
    return await global_rate_limiter.execute_with_rate_limit(api_name, func, *args, **kwargs)

def get_rate_limit_status(api_name: str) -> Dict[str, Any]:
    """Get rate limit status for an API"""
    return global_rate_limiter.get_status(api_name)

def configure_api_limits(api_name: str, max_requests: int, time_window: int, **kwargs):
    """Configure rate limits for an API"""
    config = RateLimitConfig(
        max_requests=max_requests,
        time_window=time_window,
        **kwargs
    )
    global_rate_limiter.configure_api(api_name, config)