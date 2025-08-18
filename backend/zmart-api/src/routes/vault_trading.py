#!/usr/bin/env python3
"""
Vault Trading Routes - Complete Position Management with Balance-Based Sizing
Maximum 2 positions per vault with percentage-based position sizing
"""

import logging
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel

from src.services.vault_position_manager import vault_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/vault-trading", tags=["vault-trading"])

class CreateVaultRequest(BaseModel):
    """Request to create a new trading vault"""
    name: str
    initial_balance: float

class OpenVaultPositionRequest(BaseModel):
    """Request to open position in vault"""
    vault_id: str
    symbol: str
    entry_price: float

class UpdateVaultPositionRequest(BaseModel):
    """Request to update vault position with current price"""
    position_id: str
    current_price: float

class VaultResponse(BaseModel):
    """Standard vault response"""
    success: bool
    data: Dict[str, Any]
    message: Optional[str] = None

@router.post("/vault/create", response_model=VaultResponse)
async def create_vault(request: CreateVaultRequest):
    """
    Create a new trading vault with initial balance
    - Maximum 2 positions per vault
    - Balance-based position sizing
    """
    try:
        vault = await vault_manager.create_vault(
            name=request.name,
            initial_balance=Decimal(str(request.initial_balance))
        )
        
        return VaultResponse(
            success=True,
            data={
                "vault_id": vault.vault_id,
                "name": vault.name,
                "total_balance": float(vault.total_balance),
                "available_balance": float(vault.available_balance),
                "reserved_balance": float(vault.reserved_balance),
                "max_positions": vault.max_positions,
                "created_at": vault.created_at.isoformat()
            },
            message=f"Vault '{request.name}' created successfully"
        )
        
    except Exception as e:
        logger.error(f"Error creating vault: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/position/open", response_model=VaultResponse)
