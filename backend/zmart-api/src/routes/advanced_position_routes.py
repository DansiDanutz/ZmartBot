#!/usr/bin/env python3
"""
Advanced Position Management Routes
Complete trading strategy with position doubling and dynamic TP recalculation
"""

import logging
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel

from src.services.advanced_position_manager import advanced_position_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/advanced-positions", tags=["advanced-positions"])

class OpenPositionRequest(BaseModel):
    """Request to open a new position"""
    symbol: str
    entry_price: float
    margin: float  # Initial margin (X)
    leverage: int = 20

class UpdatePriceRequest(BaseModel):
    """Request to update position with current price"""
    position_id: str
    current_price: float

class PositionResponse(BaseModel):
    """Standard position response"""
    success: bool
    data: Dict[str, Any]
    message: Optional[str] = None

@router.post("/open", response_model=PositionResponse)
async def open_advanced_position(request: OpenPositionRequest):
    """
    Open a new position with complete strategy:
    - Initial 20X leverage with TP at 175% of margin
    - Sets 2 liquidation clusters above and 2 below
    - Ready for position doubling at lower clusters
    """
    try:
        position = await advanced_position_manager.open_position(
            symbol=request.symbol,
            entry_price=Decimal(str(request.entry_price)),
            margin=Decimal(str(request.margin)),
            leverage=request.leverage
        )
        
        return PositionResponse(
            success=True,
            data={
                "position_id": position.position_id,
                "symbol": position.symbol,
                "entry_price": float(position.current_entry_price),
                "margin": float(position.total_margin_invested),
                "leverage": position.current_leverage,
                "position_size": float(position.total_position_size),
                "tp_price": float(position.current_tp_price),
                "tp_target": float(position.current_tp_target),
                "clusters_above": [
                    {"price": float(c.price_level), "type": c.cluster_type, "strength": c.strength}
                    for c in position.clusters_above
                ],
                "clusters_below": [
                    {"price": float(c.price_level), "type": c.cluster_type, "strength": c.strength}
                    for c in position.clusters_below
                ],
                "strategy": {
                    "first_tp": "Close 50% at 175% of margin",
                    "after_tp": "Exit at upper liquidation clusters with trailing stop",
                    "if_down": "Double position at lower clusters with 10X, 5X, 2X",
                    "recalculation": "New TP calculated for combined position after doubling"
                }
            },
            message=f"Position opened with {request.leverage}X leverage"
        )
        
    except Exception as e:
        logger.error(f"Error opening position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update", response_model=PositionResponse)
