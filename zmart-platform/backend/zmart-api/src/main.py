"""
Zmart Trading Bot Platform - Main Application Entry Point
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

from src.config.settings import settings
from src.agents.orchestration.orchestration_agent import OrchestrationAgent
from src.utils.database import init_database, close_database
from src.utils.monitoring import setup_monitoring
from src.utils.metrics import setup_metrics

# Import routes
from src.routes import health, auth, trading, signals, agents, monitoring

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.monitoring.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global orchestration agent instance
orchestration_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Zmart Trading Bot Platform...")
    
    # Initialize database connections
    await init_database()
    
    # Setup monitoring and metrics
    setup_monitoring()
    setup_metrics()
    
    # Initialize orchestration agent
    global orchestration_agent
    orchestration_agent = OrchestrationAgent()
    await orchestration_agent.start()
    
    logger.info("Zmart Trading Bot Platform started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Zmart Trading Bot Platform...")
    
    # Stop orchestration agent
    if orchestration_agent:
        await orchestration_agent.stop()
    
    # Close database connections
    await close_database()
    
    logger.info("Zmart Trading Bot Platform shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Zmart Trading Bot Platform",
    description="Advanced cryptocurrency trading bot platform with AI-powered signal generation and risk management",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"]
)

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
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
    """Handle request validation errors"""
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
            "message": "An unexpected error occurred",
            "path": str(request.url)
        }
    )

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(trading.router, prefix="/api/v1/trading", tags=["trading"])
app.include_router(signals.router, prefix="/api/v1/signals", tags=["signals"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic platform information"""
    return {
        "name": "Zmart Trading Bot Platform",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment.value,
        "docs": "/docs" if settings.debug else None
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.monitoring.log_level.lower()
    ) 