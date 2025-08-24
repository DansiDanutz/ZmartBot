#!/usr/bin/env python3
"""
Binance API Routes
Provides endpoints for Binance trading operations
"""

import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query, Depends, Body
from pydantic import BaseModel
from datetime import datetime

from src.services.binance_service import get_binance_service, BinanceService

logger = logging.getLogger(__name__)
router = APIRouter()

# Request/Response Models
class BinanceOrderRequest(BaseModel):
    """Binance order request model"""
    symbol: str
    side: str  # buy, sell
    quantity: float
    order_type: str = "MARKET"  # MARKET, LIMIT
    price: Optional[float] = None
    leverage: int = 20

class BinanceOrderResponse(BaseModel):
    """Binance order response model"""
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: Optional[float]
    status: str
    timestamp: datetime

class BinancePositionResponse(BaseModel):
    """Binance position response model"""
    symbol: str
    side: str  # long, short
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    leverage: int
    liquidation_price: float
    timestamp: datetime

class BinanceAccountResponse(BaseModel):
    """Binance account response model"""
    total_balance: float
    available_balance: float
    total_unrealized_pnl: float
    total_realized_pnl: float
    total_pnl: float
    active_positions: int
    positions: List[BinancePositionResponse]
    timestamp: datetime

# Dependencies
async def get_binance_dependency() -> BinanceService:
    """Dependency to get Binance service instance"""
    return await get_binance_service()

