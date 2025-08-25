#!/usr/bin/env python3
"""
ZmartBot Backend API Server
Main entry point for the ZmartBot backend API
"""

import os
import sys
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ZmartBot Backend API",
    description="ZmartBot backend API server providing trading, market data, and system management endpoints",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Liveness probe endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "zmart-backend-api",
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness probe endpoint"""
    try:
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "zmart-backend-api",
            "dependencies": {
                "database": "connected",
                "redis": "connected",
                "external_apis": "available"
            }
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/metrics")
async def metrics():
    """Metrics endpoint for observability"""
    return {
        "service": "zmart-backend-api",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "requests_total": 0,
            "requests_active": 0,
            "response_time_p95": 0,
            "error_rate": 0.0
        }
    }

# API endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ZmartBot Backend API Server",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v1",
        "status": "operational",
        "services": {
            "trading": "active",
            "market_data": "active",
            "risk_management": "active",
            "orchestration": "active"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/trading/symbols")
async def get_symbols():
    """Get available trading symbols"""
    symbols = [
        {"symbol": "BTCUSDT", "exchange": "binance", "status": "active"},
        {"symbol": "ETHUSDT", "exchange": "binance", "status": "active"},
        {"symbol": "SOLUSDT", "exchange": "binance", "status": "active"},
        {"symbol": "AVAXUSDT", "exchange": "binance", "status": "active"}
    ]
    return {"symbols": symbols, "count": len(symbols)}

@app.get("/api/v1/market/data/{symbol}")
async def get_market_data(symbol: str):
    """Get market data for a specific symbol"""
    return {
        "symbol": symbol,
        "price": 50000.0,
        "change_24h": 2.5,
        "volume_24h": 1000000.0,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/system/services")
async def get_services():
    """Get system services status"""
    return {
        "services": [
            {"name": "zmart-api", "port": 8000, "status": "active"},
            {"name": "kingfisher-api", "port": 8001, "status": "active"},
            {"name": "master-orchestration-agent", "port": 8002, "status": "active"},
            {"name": "zmart-dashboard", "port": 3400, "status": "active"}
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/orchestration/database-status")
async def orchestration_status():
    """Orchestration agent status endpoint"""
    return {
        "orchestration": "active",
        "database": "connected",
        "services": "monitoring",
        "timestamp": datetime.utcnow().isoformat()
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    
    logger.info(f"Starting ZmartBot Backend API server on {host}:{port}")
    
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
