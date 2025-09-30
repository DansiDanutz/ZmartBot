"""
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
