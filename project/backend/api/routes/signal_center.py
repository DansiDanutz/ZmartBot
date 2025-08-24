#!/usr/bin/env python3
"""
Signal Center API Routes
Unified endpoints for all signal sources and aggregation
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.services.unified_signal_center import unified_signal_center
from src.services.signal_center import signal_center_service, get_signal_center_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/signal-center",
    tags=["signal-center"]
)

@router.get("/unified/{symbol}")
async def get_unified_signals(
    symbol: str,
    include_metadata: bool = Query(True, description="Include detailed metadata")
) -> Dict[str, Any]:
    """
    Get unified signals from all sources for a symbol
    
    Args:
        symbol: Trading symbol (e.g., BTC, ETH)
        include_metadata: Whether to include detailed metadata
        
    Returns:
        Aggregated signal from all sources
    """
    try:
        # Get aggregated signal
        signal = await unified_signal_center.get_all_signals(symbol.upper())
        
        result = signal.to_dict()
        
        if not include_metadata:
            # Remove detailed metadata for lighter response
            for s in result.get('signals', []):
                s.pop('metadata', None)
        
        return {
            "success": True,
            "data": result,
            "summary": {
                "action": result['direction'].upper(),
                "score": result['total_score'],
                "confidence": result['confidence'],
                "recommendation": result['recommendation'],
                "risk": result['risk_level']
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting unified signals for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_signal_dashboard() -> Dict[str, Any]:
    """
    Get comprehensive signal dashboard for top symbols
    
    Returns:
        Dashboard with signals for multiple symbols
    """
    try:
        dashboard = await unified_signal_center.get_signal_dashboard()
        
        return {
            "success": True,
            "data": dashboard,
            "summary": {
                "market_trend": dashboard.get('market_trend'),
                "average_score": dashboard.get('average_score'),
                "active_sources": dashboard.get('active_sources'),
                "timestamp": dashboard.get('timestamp')
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting signal dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest")
async def ingest_signal(
    signal_data: Dict[str, Any] = Body(..., description="Raw signal data")
) -> Dict[str, Any]:
    """
    Ingest a new signal into the signal center
    
    Args:
        signal_data: Raw signal data to process
        
    Returns:
        Processing result
    """
    try:
        service = await get_signal_center_service()
        success, message, signal_id = await service.ingest_signal(signal_data)
        
        return {
            "success": success,
            "message": message,
            "signal_id": signal_id
        }
        
    except Exception as e:
        logger.error(f"Error ingesting signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-signals")
async def get_top_signals(
    limit: int = Query(10, ge=1, le=50, description="Number of signals"),
    min_quality: float = Query(None, ge=0, le=1, description="Minimum quality score"),
    symbols: Optional[List[str]] = Query(None, description="Filter by symbols"),
    timeframes: Optional[List[str]] = Query(None, description="Filter by timeframes")
) -> Dict[str, Any]:
    """
    Get top signals based on quality and criteria
    
    Args:
        limit: Number of signals to return
        min_quality: Minimum quality score filter
        symbols: Optional symbol filter
        timeframes: Optional timeframe filter
        
    Returns:
        Top signals matching criteria
    """
    try:
        service = await get_signal_center_service()
        signals = await service.get_top_signals(
            limit=limit,
            min_quality=min_quality,
            symbols=symbols,
            timeframes=timeframes
        )
        
        return {
            "success": True,
            "count": len(signals),
            "signals": signals
        }
        
    except Exception as e:
        logger.error(f"Error getting top signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/aggregation/{symbol}")
async def get_signal_aggregation(
    symbol: str,
    timeframe: str = Query("1h", description="Timeframe for aggregation"),
    force_refresh: bool = Query(False, description="Force refresh cache")
) -> Dict[str, Any]:
    """
    Get signal aggregation for a symbol and timeframe
    
    Args:
        symbol: Trading symbol
        timeframe: Timeframe for aggregation
        force_refresh: Force refresh cached data
        
    Returns:
        Aggregated signal data
    """
    try:
        service = await get_signal_center_service()
        aggregation = await service.get_signal_aggregation(
            symbol=symbol.upper(),
            timeframe=timeframe,
            force_refresh=force_refresh
        )
        
        if not aggregation:
            return {
                "success": False,
                "message": "No signals available for aggregation"
            }
        
        return {
            "success": True,
            "data": aggregation
        }
        
    except Exception as e:
        logger.error(f"Error getting signal aggregation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/source-weights")
async def get_source_weights() -> Dict[str, Any]:
    """
    Get current source weights configuration
    
    Returns:
        Source weights and configuration
    """
    try:
        weights = unified_signal_center.SOURCE_WEIGHTS
        
        # Calculate percentages
        total_weight = sum(weights.values())
        percentages = {
            source.value: (weight / total_weight * 100) 
            for source, weight in weights.items()
        }
        
        return {
            "success": True,
            "weights": {source.value: weight for source, weight in weights.items()},
            "percentages": percentages,
            "total_weight": total_weight,
            "sources": {
                "active": [s.value for s, w in weights.items() if w > 0],
                "inactive": [s.value for s, w in weights.items() if w == 0]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting source weights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def signal_center_health() -> Dict[str, Any]:
    """
    Check health status of signal center
    
    Returns:
        Health status and statistics
    """
    try:
        service = await get_signal_center_service()
        
        # Get cache statistics
        cache_size = len(service.signal_cache)
        
        # Clean expired signals
        expired_count = await service.cleanup_expired_signals()
        
        # Get source statuses
        source_status = {}
        for source in unified_signal_center.SOURCE_WEIGHTS.keys():
            source_status[source.value] = {
                "weight": unified_signal_center.SOURCE_WEIGHTS[source],
                "active": unified_signal_center.SOURCE_WEIGHTS[source] > 0
            }
        
        return {
            "success": True,
            "status": "healthy",
            "statistics": {
                "cached_signals": cache_size,
                "expired_cleaned": expired_count,
                "active_sources": sum(1 for w in unified_signal_center.SOURCE_WEIGHTS.values() if w > 0),
                "total_sources": len(unified_signal_center.SOURCE_WEIGHTS)
            },
            "sources": source_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking signal center health: {e}")
        return {
            "success": False,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/batch-analysis")
async def batch_signal_analysis(
    symbols: List[str] = Body(..., description="List of symbols to analyze")
) -> Dict[str, Any]:
    """
    Analyze multiple symbols in batch
    
    Args:
        symbols: List of trading symbols
        
    Returns:
        Batch analysis results
    """
    try:
        if not symbols:
            raise HTTPException(status_code=400, detail="No symbols provided")
        
        if len(symbols) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 symbols allowed")
        
        results = {}
        for symbol in symbols:
            try:
                signal = await unified_signal_center.get_all_signals(symbol.upper())
                results[symbol] = {
                    "score": signal.total_score,
                    "direction": signal.direction,
                    "confidence": signal.confidence,
                    "recommendation": signal.recommendation,
                    "risk": signal.risk_level
                }
            except Exception as e:
                results[symbol] = {
                    "error": str(e),
                    "score": 50,
                    "direction": "hold",
                    "confidence": 0
                }
        
        # Calculate batch statistics
        valid_scores = [r['score'] for r in results.values() if 'error' not in r]
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 50
        
        return {
            "success": True,
            "results": results,
            "statistics": {
                "analyzed": len(results),
                "successful": len(valid_scores),
                "failed": len(symbols) - len(valid_scores),
                "average_score": round(avg_score, 2)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))