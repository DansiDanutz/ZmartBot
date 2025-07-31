"""
Zmart Trading Bot Platform - Trading API Routes
Trading execution, position management, and symbol management
"""
import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query, Depends, Body
from pydantic import BaseModel
from datetime import datetime

from src.services.kucoin_service import get_kucoin_service, KuCoinService
from src.services.market_data_service import get_market_data_service, MarketDataService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/trading", tags=["trading"])

# Request/Response Models
class OrderRequest(BaseModel):
    """Order request model"""
    symbol: str
    side: str  # buy, sell
    size: float
    order_type: str = "market"  # market, limit
    price: Optional[float] = None
    leverage: int = 20

class OrderResponse(BaseModel):
    """Order response model"""
    order_id: str
    symbol: str
    side: str
    type: str
    size: float
    price: Optional[float] = None
    status: str
    timestamp: datetime

class PositionResponse(BaseModel):
    """Position response model"""
    symbol: str
    side: str
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    margin_type: str
    leverage: int
    liquidation_price: float
    timestamp: datetime

class PortfolioResponse(BaseModel):
    """Portfolio response model"""
    total_balance: float
    available_balance: float
    total_unrealized_pnl: float
    total_realized_pnl: float
    total_pnl: float
    active_positions: int
    positions: List[PositionResponse]
    timestamp: datetime

class MarketDataResponse(BaseModel):
    """Market data response model"""
    symbol: str
    price: float
    volume_24h: float
    change_24h: float
    high_24h: float
    low_24h: float
    source: str
    confidence: float
    timestamp: datetime

class SymbolManagementRequest(BaseModel):
    """Symbol management request model"""
    symbol: str
    action: str  # add, remove

# Dependencies
async def get_kucoin_dependency() -> KuCoinService:
    """Dependency to get KuCoin service instance"""
    return await get_kucoin_service()

async def get_market_data_dependency() -> MarketDataService:
    """Dependency to get market data service instance"""
    return await get_market_data_service()

