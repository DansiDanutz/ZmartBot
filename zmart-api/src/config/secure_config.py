#!/usr/bin/env python3
"""
Secure Configuration Manager
Loads API keys and sensitive data from environment variables only
Never stores credentials in code or configuration files
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class SecureConfig:
    """
    Secure configuration manager that loads all sensitive data from environment variables
    """
    
    def __init__(self):
        # Load environment variables from .env file if it exists
        env_path = Path(__file__).parent.parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Loaded environment from {env_path}")
        else:
            logger.warning("No .env file found, using system environment variables")
        
        # Validate critical API keys are present
        self._validate_critical_keys()
    
    def _validate_critical_keys(self):
        """Validate that critical API keys are present"""
        critical_keys = [
            'CRYPTOMETER_API_KEY',
            'OPENAI_API_KEY'
        ]
        
        missing_keys = []
        for key in critical_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        if missing_keys:
            logger.warning(f"Missing critical API keys: {missing_keys}")
    
    @staticmethod
    def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable value
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Environment variable value or default
        """
        value = os.getenv(key, default)
        if value and value.startswith('your_') and value.endswith('_here'):
            logger.warning(f"{key} appears to be a placeholder value")
            return None
        return value
    
    @property
    def kucoin_config(self) -> Dict[str, Optional[str]]:
        """Get KuCoin API configuration"""
        return {
            'api_key': self.get_env('KUCOIN_API_KEY'),
            'secret': self.get_env('KUCOIN_SECRET'),
            'passphrase': self.get_env('KUCOIN_PASSPHRASE'),
            'broker_name': self.get_env('KUCOIN_BROKER_NAME'),
            'partner': self.get_env('KUCOIN_API_PARTNER'),
            'partner_secret': self.get_env('KUCOIN_API_PARTNER_SECRET')
        }
    
    @property
    def binance_config(self) -> Dict[str, Optional[str]]:
        """Get Binance API configuration"""
        return {
            'api_key': self.get_env('BINANCE_API_KEY'),
            'secret': self.get_env('BINANCE_SECRET')
        }
    
    @property
    def cryptometer_api_key(self) -> Optional[str]:
        """Get Cryptometer API key"""
        return self.get_env('CRYPTOMETER_API_KEY')
    
    @property
    def openai_config(self) -> Dict[str, Optional[str]]:
        """Get OpenAI API configuration"""
        return {
            'api_key': self.get_env('OPENAI_API_KEY'),
            'trading_api_key': self.get_env('OPENAI_API_KEY_TRADING')
        }
    
    @property
    def telegram_config(self) -> Dict[str, Any]:
        """Get Telegram bot configuration"""
        enabled_str = self.get_env('TELEGRAM_ENABLED', 'false')
        return {
            'bot_token': self.get_env('TELEGRAM_BOT_TOKEN'),
            'chat_id': self.get_env('TELEGRAM_CHAT_ID'),
            'enabled': enabled_str.lower() == 'true' if enabled_str else False
        }
    
    @property
    def database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        port_str = self.get_env('DB_PORT', '5432')
        pool_size_str = self.get_env('DB_POOL_SIZE', '20')
        max_overflow_str = self.get_env('DB_MAX_OVERFLOW', '30')
        
        return {
            'host': self.get_env('DB_HOST', 'localhost'),
            'port': int(port_str) if port_str else 5432,
            'name': self.get_env('DB_NAME', 'zmart_platform'),
            'user': self.get_env('DB_USER'),
            'password': self.get_env('DB_PASSWORD'),
            'pool_size': int(pool_size_str) if pool_size_str else 20,
            'max_overflow': int(max_overflow_str) if max_overflow_str else 30
        }
    
    @property
    def redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        port_str = self.get_env('REDIS_PORT', '6379')
        db_str = self.get_env('REDIS_DB', '0')
        
        return {
            'host': self.get_env('REDIS_HOST', 'localhost'),
            'port': int(port_str) if port_str else 6379,
            'password': self.get_env('REDIS_PASSWORD'),
            'db': int(db_str) if db_str else 0
        }
    
    @property
    def security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        exp_str = self.get_env('JWT_EXPIRATION', '3600')
        refresh_str = self.get_env('JWT_REFRESH_EXPIRATION', '604800')
        
        return {
            'secret_key': self.get_env('SECRET_KEY', 'dev-secret-key') or 'dev-secret-key',
            'jwt_secret': self.get_env('JWT_SECRET', 'dev-jwt-secret') or 'dev-jwt-secret',
            'jwt_algorithm': self.get_env('JWT_ALGORITHM', 'HS256') or 'HS256',
            'jwt_expiration': int(exp_str) if exp_str else 3600,
            'jwt_refresh_expiration': int(refresh_str) if refresh_str else 604800
        }
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        env = self.get_env('ENVIRONMENT', 'development')
        return env.lower() == 'production' if env else False
    
    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        debug_str = self.get_env('DEBUG', 'False')
        return debug_str.lower() == 'true' if debug_str else False
    
    def get_api_key_for_service(self, service_name: str) -> Optional[str]:
        """
        Get API key for a specific service
        
        Args:
            service_name: Name of the service
            
        Returns:
            API key or None if not found
        """
        env_var_mapping = {
            'cryptometer': 'CRYPTOMETER_API_KEY',
            'binance': 'BINANCE_API_KEY',
            'kucoin': 'KUCOIN_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'etherscan': 'ETHERSCAN_API_KEY',
            'solscan': 'SOLSCAN_API_KEY',
            'telegram': 'TELEGRAM_BOT_TOKEN'
        }
        
        env_var = env_var_mapping.get(service_name.lower())
        if env_var:
            return self.get_env(env_var)
        
        logger.warning(f"No API key mapping found for service: {service_name}")
        return None
    
    def validate_trading_keys(self) -> Dict[str, bool]:
        """
        Validate that trading API keys are configured
        
        Returns:
            Dictionary with validation status for each exchange
        """
        validations = {}
        
        # Check KuCoin
        kucoin = self.kucoin_config
        validations['kucoin'] = all([
            kucoin.get('api_key'),
            kucoin.get('secret'),
            kucoin.get('passphrase')
        ])
        
        # Check Binance
        binance = self.binance_config
        validations['binance'] = all([
            binance.get('api_key'),
            binance.get('secret')
        ])
        
        return validations
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags configuration"""
        def parse_bool(value: Optional[str], default: bool = False) -> bool:
            if not value:
                return default
            return value.lower() == 'true'
        
        return {
            'mock_mode': parse_bool(self.get_env('ENABLE_MOCK_MODE', 'False')),
            'paper_trading': parse_bool(self.get_env('ENABLE_PAPER_TRADING', 'True'), True),
            'live_trading': parse_bool(self.get_env('ENABLE_LIVE_TRADING', 'False')),
            'ai_predictions': parse_bool(self.get_env('ENABLE_AI_PREDICTIONS', 'True'), True),
            'kingfisher': parse_bool(self.get_env('ENABLE_KINGFISHER', 'False'))
        }

# Create global instance
secure_config = SecureConfig()

# Helper functions for easy access
def get_api_key(service_name: str) -> Optional[str]:
    """Get API key for a service"""
    return secure_config.get_api_key_for_service(service_name)

def get_kucoin_credentials() -> Dict[str, Optional[str]]:
    """Get KuCoin API credentials"""
    return secure_config.kucoin_config

def get_binance_credentials() -> Dict[str, Optional[str]]:
    """Get Binance API credentials"""
    return secure_config.binance_config

def get_openai_key() -> Optional[str]:
    """Get OpenAI API key"""
    return secure_config.openai_config.get('api_key')

def get_cryptometer_key() -> Optional[str]:
    """Get Cryptometer API key"""
    return secure_config.cryptometer_api_key

def is_production() -> bool:
    """Check if running in production"""
    return secure_config.is_production

def validate_api_keys() -> Dict[str, bool]:
    """Validate all API keys"""
    return secure_config.validate_trading_keys()