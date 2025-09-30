#!/usr/bin/env python3
"""
ChatGPT Alerts API Routes
Handles alert generation requests using ChatGPT
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from pydantic import BaseModel

from src.services.chatgpt_alert_service import (
    RealTechnicalAlertService, 
    AlertData, 
    ChatGPTAlert
)

# Initialize the service
chatgpt_alert_service = RealTechnicalAlertService()

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chatgpt-alerts", tags=["ChatGPT Alerts"])

class AlertRequest(BaseModel):
    """Alert generation request"""
    symbol: str
    alert_type: str
    indicator: str
    value: float
    threshold: float
    timeframe: str
    price: float
    confidence: float = 0.8

class AlertResponse(BaseModel):
    """Alert response"""
    success: bool
    alert: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime

class MultipleAlertsRequest(BaseModel):
    """Multiple alerts generation request"""
    alerts: List[AlertRequest]

class MultipleAlertsResponse(BaseModel):
    """Multiple alerts response"""
    success: bool
    alerts: List[Dict[str, Any]] = []
    errors: List[str] = []
    timestamp: datetime

@router.post("/generate", response_model=AlertResponse)
async def generate_alert(request: AlertRequest):
    """Generate a single ChatGPT alert"""
    try:
        # Create AlertData object
        alert_data = AlertData(
            symbol=request.symbol,
            alert_type=request.alert_type,
            indicator=request.indicator,
            value=request.value,
            threshold=request.threshold,
            timeframe=request.timeframe,
            price=request.price,
            timestamp=datetime.now(),
            confidence=request.confidence
        )
        
        # Generate alert using real technical analysis
        alert = await chatgpt_alert_service.generate_real_alert(alert_data)
        
        # Convert to dict for response
        alert_dict = {
            "title": alert.title,
            "description": alert.description,
            "analysis": alert.analysis,
            "recommendation": alert.recommendation,
            "risk_level": alert.risk_level,
            "symbol": alert.symbol,
            "alert_type": alert.alert_type,
            "timestamp": alert.timestamp.isoformat()
        }
        
        logger.info(f"✅ Generated ChatGPT alert for {request.symbol}: {alert.title}")
        
        return AlertResponse(
            success=True,
            alert=alert_dict,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating ChatGPT alert: {e}")
        return AlertResponse(
            success=False,
            error=str(e),
            timestamp=datetime.now()
        )

@router.post("/generate-multiple", response_model=MultipleAlertsResponse)
async def generate_multiple_alerts(request: MultipleAlertsRequest):
    """Generate multiple ChatGPT alerts"""
    try:
        # Convert requests to AlertData objects
        alerts_data = []
        for req in request.alerts:
            alert_data = AlertData(
                symbol=req.symbol,
                alert_type=req.alert_type,
                indicator=req.indicator,
                value=req.value,
                threshold=req.threshold,
                timeframe=req.timeframe,
                price=req.price,
                timestamp=datetime.now(),
                confidence=req.confidence
            )
            alerts_data.append(alert_data)
        
        # Generate alerts using real technical analysis
        alerts = await chatgpt_alert_service.generate_multiple_real_alerts(alerts_data)
        
        # Convert to dict for response
        alerts_dict = []
        for alert in alerts:
            alert_dict = {
                "title": alert.title,
                "description": alert.description,
                "analysis": alert.analysis,
                "recommendation": alert.recommendation,
                "risk_level": alert.risk_level,
                "symbol": alert.symbol,
                "alert_type": alert.alert_type,
                "timestamp": alert.timestamp.isoformat()
            }
            alerts_dict.append(alert_dict)
        
        logger.info(f"✅ Generated {len(alerts)} ChatGPT alerts")
        
        return MultipleAlertsResponse(
            success=True,
            alerts=alerts_dict,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating multiple ChatGPT alerts: {e}")
        return MultipleAlertsResponse(
            success=False,
            errors=[str(e)],
            timestamp=datetime.now()
        )

@router.get("/status")
async def get_alert_service_status():
    """Get ChatGPT alert service status"""
    try:
        return {
            "success": True,
            "enabled": chatgpt_alert_service.enabled,
            "status": "operational" if chatgpt_alert_service.enabled else "disabled",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting alert service status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_alert_templates():
    """Get available alert templates - No templates available with real data"""
    try:
        return {
            "success": True,
            "templates": chatgpt_alert_service.alert_templates,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting alert templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))
