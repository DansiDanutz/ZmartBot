"""
Grok-X-Module Configuration Settings
Comprehensive configuration management for all module components
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SignalType(Enum):
    """Trading signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class XAPIConfig:
    """X API configuration settings"""
    # Rate limiting
    requests_per_minute: int = 300
    requests_per_hour: int = 1500
    requests_per_day: int = 50000
    
    # Search parameters
    max_results_per_request: int = 100
    tweet_fields: List[str] = field(default_factory=lambda: [
        "id", "text", "author_id", "created_at", "public_metrics",
        "context_annotations", "entities", "geo", "lang", "reply_settings"
    ])
    user_fields: List[str] = field(default_factory=lambda: [
        "id", "name", "username", "verified", "public_metrics",
        "description", "created_at", "location"
    ])
    expansions: List[str] = field(default_factory=lambda: [
        "author_id", "referenced_tweets.id", "entities.mentions.username"
    ])
    
    # Monitoring keywords
    crypto_keywords: List[str] = field(default_factory=lambda: [
        "bitcoin", "BTC", "ethereum", "ETH", "crypto", "cryptocurrency",
        "altcoin", "DeFi", "NFT", "blockchain", "trading", "pump", "dump",
        "moon", "hodl", "diamond hands", "paper hands", "bull", "bear"
    ])
    
    # Influencer tracking
    track_verified_only: bool = False
    min_follower_count: int = 1000
    track_influencers: List[str] = field(default_factory=lambda: [
        "elonmusk", "michael_saylor", "VitalikButerin", "cz_binance",
        "brian_armstrong", "APompliano", "DocumentingBTC", "WhalePanda"
    ])


@dataclass
class GrokConfig:
    """Grok AI configuration settings"""
    model: str = "grok-beta"
    max_tokens: int = 4000
    temperature: float = 0.3
    top_p: float = 0.9
    
    # Analysis prompts
    sentiment_analysis_prompt: str = """
    Analyze the sentiment of the following cryptocurrency-related social media posts.
    Consider market context, technical terminology, and emotional indicators.
    Provide sentiment score (-1 to 1), confidence level (0 to 1), and key insights.
    
    Posts: {posts}
    
    Response format:
    {{
        "overall_sentiment": float,
        "confidence": float,
        "individual_sentiments": [
            {{"post_id": str, "sentiment": float, "confidence": float, "reasoning": str}}
        ],
        "key_insights": [str],
        "market_implications": str
    }}
    """
    
    signal_generation_prompt: str = """
    Based on the following market sentiment analysis and social media intelligence,
    generate trading signals for cryptocurrency markets.
    
    Sentiment Data: {sentiment_data}
    Market Context: {market_context}
    Historical Performance: {historical_data}
    
    Provide specific trading recommendations with confidence scores and risk assessments.
    
    Response format:
    {{
        "signals": [
            {{
                "symbol": str,
                "signal_type": str,
                "confidence": float,
                "reasoning": str,
                "risk_level": str,
                "time_horizon": str,
                "entry_price_range": {{"min": float, "max": float}},
                "stop_loss": float,
                "take_profit": float
            }}
        ],
        "market_overview": str,
        "risk_factors": [str]
    }}
    """


@dataclass
class SentimentConfig:
    """Sentiment analysis configuration"""
    # Scoring weights
    text_sentiment_weight: float = 0.4
    author_credibility_weight: float = 0.3
    engagement_weight: float = 0.2
    recency_weight: float = 0.1
    
    # Thresholds
    bullish_threshold: float = 0.6
    bearish_threshold: float = -0.6
    neutral_range: tuple = (-0.2, 0.2)
    
    # Time windows
    short_term_window: int = 3600  # 1 hour in seconds
    medium_term_window: int = 86400  # 24 hours in seconds
    long_term_window: int = 604800  # 7 days in seconds
    
    # Filtering
    min_engagement_score: int = 5
    exclude_retweets: bool = False
    language_filter: List[str] = field(default_factory=lambda: ["en"])


