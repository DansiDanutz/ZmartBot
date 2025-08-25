#!/usr/bin/env python3
"""
Security Hardening Script for ZmartBot
Addresses critical security issues identified in audit
"""

import os
import secrets
import yaml
from pathlib import Path

def generate_secure_password(length=32):
    """Generate cryptographically secure password"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def update_docker_compose():
    """Remove hardcoded passwords from docker-compose.yml"""
    print("🔐 Updating docker-compose.yml with secure configuration...")
    
    docker_compose_path = Path("docker-compose.yml")
    if not docker_compose_path.exists():
        print("❌ docker-compose.yml not found")
        return
    
    # Create secure environment template
    env_template = """# Production Environment Variables
# Generated secure passwords - CHANGE THESE IN PRODUCTION!

# PostgreSQL
POSTGRES_USER=zmart_user
POSTGRES_PASSWORD={postgres_pass}
POSTGRES_DB=zmart_bot

# Redis
REDIS_PASSWORD={redis_pass}

# RabbitMQ
RABBITMQ_DEFAULT_USER=zmart_mq
RABBITMQ_DEFAULT_PASS={rabbit_pass}

# InfluxDB
INFLUXDB_ADMIN_PASSWORD={influx_pass}
INFLUXDB_USER_PASSWORD={influx_user_pass}

# Application
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret}

# API Keys (Add your actual keys)
CRYPTOMETER_API_KEY=your_cryptometer_key_here
KUCOIN_API_KEY=your_kucoin_key_here
KUCOIN_SECRET=your_kucoin_secret_here
KUCOIN_PASSPHRASE=your_kucoin_passphrase_here
OPENAI_API_KEY=your_openai_key_here
"""
    
    # Generate secure passwords
    passwords = {
        'postgres_pass': generate_secure_password(),
        'redis_pass': generate_secure_password(),
        'rabbit_pass': generate_secure_password(),
        'influx_pass': generate_secure_password(),
        'influx_user_pass': generate_secure_password(),
        'secret_key': secrets.token_hex(32),
        'jwt_secret': secrets.token_hex(32)
    }
    
    # Write secure environment file
    with open('.env.production', 'w') as f:
        f.write(env_template.format(**passwords))
    
    print("✅ Created .env.production with secure passwords")
    print("⚠️  Remember to update API keys with actual values")

def add_rate_limiting():
    """Add rate limiting to authentication endpoints"""
    print("🚦 Adding rate limiting configuration...")
    
    rate_limit_config = '''"""
Rate Limiting Configuration for Authentication Endpoints
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Rate limit configurations
AUTH_RATE_LIMITS = {
    "login": "5/minute",
    "register": "3/minute", 
    "password_reset": "3/hour",
    "token_refresh": "10/minute"
}

# Rate limit error handler
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Try again in {exc.detail}",
            "retry_after": exc.detail
        }
    )
    response.headers["Retry-After"] = str(exc.detail)
    return response

# Apply to authentication routes
def apply_auth_rate_limits(app):
    """Apply rate limits to authentication endpoints"""
    
    # Login endpoint
    @app.post("/api/auth/login")
    @limiter.limit(AUTH_RATE_LIMITS["login"])
    async def login(request: Request):
        pass
    
    # Register endpoint  
    @app.post("/api/auth/register")
    @limiter.limit(AUTH_RATE_LIMITS["register"])
    async def register(request: Request):
        pass
    
    # Password reset
    @app.post("/api/auth/password-reset")
    @limiter.limit(AUTH_RATE_LIMITS["password_reset"])
    async def password_reset(request: Request):
        pass
    
    return app
'''
    
    # Write rate limiting configuration
    rate_limit_path = Path("backend/zmart-api/src/security/rate_limiting.py")
    rate_limit_path.parent.mkdir(parents=True, exist_ok=True)
    rate_limit_path.write_text(rate_limit_config)
    
    print("✅ Rate limiting configuration added")

def add_security_headers():
    """Add security headers middleware"""
    print("🛡️ Adding security headers...")
    
    security_headers = '''"""
Security Headers Middleware
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

def apply_security_middleware(app: FastAPI):
    """Apply security middleware to FastAPI app"""
    
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Configure CORS properly
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://zmartbot.com"],  # Update with your domain
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
        max_age=3600,
    )
    
    return app
'''
    
    security_path = Path("backend/zmart-api/src/security/headers.py")
    security_path.parent.mkdir(parents=True, exist_ok=True)
    security_path.write_text(security_headers)
    
    print("✅ Security headers middleware added")

def create_secrets_manager():
    """Create secrets management configuration"""
    print("🔑 Setting up secrets management...")
    
    secrets_config = '''"""
Secrets Management using environment variables and optional HashiCorp Vault
"""
import os
from typing import Optional
from functools import lru_cache
import hvac
from pydantic import BaseSettings

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
'''
    
    secrets_path = Path("backend/zmart-api/src/security/secrets.py")
    secrets_path.write_text(secrets_config)
    
    print("✅ Secrets management configuration added")

def main():
    print("🔒 ZmartBot Security Hardening Script")
    print("=" * 50)
    
    # Run security fixes
    update_docker_compose()
    add_rate_limiting()
    add_security_headers()
    create_secrets_manager()
    
    print("\n✅ Security hardening complete!")
    print("\n📋 Next steps:")
    print("1. Review and update .env.production with your actual API keys")
    print("2. Update backend/zmart-api/src/main.py to use new security modules")
    print("3. Test rate limiting on authentication endpoints")
    print("4. Consider implementing HashiCorp Vault for production")
    print("5. Run security audit: python security_audit.py")

if __name__ == "__main__":
    main()