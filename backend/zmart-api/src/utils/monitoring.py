"""
Zmart Trading Bot Platform - Monitoring Utilities
System monitoring and health check utilities
"""
import asyncio
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
import psutil

from src.config.settings import settings
from .database import check_database_health, write_metric

logger = logging.getLogger(__name__)

class SystemMonitor:
    """System monitoring and health check manager"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.metrics_interval = 120  # seconds (reduced from 60)
        self.health_check_interval = 120  # seconds (reduced from 30)
        self.is_running = False
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        
    async def start(self):
        """Start the system monitor"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Starting system monitor")
        
        # Start monitoring tasks
        await asyncio.gather(
            self._collect_system_metrics(),
            self._health_check_loop()
        )
    
    async def stop(self):
        """Stop the system monitor"""
        self.is_running = False
        logger.info("Stopping system monitor")
    
    async def _collect_system_metrics(self):
        """Collect system metrics periodically"""
        while self.is_running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.metrics_interval)
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(10)
    
    async def _health_check_loop(self):
        """Perform periodic health checks"""
        while self.is_running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Error performing health check: {e}")
                await asyncio.sleep(10)
    
    async def _collect_metrics(self):
        """Collect current system metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Try to write system metrics to InfluxDB, but don't fail if it doesn't work
            try:
                await write_metric(
                    measurement="system_metrics",
                    tags={"service": "zmart-api"},
                    fields={
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_used": memory.used,
                        "memory_total": memory.total,
                        "disk_percent": disk.percent,
                        "disk_used": disk.used,
                        "disk_total": disk.total
                    }
                )
            except Exception as e:
                # Log warning but don't fail
                logger.debug(f"Could not write metrics to InfluxDB: {e}")
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            try:
                await write_metric(
                    measurement="process_metrics",
                    tags={"service": "zmart-api"},
                    fields={
                        "memory_rss": process_memory.rss,
                        "memory_vms": process_memory.vms,
                        "cpu_percent": process.cpu_percent(),
                        "num_threads": process.num_threads(),
                        "num_fds": process.num_fds() if hasattr(process, 'num_fds') else 0
                    }
                )
            except Exception as e:
                # Log debug but don't fail
                logger.debug(f"Could not write process metrics to InfluxDB: {e}")
            
            logger.debug("System metrics collected successfully")
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    async def _perform_health_check(self):
        """Perform comprehensive health check"""
        try:
            # Database health
            db_health = await check_database_health()
            
            # System health
            system_health = {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "uptime": (datetime.utcnow() - self.start_time).total_seconds()
            }
            
            # Overall health status (more lenient for development)
            critical_services_healthy = db_health["redis"]  # Only require Redis for basic functionality
            overall_healthy = critical_services_healthy and system_health["cpu_usage"] < 90 and system_health["memory_usage"] < 90
            
            # Try to write health metrics, but don't fail if it doesn't work
            try:
                await write_metric(
                    measurement="health_check",
                    tags={"service": "zmart-api"},
                    fields={
                        "overall_healthy": overall_healthy,
                        "postgresql_healthy": db_health["postgresql"],
                        "redis_healthy": db_health["redis"],
                        "influxdb_healthy": db_health["influxdb"],
                        "cpu_usage": system_health["cpu_usage"],
                        "memory_usage": system_health["memory_usage"],
                        "disk_usage": system_health["disk_usage"],
                        "uptime_seconds": system_health["uptime"]
                    }
                )
            except Exception as e:
                # Log debug but don't fail
                logger.debug(f"Could not write health metrics to InfluxDB: {e}")
            
            if not overall_healthy:
                self.consecutive_failures += 1
                # Only log warnings after multiple consecutive failures
                if self.consecutive_failures >= self.max_consecutive_failures:
                    logger.warning(f"System health check failed {self.consecutive_failures} times: {db_health}, {system_health}")
                else:
                    logger.debug(f"Health check failed ({self.consecutive_failures}/{self.max_consecutive_failures}): {db_health}")
            else:
                if self.consecutive_failures > 0:
                    logger.info(f"System health recovered after {self.consecutive_failures} failures")
                self.consecutive_failures = 0
                logger.debug("Health check passed")
                
        except Exception as e:
            logger.error(f"Error performing health check: {e}")

# Global system monitor instance
system_monitor = SystemMonitor()

async def init_monitoring():
    """Initialize monitoring system"""
    if settings.METRICS_ENABLED:
        await system_monitor.start()

async def get_system_status() -> Dict[str, Any]:
    """Get current system status"""
    try:
        # Database health
        db_health = await check_database_health()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Process metrics
        process = psutil.Process()
        
        return {
            "status": "healthy" if all(db_health.values()) else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - system_monitor.start_time).total_seconds(),
            "databases": db_health,
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2)
            },
            "process": {
                "memory_rss_mb": round(process.memory_info().rss / (1024**2), 2),
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads(),
                "create_time": datetime.fromtimestamp(process.create_time()).isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

async def get_performance_metrics(time_range: str = "1h") -> Dict[str, Any]:
    """Get performance metrics for the specified time range"""
    try:
        from .database import query_metrics
        
        # Query system metrics
        system_query = f'''
        from(bucket: "{settings.INFLUX_BUCKET}")
            |> range(start: -{time_range})
            |> filter(fn: (r) => r["_measurement"] == "system_metrics")
            |> filter(fn: (r) => r["service"] == "zmart-api")
        '''
        
        # Query process metrics
        process_query = f'''
        from(bucket: "{settings.INFLUX_BUCKET}")
            |> range(start: -{time_range})
            |> filter(fn: (r) => r["_measurement"] == "process_metrics")
            |> filter(fn: (r) => r["service"] == "zmart-api")
        '''
        
        # Query health metrics
        health_query = f'''
        from(bucket: "{settings.INFLUX_BUCKET}")
            |> range(start: -{time_range})
            |> filter(fn: (r) => r["_measurement"] == "health_check")
            |> filter(fn: (r) => r["service"] == "zmart-api")
        '''
        
        system_metrics = await query_metrics(system_query)
        process_metrics = await query_metrics(process_query)
        health_metrics = await query_metrics(health_query)
        
        return {
            "system_metrics": system_metrics,
            "process_metrics": process_metrics,
            "health_metrics": health_metrics,
            "time_range": time_range
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return {
            "error": str(e),
            "time_range": time_range
        }

# Alerting system
class AlertManager:
    """Alert management system"""
    
    def __init__(self):
        self.alerts = []
        self.alert_thresholds = {
            "cpu_percent": 80,
            "memory_percent": 85,
            "disk_percent": 90,
            "database_health": False
        }
    
    async def check_alerts(self, system_status: Dict[str, Any]):
        """Check for alert conditions"""
        alerts = []
        
        # CPU alert
        if system_status["system"]["cpu_percent"] > self.alert_thresholds["cpu_percent"]:
            alerts.append({
                "type": "high_cpu",
                "severity": "warning",
                "message": f"High CPU usage: {system_status['system']['cpu_percent']}%",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Memory alert
        if system_status["system"]["memory_percent"] > self.alert_thresholds["memory_percent"]:
            alerts.append({
                "type": "high_memory",
                "severity": "warning",
                "message": f"High memory usage: {system_status['system']['memory_percent']}%",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Disk alert
        if system_status["system"]["disk_percent"] > self.alert_thresholds["disk_percent"]:
            alerts.append({
                "type": "high_disk",
                "severity": "critical",
                "message": f"High disk usage: {system_status['system']['disk_percent']}%",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Database health alert
        if not all(system_status["databases"].values()):
            alerts.append({
                "type": "database_unhealthy",
                "severity": "critical",
                "message": f"Database health issues: {system_status['databases']}",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Store new alerts
        self.alerts.extend(alerts)
        
        # Log alerts
        for alert in alerts:
            if alert["severity"] == "critical":
                logger.critical(alert["message"])
            else:
                logger.warning(alert["message"])
        
        return alerts
    
    def get_active_alerts(self) -> list:
        """Get all active alerts"""
        return self.alerts
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()

# Global alert manager
alert_manager = AlertManager()

# API monitoring functions
async def record_api_call(service: str, endpoint: str, status_code: int, response_time: float):
    """Record API call metrics"""
    try:
        await write_metric(
            measurement="api_calls",
            tags={
                "service": service,
                "endpoint": endpoint,
                "status_code": str(status_code)
            },
            fields={
                "response_time_ms": response_time * 1000,
                "count": 1
            }
        )
    except Exception as e:
        logger.debug(f"Could not record API call metrics: {e}")

async def record_api_error(service: str, endpoint: str, status_code: int, error_message: str):
    """Record API error metrics"""
    try:
        await write_metric(
            measurement="api_errors",
            tags={
                "service": service,
                "endpoint": endpoint,
                "status_code": str(status_code)
            },
            fields={
                "error_message": error_message,
                "count": 1
            }
        )
    except Exception as e:
        logger.debug(f"Could not record API error metrics: {e}") 