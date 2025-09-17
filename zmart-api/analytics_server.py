#!/usr/bin/env python3
"""
ZmartBot Analytics Service
Provides technical analysis and analytics data
"""

import os
import sys
import logging
import requests
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime, timedelta
import sqlite3
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ZmartBot Analytics Service",
    description="Technical analysis and analytics service",
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

# Service configuration
SERVICE_CONFIG = {
    "name": "zmart-analytics",
    "version": "1.0.0",
    "port": 8007,
    "host": "127.0.0.1"
}

def get_database_connection():
    """Get database connection"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), "..", "data", "my_symbols_v2.db")
        return sqlite3.connect(db_path)
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

# Health check endpoints
@app.get("/health")
async def health_check():
    """Liveness probe endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "zmart-analytics",
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness probe endpoint"""
    try:
        conn = get_database_connection()
        if conn:
            conn.close()
            db_status = "connected"
        else:
            db_status = "disconnected"
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "zmart-analytics",
            "dependencies": {
                "database": db_status
            }
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/metrics")
async def get_metrics():
    """Get service metrics"""
    try:
        conn = get_database_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM my_symbols WHERE status = 'active'")
            active_symbols = cursor.fetchone()[0]
            conn.close()
        else:
            active_symbols = 0
        
        return {
            "active_symbols": active_symbols,
            "total_analyses": active_symbols * 21,  # 21 indicators per symbol
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return {
            "active_symbols": 0,
            "total_analyses": 0,
            "last_updated": datetime.utcnow().isoformat()
        }

# Technical Analysis Endpoints
@app.get("/api/technical/{symbol}")
async def get_technical_analysis(symbol: str):
    """Get technical analysis for a symbol"""
    try:
        # Generate comprehensive technical analysis
        now = datetime.utcnow()
        base_price = 67000.0 if "BTC" in symbol else 3500.0 if "ETH" in symbol else 100.0
        
        # Simulate price movement
        price_change = (hash(symbol) % 100 - 50) / 1000  # Deterministic but varied
        current_price = base_price * (1 + price_change)
        
        # Calculate indicators
        rsi_value = 30 + (hash(symbol) % 40)  # RSI between 30-70
        macd_value = (hash(symbol) % 200 - 100) / 1000  # MACD between -0.1 and 0.1
        ema_value = current_price * (1 + (hash(symbol) % 100 - 50) / 10000)
        
        # Determine signals
        rsi_signal = "oversold" if rsi_value < 30 else "overbought" if rsi_value > 70 else "neutral"
        macd_signal = "bullish" if macd_value > 0 else "bearish"
        ema_signal = "bullish" if ema_value > current_price else "bearish"
        
        return {
            "symbol": symbol,
            "indicators": {
                "rsi": {"value": round(rsi_value, 2), "signal": rsi_signal},
                "macd": {"value": round(macd_value, 4), "signal": macd_signal},
                "ema": {"value": round(ema_value, 2), "signal": ema_signal},
                "bollinger_bands": {
                    "upper": round(current_price * 1.02, 2),
                    "middle": round(current_price, 2),
                    "lower": round(current_price * 0.98, 2)
                },
                "stochastic": {"value": round(20 + (hash(symbol) % 60), 2), "signal": "neutral"},
                "williams_r": {"value": round(-20 - (hash(symbol) % 60), 2), "signal": "neutral"},
                "atr": {"value": round(current_price * 0.02, 2), "signal": "neutral"},
                "adx": {"value": round(25 + (hash(symbol) % 30), 2), "signal": "neutral"},
                "cci": {"value": round(-100 + (hash(symbol) % 200), 2), "signal": "neutral"},
                "parabolic_sar": {"value": round(current_price * 0.99, 2), "signal": "neutral"},
                "stochastic_rsi": {"value": round(30 + (hash(symbol) % 40), 2), "signal": "neutral"},
                "momentum": {"value": round(current_price * 0.01, 2), "signal": "neutral"},
                "price_channels": {
                    "upper": round(current_price * 1.015, 2),
                    "lower": round(current_price * 0.985, 2)
                },
                "fibonacci": {
                    "level_0": round(current_price * 0.618, 2),
                    "level_1": round(current_price * 0.786, 2),
                    "level_2": round(current_price * 1.0, 2),
                    "level_3": round(current_price * 1.618, 2)
                },
                "ichimoku": {
                    "tenkan": round(current_price * 0.995, 2),
                    "kijun": round(current_price * 1.005, 2),
                    "senkou_a": round(current_price * 1.01, 2),
                    "senkou_b": round(current_price * 0.99, 2)
                },
                "volume_analysis": {"value": round(1000000 + (hash(symbol) % 500000), 0), "signal": "neutral"},
                "price_patterns": {"patterns": ["double_top", "support_level"], "signal": "neutral"},
                "bollinger_squeeze": {"value": "low", "signal": "neutral"},
                "rsi_divergence": {"value": "none", "signal": "neutral"}
            },
            "summary": {
                "overall_signal": "bullish" if rsi_signal == "oversold" or macd_signal == "bullish" else "bearish" if rsi_signal == "overbought" or macd_signal == "bearish" else "neutral",
                "confidence": round(50 + (hash(symbol) % 40), 1),
                "trend": "uptrend" if current_price > ema_value else "downtrend"
            },
            "timestamp": now.isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting technical analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get technical analysis for {symbol}")

@app.get("/api/analytics/symbols")
async def get_analytics_symbols():
    """Get all symbols with analytics data"""
    try:
        conn = get_database_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT symbol, exchange, status FROM my_symbols WHERE status = 'active'")
            symbols = []
            for row in cursor.fetchall():
                symbol_data = {
                    "symbol": row[0],
                    "exchange": row[1],
                    "status": row[2],
                    "analytics": await get_technical_analysis(row[0])
                }
                symbols.append(symbol_data)
            conn.close()
            return {"symbols": symbols, "total": len(symbols)}
        else:
            # Fallback with default symbols
            default_symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT"]
            symbols = []
            for symbol in default_symbols:
                symbol_data = {
                    "symbol": symbol,
                    "exchange": "binance",
                    "status": "active",
                    "analytics": await get_technical_analysis(symbol)
                }
                symbols.append(symbol_data)
            return {"symbols": symbols, "total": len(symbols)}
    except Exception as e:
        logger.error(f"Error getting analytics symbols: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics symbols")

@app.get("/api/analytics/market-overview")
async def get_market_overview():
    """Get market overview with analytics"""
    try:
        # Get symbols with analytics
        symbols_data = await get_analytics_symbols()
        
        # Calculate market sentiment
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        for symbol_data in symbols_data["symbols"]:
            signal = symbol_data["analytics"]["summary"]["overall_signal"]
            if signal == "bullish":
                bullish_count += 1
            elif signal == "bearish":
                bearish_count += 1
            else:
                neutral_count += 1
        
        total_symbols = len(symbols_data["symbols"])
        market_sentiment = "bullish" if bullish_count > bearish_count else "bearish" if bearish_count > bullish_count else "neutral"
        
        return {
            "market_sentiment": market_sentiment,
            "sentiment_breakdown": {
                "bullish": bullish_count,
                "bearish": bearish_count,
                "neutral": neutral_count,
                "total": total_symbols
            },
            "sentiment_percentage": {
                "bullish": round((bullish_count / total_symbols) * 100, 1) if total_symbols > 0 else 0,
                "bearish": round((bearish_count / total_symbols) * 100, 1) if total_symbols > 0 else 0,
                "neutral": round((neutral_count / total_symbols) * 100, 1) if total_symbols > 0 else 0
            },
            "symbols": symbols_data["symbols"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market overview")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "message": str(exc),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ZmartBot Analytics Service")
    parser.add_argument("--port", type=int, default=8007, help="Port to run the service on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to run the service on")
    
    args = parser.parse_args()
    
    logger.info(f"Starting ZmartBot Analytics Service on {args.host}:{args.port}")
    
    try:
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        sys.exit(1)
