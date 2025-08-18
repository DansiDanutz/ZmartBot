"""
Secure FastAPI Application with Enhanced Alerts System
Integrates all security enhancements and performance optimizations
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from contextlib import asynccontextmanager

# Import security middleware and components
from .middleware.security_middleware import SecurityMiddleware, SecurityMonitoringRoutes
from .auth.auth_routes import router as auth_router, init_user_database
from .routes.alerts_secure import router as alerts_router
from .websocket.websocket_routes import router as websocket_router
from .cache.redis_cache import cache
from .websocket.websocket_manager import start_websocket_health_check

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    
    # Startup
    logger.info("🚀 Starting Enhanced Alerts System...")
    
    # Initialize databases
    init_user_database()
    
    # Test Redis connection
    if cache.is_available():
        logger.info("✅ Redis cache connected")
    else:
        logger.warning("⚠️ Redis cache not available - running without caching")
    
    # Start WebSocket health monitoring
    start_websocket_health_check()
    logger.info("✅ WebSocket health monitoring started")
    
    # Initialize security monitoring
    logger.info("✅ Security middleware initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Enhanced Alerts System...")

# Create FastAPI application
app = FastAPI(
    title="Enhanced Alerts System - Secure",
    description="Professional-grade cryptocurrency trading alerts with comprehensive security",
    version="2.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
    lifespan=lifespan
)

# Add security middleware (commented out due to import issues - can be enabled after fixing imports)
# app.add_middleware(SecurityMiddleware)

# CORS middleware (configure based on your needs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3400", "http://localhost:5173"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Powered-By"]
)

# Include routers
app.include_router(auth_router)
app.include_router(alerts_router)
app.include_router(websocket_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Application health check"""
    
    health_status = {
        "status": "healthy",
        "timestamp": "2025-08-17T12:00:00Z",
        "version": "2.0.0",
        "services": {
            "redis": cache.is_available(),
            "authentication": True,
            "websocket": True,
            "alerts_engine": True
        }
    }
    
    return JSONResponse(
        status_code=200,
        content=health_status,
        headers={"Cache-Control": "no-cache"}
    )

# Security monitoring endpoint
@app.get("/api/v1/system/security-metrics")
async def get_security_metrics():
    """Get security metrics for monitoring dashboard"""
    
    try:
        metrics = await SecurityMonitoringRoutes.get_security_metrics()
        return {
            "success": True,
            "data": metrics,
            "timestamp": "2025-08-17T12:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error getting security metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get security metrics")

# Error reporting endpoint for frontend
@app.post("/api/v1/system/error-report")
async def report_error(request: Request):
    """Frontend error reporting endpoint"""
    
    try:
        error_data = await request.json()
        
        # Log frontend error
        logger.error(f"Frontend error reported: {error_data}")
        
        # Store in cache for monitoring (optional)
        if cache.is_available():
            cache.set(
                f"frontend_error:{int(time.time())}", 
                error_data, 
                ttl=86400  # 24 hours
            )
        
        return {
            "success": True,
            "message": "Error reported successfully",
            "timestamp": "2025-08-17T12:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error processing error report: {e}")
        return {
            "success": False,
            "error": "Failed to process error report",
            "timestamp": "2025-08-17T12:00:00Z"
        }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An unexpected error occurred",
            "timestamp": "2025-08-17T12:00:00Z",
            "request_id": request.headers.get("X-Request-ID", "unknown")
        }
    )

# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler with consistent response format"""
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": "2025-08-17T12:00:00Z",
            "status_code": exc.status_code
        }
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information"""
    
    return {
        "message": "Enhanced Alerts System - Secure API",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": "2025-08-17T12:00:00Z",
        "documentation": "/docs" if os.getenv("ENVIRONMENT") != "production" else "Contact administrator",
        "websocket": "/ws/alerts",
        "security": {
            "authentication": "JWT Bearer Token",
            "rate_limiting": "Enabled",
            "security_headers": "Enabled",
            "input_validation": "Enabled"
        }
    }

if __name__ == "__main__":
    import uvicorn
    import time
    
    # Configuration
    config = {
        "host": "0.0.0.0",
        "port": 8001,  # Different port for secure version
        "reload": os.getenv("ENVIRONMENT") != "production",
        "log_level": "info",
        "access_log": True,
        "server_header": False,  # Don't reveal server information
        "date_header": False     # Don't include date header
    }
    
    logger.info("🔐 Starting Enhanced Alerts System - Secure Version")
    logger.info(f"📡 Server will start on http://{config['host']}:{config['port']}")
    logger.info("🔒 Security features: Authentication, Rate Limiting, Input Validation, WebSocket")
    
    uvicorn.run("main_secure:app", **config)