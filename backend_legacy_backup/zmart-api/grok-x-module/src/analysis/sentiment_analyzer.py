"""
Advanced Sentiment Analysis Engine
Comprehensive sentiment analysis for cryptocurrency social media content
"""

import asyncio
import re
import logging
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

from ..integrations.x_api_client import Tweet, User, SearchResult
from ..integrations.grok_ai_client import SentimentAnalysis, GrokAIClient
from ...config.settings.config import get_config


@dataclass
class SentimentScore:
    """Individual sentiment score with metadata"""
    score: float  # -1 to 1
    confidence: float  # 0 to 1
    reasoning: str
    factors: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AuthorCredibility:
    """Author credibility assessment"""
    base_score: float
    verification_bonus: float
    follower_influence: float
    engagement_quality: float
    historical_accuracy: float
    total_score: float
    
    @classmethod
    def calculate(cls, user: User, historical_data: Optional[Dict] = None) -> 'AuthorCredibility':
        """Calculate author credibility score"""
        base_score = 0.5
        
        # Verification bonus
        verification_bonus = 0.2 if user.verified else 0.0
        
        # Follower influence (logarithmic scale)
        follower_count = user.follower_count
        if follower_count > 0:
            follower_influence = min(0.2, math.log10(follower_count) / 25)
        else:
            follower_influence = 0.0
        
        # Engagement quality (based on follower-to-following ratio)
        following_count = user.public_metrics.get('following_count', 1)
        if following_count > 0:
            ratio = follower_count / following_count
            engagement_quality = min(0.1, math.log10(ratio + 1) / 10)
        else:
            engagement_quality = 0.1
        
        # Historical accuracy (from external data if available)
        historical_accuracy = 0.0
        if historical_data and user.username in historical_data:
            historical_accuracy = historical_data[user.username].get('accuracy_score', 0.0) * 0.2
        
        total_score = min(1.0, base_score + verification_bonus + follower_influence + engagement_quality + historical_accuracy)
        
        return cls(
            base_score=base_score,
            verification_bonus=verification_bonus,
            follower_influence=follower_influence,
            engagement_quality=engagement_quality,
            historical_accuracy=historical_accuracy,
            total_score=total_score
        )


@dataclass
class MarketContext:
    """Market context for sentiment analysis"""
    trending_symbols: List[str]
    market_sentiment: str  # "bullish", "bearish", "neutral"
    volatility_level: str  # "low", "medium", "high"
    major_events: List[str]
    time_of_day: str
    day_of_week: str