# Account Management
@router.get("/accounts")
async def get_accounts(
    service: KuCoinService = Depends(get_kucoin_dependency)
):
    """Get all trading accounts"""
    try:
        account_overview = await service.get_account_overview()
        return {
            "success": True,
            "data": account_overview,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/balance/{currency}")
async def get_account_balance(
    currency: str,
    service: KuCoinService = Depends(get_kucoin_dependency)
):
    """Get account balance for specific currency"""
    try:
        account_overview = await service.get_account_overview()
        # Extract balance for specific currency if available
        if account_overview and 'data' in account_overview:
            account_data = account_overview.get('data', {})
            return {
                "success": True,
                "data": account_data,
                "timestamp": datetime.utcnow()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Account not found for {currency}")
    except Exception as e:
        logger.error(f"Error getting account balance for {currency}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Market Data
@router.get("/market-data/{symbol}")
async def get_market_data(
    symbol: str,
    market_service: MarketDataService = Depends(get_market_data_dependency)
):
    """Get unified market data for a symbol"""
    try:
        market_data = await market_service.get_unified_market_data(symbol)
        if market_data:
            return {
                "success": True,
                "data": market_data.dict(),
                "timestamp": datetime.utcnow()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Market data not available for {symbol}")
    except Exception as e:
        logger.error(f"Error getting market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-data/bulk")
async def get_bulk_market_data(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    market_service: MarketDataService = Depends(get_market_data_dependency)
):
    """Get market data for multiple symbols"""
    try:
        symbol_list = [s.strip() for s in symbols.split(",")]
        market_data = await market_service.get_bulk_market_data(symbol_list)
        
        return {
            "success": True,
            "data": {symbol: data.dict() for symbol, data in market_data.items()},
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting bulk market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/price-verification/{symbol}")
async def verify_price(
    symbol: str,
    expected_price: float = Query(...),
    tolerance: float = Query(default=0.01, ge=0.001, le=0.1),
    market_service: MarketDataService = Depends(get_market_data_dependency)
):
    """Verify price against multiple sources"""
    try:
        verification = await market_service.verify_price(symbol, expected_price, tolerance)
        return {
            "success": True,
            "data": verification.dict(),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error verifying price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Trading Operations
@router.post("/orders", response_model=OrderResponse)
async def place_order(
    order_request: OrderRequest,
    service: KuCoinService = Depends(get_kucoin_dependency)
):
    """Place a trading order"""
    try:
        order = await service.place_order(
            symbol=order_request.symbol,
            side=order_request.side,
            size=int(order_request.size) if order_request.size else None,
            order_type=order_request.order_type,
            price=str(order_request.price) if order_request.price else None,
            leverage=order_request.leverage
        )
        
        if order:
            return OrderResponse(
                order_id=order.get("orderId", ""),
                symbol=order_request.symbol,
                side=order_request.side,
                type=order_request.order_type,
                size=order_request.size,
                price=order_request.price,
                status=order.get("status", "pending"),
                timestamp=datetime.utcnow()
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to place order")
            
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{order_id}")
async def get_order_status(
    order_id: str,
    service: KuCoinService = Depends(get_kucoin_dependency)
):
    """Get order status"""
    try:
        # Use get_orders to find specific order
        orders = await service.get_orders("active")
        if orders and 'data' in orders:
            for order in orders['data']:
                if order.get('id') == order_id:
                    return {
                        "success": True,
                        "data": order,
                        "timestamp": datetime.utcnow()
                    }
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
            
    except Exception as e:
        logger.error(f"Error getting order status for {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    service: KuCoinService = Depends(get_kucoin_dependency)
):
    """Cancel an order"""
    try:
        success = await service.cancel_order(order_id)
        if success:
            return {
                "success": True,
                "message": f"Order {order_id} cancelled successfully",
                "timestamp": datetime.utcnow()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to cancel order {order_id}")
            
    except Exception as e:
        logger.error(f"Error canceling order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Position Management
@router.get("/positions")
async def get_positions(
    symbol: Optional[str] = Query(None),
    service: KuCoinService = Depends(get_kucoin_dependency)
):
    """Get current positions"""
    try:
        positions = await service.get_positions()
        if positions:
            # Filter by symbol if provided
            if symbol:
                positions = [p for p in positions if p.get('symbol') == symbol]
            return {
                "success": True,
                "data": positions,
                "timestamp": datetime.utcnow()
            }
        else:
            return {
                "success": True,
                "data": [],
                "timestamp": datetime.utcnow()
            }
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/positions/{symbol}/close")
async def close_position(
    symbol: str,
    side: str = Query(..., description="Position side (long/short)"),
    service: KuCoinService = Depends(get_kucoin_dependency)
):
    """Close a position by placing opposite order"""
    try:
        # Place an opposite order to close the position
        opposite_side = "sell" if side == "long" else "buy"
        result = await service.place_order(
            symbol=symbol,
            side=opposite_side,
            order_type="market",
            size=None,  # Will be determined by the position size
            price=None,
            leverage=1
        )
        
        if result:
            return {
                "success": True,
                "message": f"Position {symbol} {side} close order placed successfully",
                "timestamp": datetime.utcnow()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to close position {symbol} {side}")
            
    except Exception as e:
        logger.error(f"Error closing position {symbol} {side}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Portfolio Management
@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio_summary(
    service: KuCoinService = Depends(get_kucoin_dependency)
):
    """Get portfolio summary"""
    try:
        # Get account overview and positions
        account_overview = await service.get_account_overview()
        positions = await service.get_positions()
        
        # Calculate portfolio summary
        total_balance = 0.0
        total_unrealized_pnl = 0.0
        total_realized_pnl = 0.0
        active_positions = 0
        
        if positions:
            active_positions = len(positions)
            for position in positions:
                total_unrealized_pnl += float(position.get('unrealisedPnl', 0))
                total_realized_pnl += float(position.get('realisedPnl', 0))
        
        if account_overview and 'data' in account_overview:
            account_data = account_overview['data']
            total_balance = float(account_data.get('balance', 0))
        
        total_pnl = total_unrealized_pnl + total_realized_pnl
        
        return PortfolioResponse(
            total_balance=total_balance,
            available_balance=total_balance,
            total_unrealized_pnl=total_unrealized_pnl,
            total_realized_pnl=total_realized_pnl,
            total_pnl=total_pnl,
            active_positions=active_positions,
            positions=[],  # Convert positions to PositionResponse if needed
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Symbol Management
@router.get("/my-symbols")
async def get_my_symbols(
    service: KuCoinService = Depends(get_kucoin_dependency)
):
    """Get available trading symbols"""
    try:
        # Return the available symbols from the service
        return {
            "success": True,
            "data": list(service.symbols.keys()),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/my-symbols")
async def manage_symbols(
    request: SymbolManagementRequest,
    service: KuCoinService = Depends(get_kucoin_dependency)
):
    """Symbol management endpoint (placeholder)"""
    try:
        # This is a placeholder since the service doesn't have add/remove methods
        return {
            "success": True,
            "message": f"Symbol management not implemented yet",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error managing symbol {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Market Analysis
@router.get("/market-summary")
async def get_market_summary(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    market_service: MarketDataService = Depends(get_market_data_dependency)
):
    """Get market summary for multiple symbols"""
    try:
        symbol_list = [s.strip() for s in symbols.split(",")]
        summary = await market_service.get_market_summary(symbol_list)
        
        return {
            "success": True,
            "data": summary,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting market summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical-data/{symbol}")
async def get_historical_data(
    symbol: str,
    days: int = Query(default=30, ge=1, le=365),
    market_service: MarketDataService = Depends(get_market_data_dependency)
):
    """Get historical data for a symbol"""
    try:
        historical_data = await market_service.get_historical_data(symbol, days)
        return {
            "success": True,
            "data": historical_data,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Service Statistics
@router.get("/service-stats")
async def get_service_stats(
    market_service: MarketDataService = Depends(get_market_data_dependency)
):
    """Get service statistics"""
    try:
        stats = market_service.get_service_stats()
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting service stats: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 