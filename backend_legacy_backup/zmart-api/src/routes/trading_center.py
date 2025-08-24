#!/usr/bin/env python3
"""
🎯 Trading Center API Routes
Endpoints for signal processing and trade execution with 80% win rate threshold
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.services.trading_center import trading_center, QualifiedSignal
from src.services.vault_management_system import VaultManagementSystem
from src.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/trading-center",
    tags=["Trading Center"],
    responses={404: {"description": "Not found"}}
)

@router.post("/process-signal/{symbol}")
async def process_signal(
    symbol: str,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process a signal for a specific symbol through win rate filter
    
    Args:
        symbol: Trading symbol (e.g., BTCUSDT)
        
    Returns:
        Qualified signal data if meets 80% threshold, rejection reason otherwise
    """
    try:
        logger.info(f"Processing signal for {symbol} requested by {current_user.get('username', 'unknown')}")
        
        # Process signal through Trading Center
        qualified_signal = await trading_center.process_signal(symbol)
        
        if qualified_signal:
            return {
                "success": True,
                "qualified": True,
                "data": {
                    "symbol": symbol,
                    "direction": qualified_signal.selected_direction,
                    "win_rate": qualified_signal.selected_win_rate,
                    "confidence": qualified_signal.confidence,
                    "vault_id": qualified_signal.vault_id,
                    "status": qualified_signal.status.value,
                    "signal_score": qualified_signal.signal.total_score,
                    "timestamp": qualified_signal.timestamp.isoformat() if qualified_signal.timestamp else None
                },
                "message": f"Signal qualified with {qualified_signal.selected_win_rate:.2f}% win rate"
            }
        else:
            return {
                "success": True,
                "qualified": False,
                "data": {
                    "symbol": symbol,
                    "reason": "Win rate below 80% threshold"
                },
                "message": "Signal did not meet qualification criteria"
            }
            
    except Exception as e:
        logger.error(f"Error processing signal for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-process")
