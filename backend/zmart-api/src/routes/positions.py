#!/usr/bin/env python3
"""
Positions API Routes for Position Management
"""

import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/positions", tags=["positions"])

class PositionResponse(BaseModel):
    """Position response model"""
    id: str
    symbol: str
    direction: str
    status: str
    average_entry_price: Decimal
    current_stage: int
    total_investment: Decimal
    total_position_size: Decimal
    profit_threshold_75pct: Decimal
    take_profit_trigger: Decimal
    liquidation_price: Decimal
    initial_signal_score: Decimal
    profit_take_stage: str
    total_profit_realized: Decimal
    trailing_stop_price: Optional[Decimal]
    additional_margin: Decimal
    created_at: datetime
    updated_at: datetime
    last_scaled_at: Optional[datetime]
    position_metadata: Dict[str, Any]

class PositionScaleResponse(BaseModel):
    """Position scale response model"""
    stage: int
    investment_amount: Decimal
    leverage: int
    entry_price: Decimal
    position_size: Decimal
    profit_threshold: Decimal
    take_profit_price: Decimal
    scaled_at: datetime

class PositionCreate(BaseModel):
    """Position creation model"""
    symbol: str
    direction: str
    initial_investment: Decimal
    leverage: int
    signal_score: Decimal
    entry_price: Decimal

class PositionUpdate(BaseModel):
    """Position update model"""
    status: Optional[str] = None
    current_price: Optional[Decimal] = None
    signal_score: Optional[Decimal] = None

@router.get("/", response_model=List[PositionResponse])
async def get_positions(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of positions to return"),
    offset: int = Query(0, ge=0, description="Number of positions to skip")
):
    """Get all positions with filtering and pagination"""
    try:
        # Mock positions for demonstration
        positions = [
            {
                "id": "pos_001",
                "symbol": "BTCUSDT",
                "direction": "long",
                "status": "active",
                "average_entry_price": Decimal("50000"),
                "current_stage": 1,
                "total_investment": Decimal("500"),
                "total_position_size": Decimal("10000"),
                "profit_threshold_75pct": Decimal("51250"),
                "take_profit_trigger": Decimal("50625"),
                "liquidation_price": Decimal("47500"),
                "initial_signal_score": Decimal("0.85"),
                "profit_take_stage": "none",
                "total_profit_realized": Decimal("0"),
                "trailing_stop_price": None,
                "additional_margin": Decimal("0"),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "last_scaled_at": None,
                "position_metadata": {
                    "total_invested": 500,
                    "total_position_value": 10000,
                    "profit_threshold_75pct": 51250,
                    "first_take_profit_trigger": 50625,
                    "corrected_calculations": True
                }
            }
        ]
        
        # Apply filters
        if symbol:
            positions = [p for p in positions if p["symbol"].upper() == symbol.upper()]
        if status:
            positions = [p for p in positions if p["status"] == status]
        
        # Apply pagination
        positions = positions[offset:offset + limit]
        
        return [PositionResponse(**position) for position in positions]
        
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting positions: {str(e)}")

@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(position_id: str = Path(..., description="Position ID")):
    """Get a specific position by ID"""
    try:
        # Mock position data
        position = {
            "id": position_id,
            "symbol": "BTCUSDT",
            "direction": "long",
            "status": "active",
            "average_entry_price": Decimal("50000"),
            "current_stage": 1,
            "total_investment": Decimal("500"),
            "total_position_size": Decimal("10000"),
            "profit_threshold_75pct": Decimal("51250"),
            "take_profit_trigger": Decimal("50625"),
            "liquidation_price": Decimal("47500"),
            "initial_signal_score": Decimal("0.85"),
            "profit_take_stage": "none",
            "total_profit_realized": Decimal("0"),
            "trailing_stop_price": None,
            "additional_margin": Decimal("0"),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "last_scaled_at": None,
            "position_metadata": {
                "total_invested": 500,
                "total_position_value": 10000,
                "profit_threshold_75pct": 51250,
                "first_take_profit_trigger": 50625,
                "corrected_calculations": True
            }
        }
        
        return PositionResponse(**position)
        
    except Exception as e:
        logger.error(f"Error getting position {position_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting position: {str(e)}")

