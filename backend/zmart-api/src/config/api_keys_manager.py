#!/usr/bin/env python3
"""
API Keys Manager
Secure management of all API keys and configurations for external services
Provides centralized access to API credentials with security features
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import base64
from cryptography.fernet import Fernet
from dataclasses import dataclass, asdict, field
import yaml

logger = logging.getLogger(__name__)

@dataclass
class APIKeyConfig:
    """API Key configuration with metadata"""
    service_name: str
    api_key: str
    secret_key: Optional[str] = None
    passphrase: Optional[str] = None
    base_url: Optional[str] = None
    rate_limit: Optional[int] = None
    description: str = ""
    is_active: bool = True
    created_at: str = ""
    last_used: Optional[str] = None
    usage_count: int = 0

@dataclass
class ExchangeConfig:
    """Exchange-specific configuration"""
    name: str
    api_key: str
    secret_key: str
    passphrase: Optional[str] = None
    sandbox: bool = False
    testnet: bool = False
    base_url: Optional[str] = None
    rate_limit: int = 1000
    features: List[str] = field(default_factory=list)

class APIKeysManager:
    """
    Secure API Keys Manager
    Manages all external service API keys with encryption and access control
    """
    
    def __init__(self, config_file: str = "config/api_keys.yml", encrypt: bool = True):
        self.config_file = Path(config_file)
        self.encrypt = encrypt
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key) if encrypt else None
        
        # API configurations storage
        self.api_configs: Dict[str, APIKeyConfig] = {}
        self.exchange_configs: Dict[str, ExchangeConfig] = {}
        
        # Load existing configurations
        self._load_configurations()
        
        logger.info(f"API Keys Manager initialized (Encryption: {encrypt})")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for API keys"""
        key_file = self.config_file.parent / ".api_key"
        
        if key_file.exists():
            try:
                with open(key_file, 'rb') as f:
                    return base64.b64decode(f.read())
            except Exception as e:
                logger.warning(f"Could not read encryption key: {e}")
        
        # Create new key
        key = Fernet.generate_key()
        try:
            with open(key_file, 'wb') as f:
                f.write(base64.b64encode(key))
            os.chmod(key_file, 0o600)  # Restrict permissions
            logger.info("Created new encryption key for API keys")
        except Exception as e:
            logger.error(f"Could not save encryption key: {e}")
        
        return key
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt sensitive value"""
        if not self.fernet or not value:
            return value
        try:
            return self.fernet.encrypt(value.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return value
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt sensitive value"""
        if not self.fernet or not encrypted_value:
            return encrypted_value
        try:
            return self.fernet.decrypt(encrypted_value.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_value
    
    def add_api_key(self, service_name: str, api_key: str, 
                   secret_key: Optional[str] = None,
                   passphrase: Optional[str] = None,
                   base_url: Optional[str] = None,
                   rate_limit: Optional[int] = None,
                   description: str = "") -> bool:
        """
        Add or update API key configuration
        
        Args:
            service_name: Name of the service (e.g., 'binance', 'kucoin')
            api_key: API key
            secret_key: Secret key (if required)
            passphrase: Passphrase (if required)
            base_url: Base URL for the service
            rate_limit: Rate limit per minute
            description: Description of the service
            
        Returns:
            True if successful
        """
        try:
            config = APIKeyConfig(
                service_name=service_name,
                api_key=self._encrypt_value(api_key),
                secret_key=self._encrypt_value(secret_key) if secret_key else None,
                passphrase=self._encrypt_value(passphrase) if passphrase else None,
                base_url=base_url,
                rate_limit=rate_limit,
                description=description,
                created_at=datetime.now().isoformat()
            )
            
            self.api_configs[service_name] = config
            self._save_configurations()
            
            logger.info(f"Added API key for {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding API key for {service_name}: {e}")
            return False
    
    def get_api_key(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get decrypted API key configuration
        
        Args:
            service_name: Name of the service
            
        Returns:
            Dictionary with API credentials or None
        """
        if service_name not in self.api_configs:
            logger.warning(f"API key not found for {service_name}")
            return None
        
        try:
            config = self.api_configs[service_name]
            
            # Update usage tracking
            config.last_used = datetime.now().isoformat()
            config.usage_count += 1
            
            return {
                'service_name': config.service_name,
                'api_key': self._decrypt_value(config.api_key),
                'secret_key': self._decrypt_value(config.secret_key) if config.secret_key else None,
                'passphrase': self._decrypt_value(config.passphrase) if config.passphrase else None,
                'base_url': config.base_url,
                'rate_limit': config.rate_limit,
                'description': config.description,
                'is_active': config.is_active
            }
            
        except Exception as e:
            logger.error(f"Error getting API key for {service_name}: {e}")
            return None
    
    def add_exchange_config(self, name: str, api_key: str, secret_key: str,
                           passphrase: Optional[str] = None, 
                           sandbox: bool = False,
                           testnet: bool = False,
                           base_url: Optional[str] = None,
                           rate_limit: int = 1000,
                           features: Optional[List[str]] = None) -> bool:
        """Add exchange-specific configuration"""
        try:
            config = ExchangeConfig(
                name=name,
                api_key=self._encrypt_value(api_key),
                secret_key=self._encrypt_value(secret_key),
                passphrase=self._encrypt_value(passphrase) if passphrase else None,
                sandbox=sandbox,
                testnet=testnet,
                base_url=base_url,
                rate_limit=rate_limit,
                features=features or []
            )
            
            self.exchange_configs[name] = config
            self._save_configurations()
            
            logger.info(f"Added exchange config for {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding exchange config for {name}: {e}")
            return False
    
    def get_exchange_config(self, exchange_name: str) -> Optional[Dict[str, Any]]:
        """Get decrypted exchange configuration"""
        if exchange_name not in self.exchange_configs:
            logger.warning(f"Exchange config not found for {exchange_name}")
            return None
        
        try:
            config = self.exchange_configs[exchange_name]
            
            return {
                'name': config.name,
                'api_key': self._decrypt_value(config.api_key),
                'secret_key': self._decrypt_value(config.secret_key),
                'passphrase': self._decrypt_value(config.passphrase) if config.passphrase else None,
                'sandbox': config.sandbox,
                'testnet': config.testnet,
                'base_url': config.base_url,
                'rate_limit': config.rate_limit,
                'features': config.features
            }
            
        except Exception as e:
            logger.error(f"Error getting exchange config for {exchange_name}: {e}")
            return None
    
    def list_services(self) -> List[Dict[str, Any]]:
        """List all configured services"""
        services = []
        
        for service_name, config in self.api_configs.items():
            services.append({
                'service_name': service_name,
                'description': config.description,
                'is_active': config.is_active,
                'base_url': config.base_url,
                'rate_limit': config.rate_limit,
                'created_at': config.created_at,
                'last_used': config.last_used,
                'usage_count': config.usage_count,
                'has_secret': config.secret_key is not None,
                'has_passphrase': config.passphrase is not None
            })
        
        return services
    
    def list_exchanges(self) -> List[Dict[str, Any]]:
        """List all configured exchanges"""
        exchanges = []
        
        for exchange_name, config in self.exchange_configs.items():
            exchanges.append({
                'name': exchange_name,
                'sandbox': config.sandbox,
                'testnet': config.testnet,
                'base_url': config.base_url,
                'rate_limit': config.rate_limit,
                'features': config.features,
                'has_passphrase': config.passphrase is not None
            })
        
        return exchanges
    
    def remove_api_key(self, service_name: str) -> bool:
        """Remove API key configuration"""
        if service_name in self.api_configs:
            del self.api_configs[service_name]
            self._save_configurations()
            logger.info(f"Removed API key for {service_name}")
            return True
        return False
    
    def remove_exchange_config(self, exchange_name: str) -> bool:
        """Remove exchange configuration"""
        if exchange_name in self.exchange_configs:
            del self.exchange_configs[exchange_name]
            self._save_configurations()
            logger.info(f"Removed exchange config for {exchange_name}")
            return True
        return False
    
    def activate_service(self, service_name: str, active: bool = True) -> bool:
        """Activate or deactivate a service"""
        if service_name in self.api_configs:
            self.api_configs[service_name].is_active = active
            self._save_configurations()
            logger.info(f"{'Activated' if active else 'Deactivated'} {service_name}")
            return True
        return False
    
    def _save_configurations(self):
        """Save configurations to file"""
        try:
            config_data = {
                'api_configs': {k: asdict(v) for k, v in self.api_configs.items()},
                'exchange_configs': {k: asdict(v) for k, v in self.exchange_configs.items()},
                'metadata': {
                    'version': '1.0',
                    'created_at': datetime.now().isoformat(),
                    'encrypted': self.encrypt
                }
            }
            
            with open(self.config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
            
            # Restrict file permissions
            os.chmod(self.config_file, 0o600)
            
        except Exception as e:
            logger.error(f"Error saving configurations: {e}")
    
    def _load_configurations(self):
        """Load configurations from file"""
        if not self.config_file.exists():
            logger.info("No existing API configuration file found")
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                return
            
            # Load API configs
            api_configs = config_data.get('api_configs', {})
            for service_name, config_dict in api_configs.items():
                self.api_configs[service_name] = APIKeyConfig(**config_dict)
            
            # Load exchange configs
            exchange_configs = config_data.get('exchange_configs', {})
            for exchange_name, config_dict in exchange_configs.items():
                self.exchange_configs[exchange_name] = ExchangeConfig(**config_dict)
            
            logger.info(f"Loaded {len(self.api_configs)} API configs and {len(self.exchange_configs)} exchange configs")
            
        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get health status of all configured services"""
        health = {
            'total_services': len(self.api_configs),
            'active_services': sum(1 for c in self.api_configs.values() if c.is_active),
            'total_exchanges': len(self.exchange_configs),
            'services': {},
            'exchanges': {}
        }
        
        for service_name, config in self.api_configs.items():
            health['services'][service_name] = {
                'active': config.is_active,
                'last_used': config.last_used,
                'usage_count': config.usage_count,
                'has_credentials': bool(config.api_key)
            }
        
        for exchange_name, config in self.exchange_configs.items():
            health['exchanges'][exchange_name] = {
                'sandbox': config.sandbox,
                'testnet': config.testnet,
                'rate_limit': config.rate_limit,
                'features': len(config.features) if config.features else 0
            }
        
        return health
    
    def setup_default_configurations(self):
        """Setup default API service configurations with placeholder keys"""
        default_services = [
            {
                'service_name': 'coinmarketcap',
                'description': 'CoinMarketCap API for crypto data',
                'base_url': 'https://pro-api.coinmarketcap.com',
                'rate_limit': 10000
            },
            {
                'service_name': 'coingecko',
                'description': 'CoinGecko API for crypto data',
                'base_url': 'https://api.coingecko.com/api/v3',
                'rate_limit': 50
            },
            {
                'service_name': 'binance',
                'description': 'Binance Exchange API',
                'base_url': 'https://api.binance.com',
                'rate_limit': 1200
            },
            {
                'service_name': 'kucoin',
                'description': 'KuCoin Exchange API',
                'base_url': 'https://api.kucoin.com',
                'rate_limit': 1800
            },
            {
                'service_name': 'cryptometer',
                'description': 'Cryptometer Analysis API',
                'rate_limit': 100
            },
            {
                'service_name': 'openai',
                'description': 'OpenAI API for AI analysis',
                'base_url': 'https://api.openai.com/v1',
                'rate_limit': 3500
            },
            {
                'service_name': 'ethereum',
                'description': 'Ethereum blockchain data',
                'base_url': 'https://api.etherscan.io/api',
                'rate_limit': 5
            },
            {
                'service_name': 'polygon',
                'description': 'Polygon blockchain data',
                'base_url': 'https://api.polygonscan.com/api',
                'rate_limit': 5
            },
            {
                'service_name': 'bscscan',
                'description': 'BSC blockchain data',
                'base_url': 'https://api.bscscan.com/api',
                'rate_limit': 5
            },
            {
                'service_name': 'solana',
                'description': 'Solana blockchain data',
                'base_url': 'https://api.solana.fm',
                'rate_limit': 100
            }
        ]
        
        logger.info("Setting up default service configurations...")
        
        for service in default_services:
            if service['service_name'] not in self.api_configs:
                self.add_api_key(
                    service_name=service['service_name'],
                    api_key='YOUR_API_KEY_HERE',  # Placeholder
                    base_url=service['base_url'],
                    rate_limit=service['rate_limit'],
                    description=service['description']
                )
        
        # Setup default exchange configurations
        default_exchanges = [
            {
                'name': 'binance',
                'sandbox': False,
                'base_url': 'https://api.binance.com',
                'rate_limit': 1200,
                'features': ['spot', 'futures', 'margin']
            },
            {
                'name': 'kucoin',
                'sandbox': False,
                'base_url': 'https://api.kucoin.com',
                'rate_limit': 1800,
                'features': ['spot', 'futures', 'margin']
            },
            {
                'name': 'binance_testnet',
                'sandbox': True,
                'testnet': True,
                'base_url': 'https://testnet.binance.vision',
                'rate_limit': 1200,
                'features': ['spot', 'futures']
            }
        ]
        
        for exchange in default_exchanges:
            if exchange['name'] not in self.exchange_configs:
                self.add_exchange_config(
                    name=exchange['name'],
                    api_key='YOUR_API_KEY_HERE',
                    secret_key='YOUR_SECRET_KEY_HERE',
                    sandbox=exchange['sandbox'],
                    testnet=exchange.get('testnet', False),
                    base_url=exchange['base_url'],
                    rate_limit=exchange['rate_limit'],
                    features=exchange['features']
                )
        
        logger.info("Default configurations setup complete")

# Create global instance
api_keys_manager = APIKeysManager()

# Helper functions for easy access
def get_api_key(service_name: str) -> Optional[Dict[str, Any]]:
    """Get API key for a service"""
    return api_keys_manager.get_api_key(service_name)

def get_exchange_config(exchange_name: str) -> Optional[Dict[str, Any]]:
    """Get exchange configuration"""
    return api_keys_manager.get_exchange_config(exchange_name)

def add_api_key(service_name: str, api_key: str, **kwargs) -> bool:
    """Add API key configuration"""
    return api_keys_manager.add_api_key(service_name, api_key, **kwargs)

def is_service_available(service_name: str) -> bool:
    """Check if service is available and active"""
    config = api_keys_manager.get_api_key(service_name)
    if not config:
        return False
    
    return (config.get('is_active', False) and 
            config.get('api_key') != 'YOUR_API_KEY_HERE' and
            bool(config.get('api_key')))