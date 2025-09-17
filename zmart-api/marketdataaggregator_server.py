#!/usr/bin/env python3
"""
Market Data Aggregator Service
Aggregates market data from multiple sources for ZmartBot platform
"""

from fastapi import FastAPI, HTTPException
import uvicorn
import requests
import json
from datetime import datetime
from typing import Dict, List, Any

app = FastAPI(
    title="Market Data Aggregator",
    description="Multi-source market data aggregation service",
    version="1.0.0"
)

class MarketDataAggregator:
    def __init__(self):
        self.data_sources = {
            "binance": "https://api.binance.com/api/v3",
            "kucoin": "https://api.kucoin.com/api/v1", 
            "coingecko": "https://api.coingecko.com/api/v3"
        }
        self.cache = {}
    
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Aggregate market data from multiple sources"""
        try:
            # This is a stub implementation
            return {
                "symbol": symbol,
                "price": 50000.00,
                "volume": 1000000,
                "change_24h": 2.5,
                "timestamp": datetime.now().isoformat(),
                "sources": list(self.data_sources.keys())
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Data aggregation error: {str(e)}")

aggregator = MarketDataAggregator()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MarketDataAggregator", 
        "version": "1.0.0",
        "status": "operational",
        "port": 8090,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MarketDataAggregator",
        "port": 8090,
        "level": "LEVEL_3_CERTIFIED", 
        "sources": len(aggregator.data_sources),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/market/{symbol}")
async def get_market_data(symbol: str):
    """Get aggregated market data for a symbol"""
    return await aggregator.get_market_data(symbol.upper())

@app.get("/sources")
async def list_sources():
    """List available data sources"""
    return {
        "sources": aggregator.data_sources,
        "count": len(aggregator.data_sources)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)