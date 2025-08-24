#!/usr/bin/env python3
"""
Unified Trading Methodology
Complete implementation of the ZmartBot trading strategy

Trading Rules:
1. Only trade signals with composite score >= 80/100
2. KingFisher (30%) + Cryptometer (50%) + RiskMetric (20%)
3. Position sizing based on liquidation clusters
4. Automated entry/exit with risk management
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

# Import all scoring components
from .integrated_scoring_system import IntegratedScoringSystem
from .kingfisher_advanced_features import advanced_kingfisher
from .kingfisher_alert_system import kingfisher_alerts, AlertPriority
from .unified_riskmetric import UnifiedRiskMetric
from .kucoin_service import KuCoinService

logger = logging.getLogger(__name__)

class TradingSignal(Enum):
    STRONG_BUY = "strong_buy"      # Score >= 85
    BUY = "buy"                    # Score >= 80
    HOLD = "hold"                  # Score 60-79
    SELL = "sell"                  # Score <= 40
    STRONG_SELL = "strong_sell"    # Score <= 20
    NO_TRADE = "no_trade"          # Score 41-59 or insufficient data

class PositionType(Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"

class UnifiedTradingMethodology:
    """
    Complete trading methodology implementation
    
    Core Strategy:
    1. Signal Generation: Composite score from 3 systems
    2. Risk Assessment: Liquidation cascade analysis
    3. Position Sizing: Dynamic based on risk
    4. Entry Execution: Optimal zones from KingFisher
    5. Exit Management: Stop-loss and take-profit levels
    """
    
    def __init__(self):
        # Initialize all systems
        self.scoring_system = IntegratedScoringSystem()
        self.riskmetric = UnifiedRiskMetric()
        self.kucoin = KuCoinService()
        
        # Trading parameters
        self.min_score_threshold = 80  # Minimum score to trade
        self.max_positions = 3         # Maximum concurrent positions
        self.risk_per_trade = 0.02     # 2% risk per trade
        
        # Position tracking
        self.active_positions = {}
        self.pending_orders = {}
        self.trading_history = []
        
        # Performance metrics
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0,
            'win_rate': 0,
            'average_win': 0,
            'average_loss': 0,
            'sharpe_ratio': 0
        }
        
        logger.info("Unified Trading Methodology initialized")
    
    async def analyze_and_trade(self, symbol: str, account_balance: float) -> Dict[str, Any]:
        """
        Complete trading workflow from analysis to execution
        
        Steps:
        1. Get composite score
        2. Check entry conditions
        3. Calculate position size
        4. Execute trade if conditions met
        """
        try:
            logger.info(f"Analyzing {symbol} for trading opportunity...")
            
            # Step 1: Get comprehensive score
            score_data = await self.scoring_system.get_comprehensive_score(symbol)
            final_score = score_data.get('final_score', 0)
            
            # Step 2: Generate trading signal
            signal = self._generate_trading_signal(final_score, score_data)
            
            # Step 3: Check if we should trade
            if signal in [TradingSignal.NO_TRADE, TradingSignal.HOLD]:
                return {
                    'action': 'NO_TRADE',
                    'reason': f'Score {final_score:.1f} below threshold or neutral signal',
                    'signal': signal.value,
                    'score': final_score
                }
            
            # Step 4: Get market data
            market_data = await self._get_market_data(symbol)
            current_price = market_data['price']
            
            # Step 5: Risk assessment
            risk_assessment = await self._assess_trading_risk(
                symbol, score_data, market_data
            )
            
            if risk_assessment['risk_level'] == 'EXTREME':
                return {
                    'action': 'NO_TRADE',
                    'reason': 'Risk level too high',
                    'risk_assessment': risk_assessment
                }
            
            # Step 6: Calculate position details
            position_details = await self._calculate_position_details(
                symbol, signal, current_price, account_balance, risk_assessment
            )
            
            # Step 7: Find optimal entry
            entry_zones = await advanced_kingfisher.find_optimal_entry_zones(
                symbol, score_data.get('component_data', {}).get('kingfisher', {})
            )
            
            optimal_entry = self._select_optimal_entry(
                entry_zones, current_price, signal
            )
            
            # Step 8: Execute trade (if conditions met)
            if self._should_execute_trade(signal, final_score, risk_assessment):
                trade_result = await self._execute_trade(
                    symbol, signal, position_details, optimal_entry
                )
                
                # Step 9: Set up monitoring
                if trade_result['success']:
                    await self._setup_position_monitoring(
                        symbol, trade_result['position_id'], position_details
                    )
                
                return {
                    'action': 'TRADE_EXECUTED',
                    'signal': signal.value,
                    'score': final_score,
                    'position': position_details,
                    'trade_result': trade_result,
                    'entry': optimal_entry,
                    'risk_assessment': risk_assessment
                }
            else:
                return {
                    'action': 'TRADE_SKIPPED',
                    'reason': 'Conditions not optimal',
                    'signal': signal.value,
                    'score': final_score,
                    'risk_assessment': risk_assessment
                }
            
        except Exception as e:
            logger.error(f"Error in trading methodology: {e}")
            return {
                'action': 'ERROR',
                'error': str(e)
            }
    
    def _generate_trading_signal(self, score: float, score_data: Dict) -> TradingSignal:
        """Generate trading signal based on composite score"""
        
        # Get component scores
        components = score_data.get('component_scores', {})
        kingfisher_score = components.get('kingfisher', 0)
        cryptometer_score = components.get('cryptometer', 0)
        riskmetric_score = components.get('riskmetric', 0)
        
        # Strong signals require all components to agree
        if score >= 85 and min(kingfisher_score, cryptometer_score, riskmetric_score) > 70:
            return TradingSignal.STRONG_BUY
        elif score >= 80:
            return TradingSignal.BUY
        elif score <= 20 and max(kingfisher_score, cryptometer_score, riskmetric_score) < 30:
            return TradingSignal.STRONG_SELL
        elif score <= 40:
            return TradingSignal.SELL
        elif 60 <= score < 80:
            return TradingSignal.HOLD
        else:
            return TradingSignal.NO_TRADE
    
    async def _get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data"""
        try:
            # Get from KuCoin
            ticker = await self.kucoin.get_ticker(f"{symbol}-USDT")
            
            return {
                'symbol': symbol,
                'price': float(ticker.get('price', 0)),
                'volume_24h': float(ticker.get('volume', 0)),
                'high_24h': float(ticker.get('high', 0)),
                'low_24h': float(ticker.get('low', 0)),
                'change_24h': float(ticker.get('changeRate', 0)) * 100
            }
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            # Return mock data for testing
            return {
                'symbol': symbol,
                'price': 50000 if symbol == 'BTC' else 100,
                'volume_24h': 1000000,
                'high_24h': 51000,
                'low_24h': 49000,
                'change_24h': 2.5
            }
    
    async def _assess_trading_risk(self, symbol: str, 
                                  score_data: Dict,
                                  market_data: Dict) -> Dict[str, Any]:
        """Comprehensive risk assessment before trading"""
        
        # Get KingFisher liquidation data
        kingfisher_data = score_data.get('component_data', {}).get('kingfisher', {})
        
        # Analyze cascade risk
        cascade_risk = await advanced_kingfisher.analyze_liquidation_cascade_risk(
            symbol, 
            market_data['price'],
            kingfisher_data
        )
        
        # Get RiskMetric assessment
        riskmetric_data = await self.riskmetric.assess_risk(symbol)
        # Handle RiskAssessment dataclass or None
        if riskmetric_data:
            risk_level = getattr(riskmetric_data, 'risk_value', 0.5) * 100  # Convert to percentage
        else:
            risk_level = 50  # Default if assessment fails
        
        # Calculate overall risk score
        risk_factors = {
            'cascade_risk': cascade_risk['risk_score'],
            'riskmetric_level': risk_level,
            'volatility': self._calculate_volatility(market_data),
            'position_concentration': len(self.active_positions) / self.max_positions * 100
        }
        
        overall_risk = sum(risk_factors.values()) / len(risk_factors)
        
        # Determine risk level
        if overall_risk > 80:
            risk_level = 'EXTREME'
        elif overall_risk > 60:
            risk_level = 'HIGH'
        elif overall_risk > 40:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risk_level': risk_level,
            'risk_score': overall_risk,
            'risk_factors': risk_factors,
            'cascade_analysis': cascade_risk,
            'safe_to_trade': risk_level != 'EXTREME'
        }
    
    def _calculate_volatility(self, market_data: Dict) -> float:
        """Calculate volatility score from market data"""
        high = market_data.get('high_24h', 0)
        low = market_data.get('low_24h', 0)
        price = market_data.get('price', 1)
        
        if price > 0:
            volatility = ((high - low) / price) * 100
            return min(volatility * 10, 100)  # Scale to 0-100
        return 50
    
    async def _calculate_position_details(self, symbol: str,
                                         signal: TradingSignal,
                                         current_price: float,
                                         account_balance: float,
                                         risk_assessment: Dict) -> Dict[str, Any]:
        """Calculate position size and risk parameters"""
        
        # Determine position type
        if signal in [TradingSignal.STRONG_BUY, TradingSignal.BUY]:
            position_type = PositionType.LONG
        elif signal in [TradingSignal.STRONG_SELL, TradingSignal.SELL]:
            position_type = PositionType.SHORT
        else:
            position_type = PositionType.NEUTRAL
        
        # Adjust risk based on signal strength and risk assessment
        base_risk = self.risk_per_trade
        if signal == TradingSignal.STRONG_BUY:
            risk_multiplier = 1.5
        elif risk_assessment['risk_level'] == 'HIGH':
            risk_multiplier = 0.5
        else:
            risk_multiplier = 1.0
        
        adjusted_risk = base_risk * risk_multiplier
        risk_amount = account_balance * adjusted_risk
        
        # Get stop-loss from cascade analysis
        cascade_data = risk_assessment.get('cascade_analysis', {})
        danger_zones = cascade_data.get('danger_zones', [])
        
        if danger_zones and position_type == PositionType.LONG:
            # Use nearest danger zone below price as stop
            stop_price = max([z['price'] for z in danger_zones 
                            if z['price'] < current_price], default=current_price * 0.97)
        elif danger_zones and position_type == PositionType.SHORT:
            # Use nearest danger zone above price as stop
            stop_price = min([z['price'] for z in danger_zones 
                            if z['price'] > current_price], default=current_price * 1.03)
        else:
            # Default 3% stop
            stop_price = current_price * (0.97 if position_type == PositionType.LONG else 1.03)
        
        # Calculate position size based on stop distance
        stop_distance = abs(current_price - stop_price) / current_price
        position_size = risk_amount / stop_distance
        
        # Apply maximum position limits
        max_position = account_balance * 0.1  # Max 10% per position
        position_size = min(position_size, max_position)
        
        # Calculate take-profit levels (3:1 risk-reward)
        take_profit_1 = current_price + (current_price - stop_price) * 1.5
        take_profit_2 = current_price + (current_price - stop_price) * 3
        
        return {
            'position_type': position_type.value,
            'position_size_usd': position_size,
            'position_size_coins': position_size / current_price,
            'entry_price': current_price,
            'stop_loss': stop_price,
            'stop_distance_pct': stop_distance * 100,
            'take_profit_1': take_profit_1,
            'take_profit_2': take_profit_2,
            'risk_amount': risk_amount,
            'risk_reward_ratio': 3,
            'leverage': 1  # Can be adjusted based on strategy
        }
    
    def _select_optimal_entry(self, entry_zones: Dict,
                            current_price: float,
                            signal: TradingSignal) -> Dict[str, Any]:
        """Select the best entry point from available zones"""
        
        zones = entry_zones.get('entry_zones', [])
        
        if not zones:
            return {
                'type': 'market',
                'price': current_price,
                'confidence': 50
            }
        
        # Filter zones based on signal direction
        if signal in [TradingSignal.STRONG_BUY, TradingSignal.BUY]:
            valid_zones = [z for z in zones if z['type'] == 'long']
        elif signal in [TradingSignal.STRONG_SELL, TradingSignal.SELL]:
            valid_zones = [z for z in zones if z['type'] == 'short']
        else:
            valid_zones = zones
        
        if valid_zones:
            # Select highest strength zone
            best_zone = max(valid_zones, key=lambda x: x['strength'])
            
            return {
                'type': 'limit',
                'price': best_zone['price'],
                'range': best_zone['range'],
                'confidence': best_zone['strength'],
                'protection': best_zone.get('protection', '')
            }
        
        return {
            'type': 'market',
            'price': current_price,
            'confidence': 60
        }
    
    def _should_execute_trade(self, signal: TradingSignal,
                            score: float,
                            risk_assessment: Dict) -> bool:
        """Final check before executing trade"""
        
        # Check basic conditions
        if score < self.min_score_threshold:
            return False
        
        if not risk_assessment['safe_to_trade']:
            return False
        
        if len(self.active_positions) >= self.max_positions:
            logger.warning("Maximum positions reached")
            return False
        
        if signal in [TradingSignal.NO_TRADE, TradingSignal.HOLD]:
            return False
        
        return True
    
    async def _execute_trade(self, symbol: str,
                           signal: TradingSignal,
                           position_details: Dict,
                           entry: Dict) -> Dict[str, Any]:
        """Execute the actual trade on exchange"""
        try:
            # Prepare order parameters
            side = 'buy' if position_details['position_type'] == 'long' else 'sell'
            size = position_details['position_size_coins']
            
            if entry['type'] == 'limit':
                # Place limit order
                order = await self.kucoin.place_order(
                    symbol=f"{symbol}-USDT",
                    side=side,
                    order_type='limit',
                    size=size,
                    price=str(entry['price'])
                )
            else:
                # Place market order
                order = await self.kucoin.place_order(
                    symbol=f"{symbol}-USDT",
                    side=side,
                    order_type='market',
                    size=size
                )
            
            # Store position info
            position_id = order.get('orderId', f"sim_{datetime.now().timestamp()}")
            
            self.active_positions[position_id] = {
                'symbol': symbol,
                'signal': signal.value,
                'entry_time': datetime.now(),
                'position_details': position_details,
                'order': order,
                'status': 'active'
            }
            
            # Update metrics
            self.metrics['total_trades'] += 1
            
            # Send alert
            await kingfisher_alerts._send_telegram_alert({
                'priority': 'high',
                'message': f"📈 Trade Executed: {signal.value.upper()} {symbol}\n"
                          f"Entry: ${entry['price']:,.2f}\n"
                          f"Size: {size:.4f}\n"
                          f"Stop: ${position_details['stop_loss']:,.2f}"
            })
            
            logger.info(f"Trade executed successfully: {position_id}")
            
            return {
                'success': True,
                'position_id': position_id,
                'order': order,
                'executed_price': entry['price']
            }
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _setup_position_monitoring(self, symbol: str,
                                        position_id: str,
                                        position_details: Dict):
        """Set up monitoring for active position"""
        try:
            # Place stop-loss order
            stop_side = 'sell' if position_details['position_type'] == 'long' else 'buy'
            
            # Use futures order for stop-loss
            # Note: KuCoin futures stop orders are placed as regular orders with stop conditions
            stop_order = await self.kucoin.place_futures_order(
                symbol=f"{symbol}-USDT",
                side=stop_side,
                size=position_details['position_size_coins'],
                leverage=position_details.get('leverage', 1),
                order_type='market'  # Stop orders execute as market when triggered
            )
            
            # Store stop order reference
            if position_id in self.active_positions:
                self.active_positions[position_id]['stop_order'] = stop_order
            
            # Set up periodic monitoring
            asyncio.create_task(self._monitor_position(position_id))
            
            logger.info(f"Position monitoring setup for {position_id}")
            
        except Exception as e:
            logger.error(f"Error setting up position monitoring: {e}")
    
    async def _monitor_position(self, position_id: str):
        """Monitor active position and manage exit"""
        while position_id in self.active_positions:
            try:
                position = self.active_positions[position_id]
                symbol = position['symbol']
                
                # Get current price
                market_data = await self._get_market_data(symbol)
                current_price = market_data['price']
                
                # Check exit conditions
                should_exit, exit_reason = self._check_exit_conditions(
                    position, current_price
                )
                
                if should_exit:
                    await self._close_position(position_id, current_price, exit_reason)
                    break
                
                # Sleep before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring position {position_id}: {e}")
                await asyncio.sleep(60)
    
    def _check_exit_conditions(self, position: Dict, 
                              current_price: float) -> Tuple[bool, str]:
        """Check if position should be closed"""
        
        details = position['position_details']
        entry_price = details['entry_price']
        
        # Check stop-loss
        if position['position_details']['position_type'] == 'long':
            if current_price <= details['stop_loss']:
                return True, 'stop_loss_hit'
            if current_price >= details['take_profit_2']:
                return True, 'take_profit_hit'
        else:  # Short position
            if current_price >= details['stop_loss']:
                return True, 'stop_loss_hit'
            if current_price <= details['take_profit_2']:
                return True, 'take_profit_hit'
        
        # Check time-based exit (optional)
        time_in_position = datetime.now() - position['entry_time']
        if time_in_position > timedelta(hours=24):
            return True, 'time_exit'
        
        return False, ''
    
    async def _close_position(self, position_id: str, 
                            exit_price: float,
                            reason: str):
        """Close an active position"""
        try:
            position = self.active_positions[position_id]
            details = position['position_details']
            
            # Calculate P&L
            if details['position_type'] == 'long':
                pnl = (exit_price - details['entry_price']) * details['position_size_coins']
            else:
                pnl = (details['entry_price'] - exit_price) * details['position_size_coins']
            
            pnl_pct = (pnl / details['position_size_usd']) * 100
            
            # Update metrics
            self.metrics['total_pnl'] += pnl
            if pnl > 0:
                self.metrics['winning_trades'] += 1
            else:
                self.metrics['losing_trades'] += 1
            
            # Calculate win rate
            total = self.metrics['winning_trades'] + self.metrics['losing_trades']
            if total > 0:
                self.metrics['win_rate'] = int((self.metrics['winning_trades'] / total) * 100)
            
            # Store in history
            self.trading_history.append({
                'position_id': position_id,
                'symbol': position['symbol'],
                'entry_price': details['entry_price'],
                'exit_price': exit_price,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'reason': reason,
                'duration': str(datetime.now() - position['entry_time'])
            })
            
            # Remove from active positions
            del self.active_positions[position_id]
            
            # Send notification
            emoji = '✅' if pnl > 0 else '❌'
            await kingfisher_alerts._send_telegram_alert({
                'priority': 'high',
                'message': f"{emoji} Position Closed: {position['symbol']}\n"
                          f"P&L: ${pnl:,.2f} ({pnl_pct:.2f}%)\n"
                          f"Reason: {reason}"
            })
            
            logger.info(f"Position {position_id} closed. P&L: ${pnl:,.2f}")
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
    
    def get_trading_metrics(self) -> Dict[str, Any]:
        """Get current trading performance metrics"""
        return {
            'metrics': self.metrics,
            'active_positions': len(self.active_positions),
            'position_details': list(self.active_positions.values()),
            'recent_trades': self.trading_history[-10:] if self.trading_history else [],
            'timestamp': datetime.now().isoformat()
        }
    
    async def run_automated_trading(self, symbols: List[str], 
                                   account_balance: float,
                                   interval_minutes: int = 5):
        """Run automated trading loop"""
        logger.info(f"Starting automated trading for {symbols}")
        
        while True:
            try:
                for symbol in symbols:
                    # Check if we can take new positions
                    if len(self.active_positions) < self.max_positions:
                        result = await self.analyze_and_trade(symbol, account_balance)
                        
                        if result['action'] == 'TRADE_EXECUTED':
                            logger.info(f"✅ Trade executed for {symbol}")
                        elif result['action'] == 'NO_TRADE':
                            logger.debug(f"No trade for {symbol}: {result.get('reason')}")
                
                # Wait before next iteration
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in automated trading loop: {e}")
                await asyncio.sleep(60)

# Create global instance
trading_methodology = UnifiedTradingMethodology()