class CryptoTerminologyProcessor:
    """Processor for cryptocurrency-specific terminology and slang"""
    
    def __init__(self):
        # Bullish terms and their weights
        self.bullish_terms = {
            'moon': 0.8, 'mooning': 0.8, 'to the moon': 0.9,
            'diamond hands': 0.7, 'hodl': 0.6, 'hold': 0.4,
            'buy the dip': 0.6, 'btd': 0.6, 'dip buying': 0.6,
            'bullish': 0.8, 'bull run': 0.9, 'pump': 0.7,
            'rocket': 0.6, 'lambo': 0.7, 'ath': 0.5,
            'breakout': 0.6, 'golden cross': 0.7,
            'accumulate': 0.5, 'accumulating': 0.5,
            'strong support': 0.6, 'oversold': 0.5
        }
        
        # Bearish terms and their weights
        self.bearish_terms = {
            'dump': -0.7, 'dumping': -0.7, 'crash': -0.8,
            'paper hands': -0.6, 'panic sell': -0.7,
            'bearish': -0.8, 'bear market': -0.9,
            'rekt': -0.8, 'liquidated': -0.9,
            'death cross': -0.8, 'resistance': -0.4,
            'overbought': -0.5, 'correction': -0.6,
            'sell off': -0.7, 'capitulation': -0.9,
            'fud': -0.6, 'fear': -0.5, 'uncertainty': -0.4
        }
        
        # Neutral/informational terms
        self.neutral_terms = {
            'dyor': 0.0, 'nfa': 0.0, 'ta': 0.0, 'fa': 0.0,
            'analysis': 0.0, 'chart': 0.0, 'pattern': 0.0,
            'volume': 0.0, 'market cap': 0.0, 'mcap': 0.0
        }
        
        # Intensity modifiers
        self.intensity_modifiers = {
            'very': 1.3, 'extremely': 1.5, 'super': 1.4,
            'massive': 1.4, 'huge': 1.3, 'insane': 1.5,
            'slightly': 0.7, 'somewhat': 0.8, 'maybe': 0.6,
            'probably': 0.8, 'possibly': 0.6
        }
        
        # Negation words
        self.negation_words = {
            'not', 'no', 'never', 'none', 'nothing', 'nowhere',
            'neither', 'nobody', 'cannot', "can't", "won't",
            "shouldn't", "wouldn't", "couldn't", "don't", "doesn't"
        }
    
    def analyze_crypto_sentiment(self, text: str) -> Tuple[float, Dict[str, Any]]:
        """Analyze cryptocurrency-specific sentiment in text"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        sentiment_score = 0.0
        found_terms = []
        negation_context = False
        
        for i, word in enumerate(words):
            # Check for negation context
            if word in self.negation_words:
                negation_context = True
                continue
            
            # Check for intensity modifiers
            intensity = 1.0
            if i > 0 and words[i-1] in self.intensity_modifiers:
                intensity = self.intensity_modifiers[words[i-1]]
            
            # Check crypto terms
            term_score = 0.0
            term_type = None
            
            if word in self.bullish_terms:
                term_score = self.bullish_terms[word]
                term_type = 'bullish'
            elif word in self.bearish_terms:
                term_score = self.bearish_terms[word]
                term_type = 'bearish'
            elif word in self.neutral_terms:
                term_score = self.neutral_terms[word]
                term_type = 'neutral'
            
            if term_score != 0.0:
                # Apply negation
                if negation_context:
                    term_score *= -1
                    negation_context = False
                
                # Apply intensity
                term_score *= intensity
                
                sentiment_score += term_score
                found_terms.append({
                    'term': word,
                    'score': term_score,
                    'type': term_type,
                    'intensity': intensity
                })
        
        # Normalize score
        if found_terms:
            sentiment_score = max(-1.0, min(1.0, sentiment_score / len(found_terms)))
        
        analysis_details = {
            'found_terms': found_terms,
            'term_count': len(found_terms),
            'raw_score': sentiment_score
        }
        
        return sentiment_score, analysis_details


class EngagementAnalyzer:
    """Analyzer for social media engagement patterns"""
    
    @staticmethod
    def calculate_engagement_score(tweet: Tweet) -> float:
        """Calculate normalized engagement score"""
        metrics = tweet.public_metrics
        
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        quotes = metrics.get('quote_count', 0)
        
        # Weighted engagement score
        engagement = (
            likes * 1.0 +
            retweets * 2.0 +
            replies * 3.0 +
            quotes * 2.5
        )
        
        # Normalize using logarithmic scale
        if engagement > 0:
            return min(1.0, math.log10(engagement + 1) / 5)
        return 0.0
    
    @staticmethod
    def analyze_engagement_velocity(tweets: List[Tweet]) -> Dict[str, float]:
        """Analyze how quickly engagement is growing"""
        if len(tweets) < 2:
            return {'velocity': 0.0, 'acceleration': 0.0}
        
        # Sort tweets by creation time
        sorted_tweets = sorted(tweets, key=lambda t: t.created_datetime)
        
        engagement_scores = []
        time_deltas = []
        
        for i in range(1, len(sorted_tweets)):
            current_engagement = EngagementAnalyzer.calculate_engagement_score(sorted_tweets[i])
            previous_engagement = EngagementAnalyzer.calculate_engagement_score(sorted_tweets[i-1])
            
            time_delta = (sorted_tweets[i].created_datetime - sorted_tweets[i-1].created_datetime).total_seconds()
            
            if time_delta > 0:
                velocity = (current_engagement - previous_engagement) / time_delta
                engagement_scores.append(velocity)
                time_deltas.append(time_delta)
        
        if engagement_scores:
            avg_velocity = statistics.mean(engagement_scores)
            
            # Calculate acceleration (change in velocity)
            if len(engagement_scores) > 1:
                velocity_changes = [engagement_scores[i] - engagement_scores[i-1] 
                                 for i in range(1, len(engagement_scores))]
                acceleration = statistics.mean(velocity_changes) if velocity_changes else 0.0
            else:
                acceleration = 0.0
            
            return {
                'velocity': avg_velocity,
                'acceleration': acceleration,
                'trend': 'accelerating' if acceleration > 0 else 'decelerating' if acceleration < 0 else 'stable'
            }
        
        return {'velocity': 0.0, 'acceleration': 0.0, 'trend': 'stable'}


class SentimentAggregator:
    """Aggregates sentiment scores across multiple dimensions"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def aggregate_temporal_sentiment(
        self,
        sentiment_scores: List[SentimentScore],
        time_windows: List[int] = None
    ) -> Dict[str, float]:
        """Aggregate sentiment across different time windows"""
        
        if time_windows is None:
            time_windows = [3600, 86400, 604800]  # 1 hour, 1 day, 1 week
        
        now = datetime.now()
        aggregated = {}
        
        for window_seconds in time_windows:
            window_start = now - timedelta(seconds=window_seconds)
            
            # Filter scores within time window
            window_scores = [
                score for score in sentiment_scores
                if score.timestamp >= window_start
            ]
            
            if window_scores:
                # Calculate weighted average
                total_weight = 0.0
                weighted_sum = 0.0
                
                for score in window_scores:
                    # Weight by confidence and recency
                    age_seconds = (now - score.timestamp).total_seconds()
                    recency_weight = math.exp(-age_seconds / (window_seconds / 4))  # Decay over 1/4 of window
                    
                    weight = score.confidence * recency_weight
                    weighted_sum += score.score * weight
                    total_weight += weight
                
                if total_weight > 0:
                    avg_sentiment = weighted_sum / total_weight
                else:
                    avg_sentiment = 0.0
                
                # Calculate confidence based on sample size and agreement
                confidence = min(1.0, len(window_scores) / 10)  # Max confidence at 10+ samples
                
                # Adjust confidence based on score variance
                if len(window_scores) > 1:
                    variance = statistics.variance([s.score for s in window_scores])
                    confidence *= math.exp(-variance)  # Lower confidence for high variance
                
                window_label = f"{window_seconds//3600}h" if window_seconds < 86400 else f"{window_seconds//86400}d"
                aggregated[window_label] = {
                    'sentiment': avg_sentiment,
                    'confidence': confidence,
                    'sample_size': len(window_scores)
                }
            else:
                window_label = f"{window_seconds//3600}h" if window_seconds < 86400 else f"{window_seconds//86400}d"
                aggregated[window_label] = {
                    'sentiment': 0.0,
                    'confidence': 0.0,
                    'sample_size': 0
                }
        
        return aggregated
    
    def aggregate_by_influence(
        self,
        tweets: List[Tweet],
        users: Dict[str, User],
        sentiment_scores: List[SentimentScore]
    ) -> Dict[str, Any]:
        """Aggregate sentiment weighted by author influence"""
        
        if len(tweets) != len(sentiment_scores):
            self.logger.warning("Tweet count doesn't match sentiment score count")
            return {'weighted_sentiment': 0.0, 'confidence': 0.0}
        
        total_weight = 0.0
        weighted_sum = 0.0
        influence_distribution = defaultdict(list)
        
        for tweet, sentiment in zip(tweets, sentiment_scores):
            user = users.get(tweet.author_id)
            if not user:
                continue
            
            # Calculate author credibility
            credibility = AuthorCredibility.calculate(user)
            
            # Calculate engagement weight
            engagement_weight = EngagementAnalyzer.calculate_engagement_score(tweet)
            
            # Combined weight
            total_influence = credibility.total_score * 0.7 + engagement_weight * 0.3
            
            weighted_sum += sentiment.score * total_influence * sentiment.confidence
            total_weight += total_influence * sentiment.confidence
            
            # Track influence distribution
            if credibility.total_score > 0.8:
                influence_distribution['high_influence'].append(sentiment.score)
            elif credibility.total_score > 0.6:
                influence_distribution['medium_influence'].append(sentiment.score)
            else:
                influence_distribution['low_influence'].append(sentiment.score)
        
        if total_weight > 0:
            weighted_sentiment = weighted_sum / total_weight
        else:
            weighted_sentiment = 0.0
        
        # Calculate confidence based on influence diversity
        confidence = 0.0
        if influence_distribution:
            # Higher confidence if we have diverse influence levels
            influence_levels = len([k for k, v in influence_distribution.items() if v])
            confidence = min(1.0, influence_levels / 3)
        
        return {
            'weighted_sentiment': weighted_sentiment,
            'confidence': confidence,
            'influence_distribution': dict(influence_distribution),
            'total_weight': total_weight
        }


