#!/usr/bin/env python3
"""
📅 SUBSCRIPTION MONITORING API ROUTES
Provides endpoints for monitoring Cryptometer API subscription status
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging
from datetime import datetime

from ..services.subscription_monitor import subscription_monitor
from ..utils.cryptometer_quota_manager import get_cryptometer_quota_status, cryptometer_quota_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/subscription", tags=["Subscription"])

@router.get("/status", summary="Get subscription status")
async def get_subscription_status() -> Dict[str, Any]:
    """
    📊 Get current Cryptometer API subscription status
    
    Returns:
        - API plan information
        - Current usage and limits
        - Days until expiry/reset
        - Usage forecast
        - Quota manager status
    """
    try:
        # Get subscription status
        sub_status = subscription_monitor.check_subscription_status()
        
        # Get quota manager status
        quota_status = get_cryptometer_quota_status()
        
        # Get usage forecast
        forecast = subscription_monitor.get_usage_forecast()
        
        return {
            "success": True,
            "data": {
                "subscription": sub_status,
                "quota_manager": quota_status,
                "forecast": forecast,
                "timestamp": datetime.now().isoformat()
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting subscription status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-usage", summary="Update subscription usage")
async def update_subscription_usage_endpoint(
    current_usage: int,
    reset_date: str = None,
    expiry_date: str = None
) -> Dict[str, Any]:
    """
    📝 Update current subscription usage and dates
    
    Args:
        current_usage: Current number of API calls used
        reset_date: Optional reset date (YYYY-MM-DD format)
        expiry_date: Optional expiry date (YYYY-MM-DD format)
    """
    try:
        subscription_monitor.update_usage(current_usage, reset_date, expiry_date)
        
        # Get updated status
        status = subscription_monitor.check_subscription_status()
        
        logger.info(f"✅ Subscription usage updated: {current_usage:,}/100,000")
        
        return {
            "success": True,
            "data": {
                "message": "Usage updated successfully",
                "status": status
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ Error updating subscription usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast", summary="Get usage forecast")
async def get_usage_forecast() -> Dict[str, Any]:
    """
    📈 Get usage forecast based on current patterns
    
    Returns:
        - Daily usage average
        - Forecast total usage
        - Will exceed limit warning
        - Recommended daily limit
    """
    try:
        forecast = subscription_monitor.get_usage_forecast()
        
        return {
            "success": True,
            "data": forecast,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting usage forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-expiry", summary="Check and send expiry notifications")
async def check_expiry_notifications(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    🔔 Manually trigger expiry check and notifications
    """
    try:
        status = subscription_monitor.check_subscription_status()
        
        return {
            "success": True,
            "data": {
                "message": "Expiry check completed",
                "days_until_expiry": status.get("days_until_expiry"),
                "will_notify": status.get("days_until_expiry", 999) <= 1
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking expiry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", summary="Check subscription health")
async def subscription_health() -> Dict[str, Any]:
    """
    ✅ Quick health check for subscription monitoring
    """
    try:
        status = subscription_monitor.check_subscription_status()
        quota = get_cryptometer_quota_status()
        
        # Determine health status
        usage_percent = status.get("usage_percent", 0)
        days_until_expiry = status.get("days_until_expiry", 999)
        
        if days_until_expiry <= 1:
            health = "critical"
            message = f"Subscription expires in {days_until_expiry} days"
        elif days_until_expiry <= 7:
            health = "warning" 
            message = f"Subscription expires in {days_until_expiry} days"
        elif usage_percent >= 90:
            health = "warning"
            message = f"API usage at {usage_percent:.1f}%"
        else:
            health = "healthy"
            message = "All systems operational"
        
        return {
            "success": True,
            "data": {
                "health": health,
                "message": message,
                "usage_percent": usage_percent,
                "days_until_expiry": days_until_expiry,
                "emergency_shutdown": quota.get("emergency_shutdown", False)
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking subscription health: {e}")
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }

@router.post("/toggle-rate-limiting", summary="Toggle Cryptometer rate limiting")
async def toggle_rate_limiting() -> Dict[str, Any]:
    """
    🔄 Toggle Cryptometer API rate limiting on/off
    
    When disabled: Unlimited API calls allowed (use with caution!)
    When enabled: Normal quota limits apply
    
    Returns:
        - New rate limiting status
        - Current quota information
    """
    try:
        # Toggle the rate limiting
        new_status = cryptometer_quota_manager.toggle_rate_limiting()
        
        # Get updated quota status
        quota_status = get_cryptometer_quota_status()
        
        status_text = "enabled" if new_status else "disabled"
        emoji = "🔒" if new_status else "🔓"
        
        logger.info(f"{emoji} Rate limiting toggled: {status_text}")
        
        return {
            "success": True,
            "data": {
                "rate_limiting_enabled": new_status,
                "status_message": f"Rate limiting {status_text}",
                "emoji": emoji,
                "quota_status": quota_status,
                "warning": None if new_status else "⚠️ Rate limiting disabled - unlimited API calls allowed!"
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ Error toggling rate limiting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rate-limiting-status", summary="Get rate limiting status")
async def get_rate_limiting_status() -> Dict[str, Any]:
    """
    📊 Get current rate limiting status
    """
    try:
        is_enabled = cryptometer_quota_manager.is_rate_limiting_enabled()
        quota_status = get_cryptometer_quota_status()
        
        return {
            "success": True,
            "data": {
                "rate_limiting_enabled": is_enabled,
                "quota_status": quota_status
            },
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting rate limiting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))