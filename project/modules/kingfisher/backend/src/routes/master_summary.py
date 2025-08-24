#!/usr/bin/env python3
"""
KingFisher Master Summary API Routes
Provides endpoints for generating and retrieving master summaries
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
import asyncio
from datetime import datetime

from src.services.master_summary_agent import MasterSummaryAgent

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Master Summary"])

class MasterSummaryRequest(BaseModel):
    """Request model for master summary generation"""
    hours_back: int = 24
    include_sector_analysis: bool = True
    include_risk_warnings: bool = True
    max_opportunities: int = 10

class MasterSummaryResponse(BaseModel):
    """Response model for master summary"""
    status: str
    timestamp: str
    overall_sentiment: str
    market_confidence: float
    market_trend: str
    top_performers: List[str]
    risk_alert_symbols: List[str]
    trading_opportunities_count: int
    sector_analysis_count: int
    risk_warnings_count: int
    executive_summary: str
    professional_summary: str
    summary_stats: Dict[str, Any]

@router.post("/generate", response_model=MasterSummaryResponse)
async def generate_master_summary(request: MasterSummaryRequest):
    """Generate a master summary from all symbol analyses"""
    try:
        logger.info("🎯 Generating Master Summary...")
        
        # Initialize the Master Summary Agent
        agent = MasterSummaryAgent()
        
        # Generate the master summary
        master_summary = await agent.generate_master_summary(hours_back=request.hours_back)
        
        # Prepare response
        response = MasterSummaryResponse(
            status="success",
            timestamp=master_summary.timestamp,
            overall_sentiment=master_summary.overall_sentiment,
            market_confidence=master_summary.market_confidence,
            market_trend=master_summary.market_trend,
            top_performers=master_summary.top_performers,
            risk_alert_symbols=master_summary.risk_alert_symbols,
            trading_opportunities_count=len(master_summary.trading_opportunities),
            sector_analysis_count=len(master_summary.sector_analysis),
            risk_warnings_count=len(master_summary.risk_warnings),
            executive_summary=master_summary.executive_summary,
            professional_summary=master_summary.professional_summary,
            summary_stats={
                "total_symbols_analyzed": len(master_summary.trading_opportunities) + len(master_summary.risk_alert_symbols),
                "analysis_period_hours": request.hours_back,
                "generation_time": datetime.now().isoformat()
            }
        )
        
        logger.info("✅ Master Summary generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error generating master summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate master summary: {str(e)}")

@router.get("/latest", response_model=MasterSummaryResponse)
async def get_latest_master_summary():
    """Get the latest master summary (cached or generated)"""
    try:
        logger.info("📊 Retrieving latest Master Summary...")
        
        # Initialize the Master Summary Agent
        agent = MasterSummaryAgent()
        
        # Generate the latest master summary
        master_summary = await agent.generate_master_summary(hours_back=24)
        
        # Prepare response
        response = MasterSummaryResponse(
            status="success",
            timestamp=master_summary.timestamp,
            overall_sentiment=master_summary.overall_sentiment,
            market_confidence=master_summary.market_confidence,
            market_trend=master_summary.market_trend,
            top_performers=master_summary.top_performers,
            risk_alert_symbols=master_summary.risk_alert_symbols,
            trading_opportunities_count=len(master_summary.trading_opportunities),
            sector_analysis_count=len(master_summary.sector_analysis),
            risk_warnings_count=len(master_summary.risk_warnings),
            executive_summary=master_summary.executive_summary,
            professional_summary=master_summary.professional_summary,
            summary_stats={
                "total_symbols_analyzed": len(master_summary.trading_opportunities) + len(master_summary.risk_alert_symbols),
                "analysis_period_hours": 24,
                "generation_time": datetime.now().isoformat()
            }
        )
        
        logger.info("✅ Latest Master Summary retrieved successfully")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error retrieving latest master summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve latest master summary: {str(e)}")

@router.get("/test", response_model=Dict[str, Any])
async def test_master_summary_agent():
    """Test the Master Summary Agent functionality"""
    try:
        logger.info("🧪 Testing Master Summary Agent...")
        
        # Initialize the Master Summary Agent
        agent = MasterSummaryAgent()
        
        # Run the test
        test_result = await agent.test_master_summary()
        
        logger.info("✅ Master Summary Agent test completed")
        return test_result
        
    except Exception as e:
        logger.error(f"❌ Error testing master summary agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to test master summary agent: {str(e)}")

@router.get("/stats", response_model=Dict[str, Any])
async def get_master_summary_stats():
    """Get statistics about master summary generation"""
    try:
        logger.info("📈 Getting Master Summary statistics...")
        
        # Initialize the Master Summary Agent
        agent = MasterSummaryAgent()
        
        # Get records for statistics
        records = await agent.get_all_symbol_records(hours_back=24)
        
        # Calculate statistics
        stats = {
            "total_records": len(records),
            "valid_summaries": 0,
            "symbols_analyzed": set(),
            "analysis_timestamps": [],
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
        for record in records:
            summary = agent.extract_symbol_summary(record)
            if summary:
                stats["valid_summaries"] += 1
                stats["symbols_analyzed"].add(summary.symbol)
                stats["analysis_timestamps"].append(summary.analysis_timestamp)
        
        # Convert set to list for JSON serialization
        stats["symbols_analyzed"] = list(stats["symbols_analyzed"])
        
        logger.info("✅ Master Summary statistics retrieved")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting master summary stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get master summary stats: {str(e)}")

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check for the Master Summary service"""
    try:
        logger.info("🏥 Master Summary health check...")
        
        # Initialize the Master Summary Agent
        agent = MasterSummaryAgent()
        
        # Test Airtable connection
        records = await agent.get_all_symbol_records(hours_back=1)
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "airtable_connection": "ok",
            "records_available": len(records),
            "service": "master_summary_agent"
        }
        
        logger.info("✅ Master Summary health check passed")
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Master Summary health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "service": "master_summary_agent"
        } 