class AdvancedSentimentAnalyzer:
    """Advanced sentiment analyzer combining multiple techniques"""
    
    def __init__(self):
        self.config = get_config().sentiment
        self.logger = logging.getLogger(__name__)
        self.crypto_processor = CryptoTerminologyProcessor()
        self.aggregator = SentimentAggregator(self.config)
        self.grok_client = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.grok_client = GrokAIClient()
        await self.grok_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.grok_client:
            await self.grok_client.__aexit__(exc_type, exc_val, exc_tb)
    
    def analyze_local_sentiment(self, text: str) -> SentimentScore:
        """Analyze sentiment using local processing"""
        
        # Crypto-specific sentiment analysis
        crypto_sentiment, crypto_details = self.crypto_processor.analyze_crypto_sentiment(text)
        
        # Basic text analysis
        text_lower = text.lower()
        
        # Count positive/negative indicators
        positive_indicators = ['good', 'great', 'excellent', 'amazing', 'awesome', 'love', 'like']
        negative_indicators = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'worried', 'concerned']
        
        positive_count = sum(1 for word in positive_indicators if word in text_lower)
        negative_count = sum(1 for word in negative_indicators if word in text_lower)
        
        # Calculate basic sentiment
        if positive_count + negative_count > 0:
            basic_sentiment = (positive_count - negative_count) / (positive_count + negative_count)
        else:
            basic_sentiment = 0.0
        
        # Combine crypto and basic sentiment
        combined_sentiment = (crypto_sentiment * 0.7 + basic_sentiment * 0.3)
        
        # Calculate confidence based on signal strength
        confidence = min(1.0, (abs(crypto_sentiment) + abs(basic_sentiment)) / 2)
        
        return SentimentScore(
            score=combined_sentiment,
            confidence=confidence,
            reasoning=f"Crypto sentiment: {crypto_sentiment:.2f}, Basic sentiment: {basic_sentiment:.2f}",
            factors={
                'crypto_sentiment': crypto_sentiment,
                'basic_sentiment': basic_sentiment,
                'crypto_terms': len(crypto_details['found_terms']),
                'positive_indicators': positive_count,
                'negative_indicators': negative_count
            }
        )
    
    async def analyze_comprehensive_sentiment(
        self,
        search_result: SearchResult,
        market_context: Optional[MarketContext] = None
    ) -> SentimentAnalysis:
        """Perform comprehensive sentiment analysis"""
        
        tweets = search_result.tweets
        users = search_result.users
        
        if not tweets:
            return SentimentAnalysis(
                overall_sentiment=0.0,
                confidence=0.0,
                individual_sentiments=[],
                key_insights=["No tweets to analyze"],
                market_implications="Insufficient data for analysis"
            )
        
        # Prepare data for Grok analysis
        posts_data = []
        local_sentiments = []
        
        for tweet in tweets:
            user = users.get(tweet.author_id)
            
            # Local sentiment analysis
            local_sentiment = self.analyze_local_sentiment(tweet.text)
            local_sentiments.append(local_sentiment)
            
            # Prepare post data for Grok
            post_data = {
                'text': tweet.text,
                'author': user.username if user else 'unknown',
                'engagement': tweet.engagement_score,
                'created_at': tweet.created_at,
                'local_sentiment': local_sentiment.score
            }
            posts_data.append(post_data)
        
        # Get Grok AI analysis
        try:
            grok_analysis = await self.grok_client.analyze_sentiment(
                posts_data,
                context=f"Market context: {market_context}" if market_context else None
            )
        except Exception as e:
            self.logger.error(f"Grok analysis failed: {e}")
            # Fallback to local analysis
            grok_analysis = self._create_fallback_analysis(local_sentiments, tweets, users)
        
        # Enhance analysis with local insights
        enhanced_analysis = self._enhance_with_local_analysis(
            grok_analysis, local_sentiments, tweets, users
        )
        
        return enhanced_analysis
    
    def _create_fallback_analysis(
        self,
        local_sentiments: List[SentimentScore],
        tweets: List[Tweet],
        users: Dict[str, User]
    ) -> SentimentAnalysis:
        """Create fallback analysis using local processing"""
        
        if not local_sentiments:
            return SentimentAnalysis(
                overall_sentiment=0.0,
                confidence=0.0,
                individual_sentiments=[],
                key_insights=["Local analysis failed"],
                market_implications="Unable to analyze sentiment"
            )
        
        # Calculate weighted average sentiment
        total_weight = 0.0
        weighted_sum = 0.0
        
        individual_sentiments = []
        
        for i, (sentiment, tweet) in enumerate(zip(local_sentiments, tweets)):
            user = users.get(tweet.author_id)
            
            # Calculate weight based on credibility and engagement
            weight = sentiment.confidence
            if user:
                credibility = AuthorCredibility.calculate(user)
                weight *= credibility.total_score
            
            engagement_weight = EngagementAnalyzer.calculate_engagement_score(tweet)
            weight *= (1 + engagement_weight)
            
            weighted_sum += sentiment.score * weight
            total_weight += weight
            
            individual_sentiments.append({
                'post_id': tweet.id,
                'sentiment': sentiment.score,
                'confidence': sentiment.confidence,
                'reasoning': sentiment.reasoning
            })
        
        overall_sentiment = weighted_sum / total_weight if total_weight > 0 else 0.0
        overall_confidence = min(1.0, len(local_sentiments) / 10)
        
        # Generate insights
        positive_count = sum(1 for s in local_sentiments if s.score > 0.2)
        negative_count = sum(1 for s in local_sentiments if s.score < -0.2)
        neutral_count = len(local_sentiments) - positive_count - negative_count
        
        key_insights = [
            f"Analyzed {len(local_sentiments)} posts",
            f"Positive: {positive_count}, Negative: {negative_count}, Neutral: {neutral_count}",
            f"Overall sentiment: {overall_sentiment:.2f}"
        ]
        
        if overall_sentiment > 0.3:
            market_implications = "Bullish sentiment detected in social media discussions"
        elif overall_sentiment < -0.3:
            market_implications = "Bearish sentiment detected in social media discussions"
        else:
            market_implications = "Neutral sentiment with mixed opinions"
        
        return SentimentAnalysis(
            overall_sentiment=overall_sentiment,
            confidence=overall_confidence,
            individual_sentiments=individual_sentiments,
            key_insights=key_insights,
            market_implications=market_implications
        )
    
    def _enhance_with_local_analysis(
        self,
        grok_analysis: SentimentAnalysis,
        local_sentiments: List[SentimentScore],
        tweets: List[Tweet],
        users: Dict[str, User]
    ) -> SentimentAnalysis:
        """Enhance Grok analysis with local insights"""
        
        # Calculate temporal aggregation
        temporal_sentiment = self.aggregator.aggregate_temporal_sentiment(local_sentiments)
        
        # Calculate influence-weighted sentiment
        influence_sentiment = self.aggregator.aggregate_by_influence(tweets, users, local_sentiments)
        
        # Analyze engagement patterns
        engagement_analysis = EngagementAnalyzer.analyze_engagement_velocity(tweets)
        
        # Enhance key insights
        enhanced_insights = list(grok_analysis.key_insights)
        enhanced_insights.extend([
            f"Temporal analysis: {temporal_sentiment}",
            f"Influence-weighted sentiment: {influence_sentiment['weighted_sentiment']:.2f}",
            f"Engagement trend: {engagement_analysis['trend']}"
        ])
        
        # Adjust confidence based on local analysis agreement
        local_avg = statistics.mean([s.score for s in local_sentiments]) if local_sentiments else 0.0
        agreement = 1 - abs(grok_analysis.overall_sentiment - local_avg)
        adjusted_confidence = grok_analysis.confidence * agreement
        
        return SentimentAnalysis(
            overall_sentiment=grok_analysis.overall_sentiment,
            confidence=adjusted_confidence,
            individual_sentiments=grok_analysis.individual_sentiments,
            key_insights=enhanced_insights,
            market_implications=grok_analysis.market_implications,
            analysis_timestamp=grok_analysis.analysis_timestamp
        )


