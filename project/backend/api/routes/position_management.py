#!/usr/bin/env python3
"""
Position Management Routes with Correct Take Profit and Liquidation Cluster Strategy
"""

import logging
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel

from src.services.position_manager_with_clusters import position_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/position-management", tags=["position-management"])

class OpenPositionRequest(BaseModel):
    """Request to open a new position"""
    symbol: str
    entry_price: float
    margin_investment: float  # The X amount invested
    leverage: int = 20

class UpdatePositionRequest(BaseModel):
    """Request to update position with current price"""
    position_id: str
    current_price: float

class PositionResponse(BaseModel):
    """Position response"""
    success: bool
    data: Dict[str, Any]
    message: Optional[str] = None

@router.post("/open", response_model=PositionResponse)
async def open_position(request: OpenPositionRequest):
    """
    Open a new position with the correct strategy:
    - Entry with specified leverage (default 20X)
    - First TP at 175% of margin (close 50%)
    - Trailing stop at 2% from max
    - Exit at liquidation clusters
    """
    try:
        # Calculate position size
        position_size = Decimal(str(request.margin_investment)) * request.leverage
        
        # Open position
        position = await position_manager.open_position(
            symbol=request.symbol,
            entry_price=Decimal(str(request.entry_price)),
            position_size=position_size,
            margin_used=Decimal(str(request.margin_investment)),
            leverage=request.leverage
        )
        
        # Calculate key levels
        first_tp_target = request.margin_investment * 1.75
        first_tp_price = request.entry_price * (1 + (first_tp_target - request.margin_investment) / float(position_size))
        
        return PositionResponse(
            success=True,
            data={
                "position_id": position.position_id,
                "symbol": position.symbol,
                "entry_price": float(position.entry_price),
                "margin_invested": float(position.margin_used),
                "position_size": float(position.position_size),
                "leverage": position.leverage,
                "first_tp_target": first_tp_target,
                "first_tp_price": first_tp_price,
                "first_tp_info": "Will close 50% of position at 175% of margin",
                "trailing_stop_info": "2% trailing stop after first TP",
                "liquidation_clusters": [
                    {
                        "price": float(c.price_level),
                        "strength": c.cluster_strength,
                        "type": c.cluster_type
                    } for c in position.liquidation_clusters[:3]
                ],
                "created_at": position.created_at.isoformat()
            },
            message=f"Position opened successfully with {request.leverage}X leverage"
        )
        
    except Exception as e:
        logger.error(f"Error opening position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update", response_model=PositionResponse)
async def update_position(request: UpdatePositionRequest):
    """
    Update position with current price
    Checks for:
    - First take profit (175% of margin - close 50%)
    - Liquidation cluster exits
    - Trailing stop (2% from max)
    """
    try:
        result = await position_manager.update_position(
            position_id=request.position_id,
            current_price=Decimal(str(request.current_price))
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return PositionResponse(
            success=True,
            data=result,
            message="Position updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{position_id}/status", response_model=PositionResponse)
async def get_position_status(position_id: str):
    """Get detailed position status including cluster targets"""
    try:
        status = position_manager.get_position_status(position_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Position not found")
        
        return PositionResponse(
            success=True,
            data=status,
            message="Position status retrieved"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting position status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active/all", response_model=PositionResponse)
async def get_all_active_positions():
    """Get all active positions"""
    try:
        positions = []
        for position_id in position_manager.active_positions:
            status = position_manager.get_position_status(position_id)
            if status:
                positions.append(status)
        
        return PositionResponse(
            success=True,
            data={
                "count": len(positions),
                "positions": positions
            },
            message=f"Found {len(positions)} active positions"
        )
        
    except Exception as e:
        logger.error(f"Error getting active positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate-strategy")
async def simulate_strategy(
    symbol: str = Query(..., description="Trading symbol"),
    entry_price: float = Query(..., description="Entry price"),
    margin: float = Query(500, description="Margin investment (X)"),
    leverage: int = Query(20, description="Initial leverage")
):
    """
    Simulate the complete strategy with calculations
    Shows:
    - First TP at 175% of margin (50% close)
    - Trailing stop levels
    - Liquidation price
    """
    try:
        position_size = margin * leverage
        
        # Calculate first take profit
        profit_target = margin * 1.75  # 175% of margin
        price_move_needed = (profit_target - margin) / leverage / margin
        first_tp_price = entry_price * (1 + price_move_needed)
        
        # Calculate liquidation price (5% move against at 20X)
        liquidation_move = 1 / leverage * 0.95  # 95% of max move
        liquidation_price = entry_price * (1 - liquidation_move)
        
        # Example trailing stop levels
        example_max_price = first_tp_price * 1.05  # 5% above first TP
        trailing_stop = example_max_price * 0.98  # 2% below max
        
        return {
            "strategy_simulation": {
                "entry": {
                    "price": entry_price,
                    "margin": margin,
                    "leverage": leverage,
                    "position_size": position_size
                },
                "first_take_profit": {
                    "trigger_price": round(first_tp_price, 2),
                    "price_move_percentage": round(price_move_needed * 100, 2),
                    "profit_amount": profit_target - margin,
                    "profit_percentage": 75,  # 75% profit on margin
                    "action": "Close 50% of position",
                    "remaining_position": position_size * 0.5
                },
                "trailing_stop": {
                    "activation": "After first TP is hit",
                    "percentage": "2% from maximum price",
                    "example_max_price": round(example_max_price, 2),
                    "example_trailing_stop": round(trailing_stop, 2)
                },
                "liquidation": {
                    "price": round(liquidation_price, 2),
                    "distance_from_entry": f"{round(liquidation_move * 100, 2)}%"
                },
                "exit_scenarios": [
                    "1. Liquidation cluster reached (from KingFisher)",
                    "2. Trailing stop triggered (2% from max)",
                    "3. Manual close"
                ],
                "scaling_strategy": {
                    "stage_2": {
                        "trigger": "Near liquidation cluster",
                        "leverage": 10,
                        "additional_margin": margin * 2
                    },
                    "stage_3": {
                        "trigger": "Closer to liquidation",
                        "leverage": 5,
                        "additional_margin": margin * 2
                    },
                    "stage_4": {
                        "trigger": "Very close to liquidation",
                        "leverage": 2,
                        "additional_margin": margin * 2
                    },
                    "final": "Add margin to prevent liquidation"
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error simulating strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))