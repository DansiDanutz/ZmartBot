#!/usr/bin/env python3
"""
Historical Analysis API Routes
Advanced endpoints for historical pattern analysis with multi-timeframe win rate predictions
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ..services.historical_ai_analysis_agent import HistoricalAIAnalysisAgent
from ..services.advanced_learning_agent import AdvancedLearningAgent
from ..services.historical_pattern_database import TimeFrame, Direction
from ..routes.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/historical-analysis", tags=["historical-analysis"])

# Initialize Historical AI Analysis Agent
try:
    historical_ai_agent = HistoricalAIAnalysisAgent()
    logger.info("Historical AI Analysis Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Historical AI Analysis Agent: {e}")
    historical_ai_agent = None

@router.get("/report/{symbol}")
async def generate_historical_analysis_report(
    symbol: str,
    store_prediction: bool = Query(True, description="Store prediction for historical learning"),
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generate comprehensive historical-enhanced analysis report with multi-timeframe win rates
    
    Args:
        symbol: Trading symbol (e.g., 'ETH', 'BTC')
        store_prediction: Whether to store prediction for historical validation
        current_user: Authenticated user
    
    Returns:
        Comprehensive historical analysis with win rate predictions
    """
    if not historical_ai_agent:
        raise HTTPException(
            status_code=503,
            detail="Historical AI Analysis Agent not available"
        )
    
    try:
        logger.info(f"Generating historical analysis report for {symbol}")
        
        # Generate comprehensive historical analysis
        analysis_result = await historical_ai_agent.generate_historical_enhanced_report(
            symbol.upper(), store_prediction
        )
        
        return {
            "success": True,
            "symbol": analysis_result['symbol'],
            "prediction_id": analysis_result['prediction_id'],
            "report": {
                "content": analysis_result['report_content'],
                "confidence_score": analysis_result['confidence_score'],
                "word_count": analysis_result['word_count'],
                "timestamp": analysis_result['timestamp']
            },
            "analysis_data": {
                "cryptometer_analysis": analysis_result['cryptometer_analysis'],
                "multi_timeframe_analysis": analysis_result['multi_timeframe_analysis'],
                "historical_insights": analysis_result['historical_insights']
            },
            "metadata": {
                "analysis_type": "historical_enhanced_ai_analysis",
                "prediction_stored": store_prediction,
                "user": current_user.get('username', 'unknown'),
                "features": [
                    "Multi-timeframe win rate analysis",
                    "Historical pattern validation",
                    "Probability-based scoring",
                    "Top 10 pattern analysis",
                    "Real-time learning integration"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating historical analysis for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate historical analysis: {str(e)}"
        )

@router.get("/summary/{symbol}")
async def get_symbol_historical_summary(
    symbol: str,
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get comprehensive historical summary for a symbol
    
    Args:
        symbol: Trading symbol
        current_user: Authenticated user
    
    Returns:
        Historical summary with reliability assessment
    """
    if not historical_ai_agent:
        raise HTTPException(
            status_code=503,
            detail="Historical AI Analysis Agent not available"
        )
    
    try:
        summary = await historical_ai_agent.get_symbol_historical_summary(symbol.upper())
        
        return {
            "success": True,
            "data": summary,
            "recommendations": {
                "trading_confidence": summary['reliability_assessment']['assessment'],
                "data_quality": summary['historical_summary']['historical_analysis']['overall_statistics']['data_maturity'],
                "suggested_timeframes": [
                    tf for tf, count in summary['timeframe_coverage'].items() if count > 5
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting historical summary for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get historical summary: {str(e)}"
        )

@router.get("/patterns/{symbol}")
async def get_top_patterns_analysis(
    symbol: str,
    direction: str = Query("LONG", description="Trading direction (LONG/SHORT)"),
    timeframe: str = Query("7d", description="Analysis timeframe (24h-48h/7d/1m)"),
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get detailed top patterns analysis for specific parameters
    
    Args:
        symbol: Trading symbol
        direction: Trading direction (LONG/SHORT)
        timeframe: Analysis timeframe
        current_user: Authenticated user
    
    Returns:
        Top patterns analysis with win rates and probabilities
    """
    if not historical_ai_agent:
        raise HTTPException(
            status_code=503,
            detail="Historical AI Analysis Agent not available"
        )
    
    # Validate parameters
    if direction not in ["LONG", "SHORT"]:
        raise HTTPException(
            status_code=400,
            detail="Direction must be 'LONG' or 'SHORT'"
        )
    
    if timeframe not in ["24h-48h", "7d", "1m"]:
        raise HTTPException(
            status_code=400,
            detail="Timeframe must be '24h-48h', '7d', or '1m'"
        )
    
    try:
        patterns_analysis = await historical_ai_agent.get_top_patterns_analysis(
            symbol.upper(), direction, timeframe
        )
        
        if 'error' in patterns_analysis:
            raise HTTPException(
                status_code=500,
                detail=patterns_analysis['error']
            )
        
        return {
            "success": True,
            "data": patterns_analysis,
            "summary": {
                "total_top_patterns": len(patterns_analysis['top_patterns']),
                "matching_current_patterns": len(patterns_analysis['matching_current_patterns']),
                "analysis_recommendation": patterns_analysis['analysis_recommendation']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patterns analysis for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get patterns analysis: {str(e)}"
        )

@router.get("/multi-timeframe/{symbol}")
async def get_multi_timeframe_analysis(
    symbol: str,
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get multi-timeframe analysis with win rate predictions
    
    Args:
        symbol: Trading symbol
        current_user: Authenticated user
    
    Returns:
        Multi-timeframe analysis with probability scores
    """
    if not historical_ai_agent:
        raise HTTPException(
            status_code=503,
            detail="Historical AI Analysis Agent not available"
        )
    
    try:
        # Get current analysis
        cryptometer_analysis = await historical_ai_agent.cryptometer_analyzer.analyze_symbol_complete(symbol.upper())
        
        # Get multi-timeframe analysis
        multi_timeframe = await historical_ai_agent._get_multi_timeframe_analysis(symbol.upper(), cryptometer_analysis)
        
        # Organize by timeframe
        timeframe_results = {}
        for key, data in multi_timeframe.items():
            timeframe = data['timeframe']
            direction = data['direction']
            
            if timeframe not in timeframe_results:
                timeframe_results[timeframe] = {}
            
            timeframe_results[timeframe][direction] = {
                'win_rate_prediction': data['win_rate_prediction'],
                'confidence_level': data['confidence_level'],
                'recommendation': data['recommendation'],
                'probability_analysis': data['probability_analysis']
            }
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe_analysis": timeframe_results,
            "best_opportunities": [
                {
                    "timeframe": tf,
                    "direction": dir_name,
                    "win_rate": dir_data['win_rate_prediction'],
                    "confidence": dir_data['confidence_level']
                }
                for tf, directions in timeframe_results.items()
                for dir_name, dir_data in directions.items()
                if dir_data['win_rate_prediction'] > 0.6 and dir_data['confidence_level'] > 0.5
            ],
            "overall_recommendation": "Strong opportunities found" if any(
                dir_data['win_rate_prediction'] > 0.7 and dir_data['confidence_level'] > 0.6
                for directions in timeframe_results.values()
                for dir_data in directions.values()
            ) else "Moderate to weak opportunities"
        }
        
    except Exception as e:
        logger.error(f"Error getting multi-timeframe analysis for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get multi-timeframe analysis: {str(e)}"
        )

@router.get("/database-status")
async def get_historical_database_status(
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get comprehensive historical database status
    
    Returns:
        Database statistics and status information
    """
    if not historical_ai_agent:
        raise HTTPException(
            status_code=503,
            detail="Historical AI Analysis Agent not available"
        )
    
    try:
        database_status = historical_ai_agent.advanced_learning_agent.get_database_status()
        
        return {
            "success": True,
            "database_status": database_status,
            "capabilities": {
                "historical_pattern_storage": True,
                "multi_timeframe_analysis": True,
                "win_rate_predictions": True,
                "top_pattern_tracking": True,
                "probability_scoring": True,
                "real_time_learning": True
            },
            "supported_timeframes": ["24h-48h", "7d", "1m"],
            "supported_directions": ["LONG", "SHORT", "NEUTRAL"],
            "features": [
                "Historical pattern database with win rate tracking",
                "Top 10 patterns per symbol/direction/timeframe",
                "Probability-based scoring system",
                "Multi-timeframe validation",
                "Real-time learning integration",
                "Endpoint performance tracking"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get database status: {str(e)}"
        )

@router.get("/win-rates/{symbol}")
async def get_symbol_win_rates(
    symbol: str,
    timeframe: Optional[str] = Query(None, description="Filter by timeframe"),
    direction: Optional[str] = Query(None, description="Filter by direction"),
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get historical win rates for a symbol with optional filtering
    
    Args:
        symbol: Trading symbol
        timeframe: Optional timeframe filter
        direction: Optional direction filter
        current_user: Authenticated user
    
    Returns:
        Historical win rates and statistics
    """
    if not historical_ai_agent:
        raise HTTPException(
            status_code=503,
            detail="Historical AI Analysis Agent not available"
        )
    
    try:
        comprehensive_analysis = historical_ai_agent.advanced_learning_agent.get_comprehensive_analysis(symbol.upper())
        
        win_rates = {}
        
        for tf_name, tf_data in comprehensive_analysis['historical_analysis']['timeframes'].items():
            if timeframe and tf_name != timeframe:
                continue
                
            win_rates[tf_name] = {}
            
            # Long patterns
            if not direction or direction.upper() == "LONG":
                long_patterns = tf_data['long_patterns']
                if long_patterns:
                    win_rates[tf_name]['LONG'] = {
                        'avg_win_rate': sum(p.win_rate for p in long_patterns) / len(long_patterns),
                        'best_win_rate': max(p.win_rate for p in long_patterns),
                        'total_patterns': len(long_patterns),
                        'avg_probability_score': sum(p.probability_score for p in long_patterns) / len(long_patterns)
                    }
            
            # Short patterns
            if not direction or direction.upper() == "SHORT":
                short_patterns = tf_data['short_patterns']
                if short_patterns:
                    win_rates[tf_name]['SHORT'] = {
                        'avg_win_rate': sum(p.win_rate for p in short_patterns) / len(short_patterns),
                        'best_win_rate': max(p.win_rate for p in short_patterns),
                        'total_patterns': len(short_patterns),
                        'avg_probability_score': sum(p.probability_score for p in short_patterns) / len(short_patterns)
                    }
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "win_rates": win_rates,
            "overall_statistics": comprehensive_analysis['historical_analysis']['overall_statistics'],
            "reliability_assessment": comprehensive_analysis['reliability_assessment'],
            "filters_applied": {
                "timeframe": timeframe,
                "direction": direction
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting win rates for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get win rates: {str(e)}"
        )

@router.get("/status")
async def get_historical_analysis_status() -> Dict[str, Any]:
    """
    Get Historical Analysis system status and capabilities
    
    Returns:
        System status and feature information
    """
    return {
        "success": True,
        "agent_status": "available" if historical_ai_agent else "unavailable",
        "capabilities": {
            "historical_pattern_analysis": historical_ai_agent is not None,
            "multi_timeframe_win_rates": historical_ai_agent is not None,
            "probability_based_scoring": historical_ai_agent is not None,
            "top_pattern_tracking": historical_ai_agent is not None,
            "real_time_learning": historical_ai_agent is not None,
            "ai_report_generation": historical_ai_agent is not None
        },
        "features": {
            "timeframes_supported": ["24h-48h", "7d", "1m"],
            "directions_supported": ["LONG", "SHORT", "NEUTRAL"],
            "pattern_storage": "Top 10 patterns per symbol/direction/timeframe",
            "win_rate_calculation": "Historical validation with probability scoring",
            "learning_integration": "Real-time learning with historical validation",
            "ai_enhancement": "ChatGPT-4 Mini with historical context"
        },
        "endpoints": {
            "historical_report": "/historical-analysis/report/{symbol}",
            "symbol_summary": "/historical-analysis/summary/{symbol}",
            "top_patterns": "/historical-analysis/patterns/{symbol}",
            "multi_timeframe": "/historical-analysis/multi-timeframe/{symbol}",
            "win_rates": "/historical-analysis/win-rates/{symbol}",
            "database_status": "/historical-analysis/database-status",
            "system_status": "/historical-analysis/status"
        },
        "database_features": {
            "historical_patterns": "Comprehensive pattern storage with outcomes",
            "pattern_statistics": "Win rates, profit factors, reliability ratings",
            "top_patterns": "Best performing patterns by category",
            "endpoint_performance": "Historical endpoint accuracy tracking",
            "market_conditions": "Market condition pattern analysis"
        }
    }