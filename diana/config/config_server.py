"""
Diana Platform - Configuration Server
Centralized configuration management with hot reloading and versioning
"""

import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

import yaml
import consul.aio
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from prometheus_client import Counter, Gauge, Histogram

from ..core.base_service import DianaBaseService, ServiceConfig, ServiceInfo
from ..messaging.event_bus import DianaEventBus, DianaEvent, create_event, EventPriority


# Metrics
config_requests_total = Counter(
    'diana_config_requests_total',
    'Total configuration requests',
    ['service', 'config_key', 'status']
)

config_updates_total = Counter(
    'diana_config_updates_total',
    'Total configuration updates',
    ['service', 'config_key', 'source']
)

active_config_watchers = Gauge(
    'diana_active_config_watchers',
    'Number of active configuration watchers',
    ['service', 'config_key']
)

config_cache_size = Gauge(
    'diana_config_cache_size',
    'Configuration cache size',
    ['service']
)

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class ConfigSource(Enum):
    """Configuration source types"""
    FILE = "file"
    CONSUL = "consul"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    API = "api"


class ConfigFormat(Enum):
    """Configuration format types"""
    YAML = "yaml"
    JSON = "json"
    PROPERTIES = "properties"
    TOML = "toml"


@dataclass
class ConfigEntry:
    """Configuration entry with metadata"""
    key: str
    value: Any
    source: ConfigSource
    format: ConfigFormat
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    checksum: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'key': self.key,
            'value': self.value,
            'source': self.source.value,
            'format': self.format.value,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'checksum': self.checksum,
            'metadata': self.metadata
        }


@dataclass
class ConfigWatcher:
    """Configuration watcher for hot reloading"""
    service_name: str
    config_key: str
    callback: callable
    last_version: int = 0
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConfigServerConfig:
    """Configuration server settings"""
    config_directory: str = "/config"
    consul_host: str = "localhost"
    consul_port: int = 8500
    enable_file_watching: bool = True
    enable_consul_integration: bool = True
    cache_ttl_seconds: int = 300
    hot_reload_enabled: bool = True
    encryption_key: Optional[str] = None