# Utility functions
async def analyze_crypto_sentiment(search_result: SearchResult) -> SentimentAnalysis:
    """Convenience function for sentiment analysis"""
    async with AdvancedSentimentAnalyzer() as analyzer:
        return await analyzer.analyze_comprehensive_sentiment(search_result)


def calculate_sentiment_trend(
    historical_sentiments: List[Tuple[datetime, float]]
) -> Dict[str, Any]:
    """Calculate sentiment trend over time"""
    if len(historical_sentiments) < 2:
        return {'trend': 'insufficient_data', 'slope': 0.0, 'confidence': 0.0}
    
    # Sort by timestamp
    sorted_sentiments = sorted(historical_sentiments, key=lambda x: x[0])
    
    # Calculate linear regression
    n = len(sorted_sentiments)
    x_values = list(range(n))
    y_values = [sentiment for _, sentiment in sorted_sentiments]
    
    # Calculate slope
    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(y_values)
    
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    
    if denominator == 0:
        slope = 0.0
    else:
        slope = numerator / denominator
    
    # Determine trend
    if slope > 0.1:
        trend = 'improving'
    elif slope < -0.1:
        trend = 'declining'
    else:
        trend = 'stable'
    
    # Calculate confidence based on data points and variance
    confidence = min(1.0, n / 10)
    if n > 1:
        variance = statistics.variance(y_values)
        confidence *= math.exp(-variance)
    
    return {
        'trend': trend,
        'slope': slope,
        'confidence': confidence,
        'data_points': n,
        'latest_sentiment': y_values[-1] if y_values else 0.0
    }

