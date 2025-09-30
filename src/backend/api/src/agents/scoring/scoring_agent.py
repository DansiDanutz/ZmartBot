"""
Zmart Trading Bot Platform - Scoring Agent
Signal aggregation and confidence assessment with dynamic weighting
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class SignalScore:
    """Individual signal score from a source"""
    source: str
    value: float  # 0-100 scale
    confidence: float  # 0-1 scale
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AggregatedScore:
    """Aggregated score from all sources"""
    total_score: float  # 0-100 scale
    confidence: float  # 0-1 scale
    signal_count: int
    sources: List[str]
    breakdown: Dict[str, float]
    timestamp: datetime
    recommendation: str  # BUY/SELL/HOLD

class ScoringAgent:
    """
    Scoring Agent for signal aggregation and scoring
    Combines scores from multiple sources with dynamic weighting
    """
    
    def __init__(self):
        """Initialize the scoring agent"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Scoring Agent initialized")
        
        # Default weights for different sources
        self.default_weights = {
            "cryptometer": 0.5,  # 50% weight
            "kingfisher": 0.3,   # 30% weight
            "riskmetric": 0.2    # 20% weight
        }
        
        # Score history for tracking
        self.score_history: List[AggregatedScore] = []
        self.max_history = 100
        
        # Thresholds for recommendations
        self.thresholds = {
            "strong_buy": 80,
            "buy": 60,
            "hold_high": 40,
            "hold_low": -40,
            "sell": -60,
            "strong_sell": -80
        }
    
    async def calculate_score(
        self,
        symbol: str,
        signals: List[SignalScore],
        weights: Optional[Dict[str, float]] = None
    ) -> AggregatedScore:
        """
        Calculate aggregated score from multiple signals
        
        Args:
            symbol: Trading symbol
            signals: List of signal scores from different sources
            weights: Optional custom weights for sources
            
        Returns:
            AggregatedScore with final score and recommendation
        """
        try:
            if not signals:
                self.logger.warning(f"No signals provided for {symbol}")
                return self._create_neutral_score(symbol)
            
            # Use custom weights or defaults
            active_weights = weights or self.default_weights
            
            # Calculate weighted score
            weighted_sum = 0
            total_weight = 0
            confidence_sum = 0
            breakdown = {}
            sources = []
            
            for signal in signals:
                source_weight = active_weights.get(signal.source.lower(), 0.1)
                
                # Apply confidence adjustment
                adjusted_weight = source_weight * signal.confidence
                
                # Add to weighted sum
                weighted_sum += signal.value * adjusted_weight
                total_weight += adjusted_weight
                confidence_sum += signal.confidence
                
                # Track breakdown
                breakdown[signal.source] = signal.value
                sources.append(signal.source)
            
            # Calculate final score
            if total_weight > 0:
                final_score = weighted_sum / total_weight
                avg_confidence = confidence_sum / len(signals)
            else:
                final_score = 50  # Neutral
                avg_confidence = 0
            
            # Determine recommendation
            recommendation = self._get_recommendation(final_score)
            
            # Create aggregated score
            aggregated = AggregatedScore(
                total_score=final_score,
                confidence=avg_confidence,
                signal_count=len(signals),
                sources=sources,
                breakdown=breakdown,
                timestamp=datetime.now(),
                recommendation=recommendation
            )
            
            # Store in history
            self._update_history(aggregated)
            
            self.logger.info(
                f"Score calculated for {symbol}: {final_score:.2f} "
                f"({recommendation}) with confidence {avg_confidence:.2f}"
            )
            
            return aggregated
            
        except Exception as e:
            self.logger.error(f"Error calculating score for {symbol}: {e}")
            return self._create_neutral_score(symbol)
    
    async def process_signal(
        self,
        source: str,
        symbol: str,
        value: float,
        confidence: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SignalScore:
        """
        Process individual signal from a source
        
        Args:
            source: Signal source name
            symbol: Trading symbol
            value: Signal value (0-100)
            confidence: Confidence level (0-1)
            metadata: Additional signal metadata
            
        Returns:
            SignalScore object
        """
        try:
            # Validate inputs
            value = max(0, min(100, value))  # Clamp to 0-100
            confidence = max(0, min(1, confidence))  # Clamp to 0-1
            
            signal = SignalScore(
                source=source,
                value=value,
                confidence=confidence,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            self.logger.debug(
                f"Processed signal from {source} for {symbol}: "
                f"value={value:.2f}, confidence={confidence:.2f}"
            )
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error processing signal from {source}: {e}")
            raise
    
    def _get_recommendation(self, score: float) -> str:
        """
        Get trading recommendation based on score
        
        Args:
            score: Final aggregated score (0-100)
            
        Returns:
            Recommendation string
        """
        if score >= self.thresholds["strong_buy"]:
            return "STRONG_BUY"
        elif score >= self.thresholds["buy"]:
            return "BUY"
        elif score >= 50:
            return "HOLD_BULLISH"
        elif score >= 40:
            return "HOLD_BEARISH"
        elif score >= 30:
            return "SELL"
        else:
            return "STRONG_SELL"
    
    def _create_neutral_score(self, symbol: str) -> AggregatedScore:  # noqa: ARG002
        """Create a neutral score when no signals available"""
        return AggregatedScore(
            total_score=50,
            confidence=0,
            signal_count=0,
            sources=[],
            breakdown={},
            timestamp=datetime.now(),
            recommendation="HOLD_NEUTRAL"
        )
    
    def _update_history(self, score: AggregatedScore):
        """Update score history with size limit"""
        self.score_history.append(score)
        if len(self.score_history) > self.max_history:
            self.score_history.pop(0)
    
    def get_recent_scores(self, count: int = 10) -> List[AggregatedScore]:
        """Get recent score history"""
        return self.score_history[-count:] if self.score_history else []
    
    def update_weights(self, new_weights: Dict[str, float]):
        """
        Update source weights
        
        Args:
            new_weights: Dictionary of source:weight pairs
        """
        # Validate weights sum to approximately 1.0
        total = sum(new_weights.values())
        if abs(total - 1.0) > 0.01:
            self.logger.warning(f"Weights sum to {total}, normalizing...")
            # Normalize weights
            new_weights = {k: v/total for k, v in new_weights.items()}
        
        self.default_weights.update(new_weights)
        self.logger.info(f"Updated weights: {self.default_weights}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scoring statistics"""
        if not self.score_history:
            return {
                "total_scores": 0,
                "average_score": 0,
                "average_confidence": 0,
                "recommendation_distribution": {}
            }
        
        scores = [s.total_score for s in self.score_history]
        confidences = [s.confidence for s in self.score_history]
        recommendations = [s.recommendation for s in self.score_history]
        
        # Count recommendations
        rec_dist = {}
        for rec in recommendations:
            rec_dist[rec] = rec_dist.get(rec, 0) + 1
        
        return {
            "total_scores": len(self.score_history),
            "average_score": sum(scores) / len(scores),
            "average_confidence": sum(confidences) / len(confidences),
            "recommendation_distribution": rec_dist,
            "current_weights": self.default_weights
        }
    
    async def start(self):
        """Start the scoring agent"""
        self.logger.info("Scoring Agent started")
    
    async def stop(self):
        """Stop the scoring agent"""
        self.logger.info("Scoring Agent stopped")