class DianaConfigServer(DianaBaseService):
    """Centralized configuration server with hot reloading"""
    
    def __init__(self, config: ServiceConfig, server_config: ConfigServerConfig):
        super().__init__(config)
        self.server_config = server_config
        
        # Configuration storage
        self.config_cache: Dict[str, ConfigEntry] = {}
        self.watchers: Dict[str, List[ConfigWatcher]] = {}
        self.file_watchers: Set[str] = set()
        
        # External integrations
        self.consul_client: Optional[consul.aio.Consul] = None
        self.event_bus: Optional[DianaEventBus] = None
        
        # Background tasks
        self.file_watch_task: Optional[asyncio.Task] = None
        self.consul_watch_task: Optional[asyncio.Task] = None
        
        # Setup additional routes
        self._setup_config_routes()
        
        logger.info(f"Diana Configuration Server initialized")
    
    async def initialize(self) -> None:
        """Initialize configuration server"""
        # Load configurations from files
        await self._load_file_configurations()
        
        # Initialize Consul client
        if self.server_config.enable_consul_integration:
            await self._initialize_consul()
        
        # Initialize event bus for configuration change notifications
        if hasattr(self.config, 'rabbitmq_url') and self.config.custom_config.get('rabbitmq_url'):
            from ..messaging.event_bus import EventBusConfig, create_event_bus_config
            
            event_bus_config = create_event_bus_config(
                rabbitmq_url=self.config.custom_config['rabbitmq_url'],
                service_name=self.info.name
            )
            
            self.event_bus = DianaEventBus(event_bus_config)
            await self.event_bus.start()
        
        # Add health checks
        self.add_health_check("config_cache", self._health_check_config_cache)
        if self.consul_client:
            self.add_health_check("consul", self._health_check_consul)
    
    async def start_service(self) -> None:
        """Start configuration server specific components"""
        # Start file watching
        if self.server_config.enable_file_watching:
            self.file_watch_task = asyncio.create_task(self._file_watch_loop())
            self.background_tasks.add(self.file_watch_task)
        
        # Start Consul watching
        if self.consul_client:
            self.consul_watch_task = asyncio.create_task(self._consul_watch_loop())
            self.background_tasks.add(self.consul_watch_task)
        
        logger.info("Configuration server started successfully")
    
    async def stop_service(self) -> None:
        """Stop configuration server specific components"""
        # Stop background tasks
        if self.file_watch_task:
            self.file_watch_task.cancel()
        
        if self.consul_watch_task:
            self.consul_watch_task.cancel()
        
        # Close Consul client
        if self.consul_client:
            self.consul_client.http.close()
        
        # Stop event bus
        if self.event_bus:
            await self.event_bus.stop()
        
        logger.info("Configuration server stopped successfully")
    
    def _setup_config_routes(self):
        """Setup configuration-specific routes"""
        
        @self.app.get("/config/{service_name}/{config_key}")
        async def get_config(service_name: str, config_key: str):
            """Get configuration for a service"""
            
            with tracer.start_as_current_span("get_config") as span:
                span.set_attributes({
                    "config.service": service_name,
                    "config.key": config_key
                })
                
                try:
                    config_entry = await self._get_config_entry(service_name, config_key)
                    
                    if not config_entry:
                        span.set_status(Status(StatusCode.ERROR, "Config not found"))
                        config_requests_total.labels(
                            service=service_name,
                            config_key=config_key,
                            status="not_found"
                        ).inc()
                        raise HTTPException(status_code=404, detail="Configuration not found")
                    
                    config_requests_total.labels(
                        service=service_name,
                        config_key=config_key,
                        status="success"
                    ).inc()
                    
                    span.set_status(Status(StatusCode.OK))
                    return JSONResponse(content=config_entry.to_dict())
                    
                except HTTPException:
                    raise
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    config_requests_total.labels(
                        service=service_name,
                        config_key=config_key,
                        status="error"
                    ).inc()
                    raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/config/{service_name}/{config_key}")
        async def set_config(service_name: str, config_key: str, config_data: Dict[str, Any], background_tasks: BackgroundTasks):
            """Set configuration for a service"""
            
            with tracer.start_as_current_span("set_config") as span:
                span.set_attributes({
                    "config.service": service_name,
                    "config.key": config_key
                })
                
                try:
                    config_entry = ConfigEntry(
                        key=f"{service_name}.{config_key}",
                        value=config_data.get('value'),
                        source=ConfigSource.API,
                        format=ConfigFormat.JSON,
                        metadata=config_data.get('metadata', {})
                    )
                    
                    await self._store_config_entry(config_entry)
                    
                    # Schedule notification
                    background_tasks.add_task(
                        self._notify_config_change,
                        service_name,
                        config_key,
                        config_entry
                    )
                    
                    config_updates_total.labels(
                        service=service_name,
                        config_key=config_key,
                        source="api"
                    ).inc()
                    
                    span.set_status(Status(StatusCode.OK))
                    return JSONResponse(content={"success": True, "version": config_entry.version})
                    
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/config/{service_name}")
        async def get_service_config(service_name: str):
            """Get all configurations for a service"""
            
            configs = {}
            prefix = f"{service_name}."
            
            for key, entry in self.config_cache.items():
                if key.startswith(prefix):
                    config_key = key[len(prefix):]
                    configs[config_key] = entry.value
            
            return JSONResponse(content={
                "service": service_name,
                "configs": configs,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.post("/config/{service_name}/{config_key}/watch")
        async def watch_config(service_name: str, config_key: str, watch_data: Dict[str, Any]):
            """Register a configuration watcher"""
            
            callback_url = watch_data.get('callback_url')
            if not callback_url:
                raise HTTPException(status_code=400, detail="callback_url is required")
            
            # Create HTTP callback watcher
            async def http_callback(old_value, new_value, config_entry):
                if self.http_client:
                    try:
                        await self.http_client.post(callback_url, json={
                            'service': service_name,
                            'config_key': config_key,
                            'old_value': old_value,
                            'new_value': new_value,
                            'version': config_entry.version,
                            'timestamp': datetime.now().isoformat()
                        })
                    except Exception as e:
                        logger.error(f"Failed to notify watcher: {str(e)}")
            
            watcher = ConfigWatcher(
                service_name=service_name,
                config_key=config_key,
                callback=http_callback
            )
            
            full_key = f"{service_name}.{config_key}"
            if full_key not in self.watchers:
                self.watchers[full_key] = []
            
            self.watchers[full_key].append(watcher)
            
            active_config_watchers.labels(
                service=service_name,
                config_key=config_key
            ).inc()
            
            return JSONResponse(content={
                "success": True,
                "watcher_id": str(uuid.uuid4()),
                "message": f"Watcher registered for {service_name}.{config_key}"
            })
        
        @self.app.get("/config/cache/stats")
        async def get_cache_stats():
            """Get configuration cache statistics"""
            
            stats = {
                "total_configs": len(self.config_cache),
                "cache_size_mb": sum(len(str(entry.value)) for entry in self.config_cache.values()) / (1024 * 1024),
                "watchers_count": sum(len(watchers) for watchers in self.watchers.values()),
                "sources": {}
            }
            
            # Count by source
            for entry in self.config_cache.values():
                source = entry.source.value
                if source not in stats["sources"]:
                    stats["sources"][source] = 0
                stats["sources"][source] += 1
            
            config_cache_size.labels(service=self.info.name).set(stats["total_configs"])
            
            return JSONResponse(content=stats)
    
    async def _load_file_configurations(self):
        """Load configurations from files"""
        config_dir = Path(self.server_config.config_directory)
        
        if not config_dir.exists():
            logger.warning(f"Configuration directory does not exist: {config_dir}")
            return
        
        for file_path in config_dir.rglob("*.yml"):
            await self._load_config_file(file_path)
        
        for file_path in config_dir.rglob("*.yaml"):
            await self._load_config_file(file_path)
        
        for file_path in config_dir.rglob("*.json"):
            await self._load_config_file(file_path)
        
        logger.info(f"Loaded {len(self.config_cache)} configurations from files")
    
    async def _load_config_file(self, file_path: Path):
        """Load configuration from a single file"""
        try:
            # Determine service name from filename or directory
            service_name = file_path.stem
            
            with open(file_path, 'r') as f:
                if file_path.suffix in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                    format_type = ConfigFormat.YAML
                elif file_path.suffix == '.json':
                    data = json.load(f)
                    format_type = ConfigFormat.JSON
                else:
                    logger.warning(f"Unsupported file format: {file_path}")
                    return
            
            # Store configuration entries
            for key, value in data.items():
                config_entry = ConfigEntry(
                    key=f"{service_name}.{key}",
                    value=value,
                    source=ConfigSource.FILE,
                    format=format_type,
                    metadata={"file_path": str(file_path)}
                )
                
                self.config_cache[config_entry.key] = config_entry
                self.file_watchers.add(str(file_path))
            
            logger.debug(f"Loaded configuration from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load config file {file_path}: {str(e)}")
    
    async def _initialize_consul(self):
        """Initialize Consul client"""
        try:
            self.consul_client = consul.aio.Consul(
                host=self.server_config.consul_host,
                port=self.server_config.consul_port
            )
            
            # Test connection
            await self.consul_client.agent.services()
            logger.info("Consul client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Consul client: {str(e)}")
            self.consul_client = None
    
    async def _get_config_entry(self, service_name: str, config_key: str) -> Optional[ConfigEntry]:
        """Get configuration entry"""
        full_key = f"{service_name}.{config_key}"
        return self.config_cache.get(full_key)
    
    async def _store_config_entry(self, config_entry: ConfigEntry):
        """Store configuration entry"""
        # Check if configuration changed
        old_entry = self.config_cache.get(config_entry.key)
        
        if old_entry:
            config_entry.version = old_entry.version + 1
            config_entry.created_at = old_entry.created_at
        
        config_entry.updated_at = datetime.now()
        self.config_cache[config_entry.key] = config_entry
        
        # Store in Consul if available
        if self.consul_client:
            try:
                await self.consul_client.kv.put(
                    f"diana/config/{config_entry.key}",
                    json.dumps(config_entry.to_dict())
                )
            except Exception as e:
                logger.error(f"Failed to store config in Consul: {str(e)}")
        
        logger.info(f"Configuration stored: {config_entry.key} (version {config_entry.version})")
    
    async def _notify_config_change(self, service_name: str, config_key: str, config_entry: ConfigEntry):
        """Notify watchers about configuration changes"""
        full_key = f"{service_name}.{config_key}"
        watchers = self.watchers.get(full_key, [])
        
        if not watchers:
            return
        
        # Notify all watchers
        for watcher in watchers:
            if watcher.active:
                try:
                    await watcher.callback(None, config_entry.value, config_entry)
                    watcher.last_version = config_entry.version
                except Exception as e:
                    logger.error(f"Watcher callback failed: {str(e)}")
        
        # Publish event
        if self.event_bus:
            event = create_event(
                event_type="config.updated",
                data={
                    "service": service_name,
                    "config_key": config_key,
                    "version": config_entry.version,
                    "value": config_entry.value
                },
                priority=EventPriority.HIGH
            )
            
            await self.event_bus.publish_event(event, f"config.{service_name}.{config_key}")
    
    async def _file_watch_loop(self):
        """Watch configuration files for changes"""
        # This would use a proper file watcher in production (e.g., watchdog)
        # For now, we'll implement a simple polling mechanism
        
        last_modified_times = {}
        
        while not self.shutdown_event.is_set():
            try:
                for file_path in self.file_watchers:
                    path = Path(file_path)
                    if path.exists():
                        current_mtime = path.stat().st_mtime
                        last_mtime = last_modified_times.get(file_path, 0)
                        
                        if current_mtime > last_mtime:
                            last_modified_times[file_path] = current_mtime
                            await self._load_config_file(path)
                            logger.info(f"Reloaded configuration from {file_path}")
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"File watch error: {str(e)}")
                await asyncio.sleep(10)
    
    async def _consul_watch_loop(self):
        """Watch Consul for configuration changes"""
        if not self.consul_client:
            return
        
        index = None
        
        while not self.shutdown_event.is_set():
            try:
                index, data = await self.consul_client.kv.get(
                    "diana/config/",
                    index=index,
                    recurse=True,
                    wait="30s"
                )
                
                if data:
                    for item in data:
                        key = item['Key']
                        if key.startswith("diana/config/"):
                            config_key = key[13:]  # Remove "diana/config/" prefix
                            try:
                                config_data = json.loads(item['Value'])
                                # Process Consul configuration update
                                # This would trigger reload and notification
                            except Exception as e:
                                logger.error(f"Failed to process Consul config {key}: {str(e)}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Consul watch error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _health_check_config_cache(self) -> Dict[str, Any]:
        """Health check for configuration cache"""
        return {
            "status": "healthy",
            "cache_size": len(self.config_cache),
            "message": f"Configuration cache contains {len(self.config_cache)} entries"
        }
    
    async def _health_check_consul(self) -> Dict[str, Any]:
        """Health check for Consul connection"""
        if not self.consul_client:
            return {
                "status": "unhealthy",
                "message": "Consul client not initialized"
            }
        
        try:
            await self.consul_client.agent.self()
            return {
                "status": "healthy",
                "message": "Consul connection is healthy"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Consul connection failed: {str(e)}"
            }


# Factory function
def create_config_server(
    service_name: str = "diana-config-server",
    version: str = "1.0.0",
    port: int = 8080,
    **kwargs
) -> DianaConfigServer:
    """Create a Diana configuration server"""
    
    service_info = ServiceInfo(
        name=service_name,
        version=version,
        description="Diana Platform Configuration Server",
        port=port
    )
    
    service_config = ServiceConfig(service_info=service_info, **kwargs)
    server_config = ConfigServerConfig()
    
    return DianaConfigServer(service_config, server_config)