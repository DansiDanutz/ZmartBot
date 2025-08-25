#!/usr/bin/env python3
"""
Unified Signal Center - Complete Integration Hub
Integrates all signal sources: Cryptometer, KingFisher, Sentiment (Grok-X), RiskMetric, and more
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

# Import all signal sources
from src.services.signal_center import SignalCenterService, SignalDirection, SignalStrength
from src.services.sentiment_scoring_service import sentiment_scoring_service
from src.services.cryptometer_service import MultiTimeframeCryptometerSystem
from src.services.kingfisher_service import KingFisherService
from src.services.unified_riskmetric import unified_riskmetric as enhanced_riskmetric_service
from src.services.calibrated_scoring_service import CalibratedScoringService

logger = logging.getLogger(__name__)

class SignalSource(Enum):
    """All available signal sources"""
    CRYPTOMETER = "cryptometer"
    KINGFISHER = "kingfisher"
    SENTIMENT = "sentiment"
    RISKMETRIC = "riskmetric"
    AI_ANALYSIS = "ai_analysis"
    TECHNICAL = "technical"
    BLOCKCHAIN = "blockchain"
    BINANCE = "binance"
    KUCOIN = "kucoin"

@dataclass
class UnifiedSignal:
    """Unified signal structure from all sources"""
    symbol: str
    timestamp: datetime
    source: SignalSource
    direction: SignalDirection
    strength: float  # 0-100
    confidence: float  # 0-100
    score: float  # Component score contribution
    weight: float  # Weight in overall system
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source.value,
            'direction': self.direction.value if isinstance(self.direction, Enum) else self.direction,
            'strength': self.strength,
            'confidence': self.confidence,
            'score': self.score,
            'weight': self.weight,
            'metadata': self.metadata
        }

@dataclass
class AggregatedSignal:
    """Aggregated signal from all sources"""
    symbol: str
    timestamp: datetime
    total_score: float  # 0-100
    direction: str
    confidence: float
    signals: List[UnifiedSignal]
    components: Dict[str, float]
    recommendation: str
    risk_level: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'total_score': self.total_score,
            'direction': self.direction,
            'confidence': self.confidence,
            'signals': [s.to_dict() for s in self.signals],
            'components': self.components,
            'recommendation': self.recommendation,
            'risk_level': self.risk_level
        }

class UnifiedSignalCenter:
    """Unified Signal Center that integrates all signal sources"""
    
    # Weight distribution for each source (total = 100)
    SOURCE_WEIGHTS = {
        SignalSource.CRYPTOMETER: 30,  # 30% weight
        SignalSource.KINGFISHER: 20,   # 20% weight
        SignalSource.SENTIMENT: 15,    # 15% weight (Grok-X)
        SignalSource.RISKMETRIC: 15,   # 15% weight
        SignalSource.AI_ANALYSIS: 10,  # 10% weight
        SignalSource.TECHNICAL: 5,     # 5% weight
        SignalSource.BLOCKCHAIN: 3,    # 3% weight
        SignalSource.BINANCE: 1,       # 1% weight
        SignalSource.KUCOIN: 1         # 1% weight
    }
    
    def __init__(self):
        """Initialize the unified signal center"""
        self.signal_center = SignalCenterService()
        self.cryptometer = MultiTimeframeCryptometerSystem()
        self.kingfisher = KingFisherService()
        self.calibrated_scoring = CalibratedScoringService()
        
        # Cache for aggregated signals
        self.aggregated_cache = {}
        self.cache_duration = timedelta(minutes=5)
        
        logger.info("Unified Signal Center initialized with all modules")
    
    async def get_all_signals(self, symbol: str) -> AggregatedSignal:
        """
        Get all signals for a symbol from all sources
        
        Args:
            symbol: Trading symbol
            
        Returns:
            AggregatedSignal with all source signals
        """
        # Check cache
        cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H')}"
        if cache_key in self.aggregated_cache:
            cached = self.aggregated_cache[cache_key]
            if datetime.now() - cached['timestamp'] < self.cache_duration:
                return cached['signal']
        
        try:
            # Gather signals from all sources in parallel
            signals = await self._gather_all_signals(symbol)
            
            # Aggregate signals
            aggregated = self._aggregate_signals(symbol, signals)
            
            # Cache the result
            self.aggregated_cache[cache_key] = {
                'signal': aggregated,
                'timestamp': datetime.now()
            }
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Error getting all signals for {symbol}: {e}")
            return self._get_default_aggregated_signal(symbol)
    
    async def _gather_all_signals(self, symbol: str) -> List[UnifiedSignal]:
        """Gather signals from all available sources"""
        signals = []
        
        # Create tasks for all signal sources
        tasks = [
            self._get_cryptometer_signal(symbol),
            self._get_kingfisher_signal(symbol),
            self._get_sentiment_signal(symbol),
            self._get_riskmetric_signal(symbol),
            self._get_ai_analysis_signal(symbol),
            self._get_technical_signal(symbol)
        ]
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Signal gathering error: {result}")
                continue
            if result:
                if isinstance(result, list):
                    signals.extend(result)
                else:
                    signals.append(result)
        
        return signals
    
    async def _get_cryptometer_signal(self, symbol: str) -> Optional[UnifiedSignal]:
        """Get signal from Cryptometer"""
        try:
            # Get Cryptometer analysis
            analysis = await self.cryptometer.analyze_multi_timeframe_symbol(symbol)
            
            if not analysis:
                return None
            
            # Convert to unified signal
            direction = self._convert_action_to_direction(analysis.get('action', 'HOLD'))
            
            return UnifiedSignal(
                symbol=symbol,
                timestamp=datetime.now(),
                source=SignalSource.CRYPTOMETER,
                direction=direction,
                strength=analysis.get('strength', 50),
                confidence=analysis.get('confidence', 50),
                score=analysis.get('score', 50),
                weight=self.SOURCE_WEIGHTS[SignalSource.CRYPTOMETER],
                metadata={
                    'timeframe': analysis.get('timeframe', 'MEDIUM'),
                    'indicators': analysis.get('indicators', {}),
                    'pattern': analysis.get('pattern', 'neutral')
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting Cryptometer signal: {e}")
            return None
    
    async def _get_kingfisher_signal(self, symbol: str) -> Optional[UnifiedSignal]:
        """Get signal from KingFisher"""
        try:
            # Get KingFisher analysis
            analysis = await self.kingfisher.analyze_liquidation_data(symbol)
            
            if not analysis:
                return None
            
            # Convert to unified signal
            direction = self._convert_action_to_direction(analysis.get('signal', 'HOLD'))
            
            return UnifiedSignal(
                symbol=symbol,
                timestamp=datetime.now(),
                source=SignalSource.KINGFISHER,
                direction=direction,
                strength=analysis.get('strength', 50),
                confidence=analysis.get('confidence', 50),
                score=analysis.get('liquidation_score', 50),
                weight=self.SOURCE_WEIGHTS[SignalSource.KINGFISHER],
                metadata={
                    'liquidation_levels': analysis.get('liquidation_levels', {}),
                    'heatmap_analysis': analysis.get('heatmap_analysis', {}),
                    'risk_zones': analysis.get('risk_zones', [])
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting KingFisher signal: {e}")
            return None
    
    async def _get_sentiment_signal(self, symbol: str) -> Optional[UnifiedSignal]:
        """Get signal from Sentiment (Grok-X)"""
        try:
            # Get sentiment analysis
            score = await sentiment_scoring_service.get_sentiment_score(symbol)
            
            if not score:
                return None
            
            # Convert to unified signal
            direction = self._convert_action_to_direction(score.signals.get('action', 'HOLD'))
            
            return UnifiedSignal(
                symbol=symbol,
                timestamp=score.timestamp,
                source=SignalSource.SENTIMENT,
                direction=direction,
                strength=score.signals.get('strength', 'NEUTRAL') == 'STRONG' and 80 or 50,
                confidence=score.confidence,
                score=score.sentiment_score,
                weight=self.SOURCE_WEIGHTS[SignalSource.SENTIMENT],
                metadata={
                    'raw_sentiment': score.raw_sentiment,
                    'sentiment_label': score.signals.get('sentiment_label'),
                    'key_topics': score.signals.get('key_topics', []),
                    'social_volume': score.signals.get('social_volume', 0),
                    'components': score.components
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting Sentiment signal: {e}")
            return None
    
    async def _get_riskmetric_signal(self, symbol: str) -> Optional[UnifiedSignal]:
        """Get signal from RiskMetric"""
        try:
            # Get RiskMetric analysis
            assessment = await enhanced_riskmetric_service.assess_risk(symbol)
            
            if not assessment:
                return None
            
            # Access attributes directly from the RiskAssessment dataclass
            risk_value = assessment.risk_value
            risk_band = assessment.risk_band
            score = assessment.score
            signal = assessment.signal
            win_rate = assessment.win_rate
            
            # Determine direction based on signal
            if signal == "STRONG BUY":
                direction = SignalDirection.STRONG_BUY
            elif signal == "BUY":
                direction = SignalDirection.BUY
            elif signal == "STRONG SELL":
                direction = SignalDirection.STRONG_SELL
            elif signal == "SELL":
                direction = SignalDirection.SELL
            else:
                direction = SignalDirection.HOLD
            
            return UnifiedSignal(
                symbol=symbol,
                timestamp=datetime.now(),
                source=SignalSource.RISKMETRIC,
                direction=direction,
                strength=score,  # Use the actual score from RiskMetric
                confidence=win_rate * 100,  # Convert win rate to percentage
                score=score,
                weight=self.SOURCE_WEIGHTS[SignalSource.RISKMETRIC],
                metadata={
                    'risk_value': risk_value,
                    'risk_band': risk_band,
                    'risk_zone': assessment.risk_zone,
                    'tradeable': assessment.tradeable,
                    'win_rate': win_rate
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting RiskMetric signal: {e}")
            return None
    
    async def _get_ai_analysis_signal(self, symbol: str) -> Optional[UnifiedSignal]:
        """Get signal from AI Analysis"""
        try:
            # Placeholder for AI analysis integration
            # This would connect to your AI analysis agents
            return None
            
        except Exception as e:
            logger.error(f"Error getting AI Analysis signal: {e}")
            return None
    
    async def _get_technical_signal(self, symbol: str) -> Optional[UnifiedSignal]:
        """Get signal from Technical Analysis"""
        try:
            # Placeholder for technical analysis integration
            # This would connect to your technical indicators
            return None
            
        except Exception as e:
            logger.error(f"Error getting Technical signal: {e}")
            return None
    
    def _aggregate_signals(self, symbol: str, signals: List[UnifiedSignal]) -> AggregatedSignal:
        """Aggregate all signals into a final decision"""
        if not signals:
            return self._get_default_aggregated_signal(symbol)
        
        # Calculate weighted scores
        total_score = 0
        total_weight = 0
        components = {}
        
        for signal in signals:
            weighted_score = signal.score * (signal.weight / 100)
            total_score += weighted_score
            total_weight += signal.weight
            components[signal.source.value] = signal.score
        
        # Normalize total score
        if total_weight > 0:
            total_score = (total_score / total_weight) * 100
        
        # Determine overall direction
        direction_counts = {}
        for signal in signals:
            direction = signal.direction.value if isinstance(signal.direction, Enum) else signal.direction
            weight = signal.weight * signal.confidence / 100
            direction_counts[direction] = direction_counts.get(direction, 0) + weight
        
        # Get weighted consensus direction
        if direction_counts:
            overall_direction = max(direction_counts.items(), key=lambda x: x[1])[0]
        else:
            overall_direction = "hold"
        
        # Calculate average confidence
        avg_confidence = sum(s.confidence for s in signals) / len(signals) if signals else 0
        
        # Generate recommendation
        recommendation = self._generate_recommendation(total_score, overall_direction, avg_confidence)
        
        # Assess risk level
        risk_level = self._assess_risk_level(signals, total_score)
        
        return AggregatedSignal(
            symbol=symbol,
            timestamp=datetime.now(),
            total_score=round(total_score, 2),
            direction=overall_direction,
            confidence=round(avg_confidence, 2),
            signals=signals,
            components=components,
            recommendation=recommendation,
            risk_level=risk_level
        )
    
    def _convert_action_to_direction(self, action: str) -> SignalDirection:
        """Convert various action strings to SignalDirection"""
        action = action.upper()
        
        mapping = {
            'STRONG_BUY': SignalDirection.STRONG_BUY,
            'BUY': SignalDirection.BUY,
            'HOLD': SignalDirection.HOLD,
            'SELL': SignalDirection.SELL,
            'STRONG_SELL': SignalDirection.STRONG_SELL
        }
        
        return mapping.get(action, SignalDirection.HOLD)
    
    def _generate_recommendation(self, score: float, direction: str, confidence: float) -> str:
        """Generate trading recommendation"""
        if confidence < 30:
            return "⚠️ Low confidence - Wait for clearer signals"
        
        if score >= 80:
            return "🚀 Strong BUY - Excellent opportunity detected"
        elif score >= 65:
            return "📈 BUY - Good entry point identified"
        elif score >= 55:
            return "📊 Mild BUY - Consider small position"
        elif score >= 45:
            return "⚖️ HOLD - No clear direction"
        elif score >= 35:
            return "📉 Mild SELL - Consider reducing position"
        elif score >= 20:
            return "🔻 SELL - Exit opportunity"
        else:
            return "🔴 Strong SELL - High risk detected"
    
    def _assess_risk_level(self, signals: List[UnifiedSignal], score: float) -> str:
        """Assess overall risk level"""
        # Check for conflicting signals
        directions = [s.direction.value if isinstance(s.direction, Enum) else s.direction for s in signals]
        unique_directions = set(directions)
        
        if len(unique_directions) > 2:
            return "HIGH"  # Conflicting signals
        
        # Check confidence levels
        avg_confidence = sum(s.confidence for s in signals) / len(signals) if signals else 0
        
        if avg_confidence < 40:
            return "HIGH"
        elif avg_confidence < 60:
            return "MEDIUM"
        elif score > 70 or score < 30:
            return "MEDIUM"  # Strong signals can be risky
        else:
            return "LOW"
    
    def _get_default_aggregated_signal(self, symbol: str) -> AggregatedSignal:
        """Get default aggregated signal when no data available"""
        return AggregatedSignal(
            symbol=symbol,
            timestamp=datetime.now(),
            total_score=50,
            direction="hold",
            confidence=0,
            signals=[],
            components={},
            recommendation="⚠️ No signals available",
            risk_level="UNKNOWN"
        )
    
    async def get_signal_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive signal dashboard"""
        try:
            # Get top symbols
            top_symbols = ["BTC", "ETH", "SOL", "BNB", "XRP"]
            
            # Get signals for all top symbols
            dashboard_data = {}
            for symbol in top_symbols:
                signal = await self.get_all_signals(symbol)
                dashboard_data[symbol] = signal.to_dict()
            
            # Calculate market overview
            avg_score = sum(s['total_score'] for s in dashboard_data.values()) / len(dashboard_data)
            
            # Determine market trend
            if avg_score > 65:
                market_trend = "BULLISH"
            elif avg_score < 35:
                market_trend = "BEARISH"
            else:
                market_trend = "NEUTRAL"
            
            return {
                "timestamp": datetime.now().isoformat(),
                "market_trend": market_trend,
                "average_score": round(avg_score, 2),
                "signals": dashboard_data,
                "source_weights": self.SOURCE_WEIGHTS,
                "active_sources": len([s for s in SignalSource if self.SOURCE_WEIGHTS.get(s, 0) > 0])
            }
            
        except Exception as e:
            logger.error(f"Error generating signal dashboard: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "signals": {}
            }

# Create global instance
unified_signal_center = UnifiedSignalCenter()