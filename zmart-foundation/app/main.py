from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .utils.logging import setup_logging
from .utils.otel import setup_otel
from .routers import signals, pools, credits, alerts, health, chat, engagement
from .db import init_models
from .services.pools import process_expired_pools
from .middleware.engagement_integration import EngagementIntegrationMiddleware, sync_with_engagement_system
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
import asyncio

setup_logging()
app = FastAPI(title="ZmartBot Foundation", version="0.1.0")
setup_otel(app)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://zmart-app.vercel.app",
        "https://zmart.ai"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add engagement integration middleware
app.add_middleware(EngagementIntegrationMiddleware)

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def on_startup():
    await init_models()
    
    # Start background scheduler for pool expiry
    scheduler.add_job(
        process_expired_pools,
        'interval',
        minutes=5,
        id='pool_expiry_job'
    )
    
    # Add engagement system sync task
    scheduler.add_job(
        sync_with_engagement_system,
        'interval',
        minutes=1,
        id='engagement_sync_job'
    )
    
    scheduler.start()
    logger.info("Background scheduler started for pool expiry processing and engagement sync")

@app.on_event("shutdown") 
async def on_shutdown():
    scheduler.shutdown()
    logger.info("Background scheduler stopped")

app.include_router(health.router, prefix="/v1/health", tags=["health"])
app.include_router(signals.router, prefix="/v1/signals", tags=["signals"])
app.include_router(pools.router, prefix="/v1/pools", tags=["pools"])
app.include_router(credits.router, prefix="/v1/credits", tags=["credits"])
app.include_router(alerts.router, prefix="/v1/alerts", tags=["alerts"])
app.include_router(chat.router, prefix="/v1", tags=["chat"])
app.include_router(engagement.router, prefix="/v1", tags=["engagement"])
