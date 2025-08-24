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
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.config.settings import settings
from src.utils.database import init_database, close_database
# from src.utils.monitoring import init_monitoring  # REMOVED - causing issues
from src.agents.orchestration.orchestration_agent import OrchestrationAgent
from src.agents.position_lifecycle_orchestrator import position_orchestrator

# Import security modules
from src.security.headers import SecurityHeadersMiddleware
from src.security.rate_limiting import limiter, rate_limit_handler
from src.security.secrets import get_secrets_manager

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
    # await init_monitoring()  # DISABLED - causing issues
    
    # Initialize orchestration agent
    global orchestration_agent
    try:
        orchestration_agent = OrchestrationAgent()
        await orchestration_agent.start()
    except Exception as e:
        logger.warning(f"Could not start orchestration agent: {e}")
        orchestration_agent = None
    
    # Start Position Lifecycle Orchestrator
    try:
        await position_orchestrator.start_monitoring()
        logger.info("Position Lifecycle Orchestrator started successfully")
    except Exception as e:
        logger.error(f"Could not start Position Lifecycle Orchestrator: {e}")
    
    logger.info("Zmart Trading Bot Platform API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Zmart Trading Bot Platform API")
    
    # Stop Position Lifecycle Orchestrator
    try:
        await position_orchestrator.stop_monitoring()
        logger.info("Position Lifecycle Orchestrator stopped")
    except Exception as e:
        logger.error(f"Error stopping Position Lifecycle Orchestrator: {e}")
    
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

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)

# Configure CORS with security in mind
# Explicitly allow localhost dashboard ports and use a regex as a fallback to avoid env parsing issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^http://localhost:(3000|3400|5173)$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Add rate limiting
app.state.limiter = limiter

# Rate limit exception handler wrapper
async def rate_limit_exception_handler(request: Request, exc: Exception) -> Response:
    if isinstance(exc, RateLimitExceeded):
        return await rate_limit_handler(request, exc)
    raise exc

app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)

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

# Include API routes - Fixed missing imports
from src.routes import (
    health, auth, trading, signals, agents, monitoring, cryptometer, websocket, 
    charting, explainability, analytics, ai_analysis, learning_ai_analysis, 
    historical_analysis, multi_model_analysis, unified_cryptometer, 
    professional_analysis, unified_analysis, blockchain, binance, grok_x, 
    my_symbols, real_time_prices, futures_symbols, riskmetric, coefficient, risk_bands,
    master_pattern_analysis, sentiment_analysis, signal_center, unified_trading, 
    position_management, vault_trading, vault_management, trading_center, 
    cryptometer_qa_routes, unified_qa_routes, symbol_price_history_routes, 
    daily_updater_routes, riskmatrix_grid, score_tracking_routes, symbols, 
    websocket_risk, riskmetric_monitoring, market_data, positions, unified_scoring,
    additional_health, additional_signals, chatgpt_alerts, alerts, roadmap, kingfisher
)

# Enhanced alerts routes are now integrated into the existing alerts router