async def open_vault_position(request: OpenVaultPositionRequest):
    """
    Open position in vault with automatic sizing:
    - Initial: 2% of vault balance at 20X leverage
    - Checks vault has < 2 positions
    - Sets up liquidation clusters and TP at 175%
    """
    try:
        position = await vault_manager.open_position(
            vault_id=request.vault_id,
            symbol=request.symbol,
            entry_price=Decimal(str(request.entry_price))
        )
        
        if not position:
            raise HTTPException(
                status_code=400, 
                detail="Cannot open position - vault at maximum capacity or insufficient balance"
            )
        
        vault = vault_manager.vaults[request.vault_id]
        
        return VaultResponse(
            success=True,
            data={
                "position": {
                    "position_id": position.position_id,
                    "vault_id": position.vault_id,
                    "symbol": position.symbol,
                    "entry_price": float(position.current_entry_price),
                    "margin_invested": float(position.total_margin_invested),
                    "position_size": float(position.total_position_size),
                    "leverage": position.current_leverage,
                    "stage": position.current_stage.name,
                    "tp_price": float(position.current_tp_price),
                    "tp_target": float(position.current_tp_target),
                    "liquidation_price": float(position.liquidation_price),
                    "clusters_above": [
                        {"price": float(c.price_level), "strength": c.strength}
                        for c in position.clusters_above
                    ],
                    "clusters_below": [
                        {"price": float(c.price_level), "strength": c.strength}
                        for c in position.clusters_below
                    ]
                },
                "vault_status": {
                    "vault_id": vault.vault_id,
                    "available_balance": float(vault.available_balance),
                    "reserved_balance": float(vault.reserved_balance),
                    "active_positions": f"{len(vault.active_positions)}/{vault.max_positions}",
                    "balance_used_percentage": float(position.balance_percentages.get(position.current_stage.name, 0)) * 100
                }
            },
            message=f"Position opened: 2% of balance ({position.total_margin_invested}) at 20X"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error opening vault position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/position/update", response_model=VaultResponse)
async def update_vault_position(request: UpdateVaultPositionRequest):
    """
    Update vault position with current price
    Handles:
    - First TP at 175% (close 50%)
    - Position doubling at lower clusters (4%, 8%, 16% of balance)
    - 15% margin addition when close to liquidation
    - Exit at upper clusters or trailing stop
    """
    try:
        result = await vault_manager.update_position(
            position_id=request.position_id,
            current_price=Decimal(str(request.current_price))
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return VaultResponse(
            success=True,
            data=result,
            message="Position updated"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating vault position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vault/{vault_id}/status", response_model=VaultResponse)
async def get_vault_status(vault_id: str):
    """Get complete vault status with all positions"""
    try:
        status = vault_manager.get_vault_status(vault_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Vault not found")
        
        return VaultResponse(
            success=True,
            data=status,
            message="Vault status retrieved"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vault status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vaults/all", response_model=VaultResponse)
async def get_all_vaults():
    """Get all vaults with their status"""
    try:
        vaults_data = []
        for vault_id in vault_manager.vaults:
            status = vault_manager.get_vault_status(vault_id)
            if status:
                vaults_data.append(status)
        
        return VaultResponse(
            success=True,
            data={
                "count": len(vaults_data),
                "vaults": vaults_data
            },
            message=f"Found {len(vaults_data)} vaults"
        )
        
    except Exception as e:
        logger.error(f"Error getting all vaults: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategy/breakdown")
async def get_strategy_breakdown():
    """Get detailed breakdown of the vault trading strategy"""
    return {
        "vault_system": {
            "max_positions_per_vault": 2,
            "position_sizing": {
                "stage_1_initial": {
                    "balance_percentage": "2%",
                    "leverage": 20,
                    "description": "Initial entry with 2% of total balance"
                },
                "stage_2_double": {
                    "balance_percentage": "4%",
                    "leverage": 10,
                    "trigger": "Lower liquidation cluster hit",
                    "description": "First doubling with 4% of balance"
                },
                "stage_3_double": {
                    "balance_percentage": "8%",
                    "leverage": 5,
                    "trigger": "Second lower cluster hit",
                    "description": "Second doubling with 8% of balance"
                },
                "stage_4_double": {
                    "balance_percentage": "16%",
                    "leverage": 2,
                    "trigger": "Third lower cluster hit",
                    "description": "Final doubling with 16% of balance"
                },
                "emergency_margin": {
                    "balance_percentage": "15%",
                    "trigger": "Within 1% of liquidation",
                    "description": "Add margin to prevent liquidation"
                }
            }
        },
        "trading_strategy": {
            "entry": {
                "trigger": "Trading Agent score > 80",
                "initial_size": "2% of vault balance",
                "initial_leverage": "20X"
            },
            "take_profit": {
                "first_tp": "175% of total margin invested",
                "action": "Close 50% of position",
                "after_tp": "Activate 2% trailing stop"
            },
            "position_management": {
                "upper_clusters": "Exit targets after TP",
                "lower_clusters": "Doubling triggers",
                "cluster_updates": "Every 10 minutes from KingFisher",
                "trailing_stop": "2% from maximum price"
            },
            "risk_management": {
                "max_positions": 2,
                "total_max_exposure": "45% of balance (2% + 4% + 8% + 16% + 15%)",
                "per_position_max": "45% if all stages triggered",
                "liquidation_prevention": "15% margin addition"
            }
        },
        "example_10k_vault": {
            "stage_1": {"amount": 200, "leverage": 20, "position": 4000},
            "stage_2": {"amount": 400, "leverage": 10, "position": 4000},
            "stage_3": {"amount": 800, "leverage": 5, "position": 4000},
            "stage_4": {"amount": 1600, "leverage": 2, "position": 3200},
            "emergency": {"amount": 1500, "purpose": "Prevent liquidation"},
            "total_deployed": 4500,
            "remaining_balance": 5500
        }
    }

@router.post("/simulate/full-scenario")
async def simulate_full_scenario(
    vault_balance: float = Query(10000, description="Vault balance"),
    entry_price: float = Query(50000, description="Entry price"),
    symbol: str = Query("BTC/USDT", description="Trading symbol")
):
    """Simulate complete vault trading scenario with all stages"""
    try:
        # Stage 1: Initial entry
        stage1_margin = vault_balance * 0.02
        stage1_size = stage1_margin * 20
        stage1_tp_target = stage1_margin * 1.75
        stage1_tp_price = entry_price * (1 + (stage1_tp_target - stage1_margin) / stage1_size)
        
        # Simulate doubling stages
        stages = []
        total_margin = stage1_margin
        total_size = stage1_size
        current_entry = entry_price
        
        # Stage 2: First double at 97% of entry
        stage2_price = entry_price * 0.97
        stage2_margin = vault_balance * 0.04
        stage2_size = stage2_margin * 10
        
        # Calculate combined position after first double
        combined_value = stage1_size * entry_price + stage2_size * stage2_price
        combined_size = stage1_size + stage2_size
        combined_margin = stage1_margin + stage2_margin
        combined_entry = combined_value / combined_size
        combined_tp_target = combined_margin * 1.75
        combined_tp_price = combined_entry * (1 + (combined_tp_target - combined_margin) / combined_size)
        
        return {
            "vault_balance": vault_balance,
            "initial_entry": {
                "price": entry_price,
                "margin": stage1_margin,
                "leverage": 20,
                "position_size": stage1_size,
                "tp_price": round(stage1_tp_price, 2),
                "tp_target": stage1_tp_target,
                "clusters": {
                    "above": [entry_price * 1.03, entry_price * 1.05],
                    "below": [entry_price * 0.97, entry_price * 0.95]
                }
            },
            "first_double_scenario": {
                "trigger_price": stage2_price,
                "additional_margin": stage2_margin,
                "additional_leverage": 10,
                "additional_size": stage2_size,
                "combined_position": {
                    "total_margin": combined_margin,
                    "total_size": combined_size,
                    "avg_entry": round(combined_entry, 2),
                    "new_tp_price": round(combined_tp_price, 2),
                    "new_tp_target": combined_tp_target,
                    "balance_used": f"{(combined_margin/vault_balance)*100:.1f}%"
                }
            },
            "all_stages_summary": {
                "stage_1": {"balance%": "2%", "amount": stage1_margin, "leverage": 20},
                "stage_2": {"balance%": "4%", "amount": vault_balance * 0.04, "leverage": 10},
                "stage_3": {"balance%": "8%", "amount": vault_balance * 0.08, "leverage": 5},
                "stage_4": {"balance%": "16%", "amount": vault_balance * 0.16, "leverage": 2},
                "emergency": {"balance%": "15%", "amount": vault_balance * 0.15, "leverage": 0},
                "total_potential": {
                    "amount": vault_balance * 0.45,
                    "percentage": "45% of vault balance"
                }
            },
            "position_limit": {
                "max_concurrent": 2,
                "per_position_max": "45% of balance",
                "both_positions_max": "90% of balance",
                "reserved_buffer": "10% minimum"
            }
        }
        
    except Exception as e:
        logger.error(f"Error simulating scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))