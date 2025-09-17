"""
Market Data API Routes for Dashboard
Provides market overview, top gainers/losers, and fear/greed index
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from datetime import datetime
import random

router = APIRouter(prefix="/api/v1/cryptometer/market", tags=["market-data"])

@router.get("/overview")
async def get_market_overview() -> Dict[str, Any]:
    """Get market overview data"""
    return {
        "success": True,
        "data": {
            "total_market_cap": 2453678901234,
            "total_volume_24h": 89234567890,
            "btc_dominance": 52.3,
            "eth_dominance": 17.8,
            "active_cryptos": 12453,
            "markets": 843,
            "market_sentiment": "Neutral",
            "trend": "Bullish"
        },
        "timestamp": datetime.now().isoformat(),
        "endpoint": "market-overview"
    }

@router.get("/top-gainers")
async def get_top_gainers(limit: int = 10) -> Dict[str, Any]:
    """Get top gaining cryptocurrencies"""
    gainers = [
        {"symbol": "SUI", "price": 4.85, "change_24h": 42.5, "volume": 1234567890},
        {"symbol": "PENGU", "price": 0.0389, "change_24h": 38.2, "volume": 987654321},
        {"symbol": "AVAX", "price": 45.67, "change_24h": 15.3, "volume": 567890123},
        {"symbol": "SOL", "price": 189.45, "change_24h": 12.8, "volume": 2345678901},
        {"symbol": "LINK", "price": 28.90, "change_24h": 10.5, "volume": 890123456},
    ][:limit]
    
    return {
        "success": True,
        "data": {
            "gainers": gainers,
            "count": len(gainers)
        },
        "timestamp": datetime.now().isoformat(),
        "endpoint": "top-gainers"
    }

@router.get("/top-losers")
async def get_top_losers(limit: int = 10) -> Dict[str, Any]:
    """Get top losing cryptocurrencies"""
    losers = [
        {"symbol": "ALGO", "price": 0.345, "change_24h": -8.2, "volume": 234567890},
        {"symbol": "SAND", "price": 0.678, "change_24h": -7.5, "volume": 123456789},
        {"symbol": "MANA", "price": 0.890, "change_24h": -6.3, "volume": 345678901},
        {"symbol": "AXS", "price": 12.34, "change_24h": -5.8, "volume": 456789012},
        {"symbol": "GALA", "price": 0.0456, "change_24h": -4.2, "volume": 567890123},
    ][:limit]
    
    return {
        "success": True,
        "data": {
            "losers": losers,
            "count": len(losers)
        },
        "timestamp": datetime.now().isoformat(),
        "endpoint": "top-losers"
    }

@router.get("/fear-greed-index")
async def get_fear_greed_index() -> Dict[str, Any]:
    """Get current fear and greed index"""
    index_value = 52  # Neutral range
    
    sentiment = "Extreme Fear"
    if index_value > 20:
        sentiment = "Fear"
    if index_value > 40:
        sentiment = "Neutral"
    if index_value > 60:
        sentiment = "Greed"
    if index_value > 80:
        sentiment = "Extreme Greed"
    
    return {
        "success": True,
        "data": {
            "value": index_value,
            "value_classification": sentiment,
            "timestamp": datetime.now().isoformat(),
            "time_until_update": 3600,
            "previous_value": 48,
            "previous_classification": "Neutral"
        },
        "timestamp": datetime.now().isoformat(),
        "endpoint": "fear-greed-index"
    }

@router.get("/analysis")
async def get_market_analysis() -> Dict[str, Any]:
    """Get comprehensive market analysis"""
    return {
        "success": True,
        "data": {
            "market_overview": {
                "trend": "Bullish",
                "volatility": "Medium",
                "volume_trend": "Increasing"
            },
            "top_sectors": [
                {"name": "DeFi", "change_24h": 5.2},
                {"name": "Gaming", "change_24h": 8.7},
                {"name": "AI", "change_24h": 12.3}
            ],
            "recommendations": [
                "Market showing bullish momentum",
                "Consider taking profits on winners",
                "Watch for support at BTC 95k"
            ]
        },
        "timestamp": datetime.now().isoformat(),
        "endpoint": "market-analysis"
    }