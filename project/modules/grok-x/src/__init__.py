"""
Grok-X-Module: Advanced Trading Signal Generation System
========================================================

A comprehensive cryptocurrency trading signal generation system that combines
X (Twitter) social media intelligence with xAI's Grok artificial intelligence
to provide advanced market sentiment analysis and trading signals.

Key Features:
- Real-time social media sentiment analysis
- AI-powered market intelligence with Grok
- Advanced trading signal generation
- Influencer tracking and analysis
- Risk assessment and management
- Comprehensive monitoring and alerting

Quick Start:
-----------
```python
import asyncio
from grok_x_module import analyze_crypto_market

async def main():
    result = await analyze_crypto_market(['BTC', 'ETH'])
    print(f"Sentiment: {result.sentiment_analysis.overall_sentiment}")
    for signal in result.trading_signals:
        print(f"{signal.symbol}: {signal.signal_type.value}")

asyncio.run(main())
```

Author: Manus AI
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Manus AI"
__license__ = "MIT"

# Core imports
from .core.grok_x_engine import (
    GrokXEngine,
    AnalysisRequest,
    AnalysisResult,
    analyze_crypto_market,
    get_crypto_signals,
    monitor_crypto_sentiment
)

# Integration clients
from .integrations.x_api_client import (
    XAPIClient,
    Tweet,
    User,
    SearchResult,
    search_crypto_sentiment,
    monitor_crypto_influencers,
    get_trending_crypto
)

from .integrations.grok_ai_client import (
    GrokAIClient,
    SentimentAnalysis,
    TradingSignal,
    MarketAnalysis,
    analyze_social_sentiment,
    generate_signals_from_sentiment
)

# Analysis components
from .analysis.sentiment_analyzer import (
    AdvancedSentimentAnalyzer,
    SentimentScore,
    AuthorCredibility,
    analyze_crypto_sentiment,
    calculate_sentiment_trend
)

# Signal generation
from .signals.signal_generator import (
    AdvancedSignalGenerator,
    EnhancedTradingSignal,
    SignalStrength,
    RiskLevel,
    generate_crypto_signals,
    filter_signals_by_confidence,
    rank_signals_by_strength
)

# Configuration
from .config.settings.config import (
    get_config,
    load_config,
    SignalType,
    LogLevel
)

# Utilities
from .utils.rate_limiter import (
    RateLimiter,
    AdaptiveRateLimiter,
    TokenBucketRateLimiter,
    create_rate_limiter
)

from .utils.retry_handler import (
    RetryHandler,
    RetryStrategy,
    CircuitBreaker,
    retry,
    create_api_retry_handler
)

# Export main classes and functions
__all__ = [
    # Core engine
    'GrokXEngine',
    'AnalysisRequest',
    'AnalysisResult',
    'analyze_crypto_market',
    'get_crypto_signals',
    'monitor_crypto_sentiment',
    
    # API clients
    'XAPIClient',
    'GrokAIClient',
    'Tweet',
    'User',
    'SearchResult',
    'SentimentAnalysis',
    'TradingSignal',
    'MarketAnalysis',
    
    # Analysis
    'AdvancedSentimentAnalyzer',
    'SentimentScore',
    'AuthorCredibility',
    'analyze_crypto_sentiment',
    
    # Signal generation
    'AdvancedSignalGenerator',
    'EnhancedTradingSignal',
    'SignalStrength',
    'RiskLevel',
    'generate_crypto_signals',
    
    # Configuration
    'get_config',
    'load_config',
    'SignalType',
    'LogLevel',
    
    # Utilities
    'RateLimiter',
    'RetryHandler',
    'RetryStrategy',
    'retry'
]


def get_version():
    """Get module version"""
    return __version__


def get_info():
    """Get module information"""
    return {
        'name': 'Grok-X-Module',
        'version': __version__,
        'author': __author__,
        'license': __license__,
        'description': 'Advanced cryptocurrency trading signal generation system',
        'features': [
            'Real-time social media sentiment analysis',
            'AI-powered market intelligence with Grok',
            'Advanced trading signal generation',
            'Influencer tracking and analysis',
            'Risk assessment and management',
            'Comprehensive monitoring and alerting'
        ]
    }


# Module-level configuration
import logging

# Setup default logging
logging.getLogger('grok_x_module').addHandler(logging.NullHandler())

# Version check
import sys
if sys.version_info < (3, 8):
    raise RuntimeError("Grok-X-Module requires Python 3.8 or higher")

# Optional dependency checks
try:
    import aiohttp
except ImportError:
    raise ImportError("aiohttp is required. Install with: pip install aiohttp")

try:
    import cryptography
except ImportError:
    raise ImportError("cryptography is required. Install with: pip install cryptography")

# Welcome message
def _show_welcome():
    """Show welcome message on first import"""
    print("🚀 Grok-X-Module v{} loaded successfully!".format(__version__))
    print("   Advanced cryptocurrency trading signal generation system")
    print("   Ready for market analysis and signal generation.")

# Show welcome message only in interactive mode
if hasattr(sys, 'ps1'):
    _show_welcome()

