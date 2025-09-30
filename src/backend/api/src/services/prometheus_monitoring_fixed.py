#!/usr/bin/env python3
"""
Fixed Prometheus Monitoring Service
Resolves metric conflicts and provides clean monitoring setup
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, generate_latest
import threading

logger = logging.getLogger(__name__)

@dataclass
class AlertRule:
    name: str
    condition: str
    threshold: float
    severity: str
    description: str

class PrometheusMonitoringFixed:
    """
    Fixed Prometheus monitoring service with resolved conflicts
    
    Creates its own registry to avoid conflicts with existing metrics
    """
    
    def __init__(self):
        """Initialize the fixed monitoring service"""
        self.service_id = "prometheus_monitoring_fixed"
        self.status = "stopped"
        
        # Create separate registry to avoid conflicts
        self.registry = CollectorRegistry()
        
        # Initialize metrics with unique names
        self._initialize_fixed_metrics()
        
        # Alert rules
        self.alert_rules = {}
        self._initialize_alert_rules()
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info("Fixed Prometheus Monitoring Service initialized")
    
    def _initialize_fixed_metrics(self):
        """Initialize metrics with fixed names to avoid conflicts"""
        
        # Trading metrics (fixed names)
        self.trades_executed = Counter(
            'zmart_fixed_trades_executed_total',
            'Total number of trades executed',
            ['symbol', 'direction', 'strategy'],
            registry=self.registry
        )
        
        self.trade_pnl = Histogram(
            'zmart_fixed_trade_pnl',
            'Trade profit/loss distribution',
            ['symbol', 'strategy'],
            buckets=[-1000, -500, -100, -50, 0, 50, 100, 500, 1000],
            registry=self.registry
        )
        
        self.portfolio_value_fixed = Gauge(
            'zmart_fixed_portfolio_value',
            'Current portfolio value',
            ['currency'],
            registry=self.registry
        )
        
        # Signal metrics (fixed names)
        self.signals_generated_fixed = Counter(
            'zmart_fixed_signals_generated_total',
            'Total number of signals generated',
            ['source', 'confidence_level'],
            registry=self.registry
        )
        
        self.signal_accuracy_fixed = Gauge(
            'zmart_fixed_signal_accuracy',
            'Signal prediction accuracy',
            ['source', 'timeframe'],
            registry=self.registry
        )
        
        # Risk metrics (fixed names)
        self.risk_score_fixed = Gauge(
            'zmart_fixed_risk_score',
            'Current risk score',
            ['symbol', 'type'],
            registry=self.registry
        )
        
        self.drawdown_fixed = Gauge(
            'zmart_fixed_drawdown',
            'Current drawdown percentage',
            ['symbol'],
            registry=self.registry
        )
        
        # API metrics (fixed names)
        self.api_requests_fixed = Counter(
            'zmart_fixed_api_requests_total',
            'Total API requests',
            ['endpoint', 'method', 'status'],
            registry=self.registry
        )
        
        self.api_response_time_fixed = Histogram(
            'zmart_fixed_api_response_time_seconds',
            'API response time',
            ['endpoint', 'method'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=self.registry
        )
        
        # System metrics (fixed names)
        self.system_cpu_usage = Gauge(
            'zmart_fixed_system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'zmart_fixed_system_memory_usage_percent',
            'System memory usage percentage',
            registry=self.registry
        )
        
        # Service health metrics (fixed names)
        self.service_health_fixed = Gauge(
            'zmart_fixed_service_health',
            'Service health status (1=healthy, 0=unhealthy)',
            ['service_name'],
            registry=self.registry
        )
        
        self.service_uptime_fixed = Gauge(
            'zmart_fixed_service_uptime_seconds',
            'Service uptime in seconds',
            ['service_name'],
            registry=self.registry
        )
        
        logger.info("Fixed Prometheus metrics initialized successfully")
    
    def _initialize_alert_rules(self):
        """Initialize alert rules"""
        self.alert_rules = {
            'high_risk_score': AlertRule(
                name='high_risk_score',
                condition='risk_score > 0.8',
                threshold=0.8,
                severity='warning',
                description='Risk score exceeds 80% threshold'
            ),
            'low_signal_accuracy': AlertRule(
                name='low_signal_accuracy',
                condition='signal_accuracy < 0.6',
                threshold=0.6,
                severity='warning',
                description='Signal accuracy below 60% threshold'
            ),
            'high_drawdown': AlertRule(
                name='high_drawdown',
                condition='drawdown > 0.1',
                threshold=0.1,
                severity='critical',
                description='Drawdown exceeds 10% threshold'
            ),
            'api_errors': AlertRule(
                name='api_errors',
                condition='api_error_rate > 0.05',
                threshold=0.05,
                severity='warning',
                description='API error rate exceeds 5%'
            ),
            'high_cpu_usage': AlertRule(
                name='high_cpu_usage',
                condition='cpu_usage > 80',
                threshold=80,
                severity='warning',
                description='CPU usage exceeds 80%'
            )
        }
    
    async def start(self):
        """Start the monitoring service"""
        self.status = "running"
        logger.info("Fixed Prometheus Monitoring Service started")
    
    async def stop(self):
        """Stop the monitoring service"""
        self.status = "stopped"
        logger.info("Fixed Prometheus Monitoring Service stopped")
    
    def record_trade(self, symbol: str, direction: str, strategy: str, pnl: float):
        """Record a trade execution"""
        with self.lock:
            self.trades_executed.labels(
                symbol=symbol,
                direction=direction,
                strategy=strategy
            ).inc()
            
            self.trade_pnl.labels(
                symbol=symbol,
                strategy=strategy
            ).observe(pnl)
    
    def update_portfolio_value(self, currency: str, value: float):
        """Update portfolio value"""
        with self.lock:
            self.portfolio_value_fixed.labels(currency=currency).set(value)
    
    def record_signal(self, source: str, confidence: float, timeframe: str = "1h"):
        """Record signal generation"""
        with self.lock:
            confidence_level = "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low"
            
            self.signals_generated_fixed.labels(
                source=source,
                confidence_level=confidence_level
            ).inc()
    
    def update_signal_accuracy(self, source: str, timeframe: str, accuracy: float):
        """Update signal accuracy"""
        with self.lock:
            self.signal_accuracy_fixed.labels(
                source=source,
                timeframe=timeframe
            ).set(accuracy)
    
    def update_risk_score(self, symbol: str, risk_type: str, score: float):
        """Update risk score"""
        with self.lock:
            self.risk_score_fixed.labels(
                symbol=symbol,
                type=risk_type
            ).set(score)
    
    def update_drawdown(self, symbol: str, drawdown: float):
        """Update drawdown"""
        with self.lock:
            self.drawdown_fixed.labels(symbol=symbol).set(drawdown)
    
    def record_api_request(self, endpoint: str, method: str, status: int, duration: float):
        """Record API request"""
        with self.lock:
            self.api_requests_fixed.labels(
                endpoint=endpoint,
                method=method,
                status=str(status)
            ).inc()
            
            self.api_response_time_fixed.labels(
                endpoint=endpoint,
                method=method
            ).observe(duration)
    
    def update_system_metrics(self, cpu_usage: float, memory_usage: float):
        """Update system metrics"""
        with self.lock:
            self.system_cpu_usage.set(cpu_usage)
            self.system_memory_usage.set(memory_usage)
    
    def update_service_health(self, service_name: str, is_healthy: bool, uptime: float):
        """Update service health"""
        with self.lock:
            self.service_health_fixed.labels(service_name=service_name).set(1 if is_healthy else 0)
            self.service_uptime_fixed.labels(service_name=service_name).set(uptime)
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        return generate_latest(self.registry).decode('utf-8')
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check all alert rules and return active alerts"""
        active_alerts = []
        
        # This would check actual metric values against thresholds
        # For now, return empty list (no active alerts)
        
        return active_alerts
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get monitoring service status"""
        return {
            "service_id": self.service_id,
            "status": self.status,
            "metrics_count": len(self.registry._collector_to_names),
            "alert_rules_count": len(self.alert_rules),
            "registry_type": "separate",
            "conflicts_resolved": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of available metrics"""
        return {
            "trading_metrics": [
                "zmart_fixed_trades_executed_total",
                "zmart_fixed_trade_pnl",
                "zmart_fixed_portfolio_value"
            ],
            "signal_metrics": [
                "zmart_fixed_signals_generated_total",
                "zmart_fixed_signal_accuracy"
            ],
            "risk_metrics": [
                "zmart_fixed_risk_score",
                "zmart_fixed_drawdown"
            ],
            "api_metrics": [
                "zmart_fixed_api_requests_total",
                "zmart_fixed_api_response_time_seconds"
            ],
            "system_metrics": [
                "zmart_fixed_system_cpu_usage_percent",
                "zmart_fixed_system_memory_usage_percent"
            ],
            "service_metrics": [
                "zmart_fixed_service_health",
                "zmart_fixed_service_uptime_seconds"
            ]
        }

# Global instance
prometheus_monitoring_fixed = PrometheusMonitoringFixed()