#!/usr/bin/env python3
"""
KuCoin Worker Service - FastAPI Server
Provides real-time market data and trading operations for KuCoin
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import json

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the existing KuCoin service
try:
    from src.services.kucoin_service import KuCoinService, KuCoinMarketData, KuCoinPosition, KuCoinOrder
except ImportError:
    # Fallback if import fails
    KuCoinService = None
    KuCoinMarketData = None
    KuCoinPosition = None
    KuCoinOrder = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="KuCoin Worker Service",
    description="Real-time market data and trading operations for KuCoin",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instance
kucoin_service = None
service_start_time = time.time()

# Pydantic models for API
class HealthResponse(BaseModel):
    status: str
    timestamp: float
    uptime: float
    service: str
    version: str

class MarketDataRequest(BaseModel):
    symbol: str
    timeframe: Optional[str] = "1m"

class TradingRequest(BaseModel):
    symbol: str
    side: str  # buy, sell
    order_type: str  # market, limit
    size: float
    price: Optional[float] = None

class PositionRequest(BaseModel):
    symbol: str

@app.on_event("startup")
async def startup_event():
    """Initialize the KuCoin service on startup"""
    global kucoin_service
    try:
        if KuCoinService:
            kucoin_service = KuCoinService()
            logger.info("✅ KuCoin service initialized successfully")
        else:
            logger.warning("⚠️ KuCoin service not available - using mock data")
    except Exception as e:
        logger.error(f"❌ Failed to initialize KuCoin service: {e}")
        logger.info("🔄 Using mock data mode")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - service_start_time
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        uptime=uptime,
        service="kucoin-worker",
        version="1.0.0"
    )

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if service is ready
        if kucoin_service:
            # Basic connectivity check
            return {"status": "ready", "service": "kucoin-worker"}
        else:
            # Mock mode is always ready
            return {"status": "ready", "service": "kucoin-worker", "mode": "mock"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/metrics")
async def get_metrics():
    """Metrics endpoint for monitoring"""
    uptime = time.time() - service_start_time
    return {
        "service": "kucoin-worker",
        "uptime_seconds": uptime,
        "status": "running",
        "timestamp": time.time()
    }

@app.get("/api/v1/market-data/{symbol}")
async def get_market_data(symbol: str, timeframe: str = "1m"):
    """Get real-time market data for a symbol"""
    try:
        if kucoin_service:
            # Use real KuCoin service
            market_data = await kucoin_service.get_market_data(symbol, timeframe)
            return {
                "success": True,
                "data": market_data,
                "source": "kucoin-api"
            }
        else:
            # Mock data
            mock_data = {
                "symbol": symbol,
                "price": 50000.0 + (hash(symbol) % 10000),
                "volume_24h": 1000000.0,
                "change_24h": 2.5,
                "high_24h": 52000.0,
                "low_24h": 48000.0,
                "timestamp": time.time()
            }
            return {
                "success": True,
                "data": mock_data,
                "source": "mock-data"
            }
    except Exception as e:
        logger.error(f"Error getting market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get market data: {str(e)}")

@app.get("/api/v1/positions")
async def get_positions():
    """Get current trading positions"""
    try:
        if kucoin_service:
            # Use real KuCoin service
            positions = await kucoin_service.get_positions()
            return {
                "success": True,
                "data": positions,
                "source": "kucoin-api"
            }
        else:
            # Mock positions
            mock_positions = [
                {
                    "symbol": "XBTUSDTM",
                    "side": "long",
                    "size": 0.1,
                    "entry_price": 50000.0,
                    "current_price": 51000.0,
                    "unrealized_pnl": 100.0,
                    "realized_pnl": 0.0,
                    "margin_type": "isolated",
                    "leverage": 20,
                    "liquidation_price": 47500.0,
                    "timestamp": time.time()
                }
            ]
            return {
                "success": True,
                "data": mock_positions,
                "source": "mock-data"
            }
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get positions: {str(e)}")

@app.post("/api/v1/orders")
async def create_order(request: TradingRequest):
    """Create a new trading order"""
    try:
        if kucoin_service:
            # Use real KuCoin service
            order = await kucoin_service.create_order(
                symbol=request.symbol,
                side=request.side,
                order_type=request.order_type,
                size=request.size,
                price=request.price
            )
            return {
                "success": True,
                "data": order,
                "source": "kucoin-api"
            }
        else:
            # Mock order
            mock_order = {
                "id": f"mock_order_{int(time.time())}",
                "symbol": request.symbol,
                "side": request.side,
                "type": request.order_type,
                "size": request.size,
                "price": request.price or 50000.0,
                "status": "pending",
                "timestamp": time.time()
            }
            return {
                "success": True,
                "data": mock_order,
                "source": "mock-data"
            }
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@app.get("/api/v1/account")
async def get_account_info():
    """Get account information"""
    try:
        if kucoin_service:
            # Use real KuCoin service
            account = await kucoin_service.get_account_info()
            return {
                "success": True,
                "data": account,
                "source": "kucoin-api"
            }
        else:
            # Mock account info
            mock_account = {
                "account_id": "mock_account_123",
                "currency": "USDT",
                "balance": 10000.0,
                "available": 9500.0,
                "holds": 500.0,
                "timestamp": time.time()
            }
            return {
                "success": True,
                "data": mock_account,
                "source": "mock-data"
            }
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get account info: {str(e)}")

@app.get("/api/v1/symbols")
async def get_available_symbols():
    """Get list of available trading symbols"""
    try:
        if kucoin_service:
            # Use real KuCoin service
            symbols = await kucoin_service.get_available_symbols()
            return {
                "success": True,
                "data": symbols,
                "source": "kucoin-api"
            }
        else:
            # Mock symbols
            mock_symbols = [
                "XBTUSDTM",
                "ETHUSDTM",
                "AVAXUSDTM",
                "SOLUSDTM",
                "DOGEUSDTM",
                "XRPUSDTM"
            ]
            return {
                "success": True,
                "data": mock_symbols,
                "source": "mock-data"
            }
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbols: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "KuCoin Worker Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "metrics": "/metrics",
            "market_data": "/api/v1/market-data/{symbol}",
            "positions": "/api/v1/positions",
            "orders": "/api/v1/orders",
            "account": "/api/v1/account",
            "symbols": "/api/v1/symbols"
        }
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="KuCoin Worker Service")
    parser.add_argument("--port", type=int, default=8302, help="Port to run the service on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    logger.info(f"🚀 Starting KuCoin Worker Service on {args.host}:{args.port}")
    
    uvicorn.run(
        "kucoin_server:app",
        host=args.host,
        port=args.port,
        reload=args.debug,
        log_level="info" if not args.debug else "debug"
    )
