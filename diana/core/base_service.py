"""
Diana Platform - Base Service Class
Enterprise service foundation with health checks, metrics, and lifecycle management
"""

import asyncio
import logging
import signal
import sys
import time
import uuid
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

import yaml
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from .http_client import DianaHTTPClient, HTTPClientConfig


# Service metrics
service_start_time = Gauge('diana_service_start_time', 'Service start time', ['service'])
service_health_status = Gauge('diana_service_health', 'Service health status (1=healthy, 0=unhealthy)', ['service'])
service_requests_total = Counter('diana_service_requests_total', 'Total service requests', ['service', 'endpoint', 'method'])
service_request_duration = Histogram('diana_service_request_duration_seconds', 'Service request duration', ['service', 'endpoint'])
service_errors_total = Counter('diana_service_errors_total', 'Total service errors', ['service', 'error_type'])

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class ServiceState(Enum):
    """Service lifecycle states"""
    INITIALIZING = "initializing"
    STARTING = "starting" 
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ServiceInfo:
    """Service metadata"""
    name: str
    version: str
    description: str
    port: int
    environment: str = "development"
    startup_time: Optional[datetime] = None
    service_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class HealthStatus:
    """Health check status"""
    status: str  # "healthy", "unhealthy", "degraded"
    checks: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    uptime: Optional[float] = None


@dataclass
class ServiceConfig:
    """Base service configuration"""
    service_info: ServiceInfo
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["*"])
    cors_headers: List[str] = field(default_factory=lambda: ["*"])
    metrics_enabled: bool = True
    tracing_enabled: bool = True
    health_check_interval: int = 30
    graceful_shutdown_timeout: int = 30
    
    # External service configurations
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    rabbitmq_url: Optional[str] = None
    
    # Custom service configuration
    custom_config: Dict[str, Any] = field(default_factory=dict)