# Import missing calibrated_scoring separately if it exists
has_calibrated_scoring = False

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(additional_health.router, prefix="/api/v1", tags=["additional-health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(trading.router, prefix="/api/v1/trading", tags=["trading"])
app.include_router(signals.router, prefix="/api/v1/signals", tags=["signals"])
app.include_router(additional_signals.router, prefix="/api/v1", tags=["additional-signals"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
app.include_router(cryptometer.router, tags=["cryptometer"])
app.include_router(market_data.router, tags=["market-data"])
app.include_router(ai_analysis.router, prefix="/api/v1", tags=["ai-analysis"])
app.include_router(learning_ai_analysis.router, prefix="/api/v1", tags=["learning-ai-analysis"])
app.include_router(historical_analysis.router, prefix="/api/v1", tags=["historical-analysis"])
app.include_router(multi_model_analysis.router, prefix="/api/v1", tags=["multi-model-analysis"])
app.include_router(unified_cryptometer.router, prefix="/api/v1", tags=["unified-cryptometer"])
app.include_router(professional_analysis.router, prefix="/api/v1", tags=["professional-analysis"])
app.include_router(unified_analysis.router, prefix="/api/v1/unified", tags=["unified-analysis"]) # 🚀 THE ULTIMATE ANALYSIS AGENT
app.include_router(websocket.router, tags=["websocket"])
app.include_router(charting.router, prefix="/api/v1", tags=["charting"])
app.include_router(explainability.router, prefix="/api/v1/explainability", tags=["explainability"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(blockchain.router, prefix="/api/v1/blockchain", tags=["blockchain"])
app.include_router(binance.router, prefix="/api/v1/binance", tags=["binance"])
app.include_router(grok_x.router, prefix="/api/v1", tags=["grok-x"])
app.include_router(my_symbols.router, prefix="/api/v1", tags=["my-symbols"])
app.include_router(real_time_prices.router, tags=["real-time-prices"])
app.include_router(futures_symbols.router, tags=["futures-symbols"])
app.include_router(riskmetric.router, tags=["riskmetric"])  # Benjamin Cowen RiskMetric
app.include_router(coefficient.router, tags=["coefficient"])  # DBI Coefficient calculations
app.include_router(risk_bands.router, tags=["risk-bands"])  # Risk Bands API
app.include_router(master_pattern_analysis.router, tags=["pattern-analysis"])  # Master Pattern Analysis
app.include_router(sentiment_analysis.router, tags=["sentiment"])  # Grok-X Sentiment Analysis
app.include_router(signal_center.router, tags=["signal-center"])  # Unified Signal Center
app.include_router(unified_trading.router, tags=["unified-trading"])
app.include_router(position_management.router, tags=["position-management"])  # Unified Trading Agent
app.include_router(vault_trading.router, tags=["vault-trading"])  # Vault-based Trading System
app.include_router(vault_management.router, tags=["vault-management"])  # Complete Vault Management
app.include_router(trading_center.router, tags=["trading-center"])  # Trading Center with 80% win rate filter
app.include_router(cryptometer_qa_routes.router, tags=["cryptometer-qa"])  # Cryptometer QA for high-quality data
app.include_router(unified_qa_routes.router, tags=["unified-qa"])  # 🎓 Unified QA Master Teacher Agent
app.include_router(symbol_price_history_routes.router, prefix="/api/v1/symbol-price-history", tags=["symbol-price-history"])  # Symbol Price History Data Management
app.include_router(daily_updater_routes.router, prefix="/api/v1/daily-updater", tags=["daily-updater"]) # Daily Updater Routes
app.include_router(riskmatrix_grid.router, tags=["riskmatrix-grid"])  # RiskMatrixGrid - Complete Google Sheets Integration
app.include_router(score_tracking_routes.router, tags=["score-tracking"])  # Score Tracking System - Base Score and Total Score Database
app.include_router(symbols.router, tags=["symbols"])  # Symbols Database - Single Source of Truth for All Symbol Data
app.include_router(positions.router, tags=["positions"])  # Positions management endpoints
app.include_router(unified_scoring.router, tags=["scoring"])  # Unified scoring system
app.include_router(websocket_risk.router, tags=["websocket-risk"])  # WebSocket endpoint for real-time risk updates
app.include_router(riskmetric_monitoring.router, tags=["riskmetric-monitoring"])  # RiskMetric monitoring and metrics endpoints
app.include_router(chatgpt_alerts.router, tags=["chatgpt-alerts"])  # ChatGPT-powered alert generation
app.include_router(alerts.router, tags=["alerts"])  # Professional Trading Alerts System with Enhanced Alerts
app.include_router(roadmap.router, tags=["roadmap"])  # Development Roadmap and CI/CD Orchestration
app.include_router(kingfisher.router, tags=["kingfisher"])  # KingFisher liquidation analysis

# Dashboard is served separately on port 3400 by dashboard_server.py
# This server (port 8000) only handles API requests
logger.info("API Server running on port 8000")
logger.info("Dashboard Server should be running on port 3400 (run dashboard_server.py)")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 