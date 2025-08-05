#!/usr/bin/env python3
"""
Dynamic Scoring Agent - ZmartBot
Intelligently weights KingFisher, Cryptometer, and RiskMetric 100-point win rate scores
Based on data quality, market conditions, and reliability metrics

WIN RATE CORRELATION RULE:
- Score = Win Rate Percentage (80 points = 80% win rate)
- Multi-timeframe analysis: 24h, 7d, 1m
- Each score represents probability of winning a trade
"""

import asyncio
import logging
import math
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .win_rate_scoring_standard import (
    WinRateScoringStandard, 
    MultiTimeframeWinRate, 
    TimeFrame, 
    TradeDirection,
    TradeOpportunity,
    win_rate_standard
)
from .pattern_trigger_system import (
    PatternTriggerSystem,
    PatternSignal,
    PatternAnalysis,
    PatternType,
    PatternRarity,
    pattern_trigger_system
)

logger = logging.getLogger(__name__)

class MarketCondition(Enum):
    """Market condition classifications"""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"

@dataclass
class ScoreData:
    """Individual win rate score data with metadata"""
    score: float  # 0-100 scale (represents win rate percentage)
    confidence: float  # 0-1 scale
    data_age: float  # Minutes since last update
    data_quality: float  # 0-1 scale based on completeness
    reliability: float  # Historical accuracy 0-1 scale
    timestamp: datetime
    
    # Win rate specific data
    timeframe_scores: Optional[Dict[str, float]] = None  # 24h, 7d, 1m win rates
    trade_direction: Optional[str] = None  # long, short, neutral
    opportunity_level: Optional[str] = None  # exceptional, infrequent, good, etc.

@dataclass
class DynamicWeights:
    """Dynamic weights calculated by the agent"""
    kingfisher_weight: float
    cryptometer_weight: float
    riskmetric_weight: float
    confidence: float
    reasoning: str
    timestamp: datetime

@dataclass
class DynamicScoringResult:
    """Result of dynamic win rate scoring calculation"""
    symbol: str
    final_score: float  # 0-100 scale (win rate percentage)
    kingfisher_data: Optional[ScoreData]
    cryptometer_data: Optional[ScoreData]
    riskmetric_data: Optional[ScoreData]
    dynamic_weights: DynamicWeights
    market_condition: MarketCondition
    overall_confidence: float
    signal: str
    timestamp: datetime
    
    # Win rate analysis
    multi_timeframe_analysis: Optional[MultiTimeframeWinRate] = None
    trading_recommendations: Optional[Dict[str, Any]] = None
    win_rate_percentage: Optional[float] = None  # Same as final_score for clarity

