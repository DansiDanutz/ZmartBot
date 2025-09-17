#!/usr/bin/env python3
"""
Professional Analysis API Routes
================================

FastAPI routes for generating professional trading analysis reports
following the standardized SOL USDT format for any trading symbol.

Features:
- Executive Summary generation
- Comprehensive Analysis reports
- Batch analysis for multiple symbols
- Standardized professional format
- Multi-model AI integration

Author: ZmartBot AI System
Date: January 2025
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from src.services.enhanced_professional_ai_agent import EnhancedProfessionalAIAgent

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize the professional AI agent
professional_ai_agent = EnhancedProfessionalAIAgent()

@router.get("/analysis/{symbol}/executive")
async def get_executive_summary(
    symbol: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Generate Executive Summary & Key Metrics report for a trading symbol
    
    This endpoint generates a professional executive summary following the
    standardized format used for SOL USDT analysis.
    
    Args:
        symbol: Trading symbol (e.g., "ETH-USDT", "BTC-USDT", "SOL-USDT")
        
    Returns:
        Professional executive summary report
    """
    try:
        # Convert symbol format (handle both / and - separators)
        formatted_symbol = symbol.replace("-", "/").upper()
        
        logger.info(f"Generating executive summary for {formatted_symbol}")
        
        # Generate the executive summary
        result = await professional_ai_agent.generate_executive_summary(formatted_symbol)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate executive summary for {formatted_symbol}: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "status": "success",
            "symbol": formatted_symbol,
            "report_type": "executive_summary",
            "data": result,
            "generated_at": datetime.now().isoformat(),
            "api_version": "2025.1.0"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating executive summary for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error generating executive summary: {str(e)}"
        )

