#!/usr/bin/env python3
"""
Grok-X Sentiment Analysis Agent
Combines Grok AI and X (Twitter) data for comprehensive sentiment scoring
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, cast
from dataclasses import dataclass, asdict
import os
import statistics
from enum import Enum

from src.config.secure_config import secure_config

logger = logging.getLogger(__name__)

class SentimentLevel(Enum):
    """Sentiment level classifications"""
    EXTREME_BEARISH = -100
    VERY_BEARISH = -75
    BEARISH = -50
    SLIGHTLY_BEARISH = -25
    NEUTRAL = 0
    SLIGHTLY_BULLISH = 25
    BULLISH = 50
    VERY_BULLISH = 75
    EXTREME_BULLISH = 100

@dataclass
class SentimentSignal:
    """Sentiment signal data structure"""
    symbol: str
    sentiment_score: float  # -100 to 100
    confidence: float  # 0 to 100
    sentiment_label: str
    grok_sentiment: float
    x_sentiment: float
    social_volume: int
    trending_score: float
    key_topics: List[str]
    influencer_sentiment: float
    retail_sentiment: float
    whale_sentiment: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'sentiment_score': self.sentiment_score,
            'confidence': self.confidence,
            'sentiment_label': self.sentiment_label,
            'grok_sentiment': self.grok_sentiment,
            'x_sentiment': self.x_sentiment,
            'social_volume': self.social_volume,
            'trending_score': self.trending_score,
            'key_topics': self.key_topics,
            'influencer_sentiment': self.influencer_sentiment,
            'retail_sentiment': self.retail_sentiment,
            'whale_sentiment': self.whale_sentiment,
            'timestamp': self.timestamp.isoformat()
        }

class GrokXSentimentAgent:
    """Agent for analyzing sentiment using Grok AI and X data"""
    
    def __init__(self):
        """Initialize the sentiment agent"""
        # Load API credentials from secure config
        self.grok_api_key = secure_config.get_env('GROK_API_KEY')
        self.x_api_key = secure_config.get_env('X_API_KEY')
        self.x_bearer_token = secure_config.get_env('X_BEARER_TOKEN')
        
        if not self.grok_api_key:
            logger.warning("Grok API key not configured")
        if not self.x_bearer_token:
            logger.warning("X Bearer token not configured")
            
        self.grok_base_url = "https://api.x.ai/v1"
        self.x_api_base_url = "https://api.twitter.com/2"
        
        # Rate limiting
        self.rate_limiter = {
            'grok': {'calls': 0, 'max': 100, 'reset': datetime.now()},
            'x': {'calls': 0, 'max': 300, 'reset': datetime.now()}
        }
        
        # Cache for recent analyses
        self.sentiment_cache = {}
        self.cache_duration = timedelta(minutes=5)
    
    async def analyze_sentiment(self, symbol: str) -> SentimentSignal:
        """
        Analyze sentiment for a symbol using Grok and X data
        
        Args:
            symbol: Trading symbol (e.g., 'BTC', 'ETH')
            
        Returns:
            SentimentSignal with comprehensive sentiment analysis
        """
        # Check cache
        if symbol in self.sentiment_cache:
            cached = self.sentiment_cache[symbol]
            if datetime.now() - cached['timestamp'] < self.cache_duration:
                logger.info(f"Using cached sentiment for {symbol}")
                return cached['signal']
        
        try:
            # Gather data from multiple sources
            results = await asyncio.gather(
                self._analyze_with_grok(symbol),
                self._fetch_x_sentiment(symbol),
                return_exceptions=True
            )
            
            # Handle exceptions and ensure correct types
            grok_analysis_raw = results[0]
            x_data_raw = results[1]
            
            if isinstance(grok_analysis_raw, Exception):
                logger.error(f"Grok analysis failed: {grok_analysis_raw}")
                grok_analysis: Dict[str, Any] = self._get_default_grok_analysis()
            else:
                grok_analysis: Dict[str, Any] = cast(Dict[str, Any], grok_analysis_raw)
            
            if isinstance(x_data_raw, Exception):
                logger.error(f"X data fetch failed: {x_data_raw}")
                x_data: Dict[str, Any] = self._get_default_x_data()
            else:
                x_data: Dict[str, Any] = cast(Dict[str, Any], x_data_raw)
            
            # Calculate comprehensive sentiment
            sentiment_signal = self._calculate_sentiment(symbol, grok_analysis, x_data)
            
            # Cache the result
            self.sentiment_cache[symbol] = {
                'signal': sentiment_signal,
                'timestamp': datetime.now()
            }
            
            return sentiment_signal
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed for {symbol}: {e}")
            return self._get_default_sentiment(symbol)
    
    async def _analyze_with_grok(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze sentiment using Grok AI
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Grok analysis results
        """
        if not self.grok_api_key:
            return self._get_default_grok_analysis()
        
        # Check rate limiting
        if not self._check_rate_limit('grok'):
            logger.warning("Grok rate limit reached")
            return self._get_default_grok_analysis()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.grok_api_key}',
                    'Content-Type': 'application/json'
                }
                
                prompt = f"""Analyze the current market sentiment for {symbol} cryptocurrency.
                Consider:
                1. Recent price movements and technical indicators
                2. Social media sentiment and trending topics
                3. News and fundamental developments
                4. Whale activity and on-chain metrics
                5. Overall market conditions
                
                Provide a JSON response with:
                - sentiment_score: -100 to 100 (extreme bearish to extreme bullish)
                - confidence: 0 to 100
                - key_factors: list of main sentiment drivers
                - market_outlook: brief analysis
                - risk_factors: potential risks
                """
                
                payload = {
                    'model': 'grok-beta',
                    'messages': [
                        {'role': 'system', 'content': 'You are a cryptocurrency sentiment analyst.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.3,
                    'max_tokens': 500
                }
                
                async with session.post(
                    f"{self.grok_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._increment_rate_limit('grok')
                        
                        # Parse Grok response
                        content = data['choices'][0]['message']['content']
                        try:
                            analysis = json.loads(content)
                        except:
                            # If not JSON, extract sentiment from text
                            analysis = self._parse_text_sentiment(content)
                        
                        return analysis
                    else:
                        logger.error(f"Grok API error: {response.status}")
                        return self._get_default_grok_analysis()
                        
        except Exception as e:
            logger.error(f"Grok analysis error: {e}")
            return self._get_default_grok_analysis()
    
    async def _fetch_x_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch sentiment data from X (Twitter)
        
        Args:
            symbol: Trading symbol
            
        Returns:
            X sentiment data
        """
        if not self.x_bearer_token:
            return self._get_default_x_data()
        
        # Check rate limiting
        if not self._check_rate_limit('x'):
            logger.warning("X rate limit reached")
            return self._get_default_x_data()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.x_bearer_token}',
                    'User-Agent': 'v2TweetLookupPython'
                }
                
                # Search for recent tweets about the symbol
                query = f"(${symbol} OR #{symbol}) lang:en -is:retweet"
                params = {
                    'query': query,
                    'max_results': 100,
                    'tweet.fields': 'created_at,public_metrics,author_id',
                    'expansions': 'author_id',
                    'user.fields': 'verified,public_metrics'
                }
                
                async with session.get(
                    f"{self.x_api_base_url}/tweets/search/recent",
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._increment_rate_limit('x')
                        
                        # Analyze tweet sentiment
                        sentiment_data = self._analyze_tweets(data)
                        return sentiment_data
                    else:
                        logger.error(f"X API error: {response.status}")
                        return self._get_default_x_data()
                        
        except Exception as e:
            logger.error(f"X data fetch error: {e}")
            return self._get_default_x_data()
    
    def _calculate_sentiment(self, symbol: str, grok_analysis: Dict[str, Any], x_data: Dict[str, Any]) -> SentimentSignal:
        """
        Calculate comprehensive sentiment score
        
        Args:
            symbol: Trading symbol
            grok_analysis: Grok AI analysis results
            x_data: X (Twitter) sentiment data
            
        Returns:
            SentimentSignal with calculated scores
        """
        # Extract scores
        grok_sentiment = grok_analysis.get('sentiment_score', 0)
        grok_confidence = grok_analysis.get('confidence', 50)
        
        x_sentiment = x_data.get('overall_sentiment', 0)
        social_volume = x_data.get('tweet_count', 0)
        trending_score = x_data.get('trending_score', 0)
        
        # Weighted average (Grok has higher weight due to AI analysis)
        weights = {
            'grok': 0.6,
            'x': 0.4
        }
        
        # Calculate weighted sentiment
        weighted_sentiment = (
            grok_sentiment * weights['grok'] +
            x_sentiment * weights['x']
        )
        
        # Adjust for social volume (high volume increases confidence)
        volume_factor = min(social_volume / 1000, 1.0)  # Cap at 1000 tweets
        confidence = min(100, grok_confidence * (1 + 0.2 * volume_factor))
        
        # Determine sentiment label
        sentiment_label = self._get_sentiment_label(weighted_sentiment)
        
        # Extract additional metrics
        influencer_sentiment = x_data.get('influencer_sentiment', weighted_sentiment)
        retail_sentiment = x_data.get('retail_sentiment', weighted_sentiment)
        whale_sentiment = grok_analysis.get('whale_sentiment', weighted_sentiment)
        
        # Get key topics
        key_topics = []
        if 'key_factors' in grok_analysis:
            key_topics.extend(grok_analysis['key_factors'][:3])
        if 'trending_topics' in x_data:
            key_topics.extend(x_data['trending_topics'][:2])
        
        return SentimentSignal(
            symbol=symbol,
            sentiment_score=round(weighted_sentiment, 2),
            confidence=round(confidence, 2),
            sentiment_label=sentiment_label,
            grok_sentiment=round(grok_sentiment, 2),
            x_sentiment=round(x_sentiment, 2),
            social_volume=social_volume,
            trending_score=round(trending_score, 2),
            key_topics=key_topics[:5],
            influencer_sentiment=round(influencer_sentiment, 2),
            retail_sentiment=round(retail_sentiment, 2),
            whale_sentiment=round(whale_sentiment, 2),
            timestamp=datetime.now()
        )
    
    def _analyze_tweets(self, tweet_data: Dict) -> Dict[str, Any]:
        """
        Analyze sentiment from tweet data
        
        Args:
            tweet_data: Raw tweet data from X API
            
        Returns:
            Analyzed sentiment data
        """
        if not tweet_data.get('data'):
            return self._get_default_x_data()
        
        tweets = tweet_data['data']
        users = {u['id']: u for u in tweet_data.get('includes', {}).get('users', [])}
        
        sentiments = []
        influencer_sentiments = []
        engagement_scores = []
        
        for tweet in tweets:
            # Simple sentiment analysis (can be enhanced with NLP)
            text = tweet.get('text', '').lower()
            sentiment = self._simple_text_sentiment(text)
            
            # Get engagement metrics
            metrics = tweet.get('public_metrics', {})
            engagement = (
                metrics.get('like_count', 0) * 1 +
                metrics.get('retweet_count', 0) * 2 +
                metrics.get('reply_count', 0) * 0.5
            )
            
            sentiments.append(sentiment)
            engagement_scores.append(engagement)
            
            # Check if from influencer
            author_id = tweet.get('author_id')
            if author_id in users:
                user = users[author_id]
                if user.get('verified') or user.get('public_metrics', {}).get('followers_count', 0) > 10000:
                    influencer_sentiments.append(sentiment * (1 + engagement / 1000))
        
        # Calculate overall metrics
        overall_sentiment = statistics.mean(sentiments) if sentiments else 0
        total_engagement = sum(engagement_scores)
        trending_score = min(100, total_engagement / 100)
        
        # Calculate influencer sentiment
        influencer_sentiment = statistics.mean(influencer_sentiments) if influencer_sentiments else overall_sentiment
        
        return {
            'overall_sentiment': overall_sentiment,
            'tweet_count': len(tweets),
            'trending_score': trending_score,
            'influencer_sentiment': influencer_sentiment,
            'retail_sentiment': overall_sentiment,
            'engagement_total': total_engagement,
            'trending_topics': self._extract_topics(tweets)
        }
    
    def _simple_text_sentiment(self, text: str) -> float:
        """
        Simple rule-based sentiment analysis
        
        Args:
            text: Tweet text
            
        Returns:
            Sentiment score (-100 to 100)
        """
        # Positive indicators
        positive_words = [
            'bullish', 'moon', 'pump', 'buy', 'long', 'breakout', 'rally',
            'surge', 'soar', 'rocket', 'gem', 'undervalued', 'accumulate'
        ]
        
        # Negative indicators
        negative_words = [
            'bearish', 'dump', 'sell', 'short', 'crash', 'plunge', 'drop',
            'fall', 'decline', 'overvalued', 'bubble', 'scam', 'rug'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        # Calculate sentiment
        if positive_count + negative_count == 0:
            return 0
        
        sentiment = ((positive_count - negative_count) / (positive_count + negative_count)) * 100
        return max(-100, min(100, sentiment))
    
    def _extract_topics(self, tweets: List[Dict]) -> List[str]:
        """Extract trending topics from tweets"""
        topics = []
        for tweet in tweets[:10]:  # Check first 10 tweets
            text = tweet.get('text', '')
            # Extract hashtags
            hashtags = [word for word in text.split() if word.startswith('#')]
            topics.extend(hashtags)
        
        # Return unique topics
        return list(set(topics))[:5]
    
    def _get_sentiment_label(self, score: float) -> str:
        """Get sentiment label from score"""
        if score >= 75:
            return "EXTREME_BULLISH"
        elif score >= 50:
            return "VERY_BULLISH"
        elif score >= 25:
            return "BULLISH"
        elif score >= 10:
            return "SLIGHTLY_BULLISH"
        elif score >= -10:
            return "NEUTRAL"
        elif score >= -25:
            return "SLIGHTLY_BEARISH"
        elif score >= -50:
            return "BEARISH"
        elif score >= -75:
            return "VERY_BEARISH"
        else:
            return "EXTREME_BEARISH"
    
    def _parse_text_sentiment(self, text: str) -> Dict[str, Any]:
        """Parse sentiment from text response"""
        sentiment = self._simple_text_sentiment(text.lower())
        return {
            'sentiment_score': sentiment,
            'confidence': 60,
            'key_factors': ['text_analysis'],
            'whale_sentiment': sentiment
        }
    
    def _check_rate_limit(self, service: str) -> bool:
        """Check if rate limit allows API call"""
        limit = self.rate_limiter[service]
        
        # Reset if hour passed
        if datetime.now() - limit['reset'] > timedelta(hours=1):
            limit['calls'] = 0
            limit['reset'] = datetime.now()
        
        return limit['calls'] < limit['max']
    
    def _increment_rate_limit(self, service: str):
        """Increment rate limit counter"""
        self.rate_limiter[service]['calls'] += 1
    
    def _get_default_grok_analysis(self) -> Dict[str, Any]:
        """Get default Grok analysis when API unavailable"""
        return {
            'sentiment_score': 0,
            'confidence': 30,
            'key_factors': [],
            'whale_sentiment': 0
        }
    
    def _get_default_x_data(self) -> Dict[str, Any]:
        """Get default X data when API unavailable"""
        return {
            'overall_sentiment': 0,
            'tweet_count': 0,
            'trending_score': 0,
            'influencer_sentiment': 0,
            'retail_sentiment': 0,
            'engagement_total': 0,
            'trending_topics': []
        }
    
    def _get_default_sentiment(self, symbol: str) -> SentimentSignal:
        """Get default sentiment signal"""
        return SentimentSignal(
            symbol=symbol,
            sentiment_score=0,
            confidence=0,
            sentiment_label="NEUTRAL",
            grok_sentiment=0,
            x_sentiment=0,
            social_volume=0,
            trending_score=0,
            key_topics=[],
            influencer_sentiment=0,
            retail_sentiment=0,
            whale_sentiment=0,
            timestamp=datetime.now()
        )

# Create global instance
grok_x_sentiment_agent = GrokXSentimentAgent()