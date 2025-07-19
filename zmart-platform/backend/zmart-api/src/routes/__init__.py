"""
Zmart Trading Bot Platform - API Routes
Main router that includes all API endpoints
"""

from fastapi import APIRouter

from src.routes import health, trading, signals, agents, monitoring, auth

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(trading.router, prefix="/trading", tags=["trading"])
api_router.include_router(signals.router, prefix="/signals", tags=["signals"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"]) 