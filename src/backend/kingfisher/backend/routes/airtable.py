#!/usr/bin/env python3
"""
Airtable Integration API Routes
Provides endpoints for storing and retrieving data from CryptoTrade base
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

router = APIRouter(prefix="/api/v1/airtable", tags=["Airtable Integration"])

@router.get("/test-connection")
async def test_airtable_connection():
    """Test Airtable connection"""
    try:
        from services.airtable_service import AirtableService
        
        airtable_service = AirtableService()
        connected = await airtable_service.test_connection()
        
        return {
            "success": connected,
            "message": "Airtable connection successful" if connected else "Airtable connection failed",
            "base_id": "appAs9sZH7OmtYaTJ",
            "table_name": "CursorTable",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test Airtable connection: {str(e)}")

@router.get("/analyses")
async def get_airtable_analyses(limit: int = Query(10, description="Number of analyses to return")):
    """Get recent analyses from Airtable"""
    try:
        from services.airtable_service import AirtableService
        
        airtable_service = AirtableService()
        analyses = await airtable_service.get_recent_analyses(limit=limit)
        
        return {
            "success": True,
            "analyses": analyses,
            "total_count": len(analyses),
            "limit": limit,
            "source": "Airtable",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analyses from Airtable: {str(e)}")

@router.get("/summaries")
async def get_airtable_summaries():
    """Get symbol summaries from Airtable"""
    try:
        from services.airtable_service import AirtableService
        
        airtable_service = AirtableService()
        summaries = await airtable_service.get_symbol_summaries()
        
        return {
            "success": True,
            "summaries": summaries,
            "total_count": len(summaries),
            "source": "Airtable",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summaries from Airtable: {str(e)}")

@router.get("/alerts")
async def get_airtable_alerts(limit: int = Query(10, description="Number of alerts to return")):
    """Get high significance alerts from Airtable"""
    try:
        from services.airtable_service import AirtableService
        
        airtable_service = AirtableService()
        alerts = await airtable_service.get_high_significance_alerts(limit=limit)
        
        return {
            "success": True,
            "alerts": alerts,
            "total_count": len(alerts),
            "limit": limit,
            "source": "Airtable",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts from Airtable: {str(e)}")

@router.post("/store-analysis")
async def store_analysis_in_airtable(analysis_data: Dict[str, Any]):
    """Store analysis in Airtable"""
    try:
        from services.airtable_service import AirtableService
        
        airtable_service = AirtableService()
        success = await airtable_service.store_image_analysis(analysis_data)
        
        return {
            "success": success,
            "message": "Analysis stored in Airtable" if success else "Failed to store analysis",
            "symbol": analysis_data.get("symbol", ""),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store analysis in Airtable: {str(e)}")

@router.post("/store-summary")
async def store_summary_in_airtable(summary_data: Dict[str, Any]):
    """Store symbol summary in Airtable"""
    try:
        from services.airtable_service import AirtableService
        
        airtable_service = AirtableService()
        success = await airtable_service.store_symbol_summary(summary_data)
        
        return {
            "success": success,
            "message": "Summary stored in Airtable" if success else "Failed to store summary",
            "symbol": summary_data.get("symbol", ""),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store summary in Airtable: {str(e)}")

@router.post("/store-alert")
async def store_alert_in_airtable(alert_data: Dict[str, Any]):
    """Store high significance alert in Airtable"""
    try:
        from services.airtable_service import AirtableService
        
        airtable_service = AirtableService()
        success = await airtable_service.store_high_significance_alert(alert_data)
        
        return {
            "success": success,
            "message": "Alert stored in Airtable" if success else "Failed to store alert",
            "symbol": alert_data.get("symbol", ""),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store alert in Airtable: {str(e)}")

@router.get("/status")
async def get_airtable_status():
    """Get Airtable integration status"""
    try:
        from services.airtable_service import AirtableService
        
        airtable_service = AirtableService()
        connected = await airtable_service.test_connection()
        
        # Get some sample data to show integration is working
        analyses = await airtable_service.get_recent_analyses(limit=5)
        summaries = await airtable_service.get_symbol_summaries()
        alerts = await airtable_service.get_high_significance_alerts(limit=5)
        
        return {
            "success": True,
            "status": "connected" if connected else "disconnected",
            "base_id": "appAs9sZH7OmtYaTJ",
            "table_name": "CursorTable",
            "statistics": {
                "recent_analyses": len(analyses),
                "symbol_summaries": len(summaries),
                "high_significance_alerts": len(alerts)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Airtable status: {str(e)}")

@router.get("/config")
async def get_airtable_config():
    """Get Airtable configuration"""
    return {
        "success": True,
        "config": {
            "base_id": "appAs9sZH7OmtYaTJ",
            "table_name": "CursorTable",
            "api_key": "patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835",
            "base_url": "https://api.airtable.com/v0/appAs9sZH7OmtYaTJ"
        },
        "timestamp": datetime.now().isoformat()
    } 