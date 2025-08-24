"""
Grok-X-Module Main Engine
Central orchestrator for the advanced trading signal generation system
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

from ..integrations.x_api_client import XAPIClient, SearchResult
from ..integrations.grok_ai_client import GrokAIClient, SentimentAnalysis
from ..analysis.sentiment_analyzer import AdvancedSentimentAnalyzer
from ..signals.signal_generator import AdvancedSignalGenerator, EnhancedTradingSignal
from ...config.settings.config import get_config


@dataclass
class AnalysisRequest:
    """Request for market analysis"""
    symbols: List[str]
    keywords: Optional[List[str]] = None
    time_window_hours: int = 24
    max_tweets: int = 100
    include_influencers: bool = True
    analysis_depth: str = "comprehensive"  # "basic", "standard", "comprehensive"


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    request: AnalysisRequest
    sentiment_analysis: SentimentAnalysis
    trading_signals: List[EnhancedTradingSignal]
    social_data: SearchResult
    market_context: Dict[str, Any]
    analysis_timestamp: datetime
    processing_time_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'request': asdict(self.request),
            'sentiment_analysis': {
                'overall_sentiment': self.sentiment_analysis.overall_sentiment,
                'confidence': self.sentiment_analysis.confidence,
                'sentiment_label': self.sentiment_analysis.sentiment_label,
                'key_insights': self.sentiment_analysis.key_insights,
                'market_implications': self.sentiment_analysis.market_implications,
                'individual_count': len(self.sentiment_analysis.individual_sentiments)
            },
            'trading_signals': [
                {
                    'symbol': signal.symbol,
                    'signal_type': signal.signal_type.value,
                    'strength': signal.strength.value,
                    'confidence': signal.confidence,
                    'risk_level': signal.risk_level.value,
                    'reasoning': signal.reasoning,
                    'time_horizon': signal.time_horizon,
                    'entry_range': signal.entry_price_range,
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.take_profit,
                    'expires_at': signal.expires_at.isoformat()
                }
                for signal in self.trading_signals
            ],
            'social_metrics': {
                'tweet_count': len(self.social_data.tweets),
                'user_count': len(self.social_data.users),
                'avg_engagement': sum(t.engagement_score for t in self.social_data.tweets) / max(len(self.social_data.tweets), 1),
                'verified_users': sum(1 for u in self.social_data.users.values() if u.verified)
            },
            'market_context': self.market_context,
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'processing_time_seconds': self.processing_time_seconds
        }


class GrokXEngine:
    """Main engine for the Grok-X-Module trading signal system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Grok-X-Module engine"""
        
        # Load configuration
        if config_path:
            self.config = get_config().from_file(config_path)
        else:
            self.config = get_config()
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize components
        self.x_client: Optional[XAPIClient] = None
        self.grok_client: Optional[GrokAIClient] = None
        self.sentiment_analyzer: Optional[AdvancedSentimentAnalyzer] = None
        self.signal_generator: Optional[AdvancedSignalGenerator] = None
        
        # Analysis cache
        self.analysis_cache: Dict[str, AnalysisResult] = {}
        self.cache_ttl_seconds = 1800  # 30 minutes
        
        # Performance metrics
        self.metrics = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'cache_hits': 0,
            'average_processing_time': 0.0
        }
        
        self.logger.info("Grok-X-Module engine initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('grok_x_engine')
        logger.setLevel(getattr(logging, self.config.monitoring.log_level.value))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = Path(self.config.monitoring.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
    
    async def initialize(self):
        """Initialize all components"""
        self.logger.info("Initializing Grok-X-Module components...")
        
        try:
            # Initialize X API client
            self.x_client = XAPIClient()
            await self.x_client.initialize_session()
            
            # Initialize Grok AI client
            self.grok_client = GrokAIClient()
            await self.grok_client.initialize_session()
            
            # Initialize sentiment analyzer
            self.sentiment_analyzer = AdvancedSentimentAnalyzer()
            await self.sentiment_analyzer.__aenter__()
            
            # Initialize signal generator
            self.signal_generator = AdvancedSignalGenerator()
            await self.signal_generator.__aenter__()
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            await self.cleanup()
            raise
    
    async def cleanup(self):
        """Cleanup all components"""
        self.logger.info("Cleaning up Grok-X-Module components...")
        
        if self.signal_generator:
            await self.signal_generator.__aexit__(None, None, None)
        
        if self.sentiment_analyzer:
            await self.sentiment_analyzer.__aexit__(None, None, None)
        
        if self.grok_client:
            await self.grok_client.close_session()
        
        if self.x_client:
            await self.x_client.close_session()
    
    def _generate_cache_key(self, request: AnalysisRequest) -> str:
        """Generate cache key for analysis request"""
        key_data = {
            'symbols': sorted(request.symbols),
            'keywords': sorted(request.keywords) if request.keywords else [],
            'time_window': request.time_window_hours,
            'max_tweets': request.max_tweets,
            'include_influencers': request.include_influencers,
            'analysis_depth': request.analysis_depth
        }
        return json.dumps(key_data, sort_keys=True)
    
    def _is_cache_valid(self, result: AnalysisResult) -> bool:
        """Check if cached result is still valid"""
        age_seconds = (datetime.now() - result.analysis_timestamp).total_seconds()
        return age_seconds < self.cache_ttl_seconds
    
    async def analyze_market_sentiment(self, request: AnalysisRequest) -> AnalysisResult:
        """Perform comprehensive market sentiment analysis"""
        
        start_time = datetime.now()
        self.metrics['total_analyses'] += 1
        
        # Check cache first
        cache_key = self._generate_cache_key(request)
        if cache_key in self.analysis_cache:
            cached_result = self.analysis_cache[cache_key]
            if self._is_cache_valid(cached_result):
                self.metrics['cache_hits'] += 1
                self.logger.info(f"Returning cached analysis for {request.symbols}")
                return cached_result
            else:
                # Remove expired cache entry
                del self.analysis_cache[cache_key]
        
        try:
            self.logger.info(f"Starting market analysis for symbols: {request.symbols}")
            
            # Collect social media data
            social_data = await self._collect_social_data(request)
            
            # Perform sentiment analysis
            sentiment_analysis = await self.sentiment_analyzer.analyze_comprehensive_sentiment(social_data)
            
            # Generate trading signals
            trading_signals = await self.signal_generator.generate_ai_enhanced_signals(
                social_data, request.symbols
            )
            
            # Gather market context
            market_context = await self._gather_market_context(request, social_data)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = AnalysisResult(
                request=request,
                sentiment_analysis=sentiment_analysis,
                trading_signals=trading_signals,
                social_data=social_data,
                market_context=market_context,
                analysis_timestamp=start_time,
                processing_time_seconds=processing_time
            )
            
            # Cache result
            self.analysis_cache[cache_key] = result
            
            # Update metrics
            self.metrics['successful_analyses'] += 1
            self._update_average_processing_time(processing_time)
            
            self.logger.info(
                f"Analysis completed for {request.symbols} in {processing_time:.2f}s. "
                f"Generated {len(trading_signals)} signals with sentiment {sentiment_analysis.overall_sentiment:.2f}"
            )
            
            return result
            
        except Exception as e:
            self.metrics['failed_analyses'] += 1
            self.logger.error(f"Analysis failed for {request.symbols}: {e}")
            raise
    
    async def _collect_social_data(self, request: AnalysisRequest) -> SearchResult:
        """Collect social media data based on request"""
        
        # Search for crypto-related tweets
        search_result = await self.x_client.search_crypto_tweets(
            symbols=request.symbols,
            keywords=request.keywords,
            max_results=request.max_tweets,
            time_window_hours=request.time_window_hours
        )
        
        # Include influencer data if requested
        if request.include_influencers:
            influencer_data = await self.x_client.monitor_influencers()
            
            # Merge influencer tweets with search results
            for username, influencer_result in influencer_data.items():
                search_result.tweets.extend(influencer_result.tweets)
                search_result.users.update(influencer_result.users)
        
        # Get trending content for additional context
        if request.analysis_depth == "comprehensive":
            trending_result = await self.x_client.get_trending_crypto_content()
            
            # Add high-engagement trending content
            search_result.tweets.extend(trending_result.tweets[:20])  # Top 20 trending
            search_result.users.update(trending_result.users)
        
        self.logger.info(f"Collected {len(search_result.tweets)} tweets from {len(search_result.users)} users")
        
        return search_result
    
    async def _gather_market_context(self, request: AnalysisRequest, social_data: SearchResult) -> Dict[str, Any]:
        """Gather additional market context"""
        
        context = {
            'analysis_request': asdict(request),
            'data_collection': {
                'tweet_count': len(social_data.tweets),
                'user_count': len(social_data.users),
                'time_range': f"{request.time_window_hours} hours",
                'collection_timestamp': datetime.now().isoformat()
            },
            'social_metrics': {
                'total_engagement': sum(tweet.engagement_score for tweet in social_data.tweets),
                'verified_users': sum(1 for user in social_data.users.values() if user.verified),
                'avg_follower_count': sum(user.follower_count for user in social_data.users.values()) / max(len(social_data.users), 1)
            }
        }
        
        # Add trending topics if available
        if social_data.meta:
            context['trending_info'] = social_data.meta
        
        return context
    
    def _update_average_processing_time(self, processing_time: float):
        """Update average processing time metric"""
        current_avg = self.metrics['average_processing_time']
        total_successful = self.metrics['successful_analyses']
        
        if total_successful == 1:
            self.metrics['average_processing_time'] = processing_time
        else:
            # Calculate running average
            self.metrics['average_processing_time'] = (
                (current_avg * (total_successful - 1) + processing_time) / total_successful
            )
    
    async def get_quick_sentiment(self, symbols: List[str]) -> Dict[str, float]:
        """Get quick sentiment scores for symbols"""
        
        request = AnalysisRequest(
            symbols=symbols,
            time_window_hours=6,
            max_tweets=50,
            include_influencers=False,
            analysis_depth="basic"
        )
        
        try:
            result = await self.analyze_market_sentiment(request)
            return {
                'overall_sentiment': result.sentiment_analysis.overall_sentiment,
                'confidence': result.sentiment_analysis.confidence,
                'signal_count': len(result.trading_signals)
            }
        except Exception as e:
            self.logger.error(f"Quick sentiment analysis failed: {e}")
            return {'overall_sentiment': 0.0, 'confidence': 0.0, 'signal_count': 0}
    
    async def monitor_symbols_continuously(
        self,
        symbols: List[str],
        interval_minutes: int = 30,
        callback: Optional[callable] = None
    ):
        """Continuously monitor symbols and generate signals"""
        
        self.logger.info(f"Starting continuous monitoring for {symbols} every {interval_minutes} minutes")
        
        while True:
            try:
                request = AnalysisRequest(
                    symbols=symbols,
                    time_window_hours=2,  # Shorter window for continuous monitoring
                    max_tweets=100,
                    include_influencers=True,
                    analysis_depth="standard"
                )
                
                result = await self.analyze_market_sentiment(request)
                
                # Call callback if provided
                if callback:
                    await callback(result)
                
                # Log monitoring update
                self.logger.info(
                    f"Monitoring update: {len(result.trading_signals)} signals, "
                    f"sentiment: {result.sentiment_analysis.overall_sentiment:.2f}"
                )
                
                # Wait for next interval
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get engine performance metrics"""
        
        success_rate = 0.0
        if self.metrics['total_analyses'] > 0:
            success_rate = self.metrics['successful_analyses'] / self.metrics['total_analyses']
        
        cache_hit_rate = 0.0
        if self.metrics['total_analyses'] > 0:
            cache_hit_rate = self.metrics['cache_hits'] / self.metrics['total_analyses']
        
        return {
            **self.metrics,
            'success_rate': success_rate,
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self.analysis_cache)
        }
    
    def clear_cache(self):
        """Clear analysis cache"""
        self.analysis_cache.clear()
        self.logger.info("Analysis cache cleared")
    
    async def save_analysis_result(self, result: AnalysisResult, file_path: str):
        """Save analysis result to file"""
        
        try:
            result_dict = result.to_dict()
            
            with open(file_path, 'w') as f:
                json.dump(result_dict, f, indent=2, default=str)
            
            self.logger.info(f"Analysis result saved to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save analysis result: {e}")
            raise


# Convenience functions for easy usage
async def analyze_crypto_market(symbols: List[str], **kwargs) -> AnalysisResult:
    """Convenience function for crypto market analysis"""
    
    request = AnalysisRequest(symbols=symbols, **kwargs)
    
    async with GrokXEngine() as engine:
        return await engine.analyze_market_sentiment(request)


async def get_crypto_signals(symbols: List[str]) -> List[EnhancedTradingSignal]:
    """Convenience function to get trading signals"""
    
    result = await analyze_crypto_market(symbols)
    return result.trading_signals


async def monitor_crypto_sentiment(symbols: List[str]) -> Dict[str, float]:
    """Convenience function for sentiment monitoring"""
    
    async with GrokXEngine() as engine:
        return await engine.get_quick_sentiment(symbols)

