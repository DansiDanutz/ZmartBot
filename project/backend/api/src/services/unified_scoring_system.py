#!/usr/bin/env python3
"""
Unified Scoring System - ZmartBot Trading Platform
Consolidated scoring system that replaces all scattered scoring components

This system provides:
- Single entry point for all scoring operations
- Clean API for frontend integration
- Unified 100-point scoring scale
- Dynamic weighting based on data quality and market conditions
- Comprehensive scoring history and tracking
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json

# Import existing services
from .calibrated_scoring_service import CalibratedScoringService
from .unified_riskmetric import UnifiedRiskMetric as RiskMetricService
from .kingfisher_service import KingFisherService

logger = logging.getLogger(__name__)

class MarketCondition(Enum):
    """Market condition classifications for dynamic weighting"""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    NORMAL = "normal"

class ScoringSource(Enum):
    """Scoring sources with their base weights"""
    KINGFISHER = "kingfisher"    # Liquidation analysis (30% base)
    CRYPTOMETER = "cryptometer"  # Market analysis (50% base)
    RISKMETRIC = "riskmetric"    # Risk assessment (20% base)

@dataclass
class ComponentScore:
    """Individual component score with metadata"""
    source: ScoringSource
    score: float  # 0-100 scale
    confidence: float  # 0-1 scale
    data_quality: float  # 0-1 scale
    data_age_minutes: float
    metadata: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            'source': self.source.value,
            'score': self.score,
            'confidence': self.confidence,
            'data_quality': self.data_quality,
            'data_age_minutes': self.data_age_minutes,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class DynamicWeights:
    """Dynamic weights for each scoring source"""
    kingfisher_weight: float
    cryptometer_weight: float
    riskmetric_weight: float
    confidence: float
    reasoning: str
    market_condition: MarketCondition
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            'kingfisher': self.kingfisher_weight,
            'cryptometer': self.cryptometer_weight,
            'riskmetric': self.riskmetric_weight,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'market_condition': self.market_condition.value
        }

@dataclass
class ScoringResult:
    """Complete scoring result"""
    symbol: str
    final_score: float  # 0-100 scale
    signal: str  # Buy, Sell, Hold
    confidence: float  # 0-1 scale
    market_condition: MarketCondition
    dynamic_weights: DynamicWeights
    component_scores: Dict[str, ComponentScore]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            'symbol': self.symbol,
            'final_score': self.final_score,
            'signal': self.signal,
            'confidence': self.confidence,
            'market_condition': self.market_condition.value,
            'dynamic_weights': self.dynamic_weights.to_dict(),
            'component_scores': {
                source: score.to_dict() 
                for source, score in self.component_scores.items()
            },
            'timestamp': self.timestamp.isoformat()
        }

class UnifiedScoringSystem:
    """
    Unified scoring system that consolidates all scoring components
    
    Features:
    - Single entry point for all scoring operations
    - Dynamic weighting based on data quality and market conditions
    - 100-point unified scoring scale
    - Comprehensive scoring history and tracking
    - Clean API for frontend integration
    """
    
    def __init__(self):
        """Initialize the unified scoring system"""
        self.calibrated_scoring = CalibratedScoringService()
        self.riskmetric_service = RiskMetricService()
        self.kingfisher_service = KingFisherService()
        
        # Base weights for each source
        self.base_weights = {
            ScoringSource.KINGFISHER: 0.30,    # 30%
            ScoringSource.CRYPTOMETER: 0.50,   # 50%
            ScoringSource.RISKMETRIC: 0.20     # 20%
        }
        
        # Current market condition
        self.current_market_condition = MarketCondition.NORMAL
        
        # Reliability scores for each source (0-1)
        self.reliability_scores = {
            ScoringSource.KINGFISHER: 0.85,
            ScoringSource.CRYPTOMETER: 0.80,
            ScoringSource.RISKMETRIC: 0.90
        }
        
        # Scoring history for tracking
        self.scoring_history: Dict[str, List[ScoringResult]] = {}
        
        logger.info("Unified Scoring System initialized")
    
    async def get_comprehensive_score(self, symbol: str) -> ScoringResult:
        """
        Get comprehensive score for a symbol using all available sources
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            
        Returns:
            ScoringResult with final score and all component data
        """
        try:
            logger.info(f"🎯 Getting comprehensive score for {symbol}")
            
            # Collect scores from all sources
            component_scores = {}
            
            # Get KingFisher score
            kingfisher_score = await self._get_kingfisher_score(symbol)
            if kingfisher_score:
                component_scores['kingfisher'] = kingfisher_score
            
            # Get Cryptometer score
            cryptometer_score = await self._get_cryptometer_score(symbol)
            if cryptometer_score:
                component_scores['cryptometer'] = cryptometer_score
            
            # Get RiskMetric score
            riskmetric_score = await self._get_riskmetric_score(symbol)
            if riskmetric_score:
                component_scores['riskmetric'] = riskmetric_score
            
            if not component_scores:
                raise ValueError(f"No scoring data available for {symbol}")
            
            # Calculate dynamic weights
            dynamic_weights = self._calculate_dynamic_weights(component_scores)
            
            # Calculate final weighted score
            final_score = self._calculate_weighted_score(component_scores, dynamic_weights)
            
            # Determine signal
            signal = self._determine_signal(final_score)
            
            # Calculate overall confidence
            confidence = self._calculate_overall_confidence(component_scores, dynamic_weights)
            
            # Create result
            result = ScoringResult(
                symbol=symbol,
                final_score=final_score,
                signal=signal,
                confidence=confidence,
                market_condition=self.current_market_condition,
                dynamic_weights=dynamic_weights,
                component_scores=component_scores,
                timestamp=datetime.now()
            )
            
            # Store in history
            self._store_scoring_result(result)
            
            logger.info(f"✅ Comprehensive score calculated for {symbol}: {final_score:.1f}/100 ({signal})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting comprehensive score for {symbol}: {str(e)}")
            raise
    
    async def _get_kingfisher_score(self, symbol: str) -> Optional[ComponentScore]:
        """Get KingFisher score with metadata"""
        try:
            # Get KingFisher analysis
            analysis = await self.kingfisher_service.analyze_liquidation_data(symbol)
            
            if analysis and 'score' in analysis:
                # Convert to 100-point scale if needed
                score = min(100.0, analysis['score'] * 4) if analysis['score'] <= 25 else analysis['score']
                
                return ComponentScore(
                    source=ScoringSource.KINGFISHER,
                    score=score,
                    confidence=analysis.get('confidence', 0.85),
                    data_quality=self._assess_kingfisher_data_quality(analysis),
                    data_age_minutes=analysis.get('data_age_minutes', 10.0),
                    metadata={
                        'liquidation_map': analysis.get('liquidation_map', False),
                        'toxic_flow': analysis.get('toxic_flow', False),
                        'ratios': analysis.get('ratios', False),
                        'analysis_type': analysis.get('analysis_type', 'standard')
                    },
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting KingFisher score for {symbol}: {e}")
            return None
    
    async def _get_cryptometer_score(self, symbol: str) -> Optional[ComponentScore]:
        """Get Cryptometer score with metadata"""
        try:
            # Get independent scores from calibrated service
            independent_scores = await self.calibrated_scoring.get_independent_scores(symbol)
            
            if independent_scores:
                available_scores = independent_scores.get_available_scores()
                
                if available_scores:
                    # Calculate average score and convert to 100-point scale
                    total_score = 0
                    component_count = 0
                    
                    for score_obj in available_scores.values():
                        if hasattr(score_obj, 'score'):
                            total_score += score_obj.score
                            component_count += 1
                    
                    if component_count > 0:
                        avg_score = total_score / component_count
                        # Convert to 100-point scale (assuming original was 0-25)
                        score = min(100.0, avg_score * 4)
                        
                        return ComponentScore(
                            source=ScoringSource.CRYPTOMETER,
                            score=score,
                            confidence=0.80,
                            data_quality=self._assess_cryptometer_data_quality(available_scores),
                            data_age_minutes=5.0,
                            metadata={
                                'component_count': component_count,
                                'available_components': list(available_scores.keys()),
                                'short_term': 'short_term' in available_scores,
                                'medium_term': 'medium_term' in available_scores,
                                'long_term': 'long_term' in available_scores
                            },
                            timestamp=datetime.now()
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Cryptometer score for {symbol}: {e}")
            return None
    
    async def _get_riskmetric_score(self, symbol: str) -> Optional[ComponentScore]:
        """Get RiskMetric score with metadata"""
        try:
            # Get RiskMetric assessment
            assessment = await self.riskmetric_service.assess_risk(symbol)
            
            if assessment:
                return ComponentScore(
                    source=ScoringSource.RISKMETRIC,
                    score=assessment.score,  # Already 0-100 scale
                    confidence=assessment.win_rate,
                    data_quality=0.95,  # RiskMetric data is usually very fresh
                    data_age_minutes=2.0,
                    metadata={
                        'risk_band': assessment.risk_band,
                        'risk_value': assessment.risk_value,
                        'signal': assessment.signal,
                        'tradeable': assessment.tradeable,
                        'win_rate': assessment.win_rate
                    },
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting RiskMetric score for {symbol}: {e}")
            return None
    
    def _calculate_dynamic_weights(self, component_scores: Dict[str, ComponentScore]) -> DynamicWeights:
        """Calculate dynamic weights based on data quality and market conditions"""
        
        # Start with base weights
        weights = {
            ScoringSource.KINGFISHER: self.base_weights[ScoringSource.KINGFISHER],
            ScoringSource.CRYPTOMETER: self.base_weights[ScoringSource.CRYPTOMETER],
            ScoringSource.RISKMETRIC: self.base_weights[ScoringSource.RISKMETRIC]
        }
        
        # Adjust weights based on data quality
        for source_name, score_data in component_scores.items():
            source = score_data.source
            quality_factor = score_data.data_quality * self.reliability_scores[source]
            
            # Boost weight for high-quality data
            if quality_factor > 0.8:
                weights[source] *= 1.2
            elif quality_factor < 0.5:
                weights[source] *= 0.8
        
        # Adjust weights based on market conditions
        if self.current_market_condition == MarketCondition.HIGH_VOLATILITY:
            # Boost KingFisher in high volatility
            weights[ScoringSource.KINGFISHER] *= 1.3
            weights[ScoringSource.CRYPTOMETER] *= 0.9
            weights[ScoringSource.RISKMETRIC] *= 0.9
        elif self.current_market_condition == MarketCondition.BULL_MARKET:
            # Boost Cryptometer in bull markets
            weights[ScoringSource.CRYPTOMETER] *= 1.2
            weights[ScoringSource.KINGFISHER] *= 0.9
        elif self.current_market_condition == MarketCondition.BEAR_MARKET:
            # Boost RiskMetric in bear markets
            weights[ScoringSource.RISKMETRIC] *= 1.2
            weights[ScoringSource.CRYPTOMETER] *= 0.9
        
        # Normalize weights to sum to 1.0
        total_weight = sum(weights.values())
        normalized_weights = {source: weight / total_weight for source, weight in weights.items()}
        
        # Calculate confidence in weights
        weight_confidence = min(1.0, sum(
            score_data.confidence * normalized_weights[score_data.source]
            for score_data in component_scores.values()
        ))
        
        return DynamicWeights(
            kingfisher_weight=normalized_weights[ScoringSource.KINGFISHER],
            cryptometer_weight=normalized_weights[ScoringSource.CRYPTOMETER],
            riskmetric_weight=normalized_weights[ScoringSource.RISKMETRIC],
            confidence=weight_confidence,
            reasoning=f"Dynamic weights adjusted for {self.current_market_condition.value} market conditions",
            market_condition=self.current_market_condition
        )
    
    def _calculate_weighted_score(self, component_scores: Dict[str, ComponentScore], weights: DynamicWeights) -> float:
        """Calculate final weighted score"""
        weighted_sum = 0
        
        for score_data in component_scores.values():
            if score_data.source == ScoringSource.KINGFISHER:
                weight = weights.kingfisher_weight
            elif score_data.source == ScoringSource.CRYPTOMETER:
                weight = weights.cryptometer_weight
            elif score_data.source == ScoringSource.RISKMETRIC:
                weight = weights.riskmetric_weight
            else:
                continue
            
            weighted_sum += score_data.score * weight
        
        return round(weighted_sum, 1)
    
    def _determine_signal(self, final_score: float) -> str:
        """Determine trading signal based on final score"""
        if final_score >= 80:
            return "Strong Buy"
        elif final_score >= 70:
            return "Buy"
        elif final_score >= 60:
            return "Weak Buy"
        elif final_score >= 40:
            return "Hold"
        elif final_score >= 30:
            return "Weak Sell"
        elif final_score >= 20:
            return "Sell"
        else:
            return "Strong Sell"
    
    def _calculate_overall_confidence(self, component_scores: Dict[str, ComponentScore], weights: DynamicWeights) -> float:
        """Calculate overall confidence in the scoring result"""
        confidence_sum = 0
        total_weight = 0
        
        for score_data in component_scores.values():
            if score_data.source == ScoringSource.KINGFISHER:
                weight = weights.kingfisher_weight
            elif score_data.source == ScoringSource.CRYPTOMETER:
                weight = weights.cryptometer_weight
            elif score_data.source == ScoringSource.RISKMETRIC:
                weight = weights.riskmetric_weight
            else:
                continue
            
            confidence_sum += score_data.confidence * weight
            total_weight += weight
        
        return round(confidence_sum / total_weight if total_weight > 0 else 0.0, 2)
    
    def _assess_kingfisher_data_quality(self, analysis: Dict[str, Any]) -> float:
        """Assess KingFisher data quality"""
        quality_score = 0.5  # Base score
        
        # Check for required components
        if analysis.get('liquidation_map'):
            quality_score += 0.2
        if analysis.get('toxic_flow'):
            quality_score += 0.2
        if analysis.get('ratios'):
            quality_score += 0.1
        
        # Penalize old data
        data_age = analysis.get('data_age_minutes', 60)
        if data_age > 30:
            quality_score *= 0.8
        elif data_age > 60:
            quality_score *= 0.6
        
        return min(1.0, quality_score)
    
    def _assess_cryptometer_data_quality(self, available_scores: Dict[str, Any]) -> float:
        """Assess Cryptometer data quality"""
        quality_score = 0.3  # Base score
        
        # Reward more components
        component_count = len(available_scores)
        quality_score += min(0.4, component_count * 0.1)
        
        # Reward multi-timeframe data
        if 'short_term' in available_scores:
            quality_score += 0.1
        if 'medium_term' in available_scores:
            quality_score += 0.1
        if 'long_term' in available_scores:
            quality_score += 0.1
        
        return min(1.0, quality_score)
    
    def _store_scoring_result(self, result: ScoringResult):
        """Store scoring result in history"""
        if result.symbol not in self.scoring_history:
            self.scoring_history[result.symbol] = []
        
        self.scoring_history[result.symbol].append(result)
        
        # Keep only last 100 results per symbol
        if len(self.scoring_history[result.symbol]) > 100:
            self.scoring_history[result.symbol] = self.scoring_history[result.symbol][-100:]
    
    def set_market_condition(self, condition: MarketCondition):
        """Set current market condition for dynamic weighting"""
        self.current_market_condition = condition
        logger.info(f"Market condition set to: {condition.value}")
    
    def update_reliability_score(self, source: ScoringSource, score: float):
        """Update reliability score for a scoring source"""
        if 0 <= score <= 1:
            self.reliability_scores[source] = score
            logger.info(f"Reliability score updated for {source.value}: {score}")
        else:
            logger.warning(f"Invalid reliability score: {score} (must be 0-1)")
    
    def get_scoring_history(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get scoring history for a symbol"""
        if symbol in self.scoring_history:
            return [result.to_dict() for result in self.scoring_history[symbol][-limit:]]
        return []
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        return {
            'status': 'healthy',
            'market_condition': self.current_market_condition.value,
            'reliability_scores': {
                source.value: score for source, score in self.reliability_scores.items()
            },
            'base_weights': {
                source.value: weight for source, weight in self.base_weights.items()
            },
            'scoring_history_count': len(self.scoring_history),
            'timestamp': datetime.now().isoformat()
        }

# Global instance for easy access
unified_scoring_system = UnifiedScoringSystem()
