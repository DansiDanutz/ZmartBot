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
        default=["http://localhost:3000", "http://localhost:5173"],
        alias="CORS_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        alias="ALLOWED_HOSTS"
    )
    
    # Trading Configuration
    DEFAULT_LEVERAGE: int = Field(default=20, alias="DEFAULT_LEVERAGE")
    MAX_POSITION_SIZE: float = Field(default=1000.0, alias="MAX_POSITION_SIZE")
    MIN_POSITION_SIZE: float = Field(default=10.0, alias="MIN_POSITION_SIZE")
    RISK_FREE_RATE: float = Field(default=0.02, alias="RISK_FREE_RATE")
    
    # API Configuration
    KUCOIN_API_KEY: Optional[str] = Field(default=None, alias="KUCOIN_API_KEY")
    KUCOIN_SECRET: Optional[str] = Field(default=None, alias="KUCOIN_SECRET")
    KUCOIN_PASSPHRASE: Optional[str] = Field(default=None, alias="KUCOIN_PASSPHRASE")
    CRYPTOMETER_API_KEY: str = Field(default="k77U187e08zGf4I3SLz3sYzTEyM2KNoJ9i1N4xg2", alias="CRYPTOMETER_API_KEY")
    
    # Monitoring Configuration
    PROMETHEUS_PORT: int = Field(default=9090, alias="PROMETHEUS_PORT")
    GRAFANA_PORT: int = Field(default=3001, alias="GRAFANA_PORT")
    METRICS_ENABLED: bool = Field(default=True, alias="METRICS_ENABLED")
    
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
    RISKMETRIC_SHEET_ID: str = Field(
        default="1Z9h8bBP13cdcgkcwq32N5Pcx4wiue9iH69uJ0wm9MRY",
        alias="RISKMETRIC_SHEET_ID"
    )
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False

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