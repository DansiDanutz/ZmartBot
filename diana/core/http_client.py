"""
Diana Platform - Enterprise HTTP Client
Production-ready HTTP client with circuit breakers, retries, and observability
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

import aiohttp
import backoff
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from prometheus_client import Counter, Histogram, Gauge


# Metrics
http_requests_total = Counter(
    'diana_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'diana_http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

circuit_breaker_state = Gauge(
    'diana_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half_open)',
    ['service']
)

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = 0
    OPEN = 1
    HALF_OPEN = 2


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: int = 30
    test_request_volume: int = 10
    sleep_window: int = 10
    error_percentage: int = 50
    success_threshold: int = 3  # For half-open state


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics tracking"""
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    total_requests: int = 0
    consecutive_successes: int = 0


class CircuitBreakerException(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """Enterprise-grade circuit breaker implementation"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self._lock = asyncio.Lock()
        
        # Update Prometheus metrics
        circuit_breaker_state.labels(service=name).set(self.state.value)
        
        logger.info(f"Circuit breaker '{name}' initialized with config: {self.config}")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        async with self._lock:
            # Check if we should allow the request
            if not self._should_allow_request():
                logger.warning(f"Circuit breaker '{self.name}' is OPEN - rejecting request")
                raise CircuitBreakerException(f"Circuit breaker '{self.name}' is open")
            
            # If in HALF_OPEN state, only allow limited requests
            if self.state == CircuitBreakerState.HALF_OPEN:
                if self.metrics.total_requests >= self.config.test_request_volume:
                    logger.warning(f"Circuit breaker '{self.name}' HALF_OPEN limit reached")
                    raise CircuitBreakerException(f"Circuit breaker '{self.name}' half-open limit reached")
        
        # Execute the function
        start_time = time.time()
        try:
            with tracer.start_as_current_span(f"circuit_breaker_{self.name}") as span:
                span.set_attribute("circuit_breaker.name", self.name)
                span.set_attribute("circuit_breaker.state", self.state.name)
                
                result = await func(*args, **kwargs)
                
                # Record success
                await self._record_success()
                span.set_status(Status(StatusCode.OK))
                return result
                
        except Exception as e:
            # Record failure
            await self._record_failure()
            logger.error(f"Circuit breaker '{self.name}' recorded failure: {str(e)}")
            raise
        finally:
            duration = time.time() - start_time
            logger.debug(f"Circuit breaker '{self.name}' call completed in {duration:.3f}s")
    
    def _should_allow_request(self) -> bool:
        """Determine if request should be allowed based on current state"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            # Check if we should transition to HALF_OPEN
            if (self.metrics.last_failure_time and 
                datetime.now() - self.metrics.last_failure_time > timedelta(seconds=self.config.recovery_timeout)):
                self._transition_to_half_open()
                return True
            return False
        
        # HALF_OPEN state - allow limited requests
        return True
    
    async def _record_success(self):
        """Record successful request"""
        async with self._lock:
            self.metrics.success_count += 1
            self.metrics.total_requests += 1
            self.metrics.last_success_time = datetime.now()
            self.metrics.consecutive_successes += 1
            
            # If in HALF_OPEN and enough successes, close the circuit
            if (self.state == CircuitBreakerState.HALF_OPEN and 
                self.metrics.consecutive_successes >= self.config.success_threshold):
                self._transition_to_closed()
    
    async def _record_failure(self):
        """Record failed request"""
        async with self._lock:
            self.metrics.failure_count += 1
            self.metrics.total_requests += 1
            self.metrics.last_failure_time = datetime.now()
            self.metrics.consecutive_successes = 0
            
            # Check if we should open the circuit
            if self._should_open_circuit():
                self._transition_to_open()
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened"""
        # Not enough requests to make a decision
        if self.metrics.total_requests < self.config.test_request_volume:
            return False
        
        # Check failure rate
        failure_rate = (self.metrics.failure_count / self.metrics.total_requests) * 100
        return failure_rate >= self.config.error_percentage
    
    def _transition_to_open(self):
        """Transition circuit breaker to OPEN state"""
        self.state = CircuitBreakerState.OPEN
        circuit_breaker_state.labels(service=self.name).set(self.state.value)
        logger.warning(f"Circuit breaker '{self.name}' transitioned to OPEN")
    
    def _transition_to_half_open(self):
        """Transition circuit breaker to HALF_OPEN state"""
        self.state = CircuitBreakerState.HALF_OPEN
        self.metrics.total_requests = 0
        self.metrics.consecutive_successes = 0
        circuit_breaker_state.labels(service=self.name).set(self.state.value)
        logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN")
    
    def _transition_to_closed(self):
        """Transition circuit breaker to CLOSED state"""
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics()  # Reset metrics
        circuit_breaker_state.labels(service=self.name).set(self.state.value)
        logger.info(f"Circuit breaker '{self.name}' transitioned to CLOSED")


@dataclass
class HTTPClientConfig:
    """HTTP client configuration"""
    timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 1.0
    circuit_breaker: Optional[CircuitBreakerConfig] = field(default_factory=CircuitBreakerConfig)
    default_headers: Dict[str, str] = field(default_factory=dict)
    user_agent: str = "Diana-Platform/1.0.0"


class DianaHTTPClient:
    """Enterprise HTTP client with circuit breaker, retries, and observability"""
    
    def __init__(self, name: str, config: HTTPClientConfig = None):
        self.name = name
        self.config = config or HTTPClientConfig()
        self.circuit_breaker = CircuitBreaker(name, self.config.circuit_breaker) if self.config.circuit_breaker else None
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Default headers
        self.default_headers = {
            "User-Agent": self.config.user_agent,
            "X-Service": self.name,
            **self.config.default_headers
        }
        
        logger.info(f"Diana HTTP client '{name}' initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()
    
    async def start(self):
        """Start HTTP client session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self.default_headers,
                connector=aiohttp.TCPConnector(
                    limit=100,
                    limit_per_host=30,
                    keepalive_timeout=30,
                    enable_cleanup_closed=True
                )
            )
            logger.info(f"HTTP client '{self.name}' session started")
    
    async def stop(self):
        """Stop HTTP client session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info(f"HTTP client '{self.name}' session stopped")
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=30
    )
    async def _make_request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make HTTP request with retry logic"""
        if not self.session:
            await self.start()
        
        # Add tracing headers
        headers = kwargs.get('headers', {}).copy()
        
        # Create correlation ID if not provided
        if 'X-Correlation-ID' not in headers:
            headers['X-Correlation-ID'] = f"{self.name}-{int(time.time())}-{id(asyncio.current_task())}"
        
        kwargs['headers'] = headers
        
        logger.debug(f"Making {method} request to {url}")
        start_time = time.time()
        
        try:
            response = await self.session.request(method, url, **kwargs)
            duration = time.time() - start_time
            
            # Record metrics
            http_requests_total.labels(
                method=method.upper(),
                endpoint=self._extract_endpoint(url),
                status=response.status
            ).inc()
            
            http_request_duration.labels(
                method=method.upper(),
                endpoint=self._extract_endpoint(url)
            ).observe(duration)
            
            logger.debug(f"{method} {url} -> {response.status} ({duration:.3f}s)")
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Record failed request metrics
            http_requests_total.labels(
                method=method.upper(),
                endpoint=self._extract_endpoint(url),
                status=0  # Failed request
            ).inc()
            
            logger.error(f"{method} {url} failed after {duration:.3f}s: {str(e)}")
            raise
    
    def _extract_endpoint(self, url: str) -> str:
        """Extract endpoint pattern from URL for metrics"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            # Remove query parameters and fragment
            return parsed.path or "/"
        except:
            return "unknown"
    
    async def request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with circuit breaker protection"""
        
        with tracer.start_as_current_span(f"http_request_{method}") as span:
            span.set_attributes({
                "http.method": method.upper(),
                "http.url": url,
                "http.client": self.name,
                "http.user_agent": self.config.user_agent
            })
            
            try:
                if self.circuit_breaker:
                    response = await self.circuit_breaker.call(
                        self._make_request, method, url, **kwargs
                    )
                else:
                    response = await self._make_request(method, url, **kwargs)
                
                span.set_attributes({
                    "http.status_code": response.status,
                    "http.response_size": response.content_length or 0
                })
                
                # Handle response
                content_type = response.headers.get('Content-Type', '').lower()
                
                if response.status >= 400:
                    error_text = await response.text()
                    span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status}"))
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=error_text
                    )
                
                if 'application/json' in content_type:
                    data = await response.json()
                else:
                    data = await response.text()
                
                span.set_status(Status(StatusCode.OK))
                return {
                    'status': response.status,
                    'headers': dict(response.headers),
                    'data': data
                }
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attribute("error", True)
                raise
    
    # Convenience methods
    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """GET request"""
        return await self.request('GET', url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """POST request"""
        return await self.request('POST', url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> Dict[str, Any]:
        """PUT request"""
        return await self.request('PUT', url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """DELETE request"""
        return await self.request('DELETE', url, **kwargs)
    
    async def patch(self, url: str, **kwargs) -> Dict[str, Any]:
        """PATCH request"""
        return await self.request('PATCH', url, **kwargs)


# Factory function for easy client creation
def create_http_client(name: str, config: HTTPClientConfig = None) -> DianaHTTPClient:
    """Create a new Diana HTTP client instance"""
    return DianaHTTPClient(name, config)


# Context manager for temporary clients
@asynccontextmanager
async def http_client(name: str, config: HTTPClientConfig = None):
    """Context manager for temporary HTTP clients"""
    client = DianaHTTPClient(name, config)
    try:
        async with client:
            yield client
    finally:
        pass