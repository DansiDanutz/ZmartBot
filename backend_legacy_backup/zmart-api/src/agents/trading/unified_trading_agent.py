#!/usr/bin/env python3
"""
Unified Trading Agent - Signal Center Integrated
Executes trades based on signals from the Unified Signal Center
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json

from src.services.unified_signal_center import unified_signal_center
from src.services.trading_with_notifications import TradingNotificationService, TradeAction
from src.services.kucoin_service import KuCoinService
from src.agents.risk_guard.risk_guard_agent import RiskGuardAgent
from src.config.settings import settings

logger = logging.getLogger(__name__)

class TradingMode(Enum):
    """Trading modes"""
    PAPER = "paper"        # Paper trading
    LIVE = "live"          # Live trading
    SIMULATION = "simulation"  # Backtesting simulation

class PositionType(Enum):
    """Position types"""
    SPOT = "spot"
    FUTURES_LONG = "futures_long"
    FUTURES_SHORT = "futures_short"

@dataclass
class TradingDecision:
    """Trading decision from signal analysis"""
    symbol: str
    action: TradeAction
    position_type: PositionType
    size: float
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    score: float
    risk_reward_ratio: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'action': self.action.value,
            'position_type': self.position_type.value,
            'size': self.size,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'confidence': self.confidence,
            'score': self.score,
            'risk_reward_ratio': self.risk_reward_ratio,
            'metadata': self.metadata
        }

@dataclass
class Position:
    """Active trading position"""
    position_id: str
    symbol: str
    position_type: PositionType
    size: float
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    pnl: float
    pnl_percentage: float
    opened_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'position_id': self.position_id,
            'symbol': self.symbol,
            'position_type': self.position_type.value,
            'size': self.size,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'pnl': self.pnl,
            'pnl_percentage': self.pnl_percentage,
            'opened_at': self.opened_at.isoformat()
        }

class UnifiedTradingAgent:
    """Trading agent that uses Unified Signal Center for decisions"""
    
    def __init__(self, mode: TradingMode = TradingMode.PAPER):
        """
        Initialize the unified trading agent
        
        Args:
            mode: Trading mode (paper, live, simulation)
        """
        self.mode = mode
        self.signal_center = unified_signal_center
        self.notification_service = TradingNotificationService()
        self.risk_guard = RiskGuardAgent()
        
        # Initialize exchange service if live trading
        if mode == TradingMode.LIVE:
            self.exchange_service = KuCoinService()
        else:
            self.exchange_service = None
        
        # Position management
        self.active_positions: Dict[str, Position] = {}
        self.position_counter = 0
        
        # Trading parameters
        self.max_positions = 5
        self.position_size_percentage = 0.02  # 2% per position
        self.min_score_threshold = 65  # Minimum score to trade
        self.min_confidence_threshold = 60  # Minimum confidence
        
        # Risk parameters
        self.max_daily_loss = 0.05  # 5% max daily loss
        self.default_stop_loss_percentage = 0.02  # 2% stop loss
        self.default_take_profit_percentage = 0.04  # 4% take profit
        
        # Performance tracking
        self.daily_pnl = 0.0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_trades = 0
        
        logger.info(f"Unified Trading Agent initialized in {mode.value} mode")
    
    async def analyze_and_trade(self, symbol: str) -> Optional[TradingDecision]:
        """
        Analyze signals and make trading decision
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Trading decision if trade should be executed
        """
        try:
            # Get unified signals from Signal Center
            signal = await self.signal_center.get_all_signals(symbol)
            
            # Check if signal meets threshold
            if signal.total_score < self.min_score_threshold:
                logger.info(f"{symbol}: Score {signal.total_score:.2f} below threshold {self.min_score_threshold}")
                return None
            
            if signal.confidence < self.min_confidence_threshold:
                logger.info(f"{symbol}: Confidence {signal.confidence:.2f} below threshold {self.min_confidence_threshold}")
                return None
            
            # Check risk guard
            risk_check = await self.risk_guard.check_trade_risk({
                'symbol': symbol,
                'position_size': 1000,  # Will be calculated properly later
                'trade_type': 'market'
            })
            
            if not risk_check.get('approved', False):
                logger.warning(f"{symbol}: Risk guard rejected - {risk_check.get('reason', 'Unknown')}")
                return None
            
            # Check if we have room for more positions
            if len(self.active_positions) >= self.max_positions:
                logger.info(f"Maximum positions ({self.max_positions}) reached")
                return None
            
            # Create trading decision
            decision = await self._create_trading_decision(symbol, signal)
            
            if decision:
                # Execute trade
                await self.execute_trade(decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    async def _create_trading_decision(self, symbol: str, signal) -> Optional[TradingDecision]:
        """
        Create trading decision from signal
        
        Args:
            symbol: Trading symbol
            signal: Aggregated signal from Signal Center
            
        Returns:
            Trading decision or None
        """
        try:
            # Determine action based on direction
            if signal.direction.upper() in ["BUY", "STRONG_BUY"]:
                action = TradeAction.BUY
                position_type = PositionType.FUTURES_LONG
            elif signal.direction.upper() in ["SELL", "STRONG_SELL"]:
                action = TradeAction.SELL
                position_type = PositionType.FUTURES_SHORT
            else:
                logger.info(f"{symbol}: Neutral signal, no trade")
                return None
            
            # Get current price (mock for now, should get from exchange)
            current_price = await self._get_current_price(symbol)
            if not current_price:
                return None
            
            # Calculate position size
            position_size = await self._calculate_position_size(symbol, current_price, signal.confidence)
            
            # Calculate stop loss and take profit
            if action == TradeAction.BUY:
                stop_loss = current_price * (1 - self.default_stop_loss_percentage)
                take_profit = current_price * (1 + self.default_take_profit_percentage)
            else:
                stop_loss = current_price * (1 + self.default_stop_loss_percentage)
                take_profit = current_price * (1 - self.default_take_profit_percentage)
            
            # Calculate risk reward ratio
            risk = abs(current_price - stop_loss)
            reward = abs(take_profit - current_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            return TradingDecision(
                symbol=symbol,
                action=action,
                position_type=position_type,
                size=position_size,
                entry_price=current_price,
                stop_loss=round(stop_loss, 2),
                take_profit=round(take_profit, 2),
                confidence=signal.confidence,
                score=signal.total_score,
                risk_reward_ratio=round(risk_reward_ratio, 2),
                metadata={
                    'signal_components': signal.components,
                    'recommendation': signal.recommendation,
                    'risk_level': signal.risk_level,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating trading decision: {e}")
            return None
    
    async def execute_trade(self, decision: TradingDecision) -> Dict[str, Any]:
        """
        Execute trade based on decision
        
        Args:
            decision: Trading decision
            
        Returns:
            Trade execution result
        """
        try:
            # Prepare trade parameters
            trade_params = {
                'symbol': decision.symbol,
                'action': decision.action.value,
                'size': decision.size,
                'price': decision.entry_price,
                'stop_loss': decision.stop_loss,
                'take_profit': decision.take_profit,
                'confidence': decision.confidence,
                'score': decision.score,
                'mode': self.mode.value
            }
            
            if self.mode == TradingMode.LIVE:
                # Execute real trade
                result = await self._execute_live_trade(trade_params)
            else:
                # Execute paper trade
                result = await self._execute_paper_trade(trade_params)
            
            if result.get('success'):
                # Create position
                position = Position(
                    position_id=f"POS_{self.position_counter:04d}",
                    symbol=decision.symbol,
                    position_type=decision.position_type,
                    size=decision.size,
                    entry_price=decision.entry_price,
                    current_price=decision.entry_price,
                    stop_loss=decision.stop_loss,
                    take_profit=decision.take_profit,
                    pnl=0.0,
                    pnl_percentage=0.0,
                    opened_at=datetime.now()
                )
                
                self.active_positions[position.position_id] = position
                self.position_counter += 1
                self.total_trades += 1
                
                # Send notification
                await self.notification_service.execute_trade(trade_params)
                
                logger.info(f"Trade executed: {decision.symbol} {decision.action.value} - Position {position.position_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_live_trade(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute live trade on exchange"""
        if not self.exchange_service:
            return {'success': False, 'error': 'Exchange service not initialized'}
        
        try:
            # Place order on exchange
            order = await self.exchange_service.place_order(
                symbol=trade_params['symbol'],
                side=trade_params['action'].lower(),
                size=trade_params['size'],
                price=trade_params['price']
            )
            
            return {
                'success': True,
                'order_id': order.get('orderId'),
                'executed_price': order.get('price'),
                'executed_size': order.get('size')
            }
            
        except Exception as e:
            logger.error(f"Live trade execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_paper_trade(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute paper trade (simulation)"""
        # Simulate successful trade
        return {
            'success': True,
            'order_id': f"PAPER_{datetime.now().timestamp()}",
            'executed_price': trade_params['price'],
            'executed_size': trade_params['size'],
            'mode': 'paper'
        }
    
    async def update_positions(self) -> List[Dict[str, Any]]:
        """Update all active positions with current prices"""
        updated_positions = []
        
        for position_id, position in list(self.active_positions.items()):
            try:
                # Get current price
                current_price = await self._get_current_price(position.symbol)
                if not current_price:
                    continue
                
                position.current_price = current_price
                
                # Calculate PnL
                if position.position_type == PositionType.FUTURES_LONG:
                    position.pnl = (current_price - position.entry_price) * position.size
                    position.pnl_percentage = ((current_price - position.entry_price) / position.entry_price) * 100
                else:  # SHORT
                    position.pnl = (position.entry_price - current_price) * position.size
                    position.pnl_percentage = ((position.entry_price - current_price) / position.entry_price) * 100
                
                # Check stop loss
                if position.position_type == PositionType.FUTURES_LONG:
                    if current_price <= position.stop_loss:
                        await self._close_position(position_id, "STOP_LOSS")
                    elif current_price >= position.take_profit:
                        await self._close_position(position_id, "TAKE_PROFIT")
                else:  # SHORT
                    if current_price >= position.stop_loss:
                        await self._close_position(position_id, "STOP_LOSS")
                    elif current_price <= position.take_profit:
                        await self._close_position(position_id, "TAKE_PROFIT")
                
                updated_positions.append(position.to_dict())
                
            except Exception as e:
                logger.error(f"Error updating position {position_id}: {e}")
        
        return updated_positions
    
    async def _close_position(self, position_id: str, reason: str):
        """Close a position"""
        if position_id not in self.active_positions:
            return
        
        position = self.active_positions[position_id]
        
        # Update statistics
        if position.pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        self.daily_pnl += position.pnl
        
        # Remove position
        del self.active_positions[position_id]
        
        logger.info(f"Position {position_id} closed - Reason: {reason}, PnL: {position.pnl:.2f}")
    
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        # Mock implementation - should get from exchange
        # In production, this would call exchange API
        prices = {
            'BTC': 45000.0,
            'ETH': 2500.0,
            'SOL': 100.0,
            'BNB': 300.0,
            'XRP': 0.6
        }
        return prices.get(symbol, 100.0)
    
    async def _calculate_position_size(self, symbol: str, price: float, confidence: float) -> float:
        """Calculate position size based on risk management"""
        # Base size on account percentage
        base_size = 1000 * self.position_size_percentage  # Mock account balance
        
        # Adjust based on confidence
        confidence_multiplier = confidence / 100
        
        # Calculate contracts/units
        size = (base_size * confidence_multiplier) / price
        
        return round(size, 4)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get trading performance statistics"""
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        return {
            'mode': self.mode.value,
            'active_positions': len(self.active_positions),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': round(win_rate, 2),
            'daily_pnl': round(self.daily_pnl, 2),
            'positions': [p.to_dict() for p in self.active_positions.values()]
        }

# Create global instance
unified_trading_agent = UnifiedTradingAgent(mode=TradingMode.PAPER)