"""
Zmart Trading Bot Platform - Main API Application
FastAPI-based backend service with comprehensive trading capabilities
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware

from src.config.settings import settings
from src.utils.database import init_database, close_database
from src.utils.monitoring import init_monitoring
from src.agents.orchestration.orchestration_agent import OrchestrationAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global orchestration agent instance
orchestration_agent: Optional[OrchestrationAgent] = None

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
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Zmart Trading Bot Platform API")
    
    # Initialize database connections
    await init_database()
    
    # Initialize monitoring
    await init_monitoring()
    
    # Initialize orchestration agent
    global orchestration_agent
    orchestration_agent = OrchestrationAgent()
    await orchestration_agent.start()
    
    logger.info("Zmart Trading Bot Platform API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Zmart Trading Bot Platform API")
    
    # Stop orchestration agent
    if orchestration_agent:
        await orchestration_agent.stop()
    
    # Close database connections
    await close_database()
    
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

# Add middleware
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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "zmart-api",
        "version": "1.0.0",
        "timestamp": asyncio.get_event_loop().time()
    }

# Include API routes
from src.routes import health, auth, trading, signals, agents, monitoring

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(trading.router, prefix="/api/v1/trading", tags=["trading"])
app.include_router(signals.router, prefix="/api/v1/signals", tags=["signals"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 