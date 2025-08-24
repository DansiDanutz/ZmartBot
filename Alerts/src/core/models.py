"""Data models for the Symbol Alerts System."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class AlertType(str, Enum):
    """Types of alerts supported by the system."""
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PRICE_CROSS = "price_cross"
    VOLUME_SPIKE = "volume_spike"
    RSI_OVERBOUGHT = "rsi_overbought"
    RSI_OVERSOLD = "rsi_oversold"
    MACD_BULLISH = "macd_bullish"
    MACD_BEARISH = "macd_bearish"
    BOLLINGER_UPPER = "bollinger_upper"
    BOLLINGER_LOWER = "bollinger_lower"
    SUPPORT_BREAK = "support_break"
    RESISTANCE_BREAK = "resistance_break"
    NEWS_SENTIMENT = "news_sentiment"
    CUSTOM = "custom"


class AlertStatus(str, Enum):
    """Status of an alert."""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    PAUSED = "paused"
    EXPIRED = "expired"
    DELETED = "deleted"


class TimeFrame(str, Enum):
    """Supported timeframes."""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


class MarketData(BaseModel):
    """Real-time market data structure."""
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    change_24h: Optional[float] = None
    change_percent_24h: Optional[float] = None


class TechnicalIndicators(BaseModel):
    """Technical indicators for a symbol."""
    symbol: str
    timeframe: TimeFrame
    timestamp: datetime
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    volume_sma: Optional[float] = None


class AlertCondition(BaseModel):
    """Alert condition configuration."""
    field: str  # price, volume, rsi, etc.
    operator: str  # >, <, >=, <=, ==, cross_above, cross_below
    value: Union[float, str]
    timeframe: TimeFrame = TimeFrame.M5


class AlertConfig(BaseModel):
    """Alert configuration."""
    id: Optional[str] = None
    user_id: str
    symbol: str
    alert_type: AlertType
    conditions: List[AlertCondition]
    message: Optional[str] = None
    webhook_url: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    max_triggers: Optional[int] = None
    cooldown_minutes: Optional[int] = 5

    @validator('symbol')
    def validate_symbol(cls, v):
        return v.upper()


class AlertTrigger(BaseModel):
    """Alert trigger event."""
    alert_id: str
    symbol: str
    alert_type: AlertType
    trigger_price: float
    trigger_value: Optional[float] = None
    message: str
    timestamp: datetime
    market_data: MarketData
    technical_data: Optional[TechnicalIndicators] = None


class WebhookPayload(BaseModel):
    """Webhook payload structure."""
    event_type: str = "alert_triggered"
    alert_trigger: AlertTrigger
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SystemMetrics(BaseModel):
    """System performance metrics."""
    active_alerts: int
    monitored_symbols: int
    triggers_last_hour: int
    avg_processing_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    uptime_seconds: int
    last_updated: datetime


class UserConfig(BaseModel):
    """User configuration."""
    user_id: str
    api_key: Optional[str] = None
    webhook_url: Optional[str] = None
    max_alerts: int = 100
    rate_limit_per_minute: int = 60
    notification_channels: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: Optional[datetime] = None

