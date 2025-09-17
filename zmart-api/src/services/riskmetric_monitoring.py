#!/usr/bin/env python3
"""
RiskMetric Monitoring and Metrics Service
Provides Prometheus metrics, performance monitoring, and analytics
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
import asyncio
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    method_name: str
    execution_time: float
    timestamp: datetime
    success: bool
    error: Optional[str] = None

class RiskMetricMonitoring:
    """Monitoring and metrics for RiskMetric service"""
    
    def __init__(self):
        # Create Prometheus registry
        self.registry = CollectorRegistry()
        
        # Define Prometheus metrics
        self.assessment_counter = Counter(
            'riskmetric_assessments_total',
            'Total number of risk assessments',
            ['symbol', 'risk_band'],
            registry=self.registry
        )
        
        self.assessment_duration = Histogram(
            'riskmetric_assessment_duration_seconds',
            'Duration of risk assessment operations',
            ['symbol'],
            registry=self.registry
        )
        
        self.risk_value_gauge = Gauge(
            'riskmetric_current_risk_value',
            'Current risk value for each symbol',
            ['symbol'],
            registry=self.registry
        )
        
        self.cache_hits = Counter(
            'riskmetric_cache_hits_total',
            'Total number of cache hits',
            registry=self.registry
        )
        
        self.cache_misses = Counter(
            'riskmetric_cache_misses_total',
            'Total number of cache misses',
            registry=self.registry
        )
        
        self.api_errors = Counter(
            'riskmetric_api_errors_total',
            'Total number of API errors',
            ['error_type'],
            registry=self.registry
        )
        
        self.active_connections = Gauge(
            'riskmetric_websocket_connections',
            'Number of active WebSocket connections',
            registry=self.registry
        )
        
        self.alerts_triggered = Counter(
            'riskmetric_alerts_triggered_total',
            'Total number of alerts triggered',
            ['symbol', 'alert_type'],
            registry=self.registry
        )
        
        # Performance tracking
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.error_log: deque = deque(maxlen=100)
        
        # Analytics data
        self.symbol_access_count: Dict[str, int] = defaultdict(int)
        self.hourly_stats: Dict[str, Dict[str, Any]] = {}
        self.daily_summary: Dict[str, Any] = {}
        
        # Simple counter for total assessments
        self.total_assessments = 0
        
        # Start time for uptime calculation
        self.start_time = datetime.now()
    
    def record_assessment(self, symbol: str, risk_value: float, risk_band: str, duration: float):
        """Record a risk assessment"""
        # Update Prometheus metrics
        self.assessment_counter.labels(symbol=symbol, risk_band=risk_band).inc()
        self.assessment_duration.labels(symbol=symbol).observe(duration)
        self.risk_value_gauge.labels(symbol=symbol).set(risk_value)
        
        # Update analytics
        self.symbol_access_count[symbol] += 1
        self.total_assessments += 1
        
        # Record performance
        metric = PerformanceMetrics(
            method_name="assess_risk",
            execution_time=duration,
            timestamp=datetime.now(),
            success=True
        )
        self.performance_history["assess_risk"].append(metric)
    
    def record_cache_hit(self):
        """Record a cache hit"""
        self.cache_hits.inc()
    
    def record_cache_miss(self):
        """Record a cache miss"""
        self.cache_misses.inc()
    
    def record_error(self, error_type: str, error_message: str):
        """Record an API error"""
        self.api_errors.labels(error_type=error_type).inc()
        
        # Log error details
        self.error_log.append({
            "type": error_type,
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })
    
    def record_alert(self, symbol: str, alert_type: str):
        """Record an alert trigger"""
        self.alerts_triggered.labels(symbol=symbol, alert_type=alert_type).inc()
    
    def update_connection_count(self, count: int):
        """Update WebSocket connection count"""
        self.active_connections.set(count)
    
    def get_performance_summary(self, method_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance summary statistics"""
        if method_name:
            metrics = list(self.performance_history.get(method_name, []))
        else:
            metrics = []
            for method_metrics in self.performance_history.values():
                metrics.extend(list(method_metrics))
        
        if not metrics:
            return {"message": "No performance data available"}
        
        execution_times = [m.execution_time for m in metrics]
        success_count = sum(1 for m in metrics if m.success)
        error_count = sum(1 for m in metrics if not m.success)
        
        return {
            "total_calls": len(metrics),
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": (success_count / len(metrics)) * 100 if metrics else 0,
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "p50_execution_time": sorted(execution_times)[len(execution_times) // 2] if execution_times else 0,
            "p95_execution_time": sorted(execution_times)[int(len(execution_times) * 0.95)] if execution_times else 0,
            "p99_execution_time": sorted(execution_times)[int(len(execution_times) * 0.99)] if execution_times else 0
        }
    
    def get_symbol_analytics(self) -> Dict[str, Any]:
        """Get symbol access analytics"""
        total_accesses = sum(self.symbol_access_count.values())
        
        # Sort symbols by access count
        top_symbols = sorted(
            self.symbol_access_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "total_accesses": total_accesses,
            "unique_symbols": len(self.symbol_access_count),
            "top_10_symbols": [
                {"symbol": symbol, "count": count, "percentage": (count/total_accesses)*100}
                for symbol, count in top_symbols
            ] if total_accesses > 0 else []
        }
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_hits = self.cache_hits._value.get()
        total_misses = self.cache_misses._value.get()
        total_requests = total_hits + total_misses
        
        return {
            "total_requests": total_requests,
            "cache_hits": total_hits,
            "cache_misses": total_misses,
            "hit_rate": (total_hits / total_requests * 100) if total_requests > 0 else 0,
            "miss_rate": (total_misses / total_requests * 100) if total_requests > 0 else 0
        }
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary"""
        error_counts = defaultdict(int)
        for error in self.error_log:
            error_counts[error["type"]] += 1
        
        return {
            "total_errors": len(self.error_log),
            "recent_errors": list(self.error_log)[-10:],
            "error_types": dict(error_counts)
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        uptime = datetime.now() - self.start_time
        performance = self.get_performance_summary()
        cache_stats = self.get_cache_statistics()
        
        # Calculate health score (0-100)
        health_score = 100
        
        # Deduct points for poor performance
        if performance.get("success_rate", 100) < 95:
            health_score -= 20
        if performance.get("avg_execution_time", 0) > 1.0:  # Over 1 second average
            health_score -= 10
        
        # Deduct points for poor cache performance
        if cache_stats.get("hit_rate", 0) < 50:
            health_score -= 15
        
        # Deduct points for errors
        error_summary = self.get_error_summary()
        if error_summary["total_errors"] > 10:
            health_score -= 15
        
        return {
            "status": "healthy" if health_score >= 70 else "degraded" if health_score >= 50 else "unhealthy",
            "health_score": max(0, health_score),
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": str(uptime),
            "performance_summary": performance,
            "cache_performance": cache_stats,
            "error_rate": error_summary["total_errors"] / max(1, performance.get("total_calls", 1)) * 100,
            "active_websocket_connections": self.active_connections._value.get()
        }
    
    def export_prometheus_metrics(self) -> bytes:
        """Export metrics in Prometheus format"""
        return generate_latest(self.registry)
    
    async def collect_hourly_stats(self):
        """Collect hourly statistics (run as background task)"""
        while True:
            try:
                hour_key = datetime.now().strftime("%Y-%m-%d %H:00")
                
                self.hourly_stats[hour_key] = {
                    "timestamp": datetime.now().isoformat(),
                    "performance": self.get_performance_summary(),
                    "symbol_analytics": self.get_symbol_analytics(),
                    "cache_stats": self.get_cache_statistics(),
                    "errors": self.get_error_summary(),
                    "health": self.get_system_health()
                }
                
                # Keep only last 24 hours
                if len(self.hourly_stats) > 24:
                    oldest_key = min(self.hourly_stats.keys())
                    del self.hourly_stats[oldest_key]
                
                logger.info(f"Collected hourly stats for {hour_key}")
                
                # Wait for next hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error collecting hourly stats: {e}")
                await asyncio.sleep(3600)
    
    async def generate_daily_summary(self):
        """Generate daily summary (run as background task)"""
        while True:
            try:
                # Wait until midnight
                now = datetime.now()
                tomorrow = now.replace(hour=0, minute=0, second=0) + timedelta(days=1)
                wait_seconds = (tomorrow - now).total_seconds()
                await asyncio.sleep(wait_seconds)
                
                # Generate summary for previous day
                yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
                
                # Get counter value safely
                try:
                    # Try to get the metric value
                    total_assessments = self.total_assessments
                except:
                    # Fallback to 0 if not available
                    total_assessments = 0
                
                daily_stats = {
                    "date": yesterday,
                    "generated_at": datetime.now().isoformat(),
                    "total_assessments": total_assessments,
                    "unique_symbols": len(self.symbol_access_count),
                    "top_symbols": self.get_symbol_analytics()["top_10_symbols"],
                    "cache_performance": self.get_cache_statistics(),
                    "system_health": self.get_system_health(),
                    "error_summary": self.get_error_summary()
                }
                
                self.daily_summary[yesterday] = daily_stats
                
                # Keep only last 30 days
                if len(self.daily_summary) > 30:
                    oldest_date = min(self.daily_summary.keys())
                    del self.daily_summary[oldest_date]
                
                logger.info(f"Generated daily summary for {yesterday}")
                
            except Exception as e:
                logger.error(f"Error generating daily summary: {e}")
                await asyncio.sleep(86400)  # Try again tomorrow

# Global monitoring instance
monitoring = RiskMetricMonitoring()