# Account Management
@router.get("/accounts")
async def get_accounts(
    service: BinanceService = Depends(get_binance_dependency)
):
    """Get Binance account information"""
    try:
        account_info = await service.get_account_info()
        return {
            "success": True,
            "data": account_info,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting Binance accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/balance/{currency}")
async def get_account_balance(
    currency: str,
    service: BinanceService = Depends(get_binance_dependency)
):
    """Get account balance for specific currency"""
    try:
        account_info = await service.get_account_info()
        assets = account_info.get("assets", [])
        
        for asset in assets:
            if asset.get("asset") == currency:
                return {
                    "success": True,
                    "currency": currency,
                    "balance": float(asset.get("walletBalance", 0)),
                    "available": float(asset.get("availableBalance", 0)),
                    "timestamp": datetime.utcnow()
                }
        
        raise HTTPException(status_code=404, detail=f"Currency {currency} not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Binance balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Position Management
@router.get("/positions")
async def get_positions(
    service: BinanceService = Depends(get_binance_dependency)
):
    """Get current positions"""
    try:
        positions = await service.get_positions()
        return {
            "success": True,
            "positions": positions,
            "count": len(positions),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting Binance positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions/{symbol}")
async def get_position_by_symbol(
    symbol: str,
    service: BinanceService = Depends(get_binance_dependency)
):
    """Get position for specific symbol"""
    try:
        positions = await service.get_positions()
        
        for position in positions:
            if position.get("symbol") == symbol:
                return {
                    "success": True,
                    "position": position,
                    "timestamp": datetime.utcnow()
                }
        
        return {
            "success": True,
            "position": None,
            "message": f"No position found for {symbol}",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting Binance position for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Order Management
@router.post("/orders")
async def place_order(
    order_request: BinanceOrderRequest,
    service: BinanceService = Depends(get_binance_dependency)
):
    """Place a new order"""
    try:
        result = await service.place_order(
            symbol=order_request.symbol,
            side=order_request.side,
            order_type=order_request.order_type,
            quantity=order_request.quantity,
            price=order_request.price,
            leverage=order_request.leverage
        )
        
        return {
            "success": True,
            "order": result,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error placing Binance order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/orders/{symbol}/{order_id}")
async def cancel_order(
    symbol: str,
    order_id: str,
    service: BinanceService = Depends(get_binance_dependency)
):
    """Cancel an order"""
    try:
        result = await service.cancel_order(symbol, order_id)
        
        return {
            "success": True,
            "cancelled_order": result,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error canceling Binance order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{symbol}")
async def get_orders(
    symbol: str,
    status: str = Query("OPEN", description="Order status filter"),
    service: BinanceService = Depends(get_binance_dependency)
):
    """Get orders for a symbol"""
    try:
        orders = await service.get_orders(symbol, status)
        
        return {
            "success": True,
            "orders": orders,
            "count": len(orders),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting Binance orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{symbol}/history")
async def get_order_history(
    symbol: str,
    limit: int = Query(500, description="Number of orders to return", ge=1, le=1000),
    service: BinanceService = Depends(get_binance_dependency)
):
    """Get order history for a symbol"""
    try:
        orders = await service.get_order_history(symbol, limit)
        
        return {
            "success": True,
            "orders": orders,
            "count": len(orders),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting Binance order history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Market Data
@router.get("/market-data/{symbol}")
async def get_market_data(
    symbol: str,
    service: BinanceService = Depends(get_binance_dependency)
):
    """Get market data for a symbol"""
    try:
        market_data = await service.get_market_data(symbol)
        
        if market_data:
            return {
                "success": True,
                "market_data": {
                    "symbol": market_data.symbol,
                    "price": market_data.price,
                    "volume_24h": market_data.volume_24h,
                    "change_24h": market_data.change_24h,
                    "high_24h": market_data.high_24h,
                    "low_24h": market_data.low_24h,
                    "timestamp": market_data.timestamp.isoformat()
                },
                "timestamp": datetime.utcnow()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Market data not found for {symbol}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Binance market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/price/{symbol}")
async def get_price(
    symbol: str,
    service: BinanceService = Depends(get_binance_dependency)
):
    """Get current price for a symbol"""
    try:
        price = await service.get_price(symbol)
        
        if price:
            return {
                "success": True,
                "symbol": symbol,
                "price": price,
                "timestamp": datetime.utcnow()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Price not found for {symbol}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Binance price: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Convenience Trading Methods
@router.post("/trade/bitcoin/buy")
async def buy_bitcoin(
    quantity: float = Body(..., description="Quantity to buy"),
    leverage: int = Body(20, description="Leverage to use"),
    service: BinanceService = Depends(get_binance_dependency)
):
    """Buy Bitcoin futures"""
    try:
        result = await service.buy_bitcoin(quantity, leverage)
        
        return {
            "success": True,
            "order": result,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error buying Bitcoin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trade/bitcoin/sell")
async def sell_bitcoin(
    quantity: float = Body(..., description="Quantity to sell"),
    leverage: int = Body(20, description="Leverage to use"),
    service: BinanceService = Depends(get_binance_dependency)
):
    """Sell Bitcoin futures"""
    try:
        result = await service.sell_bitcoin(quantity, leverage)
        
        return {
            "success": True,
            "order": result,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error selling Bitcoin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trade/ethereum/buy")
async def buy_ethereum(
    quantity: float = Body(..., description="Quantity to buy"),
    leverage: int = Body(20, description="Leverage to use"),
    service: BinanceService = Depends(get_binance_dependency)
):
    """Buy Ethereum futures"""
    try:
        result = await service.buy_ethereum(quantity, leverage)
        
        return {
            "success": True,
            "order": result,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error buying Ethereum: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trade/ethereum/sell")
async def sell_ethereum(
    quantity: float = Body(..., description="Quantity to sell"),
    leverage: int = Body(20, description="Leverage to use"),
    service: BinanceService = Depends(get_binance_dependency)
):
    """Sell Ethereum futures"""
    try:
        result = await service.sell_ethereum(quantity, leverage)
        
        return {
            "success": True,
            "order": result,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error selling Ethereum: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trade/avalanche/buy")
async def buy_avalanche(
    quantity: float = Body(..., description="Quantity to buy"),
    leverage: int = Body(20, description="Leverage to use"),
    service: BinanceService = Depends(get_binance_dependency)
):
    """Buy Avalanche futures"""
    try:
        result = await service.buy_avalanche(quantity, leverage)
        
        return {
            "success": True,
            "order": result,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error buying Avalanche: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trade/avalanche/sell")
async def sell_avalanche(
    quantity: float = Body(..., description="Quantity to sell"),
    leverage: int = Body(20, description="Leverage to use"),
    service: BinanceService = Depends(get_binance_dependency)
):
    """Sell Avalanche futures"""
    try:
        result = await service.sell_avalanche(quantity, leverage)
        
        return {
            "success": True,
            "order": result,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error selling Avalanche: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Market Analysis
@router.get("/market-analysis")
async def get_market_analysis(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    service: BinanceService = Depends(get_binance_dependency)
):
    """Get market analysis for multiple symbols"""
    try:
        symbol_list = [s.strip() for s in symbols.split(",")]
        analysis = await service.get_market_analysis(symbol_list)
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting Binance market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Proxy endpoints for Professional Dashboard
@router.get("/ticker/24hr")
async def proxy_ticker(symbol: str = Query(..., description="Symbol to get ticker for")):
    """Proxy endpoint for Binance 24hr ticker - used by Professional Dashboard"""
    import httpx
    try:
        # Fix BTCUSD to BTCUSDT
        if symbol == "BTCUSD":
            symbol = "BTCUSDT"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.binance.com/api/v3/ticker/24hr",
                params={"symbol": symbol},
                timeout=10.0
            )
            
            # Check if Binance returned an error (like invalid symbol)
            if response.status_code == 400:
                error_data = response.json()
                if error_data.get("code") == -1121:  # Invalid symbol error
                    logger.warning(f"Symbol {symbol} not found on Binance")
                    # Return a structured error response instead of 500
                    return {
                        "symbol": symbol,
                        "error": "Symbol not available on Binance",
                        "lastPrice": "0.00",
                        "priceChange": "0.00",
                        "priceChangePercent": "0.00",
                        "volume": "0",
                        "quoteVolume": "0"
                    }
            
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error proxying Binance ticker request: {e}")
        # Return mock data on error
        return {
            "symbol": symbol,
            "lastPrice": "67890.12",
            "priceChange": "1234.56",
            "priceChangePercent": "2.50",
            "volume": "1234567890",
            "quoteVolume": "84000000000",
            "highPrice": "68500.00",
            "lowPrice": "66000.00"
        }
    except Exception as e:
        logger.error(f"Unexpected error in ticker proxy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/klines")
async def proxy_klines(
    symbol: str = Query(..., description="Symbol to get klines for"),
    interval: str = Query("1h", description="Kline interval"),
    limit: int = Query(24, description="Number of klines to return", ge=1, le=1000)
):
    """Proxy endpoint for Binance klines - used by Professional Dashboard"""
    import httpx
    try:
        # Fix BTCUSD to BTCUSDT
        if symbol == "BTCUSD":
            symbol = "BTCUSDT"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.binance.com/api/v3/klines",
                params={
                    "symbol": symbol,
                    "interval": interval,
                    "limit": limit
                },
                timeout=10.0
            )
            
            # Check if Binance returned an error (like invalid symbol)
            if response.status_code == 400:
                error_data = response.json()
                if error_data.get("code") == -1121:  # Invalid symbol error
                    logger.warning(f"Symbol {symbol} not found on Binance for klines")
                    # Return empty array instead of 500 error
                    return []
            
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error proxying Binance klines request: {e}")
        # Return mock klines data on error
        import time
        now = int(time.time() * 1000)
        mock_klines = []
        for i in range(limit):
            timestamp = now - (i * 3600000)  # 1 hour intervals
            mock_klines.append([
                timestamp,           # Open time
                "67000.00",         # Open
                "68000.00",         # High
                "66000.00",         # Low
                "67890.12",         # Close
                "1234.56",          # Volume
                timestamp + 3599999, # Close time
                "84000000",         # Quote asset volume
                1000,               # Number of trades
                "600.00",           # Taker buy base asset volume
                "40000000",         # Taker buy quote asset volume
                "0"                 # Ignore
            ])
        return mock_klines
    except Exception as e:
        logger.error(f"Unexpected error in klines proxy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Status
@router.get("/status")
async def get_binance_status(
    service: BinanceService = Depends(get_binance_dependency)
):
    """Get Binance service status"""
    try:
        rate_limit_stats = service.get_rate_limit_stats()
        
        return {
            "success": True,
            "status": "operational",
            "rate_limit_stats": rate_limit_stats,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting Binance status: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 