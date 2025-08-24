"""
Advanced Trading Signal Generator
Combines sentiment analysis, market intelligence, and AI insights for signal generation
"""

import asyncio
import logging
import math
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from ..analysis.sentiment_analyzer import SentimentAnalysis, AdvancedSentimentAnalyzer
from ..integrations.grok_ai_client import GrokAIClient, TradingSignal, MarketAnalysis
from ..integrations.x_api_client import SearchResult
from ...config.settings.config import get_config, SignalType


class SignalStrength(Enum):
    """Signal strength levels"""
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class MarketIndicator:
    """Market indicator data point"""
    name: str
    value: float
    weight: float
    timestamp: datetime
    source: str
    confidence: float = 1.0


@dataclass
class SignalComponent:
    """Individual component contributing to a signal"""
    name: str
    value: float  # -1 to 1
    weight: float
    confidence: float
    reasoning: str
    data_points: int = 0


@dataclass
class EnhancedTradingSignal:
    """Enhanced trading signal with detailed analysis"""
    symbol: str
    signal_type: SignalType
    strength: SignalStrength
    confidence: float
    risk_level: RiskLevel
    
    # Price targets
    entry_price_range: Dict[str, float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    
    # Analysis components
    sentiment_component: SignalComponent
    technical_component: Optional[SignalComponent]
    fundamental_component: Optional[SignalComponent]
    social_component: SignalComponent
    
    # Metadata
    reasoning: str
    time_horizon: str
    generated_at: datetime
    expires_at: datetime
    
    # Supporting data
    supporting_evidence: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    market_context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def overall_score(self) -> float:
        """Calculate overall signal score"""
        components = [self.sentiment_component, self.social_component]
        if self.technical_component:
            components.append(self.technical_component)
        if self.fundamental_component:
            components.append(self.fundamental_component)
        
        total_weight = sum(comp.weight * comp.confidence for comp in components)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(comp.value * comp.weight * comp.confidence for comp in components)
        return weighted_sum / total_weight
    
    @property
    def is_valid(self) -> bool:
        """Check if signal is still valid"""
        return datetime.now() < self.expires_at and self.confidence >= 0.5


class MarketContextAnalyzer:
    """Analyzes market context for signal generation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_market_timing(self, timestamp: datetime) -> Dict[str, Any]:
        """Analyze market timing factors"""
        
        # Time of day analysis
        hour = timestamp.hour
        if 9 <= hour <= 16:
            market_session = "us_trading"
            timing_factor = 1.0
        elif 0 <= hour <= 8:
            market_session = "asian_trading"
            timing_factor = 0.8
        elif 17 <= hour <= 23:
            market_session = "after_hours"
            timing_factor = 0.6
        else:
            market_session = "overnight"
            timing_factor = 0.4
        
        # Day of week analysis
        weekday = timestamp.weekday()
        if weekday < 5:  # Monday to Friday
            day_factor = 1.0
            day_type = "weekday"
        else:  # Weekend
            day_factor = 0.3
            day_type = "weekend"
        
        # Combined timing score
        timing_score = timing_factor * day_factor
        
        return {
            'market_session': market_session,
            'day_type': day_type,
            'timing_score': timing_score,
            'hour': hour,
            'weekday': weekday
        }
    
    def analyze_volatility_context(self, recent_sentiments: List[float]) -> Dict[str, Any]:
        """Analyze volatility from sentiment patterns"""
        
        if len(recent_sentiments) < 2:
            return {
                'volatility_level': 'unknown',
                'volatility_score': 0.5,
                'trend_stability': 'unknown'
            }
        
        # Calculate sentiment volatility
        sentiment_variance = statistics.variance(recent_sentiments)
        sentiment_range = max(recent_sentiments) - min(recent_sentiments)
        
        # Volatility scoring
        if sentiment_variance > 0.3 or sentiment_range > 1.0:
            volatility_level = 'high'
            volatility_score = 0.8
        elif sentiment_variance > 0.1 or sentiment_range > 0.5:
            volatility_level = 'medium'
            volatility_score = 0.6
        else:
            volatility_level = 'low'
            volatility_score = 0.3
        
        # Trend stability
        if len(recent_sentiments) >= 3:
            recent_trend = recent_sentiments[-3:]
            if all(recent_trend[i] <= recent_trend[i+1] for i in range(len(recent_trend)-1)):
                trend_stability = 'consistently_improving'
            elif all(recent_trend[i] >= recent_trend[i+1] for i in range(len(recent_trend)-1)):
                trend_stability = 'consistently_declining'
            else:
                trend_stability = 'mixed'
        else:
            trend_stability = 'insufficient_data'
        
        return {
            'volatility_level': volatility_level,
            'volatility_score': volatility_score,
            'trend_stability': trend_stability,
            'sentiment_variance': sentiment_variance,
            'sentiment_range': sentiment_range
        }


class SignalScorer:
    """Scores and ranks trading signals"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def calculate_signal_strength(self, overall_score: float, confidence: float) -> SignalStrength:
        """Calculate signal strength based on score and confidence"""
        
        strength_score = abs(overall_score) * confidence
        
        if strength_score >= 0.8:
            return SignalStrength.VERY_STRONG
        elif strength_score >= 0.6:
            return SignalStrength.STRONG
        elif strength_score >= 0.4:
            return SignalStrength.MODERATE
        else:
            return SignalStrength.WEAK
    
    def assess_risk_level(
        self,
        signal_score: float,
        confidence: float,
        volatility_context: Dict[str, Any],
        market_timing: Dict[str, Any]
    ) -> RiskLevel:
        """Assess risk level for the signal"""
        
        risk_factors = []
        risk_score = 0.0
        
        # Confidence risk
        if confidence < 0.7:
            risk_factors.append("Low confidence")
            risk_score += 0.3
        
        # Volatility risk
        volatility_level = volatility_context.get('volatility_level', 'medium')
        if volatility_level == 'high':
            risk_factors.append("High market volatility")
            risk_score += 0.4
        elif volatility_level == 'medium':
            risk_score += 0.2
        
        # Timing risk
        timing_score = market_timing.get('timing_score', 0.5)
        if timing_score < 0.5:
            risk_factors.append("Suboptimal market timing")
            risk_score += 0.3
        
        # Signal extremity risk
        if abs(signal_score) > 0.8:
            risk_factors.append("Extreme signal value")
            risk_score += 0.2
        
        # Determine risk level
        if risk_score >= 0.7:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.5:
            return RiskLevel.HIGH
        elif risk_score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def calculate_price_targets(
        self,
        signal_type: SignalType,
        signal_strength: SignalStrength,
        current_price: Optional[float] = None
    ) -> Dict[str, Optional[float]]:
        """Calculate price targets based on signal"""
        
        if not current_price:
            return {
                'entry_min': None,
                'entry_max': None,
                'stop_loss': None,
                'take_profit': None
            }
        
        # Strength-based multipliers
        strength_multipliers = {
            SignalStrength.WEAK: 0.02,      # 2%
            SignalStrength.MODERATE: 0.05,  # 5%
            SignalStrength.STRONG: 0.10,    # 10%
            SignalStrength.VERY_STRONG: 0.15 # 15%
        }
        
        multiplier = strength_multipliers[signal_strength]
        
        if signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
            # Buy signals
            entry_min = current_price * (1 - multiplier * 0.5)
            entry_max = current_price * (1 + multiplier * 0.2)
            stop_loss = current_price * (1 - self.config.default_stop_loss_pct)
            take_profit = current_price * (1 + self.config.default_take_profit_pct)
        
        elif signal_type in [SignalType.SELL, SignalType.STRONG_SELL]:
            # Sell signals
            entry_min = current_price * (1 - multiplier * 0.2)
            entry_max = current_price * (1 + multiplier * 0.5)
            stop_loss = current_price * (1 + self.config.default_stop_loss_pct)
            take_profit = current_price * (1 - self.config.default_take_profit_pct)
        
        else:
            # Hold signals
            entry_min = current_price * 0.98
            entry_max = current_price * 1.02
            stop_loss = None
            take_profit = None
        
        return {
            'entry_min': entry_min,
            'entry_max': entry_max,
            'stop_loss': stop_loss,
            'take_profit': take_profit
        }


class AdvancedSignalGenerator:
    """Advanced trading signal generator"""
    
    def __init__(self):
        self.config = get_config().signals
        self.logger = logging.getLogger(__name__)
        self.sentiment_analyzer = None
        self.grok_client = None
        self.context_analyzer = MarketContextAnalyzer()
        self.scorer = SignalScorer(self.config)
        
        # Signal history for pattern analysis
        self.signal_history: List[EnhancedTradingSignal] = []
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.sentiment_analyzer = AdvancedSentimentAnalyzer()
        await self.sentiment_analyzer.__aenter__()
        
        self.grok_client = GrokAIClient()
        await self.grok_client.__aenter__()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.sentiment_analyzer:
            await self.sentiment_analyzer.__aexit__(exc_type, exc_val, exc_tb)
        if self.grok_client:
            await self.grok_client.__aexit__(exc_type, exc_val, exc_tb)
    
    def _create_sentiment_component(self, sentiment_analysis: SentimentAnalysis) -> SignalComponent:
        """Create sentiment component for signal"""
        
        # Normalize sentiment to signal value
        sentiment_value = sentiment_analysis.overall_sentiment
        
        # Weight based on confidence and data quality
        weight = 0.4  # Base weight for sentiment
        
        reasoning = f"Sentiment: {sentiment_value:.2f} ({sentiment_analysis.sentiment_label})"
        
        return SignalComponent(
            name="sentiment",
            value=sentiment_value,
            weight=weight,
            confidence=sentiment_analysis.confidence,
            reasoning=reasoning,
            data_points=len(sentiment_analysis.individual_sentiments)
        )
    
    def _create_social_component(self, search_result: SearchResult) -> SignalComponent:
        """Create social media component for signal"""
        
        tweets = search_result.tweets
        users = search_result.users
        
        if not tweets:
            return SignalComponent(
                name="social",
                value=0.0,
                weight=0.2,
                confidence=0.0,
                reasoning="No social media data available"
            )
        
        # Analyze social metrics
        total_engagement = sum(tweet.engagement_score for tweet in tweets)
        avg_engagement = total_engagement / len(tweets)
        
        # Analyze user influence
        high_influence_count = 0
        total_followers = 0
        
        for tweet in tweets:
            user = users.get(tweet.author_id)
            if user:
                total_followers += user.follower_count
                if user.verified or user.follower_count > 10000:
                    high_influence_count += 1
        
        # Calculate social signal value
        engagement_factor = min(1.0, avg_engagement * 2)  # Normalize engagement
        influence_factor = high_influence_count / len(tweets) if tweets else 0
        volume_factor = min(1.0, len(tweets) / 50)  # Normalize volume
        
        social_value = (engagement_factor * 0.4 + influence_factor * 0.4 + volume_factor * 0.2)
        
        # Convert to signal range (-1 to 1)
        # High social activity generally indicates bullish sentiment
        social_signal = (social_value - 0.5) * 2
        
        reasoning = f"Social metrics: {len(tweets)} posts, {avg_engagement:.2f} avg engagement, {high_influence_count} influential users"
        
        return SignalComponent(
            name="social",
            value=social_signal,
            weight=0.3,
            confidence=min(1.0, len(tweets) / 20),
            reasoning=reasoning,
            data_points=len(tweets)
        )
    
    def _determine_signal_type(self, overall_score: float) -> SignalType:
        """Determine signal type based on overall score"""
        
        if overall_score >= self.config.strong_buy_threshold:
            return SignalType.STRONG_BUY
        elif overall_score >= self.config.buy_threshold:
            return SignalType.BUY
        elif overall_score <= self.config.strong_sell_threshold:
            return SignalType.STRONG_SELL
        elif overall_score <= self.config.sell_threshold:
            return SignalType.SELL
        else:
            return SignalType.HOLD
    
    async def generate_signals_from_sentiment(
        self,
        search_result: SearchResult,
        symbols: List[str],
        market_context: Optional[Dict[str, Any]] = None
    ) -> List[EnhancedTradingSignal]:
        """Generate trading signals from sentiment analysis"""
        
        if not search_result.tweets:
            self.logger.warning("No tweets available for signal generation")
            return []
        
        # Perform comprehensive sentiment analysis
        sentiment_analysis = await self.sentiment_analyzer.analyze_comprehensive_sentiment(
            search_result, market_context
        )
        
        # Analyze market context
        now = datetime.now()
        market_timing = self.context_analyzer.analyze_market_timing(now)
        
        # Get recent sentiment history for volatility analysis
        recent_sentiments = [sentiment_analysis.overall_sentiment]  # Would include historical data in production
        volatility_context = self.context_analyzer.analyze_volatility_context(recent_sentiments)
        
        signals = []
        
        for symbol in symbols:
            try:
                # Create signal components
                sentiment_component = self._create_sentiment_component(sentiment_analysis)
                social_component = self._create_social_component(search_result)
                
                # Calculate overall signal score
                components = [sentiment_component, social_component]
                total_weight = sum(comp.weight * comp.confidence for comp in components)
                
                if total_weight == 0:
                    continue
                
                overall_score = sum(comp.value * comp.weight * comp.confidence for comp in components) / total_weight
                overall_confidence = sum(comp.confidence * comp.weight for comp in components) / sum(comp.weight for comp in components)
                
                # Filter weak signals
                if overall_confidence < self.config.min_confidence:
                    continue
                
                # Determine signal type
                signal_type = self._determine_signal_type(overall_score)
                
                # Calculate signal strength
                signal_strength = self.scorer.calculate_signal_strength(overall_score, overall_confidence)
                
                # Assess risk level
                risk_level = self.scorer.assess_risk_level(
                    overall_score, overall_confidence, volatility_context, market_timing
                )
                
                # Calculate price targets (would use real price data in production)
                price_targets = self.scorer.calculate_price_targets(signal_type, signal_strength)
                
                # Generate reasoning
                reasoning = f"Signal generated from {len(search_result.tweets)} social media posts. "
                reasoning += f"Sentiment: {sentiment_analysis.overall_sentiment:.2f}, "
                reasoning += f"Confidence: {overall_confidence:.2f}, "
                reasoning += f"Market timing: {market_timing['market_session']}"
                
                # Create enhanced signal
                signal = EnhancedTradingSignal(
                    symbol=symbol,
                    signal_type=signal_type,
                    strength=signal_strength,
                    confidence=overall_confidence,
                    risk_level=risk_level,
                    entry_price_range={
                        'min': price_targets['entry_min'],
                        'max': price_targets['entry_max']
                    },
                    stop_loss=price_targets['stop_loss'],
                    take_profit=price_targets['take_profit'],
                    sentiment_component=sentiment_component,
                    technical_component=None,  # Would be implemented with price data
                    fundamental_component=None,  # Would be implemented with fundamental data
                    social_component=social_component,
                    reasoning=reasoning,
                    time_horizon="SHORT",  # Based on social media data
                    generated_at=now,
                    expires_at=now + timedelta(minutes=self.config.signal_expiry_minutes),
                    supporting_evidence=sentiment_analysis.key_insights,
                    risk_factors=[f"Risk level: {risk_level.value}", f"Volatility: {volatility_context['volatility_level']}"],
                    market_context={
                        'sentiment_analysis': sentiment_analysis,
                        'market_timing': market_timing,
                        'volatility_context': volatility_context,
                        'social_metrics': {
                            'tweet_count': len(search_result.tweets),
                            'user_count': len(search_result.users),
                            'avg_engagement': sum(t.engagement_score for t in search_result.tweets) / len(search_result.tweets)
                        }
                    }
                )
                
                signals.append(signal)
                self.logger.info(f"Generated {signal_type.value} signal for {symbol} with confidence {overall_confidence:.2f}")
                
            except Exception as e:
                self.logger.error(f"Failed to generate signal for {symbol}: {e}")
                continue
        
        # Add to signal history
        self.signal_history.extend(signals)
        
        # Keep only recent signals in history
        cutoff_time = now - timedelta(hours=24)
        self.signal_history = [s for s in self.signal_history if s.generated_at > cutoff_time]
        
        return signals
    
    async def generate_ai_enhanced_signals(
        self,
        search_result: SearchResult,
        symbols: List[str],
        market_context: Optional[Dict[str, Any]] = None
    ) -> List[EnhancedTradingSignal]:
        """Generate AI-enhanced signals using Grok analysis"""
        
        # First generate base signals
        base_signals = await self.generate_signals_from_sentiment(search_result, symbols, market_context)
        
        if not base_signals:
            return []
        
        # Get sentiment analysis for Grok enhancement
        sentiment_analysis = await self.sentiment_analyzer.analyze_comprehensive_sentiment(search_result)
        
        # Use Grok for additional market analysis
        try:
            grok_analysis = await self.grok_client.generate_trading_signals(
                sentiment_data=sentiment_analysis,
                market_context=market_context,
                symbols=symbols
            )
            
            # Enhance base signals with Grok insights
            enhanced_signals = self._enhance_signals_with_grok(base_signals, grok_analysis)
            
            return enhanced_signals
            
        except Exception as e:
            self.logger.error(f"Grok enhancement failed: {e}")
            return base_signals
    
    def _enhance_signals_with_grok(
        self,
        base_signals: List[EnhancedTradingSignal],
        grok_analysis: MarketAnalysis
    ) -> List[EnhancedTradingSignal]:
        """Enhance base signals with Grok AI insights"""
        
        enhanced_signals = []
        
        # Create a mapping of Grok signals by symbol
        grok_signals_map = {signal.symbol: signal for signal in grok_analysis.signals}
        
        for base_signal in base_signals:
            enhanced_signal = base_signal
            
            # Find corresponding Grok signal
            grok_signal = grok_signals_map.get(base_signal.symbol)
            
            if grok_signal:
                # Adjust confidence based on Grok agreement
                grok_score = self._convert_grok_signal_to_score(grok_signal)
                base_score = base_signal.overall_score
                
                agreement = 1 - abs(grok_score - base_score) / 2
                enhanced_confidence = base_signal.confidence * agreement
                
                # Update reasoning with Grok insights
                enhanced_reasoning = base_signal.reasoning + f" | Grok AI: {grok_signal.reasoning}"
                
                # Add Grok risk factors
                enhanced_risk_factors = base_signal.risk_factors + [f"Grok risk: {grok_signal.risk_level}"]
                
                # Create enhanced signal
                enhanced_signal = EnhancedTradingSignal(
                    symbol=base_signal.symbol,
                    signal_type=base_signal.signal_type,
                    strength=base_signal.strength,
                    confidence=enhanced_confidence,
                    risk_level=base_signal.risk_level,
                    entry_price_range=base_signal.entry_price_range,
                    stop_loss=base_signal.stop_loss,
                    take_profit=base_signal.take_profit,
                    sentiment_component=base_signal.sentiment_component,
                    technical_component=base_signal.technical_component,
                    fundamental_component=base_signal.fundamental_component,
                    social_component=base_signal.social_component,
                    reasoning=enhanced_reasoning,
                    time_horizon=base_signal.time_horizon,
                    generated_at=base_signal.generated_at,
                    expires_at=base_signal.expires_at,
                    supporting_evidence=base_signal.supporting_evidence + [grok_signal.reasoning],
                    risk_factors=enhanced_risk_factors,
                    market_context=base_signal.market_context
                )
            
            enhanced_signals.append(enhanced_signal)
        
        return enhanced_signals
    
    def _convert_grok_signal_to_score(self, grok_signal: TradingSignal) -> float:
        """Convert Grok signal to numerical score"""
        signal_scores = {
            'STRONG_BUY': 0.8,
            'BUY': 0.6,
            'HOLD': 0.0,
            'SELL': -0.6,
            'STRONG_SELL': -0.8
        }
        
        base_score = signal_scores.get(grok_signal.signal_type, 0.0)
        return base_score * grok_signal.confidence
    
    def get_signal_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated signals"""
        
        if not self.signal_history:
            return {'total_signals': 0}
        
        # Count signals by type
        signal_counts = {}
        for signal in self.signal_history:
            signal_type = signal.signal_type.value
            signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1
        
        # Calculate average confidence
        avg_confidence = statistics.mean([s.confidence for s in self.signal_history])
        
        # Count by risk level
        risk_counts = {}
        for signal in self.signal_history:
            risk_level = signal.risk_level.value
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        return {
            'total_signals': len(self.signal_history),
            'signal_counts': signal_counts,
            'average_confidence': avg_confidence,
            'risk_distribution': risk_counts,
            'latest_signal_time': max(s.generated_at for s in self.signal_history) if self.signal_history else None
        }


# Utility functions
async def generate_crypto_signals(
    search_result: SearchResult,
    symbols: List[str]
) -> List[EnhancedTradingSignal]:
    """Convenience function for generating crypto signals"""
    async with AdvancedSignalGenerator() as generator:
        return await generator.generate_ai_enhanced_signals(search_result, symbols)


def filter_signals_by_confidence(
    signals: List[EnhancedTradingSignal],
    min_confidence: float = 0.7
) -> List[EnhancedTradingSignal]:
    """Filter signals by minimum confidence threshold"""
    return [signal for signal in signals if signal.confidence >= min_confidence]


def rank_signals_by_strength(
    signals: List[EnhancedTradingSignal]
) -> List[EnhancedTradingSignal]:
    """Rank signals by strength and confidence"""
    
    def signal_score(signal):
        strength_scores = {
            SignalStrength.VERY_STRONG: 4,
            SignalStrength.STRONG: 3,
            SignalStrength.MODERATE: 2,
            SignalStrength.WEAK: 1
        }
        return strength_scores[signal.strength] * signal.confidence
    
    return sorted(signals, key=signal_score, reverse=True)

