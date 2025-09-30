#!/usr/bin/env python3
"""
🏦 Vault Management API Routes
Complete vault lifecycle management with Paper and Real money support
"""

import logging
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel, Field
from enum import Enum

from src.services.vault_management_system import (
    vault_management_system,
    VaultType,
    VaultState,
    VaultDuration
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/vault-management", tags=["vault-management"])

# Pydantic models for requests/responses
class CreateVaultRequest(BaseModel):
    """Request to create a new vault"""
    vault_name: str = Field(..., description="Name of the vault")
    vault_type: str = Field(..., description="Type: 'paper' or 'real'")
    duration: str = Field(..., description="Duration: 'week_1', 'week_2', 'month_1', 'month_3'")
    initial_balance: float = Field(0, description="Initial balance (for paper vaults)")
    min_deposit: float = Field(100, description="Minimum deposit amount")
    max_deposit: float = Field(100000, description="Maximum deposit amount")

class DepositRequest(BaseModel):
    """Request to deposit to a vault"""
    vault_id: str
    investor_id: str
    wallet_address: str = Field(..., description="USDT wallet for withdrawals")
    amount: float = Field(..., gt=0, description="Deposit amount in USDT")

class OpenPositionRequest(BaseModel):
    """Request to open position in vault"""
    vault_id: str
    symbol: str
    entry_price: float
    signal_score: int = Field(..., ge=0, le=100, description="Signal score (must be > 80)")

class VaultResponse(BaseModel):
    """Standard vault API response"""
    success: bool
    data: Dict[str, Any]
    message: Optional[str] = None

# API Endpoints

@router.post("/create", response_model=VaultResponse)
async def create_vault(request: CreateVaultRequest):
    """
    Create a new trading vault
    
    Paper vaults: Start with specified initial balance
    Real vaults: Start empty, awaiting deposits
    """
    try:
        # Parse vault type
        vault_type = VaultType.PAPER if request.vault_type.lower() == "paper" else VaultType.REAL
        
        # Parse duration
        duration_map = {
            "week_1": VaultDuration.WEEK_1,
            "week_2": VaultDuration.WEEK_2,
            "month_1": VaultDuration.MONTH_1,
            "month_3": VaultDuration.MONTH_3
        }
        duration = duration_map.get(request.duration.lower())
        if not duration:
            raise ValueError(f"Invalid duration: {request.duration}")
        
        # Create vault
        vault = await vault_management_system.create_vault(
            vault_name=request.vault_name,
            vault_type=vault_type,
            duration=duration,
            initial_balance=Decimal(str(request.initial_balance)),
            min_deposit=Decimal(str(request.min_deposit)),
            max_deposit=Decimal(str(request.max_deposit))
        )
        
        return VaultResponse(
            success=True,
            data={
                "vault_id": vault.vault_id,
                "name": vault.vault_name,
                "type": vault.vault_type.value,
                "duration": vault.duration.label,
                "state": vault.vault_state.value,
                "initial_balance": float(vault.initial_balance),
                "deposit_address": vault.deposit_address,
                "min_deposit": float(vault.min_deposit),
                "max_deposit": float(vault.max_deposit),
                "created_at": vault.created_at.isoformat()
            },
            message=f"{vault_type.value.capitalize()} vault '{request.vault_name}' created successfully"
        )
        
    except Exception as e:
        logger.error(f"Error creating vault: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deposit", response_model=VaultResponse)
async def deposit_to_vault(request: DepositRequest):
    """
    Process investor deposit to vault
    
    - Only allowed during CREATED state
    - Converts deposit to shares based on NAV
    - Records wallet for future withdrawals
    """
    try:
        investor_share = await vault_management_system.deposit_to_vault(
            vault_id=request.vault_id,
            investor_id=request.investor_id,
            wallet_address=request.wallet_address,
            amount=Decimal(str(request.amount))
        )
        
        if not investor_share:
            raise HTTPException(status_code=400, detail="Deposit failed - check vault state and limits")
        
        return VaultResponse(
            success=True,
            data={
                "investor_id": investor_share.investor_id,
                "deposit_amount": float(investor_share.deposit_amount),
                "shares_allocated": float(investor_share.shares),
                "share_percentage": float(investor_share.share_percentage),
                "wallet_address": investor_share.wallet_address,
                "deposit_time": investor_share.deposit_time.isoformat()
            },
            message=f"Deposit of {request.amount} USDT processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing deposit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activate/{vault_id}", response_model=VaultResponse)
async def activate_vault(vault_id: str):
    """
    Activate vault for trading
    
    - Locks deposits
    - Starts trading period
    - Initializes position management
    """
    try:
        success = await vault_management_system.activate_vault(vault_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Cannot activate vault - check state and balance")
        
        vault = vault_management_system.vaults[vault_id]
        
        return VaultResponse(
            success=True,
            data={
                "vault_id": vault_id,
                "state": vault.vault_state.value,
                "activated_at": vault.activated_at.isoformat() if vault.activated_at else None,
                "total_balance": float(vault.current_balance),
                "total_investors": len(vault.investors),
                "duration": vault.duration.label
            },
            message=f"Vault {vault_id} activated for trading"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating vault: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/position/open", response_model=VaultResponse)
async def open_position(request: OpenPositionRequest):
    """
    Open trading position in vault
    
    - Requires signal score > 80
    - Maximum 2 positions per vault
    - Uses 2% of balance at 20X leverage initially
    """
    try:
        position = await vault_management_system.open_position_in_vault(
            vault_id=request.vault_id,
            symbol=request.symbol,
            entry_price=Decimal(str(request.entry_price)),
            signal_score=request.signal_score
        )
        
        if not position:
            raise HTTPException(
                status_code=400, 
                detail="Cannot open position - check signal score and vault limits"
            )
        
        return VaultResponse(
            success=True,
            data={
                "position_id": position.position_id,
                "vault_id": position.vault_id,
                "symbol": position.symbol,
                "entry_price": float(position.current_entry_price),
                "margin_invested": float(position.total_margin_invested),
                "position_size": float(position.total_position_size),
                "leverage": position.current_leverage,
                "stage": position.current_stage.name,
                "tp_price": float(position.current_tp_price),
                "tp_target": float(position.current_tp_target)
            },
            message=f"Position opened with {position.current_leverage}X leverage"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error opening position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete/{vault_id}", response_model=VaultResponse)
async def complete_vault(vault_id: str):
    """
    Complete vault trading period
    
    - Closes all positions
    - Calculates final NAV
    - Applies 10% performance fee (if profitable)
    """
    try:
        success = await vault_management_system.complete_vault(vault_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Cannot complete vault - not in active state")
        
        vault = vault_management_system.vaults[vault_id]
        
        return VaultResponse(
            success=True,
            data={
                "vault_id": vault_id,
                "state": vault.vault_state.value,
                "completed_at": vault.completed_at.isoformat() if vault.completed_at else None,
                "final_nav": float(vault.calculate_nav()),
                "total_pnl": float(vault.performance.total_pnl if vault.performance else 0),
                "pnl_percentage": float(vault.performance.total_pnl_percentage if vault.performance else 0),
                "platform_fee": float(vault.performance.platform_fee if vault.performance else 0),
                "net_distribution": float(vault.performance.net_distribution if vault.performance else 0)
            },
            message=f"Vault {vault_id} completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing vault: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/distribute/{vault_id}", response_model=VaultResponse)
async def distribute_profits(vault_id: str):
    """
    Distribute vault profits to investors
    
    - Calculates each investor's share
    - Sends to original deposit wallets
    - Marks vault as distributed
    """
    try:
        distributions = await vault_management_system.distribute_profits(vault_id)
        
        if not distributions:
            raise HTTPException(status_code=400, detail="Cannot distribute - vault not completed")
        
        vault = vault_management_system.vaults[vault_id]
        
        return VaultResponse(
            success=True,
            data={
                "vault_id": vault_id,
                "state": vault.vault_state.value,
                "distributed_at": vault.distributed_at.isoformat() if vault.distributed_at else None,
                "total_distributed": float(sum(distributions.values())),
                "distributions": [
                    {
                        "investor_id": investor_id,
                        "payout_amount": float(amount),
                        "wallet": vault.investors[investor_id].wallet_address
                    }
                    for investor_id, amount in distributions.items()
                ]
            },
            message=f"Profits distributed to {len(distributions)} investors"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error distributing profits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vault/{vault_id}", response_model=VaultResponse)
async def get_vault_details(vault_id: str):
    """Get complete vault details including performance and investors"""
    try:
        summary = vault_management_system.get_vault_summary(vault_id)
        
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        
        return VaultResponse(
            success=True,
            data=summary,
            message="Vault details retrieved"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vault details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vaults/all", response_model=VaultResponse)
async def get_all_vaults(
    state: Optional[str] = Query(None, description="Filter by state: created, active, completed, distributed")
):
    """Get all vaults with optional state filter"""
    try:
        vaults_data = []
        
        for vault_id, vault in vault_management_system.vaults.items():
            if state:
                if vault.vault_state.value != state.lower():
                    continue
            
            vaults_data.append({
                "vault_id": vault.vault_id,
                "name": vault.vault_name,
                "type": vault.vault_type.value,
                "state": vault.vault_state.value,
                "duration": vault.duration.label,
                "nav": float(vault.calculate_nav()),
                "investors": len(vault.investors),
                "pnl": float(vault.performance.total_pnl if vault.performance else 0),
                "created_at": vault.created_at.isoformat()
            })
        
        return VaultResponse(
            success=True,
            data={
                "count": len(vaults_data),
                "vaults": vaults_data
            },
            message=f"Found {len(vaults_data)} vaults"
        )
        
    except Exception as e:
        logger.error(f"Error getting vaults: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nav/{vault_id}")
async def get_vault_nav(vault_id: str):
    """Get current NAV (Net Asset Value) for vault"""
    try:
        nav = await vault_management_system.update_nav(vault_id)
        
        if nav == Decimal("0"):
            raise HTTPException(status_code=404, detail="Vault not found")
        
        vault = vault_management_system.vaults[vault_id]
        
        return {
            "vault_id": vault_id,
            "nav": float(nav),
            "nav_per_share": float(vault.nav_per_share),
            "total_shares": float(vault.total_shares),
            "last_updated": vault.performance.last_updated.isoformat() if vault.performance else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting NAV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategy/explanation")
async def explain_vault_strategy():
    """Get detailed explanation of vault trading strategy"""
    return {
        "vault_types": {
            "paper": {
                "description": "Paper trading with virtual funds",
                "features": [
                    "No real money required",
                    "Simulated trades with same strategy",
                    "Results count in statistics",
                    "Cannot claim profits"
                ]
            },
            "real": {
                "description": "Real money trading with KuCoin",
                "features": [
                    "Requires USDT deposits",
                    "Live trading on KuCoin Futures",
                    "10% performance fee on profits",
                    "Withdrawals to original wallets"
                ]
            }
        },
        "lifecycle": {
            "created": "Open for deposits, shares allocated by NAV",
            "active": "Trading in progress, deposits locked",
            "completed": "Trading ended, calculating distributions",
            "distributed": "Profits distributed, vault closed"
        },
        "position_strategy": {
            "entry_trigger": "Signal score > 80",
            "max_positions": "2 concurrent positions",
            "scaling_stages": {
                "stage_1": "2% of balance at 20X leverage",
                "stage_2": "4% of balance at 10X leverage (if price drops)",
                "stage_3": "8% of balance at 5X leverage",
                "stage_4": "16% of balance at 2X leverage",
                "reserve": "15% margin injection near liquidation"
            },
            "take_profit": "175% of margin (close 50%)",
            "risk_management": "Maximum 45% exposure per position"
        },
        "fee_structure": {
            "performance_fee": "10% of profits only",
            "no_fee_on_loss": "100% returned if no profit",
            "calculation": "Applied at vault completion"
        },
        "duration_options": [
            {"value": "week_1", "label": "1 Week"},
            {"value": "week_2", "label": "2 Weeks"},
            {"value": "month_1", "label": "1 Month"},
            {"value": "month_3", "label": "3 Months"}
        ]
    }

@router.post("/simulate/vault-scenario")
async def simulate_vault_scenario(
    vault_balance: float = Query(10000, description="Vault starting balance"),
    investor_count: int = Query(5, description="Number of investors"),
    final_pnl_percentage: float = Query(20, description="Final P&L percentage")
):
    """Simulate complete vault scenario with profit distribution"""
    try:
        initial_balance = Decimal(str(vault_balance))
        final_balance = initial_balance * (Decimal("1") + Decimal(str(final_pnl_percentage)) / Decimal("100"))
        profit = final_balance - initial_balance
        
        # Calculate platform fee
        platform_fee = profit * Decimal("0.10") if profit > 0 else Decimal("0")
        net_distribution = final_balance - platform_fee
        
        # Simulate investor shares
        investors = []
        share_per_investor = Decimal("1") / Decimal(str(investor_count))
        
        for i in range(investor_count):
            investor_deposit = initial_balance * share_per_investor
            investor_payout = net_distribution * share_per_investor
            
            investors.append({
                "investor_id": f"INV_{i+1}",
                "deposit": float(investor_deposit),
                "shares": float(investor_deposit),
                "share_percentage": float(share_per_investor * 100),
                "payout": float(investor_payout),
                "profit": float(investor_payout - investor_deposit)
            })
        
        return {
            "vault_simulation": {
                "initial_balance": float(initial_balance),
                "final_balance": float(final_balance),
                "total_pnl": float(profit),
                "pnl_percentage": float(final_pnl_percentage),
                "platform_fee": float(platform_fee),
                "net_distribution": float(net_distribution)
            },
            "investor_distribution": investors,
            "summary": {
                "total_deposits": float(initial_balance),
                "total_distributed": float(net_distribution),
                "platform_earnings": float(platform_fee),
                "investor_returns": f"{float((net_distribution / initial_balance - 1) * 100):.2f}%"
            }
        }
        
    except Exception as e:
        logger.error(f"Error simulating scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))