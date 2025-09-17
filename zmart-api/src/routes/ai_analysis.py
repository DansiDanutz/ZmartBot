#!/usr/bin/env python3
"""
AI Analysis Report API Routes
Provides endpoints for generating comprehensive technical analysis reports
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ..services.ai_analysis_agent import AIAnalysisAgent, AnalysisReport
from ..routes.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-analysis", tags=["ai-analysis"])

# Initialize AI Analysis Agent
try:
    ai_agent = AIAnalysisAgent()
    logger.info("AI Analysis Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AI Analysis Agent: {e}")
    ai_agent = None

@router.get("/report/{symbol}")
async def generate_analysis_report(
    symbol: str,
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generate comprehensive AI-powered technical analysis report for a symbol
    
    Args:
        symbol: Trading symbol (e.g., 'ETH', 'BTC')
        current_user: Authenticated user
    
    Returns:
        Comprehensive technical analysis report
    """
    if not ai_agent:
        raise HTTPException(
            status_code=503, 
            detail="AI Analysis Agent not available. Check OpenAI API key configuration."
        )
    
    try:
        logger.info(f"Generating AI analysis report for {symbol} (user: {current_user.get('username', 'unknown')})")
        
        # Generate comprehensive report
        report = await ai_agent.generate_comprehensive_report(symbol.upper())
        
        return {
            "success": True,
            "symbol": report.symbol,
            "report": {
                "content": report.report_content,
                "summary": report.summary,
                "recommendations": report.recommendations,
                "risk_factors": report.risk_factors,
                "confidence_score": report.confidence_score,
                "word_count": report.word_count,
                "timestamp": report.timestamp.isoformat()
            },
            "metadata": {
                "generated_by": "AI Analysis Agent",
                "model": "GPT-4 Mini",
                "analysis_type": "comprehensive_technical_analysis",
                "user": current_user.get('username', 'unknown')
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating AI analysis report for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analysis report: {str(e)}"
        )

@router.get("/report/{symbol}/markdown")
async def generate_analysis_report_markdown(
    symbol: str,
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generate analysis report in markdown format for easy viewing/saving
    
    Args:
        symbol: Trading symbol (e.g., 'ETH', 'BTC')
        current_user: Authenticated user
    
    Returns:
        Analysis report in markdown format
    """
    if not ai_agent:
        raise HTTPException(
            status_code=503, 
            detail="AI Analysis Agent not available. Check OpenAI API key configuration."
        )
    
    try:
        logger.info(f"Generating markdown AI analysis report for {symbol}")
        
        # Generate comprehensive report
        report = await ai_agent.generate_comprehensive_report(symbol.upper())
        
        # Create markdown header
        markdown_header = f"""# {report.symbol}/USDT AI Technical Analysis Report

**Generated:** {report.timestamp.strftime('%B %d, %Y at %H:%M UTC')}  
**Analysis Agent:** AI-Powered Technical Analysis  
**Model:** ChatGPT-4 Mini  
**Confidence Score:** {report.confidence_score:.1f}%  
**Word Count:** {report.word_count} words  

---

"""
        
        # Combine header with report content
        full_markdown = markdown_header + report.report_content
        
        return {
            "success": True,
            "symbol": report.symbol,
            "markdown_content": full_markdown,
            "metadata": {
                "confidence_score": report.confidence_score,
                "word_count": report.word_count,
                "timestamp": report.timestamp.isoformat(),
                "filename_suggestion": f"{report.symbol}_Analysis_Report_{report.timestamp.strftime('%Y%m%d_%H%M')}.md"
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating markdown analysis report for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate markdown report: {str(e)}"
        )

@router.get("/report/{symbol}/summary")
async def get_analysis_summary(
    symbol: str,
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get quick analysis summary without full report generation
    
    Args:
        symbol: Trading symbol (e.g., 'ETH', 'BTC')
        current_user: Authenticated user
    
    Returns:
        Quick analysis summary
    """
    if not ai_agent:
        raise HTTPException(
            status_code=503, 
            detail="AI Analysis Agent not available. Check OpenAI API key configuration."
        )
    
    try:
        logger.info(f"Generating analysis summary for {symbol}")
        
        # Get Cryptometer analysis only (faster)
        cryptometer_analysis = await ai_agent.cryptometer_analyzer.analyze_symbol(symbol.upper())
        
        # Extract key insights - EndpointScore has confidence > 0.5 means success
        successful_endpoints = len([es for es in cryptometer_analysis.endpoint_scores if es.confidence > 0.5])
        total_endpoints = len(cryptometer_analysis.endpoint_scores)
        
        # Get top performing endpoints
        top_endpoints = sorted(
            [es for es in cryptometer_analysis.endpoint_scores if es.confidence > 0.5],
            key=lambda x: x.score,
            reverse=True
        )[:5]
        
        return {
            "success": True,
            "symbol": cryptometer_analysis.symbol,
            "summary": {
                "overall_score": cryptometer_analysis.total_score,  # Use total_score instead of calibrated_score
                "confidence": cryptometer_analysis.confidence,
                "direction": cryptometer_analysis.signal,  # Use signal instead of direction
                "endpoint_coverage": f"{successful_endpoints}/{total_endpoints}",
                "coverage_percentage": (successful_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0,
                "analysis_summary": cryptometer_analysis.summary  # Use summary instead of analysis_summary
            },
            "top_performing_endpoints": [
                {
                    "name": ep.endpoint_name,  # Use endpoint_name instead of endpoint
                    "score": ep.score,
                    "confidence": ep.confidence,
                    "weight": ep.weight,  # Add weight info
                    "data": ep.data  # Use data instead of analysis/patterns
                }
                for ep in top_endpoints
            ],
            "timestamp": cryptometer_analysis.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating analysis summary for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analysis summary: {str(e)}"
        )

@router.get("/status")
async def get_ai_analysis_status() -> Dict[str, Any]:
    """
    Get AI Analysis Agent status and configuration
    
    Returns:
        Agent status and capabilities
    """
    return {
        "success": True,
        "agent_status": "available" if ai_agent else "unavailable",
        "capabilities": {
            "comprehensive_reports": ai_agent is not None,
            "markdown_export": ai_agent is not None,
            "quick_summaries": ai_agent is not None,
            "cryptometer_integration": True,
            "ai_model": "GPT-4 Mini" if ai_agent else None
        },
        "configuration": {
            "openai_configured": ai_agent is not None,
            "cryptometer_configured": True,
            "target_word_count": "1000-1500 words",
            "supported_formats": ["json", "markdown"]
        },
        "endpoints": {
            "generate_report": "/ai-analysis/report/{symbol}",
            "markdown_report": "/ai-analysis/report/{symbol}/markdown", 
            "quick_summary": "/ai-analysis/report/{symbol}/summary",
            "status": "/ai-analysis/status"
        }
    }