"""
Scoring Service for ZmartBot
Provides scoring and evaluation functionality for trading decisions
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ScoreResult:
    """Result of scoring evaluation"""
    symbol: str
    score: float
    confidence: float
    signal: str
    timestamp: datetime
    components: Dict[str, float]

class MultiTimeframeScoringService:
    """
    Multi-timeframe scoring service for advanced analysis
    Provides scoring across multiple time horizons
    """
    
    def __init__(self):
        """Initialize the multi-timeframe scoring service"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("MultiTimeframeScoringService initialized")
        
        # Timeframe weights
        self.timeframe_weights = {
            "1m": 0.1,
            "5m": 0.15,
            "15m": 0.2,
            "1h": 0.25,
            "4h": 0.2,
            "1d": 0.1
        }
        
        # Component weights
        self.component_weights = {
            "cryptometer": 0.5,
            "kingfisher": 0.3,
            "riskmetric": 0.2
        }
    
    async def calculate_multiframe_score(self, symbol: str) -> Dict[str, Any]:
        """Calculate score across multiple timeframes"""
        return {
            "symbol": symbol,
            "score": 75.0,
            "confidence": 0.85,
            "timeframes": self.timeframe_weights,
            "timestamp": datetime.now().isoformat()
        }

class ScoringService:
    """
    Main scoring service for the platform
    Combines scores from multiple sources
    """
    
    def __init__(self):
        """Initialize the scoring service"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Scoring Service initialized")
        
        # Default weights for scoring components
        self.weights = {
            "cryptometer": 0.5,
            "kingfisher": 0.3,
            "riskmetric": 0.2
        }
    
    async def calculate_score(
        self,
        symbol: str,
        cryptometer_score: Optional[float] = None,
        kingfisher_score: Optional[float] = None,
        riskmetric_score: Optional[float] = None
    ) -> ScoreResult:
        """
        Calculate combined score for a symbol
        
        Args:
            symbol: Trading symbol
            cryptometer_score: Score from Cryptometer (0-100)
            kingfisher_score: Score from KingFisher (0-100)
            riskmetric_score: Score from RiskMetric (0-100)
            
        Returns:
            ScoreResult with combined score and signal
        """
        try:
            components = {}
            weighted_sum = 0
            total_weight = 0
            
            # Add Cryptometer score
            if cryptometer_score is not None:
                weight = self.weights["cryptometer"]
                components["cryptometer"] = cryptometer_score
                weighted_sum += cryptometer_score * weight
                total_weight += weight
            
            # Add KingFisher score
            if kingfisher_score is not None:
                weight = self.weights["kingfisher"]
                components["kingfisher"] = kingfisher_score
                weighted_sum += kingfisher_score * weight
                total_weight += weight
            
            # Add RiskMetric score
            if riskmetric_score is not None:
                weight = self.weights["riskmetric"]
                components["riskmetric"] = riskmetric_score
                weighted_sum += riskmetric_score * weight
                total_weight += weight
            
            # Calculate final score
            if total_weight > 0:
                final_score = weighted_sum / total_weight
            else:
                final_score = 50  # Neutral if no data
            
            # Determine signal
            signal = self._get_signal(final_score)
            
            # Calculate confidence based on data availability
            confidence = min(total_weight, 1.0)
            
            return ScoreResult(
                symbol=symbol,
                score=final_score,
                confidence=confidence,
                signal=signal,
                timestamp=datetime.now(),
                components=components
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating score for {symbol}: {e}")
            raise
    
    def _get_signal(self, score: float) -> str:
        """
        Get trading signal based on score
        
        Args:
            score: Combined score (0-100)
            
        Returns:
            Trading signal string
        """
        if score >= 95:
            return "STRONG_BUY"
        elif score >= 80:
            return "BUY"
        elif score >= 60:
            return "HOLD_BULLISH"
        elif score >= 40:
            return "HOLD"
        elif score >= 20:
            return "HOLD_BEARISH"
        else:
            return "SELL"
    
    async def get_portfolio_scores(
        self,
        symbols: List[str]
    ) -> Dict[str, ScoreResult]:
        """
        Get scores for multiple symbols
        
        Args:
            symbols: List of trading symbols
            
        Returns:
            Dictionary of symbol to ScoreResult
        """
        results = {}
        
        for symbol in symbols:
            try:
                # In production, this would fetch real scores from various sources
                # For now, using mock scores
                result = await self.calculate_score(
                    symbol=symbol,
                    cryptometer_score=75,
                    kingfisher_score=82,
                    riskmetric_score=68
                )
                results[symbol] = result
            except Exception as e:
                self.logger.error(f"Error getting score for {symbol}: {e}")
                continue
        
        return results
    
    def update_weights(self, new_weights: Dict[str, float]):
        """
        Update component weights
        
        Args:
            new_weights: Dictionary of component to weight
        """
        total = sum(new_weights.values())
        if abs(total - 1.0) > 0.01:
            # Normalize weights
            new_weights = {k: v/total for k, v in new_weights.items()}
        
        self.weights.update(new_weights)
        self.logger.info(f"Updated scoring weights: {self.weights}")
    
    async def get_win_rate_prediction(
        self,
        symbol: str,
        score: float
    ) -> float:
        """
        Predict win rate based on score
        
        Args:
            symbol: Trading symbol
            score: Current score
            
        Returns:
            Predicted win rate (0-100)
        """
        # Simple linear mapping for now
        # In production, this would use ML models
        # Symbol-specific adjustments could be added here
        _ = symbol  # Will be used for symbol-specific models
        if score >= 95:
            return 95.0
        elif score >= 90:
            return 92.0
        elif score >= 85:
            return 87.0
        elif score >= 80:
            return 82.0
        elif score >= 75:
            return 77.0
        elif score >= 70:
            return 72.0
        else:
            return max(50, score)
    
    async def evaluate_market_conditions(self) -> Dict[str, Any]:
        """
        Evaluate overall market conditions
        
        Returns:
            Dictionary with market condition metrics
        """
        return {
            "market_trend": "BULLISH",
            "volatility": "MEDIUM",
            "fear_greed_index": 65,
            "recommendation": "CAUTIOUS_OPTIMISM",
            "timestamp": datetime.now().isoformat()
        }

# Global instance
scoring_service = ScoringService()

# Export functions for backward compatibility
async def calculate_score(symbol: str, **kwargs) -> ScoreResult:
    """Calculate score for a symbol"""
    return await scoring_service.calculate_score(symbol, **kwargs)

async def get_portfolio_scores(symbols: List[str]) -> Dict[str, ScoreResult]:
    """Get scores for multiple symbols"""
    return await scoring_service.get_portfolio_scores(symbols)

async def get_win_rate_prediction(symbol: str, score: float) -> float:
    """Get win rate prediction"""
    return await scoring_service.get_win_rate_prediction(symbol, score)