#!/usr/bin/env python3
"""
RiskMetric Monitoring API Routes
Exposes monitoring metrics and analytics endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Dict, Any, Optional
from datetime import datetime

from ..services.riskmetric_monitoring import monitoring

router = APIRouter(prefix="/api/v1/riskmetric/monitoring")

@router.get("/metrics", response_class=PlainTextResponse)
async def get_prometheus_metrics():
    """
    Get Prometheus metrics for RiskMetric service
    Returns metrics in Prometheus text format
    """
    try:
        metrics = monitoring.export_prometheus_metrics()
        return PlainTextResponse(content=metrics, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export metrics: {str(e)}")

@router.get("/health")
async def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status of RiskMetric service"""
    try:
        return monitoring.get_system_health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get health status: {str(e)}")

@router.get("/performance")
async def get_performance_metrics(method: Optional[str] = None) -> Dict[str, Any]:
    """
    Get performance metrics
    
    Args:
        method: Optional specific method to get metrics for
    
    Returns:
        Performance summary including execution times and success rates
    """
    try:
        return monitoring.get_performance_summary(method)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.get("/analytics/symbols")
async def get_symbol_analytics() -> Dict[str, Any]:
    """Get symbol access analytics including top accessed symbols"""
    try:
        return monitoring.get_symbol_analytics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get symbol analytics: {str(e)}")

@router.get("/cache/stats")
async def get_cache_statistics() -> Dict[str, Any]:
    """Get cache performance statistics"""
    try:
        return monitoring.get_cache_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache statistics: {str(e)}")

@router.get("/errors")
async def get_error_summary() -> Dict[str, Any]:
    """Get error summary including recent errors and error types"""
    try:
        return monitoring.get_error_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get error summary: {str(e)}")

@router.get("/stats/hourly")
async def get_hourly_statistics() -> Dict[str, Any]:
    """Get hourly statistics for the last 24 hours"""
    try:
        return {
            "hourly_stats": monitoring.hourly_stats,
            "total_hours": len(monitoring.hourly_stats),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get hourly statistics: {str(e)}")

@router.get("/stats/daily")
async def get_daily_summaries() -> Dict[str, Any]:
    """Get daily summaries for the last 30 days"""
    try:
        return {
            "daily_summaries": monitoring.daily_summary,
            "total_days": len(monitoring.daily_summary),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get daily summaries: {str(e)}")

@router.get("/dashboard")
async def get_monitoring_dashboard() -> Dict[str, Any]:
    """Get complete monitoring dashboard data"""
    try:
        health = monitoring.get_system_health()
        performance = monitoring.get_performance_summary()
        symbols = monitoring.get_symbol_analytics()
        cache = monitoring.get_cache_statistics()
        errors = monitoring.get_error_summary()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "health": health,
            "performance": performance,
            "symbol_analytics": symbols,
            "cache_statistics": cache,
            "error_summary": errors,
            "recent_hourly_stats": list(monitoring.hourly_stats.values())[-6:] if monitoring.hourly_stats else [],
            "websocket_connections": monitoring.active_connections._value.get()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")