async def update_position_price(request: UpdatePriceRequest):
    """
    Update position with current price
    Automatically handles:
    - First TP at 175% (closes 50%)
    - Position doubling at lower clusters
    - Exit at upper clusters after TP
    - Trailing stop management
    """
    try:
        result = await advanced_position_manager.update_position(
            position_id=request.position_id,
            current_price=Decimal(str(request.current_price))
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return PositionResponse(
            success=True,
            data=result,
            message="Position updated"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{position_id}", response_model=PositionResponse)
async def get_position_details(position_id: str):
    """Get complete position details including doubling history"""
    try:
        details = advanced_position_manager.get_position_details(position_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Position not found")
        
        return PositionResponse(
            success=True,
            data=details,
            message="Position details retrieved"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting position details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active/all", response_model=PositionResponse)
async def get_all_active_positions():
    """Get all active positions"""
    try:
        positions = []
        for position_id in advanced_position_manager.active_positions:
            details = advanced_position_manager.get_position_details(position_id)
            if details:
                positions.append(details)
        
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

@router.post("/simulate")
async def simulate_complete_strategy(
    entry_price: float = Query(50000, description="Entry price"),
    margin: float = Query(500, description="Initial margin (X)"),
    simulate_doubling: bool = Query(True, description="Simulate position doubling")
):
    """
    Simulate the complete trading strategy with all scenarios
    """
    try:
        # Initial position
        position_size = margin * 20  # 20X leverage
        tp_target = margin * 1.75  # 175% of margin
        profit_needed = tp_target - margin
        tp_price = entry_price * (1 + profit_needed / position_size)
        
        simulation = {
            "initial_position": {
                "entry_price": entry_price,
                "margin": margin,
                "leverage": 20,
                "position_size": position_size,
                "tp_price": round(tp_price, 2),
                "tp_target": tp_target,
                "tp_profit": tp_target - margin
            },
            "clusters": {
                "above": [
                    {"price": round(entry_price * 1.03, 2), "purpose": "Exit after TP"},
                    {"price": round(entry_price * 1.05, 2), "purpose": "Exit after TP"}
                ],
                "below": [
                    {"price": round(entry_price * 0.97, 2), "purpose": "Double with 10X"},
                    {"price": round(entry_price * 0.95, 2), "purpose": "Double with 5X"}
                ]
            },
            "scenario_1_profit": {
                "description": "Price goes up to TP",
                "action_1": f"Close 50% at {round(tp_price, 2)}",
                "action_2": "Activate trailing stop at 2% below max",
                "action_3": "Exit remaining at upper cluster or trailing stop"
            }
        }
        
        if simulate_doubling:
            # Simulate doubling at first lower cluster
            double_price = entry_price * 0.97
            additional_margin = margin * 2  # Double original margin
            additional_size = additional_margin * 10  # 10X leverage
            
            # New combined position
            total_margin = margin + additional_margin
            total_size = position_size + additional_size
            
            # Weighted average entry
            avg_entry = (position_size * entry_price + additional_size * double_price) / total_size
            
            # New TP for combined position
            new_tp_target = total_margin * 1.75
            new_profit_needed = new_tp_target - total_margin
            new_tp_price = avg_entry * (1 + new_profit_needed / total_size)
            
            simulation["scenario_2_doubling"] = {
                "description": "Price drops to first lower cluster",
                "trigger_price": round(double_price, 2),
                "action": "Double position with 10X leverage",
                "additional_margin": additional_margin,
                "additional_size": additional_size,
                "new_combined_position": {
                    "total_margin": total_margin,
                    "total_size": total_size,
                    "avg_entry": round(avg_entry, 2),
                    "new_tp_price": round(new_tp_price, 2),
                    "new_tp_target": new_tp_target,
                    "new_clusters": {
                        "above": [
                            {"price": round(avg_entry * 1.03, 2)},
                            {"price": round(avg_entry * 1.05, 2)}
                        ],
                        "below": [
                            {"price": round(avg_entry * 0.97, 2), "action": "Double with 5X"},
                            {"price": round(avg_entry * 0.95, 2), "action": "Double with 2X"}
                        ]
                    }
                },
                "progression": [
                    "Stage 1: Initial 20X",
                    "Stage 2: Double with 10X at lower cluster",
                    "Stage 3: Double with 5X if continues down",
                    "Stage 4: Double with 2X if further down",
                    "Stage 5: Add margin to prevent liquidation"
                ]
            }
        
        simulation["key_rules"] = [
            "Always close 50% at 175% of total margin",
            "After TP, only exit at upper clusters or trailing stop",
            "Each doubling creates new combined position with new TP",
            "Clusters are recalculated after each position change",
            "Maximum 4 doublings before just adding margin"
        ]
        
        return simulation
        
    except Exception as e:
        logger.error(f"Error simulating strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategy/explanation")
async def explain_strategy():
    """Get detailed explanation of the trading strategy"""
    return {
        "strategy_name": "Dynamic Position Doubling with Liquidation Clusters",
        "overview": "Advanced strategy that uses liquidation clusters for entries and exits with dynamic position sizing",
        "initial_entry": {
            "leverage": "20X",
            "take_profit": "175% of margin (close 50%)",
            "clusters": "Track 2 above and 2 below entry"
        },
        "profit_scenario": {
            "step_1": "Hit TP at 175% → Close 50% of position",
            "step_2": "Activate 2% trailing stop",
            "step_3": "Exit remaining at upper liquidation cluster",
            "step_4": "If no cluster hit, trailing stop exits at 98% of max price"
        },
        "loss_scenario": {
            "step_1": "Price hits lower cluster → Double position",
            "step_2": "Use decreasing leverage: 10X → 5X → 2X",
            "step_3": "Recalculate TP for combined position",
            "step_4": "Update clusters (2 up, 2 down) from new average entry",
            "step_5": "Final stage: Add margin to avoid liquidation"
        },
        "key_features": [
            "Dynamic TP recalculation after each doubling",
            "Weighted average entry price for combined positions",
            "Automatic cluster updates every 10 minutes",
            "Maximum 4 doubling stages before margin addition",
            "Each doubling creates a new unified position"
        ],
        "risk_management": [
            "50% position reduction at first TP",
            "2% trailing stop after profit taking",
            "Decreasing leverage on doubles (20X→10X→5X→2X)",
            "Exit at liquidation clusters for controlled exits",
            "Final margin addition to prevent liquidation"
        ]
    }