from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "dev"
    APP_NAME: str = "ZmartBot Foundation"
    SECRET_KEY: str = "dev"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite+aiosqlite:///./zmart.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    OTEL_SERVICE_NAME: str = "zmart-foundation"
    BINANCE_BASE: Optional[str] = None
    KUCOIN_BASE: Optional[str] = None
    CRYPTOMETER_BASE: Optional[str] = None
    CRYPTOMETER_API_KEY: Optional[str] = None
    KINGFISHER_BASE: Optional[str] = None
    KINGFISHER_API_KEY: Optional[str] = None
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    RISK_HISTORY_CSV: Optional[str] = None
    class Config:
        env_file = ".env"

settings = Settings()
