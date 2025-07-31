"""
Zmart Trading Bot Platform - Metrics Collection
Metrics collection and aggregation utilities
"""
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import psutil
from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest, CONTENT_TYPE_LATEST

from src.config.settings import settings

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Prometheus metrics collector for the Zmart platform"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        # Trading metrics
        self.trades_total = Counter(
            'zmart_trades_total',
            'Total number of trades executed',
            ['symbol', 'side', 'status']
        )
        
        self.trade_volume = Counter(
            'zmart_trade_volume',
            'Total trading volume',
            ['symbol', 'side']
        )
        
        self.active_positions = Gauge(
            'zmart_active_positions',
            'Number of active positions',
            ['symbol']
        )
        
        self.position_pnl = Gauge(
            'zmart_position_pnl',
            'Current P&L for positions',
            ['symbol', 'side']
        )
        
        # Signal metrics
        self.signals_generated = Counter(
            'zmart_signals_generated',
            'Total number of signals generated',
            ['source', 'confidence_level']
        )
        
        self.signals_processed = Counter(
            'zmart_signals_processed',
            'Total number of signals processed',
            ['status']
        )
        
        self.signal_confidence = Histogram(
            'zmart_signal_confidence',
            'Signal confidence distribution',
            ['source'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )
        
        # Risk metrics
        self.risk_score = Gauge(
            'zmart_risk_score',
            'Current risk score',
            ['symbol', 'type']
        )
        
        self.portfolio_value = Gauge(
            'zmart_portfolio_value',
            'Current portfolio value',
            ['currency']
        )
        
        self.max_drawdown = Gauge(
            'zmart_max_drawdown',
            'Maximum drawdown percentage',
            ['symbol']
        )
        
        # System metrics
        self.api_requests_total = Counter(
            'zmart_api_requests_total',
            'Total API requests',
            ['endpoint', 'method', 'status']
        )
        
        self.api_request_duration = Histogram(
            'zmart_api_request_duration_seconds',
            'API request duration',
            ['endpoint', 'method'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.database_connections = Gauge(
            'zmart_database_connections',
            'Number of active database connections',
            ['database']
        )
        
        self.cache_hit_ratio = Gauge(
            'zmart_cache_hit_ratio',
            'Cache hit ratio',
            ['cache_type']
        )
        
        # Agent metrics
        self.agent_tasks_total = Counter(
            'zmart_agent_tasks_total',
            'Total tasks processed by agents',
            ['agent_type', 'status']
        )
        
        self.agent_task_duration = Histogram(
            'zmart_agent_task_duration_seconds',
            'Agent task execution duration',
            ['agent_type'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
        )
        
        self.agent_status = Gauge(
            'zmart_agent_status',
            'Agent status (1=active, 0=inactive)',
            ['agent_type']
        )
        
        # Error metrics
        self.errors_total = Counter(
            'zmart_errors_total',
            'Total number of errors',
            ['type', 'component']
        )
        
        self.error_rate = Gauge(
            'zmart_error_rate',
            'Error rate percentage',
            ['component']
        )
        
        # Custom metrics
        self.custom_metrics: Dict[str, Any] = {}
        
        logger.info("Metrics collector initialized")
    
    def record_trade(self, symbol: str, side: str, status: str, volume: float = 0):
        """Record a trade execution"""
        self.trades_total.labels(symbol=symbol, side=side, status=status).inc()
        if volume > 0:
            self.trade_volume.labels(symbol=symbol, side=side).inc(volume)
    
    def update_position(self, symbol: str, side: str, pnl: float, count: int = 1):
        """Update position metrics"""
        self.position_pnl.labels(symbol=symbol, side=side).set(pnl)
        self.active_positions.labels(symbol=symbol).set(count)
    
    def record_signal(self, source: str, confidence: float, status: str = "generated"):
        """Record a trading signal"""
        confidence_level = self._get_confidence_level(confidence)
        self.signals_generated.labels(source=source, confidence_level=confidence_level).inc()
        self.signals_processed.labels(status=status).inc()
        self.signal_confidence.labels(source=source).observe(confidence)
    
    def update_risk_score(self, symbol: str, risk_type: str, score: float):
        """Update risk score metrics"""
        self.risk_score.labels(symbol=symbol, type=risk_type).set(score)
    
    def update_portfolio_value(self, currency: str, value: float):
        """Update portfolio value metrics"""
        self.portfolio_value.labels(currency=currency).set(value)
    
    def update_drawdown(self, symbol: str, drawdown: float):
        """Update maximum drawdown metrics"""
        self.max_drawdown.labels(symbol=symbol).set(drawdown)
    
    def record_api_request(self, endpoint: str, method: str, status: int, duration: float):
        """Record API request metrics"""
        self.api_requests_total.labels(endpoint=endpoint, method=method, status=status).inc()
        self.api_request_duration.labels(endpoint=endpoint, method=method).observe(duration)
    
    def update_database_connections(self, database: str, count: int):
        """Update database connection metrics"""
        self.database_connections.labels(database=database).set(count)
    
    def update_cache_hit_ratio(self, cache_type: str, ratio: float):
        """Update cache hit ratio metrics"""
        self.cache_hit_ratio.labels(cache_type=cache_type).set(ratio)
    
    def record_agent_task(self, agent_type: str, status: str, duration: float):
        """Record agent task metrics"""
        self.agent_tasks_total.labels(agent_type=agent_type, status=status).inc()
        self.agent_task_duration.labels(agent_type=agent_type).observe(duration)
    
    def update_agent_status(self, agent_type: str, is_active: bool):
        """Update agent status metrics"""
        status_value = 1 if is_active else 0
        self.agent_status.labels(agent_type=agent_type).set(status_value)
    
    def record_error(self, error_type: str, component: str):
        """Record error metrics"""
        self.errors_total.labels(type=error_type, component=component).inc()
    
    def update_error_rate(self, component: str, rate: float):
        """Update error rate metrics"""
        self.error_rate.labels(component=component).set(rate)
    
    def set_custom_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a custom metric value"""
        if name not in self.custom_metrics:
            self.custom_metrics[name] = Gauge(
                f'zmart_custom_{name}',
                f'Custom metric: {name}',
                list(labels.keys()) if labels else []
            )
        
        if labels:
            self.custom_metrics[name].labels(**labels).set(value)
        else:
            self.custom_metrics[name].set(value)
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence score to level string"""
        if confidence >= 0.9:
            return "very_high"
        elif confidence >= 0.8:
            return "high"
        elif confidence >= 0.7:
            return "medium"
        elif confidence >= 0.6:
            return "low"
        else:
            return "very_low"
    
    def get_metrics(self) -> bytes:
        """Get all metrics in Prometheus format"""
        return generate_latest()
    
    def get_metrics_content_type(self) -> str:
        """Get the content type for metrics"""
        return CONTENT_TYPE_LATEST

# Global metrics collector instance (singleton)
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance (singleton)"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

# For backward compatibility - only create if not already created
try:
    metrics_collector = get_metrics_collector()
except ValueError:
    # If there's a duplicate error, just get the existing instance
    metrics_collector = get_metrics_collector()

# Convenience functions for common metric operations
def record_trade_metrics(symbol: str, side: str, status: str, volume: float = 0):
    """Record trade metrics"""
    metrics_collector.record_trade(symbol, side, status, volume)

def record_signal_metrics(source: str, confidence: float, status: str = "generated"):
    """Record signal metrics"""
    metrics_collector.record_signal(source, confidence, status)

def record_api_metrics(endpoint: str, method: str, status: int, duration: float):
    """Record API request metrics"""
    metrics_collector.record_api_request(endpoint, method, status, duration)

def record_error_metrics(error_type: str, component: str):
    """Record error metrics"""
    metrics_collector.record_error(error_type, component)

def update_portfolio_metrics(currency: str, value: float):
    """Update portfolio metrics"""
    metrics_collector.update_portfolio_value(currency, value)

def update_risk_metrics(symbol: str, risk_type: str, score: float):
    """Update risk metrics"""
    metrics_collector.update_risk_score(symbol, risk_type, score)

def record_agent_task(agent_type: str, status: str, duration: float):
    """Record agent task metrics"""
    metrics_collector.record_agent_task(agent_type, status, duration)

def update_agent_status(agent_type: str, is_active: bool):
    """Update agent status metrics"""
    metrics_collector.update_agent_status(agent_type, is_active) 