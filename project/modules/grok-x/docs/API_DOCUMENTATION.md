# Grok-X-Module API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Core Engine API](#core-engine-api)
4. [Sentiment Analysis API](#sentiment-analysis-api)
5. [Signal Generation API](#signal-generation-api)
6. [Monitoring and Alerts API](#monitoring-and-alerts-api)
7. [Web Dashboard API](#web-dashboard-api)
8. [Data Models](#data-models)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)
11. [Examples](#examples)

## Overview

The Grok-X-Module provides both programmatic APIs for direct integration and RESTful web APIs through the dashboard interface. This documentation covers all available APIs, their parameters, responses, and usage examples.

### API Types

- **Python API**: Direct integration with the Grok-X-Module classes and functions
- **REST API**: HTTP-based API provided by the web dashboard
- **WebSocket API**: Real-time streaming API for live updates

### Base URLs

- **Local Development**: `http://localhost:5000`
- **Production**: `https://your-domain.com` (when deployed)

## Authentication

### Python API Authentication

The Python API uses API credentials configured in the system:

```python
# Credentials are loaded from config/credentials/api_credentials.py
from grok_x_module import GrokXEngine

# No additional authentication needed for Python API
async with GrokXEngine() as engine:
    result = await engine.analyze_market_sentiment(request)
```

### REST API Authentication

The REST API supports multiple authentication methods:

```python
import requests

# API Key Authentication (recommended)
headers = {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
}

response = requests.post(
    'http://localhost:5000/api/grok-x/analyze',
    headers=headers,
    json=request_data
)
```

## Core Engine API

### GrokXEngine Class

The main engine class that orchestrates all system components.

#### Constructor

```python
class GrokXEngine:
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the Grok-X Engine.
        
        Args:
            config: Optional custom configuration. Uses default if None.
        """
```

#### Context Manager Usage

```python
async with GrokXEngine() as engine:
    # Engine is initialized and ready for use
    result = await engine.analyze_market_sentiment(request)
    # Engine is automatically cleaned up
```

### analyze_market_sentiment

Perform comprehensive market sentiment analysis.

```python
async def analyze_market_sentiment(
    self, 
    request: AnalysisRequest
) -> AnalysisResult:
    """
    Analyze market sentiment for specified symbols.
    
    Args:
        request: Analysis configuration and parameters
        
    Returns:
        AnalysisResult: Comprehensive analysis results
        
    Raises:
        ValueError: Invalid request parameters
        APIError: External API communication error
        RateLimitError: Rate limit exceeded
    """
```

**Example:**

```python
from grok_x_module import GrokXEngine, AnalysisRequest

request = AnalysisRequest(
    symbols=['BTC', 'ETH'],
    keywords=['bitcoin', 'ethereum', 'crypto'],
    time_window_hours=24,
    max_tweets=100,
    include_influencers=True,
    analysis_depth='comprehensive'
)

async with GrokXEngine() as engine:
    result = await engine.analyze_market_sentiment(request)
    
    print(f"Sentiment: {result.sentiment_analysis.overall_sentiment}")
    print(f"Signals: {len(result.trading_signals)}")
```

### get_quick_sentiment

Get quick sentiment analysis for symbols.

```python
async def get_quick_sentiment(
    self, 
    symbols: List[str],
    time_window_hours: int = 6
) -> Dict[str, Any]:
    """
    Get quick sentiment analysis for symbols.
    
    Args:
        symbols: List of cryptocurrency symbols
        time_window_hours: Analysis time window
        
    Returns:
        Dict containing sentiment metrics
    """
```

**Example:**

```python
async with GrokXEngine() as engine:
    sentiment = await engine.get_quick_sentiment(['BTC', 'ETH'])
    
    print(f"Overall sentiment: {sentiment['overall_sentiment']}")
    print(f"Confidence: {sentiment['confidence']}")
```

### monitor_symbols_continuously

Start continuous monitoring of symbols.

```python
async def monitor_symbols_continuously(
    self,
    symbols: List[str],
    interval_minutes: int = 30,
    callback: Optional[Callable] = None
) -> None:
    """
    Monitor symbols continuously with periodic analysis.
    
    Args:
        symbols: List of symbols to monitor
        interval_minutes: Analysis interval in minutes
        callback: Optional callback function for results
    """
```

**Example:**

```python
async def handle_results(result):
    for signal in result.trading_signals:
        if signal.confidence > 0.8:
            print(f"High confidence signal: {signal.symbol}")

async with GrokXEngine() as engine:
    await engine.monitor_symbols_continuously(
        symbols=['BTC', 'ETH'],
        interval_minutes=15,
        callback=handle_results
    )
```

### get_performance_metrics

Get system performance metrics.

```python
def get_performance_metrics(self) -> Dict[str, Any]:
    """
    Get system performance metrics.
    
    Returns:
        Dict containing performance statistics
    """
```

**Example:**

```python
engine = GrokXEngine()
metrics = engine.get_performance_metrics()

print(f"Total analyses: {metrics['total_analyses']}")
print(f"Success rate: {metrics['success_rate']:.2%}")
print(f"Cache hit rate: {metrics['cache_hit_rate']:.2%}")
```

## Sentiment Analysis API

### AdvancedSentimentAnalyzer Class

Advanced sentiment analysis with credibility weighting.

#### analyze_comprehensive_sentiment

```python
async def analyze_comprehensive_sentiment(
    self,
    search_result: SearchResult,
    market_context: Optional[Dict] = None
) -> SentimentAnalysis:
    """
    Perform comprehensive sentiment analysis.
    
    Args:
        search_result: Social media search results
        market_context: Optional market context data
        
    Returns:
        SentimentAnalysis: Detailed sentiment analysis results
    """
```

**Example:**

```python
from grok_x_module import AdvancedSentimentAnalyzer

async with AdvancedSentimentAnalyzer() as analyzer:
    sentiment = await analyzer.analyze_comprehensive_sentiment(
        search_result,
        market_context={'volatility': 'high', 'trend': 'bullish'}
    )
    
    print(f"Overall sentiment: {sentiment.overall_sentiment}")
    print(f"Confidence: {sentiment.confidence}")
    print(f"Key insights: {sentiment.key_insights}")
```

## Signal Generation API

### AdvancedSignalGenerator Class

Sophisticated trading signal generation with AI enhancement.

#### generate_ai_enhanced_signals

```python
async def generate_ai_enhanced_signals(
    self,
    search_result: SearchResult,
    symbols: List[str],
    market_context: Optional[Dict] = None
) -> List[EnhancedTradingSignal]:
    """
    Generate AI-enhanced trading signals.
    
    Args:
        search_result: Social media data
        symbols: Target cryptocurrency symbols
        market_context: Optional market context
        
    Returns:
        List of enhanced trading signals
    """
```

**Example:**

```python
from grok_x_module import AdvancedSignalGenerator

async with AdvancedSignalGenerator() as generator:
    signals = await generator.generate_ai_enhanced_signals(
        search_result,
        symbols=['BTC', 'ETH'],
        market_context={'session': 'us_trading'}
    )
    
    for signal in signals:
        print(f"{signal.symbol}: {signal.signal_type.value}")
        print(f"Confidence: {signal.confidence:.3f}")
        print(f"Risk Level: {signal.risk_level.value}")
```

#### generate_signals_from_sentiment

```python
async def generate_signals_from_sentiment(
    self,
    search_result: SearchResult,
    symbols: List[str],
    sentiment_analysis: Optional[SentimentAnalysis] = None
) -> List[EnhancedTradingSignal]:
    """
    Generate signals based on sentiment analysis.
    
    Args:
        search_result: Social media data
        symbols: Target symbols
        sentiment_analysis: Pre-computed sentiment analysis
        
    Returns:
        List of trading signals
    """
```

### Utility Functions

#### filter_signals_by_confidence

```python
def filter_signals_by_confidence(
    signals: List[EnhancedTradingSignal],
    min_confidence: float = 0.7
) -> List[EnhancedTradingSignal]:
    """
    Filter signals by minimum confidence threshold.
    
    Args:
        signals: List of trading signals
        min_confidence: Minimum confidence threshold
        
    Returns:
        Filtered list of signals
    """
```

#### rank_signals_by_strength

```python
def rank_signals_by_strength(
    signals: List[EnhancedTradingSignal]
) -> List[EnhancedTradingSignal]:
    """
    Rank signals by strength and confidence.
    
    Args:
        signals: List of trading signals
        
    Returns:
        Ranked list of signals (strongest first)
    """
```

#### generate_crypto_signals (Convenience Function)

```python
async def generate_crypto_signals(
    search_result: SearchResult,
    symbols: List[str],
    **kwargs
) -> List[EnhancedTradingSignal]:
    """
    Convenience function for generating crypto signals.
    
    Args:
        search_result: Social media data
        symbols: Target symbols
        **kwargs: Additional parameters
        
    Returns:
        List of trading signals
    """
```

## Monitoring and Alerts API

### AlertManager Class

Comprehensive alerting and notification system.

#### send_custom_alert

```python
async def send_custom_alert(
    self,
    title: str,
    message: str,
    priority: AlertPriority = AlertPriority.MEDIUM,
    channels: Optional[List[AlertChannel]] = None,
    data: Optional[Dict] = None
) -> str:
    """
    Send a custom alert.
    
    Args:
        title: Alert title
        message: Alert message
        priority: Alert priority level
        channels: Target channels for alert
        data: Additional alert data
        
    Returns:
        Alert ID
    """
```

**Example:**

```python
from grok_x_module.monitoring.alert_system import alert_manager, AlertPriority

alert_id = await alert_manager.send_custom_alert(
    title="High Volume Activity",
    message="Unusual trading volume detected for BTC",
    priority=AlertPriority.HIGH,
    data={'symbol': 'BTC', 'volume_increase': '150%'}
)
```

#### process_event

```python
async def process_event(self, event: Any) -> None:
    """
    Process an event for potential alert generation.
    
    Args:
        event: Event to process (signal, sentiment, etc.)
    """
```

#### get_recent_alerts

```python
def get_recent_alerts(
    self,
    limit: int = 50,
    priority_filter: Optional[AlertPriority] = None
) -> List[Alert]:
    """
    Get recent alerts.
    
    Args:
        limit: Maximum number of alerts to return
        priority_filter: Filter by priority level
        
    Returns:
        List of recent alerts
    """
```

#### get_alert_statistics

```python
def get_alert_statistics(self) -> Dict[str, Any]:
    """
    Get alert system statistics.
    
    Returns:
        Dict containing alert statistics
    """
```

## Web Dashboard API

### System Status

#### GET /api/grok-x/status

Get system status and metrics.

**Response:**

```json
{
    "status": "healthy",
    "uptime_seconds": 3600,
    "version": "1.0.0",
    "metrics": {
        "total_analyses": 150,
        "successful_analyses": 145,
        "failed_analyses": 5,
        "cache_hits": 75,
        "cache_misses": 75,
        "success_rate": 0.967,
        "cache_hit_rate": 0.5,
        "average_processing_time": 2.5
    },
    "components": {
        "x_api": "connected",
        "grok_api": "connected",
        "database": "healthy",
        "cache": "healthy"
    }
}
```

### Market Analysis

#### POST /api/grok-x/analyze

Run comprehensive market analysis.

**Request:**

```json
{
    "symbols": ["BTC", "ETH"],
    "keywords": ["bitcoin", "ethereum"],
    "time_window_hours": 24,
    "max_tweets": 100,
    "include_influencers": true,
    "analysis_depth": "comprehensive"
}
```

**Response:**

```json
{
    "analysis_id": "analysis_123456",
    "timestamp": "2024-01-15T10:30:00Z",
    "processing_time_seconds": 3.2,
    "sentiment_analysis": {
        "overall_sentiment": 0.65,
        "confidence": 0.82,
        "sentiment_label": "POSITIVE",
        "key_insights": [
            "Strong bullish sentiment from verified accounts",
            "High engagement on positive crypto content"
        ],
        "market_implications": "Positive sentiment suggests upward momentum",
        "trend_analysis": {
            "direction": "IMPROVING",
            "strength": 0.7
        }
    },
    "trading_signals": [
        {
            "symbol": "BTC",
            "signal_type": "BUY",
            "strength": "STRONG",
            "confidence": 0.85,
            "risk_level": "MEDIUM",
            "entry_price_range": {
                "min": 49000,
                "max": 51000
            },
            "stop_loss": 45000,
            "take_profit": 55000,
            "reasoning": "Strong bullish sentiment with high confidence",
            "time_horizon": "SHORT",
            "generated_at": "2024-01-15T10:30:00Z",
            "expires_at": "2024-01-15T12:30:00Z"
        }
    ],
    "social_data": {
        "total_tweets": 95,
        "total_engagement": 15000,
        "top_influencers": ["crypto_whale", "defi_expert"],
        "trending_keywords": ["bitcoin", "bullish", "moon"]
    },
    "market_context": {
        "market_session": "us_trading",
        "volatility_level": "medium",
        "timing_score": 0.8
    }
}
```

#### POST /api/grok-x/quick-sentiment

Get quick sentiment analysis.

**Request:**

```json
{
    "symbols": ["BTC", "ETH"],
    "time_window_hours": 6
}
```

**Response:**

```json
{
    "overall_sentiment": 0.45,
    "confidence": 0.78,
    "sentiment_label": "POSITIVE",
    "signal_count": 2,
    "processing_time_seconds": 1.2,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Alert Management

#### GET /api/grok-x/alerts

Get recent alerts.

**Query Parameters:**
- `limit`: Maximum number of alerts (default: 50)
- `priority`: Filter by priority (low, medium, high, critical)
- `type`: Filter by alert type

**Response:**

```json
{
    "alerts": [
        {
            "id": "alert_123456",
            "type": "SIGNAL_GENERATED",
            "priority": "HIGH",
            "title": "Strong Buy Signal Generated",
            "message": "BTC showing strong bullish sentiment",
            "timestamp": "2024-01-15T10:30:00Z",
            "data": {
                "symbol": "BTC",
                "confidence": 0.92,
                "signal_type": "STRONG_BUY"
            },
            "channels": ["webhook", "dashboard"]
        }
    ],
    "total_count": 1,
    "has_more": false
}
```

#### POST /api/grok-x/alerts/send

Send custom alert.

**Request:**

```json
{
    "title": "Custom Alert",
    "message": "This is a custom alert message",
    "priority": "medium",
    "data": {
        "custom_field": "custom_value"
    }
}
```

**Response:**

```json
{
    "alert_id": "alert_789012",
    "status": "sent",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Monitoring Control

#### POST /api/grok-x/monitoring/start

Start continuous monitoring.

**Request:**

```json
{
    "symbols": ["BTC", "ETH", "SOL"],
    "interval_minutes": 30,
    "alert_thresholds": {
        "min_confidence": 0.8,
        "sentiment_threshold": 0.7
    }
}
```

**Response:**

```json
{
    "monitoring_id": "monitor_123456",
    "status": "started",
    "symbols": ["BTC", "ETH", "SOL"],
    "interval_minutes": 30,
    "started_at": "2024-01-15T10:30:00Z"
}
```

#### POST /api/grok-x/monitoring/stop

Stop continuous monitoring.

**Request:**

```json
{
    "monitoring_id": "monitor_123456"
}
```

**Response:**

```json
{
    "monitoring_id": "monitor_123456",
    "status": "stopped",
    "stopped_at": "2024-01-15T10:35:00Z",
    "total_runtime_minutes": 5
}
```

## Data Models

### AnalysisRequest

```python
@dataclass
class AnalysisRequest:
    symbols: List[str]
    keywords: Optional[List[str]] = None
    time_window_hours: int = 24
    max_tweets: int = 100
    include_influencers: bool = True
    analysis_depth: str = 'standard'  # 'quick', 'standard', 'comprehensive'
    custom_filters: Optional[Dict] = None
```

### AnalysisResult

```python
@dataclass
class AnalysisResult:
    analysis_id: str
    analysis_timestamp: datetime
    processing_time_seconds: float
    sentiment_analysis: SentimentAnalysis
    trading_signals: List[EnhancedTradingSignal]
    social_data: SearchResult
    market_context: Dict[str, Any]
    cache_hit: bool = False
```

### SentimentAnalysis

```python
@dataclass
class SentimentAnalysis:
    overall_sentiment: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    sentiment_label: str  # 'VERY_NEGATIVE', 'NEGATIVE', 'NEUTRAL', 'POSITIVE', 'VERY_POSITIVE'
    individual_sentiments: List[float]
    key_insights: List[str]
    market_implications: str
    trend_analysis: Dict[str, Any]
```

### EnhancedTradingSignal

```python
@dataclass
class EnhancedTradingSignal:
    symbol: str
    signal_type: SignalType
    strength: SignalStrength
    confidence: float
    risk_level: RiskLevel
    entry_price_range: Dict[str, float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    sentiment_component: SignalComponent
    technical_component: Optional[SignalComponent]
    fundamental_component: Optional[SignalComponent]
    social_component: SignalComponent
    reasoning: str
    time_horizon: str
    generated_at: datetime
    expires_at: datetime
    
    @property
    def overall_score(self) -> float:
        """Calculate overall signal score"""
        
    @property
    def is_valid(self) -> bool:
        """Check if signal is still valid"""
```

### SignalComponent

```python
@dataclass
class SignalComponent:
    name: str
    value: float  # -1.0 to 1.0
    weight: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    reasoning: str
    data_points: int = 0
```

### Alert

```python
@dataclass
class Alert:
    id: str
    type: AlertType
    priority: AlertPriority
    title: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    channels: List[AlertChannel]
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
```

### Enums

```python
class SignalType(Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

class SignalStrength(Enum):
    VERY_STRONG = "VERY_STRONG"
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"

class RiskLevel(Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertType(Enum):
    SIGNAL_GENERATED = "SIGNAL_GENERATED"
    SENTIMENT_EXTREME = "SENTIMENT_EXTREME"
    VOLUME_SPIKE = "VOLUME_SPIKE"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    CUSTOM = "CUSTOM"

class AlertPriority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertChannel(Enum):
    DASHBOARD = "DASHBOARD"
    WEBHOOK = "WEBHOOK"
    EMAIL = "EMAIL"
    SLACK = "SLACK"
```

## Error Handling

### Exception Types

```python
class GrokXError(Exception):
    """Base exception for Grok-X-Module"""

class APIError(GrokXError):
    """External API communication error"""

class RateLimitError(APIError):
    """Rate limit exceeded"""

class AuthenticationError(APIError):
    """Authentication failed"""

class ValidationError(GrokXError):
    """Request validation error"""

class ConfigurationError(GrokXError):
    """Configuration error"""
```

### Error Response Format

```json
{
    "error": {
        "type": "ValidationError",
        "message": "Invalid symbol format",
        "code": "INVALID_SYMBOL",
        "details": {
            "symbol": "INVALID_SYMBOL",
            "expected_format": "3-5 uppercase letters"
        },
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req_123456"
    }
}
```

### Error Handling Examples

```python
from grok_x_module import GrokXEngine, ValidationError, RateLimitError

async def handle_analysis():
    try:
        async with GrokXEngine() as engine:
            result = await engine.analyze_market_sentiment(request)
            return result
            
    except ValidationError as e:
        print(f"Invalid request: {e.message}")
        
    except RateLimitError as e:
        print(f"Rate limit exceeded: {e.message}")
        # Implement backoff strategy
        
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Rate Limiting

### Rate Limits

- **X API**: 300 requests per 15-minute window
- **Grok API**: 60 requests per minute
- **Dashboard API**: 1000 requests per hour per IP

### Rate Limit Headers

```http
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 250
X-RateLimit-Reset: 1642248600
X-RateLimit-Window: 900
```

### Rate Limit Handling

```python
import time
from grok_x_module import RateLimitError

async def with_rate_limit_handling():
    try:
        result = await engine.analyze_market_sentiment(request)
        return result
        
    except RateLimitError as e:
        # Get reset time from error
        reset_time = e.reset_time
        wait_seconds = reset_time - time.time()
        
        print(f"Rate limit exceeded. Waiting {wait_seconds} seconds...")
        await asyncio.sleep(wait_seconds)
        
        # Retry the request
        return await engine.analyze_market_sentiment(request)
```

## Examples

### Complete Analysis Workflow

```python
import asyncio
from grok_x_module import (
    GrokXEngine, 
    AnalysisRequest,
    filter_signals_by_confidence,
    rank_signals_by_strength
)
from grok_x_module.monitoring.alert_system import alert_manager

async def complete_analysis_workflow():
    # Configure analysis
    request = AnalysisRequest(
        symbols=['BTC', 'ETH', 'SOL'],
        keywords=['bitcoin', 'ethereum', 'solana', 'crypto'],
        time_window_hours=12,
        max_tweets=200,
        include_influencers=True,
        analysis_depth='comprehensive'
    )
    
    # Run analysis
    async with GrokXEngine() as engine:
        print("Starting market analysis...")
        result = await engine.analyze_market_sentiment(request)
        
        # Display sentiment results
        sentiment = result.sentiment_analysis
        print(f"\nSentiment Analysis:")
        print(f"Overall Sentiment: {sentiment.overall_sentiment:.3f}")
        print(f"Confidence: {sentiment.confidence:.3f}")
        print(f"Label: {sentiment.sentiment_label}")
        
        # Process trading signals
        signals = result.trading_signals
        high_confidence_signals = filter_signals_by_confidence(signals, 0.8)
        ranked_signals = rank_signals_by_strength(high_confidence_signals)
        
        print(f"\nTrading Signals ({len(ranked_signals)} high confidence):")
        for signal in ranked_signals[:5]:  # Top 5 signals
            print(f"{signal.symbol}: {signal.signal_type.value}")
            print(f"  Confidence: {signal.confidence:.3f}")
            print(f"  Strength: {signal.strength.value}")
            print(f"  Risk: {signal.risk_level.value}")
            print(f"  Reasoning: {signal.reasoning}")
            
            # Send alert for very high confidence signals
            if signal.confidence > 0.9:
                await alert_manager.send_custom_alert(
                    title=f"High Confidence Signal: {signal.symbol}",
                    message=f"{signal.signal_type.value} signal with {signal.confidence:.1%} confidence",
                    priority="high",
                    data={
                        'symbol': signal.symbol,
                        'signal_type': signal.signal_type.value,
                        'confidence': signal.confidence
                    }
                )
        
        # Display social metrics
        social = result.social_data
        print(f"\nSocial Data:")
        print(f"Total Tweets: {len(social.tweets)}")
        print(f"Total Users: {len(social.users)}")
        
        # Display performance metrics
        metrics = engine.get_performance_metrics()
        print(f"\nPerformance:")
        print(f"Processing Time: {result.processing_time_seconds:.2f}s")
        print(f"Cache Hit: {'Yes' if result.cache_hit else 'No'}")
        print(f"Success Rate: {metrics['success_rate']:.1%}")

# Run the workflow
asyncio.run(complete_analysis_workflow())
```

### Continuous Monitoring Setup

```python
import asyncio
from datetime import datetime
from grok_x_module import GrokXEngine
from grok_x_module.monitoring.alert_system import alert_manager, AlertPriority

class CryptoMonitor:
    def __init__(self):
        self.engine = None
        self.monitoring_active = False
    
    async def start_monitoring(self, symbols, interval_minutes=30):
        """Start continuous monitoring"""
        self.monitoring_active = True
        
        async with GrokXEngine() as engine:
            self.engine = engine
            
            print(f"Starting monitoring for {symbols}")
            await alert_manager.send_custom_alert(
                title="Monitoring Started",
                message=f"Continuous monitoring started for {', '.join(symbols)}",
                priority=AlertPriority.MEDIUM
            )
            
            while self.monitoring_active:
                try:
                    # Run quick sentiment analysis
                    sentiment = await engine.get_quick_sentiment(symbols)
                    
                    print(f"[{datetime.now()}] Sentiment: {sentiment['overall_sentiment']:.3f}")
                    
                    # Check for extreme sentiment
                    if abs(sentiment['overall_sentiment']) > 0.8:
                        await alert_manager.send_custom_alert(
                            title="Extreme Sentiment Detected",
                            message=f"Sentiment: {sentiment['overall_sentiment']:.3f}",
                            priority=AlertPriority.HIGH,
                            data=sentiment
                        )
                    
                    # Wait for next interval
                    await asyncio.sleep(interval_minutes * 60)
                    
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        print("Monitoring stopped")

# Usage
monitor = CryptoMonitor()

# Start monitoring in background
asyncio.create_task(monitor.start_monitoring(['BTC', 'ETH'], interval_minutes=15))

# Stop monitoring after some time
# monitor.stop_monitoring()
```

### Custom Signal Strategy

```python
from grok_x_module import AdvancedSignalGenerator, EnhancedTradingSignal
from grok_x_module.signals.signal_generator import SignalComponent

class CustomSignalStrategy:
    def __init__(self):
        self.generator = AdvancedSignalGenerator()
    
    async def generate_custom_signals(self, search_result, symbols):
        """Generate signals with custom logic"""
        
        async with self.generator as gen:
            # Get base signals
            base_signals = await gen.generate_ai_enhanced_signals(
                search_result, symbols
            )
            
            # Apply custom filtering and enhancement
            enhanced_signals = []
            
            for signal in base_signals:
                # Custom logic: Boost signals during high volatility
                if self._is_high_volatility_period():
                    signal.confidence *= 1.1  # Boost confidence
                    signal.reasoning += " (Enhanced for high volatility)"
                
                # Custom logic: Reduce risk during uncertain times
                if self._is_uncertain_market():
                    signal.risk_level = self._increase_risk_level(signal.risk_level)
                    signal.reasoning += " (Risk increased due to market uncertainty)"
                
                # Only include signals meeting custom criteria
                if self._meets_custom_criteria(signal):
                    enhanced_signals.append(signal)
            
            return enhanced_signals
    
    def _is_high_volatility_period(self) -> bool:
        """Check if current period has high volatility"""
        # Custom volatility detection logic
        return True  # Placeholder
    
    def _is_uncertain_market(self) -> bool:
        """Check if market conditions are uncertain"""
        # Custom uncertainty detection logic
        return False  # Placeholder
    
    def _increase_risk_level(self, current_risk):
        """Increase risk level by one step"""
        risk_levels = ['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        current_index = risk_levels.index(current_risk.value)
        new_index = min(current_index + 1, len(risk_levels) - 1)
        return RiskLevel(risk_levels[new_index])
    
    def _meets_custom_criteria(self, signal) -> bool:
        """Check if signal meets custom criteria"""
        return (
            signal.confidence > 0.75 and
            signal.sentiment_component.confidence > 0.7 and
            signal.social_component.data_points > 50
        )

# Usage
strategy = CustomSignalStrategy()
custom_signals = await strategy.generate_custom_signals(search_result, ['BTC'])
```

This comprehensive API documentation provides detailed information about all available APIs, their parameters, responses, and practical usage examples. The documentation covers both the Python API for direct integration and the REST API for web-based access, making it easy for developers to integrate the Grok-X-Module into their trading systems.

