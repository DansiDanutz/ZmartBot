#!/usr/bin/env python3
"""
KingFisher Module - Telegram Image Processing
Processes KingFisher automation images from Telegram channel
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.config.settings import settings
from src.services.telegram_service import TelegramService
from src.services.image_processing_service import ImageProcessingService
from src.services.liquidation_service import LiquidationService
from src.services.local_ai_models import LocalAIModelsService
from src.routes.telegram import router as telegram_router
from src.routes.images import router as images_router
from src.routes.liquidation import router as liquidation_router
from src.routes.analysis import router as analysis_router
from src.routes.airtable import router as airtable_router
from src.routes.enhanced_analysis import router as enhanced_analysis_router
from src.routes.complete_workflow import router as complete_workflow_router
from src.routes.master_summary import router as master_summary_router
from src.routes.automated_reports import router as automated_reports_router
from src.routes.local_ai_models import router as local_ai_models_router
from src.utils.database import init_database, close_database
from src.utils.monitoring import init_monitoring

# Import Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
    from fastapi.responses import Response
    METRICS_AVAILABLE = True
    
    # Check if metrics already exist to prevent conflicts
    try:
        # Try to get existing metrics first
        images_downloaded = REGISTRY._collector_to_names.get("kingfisher_images_downloaded_total")
        if not images_downloaded:
            images_downloaded = Counter("kingfisher_images_downloaded_total", "Images downloaded", ["source"])
        
        images_deduplicated = REGISTRY._collector_to_names.get("kingfisher_images_deduplicated_total") 
        if not images_deduplicated:
            images_deduplicated = Counter("kingfisher_images_deduplicated_total", "Images deduplicated")
            
        analysis_duration = REGISTRY._collector_to_names.get("kingfisher_analysis_duration_seconds")
        if not analysis_duration:
            analysis_duration = Histogram("kingfisher_analysis_duration_seconds", "Analysis duration", ["step"])
            
        reports_generated = REGISTRY._collector_to_names.get("kingfisher_reports_generated_total")
        if not reports_generated:
            reports_generated = Counter("kingfisher_reports_generated_total", "Reports generated", ["format"])
            
        pipeline_failures = REGISTRY._collector_to_names.get("kingfisher_pipeline_failures_total")
        if not pipeline_failures:
            pipeline_failures = Counter("kingfisher_pipeline_failures_total", "Pipeline failures", ["step", "reason"])
            
    except Exception as e:
        print(f"⚠️ Warning: Error setting up metrics: {e}")
        METRICS_AVAILABLE = False
    
except ImportError:
    METRICS_AVAILABLE = False

# Import security middleware (if available)
try:
    from src.middleware.security_middleware import SecurityMiddleware, IdempotencyMiddleware
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="KingFisher Telegram Image Processor",
    description="Processes KingFisher automation images from Telegram channel",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware if available
if SECURITY_AVAILABLE:
    try:
        import os
        # Add security middleware
        SECRET_KEY = os.getenv("SERVICE_TOKEN_SECRET", "kingfisher-dev-secret")
        REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")
        
        app.add_middleware(SecurityMiddleware, secret_key=SECRET_KEY, redis_url=REDIS_URL)
        app.add_middleware(IdempotencyMiddleware, redis_url=REDIS_URL, ttl_hours=24)
        
        print("✅ Security middleware enabled")
    except Exception as e:
        print(f"⚠️ Failed to enable security middleware: {e}")
else:
    print("⚠️ Security middleware disabled - development mode only")

# Initialize services
telegram_service = TelegramService()
image_processor = ImageProcessingService()
liquidation_service = LiquidationService()
local_ai_service = LocalAIModelsService()

@app.on_event("startup") 
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting KingFisher Telegram Image Processor v1.1.0")
    
    try:
        # Initialize database
        await init_database()
        logger.info("✅ Database initialized")
        
        # Initialize monitoring  
        await init_monitoring()
        logger.info("✅ Monitoring initialized")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize core services: {e}")
    
    try:
        # Initialize Telegram service
        telegram_initialized = await telegram_service.initialize()
        if telegram_initialized:
            # Start Telegram monitoring
            asyncio.create_task(telegram_service.start_monitoring())
            logger.info("✅ Telegram service initialized and monitoring started")
        else:
            logger.warning("⚠️ Telegram service failed to initialize - monitoring disabled")
    except Exception as e:
        logger.warning(f"⚠️ Telegram service initialization failed: {e}")
    
    try:
        # Initialize Local AI Models service
        local_ai_initialized = await local_ai_service.initialize()
        if local_ai_initialized:
            logger.info("✅ Local AI Models service initialized successfully")
        else:
            logger.warning("⚠️ Local AI Models service failed to initialize")
    except Exception as e:
        logger.warning(f"⚠️ Local AI Models service initialization failed: {e}")
    
    logger.info("KingFisher module v1.1.0 startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down KingFisher module v1.1.0")
    try:
        await close_database()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

# Include API routes
app.include_router(telegram_router, prefix="/api/v1/telegram", tags=["telegram"])
app.include_router(images_router, prefix="/api/v1/images", tags=["images"])
app.include_router(liquidation_router, prefix="/api/v1/liquidation", tags=["liquidation"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(airtable_router, prefix="/api/v1/airtable", tags=["airtable"])
app.include_router(enhanced_analysis_router, prefix="/api/v1/enhanced-analysis", tags=["enhanced-analysis"])
app.include_router(complete_workflow_router, prefix="/api/v1/complete-workflow", tags=["complete-workflow"])
app.include_router(master_summary_router, prefix="/api/v1/master-summary", tags=["master-summary"])
app.include_router(automated_reports_router, prefix="/api/v1/automated-reports", tags=["automated-reports"])
app.include_router(local_ai_models_router, prefix="/api/v1/local-ai-models", tags=["local-ai-models"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "zmart-kingfisher", 
        "version": "1.1.0",
        "uptime_seconds": 0,  # TODO: Add actual uptime tracking
        "timestamp": datetime.now().isoformat(),
        "services": {
            "telegram": telegram_service.is_ready() if hasattr(telegram_service, 'is_ready') else False,
            "image_processor": image_processor.is_ready() if hasattr(image_processor, 'is_ready') else False,
            "liquidation": liquidation_service.is_ready() if hasattr(liquidation_service, 'is_ready') else False,
            "local_ai_models": local_ai_service.is_ready() if hasattr(local_ai_service, 'is_ready') else False
        }
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint - v1.1.0 specification"""
    # Check hard dependencies
    hard_deps = {
        "db": "ok",      # TODO: Add actual database health check
        "redis": "ok",   # TODO: Add actual Redis health check  
        "mq": "ok",      # TODO: Add actual RabbitMQ health check
        "config": "ok"   # TODO: Add actual config validation
    }
    
    # Check soft dependencies (can be warn)
    soft_deps = {
        "telegram": "warn",  # Telegram can be degraded
        "openai": "warn"     # OpenAI can be degraded
    }
    
    # Determine overall status
    all_hard_ok = all(v == "ok" for v in hard_deps.values())
    status = "ready" if all_hard_ok else "not_ready"
    
    return {
        "status": status,
        "hard_dependencies": hard_deps,
        "soft_dependencies": soft_deps,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if METRICS_AVAILABLE:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    else:
        return {"error": "Metrics not available"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "KingFisher Telegram Image Processor",
        "version": "1.1.0",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "metrics": "/metrics"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 