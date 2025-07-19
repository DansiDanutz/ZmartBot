"""
Zmart Trading Bot Platform - Configuration Settings
"""
import os
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "zmart_platform")
    user: str = os.getenv("DB_USER", "zmart_user")
    password: str = os.getenv("DB_PASSWORD", "")
    
    # Time-series database (InfluxDB)
    influx_host: str = os.getenv("INFLUX_HOST", "localhost")
    influx_port: int = int(os.getenv("INFLUX_PORT", "8086"))
    influx_database: str = os.getenv("INFLUX_DATABASE", "zmart_timeseries")
    influx_username: str = os.getenv("INFLUX_USERNAME", "")
    influx_password: str = os.getenv("INFLUX_PASSWORD", "")
    
    # Redis configuration
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))

@dataclass
class SecurityConfig:
    """Security and authentication configuration"""
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    jwt_secret: str = os.getenv("JWT_SECRET", "your-jwt-secret-change-in-production")
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    jwt_refresh_expiration_days: int = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", "30"))
    
    # API rate limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    rate_limit_per_hour: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # CORS settings
    cors_origins: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Encryption settings
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "")
    password_salt: str = os.getenv("PASSWORD_SALT", "zmart-platform-salt")

@dataclass
class TradingConfig:
    """Trading engine configuration"""
    # Risk management
    max_position_size_percent: float = float(os.getenv("MAX_POSITION_SIZE_PERCENT", "10.0"))
    max_daily_loss_percent: float = float(os.getenv("MAX_DAILY_LOSS_PERCENT", "5.0"))
    max_drawdown_percent: float = float(os.getenv("MAX_DRAWDOWN_PERCENT", "15.0"))
    
    # Signal processing
    signal_confidence_threshold: float = float(os.getenv("SIGNAL_CONFIDENCE_THRESHOLD", "0.7"))
    max_signals_per_hour: int = int(os.getenv("MAX_SIGNALS_PER_HOUR", "100"))
    signal_processing_timeout: int = int(os.getenv("SIGNAL_PROCESSING_TIMEOUT", "30"))
    
    # Trading execution
    trade_execution_timeout: int = int(os.getenv("TRADE_EXECUTION_TIMEOUT", "10"))
    min_trade_amount_usd: float = float(os.getenv("MIN_TRADE_AMOUNT_USD", "10.0"))
    max_trade_amount_usd: float = float(os.getenv("MAX_TRADE_AMOUNT_USD", "10000.0"))
    
    # Paper trading
    paper_trading_enabled: bool = os.getenv("PAPER_TRADING_ENABLED", "true").lower() == "true"
    paper_trading_initial_balance: float = float(os.getenv("PAPER_TRADING_INITIAL_BALANCE", "100000.0"))

@dataclass
class ExchangeConfig:
    """Exchange API configuration"""
    # KuCoin configuration
    kucoin_api_key: str = os.getenv("KUCOIN_API_KEY", "")
    kucoin_api_secret: str = os.getenv("KUCOIN_API_SECRET", "")
    kucoin_api_passphrase: str = os.getenv("KUCOIN_API_PASSPHRASE", "")
    kucoin_sandbox: bool = os.getenv("KUCOIN_SANDBOX", "true").lower() == "true"
    
    # Binance configuration
    binance_api_key: str = os.getenv("BINANCE_API_KEY", "")
    binance_api_secret: str = os.getenv("BINANCE_API_SECRET", "")
    binance_testnet: bool = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
    
    # Coinbase configuration
    coinbase_api_key: str = os.getenv("COINBASE_API_KEY", "")
    coinbase_api_secret: str = os.getenv("COINBASE_API_SECRET", "")
    coinbase_sandbox: bool = os.getenv("COINBASE_SANDBOX", "true").lower() == "true"

