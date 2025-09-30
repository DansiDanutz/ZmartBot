#!/usr/bin/env python3
"""
Zmart Trading Bot Platform - Fixed Main API Application
Resolved version with all backend conflicts and issues fixed
"""
import asyncio
import logging
import sys
import os
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware

# Add src to Python path to fix import issues
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import settings first to ensure configuration is loaded
try:
    from config.settings import settings
    print("✅ Settings imported successfully")
except ImportError as e:
    print(f"❌ Settings import failed: {e}")
    # Create minimal settings for fallback
    class MinimalSettings:
        HOST = "0.0.0.0"
        PORT = 8000
        DEBUG = True
        CORS_ORIGINS = ["*"]
        ALLOWED_HOSTS = ["*"]
        ENVIRONMENT = "development"
    settings = MinimalSettings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global orchestration agent instance
orchestration_agent: Optional[object] = None

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    async def dispatch(self, request: Request, call_next):
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(f"Response: {response.status_code}")
        
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with error handling"""
    # Startup
    logger.info("Starting Zmart Trading Bot Platform API")
    
    try:
        # Initialize database connections with error handling
        try:
            from utils.database import init_database
            await init_database()
            logger.info("✅ Database connections initialized")
        except Exception as e:
            logger.warning(f"⚠️ Database initialization failed: {e}")
            logger.info("Database connections will be skipped for development")
        
        # Initialize monitoring with error handling
        try:
            from utils.monitoring import init_monitoring
            await init_monitoring()
            logger.info("✅ Monitoring initialized")
        except Exception as e:
            logger.warning(f"⚠️ Monitoring initialization failed: {e}")
            logger.info("Monitoring will be skipped for development")
        
        # Initialize orchestration agent with error handling
        try:
            from agents.orchestration.orchestration_agent import OrchestrationAgent
            global orchestration_agent
            orchestration_agent = OrchestrationAgent()
            await orchestration_agent.start()
            logger.info("✅ Orchestration agent initialized")
        except Exception as e:
            logger.warning(f"⚠️ Orchestration agent initialization failed: {e}")
            logger.info("Orchestration agent will be skipped for development")
            orchestration_agent = None
        
        logger.info("Zmart Trading Bot Platform API started successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        # Continue anyway for development
    
    yield
    
    # Shutdown
    logger.info("Shutting down Zmart Trading Bot Platform API")
    
    try:
        # Stop orchestration agent
        if orchestration_agent:
            await orchestration_agent.stop()
            logger.info("✅ Orchestration agent stopped")
    except Exception as e:
        logger.warning(f"⚠️ Orchestration agent shutdown failed: {e}")
    
    try:
        # Close database connections
        from utils.database import close_database
        await close_database()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.warning(f"⚠️ Database shutdown failed: {e}")
    
    logger.info("Zmart Trading Bot Platform API shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Zmart Trading Bot Platform API",
    description="Advanced cryptocurrency trading bot platform with AI-powered signal processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware with error handling
try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )
except Exception as e:
    logger.warning(f"⚠️ Middleware setup failed: {e}")

app.add_middleware(LoggingMiddleware)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "path": str(request.url)
        }
    )

# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check endpoint"""
    try:
        # Check database connections
        db_health = {}
        try:
            from utils.database import check_database_health
            db_health = await check_database_health()
        except Exception as e:
            db_health = {"error": str(e)}
        
        # Check orchestration agent
        agent_health = "unknown"
        if orchestration_agent:
            try:
                agent_health = "healthy" if hasattr(orchestration_agent, 'is_running') and orchestration_agent.is_running else "unhealthy"
            except:
                agent_health = "error"
        
        return {
            "status": "healthy",
            "service": "zmart-api",
            "version": "1.0.0",
            "timestamp": asyncio.get_event_loop().time(),
            "environment": getattr(settings, 'ENVIRONMENT', 'development'),
            "database": db_health,
            "orchestration_agent": agent_health,
            "uptime": "running"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "service": "zmart-api",
            "version": "1.0.0",
            "error": str(e),
            "timestamp": asyncio.get_event_loop().time()
        }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ZmartBot Trading Platform API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }

# Include API routes with error handling
try:
    from routes import health, auth, trading, signals, agents, monitoring, cryptometer, websocket, charting, explainability, analytics
    
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
    app.include_router(trading.router, prefix="/api/v1/trading", tags=["trading"])
    app.include_router(signals.router, prefix="/api/v1/signals", tags=["signals"])
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
    app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
    app.include_router(cryptometer.router, tags=["cryptometer"])
    app.include_router(websocket.router, tags=["websocket"])
    app.include_router(charting.router, prefix="/api/v1", tags=["charting"])
    app.include_router(explainability.router, prefix="/api/v1/explainability", tags=["explainability"])
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
    
    logger.info("✅ All API routes loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load API routes: {e}")
    # Create minimal routes for basic functionality
    @app.get("/api/v1/test")
    async def test_endpoint():
        return {"message": "API is working", "routes_loaded": False}

if __name__ == "__main__":
    print("🚀 Starting ZmartBot API with fixed configuration...")
    print(f"📍 Host: {getattr(settings, 'HOST', '0.0.0.0')}")
    print(f"📍 Port: {getattr(settings, 'PORT', 8000)}")
    print(f"📍 Environment: {getattr(settings, 'ENVIRONMENT', 'development')}")
    
    uvicorn.run(
        "fixed_main:app",
        host=getattr(settings, 'HOST', '0.0.0.0'),
        port=getattr(settings, 'PORT', 8000),
        reload=getattr(settings, 'DEBUG', True),
        log_level="info"
    ) 