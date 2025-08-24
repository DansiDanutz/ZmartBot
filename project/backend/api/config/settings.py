"""
Zmart Trading Bot Platform - Configuration Settings
Centralized configuration management for all platform components
"""
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Environment Configuration
    ENVIRONMENT: str = Field(default="development", alias="ENVIRONMENT")
    DEBUG: bool = Field(default=True, alias="DEBUG")
    HOST: str = Field(default="0.0.0.0", alias="HOST")
    PORT: int = Field(default=8000, alias="PORT")
    
    # Database Configuration
    DB_HOST: str = Field(default="localhost", alias="DB_HOST")
    DB_PORT: int = Field(default=5432, alias="DB_PORT")
    DB_NAME: str = Field(default="zmart_platform", alias="DB_NAME")
    DB_USER: str = Field(default="zmart_user", alias="DB_USER")
    DB_PASSWORD: str = Field(default="zmart_password_dev", alias="DB_PASSWORD")
    DB_POOL_SIZE: int = Field(default=20, alias="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=30, alias="DB_MAX_OVERFLOW")
    
    # Redis Configuration
    REDIS_HOST: str = Field(default="localhost", alias="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, alias="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, alias="REDIS_DB")
    
    # InfluxDB Configuration
    INFLUX_HOST: str = Field(default="localhost", alias="INFLUX_HOST")
    INFLUX_PORT: int = Field(default=8086, alias="INFLUX_PORT")
    INFLUX_TOKEN: str = Field(default="zmart-super-secret-auth-token", alias="INFLUX_TOKEN")
    INFLUX_ORG: str = Field(default="zmart", alias="INFLUX_ORG")
    INFLUX_BUCKET: str = Field(default="trading_data", alias="INFLUX_BUCKET")
    
    # RabbitMQ Configuration
    RABBITMQ_HOST: str = Field(default="localhost", alias="RABBITMQ_HOST")
    RABBITMQ_PORT: int = Field(default=5672, alias="RABBITMQ_PORT")
    RABBITMQ_USER: str = Field(default="zmart_user", alias="RABBITMQ_USER")
    RABBITMQ_PASSWORD: str = Field(default="zmart_rabbitmq_password", alias="RABBITMQ_PASSWORD")
    RABBITMQ_VHOST: str = Field(default="zmart_vhost", alias="RABBITMQ_VHOST")
    
    # Security Configuration
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", alias="SECRET_KEY")
    JWT_SECRET: str = Field(default="dev-jwt-secret-change-in-production", alias="JWT_SECRET")
    JWT_ALGORITHM: str = Field(default="HS256", alias="JWT_ALGORITHM")
    JWT_EXPIRATION: int = Field(default=3600, alias="JWT_EXPIRATION")  # 1 hour
    JWT_REFRESH_EXPIRATION: int = Field(default=604800, alias="JWT_REFRESH_EXPIRATION")  # 7 days
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:3400",  # Professional Dashboard module
        ],
        alias="CORS_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1", "testserver"],
        alias="ALLOWED_HOSTS"
    )
    
    # Trading Configuration
    DEFAULT_LEVERAGE: int = Field(default=20, alias="DEFAULT_LEVERAGE")
    MAX_POSITION_SIZE: float = Field(default=1000.0, alias="MAX_POSITION_SIZE")
    MIN_POSITION_SIZE: float = Field(default=10.0, alias="MIN_POSITION_SIZE")
    RISK_FREE_RATE: float = Field(default=0.02, alias="RISK_FREE_RATE")
    
        # API Configuration - MUST be set via environment variables
    KUCOIN_API_KEY: str = Field(default="", alias="KUCOIN_API_KEY")
    KUCOIN_SECRET: str = Field(default="", alias="KUCOIN_SECRET")
    KUCOIN_PASSPHRASE: str = Field(default="", alias="KUCOIN_PASSPHRASE")
    KUCOIN_BROKER_NAME: str = Field(default="", alias="KUCOIN_BROKER_NAME")
    KUCOIN_API_PARTNER: str = Field(default="", alias="KUCOIN_API_PARTNER")
    KUCOIN_API_PARTNER_SECRET: str = Field(default="", alias="KUCOIN_API_PARTNER_SECRET")
    CRYPTOMETER_API_KEY: str = Field(default="", alias="CRYPTOMETER_API_KEY")
    
    # Binance API Configuration - MUST be set via environment variables
    BINANCE_API_KEY: str = Field(default="", alias="BINANCE_API_KEY")
    BINANCE_SECRET: str = Field(default="", alias="BINANCE_SECRET")
    
    # OpenAI Configuration - Use environment variables for security
    OPENAI_API_KEY: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    OPENAI_API_KEY_TRADING: Optional[str] = Field(default=None, alias="OPENAI_API_KEY_TRADING")
    
    # Monitoring Configuration
    PROMETHEUS_PORT: int = Field(default=9090, alias="PROMETHEUS_PORT")
    GRAFANA_PORT: int = Field(default=3001, alias="GRAFANA_PORT")
    METRICS_ENABLED: bool = Field(default=False, alias="METRICS_ENABLED")
    
    # Agent Configuration
    SCORING_AGENT_ENABLED: bool = Field(default=True, alias="SCORING_AGENT_ENABLED")
    RISK_GUARD_AGENT_ENABLED: bool = Field(default=True, alias="RISK_GUARD_AGENT_ENABLED")
    SIGNAL_GENERATOR_AGENT_ENABLED: bool = Field(default=True, alias="SIGNAL_GENERATOR_AGENT_ENABLED")
    
    # Signal Configuration
    SIGNAL_CONFIDENCE_THRESHOLD: float = Field(default=0.7, alias="SIGNAL_CONFIDENCE_THRESHOLD")
    MAX_SIGNALS_PER_HOUR: int = Field(default=100, alias="MAX_SIGNALS_PER_HOUR")
    SIGNAL_RATE_LIMIT_WINDOW: int = Field(default=3600, alias="SIGNAL_RATE_LIMIT_WINDOW")
    
    # Risk Management Configuration
    CIRCUIT_BREAKER_THRESHOLD: float = Field(default=0.1, alias="CIRCUIT_BREAKER_THRESHOLD")
    MAX_DAILY_LOSS: float = Field(default=0.05, alias="MAX_DAILY_LOSS")
    MAX_DRAWDOWN: float = Field(default=0.15, alias="MAX_DRAWDOWN")
    
    # Blockchain Configuration
    WEB3_PROVIDER_URL: Optional[str] = Field(default=None, alias="WEB3_PROVIDER_URL")
    SMART_CONTRACT_ADDRESS: Optional[str] = Field(default=None, alias="SMART_CONTRACT_ADDRESS")
    GAS_LIMIT: int = Field(default=300000, alias="GAS_LIMIT")
    
    # Google Sheets Configuration
    GOOGLE_SHEETS_CREDENTIALS: Optional[str] = Field(default=None, alias="GOOGLE_SHEETS_CREDENTIALS")

    HISTORICAL_RISK_SHEET_ID: str = Field(
        default="1fup2CUYxg7Tj3a2BvpoN3OcfGBoSe7EqHIxmp1RRjqg",
        alias="HISTORICAL_RISK_SHEET_ID"
    )
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, alias="MAX_FILE_SIZE")  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif"],
        alias="ALLOWED_IMAGE_TYPES"
    )
    UPLOAD_DIR: str = Field(default="./uploads", alias="UPLOAD_DIR")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        alias="LOG_FORMAT"
    )
    
    # Performance Configuration
    WORKER_PROCESSES: int = Field(default=4, alias="WORKER_PROCESSES")
    MAX_CONCURRENT_REQUESTS: int = Field(default=1000, alias="MAX_CONCURRENT_REQUESTS")
    REQUEST_TIMEOUT: int = Field(default=30, alias="REQUEST_TIMEOUT")
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: Optional[str] = Field(default=None, alias="TELEGRAM_CHAT_ID")
    TELEGRAM_ENABLED: bool = Field(default=False, alias="TELEGRAM_ENABLED")
    
    # X (Twitter) API Configuration
    X_CLIENT_ID: Optional[str] = Field(default=None, alias="X_CLIENT_ID")
    X_CLIENT_SECRET: Optional[str] = Field(default=None, alias="X_CLIENT_SECRET")
    X_API_KEY: Optional[str] = Field(default=None, alias="X_API_KEY")
    X_API_KEY_SECRET: Optional[str] = Field(default=None, alias="X_API_KEY_SECRET")
    X_BEARER_TOKEN: Optional[str] = Field(default=None, alias="X_BEARER_TOKEN")
    X_ACCESS_TOKEN: Optional[str] = Field(default=None, alias="X_ACCESS_TOKEN")
    X_ACCESS_TOKEN_SECRET: Optional[str] = Field(default=None, alias="X_ACCESS_TOKEN_SECRET")
    
    # Grok API Configuration
    GROK_API_KEY: Optional[str] = Field(default=None, alias="GROK_API_KEY")
    
    # Blockchain API Keys
    ETHERSCAN_API_KEY: Optional[str] = Field(default=None, alias="ETHERSCAN_API_KEY")
    SOLSCAN_API_KEY: Optional[str] = Field(default=None, alias="SOLSCAN_API_KEY")
    TRONSCAN_API_KEY: Optional[str] = Field(default=None, alias="TRONSCAN_API_KEY")
    
    # Airtable Configuration
    AIRTABLE_API_KEY: Optional[str] = Field(default=None, alias="AIRTABLE_API_KEY")
    AIRTABLE_BASE_ID: Optional[str] = Field(default=None, alias="AIRTABLE_BASE_ID")
    
    # Additional APIs
    COINGECKO_API_KEY: Optional[str] = Field(default=None, alias="COINGECKO_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    
    # Email Configuration
    MAIL_USERNAME: Optional[str] = Field(default=None, alias="MAIL_USERNAME")
    MAIL_PASSWORD: Optional[str] = Field(default=None, alias="MAIL_PASSWORD")
    
    # Additional Monitoring & Feature Flags (from .env)
    PROMETHEUS_ENABLED: bool = Field(default=True, alias="PROMETHEUS_ENABLED")
    METRICS_PORT: int = Field(default=9090, alias="METRICS_PORT")
    RATE_LIMIT_ENABLED: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, alias="RATE_LIMIT_PER_HOUR")
    
    # Feature Flags
    ENABLE_MOCK_MODE: bool = Field(default=False, alias="ENABLE_MOCK_MODE")
    ENABLE_PAPER_TRADING: bool = Field(default=True, alias="ENABLE_PAPER_TRADING")
    ENABLE_LIVE_TRADING: bool = Field(default=False, alias="ENABLE_LIVE_TRADING")
    ENABLE_AI_PREDICTIONS: bool = Field(default=False, alias="ENABLE_AI_PREDICTIONS")
    ENABLE_KINGFISHER: bool = Field(default=False, alias="ENABLE_KINGFISHER")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from .env file

# Global settings instance
settings = Settings()

# Database URL construction
def get_database_url() -> str:
    """Construct database URL from settings"""
    return f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Redis URL construction
def get_redis_url() -> str:
    """Construct Redis URL from settings"""
    if settings.REDIS_PASSWORD:
        return f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
    return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

# InfluxDB URL construction
def get_influxdb_url() -> str:
    """Construct InfluxDB URL from settings"""
    return f"http://{settings.INFLUX_HOST}:{settings.INFLUX_PORT}"

# RabbitMQ URL construction
def get_rabbitmq_url() -> str:
    """Construct RabbitMQ URL from settings"""
    return f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/{settings.RABBITMQ_VHOST}" 