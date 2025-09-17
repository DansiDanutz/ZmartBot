#!/usr/bin/env python3
"""
ZmartBot Notification Service
Provides alerts and notifications
"""

import os
import sys
import logging
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
    title="ZmartBot Notification Service",
    description="Alerts and notifications service",
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
    "name": "zmart-notification",
    "version": "1.0.0",
    "port": 8008,
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
        "service": "zmart-notification",
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
            "service": "zmart-notification",
            "dependencies": {
                "database": db_status
            }
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

# Alerts Endpoints
@app.get("/api/alerts")
async def get_alerts():
    """Get all alerts"""
    try:
        # Generate sample alerts based on symbols
        conn = get_database_connection()
        symbols = []
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT symbol, exchange FROM my_symbols WHERE status = 'active' LIMIT 10")
            symbols = [row[0] for row in cursor.fetchall()]
            conn.close()
        
        if not symbols:
            symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT"]
        
        alerts = []
        alert_id = 1
        
        for symbol in symbols:
            # Generate different types of alerts
            alert_types = [
                {
                    "type": "liquidation",
                    "message": f"Large liquidation cluster detected for {symbol}",
                    "severity": "high"
                },
                {
                    "type": "technical",
                    "message": f"RSI oversold condition for {symbol}",
                    "severity": "medium"
                },
                {
                    "type": "price_alert",
                    "message": f"Price breakout detected for {symbol}",
                    "severity": "medium"
                },
                {
                    "type": "volume_alert",
                    "message": f"Unusual volume spike for {symbol}",
                    "severity": "low"
                }
            ]
            
            for alert_type in alert_types:
                alerts.append({
                    "id": alert_id,
                    "symbol": symbol,
                    "type": alert_type["type"],
                    "message": alert_type["message"],
                    "severity": alert_type["severity"],
                    "timestamp": (datetime.utcnow() - timedelta(minutes=alert_id * 5)).isoformat(),
                    "status": "active"
                })
                alert_id += 1
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "active_alerts": len(alerts),
            "severity_breakdown": {
                "high": len([a for a in alerts if a["severity"] == "high"]),
                "medium": len([a for a in alerts if a["severity"] == "medium"]),
                "low": len([a for a in alerts if a["severity"] == "low"])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alerts")

@app.get("/api/alerts/{symbol}")
async def get_alerts_for_symbol(symbol: str):
    """Get alerts for a specific symbol"""
    try:
        # Generate alerts for specific symbol
        alerts = []
        alert_id = 1
        
        # Generate different types of alerts for the symbol
        alert_types = [
            {
                "type": "liquidation",
                "message": f"Large liquidation cluster detected for {symbol}",
                "severity": "high"
            },
            {
                "type": "technical",
                "message": f"RSI oversold condition for {symbol}",
                "severity": "medium"
            },
            {
                "type": "price_alert",
                "message": f"Price breakout detected for {symbol}",
                "severity": "medium"
            },
            {
                "type": "volume_alert",
                "message": f"Unusual volume spike for {symbol}",
                "severity": "low"
            }
        ]
        
        for alert_type in alert_types:
            alerts.append({
                "id": alert_id,
                "symbol": symbol,
                "type": alert_type["type"],
                "message": alert_type["message"],
                "severity": alert_type["severity"],
                "timestamp": (datetime.utcnow() - timedelta(minutes=alert_id * 5)).isoformat(),
                "status": "active"
            })
            alert_id += 1
        
        return {
            "symbol": symbol,
            "alerts": alerts,
            "total_alerts": len(alerts),
            "active_alerts": len(alerts),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting alerts for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get alerts for {symbol}")

@app.get("/api/alerts/live")
async def get_live_alerts():
    """Get live alerts (real-time)"""
    try:
        # Generate live alerts
        live_alerts = []
        alert_id = 1
        
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT"]
        
        for symbol in symbols:
            # Generate live alerts
            live_alerts.append({
                "id": alert_id,
                "symbol": symbol,
                "type": "live_price",
                "message": f"Live price update for {symbol}",
                "severity": "info",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "active",
                "data": {
                    "price": 67000.0 + (hash(symbol) % 1000),
                    "change_24h": (hash(symbol) % 200 - 100) / 100,
                    "volume": 1000000 + (hash(symbol) % 500000)
                }
            })
            alert_id += 1
        
        return {
            "live_alerts": live_alerts,
            "total_active": len(live_alerts),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting live alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get live alerts")

@app.get("/api/notifications")
async def get_notifications():
    """Get all notifications"""
    try:
        notifications = [
            {
                "id": 1,
                "type": "system",
                "title": "System Update",
                "message": "ZmartBot system updated to version 2.0.0",
                "severity": "info",
                "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "read": False
            },
            {
                "id": 2,
                "type": "trading",
                "title": "New Trading Signal",
                "message": "Strong bullish signal detected for BTCUSDT",
                "severity": "medium",
                "timestamp": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                "read": False
            },
            {
                "id": 3,
                "type": "alert",
                "title": "Alert Triggered",
                "message": "RSI oversold condition for ETHUSDT",
                "severity": "high",
                "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                "read": True
            }
        ]
        
        return {
            "notifications": notifications,
            "total_notifications": len(notifications),
            "unread_count": len([n for n in notifications if not n["read"]]),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notifications")

@app.get("/api/notifications/unread")
async def get_unread_notifications():
    """Get unread notifications"""
    try:
        notifications = await get_notifications()
        unread = [n for n in notifications["notifications"] if not n["read"]]
        
        return {
            "notifications": unread,
            "total_unread": len(unread),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting unread notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to get unread notifications")

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
    
    parser = argparse.ArgumentParser(description="ZmartBot Notification Service")
    parser.add_argument("--port", type=int, default=8008, help="Port to run the service on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to run the service on")
    
    args = parser.parse_args()
    
    logger.info(f"Starting ZmartBot Notification Service on {args.host}:{args.port}")
    
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
