#!/usr/bin/env python3
"""
Master Scoring Agent
Combines scores from Cryptometer, RiskMetric, and KingFisher modules
Applies dynamic weighting, historical pattern triggers, and market conditions
Produces the final authoritative trading score
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import asyncio
import json
from dataclasses import dataclass
from collections import deque
import statistics
import uuid
import sys
from pathlib import Path

# Add learning system import
sys.path.append(str(Path(__file__).parent.parent.parent))
try:
    from src.learning.self_learning_system import learning_system, Prediction
    LEARNING_AVAILABLE = True
except ImportError:
    LEARNING_AVAILABLE = False
    learning_system = None

logger = logging.getLogger(__name__)

class MarketCondition(Enum):
    """Current market conditions affecting weight distribution"""
    EXTREME_VOLATILITY = "extreme_volatility"    # High weight to KingFisher
    HIGH_VOLATILITY = "high_volatility"           # Balanced with KingFisher bias
    NORMAL = "normal"                             # Standard weights
    LOW_VOLATILITY = "low_volatility"             # Higher weight to RiskMetric
    TRENDING_STRONG = "trending_strong"           # Higher weight to Cryptometer
    RANGING = "ranging"                           # Balanced weights
    UNCERTAIN = "uncertain"                       # Conservative weights

class PatternTrigger(Enum):
    """Historical pattern triggers that affect scoring"""
    GOLDEN_CROSS = "golden_cross"                 # Bullish MA crossover
    DEATH_CROSS = "death_cross"                   # Bearish MA crossover
    SUPPORT_BOUNCE = "support_bounce"             # Price bouncing off support
    RESISTANCE_REJECTION = "resistance_rejection"  # Price rejected at resistance
    VOLUME_BREAKOUT = "volume_breakout"           # High volume price breakout
    LIQUIDATION_CASCADE = "liquidation_cascade"    # Liquidation cascade detected
    DIVERGENCE_BULLISH = "divergence_bullish"     # Price/indicator divergence
    DIVERGENCE_BEARISH = "divergence_bearish"     # Price/indicator divergence
    ACCUMULATION = "accumulation"                 # Smart money accumulating
    DISTRIBUTION = "distribution"                 # Smart money distributing
    SQUEEZE_BREAKOUT = "squeeze_breakout"         # Volatility squeeze breakout
    TREND_EXHAUSTION = "trend_exhaustion"         # Trend losing momentum

@dataclass
class ModuleScore:
    """Score from individual module"""
    module_name: str
    raw_score: float          # 0-100 scale
    confidence: float         # 0-1 confidence level
    timeframe: str           # short/medium/long
    win_rate_long: float     # Win rate for long positions
    win_rate_short: float    # Win rate for short positions
    risk_level: str          # low/medium/high
    key_factors: List[str]   # Key factors affecting score
    timestamp: datetime
    report: str              # Full professional report

@dataclass
class FinalScore:
    """Final combined score with all components"""
    symbol: str
    final_score: float                    # 0-100 final weighted score
    position_recommendation: str          # STRONG_LONG/LONG/NEUTRAL/SHORT/STRONG_SHORT
    confidence_level: float               # 0-1 overall confidence
    
    # Individual module contributions
    cryptometer_weight: float
    cryptometer_contribution: float
    riskmetric_weight: float
    riskmetric_contribution: float
    kingfisher_weight: float
    kingfisher_contribution: float
    
    # Pattern and market adjustments
    pattern_coefficient: float            # Multiplier from pattern triggers
    market_condition: MarketCondition
    active_patterns: List[PatternTrigger]
    
    # Risk and position sizing
    risk_score: float                     # 0-100 risk level
    suggested_position_size: str         # Position size recommendation
    stop_loss_percentage: float          # Suggested stop loss %
    take_profit_targets: List[float]     # Take profit levels
    
    # Detailed analysis
    key_insights: List[str]
    warnings: List[str]
    opportunities: List[str]
    
    # Metadata
    timestamp: datetime
    processing_time_ms: int
    data_quality_score: float            # 0-1 quality of input data

class MasterScoringAgent:
    """
    Master Scoring Agent that combines all module scores
    Implements sophisticated weighting and pattern recognition
    """
    
    def __init__(self):
        # Base weight distributions
        self.base_weights = {
            'cryptometer': 0.35,   # 35% - Real-time market data
            'riskmetric': 0.35,    # 35% - Historical patterns
            'kingfisher': 0.30     # 30% - Liquidation analysis
        }
        
        # Market condition weight adjustments
        self.market_condition_weights = {
            MarketCondition.EXTREME_VOLATILITY: {
                'cryptometer': 0.25,
                'riskmetric': 0.25,
                'kingfisher': 0.50  # Higher weight for liquidation data
            },
            MarketCondition.HIGH_VOLATILITY: {
                'cryptometer': 0.30,
                'riskmetric': 0.30,
                'kingfisher': 0.40
            },
            MarketCondition.NORMAL: {
                'cryptometer': 0.35,
                'riskmetric': 0.35,
                'kingfisher': 0.30
            },
            MarketCondition.LOW_VOLATILITY: {
                'cryptometer': 0.35,
                'riskmetric': 0.45,  # Historical patterns more reliable
                'kingfisher': 0.20
            },
            MarketCondition.TRENDING_STRONG: {
                'cryptometer': 0.45,  # Trend indicators important
                'riskmetric': 0.30,
                'kingfisher': 0.25
            },
            MarketCondition.RANGING: {
                'cryptometer': 0.33,
                'riskmetric': 0.34,
                'kingfisher': 0.33
            },
            MarketCondition.UNCERTAIN: {
                'cryptometer': 0.30,
                'riskmetric': 0.40,  # Rely on historical data
                'kingfisher': 0.30
            }
        }
        
        # Pattern trigger coefficients (multipliers)
        self.pattern_coefficients = {
            PatternTrigger.GOLDEN_CROSS: 1.15,          # +15% bullish bias
            PatternTrigger.DEATH_CROSS: 0.85,           # -15% bearish bias
            PatternTrigger.SUPPORT_BOUNCE: 1.10,        # +10% bullish
            PatternTrigger.RESISTANCE_REJECTION: 0.90,   # -10% bearish
            PatternTrigger.VOLUME_BREAKOUT: 1.20,       # +20% strong signal
            PatternTrigger.LIQUIDATION_CASCADE: 0.75,    # -25% danger signal
            PatternTrigger.DIVERGENCE_BULLISH: 1.12,    # +12% bullish
            PatternTrigger.DIVERGENCE_BEARISH: 0.88,    # -12% bearish
            PatternTrigger.ACCUMULATION: 1.08,          # +8% bullish
            PatternTrigger.DISTRIBUTION: 0.92,          # -8% bearish
            PatternTrigger.SQUEEZE_BREAKOUT: 1.18,      # +18% momentum
            PatternTrigger.TREND_EXHAUSTION: 0.95       # -5% caution
        }
        
        # Historical data storage
        self.score_history = {}  # Symbol -> deque of scores
        self.pattern_history = {}  # Symbol -> pattern occurrences
        
        # Confidence thresholds
        self.confidence_thresholds = {
            'high': 0.75,
            'medium': 0.50,
            'low': 0.25
        }
        
        # Self-learning integration
        self.learning_enabled = LEARNING_AVAILABLE
        self.learning_history = deque(maxlen=1000)  # Track recent predictions
        
        logger.info(f"Master Scoring Agent initialized (Learning: {self.learning_enabled})")
    
    async def calculate_final_score(
        self,
        symbol: str,
        cryptometer_score: ModuleScore,
        riskmetric_score: ModuleScore,
        kingfisher_score: ModuleScore,
        market_data: Optional[Dict[str, Any]] = None
    ) -> FinalScore:
        """
        Calculate the final weighted score combining all modules
        
        Args:
            symbol: Trading symbol
            cryptometer_score: Score from Cryptometer module
            riskmetric_score: Score from RiskMetric module
            kingfisher_score: Score from KingFisher module
            market_data: Optional current market data
            
        Returns:
            FinalScore with all analysis components
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Detect market condition
            market_condition = self._detect_market_condition(
                cryptometer_score, market_data
            )
            
            # Step 2: Get dynamic weights based on market condition
            weights = self._calculate_dynamic_weights(
                market_condition,
                cryptometer_score,
                riskmetric_score,
                kingfisher_score
            )
            
            # Step 3: Detect active patterns
            active_patterns = self._detect_patterns(
                symbol,
                cryptometer_score,
                riskmetric_score,
                kingfisher_score,
                market_data
            )
            
            # Step 4: Calculate pattern coefficient
            pattern_coefficient = self._calculate_pattern_coefficient(active_patterns)
            
            # Step 5: Calculate weighted base score
            base_score = self._calculate_weighted_score(
                cryptometer_score.raw_score,
                riskmetric_score.raw_score,
                kingfisher_score.raw_score,
                weights
            )
            
            # Step 6: Apply pattern coefficient
            adjusted_score = base_score * pattern_coefficient
            
            # Step 7: Apply confidence weighting
            confidence_weighted_score = self._apply_confidence_weighting(
                adjusted_score,
                cryptometer_score.confidence,
                riskmetric_score.confidence,
                kingfisher_score.confidence,
                weights
            )
            
            # Step 8: Apply self-learning correction
            if self.learning_enabled and learning_system:
                # Create learning features
                learning_features = self._create_learning_features(
                    symbol, cryptometer_score, riskmetric_score, kingfisher_score,
                    market_condition, active_patterns, market_data
                )
                
                # Get learning correction
                corrected_score, learning_confidence = await learning_system.get_learning_correction(
                    agent_name="MasterScoringAgent",
                    prediction_type="score",
                    features=learning_features,
                    original_prediction=confidence_weighted_score
                )
                
                # Blend original and corrected based on learning confidence
                blend_factor = learning_confidence * 0.3  # Max 30% influence
                final_score_value = (confidence_weighted_score * (1 - blend_factor) + 
                                   corrected_score * blend_factor)
                
                logger.debug(f"Applied learning correction: {confidence_weighted_score:.1f} -> {final_score_value:.1f}")
            else:
                final_score_value = confidence_weighted_score
            
            # Step 9: Calculate final score (0-100 bounded)
            final_score_value = max(0, min(100, final_score_value))
            
            # Step 10: Determine position recommendation
            position_recommendation = self._determine_position(
                final_score_value,
                cryptometer_score,
                riskmetric_score,
                kingfisher_score
            )
            
            # Step 11: Calculate risk metrics
            risk_score = self._calculate_risk_score(
                cryptometer_score,
                riskmetric_score,
                kingfisher_score
            )
            
            # Step 12: Generate insights and warnings
            insights, warnings, opportunities = self._generate_insights(
                symbol,
                final_score_value,
                active_patterns,
                market_condition,
                cryptometer_score,
                riskmetric_score,
                kingfisher_score
            )
            
            # Step 13: Calculate position sizing and targets
            position_size, stop_loss, take_profits = self._calculate_trading_parameters(
                final_score_value,
                risk_score,
                market_condition,
                position_recommendation
            )
            
            # Step 14: Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(
                cryptometer_score.confidence,
                riskmetric_score.confidence,
                kingfisher_score.confidence,
                len(active_patterns),
                market_condition
            )
            
            # Step 15: Calculate data quality
            data_quality = self._assess_data_quality(
                cryptometer_score,
                riskmetric_score,
                kingfisher_score
            )
            
            # Step 16: Record prediction for learning
            if self.learning_enabled and learning_system:
                prediction_id = str(uuid.uuid4())
                
                prediction = Prediction(
                    agent_name="MasterScoringAgent",
                    symbol=symbol,
                    prediction_type="score",
                    predicted_value=final_score_value,
                    confidence=overall_confidence,
                    features=learning_features,
                    timestamp=datetime.now(),
                    prediction_id=prediction_id
                )
                
                # Record prediction for future learning
                await learning_system.record_prediction(prediction)
                
                # Store in local history for outcome tracking
                self.learning_history.append({
                    'prediction_id': prediction_id,
                    'symbol': symbol,
                    'score': final_score_value,
                    'timestamp': datetime.now(),
                    'position': position_recommendation
                })
            
            # Store in history
            self._update_history(symbol, final_score_value, active_patterns)
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Create final score object
            return FinalScore(
                symbol=symbol,
                final_score=final_score_value,
                position_recommendation=position_recommendation,
                confidence_level=overall_confidence,
                
                # Weights and contributions
                cryptometer_weight=weights['cryptometer'],
                cryptometer_contribution=cryptometer_score.raw_score * weights['cryptometer'],
                riskmetric_weight=weights['riskmetric'],
                riskmetric_contribution=riskmetric_score.raw_score * weights['riskmetric'],
                kingfisher_weight=weights['kingfisher'],
                kingfisher_contribution=kingfisher_score.raw_score * weights['kingfisher'],
                
                # Adjustments
                pattern_coefficient=pattern_coefficient,
                market_condition=market_condition,
                active_patterns=active_patterns,
                
                # Risk and trading
                risk_score=risk_score,
                suggested_position_size=position_size,
                stop_loss_percentage=stop_loss,
                take_profit_targets=take_profits,
                
                # Analysis
                key_insights=insights,
                warnings=warnings,
                opportunities=opportunities,
                
                # Metadata
                timestamp=datetime.now(),
                processing_time_ms=processing_time,
                data_quality_score=data_quality
            )
            
        except Exception as e:
            logger.error(f"Error calculating final score for {symbol}: {e}")
            raise
    
    def _detect_market_condition(self, cryptometer_score: ModuleScore,
                                market_data: Optional[Dict]) -> MarketCondition:
        """Detect current market condition"""
        # Extract volatility from Cryptometer data
        volatility = market_data.get('volatility_index', 0.5) if market_data else 0.5
        trend_strength = market_data.get('trend_strength', 0.5) if market_data else 0.5
        
        # Determine market condition
        if volatility > 0.8:
            return MarketCondition.EXTREME_VOLATILITY
        elif volatility > 0.6:
            return MarketCondition.HIGH_VOLATILITY
        elif volatility < 0.3:
            return MarketCondition.LOW_VOLATILITY
        elif trend_strength > 0.7:
            return MarketCondition.TRENDING_STRONG
        elif trend_strength < 0.3:
            return MarketCondition.RANGING
        elif cryptometer_score.confidence < 0.5:
            return MarketCondition.UNCERTAIN
        else:
            return MarketCondition.NORMAL
    
    def _calculate_dynamic_weights(self, market_condition: MarketCondition,
                                  crypto_score: ModuleScore,
                                  risk_score: ModuleScore,
                                  king_score: ModuleScore) -> Dict[str, float]:
        """Calculate dynamic weights based on market condition and data quality"""
        # Start with market condition weights
        weights = self.market_condition_weights[market_condition].copy()
        
        # Adjust based on confidence levels
        total_confidence = crypto_score.confidence + risk_score.confidence + king_score.confidence
        
        if total_confidence > 0:
            confidence_adjustments = {
                'cryptometer': crypto_score.confidence / total_confidence,
                'riskmetric': risk_score.confidence / total_confidence,
                'kingfisher': king_score.confidence / total_confidence
            }
            
            # Blend market weights with confidence weights (70/30 split)
            for module in weights:
                weights[module] = (weights[module] * 0.7 + 
                                 confidence_adjustments[module] * 0.3)
        
        # Normalize weights to sum to 1
        total_weight = sum(weights.values())
        for module in weights:
            weights[module] /= total_weight
        
        return weights
    
    def _detect_patterns(self, symbol: str, crypto_score: ModuleScore,
                        risk_score: ModuleScore, king_score: ModuleScore,
                        market_data: Optional[Dict]) -> List[PatternTrigger]:
        """Detect active historical patterns"""
        patterns = []
        
        # Check for MA crossovers (from Cryptometer)
        if market_data:
            ema_9 = market_data.get('ema_9', 0)
            ema_21 = market_data.get('ema_21', 0)
            ema_50 = market_data.get('ema_50', 0)
            ema_200 = market_data.get('ema_200', 0)
            
            if ema_50 > ema_200 and ema_21 > ema_50:
                patterns.append(PatternTrigger.GOLDEN_CROSS)
            elif ema_50 < ema_200 and ema_21 < ema_50:
                patterns.append(PatternTrigger.DEATH_CROSS)
        
        # Check for support/resistance (from KingFisher)
        if 'support_bounce' in king_score.key_factors:
            patterns.append(PatternTrigger.SUPPORT_BOUNCE)
        if 'resistance_rejection' in king_score.key_factors:
            patterns.append(PatternTrigger.RESISTANCE_REJECTION)
        
        # Check for volume patterns (from Cryptometer)
        if 'volume_breakout' in crypto_score.key_factors:
            patterns.append(PatternTrigger.VOLUME_BREAKOUT)
        
        # Check for liquidation cascade (from KingFisher)
        if king_score.risk_level == 'high' and 'liquidation_cluster' in king_score.key_factors:
            patterns.append(PatternTrigger.LIQUIDATION_CASCADE)
        
        # Check for divergences
        if crypto_score.win_rate_long > 60 and king_score.win_rate_short > 60:
            patterns.append(PatternTrigger.DIVERGENCE_BULLISH)
        elif crypto_score.win_rate_short > 60 and king_score.win_rate_long > 60:
            patterns.append(PatternTrigger.DIVERGENCE_BEARISH)
        
        # Check for accumulation/distribution (from RiskMetric)
        if 'accumulation_phase' in risk_score.key_factors:
            patterns.append(PatternTrigger.ACCUMULATION)
        elif 'distribution_phase' in risk_score.key_factors:
            patterns.append(PatternTrigger.DISTRIBUTION)
        
        # Check for volatility squeeze
        if market_data and market_data.get('volatility_index', 1) < 0.3:
            if 'breakout_imminent' in crypto_score.key_factors:
                patterns.append(PatternTrigger.SQUEEZE_BREAKOUT)
        
        # Check for trend exhaustion
        if risk_score.raw_score < 40 and 'trend_weakening' in risk_score.key_factors:
            patterns.append(PatternTrigger.TREND_EXHAUSTION)
        
        return patterns
    
    def _calculate_pattern_coefficient(self, patterns: List[PatternTrigger]) -> float:
        """Calculate combined pattern coefficient"""
        if not patterns:
            return 1.0
        
        # Multiply all pattern coefficients
        coefficient = 1.0
        for pattern in patterns:
            coefficient *= self.pattern_coefficients.get(pattern, 1.0)
        
        # Limit the coefficient to prevent extreme values
        return max(0.5, min(1.5, coefficient))
    
    def _calculate_weighted_score(self, crypto: float, risk: float, 
                                 king: float, weights: Dict[str, float]) -> float:
        """Calculate weighted average of module scores"""
        return (crypto * weights['cryptometer'] +
                risk * weights['riskmetric'] +
                king * weights['kingfisher'])
    
    def _apply_confidence_weighting(self, score: float, crypto_conf: float,
                                   risk_conf: float, king_conf: float,
                                   weights: Dict[str, float]) -> float:
        """Apply confidence-based adjustment to score"""
        # Calculate weighted confidence
        weighted_confidence = (crypto_conf * weights['cryptometer'] +
                              risk_conf * weights['riskmetric'] +
                              king_conf * weights['kingfisher'])
        
        # Apply confidence factor (reduces score if confidence is low)
        confidence_factor = 0.7 + (0.3 * weighted_confidence)
        
        return score * confidence_factor
    
    def _determine_position(self, score: float, crypto: ModuleScore,
                          risk: ModuleScore, king: ModuleScore) -> str:
        """Determine position recommendation based on score and win rates"""
        # Calculate average win rates
        avg_long_win = np.mean([crypto.win_rate_long, risk.win_rate_long, king.win_rate_long])
        avg_short_win = np.mean([crypto.win_rate_short, risk.win_rate_short, king.win_rate_short])
        
        # Determine position based on score and win rates
        if score >= 70 and avg_long_win > 65:
            return "STRONG_LONG"
        elif score >= 55 and avg_long_win > 55:
            return "LONG"
        elif score <= 30 and avg_short_win > 65:
            return "STRONG_SHORT"
        elif score <= 45 and avg_short_win > 55:
            return "SHORT"
        else:
            return "NEUTRAL"
    
    def _calculate_risk_score(self, crypto: ModuleScore, risk: ModuleScore,
                            king: ModuleScore) -> float:
        """Calculate overall risk score"""
        risk_levels = {
            'low': 25,
            'medium': 50,
            'high': 75,
            'extreme': 90
        }
        
        # Get risk values
        crypto_risk = risk_levels.get(crypto.risk_level, 50)
        risk_risk = risk_levels.get(risk.risk_level, 50)
        king_risk = risk_levels.get(king.risk_level, 50)
        
        # Weighted average with higher weight on highest risk
        max_risk = max(crypto_risk, risk_risk, king_risk)
        avg_risk = np.mean([crypto_risk, risk_risk, king_risk])
        
        # 60% weight on max risk, 40% on average
        return float(max_risk * 0.6 + avg_risk * 0.4)
    
    def _generate_insights(self, symbol: str, score: float,
                         patterns: List[PatternTrigger],
                         market_condition: MarketCondition,
                         crypto: ModuleScore, risk: ModuleScore,
                         king: ModuleScore) -> Tuple[List[str], List[str], List[str]]:
        """Generate insights, warnings, and opportunities"""
        insights = []
        warnings = []
        opportunities = []
        
        # Score-based insights
        if score >= 70:
            insights.append(f"Strong bullish signal with score of {score:.1f}/100")
        elif score <= 30:
            insights.append(f"Strong bearish signal with score of {score:.1f}/100")
        else:
            insights.append(f"Neutral market conditions with score of {score:.1f}/100")
        
        # Pattern insights
        if PatternTrigger.GOLDEN_CROSS in patterns:
            opportunities.append("Golden cross detected - potential uptrend beginning")
        if PatternTrigger.DEATH_CROSS in patterns:
            warnings.append("Death cross detected - potential downtrend beginning")
        if PatternTrigger.LIQUIDATION_CASCADE in patterns:
            warnings.append("Liquidation cascade risk - extreme caution advised")
        if PatternTrigger.SQUEEZE_BREAKOUT in patterns:
            opportunities.append("Volatility squeeze breakout - strong move expected")
        
        # Market condition insights
        if market_condition == MarketCondition.EXTREME_VOLATILITY:
            warnings.append("Extreme volatility - reduce position sizes")
        elif market_condition == MarketCondition.TRENDING_STRONG:
            insights.append("Strong trend detected - follow the momentum")
        
        # Module agreement/disagreement
        scores = [crypto.raw_score, risk.raw_score, king.raw_score]
        if statistics.stdev(scores) < 10:
            insights.append("All modules in strong agreement - high confidence signal")
        elif statistics.stdev(scores) > 25:
            warnings.append("Module disagreement detected - exercise caution")
        
        # Win rate insights
        avg_long = np.mean([crypto.win_rate_long, risk.win_rate_long, king.win_rate_long])
        avg_short = np.mean([crypto.win_rate_short, risk.win_rate_short, king.win_rate_short])
        
        if avg_long > 65:
            opportunities.append(f"High long win rate of {avg_long:.1f}% across all modules")
        if avg_short > 65:
            opportunities.append(f"High short win rate of {avg_short:.1f}% across all modules")
        
        return insights, warnings, opportunities
    
    def _calculate_trading_parameters(self, score: float, risk_score: float,
                                     market_condition: MarketCondition,
                                     position: str) -> Tuple[str, float, List[float]]:
        """Calculate position size, stop loss, and take profit targets"""
        
        # Position sizing based on risk and score
        if risk_score > 70:
            position_size = "0.5-1% of portfolio"
        elif risk_score > 50:
            position_size = "1-2% of portfolio"
        elif score > 70 or score < 30:
            position_size = "2-3% of portfolio"
        else:
            position_size = "1-1.5% of portfolio"
        
        # Stop loss based on market condition and risk
        if market_condition == MarketCondition.EXTREME_VOLATILITY:
            stop_loss = 5.0  # 5%
        elif market_condition == MarketCondition.HIGH_VOLATILITY:
            stop_loss = 4.0  # 4%
        elif risk_score > 70:
            stop_loss = 2.0  # 2%
        else:
            stop_loss = 3.0  # 3%
        
        # Take profit targets based on position strength
        if position in ["STRONG_LONG", "STRONG_SHORT"]:
            take_profits = [3.0, 6.0, 10.0]  # 3%, 6%, 10%
        elif position in ["LONG", "SHORT"]:
            take_profits = [2.0, 4.0, 7.0]   # 2%, 4%, 7%
        else:
            take_profits = [1.5, 3.0, 5.0]  # 1.5%, 3%, 5%
        
        return position_size, stop_loss, take_profits
    
    def _calculate_overall_confidence(self, crypto_conf: float, risk_conf: float,
                                     king_conf: float, pattern_count: int,
                                     market_condition: MarketCondition) -> float:
        """Calculate overall confidence level"""
        # Base confidence from modules
        base_confidence = np.mean([crypto_conf, risk_conf, king_conf])
        
        # Boost confidence if patterns detected
        pattern_boost = min(0.1, pattern_count * 0.02)
        
        # Adjust for market condition
        condition_factors = {
            MarketCondition.NORMAL: 1.0,
            MarketCondition.TRENDING_STRONG: 1.1,
            MarketCondition.LOW_VOLATILITY: 1.05,
            MarketCondition.HIGH_VOLATILITY: 0.95,
            MarketCondition.EXTREME_VOLATILITY: 0.85,
            MarketCondition.UNCERTAIN: 0.80,
            MarketCondition.RANGING: 0.90
        }
        
        condition_factor = condition_factors.get(market_condition, 1.0)
        
        # Calculate final confidence
        confidence = (base_confidence + pattern_boost) * condition_factor
        
        return float(max(0, min(1, confidence)))
    
    def _assess_data_quality(self, crypto: ModuleScore, risk: ModuleScore,
                            king: ModuleScore) -> float:
        """Assess quality of input data"""
        quality_scores = []
        
        # Check data freshness (assuming timestamps available)
        now = datetime.now()
        for score in [crypto, risk, king]:
            age_minutes = (now - score.timestamp).total_seconds() / 60
            if age_minutes < 5:
                quality_scores.append(1.0)
            elif age_minutes < 15:
                quality_scores.append(0.9)
            elif age_minutes < 30:
                quality_scores.append(0.7)
            elif age_minutes < 60:
                quality_scores.append(0.5)
            else:
                quality_scores.append(0.3)
        
        # Check confidence levels
        confidence_quality = np.mean([crypto.confidence, risk.confidence, king.confidence])
        
        # Combined quality score
        return float(np.mean(quality_scores) * 0.7 + confidence_quality * 0.3)
    
    def _update_history(self, symbol: str, score: float, patterns: List[PatternTrigger]):
        """Update historical tracking"""
        # Initialize if needed
        if symbol not in self.score_history:
            self.score_history[symbol] = deque(maxlen=100)
            self.pattern_history[symbol] = {}
        
        # Store score
        self.score_history[symbol].append({
            'score': score,
            'timestamp': datetime.now(),
            'patterns': patterns
        })
        
        # Track pattern occurrences
        for pattern in patterns:
            if pattern not in self.pattern_history[symbol]:
                self.pattern_history[symbol][pattern] = 0
            self.pattern_history[symbol][pattern] += 1
    
    def _create_learning_features(self, symbol: str, crypto_score: ModuleScore,
                                risk_score: ModuleScore, king_score: ModuleScore,
                                market_condition: MarketCondition, 
                                active_patterns: List[PatternTrigger],
                                market_data: Optional[Dict]) -> Dict[str, Any]:
        """Create feature dictionary for machine learning"""
        features = {
            # Module scores
            'crypto_score': crypto_score.raw_score,
            'crypto_confidence': crypto_score.confidence,
            'crypto_win_rate_long': crypto_score.win_rate_long,
            'crypto_win_rate_short': crypto_score.win_rate_short,
            'crypto_risk_level': hash(crypto_score.risk_level) % 100,
            
            'risk_score': risk_score.raw_score,
            'risk_confidence': risk_score.confidence,
            'risk_win_rate_long': risk_score.win_rate_long,
            'risk_win_rate_short': risk_score.win_rate_short,
            'risk_level_risk': hash(risk_score.risk_level) % 100,
            
            'king_score': king_score.raw_score,
            'king_confidence': king_score.confidence,
            'king_win_rate_long': king_score.win_rate_long,
            'king_win_rate_short': king_score.win_rate_short,
            'king_risk_level': hash(king_score.risk_level) % 100,
            
            # Market conditions
            'market_condition': market_condition.value,
            'volatility_index': market_data.get('volatility_index', 0.5) if market_data else 0.5,
            'trend_strength': market_data.get('trend_strength', 0.5) if market_data else 0.5,
            
            # Pattern analysis
            'pattern_count': len(active_patterns),
            'has_golden_cross': PatternTrigger.GOLDEN_CROSS in active_patterns,
            'has_death_cross': PatternTrigger.DEATH_CROSS in active_patterns,
            'has_liquidation_cascade': PatternTrigger.LIQUIDATION_CASCADE in active_patterns,
            'has_volume_breakout': PatternTrigger.VOLUME_BREAKOUT in active_patterns,
            
            # Symbol characteristics
            'symbol_hash': hash(symbol) % 1000,
            
            # Temporal features
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'is_weekend': datetime.now().weekday() >= 5,
            
            # Score agreement
            'score_std': float(np.std([crypto_score.raw_score, risk_score.raw_score, king_score.raw_score])),
            'confidence_avg': float(np.mean([crypto_score.confidence, risk_score.confidence, king_score.confidence])),
            
            # Historical context
            'has_history': symbol in self.score_history,
            'recent_scores_count': len(self.score_history.get(symbol, [])),
        }
        
        # Add historical features if available
        if symbol in self.score_history and len(self.score_history[symbol]) > 0:
            recent_scores = [s['score'] for s in list(self.score_history[symbol])[-10:]]
            features.update({
                'recent_avg_score': float(np.mean(recent_scores)),
                'recent_score_trend': recent_scores[-1] - recent_scores[0] if len(recent_scores) > 1 else 0,
                'score_volatility': float(np.std(recent_scores)) if len(recent_scores) > 1 else 0,
            })
        else:
            features.update({
                'recent_avg_score': 50.0,
                'recent_score_trend': 0.0,
                'score_volatility': 0.0,
            })
        
        return features
    
    async def record_outcome(self, symbol: str, actual_score: float, 
                           outcome_timestamp: Optional[datetime] = None) -> bool:
        """
        Record actual outcome for learning
        
        Args:
            symbol: Trading symbol
            actual_score: The actual score that should have been predicted
            outcome_timestamp: When the outcome occurred
            
        Returns:
            True if outcome was recorded
        """
        if not self.learning_enabled or not learning_system:
            return False
        
        # Find recent predictions for this symbol
        outcomes_recorded = 0
        
        for record in reversed(list(self.learning_history)):
            if record['symbol'] == symbol:
                # Check if this outcome is within reasonable time window
                time_diff = (outcome_timestamp or datetime.now()) - record['timestamp']
                
                if timedelta(minutes=5) <= time_diff <= timedelta(hours=24):
                    # Record the outcome
                    success = await learning_system.record_outcome(
                        record['prediction_id'],
                        actual_score,
                        outcome_timestamp
                    )
                    
                    if success:
                        outcomes_recorded += 1
                        logger.info(f"Recorded outcome for {symbol}: predicted={record['score']:.1f}, actual={actual_score:.1f}")
                        
                        # Only record most recent prediction to avoid duplicates
                        break
        
        return outcomes_recorded > 0
    
    async def get_learning_performance(self) -> Dict[str, Any]:
        """Get learning performance metrics"""
        if not self.learning_enabled or not learning_system:
            return {'learning_enabled': False}
        
        performance = await learning_system.get_agent_performance("MasterScoringAgent")
        insights = await learning_system.get_learning_insights("MasterScoringAgent")
        
        return {
            'learning_enabled': True,
            'performance': performance,
            'insights': insights,
            'predictions_tracked': len(self.learning_history),
            'learning_system_available': True
        }
    
    def get_historical_performance(self, symbol: str) -> Dict[str, Any]:
        """Get historical performance for a symbol"""
        if symbol not in self.score_history:
            return {'error': 'No historical data available'}
        
        history = list(self.score_history[symbol])
        
        if not history:
            return {'error': 'No historical data available'}
        
        scores = [h['score'] for h in history]
        
        return {
            'symbol': symbol,
            'average_score': np.mean(scores),
            'score_std': np.std(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'recent_trend': 'up' if len(scores) > 1 and scores[-1] > scores[-2] else 'down',
            'pattern_frequency': self.pattern_history.get(symbol, {}),
            'data_points': len(scores)
        }
    
    async def generate_master_report(self, final_score: FinalScore,
                                    crypto: ModuleScore, risk: ModuleScore,
                                    king: ModuleScore) -> str:
        """
        Generate comprehensive master report combining all analyses
        """
        report = f"""
# MASTER SCORING REPORT - {final_score.symbol}

## FINAL SCORE: {final_score.final_score:.1f}/100
## POSITION: {final_score.position_recommendation}
## CONFIDENCE: {final_score.confidence_level*100:.1f}%

---

## 🎯 SCORING BREAKDOWN

### Module Contributions:
- **Cryptometer**: {final_score.cryptometer_contribution:.1f} (Weight: {final_score.cryptometer_weight*100:.1f}%)
- **RiskMetric**: {final_score.riskmetric_contribution:.1f} (Weight: {final_score.riskmetric_weight*100:.1f}%)
- **KingFisher**: {final_score.kingfisher_contribution:.1f} (Weight: {final_score.kingfisher_weight*100:.1f}%)

### Pattern Coefficient: {final_score.pattern_coefficient:.2f}x
### Market Condition: {final_score.market_condition.value.replace('_', ' ').title()}

---

## 📈 WIN RATE ANALYSIS

### Long Position Win Rates:
- Cryptometer: {crypto.win_rate_long:.1f}%
- RiskMetric: {risk.win_rate_long:.1f}%
- KingFisher: {king.win_rate_long:.1f}%
- **Average: {np.mean([crypto.win_rate_long, risk.win_rate_long, king.win_rate_long]):.1f}%**

### Short Position Win Rates:
- Cryptometer: {crypto.win_rate_short:.1f}%
- RiskMetric: {risk.win_rate_short:.1f}%
- KingFisher: {king.win_rate_short:.1f}%
- **Average: {np.mean([crypto.win_rate_short, risk.win_rate_short, king.win_rate_short]):.1f}%**

---

## 🎯 ACTIVE PATTERNS

{self._format_patterns(final_score.active_patterns)}

---

## 📊 TRADING PARAMETERS

- **Position Size**: {final_score.suggested_position_size}
- **Stop Loss**: {final_score.stop_loss_percentage:.1f}%
- **Take Profit Targets**: {', '.join([f'{tp:.1f}%' for tp in final_score.take_profit_targets])}
- **Risk Score**: {final_score.risk_score:.1f}/100

---

## 🔍 KEY INSIGHTS

{self._format_list(final_score.key_insights)}

## ⚠️ WARNINGS

{self._format_list(final_score.warnings) if final_score.warnings else '- No warnings'}

## 🎯 OPPORTUNITIES

{self._format_list(final_score.opportunities) if final_score.opportunities else '- No specific opportunities identified'}

---

## 📊 DATA QUALITY

- **Overall Quality**: {final_score.data_quality_score*100:.1f}%
- **Processing Time**: {final_score.processing_time_ms}ms
- **Timestamp**: {final_score.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

---

## 📝 RECOMMENDATION SUMMARY

{self._generate_recommendation_summary(final_score)}

---

*Generated by Master Scoring Agent v2.0*
        """
        
        return report
    
    def _format_patterns(self, patterns: List[PatternTrigger]) -> str:
        """Format pattern list for report"""
        if not patterns:
            return "- No significant patterns detected"
        
        formatted = []
        for pattern in patterns:
            coefficient = self.pattern_coefficients.get(pattern, 1.0)
            impact = "Bullish" if coefficient > 1 else "Bearish"
            percentage = abs((coefficient - 1) * 100)
            formatted.append(f"- **{pattern.value.replace('_', ' ').title()}**: {impact} ({percentage:+.0f}%)")
        
        return "\n".join(formatted)
    
    def _format_list(self, items: List[str]) -> str:
        """Format list items for report"""
        if not items:
            return "- None"
        return "\n".join([f"- {item}" for item in items])
    
    def _generate_recommendation_summary(self, score: FinalScore) -> str:
        """Generate final recommendation summary"""
        if score.position_recommendation == "STRONG_LONG":
            action = "STRONG BUY"
            description = "Excellent opportunity for long positions with high confidence"
        elif score.position_recommendation == "LONG":
            action = "BUY"
            description = "Good opportunity for long positions with moderate confidence"
        elif score.position_recommendation == "STRONG_SHORT":
            action = "STRONG SELL"
            description = "Strong bearish signal, consider short positions"
        elif score.position_recommendation == "SHORT":
            action = "SELL"
            description = "Bearish conditions, consider reducing exposure"
        else:
            action = "HOLD"
            description = "Neutral conditions, wait for clearer signals"
        
        return f"""
**Action: {action}**

{description}

- Final Score: {score.final_score:.1f}/100
- Confidence: {score.confidence_level*100:.1f}%
- Risk Level: {'High' if score.risk_score > 70 else 'Medium' if score.risk_score > 40 else 'Low'}
- Position Size: {score.suggested_position_size}

This recommendation is based on the combined analysis of real-time market data (Cryptometer),
historical patterns (RiskMetric), and liquidation analysis (KingFisher), with dynamic weighting
adjusted for current market conditions and detected patterns.
        """

# Create global instance
master_scoring_agent = MasterScoringAgent()