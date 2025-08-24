#!/usr/bin/env python3
"""
Enhanced Short Position Analyzer
Specialized analysis for improving short position win rates from 59% to 65%
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics

from src.config.settings import settings
from src.services.cryptometer_data_types import CryptometerEndpointAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class ShortPositionAnalysis:
    """Enhanced short position analysis result"""
    symbol: str
    short_confidence: float
    short_win_probability: float
    optimal_entry_price: float
    optimal_stop_loss: float
    optimal_take_profit: float
    risk_reward_ratio: float
    market_conditions: Dict[str, Any]
    short_specific_indicators: Dict[str, float]
    confidence_factors: List[str]
    risk_factors: List[str]
    timestamp: datetime

@dataclass
class ShortPositionMetrics:
    """Short position performance metrics"""
    total_short_signals: int
    successful_shorts: int
    short_win_rate: float
    average_short_profit: float
    average_short_loss: float
    short_profit_factor: float
    short_max_drawdown: float
    short_sharpe_ratio: float
    short_best_timeframes: List[str]
    short_risk_adjusted_return: float

class EnhancedShortPositionAnalyzer:
    """
    Specialized analyzer for improving short position performance
    Target: Increase short position win rate from 59% to 65%
    """
    
    def __init__(self):
        """Initialize the enhanced short position analyzer"""
        self.cryptometer_analyzer = CryptometerEndpointAnalyzer()
        
        # Short position specific configurations
        self.short_specific_endpoints = {
            'liquidation_data_v2': {'weight': 15.0, 'short_bias': 1.2},
            'ls_ratio': {'weight': 12.0, 'short_bias': 1.1},
            'rapid_movements': {'weight': 10.0, 'short_bias': 1.3},
            '24h_trade_volume_v2': {'weight': 8.0, 'short_bias': 1.0},
            'xtrades': {'weight': 7.0, 'short_bias': 1.1},
            'ai_screener': {'weight': 6.0, 'short_bias': 1.0}
        }
        
        # Short position optimization parameters
        self.short_optimization_params = {
            'min_confidence_threshold': 0.75,  # Higher threshold for shorts
            'risk_reward_minimum': 1.5,  # Minimum 1:1.5 risk/reward
            'max_position_size_multiplier': 0.8,  # Smaller positions for shorts
            'stop_loss_tightness': 1.2,  # Tighter stops for shorts
            'take_profit_aggressiveness': 1.3  # More aggressive targets
        }
        
        # Historical short performance tracking
        self.short_performance_history = []
        self.short_metrics = ShortPositionMetrics(
            total_short_signals=0,
            successful_shorts=0,
            short_win_rate=0.59,  # Current baseline
            average_short_profit=0.0,
            average_short_loss=0.0,
            short_profit_factor=0.0,
            short_max_drawdown=0.0,
            short_sharpe_ratio=0.0,
            short_best_timeframes=[],
            short_risk_adjusted_return=0.0
        )
        
        logger.info("Enhanced Short Position Analyzer initialized")
    
    async def analyze_short_position(self, symbol: str) -> ShortPositionAnalysis:
        """Analyze short position opportunity with enhanced metrics"""
        try:
            # Get comprehensive Cryptometer analysis
            cryptometer_analysis = await self.cryptometer_analyzer.analyze_symbol(symbol)
            
            # Apply short-specific analysis
            short_analysis = await self._apply_short_specific_analysis(symbol, cryptometer_analysis)
            
            # Calculate optimal entry/exit points
            entry_exit_points = await self._calculate_short_entry_exit_points(symbol, short_analysis)
            
            # Assess market conditions for shorting
            market_conditions = await self._assess_short_market_conditions(symbol, cryptometer_analysis)
            
            # Generate short-specific indicators
            short_indicators = await self._generate_short_specific_indicators(symbol, cryptometer_analysis)
            
            # Calculate confidence and risk factors
            confidence_factors, risk_factors = await self._calculate_short_confidence_factors(
                symbol, short_analysis, market_conditions
            )
            
            # Calculate final short confidence
            short_confidence = await self._calculate_short_confidence(
                short_analysis, market_conditions, short_indicators
            )
            
            # Calculate win probability
            short_win_probability = await self._calculate_short_win_probability(
                short_confidence, market_conditions, short_indicators
            )
            
            return ShortPositionAnalysis(
                symbol=symbol,
                short_confidence=short_confidence,
                short_win_probability=short_win_probability,
                optimal_entry_price=entry_exit_points['entry_price'],
                optimal_stop_loss=entry_exit_points['stop_loss'],
                optimal_take_profit=entry_exit_points['take_profit'],
                risk_reward_ratio=entry_exit_points['risk_reward_ratio'],
                market_conditions=market_conditions,
                short_specific_indicators=short_indicators,
                confidence_factors=confidence_factors,
                risk_factors=risk_factors,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing short position for {symbol}: {e}")
            raise
    
    async def _apply_short_specific_analysis(self, symbol: str, cryptometer_analysis) -> Dict[str, Any]:
        """Apply short-specific analysis to Cryptometer data"""
        short_analysis = {
            'liquidation_pressure': 0.0,
            'short_sentiment': 0.0,
            'momentum_reversal': 0.0,
            'volume_confirmation': 0.0,
            'whale_activity': 0.0,
            'ai_short_signal': 0.0
        }
        
        # Analyze each endpoint with short bias
        for endpoint_score in cryptometer_analysis.endpoint_scores:
            if endpoint_score.endpoint in self.short_specific_endpoints:
                config = self.short_specific_endpoints[endpoint_score.endpoint]
                short_bias = config['short_bias']
                
                # Apply short-specific scoring
                if endpoint_score.endpoint == 'liquidation_data_v2':
                    short_analysis['liquidation_pressure'] = endpoint_score.score * short_bias
                elif endpoint_score.endpoint == 'ls_ratio':
                    short_analysis['short_sentiment'] = endpoint_score.score * short_bias
                elif endpoint_score.endpoint == 'rapid_movements':
                    short_analysis['momentum_reversal'] = endpoint_score.score * short_bias
                elif endpoint_score.endpoint == '24h_trade_volume_v2':
                    short_analysis['volume_confirmation'] = endpoint_score.score * short_bias
                elif endpoint_score.endpoint == 'xtrades':
                    short_analysis['whale_activity'] = endpoint_score.score * short_bias
                elif endpoint_score.endpoint == 'ai_screener':
                    short_analysis['ai_short_signal'] = endpoint_score.score * short_bias
        
        return short_analysis
    
    async def _calculate_short_entry_exit_points(self, symbol: str, short_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate optimal entry and exit points for short positions"""
        # Get current market price (mock for now)
        current_price = 315.67  # Would be fetched from market data
        
        # Calculate optimal entry price based on short analysis
        entry_price = current_price * (1 + 0.02)  # Enter slightly higher
        
        # Calculate tight stop loss
        stop_loss = entry_price * (1 + 0.015)  # 1.5% above entry
        
        # Calculate aggressive take profit
        take_profit = entry_price * (1 - 0.025)  # 2.5% below entry
        
        # Calculate risk/reward ratio
        risk = stop_loss - entry_price
        reward = entry_price - take_profit
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        return {
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward_ratio': risk_reward_ratio
        }
    
    async def _assess_short_market_conditions(self, symbol: str, cryptometer_analysis) -> Dict[str, Any]:
        """Assess market conditions specifically for short positions"""
        market_conditions = {
            'volatility_regime': 'moderate',
            'trend_strength': 0.0,
            'support_resistance': {},
            'market_sentiment': 'neutral',
            'short_favorable_conditions': []
        }
        
        # Analyze volatility for short opportunities
        volatility_score = 0.0
        for endpoint_score in cryptometer_analysis.endpoint_scores:
            if endpoint_score.endpoint == 'rapid_movements':
                volatility_score = endpoint_score.score
                break
        
        if volatility_score > 0.7:
            market_conditions['volatility_regime'] = 'high'
            market_conditions['short_favorable_conditions'].append('high_volatility')
        
        # Analyze trend strength
        trend_score = 0.0
        for endpoint_score in cryptometer_analysis.endpoint_scores:
            if endpoint_score.endpoint == 'trend_indicator_v3':
                trend_score = endpoint_score.score
                break
        
        market_conditions['trend_strength'] = trend_score
        
        # Determine market sentiment
        sentiment_score = cryptometer_analysis.calibrated_score
        if sentiment_score < 0.4:
            market_conditions['market_sentiment'] = 'bearish'
            market_conditions['short_favorable_conditions'].append('bearish_sentiment')
        elif sentiment_score > 0.6:
            market_conditions['market_sentiment'] = 'bullish'
        else:
            market_conditions['market_sentiment'] = 'neutral'
        
        return market_conditions
    
    async def _generate_short_specific_indicators(self, symbol: str, cryptometer_analysis) -> Dict[str, float]:
        """Generate short-specific technical indicators"""
        indicators = {
            'liquidation_cluster_density': 0.0,
            'short_squeeze_probability': 0.0,
            'bearish_momentum_strength': 0.0,
            'support_breakdown_probability': 0.0,
            'volume_divergence': 0.0,
            'whale_short_activity': 0.0
        }
        
        # Calculate liquidation cluster density
        for endpoint_score in cryptometer_analysis.endpoint_scores:
            if endpoint_score.endpoint == 'liquidation_data_v2':
                indicators['liquidation_cluster_density'] = endpoint_score.score
                break
        
        # Calculate short squeeze probability (inverse of liquidation pressure)
        indicators['short_squeeze_probability'] = 1.0 - indicators['liquidation_cluster_density']
        
        # Calculate bearish momentum strength
        for endpoint_score in cryptometer_analysis.endpoint_scores:
            if endpoint_score.endpoint == 'rapid_movements':
                indicators['bearish_momentum_strength'] = endpoint_score.score
                break
        
        # Calculate support breakdown probability
        for endpoint_score in cryptometer_analysis.endpoint_scores:
            if endpoint_score.endpoint == 'ai_screener':
                indicators['support_breakdown_probability'] = endpoint_score.score
                break
        
        # Calculate volume divergence
        for endpoint_score in cryptometer_analysis.endpoint_scores:
            if endpoint_score.endpoint == '24h_trade_volume_v2':
                indicators['volume_divergence'] = endpoint_score.score
                break
        
        # Calculate whale short activity
        for endpoint_score in cryptometer_analysis.endpoint_scores:
            if endpoint_score.endpoint == 'xtrades':
                indicators['whale_short_activity'] = endpoint_score.score
                break
        
        return indicators
    
    async def _calculate_short_confidence_factors(self, symbol: str, short_analysis: Dict[str, Any], 
                                                market_conditions: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Calculate confidence and risk factors for short positions"""
        confidence_factors = []
        risk_factors = []
        
        # Analyze liquidation pressure
        if short_analysis['liquidation_pressure'] > 0.7:
            confidence_factors.append("High liquidation pressure supports short")
        elif short_analysis['liquidation_pressure'] < 0.3:
            risk_factors.append("Low liquidation pressure - potential short squeeze")
        
        # Analyze short sentiment
        if short_analysis['short_sentiment'] > 0.6:
            confidence_factors.append("Strong short sentiment confirmed")
        elif short_analysis['short_sentiment'] < 0.4:
            risk_factors.append("Weak short sentiment - potential reversal")
        
        # Analyze momentum reversal
        if short_analysis['momentum_reversal'] > 0.7:
            confidence_factors.append("Clear momentum reversal pattern")
        elif short_analysis['momentum_reversal'] < 0.3:
            risk_factors.append("No clear reversal pattern detected")
        
        # Analyze volume confirmation
        if short_analysis['volume_confirmation'] > 0.6:
            confidence_factors.append("Volume confirms short direction")
        else:
            risk_factors.append("Volume doesn't confirm short direction")
        
        # Analyze market conditions
        if market_conditions['volatility_regime'] == 'high':
            confidence_factors.append("High volatility favorable for shorts")
        
        if market_conditions['market_sentiment'] == 'bearish':
            confidence_factors.append("Bearish market sentiment supports short")
        elif market_conditions['market_sentiment'] == 'bullish':
            risk_factors.append("Bullish market sentiment - short risk")
        
        return confidence_factors, risk_factors
    
    async def _calculate_short_confidence(self, short_analysis: Dict[str, Any], 
                                        market_conditions: Dict[str, Any], 
                                        short_indicators: Dict[str, float]) -> float:
        """Calculate overall short position confidence"""
        # Weighted average of short-specific factors
        weights = {
            'liquidation_pressure': 0.25,
            'short_sentiment': 0.20,
            'momentum_reversal': 0.20,
            'volume_confirmation': 0.15,
            'whale_activity': 0.10,
            'ai_short_signal': 0.10
        }
        
        confidence_score = 0.0
        total_weight = 0.0
        
        for factor, weight in weights.items():
            if factor in short_analysis:
                confidence_score += short_analysis[factor] * weight
                total_weight += weight
        
        # Apply market condition adjustments
        if market_conditions['volatility_regime'] == 'high':
            confidence_score *= 1.1  # 10% boost for high volatility
        
        if market_conditions['market_sentiment'] == 'bearish':
            confidence_score *= 1.15  # 15% boost for bearish sentiment
        elif market_conditions['market_sentiment'] == 'bullish':
            confidence_score *= 0.85  # 15% reduction for bullish sentiment
        
        # Normalize to 0-1 range
        final_confidence = min(1.0, max(0.0, confidence_score / total_weight))
        
        return final_confidence
    
    async def _calculate_short_win_probability(self, short_confidence: float, 
                                             market_conditions: Dict[str, Any], 
                                             short_indicators: Dict[str, float]) -> float:
        """Calculate probability of short position success"""
        # Base win probability from confidence
        base_probability = short_confidence * 0.65  # Target 65% win rate
        
        # Adjust based on market conditions
        if market_conditions['volatility_regime'] == 'high':
            base_probability *= 1.05  # 5% boost for high volatility
        
        if market_conditions['market_sentiment'] == 'bearish':
            base_probability *= 1.08  # 8% boost for bearish sentiment
        
        # Adjust based on short indicators
        if short_indicators['liquidation_cluster_density'] > 0.7:
            base_probability *= 1.03  # 3% boost for high liquidation density
        
        if short_indicators['short_squeeze_probability'] < 0.3:
            base_probability *= 1.02  # 2% boost for low squeeze probability
        
        # Cap at 85% maximum probability
        final_probability = min(0.85, base_probability)
        
        return final_probability
    
    async def update_short_performance(self, symbol: str, success: bool, profit: float):
        """Update short position performance metrics"""
        self.short_metrics.total_short_signals += 1
        
        if success:
            self.short_metrics.successful_shorts += 1
        
        # Update win rate
        self.short_metrics.short_win_rate = (
            self.short_metrics.successful_shorts / self.short_metrics.total_short_signals
        )
        
        # Update profit metrics
        if success:
            self.short_metrics.average_short_profit = (
                (self.short_metrics.average_short_profit * (self.short_metrics.successful_shorts - 1) + profit) /
                self.short_metrics.successful_shorts
            )
        else:
            self.short_metrics.average_short_loss = (
                (self.short_metrics.average_short_loss * (self.short_metrics.total_short_signals - self.short_metrics.successful_shorts - 1) + abs(profit)) /
                (self.short_metrics.total_short_signals - self.short_metrics.successful_shorts)
            )
        
        # Update profit factor
        if self.short_metrics.average_short_loss > 0:
            self.short_metrics.short_profit_factor = (
                self.short_metrics.average_short_profit / self.short_metrics.average_short_loss
            )
        
        # Store performance history
        self.short_performance_history.append({
            'symbol': symbol,
            'success': success,
            'profit': profit,
            'timestamp': datetime.now()
        })
        
        logger.info(f"Updated short performance for {symbol}: Success={success}, Profit={profit}, Win Rate={self.short_metrics.short_win_rate:.2%}")
    
    async def get_short_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive short position performance report"""
        return {
            'short_metrics': {
                'total_signals': self.short_metrics.total_short_signals,
                'successful_shorts': self.short_metrics.successful_shorts,
                'win_rate': self.short_metrics.short_win_rate,
                'average_profit': self.short_metrics.average_short_profit,
                'average_loss': self.short_metrics.average_short_loss,
                'profit_factor': self.short_metrics.short_profit_factor,
                'target_win_rate': 0.65,
                'improvement_needed': 0.65 - self.short_metrics.short_win_rate
            },
            'optimization_status': {
                'current_performance': 'improving' if self.short_metrics.short_win_rate > 0.59 else 'needs_optimization',
                'target_achievement': f"{(self.short_metrics.short_win_rate / 0.65) * 100:.1f}%",
                'recommendations': await self._generate_short_optimization_recommendations()
            },
            'recent_performance': self.short_performance_history[-10:] if self.short_performance_history else []
        }
    
    async def _generate_short_optimization_recommendations(self) -> List[str]:
        """Generate recommendations for improving short position performance"""
        recommendations = []
        
        if self.short_metrics.short_win_rate < 0.65:
            recommendations.append("Increase confidence threshold for short signals")
            recommendations.append("Focus on high liquidation pressure scenarios")
            recommendations.append("Implement tighter stop losses for short positions")
            recommendations.append("Add volume confirmation requirements")
            recommendations.append("Enhance bearish sentiment analysis")
        
        if self.short_metrics.short_profit_factor < 1.5:
            recommendations.append("Improve risk/reward ratio targeting")
            recommendations.append("Optimize take profit levels")
            recommendations.append("Reduce position sizes for lower confidence signals")
        
        return recommendations

# Global instance
enhanced_short_analyzer = EnhancedShortPositionAnalyzer() 