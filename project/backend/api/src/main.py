"""
Zmart Trading Bot Platform - Main API Application
FastAPI-based backend service with comprehensive trading capabilities
"""
import asyncio
import logging
import traceback
from datetime import datetime
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
    import time
    app.state.start_time = time.time()
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
    
    # Start indicators collector service (re-enabled with stability improvements)
    try:
        from src.services.indicators_collector_service import get_indicators_collector
        indicators_collector = await get_indicators_collector()
        asyncio.create_task(indicators_collector.start())
        logger.info("✅ Indicators Collector Service started with improved stability")
    except Exception as e:
        logger.warning(f"Could not start Indicators Collector Service: {e}")
    
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
    """Handle general exceptions with enhanced error tracking"""
    from src.utils.enhanced_error_handler import error_tracker, classify_error, ErrorRecord
    
    # Classify the error
    severity, category = classify_error(exc)
    
    # Create error record
    error_record = ErrorRecord(
        timestamp=datetime.now(),
        error_type=type(exc).__name__,
        error_message=str(exc),
        severity=severity,
        category=category,
        component="api",
        endpoint=str(request.url),
        stack_trace=traceback.format_exc(),
        context={
            "method": request.method,
            "path": str(request.url),
            "headers": dict(request.headers)
        }
    )
    
    # Record the error
    error_tracker.record_error(error_record)
    
    # Log the error
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "path": str(request.url),
            "error_id": f"{error_record.timestamp.isoformat()}_{type(exc).__name__}"
        }
    )

# Enhanced Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "zmart-api",
        "version": "1.0.0",
        "timestamp": asyncio.get_event_loop().time()
    }

@app.get("/health/ready")
async def readiness_check():
    """Comprehensive readiness check for all services"""
    from datetime import datetime
    import time
    
    health_status = {
        "status": "ready",
        "service": "zmart-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - getattr(app.state, 'start_time', time.time()),
        "components": {}
    }
    
    # Check database connections
    try:
        from src.utils.database import check_database_health
        db_health = await check_database_health()
        healthy_dbs = [db for db, status in db_health.items() if status]
        total_dbs = len(db_health)
        
        if len(healthy_dbs) == total_dbs:
            health_status["components"]["database"] = {
                "status": "healthy",
                "details": f"All databases healthy: {', '.join(healthy_dbs)}"
            }
        elif len(healthy_dbs) > 0:
            health_status["components"]["database"] = {
                "status": "degraded",
                "details": f"Partial database health: {len(healthy_dbs)}/{total_dbs} healthy"
            }
            health_status["status"] = "degraded"
        else:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "details": "No databases healthy"
            }
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "details": f"Database check failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Check orchestration agent
    global orchestration_agent
    if orchestration_agent is not None:
        health_status["components"]["orchestration"] = {
            "status": "healthy",
            "details": "Orchestration agent running"
        }
    else:
        health_status["components"]["orchestration"] = {
            "status": "unhealthy",
            "details": "Orchestration agent not available"
        }
        health_status["status"] = "degraded"
    
    # Check position lifecycle orchestrator
    try:
        from src.agents.position_lifecycle_orchestrator import position_orchestrator
        if hasattr(position_orchestrator, 'is_monitoring') and position_orchestrator.is_monitoring:
            health_status["components"]["position_orchestrator"] = {
                "status": "healthy",
                "details": "Position orchestrator monitoring active"
            }
        else:
            health_status["components"]["position_orchestrator"] = {
                "status": "unhealthy",
                "details": "Position orchestrator not monitoring"
            }
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["position_orchestrator"] = {
            "status": "unhealthy",
            "details": f"Position orchestrator check failed: {str(e)}"
        }
        health_status["status"] = "degraded"
    
    # Check enhanced alerts system
    try:
        from src.lib.services.enhanced_alerts_integration import enhanced_alerts_integration
        health_status["components"]["enhanced_alerts"] = {
            "status": "healthy" if enhanced_alerts_integration.existing_services_available else "degraded",
            "details": "Enhanced alerts system loaded" if enhanced_alerts_integration.existing_services_available else "Enhanced alerts using mock data"
        }
    except Exception as e:
        health_status["components"]["enhanced_alerts"] = {
            "status": "unhealthy",
            "details": f"Enhanced alerts check failed: {str(e)}"
        }
    
    # Check external API connections (non-blocking)
    try:
        # This is a quick check - you can expand this
        health_status["components"]["external_apis"] = {
            "status": "unknown",
            "details": "External API health checks not implemented"
        }
    except Exception as e:
        health_status["components"]["external_apis"] = {
            "status": "unhealthy",
            "details": f"External API check failed: {str(e)}"
        }
    
    # Determine overall status
    component_statuses = [comp["status"] for comp in health_status["components"].values()]
    if "unhealthy" in component_statuses:
        health_status["status"] = "unhealthy"
    elif "degraded" in component_statuses:
        health_status["status"] = "degraded"
    else:
        health_status["status"] = "ready"
    
    # Return appropriate HTTP status code
    if health_status["status"] == "unhealthy":
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