@dataclass
class BlockchainConfig:
    """Blockchain and Web3 configuration"""
    # Ethereum
    ethereum_rpc_url: str = os.getenv("ETHEREUM_RPC_URL", "https://mainnet.infura.io/v3/your-project-id")
    ethereum_testnet_rpc_url: str = os.getenv("ETHEREUM_TESTNET_RPC_URL", "https://goerli.infura.io/v3/your-project-id")
    
    # Binance Smart Chain
    bsc_rpc_url: str = os.getenv("BSC_RPC_URL", "https://bsc-dataseed1.binance.org/")
    bsc_testnet_rpc_url: str = os.getenv("BSC_TESTNET_RPC_URL", "https://data-seed-prebsc-1-s1.binance.org:8545/")
    
    # Polygon
    polygon_rpc_url: str = os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com/")
    polygon_testnet_rpc_url: str = os.getenv("POLYGON_TESTNET_RPC_URL", "https://rpc-mumbai.maticvigil.com/")
    
    # Wallet configuration
    private_key: str = os.getenv("WALLET_PRIVATE_KEY", "")
    gas_price_gwei: int = int(os.getenv("GAS_PRICE_GWEI", "20"))
    gas_limit: int = int(os.getenv("GAS_LIMIT", "200000"))

@dataclass
class AIConfig:
    """AI and machine learning configuration"""
    # OpenAI configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Model training
    model_retrain_interval_hours: int = int(os.getenv("MODEL_RETRAIN_INTERVAL_HOURS", "24"))
    model_validation_split: float = float(os.getenv("MODEL_VALIDATION_SPLIT", "0.2"))
    model_confidence_threshold: float = float(os.getenv("MODEL_CONFIDENCE_THRESHOLD", "0.8"))
    
    # Signal generation
    technical_analysis_enabled: bool = os.getenv("TECHNICAL_ANALYSIS_ENABLED", "true").lower() == "true"
    sentiment_analysis_enabled: bool = os.getenv("SENTIMENT_ANALYSIS_ENABLED", "true").lower() == "true"
    fundamental_analysis_enabled: bool = os.getenv("FUNDAMENTAL_ANALYSIS_ENABLED", "true").lower() == "true"

@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration"""
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "json")
    
    # Metrics and monitoring
    prometheus_enabled: bool = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
    prometheus_port: int = int(os.getenv("PROMETHEUS_PORT", "9090"))
    
    # Health checks
    health_check_interval: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
    
    # Alerting
    slack_webhook_url: str = os.getenv("SLACK_WEBHOOK_URL", "")
    email_alerts_enabled: bool = os.getenv("EMAIL_ALERTS_ENABLED", "false").lower() == "true"
    email_smtp_host: str = os.getenv("EMAIL_SMTP_HOST", "")
    email_smtp_port: int = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    email_username: str = os.getenv("EMAIL_USERNAME", "")
    email_password: str = os.getenv("EMAIL_PASSWORD", "")

class Settings:
    """Main settings class that aggregates all configuration"""
    
    def __init__(self):
        self.environment = Environment(os.getenv("ENVIRONMENT", "development"))
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "5000"))
        
        # Configuration sections
        self.database = DatabaseConfig()
        self.security = SecurityConfig()
        self.trading = TradingConfig()
        self.exchange = ExchangeConfig()
        self.blockchain = BlockchainConfig()
        self.ai = AIConfig()
        self.monitoring = MonitoringConfig()
    
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION
    
    def is_testing(self) -> bool:
        return self.environment == Environment.TESTING
    
    def get_database_url(self) -> str:
        """Get PostgreSQL database URL"""
        return f"postgresql://{self.database.user}:{self.database.password}@{self.database.host}:{self.database.port}/{self.database.name}"
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.database.redis_password:
            return f"redis://:{self.database.redis_password}@{self.database.redis_host}:{self.database.redis_port}/{self.database.redis_db}"
        return f"redis://{self.database.redis_host}:{self.database.redis_port}/{self.database.redis_db}"
    
    def get_influx_config(self) -> Dict[str, Any]:
        """Get InfluxDB configuration"""
        return {
            "host": self.database.influx_host,
            "port": self.database.influx_port,
            "database": self.database.influx_database,
            "username": self.database.influx_username,
            "password": self.database.influx_password
        }

# Global settings instance
settings = Settings()

