"""
Grok-X-Module API Credentials Configuration
Secure storage and management of API credentials for X API and Grok AI
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass
import json
from cryptography.fernet import Fernet
import base64


@dataclass
class XAPICredentials:
    """X API credentials configuration"""
    client_id: str
    client_secret: str
    api_key: str
    api_key_secret: str
    bearer_token: str
    access_token: str
    access_token_secret: str


@dataclass
class GrokAPICredentials:
    """Grok AI API credentials configuration"""
    api_key: str
    base_url: str = "https://api.x.ai/v1"


class CredentialManager:
    """Secure credential management system"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize credential manager with optional encryption"""
        self.encryption_key = encryption_key
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            self.cipher = None
    
    def get_x_api_credentials(self) -> XAPICredentials:
        """Get X API credentials"""
        return XAPICredentials(
            client_id="Z2tCQk1Za1JYYnhNeW9TX212UlA6MTpjaQ",
            client_secret="mtUXayWMzMJk-K509bxaL9LV7lPGI_lpeCykXEtM2nBSGHOHTc",
            api_key="NYQjjs8z71qXBXQd9VlhIMVwe",
            api_key_secret="Z7NriVoexvziRrEGUnPjCNyCXRzQZzrmVcAB7vm5XUIc15HmET",
            bearer_token="AAAAAAAAAAAAAAAAAAAAADijzQEAAAAA1dxLcD8JDxLD640WmcRIbSib%2BDY%3DepaYbHCEaHzItD9aqTwD7Dd2gYAT5V78UoH4qevsmMFna7H7sq",
            access_token="1865530517992464384-SMgujnikDO8r2LkJGqdQhVfJP5XTmN",
            access_token_secret="ivOfZkhRfvQaO7Zve7Nkrzf5ow2xzYyaJzuDRA54anmTt"
        )
    
    def get_grok_api_credentials(self) -> GrokAPICredentials:
        """Get Grok AI API credentials"""
        return GrokAPICredentials(
            api_key="xai-8dDS88EczSjvKVUcqsofiFQQjYU1xlP1yoXBSS2j8VevhArgeWET1xDsbdzPhHvedCpGF78AeVD5MVLY"
        )
    
    def encrypt_credentials(self, credentials: Dict) -> str:
        """Encrypt credentials for secure storage"""
        if not self.cipher:
            raise ValueError("Encryption key not provided")
        
        credentials_json = json.dumps(credentials)
        encrypted_data = self.cipher.encrypt(credentials_json.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_credentials(self, encrypted_data: str) -> Dict:
        """Decrypt credentials from secure storage"""
        if not self.cipher:
            raise ValueError("Encryption key not provided")
        
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return json.loads(decrypted_data.decode())
    
    @staticmethod
    def generate_encryption_key() -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()


# Global credential manager instance
credential_manager = CredentialManager()


def get_x_credentials() -> XAPICredentials:
    """Convenience function to get X API credentials"""
    return credential_manager.get_x_api_credentials()


def get_grok_credentials() -> GrokAPICredentials:
    """Convenience function to get Grok AI credentials"""
    return credential_manager.get_grok_api_credentials()

