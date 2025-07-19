"""
Zmart Trading Bot Platform - Metrics Utilities
Handles Prometheus metrics collection and monitoring
"""
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Prometheus metrics collector for the trading platform"""
    
    def __init__(self):
        # Trading metrics
        self.trades_total = Counter(
            'zmart_trades_total',
            'Total number of trades executed',
            ['symbol', 'side', 'status']
        )
        
        self.trade_volume = Counter(
            'zmart_trade_volume_usd',
            'Total trade volume in USD',
            ['symbol', 'side']
        )
        
        self.trade_profit_loss = Gauge(
            'zmart_trade_pnl_usd',
            'Current profit/loss in USD',
            ['symbol', 'side']
        )
        
        # Signal metrics
        self.signals_generated = Counter(
            'zmart_signals_generated_total',
            'Total number of signals generated',
            ['signal_type', 'confidence_level']
        )
        
        self.signal_accuracy = Gauge(
            'zmart_signal_accuracy_percent',
            'Signal accuracy percentage',
            ['signal_type', 'timeframe']
        )
        
        # Risk metrics
        self.risk_score = Gauge(
            'zmart_risk_score',
            'Current risk score',
            ['portfolio', 'risk_type']
        )
        
        self.position_size = Gauge(
            'zmart_position_size_usd',
            'Current position size in USD',
            ['symbol', 'side']
        )
        
        # Performance metrics
        self.api_request_duration = Histogram(
            'zmart_api_request_duration_seconds',
            'API request duration in seconds',
            ['endpoint', 'method', 'status']
        )
        
        self.database_query_duration = Histogram(
            'zmart_database_query_duration_seconds',
            'Database query duration in seconds',
            ['database', 'operation']
        )
        
        # System metrics
        self.system_cpu_usage = Gauge(
            'zmart_system_cpu_usage_percent',
            'System CPU usage percentage'
        )
        
        self.system_memory_usage = Gauge(
            'zmart_system_memory_usage_bytes',
            'System memory usage in bytes'
        )
        
        self.system_disk_usage = Gauge(
            'zmart_system_disk_usage_percent',
            'System disk usage percentage'
        )
        
        # Agent metrics
        self.agent_tasks_total = Counter(
            'zmart_agent_tasks_total',
            'Total number of agent tasks',
            ['agent_type', 'task_type', 'status']
        )
        
        self.agent_task_duration = Histogram(
            'zmart_agent_task_duration_seconds',
            'Agent task duration in seconds',
            ['agent_type', 'task_type']
        )
        
        # Error metrics
        self.errors_total = Counter(
            'zmart_errors_total',
            'Total number of errors',
            ['error_type', 'component']
        )
        
        # Custom metrics storage
        self.custom_metrics = {}
        
        logger.info("Metrics collector initialized")
    
    def record_trade(self, symbol: str, side: str, amount_usd: float, status: str = "executed"):
        """Record a trade execution"""
        self.trades_total.labels(symbol=symbol, side=side, status=status).inc()
        self.trade_volume.labels(symbol=symbol, side=side).inc(amount_usd)
        
        logger.debug(f"Recorded trade: {symbol} {side} ${amount_usd} {status}")
    
    def record_signal(self, signal_type: str, confidence: float):
        """Record a signal generation"""
        confidence_level = self._get_confidence_level(confidence)
        self.signals_generated.labels(
            signal_type=signal_type,
            confidence_level=confidence_level
        ).inc()
        
        logger.debug(f"Recorded signal: {signal_type} confidence={confidence}")
    
    def update_signal_accuracy(self, signal_type: str, timeframe: str, accuracy: float):
        """Update signal accuracy"""
        self.signal_accuracy.labels(
            signal_type=signal_type,
            timeframe=timeframe
        ).set(accuracy)
        
        logger.debug(f"Updated signal accuracy: {signal_type} {timeframe} {accuracy}%")
    
    def update_risk_score(self, portfolio: str, risk_type: str, score: float):
        """Update risk score"""
        self.risk_score.labels(
            portfolio=portfolio,
            risk_type=risk_type
        ).set(score)
        
        logger.debug(f"Updated risk score: {portfolio} {risk_type} {score}")
    
    def update_position_size(self, symbol: str, side: str, size_usd: float):
        """Update position size"""
        self.position_size.labels(
            symbol=symbol,
            side=side
        ).set(size_usd)
        
        logger.debug(f"Updated position size: {symbol} {side} ${size_usd}")
    
    def record_api_request(self, endpoint: str, method: str, status: int, duration: float):
        """Record API request metrics"""
        self.api_request_duration.labels(
            endpoint=endpoint,
            method=method,
            status=str(status)
        ).observe(duration)
        
        logger.debug(f"Recorded API request: {method} {endpoint} {status} {duration}s")
    
    def record_database_query(self, database: str, operation: str, duration: float):
        """Record database query metrics"""
        self.database_query_duration.labels(
            database=database,
            operation=operation
        ).observe(duration)
        
        logger.debug(f"Recorded DB query: {database} {operation} {duration}s")
    
    def record_agent_task(self, agent_type: str, task_type: str, status: str, duration: float = None):
        """Record agent task metrics"""
        self.agent_tasks_total.labels(
            agent_type=agent_type,
            task_type=task_type,
            status=status
        ).inc()
        
        if duration is not None:
            self.agent_task_duration.labels(
                agent_type=agent_type,
                task_type=task_type
            ).observe(duration)
        
        logger.debug(f"Recorded agent task: {agent_type} {task_type} {status}")
    
    def record_error(self, error_type: str, component: str):
        """Record an error"""
        self.errors_total.labels(
            error_type=error_type,
            component=component
        ).inc()
        
        logger.error(f"Recorded error: {error_type} in {component}")
    
    def update_system_metrics(self, cpu_percent: float, memory_bytes: int, disk_percent: float):
        """Update system metrics"""
        self.system_cpu_usage.set(cpu_percent)
        self.system_memory_usage.set(memory_bytes)
        self.system_disk_usage.set(disk_percent)
        
        logger.debug(f"Updated system metrics: CPU={cpu_percent}% Memory={memory_bytes}B Disk={disk_percent}%")
    
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
        
        logger.debug(f"Set custom metric: {name} = {value}")
    
    def increment_custom_counter(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Increment a custom counter"""
        if name not in self.custom_metrics:
            self.custom_metrics[name] = Counter(
                f'zmart_custom_{name}_total',
                f'Custom counter: {name}',
                list(labels.keys()) if labels else []
            )
        
        if labels:
            self.custom_metrics[name].labels(**labels).inc()
        else:
            self.custom_metrics[name].inc()
        
        logger.debug(f"Incremented custom counter: {name}")
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence score to level"""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        else:
            return "low"
    
    def get_metrics(self) -> str:
        """Get all metrics in Prometheus format"""
        return generate_latest()
    
    def get_metrics_content_type(self) -> str:
        """Get content type for metrics"""
        return CONTENT_TYPE_LATEST

# Global metrics collector instance
metrics_collector = MetricsCollector()

def setup_metrics():
    """Setup metrics collection"""
    logger.info("Setting up metrics collection")
    # Metrics setup is complete when the collector is created

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    return metrics_collector 