@router.get("/{position_id}/calculations", response_model=Dict[str, Any])
async def get_position_calculations(
    position_id: str = Path(..., description="Position ID"),
    current_price: Optional[Decimal] = Query(None, description="Current market price for calculations")
):
    """Get detailed position calculations"""
    try:
        if current_price is None:
            current_price = Decimal("51000")  # Mock current price
        
        # Mock calculations
        calculations = {
            "position_id": position_id,
            "current_price": float(current_price),
            "entry_price": 50000.0,
            "total_invested": 500.0,
            "total_position_value": 10000.0,
            "current_pnl": float(current_price - 50000) * 0.2,  # 20% of price difference
            "pnl_percentage": float((current_price - 50000) / 50000 * 100),
            "profit_threshold_75pct": 51250.0,
            "take_profit_trigger": 50625.0,
            "liquidation_price": 47500.0,
            "margin_ratio": 0.05,
            "leverage": 20,
            "risk_level": "medium",
            "scaling_opportunity": current_price > 50625,
            "take_profit_opportunity": current_price > 51250,
            "stop_loss_triggered": current_price < 47500
        }
        
        return calculations
        
    except Exception as e:
        logger.error(f"Error getting position calculations: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting calculations: {str(e)}")

@router.get("/{position_id}/scaling-stages", response_model=List[PositionScaleResponse])
async def get_position_scaling_stages(position_id: str = Path(..., description="Position ID")):
    """Get scaling stages for a position"""
    try:
        # Mock scaling stages
        stages = [
            {
                "stage": 1,
                "investment_amount": Decimal("500"),
                "leverage": 20,
                "entry_price": Decimal("50000"),
                "position_size": Decimal("10000"),
                "profit_threshold": Decimal("51250"),
                "take_profit_price": Decimal("50625"),
                "scaled_at": datetime.now(timezone.utc)
            },
            {
                "stage": 2,
                "investment_amount": Decimal("1000"),
                "leverage": 10,
                "entry_price": Decimal("51000"),
                "position_size": Decimal("10000"),
                "profit_threshold": Decimal("52275"),
                "take_profit_price": Decimal("51637.5"),
                "scaled_at": datetime.now(timezone.utc)
            }
        ]
        
        return [PositionScaleResponse(**stage) for stage in stages]
        
    except Exception as e:
        logger.error(f"Error getting scaling stages: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting scaling stages: {str(e)}")

@router.post("/{position_id}/scale")
async def scale_position(
    position_id: str = Path(..., description="Position ID"),
    current_price: Decimal = Query(..., description="Current market price"),
    signal_score: Decimal = Query(..., description="Current signal score")
):
    """Scale a position based on current conditions"""
    try:
        # Mock scaling logic
        scaling_result = {
            "position_id": position_id,
            "scaled": True,
            "new_stage": 2,
            "additional_investment": float(Decimal("1000")),
            "new_leverage": 10,
            "new_entry_price": float(current_price),
            "new_position_size": float(current_price * Decimal("100")),  # 100 USDT at new leverage
            "new_profit_threshold": float(current_price * Decimal("1.025")),  # 2.5% profit threshold
            "scaled_at": datetime.now(timezone.utc).isoformat(),
            "signal_score": float(signal_score),
            "scaling_conditions_met": signal_score > Decimal("0.7")
        }
        
        return scaling_result
        
    except Exception as e:
        logger.error(f"Error scaling position: {e}")
        raise HTTPException(status_code=500, detail=f"Error scaling position: {str(e)}")

@router.post("/{position_id}/take-profit")
async def take_profit(
    position_id: str = Path(..., description="Position ID"),
    current_price: Decimal = Query(..., description="Current market price"),
    profit_stage: Optional[str] = Query(None, description="Specific profit stage to execute")
):
    """Take profit on a position"""
    try:
        # Mock take profit logic
        take_profit_result = {
            "position_id": position_id,
            "profit_taken": True,
            "profit_amount": float(current_price - 50000) * 0.2,  # 20% of position
            "profit_percentage": float((current_price - 50000) / 50000 * 100),
            "remaining_position": 0.8,  # 80% remaining
            "profit_stage": profit_stage or "first",
            "taken_at": datetime.now(timezone.utc).isoformat(),
            "current_price": float(current_price)
        }
        
        return take_profit_result
        
    except Exception as e:
        logger.error(f"Error taking profit: {e}")
        raise HTTPException(status_code=500, detail=f"Error taking profit: {str(e)}")

