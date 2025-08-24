"""Configuration settings for the Symbol Alerts System."""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    url: str = Field(default="sqlite:///./alerts.db", env="DATABASE_URL")
    echo: bool = Field(default=False, env="DATABASE_ECHO")
    pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")


class RedisSettings(BaseSettings):
    """Redis configuration."""
    url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")


class APISettings(BaseSettings):
    """API server configuration."""
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=1, env="API_WORKERS")
    reload: bool = Field(default=False, env="API_RELOAD")
    secret_key: str = Field(default="your-secret-key-here", env="API_SECRET_KEY")


class WebSocketSettings(BaseSettings):
    """WebSocket server configuration."""
    host: str = Field(default="0.0.0.0", env="WS_HOST")
    port: int = Field(default=8001, env="WS_PORT")
    ping_interval: int = Field(default=20, env="WS_PING_INTERVAL")
    ping_timeout: int = Field(default=10, env="WS_PING_TIMEOUT")


class ExchangeSettings(BaseSettings):
    """Exchange API configuration."""
    binance_api_key: Optional[str] = Field(default=None, env="BINANCE_API_KEY")
    binance_secret: Optional[str] = Field(default=None, env="BINANCE_SECRET")
    kucoin_api_key: Optional[str] = Field(default=None, env="KUCOIN_API_KEY")
    kucoin_secret: Optional[str] = Field(default=None, env="KUCOIN_SECRET")
    kucoin_passphrase: Optional[str] = Field(default=None, env="KUCOIN_PASSPHRASE")
    sandbox_mode: bool = Field(default=True, env="EXCHANGE_SANDBOX")


class AlertSettings(BaseSettings):
    """Alert system configuration."""
    max_alerts_per_user: int = Field(default=100, env="MAX_ALERTS_PER_USER")
    default_cooldown_minutes: int = Field(default=5, env="DEFAULT_COOLDOWN_MINUTES")
    max_trigger_history: int = Field(default=1000, env="MAX_TRIGGER_HISTORY")
    cleanup_interval_hours: int = Field(default=24, env="CLEANUP_INTERVAL_HOURS")


class NotificationSettings(BaseSettings):
    """Notification configuration."""
    webhook_timeout: int = Field(default=10, env="WEBHOOK_TIMEOUT")
    max_retries: int = Field(default=3, env="WEBHOOK_MAX_RETRIES")
    retry_delay_base: int = Field(default=2, env="WEBHOOK_RETRY_DELAY_BASE")
    queue_size_limit: int = Field(default=10000, env="NOTIFICATION_QUEUE_LIMIT")


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH")
    max_file_size: int = Field(default=10485760, env="LOG_MAX_FILE_SIZE")  # 10MB
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")


class SecuritySettings(BaseSettings):
    """Security configuration."""
    jwt_secret_key: str = Field(default="your-jwt-secret-here", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    webhook_signature_secret: Optional[str] = Field(default=None, env="WEBHOOK_SIGNATURE_SECRET")


class MonitoringSettings(BaseSettings):
    """Monitoring and metrics configuration."""
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=8002, env="METRICS_PORT")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Component settings
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    api: APISettings = APISettings()
    websocket: WebSocketSettings = WebSocketSettings()
    exchange: ExchangeSettings = ExchangeSettings()
    alerts: AlertSettings = AlertSettings()
    notifications: NotificationSettings = NotificationSettings()
    logging: LoggingSettings = LoggingSettings()
    security: SecuritySettings = SecuritySettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def update_settings(**kwargs):
    """Update settings dynamically."""
    global settings
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)


def load_settings_from_file(file_path: str):
    """Load settings from a configuration file."""
    global settings
    settings = Settings(_env_file=file_path)

