#!/usr/bin/env python3
"""
Trading Service with Integrated Telegram Notifications
Real-time alerts for all trading activities
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from src.services.telegram_notifications import get_telegram_service, AlertLevel
from src.utils.rate_limiter import rate_limit, global_rate_limiter

logger = logging.getLogger(__name__)

class TradeAction(Enum):
    """Trade action types"""
    BUY = "BUY"
    SELL = "SELL"
    LONG = "LONG"
    SHORT = "SHORT"
    CLOSE = "CLOSE"

class TradingNotificationService:
    """
    Trading service with integrated notifications and monitoring
    """
    
    def __init__(self):
        self.telegram = get_telegram_service()
        self.active_positions = {}
        self.daily_stats = {
            'trades_executed': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'start_time': datetime.now()
        }
    
    @rate_limit(max_calls=10, time_window=60, service='trading')
    async def execute_trade(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute trade with notifications
        
        Args:
            trade_params: Trade parameters including symbol, action, size, etc.
            
        Returns:
            Trade execution result
        """
        try:
            symbol = trade_params.get('symbol', 'UNKNOWN')
            action = trade_params.get('action', TradeAction.BUY)
            size = trade_params.get('size', 0)
            price = trade_params.get('price', 0)
            confidence = trade_params.get('confidence', 0)
            score = trade_params.get('score', 0)
            
            # Check rate limiting for trading
            if not await global_rate_limiter.check_limit('trading', f'trade_{symbol}'):
                await self._notify_trade_rate_limited(symbol)
                return {
                    'success': False,
                    'error': 'Trade rate limited',
                    'symbol': symbol
                }
            
            # Simulate trade execution (replace with actual trading logic)
            trade_result = await self._execute_trade_logic(trade_params)
            
            if trade_result['success']:
                # Update statistics
                self.daily_stats['trades_executed'] += 1
                
                # Store position
                self.active_positions[symbol] = {
                    'action': action,
                    'size': size,
                    'entry_price': price,
                    'timestamp': datetime.now()
                }
                
                # Send trade notification
                await self.telegram.send_trade_alert({
                    'symbol': symbol,
                    'action': action.value if isinstance(action, TradeAction) else action,
                    'size': size,
                    'price': price,
                    'confidence': confidence,
                    'score': score
                })
                
                logger.info(f"Trade executed: {symbol} {action} {size} @ {price}")
            else:
                # Send failure notification
                await self._notify_trade_failure(symbol, trade_result.get('error', 'Unknown error'))
            
            return trade_result
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            await self._notify_trade_error(trade_params.get('symbol', 'UNKNOWN'), str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    async def close_position(self, symbol: str, exit_price: float) -> Dict[str, Any]:
        """
        Close position with P&L calculation and notification
        
        Args:
            symbol: Trading symbol
            exit_price: Exit price for the position
            
        Returns:
            Position close result
        """
        try:
            if symbol not in self.active_positions:
                return {
                    'success': False,
                    'error': f'No active position for {symbol}'
                }
            
            position = self.active_positions[symbol]
            entry_price = position['entry_price']
            size = position['size']
            
            # Calculate P&L
            if position['action'] in [TradeAction.BUY, TradeAction.LONG, 'BUY', 'LONG']:
                pnl = (exit_price - entry_price) * size
                pnl_pct = ((exit_price - entry_price) / entry_price) * 100
            else:  # SHORT/SELL
                pnl = (entry_price - exit_price) * size
                pnl_pct = ((entry_price - exit_price) / entry_price) * 100
            
            # Update statistics
            self.daily_stats['total_pnl'] += pnl
            if pnl > 0:
                self.daily_stats['winning_trades'] += 1
            else:
                self.daily_stats['losing_trades'] += 1
            
            # Remove from active positions
            del self.active_positions[symbol]
            
            # Send close notification
            await self._notify_position_closed(symbol, pnl, pnl_pct, exit_price)
            
            return {
                'success': True,
                'symbol': symbol,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'exit_price': exit_price
            }
            
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_risk_limits(self, symbol: str, risk_data: Dict[str, Any]) -> bool:
        """
        Check risk limits and send alerts if needed
        
        Args:
            symbol: Trading symbol
            risk_data: Risk metrics data
            
        Returns:
            True if within limits, False if risk exceeded
        """
        try:
            drawdown = risk_data.get('drawdown', 0)
            position_size = risk_data.get('position_size', 0)
            stop_loss = risk_data.get('stop_loss', 0)
            risk_level = risk_data.get('risk_level', 'MEDIUM')
            
            # Check drawdown limit
            if abs(drawdown) > 0.05:  # 5% drawdown threshold
                await self.telegram.send_risk_alert({
                    'symbol': symbol,
                    'risk_level': 'HIGH',
                    'drawdown': drawdown,
                    'position_size': position_size,
                    'stop_loss': stop_loss,
                    'action': 'Consider reducing position size or closing position'
                })
                return False
            
            # Check for critical risk
            if risk_level == 'CRITICAL':
                await self.telegram.send_risk_alert({
                    'symbol': symbol,
                    'risk_level': 'CRITICAL',
                    'drawdown': drawdown,
                    'position_size': position_size,
                    'stop_loss': stop_loss,
                    'action': 'IMMEDIATE ACTION REQUIRED - Close position'
                })
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking risk limits for {symbol}: {e}")
            return False
    
    async def send_daily_summary(self) -> None:
        """Send daily trading summary"""
        try:
            # Calculate win rate
            total_trades = self.daily_stats['winning_trades'] + self.daily_stats['losing_trades']
            win_rate = (self.daily_stats['winning_trades'] / total_trades) if total_trades > 0 else 0
            
            # Get top performers (mock data for example)
            top_performers = []
            worst_performers = []
            
            # Prepare summary
            summary = {
                'daily_pnl': self.daily_stats['total_pnl'],
                'daily_pnl_pct': (self.daily_stats['total_pnl'] / 10000) * 100,  # Assuming $10k account
                'total_trades': self.daily_stats['trades_executed'],
                'winning_trades': self.daily_stats['winning_trades'],
                'losing_trades': self.daily_stats['losing_trades'],
                'win_rate': win_rate,
                'top_performers': top_performers,
                'worst_performers': worst_performers,
                'portfolio_value': 10000 + self.daily_stats['total_pnl'],
                'available_balance': 5000  # Mock available balance
            }
            
            await self.telegram.send_daily_summary(summary)
            
            # Reset daily stats
            self.daily_stats = {
                'trades_executed': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_pnl': 0.0,
                'start_time': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
    
    async def send_system_health_update(self) -> None:
        """Send system health status update"""
        try:
            # Get rate limit status
            cryptometer_stats = global_rate_limiter.tiers['cryptometer'].get_stats()
            kucoin_stats = global_rate_limiter.tiers['kucoin'].get_stats()
            
            # Prepare status
            status = {
                'healthy': True,
                'uptime': '24h 15m',  # Mock uptime
                'active_positions': len(self.active_positions),
                'total_pnl': self.daily_stats['total_pnl'],
                'cryptometer_status': '🟢' if cryptometer_stats['block_rate'] < 0.1 else '🟡',
                'kucoin_status': '🟢' if kucoin_stats['block_rate'] < 0.1 else '🟡',
                'database_status': '🟢',
                'ai_status': '🟢',
                'api_calls_remaining': 100 - cryptometer_stats['allowed_requests'],
                'api_calls_limit': 100
            }
            
            await self.telegram.send_system_status(status)
            
        except Exception as e:
            logger.error(f"Error sending system health update: {e}")
    
    async def _execute_trade_logic(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute actual trade logic (placeholder)
        Replace with actual exchange API calls
        """
        # Simulate trade execution
        await asyncio.sleep(0.5)  # Simulate API call delay
        
        # Mock successful trade
        return {
            'success': True,
            'order_id': f"ORD_{datetime.now().timestamp()}",
            'executed_price': trade_params.get('price', 0),
            'executed_size': trade_params.get('size', 0),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _notify_trade_failure(self, symbol: str, error: str):
        """Notify about trade execution failure"""
        message = f"""
<b>Trade Execution Failed</b>

❌ <b>Symbol:</b> {symbol}
⚠️ <b>Error:</b> {error}

Please check the logs for more details.
"""
        await self.telegram.send_message(message, AlertLevel.WARNING)
    
    async def _notify_trade_error(self, symbol: str, error: str):
        """Notify about trade error"""
        message = f"""
<b>Trade Error</b>

🚨 <b>Symbol:</b> {symbol}
❌ <b>Error:</b> {error}

Critical error occurred during trade execution.
"""
        await self.telegram.send_message(message, AlertLevel.CRITICAL)
    
    async def _notify_trade_rate_limited(self, symbol: str):
        """Notify about trade rate limiting"""
        message = f"""
<b>Trade Rate Limited</b>

⏸️ <b>Symbol:</b> {symbol}
⚠️ Trading temporarily paused due to rate limits

The system will retry after the rate limit window.
"""
        await self.telegram.send_message(message, AlertLevel.WARNING)
    
    async def _notify_position_closed(self, symbol: str, pnl: float, pnl_pct: float, exit_price: float):
        """Notify about position closure"""
        emoji = "🟢" if pnl > 0 else "🔴"
        
        message = f"""
<b>Position Closed</b>

{emoji} <b>Symbol:</b> {symbol}
💰 <b>P&L:</b> ${pnl:.2f} ({pnl_pct:.2f}%)
💲 <b>Exit Price:</b> ${exit_price:.4f}

<i>Position closed at {datetime.now().strftime('%H:%M:%S')}</i>
"""
        level = AlertLevel.SUCCESS if pnl > 0 else AlertLevel.INFO
        await self.telegram.send_message(message, level)

# Global instance
trading_notifier = TradingNotificationService()

# Helper functions for easy integration
async def execute_trade_with_notifications(
    symbol: str,
    action: str,
    size: float,
    price: float,
    confidence: float = 0.0,
    score: float = 0.0
) -> Dict[str, Any]:
    """Helper function to execute trade with notifications"""
    return await trading_notifier.execute_trade({
        'symbol': symbol,
        'action': action,
        'size': size,
        'price': price,
        'confidence': confidence,
        'score': score
    })

async def close_position_with_notifications(symbol: str, exit_price: float) -> Dict[str, Any]:
    """Helper function to close position with notifications"""
    return await trading_notifier.close_position(symbol, exit_price)

async def check_trading_risk(symbol: str, drawdown: float, position_size: float, stop_loss: float) -> bool:
    """Helper function to check trading risk"""
    return await trading_notifier.check_risk_limits(symbol, {
        'drawdown': drawdown,
        'position_size': position_size,
        'stop_loss': stop_loss,
        'risk_level': 'HIGH' if abs(drawdown) > 0.03 else 'MEDIUM'
    })