async def batch_process_signals(
    symbols: List[str],
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process multiple signals in batch
    
    Args:
        symbols: List of trading symbols
        
    Returns:
        Processing results for all symbols
    """
    try:
        logger.info(f"Batch processing {len(symbols)} symbols")
        
        results = []
        qualified_count = 0
        
        for symbol in symbols:
            try:
                qualified_signal = await trading_center.process_signal(symbol)
                
                if qualified_signal:
                    qualified_count += 1
                    results.append({
                        "symbol": symbol,
                        "qualified": True,
                        "win_rate": qualified_signal.selected_win_rate,
                        "direction": qualified_signal.selected_direction,
                        "vault_id": qualified_signal.vault_id
                    })
                else:
                    results.append({
                        "symbol": symbol,
                        "qualified": False,
                        "reason": "Below threshold"
                    })
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                results.append({
                    "symbol": symbol,
                    "qualified": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "total_processed": len(symbols),
            "qualified_count": qualified_count,
            "qualification_rate": round(qualified_count / len(symbols) * 100, 2) if symbols else 0,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_trading_center_stats(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get Trading Center statistics
    
    Returns:
        Trading center performance metrics
    """
    try:
        stats = trading_center.get_statistics()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/qualified-signals")
async def get_qualified_signals(
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get list of qualified signals
    
    Args:
        limit: Maximum number of signals to return
        
    Returns:
        List of qualified signals
    """
    try:
        # Get recent qualified signals
        qualified = trading_center.qualified_signals[-limit:] if limit > 0 else trading_center.qualified_signals
        
        signals_data = []
        for signal in qualified:
            signals_data.append({
                "symbol": signal.signal.symbol,
                "direction": signal.selected_direction,
                "win_rate": signal.selected_win_rate,
                "confidence": signal.confidence,
                "vault_id": signal.vault_id,
                "status": signal.status.value,
                "timestamp": signal.timestamp.isoformat() if signal.timestamp else None
            })
        
        return {
            "success": True,
            "count": len(signals_data),
            "data": signals_data
        }
        
    except Exception as e:
        logger.error(f"Error getting qualified signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monitor/start")
async def start_signal_monitoring(
    symbols: List[str],
    background_tasks: BackgroundTasks,
    interval: int = 60,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Start continuous signal monitoring for symbols
    
    Args:
        symbols: List of symbols to monitor
        interval: Check interval in seconds (default 60)
        
    Returns:
        Monitoring status
    """
    try:
        # Start monitoring in background
        background_tasks.add_task(
            trading_center.monitor_signals,
            symbols,
            interval
        )
        
        return {
            "success": True,
            "message": f"Started monitoring {len(symbols)} symbols",
            "symbols": symbols,
            "interval": interval
        }
        
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vault-capacity")
async def get_vault_capacity(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current vault capacity status
    
    Returns:
        Vault capacity information
    """
    try:
        vault_manager = VaultManagementSystem()
        active_vaults = await vault_manager.get_active_vaults()
        
        vault_status = []
        total_capacity = 0
        used_capacity = 0
        
        for vault in active_vaults:
            vault_id = vault['id']
            positions = await trading_center.position_manager.get_vault_positions(vault_id)
            active_positions = [p for p in positions if p.get('status') == 'open']
            
            capacity = trading_center.max_trades_per_vault
            used = len(active_positions)
            available = capacity - used
            
            vault_status.append({
                "vault_id": vault_id,
                "type": vault.get('type', 'unknown'),
                "capacity": capacity,
                "used": used,
                "available": available,
                "utilization": round(used / capacity * 100, 2) if capacity > 0 else 0
            })
            
            total_capacity += capacity
            used_capacity += used
        
        return {
            "success": True,
            "total_vaults": len(active_vaults),
            "total_capacity": total_capacity,
            "used_capacity": used_capacity,
            "available_capacity": total_capacity - used_capacity,
            "overall_utilization": round(used_capacity / total_capacity * 100, 2) if total_capacity > 0 else 0,
            "vaults": vault_status
        }
        
    except Exception as e:
        logger.error(f"Error getting vault capacity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-my-symbols")
async def process_my_symbols_batch(
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process all My Symbols in batch with comprehensive analysis
    
    Returns:
        Batch processing results with cross-module insights
    """
    try:
        logger.info(f"My Symbols batch processing requested by {current_user.get('username', 'unknown')}")
        
        # Process My Symbols batch
        qualified_signals = await trading_center.process_my_symbols_batch()
        
        # Get orchestrator insights
        opportunities = await trading_center.my_symbols_orchestrator.get_high_value_opportunities()
        rare_events = await trading_center.my_symbols_orchestrator.get_rare_events()
        stats = trading_center.my_symbols_orchestrator.get_statistics()
        
        # Format results
        qualified_data = []
        for signal in qualified_signals:
            qualified_data.append({
                "symbol": signal.signal.symbol,
                "direction": signal.selected_direction,
                "win_rate": signal.selected_win_rate,
                "confidence": signal.confidence,
                "has_pattern": signal.has_pattern,
                "pattern_type": signal.pattern_type,
                "is_rare_event": signal.is_rare_event,
                "vault_id": signal.vault_id,
                "status": signal.status.value
            })
        
        opportunity_data = []
        for package in opportunities:
            opportunity_data.append({
                "symbol": package.symbol,
                "priority": package.priority.value,
                "score": package.composite_score,
                "opportunities": package.high_value_opportunities,
                "rare_events": package.rare_events_detected
            })
        
        return {
            "success": True,
            "qualified_signals": qualified_data,
            "high_value_opportunities": opportunity_data,
            "rare_events_count": len(rare_events),
            "statistics": stats,
            "message": f"Processed My Symbols: {len(qualified_signals)} qualified, {len(opportunities)} with opportunities"
        }
        
    except Exception as e:
        logger.error(f"Error in My Symbols batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-symbols-status")
async def get_my_symbols_status(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get comprehensive My Symbols status from orchestrator
    
    Returns:
        Complete status of My Symbols integration
    """
    try:
        # Get orchestrator statistics
        stats = trading_center.my_symbols_orchestrator.get_statistics()
        
        # Get high-value opportunities and rare events
        opportunities = await trading_center.my_symbols_orchestrator.get_high_value_opportunities()
        rare_events = await trading_center.my_symbols_orchestrator.get_rare_events()
        
        return {
            "success": True,
            "statistics": stats,
            "opportunities_count": len(opportunities),
            "rare_events_count": len(rare_events),
            "top_opportunities": [
                {
                    "symbol": pkg.symbol,
                    "score": pkg.composite_score,
                    "priority": pkg.priority.value,
                    "opportunities": pkg.high_value_opportunities[:3]  # Top 3
                } for pkg in opportunities[:5]  # Top 5 symbols
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting My Symbols status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-threshold")
async def update_win_rate_threshold(
    threshold: float,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update the win rate threshold (admin only)
    
    Args:
        threshold: New win rate threshold (0-100)
        
    Returns:
        Update confirmation
    """
    try:
        # Validate threshold
        if threshold < 0 or threshold > 100:
            raise ValueError("Threshold must be between 0 and 100")
        
        # Check admin permission (implement your auth logic)
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        old_threshold = trading_center.win_rate_threshold
        trading_center.win_rate_threshold = threshold
        
        logger.info(f"Win rate threshold updated from {old_threshold}% to {threshold}% by {current_user.get('username')}")
        
        return {
            "success": True,
            "old_threshold": old_threshold,
            "new_threshold": threshold,
            "message": f"Win rate threshold updated to {threshold}%"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating threshold: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export router
__all__ = ['router']