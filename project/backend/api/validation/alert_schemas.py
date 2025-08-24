"""
Comprehensive Input Validation Schemas - Fixed Version
Provides robust validation for Enhanced Alerts System
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime
from enum import Enum
import re

# Configure Pydantic v2 settings
class BaseConfig:
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=False
    )

# Enums for validation
class AlertType(str, Enum):
    PRICE = "PRICE"
    VOLUME = "VOLUME"
    TECHNICAL = "TECHNICAL"
    PATTERN = "PATTERN"
    CUSTOM = "CUSTOM"

class ConditionOperator(str, Enum):
    ABOVE = "above"
    BELOW = "below"
    CROSSES_ABOVE = "crosses_above"
    CROSSES_BELOW = "crosses_below"
    EQUALS = "equals"
    BETWEEN = "between"
    OUTSIDE = "outside"

class TimeFrame(str, Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    EIGHT_HOURS = "8h"
    TWELVE_HOURS = "12h"
    ONE_DAY = "1d"
    THREE_DAYS = "3d"
    ONE_WEEK = "1w"

class NotificationChannel(str, Enum):
    WEBHOOK = "webhook"
    DATABASE = "database"
    TELEGRAM = "telegram"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

class TechnicalIndicator(str, Enum):
    RSI = "rsi"
    MACD = "macd"
    BOLLINGER_BANDS = "bollinger_bands"
    EMA = "ema"
    SMA = "sma"
    STOCHASTIC = "stochastic"
    WILLIAMS_R = "williams_r"
    ADX = "adx"
    CCI = "cci"
    ATR = "atr"

# Alert condition schemas
class PriceCondition(BaseModel, BaseConfig):
    """Price-based alert conditions"""
    threshold: float = Field(..., gt=0, le=1000000000)
    operator: ConditionOperator
    timeframe: TimeFrame = TimeFrame.ONE_HOUR
    threshold_high: Optional[float] = Field(None, gt=0, le=1000000000)

class VolumeCondition(BaseModel, BaseConfig):
    """Volume-based alert conditions"""
    threshold: float = Field(..., gt=0)
    operator: ConditionOperator
    timeframe: TimeFrame = TimeFrame.ONE_HOUR
    comparison_type: Literal["absolute", "percentage", "average_multiple"] = "absolute"
    average_periods: Optional[int] = Field(None, ge=1, le=100)

class TechnicalCondition(BaseModel, BaseConfig):
    """Technical indicator-based alert conditions"""
    indicator: TechnicalIndicator
    threshold: float = Field(..., ge=-100, le=200)
    operator: ConditionOperator
    timeframe: TimeFrame = TimeFrame.ONE_HOUR
    period: Optional[int] = Field(None, ge=1, le=200)
    signal_line_period: Optional[int] = Field(None, ge=1, le=200)
    standard_deviations: Optional[float] = Field(None, ge=0.1, le=5.0)

class PatternCondition(BaseModel, BaseConfig):
    """Pattern recognition alert conditions"""
    pattern_type: Literal[
        "golden_cross", "death_cross", "breakout", "breakdown",
        "double_top", "double_bottom", "head_shoulders", "inverse_head_shoulders",
        "triangle", "wedge", "flag", "pennant"
    ]
    timeframe: TimeFrame = TimeFrame.ONE_HOUR
    confidence_threshold: float = Field(0.7, ge=0.1, le=1.0)
    lookback_periods: int = Field(50, ge=10, le=500)
    volume_confirmation: bool = False

# Main alert creation schema
class CreateAlertRequest(BaseModel, BaseConfig):
    """Comprehensive alert creation request validation"""
    symbol: str = Field(..., min_length=3, max_length=20)
    alert_type: AlertType
    conditions: Union[PriceCondition, VolumeCondition, TechnicalCondition, PatternCondition]
    notification_channels: List[NotificationChannel] = Field(..., min_length=1, max_length=5)
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    is_active: bool = True
    expires_at: Optional[datetime] = None
    max_triggers: Optional[int] = Field(None, ge=1, le=1000)
    cooldown_minutes: int = Field(5, ge=0, le=1440)
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        """Validate symbol format"""
        if not re.match(r'^[A-Z0-9]{3,20}$', v.upper()):
            raise ValueError('Invalid symbol format')
        return v.upper()

    @field_validator('expires_at')
    @classmethod
    def validate_expiration(cls, v):
        """Validate expiration date"""
        if v and v <= datetime.now():
            raise ValueError('Expiration date must be in the future')
        return v

# Alert update schema
class UpdateAlertRequest(BaseModel, BaseConfig):
    """Alert update request validation"""
    is_active: Optional[bool] = None
    notification_channels: Optional[List[NotificationChannel]] = Field(None, min_length=1, max_length=5)
    priority: Optional[Literal["low", "medium", "high", "critical"]] = None
    cooldown_minutes: Optional[int] = Field(None, ge=0, le=1440)
    expires_at: Optional[datetime] = None
    max_triggers: Optional[int] = Field(None, ge=1, le=1000)

    @field_validator('expires_at')
    @classmethod
    def validate_expiration(cls, v):
        """Validate expiration date"""
        if v and v <= datetime.now():
            raise ValueError('Expiration date must be in the future')
        return v

# System configuration schemas
class TelegramConfigRequest(BaseModel, BaseConfig):
    """Telegram configuration validation"""
    bot_token: str = Field(..., min_length=10, max_length=100)
    chat_id: str = Field(..., min_length=1, max_length=50)
    enabled: bool = True
    notifications_enabled: bool = True

    @field_validator('bot_token')
    @classmethod
    def validate_bot_token(cls, v):
        """Validate Telegram bot token format"""
        if not re.match(r'^\d+:[A-Za-z0-9_-]+$', v):
            raise ValueError('Invalid Telegram bot token format')
        return v

    @field_validator('chat_id')
    @classmethod
    def validate_chat_id(cls, v):
        """Validate chat ID format"""
        if not re.match(r'^-?\d+$', v) and not v.startswith('@'):
            raise ValueError('Invalid chat ID format')
        return v

# Query parameter schemas
class AlertListQuery(BaseModel, BaseConfig):
    """Alert list query parameters validation"""
    symbol: Optional[str] = Field(None, min_length=3, max_length=20)
    alert_type: Optional[AlertType] = None
    is_active: Optional[bool] = None
    priority: Optional[Literal["low", "medium", "high", "critical"]] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        """Validate symbol format"""
        if v and not re.match(r'^[A-Z0-9]{3,20}$', v.upper()):
            raise ValueError('Invalid symbol format')
        return v.upper() if v else None

class TechnicalAnalysisQuery(BaseModel, BaseConfig):
    """Technical analysis query validation"""
    symbol: str = Field(..., min_length=3, max_length=20)
    timeframes: Optional[List[TimeFrame]] = Field(None, max_length=10)
    indicators: Optional[List[TechnicalIndicator]] = Field(None, max_length=20)

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        """Validate symbol format"""
        if not re.match(r'^[A-Z0-9]{3,20}$', v.upper()):
            raise ValueError('Invalid symbol format')
        return v.upper()

# Report generation schemas
class ReportRequest(BaseModel, BaseConfig):
    """Report generation request validation"""
    report_type: Literal[
        "performance", "technical", "alert_analytics", 
        "notification", "user_activity", "system_health"
    ]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    symbols: Optional[List[str]] = Field(None, max_length=50)
    format: Literal["json", "csv", "pdf"] = "json"

    @field_validator('symbols')
    @classmethod
    def validate_symbols(cls, v):
        """Validate symbols list"""
        if v:
            for symbol in v:
                if not re.match(r'^[A-Z0-9]{3,20}$', symbol.upper()):
                    raise ValueError(f'Invalid symbol format: {symbol}')
        return [s.upper() for s in v] if v else None

# Response schemas for API documentation
class AlertResponse(BaseModel, BaseConfig):
    """Alert response model"""
    id: str
    symbol: str
    alert_type: AlertType
    conditions: Dict[str, Any]
    notification_channels: List[NotificationChannel]
    is_active: bool
    created_at: datetime
    last_triggered: Optional[datetime]
    trigger_count: int
    priority: str

class SystemStatusResponse(BaseModel, BaseConfig):
    """System status response model"""
    engine_running: bool
    active_alerts: int
    monitored_symbols: int
    total_triggers: int
    uptime_seconds: int
    last_update: datetime

class TechnicalAnalysisResponse(BaseModel, BaseConfig):
    """Technical analysis response model"""
    symbol: str
    current_price: float
    price_change_24h: float
    volume_24h: float
    indicators: Dict[str, Any]
    patterns: List[Dict[str, Any]]
    timestamp: datetime