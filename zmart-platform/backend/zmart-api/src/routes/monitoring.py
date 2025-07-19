"""
Zmart Trading Bot Platform - Monitoring Routes
Handles system monitoring, metrics, and observability
"""
from fastapi import APIRouter, HTTPException, Response
from typing import Dict, Any
import time

from src.utils.monitoring import get_system_health, get_system_metrics
from src.utils.metrics import get_metrics_collector
from src.utils.locking import get_lock_manager

router = APIRouter()

@router.get("/metrics")
async def get_metrics() -> Response:
    """Get Prometheus metrics"""
    try:
        metrics_collector = get_metrics_collector()
        metrics_data = metrics_collector.get_metrics()
        return Response(
            content=metrics_data,
            media_type=metrics_collector.get_metrics_content_type()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/system")
async def get_system_monitoring() -> Dict[str, Any]:
    """Get system monitoring information"""
    try:
        system_health = await get_system_health()
        system_metrics = await get_system_metrics()
        
        return {
            "health": system_health,
            "metrics": system_metrics,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system monitoring: {str(e)}")

@router.get("/locks")
async def get_lock_status() -> Dict[str, Any]:
    """Get lock manager status"""
    try:
        lock_manager = get_lock_manager()
        lock_stats = lock_manager.get_statistics()
        
        return {
            "locks": lock_stats,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get lock status: {str(e)}")

@router.get("/alerts")
async def get_alerts() -> Dict[str, Any]:
    """Get active alerts"""
    # TODO: Implement alert retrieval
    return {
        "message": "Alerts endpoint - to be implemented",
        "status": "placeholder"
    }

@router.get("/logs")
async def get_logs() -> Dict[str, Any]:
    """Get system logs"""
    # TODO: Implement log retrieval
    return {
        "message": "Logs endpoint - to be implemented",
        "status": "placeholder"
    }

@router.get("/performance")
async def get_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics"""
    try:
        system_metrics = await get_system_metrics()
        metrics_collector = get_metrics_collector()
        metrics_stats = metrics_collector.get_statistics()
        
        return {
            "system": system_metrics,
            "metrics": metrics_stats,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}") 