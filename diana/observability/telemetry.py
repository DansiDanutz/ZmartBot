"""
Diana Platform - OpenTelemetry Observability
Comprehensive observability with distributed tracing, metrics, and logging
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager, asynccontextmanager
from functools import wraps

from opentelemetry import trace, metrics, baggage
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.propagators.composite import CompositeHTTPPropagator
from opentelemetry.propagators.jaeger import JaegerPropagator
from opentelemetry.sdk.trace import TracerProvider, sampling
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Status, StatusCode
from opentelemetry.util.http import get_excluded_urls
from prometheus_client import CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST

# Custom Diana imports
from ..core.http_client import DianaHTTPClient


logger = logging.getLogger(__name__)


@dataclass
class TelemetryConfig:
    """OpenTelemetry configuration"""
    service_name: str
    service_version: str = "1.0.0"
    environment: str = "production"
    
    # Tracing configuration
    enable_tracing: bool = True
    jaeger_endpoint: str = "http://localhost:14268/api/traces"
    otlp_endpoint: str = "http://localhost:4317"
    trace_sampling_ratio: float = 1.0
    
    # Metrics configuration
    enable_metrics: bool = True
    prometheus_port: int = 9090
    metrics_export_interval: int = 10
    
    # Logging configuration
    enable_logging_instrumentation: bool = True
    log_correlation: bool = True
    
    # Instrumentation configuration
    instrument_fastapi: bool = True
    instrument_aiohttp: bool = True
    instrument_asyncio: bool = True
    instrument_database: bool = True
    instrument_redis: bool = True
    
    # Baggage configuration
    enable_baggage: bool = True
    
    # Custom attributes
    custom_resource_attributes: Dict[str, str] = field(default_factory=dict)


class DianaTracer:
    """Enhanced tracer with Diana-specific functionality"""
    
    def __init__(self, name: str, tracer: trace.Tracer):
        self.name = name
        self.tracer = tracer
        self._active_spans: Dict[str, trace.Span] = {}
    
    def start_span(self, name: str, **kwargs) -> trace.Span:
        """Start a new span with Diana enhancements"""
        span = self.tracer.start_span(name, **kwargs)
        
        # Add common Diana attributes
        span.set_attribute("diana.service", self.name)
        span.set_attribute("diana.timestamp", datetime.now().isoformat())
        
        return span
    
    @contextmanager
    def span(self, name: str, **kwargs):
        """Context manager for spans"""
        span = self.start_span(name, **kwargs)
        try:
            with trace.use_span(span):
                yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise
        finally:
            span.end()
    
    @asynccontextmanager
    async def async_span(self, name: str, **kwargs):
        """Async context manager for spans"""
        span = self.start_span(name, **kwargs)
        try:
            with trace.use_span(span):
                yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise
        finally:
            span.end()
    
    def trace_function(self, operation_name: str = None, attributes: Dict[str, Any] = None):
        """Decorator to trace functions"""
        def decorator(func):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    with self.span(op_name) as span:
                        if attributes:
                            for key, value in attributes.items():
                                span.set_attribute(key, value)
                        
                        # Add function metadata
                        span.set_attribute("code.function", func.__name__)
                        span.set_attribute("code.namespace", func.__module__)
                        
                        try:
                            result = await func(*args, **kwargs)
                            span.set_status(Status(StatusCode.OK))
                            return result
                        except Exception as e:
                            span.record_exception(e)
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                            raise
                
                return async_wrapper
            else:
                @wraps(func)
                def wrapper(*args, **kwargs):
                    with self.span(op_name) as span:
                        if attributes:
                            for key, value in attributes.items():
                                span.set_attribute(key, value)
                        
                        # Add function metadata
                        span.set_attribute("code.function", func.__name__)
                        span.set_attribute("code.namespace", func.__module__)
                        
                        try:
                            result = func(*args, **kwargs)
                            span.set_status(Status(StatusCode.OK))
                            return result
                        except Exception as e:
                            span.record_exception(e)
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                            raise
                
                return wrapper
        
        return decorator
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """Add an event to the current span"""
        current_span = trace.get_current_span()
        if current_span:
            current_span.add_event(name, attributes or {})


class DianaMeter:
    """Enhanced meter with Diana-specific functionality"""
    
    def __init__(self, name: str, meter: metrics.Meter):
        self.name = name
        self.meter = meter
        self._instruments: Dict[str, Any] = {}
    
    def create_counter(self, name: str, description: str = "", unit: str = ""):
        """Create a counter instrument"""
        if name not in self._instruments:
            self._instruments[name] = self.meter.create_counter(
                name=f"diana_{name}",
                description=description,
                unit=unit
            )
        return self._instruments[name]
    
    def create_histogram(self, name: str, description: str = "", unit: str = ""):
        """Create a histogram instrument"""
        if name not in self._instruments:
            self._instruments[name] = self.meter.create_histogram(
                name=f"diana_{name}",
                description=description,
                unit=unit
            )
        return self._instruments[name]
    
    def create_gauge(self, name: str, description: str = "", unit: str = ""):
        """Create a gauge instrument"""
        if name not in self._instruments:
            self._instruments[name] = self.meter.create_observable_gauge(
                name=f"diana_{name}",
                description=description,
                unit=unit
            )
        return self._instruments[name]


class DianaTelemetry:
    """Diana Platform Telemetry Manager"""
    
    def __init__(self, config: TelemetryConfig):
        self.config = config
        self.resource = self._create_resource()
        
        # Providers
        self.tracer_provider: Optional[TracerProvider] = None
        self.meter_provider: Optional[MeterProvider] = None
        
        # Diana enhanced wrappers
        self.tracers: Dict[str, DianaTracer] = {}
        self.meters: Dict[str, DianaMeter] = {}
        
        # Instrumentation tracking
        self._instrumentation_enabled = set()
        
        logger.info(f"Diana Telemetry initialized for service '{config.service_name}'")
    
    def _create_resource(self) -> Resource:
        """Create OpenTelemetry resource with Diana attributes"""
        attributes = {
            SERVICE_NAME: self.config.service_name,
            SERVICE_VERSION: self.config.service_version,
            "service.environment": self.config.environment,
            "service.platform": "diana",
            "service.runtime": "python",
            **self.config.custom_resource_attributes
        }
        
        return Resource.create(attributes)
    
    async def initialize(self) -> None:
        """Initialize telemetry components"""
        logger.info("Initializing Diana Telemetry...")
        
        try:
            # Initialize tracing
            if self.config.enable_tracing:
                await self._setup_tracing()
            
            # Initialize metrics
            if self.config.enable_metrics:
                await self._setup_metrics()
            
            # Setup propagators
            self._setup_propagators()
            
            # Setup auto-instrumentation
            await self._setup_instrumentation()
            
            logger.info("Diana Telemetry initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize telemetry: {str(e)}")
            raise
    
    async def _setup_tracing(self) -> None:
        """Setup distributed tracing"""
        # Create tracer provider
        self.tracer_provider = TracerProvider(
            resource=self.resource,
            sampler=sampling.TraceIdRatioBased(self.config.trace_sampling_ratio)
        )
        
        # Setup exporters
        exporters = []
        
        # Jaeger exporter
        try:
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=14268,
                endpoint=self.config.jaeger_endpoint
            )
            exporters.append(jaeger_exporter)
            logger.info("Jaeger trace exporter configured")
        except Exception as e:
            logger.warning(f"Failed to setup Jaeger exporter: {str(e)}")
        
        # OTLP exporter
        try:
            otlp_exporter = OTLPSpanExporter(
                endpoint=self.config.otlp_endpoint,
                insecure=True
            )
            exporters.append(otlp_exporter)
            logger.info("OTLP trace exporter configured")
        except Exception as e:
            logger.warning(f"Failed to setup OTLP exporter: {str(e)}")
        
        # Add span processors
        for exporter in exporters:
            processor = BatchSpanProcessor(
                exporter,
                max_queue_size=2048,
                export_timeout_millis=30000,
                max_export_batch_size=512
            )
            self.tracer_provider.add_span_processor(processor)
        
        # Set global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        
        logger.info("Distributed tracing setup completed")
    
    async def _setup_metrics(self) -> None:
        """Setup metrics collection"""
        readers = []
        
        # Prometheus metrics reader
        try:
            prometheus_reader = PrometheusMetricReader()
            readers.append(prometheus_reader)
            logger.info("Prometheus metrics reader configured")
        except Exception as e:
            logger.warning(f"Failed to setup Prometheus reader: {str(e)}")
        
        # OTLP metrics reader
        try:
            otlp_reader = PeriodicExportingMetricReader(
                exporter=OTLPMetricExporter(
                    endpoint=self.config.otlp_endpoint,
                    insecure=True
                ),
                export_interval_millis=self.config.metrics_export_interval * 1000
            )
            readers.append(otlp_reader)
            logger.info("OTLP metrics reader configured")
        except Exception as e:
            logger.warning(f"Failed to setup OTLP metrics reader: {str(e)}")
        
        # Create meter provider
        self.meter_provider = MeterProvider(
            resource=self.resource,
            metric_readers=readers
        )
        
        # Set global meter provider
        metrics.set_meter_provider(self.meter_provider)
        
        logger.info("Metrics collection setup completed")
    
    def _setup_propagators(self) -> None:
        """Setup trace propagators"""
        propagators = [
            B3MultiFormat(),
            JaegerPropagator(),
        ]
        
        composite_propagator = CompositeHTTPPropagator(propagators)
        set_global_textmap(composite_propagator)
        
        logger.info("Trace propagators configured")
    
    async def _setup_instrumentation(self) -> None:
        """Setup auto-instrumentation"""
        
        # FastAPI instrumentation
        if self.config.instrument_fastapi:
            try:
                FastAPIInstrumentor().instrument()
                self._instrumentation_enabled.add("fastapi")
                logger.info("FastAPI instrumentation enabled")
            except Exception as e:
                logger.warning(f"Failed to instrument FastAPI: {str(e)}")
        
        # AioHTTP client instrumentation
        if self.config.instrument_aiohttp:
            try:
                AioHttpClientInstrumentor().instrument()
                self._instrumentation_enabled.add("aiohttp")
                logger.info("AioHTTP client instrumentation enabled")
            except Exception as e:
                logger.warning(f"Failed to instrument AioHTTP: {str(e)}")
        
        # Asyncio instrumentation
        if self.config.instrument_asyncio:
            try:
                AsyncioInstrumentor().instrument()
                self._instrumentation_enabled.add("asyncio")
                logger.info("Asyncio instrumentation enabled")
            except Exception as e:
                logger.warning(f"Failed to instrument Asyncio: {str(e)}")
        
        # Database instrumentation
        if self.config.instrument_database:
            try:
                SQLAlchemyInstrumentor().instrument()
                Psycopg2Instrumentor().instrument()
                self._instrumentation_enabled.add("database")
                logger.info("Database instrumentation enabled")
            except Exception as e:
                logger.warning(f"Failed to instrument databases: {str(e)}")
        
        # Redis instrumentation
        if self.config.instrument_redis:
            try:
                RedisInstrumentor().instrument()
                self._instrumentation_enabled.add("redis")
                logger.info("Redis instrumentation enabled")
            except Exception as e:
                logger.warning(f"Failed to instrument Redis: {str(e)}")
        
        # Logging instrumentation
        if self.config.enable_logging_instrumentation:
            try:
                LoggingInstrumentor().instrument(set_logging_format=True)
                self._instrumentation_enabled.add("logging")
                logger.info("Logging instrumentation enabled")
            except Exception as e:
                logger.warning(f"Failed to instrument logging: {str(e)}")
        
        logger.info(f"Auto-instrumentation setup completed: {self._instrumentation_enabled}")
    
    def get_tracer(self, name: str = None) -> DianaTracer:
        """Get Diana enhanced tracer"""
        tracer_name = name or self.config.service_name
        
        if tracer_name not in self.tracers:
            otel_tracer = trace.get_tracer(
                tracer_name,
                version=self.config.service_version
            )
            self.tracers[tracer_name] = DianaTracer(tracer_name, otel_tracer)
        
        return self.tracers[tracer_name]
    
    def get_meter(self, name: str = None) -> DianaMeter:
        """Get Diana enhanced meter"""
        meter_name = name or self.config.service_name
        
        if meter_name not in self.meters:
            otel_meter = metrics.get_meter(
                meter_name,
                version=self.config.service_version
            )
            self.meters[meter_name] = DianaMeter(meter_name, otel_meter)
        
        return self.meters[meter_name]
    
    def set_baggage(self, key: str, value: str) -> None:
        """Set baggage item"""
        if self.config.enable_baggage:
            baggage.set_baggage(key, value)
    
    def get_baggage(self, key: str) -> Optional[str]:
        """Get baggage item"""
        if self.config.enable_baggage:
            return baggage.get_baggage(key)
        return None
    
    def add_span_attribute(self, key: str, value: Any) -> None:
        """Add attribute to current span"""
        current_span = trace.get_current_span()
        if current_span:
            current_span.set_attribute(key, value)
    
    def add_span_event(self, name: str, attributes: Dict[str, Any] = None) -> None:
        """Add event to current span"""
        current_span = trace.get_current_span()
        if current_span:
            current_span.add_event(name, attributes or {})
    
    def record_exception(self, exception: Exception) -> None:
        """Record exception in current span"""
        current_span = trace.get_current_span()
        if current_span:
            current_span.record_exception(exception)
            current_span.set_status(Status(StatusCode.ERROR, str(exception)))
    
    async def shutdown(self) -> None:
        """Shutdown telemetry"""
        logger.info("Shutting down Diana Telemetry...")
        
        try:
            # Shutdown tracer provider
            if self.tracer_provider:
                self.tracer_provider.shutdown()
            
            # Shutdown meter provider
            if self.meter_provider:
                self.meter_provider.shutdown()
            
            logger.info("Diana Telemetry shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during telemetry shutdown: {str(e)}")
    
    def get_telemetry_info(self) -> Dict[str, Any]:
        """Get telemetry system information"""
        return {
            "service_name": self.config.service_name,
            "service_version": self.config.service_version,
            "environment": self.config.environment,
            "tracing_enabled": self.config.enable_tracing,
            "metrics_enabled": self.config.enable_metrics,
            "instrumentation_enabled": list(self._instrumentation_enabled),
            "active_tracers": list(self.tracers.keys()),
            "active_meters": list(self.meters.keys())
        }


# Global telemetry instance
_global_telemetry: Optional[DianaTelemetry] = None


def initialize_telemetry(config: TelemetryConfig) -> DianaTelemetry:
    """Initialize global telemetry"""
    global _global_telemetry
    _global_telemetry = DianaTelemetry(config)
    return _global_telemetry


async def setup_telemetry(config: TelemetryConfig) -> DianaTelemetry:
    """Setup and initialize telemetry"""
    telemetry = initialize_telemetry(config)
    await telemetry.initialize()
    return telemetry


def get_telemetry() -> Optional[DianaTelemetry]:
    """Get global telemetry instance"""
    return _global_telemetry


def get_tracer(name: str = None) -> DianaTracer:
    """Get global tracer"""
    if _global_telemetry:
        return _global_telemetry.get_tracer(name)
    
    # Fallback to basic OpenTelemetry tracer
    otel_tracer = trace.get_tracer(name or "diana-fallback")
    return DianaTracer(name or "diana-fallback", otel_tracer)


def get_meter(name: str = None) -> DianaMeter:
    """Get global meter"""
    if _global_telemetry:
        return _global_telemetry.get_meter(name)
    
    # Fallback to basic OpenTelemetry meter
    otel_meter = metrics.get_meter(name or "diana-fallback")
    return DianaMeter(name or "diana-fallback", otel_meter)


# Convenience decorators
def trace_function(operation_name: str = None, attributes: Dict[str, Any] = None):
    """Global function tracing decorator"""
    tracer = get_tracer()
    return tracer.trace_function(operation_name, attributes)


@contextmanager
def span(name: str, **kwargs):
    """Global span context manager"""
    tracer = get_tracer()
    with tracer.span(name, **kwargs) as s:
        yield s


@asynccontextmanager
async def async_span(name: str, **kwargs):
    """Global async span context manager"""
    tracer = get_tracer()
    async with tracer.async_span(name, **kwargs) as s:
        yield s


# Factory functions
def create_telemetry_config(
    service_name: str,
    service_version: str = "1.0.0",
    environment: str = "production",
    **kwargs
) -> TelemetryConfig:
    """Create telemetry configuration"""
    return TelemetryConfig(
        service_name=service_name,
        service_version=service_version,
        environment=environment,
        **kwargs
    )


# Diana service integration decorator
def telemetry_enabled(config: TelemetryConfig):
    """Decorator to enable telemetry for Diana services"""
    def decorator(service_class):
        original_initialize = service_class.initialize
        original_start_service = service_class.start_service
        original_stop_service = service_class.stop_service
        
        async def enhanced_initialize(self):
            # Initialize telemetry
            self.telemetry = await setup_telemetry(config)
            self.tracer = self.telemetry.get_tracer()
            self.meter = self.telemetry.get_meter()
            
            # Call original initialize
            await original_initialize(self)
        
        async def enhanced_start_service(self):
            with self.tracer.span("service_startup"):
                await original_start_service(self)
        
        async def enhanced_stop_service(self):
            with self.tracer.span("service_shutdown"):
                await original_stop_service(self)
                
                # Shutdown telemetry
                if hasattr(self, 'telemetry'):
                    await self.telemetry.shutdown()
        
        service_class.initialize = enhanced_initialize
        service_class.start_service = enhanced_start_service
        service_class.stop_service = enhanced_stop_service
        
        return service_class
    
    return decorator