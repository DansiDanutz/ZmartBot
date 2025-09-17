#!/usr/bin/env python3
"""
Sentiment Scoring Service
Integrates Grok-X sentiment analysis into the main scoring system
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from src.agents.sentiment.grok_x_sentiment_agent import grok_x_sentiment_agent, SentimentSignal

logger = logging.getLogger(__name__)

@dataclass
class SentimentScore:
    """Sentiment score for integration with main scoring system"""
    symbol: str
    sentiment_score: float  # 0-100 normalized for scoring system
    raw_sentiment: float  # -100 to 100 original sentiment
    confidence: float
    components: Dict[str, float]
    signals: Dict[str, Any]
    timestamp: datetime

class SentimentScoringService:
    """Service for calculating sentiment-based scoring"""
    
    # Weight of sentiment in overall scoring (adjust as needed)
    SENTIMENT_WEIGHT = 15  # 15% of total score
    
    def __init__(self):
        """Initialize sentiment scoring service"""
        self.agent = grok_x_sentiment_agent
        self.cache = {}
        self.cache_duration = 300  # 5 minutes in seconds
    
    async def get_sentiment_score(self, symbol: str) -> SentimentScore:
        """
        Get sentiment score for a symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            SentimentScore with normalized scoring
        """
        try:
            # Get sentiment signal from agent
            signal = await self.agent.analyze_sentiment(symbol)
            
            # Normalize sentiment for scoring system
            normalized_score = self._normalize_sentiment(signal)
            
            # Calculate component scores
            components = self._calculate_components(signal)
            
            # Prepare signals for decision making
            signals = self._prepare_signals(signal)
            
            return SentimentScore(
                symbol=symbol,
                sentiment_score=normalized_score,
                raw_sentiment=signal.sentiment_score,
                confidence=signal.confidence,
                components=components,
                signals=signals,
                timestamp=signal.timestamp
            )
            
        except Exception as e:
            logger.error(f"Error getting sentiment score for {symbol}: {e}")
            return self._get_default_score(symbol)
    
    def _normalize_sentiment(self, signal: SentimentSignal) -> float:
        """
        Normalize sentiment from -100 to 100 range to 0-100 for scoring
        
        Args:
            signal: Sentiment signal
            
        Returns:
            Normalized score (0-100)
        """
        # Convert -100 to 100 range to 0-100
        normalized = (signal.sentiment_score + 100) / 2
        
        # Apply confidence weighting
        confidence_factor = signal.confidence / 100
        
        # Weighted score
        weighted_score = normalized * confidence_factor + 50 * (1 - confidence_factor)
        
        return min(100, max(0, weighted_score))
    
    def _calculate_components(self, signal: SentimentSignal) -> Dict[str, float]:
        """
        Calculate component scores for detailed analysis
        
        Args:
            signal: Sentiment signal
            
        Returns:
            Component scores dictionary
        """
        components = {
            'grok_ai': self._normalize_value(signal.grok_sentiment),
            'x_social': self._normalize_value(signal.x_sentiment),
            'influencer': self._normalize_value(signal.influencer_sentiment),
            'retail': self._normalize_value(signal.retail_sentiment),
            'whale': self._normalize_value(signal.whale_sentiment),
            'trending': signal.trending_score,
            'volume': min(100, signal.social_volume / 10)  # Normalize volume
        }
        
        return components
    
    def _prepare_signals(self, signal: SentimentSignal) -> Dict[str, Any]:
        """
        Prepare sentiment signals for trading decisions
        
        Args:
            signal: Sentiment signal
            
        Returns:
            Trading signals dictionary
        """
        # Determine action based on sentiment
        if signal.sentiment_score >= 50:
            action = "BUY"
            strength = "STRONG" if signal.sentiment_score >= 75 else "MODERATE"
        elif signal.sentiment_score <= -50:
            action = "SELL"
            strength = "STRONG" if signal.sentiment_score <= -75 else "MODERATE"
        else:
            action = "HOLD"
            strength = "NEUTRAL"
        
        return {
            'action': action,
            'strength': strength,
            'sentiment_label': signal.sentiment_label,
            'confidence': signal.confidence,
            'key_topics': signal.key_topics,
            'social_volume': signal.social_volume,
            'trending': signal.trending_score > 50,
            'influencer_bullish': signal.influencer_sentiment > 25,
            'retail_bullish': signal.retail_sentiment > 25,
            'whale_bullish': signal.whale_sentiment > 25
        }
    
    def _normalize_value(self, value: float) -> float:
        """Normalize value from -100 to 100 range to 0-100"""
        return (value + 100) / 2
    
    def _get_default_score(self, symbol: str) -> SentimentScore:
        """Get default sentiment score when analysis fails"""
        return SentimentScore(
            symbol=symbol,
            sentiment_score=50,  # Neutral
            raw_sentiment=0,
            confidence=0,
            components={
                'grok_ai': 50,
                'x_social': 50,
                'influencer': 50,
                'retail': 50,
                'whale': 50,
                'trending': 0,
                'volume': 0
            },
            signals={
                'action': 'HOLD',
                'strength': 'NEUTRAL',
                'sentiment_label': 'NEUTRAL',
                'confidence': 0,
                'key_topics': [],
                'social_volume': 0,
                'trending': False,
                'influencer_bullish': False,
                'retail_bullish': False,
                'whale_bullish': False
            },
            timestamp=datetime.now()
        )
    
    async def get_multiple_sentiments(self, symbols: List[str]) -> Dict[str, SentimentScore]:
        """
        Get sentiment scores for multiple symbols
        
        Args:
            symbols: List of trading symbols
            
        Returns:
            Dictionary of symbol to SentimentScore
        """
        tasks = [self.get_sentiment_score(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        sentiment_scores = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to get sentiment for {symbol}: {result}")
                sentiment_scores[symbol] = self._get_default_score(symbol)
            else:
                sentiment_scores[symbol] = result
        
        return sentiment_scores
    
    def calculate_weighted_sentiment(self, sentiment_score: float) -> float:
        """
        Calculate weighted sentiment contribution to total score
        
        Args:
            sentiment_score: Normalized sentiment score (0-100)
            
        Returns:
            Weighted contribution (0 to SENTIMENT_WEIGHT)
        """
        return (sentiment_score / 100) * self.SENTIMENT_WEIGHT
    
    def get_sentiment_recommendation(self, score: SentimentScore) -> str:
        """
        Get trading recommendation based on sentiment
        
        Args:
            score: Sentiment score
            
        Returns:
            Recommendation text
        """
        if score.raw_sentiment >= 75:
            return "🚀 Extreme bullish sentiment - Strong buy signal from social media"
        elif score.raw_sentiment >= 50:
            return "📈 Very bullish sentiment - Positive market sentiment detected"
        elif score.raw_sentiment >= 25:
            return "📊 Bullish sentiment - Moderate positive signals"
        elif score.raw_sentiment >= -25:
            return "⚖️ Neutral sentiment - Mixed signals from market"
        elif score.raw_sentiment >= -50:
            return "📉 Bearish sentiment - Negative market sentiment emerging"
        elif score.raw_sentiment >= -75:
            return "⚠️ Very bearish sentiment - Strong sell pressure detected"
        else:
            return "🔴 Extreme bearish sentiment - High risk, consider exit"

# Create global instance
sentiment_scoring_service = SentimentScoringService()