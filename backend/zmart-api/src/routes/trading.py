"""
Zmart Trading Bot Platform - Trading Routes
Trade execution, position management, and portfolio operations
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

from src.routes.auth import get_current_active_user, require_role
from src.utils.locking import trading_lock, portfolio_lock
from src.utils.metrics import record_trade_metrics, update_portfolio_metrics
from src.utils.event_bus import emit_trade_event

router = APIRouter()

# Pydantic models
class TradeRequest(BaseModel):
    symbol: str
    side: str  # "buy" or "sell"
    quantity: float
    order_type: str = "market"  # "market", "limit", "stop"
    price: Optional[float] = None
    stop_price: Optional[float] = None
    leverage: Optional[int] = None

class TradeResponse(BaseModel):
    trade_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    status: str
    timestamp: datetime
    fees: float
    total_value: float

class Position(BaseModel):
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    leverage: int
    liquidation_price: float
    margin_used: float
    timestamp: datetime

class Portfolio(BaseModel):
    total_value: float
    available_balance: float
    margin_used: float
    unrealized_pnl: float
    realized_pnl: float
    positions: List[Position]
    last_updated: datetime

# Mock data (replace with database)
MOCK_TRADES = []
MOCK_POSITIONS = {}
MOCK_PORTFOLIO = {
    "total_value": 10000.0,
    "available_balance": 8000.0,
    "margin_used": 2000.0,
    "unrealized_pnl": 150.0,
    "realized_pnl": 500.0,
    "last_updated": datetime.utcnow()
}

@router.post("/execute", response_model=TradeResponse)
async def execute_trade(
    trade_request: TradeRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Execute a trade"""
    async with trading_lock(trade_request.symbol, current_user["username"]) as lock_context:
        try:
            # Validate trade request
            if trade_request.side not in ["buy", "sell"]:
                raise HTTPException(status_code=400, detail="Invalid side. Must be 'buy' or 'sell'")
            
            if trade_request.quantity <= 0:
                raise HTTPException(status_code=400, detail="Quantity must be positive")
            
            # Mock trade execution (replace with actual trading logic)
            trade_id = f"trade_{len(MOCK_TRADES) + 1}_{datetime.utcnow().timestamp()}"
            current_price = 50000.0  # Mock price (replace with real market data)
            fees = trade_request.quantity * current_price * 0.001  # 0.1% fee
            total_value = trade_request.quantity * current_price
            
            trade = {
                "trade_id": trade_id,
                "symbol": trade_request.symbol,
                "side": trade_request.side,
                "quantity": trade_request.quantity,
                "price": current_price,
                "status": "executed",
                "timestamp": datetime.utcnow(),
                "fees": fees,
                "total_value": total_value,
                "user_id": current_user["id"]
            }
            
            MOCK_TRADES.append(trade)
            
            # Record metrics
            record_trade_metrics(
                symbol=trade_request.symbol,
                side=trade_request.side,
                status="executed",
                volume=total_value
            )
            
            # Emit trade event
            await emit_trade_event(
                symbol=trade_request.symbol,
                side=trade_request.side,
                volume=trade_request.quantity,
                price=current_price
            )
            
            return TradeResponse(**trade)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Trade execution failed: {str(e)}")

@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    symbol: Optional[str] = None,
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get trade history"""
    trades = [trade for trade in MOCK_TRADES if trade["user_id"] == current_user["id"]]
    
    if symbol:
        trades = [trade for trade in trades if trade["symbol"] == symbol]
    
    # Sort by timestamp (newest first) and limit
    trades.sort(key=lambda x: x["timestamp"], reverse=True)
    trades = trades[:limit]
    
    return [TradeResponse(**trade) for trade in trades]

@router.get("/positions", response_model=List[Position])
async def get_positions(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get current positions"""
    # Mock positions (replace with database query)
    positions = []
    for symbol, position_data in MOCK_POSITIONS.items():
        if position_data["user_id"] == current_user["id"]:
            # Calculate current P&L
            current_price = 50000.0  # Mock price
            unrealized_pnl = (current_price - position_data["entry_price"]) * position_data["quantity"]
            if position_data["side"] == "sell":
                unrealized_pnl = -unrealized_pnl
            
            position = Position(
                symbol=symbol,
                side=position_data["side"],
                quantity=position_data["quantity"],
                entry_price=position_data["entry_price"],
                current_price=current_price,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=position_data.get("realized_pnl", 0.0),
                leverage=position_data.get("leverage", 1),
                liquidation_price=position_data.get("liquidation_price", 0.0),
                margin_used=position_data.get("margin_used", 0.0),
                timestamp=position_data["timestamp"]
            )
            positions.append(position)
    
    return positions

