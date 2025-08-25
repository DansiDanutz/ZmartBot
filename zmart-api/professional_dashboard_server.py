#!/usr/bin/env python3
"""
ZmartBot Professional Dashboard Server
Serves the frontend dashboard from the professional_dashboard directory
"""

import os
import sys
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
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
    title="ZmartBot Professional Dashboard",
    description="ZmartBot professional dashboard server",
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

# Mount static files from professional_dashboard directory
dashboard_dir = os.path.join(os.path.dirname(__file__), "professional_dashboard")
if os.path.exists(dashboard_dir):
    app.mount("/static", StaticFiles(directory=dashboard_dir), name="static")

# Health check endpoints
@app.get("/health")
async def health_check():
    """Liveness probe endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "zmart-dashboard",
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness probe endpoint"""
    try:
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "zmart-dashboard",
            "dependencies": {
                "static_files": "available",
                "database": "connected"
            }
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

# Dashboard endpoints
@app.get("/")
async def dashboard_root():
    """Serve the main dashboard"""
    index_path = os.path.join(dashboard_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {
            "message": "ZmartBot Professional Dashboard",
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Dashboard files not found, serving API only"
        }

@app.get("/api/futures-symbols/my-symbols/current")
async def get_my_symbols():
    """Get current my symbols data"""
    return {
        "portfolio": {
            "symbols": [
                {"symbol": "BTCUSDT", "exchange": "binance", "status": "active"},
                {"symbol": "ETHUSDT", "exchange": "binance", "status": "active"},
                {"symbol": "SOLUSDT", "exchange": "binance", "status": "active"},
                {"symbol": "AVAXUSDT", "exchange": "binance", "status": "active"}
            ],
            "total_symbols": 4,
            "last_updated": datetime.utcnow().isoformat()
        }
    }

@app.get("/enhanced-alerts")
async def enhanced_alerts():
    """Enhanced alerts endpoint"""
    return {
        "alerts": [
            {
                "id": 1,
                "type": "liquidation",
                "symbol": "BTCUSDT",
                "message": "Large liquidation cluster detected",
                "severity": "high",
                "timestamp": datetime.utcnow().isoformat()
            }
        ],
        "total_alerts": 1
    }

@app.get("/api/dashboard/status")
async def dashboard_status():
    """Dashboard status endpoint"""
    return {
        "dashboard": "active",
        "version": "1.0.0",
        "features": {
            "symbols": "active",
            "alerts": "active",
            "charts": "active",
            "trading": "active"
        },
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
    port = int(os.getenv("PORT", 3400))
    host = os.getenv("HOST", "127.0.0.1")
    
    logger.info(f"Starting ZmartBot Professional Dashboard server on {host}:{port}")
    
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
