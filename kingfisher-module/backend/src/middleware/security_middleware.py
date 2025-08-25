#!/usr/bin/env python3
"""
Security Middleware for KingFisher API
Implements JWT token validation, role-based access control, and request security
"""

import jwt
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware for KingFisher API"""
    
    def __init__(self, app, secret_key: str, redis_url: str, 
                 max_request_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.secret_key = secret_key
        self.max_request_size = max_request_size
        self.redis_client: Optional[redis.Redis] = None
        self.redis_url = redis_url
        
        # Initialize Redis connection
        self._initialize_redis()
        
        # Public endpoints that don't require authentication
        self.public_endpoints = {
            "/health",
            "/ready",
            "/metrics",
            "/docs",
            "/openapi.json"
        }
        
        # Rate limiting configuration
        self.rate_limits = {
            "default": {"requests": 100, "window": 60},      # 100 req/min default
            "upload": {"requests": 10, "window": 60},        # 10 uploads/min
            "ai": {"requests": 30, "window": 60}             # 30 AI requests/min
        }
    
    def _initialize_redis(self):
        """Initialize Redis connection for rate limiting and session management"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            logger.info("✅ Redis connection initialized for security middleware")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.redis_client = None
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware dispatch method"""
        try:
            # Check request size
            await self._check_request_size(request)
            
            # Skip security for public endpoints
            if self._is_public_endpoint(request.url.path):
                return await call_next(request)
            
            # Validate authentication
            user_info = await self._validate_authentication(request)
            if not user_info:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Check authorization
            await self._check_authorization(request, user_info)
            
            # Apply rate limiting
            await self._apply_rate_limiting(request, user_info)
            
            # Add security headers
            request.state.user = user_info
            
            # Process request
            response = await call_next(request)
            
            # Add security headers to response
            self._add_security_headers(response)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            raise HTTPException(status_code=500, detail="Security check failed")
    
    async def _check_request_size(self, request: Request):
        """Check request size limits"""
        content_length = request.headers.get('content-length')
        
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_request_size:
                    logger.warning(f"Request too large: {size} bytes (max: {self.max_request_size})")
                    raise HTTPException(
                        status_code=413, 
                        detail=f"Request too large. Max size: {self.max_request_size // (1024*1024)}MB"
                    )
            except ValueError:
                pass
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no auth required)"""
        return any(path.startswith(public) for public in self.public_endpoints)
    
    async def _validate_authentication(self, request: Request) -> Optional[Dict[str, Any]]:
        """Validate JWT token and extract user information"""
        auth_header = request.headers.get('Authorization')
        service_token = request.headers.get('SERVICE-TOKEN')
        
        # Check for SERVICE_TOKEN (internal services)
        if service_token:
            return await self._validate_service_token(service_token)
        
        # Check for Authorization header
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Validate token expiration
            if datetime.utcfromtimestamp(payload.get('exp', 0)) < datetime.utcnow():
                logger.warning("Token expired")
                return None
            
            # Extract user information
            user_info = {
                "user_id": payload.get('sub'),
                "email": payload.get('email'),
                "roles": payload.get('roles', []),
                "permissions": payload.get('permissions', []),
                "token_type": "user",
                "exp": payload.get('exp')
            }
            
            logger.debug(f"User authenticated: {user_info['user_id']}")
            return user_info
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    async def _validate_service_token(self, service_token: str) -> Optional[Dict[str, Any]]:
        """Validate internal service token"""
        try:
            # In production, this would validate against a secure service registry
            # For now, use a simple JWT validation with service-specific claims
            
            payload = jwt.decode(service_token, self.secret_key, algorithms=['HS256'])
            
            # Validate service token structure
            service_name = payload.get('service')
            if not service_name:
                logger.warning("Invalid service token: missing service name")
                return None
            
            # Check expiration
            if datetime.utcfromtimestamp(payload.get('exp', 0)) < datetime.utcnow():
                logger.warning("Service token expired")
                return None
            
            # Return service information
            return {
                "service_name": service_name,
                "permissions": payload.get('permissions', ['analysis.read', 'analysis.write', 'admin']),
                "token_type": "service",
                "exp": payload.get('exp')
            }
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid service token: {e}")
            return None
    
    async def _check_authorization(self, request: Request, user_info: Dict[str, Any]):
        """Check if user has required permissions for the endpoint"""
        path = request.url.path
        method = request.method
        
        # Define permission requirements for endpoints
        permission_map = {
            ("/api/v1/automated-reports", "POST"): ["analysis.write"],
            ("/api/v1/images/upload", "POST"): ["analysis.write"], 
            ("/api/v1/images/analyze", "GET"): ["analysis.read"],
            ("/api/v1/liquidation", "GET"): ["analysis.read"],
            ("/api/v1/liquidation", "POST"): ["analysis.write"],
            ("/api/v1/ai", "POST"): ["analysis.write"],
            ("/api/v1/master-summary", "GET"): ["analysis.read"],
            ("/api/v1/master-summary", "POST"): ["analysis.write"]
        }
        
        # Check specific endpoint permissions
        required_permissions = None
        for (endpoint_path, endpoint_method), perms in permission_map.items():
            if path.startswith(endpoint_path) and method == endpoint_method:
                required_permissions = perms
                break
        
        # Default to read permission if not specified
        if required_permissions is None:
            if method in ["GET", "HEAD", "OPTIONS"]:
                required_permissions = ["analysis.read"]
            else:
                required_permissions = ["analysis.write"]
        
        # Check permissions
        user_permissions = user_info.get("permissions", [])
        user_roles = user_info.get("roles", [])
        
        # Admin role has all permissions
        if "admin" in user_roles:
            return
        
        # Check if user has required permissions
        if not any(perm in user_permissions for perm in required_permissions):
            logger.warning(f"User {user_info.get('user_id', 'unknown')} lacks permissions {required_permissions}")
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {required_permissions}"
            )
    
    async def _apply_rate_limiting(self, request: Request, user_info: Dict[str, Any]):
        """Apply rate limiting based on endpoint and user"""
        if not self.redis_client:
            logger.warning("Redis not available, skipping rate limiting")
            return
        
        # Determine rate limit category
        path = request.url.path
        rate_limit_key = "default"
        
        if "/images/upload" in path:
            rate_limit_key = "upload"
        elif "/ai/" in path:
            rate_limit_key = "ai"
        
        # Get rate limit configuration
        rate_config = self.rate_limits[rate_limit_key]
        max_requests = rate_config["requests"]
        window_seconds = rate_config["window"]
        
        # Create Redis key for user/service
        if user_info.get("token_type") == "service":
            client_id = f"service:{user_info['service_name']}"
        else:
            client_id = f"user:{user_info.get('user_id', 'unknown')}"
        
        redis_key = f"ratelimit:{rate_limit_key}:{client_id}"
        
        try:
            # Get current request count
            current_count = await self.redis_client.get(redis_key)
            current_count = int(current_count) if current_count else 0
            
            if current_count >= max_requests:
                logger.warning(f"Rate limit exceeded for {client_id}: {current_count}/{max_requests}")
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {max_requests} requests per {window_seconds} seconds",
                    headers={"Retry-After": str(window_seconds)}
                )
            
            # Increment counter
            pipe = self.redis_client.pipeline()
            pipe.incr(redis_key)
            pipe.expire(redis_key, window_seconds)
            await pipe.execute()
            
        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiting: {e}")
            # Continue without rate limiting if Redis fails
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Middleware for handling idempotency keys"""
    
    def __init__(self, app, redis_url: str, ttl_hours: int = 24):
        super().__init__(app)
        self.redis_url = redis_url
        self.ttl_seconds = ttl_hours * 3600
        self.redis_client: Optional[redis.Redis] = None
        
        # Initialize Redis
        try:
            self.redis_client = redis.from_url(redis_url)
        except Exception as e:
            logger.error(f"Failed to initialize Redis for idempotency: {e}")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle idempotency for POST requests"""
        if request.method != "POST":
            return await call_next(request)
        
        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            # Idempotency-Key required for POST requests to protected endpoints
            if not self._is_public_endpoint(request.url.path):
                raise HTTPException(
                    status_code=400,
                    detail="Idempotency-Key header required for POST requests"
                )
            return await call_next(request)
        
        if not self.redis_client:
            logger.warning("Redis not available, skipping idempotency check")
            return await call_next(request)
        
        # Check if this key was already processed
        cache_key = f"idempotency:{idempotency_key}"
        
        try:
            cached_response = await self.redis_client.get(cache_key)
            if cached_response:
                # Return cached response
                cached_data = json.loads(cached_response)
                logger.info(f"Returning cached response for idempotency key: {idempotency_key}")
                
                return Response(
                    content=json.dumps(cached_data["body"]),
                    status_code=cached_data["status_code"],
                    headers=cached_data.get("headers", {}),
                    media_type="application/json"
                )
            
            # Process request
            response = await call_next(request)
            
            # Cache response for successful requests
            if 200 <= response.status_code < 300:
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk
                
                cached_data = {
                    "body": response_body.decode() if response_body else "",
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }
                
                await self.redis_client.setex(
                    cache_key,
                    self.ttl_seconds,
                    json.dumps(cached_data)
                )
                
                # Recreate response with body
                response = Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in idempotency middleware: {e}")
            # Continue without idempotency if Redis fails
            return await call_next(request)
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public"""
        public_endpoints = {"/health", "/ready", "/metrics", "/docs", "/openapi.json"}
        return any(path.startswith(public) for public in public_endpoints)


# Utility functions for token generation
class TokenGenerator:
    """Utility class for generating JWT tokens"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def generate_user_token(self, user_id: str, email: str, roles: List[str], 
                           permissions: List[str], expires_in_hours: int = 24) -> str:
        """Generate JWT token for user"""
        payload = {
            "sub": user_id,
            "email": email,
            "roles": roles,
            "permissions": permissions,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=expires_in_hours)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def generate_service_token(self, service_name: str, permissions: List[str], 
                              expires_in_hours: int = 24 * 7) -> str:  # 7 days default
        """Generate JWT token for internal service"""
        payload = {
            "service": service_name,
            "permissions": permissions,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=expires_in_hours)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')