class DianaBaseService(ABC):
    """Enterprise base service class for Diana platform"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.info = config.service_info
        self.state = ServiceState.INITIALIZING
        self.app = FastAPI(
            title=self.info.name,
            version=self.info.version,
            description=self.info.description
        )
        
        # Service components
        self.http_client: Optional[DianaHTTPClient] = None
        self.health_checks: Dict[str, callable] = {}
        self.background_tasks: Set[asyncio.Task] = set()
        self.shutdown_event = asyncio.Event()
        
        # Metrics
        self.start_time = time.time()
        service_start_time.labels(service=self.info.name).set(self.start_time)
        
        # Setup FastAPI
        self._setup_fastapi()
        self._setup_middleware()
        self._setup_routes()
        
        # Signal handlers
        self._setup_signal_handlers()
        
        logger.info(f"Service '{self.info.name}' initialized with ID: {self.info.service_id}")
    
    def _setup_fastapi(self):
        """Setup FastAPI application"""
        # Add custom configuration to app state
        self.app.state.service = self
        self.app.state.config = self.config
        self.app.state.start_time = self.start_time
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=self.config.cors_methods,
            allow_headers=self.config.cors_headers,
        )
        
        # Request tracking middleware
        @self.app.middleware("http")
        async def track_requests(request, call_next):
            start_time = time.time()
            path = request.url.path
            method = request.method
            
            # Add correlation ID
            correlation_id = request.headers.get("X-Correlation-ID", f"{self.info.name}-{uuid.uuid4()}")
            
            with tracer.start_as_current_span(f"{self.info.name}_{method}_{path}") as span:
                span.set_attributes({
                    "service.name": self.info.name,
                    "service.version": self.info.version,
                    "http.method": method,
                    "http.path": path,
                    "correlation.id": correlation_id
                })
                
                try:
                    response = await call_next(request)
                    duration = time.time() - start_time
                    
                    # Record metrics
                    service_requests_total.labels(
                        service=self.info.name,
                        endpoint=path,
                        method=method
                    ).inc()
                    
                    service_request_duration.labels(
                        service=self.info.name,
                        endpoint=path
                    ).observe(duration)
                    
                    span.set_attributes({
                        "http.status_code": response.status_code,
                        "http.response_time": duration
                    })
                    
                    # Add correlation ID to response headers
                    response.headers["X-Correlation-ID"] = correlation_id
                    
                    if response.status_code >= 400:
                        span.set_status(Status(StatusCode.ERROR))
                        service_errors_total.labels(
                            service=self.info.name,
                            error_type=f"http_{response.status_code}"
                        ).inc()
                    else:
                        span.set_status(Status(StatusCode.OK))
                    
                    return response
                    
                except Exception as e:
                    duration = time.time() - start_time
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    
                    service_errors_total.labels(
                        service=self.info.name,
                        error_type=type(e).__name__
                    ).inc()
                    
                    logger.error(f"Request failed: {method} {path} - {str(e)}")
                    raise
    
    def _setup_routes(self):
        """Setup standard service routes"""
        
        @self.app.get("/health", response_model=Dict[str, Any])
        async def health_check():
            """Service health check endpoint"""
            health = await self.get_health_status()
            status_code = 200 if health.status == "healthy" else 503
            
            return JSONResponse(
                status_code=status_code,
                content={
                    "status": health.status,
                    "service": self.info.name,
                    "version": self.info.version,
                    "timestamp": health.timestamp.isoformat(),
                    "uptime": health.uptime,
                    "checks": health.checks
                }
            )
        
        @self.app.get("/ready", response_model=Dict[str, Any])
        async def readiness_check():
            """Service readiness check endpoint"""
            ready = await self.is_ready()
            status_code = 200 if ready else 503
            
            return JSONResponse(
                status_code=status_code,
                content={
                    "ready": ready,
                    "service": self.info.name,
                    "state": self.state.value,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        @self.app.get("/info", response_model=Dict[str, Any])
        async def service_info():
            """Service information endpoint"""
            return {
                "name": self.info.name,
                "version": self.info.version,
                "description": self.info.description,
                "service_id": self.info.service_id,
                "environment": self.info.environment,
                "state": self.state.value,
                "startup_time": self.info.startup_time.isoformat() if self.info.startup_time else None,
                "uptime": time.time() - self.start_time
            }
        
        if self.config.metrics_enabled:
            @self.app.get("/metrics")
            async def metrics():
                """Prometheus metrics endpoint"""
                return generate_latest()
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    # Abstract methods that services must implement
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize service-specific components"""
        pass
    
    @abstractmethod
    async def start_service(self) -> None:
        """Start service-specific components"""
        pass
    
    @abstractmethod
    async def stop_service(self) -> None:
        """Stop service-specific components"""
        pass
    
    # Service lifecycle management
    async def start(self) -> None:
        """Start the service"""
        try:
            self.state = ServiceState.STARTING
            logger.info(f"Starting service '{self.info.name}'...")
            
            # Initialize HTTP client
            self.http_client = DianaHTTPClient(
                name=f"{self.info.name}-client",
                config=HTTPClientConfig()
            )
            await self.http_client.start()
            
            # Initialize service-specific components
            await self.initialize()
            
            # Start service-specific components
            await self.start_service()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Mark as running
            self.state = ServiceState.RUNNING
            self.info.startup_time = datetime.now()
            
            # Update health status
            service_health_status.labels(service=self.info.name).set(1)
            
            logger.info(f"Service '{self.info.name}' started successfully")
            
        except Exception as e:
            self.state = ServiceState.ERROR
            service_health_status.labels(service=self.info.name).set(0)
            logger.error(f"Failed to start service '{self.info.name}': {str(e)}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the service gracefully"""
        if self.state in [ServiceState.STOPPING, ServiceState.STOPPED]:
            return
        
        try:
            self.state = ServiceState.STOPPING
            logger.info(f"Shutting down service '{self.info.name}'...")
            
            # Signal shutdown to all components
            self.shutdown_event.set()
            
            # Stop background tasks
            await self._stop_background_tasks()
            
            # Stop service-specific components
            await self.stop_service()
            
            # Stop HTTP client
            if self.http_client:
                await self.http_client.stop()
            
            self.state = ServiceState.STOPPED
            service_health_status.labels(service=self.info.name).set(0)
            
            logger.info(f"Service '{self.info.name}' shutdown completed")
            
        except Exception as e:
            self.state = ServiceState.ERROR
            logger.error(f"Error during shutdown of service '{self.info.name}': {str(e)}")
            raise
    
    async def _start_background_tasks(self):
        """Start background monitoring tasks"""
        # Health check task
        if self.config.health_check_interval > 0:
            task = asyncio.create_task(self._health_check_loop())
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
    
    async def _stop_background_tasks(self):
        """Stop all background tasks"""
        for task in self.background_tasks:
            if not task.done():
                task.cancel()
        
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        self.background_tasks.clear()
    
    async def _health_check_loop(self):
        """Background health check loop"""
        while not self.shutdown_event.is_set():
            try:
                health = await self.get_health_status()
                
                # Update metrics based on health status
                if health.status == "healthy":
                    service_health_status.labels(service=self.info.name).set(1)
                else:
                    service_health_status.labels(service=self.info.name).set(0)
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {str(e)}")
                await asyncio.sleep(self.config.health_check_interval)
    
    # Health check methods
    def add_health_check(self, name: str, check_func: callable):
        """Add a custom health check"""
        self.health_checks[name] = check_func
    
    async def get_health_status(self) -> HealthStatus:
        """Get comprehensive health status"""
        checks = {}
        overall_status = "healthy"
        
        # Basic service state check
        checks["service_state"] = {
            "status": "healthy" if self.state == ServiceState.RUNNING else "unhealthy",
            "state": self.state.value,
            "message": f"Service is {self.state.value}"
        }
        
        if self.state != ServiceState.RUNNING:
            overall_status = "unhealthy"
        
        # Run custom health checks
        for name, check_func in self.health_checks.items():
            try:
                check_result = await check_func()
                checks[name] = check_result
                
                if check_result.get("status") != "healthy":
                    overall_status = "degraded" if overall_status == "healthy" else "unhealthy"
                    
            except Exception as e:
                checks[name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "message": f"Health check '{name}' failed"
                }
                overall_status = "unhealthy"
        
        # Calculate uptime
        uptime = time.time() - self.start_time if self.info.startup_time else None
        
        return HealthStatus(
            status=overall_status,
            checks=checks,
            uptime=uptime
        )
    
    async def is_ready(self) -> bool:
        """Check if service is ready to accept requests"""
        return self.state == ServiceState.RUNNING
    
    # Configuration methods
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.custom_config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config.custom_config[key] = value
    
    @classmethod
    def load_config_from_file(cls, config_path: str) -> ServiceConfig:
        """Load service configuration from YAML file"""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Extract service info
        service_info = ServiceInfo(**config_data.get('service_info', {}))
        
        # Create service config
        config = ServiceConfig(service_info=service_info)
        
        # Apply configuration values
        for key, value in config_data.items():
            if key != 'service_info' and hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    # Context manager support
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.shutdown()


# Utility functions
def create_service_config(
    name: str,
    version: str,
    description: str,
    port: int,
    **kwargs
) -> ServiceConfig:
    """Create a service configuration"""
    service_info = ServiceInfo(
        name=name,
        version=version,
        description=description,
        port=port
    )
    
    return ServiceConfig(service_info=service_info, **kwargs)


@asynccontextmanager
async def diana_service(service: DianaBaseService):
    """Context manager for Diana services"""
    try:
        async with service:
            yield service
    finally:
        pass