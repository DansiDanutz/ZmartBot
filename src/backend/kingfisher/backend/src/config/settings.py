#!/usr/bin/env python3
"""
KingFisher Module Configuration
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8100
    DEBUG: bool = True
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Database settings
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # Telegram settings
    TELEGRAM_API_ID: str = os.getenv("TELEGRAM_API_ID", "")
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    KINGFISHER_CHANNEL: str = os.getenv("KINGFISHER_CHANNEL", "@KingFisherAutomation")
    
    # Image processing settings
    IMAGE_PROCESSING_ENABLED: bool = True
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    SUPPORTED_FORMATS: str = "jpg,jpeg,png,webp"
    
    @property
    def supported_formats(self) -> list:
        """Get supported image formats"""
        return self.SUPPORTED_FORMATS.split(",")
    
    # Liquidation analysis settings
    LIQUIDATION_SCORE_THRESHOLD: float = 0.7
    CLUSTER_DENSITY_THRESHOLD: float = 0.5
    TOXIC_FLOW_THRESHOLD: float = 0.3
    LIQUIDATION_THRESHOLD: float = 0.7
    CLUSTER_DENSITY_THRESHOLD: float = 0.5
    TOXIC_FLOW_THRESHOLD: float = 0.3
    
    # Integration settings
    ZMARTBOT_API_URL: str = os.getenv("ZMARTBOT_API_URL", "http://localhost:8000")
    ZMARTBOT_API_KEY: str = os.getenv("ZMARTBOT_API_KEY", "")
    
    # Monitoring settings
    MONITORING_ENABLED: bool = True
    METRICS_PORT: int = 9100
    ENABLE_METRICS: bool = True
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()

def get_database_url() -> str:
    """Get database URL"""
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    
    # Default to SQLite for development
    return "sqlite:///./kingfisher.db"

def get_redis_url() -> str:
    """Get Redis URL"""
    if settings.REDIS_URL:
        return settings.REDIS_URL
    
    # Default to local Redis
    return "redis://localhost:6379/1" 