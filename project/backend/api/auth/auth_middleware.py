"""
Authentication and Authorization Middleware
Provides JWT-based authentication for the Enhanced Alerts System
"""

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import redis
import hashlib

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "zmart_alerts_secret_key_2024_secure")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Redis for token blacklisting and rate limiting
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_AUTH_DB", "1")),
        decode_responses=True
    )
    redis_client.ping()
    logger.info("✅ Redis connection established for auth")
except Exception as e:
    logger.warning(f"⚠️ Redis not available for auth: {e}")
    redis_client = None

security = HTTPBearer()

class AuthManager:
    """Handles JWT token creation, validation, and user management"""
    
    def __init__(self):
        self.active_sessions = {}
        
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            # Check if token is blacklisted
            if redis_client and redis_client.get(f"blacklist:{token}"):
                raise HTTPException(status_code=401, detail="Token has been revoked")
            
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Verify token type
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            return payload
            
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def blacklist_token(self, token: str) -> bool:
        """Add token to blacklist"""
        try:
            if redis_client:
                # Set with expiration matching token expiration
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
                exp = payload.get("exp", 0)
                current_time = datetime.now(timezone.utc).timestamp()
                ttl = max(1, int(exp - current_time))
                
                redis_client.setex(f"blacklist:{token}", ttl, "revoked")
                return True
            return False
        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
            return False
    
    def get_user_permissions(self, user_id: str) -> Dict[str, bool]:
        """Get user permissions for authorization"""
        # Default permissions for alerts system
        default_permissions = {
            "read_alerts": True,
            "create_alerts": True,
            "edit_alerts": True,
            "delete_alerts": True,
            "manage_system": False,  # Admin only
            "view_analytics": True,
            "configure_notifications": True
        }
        
        # In production, this would query a database
        # For now, return default permissions
        return default_permissions

auth_manager = AuthManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = auth_manager.verify_token(token)
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Get user permissions
    permissions = auth_manager.get_user_permissions(user_id)
    
    return {
        "user_id": user_id,
        "username": payload.get("username"),
        "email": payload.get("email"),
        "permissions": permissions,
        "session_id": payload.get("session_id")
    }

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_dependency(current_user: Dict[str, Any] = Depends(get_current_user)):
        if not current_user["permissions"].get(permission, False):
            raise HTTPException(
                status_code=403, 
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return current_user
    return permission_dependency

# Rate limiting
class RateLimiter:
    """Rate limiting for API endpoints"""
    
    def __init__(self, max_requests: int = 100, window_minutes: int = 15):
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed based on rate limit"""
        if not redis_client:
            return True  # Allow if Redis is not available
        
        try:
            key = f"rate_limit:{identifier}"
            current = redis_client.get(key)
            
            if current is None:
                # First request in window
                redis_client.setex(key, self.window_seconds, 1)
                return True
            
            # Convert Redis response to integer safely
            try:
                if isinstance(current, bytes):
                    current_count = int(current.decode('utf-8'))
                elif isinstance(current, str):
                    current_count = int(current)
                elif hasattr(current, '__str__'):
                    current_count = int(str(current))
                else:
                    # Unknown type, reset counter
                    redis_client.setex(key, self.window_seconds, 1)
                    return True
            except (ValueError, AttributeError, UnicodeDecodeError):
                # If conversion fails, assume it's the first request
                redis_client.setex(key, self.window_seconds, 1)
                return True
            
            if current_count >= self.max_requests:
                return False
            
            # Increment counter
            redis_client.incr(key)
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True  # Allow on error

rate_limiter = RateLimiter()

async def check_rate_limit(request: Request):
    """Rate limiting middleware"""
    # Use IP address as identifier
    client_ip = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
    
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "900"}  # 15 minutes
        )
    
    return True

# Security headers middleware
def add_security_headers(response):
    """Add security headers to response"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    return response