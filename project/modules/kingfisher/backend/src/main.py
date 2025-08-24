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

# Initialize services
telegram_service = TelegramService()
image_processor = ImageProcessingService()
liquidation_service = LiquidationService()
local_ai_service = LocalAIModelsService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting KingFisher Telegram Image Processor")
    
    # Initialize database
    await init_database()
    
    # Initialize monitoring
    await init_monitoring()
    
    # Initialize Telegram service
    telegram_initialized = await telegram_service.initialize()
    if telegram_initialized:
        # Start Telegram monitoring
        asyncio.create_task(telegram_service.start_monitoring())
        logger.info("✅ Telegram service initialized and monitoring started")
    else:
        logger.warning("⚠️ Telegram service failed to initialize - monitoring disabled")
    
    # Initialize Local AI Models service
    local_ai_initialized = await local_ai_service.initialize()
    if local_ai_initialized:
        logger.info("✅ Local AI Models service initialized successfully")
    else:
        logger.warning("⚠️ Local AI Models service failed to initialize")
    
    logger.info("KingFisher module started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down KingFisher module")
    await close_database()

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
        "status": "healthy",
        "module": "kingfisher",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "telegram": telegram_service.is_ready(),
            "image_processor": image_processor.is_ready(),
            "liquidation": liquidation_service.is_ready(),
            "local_ai_models": local_ai_service.is_ready()
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "KingFisher Telegram Image Processor",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 