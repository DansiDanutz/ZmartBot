"""
Performance Monitor - ZmartBot
Comprehensive performance monitoring and optimization system
"""

import asyncio
import time
import logging
import psutil
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    active_connections: int
    request_count: int
    response_time_avg: float
    error_count: int
    cache_hit_rate: float
    database_connections: int
    ai_requests_per_minute: int

class PerformanceMonitor:
    """
    Comprehensive performance monitoring system for ZmartBot
    
    Features:
    - Real-time system metrics
    - API performance tracking
    - Database performance monitoring
    - Cache performance analysis
    - AI request tracking
    - Automatic alerting
    - Performance optimization suggestions
    """
    
    def __init__(self):
        self.metrics_history: deque = deque(maxlen=1000)  # Keep last 1000 measurements
        self.api_performance: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'request_count': 0,
            'response_times': deque(maxlen=100),
            'error_count': 0,
            'last_request': None
        })
        self.database_performance: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'query_count': 0,
            'query_times': deque(maxlen=100),
            'connection_count': 0,
            'error_count': 0
        })
        self.cache_performance: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'hit_count': 0,
            'miss_count': 0,
            'set_count': 0,
            'delete_count': 0
        })
        self.ai_performance: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'request_count': 0,
            'response_times': deque(maxlen=100),
            'success_rate': 0.0,
            'last_request': None
        })
        
        self.monitoring_active = False
        self.monitoring_thread = None
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'response_time_avg': 2.0,  # seconds
            'error_rate': 0.05,  # 5%
            'cache_hit_rate': 0.7,  # 70%
        }
        
    async def start_monitoring(self, interval: int = 30):
        """Start performance monitoring"""
        if self.monitoring_active:
            logger.warning("Performance monitoring already active")
            return
        
        self.monitoring_active = True
        logger.info(f"Starting performance monitoring with {interval}s interval")
        
        while self.monitoring_active:
            try:
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Check for performance issues
                await self._check_alerts(metrics)
                
                # Generate optimization suggestions
                await self._generate_optimization_suggestions()
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Performance monitoring stopped")
    
    async def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            network_io = psutil.net_io_counters()
            
            # Application metrics
            active_connections = len(psutil.net_connections())
            request_count = sum(api['request_count'] for api in self.api_performance.values())
            response_time_avg = self._calculate_avg_response_time()
            error_count = sum(api['error_count'] for api in self.api_performance.values())
            cache_hit_rate = self._calculate_cache_hit_rate()
            database_connections = sum(db['connection_count'] for db in self.database_performance.values())
            ai_requests_per_minute = self._calculate_ai_requests_per_minute()
            
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                disk_io_read_mb=disk_io.read_bytes / (1024 * 1024) if disk_io else 0,
                disk_io_write_mb=disk_io.write_bytes / (1024 * 1024) if disk_io else 0,
                network_sent_mb=network_io.bytes_sent / (1024 * 1024) if network_io else 0,
                network_recv_mb=network_io.bytes_recv / (1024 * 1024) if network_io else 0,
                active_connections=active_connections,
                request_count=request_count,
                response_time_avg=response_time_avg,
                error_count=error_count,
                cache_hit_rate=cache_hit_rate,
                database_connections=database_connections,
                ai_requests_per_minute=ai_requests_per_minute
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                disk_io_read_mb=0.0,
                disk_io_write_mb=0.0,
                network_sent_mb=0.0,
                network_recv_mb=0.0,
                active_connections=0,
                request_count=0,
                response_time_avg=0.0,
                error_count=0,
                cache_hit_rate=0.0,
                database_connections=0,
                ai_requests_per_minute=0
            )
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time across all APIs"""
        all_response_times = []
        for api_data in self.api_performance.values():
            all_response_times.extend(api_data['response_times'])
        
        if not all_response_times:
            return 0.0
        
        return sum(all_response_times) / len(all_response_times)
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate overall cache hit rate"""
        total_hits = sum(cache['hit_count'] for cache in self.cache_performance.values())
        total_misses = sum(cache['miss_count'] for cache in self.cache_performance.values())
        
        total_requests = total_hits + total_misses
        if total_requests == 0:
            return 0.0
        
        return total_hits / total_requests
    
    def _calculate_ai_requests_per_minute(self) -> int:
        """Calculate AI requests per minute"""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        total_requests = 0
        for ai_data in self.ai_performance.values():
            if ai_data['last_request'] and ai_data['last_request'] > one_minute_ago:
                total_requests += ai_data['request_count']
        
        return total_requests
    
    async def _check_alerts(self, metrics: PerformanceMetrics):
        """Check for performance alerts"""
        alerts = []
        
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append(f"High memory usage: {metrics.memory_percent:.1f}%")
        
        if metrics.response_time_avg > self.alert_thresholds['response_time_avg']:
            alerts.append(f"Slow response time: {metrics.response_time_avg:.2f}s")
        
        if metrics.cache_hit_rate < self.alert_thresholds['cache_hit_rate']:
            alerts.append(f"Low cache hit rate: {metrics.cache_hit_rate:.1%}")
        
        if alerts:
            logger.warning(f"Performance alerts: {'; '.join(alerts)}")
            await self._send_alerts(alerts)
    
    async def _send_alerts(self, alerts: List[str]):
        """Send performance alerts"""
        # This would integrate with your alerting system
        # For now, just log the alerts
        for alert in alerts:
            logger.warning(f"PERFORMANCE ALERT: {alert}")
    
    async def _generate_optimization_suggestions(self):
        """Generate performance optimization suggestions"""
        if len(self.metrics_history) < 10:
            return
        
        recent_metrics = list(self.metrics_history)[-10:]
        
        suggestions = []
        
        # CPU optimization
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        if avg_cpu > 70:
            suggestions.append("Consider scaling horizontally or optimizing CPU-intensive operations")
        
        # Memory optimization
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        if avg_memory > 80:
            suggestions.append("Consider increasing memory or optimizing memory usage")
        
        # Cache optimization
        avg_cache_hit = sum(m.cache_hit_rate for m in recent_metrics) / len(recent_metrics)
        if avg_cache_hit < 0.6:
            suggestions.append("Consider expanding cache size or improving cache strategies")
        
        # Response time optimization
        avg_response = sum(m.response_time_avg for m in recent_metrics) / len(recent_metrics)
        if avg_response > 1.0:
            suggestions.append("Consider optimizing database queries or adding more caching")
        
        if suggestions:
            logger.info(f"Performance optimization suggestions: {'; '.join(suggestions)}")
    
    def record_api_request(self, api_name: str, response_time: float, success: bool = True):
        """Record API request performance"""
        api_data = self.api_performance[api_name]
        api_data['request_count'] += 1
        api_data['response_times'].append(response_time)
        api_data['last_request'] = datetime.now()
        
        if not success:
            api_data['error_count'] += 1
    
    def record_database_query(self, db_name: str, query_time: float, success: bool = True):
        """Record database query performance"""
        db_data = self.database_performance[db_name]
        db_data['query_count'] += 1
        db_data['query_times'].append(query_time)
        
        if not success:
            db_data['error_count'] += 1
    
    def record_cache_operation(self, cache_name: str, operation: str, success: bool = True):
        """Record cache operation performance"""
        cache_data = self.cache_performance[cache_name]
        
        if operation == 'get':
            if success:
                cache_data['hit_count'] += 1
            else:
                cache_data['miss_count'] += 1
        elif operation == 'set':
            cache_data['set_count'] += 1
        elif operation == 'delete':
            cache_data['delete_count'] += 1
    
    def record_ai_request(self, ai_name: str, response_time: float, success: bool = True):
        """Record AI request performance"""
        ai_data = self.ai_performance[ai_name]
        ai_data['request_count'] += 1
        ai_data['response_times'].append(response_time)
        ai_data['last_request'] = datetime.now()
        
        # Update success rate
        total_requests = ai_data['request_count']
        if total_requests > 0:
            success_count = total_requests - ai_data.get('error_count', 0)
            ai_data['success_rate'] = success_count / total_requests
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        latest_metrics = self.metrics_history[-1]
        
        return {
            "timestamp": latest_metrics.timestamp.isoformat(),
            "system": {
                "cpu_percent": latest_metrics.cpu_percent,
                "memory_percent": latest_metrics.memory_percent,
                "memory_used_mb": latest_metrics.memory_used_mb,
                "active_connections": latest_metrics.active_connections
            },
            "performance": {
                "request_count": latest_metrics.request_count,
                "response_time_avg": latest_metrics.response_time_avg,
                "error_count": latest_metrics.error_count,
                "cache_hit_rate": latest_metrics.cache_hit_rate
            },
            "ai_performance": {
                "requests_per_minute": latest_metrics.ai_requests_per_minute,
                "success_rate": self._calculate_ai_success_rate()
            },
            "alerts": self._get_active_alerts(latest_metrics)
        }
    
    def _calculate_ai_success_rate(self) -> float:
        """Calculate overall AI success rate"""
        total_requests = sum(ai['request_count'] for ai in self.ai_performance.values())
        if total_requests == 0:
            return 0.0
        
        total_success = sum(ai['request_count'] * ai['success_rate'] for ai in self.ai_performance.values())
        return total_success / total_requests
    
    def _get_active_alerts(self, metrics: PerformanceMetrics) -> List[str]:
        """Get active performance alerts"""
        alerts = []
        
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append("high_cpu")
        
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append("high_memory")
        
        if metrics.response_time_avg > self.alert_thresholds['response_time_avg']:
            alerts.append("slow_response")
        
        if metrics.cache_hit_rate < self.alert_thresholds['cache_hit_rate']:
            alerts.append("low_cache_hit")
        
        return alerts

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Performance monitoring decorators
def monitor_api_performance(api_name: str):
    """Decorator to monitor API performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                response_time = time.time() - start_time
                performance_monitor.record_api_request(api_name, response_time, success=True)
                return result
            except Exception as e:
                response_time = time.time() - start_time
                performance_monitor.record_api_request(api_name, response_time, success=False)
                raise e
        return wrapper
    return decorator

def monitor_database_performance(db_name: str):
    """Decorator to monitor database performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                query_time = time.time() - start_time
                performance_monitor.record_database_query(db_name, query_time, success=True)
                return result
            except Exception as e:
                query_time = time.time() - start_time
                performance_monitor.record_database_query(db_name, query_time, success=False)
                raise e
        return wrapper
    return decorator

def monitor_ai_performance(ai_name: str):
    """Decorator to monitor AI performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                response_time = time.time() - start_time
                performance_monitor.record_ai_request(ai_name, response_time, success=True)
                return result
            except Exception as e:
                response_time = time.time() - start_time
                performance_monitor.record_ai_request(ai_name, response_time, success=False)
                raise e
        return wrapper
    return decorator 