@app.get("/health/live")
async def liveness_check():
    """Simple liveness check - just confirms the server is responding"""
    from datetime import datetime
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

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
    additional_health, additional_signals, chatgpt_alerts, alerts, openai_trading_advice
)

# Import missing calibrated_scoring separately if it exists
has_calibrated_scoring = False

# Import indicators history routes
from src.routes.indicators_history import router as indicators_history_router

# Import demo real-time routes for fallback
from src.routes.demo_real_time import router as demo_real_time_router

# Import Cryptometer management routes
from src.routes.cryptometer_management import router as cryptometer_management_router
# Import subscription monitoring routes
from src.routes.subscription import router as subscription_router

# Import error monitoring routes
from src.routes.error_monitoring import router as error_monitoring_router

# Import memory optimization routes
from src.routes.memory_optimization import router as memory_optimization_router

# Import real-time alert routes
from src.routes.real_time_alerts import router as real_time_alerts_router

# Import live alerts dashboard routes
from src.routes.live_alerts_dashboard import router as live_alerts_dashboard_router

# Import database orchestrator
from src.services.database_orchestrator import start_database_orchestrator, stop_database_orchestrator

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
app.include_router(openai_trading_advice.router, prefix="/api/v1", tags=["openai-trading-advice"])
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
app.include_router(alerts.router, tags=["alerts"])  # Professional Trading Alerts System
app.include_router(indicators_history_router, tags=["indicators-history"])  # 📊 Comprehensive Indicators History Database
app.include_router(demo_real_time_router, tags=["demo-real-time"])
app.include_router(cryptometer_management_router, tags=["cryptometer-management"])  # 🎭 Demo Real-Time Data for Testing
app.include_router(subscription_router, tags=["subscription"])  # 📅 Subscription monitoring and notifications
app.include_router(error_monitoring_router, prefix="/api/v1/error-monitoring", tags=["error-monitoring"])  # 🚨 Enhanced Error Handling and Monitoring
app.include_router(memory_optimization_router, prefix="/api/v1/memory", tags=["memory-optimization"])  # 🧠 Memory Optimization and Monitoring
app.include_router(real_time_alerts_router, prefix="/api/v1/real-alerts", tags=["real-time-alerts"])  # 🚨 Real-Time Alerts with Live Data
app.include_router(live_alerts_dashboard_router, prefix="/api/v1/live-alerts", tags=["live-alerts-dashboard"])  # 📊 Live Alerts Dashboard with 21 Indicators

# Orchestration Status Endpoint
@app.get("/api/v1/orchestration/indicator-history-status")
async def get_orchestration_indicator_history_status():
    """Get IndicatorHistory system status from orchestration"""
    try:
        if orchestration_agent:
            status = orchestration_agent.get_indicator_history_status()
            return {"success": True, "data": status}
        else:
            return {"success": False, "error": "Orchestration agent not initialized"}
    except Exception as e:
        logger.error(f"Error getting orchestration status: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/v1/orchestration/status")
async def get_orchestration_status():
    """Get overall orchestration system status"""
    try:
        if orchestration_agent:
            return {
                "success": True,
                "data": {
                    "status": orchestration_agent.status.value,
                    "agents": {agent_id: {
                        "type": agent_info.agent_type.value,
                        "status": agent_info.status.value,
                        "last_heartbeat": agent_info.last_heartbeat.isoformat(),
                        "metadata": agent_info.metadata
                    } for agent_id, agent_info in orchestration_agent.agents.items()},
                    "indicator_history": orchestration_agent.get_indicator_history_status(),
                    "database_orchestrator": orchestration_agent.get_database_orchestrator_status(),
                    "last_update": datetime.now().isoformat()
                }
            }
        else:
            return {"success": False, "error": "Orchestration agent not initialized"}
    except Exception as e:
        logger.error(f"Error getting orchestration status: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/v1/orchestration/database-status")
async def get_database_orchestrator_status():
    """Get database orchestrator status - Fixes all database update issues"""
    try:
        if orchestration_agent:
            return {
                "success": True,
                "data": orchestration_agent.get_database_orchestrator_status(),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"success": False, "error": "Orchestration agent not initialized"}
    except Exception as e:
        logger.error(f"Error getting database orchestrator status: {e}")
        return {"success": False, "error": str(e)}

# Dashboard is served separately on port 3400 by dashboard_server.py
# This server (port 8000) only handles API requests
logger.info("API Server running on port 8000")
logger.info("Dashboard Server should be running on port 3400 (run dashboard_server.py)")
logger.info("IndicatorHistory system integrated into orchestration")

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("🚀 Starting ZmartBot API Server")
    
    # Start database orchestrator
    asyncio.create_task(start_database_orchestrator())
    
    logger.info("✅ ZmartBot API Server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("🛑 Shutting down ZmartBot API Server")
    
    # Stop database orchestrator
    await stop_database_orchestrator()
    
    logger.info("✅ ZmartBot API Server shutdown complete")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 