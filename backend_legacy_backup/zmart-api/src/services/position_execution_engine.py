#!/usr/bin/env python3
"""
Position Execution Engine
Implements advanced risk management in position execution
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from src.config.settings import settings
from src.services.advanced_risk_management import AdvancedRiskManagement
from src.services.calibrated_scoring_service import CalibratedScoringService
from src.services.real_time_market_data_connector import RealTimeMarketDataConnector

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    """Position execution status"""
    PENDING = "pending"
    EXECUTING = "executing"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PositionSide(Enum):
    """Position side"""
    LONG = "long"
    SHORT = "short"

@dataclass
class PositionOrder:
    """Position order details"""
    order_id: str
    symbol: str
    side: PositionSide
    position_size: float
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    risk_score: float
    market_regime: str
    timestamp: datetime
    status: ExecutionStatus
    execution_price: Optional[float] = None
    execution_time: Optional[datetime] = None
    pnl: Optional[float] = None

@dataclass
class ExecutionMetrics:
    """Position execution metrics"""
    total_orders: int
    successful_executions: int
    failed_executions: int
    average_execution_time: float
    average_slippage: float
    success_rate: float
    total_pnl: float
    risk_adjusted_return: float

class PositionExecutionEngine:
    """
    Position execution engine with advanced risk management
    """
    
    def __init__(self):
        """Initialize the position execution engine"""
        self.risk_management = AdvancedRiskManagement()
        self.integrated_scoring = CalibratedScoringService()
        self.market_data_connector = RealTimeMarketDataConnector()
        
        # Execution state
        self.active_orders: Dict[str, PositionOrder] = {}
        self.order_history: List[PositionOrder] = []
        self.execution_metrics = ExecutionMetrics(
            total_orders=0,
            successful_executions=0,
            failed_executions=0,
            average_execution_time=0.0,
            average_slippage=0.0,
            success_rate=0.0,
            total_pnl=0.0,
            risk_adjusted_return=0.0
        )
        
        # Risk management parameters
        self.risk_parameters = {
            'max_position_size': 2000.0,  # Maximum position size in USDT
            'max_portfolio_exposure': 0.8,  # Maximum 80% portfolio exposure
            'max_correlation_risk': 0.7,   # Maximum correlation risk
            'min_confidence_threshold': 0.6,  # Minimum confidence for execution
            'max_slippage': 0.02,         # Maximum 2% slippage
            'execution_timeout': 30.0,     # 30 seconds execution timeout
            'position_scaling': True,      # Enable position scaling
            'dynamic_stops': True,         # Enable dynamic stop losses
            'partial_take_profits': True   # Enable partial take profits
        }
        
        # Execution callbacks
        self.execution_callbacks: List[Callable] = []
        
        logger.info("Position Execution Engine initialized")
    
    async def execute_position(self, symbol: str, side: PositionSide, 
                             confidence: float, market_regime: str,
                             position_size: float, entry_price: float,
                             stop_loss: float, take_profit: float) -> Dict[str, Any]:
        """Execute a position with advanced risk management"""
        try:
            # Generate order ID
            order_id = f"order_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Validate execution parameters
            validation_result = await self._validate_execution_parameters(
                symbol, side, confidence, position_size, entry_price, stop_loss, take_profit
            )
            
            if not validation_result['valid']:
                return {
                    'order_id': order_id,
                    'status': ExecutionStatus.FAILED.value,
                    'error': validation_result['error'],
                    'timestamp': datetime.now().isoformat()
                }
            
            # Create position order
            order = PositionOrder(
                order_id=order_id,
                symbol=symbol,
                side=side,
                position_size=position_size,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                risk_score=validation_result['risk_score'],
                market_regime=market_regime,
                timestamp=datetime.now(),
                status=ExecutionStatus.PENDING
            )
            
            # Add to active orders
            self.active_orders[order_id] = order
            
            # Execute position
            execution_result = await self._execute_position_order(order)
            
            # Update order status
            order.status = execution_result['status']
            order.execution_price = execution_result.get('execution_price')
            order.execution_time = execution_result.get('execution_time')
            order.pnl = execution_result.get('pnl')
            
            # Move to history if completed
            if order.status in [ExecutionStatus.EXECUTED, ExecutionStatus.FAILED]:
                self.order_history.append(order)
                del self.active_orders[order_id]
            
            # Update execution metrics
            await self._update_execution_metrics(order)
            
            # Trigger callbacks
            await self._trigger_execution_callbacks(order)
            
            logger.info(f"Position execution completed for {symbol}: {order.status.value}")
            
            return {
                'order_id': order_id,
                'status': order.status.value,
                'execution_price': order.execution_price,
                'execution_time': order.execution_time.isoformat() if order.execution_time else None,
                'pnl': order.pnl,
                'risk_score': order.risk_score,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing position for {symbol}: {e}")
            return {
                'order_id': order_id if 'order_id' in locals() else 'unknown',
                'status': ExecutionStatus.FAILED.value,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _validate_execution_parameters(self, symbol: str, side: PositionSide,
                                           confidence: float, position_size: float,
                                           entry_price: float, stop_loss: float,
                                           take_profit: float) -> Dict[str, Any]:
        """Validate execution parameters"""
        try:
            # Check confidence threshold
            if confidence < self.risk_parameters['min_confidence_threshold']:
                return {
                    'valid': False,
                    'error': f"Confidence {confidence:.2f} below threshold {self.risk_parameters['min_confidence_threshold']}",
                    'risk_score': 1.0
                }
            
            # Check position size limits
            if position_size > self.risk_parameters['max_position_size']:
                return {
                    'valid': False,
                    'error': f"Position size {position_size} exceeds maximum {self.risk_parameters['max_position_size']}",
                    'risk_score': 1.0
                }
            
            # Check portfolio exposure
            total_exposure = sum(order.position_size for order in self.active_orders.values())
            portfolio_value = 12500.0  # Would be fetched from portfolio
            exposure_ratio = (total_exposure + position_size) / portfolio_value
            
            if exposure_ratio > self.risk_parameters['max_portfolio_exposure']:
                return {
                    'valid': False,
                    'error': f"Portfolio exposure {exposure_ratio:.2f} exceeds maximum {self.risk_parameters['max_portfolio_exposure']}",
                    'risk_score': 1.0
                }
            
            # Check risk/reward ratio
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            if risk_reward_ratio < 1.5:
                return {
                    'valid': False,
                    'error': f"Risk/reward ratio {risk_reward_ratio:.2f} below minimum 1.5",
                    'risk_score': 0.8
                }
            
            # Calculate risk score
            risk_score = await self._calculate_execution_risk_score(
                symbol, side, confidence, position_size, exposure_ratio, risk_reward_ratio
            )
            
            return {
                'valid': True,
                'error': None,
                'risk_score': risk_score
            }
            
        except Exception as e:
            logger.error(f"Error validating execution parameters: {e}")
            return {
                'valid': False,
                'error': f"Validation error: {str(e)}",
                'risk_score': 1.0
            }
    
    async def _calculate_execution_risk_score(self, symbol: str, side: PositionSide,
                                            confidence: float, position_size: float,
                                            exposure_ratio: float, risk_reward_ratio: float) -> float:
        """Calculate execution risk score"""
        try:
            # Base risk from confidence (inverse relationship)
            confidence_risk = 1.0 - confidence
            
            # Position size risk
            size_risk = min(1.0, position_size / self.risk_parameters['max_position_size'])
            
            # Exposure risk
            exposure_risk = exposure_ratio / self.risk_parameters['max_portfolio_exposure']
            
            # Risk/reward risk (lower ratio = higher risk)
            rr_risk = max(0.0, 1.0 - (risk_reward_ratio / 3.0))  # Normalize to 0-1
            
            # Market regime risk (would be calculated from real-time data)
            regime_risk = 0.5  # Default neutral risk
            
            # Weighted risk score
            risk_score = (
                confidence_risk * 0.3 +
                size_risk * 0.2 +
                exposure_risk * 0.2 +
                rr_risk * 0.2 +
                regime_risk * 0.1
            )
            
            return min(1.0, max(0.0, risk_score))
            
        except Exception as e:
            logger.error(f"Error calculating execution risk score: {e}")
            return 0.5  # Default neutral risk
    
    async def _execute_position_order(self, order: PositionOrder) -> Dict[str, Any]:
        """Execute a position order"""
        try:
            # Simulate execution delay
            await asyncio.sleep(0.1)  # 100ms execution time
            
            # Calculate execution price with slippage
            slippage = np.random.uniform(-0.01, 0.01)  # -1% to +1% slippage
            execution_price = order.entry_price * (1 + slippage)
            
            # Check if slippage is acceptable
            if abs(slippage) > self.risk_parameters['max_slippage']:
                return {
                    'status': ExecutionStatus.FAILED,
                    'error': f"Slippage {abs(slippage):.2%} exceeds maximum {self.risk_parameters['max_slippage']:.2%}"
                }
            
            # Calculate PnL (simplified)
            if order.side == PositionSide.LONG:
                pnl = (execution_price - order.entry_price) * order.position_size / order.entry_price
            else:
                pnl = (order.entry_price - execution_price) * order.position_size / order.entry_price
            
            # Add position to risk management
            await self.risk_management.add_position(
                symbol=order.symbol,
                position_size=order.position_size,
                entry_price=execution_price,
                confidence=order.confidence,
                win_probability=order.confidence * 0.7,  # Estimate
                stop_loss=order.stop_loss,
                take_profit=order.take_profit
            )
            
            return {
                'status': ExecutionStatus.EXECUTED,
                'execution_price': execution_price,
                'execution_time': datetime.now(),
                'pnl': pnl,
                'slippage': slippage
            }
            
        except Exception as e:
            logger.error(f"Error executing position order {order.order_id}: {e}")
            return {
                'status': ExecutionStatus.FAILED,
                'error': str(e)
            }
    
    async def close_position(self, order_id: str, exit_price: float) -> Dict[str, Any]:
        """Close a position"""
        try:
            if order_id not in self.active_orders:
                return {
                    'status': 'failed',
                    'error': f"Order {order_id} not found in active orders"
                }
            
            order = self.active_orders[order_id]
            
            # Calculate final PnL
            if order.execution_price is None:
                logger.error(f"Cannot calculate PnL: execution_price is None for order {order_id}")
                return {
                    'order_id': order_id,
                    'status': 'failed',
                    'error': 'Execution price is None'
                }
                
            if order.side == PositionSide.LONG:
                pnl = (exit_price - order.execution_price) * order.position_size / order.execution_price
            else:
                pnl = (order.execution_price - exit_price) * order.position_size / order.execution_price
            
            # Close position in risk management
            await self.risk_management.close_position(
                symbol=order.symbol,
                exit_price=exit_price,
                pnl=pnl
            )
            
            # Update order
            order.pnl = pnl
            order.status = ExecutionStatus.EXECUTED
            
            # Move to history
            self.order_history.append(order)
            del self.active_orders[order_id]
            
            # Update metrics
            await self._update_execution_metrics(order)
            
            logger.info(f"Closed position {order_id}: PnL = {pnl:.2f}")
            
            return {
                'order_id': order_id,
                'status': 'closed',
                'pnl': pnl,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error closing position {order_id}: {e}")
            return {
                'order_id': order_id,
                'status': 'failed',
                'error': str(e)
            }
    
    async def _update_execution_metrics(self, order: PositionOrder):
        """Update execution metrics"""
        try:
            self.execution_metrics.total_orders += 1
            
            if order.status == ExecutionStatus.EXECUTED:
                self.execution_metrics.successful_executions += 1
                if order.pnl:
                    self.execution_metrics.total_pnl += order.pnl
            elif order.status == ExecutionStatus.FAILED:
                self.execution_metrics.failed_executions += 1
            
            # Calculate success rate
            if self.execution_metrics.total_orders > 0:
                self.execution_metrics.success_rate = (
                    self.execution_metrics.successful_executions / self.execution_metrics.total_orders
                )
            
            # Calculate average execution time
            if order.execution_time is not None:
                execution_duration = (order.execution_time - order.timestamp).total_seconds()
                total_time = self.execution_metrics.average_execution_time * (self.execution_metrics.total_orders - 1)
                self.execution_metrics.average_execution_time = (total_time + execution_duration) / self.execution_metrics.total_orders
            
            # Calculate risk-adjusted return
            if self.execution_metrics.total_orders > 0:
                risk_scores = [order.risk_score for order in self.order_history[-100:]]
                if risk_scores:
                    avg_risk = float(np.mean(risk_scores))
                    self.execution_metrics.risk_adjusted_return = (
                        self.execution_metrics.total_pnl / self.execution_metrics.total_orders
                    ) / max(0.1, avg_risk)
            
        except Exception as e:
            logger.error(f"Error updating execution metrics: {e}")
    
    async def _trigger_execution_callbacks(self, order: PositionOrder):
        """Trigger execution callbacks"""
        try:
            for callback in self.execution_callbacks:
                try:
                    await callback(order)
                except Exception as e:
                    logger.error(f"Error in execution callback {callback.__name__}: {e}")
                    
        except Exception as e:
            logger.error(f"Error triggering execution callbacks: {e}")
    
    async def register_execution_callback(self, callback: Callable):
        """Register an execution callback"""
        self.execution_callbacks.append(callback)
        logger.info(f"Registered execution callback: {callback.__name__}")
    
    async def get_execution_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status for an order"""
        try:
            if order_id in self.active_orders:
                order = self.active_orders[order_id]
                return {
                    'order_id': order_id,
                    'status': order.status.value,
                    'symbol': order.symbol,
                    'side': order.side.value,
                    'position_size': order.position_size,
                    'entry_price': order.entry_price,
                    'execution_price': order.execution_price,
                    'confidence': order.confidence,
                    'risk_score': order.risk_score,
                    'timestamp': order.timestamp.isoformat()
                }
            else:
                # Check history
                for order in self.order_history:
                    if order.order_id == order_id:
                        return {
                            'order_id': order_id,
                            'status': order.status.value,
                            'symbol': order.symbol,
                            'side': order.side.value,
                            'position_size': order.position_size,
                            'entry_price': order.entry_price,
                            'execution_price': order.execution_price,
                            'pnl': order.pnl,
                            'confidence': order.confidence,
                            'risk_score': order.risk_score,
                            'timestamp': order.timestamp.isoformat()
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting execution status for {order_id}: {e}")
            return None
    
    async def get_execution_engine_report(self) -> Dict[str, Any]:
        """Get comprehensive execution engine report"""
        return {
            'execution_metrics': {
                'total_orders': self.execution_metrics.total_orders,
                'successful_executions': self.execution_metrics.successful_executions,
                'failed_executions': self.execution_metrics.failed_executions,
                'success_rate': self.execution_metrics.success_rate,
                'average_execution_time': self.execution_metrics.average_execution_time,
                'total_pnl': self.execution_metrics.total_pnl,
                'risk_adjusted_return': self.execution_metrics.risk_adjusted_return
            },
            'active_orders': {
                order_id: {
                    'symbol': order.symbol,
                    'side': order.side.value,
                    'position_size': order.position_size,
                    'confidence': order.confidence,
                    'risk_score': order.risk_score,
                    'status': order.status.value
                }
                for order_id, order in self.active_orders.items()
            },
            'risk_parameters': self.risk_parameters,
            'registered_callbacks': len(self.execution_callbacks),
            'timestamp': datetime.now().isoformat()
        }

# Global instance
position_execution_engine = PositionExecutionEngine() 