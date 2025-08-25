#!/usr/bin/env python3
"""
Prometheus Monitoring System
Implements comprehensive monitoring and alerting with Prometheus/Grafana integration
"""

import asyncio
import logging
import time
import psutil
import json
import numpy as np
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from prometheus_client import (
    Counter, Gauge, Histogram, Summary, generate_latest, 
    CONTENT_TYPE_LATEST, start_http_server
)

from src.config.settings import settings
from src.services.calibrated_scoring_service import CalibratedScoringService
from src.services.position_execution_engine import PositionExecutionEngine
from src.services.real_time_market_data_connector import RealTimeMarketDataConnector

logger = logging.getLogger(__name__)

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: str
    threshold: float
    severity: str  # info, warning, critical
    description: str
    enabled: bool = True

@dataclass
class Alert:
    """Alert instance"""
    rule_name: str
    severity: str
    message: str
    timestamp: datetime
    value: float
    threshold: float
    status: str = "active"  # active, resolved, acknowledged

class PrometheusMonitoring:
    """
    Comprehensive monitoring and alerting system with Prometheus/Grafana integration
    """
    
    def __init__(self):
        """Initialize the Prometheus monitoring system"""
        self.integrated_scoring = CalibratedScoringService()
        self.position_execution = PositionExecutionEngine()
        self.market_data_connector = RealTimeMarketDataConnector()
        
        # Prometheus metrics
        self._initialize_prometheus_metrics()
        
        # Alert rules
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Monitoring state
        self.monitoring_enabled = True
        self.metrics_collection_interval = 5.0  # seconds
        self.alert_check_interval = 10.0  # seconds
        
        # Performance tracking
        self.performance_metrics = {
            'total_metrics_collected': 0,
            'total_alerts_generated': 0,
            'system_uptime': 0.0,
            'last_metrics_update': None,
            'monitoring_health': 'healthy'
        }
        
        # Callbacks for alerts
        self.alert_callbacks: List[Callable] = []
        
        # Initialize alert rules
        self._initialize_alert_rules()
        
        logger.info("Prometheus Monitoring System initialized")
    
    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        # Import existing metrics to avoid duplicates
        from ..utils.metrics import get_metrics_registry
        
        metrics_registry = get_metrics_registry()
        
        # Use existing metrics from utils.metrics
        self.trades_total = metrics_registry.trades_total
        self.trade_volume = metrics_registry.trade_volume
        self.active_positions = metrics_registry.active_positions
        self.position_pnl = metrics_registry.position_pnl
        self.signals_processed = metrics_registry.signals_processed
        self.signal_confidence = metrics_registry.signal_confidence
        self.risk_score = metrics_registry.risk_score
        self.portfolio_value = metrics_registry.portfolio_value
        self.max_drawdown = metrics_registry.max_drawdown
        
        # Use existing system and agent metrics from registry
        self.api_requests_total = metrics_registry.api_requests_total
        self.api_request_duration = metrics_registry.api_request_duration
        self.database_connections = metrics_registry.database_connections
        self.cache_hit_ratio = metrics_registry.cache_hit_ratio
        self.agent_tasks_total = metrics_registry.agent_tasks_total
        self.agent_task_duration = metrics_registry.agent_task_duration
        self.agent_status = metrics_registry.agent_status
        
        # Use existing error metrics from registry
        self.errors_total = metrics_registry.errors_total
        self.error_rate = metrics_registry.error_rate
        
        # Neural network metrics
        self.model_accuracy = Gauge(
            'zmart_model_accuracy',
            'Model prediction accuracy',
            ['model_name']
        )
        
        self.training_loss = Gauge(
            'zmart_training_loss',
            'Model training loss',
            ['model_name']
        )
        
        # Market data metrics
        self.market_data_latency = Histogram(
            'zmart_market_data_latency_seconds',
            'Market data latency',
            ['exchange', 'symbol'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
        )
        
        self.market_data_volume = Counter(
            'zmart_market_data_volume',
            'Market data volume processed',
            ['exchange', 'symbol']
        )
    
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
            'low_win_rate': AlertRule(
                name='low_win_rate',
                condition='win_rate < 0.6',
                threshold=0.6,
                severity='warning',
                description='Win rate below 60% threshold'
            ),
            'high_drawdown': AlertRule(
                name='high_drawdown',
                condition='drawdown > 0.1',
                threshold=0.1,
                severity='critical',
                description='Drawdown exceeds 10% threshold'
            ),
            'api_error_rate': AlertRule(
                name='api_error_rate',
                condition='error_rate > 0.05',
                threshold=0.05,
                severity='warning',
                description='API error rate exceeds 5% threshold'
            ),
            'low_confidence': AlertRule(
                name='low_confidence',
                condition='confidence < 0.5',
                threshold=0.5,
                severity='info',
                description='Signal confidence below 50% threshold'
            ),
            'system_memory_high': AlertRule(
                name='system_memory_high',
                condition='memory_usage > 0.9',
                threshold=0.9,
                severity='warning',
                description='System memory usage above 90%'
            ),
            'cpu_usage_high': AlertRule(
                name='cpu_usage_high',
                condition='cpu_usage > 0.8',
                threshold=0.8,
                severity='warning',
                description='CPU usage above 80%'
            )
        }
    
    async def start_monitoring(self, port: int = 8000):
        """Start the monitoring system"""
        try:
            logger.info(f"Starting Prometheus monitoring on port {port}")
            
            # Start Prometheus HTTP server
            start_http_server(port)
            
            # Start metrics collection
            asyncio.create_task(self._metrics_collection_loop())
            
            # Start alert checking
            asyncio.create_task(self._alert_checking_loop())
            
            # Start system health monitoring
            asyncio.create_task(self._system_health_monitoring())
            
            logger.info("Prometheus monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            raise
    
    async def _metrics_collection_loop(self):
        """Main metrics collection loop"""
        try:
            while self.monitoring_enabled:
                await self._collect_system_metrics()
                await self._collect_trading_metrics()
                await self._collect_agent_metrics()
                await self._collect_market_data_metrics()
                
                self.performance_metrics['total_metrics_collected'] += 1
                self.performance_metrics['last_metrics_update'] = datetime.now()
                
                await asyncio.sleep(self.metrics_collection_interval)
                
        except Exception as e:
            logger.error(f"Error in metrics collection loop: {e}")
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent / 100.0
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent / 100.0
            
            # Network I/O
            network = psutil.net_io_counters()
            
            # Update system metrics
            self.agent_status.labels(agent_type='system').set(1 if cpu_percent < 90 else 0)
            
            # Log system metrics
            logger.debug(f"System metrics - CPU: {cpu_percent}%, Memory: {memory_percent:.2%}, Disk: {disk_percent:.2%}")
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _collect_trading_metrics(self):
        """Collect trading-related metrics"""
        try:
            # Get execution engine report
            execution_report = await self.position_execution.get_execution_engine_report()
            
            # Update trading metrics
            self.portfolio_value.labels(currency='USDT').set(execution_report['execution_metrics']['total_pnl'])
            
            # Update active positions
            for order_id, order_data in execution_report['active_orders'].items():
                self.active_positions.labels(symbol=order_data['symbol']).set(1)
                self.position_pnl.labels(symbol=order_data['symbol'], side=order_data['side']).set(
                    execution_report['execution_metrics']['total_pnl']
                )
            
            # Update risk metrics
            risk_report = await self.position_execution.risk_management.get_risk_management_report()
            self.risk_score.labels(symbol='portfolio', type='overall').set(
                risk_report['risk_metrics']['correlation_risk']
            )
            
        except Exception as e:
            logger.error(f"Error collecting trading metrics: {e}")
    
    async def _collect_agent_metrics(self):
        """Collect agent-related metrics"""
        try:
            # Update agent status
            self.agent_status.labels(agent_type='integrated_scoring').set(1)
            self.agent_status.labels(agent_type='position_execution').set(1)
            self.agent_status.labels(agent_type='market_data_connector').set(1)
            
            # Update agent task metrics
            self.agent_tasks_total.labels(agent_type='integrated_scoring', status='completed').inc()
            self.agent_tasks_total.labels(agent_type='position_execution', status='completed').inc()
            
        except Exception as e:
            logger.error(f"Error collecting agent metrics: {e}")
    
    async def _collect_market_data_metrics(self):
        """Collect market data metrics"""
        try:
            # Get connector status
            connector_status = await self.market_data_connector.get_connector_status()
            
            # Update market data metrics
            for symbol in ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']:
                self.market_data_volume.labels(exchange='binance', symbol=symbol).inc()
                
                # Simulate latency
                latency = np.random.uniform(0.01, 0.1)
                self.market_data_latency.labels(exchange='binance', symbol=symbol).observe(latency)
            
        except Exception as e:
            logger.error(f"Error collecting market data metrics: {e}")
    
    async def _alert_checking_loop(self):
        """Main alert checking loop"""
        try:
            while self.monitoring_enabled:
                await self._check_alert_rules()
                await asyncio.sleep(self.alert_check_interval)
                
        except Exception as e:
            logger.error(f"Error in alert checking loop: {e}")
    
    async def _check_alert_rules(self):
        """Check all alert rules"""
        try:
            for rule_name, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue
                
                # Get current metric value
                current_value = await self._get_metric_value(rule_name)
                
                # Check if alert should be triggered
                if await self._evaluate_alert_condition(rule, current_value):
                    await self._trigger_alert(rule, current_value)
                else:
                    await self._resolve_alert(rule_name)
                    
        except Exception as e:
            logger.error(f"Error checking alert rules: {e}")
    
    async def _get_metric_value(self, rule_name: str) -> float:
        """Get current metric value for alert rule"""
        try:
            if rule_name == 'high_risk_score':
                risk_report = await self.position_execution.risk_management.get_risk_management_report()
                return risk_report['risk_metrics']['correlation_risk']
            
            elif rule_name == 'low_win_rate':
                execution_report = await self.position_execution.get_execution_engine_report()
                return execution_report['execution_metrics']['success_rate']
            
            elif rule_name == 'high_drawdown':
                risk_report = await self.position_execution.risk_management.get_risk_management_report()
                return risk_report['risk_metrics']['max_drawdown']
            
            elif rule_name == 'api_error_rate':
                return 0.02  # Simulated error rate
            
            elif rule_name == 'low_confidence':
                return 0.6  # Simulated confidence
            
            elif rule_name == 'system_memory_high':
                memory = psutil.virtual_memory()
                return memory.percent / 100.0
            
            elif rule_name == 'cpu_usage_high':
                return psutil.cpu_percent(interval=1) / 100.0
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting metric value for {rule_name}: {e}")
            return 0.0
    
    async def _evaluate_alert_condition(self, rule: AlertRule, current_value: float) -> bool:
        """Evaluate if alert condition is met"""
        try:
            if '>' in rule.condition:
                return current_value > rule.threshold
            elif '<' in rule.condition:
                return current_value < rule.threshold
            elif '>=' in rule.condition:
                return current_value >= rule.threshold
            elif '<=' in rule.condition:
                return current_value <= rule.threshold
            elif '==' in rule.condition:
                return current_value == rule.threshold
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating alert condition: {e}")
            return False
    
    async def _trigger_alert(self, rule: AlertRule, current_value: float):
        """Trigger an alert"""
        try:
            alert = Alert(
                rule_name=rule.name,
                severity=rule.severity,
                message=f"{rule.description}: Current value {current_value:.2f}, Threshold {rule.threshold:.2f}",
                timestamp=datetime.now(),
                value=current_value,
                threshold=rule.threshold
            )
            
            # Add to active alerts
            self.active_alerts[rule.name] = alert
            
            # Add to history
            self.alert_history.append(alert)
            
            # Update metrics
            self.performance_metrics['total_alerts_generated'] += 1
            
            # Trigger callbacks
            await self._trigger_alert_callbacks(alert)
            
            logger.warning(f"Alert triggered: {alert.message}")
            
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    async def _resolve_alert(self, rule_name: str):
        """Resolve an alert"""
        try:
            if rule_name in self.active_alerts:
                alert = self.active_alerts[rule_name]
                alert.status = "resolved"
                
                # Remove from active alerts
                del self.active_alerts[rule_name]
                
                logger.info(f"Alert resolved: {alert.message}")
                
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
    
    async def _trigger_alert_callbacks(self, alert: Alert):
        """Trigger alert callbacks"""
        try:
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback {callback.__name__}: {e}")
                    
        except Exception as e:
            logger.error(f"Error triggering alert callbacks: {e}")
    
    async def _system_health_monitoring(self):
        """Monitor system health"""
        try:
            while self.monitoring_enabled:
                # Check system health
                cpu_usage = psutil.cpu_percent(interval=1)
                memory_usage = psutil.virtual_memory().percent
                
                # Update health status
                if cpu_usage > 90 or memory_usage > 90:
                    self.performance_metrics['monitoring_health'] = 'critical'
                elif cpu_usage > 80 or memory_usage > 80:
                    self.performance_metrics['monitoring_health'] = 'warning'
                else:
                    self.performance_metrics['monitoring_health'] = 'healthy'
                
                # Update uptime
                self.performance_metrics['system_uptime'] += 1
                
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            logger.error(f"Error in system health monitoring: {e}")
    
    async def register_alert_callback(self, callback: Callable):
        """Register an alert callback"""
        self.alert_callbacks.append(callback)
        logger.info(f"Registered alert callback: {callback.__name__}")
    
    async def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        try:
            return generate_latest().decode('utf-8')
        except Exception as e:
            logger.error(f"Error generating Prometheus metrics: {e}")
            return ""
    
    async def get_monitoring_report(self) -> Dict[str, Any]:
        """Get comprehensive monitoring report"""
        return {
            'system_health': {
                'status': self.performance_metrics['monitoring_health'],
                'uptime': self.performance_metrics['system_uptime'],
                'last_update': self.performance_metrics['last_metrics_update'].isoformat() if self.performance_metrics['last_metrics_update'] else None
            },
            'metrics_collection': {
                'total_metrics_collected': self.performance_metrics['total_metrics_collected'],
                'collection_interval': self.metrics_collection_interval,
                'monitoring_enabled': self.monitoring_enabled
            },
            'alerts': {
                'active_alerts': len(self.active_alerts),
                'total_alerts_generated': self.performance_metrics['total_alerts_generated'],
                'alert_rules': len(self.alert_rules),
                'alert_check_interval': self.alert_check_interval
            },
            'active_alerts': {
                rule_name: {
                    'severity': alert.severity,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'value': alert.value,
                    'threshold': alert.threshold
                }
                for rule_name, alert in self.active_alerts.items()
            },
            'alert_rules': {
                rule_name: {
                    'condition': rule.condition,
                    'threshold': rule.threshold,
                    'severity': rule.severity,
                    'description': rule.description,
                    'enabled': rule.enabled
                }
                for rule_name, rule in self.alert_rules.items()
            },
            'registered_callbacks': len(self.alert_callbacks),
            'timestamp': datetime.now().isoformat()
        }

# Global instance
prometheus_monitoring = PrometheusMonitoring() 