@router.post("/{position_id}/add-margin")
async def add_margin(
    position_id: str = Path(..., description="Position ID"),
    current_price: Decimal = Query(..., description="Current market price")
):
    """Add margin to a position"""
    try:
        # Mock margin addition
        margin_result = {
            "position_id": position_id,
            "margin_added": True,
            "additional_margin": 100.0,
            "new_margin_ratio": 0.06,
            "liquidation_price_updated": 47000.0,
            "margin_added_at": datetime.now(timezone.utc).isoformat(),
            "current_price": float(current_price)
        }
        
        return margin_result
        
    except Exception as e:
        logger.error(f"Error adding margin: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding margin: {str(e)}")

@router.get("/summary/all")
async def get_positions_summary():
    """Get summary of all positions"""
    try:
        # Mock summary
        summary = {
            "total_positions": 5,
            "active_positions": 3,
            "closed_positions": 2,
            "total_invested": 2500.0,
            "total_pnl": 125.0,
            "total_pnl_percentage": 5.0,
            "average_signal_score": 0.82,
            "positions_by_symbol": {
                "BTCUSDT": 2,
                "ETHUSDT": 2,
                "ADAUSDT": 1
            },
            "positions_by_status": {
                "active": 3,
                "closed": 2
            },
            "risk_distribution": {
                "low": 1,
                "medium": 2,
                "high": 2
            }
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting positions summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")

@router.post("/", response_model=PositionResponse)
async def create_position(position: PositionCreate):
    """Create a new position"""
    try:
        # Mock position creation
        new_position = {
            "id": f"pos_{datetime.now().timestamp()}",
            "symbol": position.symbol,
            "direction": position.direction,
            "status": "active",
            "average_entry_price": position.entry_price,
            "current_stage": 1,
            "total_investment": position.initial_investment,
            "total_position_size": position.initial_investment * position.leverage,
            "profit_threshold_75pct": position.entry_price * Decimal("1.025"),
            "take_profit_trigger": position.entry_price * Decimal("1.0125"),
            "liquidation_price": position.entry_price * Decimal("0.95"),
            "initial_signal_score": position.signal_score,
            "profit_take_stage": "none",
            "total_profit_realized": Decimal("0"),
            "trailing_stop_price": None,
            "additional_margin": Decimal("0"),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "last_scaled_at": None,
            "position_metadata": {
                "total_invested": float(position.initial_investment),
                "total_position_value": float(position.initial_investment * position.leverage),
                "profit_threshold_75pct": float(position.entry_price * Decimal("1.025")),
                "first_take_profit_trigger": float(position.entry_price * Decimal("1.0125")),
                "corrected_calculations": True
            }
        }
        
        return PositionResponse(**new_position)
        
    except Exception as e:
        logger.error(f"Error creating position: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating position: {str(e)}")

@router.put("/{position_id}", response_model=PositionResponse)
async def update_position(
    position_id: str = Path(..., description="Position ID"),
    position_update: Optional[PositionUpdate] = None
):
    """Update a position"""
    try:
        # Mock position update
        updated_position = {
            "id": position_id,
            "symbol": "BTCUSDT",
            "direction": "long",
            "status": position_update.status if position_update and position_update.status else "active",
            "average_entry_price": Decimal("50000"),
            "current_stage": 1,
            "total_investment": Decimal("500"),
            "total_position_size": Decimal("10000"),
            "profit_threshold_75pct": Decimal("51250"),
            "take_profit_trigger": Decimal("50625"),
            "liquidation_price": Decimal("47500"),
            "initial_signal_score": Decimal("0.85"),
            "profit_take_stage": "none",
            "total_profit_realized": Decimal("0"),
            "trailing_stop_price": None,
            "additional_margin": Decimal("0"),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "last_scaled_at": None,
            "position_metadata": {
                "total_invested": 500,
                "total_position_value": 10000,
                "profit_threshold_75pct": 51250,
                "first_take_profit_trigger": 50625,
                "corrected_calculations": True
            }
        }
        
        return PositionResponse(**updated_position)
        
    except Exception as e:
        logger.error(f"Error updating position: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating position: {str(e)}")

@router.delete("/{position_id}")
async def close_position(position_id: str = Path(..., description="Position ID")):
    """Close a position"""
    try:
        # Mock position closure
        closure_result = {
            "position_id": position_id,
            "closed": True,
            "final_pnl": 125.0,
            "final_pnl_percentage": 5.0,
            "closed_at": datetime.now(timezone.utc).isoformat(),
            "reason": "manual_closure"
        }
        
        return closure_result
        
    except Exception as e:
        logger.error(f"Error closing position: {e}")
        raise HTTPException(status_code=500, detail=f"Error closing position: {str(e)}") 