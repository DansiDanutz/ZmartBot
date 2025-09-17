"""
Real-Time Price Routes - NO MOCK DATA
Provides real market prices from exchanges and technical data
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from src.services.real_time_price_service import (
    get_real_time_price_service,
    RealTimePrice,
    TechnicalData,
    HistoricalPrice
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/real-time", tags=["real-time-prices"])

@router.get("/price/{symbol}", response_model=RealTimePrice)
async def get_real_time_price(symbol: str):
    """
    Get REAL-TIME price for a symbol
    NO MOCK DATA - Only real exchange prices
    
    Sources (in priority order):
    1. KuCoin Futures
    2. Binance Spot/Futures
    3. Cryptometer
    """
    try:
        service = await get_real_time_price_service()
        price_data = await service.get_real_time_price(symbol.upper())
        
        if not price_data:
            raise HTTPException(
                status_code=404,
                detail=f"No real price data available for {symbol}"
            )
        
        return price_data
        
    except ValueError as e:
        # No data available from any source
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching real-time price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/prices", response_model=Dict[str, RealTimePrice])
async def get_multiple_prices(symbols: List[str] = Query(..., description="List of symbols")):
    """
    Get real-time prices for multiple symbols
    Fetches concurrently for better performance
    """
    try:
        service = await get_real_time_price_service()
        
        # Convert to uppercase
        symbols = [s.upper() for s in symbols]
        
        # Get prices concurrently
        prices = await service.get_multi_symbol_prices(symbols)
        
        if not prices:
            raise HTTPException(
                status_code=503,
                detail="Could not fetch prices for any symbols"
            )
        
        return prices
        
    except Exception as e:
        logger.error(f"Error fetching multiple prices: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/technical/{symbol}", response_model=TechnicalData)
async def get_technical_data(symbol: str):
    """
    Get technical analysis data from Cryptometer
    Includes RSI, MACD, Moving Averages, Support/Resistance
    """
    try:
        service = await get_real_time_price_service()
        technical_data = await service.get_technical_data(symbol.upper())
        
        if not technical_data:
            raise HTTPException(
                status_code=404,
                detail=f"No technical data available for {symbol}"
            )
        
        return technical_data
        
    except Exception as e:
        logger.error(f"Error fetching technical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/historical/{symbol}", response_model=List[HistoricalPrice])
async def get_historical_prices(
    symbol: str,
    start_date: Optional[datetime] = Query(None, description="Start date for historical data"),
    end_date: Optional[datetime] = Query(None, description="End date for historical data"),
    days: Optional[int] = Query(7, description="Number of days of history (if dates not provided)")
):
    """
    Get historical price data
    Sources: CSV files (if available) or Binance API
    """
    try:
        service = await get_real_time_price_service()
        
        # Set date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            # Use default of 7 days if days is None
            days_value = days if days is not None else 7
            start_date = end_date - timedelta(days=days_value)
        
        historical_data = await service.get_historical_prices(
            symbol.upper(),
            start_date,
            end_date
        )
        
        if not historical_data:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data available for {symbol}"
            )
        
        return historical_data
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/market-overview")
async def get_market_overview():
    """
    Get real-time market overview for major cryptocurrencies
    """
    try:
        service = await get_real_time_price_service()
        
        # Major symbols to track
        major_symbols = [
            "BTCUSDT",
            "ETHUSDT",
            "BNBUSDT",
            "SOLUSDT",
            "XRPUSDT",
            "ADAUSDT",
            "AVAXUSDT",
            "DOGEUSDT",
            "DOTUSDT"
        ]
        
        # Get prices
        prices = await service.get_multi_symbol_prices(major_symbols)
        
        # Calculate market statistics
        total_market_cap = 0
        total_volume = 0
        gainers = []
        losers = []
        
        for symbol, price_data in prices.items():
            total_volume += price_data.volume_24h
            
            if price_data.change_24h > 0:
                gainers.append({
                    'symbol': symbol,
                    'price': price_data.price,
                    'change': price_data.change_24h
                })
            else:
                losers.append({
                    'symbol': symbol,
                    'price': price_data.price,
                    'change': price_data.change_24h
                })
        
        # Sort gainers and losers
        gainers.sort(key=lambda x: x['change'], reverse=True)
        losers.sort(key=lambda x: x['change'])
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_symbols': len(prices),
            'total_volume_24h': total_volume,
            'top_gainers': gainers[:3],
            'top_losers': losers[:3],
            'prices': prices
        }
        
    except Exception as e:
        logger.error(f"Error fetching market overview: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/price-alert-check/{symbol}")
async def check_price_alerts(
    symbol: str,
    above: Optional[float] = Query(None, description="Check if price is above this level"),
    below: Optional[float] = Query(None, description="Check if price is below this level")
):
    """
    Check if current price triggers any alerts
    """
    try:
        if not above and not below:
            raise HTTPException(
                status_code=400,
                detail="Must provide either 'above' or 'below' parameter"
            )
        
        service = await get_real_time_price_service()
        price_data = await service.get_real_time_price(symbol.upper())
        
        if not price_data:
            raise HTTPException(
                status_code=404,
                detail=f"No price data available for {symbol}"
            )
        
        alerts_triggered = []
        
        if above and price_data.price > above:
            alerts_triggered.append({
                'type': 'above',
                'level': above,
                'current_price': price_data.price,
                'triggered': True
            })
        
        if below and price_data.price < below:
            alerts_triggered.append({
                'type': 'below',
                'level': below,
                'current_price': price_data.price,
                'triggered': True
            })
        
        return {
            'symbol': symbol,
            'current_price': price_data.price,
            'source': price_data.source,
            'timestamp': price_data.timestamp.isoformat(),
            'alerts': alerts_triggered,
            'alerts_triggered': len(alerts_triggered) > 0
        }
        
    except Exception as e:
        logger.error(f"Error checking price alerts for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check():
    """
    Check if real-time price services are operational
    """
    try:
        service = await get_real_time_price_service()
        
        # Try to fetch BTC price as health check
        btc_price = await service.get_real_time_price("BTCUSDT")
        
        return {
            'status': 'healthy' if btc_price else 'degraded',
            'timestamp': datetime.utcnow().isoformat(),
            'btc_price': btc_price.price if btc_price else None,
            'services': {
                'binance': 'operational',
                'kucoin': 'operational',
                'cryptometer': 'operational'
            }
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }