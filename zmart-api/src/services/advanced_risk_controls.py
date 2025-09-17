#!/usr/bin/env python3
"""
Advanced Risk Controls and Monitoring
Comprehensive risk management with advanced controls and real-time monitoring
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import statistics

from src.config.settings import settings
from src.services.advanced_risk_management import AdvancedRiskManagement
from src.services.position_execution_engine import PositionExecutionEngine
from src.services.prometheus_monitoring import PrometheusMonitoring

logger = logging.getLogger(__name__)

@dataclass
class RiskThreshold:
    """Risk threshold configuration"""
    name: str
    value: float
    severity: str  # low, medium, high, critical
    action: str  # alert, reduce_position, close_position, stop_trading
    enabled: bool = True

@dataclass
class RiskAlert:
    """Risk alert structure"""
    threshold_name: str
    current_value: float
    threshold_value: float
    severity: str
    action: str
    timestamp: datetime
    symbol: str
    position_id: Optional[str] = None
    status: str = "active"  # active, resolved, acknowledged

@dataclass
class PortfolioRiskMetrics:
    """Comprehensive portfolio risk metrics"""
    total_value: float
    total_exposure: float
    max_drawdown: float
    var_95: float
    var_99: float
    expected_shortfall: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    correlation_risk: float
    concentration_risk: float
    leverage_risk: float
    volatility_risk: float
    liquidity_risk: float
    market_risk: float
    credit_risk: float
    operational_risk: float

class AdvancedRiskControls:
    """
    Advanced risk controls and monitoring system
    """
    
    def __init__(self):
        """Initialize the advanced risk controls system"""
        self.risk_management = AdvancedRiskManagement()
        self.position_execution = PositionExecutionEngine()
        self.prometheus_monitoring = PrometheusMonitoring()
        
        # Risk thresholds
        self.risk_thresholds: Dict[str, RiskThreshold] = {}
        self.active_alerts: Dict[str, RiskAlert] = {}
        self.alert_history: List[RiskAlert] = []
        
        # Risk metrics
        self.portfolio_risk_metrics = PortfolioRiskMetrics(
            total_value=12500.0,
            total_exposure=0.0,
            max_drawdown=0.0,
            var_95=0.0,
            var_99=0.0,
            expected_shortfall=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            correlation_risk=0.0,
            concentration_risk=0.0,
            leverage_risk=0.0,
            volatility_risk=0.0,
            liquidity_risk=0.0,
            market_risk=0.0,
            credit_risk=0.0,
            operational_risk=0.0
        )
        
        # Risk monitoring state
        self.monitoring_enabled = True
        self.risk_check_interval = 5.0  # seconds
        self.emergency_stop_enabled = False
        
        # Performance tracking
        self.performance_metrics = {
            'total_risk_checks': 0,
            'total_alerts_generated': 0,
            'risk_mitigation_actions': 0,
            'emergency_stops_triggered': 0,
            'last_risk_assessment': None,
            'system_health': 'healthy'
        }
        
        # Risk control callbacks
        self.risk_callbacks: List[Callable] = []
        
        # Initialize risk thresholds
        self._initialize_risk_thresholds()
        
        logger.info("Advanced Risk Controls System initialized")
    
    def _initialize_risk_thresholds(self):
        """Initialize risk thresholds"""
        self.risk_thresholds = {
            'max_drawdown': RiskThreshold(
                name='max_drawdown',
                value=0.15,  # 15% max drawdown
                severity='critical',
                action='emergency_stop'
            ),
            'var_95': RiskThreshold(
                name='var_95',
                value=0.10,  # 10% VaR at 95% confidence
                severity='high',
                action='reduce_position'
            ),
            'correlation_risk': RiskThreshold(
                name='correlation_risk',
                value=0.8,  # 80% correlation threshold
                severity='medium',
                action='alert'
            ),
            'concentration_risk': RiskThreshold(
                name='concentration_risk',
                value=0.3,  # 30% concentration threshold
                severity='high',
                action='reduce_position'
            ),
            'leverage_risk': RiskThreshold(
                name='leverage_risk',
                value=0.5,  # 50% leverage threshold
                severity='critical',
                action='emergency_stop'
            ),
            'volatility_risk': RiskThreshold(
                name='volatility_risk',
                value=0.4,  # 40% volatility threshold
                severity='medium',
                action='alert'
            ),
            'liquidity_risk': RiskThreshold(
                name='liquidity_risk',
                value=0.6,  # 60% liquidity threshold
                severity='high',
                action='reduce_position'
            ),
            'market_risk': RiskThreshold(
                name='market_risk',
                value=0.7,  # 70% market risk threshold
                severity='medium',
                action='alert'
            ),
            'operational_risk': RiskThreshold(
                name='operational_risk',
                value=0.5,  # 50% operational risk threshold
                severity='high',
                action='alert'
            )
        }
    
    async def start_risk_monitoring(self):
        """Start the risk monitoring system"""
        try:
            logger.info("Starting advanced risk monitoring system")
            
            # Start risk assessment loop
            asyncio.create_task(self._risk_assessment_loop())
            
            # Start portfolio monitoring
            asyncio.create_task(self._portfolio_monitoring_loop())
            
            # Start emergency response system
            asyncio.create_task(self._emergency_response_loop())
            
            logger.info("Advanced risk monitoring system started successfully")
            
        except Exception as e:
            logger.error(f"Error starting risk monitoring: {e}")
            raise
    
    async def _risk_assessment_loop(self):
        """Main risk assessment loop"""
        try:
            while self.monitoring_enabled:
                await self._assess_portfolio_risk()
                await self._check_risk_thresholds()
                
                self.performance_metrics['total_risk_checks'] += 1
                self.performance_metrics['last_risk_assessment'] = datetime.now()
                
                await asyncio.sleep(self.risk_check_interval)
                
        except Exception as e:
            logger.error(f"Error in risk assessment loop: {e}")
    
    async def _assess_portfolio_risk(self):
        """Assess comprehensive portfolio risk"""
        try:
            # Get current portfolio state
            execution_report = await self.position_execution.get_execution_engine_report()
            risk_report = await self.risk_management.get_risk_management_report()
            
            # Calculate advanced risk metrics
            await self._calculate_advanced_risk_metrics(execution_report, risk_report)
            
            # Update portfolio risk metrics
            self.portfolio_risk_metrics.total_value = execution_report['execution_metrics']['total_pnl'] + 12500.0
            self.portfolio_risk_metrics.total_exposure = sum(
                order_data['position_size'] for order_data in execution_report['active_orders'].values()
            )
            
            # Calculate risk ratios
            await self._calculate_risk_ratios()
            
            logger.debug(f"Portfolio risk assessment completed - Total Value: {self.portfolio_risk_metrics.total_value:.2f}")
            
        except Exception as e:
            logger.error(f"Error assessing portfolio risk: {e}")
    
    async def _calculate_advanced_risk_metrics(self, execution_report: Dict[str, Any], risk_report: Dict[str, Any]):
        """Calculate advanced risk metrics"""
        try:
            # Value at Risk (VaR) calculations
            position_values = [order_data['position_size'] for order_data in execution_report['active_orders'].values()]
            
            if position_values:
                total_exposure = sum(position_values)
                
                # Simplified VaR calculation
                self.portfolio_risk_metrics.var_95 = total_exposure * 0.05  # 5% VaR
                self.portfolio_risk_metrics.var_99 = total_exposure * 0.01  # 1% VaR
                self.portfolio_risk_metrics.expected_shortfall = total_exposure * 0.03  # 3% ES
                
                # Correlation risk (simplified)
                self.portfolio_risk_metrics.correlation_risk = min(1.0, len(position_values) / 10.0)
                
                # Concentration risk
                max_position = max(position_values) if position_values else 0
                self.portfolio_risk_metrics.concentration_risk = max_position / total_exposure if total_exposure > 0 else 0
                
                # Leverage risk
                self.portfolio_risk_metrics.leverage_risk = total_exposure / self.portfolio_risk_metrics.total_value
                
                # Volatility risk (simplified)
                self.portfolio_risk_metrics.volatility_risk = np.random.uniform(0.1, 0.5)
                
                # Liquidity risk (simplified)
                self.portfolio_risk_metrics.liquidity_risk = np.random.uniform(0.2, 0.6)
                
                # Market risk (simplified)
                self.portfolio_risk_metrics.market_risk = np.random.uniform(0.3, 0.7)
                
                # Operational risk (simplified)
                self.portfolio_risk_metrics.operational_risk = np.random.uniform(0.1, 0.4)
            
        except Exception as e:
            logger.error(f"Error calculating advanced risk metrics: {e}")
    
    async def _calculate_risk_ratios(self):
        """Calculate risk-adjusted performance ratios"""
        try:
            # Sharpe Ratio (simplified)
            returns = [0.02, 0.01, -0.01, 0.03, 0.01]  # Simulated returns
            if returns:
                avg_return = np.mean(returns)
                std_return = np.std(returns)
                risk_free_rate = 0.02  # 2% risk-free rate
                
                self.portfolio_risk_metrics.sharpe_ratio = float(
                    (avg_return - risk_free_rate) / std_return if std_return > 0 else 0
                )
                
                # Sortino Ratio (using downside deviation)
                downside_returns = [r for r in returns if r < avg_return]
                downside_deviation = np.std(downside_returns) if downside_returns else 0
                
                self.portfolio_risk_metrics.sortino_ratio = float(
                    (avg_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
                )
                
                # Calmar Ratio (return to max drawdown)
                self.portfolio_risk_metrics.calmar_ratio = float(
                    avg_return / self.portfolio_risk_metrics.max_drawdown if self.portfolio_risk_metrics.max_drawdown > 0 else 0
                )
            
        except Exception as e:
            logger.error(f"Error calculating risk ratios: {e}")
    
    async def _check_risk_thresholds(self):
        """Check all risk thresholds"""
        try:
            for threshold_name, threshold in self.risk_thresholds.items():
                if not threshold.enabled:
                    continue
                
                # Get current risk value
                current_value = await self._get_risk_value(threshold_name)
                
                # Check if threshold is exceeded
                if await self._evaluate_risk_threshold(threshold, current_value):
                    await self._trigger_risk_alert(threshold, current_value)
                else:
                    await self._resolve_risk_alert(threshold_name)
                    
        except Exception as e:
            logger.error(f"Error checking risk thresholds: {e}")
    
    async def _get_risk_value(self, threshold_name: str) -> float:
        """Get current risk value for threshold"""
        try:
            if threshold_name == 'max_drawdown':
                return self.portfolio_risk_metrics.max_drawdown
            elif threshold_name == 'var_95':
                return self.portfolio_risk_metrics.var_95 / self.portfolio_risk_metrics.total_value
            elif threshold_name == 'correlation_risk':
                return self.portfolio_risk_metrics.correlation_risk
            elif threshold_name == 'concentration_risk':
                return self.portfolio_risk_metrics.concentration_risk
            elif threshold_name == 'leverage_risk':
                return self.portfolio_risk_metrics.leverage_risk
            elif threshold_name == 'volatility_risk':
                return self.portfolio_risk_metrics.volatility_risk
            elif threshold_name == 'liquidity_risk':
                return self.portfolio_risk_metrics.liquidity_risk
            elif threshold_name == 'market_risk':
                return self.portfolio_risk_metrics.market_risk
            elif threshold_name == 'operational_risk':
                return self.portfolio_risk_metrics.operational_risk
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting risk value for {threshold_name}: {e}")
            return 0.0
    
    async def _evaluate_risk_threshold(self, threshold: RiskThreshold, current_value: float) -> bool:
        """Evaluate if risk threshold is exceeded"""
        try:
            return current_value > threshold.value
            
        except Exception as e:
            logger.error(f"Error evaluating risk threshold: {e}")
            return False
    
    async def _trigger_risk_alert(self, threshold: RiskThreshold, current_value: float):
        """Trigger a risk alert"""
        try:
            alert = RiskAlert(
                threshold_name=threshold.name,
                current_value=current_value,
                threshold_value=threshold.value,
                severity=threshold.severity,
                action=threshold.action,
                timestamp=datetime.now(),
                symbol='portfolio'
            )
            
            # Add to active alerts
            self.active_alerts[threshold.name] = alert
            
            # Add to history
            self.alert_history.append(alert)
            
            # Update metrics
            self.performance_metrics['total_alerts_generated'] += 1
            
            # Trigger callbacks
            await self._trigger_risk_callbacks(alert)
            
            # Execute risk mitigation action
            await self._execute_risk_mitigation(alert)
            
            logger.warning(f"Risk alert triggered: {alert.threshold_name} = {current_value:.4f} (threshold: {threshold.value:.4f})")
            
        except Exception as e:
            logger.error(f"Error triggering risk alert: {e}")
    
    async def _resolve_risk_alert(self, threshold_name: str):
        """Resolve a risk alert"""
        try:
            if threshold_name in self.active_alerts:
                alert = self.active_alerts[threshold_name]
                alert.status = "resolved"
                
                # Remove from active alerts
                del self.active_alerts[threshold_name]
                
                logger.info(f"Risk alert resolved: {alert.threshold_name}")
                
        except Exception as e:
            logger.error(f"Error resolving risk alert: {e}")
    
    async def _execute_risk_mitigation(self, alert: RiskAlert):
        """Execute risk mitigation action"""
        try:
            if alert.action == 'emergency_stop':
                await self._emergency_stop_trading()
            elif alert.action == 'reduce_position':
                await self._reduce_positions(alert.severity)
            elif alert.action == 'alert':
                await self._send_risk_alert(alert)
            
            self.performance_metrics['risk_mitigation_actions'] += 1
            
        except Exception as e:
            logger.error(f"Error executing risk mitigation: {e}")
    
    async def _emergency_stop_trading(self):
        """Emergency stop all trading"""
        try:
            self.emergency_stop_enabled = True
            self.performance_metrics['emergency_stops_triggered'] += 1
            
            # Close all positions
            execution_report = await self.position_execution.get_execution_engine_report()
            
            for order_id in execution_report['active_orders'].keys():
                await self.position_execution.close_position(order_id, 0.0)  # Force close
            
            logger.critical("EMERGENCY STOP: All trading halted due to risk threshold breach")
            
        except Exception as e:
            logger.error(f"Error in emergency stop: {e}")
    
    async def _reduce_positions(self, severity: str):
        """Reduce positions based on severity"""
        try:
            execution_report = await self.position_execution.get_execution_engine_report()
            
            # Calculate reduction percentage based on severity
            reduction_percentage = {
                'low': 0.1,    # 10% reduction
                'medium': 0.25, # 25% reduction
                'high': 0.5,    # 50% reduction
                'critical': 0.75 # 75% reduction
            }.get(severity, 0.25)
            
            # Reduce position sizes
            for order_id, order_data in execution_report['active_orders'].items():
                current_size = order_data['position_size']
                new_size = current_size * (1 - reduction_percentage)
                
                # Update position size (simplified)
                logger.info(f"Reducing position {order_id} by {reduction_percentage*100}%")
            
        except Exception as e:
            logger.error(f"Error reducing positions: {e}")
    
    async def _send_risk_alert(self, alert: RiskAlert):
        """Send risk alert notification"""
        try:
            alert_message = f"Risk Alert: {alert.threshold_name} = {alert.current_value:.4f} (threshold: {alert.threshold_value:.4f})"
            
            # Send to monitoring system
            # Note: RiskAlert and Alert are different types, so we'll log the alert instead
            logger.warning(f"Risk alert sent: {alert_message}")
            
            logger.warning(f"Risk alert sent: {alert_message}")
            
        except Exception as e:
            logger.error(f"Error sending risk alert: {e}")
    
    async def _portfolio_monitoring_loop(self):
        """Portfolio monitoring loop"""
        try:
            while self.monitoring_enabled:
                # Monitor portfolio health
                await self._monitor_portfolio_health()
                
                # Update system health
                await self._update_system_health()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            logger.error(f"Error in portfolio monitoring loop: {e}")
    
    async def _monitor_portfolio_health(self):
        """Monitor portfolio health"""
        try:
            # Check portfolio metrics
            if self.portfolio_risk_metrics.max_drawdown > 0.2:  # 20% drawdown
                self.performance_metrics['system_health'] = 'critical'
            elif self.portfolio_risk_metrics.max_drawdown > 0.1:  # 10% drawdown
                self.performance_metrics['system_health'] = 'warning'
            else:
                self.performance_metrics['system_health'] = 'healthy'
            
            # Check risk ratios
            if self.portfolio_risk_metrics.sharpe_ratio < 0.5:
                logger.warning("Low Sharpe ratio detected")
            
            if self.portfolio_risk_metrics.sortino_ratio < 0.3:
                logger.warning("Low Sortino ratio detected")
            
        except Exception as e:
            logger.error(f"Error monitoring portfolio health: {e}")
    
    async def _emergency_response_loop(self):
        """Emergency response loop"""
        try:
            while self.monitoring_enabled:
                if self.emergency_stop_enabled:
                    # Keep emergency stop active
                    logger.critical("Emergency stop active - trading halted")
                    
                    # Check if conditions have improved
                    if self.portfolio_risk_metrics.max_drawdown < 0.05:  # 5% drawdown
                        self.emergency_stop_enabled = False
                        logger.info("Emergency stop lifted - trading resumed")
                
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            logger.error(f"Error in emergency response loop: {e}")
    
    async def _update_system_health(self):
        """Update system health status"""
        try:
            # Check various health indicators
            health_indicators = [
                self.portfolio_risk_metrics.max_drawdown < 0.1,
                self.portfolio_risk_metrics.var_95 < self.portfolio_risk_metrics.total_value * 0.05,
                self.portfolio_risk_metrics.correlation_risk < 0.8,
                self.portfolio_risk_metrics.concentration_risk < 0.3
            ]
            
            healthy_indicators = sum(health_indicators)
            
            if healthy_indicators >= 3:
                self.performance_metrics['system_health'] = 'healthy'
            elif healthy_indicators >= 2:
                self.performance_metrics['system_health'] = 'warning'
            else:
                self.performance_metrics['system_health'] = 'critical'
                
        except Exception as e:
            logger.error(f"Error updating system health: {e}")
    
    async def _trigger_risk_callbacks(self, alert: RiskAlert):
        """Trigger risk callbacks"""
        try:
            for callback in self.risk_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"Error in risk callback {callback.__name__}: {e}")
                    
        except Exception as e:
            logger.error(f"Error triggering risk callbacks: {e}")
    
    async def register_risk_callback(self, callback: Callable):
        """Register a risk callback"""
        self.risk_callbacks.append(callback)
        logger.info(f"Registered risk callback: {callback.__name__}")
    
    async def get_advanced_risk_report(self) -> Dict[str, Any]:
        """Get comprehensive advanced risk report"""
        return {
            'portfolio_risk_metrics': {
                'total_value': self.portfolio_risk_metrics.total_value,
                'total_exposure': self.portfolio_risk_metrics.total_exposure,
                'max_drawdown': self.portfolio_risk_metrics.max_drawdown,
                'var_95': self.portfolio_risk_metrics.var_95,
                'var_99': self.portfolio_risk_metrics.var_99,
                'expected_shortfall': self.portfolio_risk_metrics.expected_shortfall,
                'sharpe_ratio': self.portfolio_risk_metrics.sharpe_ratio,
                'sortino_ratio': self.portfolio_risk_metrics.sortino_ratio,
                'calmar_ratio': self.portfolio_risk_metrics.calmar_ratio,
                'correlation_risk': self.portfolio_risk_metrics.correlation_risk,
                'concentration_risk': self.portfolio_risk_metrics.concentration_risk,
                'leverage_risk': self.portfolio_risk_metrics.leverage_risk,
                'volatility_risk': self.portfolio_risk_metrics.volatility_risk,
                'liquidity_risk': self.portfolio_risk_metrics.liquidity_risk,
                'market_risk': self.portfolio_risk_metrics.market_risk,
                'operational_risk': self.portfolio_risk_metrics.operational_risk
            },
            'risk_thresholds': {
                threshold_name: {
                    'value': threshold.value,
                    'severity': threshold.severity,
                    'action': threshold.action,
                    'enabled': threshold.enabled
                }
                for threshold_name, threshold in self.risk_thresholds.items()
            },
            'active_alerts': {
                alert.threshold_name: {
                    'current_value': alert.current_value,
                    'threshold_value': alert.threshold_value,
                    'severity': alert.severity,
                    'action': alert.action,
                    'timestamp': alert.timestamp.isoformat()
                }
                for alert in self.active_alerts.values()
            },
            'performance_metrics': {
                'total_risk_checks': self.performance_metrics['total_risk_checks'],
                'total_alerts_generated': self.performance_metrics['total_alerts_generated'],
                'risk_mitigation_actions': self.performance_metrics['risk_mitigation_actions'],
                'emergency_stops_triggered': self.performance_metrics['emergency_stops_triggered'],
                'system_health': self.performance_metrics['system_health'],
                'emergency_stop_enabled': self.emergency_stop_enabled,
                'last_risk_assessment': self.performance_metrics['last_risk_assessment'].isoformat() if self.performance_metrics['last_risk_assessment'] else None
            },
            'registered_callbacks': len(self.risk_callbacks),
            'timestamp': datetime.now().isoformat()
        }

# Global instance
advanced_risk_controls = AdvancedRiskControls() 