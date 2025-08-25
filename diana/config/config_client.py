"""
Diana Platform - Configuration Client
Dynamic configuration client with hot reloading and caching
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from dataclasses import dataclass, field
from enum import Enum

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from prometheus_client import Counter, Gauge, Histogram

from ..core.http_client import DianaHTTPClient, HTTPClientConfig, CircuitBreakerConfig


# Metrics
config_client_requests_total = Counter(
    'diana_config_client_requests_total',
    'Total configuration client requests',
    ['service', 'config_key', 'status']
)

config_client_cache_hits = Counter(
    'diana_config_client_cache_hits_total',
    'Configuration client cache hits',
    ['service', 'config_key']
)

config_client_cache_misses = Counter(
    'diana_config_client_cache_misses_total',
    'Configuration client cache misses',
    ['service', 'config_key']
)

config_client_updates_received = Counter(
    'diana_config_client_updates_received_total',
    'Configuration updates received',
    ['service', 'config_key']
)

config_client_cache_size = Gauge(
    'diana_config_client_cache_size',
    'Configuration client cache size',
    ['service']
)

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

T = TypeVar('T')


class ConfigChangeType(Enum):
    """Configuration change types"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


@dataclass
class ConfigValue:
    """Configuration value with metadata"""
    key: str
    value: Any
    version: int = 1
    last_updated: datetime = field(default_factory=datetime.now)
    source: str = "server"
    ttl: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if configuration value has expired"""
        if not self.ttl:
            return False
        
        return datetime.now() > self.last_updated + timedelta(seconds=self.ttl)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'key': self.key,
            'value': self.value,
            'version': self.version,
            'last_updated': self.last_updated.isoformat(),
            'source': self.source,
            'ttl': self.ttl
        }


@dataclass
class ConfigWatcherCallback:
    """Configuration watcher callback"""
    config_key: str
    callback: Callable[[str, Any, Any], None]  # (key, old_value, new_value)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigClientConfig:
    """Configuration client settings"""
    server_url: str
    service_name: str
    cache_ttl_seconds: int = 300
    refresh_interval_seconds: int = 60
    retry_attempts: int = 3
    timeout_seconds: int = 30
    enable_caching: bool = True
    enable_hot_reload: bool = True
    circuit_breaker_config: Optional[CircuitBreakerConfig] = field(default_factory=CircuitBreakerConfig)


class DianaConfigClient:
    """Diana platform configuration client with caching and hot reloading"""
    
    def __init__(self, config: ConfigClientConfig):
        self.config = config
        self.service_name = config.service_name
        
        # HTTP client for server communication
        http_config = HTTPClientConfig(
            timeout=config.timeout_seconds,
            max_retries=config.retry_attempts,
            circuit_breaker=config.circuit_breaker_config
        )
        
        self.http_client = DianaHTTPClient(f"{config.service_name}-config-client", http_config)
        
        # Configuration cache
        self.cache: Dict[str, ConfigValue] = {}
        self.watchers: List[ConfigWatcherCallback] = []
        
        # Background tasks
        self.refresh_task: Optional[asyncio.Task] = None
        self.shutdown_event = asyncio.Event()
        
        # Default values registry
        self.defaults: Dict[str, Any] = {}
        
        logger.info(f"Diana Config Client initialized for service '{self.service_name}'")
    
    async def start(self) -> None:
        """Start the configuration client"""
        logger.info(f"Starting configuration client for '{self.service_name}'...")
        
        try:
            # Start HTTP client
            await self.http_client.start()
            
            # Start background refresh if enabled
            if self.config.enable_hot_reload and self.config.refresh_interval_seconds > 0:
                self.refresh_task = asyncio.create_task(self._refresh_loop())
            
            logger.info(f"Configuration client started successfully for '{self.service_name}'")
            
        except Exception as e:
            logger.error(f"Failed to start configuration client: {str(e)}")
            raise
    
    async def stop(self) -> None:
        """Stop the configuration client"""
        logger.info(f"Stopping configuration client for '{self.service_name}'...")
        
        try:
            # Signal shutdown
            self.shutdown_event.set()
            
            # Stop background refresh task
            if self.refresh_task and not self.refresh_task.done():
                self.refresh_task.cancel()
                try:
                    await self.refresh_task
                except asyncio.CancelledError:
                    pass
            
            # Stop HTTP client
            await self.http_client.stop()
            
            logger.info(f"Configuration client stopped successfully for '{self.service_name}'")
            
        except Exception as e:
            logger.error(f"Error stopping configuration client: {str(e)}")
            raise
    
    async def get(self, config_key: str, default: T = None, force_refresh: bool = False) -> T:
        """
        Get configuration value
        
        Args:
            config_key: Configuration key
            default: Default value if config not found
            force_refresh: Force refresh from server
            
        Returns:
            Configuration value
        """
        
        with tracer.start_as_current_span(f"config_get_{config_key}") as span:
            span.set_attributes({
                "config.service": self.service_name,
                "config.key": config_key,
                "config.force_refresh": force_refresh
            })
            
            try:
                # Check cache first (unless force refresh)
                if not force_refresh and self.config.enable_caching:
                    cached_value = self._get_from_cache(config_key)
                    if cached_value is not None:
                        config_client_cache_hits.labels(
                            service=self.service_name,
                            config_key=config_key
                        ).inc()
                        
                        span.set_attribute("config.cache_hit", True)
                        span.set_status(Status(StatusCode.OK))
                        return cached_value
                
                # Cache miss - fetch from server
                config_client_cache_misses.labels(
                    service=self.service_name,
                    config_key=config_key
                ).inc()
                
                value = await self._fetch_from_server(config_key)
                
                if value is not None:
                    # Store in cache
                    if self.config.enable_caching:
                        self._store_in_cache(config_key, value)
                    
                    config_client_requests_total.labels(
                        service=self.service_name,
                        config_key=config_key,
                        status="success"
                    ).inc()
                    
                    span.set_attribute("config.cache_hit", False)
                    span.set_status(Status(StatusCode.OK))
                    return value
                else:
                    # Return default value
                    default_value = default if default is not None else self.defaults.get(config_key)
                    
                    config_client_requests_total.labels(
                        service=self.service_name,
                        config_key=config_key,
                        status="not_found"
                    ).inc()
                    
                    span.set_attribute("config.used_default", True)
                    span.set_status(Status(StatusCode.OK))
                    return default_value
                
            except Exception as e:
                config_client_requests_total.labels(
                    service=self.service_name,
                    config_key=config_key,
                    status="error"
                ).inc()
                
                span.set_status(Status(StatusCode.ERROR, str(e)))
                logger.error(f"Failed to get configuration '{config_key}': {str(e)}")
                
                # Return default on error
                return default if default is not None else self.defaults.get(config_key)
    
    async def get_all(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get all configurations for the service
        
        Args:
            force_refresh: Force refresh from server
            
        Returns:
            Dictionary of all configurations
        """
        
        with tracer.start_as_current_span("config_get_all") as span:
            span.set_attributes({
                "config.service": self.service_name,
                "config.force_refresh": force_refresh
            })
            
            try:
                response = await self.http_client.get(
                    f"{self.config.server_url}/config/{self.service_name}"
                )
                
                if response['status'] == 200:
                    configs = response['data'].get('configs', {})
                    
                    # Update cache
                    if self.config.enable_caching:
                        for key, value in configs.items():
                            self._store_in_cache(key, value)
                    
                    span.set_status(Status(StatusCode.OK))
                    return configs
                else:
                    span.set_status(Status(StatusCode.ERROR, f"HTTP {response['status']}"))
                    return {}
                    
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                logger.error(f"Failed to get all configurations: {str(e)}")
                return {}
    
    async def set(self, config_key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Set configuration value
        
        Args:
            config_key: Configuration key
            value: Configuration value
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        
        with tracer.start_as_current_span(f"config_set_{config_key}") as span:
            span.set_attributes({
                "config.service": self.service_name,
                "config.key": config_key
            })
            
            try:
                data = {
                    'value': value,
                    'metadata': metadata or {}
                }
                
                response = await self.http_client.post(
                    f"{self.config.server_url}/config/{self.service_name}/{config_key}",
                    json=data
                )
                
                if response['status'] == 200:
                    # Update local cache
                    if self.config.enable_caching:
                        self._store_in_cache(config_key, value)
                    
                    span.set_status(Status(StatusCode.OK))
                    return True
                else:
                    span.set_status(Status(StatusCode.ERROR, f"HTTP {response['status']}"))
                    return False
                    
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                logger.error(f"Failed to set configuration '{config_key}': {str(e)}")
                return False
    
    def set_default(self, config_key: str, value: Any) -> None:
        """
        Set default value for a configuration key
        
        Args:
            config_key: Configuration key
            value: Default value
        """
        self.defaults[config_key] = value
        logger.debug(f"Set default value for '{config_key}': {value}")
    
    def watch(self, config_key: str, callback: Callable[[str, Any, Any], None]) -> None:
        """
        Watch configuration key for changes
        
        Args:
            config_key: Configuration key to watch
            callback: Callback function (key, old_value, new_value)
        """
        watcher = ConfigWatcherCallback(
            config_key=config_key,
            callback=callback
        )
        
        self.watchers.append(watcher)
        logger.info(f"Added watcher for configuration key '{config_key}'")
    
    def unwatch(self, config_key: str) -> None:
        """
        Stop watching configuration key
        
        Args:
            config_key: Configuration key to stop watching
        """
        self.watchers = [w for w in self.watchers if w.config_key != config_key or not w.active]
        logger.info(f"Removed watcher for configuration key '{config_key}'")
    
    async def refresh(self, config_key: Optional[str] = None) -> None:
        """
        Refresh configuration from server
        
        Args:
            config_key: Specific key to refresh, or None for all
        """
        if config_key:
            await self.get(config_key, force_refresh=True)
        else:
            await self.get_all(force_refresh=True)
        
        logger.debug(f"Refreshed configuration{'s' if not config_key else f' for {config_key}'}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get configuration cache statistics"""
        now = datetime.now()
        expired_count = sum(1 for v in self.cache.values() if v.is_expired())
        
        stats = {
            "cache_size": len(self.cache),
            "expired_entries": expired_count,
            "active_watchers": len([w for w in self.watchers if w.active]),
            "service_name": self.service_name,
            "last_refresh": now.isoformat()
        }
        
        config_client_cache_size.labels(service=self.service_name).set(len(self.cache))
        return stats
    
    def _get_from_cache(self, config_key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        cached_value = self.cache.get(config_key)
        
        if cached_value and not cached_value.is_expired():
            return cached_value.value
        
        # Remove expired entry
        if cached_value:
            del self.cache[config_key]
        
        return None
    
    def _store_in_cache(self, config_key: str, value: Any, version: int = 1) -> None:
        """Store value in cache"""
        config_value = ConfigValue(
            key=config_key,
            value=value,
            version=version,
            ttl=self.config.cache_ttl_seconds
        )
        
        self.cache[config_key] = config_value
    
    async def _fetch_from_server(self, config_key: str) -> Optional[Any]:
        """Fetch configuration from server"""
        try:
            response = await self.http_client.get(
                f"{self.config.server_url}/config/{self.service_name}/{config_key}"
            )
            
            if response['status'] == 200:
                config_data = response['data']
                return config_data.get('value')
            elif response['status'] == 404:
                return None  # Configuration not found
            else:
                logger.error(f"Server returned status {response['status']} for config '{config_key}'")
                return None
                
        except Exception as e:
            logger.error(f"Failed to fetch config '{config_key}' from server: {str(e)}")
            return None
    
    async def _refresh_loop(self):
        """Background refresh loop for hot reloading"""
        while not self.shutdown_event.is_set():
            try:
                # Refresh all cached configurations
                for config_key in list(self.cache.keys()):
                    old_value = self.cache[config_key].value
                    
                    try:
                        new_value = await self._fetch_from_server(config_key)
                        
                        if new_value is not None and new_value != old_value:
                            # Configuration changed
                            self._store_in_cache(config_key, new_value)
                            
                            # Notify watchers
                            await self._notify_watchers(config_key, old_value, new_value)
                            
                            config_client_updates_received.labels(
                                service=self.service_name,
                                config_key=config_key
                            ).inc()
                            
                            logger.info(f"Configuration updated: {config_key}")
                            
                    except Exception as e:
                        logger.error(f"Failed to refresh config '{config_key}': {str(e)}")
                
                # Wait for next refresh
                await asyncio.sleep(self.config.refresh_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Refresh loop error: {str(e)}")
                await asyncio.sleep(self.config.refresh_interval_seconds)
    
    async def _notify_watchers(self, config_key: str, old_value: Any, new_value: Any):
        """Notify watchers about configuration changes"""
        for watcher in self.watchers:
            if watcher.config_key == config_key and watcher.active:
                try:
                    if asyncio.iscoroutinefunction(watcher.callback):
                        await watcher.callback(config_key, old_value, new_value)
                    else:
                        watcher.callback(config_key, old_value, new_value)
                        
                except Exception as e:
                    logger.error(f"Watcher callback failed for '{config_key}': {str(e)}")
    
    # Context manager support
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()


# Utility functions and decorators
def config_property(config_client: DianaConfigClient, key: str, default: Any = None):
    """
    Decorator to create a configuration property
    
    Usage:
        @config_property(config_client, "database.host", "localhost")
        def database_host(self):
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await config_client.get(key, default)
        return wrapper
    return decorator


class ConfigManager:
    """High-level configuration manager for services"""
    
    def __init__(self, config_client: DianaConfigClient):
        self.client = config_client
        self._config_cache: Dict[str, Any] = {}
    
    async def __aenter__(self):
        await self.client.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.stop()
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            'host': self._config_cache.get('database.host', 'localhost'),
            'port': self._config_cache.get('database.port', 5432),
            'database': self._config_cache.get('database.name', 'diana'),
            'username': self._config_cache.get('database.username', 'diana'),
            'password': self._config_cache.get('database.password', 'password')
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        return {
            'host': self._config_cache.get('redis.host', 'localhost'),
            'port': self._config_cache.get('redis.port', 6379),
            'database': self._config_cache.get('redis.database', 0),
            'password': self._config_cache.get('redis.password')
        }
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags"""
        return {
            'enable_metrics': self._config_cache.get('features.metrics', True),
            'enable_tracing': self._config_cache.get('features.tracing', True),
            'enable_caching': self._config_cache.get('features.caching', True),
            'debug_mode': self._config_cache.get('features.debug', False)
        }
    
    async def refresh_all(self):
        """Refresh all configurations"""
        configs = await self.client.get_all(force_refresh=True)
        self._config_cache.update(configs)


# Factory function
def create_config_client(
    server_url: str,
    service_name: str,
    **kwargs
) -> DianaConfigClient:
    """Create a Diana configuration client"""
    config = ConfigClientConfig(
        server_url=server_url,
        service_name=service_name,
        **kwargs
    )
    
    return DianaConfigClient(config)