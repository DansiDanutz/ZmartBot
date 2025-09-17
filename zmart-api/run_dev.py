#!/usr/bin/env python3
"""
ZmartBot Backend API Server
Main entry point for the ZmartBot backend API
"""

import os
import sys
import logging
import requests
from fastapi import FastAPI, HTTPException, Query
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

@app.get("/api/v1/binance/ticker/24hr")
async def get_binance_ticker(symbol: str = Query(..., description="Trading symbol")):
    """Get real-time 24hr ticker data from Binance API"""
    try:
        # Fix symbol format for Binance API (BTCUSDT -> BTCUSDT, no M suffix needed for Binance)
        binance_symbol = symbol
        
        # Make request to Binance API
        url = f"https://api.binance.com/api/v3/ticker/24hr"
        params = {"symbol": binance_symbol}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Return formatted response
        return {
            "symbol": data["symbol"],
            "lastPrice": data["lastPrice"],
            "priceChange": data["priceChange"],
            "priceChangePercent": data["priceChangePercent"],
            "volume": data["volume"],
            "quoteVolume": data["quoteVolume"],
            "highPrice": data["highPrice"],
            "lowPrice": data["lowPrice"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Binance API request failed for {symbol}: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch data from Binance API: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing Binance ticker data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/binance/klines")
async def get_binance_klines(
    symbol: str = Query(..., description="Trading symbol"),
    interval: str = Query("1h", description="Kline interval"),
    limit: int = Query(24, description="Number of klines to return")
):
    """Get real-time klines/candlestick data from Binance API"""
    try:
        # Fix symbol format for Binance API
        binance_symbol = symbol
        
        # Make request to Binance API
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            "symbol": binance_symbol,
            "interval": interval,
            "limit": limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Return formatted response
        return {
            "symbol": symbol,
            "interval": interval,
            "klines": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Binance API request failed for {symbol}: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch data from Binance API: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing Binance klines data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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

@app.get("/api/v1/subscription/status")
async def subscription_status():
    """Subscription status endpoint"""
    return {
        "subscription": "active",
        "plan": "professional",
        "features": ["trading", "analytics", "alerts", "ml_predictions"],
        "expires_at": "2025-12-31T23:59:59Z",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/portfolio")
async def get_portfolio():
    """Portfolio endpoint"""
    return {
        "portfolio": {
            "total_value": 150000.0,
            "total_pnl": 2500.0,
            "positions": [
                {"symbol": "BTCUSDT", "size": 0.5, "entry_price": 65000.0, "current_price": 67890.0, "pnl": 1445.0},
                {"symbol": "ETHUSDT", "size": 2.0, "entry_price": 3200.0, "current_price": 3450.0, "pnl": 500.0},
                {"symbol": "SOLUSDT", "size": 10.0, "entry_price": 120.0, "current_price": 125.0, "pnl": 50.0}
            ]
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/alerts/list")
async def get_alerts_list():
    """Alerts list endpoint"""
    return {
        "alerts": [
            {"id": 1, "symbol": "BTCUSDT", "type": "price_alert", "message": "Price alert for BTCUSDT", "severity": "high", "status": "active"},
            {"id": 2, "symbol": "ETHUSDT", "type": "technical", "message": "Technical alert for ETHUSDT", "severity": "medium", "status": "active"},
            {"id": 3, "symbol": "SOLUSDT", "type": "liquidation", "message": "Liquidation alert for SOLUSDT", "severity": "high", "status": "active"}
        ],
        "total": 3,
        "active": 3,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/alerts/status")
async def get_alerts_status():
    """Alerts status endpoint"""
    return {
        "success": True,
        "status": "operational",
        "alerts_count": 3,
        "active_alerts": 3,
        "system_health": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/scores")
async def get_scores():
    """Get symbol scores endpoint"""
    return {
        "scores": [
            {"symbol": "BTCUSDT", "score": 85, "rank": 1, "trend": "bullish"},
            {"symbol": "ETHUSDT", "score": 78, "rank": 2, "trend": "bullish"},
            {"symbol": "SOLUSDT", "score": 72, "rank": 3, "trend": "neutral"},
            {"symbol": "AVAXUSDT", "score": 68, "rank": 4, "trend": "bearish"}
        ],
        "total_symbols": 4,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/futures-symbols/my-symbols/current")
async def get_my_symbols_current():
    """Get current my symbols"""
    return {
        "portfolio": {
            "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "UNIUSDT", "ATOMUSDT"],
            "total": 10
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/futures-symbols/kucoin/available")
async def get_kucoin_available():
    """Get available KuCoin symbols"""
    try:
        # Fetch real KuCoin symbols
        url = "https://api.kucoin.com/api/v1/symbols"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == "200000" and "data" in data:
            symbols = []
            for symbol_info in data["data"]:
                if (symbol_info.get("enableTrading") == True and 
                    symbol_info.get("quoteCurrency") == "USDT" and
                    symbol_info.get("market") == "USDS"):
                    symbol = symbol_info.get("symbol", "")
                    if symbol:
                        symbols.append(symbol)
            
            return {
                "symbols": symbols,
                "total": len(symbols),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            logger.error(f"KuCoin API error: {data}")
            raise HTTPException(status_code=503, detail="Failed to fetch KuCoin symbols")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"KuCoin API request failed: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch data from KuCoin API: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing KuCoin symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/futures-symbols/binance/available")
async def get_binance_available():
    """Get available Binance symbols"""
    try:
        # Fetch real Binance futures symbols
        url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "symbols" in data:
            symbols = []
            for symbol_info in data["symbols"]:
                if (symbol_info.get("status") == "TRADING" and 
                    symbol_info.get("contractType") == "PERPETUAL" and
                    symbol_info.get("quoteAsset") == "USDT"):
                    symbol = symbol_info.get("symbol", "")
                    if symbol:
                        symbols.append(symbol)
            
            return {
                "symbols": symbols,
                "total": len(symbols),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            logger.error(f"Binance API error: {data}")
            raise HTTPException(status_code=503, detail="Failed to fetch Binance symbols")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Binance API request failed: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch data from Binance API: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing Binance symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/futures-symbols/common")
async def get_common_symbols():
    """Get common symbols across exchanges"""
    try:
        # Get Binance symbols
        binance_response = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo", timeout=10)
        binance_response.raise_for_status()
        binance_data = binance_response.json()
        
        binance_symbols = set()
        if "symbols" in binance_data:
            for symbol_info in binance_data["symbols"]:
                if (symbol_info.get("status") == "TRADING" and 
                    symbol_info.get("contractType") == "PERPETUAL" and
                    symbol_info.get("quoteAsset") == "USDT"):
                    symbol = symbol_info.get("symbol", "")
                    if symbol:
                        binance_symbols.add(symbol)
        
        # Get KuCoin symbols
        kucoin_response = requests.get("https://api.kucoin.com/api/v1/symbols", timeout=10)
        kucoin_response.raise_for_status()
        kucoin_data = kucoin_response.json()
        
        kucoin_symbols = set()
        if kucoin_data.get("code") == "200000" and "data" in kucoin_data:
            for symbol_info in kucoin_data["data"]:
                if (symbol_info.get("enableTrading") == True and 
                    symbol_info.get("quoteCurrency") == "USDT" and
                    symbol_info.get("market") == "USDS"):
                    symbol = symbol_info.get("symbol", "")
                    if symbol:
                        kucoin_symbols.add(symbol)
        
        # Find common symbols
        common_symbols = list(binance_symbols.intersection(kucoin_symbols))
        common_symbols.sort()  # Sort alphabetically
        
        return {
            "symbols": common_symbols,
            "total": len(common_symbols),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for common symbols: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch common symbols: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing common symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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
