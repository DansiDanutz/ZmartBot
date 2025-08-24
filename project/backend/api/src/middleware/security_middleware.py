"""
Comprehensive Security Middleware
Provides rate limiting, security headers, input sanitization, and request monitoring
"""

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any, Optional
import time
import json
import re
import logging
from datetime import datetime, timedelta
import hashlib
import ipaddress
from urllib.parse import urlparse

from ..cache.redis_cache import cache

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware for Enhanced Alerts System"""
    
    def __init__(self, app, config: Optional[Dict[str, Any]] = None):
        super().__init__(app)
        self.config = config or {}
        
        # Rate limiting configuration
        self.rate_limits = {
            "auth": {"requests": 5, "window": 300},      # 5 requests per 5 minutes
            "api": {"requests": 100, "window": 600},     # 100 requests per 10 minutes
            "websocket": {"requests": 50, "window": 300}, # 50 connections per 5 minutes
            "public": {"requests": 200, "window": 600}   # 200 requests per 10 minutes
        }
        
        # Security patterns
        self.sql_injection_patterns = [
            r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b|\bDROP\b)",
            r"(\bOR\b\s+\d+\s*=\s*\d+|\bAND\b\s+\d+\s*=\s*\d+)",
            r"(--|#|\/\*|\*\/)",
            r"(\bEXEC\b|\bEXECUTE\b|\bxp_cmdshell\b)"
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>",
            r"eval\s*\(",
            r"document\.(cookie|write|location)"
        ]
        
        # Blocked IP ranges (example: known malicious IPs)
        self.blocked_ips = set()
        self.blocked_networks = [
            # Add known malicious networks here
            # ipaddress.ip_network("192.168.1.0/24")  # Example
        ]
        
        # Trusted proxy headers
        self.trusted_proxies = {
            "cloudflare": ["CF-Connecting-IP", "CF-IPCountry"],
            "aws": ["X-Forwarded-For", "X-Real-IP"],
            "nginx": ["X-Real-IP", "X-Forwarded-For"]
        }
    
    async def dispatch(self, request: Request, call_next):
        """Main security middleware dispatcher"""
        
        start_time = time.time()
        
        try:
            # Extract client information
            client_info = self.extract_client_info(request)
            
            # Security checks
            await self.check_ip_security(client_info["ip"])
            await self.check_rate_limiting(request, client_info)
            await self.check_request_security(request)
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response = self.add_security_headers(response)
            
            # Log request
            await self.log_request(request, response, client_info, time.time() - start_time)
            
            return response
            
        except HTTPException as e:
            # Create error response with security headers
            response = Response(
                content=json.dumps({
                    "success": False,
                    "error": e.detail,
                    "timestamp": datetime.now().isoformat()
                }),
                status_code=e.status_code,
                headers={"Content-Type": "application/json"}
            )
            
            response = self.add_security_headers(response)
            await self.log_security_event(request, client_info, e.detail, e.status_code)
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            
            # Create safe error response
            response = Response(
                content=json.dumps({
                    "success": False,
                    "error": "Internal server error",
                    "timestamp": datetime.now().isoformat()
                }),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
            
            response = self.add_security_headers(response)
            return response
    
    def extract_client_info(self, request: Request) -> Dict[str, str]:
        """Extract client IP and other information"""
        
        # Get real IP from trusted headers
        client_ip = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
        
        # Check trusted proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get first IP in chain (client IP)
            client_ip = forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            client_ip = real_ip.strip()
        
        # Cloudflare specific
        cf_connecting_ip = request.headers.get("CF-Connecting-IP")
        if cf_connecting_ip:
            client_ip = cf_connecting_ip.strip()
        
        return {
            "ip": client_ip,
            "user_agent": request.headers.get("User-Agent", ""),
            "referer": request.headers.get("Referer", ""),
            "origin": request.headers.get("Origin", ""),
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query) if request.url.query else ""
        }
    
    async def check_ip_security(self, client_ip: str):
        """Check IP-based security"""
        
        try:
            ip_addr = ipaddress.ip_address(client_ip)
            
            # Check blocked IPs
            if client_ip in self.blocked_ips:
                raise HTTPException(status_code=403, detail="Access denied: IP blocked")
            
            # Check blocked networks
            for network in self.blocked_networks:
                if ip_addr in network:
                    raise HTTPException(status_code=403, detail="Access denied: Network blocked")
            
            # Check if IP is in temporary block list (Redis)
            if cache.is_available():
                block_key = f"ip_block:{client_ip}"
                if cache.get(block_key):
                    raise HTTPException(status_code=429, detail="IP temporarily blocked due to suspicious activity")
                    
        except ValueError:
            # Invalid IP address
            logger.warning(f"Invalid IP address: {client_ip}")
    
    async def check_rate_limiting(self, request: Request, client_info: Dict[str, str]):
        """Advanced rate limiting with different limits for different endpoints"""
        
        if not cache.is_available():
            return  # Skip rate limiting if Redis is not available
        
        client_ip = client_info["ip"]
        path = client_info["path"]
        
        # Determine rate limit category
        if path.startswith("/api/v1/auth"):
            category = "auth"
        elif path.startswith("/ws/"):
            category = "websocket"
        elif path.startswith("/api/"):
            category = "api"
        else:
            category = "public"
        
        limits = self.rate_limits[category]
        
        # Create rate limiting keys
        window_start = int(time.time() // limits["window"]) * limits["window"]
        rate_key = f"rate_limit:{category}:{client_ip}:{window_start}"
        
        try:
            # Get current count
            current_count = cache.get(rate_key) or 0
            
            if current_count >= limits["requests"]:
                # Add to suspicious activity if severely over limit
                if current_count > limits["requests"] * 2:
                    await self.add_suspicious_activity(client_ip, "severe_rate_limit_violation")
                
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded for {category}. Try again in {limits['window']} seconds.",
                    headers={"Retry-After": str(limits["window"])}
                )
            
            # Increment counter
            cache.increment(rate_key)
            cache.set(rate_key, current_count + 1, ttl=limits["window"])
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
    
    async def check_request_security(self, request: Request):
        """Check request for security threats"""
        
        # Get request body for POST/PUT requests
        body = ""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Read body (this consumes the stream, so we need to be careful)
                body_bytes = await request.body()
                if body_bytes:
                    body = body_bytes.decode("utf-8")
                    
                    # Check body size
                    if len(body) > 10 * 1024 * 1024:  # 10MB limit
                        raise HTTPException(status_code=413, detail="Request body too large")
                        
            except UnicodeDecodeError:
                # Binary data is okay for file uploads
                pass
            except Exception as e:
                logger.warning(f"Error reading request body: {e}")
        
        # Check for SQL injection
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, str(request.url.query), re.IGNORECASE):
                await self.add_suspicious_activity(getattr(request.client, 'host', 'unknown') if request.client else 'unknown', "sql_injection_attempt")
                raise HTTPException(status_code=400, detail="Invalid request format")
            
            if body and re.search(pattern, body, re.IGNORECASE):
                await self.add_suspicious_activity(getattr(request.client, 'host', 'unknown') if request.client else 'unknown', "sql_injection_attempt")
                raise HTTPException(status_code=400, detail="Invalid request content")
        
        # Check for XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, str(request.url.query), re.IGNORECASE):
                await self.add_suspicious_activity(getattr(request.client, 'host', 'unknown') if request.client else 'unknown', "xss_attempt")
                raise HTTPException(status_code=400, detail="Invalid request format")
            
            if body and re.search(pattern, body, re.IGNORECASE):
                await self.add_suspicious_activity(getattr(request.client, 'host', 'unknown') if request.client else 'unknown', "xss_attempt")
                raise HTTPException(status_code=400, detail="Invalid request content")
        
        # Check User-Agent
        user_agent = request.headers.get("User-Agent", "")
        if not user_agent or len(user_agent) < 10:
            await self.add_suspicious_activity(getattr(request.client, 'host', 'unknown') if request.client else 'unknown', "suspicious_user_agent")
        
        # Check for common attack patterns in headers
        suspicious_headers = ["X-Forwarded-Host", "X-Originating-IP", "X-Remote-IP"]
        for header in suspicious_headers:
            if request.headers.get(header):
                await self.add_suspicious_activity(getattr(request.client, 'host', 'unknown') if request.client else 'unknown', f"suspicious_header_{header}")
    
    def add_security_headers(self, response: Response) -> Response:
        """Add comprehensive security headers"""
        
        security_headers = {
            # Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' ws: wss:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'"
            ),
            
            # Security headers
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            
            # HTTPS enforcement
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Custom headers
            "X-Powered-By": "ZmartBot-Alerts-v2.0",
            "X-Request-ID": f"req_{int(time.time())}_{hash(str(time.time())) % 10000}",
            
            # CORS headers (adjust based on your needs)
            "Access-Control-Allow-Origin": "http://localhost:3400",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    async def add_suspicious_activity(self, client_ip: str, activity_type: str):
        """Track suspicious activity and implement progressive blocking"""
        
        if not cache.is_available():
            return
        
        try:
            # Track activity
            activity_key = f"suspicious:{client_ip}:{activity_type}"
            current_count = cache.increment(activity_key) or 0
            
            # Set expiration if this is the first occurrence
            if current_count == 1:
                cache.set(activity_key, 1, ttl=3600)  # 1 hour window
            
            # Progressive blocking
            total_suspicious = 0
            activity_types = ["sql_injection_attempt", "xss_attempt", "suspicious_user_agent", 
                            "severe_rate_limit_violation", "suspicious_header"]
            
            for act_type in activity_types:
                key = f"suspicious:{client_ip}:{act_type}"
                total_suspicious += cache.get(key) or 0
            
            # Block IP if too much suspicious activity
            if total_suspicious >= 10:
                block_key = f"ip_block:{client_ip}"
                cache.set(block_key, True, ttl=3600)  # Block for 1 hour
                
                logger.warning(f"🚨 IP {client_ip} blocked due to suspicious activity: {total_suspicious} incidents")
            
            elif total_suspicious >= 5:
                # Shorter block for moderate activity
                block_key = f"ip_block:{client_ip}"
                cache.set(block_key, True, ttl=300)  # Block for 5 minutes
                
                logger.warning(f"⚠️ IP {client_ip} temporarily blocked: {total_suspicious} incidents")
            
        except Exception as e:
            logger.error(f"Error tracking suspicious activity: {e}")
    
    async def log_request(self, request: Request, response: Response, client_info: Dict[str, str], duration: float):
        """Log request for monitoring"""
        
        try:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "client_ip": client_info["ip"],
                "method": client_info["method"],
                "path": client_info["path"],
                "query": client_info["query"],
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "user_agent": client_info["user_agent"][:200],  # Truncate long user agents
                "referer": client_info["referer"][:200],
                "response_size": len(response.body) if hasattr(response, 'body') else 0
            }
            
            # Log to appropriate level based on status code
            if response.status_code >= 500:
                logger.error(f"Server error: {json.dumps(log_data)}")
            elif response.status_code >= 400:
                logger.warning(f"Client error: {json.dumps(log_data)}")
            elif response.status_code >= 300:
                logger.info(f"Redirect: {json.dumps(log_data)}")
            else:
                logger.debug(f"Success: {json.dumps(log_data)}")
            
            # Store metrics in cache for monitoring dashboard
            if cache.is_available():
                # Store recent requests for monitoring
                cache.set(f"request_log:{int(time.time())}", log_data, ttl=3600)
                
                # Update metrics counters
                cache.increment(f"metrics:requests:total")
                cache.increment(f"metrics:requests:status_{response.status_code}")
                cache.increment(f"metrics:requests:method_{client_info['method']}")
                
        except Exception as e:
            logger.error(f"Error logging request: {e}")
    
    async def log_security_event(self, request: Request, client_info: Dict[str, str], error: str, status_code: int):
        """Log security events for monitoring"""
        
        try:
            security_event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "security_violation",
                "client_ip": client_info["ip"],
                "method": client_info["method"],
                "path": client_info["path"],
                "query": client_info["query"],
                "error": error,
                "status_code": status_code,
                "user_agent": client_info["user_agent"][:200],
                "referer": client_info["referer"][:200],
                "severity": "high" if status_code == 403 else "medium"
            }
            
            logger.warning(f"🔒 Security event: {json.dumps(security_event)}")
            
            # Store in cache for security monitoring
            if cache.is_available():
                cache.set(f"security_event:{int(time.time())}", security_event, ttl=86400)  # 24 hours
                cache.increment("metrics:security:total_violations")
                
        except Exception as e:
            logger.error(f"Error logging security event: {e}")

# Security monitoring endpoints
class SecurityMonitoringRoutes:
    """Security monitoring and metrics endpoints"""
    
    @staticmethod
    def _get_keys_count(cache_instance, pattern: str) -> int:
        """Safely get count of keys matching pattern"""
        try:
            if hasattr(cache_instance, 'redis_client') and cache_instance.redis_client:
                keys = cache_instance.redis_client.keys(pattern)
                # Handle different Redis response types
                if hasattr(keys, '__len__'):
                    return len(keys)
                elif hasattr(keys, '__iter__') and not hasattr(keys, '__await__'):
                    return len(list(keys))
                else:
                    return 0
            return 0
        except Exception:
            return 0

    @staticmethod
    async def get_security_metrics():
        """Get security metrics for dashboard"""
        
        if not cache.is_available():
            return {"error": "Monitoring not available"}
        
        try:
            metrics = {
                "total_requests": cache.get("metrics:requests:total") or 0,
                "security_violations": cache.get("metrics:security:total_violations") or 0,
                "blocked_ips": SecurityMonitoringRoutes._get_keys_count(cache, "ip_block:*"),
                "suspicious_activities": SecurityMonitoringRoutes._get_keys_count(cache, "suspicious:*"),
                "status_codes": {
                    "2xx": sum(cache.get(f"metrics:requests:status_{code}") or 0 for code in range(200, 300)),
                    "4xx": sum(cache.get(f"metrics:requests:status_{code}") or 0 for code in range(400, 500)),
                    "5xx": sum(cache.get(f"metrics:requests:status_{code}") or 0 for code in range(500, 600))
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting security metrics: {e}")
            return {"error": "Failed to get metrics"}

# Export security middleware
security_middleware = SecurityMiddleware