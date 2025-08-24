"""
Retry Handler Utility
Advanced retry mechanisms with exponential backoff and circuit breaker patterns
"""

import asyncio
import time
import logging
import random
from typing import Callable, Any, Optional, List, Type, Union
from dataclasses import dataclass
from enum import Enum
import functools


class RetryStrategy(Enum):
    """Retry strategy types"""
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    JITTERED_BACKOFF = "jittered_backoff"


@dataclass
class RetryConfig:
    """Retry configuration"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    jitter: bool = True
    backoff_multiplier: float = 2.0
    
    # Exception handling
    retryable_exceptions: List[Type[Exception]] = None
    non_retryable_exceptions: List[Type[Exception]] = None
    
    # Conditional retry
    retry_condition: Optional[Callable[[Exception], bool]] = None
    
    def __post_init__(self):
        if self.retryable_exceptions is None:
            self.retryable_exceptions = [
                ConnectionError,
                TimeoutError,
                OSError,
                Exception  # Catch-all, but will be filtered by non_retryable
            ]
        
        if self.non_retryable_exceptions is None:
            self.non_retryable_exceptions = [
                KeyboardInterrupt,
                SystemExit,
                ValueError,  # Usually indicates programming error
                TypeError,   # Usually indicates programming error
            ]


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    success_threshold: int = 3  # Successes needed to close circuit
    
    
class CircuitBreaker:
    """Circuit breaker for preventing cascading failures"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.logger = logging.getLogger(__name__)
    
    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                self.logger.info("Circuit breaker moving to HALF_OPEN state")
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record a successful execution"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.logger.info("Circuit breaker CLOSED - service recovered")
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0  # Reset failure count on success
    
    def record_failure(self):
        """Record a failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                self.logger.warning(f"Circuit breaker OPEN - {self.failure_count} failures")
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning("Circuit breaker back to OPEN - test failed")


class RetryHandler:
    """Advanced retry handler with multiple strategies and circuit breaker"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        **kwargs
    ):
        """
        Initialize retry handler
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            strategy: Retry strategy to use
            circuit_breaker_config: Optional circuit breaker configuration
            **kwargs: Additional configuration options
        """
        self.config = RetryConfig(
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=strategy,
            **kwargs
        )
        
        self.circuit_breaker = None
        if circuit_breaker_config:
            self.circuit_breaker = CircuitBreaker(circuit_breaker_config)
        
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.total_attempts = 0
        self.total_retries = 0
        self.total_failures = 0
        self.total_successes = 0
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number"""
        if self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * attempt
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.backoff_multiplier ** (attempt - 1))
        elif self.config.strategy == RetryStrategy.JITTERED_BACKOFF:
            base_delay = self.config.base_delay * (self.config.backoff_multiplier ** (attempt - 1))
            jitter = random.uniform(0.5, 1.5)
            delay = base_delay * jitter
        else:
            delay = self.config.base_delay
        
        # Apply jitter if enabled (except for jittered backoff which already has it)
        if self.config.jitter and self.config.strategy != RetryStrategy.JITTERED_BACKOFF:
            jitter_factor = random.uniform(0.8, 1.2)
            delay *= jitter_factor
        
        return min(delay, self.config.max_delay)
    
    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if the exception should trigger a retry"""
        # Check attempt limit
        if attempt > self.config.max_retries:
            return False
        
        # Check non-retryable exceptions first
        for exc_type in self.config.non_retryable_exceptions:
            if isinstance(exception, exc_type):
                return False
        
        # Check retryable exceptions
        is_retryable = False
        for exc_type in self.config.retryable_exceptions:
            if isinstance(exception, exc_type):
                is_retryable = True
                break
        
        if not is_retryable:
            return False
        
        # Check custom retry condition
        if self.config.retry_condition:
            return self.config.retry_condition(exception)
        
        return True
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute (can be sync or async)
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result
        
        Raises:
            Last exception if all retries failed
        """
        attempt = 0
        last_exception = None
        
        while attempt <= self.config.max_retries:
            attempt += 1
            self.total_attempts += 1
            
            # Check circuit breaker
            if self.circuit_breaker and not self.circuit_breaker.can_execute():
                raise Exception("Circuit breaker is OPEN - service unavailable")
            
            try:
                # Execute function (handle both sync and async)
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Success
                self.total_successes += 1
                if self.circuit_breaker:
                    self.circuit_breaker.record_success()
                
                if attempt > 1:
                    self.logger.info(f"Function succeeded after {attempt} attempts")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Record failure for circuit breaker
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure()
                
                # Check if we should retry
                if not self._should_retry(e, attempt):
                    self.total_failures += 1
                    self.logger.error(f"Function failed permanently: {e}")
                    raise e
                
                # Calculate delay for next attempt
                if attempt <= self.config.max_retries:
                    delay = self._calculate_delay(attempt)
                    self.total_retries += 1
                    
                    self.logger.warning(
                        f"Attempt {attempt} failed: {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    await asyncio.sleep(delay)
        
        # All retries exhausted
        self.total_failures += 1
        self.logger.error(f"Function failed after {self.config.max_retries + 1} attempts")
        raise last_exception
    
    def get_stats(self) -> dict:
        """Get retry handler statistics"""
        return {
            'total_attempts': self.total_attempts,
            'total_retries': self.total_retries,
            'total_failures': self.total_failures,
            'total_successes': self.total_successes,
            'success_rate': self.total_successes / max(self.total_attempts, 1),
            'retry_rate': self.total_retries / max(self.total_attempts, 1),
            'circuit_breaker_state': self.circuit_breaker.state.value if self.circuit_breaker else None
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.total_attempts = 0
        self.total_retries = 0
        self.total_failures = 0
        self.total_successes = 0


def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    retryable_exceptions: Optional[List[Type[Exception]]] = None,
    **kwargs
):
    """
    Decorator for adding retry logic to functions
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries
        strategy: Retry strategy to use
        retryable_exceptions: List of exceptions that should trigger retries
        **kwargs: Additional retry configuration
    
    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        retry_handler = RetryHandler(
            max_retries=max_retries,
            base_delay=base_delay,
            strategy=strategy,
            retryable_exceptions=retryable_exceptions,
            **kwargs
        )
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await retry_handler.execute(func, *args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we need to run in an event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(
                retry_handler.execute(func, *args, **kwargs)
            )
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class BulkRetryHandler:
    """Handler for retrying bulk operations with partial failure support"""
    
    def __init__(self, retry_handler: RetryHandler):
        self.retry_handler = retry_handler
        self.logger = logging.getLogger(__name__)
    
    async def execute_bulk(
        self,
        func: Callable,
        items: List[Any],
        batch_size: int = 10,
        fail_fast: bool = False
    ) -> tuple[List[Any], List[tuple[Any, Exception]]]:
        """
        Execute function on batches of items with retry logic
        
        Args:
            func: Function to execute on each batch
            items: List of items to process
            batch_size: Size of each batch
            fail_fast: If True, stop on first batch failure
        
        Returns:
            Tuple of (successful_results, failed_items_with_exceptions)
        """
        successful_results = []
        failed_items = []
        
        # Process items in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            try:
                result = await self.retry_handler.execute(func, batch)
                successful_results.extend(result if isinstance(result, list) else [result])
                
            except Exception as e:
                self.logger.error(f"Batch {i//batch_size + 1} failed: {e}")
                
                # Add all items in failed batch to failed_items
                for item in batch:
                    failed_items.append((item, e))
                
                if fail_fast:
                    break
        
        return successful_results, failed_items


# Utility functions
def create_api_retry_handler(
    api_name: str,
    max_retries: int = 3,
    enable_circuit_breaker: bool = True
) -> RetryHandler:
    """Create a retry handler optimized for API calls"""
    
    # API-specific retryable exceptions
    retryable_exceptions = [
        ConnectionError,
        TimeoutError,
        OSError,
    ]
    
    # Add HTTP-specific exceptions if available
    try:
        import aiohttp
        retryable_exceptions.extend([
            aiohttp.ClientError,
            aiohttp.ServerTimeoutError,
            aiohttp.ClientConnectorError,
        ])
    except ImportError:
        pass
    
    circuit_breaker_config = None
    if enable_circuit_breaker:
        circuit_breaker_config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60.0,
            success_threshold=3
        )
    
    return RetryHandler(
        max_retries=max_retries,
        base_delay=1.0,
        max_delay=30.0,
        strategy=RetryStrategy.JITTERED_BACKOFF,
        retryable_exceptions=retryable_exceptions,
        circuit_breaker_config=circuit_breaker_config
    )

