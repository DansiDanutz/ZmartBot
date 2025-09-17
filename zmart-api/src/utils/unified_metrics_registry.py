#!/usr/bin/env python3
"""
Unified Metrics Registry
Centralized Prometheus metrics registry to prevent conflicts
"""

import logging
from typing import Dict, Any, Optional
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, generate_latest
import threading

logger = logging.getLogger(__name__)

class UnifiedMetricsRegistry:
    """
    Unified metrics registry to prevent Prometheus conflicts
    
    All services should use this registry instead of creating their own metrics
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure only one registry exists"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the unified registry (only once)"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.registry = CollectorRegistry()
        self.metrics: Dict[str, Any] = {}
        self.lock = threading.Lock()
        
        # Initialize all metrics once
        self._initialize_all_metrics()
        
        logger.info("Unified Metrics Registry initialized")
    
    def _initialize_all_metrics(self):
        """Initialize all metrics that might be used across services"""
        
        # Trading metrics
        self.metrics['trades_total'] = Counter(
            'zmart_trades_total',
            'Total number of trades executed',
            ['symbol', 'direction', 'strategy'],
            registry=self.registry
        )
        
        self.metrics['trade_volume'] = Gauge(
            'zmart_trade_volume',
            'Current trade volume',
            ['symbol', 'currency'],
            registry=self.registry
        )
        
        self.metrics['active_positions'] = Gauge(
            'zmart_active_positions',
            'Number of active positions',
            ['symbol', 'direction'],
            registry=self.registry
        )
        
        self.metrics['portfolio_value'] = Gauge(
            'zmart_portfolio_value',
            'Current portfolio value',
            ['currency'],
            registry=self.registry
        )
        
        # Signal metrics
        self.metrics['signals_generated'] = Counter(
            'zmart_signals_generated_total',
            'Total signals generated',
            ['source', 'confidence_level'],
            registry=self.registry
        )
        
        self.metrics['signals_processed'] = Counter(
            'zmart_signals_processed_total',
            'Total signals processed',
            ['source', 'action'],
            registry=self.registry
        )
        
        self.metrics['signal_confidence'] = Gauge(
            'zmart_signal_confidence',
            'Current signal confidence',
            ['source', 'symbol'],
            registry=self.registry
        )
        
        self.metrics['signal_accuracy'] = Gauge(
            'zmart_signal_accuracy',
            'Signal prediction accuracy',
            ['source', 'timeframe'],
            registry=self.registry
        )
        
        # Risk metrics
        self.metrics['risk_score'] = Gauge(
            'zmart_risk_score',
            'Current risk score',
            ['symbol', 'type'],
            registry=self.registry
        )
        
        self.metrics['drawdown'] = Gauge(
            'zmart_drawdown',
            'Current drawdown percentage',
            ['symbol'],
            registry=self.registry
        )
        
        self.metrics['risk_assessments'] = Counter(
            'zmart_risk_assessments_total',
            'Total risk assessments performed',
            ['symbol', 'result'],
            registry=self.registry
        )
        
        # API metrics
        self.metrics['api_requests'] = Counter(
            'zmart_api_requests_total',
            'Total API requests',
            ['endpoint', 'method', 'status'],
            registry=self.registry
        )
        
        self.metrics['api_response_time'] = Histogram(
            'zmart_api_response_time_seconds',
            'API response time',
            ['endpoint', 'method'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=self.registry
        )
        
        self.metrics['api_rate_limits'] = Gauge(
            'zmart_api_rate_limits',
            'API rate limit status',
            ['api_name', 'status'],
            registry=self.registry
        )
        
        # System metrics
        self.metrics['system_cpu_usage'] = Gauge(
            'zmart_system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.metrics['system_memory_usage'] = Gauge(
            'zmart_system_memory_usage_percent',
            'System memory usage percentage',
            registry=self.registry
        )
        
        self.metrics['system_disk_usage'] = Gauge(
            'zmart_system_disk_usage_percent',
            'System disk usage percentage',
            registry=self.registry
        )
        
        # Service health metrics
        self.metrics['service_health'] = Gauge(
            'zmart_service_health',
            'Service health status (1=healthy, 0=unhealthy)',
            ['service_name'],
            registry=self.registry
        )
        
        self.metrics['service_uptime'] = Gauge(
            'zmart_service_uptime_seconds',
            'Service uptime in seconds',
            ['service_name'],
            registry=self.registry
        )
        
        self.metrics['service_errors'] = Counter(
            'zmart_service_errors_total',
            'Total service errors',
            ['service_name', 'error_type'],
            registry=self.registry
        )
        
        # Database metrics
        self.metrics['database_connections'] = Gauge(
            'zmart_database_connections',
            'Active database connections',
            ['database_name'],
            registry=self.registry
        )
        
        self.metrics['database_query_time'] = Histogram(
            'zmart_database_query_time_seconds',
            'Database query execution time',
            ['database_name', 'query_type'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0],
            registry=self.registry
        )
        
        # Market data metrics
        self.metrics['market_data_updates'] = Counter(
            'zmart_market_data_updates_total',
            'Total market data updates',
            ['exchange', 'symbol'],
            registry=self.registry
        )
        
        self.metrics['market_data_latency'] = Histogram(
            'zmart_market_data_latency_seconds',
            'Market data latency',
            ['exchange', 'symbol'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
            registry=self.registry
        )
        
        logger.info(f"Initialized {len(self.metrics)} unified metrics")
    
    def get_metric(self, metric_name: str):
        """Get a metric by name"""
        with self.lock:
            return self.metrics.get(metric_name)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        with self.lock:
            return self.metrics.copy()
    
    def get_metrics_text(self) -> str:
        """Get Prometheus metrics in text format"""
        return generate_latest(self.registry).decode('utf-8')
    
    def get_registry(self) -> CollectorRegistry:
        """Get the underlying Prometheus registry"""
        return self.registry
    
    def record_trade(self, symbol: str, direction: str, strategy: str, volume: float = 0):
        """Record a trade execution"""
        with self.lock:
            self.metrics['trades_total'].labels(
                symbol=symbol,
                direction=direction,
                strategy=strategy
            ).inc()
            
            if volume > 0:
                self.metrics['trade_volume'].labels(
                    symbol=symbol,
                    currency='USDT'
                ).set(volume)
    
    def update_position(self, symbol: str, direction: str, count: int):
        """Update active positions"""
        with self.lock:
            self.metrics['active_positions'].labels(
                symbol=symbol,
                direction=direction
            ).set(count)
    
    def record_signal(self, source: str, confidence: float, symbol: Optional[str] = None):
        """Record signal generation"""
        with self.lock:
            confidence_level = "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low"
            
            self.metrics['signals_generated'].labels(
                source=source,
                confidence_level=confidence_level
            ).inc()
            
            if symbol:
                self.metrics['signal_confidence'].labels(
                    source=source,
                    symbol=symbol
                ).set(confidence)
    
    def update_risk_score(self, symbol: str, risk_type: str, score: float):
        """Update risk score"""
        with self.lock:
            self.metrics['risk_score'].labels(
                symbol=symbol,
                type=risk_type
            ).set(score)
    
    def record_api_request(self, endpoint: str, method: str, status: int, duration: float):
        """Record API request"""
        with self.lock:
            self.metrics['api_requests'].labels(
                endpoint=endpoint,
                method=method,
                status=str(status)
            ).inc()
            
            self.metrics['api_response_time'].labels(
                endpoint=endpoint,
                method=method
            ).observe(duration)
    
    def update_service_health(self, service_name: str, is_healthy: bool, uptime: float = 0):
        """Update service health"""
        with self.lock:
            self.metrics['service_health'].labels(service_name=service_name).set(1 if is_healthy else 0)
            
            if uptime > 0:
                self.metrics['service_uptime'].labels(service_name=service_name).set(uptime)
    
    def record_service_error(self, service_name: str, error_type: str):
        """Record service error"""
        with self.lock:
            self.metrics['service_errors'].labels(
                service_name=service_name,
                error_type=error_type
            ).inc()
    
    def update_system_metrics(self, cpu: Optional[float] = None, memory: Optional[float] = None, disk: Optional[float] = None):
        """Update system metrics"""
        with self.lock:
            if cpu is not None:
                self.metrics['system_cpu_usage'].set(cpu)
            if memory is not None:
                self.metrics['system_memory_usage'].set(memory)
            if disk is not None:
                self.metrics['system_disk_usage'].set(disk)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of available metrics"""
        return {
            'total_metrics': len(self.metrics),
            'metric_categories': {
                'trading': [k for k in self.metrics.keys() if k.startswith(('trade', 'position', 'portfolio'))],
                'signals': [k for k in self.metrics.keys() if k.startswith('signal')],
                'risk': [k for k in self.metrics.keys() if k.startswith('risk') or k == 'drawdown'],
                'api': [k for k in self.metrics.keys() if k.startswith('api')],
                'system': [k for k in self.metrics.keys() if k.startswith('system')],
                'service': [k for k in self.metrics.keys() if k.startswith('service')],
                'database': [k for k in self.metrics.keys() if k.startswith('database')],
                'market_data': [k for k in self.metrics.keys() if k.startswith('market_data')]
            },
            'registry_type': 'unified',
            'conflicts_resolved': True
        }

# Global singleton instance
unified_metrics_registry = UnifiedMetricsRegistry()

# Convenience functions for common operations
def get_unified_registry() -> UnifiedMetricsRegistry:
    """Get the unified metrics registry instance"""
    return unified_metrics_registry

def record_trade_metric(symbol: str, direction: str, strategy: str, volume: float = 0):
    """Convenience function to record trade"""
    unified_metrics_registry.record_trade(symbol, direction, strategy, volume)

def record_signal_metric(source: str, confidence: float, symbol: Optional[str] = None):
    """Convenience function to record signal"""
    unified_metrics_registry.record_signal(source, confidence, symbol)

def update_service_health_metric(service_name: str, is_healthy: bool, uptime: float = 0):
    """Convenience function to update service health"""
    unified_metrics_registry.update_service_health(service_name, is_healthy, uptime)