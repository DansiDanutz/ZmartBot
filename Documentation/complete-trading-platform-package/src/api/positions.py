"""
Trade Strategy Module - Positions API Endpoints
===============================================

API endpoints for position management with CORRECTED profit calculation logic.
All profit calculations are based on TOTAL INVESTED AMOUNT across all scaling stages.

Author: Manus AI
Version: 1.0 Professional Edition - CORRECTED PROFIT CALCULATIONS
Compatibility: Mac Mini 2025 M2 Pro Integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from ..core.config import get_session, get_redis_client
from ..models.positions import (
    Position, PositionScale, PositionCreate, PositionUpdate,
    PositionResponse, PositionScaleResponse, PositionStatus
)
from ..services.position_scaler import PositionScaler, ProfitTakeStage
from ..services.trading_agent import TradingAgent
from ..services.vault_manager import VaultManagerService

router = APIRouter(prefix="/api/v1/positions", tags=["positions"])


@router.get("/", response_model=List[PositionResponse])
async def get_positions(
    vault_id: Optional[str] = Query(None, description="Filter by vault ID"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    status: Optional[PositionStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of positions to return"),
    offset: int = Query(0, ge=0, description="Number of positions to skip"),
    session: Session = Depends(get_session)
):
    """
    Get positions with CORRECTED profit calculations.
    
    Returns positions with accurate profit thresholds based on total invested amount.
    """
    try:
        query = session.query(Position)
        
        # Apply filters
        if vault_id:
            query = query.filter(Position.vault_id == vault_id)
        if symbol:
            query = query.filter(Position.symbol == symbol)
        if status:
            query = query.filter(Position.status == status.value)
        
        # Apply pagination
        positions = query.offset(offset).limit(limit).all()
        
        # Enhance positions with corrected calculations
        enhanced_positions = []
        redis_client = get_redis_client()
        position_scaler = PositionScaler(session, redis_client)
        
        for position in positions:
            # Get position summary with corrected calculations
            summary = position_scaler.get_position_summary(position)
            
            # Convert to response model with corrected data
            position_response = PositionResponse(
                id=str(position.id),
                vault_id=str(position.vault_id),
                symbol=position.symbol,
                direction=position.direction,
                status=position.status,
                average_entry_price=position.average_entry_price,
                current_stage=position.current_stage,
                
                # CORRECTED: Use total invested from summary
                total_investment=Decimal(str(summary["total_invested"])),
                total_position_size=Decimal(str(summary["total_position_value"])),
                
                # CORRECTED: Profit calculations based on total invested
                profit_threshold_75pct=Decimal(str(summary["profit_threshold_75pct"])),
                take_profit_trigger=Decimal(str(summary["first_take_profit_trigger"])),
                
                liquidation_price=position.liquidation_price,
                initial_signal_score=position.initial_signal_score,
                profit_take_stage=position.profit_take_stage,
                total_profit_realized=position.total_profit_realized,
                trailing_stop_price=position.trailing_stop_price,
                additional_margin=position.additional_margin,
                created_at=position.created_at,
                updated_at=position.updated_at,
                last_scaled_at=position.last_scaled_at,
                
                # Additional corrected metadata
                position_metadata={
                    **summary,
                    "corrected_calculations": True,
                    "calculation_method": "total_invested_based"
                }
            )
            
            enhanced_positions.append(position_response)
        
        return enhanced_positions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving positions: {str(e)}")


@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(
    position_id: str = Path(..., description="Position ID"),
    session: Session = Depends(get_session)
):
    """
    Get specific position with CORRECTED profit calculations.
    """
    try:
        position = session.query(Position).filter(Position.id == position_id).first()
        
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        # Get corrected calculations
        redis_client = get_redis_client()
        position_scaler = PositionScaler(session, redis_client)
        summary = position_scaler.get_position_summary(position)
        
        return PositionResponse(
            id=str(position.id),
            vault_id=str(position.vault_id),
            symbol=position.symbol,
            direction=position.direction,
            status=position.status,
            average_entry_price=position.average_entry_price,
            current_stage=position.current_stage,
            total_investment=Decimal(str(summary["total_invested"])),
            total_position_size=Decimal(str(summary["total_position_value"])),
            profit_threshold_75pct=Decimal(str(summary["profit_threshold_75pct"])),
            take_profit_trigger=Decimal(str(summary["first_take_profit_trigger"])),
            liquidation_price=position.liquidation_price,
            initial_signal_score=position.initial_signal_score,
            profit_take_stage=position.profit_take_stage,
            total_profit_realized=position.total_profit_realized,
            trailing_stop_price=position.trailing_stop_price,
            additional_margin=position.additional_margin,
            created_at=position.created_at,
            updated_at=position.updated_at,
            last_scaled_at=position.last_scaled_at,
            position_metadata={
                **summary,
                "corrected_calculations": True,
                "detailed_view": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving position: {str(e)}")


@router.get("/{position_id}/calculations", response_model=Dict[str, Any])
async def get_position_calculations(
    position_id: str = Path(..., description="Position ID"),
    current_price: Optional[Decimal] = Query(None, description="Current market price for calculations"),
    session: Session = Depends(get_session)
):
    """
    Get detailed position calculations with CORRECTED profit logic.
    
    Returns comprehensive calculations including:
    - Total invested amount across all scaling stages
    - 75% profit threshold based on total invested
    - Take profit trigger levels
    - Liquidation calculations
    - Risk metrics
    """
    try:
        position = session.query(Position).filter(Position.id == position_id).first()
        
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        redis_client = get_redis_client()
        position_scaler = PositionScaler(session, redis_client)
        
        # Get vault for bankroll calculation
        from ..models.vaults import Vault
        vault = session.query(Vault).filter(Vault.id == position.vault_id).first()
        vault_bankroll = vault.current_balance if vault else Decimal('10000')
        
        # Use current price if provided, otherwise use entry price
        calc_price = current_price or position.average_entry_price
        
        # Get comprehensive calculations
        calculation = await position_scaler.calculate_position_metrics(
            position, calc_price, vault_bankroll
        )
        
        # Get scaling stages for detailed breakdown
        scales = session.query(PositionScale).filter(
            PositionScale.position_id == position_id
        ).order_by(PositionScale.stage).all()
        
        scaling_breakdown = []
        for scale in scales:
            scaling_breakdown.append({
                "stage": scale.stage,
                "investment_amount": float(scale.investment_amount),
                "leverage": float(scale.leverage),
                "entry_price": float(scale.entry_price),
                "position_value": float(scale.investment_amount * scale.leverage),
                "signal_score": float(scale.signal_score),
                "trigger_reason": scale.trigger_reason
            })
        
        # Check profit taking triggers
        profit_triggers = await position_scaler.check_profit_taking_triggers(
            position, calc_price, vault_bankroll
        )
        
        return {
            "position_id": position_id,
            "calculation_price": float(calc_price),
            "calculation_timestamp": datetime.now(timezone.utc).isoformat(),
            
            # CORRECTED: Investment breakdown
            "investment_breakdown": {
                "total_invested": float(calculation.total_invested),
                "scaling_stages": scaling_breakdown,
                "current_stage": position.current_stage,
                "max_stages": 4
            },
            
            # CORRECTED: Profit calculations
            "profit_calculations": {
                "profit_threshold_75pct": float(calculation.profit_threshold_75pct),
                "take_profit_trigger": float(calculation.first_take_profit_trigger),
                "current_margin": float(calculation.current_margin),
                "profit_amount": float(calculation.current_margin - calculation.total_invested),
                "profit_percentage": float((calculation.current_margin - calculation.total_invested) / calculation.total_invested * 100) if calculation.total_invested > 0 else 0,
                "profit_triggers": profit_triggers
            },
            
            # Position metrics
            "position_metrics": {
                "total_position_value": float(calculation.total_position_value),
                "liquidation_price": float(calculation.liquidation_price),
                "liquidation_distance_pct": float(calculation.liquidation_distance_pct * 100),
                "break_even_price": float(calculation.break_even_price)
            },
            
            # Profit taking structure
            "profit_taking": {
                "first_take_amount": float(calculation.first_take_amount),
                "first_take_percentage": 30.0,
                "second_take_amount": float(calculation.second_take_amount),
                "second_take_percentage": 25.0,
                "final_take_amount": float(calculation.final_take_amount),
                "final_take_percentage": 45.0,
                "trailing_stop_1_pct": float(calculation.trailing_stop_1_pct * 100),
                "trailing_stop_2_pct": float(calculation.trailing_stop_2_pct * 100)
            },
            
            # Risk metrics
            "risk_metrics": {
                "max_loss_amount": float(calculation.max_loss_amount),
                "risk_reward_ratio": float(calculation.risk_reward_ratio),
                "risk_percentage": float(calculation.total_invested / vault_bankroll * 100) if vault_bankroll > 0 else 0
            },
            
            # Calculation metadata
            "calculation_metadata": {
                "method": "corrected_total_invested_based",
                "profit_threshold_method": "75_percent_of_total_invested",
                "scaling_method": "1_2_4_8_percent_bankroll",
                "leverage_sequence": "20x_10x_5x_2x",
                "vault_bankroll": float(vault_bankroll)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating position metrics: {str(e)}")


@router.get("/{position_id}/scaling-stages", response_model=List[PositionScaleResponse])
async def get_position_scaling_stages(
    position_id: str = Path(..., description="Position ID"),
    session: Session = Depends(get_session)
):
    """Get all scaling stages for a position."""
    try:
        position = session.query(Position).filter(Position.id == position_id).first()
        
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        scales = session.query(PositionScale).filter(
            PositionScale.position_id == position_id
        ).order_by(PositionScale.stage).all()
        
        return [
            PositionScaleResponse(
                id=str(scale.id),
                position_id=str(scale.position_id),
                stage=scale.stage,
                investment_amount=scale.investment_amount,
                leverage=scale.leverage,
                entry_price=scale.entry_price,
                signal_score=scale.signal_score,
                trigger_reason=scale.trigger_reason,
                created_at=scale.created_at,
                scaling_metadata=scale.scaling_metadata or {}
            )
            for scale in scales
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving scaling stages: {str(e)}")


@router.post("/{position_id}/scale")
async def scale_position(
    position_id: str = Path(..., description="Position ID"),
    current_price: Decimal = Query(..., description="Current market price"),
    signal_score: Decimal = Query(..., description="Current signal score"),
    session: Session = Depends(get_session)
):
    """
    Scale position with CORRECTED profit calculations.
    
    Evaluates scaling opportunity and executes if recommended.
    Updates profit thresholds based on new total invested amount.
    """
    try:
        position = session.query(Position).filter(Position.id == position_id).first()
        
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        if position.status != PositionStatus.OPEN.value:
            raise HTTPException(status_code=400, detail="Position is not open for scaling")
        
        # Get vault for bankroll
        from ..models.vaults import Vault
        vault = session.query(Vault).filter(Vault.id == position.vault_id).first()
        if not vault:
            raise HTTPException(status_code=404, detail="Vault not found")
        
        redis_client = get_redis_client()
        position_scaler = PositionScaler(session, redis_client)
        
        # Evaluate scaling opportunity
        scaling_decision = await position_scaler.evaluate_scaling_opportunity(
            position, current_price, signal_score, vault.current_balance
        )
        
        if not scaling_decision.should_scale:
            return JSONResponse(
                status_code=200,
                content={
                    "scaled": False,
                    "reason": scaling_decision.risk_assessment,
                    "current_stage": position.current_stage,
                    "max_stages": 4
                }
            )
        
        # Execute scaling
        success, message, new_scale = await position_scaler.execute_position_scaling(
            position, scaling_decision, current_price, vault.current_balance, signal_score
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Get updated calculations
        updated_calculation = await position_scaler.calculate_position_metrics(
            position, current_price, vault.current_balance
        )
        
        return {
            "scaled": True,
            "message": message,
            "new_stage": scaling_decision.recommended_stage,
            "scaling_details": {
                "investment_amount": float(new_scale.investment_amount) if new_scale else 0,
                "leverage": float(new_scale.leverage) if new_scale else 0,
                "trigger_reason": scaling_decision.trigger_reason.value,
                "confidence_score": float(scaling_decision.confidence_score)
            },
            "updated_calculations": {
                "total_invested": float(updated_calculation.total_invested),
                "profit_threshold_75pct": float(updated_calculation.profit_threshold_75pct),
                "take_profit_trigger": float(updated_calculation.first_take_profit_trigger),
                "liquidation_price": float(updated_calculation.liquidation_price)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scaling position: {str(e)}")


@router.post("/{position_id}/take-profit")
async def take_profit(
    position_id: str = Path(..., description="Position ID"),
    current_price: Decimal = Query(..., description="Current market price"),
    profit_stage: Optional[ProfitTakeStage] = Query(None, description="Specific profit stage to execute"),
    session: Session = Depends(get_session)
):
    """
    Execute profit taking with CORRECTED calculations.
    
    Takes profit based on corrected thresholds calculated from total invested amount.
    """
    try:
        position = session.query(Position).filter(Position.id == position_id).first()
        
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        if position.status != PositionStatus.OPEN.value:
            raise HTTPException(status_code=400, detail="Position is not open for profit taking")
        
        # Get vault for bankroll
        from ..models.vaults import Vault
        vault = session.query(Vault).filter(Vault.id == position.vault_id).first()
        if not vault:
            raise HTTPException(status_code=404, detail="Vault not found")
        
        redis_client = get_redis_client()
        position_scaler = PositionScaler(session, redis_client)
        
        # Check profit taking triggers
        triggers = await position_scaler.check_profit_taking_triggers(
            position, current_price, vault.current_balance
        )
        
        if triggers.get("error"):
            raise HTTPException(status_code=400, detail=triggers["error"])
        
        # Determine profit stage if not specified
        if not profit_stage:
            if triggers.get("first_take_profit"):
                profit_stage = ProfitTakeStage.FIRST_TAKE
            elif triggers.get("trailing_stop_1"):
                profit_stage = ProfitTakeStage.SECOND_TAKE
            elif triggers.get("final_take"):
                profit_stage = ProfitTakeStage.FINAL_TAKE
            else:
                return JSONResponse(
                    status_code=200,
                    content={
                        "profit_taken": False,
                        "reason": "No profit taking triggers met",
                        "current_margin": float(triggers.get("current_margin", 0)),
                        "profit_threshold": float(triggers.get("profit_threshold", 0)),
                        "profit_percentage": float(triggers.get("profit_percentage", 0))
                    }
                )
        
        # Calculate take amount
        calculation = await position_scaler.calculate_position_metrics(
            position, current_price, vault.current_balance
        )
        
        if profit_stage == ProfitTakeStage.FIRST_TAKE:
            take_amount = calculation.first_take_amount
        elif profit_stage == ProfitTakeStage.SECOND_TAKE:
            take_amount = calculation.second_take_amount
        else:
            take_amount = calculation.final_take_amount
        
        # Execute profit taking
        success, message, profit_realized = await position_scaler.execute_profit_taking(
            position, profit_stage, current_price, take_amount
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Update vault balance
        vault.current_balance += profit_realized
        if profit_stage == ProfitTakeStage.FINAL_TAKE:
            vault.positions_count -= 1
        
        session.commit()
        
        return {
            "profit_taken": True,
            "message": message,
            "profit_stage": profit_stage.value,
            "profit_details": {
                "amount_closed": float(take_amount),
                "profit_realized": float(profit_realized),
                "profit_percentage": float(triggers.get("profit_percentage", 0)),
                "remaining_position": float(calculation.total_position_value - take_amount) if profit_stage != ProfitTakeStage.FINAL_TAKE else 0
            },
            "updated_vault_balance": float(vault.current_balance),
            "position_status": "closed" if profit_stage == ProfitTakeStage.FINAL_TAKE else "partially_closed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error taking profit: {str(e)}")


@router.post("/{position_id}/add-margin")
async def add_margin(
    position_id: str = Path(..., description="Position ID"),
    current_price: Decimal = Query(..., description="Current market price"),
    session: Session = Depends(get_session)
):
    """Add margin to prevent liquidation when scaling is exhausted."""
    try:
        position = session.query(Position).filter(Position.id == position_id).first()
        
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        if position.status != PositionStatus.OPEN.value:
            raise HTTPException(status_code=400, detail="Position is not open")
        
        # Get vault for bankroll
        from ..models.vaults import Vault
        vault = session.query(Vault).filter(Vault.id == position.vault_id).first()
        if not vault:
            raise HTTPException(status_code=404, detail="Vault not found")
        
        redis_client = get_redis_client()
        position_scaler = PositionScaler(session, redis_client)
        
        # Add margin to prevent liquidation
        success, message, margin_added = await position_scaler.add_margin_to_prevent_liquidation(
            position, current_price, vault.current_balance
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Update vault balance
        vault.current_balance -= margin_added
        session.commit()
        
        return {
            "margin_added": True,
            "message": message,
            "margin_amount": float(margin_added),
            "updated_vault_balance": float(vault.current_balance),
            "total_additional_margin": float(position.additional_margin)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding margin: {str(e)}")


@router.get("/summary/all")
async def get_positions_summary(
    vault_id: Optional[str] = Query(None, description="Filter by vault ID"),
    session: Session = Depends(get_session)
):
    """
    Get comprehensive positions summary with CORRECTED calculations.
    
    Returns summary of all positions with accurate profit metrics based on total invested amounts.
    """
    try:
        query = session.query(Position)
        
        if vault_id:
            query = query.filter(Position.vault_id == vault_id)
        
        positions = query.all()
        
        # Initialize summary metrics
        total_positions = len(positions)
        active_positions = len([p for p in positions if p.status == PositionStatus.OPEN.value])
        closed_positions = len([p for p in positions if p.status == PositionStatus.CLOSED.value])
        
        total_invested = Decimal('0')
        total_profit_targets = Decimal('0')
        total_profit_realized = Decimal('0')
        total_unrealized_pnl = Decimal('0')
        
        redis_client = get_redis_client()
        position_scaler = PositionScaler(session, redis_client)
        
        position_summaries = []
        
        for position in positions:
            if position.status == PositionStatus.OPEN.value:
                # Get corrected calculations for active positions
                summary = position_scaler.get_position_summary(position)
                
                position_total_invested = Decimal(str(summary["total_invested"]))
                position_profit_threshold = Decimal(str(summary["profit_threshold_75pct"]))
                
                total_invested += position_total_invested
                total_profit_targets += position_profit_threshold
                
                position_summaries.append({
                    "position_id": str(position.id),
                    "symbol": position.symbol,
                    "direction": position.direction,
                    "status": position.status,
                    "stage": position.current_stage,
                    "total_invested": float(position_total_invested),
                    "profit_threshold": float(position_profit_threshold),
                    "take_profit_trigger": float(summary["first_take_profit_trigger"]),
                    "liquidation_price": summary.get("liquidation_price")
                })
            
            else:
                # Closed positions
                if position.total_profit_realized:
                    total_profit_realized += position.total_profit_realized
                
                position_summaries.append({
                    "position_id": str(position.id),
                    "symbol": position.symbol,
                    "direction": position.direction,
                    "status": position.status,
                    "profit_realized": float(position.total_profit_realized or 0),
                    "closed_at": position.closed_at.isoformat() if position.closed_at else None
                })
        
        # Calculate performance metrics
        win_rate = Decimal('0')
        if closed_positions > 0:
            winning_positions = len([
                p for p in positions 
                if p.status == PositionStatus.CLOSED.value and (p.total_profit_realized or 0) > 0
            ])
            win_rate = Decimal(str(winning_positions / closed_positions))
        
        return {
            "summary": {
                "total_positions": total_positions,
                "active_positions": active_positions,
                "closed_positions": closed_positions,
                "total_invested": float(total_invested),
                "total_profit_targets": float(total_profit_targets),
                "total_profit_realized": float(total_profit_realized),
                "win_rate": float(win_rate * 100),  # Percentage
                "average_profit_threshold_pct": 75.0  # Always 75% in corrected logic
            },
            "positions": position_summaries,
            "calculation_metadata": {
                "method": "corrected_total_invested_based",
                "profit_calculation": "75_percent_of_total_invested_per_position",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating positions summary: {str(e)}")


# Export router
__all__ = ["router"]