class DynamicScoringAgent:
    """
    Dynamic Win Rate Scoring Agent that intelligently weights three 100-point win rate systems:
    - KingFisher: Liquidation analysis win rate predictions
    - Cryptometer: Multi-timeframe market analysis win rates  
    - RiskMetric: Benjamin Cowen risk methodology win rates
    
    WIN RATE CORRELATION RULE:
    - Each score represents win rate percentage (80 points = 80% win rate)
    - Multi-timeframe analysis: 24h, 7d, 1m for each source
    - 95%+ = Exceptional opportunity (All in trade)
    - 90%+ = Infrequent opportunity (High confidence)
    - 80%+ = Good opportunity (Enter trade)
    
    The agent dynamically adjusts weights based on:
    - Data quality and freshness
    - Market conditions
    - Historical accuracy
    - Win rate confidence levels
    """
    
    def __init__(self):
        """Initialize the Dynamic Scoring Agent"""
        self.agent_id = "dynamic_scoring_agent"
        self.status = "stopped"
        
        # Historical performance tracking
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {
            'kingfisher': [],
            'cryptometer': [],
            'riskmetric': []
        }
        
        # Default reliability scores (updated based on performance)
        self.reliability_scores = {
            'kingfisher': 0.85,  # Strong for liquidation analysis
            'cryptometer': 0.80,  # Good for multi-timeframe
            'riskmetric': 0.90   # Excellent for risk assessment
        }
        
        # Market condition detection
        self.current_market_condition = MarketCondition.SIDEWAYS
        
        # Win rate scoring standard
        self.win_rate_standard = win_rate_standard
        
        # Pattern trigger system for rare event detection
        self.pattern_trigger_system = pattern_trigger_system
        
        # Task management
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
        logger.info("Dynamic Win Rate Scoring Agent with Pattern Triggers initialized")
    
    async def start(self):
        """Start the dynamic scoring agent"""
        if self._running:
            logger.warning("Dynamic scoring agent is already running")
            return
        
        self._running = True
        self.status = "running"
        
        # Start background tasks
        self._tasks = [
            asyncio.create_task(self._performance_tracking_loop()),
            asyncio.create_task(self._market_condition_detection_loop()),
            asyncio.create_task(self._reliability_update_loop())
        ]
        
        logger.info("Dynamic scoring agent started")
    
    async def stop(self):
        """Stop the dynamic scoring agent"""
        if not self._running:
            logger.warning("Dynamic scoring agent is not running")
            return
        
        self._running = False
        self.status = "stopped"
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks = []
        
        logger.info("Dynamic scoring agent stopped")
    
    async def calculate_multi_timeframe_win_rate(
        self,
        symbol: str,
        kingfisher_timeframes: Optional[Dict[str, Dict[str, float]]] = None,
        cryptometer_timeframes: Optional[Dict[str, Dict[str, float]]] = None,
        riskmetric_timeframes: Optional[Dict[str, Dict[str, float]]] = None
    ) -> DynamicScoringResult:
        """
        Calculate dynamic weighted win rate score with multi-timeframe analysis
        
        Expected timeframe structure:
        {
            "24h": {"long_win_rate": 85.0, "short_win_rate": 75.0, "confidence": 0.8},
            "7d": {"long_win_rate": 78.0, "short_win_rate": 82.0, "confidence": 0.9},
            "1m": {"long_win_rate": 70.0, "short_win_rate": 88.0, "confidence": 0.85}
        }
        """
        try:
            timestamp = datetime.now()
            
            # Create multi-timeframe analysis for each source
            source_analyses = {}
            
            if kingfisher_timeframes:
                source_analyses['kingfisher'] = self.win_rate_standard.create_multi_timeframe_analysis(
                    f"{symbol}_kingfisher",
                    kingfisher_timeframes.get('24h', {}),
                    kingfisher_timeframes.get('7d', {}),
                    kingfisher_timeframes.get('1m', {})
                )
            
            if cryptometer_timeframes:
                source_analyses['cryptometer'] = self.win_rate_standard.create_multi_timeframe_analysis(
                    f"{symbol}_cryptometer",
                    cryptometer_timeframes.get('24h', {}),
                    cryptometer_timeframes.get('7d', {}),
                    cryptometer_timeframes.get('1m', {})
                )
            
            if riskmetric_timeframes:
                source_analyses['riskmetric'] = self.win_rate_standard.create_multi_timeframe_analysis(
                    f"{symbol}_riskmetric",
                    riskmetric_timeframes.get('24h', {}),
                    riskmetric_timeframes.get('7d', {}),
                    riskmetric_timeframes.get('1m', {})
                )
            
            # Calculate weighted averages for each timeframe
            timeframe_scores = {}
            for tf in ['24h', '7d', '1m']:
                tf_scores = []
                tf_weights = []
                
                for source, analysis in source_analyses.items():
                    if hasattr(analysis, tf.replace('h', '_term').replace('d', '_term').replace('m', '_term')):
                        tf_score_obj = getattr(analysis, tf.replace('h', '_term').replace('d', '_term').replace('m', '_term'))
                        tf_scores.append(tf_score_obj.score)
                        tf_weights.append(self.reliability_scores.get(source, 0.8))
                
                if tf_scores:
                    weighted_score = sum(s * w for s, w in zip(tf_scores, tf_weights)) / sum(tf_weights)
                    timeframe_scores[tf] = weighted_score
            
            # Use best timeframe score as final score
            final_score = max(timeframe_scores.values()) if timeframe_scores else 50.0
            
            # Create combined multi-timeframe analysis
            combined_analysis = self._create_combined_timeframe_analysis(symbol, source_analyses, timeframe_scores)
            
            # Generate trading recommendations
            trading_recommendations = self.win_rate_standard.get_trading_recommendations(combined_analysis)
            
            # Create result
            result = DynamicScoringResult(
                symbol=symbol,
                final_score=final_score,
                kingfisher_data=None,  # Will be populated if needed
                cryptometer_data=None,
                riskmetric_data=None,
                dynamic_weights=DynamicWeights(
                    kingfisher_weight=0.33,
                    cryptometer_weight=0.33,
                    riskmetric_weight=0.34,
                    confidence=0.8,
                    reasoning=f"Multi-timeframe win rate analysis for {symbol}",
                    timestamp=timestamp
                ),
                market_condition=self.current_market_condition,
                overall_confidence=combined_analysis.overall_confidence,
                signal=trading_recommendations['overall_recommendation'],
                timestamp=timestamp,
                multi_timeframe_analysis=combined_analysis,
                trading_recommendations=trading_recommendations,
                win_rate_percentage=final_score
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating multi-timeframe win rate for {symbol}: {e}")
            return self._create_error_result(symbol, str(e))

    async def calculate_dynamic_score(
        self, 
        symbol: str,
        kingfisher_score: Optional[float] = None,
        cryptometer_score: Optional[float] = None,
        riskmetric_score: Optional[float] = None,
        kingfisher_metadata: Optional[Dict[str, Any]] = None,
        cryptometer_metadata: Optional[Dict[str, Any]] = None,
        riskmetric_metadata: Optional[Dict[str, Any]] = None
    ) -> DynamicScoringResult:
        """
        Calculate dynamic weighted score from three 100-point systems
        
        Args:
            symbol: Trading symbol
            kingfisher_score: KingFisher 100-point score
            cryptometer_score: Cryptometer 100-point score  
            riskmetric_score: RiskMetric 100-point score
            *_metadata: Additional metadata for each score
        
        Returns:
            DynamicScoringResult with final 100-point score and analysis
        """
        try:
            timestamp = datetime.now()
            
            # Process individual score data
            kingfisher_data = self._process_score_data(
                'kingfisher', kingfisher_score, kingfisher_metadata, timestamp
            ) if kingfisher_score is not None else None
            
            cryptometer_data = self._process_score_data(
                'cryptometer', cryptometer_score, cryptometer_metadata, timestamp
            ) if cryptometer_score is not None else None
            
            riskmetric_data = self._process_score_data(
                'riskmetric', riskmetric_score, riskmetric_metadata, timestamp
            ) if riskmetric_score is not None else None
            
            # Calculate dynamic weights
            dynamic_weights = await self._calculate_dynamic_weights(
                kingfisher_data, cryptometer_data, riskmetric_data, symbol
            )
            
            # Calculate final weighted score
            final_score = self._calculate_final_score(
                kingfisher_data, cryptometer_data, riskmetric_data, dynamic_weights
            )
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(
                kingfisher_data, cryptometer_data, riskmetric_data, dynamic_weights
            )
            
            # Generate trading signal
            signal = self._generate_trading_signal(final_score, overall_confidence)
            
            # Create result
            result = DynamicScoringResult(
                symbol=symbol,
                final_score=final_score,
                kingfisher_data=kingfisher_data,
                cryptometer_data=cryptometer_data,
                riskmetric_data=riskmetric_data,
                dynamic_weights=dynamic_weights,
                market_condition=self.current_market_condition,
                overall_confidence=overall_confidence,
                signal=signal,
                timestamp=timestamp
            )
            
            # Log the scoring decision
            await self._log_scoring_decision(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating dynamic score for {symbol}: {e}")
            return self._create_error_result(symbol, str(e))
    
    def _process_score_data(
        self, 
        source: str, 
        score: float, 
        metadata: Optional[Dict[str, Any]], 
        timestamp: datetime
    ) -> ScoreData:
        """Process raw score data into ScoreData object"""
        
        # Validate score range
        score = max(0.0, min(100.0, score))
        
        # Extract metadata
        if metadata is None:
            metadata = {}
        
        confidence = metadata.get('confidence', 0.7)
        data_age = metadata.get('data_age_minutes', 5.0)
        
        # Calculate data quality based on completeness
        data_quality = self._calculate_data_quality(metadata, source)
        
        # Get historical reliability
        reliability = self.reliability_scores.get(source, 0.8)
        
        return ScoreData(
            score=score,
            confidence=confidence,
            data_age=data_age,
            data_quality=data_quality,
            reliability=reliability,
            timestamp=timestamp
        )
    
    def _calculate_data_quality(self, metadata: Dict[str, Any], source: str) -> float:
        """Calculate data quality score based on completeness and freshness"""
        quality_score = 1.0
        
        # Check data freshness (penalize old data)
        data_age = metadata.get('data_age_minutes', 5.0)
        if data_age > 60:  # Older than 1 hour
            quality_score *= 0.5
        elif data_age > 30:  # Older than 30 minutes
            quality_score *= 0.8
        
        # Check data completeness based on source
        if source == 'kingfisher':
            required_fields = ['liquidation_map', 'toxic_flow', 'ratios']
            available_fields = sum(1 for field in required_fields if metadata.get(field))
            quality_score *= available_fields / len(required_fields)
            
        elif source == 'cryptometer':
            required_fields = ['short_term', 'medium_term', 'long_term']
            available_fields = sum(1 for field in required_fields if metadata.get(field))
            quality_score *= available_fields / len(required_fields)
            
        elif source == 'riskmetric':
            required_fields = ['risk_band', 'historical_data', 'cowen_score']
            available_fields = sum(1 for field in required_fields if metadata.get(field))
            quality_score *= available_fields / len(required_fields)
        
        return max(0.1, quality_score)  # Minimum quality of 0.1
    
    async def _calculate_dynamic_weights(
        self,
        kingfisher_data: Optional[ScoreData],
        cryptometer_data: Optional[ScoreData],
        riskmetric_data: Optional[ScoreData],
        symbol: str
    ) -> DynamicWeights:
        """Calculate dynamic weights based on data quality, market conditions, and reliability"""
        
        # Initialize base weights
        weights = {'kingfisher': 0.0, 'cryptometer': 0.0, 'riskmetric': 0.0}
        available_sources = []
        
        # Calculate individual source weights
        if kingfisher_data:
            weights['kingfisher'] = self._calculate_source_weight(kingfisher_data, 'kingfisher')
            available_sources.append('kingfisher')
        
        if cryptometer_data:
            weights['cryptometer'] = self._calculate_source_weight(cryptometer_data, 'cryptometer')
            available_sources.append('cryptometer')
        
        if riskmetric_data:
            weights['riskmetric'] = self._calculate_source_weight(riskmetric_data, 'riskmetric')
            available_sources.append('riskmetric')
        
        # Apply market condition adjustments
        weights = self._apply_market_condition_adjustments(weights, available_sources)
        
        # Normalize weights to sum to 1.0
        total_weight = sum(weights.values())
        if total_weight > 0:
            for source in weights:
                weights[source] /= total_weight
        else:
            # Fallback to equal weights if no data
            equal_weight = 1.0 / max(1, len(available_sources))
            for source in available_sources:
                weights[source] = equal_weight
        
        # Calculate confidence in the weighting decision
        weight_confidence = self._calculate_weight_confidence(
            kingfisher_data, cryptometer_data, riskmetric_data
        )
        
        # Generate reasoning
        reasoning = self._generate_weight_reasoning(weights, available_sources)
        
        return DynamicWeights(
            kingfisher_weight=weights['kingfisher'],
            cryptometer_weight=weights['cryptometer'],
            riskmetric_weight=weights['riskmetric'],
            confidence=weight_confidence,
            reasoning=reasoning,
            timestamp=datetime.now()
        )
    
    def _calculate_source_weight(self, score_data: ScoreData, source: str) -> float:
        """Calculate weight for a single source based on its data quality metrics"""
        
        # Base weight from reliability
        weight = score_data.reliability
        
        # Adjust for data quality
        weight *= score_data.data_quality
        
        # Adjust for confidence
        weight *= score_data.confidence
        
        # Adjust for data freshness
        freshness_factor = max(0.1, 1.0 - (score_data.data_age / 120.0))  # Decay over 2 hours
        weight *= freshness_factor
        
        # Source-specific adjustments
        if source == 'kingfisher':
            # KingFisher is most valuable during high volatility
            if self.current_market_condition == MarketCondition.HIGH_VOLATILITY:
                weight *= 1.3
        
        elif source == 'cryptometer':
            # Cryptometer is valuable for trend analysis
            if self.current_market_condition in [MarketCondition.BULL_MARKET, MarketCondition.BEAR_MARKET]:
                weight *= 1.2
        
        elif source == 'riskmetric':
            # RiskMetric is most valuable during uncertain conditions
            if self.current_market_condition == MarketCondition.SIDEWAYS:
                weight *= 1.4
        
        return max(0.0, weight)
    
    def _apply_market_condition_adjustments(
        self, 
        weights: Dict[str, float], 
        available_sources: List[str]
    ) -> Dict[str, float]:
        """Apply market condition specific weight adjustments"""
        
        if self.current_market_condition == MarketCondition.HIGH_VOLATILITY:
            # Favor KingFisher during high volatility
            if 'kingfisher' in available_sources:
                weights['kingfisher'] *= 1.5
        
        elif self.current_market_condition == MarketCondition.BULL_MARKET:
            # Favor Cryptometer during bull markets
            if 'cryptometer' in available_sources:
                weights['cryptometer'] *= 1.3
        
        elif self.current_market_condition == MarketCondition.BEAR_MARKET:
            # Favor RiskMetric during bear markets
            if 'riskmetric' in available_sources:
                weights['riskmetric'] *= 1.4
        
        elif self.current_market_condition == MarketCondition.SIDEWAYS:
            # Balanced approach during sideways markets
            # Slightly favor RiskMetric for risk assessment
            if 'riskmetric' in available_sources:
                weights['riskmetric'] *= 1.1
        
        return weights
    
    def _calculate_final_score(
        self,
        kingfisher_data: Optional[ScoreData],
        cryptometer_data: Optional[ScoreData],
        riskmetric_data: Optional[ScoreData],
        weights: DynamicWeights
    ) -> float:
        """Calculate final weighted score (0-100 scale)"""
        
        final_score = 0.0
        
        if kingfisher_data and weights.kingfisher_weight > 0:
            final_score += kingfisher_data.score * weights.kingfisher_weight
        
        if cryptometer_data and weights.cryptometer_weight > 0:
            final_score += cryptometer_data.score * weights.cryptometer_weight
        
        if riskmetric_data and weights.riskmetric_weight > 0:
            final_score += riskmetric_data.score * weights.riskmetric_weight
        
        return max(0.0, min(100.0, final_score))
    
    def _calculate_overall_confidence(
        self,
        kingfisher_data: Optional[ScoreData],
        cryptometer_data: Optional[ScoreData],
        riskmetric_data: Optional[ScoreData],
        weights: DynamicWeights
    ) -> float:
        """Calculate overall confidence in the final score"""
        
        confidence_components = []
        
        if kingfisher_data and weights.kingfisher_weight > 0:
            component_confidence = (
                kingfisher_data.confidence * 
                kingfisher_data.data_quality * 
                kingfisher_data.reliability *
                weights.kingfisher_weight
            )
            confidence_components.append(component_confidence)
        
        if cryptometer_data and weights.cryptometer_weight > 0:
            component_confidence = (
                cryptometer_data.confidence * 
                cryptometer_data.data_quality * 
                cryptometer_data.reliability *
                weights.cryptometer_weight
            )
            confidence_components.append(component_confidence)
        
        if riskmetric_data and weights.riskmetric_weight > 0:
            component_confidence = (
                riskmetric_data.confidence * 
                riskmetric_data.data_quality * 
                riskmetric_data.reliability *
                weights.riskmetric_weight
            )
            confidence_components.append(component_confidence)
        
        if confidence_components:
            # Weighted average of component confidences
            overall_confidence = sum(confidence_components)
            # Factor in weight confidence
            overall_confidence *= weights.confidence
            return max(0.0, min(1.0, overall_confidence))
        
        return 0.0
    
    def _calculate_weight_confidence(
        self,
        kingfisher_data: Optional[ScoreData],
        cryptometer_data: Optional[ScoreData],
        riskmetric_data: Optional[ScoreData]
    ) -> float:
        """Calculate confidence in the weight assignment"""
        
        available_count = sum(1 for data in [kingfisher_data, cryptometer_data, riskmetric_data] if data)
        
        if available_count == 0:
            return 0.0
        elif available_count == 1:
            return 0.6  # Low confidence with only one source
        elif available_count == 2:
            return 0.8  # Good confidence with two sources
        else:
            return 0.95  # High confidence with all three sources
    
    def _generate_weight_reasoning(
        self, 
        weights: Dict[str, float], 
        available_sources: List[str]
    ) -> str:
        """Generate human-readable reasoning for weight assignment"""
        
        reasoning_parts = []
        
        # Identify dominant source
        max_weight = max(weights.values()) if weights else 0
        dominant_source = None
        for source, weight in weights.items():
            if weight == max_weight and weight > 0:
                dominant_source = source
                break
        
        if dominant_source:
            reasoning_parts.append(f"{dominant_source.title()} weighted highest ({weights[dominant_source]:.2f})")
            
            # Explain why
            if dominant_source == 'kingfisher':
                if self.current_market_condition == MarketCondition.HIGH_VOLATILITY:
                    reasoning_parts.append("due to high market volatility favoring liquidation analysis")
                else:
                    reasoning_parts.append("due to high data quality and reliability")
            
            elif dominant_source == 'cryptometer':
                if self.current_market_condition in [MarketCondition.BULL_MARKET, MarketCondition.BEAR_MARKET]:
                    reasoning_parts.append(f"due to {self.current_market_condition.value} conditions favoring trend analysis")
                else:
                    reasoning_parts.append("due to comprehensive multi-timeframe analysis")
            
            elif dominant_source == 'riskmetric':
                if self.current_market_condition == MarketCondition.SIDEWAYS:
                    reasoning_parts.append("due to sideways market favoring risk assessment")
                else:
                    reasoning_parts.append("due to superior historical accuracy")
        
        # Market condition context
        reasoning_parts.append(f"Market condition: {self.current_market_condition.value}")
        
        # Data availability
        reasoning_parts.append(f"Available sources: {len(available_sources)}/3")
        
        return "; ".join(reasoning_parts)
    
    def _generate_trading_signal(self, score: float, confidence: float) -> str:
        """Generate trading signal based on score and confidence"""
        
        # Adjust thresholds based on confidence
        confidence_multiplier = max(0.5, confidence)
        
        if score >= 80 * confidence_multiplier:
            return "Strong Buy"
        elif score >= 65 * confidence_multiplier:
            return "Buy"
        elif score >= 55 * confidence_multiplier:
            return "Weak Buy"
        elif score >= 45:
            return "Hold"
        elif score >= 35:
            return "Weak Sell"
        elif score >= 20:
            return "Sell"
        else:
            return "Strong Sell"
    
    def _create_error_result(self, symbol: str, error_message: str) -> DynamicScoringResult:
        """Create error result when scoring fails"""
        return DynamicScoringResult(
            symbol=symbol,
            final_score=50.0,  # Neutral score
            kingfisher_data=None,
            cryptometer_data=None,
            riskmetric_data=None,
            dynamic_weights=DynamicWeights(
                kingfisher_weight=0.33,
                cryptometer_weight=0.33,
                riskmetric_weight=0.34,
                confidence=0.0,
                reasoning=f"Error occurred: {error_message}",
                timestamp=datetime.now()
            ),
            market_condition=self.current_market_condition,
            overall_confidence=0.0,
            signal="Hold",
            timestamp=datetime.now()
        )
    
    async def _log_scoring_decision(self, result: DynamicScoringResult):
        """Log the scoring decision for analysis and debugging"""
        logger.info(
            f"Dynamic Score for {result.symbol}: {result.final_score:.2f} "
            f"(KF: {result.dynamic_weights.kingfisher_weight:.2f}, "
            f"CM: {result.dynamic_weights.cryptometer_weight:.2f}, "
            f"RM: {result.dynamic_weights.riskmetric_weight:.2f}) "
            f"Signal: {result.signal}, Confidence: {result.overall_confidence:.2f}"
        )
    
    async def _performance_tracking_loop(self):
        """Background task to track performance of each scoring source"""
        while self._running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                # TODO: Implement performance tracking logic
                # This would analyze historical accuracy and update reliability scores
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance tracking loop: {e}")
    
    async def _market_condition_detection_loop(self):
        """Background task to detect current market conditions"""
        while self._running:
            try:
                await asyncio.sleep(60)  # Every minute
                # TODO: Implement market condition detection
                # This would analyze market data to determine current conditions
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in market condition detection loop: {e}")
    
    async def _reliability_update_loop(self):
        """Background task to update reliability scores based on performance"""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Every hour
                # TODO: Implement reliability score updates
                # This would adjust reliability scores based on recent performance
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in reliability update loop: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "market_condition": self.current_market_condition.value,
            "reliability_scores": self.reliability_scores,
            "performance_history_size": {
                source: len(history) 
                for source, history in self.performance_history.items()
            },
            "last_updated": datetime.now().isoformat()
        }
    
    async def update_reliability_score(self, source: str, new_score: float):
        """Manually update reliability score for a source"""
        if source in self.reliability_scores:
            old_score = self.reliability_scores[source]
            self.reliability_scores[source] = max(0.0, min(1.0, new_score))
            logger.info(f"Updated {source} reliability: {old_score:.3f} -> {new_score:.3f}")
    
    async def set_market_condition(self, condition: MarketCondition):
        """Manually set market condition"""
        old_condition = self.current_market_condition
        self.current_market_condition = condition
        logger.info(f"Market condition updated: {old_condition.value} -> {condition.value}")
    
    def _create_combined_timeframe_analysis(
        self, 
        symbol: str, 
        source_analyses: Dict[str, MultiTimeframeWinRate], 
        timeframe_scores: Dict[str, float]
    ) -> MultiTimeframeWinRate:
        """Create combined multi-timeframe analysis from all sources"""
        
        # Create combined timeframe scores
        short_term_data = {
            'long_win_rate': timeframe_scores.get('24h', 50.0),
            'short_win_rate': timeframe_scores.get('24h', 50.0),
            'confidence': 0.8
        }
        
        medium_term_data = {
            'long_win_rate': timeframe_scores.get('7d', 50.0),
            'short_win_rate': timeframe_scores.get('7d', 50.0),
            'confidence': 0.8
        }
        
        long_term_data = {
            'long_win_rate': timeframe_scores.get('1m', 50.0),
            'short_win_rate': timeframe_scores.get('1m', 50.0),
            'confidence': 0.8
        }
        
        return self.win_rate_standard.create_multi_timeframe_analysis(
            symbol,
            short_term_data,
            medium_term_data,
            long_term_data
        )
    
    async def calculate_pattern_based_score(
        self,
        symbol: str,
        kingfisher_data: Optional[Dict[str, Any]] = None,
        cryptometer_data: Optional[Dict[str, Any]] = None,
        riskmetric_data: Optional[Dict[str, Any]] = None,
        current_price: Optional[float] = None,
        historical_prices: Optional[List[Dict[str, Any]]] = None
    ) -> DynamicScoringResult:
        """
        Calculate score using pattern-based triggers and rare event detection
        
        PATTERN-BASED TRIGGER RULES:
        1. Big liquidation clusters trigger KingFisher weight boost
        2. RiskMetric rare bands (0-0.25, 0.75-1) trigger RiskMetric weight boost  
        3. Technical rare patterns (golden cross, etc.) trigger Cryptometer weight boost
        4. Historical pattern matching with 80%+ win rate triggers trade entry
        5. Self-learning from historical data and pattern success rates
        """
        try:
            timestamp = datetime.now()
            logger.info(f"🎯 Starting pattern-based scoring for {symbol}")
            
            # Analyze patterns from all agents
            pattern_analysis = await self.pattern_trigger_system.analyze_patterns(
                symbol=symbol,
                kingfisher_data=kingfisher_data,
                cryptometer_data=cryptometer_data,
                riskmetric_data=riskmetric_data,
                current_price=current_price,
                historical_prices=historical_prices
            )
            
            # Extract individual scores with pattern adjustments
            kingfisher_score = self._extract_pattern_adjusted_score(
                kingfisher_data, pattern_analysis.kingfisher_patterns, 'kingfisher'
            )
            
            cryptometer_score = self._extract_pattern_adjusted_score(
                cryptometer_data, pattern_analysis.cryptometer_patterns, 'cryptometer'
            )
            
            riskmetric_score = self._extract_pattern_adjusted_score(
                riskmetric_data, pattern_analysis.riskmetric_patterns, 'riskmetric'
            )
            
            # Apply pattern-based weight adjustments
            base_weights = self._calculate_base_weights(
                kingfisher_score, cryptometer_score, riskmetric_score
            )
            
            # Apply pattern trigger weight adjustments
            adjusted_weights = self._apply_pattern_weight_adjustments(
                base_weights, pattern_analysis.weight_adjustments
            )
            
            # Calculate final score with pattern boosts
            final_score = self._calculate_pattern_weighted_score(
                kingfisher_score, cryptometer_score, riskmetric_score, adjusted_weights
            )
            
            # Apply pattern confluence bonus
            if len(pattern_analysis.combined_signals) > 0:
                confluence_bonus = min(len(pattern_analysis.combined_signals) * 2.0, 8.0)
                final_score = min(final_score + confluence_bonus, 95.0)
                logger.info(f"🎯 Pattern confluence bonus applied: +{confluence_bonus:.1f} points")
            
            # Generate signal based on pattern analysis
            signal = self._generate_pattern_based_signal(pattern_analysis, final_score)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_pattern_confidence(pattern_analysis, adjusted_weights)
            
            # Create multi-timeframe analysis if we have enough patterns
            multi_timeframe_analysis = None
            if pattern_analysis.overall_trigger:
                multi_timeframe_analysis = self._create_pattern_timeframe_analysis(
                    symbol, pattern_analysis
                )
            
            # Generate trading recommendations
            trading_recommendations = self._generate_pattern_trading_recommendations(
                pattern_analysis, final_score, signal
            )
            
            # Create result
            result = DynamicScoringResult(
                symbol=symbol,
                final_score=final_score,
                kingfisher_data=self._create_score_data(
                    kingfisher_score, kingfisher_data, pattern_analysis.kingfisher_patterns
                ),
                cryptometer_data=self._create_score_data(
                    cryptometer_score, cryptometer_data, pattern_analysis.cryptometer_patterns
                ),
                riskmetric_data=self._create_score_data(
                    riskmetric_score, riskmetric_data, pattern_analysis.riskmetric_patterns
                ),
                dynamic_weights=DynamicWeights(
                    kingfisher_weight=adjusted_weights['kingfisher'],
                    cryptometer_weight=adjusted_weights['cryptometer'],
                    riskmetric_weight=adjusted_weights['riskmetric'],
                    confidence=overall_confidence,
                    reasoning=self._generate_pattern_reasoning(pattern_analysis, adjusted_weights),
                    timestamp=timestamp
                ),
                market_condition=self.current_market_condition,
                overall_confidence=overall_confidence,
                signal=signal,
                timestamp=timestamp,
                multi_timeframe_analysis=multi_timeframe_analysis,
                trading_recommendations=trading_recommendations,
                win_rate_percentage=final_score
            )
            
            logger.info(f"✅ Pattern-based scoring complete for {symbol}: {final_score:.1f}% win rate, Signal: {signal}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in pattern-based scoring for {symbol}: {e}")
            return self._create_error_result(symbol, str(e))
    
    def _extract_pattern_adjusted_score(
        self, 
        agent_data: Optional[Dict[str, Any]], 
        patterns: List[PatternSignal], 
        agent_name: str
    ) -> float:
        """Extract score from agent data and adjust based on patterns"""
        
        # Get base score
        base_score = 50.0  # Default neutral score
        if agent_data:
            base_score = agent_data.get('win_rate', agent_data.get('score', 50.0))
        
        # Apply pattern adjustments
        pattern_boost = 0.0
        for pattern in patterns:
            if pattern.rarity in [PatternRarity.RARE, PatternRarity.EXCEPTIONAL]:
                boost = (pattern.win_rate_prediction - base_score) * 0.3  # 30% of the difference
                pattern_boost += max(boost, 0)  # Only positive boosts
                logger.info(f"🎯 {agent_name} pattern boost: +{boost:.1f} from {pattern.pattern_type.value}")
        
        adjusted_score = min(base_score + pattern_boost, 95.0)
        return adjusted_score
    
    def _apply_pattern_weight_adjustments(
        self, 
        base_weights: Dict[str, float], 
        pattern_adjustments: Dict[str, float]
    ) -> Dict[str, float]:
        """Apply pattern-based weight adjustments"""
        
        adjusted_weights = {}
        for agent, base_weight in base_weights.items():
            pattern_multiplier = pattern_adjustments.get(agent, 1.0)
            adjusted_weights[agent] = base_weight * pattern_multiplier
        
        # Normalize weights
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            for agent in adjusted_weights:
                adjusted_weights[agent] /= total_weight
        
        return adjusted_weights
    
    def _calculate_pattern_weighted_score(
        self,
        kingfisher_score: float,
        cryptometer_score: float,
        riskmetric_score: float,
        weights: Dict[str, float]
    ) -> float:
        """Calculate weighted score with pattern adjustments"""
        
        weighted_score = (
            kingfisher_score * weights.get('kingfisher', 0.33) +
            cryptometer_score * weights.get('cryptometer', 0.33) +
            riskmetric_score * weights.get('riskmetric', 0.34)
        )
        
        return min(weighted_score, 95.0)
    
    def _generate_pattern_based_signal(
        self, 
        pattern_analysis: PatternAnalysis, 
        final_score: float
    ) -> str:
        """Generate trading signal based on pattern analysis and score"""
        
        if pattern_analysis.overall_trigger and final_score >= 90.0:
            return "STRONG_LONG" if self._get_dominant_direction(pattern_analysis) == "long" else "STRONG_SHORT"
        elif pattern_analysis.overall_trigger and final_score >= 80.0:
            return "LONG" if self._get_dominant_direction(pattern_analysis) == "long" else "SHORT"
        elif final_score >= 75.0:
            return "WEAK_LONG" if self._get_dominant_direction(pattern_analysis) == "long" else "WEAK_SHORT"
        elif final_score <= 40.0:
            return "STRONG_SELL" if self._get_dominant_direction(pattern_analysis) == "short" else "STRONG_BUY"
        else:
            return "HOLD"
    
    def _get_dominant_direction(self, pattern_analysis: PatternAnalysis) -> str:
        """Get dominant direction from pattern analysis"""
        
        all_patterns = (
            pattern_analysis.kingfisher_patterns + 
            pattern_analysis.cryptometer_patterns + 
            pattern_analysis.riskmetric_patterns +
            pattern_analysis.combined_signals
        )
        
        long_weight = sum(p.confidence for p in all_patterns if p.direction == "long")
        short_weight = sum(p.confidence for p in all_patterns if p.direction == "short")
        
        return "long" if long_weight > short_weight else "short"
    
    def _calculate_pattern_confidence(
        self, 
        pattern_analysis: PatternAnalysis, 
        weights: Dict[str, float]
    ) -> float:
        """Calculate overall confidence based on patterns and weights"""
        
        # Base confidence from pattern analysis
        pattern_confidence = 0.7  # Default
        
        if pattern_analysis.combined_signals:
            # Higher confidence with combined signals
            avg_pattern_confidence = sum(p.confidence for p in pattern_analysis.combined_signals) / len(pattern_analysis.combined_signals)
            pattern_confidence = min(avg_pattern_confidence + 0.1, 0.95)
        
        # Weight confidence (how balanced are the weights)
        weight_values = list(weights.values())
        weight_balance = 1.0 - float(np.std(weight_values)) if len(weight_values) > 1 else 0.8
        
        return min(pattern_confidence * weight_balance, 0.95)
    
    def _calculate_base_weights(
        self,
        kingfisher_score: float,
        cryptometer_score: float,
        riskmetric_score: float
    ) -> Dict[str, float]:
        """Calculate base weights for the three agents"""
        # Simple equal weighting as base
        return {
            'kingfisher': 0.33,
            'cryptometer': 0.33,
            'riskmetric': 0.34
        }
    
    def _create_pattern_timeframe_analysis(
        self,
        symbol: str,
        pattern_analysis: PatternAnalysis
    ) -> MultiTimeframeWinRate:
        """Create multi-timeframe analysis from pattern analysis"""
        # Extract timeframe data from pattern analysis
        short_term_data = {
            'long_win_rate': 50.0,
            'short_win_rate': 50.0,
            'confidence': 0.5
        }
        medium_term_data = {
            'long_win_rate': 50.0,
            'short_win_rate': 50.0,
            'confidence': 0.5
        }
        long_term_data = {
            'long_win_rate': 50.0,
            'short_win_rate': 50.0,
            'confidence': 0.5
        }
        
        # Update with pattern analysis data if available
        if pattern_analysis.overall_win_rate > 0:
            win_rate = pattern_analysis.overall_win_rate
            short_term_data['long_win_rate'] = win_rate
            short_term_data['short_win_rate'] = win_rate
            medium_term_data['long_win_rate'] = win_rate
            medium_term_data['short_win_rate'] = win_rate
            long_term_data['long_win_rate'] = win_rate
            long_term_data['short_win_rate'] = win_rate
        
        return self.win_rate_standard.create_multi_timeframe_analysis(
            symbol,
            short_term_data,
            medium_term_data,
            long_term_data
        )
    
    def _generate_pattern_trading_recommendations(
        self,
        pattern_analysis: PatternAnalysis,
        final_score: float,
        signal: str
    ) -> Dict[str, Any]:
        """Generate trading recommendations based on pattern analysis"""
        recommendations = {
            'action': signal,
            'confidence': pattern_analysis.overall_win_rate / 100.0,
            'patterns_detected': len(pattern_analysis.kingfisher_patterns + 
                                   pattern_analysis.cryptometer_patterns + 
                                   pattern_analysis.riskmetric_patterns),
            'rare_patterns': len([p for p in pattern_analysis.kingfisher_patterns + 
                                pattern_analysis.cryptometer_patterns + 
                                pattern_analysis.riskmetric_patterns
                                if p.rarity in ['rare', 'exceptional']]),
            'reasoning': f"Pattern analysis shows {pattern_analysis.overall_win_rate:.1f}% win rate with {len(pattern_analysis.combined_signals)} combined signals"
        }
        
        # Add opportunity level
        if final_score >= 95.0:
            recommendations['opportunity_level'] = 'exceptional'
            recommendations['position_size'] = '100%'
        elif final_score >= 90.0:
            recommendations['opportunity_level'] = 'infrequent'
            recommendations['position_size'] = '70%'
        elif final_score >= 80.0:
            recommendations['opportunity_level'] = 'good'
            recommendations['position_size'] = '70%'
        else:
            recommendations['opportunity_level'] = 'moderate'
            recommendations['position_size'] = '40%'
        
        return recommendations
    
    def _create_score_data(
        self,
        score: float,
        agent_data: Optional[Dict[str, Any]],
        patterns: List[PatternSignal]
    ) -> ScoreData:
        """Create ScoreData from agent data and patterns"""
        timestamp = datetime.now()
        
        # Extract metadata from agent data
        metadata = agent_data or {}
        confidence = metadata.get('confidence', 0.7)
        data_age = metadata.get('data_age', 5.0)  # 5 minutes default
        data_quality = metadata.get('data_quality', 0.8)
        reliability = metadata.get('reliability', 0.75)
        
        # Create timeframe scores if available
        timeframe_scores = None
        if 'timeframes' in metadata:
            timeframe_scores = {
                '24h': metadata['timeframes'].get('24h', {}).get('long_win_rate', score),
                '7d': metadata['timeframes'].get('7d', {}).get('long_win_rate', score),
                '1m': metadata['timeframes'].get('1m', {}).get('long_win_rate', score)
            }
        
        # Determine trade direction from patterns
        trade_direction = 'neutral'
        if patterns:
            long_patterns = [p for p in patterns if p.direction == 'long']
            short_patterns = [p for p in patterns if p.direction == 'short']
            if len(long_patterns) > len(short_patterns):
                trade_direction = 'long'
            elif len(short_patterns) > len(long_patterns):
                trade_direction = 'short'
        
        return ScoreData(
            score=score,
            confidence=confidence,
            data_age=data_age,
            data_quality=data_quality,
            reliability=reliability,
            timestamp=timestamp,
            timeframe_scores=timeframe_scores,
            trade_direction=trade_direction,
            opportunity_level=self._classify_opportunity(score)
        )
    
    def _classify_opportunity(self, score: float) -> str:
        """Classify opportunity based on win rate score"""
        score_float = float(score)  # Ensure it's a float
        if score_float >= 95.0:
            return "exceptional"
        elif score_float >= 90.0:
            return "infrequent"
        elif score_float >= 80.0:
            return "good"
        elif score_float >= 70.0:
            return "moderate"
        elif score_float >= 60.0:
            return "weak"
        else:
            return "avoid"
    
    def _generate_pattern_reasoning(
        self, 
        pattern_analysis: PatternAnalysis, 
        weights: Dict[str, float]
    ) -> str:
        """Generate reasoning for pattern-based weight adjustments"""
        
        reasoning_parts = []
        
        # Weight adjustments
        for agent, weight in weights.items():
            if weight > 0.4:  # Significantly boosted
                reasoning_parts.append(f"{agent.title()} weight boosted to {weight:.2f}")
        
        # Pattern triggers
        rare_patterns = []
        for patterns in [pattern_analysis.kingfisher_patterns, pattern_analysis.cryptometer_patterns, pattern_analysis.riskmetric_patterns]:
            for pattern in patterns:
                if pattern.rarity in [PatternRarity.RARE, PatternRarity.EXCEPTIONAL]:
                    rare_patterns.append(f"{pattern.pattern_type.value} ({pattern.rarity.value})")
        
        if rare_patterns:
            reasoning_parts.append(f"Rare patterns detected: {', '.join(rare_patterns)}")
        
        # Combined signals
        if pattern_analysis.combined_signals:
            reasoning_parts.append(f"{len(pattern_analysis.combined_signals)} combined signals detected")
        
        # Overall trigger
        if pattern_analysis.overall_trigger:
            reasoning_parts.append(f"Pattern trigger activated (win rate: {pattern_analysis.overall_win_rate:.1f}%)")
        
        return ". ".join(reasoning_parts) if reasoning_parts else "Standard dynamic weighting applied"