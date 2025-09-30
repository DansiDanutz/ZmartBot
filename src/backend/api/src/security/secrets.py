"""
Secrets Management using environment variables and optional HashiCorp Vault
"""
import os
from typing import Optional
from functools import lru_cache
import hvac
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with secret management"""
    
    # Vault Configuration (optional)
    vault_url: Optional[str] = os.getenv("VAULT_URL")
    vault_token: Optional[str] = os.getenv("VAULT_TOKEN")
    use_vault: bool = os.getenv("USE_VAULT", "false").lower() == "true"
    
    # Database
    postgres_user: str = os.getenv("POSTGRES_USER", "")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "")
    postgres_db: str = os.getenv("POSTGRES_DB", "zmart_bot")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    
    # Redis
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    
    # API Keys
    cryptometer_api_key: str = os.getenv("CRYPTOMETER_API_KEY", "")
    kucoin_api_key: str = os.getenv("KUCOIN_API_KEY", "")
    kucoin_secret: str = os.getenv("KUCOIN_SECRET", "")
    kucoin_passphrase: str = os.getenv("KUCOIN_PASSPHRASE", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

class SecretsManager:
    """Manage secrets from environment or Vault"""
    
    def __init__(self):
        self.settings = Settings()
        self.vault_client = None
        
        if self.settings.use_vault and self.settings.vault_url:
            self.vault_client = hvac.Client(
                url=self.settings.vault_url,
                token=self.settings.vault_token
            )
    
    def get_secret(self, key: str) -> str:
        """Get secret from Vault or environment"""
        if self.vault_client and self.vault_client.is_authenticated():
            # Try to get from Vault
            try:
                response = self.vault_client.secrets.kv.v2.read_secret_version(
                    path=f"zmartbot/{key}"
                )
                return response["data"]["data"]["value"]
            except Exception:
                pass
        
        # Fallback to environment variable
        return getattr(self.settings, key, "")
    
    def rotate_api_key(self, service: str, new_key: str):
        """Rotate API key"""
        if self.vault_client and self.vault_client.is_authenticated():
            self.vault_client.secrets.kv.v2.create_or_update_secret(
                path=f"zmartbot/{service}_api_key",
                secret={"value": new_key}
            )
        else:
            # Update environment variable (requires restart)
            os.environ[f"{service.upper()}_API_KEY"] = new_key

@lru_cache()
def get_secrets_manager() -> SecretsManager:
    """Get singleton secrets manager"""
    return SecretsManager()
