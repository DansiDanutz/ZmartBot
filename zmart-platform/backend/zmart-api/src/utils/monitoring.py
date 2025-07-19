"""
Zmart Trading Bot Platform - Monitoring Utilities
Handles system monitoring, health checks, and alerting
"""
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import psutil
import aiohttp

from src.config.settings import settings
from src.utils.database import check_postgres_health, check_redis_health, check_influx_health

logger = logging.getLogger(__name__)

class SystemMonitor:
    """System monitoring and health check manager"""
    
    def __init__(self):
        self.health_checks = {
            "database": self._check_database_health,
            "memory": self._check_memory_health,
            "cpu": self._check_cpu_health,
            "disk": self._check_disk_health,
            "network": self._check_network_health
        }
        self.last_health_check = None
        self.health_status = {}
        
    async def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        start_time = time.time()
        
        # Run all health checks concurrently
        tasks = []
        for check_name, check_func in self.health_checks.items():
            tasks.append(self._run_health_check(check_name, check_func))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile results
        health_status = {}
        overall_status = "healthy"
        
        for check_name, result in zip(self.health_checks.keys(), results):
            if isinstance(result, Exception):
                health_status[check_name] = {
                    "status": "error",
                    "error": str(result),
                    "timestamp": datetime.utcnow().isoformat()
                }
                overall_status = "unhealthy"
            else:
                health_status[check_name] = result
                if result.get("status") == "unhealthy":
                    overall_status = "unhealthy"
        
        self.health_status = health_status
        self.last_health_check = datetime.utcnow()
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "response_time": time.time() - start_time,
            "checks": health_status
        }
    
    async def _run_health_check(self, check_name: str, check_func) -> Dict[str, Any]:
        """Run a single health check with timeout"""
        try:
            result = await asyncio.wait_for(check_func(), timeout=10.0)
            return result
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "error": f"Health check {check_name} timed out",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        postgres_health = await check_postgres_health()
        redis_health = await check_redis_health()
        influx_health = await check_influx_health()
        
        databases_healthy = all([
            postgres_health["status"] == "healthy",
            redis_health["status"] == "healthy",
            influx_health["status"] == "healthy"
        ])
        
        return {
            "status": "healthy" if databases_healthy else "unhealthy",
            "databases": {
                "postgresql": postgres_health,
                "redis": redis_health,
                "influxdb": influx_health
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _check_memory_health(self) -> Dict[str, Any]:
        """Check memory usage"""
        memory = psutil.virtual_memory()
        
        # Define thresholds
        warning_threshold = 80.0  # 80%
        critical_threshold = 95.0  # 95%
        
        memory_percent = memory.percent
        status = "healthy"
        
        if memory_percent > critical_threshold:
            status = "critical"
        elif memory_percent > warning_threshold:
            status = "warning"
        
        return {
            "status": status,
            "usage_percent": memory_percent,
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _check_cpu_health(self) -> Dict[str, Any]:
        """Check CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Define thresholds
        warning_threshold = 80.0  # 80%
        critical_threshold = 95.0  # 95%
        
        status = "healthy"
        if cpu_percent > critical_threshold:
            status = "critical"
        elif cpu_percent > warning_threshold:
            status = "warning"
        
        return {
            "status": status,
            "usage_percent": cpu_percent,
            "core_count": psutil.cpu_count(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _check_disk_health(self) -> Dict[str, Any]:
        """Check disk usage"""
        disk = psutil.disk_usage('/')
        
        # Define thresholds
        warning_threshold = 80.0  # 80%
        critical_threshold = 95.0  # 95%
        
        disk_percent = (disk.used / disk.total) * 100
        status = "healthy"
        
        if disk_percent > critical_threshold:
            status = "critical"
        elif disk_percent > warning_threshold:
            status = "warning"
        
        return {
            "status": status,
            "usage_percent": round(disk_percent, 2),
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _check_network_health(self) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            # Test external connectivity
            async with aiohttp.ClientSession() as session:
                async with session.get('https://httpbin.org/get', timeout=5) as response:
                    if response.status == 200:
                        return {
                            "status": "healthy",
                            "connectivity": "external_ok",
                            "response_time": "ok",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        return {
                            "status": "warning",
                            "connectivity": "external_slow",
                            "response_time": "slow",
                            "timestamp": datetime.utcnow().isoformat()
                        }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connectivity": "external_failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

class AlertManager:
    """Alert management system"""
    
    def __init__(self):
        self.alerts = []
        self.alert_rules = {
            "memory_critical": {"threshold": 95.0, "type": "memory"},
            "cpu_critical": {"threshold": 95.0, "type": "cpu"},
            "disk_critical": {"threshold": 95.0, "type": "disk"},
            "database_unhealthy": {"type": "database"}
        }
    
    async def check_alerts(self, health_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for new alerts based on health status"""
        new_alerts = []
        
        for check_name, check_result in health_status.get("checks", {}).items():
            if check_result.get("status") in ["critical", "unhealthy"]:
                alert = {
                    "id": f"{check_name}_{int(time.time())}",
                    "type": check_name,
                    "severity": "critical" if check_result.get("status") == "critical" else "warning",
                    "message": f"{check_name} is {check_result.get('status')}",
                    "details": check_result,
                    "timestamp": datetime.utcnow().isoformat()
                }
                new_alerts.append(alert)
        
        # Add new alerts to the list
        self.alerts.extend(new_alerts)
        
        # Keep only recent alerts (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.alerts = [
            alert for alert in self.alerts 
            if datetime.fromisoformat(alert["timestamp"]) > cutoff_time
        ]
        
        return new_alerts
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        return self.alerts
    
    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """Send alert notification"""
        try:
            # TODO: Implement alert sending (Slack, email, etc.)
            logger.warning(f"ALERT: {alert['message']} - {alert['details']}")
            return True
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False

# Global instances
system_monitor = SystemMonitor()
alert_manager = AlertManager()

def setup_monitoring():
    """Setup monitoring system"""
    logger.info("Setting up monitoring system")
    # Monitoring setup is complete when the instances are created

async def get_system_health() -> Dict[str, Any]:
    """Get current system health status"""
    return await system_monitor.perform_health_check()

async def get_system_metrics() -> Dict[str, Any]:
    """Get system performance metrics"""
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100,
        "timestamp": datetime.utcnow().isoformat()
    }

async def check_external_services() -> Dict[str, Any]:
    """Check external service connectivity"""
    services = {
        "kucoin_api": "https://api.kucoin.com/api/v1/status",
        "binance_api": "https://api.binance.com/api/v3/ping",
        "cryptometer_api": "https://api.cryptometer.io/health"
    }
    
    results = {}
    
    async with aiohttp.ClientSession() as session:
        for service_name, url in services.items():
            try:
                async with session.get(url, timeout=5) as response:
                    results[service_name] = {
                        "status": "healthy" if response.status == 200 else "unhealthy",
                        "response_time": "ok",
                        "status_code": response.status
                    }
            except Exception as e:
                results[service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "response_time": "timeout"
                }
    
    return results 