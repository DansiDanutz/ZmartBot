from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://localhost/zmarty_dashboard"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Zmarty Dashboard API"
    VERSION: str = "1.0.0"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # Redis (for WebSocket and caching)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Payment Processing (Stripe)
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # Credit System Configuration
    DEFAULT_CREDIT_COSTS: dict = {
        "basic_query": 1,
        "market_analysis": 3,
        "trading_strategy": 5,
        "ai_predictions": 8,
        "live_signals": 10,
        "custom_research": 25
    }
    
    # Zmarty AI Configuration
    ZMARTY_API_KEY: str = ""
    ZMARTY_MODEL: str = "gpt-4-turbo"
    ZMARTY_MAX_TOKENS: int = 4000
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS_PER_USER: int = 3
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: set = {".jpg", ".jpeg", ".png", ".pdf", ".csv", ".json"}
    
    # Email Configuration (for notifications)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@zmartydashboard.com"
    
    # MCP Configuration
    MCP_FIGMA_SERVER_URL: str = "http://localhost:3001"
    MCP_FIGMA_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()