@dataclass
class SignalConfig:
    """Signal generation configuration"""
    # Signal thresholds
    strong_buy_threshold: float = 0.8
    buy_threshold: float = 0.6
    hold_threshold_upper: float = 0.2
    hold_threshold_lower: float = -0.2
    sell_threshold: float = -0.6
    strong_sell_threshold: float = -0.8
    
    # Confidence requirements
    min_confidence: float = 0.7
    min_data_points: int = 10
    
    # Risk management
    max_risk_level: str = "HIGH"
    default_stop_loss_pct: float = 0.05  # 5%
    default_take_profit_pct: float = 0.15  # 15%
    
    # Signal validity
    signal_expiry_minutes: int = 60
    max_signals_per_hour: int = 10


@dataclass
class MonitoringConfig:
    """Monitoring and alerting configuration"""
    # Performance metrics
    track_signal_accuracy: bool = True
    track_api_performance: bool = True
    track_sentiment_quality: bool = True
    
    # Alerting
    enable_alerts: bool = True
    alert_channels: List[str] = field(default_factory=lambda: ["webhook", "log"])
    webhook_url: Optional[str] = None
    
    # Health checks
    health_check_interval: int = 300  # 5 minutes
    api_timeout_threshold: int = 30  # seconds
    error_rate_threshold: float = 0.1  # 10%
    
    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_file: str = "logs/grok_x_module.log"
    max_log_size: int = 100 * 1024 * 1024  # 100MB
    log_backup_count: int = 5


@dataclass
class DatabaseConfig:
    """Database configuration"""
    # Primary database
    db_type: str = "postgresql"
    host: str = "localhost"
    port: int = 5432
    database: str = "grok_x_signals"
    username: str = "grok_user"
    password: str = "secure_password"
    
    # Redis cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    cache_ttl: int = 3600  # 1 hour
    
    # Connection pooling
    max_connections: int = 20
    connection_timeout: int = 30


@dataclass
class GrokXModuleConfig:
    """Main configuration class combining all settings"""
    x_api: XAPIConfig = field(default_factory=XAPIConfig)
    grok: GrokConfig = field(default_factory=GrokConfig)
    sentiment: SentimentConfig = field(default_factory=SentimentConfig)
    signals: SignalConfig = field(default_factory=SignalConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # General settings
    environment: str = "development"
    debug_mode: bool = True
    data_retention_days: int = 30
    
    @classmethod
    def from_file(cls, config_path: str) -> 'GrokXModuleConfig':
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        return cls(**config_data)
    
    def to_file(self, config_path: str) -> None:
        """Save configuration to JSON file"""
        with open(config_path, 'w') as f:
            json.dump(self.__dict__, f, indent=2, default=str)
    
    def update_from_env(self) -> None:
        """Update configuration from environment variables"""
        # Database settings
        if os.getenv('DB_HOST'):
            self.database.host = os.getenv('DB_HOST')
        if os.getenv('DB_PORT'):
            self.database.port = int(os.getenv('DB_PORT'))
        if os.getenv('DB_NAME'):
            self.database.database = os.getenv('DB_NAME')
        if os.getenv('DB_USER'):
            self.database.username = os.getenv('DB_USER')
        if os.getenv('DB_PASSWORD'):
            self.database.password = os.getenv('DB_PASSWORD')
        
        # Redis settings
        if os.getenv('REDIS_HOST'):
            self.database.redis_host = os.getenv('REDIS_HOST')
        if os.getenv('REDIS_PORT'):
            self.database.redis_port = int(os.getenv('REDIS_PORT'))
        
        # Environment
        if os.getenv('ENVIRONMENT'):
            self.environment = os.getenv('ENVIRONMENT')
        if os.getenv('DEBUG_MODE'):
            self.debug_mode = os.getenv('DEBUG_MODE').lower() == 'true'


# Default configuration instance
default_config = GrokXModuleConfig()


def get_config() -> GrokXModuleConfig:
    """Get the default configuration instance"""
    return default_config


def load_config(config_path: str) -> GrokXModuleConfig:
    """Load configuration from file"""
    return GrokXModuleConfig.from_file(config_path)