@router.get("/portfolio", response_model=Portfolio)
async def get_portfolio(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get portfolio information"""
    async with portfolio_lock(current_user["username"]) as lock_context:
        # Get positions
        positions = await get_positions(current_user)
        
        # Calculate portfolio metrics
        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
        total_margin_used = sum(pos.margin_used for pos in positions)
        
        portfolio = Portfolio(
            total_value=MOCK_PORTFOLIO["total_value"],
            available_balance=MOCK_PORTFOLIO["available_balance"],
            margin_used=total_margin_used,
            unrealized_pnl=total_unrealized_pnl,
            realized_pnl=MOCK_PORTFOLIO["realized_pnl"],
            positions=positions,
            last_updated=datetime.utcnow()
        )
        
        return portfolio

@router.post("/close-position")
async def close_position(
    symbol: str,
    quantity: Optional[float] = None,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Close a position"""
    async with trading_lock(symbol, current_user["username"]) as lock_context:
        if symbol not in MOCK_POSITIONS:
            raise HTTPException(status_code=404, detail="Position not found")
        
        position = MOCK_POSITIONS[symbol]
        if position["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not your position")
        
        close_quantity = quantity or position["quantity"]
        if close_quantity > position["quantity"]:
            raise HTTPException(status_code=400, detail="Cannot close more than current position")
        
        # Mock position closing
        current_price = 50000.0  # Mock price
        pnl = (current_price - position["entry_price"]) * close_quantity
        if position["side"] == "sell":
            pnl = -pnl
        
        # Update position
        position["quantity"] -= close_quantity
        position["realized_pnl"] = position.get("realized_pnl", 0.0) + pnl
        
        if position["quantity"] <= 0:
            del MOCK_POSITIONS[symbol]
        
        # Update portfolio
        MOCK_PORTFOLIO["realized_pnl"] += pnl
        MOCK_PORTFOLIO["available_balance"] += close_quantity * current_price
        
        return {
            "message": f"Closed {close_quantity} {symbol}",
            "realized_pnl": pnl,
            "remaining_quantity": position.get("quantity", 0)
        }

@router.get("/balance")
async def get_balance(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get account balance"""
    return {
        "available_balance": MOCK_PORTFOLIO["available_balance"],
        "margin_used": MOCK_PORTFOLIO["margin_used"],
        "total_value": MOCK_PORTFOLIO["total_value"],
        "currency": "USDT"
    }

@router.post("/deposit")
async def deposit_funds(
    amount: float,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Deposit funds to account"""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    MOCK_PORTFOLIO["available_balance"] += amount
    MOCK_PORTFOLIO["total_value"] += amount
    
    return {
        "message": f"Deposited {amount} USDT",
        "new_balance": MOCK_PORTFOLIO["available_balance"]
    }

@router.post("/withdraw")
async def withdraw_funds(
    amount: float,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Withdraw funds from account"""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    if amount > MOCK_PORTFOLIO["available_balance"]:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    MOCK_PORTFOLIO["available_balance"] -= amount
    MOCK_PORTFOLIO["total_value"] -= amount
    
    return {
        "message": f"Withdrawn {amount} USDT",
        "new_balance": MOCK_PORTFOLIO["available_balance"]
    }

@router.get("/orders")
async def get_orders(
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get open orders"""
    # Mock orders (replace with database query)
    orders = [
        {
            "order_id": "order_1",
            "symbol": "BTCUSDT",
            "side": "buy",
            "quantity": 0.1,
            "price": 50000.0,
            "status": "open",
            "timestamp": datetime.utcnow()
        }
    ]
    
    if symbol:
        orders = [order for order in orders if order["symbol"] == symbol]
    
    if status:
        orders = [order for order in orders if order["status"] == status]
    
    return orders

@router.post("/cancel-order/{order_id}")
async def cancel_order(
    order_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Cancel an open order"""
    # Mock order cancellation (replace with actual logic)
    return {
        "message": f"Order {order_id} cancelled successfully"
    }

@router.get("/market-data/{symbol}")
async def get_market_data(symbol: str):
    """Get market data for a symbol"""
    # Mock market data (replace with real market data)
    return {
        "symbol": symbol,
        "price": 50000.0,
        "volume_24h": 1000000.0,
        "change_24h": 2.5,
        "high_24h": 51000.0,
        "low_24h": 49000.0,
        "timestamp": datetime.utcnow()
    }

@router.get("/trading-pairs")
async def get_trading_pairs():
    """Get available trading pairs"""
    # Mock trading pairs (replace with database query)
    return [
        {"symbol": "BTCUSDT", "base": "BTC", "quote": "USDT", "status": "active"},
        {"symbol": "ETHUSDT", "base": "ETH", "quote": "USDT", "status": "active"},
        {"symbol": "ADAUSDT", "base": "ADA", "quote": "USDT", "status": "active"}
    ] 