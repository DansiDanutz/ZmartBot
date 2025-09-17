#!/usr/bin/env python3
"""
MySymbols Internal API Service - FastAPI Server
Provides internal symbol management and portfolio data access
"""

import asyncio
import logging
import sys
import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import json
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="MySymbols Internal API Service",
    description="Internal API service for managing trading symbols and portfolio data",
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

# Global variables
service_start_time = time.time()
db_path = project_root / "my_symbols_v2.db"

# Pydantic models for API
class HealthResponse(BaseModel):
    status: str
    timestamp: float
    uptime: float
    service: str
    version: str

class SymbolData(BaseModel):
    symbol: str
    name: Optional[str] = None
    exchange: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class PortfolioData(BaseModel):
    symbol: str
    quantity: float
    avg_price: float
    current_price: Optional[float] = None
    total_value: Optional[float] = None
    pnl: Optional[float] = None
    last_updated: Optional[str] = None

class SymbolRequest(BaseModel):
    symbol: str
    name: Optional[str] = None
    exchange: Optional[str] = None
    type: Optional[str] = None

def get_db_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def init_database():
    """Initialize database tables if they don't exist"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create symbols table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT,
                exchange TEXT,
                type TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create portfolio table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                avg_price REAL NOT NULL,
                current_price REAL,
                total_value REAL,
                pnl REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES symbols (symbol)
            )
        """)
        
        conn.commit()
        logger.info("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False
    finally:
        conn.close()

@app.on_event("startup")
async def startup_event():
    """Initialize the service on startup"""
    logger.info("🚀 Starting MySymbols Internal API Service")
    
    # Initialize database
    if not init_database():
        logger.error("❌ Failed to initialize database")
    else:
        logger.info("✅ Database initialized successfully")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - service_start_time
    
    # Check database connectivity
    db_healthy = get_db_connection() is not None
    
    return HealthResponse(
        status="healthy" if db_healthy else "unhealthy",
        timestamp=time.time(),
        uptime=uptime,
        service="mysymbols-internal-api",
        version="1.0.0"
    )

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check database connectivity
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Test database query
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        conn.close()
        
        if table_count > 0:
            return {"status": "ready", "service": "mysymbols-internal-api", "database": "connected"}
        else:
            return {"status": "not_ready", "service": "mysymbols-internal-api", "database": "no_tables"}
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/metrics")
async def get_metrics():
    """Metrics endpoint for monitoring"""
    uptime = time.time() - service_start_time
    
    # Get database metrics
    conn = get_db_connection()
    symbol_count = 0
    portfolio_count = 0
    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM symbols")
            symbol_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM portfolio")
            portfolio_count = cursor.fetchone()[0]
        except:
            pass
        finally:
            conn.close()
    
    return {
        "service": "mysymbols-internal-api",
        "uptime_seconds": uptime,
        "status": "running",
        "timestamp": time.time(),
        "database": {
            "symbols_count": symbol_count,
            "portfolio_count": portfolio_count
        }
    }

@app.get("/api/v1/symbols", response_model=List[SymbolData])
async def get_symbols():
    """Get all symbols"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM symbols ORDER BY symbol")
        rows = cursor.fetchall()
        conn.close()
        
        symbols = []
        for row in rows:
            symbols.append(SymbolData(
                symbol=row['symbol'],
                name=row['name'],
                exchange=row['exchange'],
                type=row['type'],
                status=row['status'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ))
        
        return symbols
        
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbols: {str(e)}")

@app.get("/api/v1/symbols/{symbol}", response_model=SymbolData)
async def get_symbol(symbol: str):
    """Get specific symbol"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM symbols WHERE symbol = ?", (symbol,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Symbol not found")
        
        return SymbolData(
            symbol=row['symbol'],
            name=row['name'],
            exchange=row['exchange'],
            type=row['type'],
            status=row['status'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting symbol {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbol: {str(e)}")

@app.post("/api/v1/symbols", response_model=SymbolData)
async def create_symbol(symbol_data: SymbolRequest):
    """Create a new symbol"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO symbols (symbol, name, exchange, type, status)
            VALUES (?, ?, ?, ?, 'active')
        """, (symbol_data.symbol, symbol_data.name, symbol_data.exchange, symbol_data.type))
        
        conn.commit()
        conn.close()
        
        return SymbolData(
            symbol=symbol_data.symbol,
            name=symbol_data.name,
            exchange=symbol_data.exchange,
            type=symbol_data.type,
            status="active",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Symbol already exists")
    except Exception as e:
        logger.error(f"Error creating symbol: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create symbol: {str(e)}")

@app.get("/api/v1/portfolio", response_model=List[PortfolioData])
async def get_portfolio():
    """Get portfolio data"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, s.name as symbol_name 
            FROM portfolio p 
            LEFT JOIN symbols s ON p.symbol = s.symbol 
            ORDER BY p.symbol
        """)
        rows = cursor.fetchall()
        conn.close()
        
        portfolio = []
        for row in rows:
            portfolio.append(PortfolioData(
                symbol=row['symbol'],
                quantity=row['quantity'],
                avg_price=row['avg_price'],
                current_price=row['current_price'],
                total_value=row['total_value'],
                pnl=row['pnl'],
                last_updated=row['last_updated']
            ))
        
        return portfolio
        
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio: {str(e)}")

@app.get("/api/v1/symbols/count")
async def get_symbol_count():
    """Get total number of symbols"""
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM symbols")
        count = cursor.fetchone()[0]
        conn.close()
        
        return {"count": count, "service": "mysymbols-internal-api"}
        
    except Exception as e:
        logger.error(f"Error getting symbol count: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbol count: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "MySymbols Internal API Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "metrics": "/metrics",
            "symbols": "/api/v1/symbols",
            "symbol": "/api/v1/symbols/{symbol}",
            "portfolio": "/api/v1/portfolio",
            "symbol_count": "/api/v1/symbols/count"
        }
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MySymbols Internal API Service")
    parser.add_argument("--port", type=int, default=8201, help="Port to run the service on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    logger.info(f"🚀 Starting MySymbols Internal API Service on {args.host}:{args.port}")
    
    uvicorn.run(
        "mysymbols_server:app",
        host=args.host,
        port=args.port,
        reload=args.debug,
        log_level="info" if not args.debug else "debug"
    )
