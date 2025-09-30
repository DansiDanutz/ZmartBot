#!/usr/bin/env python3
"""
Unified Trading API Routes
Trading endpoints integrated with Signal Center
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.agents.trading.unified_trading_agent import (
    unified_trading_agent,
    TradingMode,
    UnifiedTradingAgent
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/unified-trading",
    tags=["unified-trading"]
)

@router.post("/analyze-and-trade/{symbol}")
async def analyze_and_trade(
    symbol: str,
    dry_run: bool = Query(False, description="Perform analysis without executing trade")
) -> Dict[str, Any]:
    """
    Analyze signals and execute trade if conditions are met
    
    Args:
        symbol: Trading symbol
        dry_run: If true, only analyze without trading
        
    Returns:
        Analysis and trade execution result
    """
    try:
        if dry_run:
            # Just analyze without trading
            signal = await unified_trading_agent.signal_center.get_all_signals(symbol.upper())
            
            return {
                "success": True,
                "mode": "dry_run",
                "analysis": {
                    "symbol": signal.symbol,
                    "score": signal.total_score,
                    "direction": signal.direction,
                    "confidence": signal.confidence,
                    "recommendation": signal.recommendation,
                    "risk_level": signal.risk_level,
                    "would_trade": (
                        signal.total_score >= unified_trading_agent.min_score_threshold and
                        signal.confidence >= unified_trading_agent.min_confidence_threshold
                    )
                }
            }
        
        # Analyze and potentially trade
        decision = await unified_trading_agent.analyze_and_trade(symbol.upper())
        
        if decision:
            return {
                "success": True,
                "traded": True,
                "decision": decision.to_dict()
            }
        else:
            return {
                "success": True,
                "traded": False,
                "message": "No trade executed - conditions not met"
            }
        
    except Exception as e:
        logger.error(f"Error in analyze_and_trade for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-analyze")
async def batch_analyze_and_trade(
    symbols: List[str] = Body(..., description="List of symbols to analyze"),
    execute_trades: bool = Query(True, description="Execute trades if conditions met")
) -> Dict[str, Any]:
    """
    Analyze multiple symbols and optionally execute trades
    
    Args:
        symbols: List of trading symbols
        execute_trades: Whether to execute trades
        
    Returns:
        Batch analysis results
    """
    try:
        if not symbols:
            raise HTTPException(status_code=400, detail="No symbols provided")
        
        if len(symbols) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 symbols allowed")
        
        results = {}
        trades_executed = []
        
        for symbol in symbols:
            try:
                if execute_trades:
                    decision = await unified_trading_agent.analyze_and_trade(symbol.upper())
                    if decision:
                        trades_executed.append(symbol)
                        results[symbol] = {
                            "traded": True,
                            "decision": decision.to_dict()
                        }
                    else:
                        results[symbol] = {
                            "traded": False,
                            "reason": "Conditions not met"
                        }
                else:
                    # Just analyze
                    signal = await unified_trading_agent.signal_center.get_all_signals(symbol.upper())
                    results[symbol] = {
                        "score": signal.total_score,
                        "direction": signal.direction,
                        "confidence": signal.confidence,
                        "would_trade": (
                            signal.total_score >= unified_trading_agent.min_score_threshold and
                            signal.confidence >= unified_trading_agent.min_confidence_threshold
                        )
                    }
            except Exception as e:
                results[symbol] = {
                    "error": str(e)
                }
        
        return {
            "success": True,
            "analyzed": len(results),
            "trades_executed": len(trades_executed),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions")
async def get_positions() -> Dict[str, Any]:
    """
    Get all active positions
    
    Returns:
        Active positions and statistics
    """
    try:
        # Update positions with current prices
        positions = await unified_trading_agent.update_positions()
        
        # Get performance stats
        stats = unified_trading_agent.get_performance_stats()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/close-position/{position_id}")
async def close_position(
    position_id: str,
    reason: str = Query("MANUAL", description="Reason for closing")
) -> Dict[str, Any]:
    """
    Close a specific position
    
    Args:
        position_id: Position ID to close
        reason: Reason for closing
        
    Returns:
        Closure result
    """
    try:
        if position_id not in unified_trading_agent.active_positions:
            raise HTTPException(status_code=404, detail="Position not found")
        
        position = unified_trading_agent.active_positions[position_id]
        pnl = position.pnl
        
        # Close position
        await unified_trading_agent._close_position(position_id, reason)
        
        return {
            "success": True,
            "position_id": position_id,
            "symbol": position.symbol,
            "pnl": round(pnl, 2),
            "reason": reason,
            "closed_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing position {position_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance() -> Dict[str, Any]:
    """
    Get trading performance statistics
    
    Returns:
        Performance metrics
    """
    try:
        stats = unified_trading_agent.get_performance_stats()
        
        return {
            "success": True,
            "performance": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-mode")
async def set_trading_mode(
    mode: str = Body(..., description="Trading mode: paper, live, simulation")
) -> Dict[str, Any]:
    """
    Change trading mode
    
    Args:
        mode: New trading mode
        
    Returns:
        Mode change result
    """
    try:
        mode_enum = TradingMode(mode.lower())
        
        # Create new agent with new mode
        global unified_trading_agent
        old_mode = unified_trading_agent.mode.value
        unified_trading_agent = UnifiedTradingAgent(mode=mode_enum)
        
        return {
            "success": True,
            "old_mode": old_mode,
            "new_mode": mode_enum.value,
            "message": f"Trading mode changed to {mode_enum.value}"
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}")
    except Exception as e:
        logger.error(f"Error setting mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settings")
async def get_trading_settings() -> Dict[str, Any]:
    """
    Get current trading settings
    
    Returns:
        Trading configuration
    """
    try:
        return {
            "success": True,
            "settings": {
                "mode": unified_trading_agent.mode.value,
                "max_positions": unified_trading_agent.max_positions,
                "position_size_percentage": unified_trading_agent.position_size_percentage * 100,
                "min_score_threshold": unified_trading_agent.min_score_threshold,
                "min_confidence_threshold": unified_trading_agent.min_confidence_threshold,
                "max_daily_loss": unified_trading_agent.max_daily_loss * 100,
                "default_stop_loss": unified_trading_agent.default_stop_loss_percentage * 100,
                "default_take_profit": unified_trading_agent.default_take_profit_percentage * 100
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-settings")
async def update_trading_settings(
    settings: Dict[str, Any] = Body(..., description="Settings to update")
) -> Dict[str, Any]:
    """
    Update trading settings
    
    Args:
        settings: Dictionary of settings to update
        
    Returns:
        Update result
    """
    try:
        updated = []
        
        # Update allowed settings
        if 'max_positions' in settings:
            unified_trading_agent.max_positions = int(settings['max_positions'])
            updated.append('max_positions')
        
        if 'min_score_threshold' in settings:
            unified_trading_agent.min_score_threshold = int(settings['min_score_threshold'])
            updated.append('min_score_threshold')
        
        if 'min_confidence_threshold' in settings:
            unified_trading_agent.min_confidence_threshold = int(settings['min_confidence_threshold'])
            updated.append('min_confidence_threshold')
        
        if 'position_size_percentage' in settings:
            unified_trading_agent.position_size_percentage = float(settings['position_size_percentage']) / 100
            updated.append('position_size_percentage')
        
        if 'max_daily_loss' in settings:
            unified_trading_agent.max_daily_loss = float(settings['max_daily_loss']) / 100
            updated.append('max_daily_loss')
        
        return {
            "success": True,
            "updated": updated,
            "message": f"Updated {len(updated)} settings"
        }
        
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))