"""
Zmart Trading Bot Platform - Monitoring Routes
System monitoring, alerts, and performance metrics
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.routes.auth import get_current_active_user, require_role
from src.utils.monitoring import get_system_status, get_performance_metrics, alert_manager
from src.utils.metrics import metrics_collector

router = APIRouter()

# Pydantic models
class Alert(BaseModel):
    alert_id: str
    type: str
    severity: str  # "info", "warning", "critical"
    message: str
    timestamp: datetime
    acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, float]
    timestamp: datetime

class PerformanceMetrics(BaseModel):
    api_response_time: float
    database_query_time: float
    cache_hit_ratio: float
    active_connections: int
    timestamp: datetime

@router.get("/status")
async def get_status(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get current system status"""
    try:
        status = await get_system_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.get("/metrics")
async def get_metrics(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get current system metrics"""
    try:
        metrics = metrics_collector.get_metrics()
        return {
            "metrics": metrics,
            "content_type": metrics_collector.get_metrics_content_type()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/performance")
async def get_performance(
    time_range: str = "1h",
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get performance metrics for the specified time range"""
    try:
        metrics = await get_performance_metrics(time_range)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.get("/alerts")
async def get_alerts(
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get system alerts"""
    alerts = alert_manager.get_active_alerts()
    
    # Apply filters
    if severity:
        alerts = [alert for alert in alerts if alert["severity"] == severity]
    
    if acknowledged is not None:
        alerts = [alert for alert in alerts if alert.get("acknowledged", False) == acknowledged]
    
    # Sort by timestamp (newest first) and limit
    alerts.sort(key=lambda x: x["timestamp"], reverse=True)
    alerts = alerts[:limit]
    
    return alerts

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Acknowledge an alert"""
    # Mock alert acknowledgment (replace with database)
    return {
        "message": f"Alert {alert_id} acknowledged",
        "acknowledged_by": current_user["username"],
        "acknowledged_at": datetime.utcnow().isoformat()
    }

@router.delete("/alerts/{alert_id}")
async def delete_alert(
    alert_id: str,
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Delete an alert"""
    # Mock alert deletion (replace with database)
    return {"message": f"Alert {alert_id} deleted"}

@router.get("/health/detailed")
async def detailed_health_check(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get detailed health check information"""
    try:
        system_status = await get_system_status()
        
        # Check for critical issues
        critical_issues = []
        
        if system_status["status"] != "healthy":
            critical_issues.append("System is unhealthy")
        
        for db_name, db_healthy in system_status["databases"].items():
            if not db_healthy:
                critical_issues.append(f"Database {db_name} is unhealthy")
        
        if system_status["system"]["cpu_percent"] > 90:
            critical_issues.append("High CPU usage")
        
        if system_status["system"]["memory_percent"] > 90:
            critical_issues.append("High memory usage")
        
        if system_status["system"]["disk_percent"] > 90:
            critical_issues.append("High disk usage")
        
        return {
            "status": system_status["status"],
            "critical_issues": critical_issues,
            "details": system_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/logs")
async def get_logs(
    level: Optional[str] = None,
    service: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Get system logs"""
    # Mock logs (replace with actual log retrieval)
    logs = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "service": "zmart-api",
            "message": "System started successfully"
        },
        {
            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
            "level": "WARNING",
            "service": "trading-engine",
            "message": "High latency detected in trade execution"
        }
    ]
    
    # Apply filters
    if level:
        logs = [log for log in logs if log["level"] == level.upper()]
    
    if service:
        logs = [log for log in logs if log["service"] == service]
    
    if start_time:
        logs = [log for log in logs if datetime.fromisoformat(log["timestamp"]) >= start_time]
    
    if end_time:
        logs = [log for log in logs if datetime.fromisoformat(log["timestamp"]) <= end_time]
    
    # Sort by timestamp (newest first) and limit
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    logs = logs[:limit]
    
    return logs

@router.get("/dashboard")
async def get_dashboard_data(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get dashboard data for monitoring"""
    try:
        system_status = await get_system_status()
        
        # Get recent alerts
        alerts = alert_manager.get_active_alerts()
        recent_alerts = alerts[:5]  # Last 5 alerts
        
        # Get basic metrics
        metrics = {
            "total_trades": 150,
            "total_signals": 300,
            "active_positions": 5,
            "portfolio_value": 10000.0,
            "daily_pnl": 250.0
        }
        
        return {
            "system_status": system_status,
            "recent_alerts": recent_alerts,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

@router.get("/services")
async def get_services_status(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get status of all services"""
    try:
        system_status = await get_system_status()
        
        services = {
            "api": {
                "status": "healthy",
                "uptime": system_status["uptime_seconds"],
                "version": "1.0.0"
            },
            "database": {
                "status": "healthy" if all(system_status["databases"].values()) else "unhealthy",
                "connections": system_status["process"]["num_threads"]
            },
            "cache": {
                "status": "healthy" if system_status["databases"]["redis"] else "unhealthy",
                "hit_ratio": 0.85
            },
            "message_queue": {
                "status": "healthy",
                "queue_size": 0
            }
        }
        
        return services
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get services status: {str(e)}")

@router.post("/maintenance")
async def start_maintenance_mode(
    reason: str,
    duration_minutes: int = 30,
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Start maintenance mode"""
    # Mock maintenance mode (replace with actual implementation)
    return {
        "message": "Maintenance mode started",
        "reason": reason,
        "duration_minutes": duration_minutes,
        "started_by": current_user["username"],
        "started_at": datetime.utcnow().isoformat()
    }

@router.delete("/maintenance")
async def stop_maintenance_mode(
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Stop maintenance mode"""
    # Mock maintenance mode stop (replace with actual implementation)
    return {
        "message": "Maintenance mode stopped",
        "stopped_by": current_user["username"],
        "stopped_at": datetime.utcnow().isoformat()
    }

@router.get("/performance/summary")
async def get_performance_summary(
    time_range: str = "24h",
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get performance summary for the specified time range"""
    try:
        # Mock performance summary (replace with actual calculation)
        summary = {
            "time_range": time_range,
            "api_requests": {
                "total": 15000,
                "successful": 14950,
                "failed": 50,
                "average_response_time": 0.15
            },
            "trading": {
                "total_trades": 150,
                "successful_trades": 145,
                "failed_trades": 5,
                "average_execution_time": 0.05
            },
            "signals": {
                "total_signals": 300,
                "high_confidence": 200,
                "medium_confidence": 80,
                "low_confidence": 20
            },
            "system": {
                "cpu_average": 45.2,
                "memory_average": 62.8,
                "disk_usage": 35.5,
                "uptime_percentage": 99.8
            }
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance summary: {str(e)}")

@router.get("/alerts/statistics")
async def get_alert_statistics(
    time_range: str = "24h",
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get alert statistics"""
    alerts = alert_manager.get_active_alerts()
    
    # Filter by time range
    cutoff_time = datetime.utcnow() - timedelta(hours=int(time_range.replace("h", "")))
    recent_alerts = [alert for alert in alerts if alert["timestamp"] >= cutoff_time]
    
    # Calculate statistics
    total_alerts = len(recent_alerts)
    critical_alerts = len([a for a in recent_alerts if a["severity"] == "critical"])
    warning_alerts = len([a for a in recent_alerts if a["severity"] == "warning"])
    info_alerts = len([a for a in recent_alerts if a["severity"] == "info"])
    
    alert_types = {}
    for alert in recent_alerts:
        alert_type = alert["type"]
        if alert_type not in alert_types:
            alert_types[alert_type] = 0
        alert_types[alert_type] += 1
    
    return {
        "time_range": time_range,
        "total_alerts": total_alerts,
        "critical_alerts": critical_alerts,
        "warning_alerts": warning_alerts,
        "info_alerts": info_alerts,
        "alert_types": alert_types
    } 