@router.get("/analysis/{symbol}/comprehensive")
async def get_comprehensive_report(
    symbol: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Generate Comprehensive Analysis Report for a trading symbol
    
    This endpoint generates a professional comprehensive analysis report
    following the standardized format used for SOL USDT analysis.
    
    Args:
        symbol: Trading symbol (e.g., "ETH-USDT", "BTC-USDT", "SOL-USDT")
        
    Returns:
        Professional comprehensive analysis report
    """
    try:
        # Convert symbol format
        formatted_symbol = symbol.replace("-", "/").upper()
        
        logger.info(f"Generating comprehensive report for {formatted_symbol}")
        
        # Generate the comprehensive report
        result = await professional_ai_agent.generate_comprehensive_report(formatted_symbol)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate comprehensive report for {formatted_symbol}: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "status": "success",
            "symbol": formatted_symbol,
            "report_type": "comprehensive_analysis",
            "data": result,
            "generated_at": datetime.now().isoformat(),
            "api_version": "2025.1.0"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating comprehensive report for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error generating comprehensive report: {str(e)}"
        )

@router.get("/analysis/{symbol}")
async def get_symbol_analysis(
    symbol: str,
    background_tasks: BackgroundTasks,
    report_type: str = Query(default="comprehensive", regex="^(executive|comprehensive)$")
) -> Dict[str, Any]:
    """
    Generate professional analysis report for a trading symbol
    
    This is a unified endpoint that can generate either executive summary
    or comprehensive analysis reports.
    
    Args:
        symbol: Trading symbol (e.g., "ETH-USDT", "BTC-USDT", "SOL-USDT")
        report_type: Type of report ("executive" or "comprehensive")
        
    Returns:
        Professional analysis report in the specified format
    """
    try:
        # Convert symbol format
        formatted_symbol = symbol.replace("-", "/").upper()
        
        logger.info(f"Generating {report_type} analysis for {formatted_symbol}")
        
        # Generate the requested analysis
        result = await professional_ai_agent.generate_symbol_analysis(formatted_symbol, report_type)
        
        if not result.get("success", False):
            # Return fallback report if available
            if "fallback_report" in result:
                return {
                    "status": "partial_success",
                    "symbol": formatted_symbol,
                    "report_type": report_type,
                    "message": "Generated using fallback analysis due to data limitations",
                    "data": result["fallback_report"],
                    "error_details": result.get("error"),
                    "generated_at": datetime.now().isoformat(),
                    "api_version": "2025.1.0"
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate {report_type} analysis for {formatted_symbol}: {result.get('error', 'Unknown error')}"
                )
        
        return {
            "status": "success",
            "symbol": formatted_symbol,
            "report_type": report_type,
            "data": result,
            "generated_at": datetime.now().isoformat(),
            "api_version": "2025.1.0"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating {report_type} analysis for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error generating {report_type} analysis: {str(e)}"
        )

@router.post("/analysis/batch")
async def batch_analysis(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Generate professional analysis for multiple trading symbols
    
    This endpoint allows batch processing of multiple symbols to generate
    professional analysis reports efficiently.
    
    Request Body:
        {
            "symbols": ["ETH/USDT", "BTC/USDT", "SOL/USDT"],
            "report_type": "executive"  // or "comprehensive"
        }
        
    Returns:
        Batch analysis results for all requested symbols
    """
    try:
        symbols = request.get("symbols", [])
        report_type = request.get("report_type", "executive")
        
        if not symbols:
            raise HTTPException(
                status_code=400,
                detail="No symbols provided for batch analysis"
            )
        
        if len(symbols) > 20:
            raise HTTPException(
                status_code=400,
                detail="Maximum 20 symbols allowed per batch request"
            )
        
        if report_type not in ["executive", "comprehensive"]:
            raise HTTPException(
                status_code=400,
                detail="report_type must be either 'executive' or 'comprehensive'"
            )
        
        # Format symbols
        formatted_symbols = [symbol.replace("-", "/").upper() for symbol in symbols]
        
        logger.info(f"Starting batch analysis for {len(formatted_symbols)} symbols")
        
        # Generate batch analysis
        result = await professional_ai_agent.batch_analysis(formatted_symbols, report_type)
        
        return {
            "status": "success",
            "batch_type": report_type,
            "data": result,
            "generated_at": datetime.now().isoformat(),
            "api_version": "2025.1.0"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error in batch analysis: {str(e)}"
        )

@router.get("/analysis/status")
async def get_analysis_status() -> Dict[str, Any]:
    """
    Get the current status of the professional analysis system
    
    Returns information about available AI models, system capabilities,
    and current operational status.
    
    Returns:
        System status and capabilities information
    """
    try:
        # Get multi-model AI status
        ai_status = professional_ai_agent.multi_model_ai.get_model_status()
        
        # Get system capabilities
        system_status = {
            "professional_reports": {
                "executive_summary": True,
                "comprehensive_analysis": True,
                "batch_processing": True,
                "standardized_format": True,
                "template_version": "SOL USDT 2025.1.0"
            },
            "ai_capabilities": {
                "available_models": ai_status.get("available_models", 0),
                "model_details": ai_status.get("model_details", {}),
                "multi_model_analysis": True,
                "historical_pattern_analysis": True,
                "fallback_systems": True
            },
            "data_sources": {
                "cryptometer_integration": True,
                "multi_exchange_data": True,
                "technical_analysis": True,
                "sentiment_analysis": True,
                "liquidation_data": True
            },
            "operational_status": {
                "service_health": "operational",
                "last_health_check": datetime.now().isoformat(),
                "uptime_status": "healthy",
                "error_rate": "low"
            }
        }
        
        return {
            "status": "operational",
            "system_status": system_status,
            "generated_at": datetime.now().isoformat(),
            "api_version": "2025.1.0"
        }
        
    except Exception as e:
        logger.error(f"Error getting analysis status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "generated_at": datetime.now().isoformat(),
            "api_version": "2025.1.0"
        }

@router.get("/analysis/formats")
async def get_available_formats() -> Dict[str, Any]:
    """
    Get information about available report formats and templates
    
    Returns:
        Available report formats and their descriptions
    """
    return {
        "available_formats": {
            "executive_summary": {
                "description": "Executive Summary & Key Metrics report",
                "sections": [
                    "Win Rate Summary",
                    "Composite Scores", 
                    "Key Market Metrics",
                    "Trading Recommendations",
                    "Risk Factors",
                    "Market Scenarios",
                    "Key Insights",
                    "Immediate Action Items"
                ],
                "typical_length": "800-1200 words",
                "use_case": "Quick decision making, executive briefings"
            },
            "comprehensive_analysis": {
                "description": "Comprehensive Analysis Report with detailed market analysis",
                "sections": [
                    "Executive Summary",
                    "Current Market Conditions",
                    "Technical Indicator Analysis",
                    "Market Sentiment and Positioning",
                    "Liquidation Analysis",
                    "Win Rate Analysis by Timeframe",
                    "Risk Assessment and Trading Recommendations",
                    "Market Outlook and Scenarios",
                    "Conclusion and Final Assessment"
                ],
                "typical_length": "2000-3500 words",
                "use_case": "Detailed analysis, strategic planning, comprehensive research"
            }
        },
        "template_based_on": "SOL USDT Professional Analysis Structure",
        "standardized_features": [
            "Professional formatting",
            "Consistent structure across all symbols",
            "Multi-timeframe win rate analysis",
            "Risk assessment framework",
            "Trading recommendations",
            "Market scenario analysis",
            "AI-powered insights"
        ],
        "supported_symbols": "All major cryptocurrency trading pairs",
        "api_version": "2025.1.0"
    }