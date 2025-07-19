"""
Zmart Trading Bot Platform - Health Check Routes
System health monitoring and status endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import asyncio

from src.utils.monitoring import get_system_status, get_performance_metrics
from src.utils.database import check_database_health
from src.utils.metrics import metrics_collector

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "zmart-api",
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with system status"""
    try:
        system_status = await get_system_status()
        return system_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/health/databases")
async def database_health_check() -> Dict[str, Any]:
    """Database health check"""
    try:
        db_health = await check_database_health()
        overall_healthy = all(db_health.values())
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "databases": db_health,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database health check failed: {str(e)}")

@router.get("/health/metrics")
async def metrics_endpoint() -> Dict[str, Any]:
    """Get Prometheus metrics"""
    try:
        metrics = metrics_collector.get_metrics()
        return {
            "metrics": metrics,
            "content_type": metrics_collector.get_metrics_content_type()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")

@router.get("/health/performance")
async def performance_metrics(time_range: str = "1h") -> Dict[str, Any]:
    """Get performance metrics for the specified time range"""
    try:
        metrics = await get_performance_metrics(time_range)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance metrics failed: {str(e)}")

@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check for Kubernetes"""
    try:
        # Check critical dependencies
        db_health = await check_database_health()
        critical_healthy = db_health.get("postgresql", False) and db_health.get("redis", False)
        
        if not critical_healthy:
            raise HTTPException(status_code=503, detail="Critical dependencies unavailable")
        
        return {
            "status": "ready",
            "timestamp": asyncio.get_event_loop().time()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Readiness check failed: {str(e)}")

@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for Kubernetes"""
    return {
        "status": "alive",
        "timestamp": asyncio.get_event_loop().time()
    } 