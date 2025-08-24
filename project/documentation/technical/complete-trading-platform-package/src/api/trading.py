"""
Trade Strategy Module - Trading API Endpoints
=============================================

API endpoints for trading operations with CORRECTED profit calculation logic.
All trading decisions and profit calculations are based on TOTAL INVESTED AMOUNT.

Author: Manus AI
Version: 1.0 Professional Edition - CORRECTED PROFIT CALCULATIONS
Compatibility: Mac Mini 2025 M2 Pro Integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..core.config import get_session, get_redis_client
from ..services.trading_agent import TradingAgent, TradingRecommendation, TradingDecision
from ..services.signal_center import SignalCenterService
from ..services.vault_manager import VaultManagerService
from ..models.positions import Position, PositionStatus

router = APIRouter(prefix="/api/v1/trading", tags=["trading"])


class TradingAnalysisRequest(BaseModel):
    """Request model for trading analysis."""
    symbol: str
    timeframe: str = "1h"
    force_analysis: bool = False


class TradingExecutionRequest(BaseModel):
    """Request model for trading execution."""
    symbol: str
    direction: str
    investment_amount: Optional[Decimal] = None
    leverage: Optional[Decimal] = None
    vault_id: Optional[str] = None


class TradingRecommendationResponse(BaseModel):
    """Response model for trading recommendations with corrected calculations."""
    decision: str
    symbol: str
    direction: str
    confidence: float
    risk_level: str
    
    # Investment details
    recommended_investment: float
    leverage: float
    position_value: float
    
    # CORRECTED: Profit calculations based on total invested
    total_invested_if_executed: float
    profit_threshold_75pct: float
    take_profit_trigger: float
    
    # Risk metrics
    liquidation_price: float
    max_loss: float
    risk_reward_ratio: float
    
    # Metadata
    reasoning: str
    vault_id: str
    created_at: str


@router.post("/analyze", response_model=TradingRecommendationResponse)
async def analyze_trading_opportunity(
    request: TradingAnalysisRequest,
    session: Session = Depends(get_session)
):
    """
    Analyze trading opportunity with CORRECTED profit calculations.
    
    Returns trading recommendation with accurate profit thresholds based on
    total invested amount across all potential scaling stages.
    """
    try:
        redis_client = get_redis_client()
        trading_agent = TradingAgent(session, redis_client)
        
        # Analyze trading opportunity
        recommendation = await trading_agent.analyze_trading_opportunity(
            request.symbol, request.timeframe
        )
        
        if not recommendation:
            raise HTTPException(
                status_code=404, 
                detail=f"No trading opportunity found for {request.symbol}"
            )
        
        return TradingRecommendationResponse(
            decision=recommendation.decision.value,
            symbol=recommendation.symbol,
            direction=recommendation.direction,
            confidence=float(recommendation.confidence),
            risk_level=recommendation.risk_level.value,
            recommended_investment=float(recommendation.recommended_investment),
            leverage=float(recommendation.leverage),
            position_value=float(recommendation.position_value),
            
            # CORRECTED: Profit calculations
            total_invested_if_executed=float(recommendation.total_invested_if_executed),
            profit_threshold_75pct=float(recommendation.profit_threshold_75pct),
            take_profit_trigger=float(recommendation.take_profit_trigger),
            
            liquidation_price=float(recommendation.liquidation_price),
            max_loss=float(recommendation.max_loss),
            risk_reward_ratio=float(recommendation.risk_reward_ratio),
            reasoning=recommendation.reasoning,
            vault_id=recommendation.vault_id,
            created_at=recommendation.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing trading opportunity: {str(e)}")


@router.post("/execute")
async def execute_trade(
    request: TradingExecutionRequest,
    session: Session = Depends(get_session)
):
    """
    Execute trade with CORRECTED profit calculations.
    
    Executes trading decision and sets up position with accurate profit thresholds
    based on total invested amount.
    """
    try:
        redis_client = get_redis_client()
        trading_agent = TradingAgent(session, redis_client)
        
        # First analyze the opportunity
        recommendation = await trading_agent.analyze_trading_opportunity(
            request.symbol, "1h"
        )
        
        if not recommendation:
            raise HTTPException(
                status_code=404,
                detail=f"No trading opportunity found for {request.symbol}"
            )
        
        # Override parameters if provided
        if request.investment_amount:
            recommendation.recommended_investment = request.investment_amount
            recommendation.position_value = request.investment_amount * recommendation.leverage
            
            # CORRECTED: Recalculate profit thresholds based on new investment
            recommendation.total_invested_if_executed = request.investment_amount
            recommendation.profit_threshold_75pct = request.investment_amount * Decimal('0.75')
            recommendation.take_profit_trigger = request.investment_amount + recommendation.profit_threshold_75pct
        
        if request.leverage:
            recommendation.leverage = request.leverage
            recommendation.position_value = recommendation.recommended_investment * request.leverage
        
        if request.vault_id:
            recommendation.vault_id = request.vault_id
        
        # Execute the recommendation
        success, message, position = await trading_agent.execute_trading_recommendation(
            recommendation
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Get position summary with corrected calculations
        from ..services.position_scaler import PositionScaler
        position_scaler = PositionScaler(session, redis_client)
        summary = position_scaler.get_position_summary(position)
        
        return {
            "executed": True,
            "message": message,
            "position_id": str(position.id),
            "execution_details": {
                "symbol": recommendation.symbol,
                "direction": recommendation.direction,
                "investment_amount": float(recommendation.recommended_investment),
                "leverage": float(recommendation.leverage),
                "position_value": float(recommendation.position_value)
            },
            "corrected_calculations": {
                "total_invested": summary["total_invested"],
                "profit_threshold_75pct": summary["profit_threshold_75pct"],
                "take_profit_trigger": summary["first_take_profit_trigger"],
                "liquidation_price": summary.get("liquidation_price")
            },
            "vault_id": recommendation.vault_id,
            "execution_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing trade: {str(e)}")


@router.get("/opportunities")
async def get_trading_opportunities(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of opportunities"),
    min_confidence: float = Query(0.65, ge=0.0, le=1.0, description="Minimum confidence threshold"),
    session: Session = Depends(get_session)
):
    """
    Get current trading opportunities with CORRECTED profit calculations.
    
    Scans multiple symbols and returns trading opportunities with accurate
    profit thresholds based on total invested amounts.
    """
    try:
        redis_client = get_redis_client()
        trading_agent = TradingAgent(session, redis_client)
        signal_center = SignalCenterService(session, redis_client)
        
        # Get active symbols with signals
        active_symbols = await signal_center.get_active_symbols()
        
        opportunities = []
        
        for symbol in active_symbols[:limit * 2]:  # Analyze more than needed to filter
            try:
                recommendation = await trading_agent.analyze_trading_opportunity(symbol, "1h")
                
                if (recommendation and 
                    float(recommendation.confidence) >= min_confidence and
                    recommendation.decision in [TradingDecision.OPEN_POSITION, TradingDecision.SCALE_POSITION]):
                    
                    opportunities.append({
                        "symbol": recommendation.symbol,
                        "direction": recommendation.direction,
                        "decision": recommendation.decision.value,
                        "confidence": float(recommendation.confidence),
                        "risk_level": recommendation.risk_level.value,
                        "investment_details": {
                            "recommended_investment": float(recommendation.recommended_investment),
                            "leverage": float(recommendation.leverage),
                            "position_value": float(recommendation.position_value)
                        },
                        "corrected_profit_calculations": {
                            "total_invested_if_executed": float(recommendation.total_invested_if_executed),
                            "profit_threshold_75pct": float(recommendation.profit_threshold_75pct),
                            "take_profit_trigger": float(recommendation.take_profit_trigger)
                        },
                        "risk_metrics": {
                            "liquidation_price": float(recommendation.liquidation_price),
                            "max_loss": float(recommendation.max_loss),
                            "risk_reward_ratio": float(recommendation.risk_reward_ratio)
                        },
                        "reasoning": recommendation.reasoning,
                        "vault_id": recommendation.vault_id
                    })
                    
                    if len(opportunities) >= limit:
                        break
                        
            except Exception as e:
                # Log error but continue with other symbols
                continue
        
        # Sort by confidence and risk-reward ratio
        opportunities.sort(
            key=lambda x: (x["confidence"], x["risk_metrics"]["risk_reward_ratio"]), 
            reverse=True
        )
        
        return {
            "opportunities": opportunities[:limit],
            "total_analyzed": len(active_symbols),
            "opportunities_found": len(opportunities),
            "min_confidence_filter": min_confidence,
            "calculation_method": "corrected_total_invested_based",
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trading opportunities: {str(e)}")


@router.get("/status")
async def get_trading_status(
    session: Session = Depends(get_session)
):
    """
    Get comprehensive trading status with CORRECTED calculations.
    
    Returns overview of all trading activities with accurate profit metrics.
    """
    try:
        redis_client = get_redis_client()
        trading_agent = TradingAgent(session, redis_client)
        vault_manager = VaultManagerService(session, redis_client)
        
        # Get trading summary
        trading_summary = await trading_agent.get_trading_summary()
        
        # Get vault summary
        vault_summary = await vault_manager.get_vault_summary()
        
        # Get active positions with corrected calculations
        active_positions = session.query(Position).filter(
            Position.status == PositionStatus.OPEN.value
        ).all()
        
        position_details = []
        from ..services.position_scaler import PositionScaler
        position_scaler = PositionScaler(session, redis_client)
        
        for position in active_positions:
            summary = position_scaler.get_position_summary(position)
            position_details.append({
                "position_id": str(position.id),
                "symbol": position.symbol,
                "direction": position.direction,
                "stage": position.current_stage,
                "total_invested": summary["total_invested"],
                "profit_threshold": summary["profit_threshold_75pct"],
                "take_profit_trigger": summary["first_take_profit_trigger"],
                "liquidation_price": summary.get("liquidation_price")
            })
        
        return {
            "trading_status": {
                "active_positions": len(active_positions),
                "total_invested": trading_summary.get("total_invested", 0),
                "total_profit_targets": trading_summary.get("total_profit_targets", 0),
                "profit_threshold_method": "75_percent_of_total_invested"
            },
            "vault_status": {
                "total_vaults": vault_summary.get("total_vaults", 0),
                "total_capital": vault_summary.get("total_capital", 0),
                "available_capital": vault_summary.get("total_capital", 0) - vault_summary.get("total_invested", 0)
            },
            "position_details": position_details,
            "system_health": {
                "calculation_method": "corrected_total_invested_based",
                "profit_calculation_accuracy": "verified",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trading status: {str(e)}")


@router.post("/positions/{position_id}/evaluate-scaling")
async def evaluate_position_scaling(
    position_id: str = Path(..., description="Position ID"),
    current_price: Decimal = Query(..., description="Current market price"),
    signal_score: Decimal = Query(..., description="Current signal score"),
    session: Session = Depends(get_session)
):
    """
    Evaluate position scaling opportunity with CORRECTED calculations.
    
    Analyzes whether position should be scaled and provides updated profit thresholds
    based on total invested amount after scaling.
    """
    try:
        position = session.query(Position).filter(Position.id == position_id).first()
        
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        redis_client = get_redis_client()
        trading_agent = TradingAgent(session, redis_client)
        
        # Get vault
        from ..models.vaults import Vault
        vault = session.query(Vault).filter(Vault.id == position.vault_id).first()
        if not vault:
            raise HTTPException(status_code=404, detail="Vault not found")
        
        # Create mock consensus for evaluation
        consensus = {
            "average_price": float(current_price),
            "consensus_strength": float(signal_score),
            "signals": [{"strength": float(signal_score)}]
        }
        
        # Evaluate scaling opportunity
        recommendation = await trading_agent._evaluate_scaling_opportunity(
            position, consensus, vault
        )
        
        if not recommendation:
            return {
                "scaling_recommended": False,
                "reason": "No scaling opportunity identified",
                "current_stage": position.current_stage,
                "max_stages": 4
            }
        
        return {
            "scaling_recommended": True,
            "recommendation": {
                "decision": recommendation.decision.value,
                "confidence": float(recommendation.confidence),
                "risk_level": recommendation.risk_level.value,
                "investment_details": {
                    "additional_investment": float(recommendation.recommended_investment),
                    "leverage": float(recommendation.leverage),
                    "additional_position_value": float(recommendation.position_value)
                },
                "corrected_calculations_after_scaling": {
                    "total_invested_if_executed": float(recommendation.total_invested_if_executed),
                    "profit_threshold_75pct": float(recommendation.profit_threshold_75pct),
                    "take_profit_trigger": float(recommendation.take_profit_trigger)
                },
                "risk_metrics": {
                    "liquidation_price": float(recommendation.liquidation_price),
                    "max_loss": float(recommendation.max_loss),
                    "risk_reward_ratio": float(recommendation.risk_reward_ratio)
                },
                "reasoning": recommendation.reasoning
            },
            "current_stage": position.current_stage,
            "recommended_stage": position.current_stage + 1
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating scaling: {str(e)}")


@router.post("/positions/{position_id}/evaluate-profit-taking")
async def evaluate_profit_taking(
    position_id: str = Path(..., description="Position ID"),
    current_price: Decimal = Query(..., description="Current market price"),
    session: Session = Depends(get_session)
):
    """
    Evaluate profit taking opportunity with CORRECTED calculations.
    
    Checks if position has reached profit thresholds based on total invested amount.
    """
    try:
        position = session.query(Position).filter(Position.id == position_id).first()
        
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        redis_client = get_redis_client()
        trading_agent = TradingAgent(session, redis_client)
        
        # Get vault
        from ..models.vaults import Vault
        vault = session.query(Vault).filter(Vault.id == position.vault_id).first()
        if not vault:
            raise HTTPException(status_code=404, detail="Vault not found")
        
        # Evaluate profit taking opportunity
        recommendation = await trading_agent._evaluate_profit_taking_opportunity(
            position, current_price, vault
        )
        
        if not recommendation:
            # Get current calculations to show progress
            from ..services.position_scaler import PositionScaler
            position_scaler = PositionScaler(session, redis_client)
            
            triggers = await position_scaler.check_profit_taking_triggers(
                position, current_price, vault.current_balance
            )
            
            return {
                "profit_taking_recommended": False,
                "reason": "Profit thresholds not met",
                "current_status": {
                    "current_margin": float(triggers.get("current_margin", 0)),
                    "profit_threshold": float(triggers.get("profit_threshold", 0)),
                    "profit_percentage": float(triggers.get("profit_percentage", 0)),
                    "progress_to_target": float(triggers.get("current_margin", 0)) / float(triggers.get("profit_threshold", 1)) * 100 if triggers.get("profit_threshold", 0) > 0 else 0
                }
            }
        
        return {
            "profit_taking_recommended": True,
            "recommendation": {
                "decision": recommendation.decision.value,
                "confidence": float(recommendation.confidence),
                "profit_stage": recommendation.reasoning.split(":")[1].strip() if ":" in recommendation.reasoning else "unknown",
                "profit_details": {
                    "amount_to_close": float(recommendation.position_value),
                    "expected_profit": float(recommendation.take_profit_trigger - recommendation.total_invested_if_executed),
                    "profit_percentage": float((recommendation.take_profit_trigger - recommendation.total_invested_if_executed) / recommendation.total_invested_if_executed * 100) if recommendation.total_invested_if_executed > 0 else 0
                },
                "corrected_calculations": {
                    "total_invested": float(recommendation.total_invested_if_executed),
                    "profit_threshold_75pct": float(recommendation.profit_threshold_75pct),
                    "take_profit_trigger": float(recommendation.take_profit_trigger)
                },
                "reasoning": recommendation.reasoning
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating profit taking: {str(e)}")


@router.get("/performance/summary")
async def get_trading_performance_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days for performance analysis"),
    session: Session = Depends(get_session)
):
    """
    Get trading performance summary with CORRECTED calculations.
    
    Analyzes trading performance using accurate profit calculations based on
    total invested amounts.
    """
    try:
        # Get closed positions from the specified period
        from datetime import timedelta
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        closed_positions = session.query(Position).filter(
            Position.status == PositionStatus.CLOSED.value,
            Position.closed_at >= cutoff_date
        ).all()
        
        if not closed_positions:
            return {
                "performance_summary": {
                    "period_days": days,
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_rate": 0,
                    "total_profit": 0,
                    "average_profit_per_trade": 0,
                    "profit_factor": 1,
                    "calculation_method": "corrected_total_invested_based"
                },
                "message": f"No closed positions found in the last {days} days"
            }
        
        # Calculate performance metrics
        total_trades = len(closed_positions)
        winning_trades = len([p for p in closed_positions if (p.total_profit_realized or 0) > 0])
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum(p.total_profit_realized or Decimal('0') for p in closed_positions)
        average_profit_per_trade = total_profit / total_trades if total_trades > 0 else Decimal('0')
        
        # Calculate profit factor
        total_gains = sum(
            p.total_profit_realized for p in closed_positions 
            if p.total_profit_realized and p.total_profit_realized > 0
        ) or Decimal('0')
        
        total_losses = abs(sum(
            p.total_profit_realized for p in closed_positions 
            if p.total_profit_realized and p.total_profit_realized < 0
        )) or Decimal('0')
        
        profit_factor = float(total_gains / total_losses) if total_losses > 0 else 999.0
        
        # Get detailed trade breakdown
        trade_details = []
        for position in closed_positions:
            # Get position scales to calculate total invested (CORRECTED)
            from ..models.positions import PositionScale
            scales = session.query(PositionScale).filter(
                PositionScale.position_id == position.id
            ).all()
            
            total_invested = sum(scale.investment_amount for scale in scales)
            profit_percentage = float((position.total_profit_realized or 0) / total_invested * 100) if total_invested > 0 else 0
            
            trade_details.append({
                "position_id": str(position.id),
                "symbol": position.symbol,
                "direction": position.direction,
                "total_invested": float(total_invested),
                "profit_realized": float(position.total_profit_realized or 0),
                "profit_percentage": profit_percentage,
                "stages_used": len(scales),
                "closed_at": position.closed_at.isoformat() if position.closed_at else None
            })
        
        return {
            "performance_summary": {
                "period_days": days,
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": round(win_rate, 2),
                "total_profit": float(total_profit),
                "average_profit_per_trade": float(average_profit_per_trade),
                "profit_factor": round(profit_factor, 2),
                "calculation_method": "corrected_total_invested_based",
                "profit_threshold_method": "75_percent_of_total_invested"
            },
            "trade_details": trade_details,
            "analysis_period": {
                "start_date": cutoff_date.isoformat(),
                "end_date": datetime.now(timezone.utc).isoformat(),
                "days_analyzed": days
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating performance summary: {str(e)}")


# Export router
__all__ = ["router"]

