#!/usr/bin/env python3
"""
🔐 CRYPTOMETER MANAGEMENT API
Monitor and control Cryptometer API usage, quotas, and triggers
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from src.utils.cryptometer_quota_manager import (
    get_cryptometer_quota_status,
    get_cryptometer_usage_report,
    cryptometer_quota_manager
)
from src.utils.price_movement_trigger import (
    get_price_trigger_status,
    price_movement_trigger,
    force_trigger_analysis
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/cryptometer", tags=["Cryptometer Management"])

@router.get("/quota/status", summary="Get Cryptometer quota status")
async def get_quota_status() -> Dict[str, Any]:
    """
    Get current Cryptometer API quota status
    Shows daily/monthly usage, limits, and health
    """
    try:
        status = get_cryptometer_quota_status()
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting quota status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quota/report", summary="Get detailed usage report")
async def get_usage_report() -> Dict[str, Any]:
    """
    Get detailed Cryptometer usage report by service
    """
    try:
        report = get_cryptometer_usage_report()
        return {
            "success": True,
            "data": report,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting usage report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trigger/status/{symbol}", summary="Get price movement trigger status")
async def get_trigger_status(symbol: str) -> Dict[str, Any]:
    """
    Get price movement trigger status for a symbol
    Shows if API calls are being suppressed due to ranging market
    """
    try:
        trigger_status = get_price_trigger_status(symbol)
        market_state = price_movement_trigger.get_market_state(symbol)
        
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "trigger_status": trigger_status,
                "market_state": market_state
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting trigger status for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trigger/status", summary="Get trigger status for multiple symbols")
async def get_multiple_trigger_status(
    symbols: Optional[str] = Query(None, description="Comma-separated list of symbols")
) -> Dict[str, Any]:
    """
    Get price movement trigger status for multiple symbols
    """
    try:
        if not symbols:
            # Get status for common symbols
            default_symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
        else:
            default_symbols = [s.strip().upper() for s in symbols.split(",")]
        
        statuses = {}
        for symbol in default_symbols:
            trigger_status = get_price_trigger_status(symbol)
            market_state = price_movement_trigger.get_market_state(symbol)
            statuses[symbol] = {
                "trigger_status": trigger_status,
                "market_state": market_state
            }
        
        return {
            "success": True,
            "data": statuses,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting multiple trigger statuses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quota/reset-emergency", summary="Reset emergency shutdown")
async def reset_emergency_shutdown() -> Dict[str, Any]:
    """
    Reset emergency shutdown (admin function)
    Use when system was emergency stopped due to quota limits
    """
    try:
        cryptometer_quota_manager.reset_emergency_shutdown()
        return {
            "success": True,
            "message": "Emergency shutdown reset successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error resetting emergency shutdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quota/set-daily-limit", summary="Set daily quota limit")
async def set_daily_limit(new_limit: int = Query(..., ge=100, le=10000)) -> Dict[str, Any]:
    """
    Set daily API call limit (admin function)
    """
    try:
        cryptometer_quota_manager.set_daily_limit(new_limit)
        return {
            "success": True,
            "message": f"Daily limit set to {new_limit}",
            "new_limit": new_limit,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error setting daily limit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger/force/{symbol}", summary="Force trigger analysis")
async def force_trigger(symbol: str) -> Dict[str, Any]:
    """
    Force trigger Cryptometer analysis for a symbol (admin function)
    Bypasses movement detection and cooldowns
    """
    try:
        success = force_trigger_analysis(symbol.upper())
        return {
            "success": success,
            "message": f"Analysis triggered for {symbol}" if success else f"Failed to trigger analysis for {symbol}",
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error force triggering analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/health", summary="Get overall system health")
async def get_system_health() -> Dict[str, Any]:
    """
    Get overall Cryptometer system health
    Combines quota status and trigger system status
    """
    try:
        quota_status = get_cryptometer_quota_status()
        
        # Get health for major symbols
        major_symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        trigger_health = {}
        
        for symbol in major_symbols:
            market_state = price_movement_trigger.get_market_state(symbol)
            trigger_health[symbol] = market_state
        
        # Determine overall health
        daily_usage_pct = quota_status['daily']['percent_used']
        monthly_usage_pct = quota_status['monthly']['percent_used']
        emergency_shutdown = quota_status['emergency_shutdown']
        
        if emergency_shutdown or monthly_usage_pct >= 95:
            health_status = "critical"
        elif daily_usage_pct >= 90 or monthly_usage_pct >= 90:
            health_status = "warning"
        elif daily_usage_pct >= 75 or monthly_usage_pct >= 75:
            health_status = "caution"
        else:
            health_status = "healthy"
        
        return {
            "success": True,
            "data": {
                "overall_status": health_status,
                "quota_status": quota_status,
                "trigger_system": trigger_health,
                "recommendations": _get_health_recommendations(health_status, quota_status)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _get_health_recommendations(health_status: str, quota_status: Dict[str, Any]) -> List[str]:
    """Generate health recommendations based on system status"""
    recommendations = []
    
    daily_pct = quota_status['daily']['percent_used']
    monthly_pct = quota_status['monthly']['percent_used']
    
    if health_status == "critical":
        recommendations.extend([
            "🚨 CRITICAL: Stop all non-essential API calls immediately",
            "🔒 Consider enabling emergency mode",
            "📞 Contact administrator for quota increase"
        ])
    elif health_status == "warning":
        recommendations.extend([
            "⚠️ HIGH USAGE: Reduce API call frequency",
            "🎯 Enable stricter movement triggers",
            "📊 Monitor usage closely"
        ])
    elif health_status == "caution":
        recommendations.extend([
            "📈 Moderate usage - monitor trends",
            "🔍 Consider optimizing API call patterns",
            "💾 Increase caching duration"
        ])
    else:
        recommendations.extend([
            "✅ System healthy",
            "📊 Continue normal operations",
            "🔄 Regular monitoring recommended"
        ])
    
    return recommendations