"""
Grok AI Integration Client
Advanced integration with xAI's Grok for market analysis and signal generation
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import re

from ..utils.rate_limiter import RateLimiter
from ..utils.retry_handler import RetryHandler
from ...config.credentials.api_credentials import get_grok_credentials
from ...config.settings.config import get_config


class AnalysisType(Enum):
    """Types of analysis supported by Grok"""
    SENTIMENT = "sentiment"
    SIGNAL_GENERATION = "signal_generation"
    MARKET_ANALYSIS = "market_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    TREND_PREDICTION = "trend_prediction"


@dataclass
class SentimentAnalysis:
    """Sentiment analysis result structure"""
    overall_sentiment: float  # -1 to 1
    confidence: float  # 0 to 1
    individual_sentiments: List[Dict[str, Any]]
    key_insights: List[str]
    market_implications: str
    analysis_timestamp: datetime = None
    
    def __post_init__(self):
        if self.analysis_timestamp is None:
            self.analysis_timestamp = datetime.now()
    
    @property
    def sentiment_label(self) -> str:
        """Get human-readable sentiment label"""
        if self.overall_sentiment >= 0.6:
            return "Very Bullish"
        elif self.overall_sentiment >= 0.2:
            return "Bullish"
        elif self.overall_sentiment >= -0.2:
            return "Neutral"
        elif self.overall_sentiment >= -0.6:
            return "Bearish"
        else:
            return "Very Bearish"


@dataclass
class TradingSignal:
    """Trading signal structure"""
    symbol: str
    signal_type: str  # BUY, SELL, HOLD, STRONG_BUY, STRONG_SELL
    confidence: float
    reasoning: str
    risk_level: str
    time_horizon: str
    entry_price_range: Dict[str, float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    generated_at: datetime = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()


@dataclass
class MarketAnalysis:
    """Comprehensive market analysis result"""
    signals: List[TradingSignal]
    market_overview: str
    risk_factors: List[str]
    sentiment_summary: Optional[SentimentAnalysis] = None
    analysis_timestamp: datetime = None
    
    def __post_init__(self):
        if self.analysis_timestamp is None:
            self.analysis_timestamp = datetime.now()


@dataclass
class GrokRequest:
    """Grok API request structure"""
    model: str
    messages: List[Dict[str, str]]
    max_tokens: int
    temperature: float
    top_p: float
    stream: bool = False


class GrokAIClient:
    """Comprehensive Grok AI client for market analysis"""
    
    def __init__(self):
        """Initialize Grok AI client"""
        self.credentials = get_grok_credentials()
        self.config = get_config().grok
        self.logger = logging.getLogger(__name__)
        
        # Rate limiter for Grok API
        self.rate_limiter = RateLimiter(
            requests_per_minute=60,  # Conservative estimate
            requests_per_hour=1000
        )
        
        self.retry_handler = RetryHandler(max_retries=3, base_delay=2.0)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_session()
    
    async def initialize_session(self):
        """Initialize HTTP session"""
        headers = {
            "Authorization": f"Bearer {self.credentials.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "GrokXModule/1.0"
        }
        
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=10)
        )
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, request_data: GrokRequest) -> Dict[str, Any]:
        """Make authenticated request to Grok API"""
        
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        url = f"{self.credentials.base_url}/chat/completions"
        
        async def _request():
            async with self.session.post(url, json=asdict(request_data)) as response:
                return await self._handle_response(response)
        
        return await self.retry_handler.execute(_request)
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle API response and errors"""
        if response.status == 200:
            return await response.json()
        elif response.status == 429:
            # Rate limit exceeded
            self.logger.warning("Grok API rate limit exceeded")
            await asyncio.sleep(60)
            raise Exception("Rate limit exceeded")
        else:
            error_text = await response.text()
            self.logger.error(f"Grok API request failed: {response.status} - {error_text}")
            raise Exception(f"Grok API request failed: {response.status} - {error_text}")
    
    def _extract_json_from_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from Grok response text"""
        try:
            # Try to parse the entire response as JSON
            return json.loads(text)
        except json.JSONDecodeError:
            # Look for JSON blocks in the response
            json_pattern = r'```json\s*(.*?)\s*```'
            matches = re.findall(json_pattern, text, re.DOTALL)
            
            if matches:
                try:
                    return json.loads(matches[0])
                except json.JSONDecodeError:
                    pass
            
            # Look for JSON objects without code blocks
            json_pattern = r'\{.*\}'
            matches = re.findall(json_pattern, text, re.DOTALL)
            
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
            
            self.logger.warning(f"Could not extract JSON from response: {text[:200]}...")
            return None
    
    async def analyze_sentiment(
        self,
        posts: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> SentimentAnalysis:
        """Analyze sentiment of social media posts"""
        
        # Prepare posts data for analysis
        posts_text = []
        for i, post in enumerate(posts):
            post_text = f"Post {i+1}: {post.get('text', '')}"
            if 'author' in post:
                post_text += f" (by @{post['author']})"
            if 'engagement' in post:
                post_text += f" [Engagement: {post['engagement']}]"
            posts_text.append(post_text)
        
        posts_content = "\n\n".join(posts_text)
        
        # Build prompt with context
        prompt = self.config.sentiment_analysis_prompt.format(posts=posts_content)
        if context:
            prompt += f"\n\nAdditional Context: {context}"
        
        request = GrokRequest(
            model=self.config.model,
            messages=[
                {"role": "system", "content": "You are an expert cryptocurrency market analyst specializing in social sentiment analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p
        )
        
        self.logger.info(f"Analyzing sentiment for {len(posts)} posts")
        
        try:
            response = await self._make_request(request)
            
            if 'choices' in response and response['choices']:
                content = response['choices'][0]['message']['content']
                
                # Extract JSON from response
                analysis_data = self._extract_json_from_response(content)
                
                if analysis_data:
                    return SentimentAnalysis(
                        overall_sentiment=analysis_data.get('overall_sentiment', 0.0),
                        confidence=analysis_data.get('confidence', 0.0),
                        individual_sentiments=analysis_data.get('individual_sentiments', []),
                        key_insights=analysis_data.get('key_insights', []),
                        market_implications=analysis_data.get('market_implications', '')
                    )
                else:
                    # Fallback: create analysis from raw text
                    return SentimentAnalysis(
                        overall_sentiment=0.0,
                        confidence=0.5,
                        individual_sentiments=[],
                        key_insights=[content[:200] + "..."],
                        market_implications=content
                    )
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            
        # Return neutral sentiment on failure
        return SentimentAnalysis(
            overall_sentiment=0.0,
            confidence=0.0,
            individual_sentiments=[],
            key_insights=["Analysis failed"],
            market_implications="Unable to analyze sentiment"
        )
    
    async def generate_trading_signals(
        self,
        sentiment_data: SentimentAnalysis,
        market_context: Optional[Dict[str, Any]] = None,
        historical_data: Optional[Dict[str, Any]] = None,
        symbols: Optional[List[str]] = None
    ) -> MarketAnalysis:
        """Generate trading signals based on sentiment and market data"""
        
        # Prepare context data
        context_parts = []
        
        # Add sentiment data
        context_parts.append(f"Sentiment Analysis:")
        context_parts.append(f"- Overall Sentiment: {sentiment_data.overall_sentiment:.2f} ({sentiment_data.sentiment_label})")
        context_parts.append(f"- Confidence: {sentiment_data.confidence:.2f}")
        context_parts.append(f"- Key Insights: {', '.join(sentiment_data.key_insights)}")
        context_parts.append(f"- Market Implications: {sentiment_data.market_implications}")
        
        # Add market context
        if market_context:
            context_parts.append(f"\nMarket Context:")
            for key, value in market_context.items():
                context_parts.append(f"- {key}: {value}")
        
        # Add historical data
        if historical_data:
            context_parts.append(f"\nHistorical Data:")
            for key, value in historical_data.items():
                context_parts.append(f"- {key}: {value}")
        
        # Add target symbols
        if symbols:
            context_parts.append(f"\nTarget Symbols: {', '.join(symbols)}")
        
        context_text = "\n".join(context_parts)
        
        # Build signal generation prompt
        prompt = self.config.signal_generation_prompt.format(
            sentiment_data=context_text,
            market_context=market_context or {},
            historical_data=historical_data or {}
        )
        
        request = GrokRequest(
            model=self.config.model,
            messages=[
                {"role": "system", "content": "You are an expert cryptocurrency trading analyst. Generate precise, actionable trading signals based on comprehensive market analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p
        )
        
        self.logger.info("Generating trading signals based on sentiment analysis")
        
        try:
            response = await self._make_request(request)
            
            if 'choices' in response and response['choices']:
                content = response['choices'][0]['message']['content']
                
                # Extract JSON from response
                signal_data = self._extract_json_from_response(content)
                
                if signal_data:
                    # Parse signals
                    signals = []
                    for signal_info in signal_data.get('signals', []):
                        signal = TradingSignal(
                            symbol=signal_info.get('symbol', 'UNKNOWN'),
                            signal_type=signal_info.get('signal_type', 'HOLD'),
                            confidence=signal_info.get('confidence', 0.5),
                            reasoning=signal_info.get('reasoning', ''),
                            risk_level=signal_info.get('risk_level', 'MEDIUM'),
                            time_horizon=signal_info.get('time_horizon', 'SHORT'),
                            entry_price_range=signal_info.get('entry_price_range', {'min': 0, 'max': 0}),
                            stop_loss=signal_info.get('stop_loss'),
                            take_profit=signal_info.get('take_profit')
                        )
                        signals.append(signal)
                    
                    return MarketAnalysis(
                        signals=signals,
                        market_overview=signal_data.get('market_overview', ''),
                        risk_factors=signal_data.get('risk_factors', []),
                        sentiment_summary=sentiment_data
                    )
                else:
                    # Fallback: create basic analysis from raw text
                    return MarketAnalysis(
                        signals=[],
                        market_overview=content,
                        risk_factors=["Unable to parse structured signals"],
                        sentiment_summary=sentiment_data
                    )
            
        except Exception as e:
            self.logger.error(f"Signal generation failed: {e}")
        
        # Return empty analysis on failure
        return MarketAnalysis(
            signals=[],
            market_overview="Signal generation failed",
            risk_factors=["Analysis error"],
            sentiment_summary=sentiment_data
        )
    
    async def analyze_market_trends(
        self,
        data_points: List[Dict[str, Any]],
        timeframe: str = "24h"
    ) -> Dict[str, Any]:
        """Analyze market trends and patterns"""
        
        # Prepare data summary
        data_summary = []
        for point in data_points:
            summary = f"- {point.get('timestamp', 'Unknown time')}: {point.get('description', 'No description')}"
            if 'metrics' in point:
                summary += f" (Metrics: {point['metrics']})"
            data_summary.append(summary)
        
        data_text = "\n".join(data_summary)
        
        prompt = f"""
        Analyze the following market trend data for cryptocurrency markets over the {timeframe} timeframe.
        Identify patterns, anomalies, and potential future movements.
        
        Data Points:
        {data_text}
        
        Provide analysis in the following format:
        {{
            "trend_direction": "bullish/bearish/neutral",
            "trend_strength": float (0-1),
            "key_patterns": [list of identified patterns],
            "anomalies": [list of unusual observations],
            "predictions": {{
                "short_term": "prediction for next 4-6 hours",
                "medium_term": "prediction for next 24-48 hours",
                "confidence": float (0-1)
            }},
            "supporting_evidence": [list of evidence points]
        }}
        """
        
        request = GrokRequest(
            model=self.config.model,
            messages=[
                {"role": "system", "content": "You are an expert technical analyst specializing in cryptocurrency market trends and pattern recognition."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.config.max_tokens,
            temperature=0.2,  # Lower temperature for more consistent analysis
            top_p=self.config.top_p
        )
        
        try:
            response = await self._make_request(request)
            
            if 'choices' in response and response['choices']:
                content = response['choices'][0]['message']['content']
                analysis_data = self._extract_json_from_response(content)
                
                if analysis_data:
                    return analysis_data
                else:
                    return {
                        "trend_direction": "neutral",
                        "trend_strength": 0.5,
                        "key_patterns": [],
                        "anomalies": [],
                        "predictions": {
                            "short_term": content[:100] + "...",
                            "medium_term": "Unable to generate prediction",
                            "confidence": 0.3
                        },
                        "supporting_evidence": []
                    }
        
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            return {
                "trend_direction": "neutral",
                "trend_strength": 0.0,
                "key_patterns": [],
                "anomalies": [],
                "predictions": {
                    "short_term": "Analysis failed",
                    "medium_term": "Analysis failed",
                    "confidence": 0.0
                },
                "supporting_evidence": []
            }
    
    async def assess_risk(
        self,
        signals: List[TradingSignal],
        market_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risk for trading signals"""
        
        # Prepare signals summary
        signals_summary = []
        for signal in signals:
            summary = f"- {signal.symbol}: {signal.signal_type} (Confidence: {signal.confidence:.2f}, Risk: {signal.risk_level})"
            summary += f"\n  Reasoning: {signal.reasoning}"
            signals_summary.append(summary)
        
        signals_text = "\n".join(signals_summary)
        
        # Prepare market conditions
        conditions_text = "\n".join([f"- {k}: {v}" for k, v in market_conditions.items()])
        
        prompt = f"""
        Assess the risk profile for the following trading signals given current market conditions.
        
        Trading Signals:
        {signals_text}
        
        Market Conditions:
        {conditions_text}
        
        Provide risk assessment in the following format:
        {{
            "overall_risk_level": "LOW/MEDIUM/HIGH/CRITICAL",
            "risk_score": float (0-1),
            "individual_signal_risks": [
                {{
                    "symbol": "symbol",
                    "risk_level": "LOW/MEDIUM/HIGH",
                    "risk_factors": [list of specific risks],
                    "mitigation_strategies": [list of risk mitigation approaches]
                }}
            ],
            "market_risks": [list of broader market risks],
            "recommendations": [list of risk management recommendations]
        }}
        """
        
        request = GrokRequest(
            model=self.config.model,
            messages=[
                {"role": "system", "content": "You are an expert risk management analyst specializing in cryptocurrency trading risk assessment."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.config.max_tokens,
            temperature=0.1,  # Very low temperature for consistent risk assessment
            top_p=self.config.top_p
        )
        
        try:
            response = await self._make_request(request)
            
            if 'choices' in response and response['choices']:
                content = response['choices'][0]['message']['content']
                risk_data = self._extract_json_from_response(content)
                
                if risk_data:
                    return risk_data
                else:
                    return {
                        "overall_risk_level": "MEDIUM",
                        "risk_score": 0.5,
                        "individual_signal_risks": [],
                        "market_risks": ["Unable to assess specific risks"],
                        "recommendations": ["Exercise caution", "Use proper position sizing"]
                    }
        
        except Exception as e:
            self.logger.error(f"Risk assessment failed: {e}")
            return {
                "overall_risk_level": "HIGH",
                "risk_score": 0.8,
                "individual_signal_risks": [],
                "market_risks": ["Analysis system error"],
                "recommendations": ["Avoid trading until system is restored"]
            }


# Utility functions for easy access
async def analyze_social_sentiment(posts: List[Dict[str, Any]]) -> SentimentAnalysis:
    """Convenience function for sentiment analysis"""
    async with GrokAIClient() as client:
        return await client.analyze_sentiment(posts)


async def generate_signals_from_sentiment(
    sentiment: SentimentAnalysis,
    symbols: List[str]
) -> MarketAnalysis:
    """Convenience function for signal generation"""
    async with GrokAIClient() as client:
        return await client.generate_trading_signals(
            sentiment_data=sentiment,
            symbols=symbols
        )

