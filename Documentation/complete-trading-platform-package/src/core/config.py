"""
Trade Strategy Module - Core Configuration
==========================================

Advanced configuration management for the Trade Strategy module with
seamless integration to ZmartBot + KingFisher systems.

Author: Manus AI
Version: 1.0 Professional Edition
Compatibility: Mac Mini 2025 M2 Pro Integration
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseSettings, validator, Field
from cryptography.fernet import Fernet


class Environment(str, Enum):
    """Environment types for configuration management."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class RiskLevel(str, Enum):
    """Risk level definitions for trading operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AGGRESSIVE = "aggressive"


class SignalType(str, Enum):
    """Signal type definitions."""
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    EXTERNAL = "external"


@dataclass
class PositionScalingConfig:
    """Configuration for position scaling strategy."""
    stage_1_bankroll_pct: Decimal = Decimal('0.01')  # 1%
    stage_1_leverage: Decimal = Decimal('20.0')      # 20X
    
    stage_2_bankroll_pct: Decimal = Decimal('0.02')  # 2%
    stage_2_leverage: Decimal = Decimal('10.0')      # 10X
    
    stage_3_bankroll_pct: Decimal = Decimal('0.04')  # 4%
    stage_3_leverage: Decimal = Decimal('5.0')       # 5X
    
    stage_4_bankroll_pct: Decimal = Decimal('0.08')  # 8%
    stage_4_leverage: Decimal = Decimal('2.0')       # 2X
    
    max_scaling_stages: int = 4
    min_profit_threshold: Decimal = Decimal('0.75')  # 75% minimum profit
    
    # Profit taking configuration
    profit_take_1_pct: Decimal = Decimal('0.30')     # 30% at liquidation price
    profit_take_2_pct: Decimal = Decimal('0.25')     # 25% at trailing stop
    trailing_stop_1_pct: Decimal = Decimal('0.30')   # Initial trailing stop
    trailing_stop_2_pct: Decimal = Decimal('0.03')   # Final trailing stop (3%)


@dataclass
class RiskManagementConfig:
    """Risk management configuration."""
    max_positions_per_vault: int = 2
    max_daily_loss_pct: Decimal = Decimal('0.05')    # 5% max daily loss
    max_drawdown_pct: Decimal = Decimal('0.20')      # 20% max drawdown
    max_position_size_pct: Decimal = Decimal('0.15') # 15% max position size
    
    # Risk assessment intervals
    risk_check_interval_minutes: int = 15
    liquidation_buffer_pct: Decimal = Decimal('0.05') # 5% buffer from liquidation
    
    # Correlation limits
    max_correlation_exposure: Decimal = Decimal('0.30') # 30% max correlated exposure
    correlation_threshold: Decimal = Decimal('0.70')    # 70% correlation threshold


@dataclass
class SignalProcessingConfig:
    """Signal processing configuration."""
    signal_expiry_minutes: int = 60
    min_signal_confidence: Decimal = Decimal('0.60')  # 60% minimum confidence
    min_signal_quality: Decimal = Decimal('0.65')     # 65% minimum quality
    
    # Aggregation settings
    min_signals_for_consensus: int = 3
    consensus_threshold: Decimal = Decimal('0.70')    # 70% consensus required
    
    # Source reliability
    min_source_reliability: Decimal = Decimal('0.50') # 50% minimum reliability
    reliability_decay_factor: Decimal = Decimal('0.95') # Daily decay factor


class TradeStrategySettings(BaseSettings):
    """Main configuration class for Trade Strategy module."""
    
    # Environment and basic settings
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    testing: bool = False
    
    # Service configuration (zero-conflict ports)
    api_host: str = "0.0.0.0"
    api_port: int = 8200  # Offset +200 from KingFisher
    frontend_port: int = 3200  # Offset +200 from KingFisher
    websocket_port: int = 8201
    
    # Database configuration (shared with existing systems)
    database_url: str = "postgresql://trade_strategy_app:secure_app_password_2025@localhost:5432/trading_platform"
    database_schema: str = "trade_strategy"
    database_pool_size: int = 20
    database_max_overflow: int = 30
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    # Redis configuration (shared with namespace isolation)
    redis_url: str = "redis://localhost:6379/0"
    redis_namespace: str = "ts"  # Trade Strategy namespace
    redis_ttl_seconds: int = 300
    redis_max_connections: int = 50
    
    # Security configuration
    secret_key: str = Field(default_factory=lambda: Fernet.generate_key().decode())
    encryption_key: str = Field(default_factory=lambda: Fernet.generate_key().decode())
    api_key_header: str = "X-API-Key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Integration with existing systems
    zmartbot_api_url: str = "http://localhost:8000"
    kingfisher_api_url: str = "http://localhost:8100"
    shared_database_url: str = "postgresql://postgres:postgres@localhost:5432/trading_platform"
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "logs/trade_strategy.log"
    log_max_bytes: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5
    
    # Performance and monitoring
    enable_metrics: bool = True
    metrics_port: int = 8202
    health_check_interval: int = 30
    performance_monitoring: bool = True
    
    # Trading configuration
    position_scaling: PositionScalingConfig = field(default_factory=PositionScalingConfig)
    risk_management: RiskManagementConfig = field(default_factory=RiskManagementConfig)
    signal_processing: SignalProcessingConfig = field(default_factory=SignalProcessingConfig)
    
    # Exchange configurations
    supported_exchanges: List[str] = field(default_factory=lambda: [
        "binance", "kucoin", "bybit", "okx", "bitget"
    ])
    
    # API rate limiting
    api_rate_limit_per_minute: int = 1000
    api_burst_limit: int = 100
    
    # Celery configuration for background tasks
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/1"
    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"
    celery_timezone: str = "UTC"
    
    # WebSocket configuration
    websocket_heartbeat_interval: int = 30
    websocket_max_connections: int = 1000
    websocket_message_queue_size: int = 10000
    
    # Data retention policies
    raw_signals_retention_days: int = 30
    processed_signals_retention_days: int = 90
    audit_log_retention_days: int = 180
    performance_data_retention_days: int = 365
    
    class Config:
        env_file = ".env.trade_strategy"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @validator('database_url')
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(('postgresql://', 'postgresql+psycopg2://')):
            raise ValueError('Database URL must start with postgresql:// or postgresql+psycopg2://')
        return v
    
    @validator('redis_url')
    def validate_redis_url(cls, v):
        """Validate Redis URL format."""
        if not v.startswith('redis://'):
            raise ValueError('Redis URL must start with redis://')
        return v
    
    @validator('api_port', 'frontend_port', 'websocket_port', 'metrics_port')
    def validate_ports(cls, v):
        """Validate port numbers are in valid range."""
        if not 1024 <= v <= 65535:
            raise ValueError('Port must be between 1024 and 65535')
        return v


class ConfigurationManager:
    """Advanced configuration management with encryption and caching."""
    
    def __init__(self, settings: TradeStrategySettings):
        self.settings = settings
        self._encryption_key = settings.encryption_key.encode()
        self._fernet = Fernet(self._encryption_key)
        self._cache = {}
        self._redis_client = None
        
    def get_redis_client(self) -> redis.Redis:
        """Get Redis client with proper configuration."""
        if self._redis_client is None:
            self._redis_client = redis.from_url(
                self.settings.redis_url,
                max_connections=self.settings.redis_max_connections,
                decode_responses=True
            )
        return self._redis_client
    
    def get_database_engine(self):
        """Get SQLAlchemy database engine."""
        return create_engine(
            self.settings.database_url,
            pool_size=self.settings.database_pool_size,
            max_overflow=self.settings.database_max_overflow,
            pool_timeout=self.settings.database_pool_timeout,
            pool_recycle=self.settings.database_pool_recycle,
            echo=self.settings.debug
        )
    
    def get_session_factory(self):
        """Get SQLAlchemy session factory."""
        engine = self.get_database_engine()
        return sessionmaker(bind=engine)
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt sensitive configuration values."""
        return self._fernet.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt sensitive configuration values."""
        return self._fernet.decrypt(encrypted_value.encode()).decode()
    
    def get_exchange_config(self, exchange: str, vault_id: str) -> Dict[str, Any]:
        """Get exchange configuration for specific vault."""
        cache_key = f"exchange_config:{exchange}:{vault_id}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # In production, this would fetch from database
        # For now, return default configuration
        config = {
            "exchange": exchange,
            "testnet": self.settings.environment != Environment.PRODUCTION,
            "rate_limit": 1000,
            "timeout": 30,
            "retry_count": 3
        }
        
        self._cache[cache_key] = config
        return config
    
    def update_runtime_config(self, key: str, value: Any) -> None:
        """Update runtime configuration values."""
        redis_client = self.get_redis_client()
        cache_key = f"{self.settings.redis_namespace}:config:{key}"
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        redis_client.setex(
            cache_key,
            self.settings.redis_ttl_seconds,
            str(value)
        )
        
        # Update local cache
        self._cache[key] = value
    
    def get_runtime_config(self, key: str, default: Any = None) -> Any:
        """Get runtime configuration values."""
        # Check local cache first
        if key in self._cache:
            return self._cache[key]
        
        # Check Redis cache
        redis_client = self.get_redis_client()
        cache_key = f"{self.settings.redis_namespace}:config:{key}"
        
        value = redis_client.get(cache_key)
        if value is not None:
            try:
                # Try to parse as JSON
                parsed_value = json.loads(value)
                self._cache[key] = parsed_value
                return parsed_value
            except json.JSONDecodeError:
                # Return as string if not JSON
                self._cache[key] = value
                return value
        
        return default
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Check port conflicts
        ports = [
            self.settings.api_port,
            self.settings.frontend_port,
            self.settings.websocket_port,
            self.settings.metrics_port
        ]
        
        if len(ports) != len(set(ports)):
            issues.append("Port conflicts detected in configuration")
        
        # Check database connectivity
        try:
            engine = self.get_database_engine()
            with engine.connect() as conn:
                conn.execute("SELECT 1")
        except Exception as e:
            issues.append(f"Database connection failed: {str(e)}")
        
        # Check Redis connectivity
        try:
            redis_client = self.get_redis_client()
            redis_client.ping()
        except Exception as e:
            issues.append(f"Redis connection failed: {str(e)}")
        
        # Validate scaling configuration
        scaling = self.settings.position_scaling
        total_bankroll = (
            scaling.stage_1_bankroll_pct +
            scaling.stage_2_bankroll_pct +
            scaling.stage_3_bankroll_pct +
            scaling.stage_4_bankroll_pct
        )
        
        if total_bankroll > Decimal('0.20'):  # 20% max total exposure
            issues.append(f"Total position scaling exceeds 20% of bankroll: {total_bankroll}")
        
        return issues


class DevelopmentConfig(TradeStrategySettings):
    """Development environment configuration."""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    log_level: str = "DEBUG"
    
    # Use local test database
    database_url: str = "postgresql://trade_strategy_app:secure_app_password_2025@localhost:5432/trading_platform_dev"
    
    # Reduced limits for development
    api_rate_limit_per_minute: int = 100
    redis_ttl_seconds: int = 60


class ProductionConfig(TradeStrategySettings):
    """Production environment configuration."""
    environment: Environment = Environment.PRODUCTION
    debug: bool = False
    log_level: str = "INFO"
    
    # Enhanced security for production
    api_rate_limit_per_minute: int = 2000
    jwt_expiration_hours: int = 12
    
    # Longer retention for production
    audit_log_retention_days: int = 365
    performance_data_retention_days: int = 730


class TestingConfig(TradeStrategySettings):
    """Testing environment configuration."""
    environment: Environment = Environment.TESTING
    debug: bool = True
    testing: bool = True
    log_level: str = "DEBUG"
    
    # Use in-memory database for testing
    database_url: str = "sqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/15"  # Use separate Redis DB
    
    # Minimal retention for testing
    raw_signals_retention_days: int = 1
    processed_signals_retention_days: int = 7
    audit_log_retention_days: int = 7


def get_settings(environment: Optional[str] = None) -> TradeStrategySettings:
    """Get configuration settings based on environment."""
    env = environment or os.getenv("TRADE_STRATEGY_ENV", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
        "staging": TradeStrategySettings  # Use base config for staging
    }
    
    config_class = config_map.get(env.lower(), DevelopmentConfig)
    return config_class()


def setup_logging(settings: TradeStrategySettings) -> None:
    """Setup logging configuration."""
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format,
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler()
        ]
    )
    
    # Set specific log levels for third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)


# Global configuration instance
settings = get_settings()
config_manager = ConfigurationManager(settings)

# Setup logging
setup_logging(settings)

# Create logger for this module
logger = logging.getLogger(__name__)

# Log configuration loading
logger.info(f"Trade Strategy Module configuration loaded")
logger.info(f"Environment: {settings.environment}")
logger.info(f"API Port: {settings.api_port}")
logger.info(f"Frontend Port: {settings.frontend_port}")
logger.info(f"Database Schema: {settings.database_schema}")
logger.info(f"Redis Namespace: {settings.redis_namespace}")

# Validate configuration on import
validation_issues = config_manager.validate_configuration()
if validation_issues:
    logger.warning("Configuration validation issues found:")
    for issue in validation_issues:
        logger.warning(f"  - {issue}")
else:
    logger.info("Configuration validation passed successfully")


# Export commonly used objects
__all__ = [
    'TradeStrategySettings',
    'ConfigurationManager',
    'Environment',
    'RiskLevel',
    'SignalType',
    'PositionScalingConfig',
    'RiskManagementConfig',
    'SignalProcessingConfig',
    'settings',
    'config_manager',
    'get_settings',
    'setup_logging'
]

