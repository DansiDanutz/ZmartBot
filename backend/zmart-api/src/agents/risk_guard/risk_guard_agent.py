"""
Zmart Trading Bot Platform - Risk Guard Agent
Circuit breaker and risk management system for portfolio protection
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from src.config.settings import settings
from src.utils.event_bus import EventBus, EventType, Event
from src.utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CircuitBreakerState(Enum):
    """Circuit breaker state enumeration"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Trading halted
    HALF_OPEN = "half_open"  # Limited trading

@dataclass
class RiskAlert:
    """Risk alert structure"""
    alert_id: str
    risk_level: RiskLevel
    alert_type: str
    message: str
    symbol: Optional[str]
    portfolio_impact: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class PositionRisk:
    """Position risk assessment"""
    symbol: str
    position_size: float
    unrealized_pnl: float
    risk_score: float
    liquidation_price: Optional[float]
    margin_ratio: float
    timestamp: datetime

class RiskGuardAgent:
    """
    Risk management agent that monitors portfolio exposure and implements
    circuit breaker patterns to protect against catastrophic losses.
    
    Responsibilities:
    - Portfolio risk monitoring
    - Circuit breaker implementation
    - Position size limits
    - Drawdown protection
    - Real-time risk alerts
    - Correlation risk analysis
    """
    
    def __init__(self):
        """Initialize the risk guard agent"""
        self.agent_id = "risk_guard_agent"
        self.status = "stopped"
        self.event_bus = EventBus()
        self.metrics = MetricsCollector()
        
        # Risk configuration
        self.max_daily_loss = settings.MAX_DAILY_LOSS
        self.max_drawdown = settings.MAX_DRAWDOWN
        self.circuit_breaker_threshold = settings.CIRCUIT_BREAKER_THRESHOLD
        self.max_position_size = settings.MAX_POSITION_SIZE
        self.min_position_size = settings.MIN_POSITION_SIZE
        
        # Circuit breaker state
        self.circuit_breaker_state = CircuitBreakerState.CLOSED
        self.circuit_breaker_triggered_at: Optional[datetime] = None
        self.circuit_breaker_recovery_time = 300  # 5 minutes
        
        # Risk monitoring state
        self.active_positions: Dict[str, PositionRisk] = {}
        self.risk_alerts: List[RiskAlert] = []
        self.daily_pnl = 0.0
        self.peak_portfolio_value = 0.0
        self.current_portfolio_value = 0.0
        
        # Risk metrics
        self.risk_metrics = {
            "total_positions": 0,
            "total_exposure": 0.0,
            "largest_position": 0.0,
            "average_position_size": 0.0,
            "portfolio_beta": 0.0,
            "var_95": 0.0,  # Value at Risk (95%)
            "max_drawdown_current": 0.0,
            "last_updated": datetime.now()
        }
        
        # Task management
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
        logger.info("Risk guard agent initialized")
    
    async def start(self):
        """Start the risk guard agent"""
        if self.status == "running":
            logger.warning("Risk guard agent already running")
            return
        
        logger.info("Starting risk guard agent")
        self.status = "starting"
        
        try:
            # Start background tasks
            self._running = True
            self._tasks = [
                asyncio.create_task(self._risk_monitoring_loop()),
                asyncio.create_task(self._circuit_breaker_loop()),
                asyncio.create_task(self._position_monitoring_loop()),
                asyncio.create_task(self._metrics_update_loop())
            ]
            
            # Register event handlers
            await self._register_event_handlers()
            
            # Update status
            self.status = "running"
            logger.info("Risk guard agent started successfully")
            
            # Emit startup event
            startup_event = Event(
                type=EventType.AGENT_STARTED,
                data={
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            await self.event_bus.emit(startup_event)
            
        except Exception as e:
            self.status = "error"
            logger.error(f"Failed to start risk guard agent: {e}")
            raise
    
    async def stop(self):
        """Stop the risk guard agent"""
        if self.status == "stopped":
            logger.warning("Risk guard agent already stopped")
            return
        
        logger.info("Stopping risk guard agent")
        self.status = "stopping"
        
        try:
            # Stop background tasks
            self._running = False
            
            # Cancel all tasks
            for task in self._tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            if self._tasks:
                await asyncio.gather(*self._tasks, return_exceptions=True)
            
            # Update status
            self.status = "stopped"
            logger.info("Risk guard agent stopped successfully")
            
            # Emit shutdown event
            shutdown_event = Event(
                type=EventType.AGENT_STOPPED,
                data={
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            await self.event_bus.emit(shutdown_event)
            
        except Exception as e:
            logger.error(f"Error stopping risk guard agent: {e}")
            raise
    
    async def check_trade_risk(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a trade meets risk management requirements
        
        Args:
            trade_data: Trade data including symbol, size, type, etc.
            
        Returns:
            Dict containing risk assessment and approval status
        """
        symbol = trade_data.get("symbol")
        position_size = trade_data.get("position_size", 0.0)
        trade_type = trade_data.get("trade_type", "market")
        
        logger.info(f"Checking risk for trade: {symbol} - {position_size}")
        
        # Check circuit breaker state
        if self.circuit_breaker_state == CircuitBreakerState.OPEN:
            return {
                "approved": False,
                "reason": "Circuit breaker is OPEN - trading halted",
                "risk_level": RiskLevel.CRITICAL,
                "timestamp": datetime.now().isoformat()
            }
        
        # Check position size limits
        if position_size > self.max_position_size:
            return {
                "approved": False,
                "reason": f"Position size {position_size} exceeds maximum {self.max_position_size}",
                "risk_level": RiskLevel.HIGH,
                "timestamp": datetime.now().isoformat()
            }
        
        if position_size < self.min_position_size:
            return {
                "approved": False,
                "reason": f"Position size {position_size} below minimum {self.min_position_size}",
                "risk_level": RiskLevel.LOW,
                "timestamp": datetime.now().isoformat()
            }
        
        # Check daily loss limits
        if self.daily_pnl < -self.max_daily_loss:
            return {
                "approved": False,
                "reason": f"Daily loss limit exceeded: {self.daily_pnl}",
                "risk_level": RiskLevel.CRITICAL,
                "timestamp": datetime.now().isoformat()
            }
        
        # Check drawdown limits
        current_drawdown = await self._calculate_drawdown()
        if current_drawdown > self.max_drawdown:
            return {
                "approved": False,
                "reason": f"Maximum drawdown exceeded: {current_drawdown:.2%}",
                "risk_level": RiskLevel.CRITICAL,
                "timestamp": datetime.now().isoformat()
            }
        
        # Check correlation risk
        if symbol is not None:
            correlation_risk = await self._check_correlation_risk(symbol, position_size)
            if correlation_risk["high_correlation"]:
                return {
                    "approved": False,
                    "reason": f"High correlation risk with {correlation_risk['correlated_symbols']}",
                    "risk_level": RiskLevel.HIGH,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Check portfolio concentration
        if symbol is not None:
            concentration_risk = await self._check_concentration_risk(symbol, position_size)
            if concentration_risk["over_concentrated"]:
                return {
                    "approved": False,
                    "reason": f"Portfolio concentration risk: {concentration_risk['concentration']:.2%}",
                    "risk_level": RiskLevel.HIGH,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Trade approved
        return {
            "approved": True,
            "risk_level": RiskLevel.LOW,
            "risk_score": await self._calculate_trade_risk_score(trade_data),
            "timestamp": datetime.now().isoformat()
        }
    
    async def update_position(self, position_data: Dict[str, Any]):
        """Update position information for risk monitoring"""
        symbol = position_data.get("symbol")
        
        if symbol is not None:
            position_risk = PositionRisk(
                symbol=symbol,
                position_size=position_data.get("position_size", 0.0),
                unrealized_pnl=position_data.get("unrealized_pnl", 0.0),
                risk_score=position_data.get("risk_score", 0.0),
                liquidation_price=position_data.get("liquidation_price"),
                margin_ratio=position_data.get("margin_ratio", 0.0),
                timestamp=datetime.now()
            )
            
            self.active_positions[symbol] = position_risk
            
            # Update portfolio value
            await self._update_portfolio_value()
            
            logger.info(f"Updated position risk for {symbol}")
    
    async def remove_position(self, symbol: str):
        """Remove a position from risk monitoring"""
        if symbol in self.active_positions:
            del self.active_positions[symbol]
            await self._update_portfolio_value()
            logger.info(f"Removed position risk monitoring for {symbol}")
    
    async def get_risk_status(self) -> Dict[str, Any]:
        """Get current risk status and metrics"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "circuit_breaker_state": self.circuit_breaker_state.value,
            "circuit_breaker_triggered_at": self.circuit_breaker_triggered_at.isoformat() if self.circuit_breaker_triggered_at else None,
            "risk_metrics": self.risk_metrics,
            "active_positions": len(self.active_positions),
            "daily_pnl": self.daily_pnl,
            "current_drawdown": await self._calculate_drawdown(),
            "recent_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "risk_level": alert.risk_level.value,
                    "alert_type": alert.alert_type,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat()
                }
                for alert in self.risk_alerts[-10:]  # Last 10 alerts
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_position_risk(self, symbol: str) -> Optional[PositionRisk]:
        """Get risk assessment for a specific position"""
        return self.active_positions.get(symbol)
    
    async def get_all_position_risks(self) -> List[PositionRisk]:
        """Get risk assessment for all active positions"""
        return list(self.active_positions.values())
    
    async def _register_event_handlers(self):
        """Register event handlers for the risk guard agent"""
        self.event_bus.subscribe(EventType.TRADE_EXECUTED, self._handle_trade_executed)
        self.event_bus.subscribe(EventType.POSITION_UPDATED, self._handle_position_updated)
        self.event_bus.subscribe(EventType.MARKET_DATA_UPDATED, self._handle_market_data_updated)
    
    async def _risk_monitoring_loop(self):
        """Background task for continuous risk monitoring"""
        while self._running:
            try:
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
                # Check for risk violations
                await self._check_risk_violations()
                
                # Update risk metrics
                await self._update_risk_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in risk monitoring loop: {e}")
    
    async def _circuit_breaker_loop(self):
        """Background task for circuit breaker management"""
        while self._running:
            try:
                await asyncio.sleep(10.0)  # Check every 10 seconds
                
                # Check if circuit breaker should be triggered
                await self._check_circuit_breaker_conditions()
                
                # Check if circuit breaker should be reset
                await self._check_circuit_breaker_reset()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in circuit breaker loop: {e}")
    
    async def _position_monitoring_loop(self):
        """Background task for position monitoring"""
        while self._running:
            try:
                await asyncio.sleep(30.0)  # Check every 30 seconds
                
                # Monitor active positions
                await self._monitor_positions()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in position monitoring loop: {e}")
    
    async def _metrics_update_loop(self):
        """Background task for metrics updates"""
        while self._running:
            try:
                await asyncio.sleep(60.0)  # Update every minute
                
                # Update comprehensive risk metrics
                await self._update_comprehensive_metrics()
                
                # Emit risk metrics event
                risk_metrics_event = Event(
                    type=EventType.RISK_SCORE_UPDATED,
                    data={
                        "agent_id": self.agent_id,
                        "metrics": self.risk_metrics,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                await self.event_bus.emit(risk_metrics_event)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics update loop: {e}")
    
    async def _check_risk_violations(self):
        """Check for various risk violations"""
        # Check daily loss limit
        if self.daily_pnl < -self.max_daily_loss:
            await self._create_risk_alert(
                RiskLevel.CRITICAL,
                "daily_loss_limit",
                f"Daily loss limit exceeded: {self.daily_pnl:.2f}",
                None,
                self.daily_pnl
            )
        
        # Check drawdown limit
        current_drawdown = await self._calculate_drawdown()
        if current_drawdown > self.max_drawdown:
            await self._create_risk_alert(
                RiskLevel.CRITICAL,
                "drawdown_limit",
                f"Maximum drawdown exceeded: {current_drawdown:.2%}",
                None,
                current_drawdown
            )
        
        # Check individual position risks
        for symbol, position in self.active_positions.items():
            # Check margin ratio
            if position.margin_ratio > 0.8:
                await self._create_risk_alert(
                    RiskLevel.HIGH,
                    "high_margin_ratio",
                    f"High margin ratio for {symbol}: {position.margin_ratio:.2%}",
                    symbol,
                    position.margin_ratio
                )
            
            # Check unrealized PnL
            if position.unrealized_pnl < -position.position_size * 0.1:  # 10% loss
                await self._create_risk_alert(
                    RiskLevel.HIGH,
                    "large_unrealized_loss",
                    f"Large unrealized loss for {symbol}: {position.unrealized_pnl:.2f}",
                    symbol,
                    position.unrealized_pnl
                )
    
    async def _check_circuit_breaker_conditions(self):
        """Check if circuit breaker should be triggered"""
        # Check daily loss threshold
        if self.daily_pnl < -self.circuit_breaker_threshold:
            await self._trigger_circuit_breaker("Daily loss threshold exceeded")
            return
        
        # Check drawdown threshold
        current_drawdown = await self._calculate_drawdown()
        if current_drawdown > self.circuit_breaker_threshold:
            await self._trigger_circuit_breaker("Maximum drawdown threshold exceeded")
            return
        
        # Check portfolio concentration
        total_exposure = sum(pos.position_size for pos in self.active_positions.values())
        if total_exposure > self.current_portfolio_value * 0.8:  # 80% exposure
            await self._trigger_circuit_breaker("Portfolio concentration threshold exceeded")
            return
    
    async def _check_circuit_breaker_reset(self):
        """Check if circuit breaker should be reset"""
        if (self.circuit_breaker_state == CircuitBreakerState.OPEN and 
            self.circuit_breaker_triggered_at and
            datetime.now() - self.circuit_breaker_triggered_at > timedelta(seconds=self.circuit_breaker_recovery_time)):
            
            await self._reset_circuit_breaker()
    
    async def _trigger_circuit_breaker(self, reason: str):
        """Trigger the circuit breaker"""
        if self.circuit_breaker_state != CircuitBreakerState.OPEN:
            self.circuit_breaker_state = CircuitBreakerState.OPEN
            self.circuit_breaker_triggered_at = datetime.now()
            
            logger.warning(f"Circuit breaker triggered: {reason}")
            
            # Emit circuit breaker event
            circuit_breaker_event = Event(
                type=EventType.CIRCUIT_BREAKER_TRIGGERED,
                data={
                    "agent_id": self.agent_id,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                }
            )
            await self.event_bus.emit(circuit_breaker_event)
    
    async def _reset_circuit_breaker(self):
        """Reset the circuit breaker"""
        self.circuit_breaker_state = CircuitBreakerState.HALF_OPEN
        logger.info("Circuit breaker reset to HALF_OPEN state")
        
        # Emit circuit breaker reset event
        reset_event = Event(
            type=EventType.CIRCUIT_BREAKER_TRIGGERED,  # Reuse the same event type
            data={
                "agent_id": self.agent_id,
                "action": "reset",
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.event_bus.emit(reset_event)
    
    async def _monitor_positions(self):
        """Monitor active positions for risk changes"""
        for symbol, position in self.active_positions.items():
            # Update position risk score
            current_price = await self._get_current_price(symbol)
            if current_price:
                # Recalculate unrealized PnL and risk metrics
                # This is a simplified calculation
                pass
    
    async def _update_risk_metrics(self):
        """Update basic risk metrics"""
        self.risk_metrics["total_positions"] = len(self.active_positions)
        self.risk_metrics["total_exposure"] = sum(pos.position_size for pos in self.active_positions.values())
        self.risk_metrics["largest_position"] = max((pos.position_size for pos in self.active_positions.values()), default=0.0)
        self.risk_metrics["average_position_size"] = self.risk_metrics["total_exposure"] / max(self.risk_metrics["total_positions"], 1)
        self.risk_metrics["last_updated"] = datetime.now()
    
    async def _update_comprehensive_metrics(self):
        """Update comprehensive risk metrics including VaR and Beta"""
        # Calculate Value at Risk (simplified)
        position_values = [pos.position_size for pos in self.active_positions.values()]
        if position_values:
            # Simple VaR calculation (95% confidence)
            self.risk_metrics["var_95"] = sum(position_values) * 0.05  # 5% of total exposure
        
        # Calculate current drawdown
        self.risk_metrics["max_drawdown_current"] = await self._calculate_drawdown()
        
        # Update portfolio beta (simplified)
        self.risk_metrics["portfolio_beta"] = 1.0  # Placeholder
    
    async def _calculate_drawdown(self) -> float:
        """Calculate current portfolio drawdown"""
        if self.peak_portfolio_value > 0:
            return (self.peak_portfolio_value - self.current_portfolio_value) / self.peak_portfolio_value
        return 0.0
    
    async def _update_portfolio_value(self):
        """Update current portfolio value"""
        total_value = sum(pos.position_size for pos in self.active_positions.values())
        self.current_portfolio_value = total_value
        
        if self.current_portfolio_value > self.peak_portfolio_value:
            self.peak_portfolio_value = self.current_portfolio_value
    
    async def _check_correlation_risk(self, symbol: str, position_size: float) -> Dict[str, Any]:
        """Check correlation risk with existing positions"""
        # Simplified correlation check
        correlated_symbols = []
        for existing_symbol in self.active_positions.keys():
            if existing_symbol != symbol:
                # Simple correlation check (placeholder)
                correlated_symbols.append(existing_symbol)
        
        return {
            "high_correlation": len(correlated_symbols) > 2,
            "correlated_symbols": correlated_symbols
        }
    
    async def _check_concentration_risk(self, symbol: str, position_size: float) -> Dict[str, Any]:
        """Check portfolio concentration risk"""
        total_exposure = sum(pos.position_size for pos in self.active_positions.values()) + position_size
        concentration = position_size / total_exposure if total_exposure > 0 else 0
        
        return {
            "over_concentrated": concentration > 0.3,  # 30% threshold
            "concentration": concentration
        }
    
    async def _calculate_trade_risk_score(self, trade_data: Dict[str, Any]) -> float:
        """Calculate risk score for a trade"""
        # Simplified risk scoring
        base_score = 0.5
        position_size = trade_data.get("position_size", 0.0)
        
        # Adjust score based on position size
        if position_size > self.max_position_size * 0.8:
            base_score += 0.3
        
        return min(base_score, 1.0)
    
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        # Placeholder implementation
        return 100.0  # Mock price
    
    async def _create_risk_alert(self, risk_level: RiskLevel, alert_type: str, 
                                message: str, symbol: Optional[str], impact: float):
        """Create and store a risk alert"""
        alert = RiskAlert(
            alert_id=f"alert_{len(self.risk_alerts) + 1}",
            risk_level=risk_level,
            alert_type=alert_type,
            message=message,
            symbol=symbol,
            portfolio_impact=impact,
            timestamp=datetime.now(),
            metadata={}
        )
        
        self.risk_alerts.append(alert)
        
        # Emit risk alert event
        risk_alert_event = Event(
            type=EventType.RISK_THRESHOLD_EXCEEDED,
            data={
                "alert_id": alert.alert_id,
                "risk_level": alert.risk_level.value,
                "alert_type": alert.alert_type,
                "message": alert.message,
                "symbol": alert.symbol,
                "impact": alert.portfolio_impact,
                "timestamp": alert.timestamp.isoformat()
            }
        )
        await self.event_bus.emit(risk_alert_event)
        
        logger.warning(f"Risk alert created: {message}")
    
    async def _handle_trade_executed(self, event: Event):
        """Handle trade executed events"""
        trade_data = event.data
        symbol = trade_data.get("symbol")
        position_size = trade_data.get("position_size", 0.0)
        
        if symbol and position_size > 0:
            await self.update_position({
                "symbol": symbol,
                "position_size": position_size,
                "unrealized_pnl": 0.0,
                "risk_score": 0.5,
                "liquidation_price": None,
                "margin_ratio": 0.0
            })
    
    async def _handle_position_updated(self, event: Event):
        """Handle position updated events"""
        position_data = event.data
        await self.update_position(position_data)
    
    async def _handle_market_data_updated(self, event: Event):
        """Handle market data updated events"""
        # Update risk metrics based on market data
        await self._update_risk_metrics() 