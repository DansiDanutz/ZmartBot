#!/usr/bin/env python3
"""
Dynamic Weight Adjuster
Implements dynamic weight adjustment for Cryptometer endpoints based on market conditions
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
class MarketRegime:
    """Market regime classification"""
    regime_type: str  # trending, ranging, volatile, stable
    confidence: float
    volatility_level: float
    trend_strength: float
    market_sentiment: str
    timestamp: datetime

@dataclass
class EndpointPerformance:
    """Endpoint performance tracking"""
    endpoint_name: str
    current_weight: float
    base_weight: float
    performance_score: float
    success_rate: float
    market_condition_adaptation: float
    last_updated: datetime

@dataclass
class DynamicWeightConfig:
    """Dynamic weight configuration"""
    market_regime_weights: Dict[str, Dict[str, float]]
    performance_thresholds: Dict[str, float]
    adaptation_speed: float
    max_weight_adjustment: float
    min_weight: float
    max_weight: float

class DynamicWeightAdjuster:
    """
    Dynamic weight adjustment system for Cryptometer endpoints
    Optimizes endpoint weights based on market conditions and performance
    """
    
    def __init__(self):
        """Initialize the dynamic weight adjuster"""
        self.cryptometer_analyzer = CryptometerEndpointAnalyzer()
        
        # Market regime configurations
        self.market_regimes = {
            'trending_bullish': {
                'description': 'Strong upward trend with high momentum',
                'volatility_range': (0.3, 0.7),
                'trend_strength_range': (0.6, 1.0),
                'sentiment': 'bullish'
            },
            'trending_bearish': {
                'description': 'Strong downward trend with high momentum',
                'volatility_range': (0.3, 0.7),
                'trend_strength_range': (0.6, 1.0),
                'sentiment': 'bearish'
            },
            'ranging_volatile': {
                'description': 'Sideways movement with high volatility',
                'volatility_range': (0.6, 1.0),
                'trend_strength_range': (0.0, 0.4),
                'sentiment': 'neutral'
            },
            'ranging_stable': {
                'description': 'Sideways movement with low volatility',
                'volatility_range': (0.0, 0.3),
                'trend_strength_range': (0.0, 0.4),
                'sentiment': 'neutral'
            },
            'breakout_volatile': {
                'description': 'High volatility breakout conditions',
                'volatility_range': (0.7, 1.0),
                'trend_strength_range': (0.5, 1.0),
                'sentiment': 'mixed'
            }
        }
        
        # Dynamic weight configurations for different market regimes
        self.dynamic_config = DynamicWeightConfig(
            market_regime_weights={
                'trending_bullish': {
                    'ai_screener': 18.0,  # Increased for trend following
                    'trend_indicator_v3': 12.0,  # Strong trend analysis
                    'ls_ratio': 10.0,  # Sentiment analysis
                    'liquidation_data_v2': 8.0,  # Reduced in bullish trend
                    'rapid_movements': 8.0,
                    'ohlcv': 8.0,
                    'ticker': 7.0,
                    'volume_v2': 7.0,
                    'xtrades': 6.0,
                    'tickerlist_pro': 6.0,
                    'cryptocurrency_info': 5.0,
                    'large_trades': 4.0,
                    'coin_info': 3.0,
                    'forex_rates': 3.0,
                    'ai_screener_analysis': 2.0,
                    'coinlist': 1.0
                },
                'trending_bearish': {
                    'liquidation_data_v2': 18.0,  # Increased for bearish analysis
                    'ls_ratio': 15.0,  # Strong short sentiment
                    'rapid_movements': 12.0,  # Momentum analysis
                    'ai_screener': 10.0,
                    'xtrades': 9.0,  # Whale activity
                    'volume_v2': 8.0,
                    'trend_indicator_v3': 7.0,
                    'ohlcv': 6.0,
                    'ticker': 5.0,
                    'tickerlist_pro': 4.0,
                    'cryptocurrency_info': 3.0,
                    'large_trades': 3.0,
                    'coin_info': 2.0,
                    'forex_rates': 2.0,
                    'ai_screener_analysis': 1.0,
                    'coinlist': 1.0
                },
                'ranging_volatile': {
                    'rapid_movements': 16.0,  # High volatility focus
                    'liquidation_data_v2': 14.0,  # Liquidation clusters
                    'ai_screener': 12.0,  # AI analysis
                    'volume_v2': 10.0,  # Volume analysis
                    'xtrades': 9.0,  # Whale activity
                    'ls_ratio': 8.0,
                    'trend_indicator_v3': 7.0,
                    'ohlcv': 6.0,
                    'ticker': 5.0,
                    'tickerlist_pro': 4.0,
                    'cryptocurrency_info': 3.0,
                    'large_trades': 3.0,
                    'coin_info': 2.0,
                    'forex_rates': 1.0,
                    'ai_screener_analysis': 1.0,
                    'coinlist': 1.0
                },
                'ranging_stable': {
                    'ai_screener': 15.0,  # AI analysis for stable markets
                    'trend_indicator_v3': 12.0,  # Trend detection
                    'ls_ratio': 10.0,  # Sentiment analysis
                    'ohlcv': 9.0,  # Technical analysis
                    'ticker': 8.0,
                    'volume_v2': 8.0,
                    'cryptocurrency_info': 7.0,  # Fundamental analysis
                    'tickerlist_pro': 6.0,
                    'xtrades': 5.0,
                    'liquidation_data_v2': 4.0,  # Reduced in stable markets
                    'rapid_movements': 4.0,  # Reduced in stable markets
                    'large_trades': 4.0,
                    'coin_info': 3.0,
                    'forex_rates': 2.0,
                    'ai_screener_analysis': 2.0,
                    'coinlist': 1.0
                },
                'breakout_volatile': {
                    'rapid_movements': 18.0,  # Maximum volatility focus
                    'liquidation_data_v2': 15.0,  # Liquidation analysis
                    'ai_screener': 12.0,  # AI analysis
                    'xtrades': 10.0,  # Whale activity
                    'volume_v2': 9.0,  # Volume analysis
                    'trend_indicator_v3': 8.0,
                    'ls_ratio': 7.0,
                    'ohlcv': 6.0,
                    'ticker': 5.0,
                    'tickerlist_pro': 4.0,
                    'cryptocurrency_info': 3.0,
                    'large_trades': 3.0,
                    'coin_info': 2.0,
                    'forex_rates': 1.0,
                    'ai_screener_analysis': 1.0,
                    'coinlist': 1.0
                }
            },
            performance_thresholds={
                'min_success_rate': 0.55,
                'min_performance_score': 0.6,
                'adaptation_threshold': 0.1
            },
            adaptation_speed=0.1,  # 10% weight adjustment per cycle
            max_weight_adjustment=0.3,  # Maximum 30% weight change
            min_weight=1.0,
            max_weight=20.0
        )
        
        # Performance tracking
        self.endpoint_performance: Dict[str, EndpointPerformance] = {}
        self.market_regime_history: List[MarketRegime] = []
        self.weight_adjustment_history: List[Dict[str, Any]] = []
        
        # Initialize endpoint performance tracking
        self._initialize_endpoint_performance()
        
        logger.info("Dynamic Weight Adjuster initialized")
    
    def _initialize_endpoint_performance(self):
        """Initialize endpoint performance tracking"""
        base_endpoints = {
            'ai_screener': 15.0,
            'ls_ratio': 12.0,
            'liquidation_data_v2': 11.0,
            'ohlcv': 10.0,
            'trend_indicator_v3': 9.0,
            'ticker': 8.0,
            'volume_v2': 8.0,
            'xtrades': 7.0,
            'tickerlist_pro': 7.0,
            'cryptocurrency_info': 6.0,
            'rapid_movements': 6.0,
            'tickerlist': 5.0,
            'large_trades': 5.0,
            'coin_info': 4.0,
            'forex_rates': 4.0,
            'ai_screener_analysis': 3.0,
            'coinlist': 2.0
        }
        
        for endpoint, base_weight in base_endpoints.items():
            self.endpoint_performance[endpoint] = EndpointPerformance(
                endpoint_name=endpoint,
                current_weight=base_weight,
                base_weight=base_weight,
                performance_score=0.7,  # Initial neutral score
                success_rate=0.65,  # Initial neutral rate
                market_condition_adaptation=1.0,
                last_updated=datetime.now()
            )
    
    async def detect_market_regime(self, symbol: str) -> MarketRegime:
        """Detect current market regime based on Cryptometer data"""
        try:
            # Get comprehensive analysis
            cryptometer_analysis = await self.cryptometer_analyzer.analyze_symbol(symbol)
            
            # Extract key metrics for regime detection
            volatility_score = 0.0
            trend_strength = 0.0
            sentiment_score = cryptometer_analysis.total_score
            
            # Analyze volatility from rapid movements
            for endpoint_score in cryptometer_analysis.endpoint_scores:
                if endpoint_score.endpoint_name == 'rapid_movements':
                    volatility_score = endpoint_score.score
                    break
            
            # Analyze trend strength from trend indicator
            for endpoint_score in cryptometer_analysis.endpoint_scores:
                if endpoint_score.endpoint_name == 'trend_indicator_v3':
                    trend_strength = endpoint_score.score
                    break
            
            # Determine market regime
            regime_type = await self._classify_market_regime(volatility_score, trend_strength, sentiment_score)
            
            # Calculate regime confidence
            confidence = await self._calculate_regime_confidence(volatility_score, trend_strength, sentiment_score)
            
            market_regime = MarketRegime(
                regime_type=regime_type,
                confidence=confidence,
                volatility_level=volatility_score,
                trend_strength=trend_strength,
                market_sentiment=await self._determine_sentiment(sentiment_score),
                timestamp=datetime.now()
            )
            
            # Store regime history
            self.market_regime_history.append(market_regime)
            
            logger.info(f"Detected market regime for {symbol}: {regime_type} (confidence: {confidence:.2f})")
            
            return market_regime
            
        except Exception as e:
            logger.error(f"Error detecting market regime for {symbol}: {e}")
            # Return default regime
            return MarketRegime(
                regime_type='ranging_stable',
                confidence=0.5,
                volatility_level=0.3,
                trend_strength=0.2,
                market_sentiment='neutral',
                timestamp=datetime.now()
            )
    
    async def _classify_market_regime(self, volatility: float, trend_strength: float, sentiment: float) -> str:
        """Classify market regime based on volatility, trend strength, and sentiment"""
        # High volatility conditions
        if volatility > 0.7:
            if trend_strength > 0.6:
                return 'breakout_volatile'
            else:
                return 'ranging_volatile'
        
        # Low volatility conditions
        elif volatility < 0.3:
            if trend_strength > 0.6:
                if sentiment > 0.6:
                    return 'trending_bullish'
                elif sentiment < 0.4:
                    return 'trending_bearish'
                else:
                    return 'trending_bullish'  # Default to bullish in strong trends
            else:
                return 'ranging_stable'
        
        # Medium volatility conditions
        else:
            if trend_strength > 0.6:
                if sentiment > 0.6:
                    return 'trending_bullish'
                elif sentiment < 0.4:
                    return 'trending_bearish'
                else:
                    return 'trending_bullish'  # Default to bullish
            else:
                return 'ranging_volatile'
    
    async def _calculate_regime_confidence(self, volatility: float, trend_strength: float, sentiment: float) -> float:
        """Calculate confidence in market regime classification"""
        # Base confidence from data quality
        base_confidence = 0.7
        
        # Adjust based on volatility clarity
        volatility_confidence = 1.0 - abs(volatility - 0.5) * 2  # Higher confidence at extremes
        
        # Adjust based on trend strength clarity
        trend_confidence = 1.0 - abs(trend_strength - 0.5) * 2  # Higher confidence at extremes
        
        # Adjust based on sentiment clarity
        sentiment_confidence = 1.0 - abs(sentiment - 0.5) * 2  # Higher confidence at extremes
        
        # Calculate weighted average
        confidence = (base_confidence + volatility_confidence + trend_confidence + sentiment_confidence) / 4
        
        return min(1.0, max(0.0, confidence))
    
    async def _determine_sentiment(self, sentiment_score: float) -> str:
        """Determine market sentiment from score"""
        if sentiment_score > 0.6:
            return 'bullish'
        elif sentiment_score < 0.4:
            return 'bearish'
        else:
            return 'neutral'
    
    async def get_optimized_weights(self, symbol: str, market_regime: MarketRegime) -> Dict[str, float]:
        """Get optimized endpoint weights for current market regime"""
        try:
            # Get base weights for the detected regime
            regime_weights = self.dynamic_config.market_regime_weights.get(
                market_regime.regime_type, 
                self.dynamic_config.market_regime_weights['ranging_stable']
            )
            
            # Apply performance-based adjustments
            optimized_weights = {}
            for endpoint, base_weight in regime_weights.items():
                if endpoint in self.endpoint_performance:
                    performance = self.endpoint_performance[endpoint]
                    
                    # Calculate performance adjustment
                    performance_adjustment = await self._calculate_performance_adjustment(performance)
                    
                    # Apply adjustment
                    adjusted_weight = base_weight * performance_adjustment
                    
                    # Ensure within bounds
                    adjusted_weight = max(
                        self.dynamic_config.min_weight,
                        min(self.dynamic_config.max_weight, adjusted_weight)
                    )
                    
                    optimized_weights[endpoint] = adjusted_weight
                else:
                    optimized_weights[endpoint] = base_weight
            
            # Normalize weights to sum to 100
            total_weight = sum(optimized_weights.values())
            if total_weight > 0:
                normalized_weights = {
                    endpoint: (weight / total_weight) * 100
                    for endpoint, weight in optimized_weights.items()
                }
            else:
                normalized_weights = optimized_weights
            
            logger.info(f"Optimized weights for {symbol} ({market_regime.regime_type}): {normalized_weights}")
            
            return normalized_weights
            
        except Exception as e:
            logger.error(f"Error getting optimized weights for {symbol}: {e}")
            # Return default weights
            return self.dynamic_config.market_regime_weights['ranging_stable']
    
    async def _calculate_performance_adjustment(self, performance: EndpointPerformance) -> float:
        """Calculate performance-based weight adjustment"""
        # Base adjustment factor
        adjustment = 1.0
        
        # Adjust based on success rate
        if performance.success_rate > self.dynamic_config.performance_thresholds['min_success_rate']:
            success_adjustment = (performance.success_rate - 0.5) * 2  # Scale to 0-1
            adjustment *= (1 + success_adjustment * 0.2)  # Max 20% boost
        
        # Adjust based on performance score
        if performance.performance_score > self.dynamic_config.performance_thresholds['min_performance_score']:
            performance_adjustment = (performance.performance_score - 0.5) * 2  # Scale to 0-1
            adjustment *= (1 + performance_adjustment * 0.15)  # Max 15% boost
        
        # Apply market condition adaptation
        adjustment *= performance.market_condition_adaptation
        
        return adjustment
    
    async def update_endpoint_performance(self, endpoint: str, success: bool, profit: float, 
                                        market_regime: str, symbol: str):
        """Update endpoint performance metrics"""
        if endpoint not in self.endpoint_performance:
            return
        
        performance = self.endpoint_performance[endpoint]
        
        # Update success rate (simplified calculation)
        # In a real implementation, this would track historical performance
        if success:
            performance.success_rate = min(1.0, performance.success_rate + 0.01)
        else:
            performance.success_rate = max(0.0, performance.success_rate - 0.01)
        
        # Update performance score based on profit
        if profit > 0:
            performance.performance_score = min(1.0, performance.performance_score + 0.02)
        else:
            performance.performance_score = max(0.0, performance.performance_score - 0.02)
        
        # Update market condition adaptation
        current_regime_weights = self.dynamic_config.market_regime_weights.get(market_regime, {})
        if endpoint in current_regime_weights:
            expected_weight = current_regime_weights[endpoint]
            actual_performance = performance.success_rate * performance.performance_score
            
            if actual_performance > 0.7:  # Good performance
                performance.market_condition_adaptation = min(1.2, performance.market_condition_adaptation + 0.05)
            elif actual_performance < 0.5:  # Poor performance
                performance.market_condition_adaptation = max(0.8, performance.market_condition_adaptation - 0.05)
        
        performance.last_updated = datetime.now()
        
        logger.info(f"Updated performance for {endpoint}: Success={success}, Profit={profit}, Success Rate={performance.success_rate:.2f}")
    
    async def get_dynamic_analysis_report(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive dynamic weight analysis report"""
        try:
            # Detect current market regime
            market_regime = await self.detect_market_regime(symbol)
            
            # Get optimized weights
            optimized_weights = await self.get_optimized_weights(symbol, market_regime)
            
            # Calculate weight adjustments
            weight_adjustments = {}
            for endpoint, optimized_weight in optimized_weights.items():
                if endpoint in self.endpoint_performance:
                    current_weight = self.endpoint_performance[endpoint].current_weight
                    adjustment = ((optimized_weight - current_weight) / current_weight) * 100
                    weight_adjustments[endpoint] = adjustment
            
            return {
                'market_regime': {
                    'type': market_regime.regime_type,
                    'confidence': market_regime.confidence,
                    'volatility_level': market_regime.volatility_level,
                    'trend_strength': market_regime.trend_strength,
                    'sentiment': market_regime.market_sentiment,
                    'description': self.market_regimes.get(market_regime.regime_type, {}).get('description', '')
                },
                'optimized_weights': optimized_weights,
                'weight_adjustments': weight_adjustments,
                'performance_summary': {
                    'top_performers': await self._get_top_performers(),
                    'underperformers': await self._get_underperformers(),
                    'adaptation_status': await self._get_adaptation_status()
                },
                'recommendations': await self._generate_dynamic_recommendations(market_regime, weight_adjustments),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating dynamic analysis report for {symbol}: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _get_top_performers(self) -> List[Dict[str, Any]]:
        """Get top performing endpoints"""
        performers = []
        for endpoint, performance in self.endpoint_performance.items():
            if performance.success_rate > 0.7 and performance.performance_score > 0.7:
                performers.append({
                    'endpoint': endpoint,
                    'success_rate': performance.success_rate,
                    'performance_score': performance.performance_score,
                    'current_weight': performance.current_weight
                })
        
        return sorted(performers, key=lambda x: x['success_rate'], reverse=True)[:5]
    
    async def _get_underperformers(self) -> List[Dict[str, Any]]:
        """Get underperforming endpoints"""
        underperformers = []
        for endpoint, performance in self.endpoint_performance.items():
            if performance.success_rate < 0.5 or performance.performance_score < 0.5:
                underperformers.append({
                    'endpoint': endpoint,
                    'success_rate': performance.success_rate,
                    'performance_score': performance.performance_score,
                    'current_weight': performance.current_weight
                })
        
        return sorted(underperformers, key=lambda x: x['success_rate'])[:5]
    
    async def _get_adaptation_status(self) -> Dict[str, Any]:
        """Get adaptation status summary"""
        total_endpoints = len(self.endpoint_performance)
        adapted_endpoints = sum(1 for p in self.endpoint_performance.values() 
                              if p.market_condition_adaptation != 1.0)
        
        return {
            'total_endpoints': total_endpoints,
            'adapted_endpoints': adapted_endpoints,
            'adaptation_rate': adapted_endpoints / total_endpoints if total_endpoints > 0 else 0,
            'average_adaptation': statistics.mean([p.market_condition_adaptation for p in self.endpoint_performance.values()])
        }
    
    async def _generate_dynamic_recommendations(self, market_regime: MarketRegime, 
                                              weight_adjustments: Dict[str, float]) -> List[str]:
        """Generate recommendations based on dynamic analysis"""
        recommendations = []
        
        # Market regime specific recommendations
        if market_regime.regime_type == 'trending_bullish':
            recommendations.append("Focus on trend-following endpoints (ai_screener, trend_indicator_v3)")
            recommendations.append("Reduce weight on liquidation analysis in bullish trends")
        
        elif market_regime.regime_type == 'trending_bearish':
            recommendations.append("Increase weight on liquidation and sentiment analysis")
            recommendations.append("Focus on rapid movements and whale activity endpoints")
        
        elif market_regime.regime_type == 'ranging_volatile':
            recommendations.append("Prioritize volatility-focused endpoints (rapid_movements, liquidation_data_v2)")
            recommendations.append("Use AI screener for pattern recognition in volatile conditions")
        
        elif market_regime.regime_type == 'ranging_stable':
            recommendations.append("Focus on fundamental and technical analysis endpoints")
            recommendations.append("Reduce weight on volatility-focused endpoints")
        
        elif market_regime.regime_type == 'breakout_volatile':
            recommendations.append("Maximum weight on volatility and momentum endpoints")
            recommendations.append("Monitor whale activity for breakout confirmation")
        
        # Performance-based recommendations
        large_adjustments = [ep for ep, adj in weight_adjustments.items() if abs(adj) > 20]
        if large_adjustments:
            recommendations.append(f"Significant weight adjustments needed for: {', '.join(large_adjustments)}")
        
        # Confidence-based recommendations
        if market_regime.confidence < 0.6:
            recommendations.append("Low confidence in market regime - use conservative weight adjustments")
        
        return recommendations

# Global instance
dynamic_weight_adjuster = DynamicWeightAdjuster() 