"""
Demo Real-Time Routes - Fallback when external APIs are unavailable
Provides realistic demo data for testing the Live Alerts Dashboard
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import random

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/demo-real-time", tags=["demo-real-time"])

# Demo price data with realistic values
DEMO_PRICES = {
    'BTCUSDT': 45100.0,
    'ETHUSDT': 2380.0,
    'SOLUSDT': 98.5,
    'BNBUSDT': 315.2,
    'XRPUSDT': 0.52,
    'ADAUSDT': 0.38,
    'AVAXUSDT': 24.7,
    'DOGEUSDT': 0.08,
    'DOTUSDT': 5.2,
    'LINKUSDT': 14.8
}

# Demo technical indicators
DEMO_TECHNICAL = {
    'BTCUSDT': {
        'rsi': 65.5,
        'rsi_14': 64.2,
        'macd': {'macd': 150.3, 'signal': 142.8, 'histogram': 7.5},
        'ema_9': 45200.0,
        'ema_21': 44850.0,
        'sma_20': 44900.0,
        'bollinger_upper': 46200.0,
        'bollinger_middle': 45100.0,
        'bollinger_lower': 44000.0,
        'trend_direction': 'bullish',
        'signal_strength': 75.0
    },
    'ETHUSDT': {
        'rsi': 58.2,
        'rsi_14': 57.8,
        'macd': {'macd': 12.5, 'signal': 10.8, 'histogram': 1.7},
        'ema_9': 2385.0,
        'ema_21': 2375.0,
        'sma_20': 2370.0,
        'bollinger_upper': 2420.0,
        'bollinger_middle': 2380.0,
        'bollinger_lower': 2340.0,
        'trend_direction': 'bullish',
        'signal_strength': 68.0
    },
    'SOLUSDT': {
        'rsi': 72.1,
        'rsi_14': 71.8,
        'macd': {'macd': 2.8, 'signal': 2.1, 'histogram': 0.7},
        'ema_9': 99.2,
        'ema_21': 97.8,
        'sma_20': 98.0,
        'bollinger_upper': 102.0,
        'bollinger_middle': 98.5,
        'bollinger_lower': 95.0,
        'trend_direction': 'bullish',
        'signal_strength': 82.0
    }
}

def get_price_with_variation(base_price: float) -> float:
    """Add realistic price variation (±0.5%)"""
    variation = random.uniform(-0.005, 0.005)
    return round(base_price * (1 + variation), 8)

def get_24h_change() -> float:
    """Generate realistic 24h change"""
    return round(random.uniform(-8.0, 12.0), 2)

@router.get("/prices")
async def get_demo_prices(symbols: List[str] = Query(..., description="List of symbols")):
    """
    Get demo real-time prices for multiple symbols
    Returns realistic but fake data for testing
    """
    try:
        result = {}
        
        for symbol in symbols:
            symbol = symbol.upper()
            
            if symbol in DEMO_PRICES:
                base_price = DEMO_PRICES[symbol]
                current_price = get_price_with_variation(base_price)
                change_24h = get_24h_change()
                
                result[symbol] = {
                    'symbol': symbol,
                    'price': current_price,
                    'change_24h': change_24h,
                    'change_percent_24h': round((change_24h / current_price) * 100, 2),
                    'volume_24h': random.randint(1000000, 50000000),
                    'high_24h': current_price * 1.05,
                    'low_24h': current_price * 0.95,
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'demo'
                }
            else:
                # Generate random price for unknown symbols
                random_price = random.uniform(0.1, 1000)
                result[symbol] = {
                    'symbol': symbol,
                    'price': round(random_price, 6),
                    'change_24h': get_24h_change(),
                    'change_percent_24h': round(random.uniform(-10, 10), 2),
                    'volume_24h': random.randint(100000, 10000000),
                    'high_24h': random_price * 1.05,
                    'low_24h': random_price * 0.95,
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'demo'
                }
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating demo prices: {e}")
        raise HTTPException(status_code=500, detail="Demo price generation failed")

@router.get("/technical/{symbol}")
async def get_demo_technical(symbol: str):
    """
    Get demo technical indicators for a symbol
    Returns realistic but fake technical data
    """
    try:
        symbol = symbol.upper()
        
        if symbol in DEMO_TECHNICAL:
            tech_data = DEMO_TECHNICAL[symbol].copy()
        else:
            # Generate random technical data for unknown symbols
            tech_data = {
                'rsi': round(random.uniform(20, 80), 1),
                'rsi_14': round(random.uniform(20, 80), 1),
                'macd': {
                    'macd': round(random.uniform(-50, 50), 2),
                    'signal': round(random.uniform(-50, 50), 2),
                    'histogram': round(random.uniform(-10, 10), 2)
                },
                'ema_9': round(DEMO_PRICES.get(symbol, 100) * random.uniform(0.95, 1.05), 2),
                'ema_21': round(DEMO_PRICES.get(symbol, 100) * random.uniform(0.90, 1.10), 2),
                'sma_20': round(DEMO_PRICES.get(symbol, 100) * random.uniform(0.92, 1.08), 2),
                'bollinger_upper': round(DEMO_PRICES.get(symbol, 100) * 1.08, 2),
                'bollinger_middle': round(DEMO_PRICES.get(symbol, 100), 2),
                'bollinger_lower': round(DEMO_PRICES.get(symbol, 100) * 0.92, 2),
                'trend_direction': random.choice(['bullish', 'bearish', 'neutral']),
                'signal_strength': round(random.uniform(30, 85), 1)
            }
        
        # Add small variations to make it look live
        tech_data['rsi'] += random.uniform(-2, 2)
        tech_data['rsi'] = max(0, min(100, tech_data['rsi']))
        tech_data['signal_strength'] += random.uniform(-5, 5)
        tech_data['signal_strength'] = max(0, min(100, tech_data['signal_strength']))
        
        return {
            'symbol': symbol,
            'timestamp': datetime.utcnow().isoformat(),
            'data': tech_data,
            'source': 'demo'
        }
        
    except Exception as e:
        logger.error(f"Error generating demo technical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Demo technical data generation failed")

@router.get("/health")
async def demo_health():
    """Demo service health check"""
    return {
        'status': 'healthy',
        'service': 'demo-real-time',
        'timestamp': datetime.utcnow().isoformat(),
        'note': 'This is demo data for testing purposes'
    }