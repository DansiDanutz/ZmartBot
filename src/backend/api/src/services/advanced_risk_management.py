#!/usr/bin/env python3
"""
Advanced Risk Management System
Implements position sizing based on win rate confidence and advanced risk controls
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics

from src.config.settings import settings
from src.services.enhanced_short_position_analyzer import EnhancedShortPositionAnalyzer
from src.services.dynamic_weight_adjuster import DynamicWeightAdjuster

logger = logging.getLogger(__name__)

@dataclass
class PositionSizingConfig:
    """Position sizing configuration based on win rate confidence"""
    base_position_size: float = 500.0  # Base position size in USDT
    max_position_size: float = 2000.0  # Maximum position size
    min_position_size: float = 100.0   # Minimum position size
    confidence_multiplier: float = 1.5  # Multiplier for high confidence
    risk_adjustment_factor: float = 0.8  # Risk adjustment factor
    win_rate_thresholds: Optional[Dict[str, float]] = None
    volatility_adjustments: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        if self.win_rate_thresholds is None:
            self.win_rate_thresholds = {
                'excellent': 0.75,  # 75%+ win rate
                'good': 0.65,       # 65-75% win rate
                'average': 0.55,    # 55-65% win rate
                'poor': 0.45        # <55% win rate
            }
        if self.volatility_adjustments is None:
            self.volatility_adjustments = {
                'low': 1.2,         # 20% increase for low volatility
                'medium': 1.0,      # No adjustment for medium volatility
                'high': 0.8,        # 20% decrease for high volatility
                'extreme': 0.6      # 40% decrease for extreme volatility
            }

@dataclass
class RiskMetrics:
    """Comprehensive risk metrics"""
    portfolio_value: float
    total_exposure: float
    max_drawdown: float
    var_95: float  # Value at Risk (95%)
    var_99: float  # Value at Risk (99%)
    expected_shortfall: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    risk_adjusted_return: float
    correlation_risk: float
    concentration_risk: float
    leverage_risk: float

@dataclass
class PositionRiskProfile:
    """Individual position risk profile"""
    symbol: str
    position_size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    risk_score: float
    confidence_level: float
    win_probability: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    time_in_position: int  # seconds
    market_volatility: float
    position_volatility: float
    correlation_with_portfolio: float
    timestamp: datetime

class AdvancedRiskManagement:
    """
    Advanced risk management system with position sizing based on win rate confidence
    """
    
    def __init__(self):
        """Initialize the advanced risk management system"""
        self.short_analyzer = EnhancedShortPositionAnalyzer()
        self.dynamic_weight_adjuster = DynamicWeightAdjuster()
        
        # Position sizing configuration
        self.position_config = PositionSizingConfig(
            win_rate_thresholds={
                'excellent': 0.75,  # 75%+ win rate
                'good': 0.65,       # 65-75% win rate
                'average': 0.55,    # 55-65% win rate
                'poor': 0.45        # <55% win rate
            },
            volatility_adjustments={
                'low': 1.2,         # 20% increase for low volatility
                'medium': 1.0,      # No adjustment for medium volatility
                'high': 0.8,        # 20% decrease for high volatility
                'extreme': 0.6      # 40% decrease for extreme volatility
            }
        )
        
        # Risk management state
        self.active_positions: Dict[str, PositionRiskProfile] = {}
        self.risk_metrics = RiskMetrics(
            portfolio_value=12500.0,
            total_exposure=0.0,
            max_drawdown=0.0,
            var_95=0.0,
            var_99=0.0,
            expected_shortfall=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            win_rate=0.68,
            profit_factor=0.0,
            risk_adjusted_return=0.0,
            correlation_risk=0.0,
            concentration_risk=0.0,
            leverage_risk=0.0
        )
        
        # Performance tracking
        self.position_history: List[Dict[str, Any]] = []
        self.risk_alerts: List[Dict[str, Any]] = []
        
        logger.info("Advanced Risk Management System initialized")
    
    async def calculate_position_size(self, symbol: str, signal_confidence: float, 
                                   win_probability: float, market_volatility: float) -> Dict[str, Any]:
        """Calculate optimal position size based on win rate confidence"""
        try:
            # Base position size
            base_size = self.position_config.base_position_size
            
            # Confidence-based adjustment
            confidence_multiplier = await self._calculate_confidence_multiplier(signal_confidence, win_probability)
            
            # Volatility-based adjustment
            volatility_multiplier = await self._calculate_volatility_multiplier(market_volatility)
            
            # Risk-adjusted position size
            risk_adjusted_size = base_size * confidence_multiplier * volatility_multiplier * self.position_config.risk_adjustment_factor
            
            # Apply position size limits
            final_position_size = max(
                self.position_config.min_position_size,
                min(self.position_config.max_position_size, risk_adjusted_size)
            )
            
            # Calculate risk metrics for this position
            position_risk = await self._calculate_position_risk(symbol, final_position_size, signal_confidence)
            
            return {
                'symbol': symbol,
                'position_size': final_position_size,
                'confidence_multiplier': confidence_multiplier,
                'volatility_multiplier': volatility_multiplier,
                'risk_adjusted_size': risk_adjusted_size,
                'position_risk': position_risk,
                'recommendations': await self._generate_position_recommendations(symbol, final_position_size, signal_confidence)
            }
            
        except Exception as e:
            logger.error(f"Error calculating position size for {symbol}: {e}")
            return {
                'symbol': symbol,
                'position_size': self.position_config.base_position_size,
                'confidence_multiplier': 1.0,
                'volatility_multiplier': 1.0,
                'risk_adjusted_size': self.position_config.base_position_size,
                'position_risk': 0.5,
                'recommendations': ['Use default position size due to calculation error']
            }
    
    async def _calculate_confidence_multiplier(self, signal_confidence: float, win_probability: float) -> float:
        """Calculate confidence-based position size multiplier"""
        # Combine signal confidence and win probability
        combined_confidence = (signal_confidence + win_probability) / 2
        
        # Determine win rate category
        win_rate_thresholds = self.position_config.win_rate_thresholds
        if win_rate_thresholds is None:
            return 1.0  # Default multiplier if thresholds not set
            
        if combined_confidence >= win_rate_thresholds['excellent']:
            multiplier = self.position_config.confidence_multiplier
        elif combined_confidence >= win_rate_thresholds['good']:
            multiplier = 1.2
        elif combined_confidence >= win_rate_thresholds['average']:
            multiplier = 1.0
        else:
            multiplier = 0.8
        
        return multiplier
    
    async def _calculate_volatility_multiplier(self, market_volatility: float) -> float:
        """Calculate volatility-based position size multiplier"""
        volatility_adjustments = self.position_config.volatility_adjustments
        if volatility_adjustments is None:
            return 1.0  # Default multiplier if adjustments not set
            
        if market_volatility < 0.2:
            return volatility_adjustments['low']
        elif market_volatility < 0.4:
            return volatility_adjustments['medium']
        elif market_volatility < 0.6:
            return volatility_adjustments['high']
        else:
            return volatility_adjustments['extreme']
    
    async def _calculate_position_risk(self, symbol: str, position_size: float, confidence: float) -> float:
        """Calculate risk score for a position"""
        # Base risk score
        base_risk = 1.0 - confidence
        
        # Position size risk (larger positions = higher risk)
        size_risk = min(1.0, position_size / self.position_config.max_position_size)
        
        # Portfolio concentration risk
        concentration_risk = position_size / self.risk_metrics.portfolio_value if self.risk_metrics.portfolio_value > 0 else 0
        
        # Combined risk score
        risk_score = (base_risk * 0.4 + size_risk * 0.3 + concentration_risk * 0.3)
        
        return min(1.0, risk_score)
    
    async def _generate_position_recommendations(self, symbol: str, position_size: float, confidence: float) -> List[str]:
        """Generate recommendations for position management"""
        recommendations = []
        
        # Confidence-based recommendations
        if confidence < 0.6:
            recommendations.append("Low confidence signal - consider reducing position size")
            recommendations.append("Implement tighter stop loss")
        
        elif confidence > 0.8:
            recommendations.append("High confidence signal - optimal position sizing")
            recommendations.append("Consider scaling in for larger positions")
        
        # Position size recommendations
        if position_size > self.position_config.max_position_size * 0.8:
            recommendations.append("Large position size - monitor closely")
            recommendations.append("Consider partial profit taking")
        
        elif position_size < self.position_config.min_position_size * 1.5:
            recommendations.append("Small position size - consider increasing if confidence improves")
        
        # Risk management recommendations
        if len(self.active_positions) > 5:
            recommendations.append("High number of active positions - monitor correlation risk")
        
        return recommendations
    
    async def update_position_risk(self, symbol: str, current_price: float, unrealized_pnl: float):
        """Update risk metrics for an active position"""
        if symbol not in self.active_positions:
            return
        
        position = self.active_positions[symbol]
        
        # Update position metrics
        position.current_price = current_price
        position.unrealized_pnl = unrealized_pnl
        position.unrealized_pnl_percent = (unrealized_pnl / position.position_size) * 100
        
        # Update time in position
        position.time_in_position = int((datetime.now() - position.timestamp).total_seconds())
        
        # Recalculate risk score
        position.risk_score = await self._calculate_position_risk(symbol, position.position_size, position.confidence_level)
        
        # Update portfolio risk metrics
        await self._update_portfolio_risk_metrics()
        
        # Check for risk alerts
        await self._check_risk_alerts(symbol, position)
    
    async def _update_portfolio_risk_metrics(self):
        """Update comprehensive portfolio risk metrics"""
        if not self.active_positions:
            return
        
        # Calculate total exposure
        total_exposure = sum(pos.position_size for pos in self.active_positions.values())
        self.risk_metrics.total_exposure = total_exposure
        
        # Calculate portfolio value
        total_pnl = sum(pos.unrealized_pnl for pos in self.active_positions.values())
        self.risk_metrics.portfolio_value = 12500.0 + total_pnl  # Base + unrealized PnL
        
        # Calculate Value at Risk (simplified)
        position_values = [pos.position_size for pos in self.active_positions.values()]
        if position_values:
            self.risk_metrics.var_95 = sum(position_values) * 0.05  # 5% VaR
            self.risk_metrics.var_99 = sum(position_values) * 0.01  # 1% VaR
        
        # Calculate correlation risk
        self.risk_metrics.correlation_risk = await self._calculate_correlation_risk()
        
        # Calculate concentration risk
        self.risk_metrics.concentration_risk = await self._calculate_concentration_risk()
        
        # Calculate leverage risk
        self.risk_metrics.leverage_risk = await self._calculate_leverage_risk()
        
        # Update performance metrics
        await self._update_performance_metrics()
    
    async def _calculate_correlation_risk(self) -> float:
        """Calculate correlation risk between positions"""
        if len(self.active_positions) < 2:
            return 0.0
        
        # Simplified correlation calculation
        # In a real implementation, this would use actual price correlation data
        symbols = list(self.active_positions.keys())
        correlation_matrix = np.random.uniform(0.3, 0.9, (len(symbols), len(symbols)))
        np.fill_diagonal(correlation_matrix, 1.0)
        
        # Calculate average correlation
        total_correlation = 0.0
        count = 0
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                total_correlation += correlation_matrix[i, j]
                count += 1
        
        return total_correlation / count if count > 0 else 0.0
    
    async def _calculate_concentration_risk(self) -> float:
        """Calculate concentration risk (exposure to single positions)"""
        if not self.active_positions:
            return 0.0
        
        position_sizes = [pos.position_size for pos in self.active_positions.values()]
        total_exposure = sum(position_sizes)
        
        if total_exposure == 0:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index (HHI) for concentration
        hhi = sum((size / total_exposure) ** 2 for size in position_sizes)
        
        # Normalize to 0-1 scale
        concentration_risk = min(1.0, hhi)
        
        return concentration_risk
    
    async def _calculate_leverage_risk(self) -> float:
        """Calculate leverage risk"""
        if not self.active_positions:
            return 0.0
        
        total_exposure = sum(pos.position_size for pos in self.active_positions.values())
        portfolio_value = self.risk_metrics.portfolio_value
        
        if portfolio_value == 0:
            return 0.0
        
        # Calculate leverage ratio
        leverage_ratio = total_exposure / portfolio_value
        
        # Risk increases exponentially with leverage
        leverage_risk = min(1.0, leverage_ratio / 10.0)  # 10x leverage = 100% risk
        
        return leverage_risk
    
    async def _update_performance_metrics(self):
        """Update performance metrics"""
        if not self.active_positions:
            return
        
        # Calculate win rate from position history
        if self.position_history:
            winning_positions = sum(1 for pos in self.position_history if pos.get('pnl', 0) > 0)
            total_positions = len(self.position_history)
            self.risk_metrics.win_rate = winning_positions / total_positions if total_positions > 0 else 0
        
        # Calculate profit factor
        if self.position_history:
            total_profit = sum(pos.get('pnl', 0) for pos in self.position_history if pos.get('pnl', 0) > 0)
            total_loss = abs(sum(pos.get('pnl', 0) for pos in self.position_history if pos.get('pnl', 0) < 0))
            self.risk_metrics.profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # Calculate risk-adjusted return
        if self.risk_metrics.portfolio_value > 0:
            self.risk_metrics.risk_adjusted_return = (self.risk_metrics.win_rate * self.risk_metrics.profit_factor) / max(0.1, self.risk_metrics.leverage_risk)
    
    async def _check_risk_alerts(self, symbol: str, position: PositionRiskProfile):
        """Check for risk alerts and generate warnings"""
        alerts = []
        
        # Unrealized loss alert
        if position.unrealized_pnl_percent < -10:
            alerts.append({
                'type': 'unrealized_loss',
                'symbol': symbol,
                'severity': 'high',
                'message': f"Position {symbol} has unrealized loss of {position.unrealized_pnl_percent:.1f}%",
                'timestamp': datetime.now()
            })
        
        # Risk score alert
        if position.risk_score > 0.8:
            alerts.append({
                'type': 'high_risk',
                'symbol': symbol,
                'severity': 'medium',
                'message': f"Position {symbol} has high risk score of {position.risk_score:.2f}",
                'timestamp': datetime.now()
            })
        
        # Concentration risk alert
        if self.risk_metrics.concentration_risk > 0.7:
            alerts.append({
                'type': 'concentration_risk',
                'symbol': symbol,
                'severity': 'high',
                'message': f"High concentration risk: {self.risk_metrics.concentration_risk:.2f}",
                'timestamp': datetime.now()
            })
        
        # Leverage risk alert
        if self.risk_metrics.leverage_risk > 0.8:
            alerts.append({
                'type': 'leverage_risk',
                'symbol': symbol,
                'severity': 'high',
                'message': f"High leverage risk: {self.risk_metrics.leverage_risk:.2f}",
                'timestamp': datetime.now()
            })
        
        # Add alerts to history
        self.risk_alerts.extend(alerts)
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"Risk Alert: {alert['message']}")
    
    async def add_position(self, symbol: str, position_size: float, entry_price: float, 
                          confidence: float, win_probability: float, stop_loss: float, 
                          take_profit: float) -> PositionRiskProfile:
        """Add a new position to risk management"""
        position = PositionRiskProfile(
            symbol=symbol,
            position_size=position_size,
            entry_price=entry_price,
            current_price=entry_price,
            unrealized_pnl=0.0,
            unrealized_pnl_percent=0.0,
            risk_score=0.0,
            confidence_level=confidence,
            win_probability=win_probability,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=abs(take_profit - entry_price) / abs(stop_loss - entry_price) if stop_loss != entry_price else 0,
            time_in_position=0,
            market_volatility=0.0,
            position_volatility=0.0,
            correlation_with_portfolio=0.0,
            timestamp=datetime.now()
        )
        
        self.active_positions[symbol] = position
        
        # Update portfolio risk metrics
        await self._update_portfolio_risk_metrics()
        
        logger.info(f"Added position for {symbol}: Size={position_size}, Confidence={confidence:.2f}")
        
        return position
    
    async def close_position(self, symbol: str, exit_price: float, pnl: float):
        """Close a position and update performance metrics"""
        if symbol not in self.active_positions:
            return
        
        position = self.active_positions[symbol]
        
        # Add to position history
        self.position_history.append({
            'symbol': symbol,
            'entry_price': position.entry_price,
            'exit_price': exit_price,
            'position_size': position.position_size,
            'pnl': pnl,
            'pnl_percent': (pnl / position.position_size) * 100,
            'time_in_position': position.time_in_position,
            'confidence_level': position.confidence_level,
            'win_probability': position.win_probability,
            'risk_score': position.risk_score,
            'timestamp': datetime.now()
        })
        
        # Remove from active positions
        del self.active_positions[symbol]
        
        # Update portfolio risk metrics
        await self._update_portfolio_risk_metrics()
        
        logger.info(f"Closed position for {symbol}: PnL={pnl:.2f}, Duration={position.time_in_position}s")
    
    async def get_risk_management_report(self) -> Dict[str, Any]:
        """Get comprehensive risk management report"""
        return {
            'portfolio_metrics': {
                'portfolio_value': self.risk_metrics.portfolio_value,
                'total_exposure': self.risk_metrics.total_exposure,
                'exposure_ratio': self.risk_metrics.total_exposure / self.risk_metrics.portfolio_value if self.risk_metrics.portfolio_value > 0 else 0,
                'win_rate': self.risk_metrics.win_rate,
                'profit_factor': self.risk_metrics.profit_factor,
                'risk_adjusted_return': self.risk_metrics.risk_adjusted_return
            },
            'risk_metrics': {
                'var_95': self.risk_metrics.var_95,
                'var_99': self.risk_metrics.var_99,
                'correlation_risk': self.risk_metrics.correlation_risk,
                'concentration_risk': self.risk_metrics.concentration_risk,
                'leverage_risk': self.risk_metrics.leverage_risk,
                'max_drawdown': self.risk_metrics.max_drawdown
            },
            'active_positions': {
                symbol: {
                    'position_size': pos.position_size,
                    'unrealized_pnl': pos.unrealized_pnl,
                    'unrealized_pnl_percent': pos.unrealized_pnl_percent,
                    'risk_score': pos.risk_score,
                    'confidence_level': pos.confidence_level,
                    'time_in_position': pos.time_in_position
                }
                for symbol, pos in self.active_positions.items()
            },
            'position_history_summary': {
                'total_positions': len(self.position_history),
                'winning_positions': sum(1 for pos in self.position_history if pos.get('pnl', 0) > 0),
                'average_pnl': statistics.mean([pos.get('pnl', 0) for pos in self.position_history]) if self.position_history else 0,
                'average_hold_time': statistics.mean([pos.get('time_in_position', 0) for pos in self.position_history]) if self.position_history else 0
            },
            'risk_alerts': self.risk_alerts[-10:] if self.risk_alerts else [],  # Last 10 alerts
            'recommendations': await self._generate_risk_recommendations(),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _generate_risk_recommendations(self) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        # Portfolio-level recommendations
        if self.risk_metrics.total_exposure / self.risk_metrics.portfolio_value > 0.8:
            recommendations.append("High portfolio exposure - consider reducing position sizes")
        
        if self.risk_metrics.correlation_risk > 0.7:
            recommendations.append("High correlation risk - diversify positions")
        
        if self.risk_metrics.concentration_risk > 0.6:
            recommendations.append("High concentration risk - reduce largest positions")
        
        if self.risk_metrics.leverage_risk > 0.7:
            recommendations.append("High leverage risk - reduce total exposure")
        
        # Performance-based recommendations
        if self.risk_metrics.win_rate < 0.6:
            recommendations.append("Low win rate - review signal quality and risk management")
        
        if self.risk_metrics.profit_factor < 1.5:
            recommendations.append("Low profit factor - improve risk/reward ratios")
        
        # Position-specific recommendations
        for symbol, pos in self.active_positions.items():
            if pos.unrealized_pnl_percent < -15:
                recommendations.append(f"Consider closing {symbol} position due to large unrealized loss")
            
            if pos.risk_score > 0.8:
                recommendations.append(f"High risk position {symbol} - monitor closely")
        
        return recommendations

# Global instance
advanced_risk_management = AdvancedRiskManagement() 