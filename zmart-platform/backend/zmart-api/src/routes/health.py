"""
Zmart Trading Bot Platform - Health Check Routes
Provides comprehensive health monitoring and system status endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import psutil
import time

from src.utils.monitoring import get_system_health, get_system_metrics, check_external_services
from src.utils.database import check_postgres_health, check_redis_health, check_influx_health
from src.utils.metrics import get_metrics_collector
from src.config.settings import settings

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint"""
    start_time = time.time()
    
    try:
        # Get system health status
        system_health = await get_system_health()
        
        # Get system metrics
        system_metrics = await get_system_metrics()
        
        # Check external services
        external_services = await check_external_services()
        
        # Determine overall health
        overall_status = "healthy"
        if system_health["status"] != "healthy":
            overall_status = "unhealthy"
        
        response_time = time.time() - start_time
        
        return {
            "status": overall_status,
            "timestamp": system_health["timestamp"],
            "response_time": response_time,
            "version": "1.0.0",
            "environment": settings.environment.value,
            "system": system_health,
            "metrics": system_metrics,
            "external_services": external_services
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time(),
            "response_time": time.time() - start_time
        }

@router.get("/health/simple")
async def simple_health_check() -> Dict[str, Any]:
    """Simple health check for load balancers"""
    return {
        "status": "healthy",
        "service": "zmart-trading-bot",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with all system components"""
    start_time = time.time()
    
    # Check all database connections
    db_checks = {
        "postgresql": await check_postgres_health(),
        "redis": await check_redis_health(),
        "influxdb": await check_influx_health()
    }
    
    # Get system resources
    system_resources = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
    }
    
    # Get metrics statistics
    metrics_collector = get_metrics_collector()
    metrics_stats = metrics_collector.get_statistics()
    
    # Determine overall health
    all_healthy = all(
        check["status"] == "healthy" 
        for check in db_checks.values()
    )
    
    overall_status = "healthy" if all_healthy else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": time.time(),
        "response_time": time.time() - start_time,
        "databases": db_checks,
        "system_resources": system_resources,
        "metrics": metrics_stats,
        "configuration": {
            "environment": settings.environment.value,
            "debug": settings.debug,
            "host": settings.host,
            "port": settings.port
        }
    }

@router.get("/health/databases")
async def database_health_check() -> Dict[str, Any]:
    """Database-specific health check"""
    start_time = time.time()
    
    db_checks = {
        "postgresql": await check_postgres_health(),
        "redis": await check_redis_health(),
        "influxdb": await check_influx_health()
    }
    
    all_healthy = all(
        check["status"] == "healthy" 
        for check in db_checks.values()
    )
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "databases": db_checks,
        "timestamp": time.time(),
        "response_time": time.time() - start_time
    }

@router.get("/health/external")
async def external_services_health_check() -> Dict[str, Any]:
    """External services health check"""
    start_time = time.time()
    
    external_services = await check_external_services()
    
    all_healthy = all(
        service["status"] == "healthy" 
        for service in external_services.values()
    )
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "services": external_services,
        "timestamp": time.time(),
        "response_time": time.time() - start_time
    }

@router.get("/health/metrics")
async def metrics_health_check() -> Dict[str, Any]:
    """Metrics and monitoring health check"""
    start_time = time.time()
    
    # Get system metrics
    system_metrics = await get_system_metrics()
    
    # Get metrics collector statistics
    metrics_collector = get_metrics_collector()
    metrics_stats = metrics_collector.get_statistics()
    
    return {
        "status": "healthy",
        "system_metrics": system_metrics,
        "metrics_collector": metrics_stats,
        "timestamp": time.time(),
        "response_time": time.time() - start_time
    }

@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check for Kubernetes"""
    try:
        # Check critical dependencies
        postgres_health = await check_postgres_health()
        redis_health = await check_redis_health()
        
        # Service is ready if critical databases are healthy
        ready = (
            postgres_health["status"] == "healthy" and
            redis_health["status"] == "healthy"
        )
        
        return {
            "ready": ready,
            "timestamp": time.time(),
            "checks": {
                "postgresql": postgres_health["status"] == "healthy",
                "redis": redis_health["status"] == "healthy"
            }
        }
        
    except Exception as e:
        return {
            "ready": False,
            "error": str(e),
            "timestamp": time.time()
        }

@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for Kubernetes"""
    return {
        "alive": True,
        "timestamp": time.time()
    } 