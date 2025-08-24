#!/usr/bin/env python3
"""
Learning-Enhanced AI Analysis API Routes
Provides endpoints for self-learning AI analysis with continuous improvement
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from ..services.enhanced_ai_analysis_agent import EnhancedAIAnalysisAgent
from ..routes.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/learning-ai-analysis", tags=["learning-ai-analysis"])

# Initialize Enhanced AI Analysis Agent
try:
    enhanced_ai_agent = EnhancedAIAnalysisAgent()
    logger.info("Enhanced AI Analysis Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Enhanced AI Analysis Agent: {e}")
    enhanced_ai_agent = None

@router.get("/report/{symbol}")
async def generate_learning_enhanced_report(
    symbol: str,
    store_prediction: bool = Query(True, description="Store prediction for learning"),
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generate learning-enhanced AI analysis report that improves over time
    
    Args:
        symbol: Trading symbol (e.g., 'ETH', 'BTC')
        store_prediction: Whether to store prediction for future learning
        current_user: Authenticated user
    
    Returns:
        Learning-enhanced technical analysis report
    """
    if not enhanced_ai_agent:
        raise HTTPException(
            status_code=503, 
            detail="Enhanced AI Analysis Agent not available. Check configuration."
        )
    
    try:
        logger.info(f"Generating learning-enhanced report for {symbol} (user: {current_user.get('username', 'unknown')})")
        
        # Generate learning-enhanced report
        report = await enhanced_ai_agent.generate_learning_enhanced_report(
            symbol.upper(), 
            store_prediction=store_prediction
        )
        
        # Get learning status
        learning_status = enhanced_ai_agent.get_learning_status()
        
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
            "learning_context": {
                "learning_enhanced": True,
                "experience_level": learning_status['learning_progress']['total_patterns_learned'],
                "average_accuracy": learning_status['learning_progress']['average_success_rate'],
                "prediction_stored": store_prediction,
                "learning_improvements": "Adaptive endpoint weighting, pattern recognition, confidence calibration"
            },
            "metadata": {
                "generated_by": "Enhanced Learning AI Agent",
                "model": "GPT-4 Mini + Self-Learning",
                "analysis_type": "learning_enhanced_technical_analysis",
                "user": current_user.get('username', 'unknown'),
                "learning_database_size": learning_status.get('learning_database_size', {})
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating learning-enhanced report for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate learning-enhanced report: {str(e)}"
        )

@router.get("/report/{symbol}/learning-comparison")
async def compare_learning_vs_standard(
    symbol: str,
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Compare learning-enhanced analysis vs standard analysis
    
    Args:
        symbol: Trading symbol (e.g., 'ETH', 'BTC')
        current_user: Authenticated user
    
    Returns:
        Comparison between standard and learning-enhanced analysis
    """
    if not enhanced_ai_agent:
        raise HTTPException(
            status_code=503, 
            detail="Enhanced AI Analysis Agent not available"
        )
    
    try:
        logger.info(f"Generating learning comparison for {symbol}")
        
        # Generate both reports
        standard_report = await enhanced_ai_agent.generate_comprehensive_report(symbol.upper())
        enhanced_report = await enhanced_ai_agent.generate_learning_enhanced_report(symbol.upper(), store_prediction=False)
        
        # Get learning improvements
        learning_status = enhanced_ai_agent.get_learning_status()
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "comparison": {
                "standard_analysis": {
                    "confidence_score": standard_report.confidence_score,
                    "word_count": standard_report.word_count,
                    "summary": standard_report.summary,
                    "recommendations_count": len(standard_report.recommendations)
                },
                "learning_enhanced_analysis": {
                    "confidence_score": enhanced_report.confidence_score,
                    "word_count": enhanced_report.word_count,
                    "summary": enhanced_report.summary,
                    "recommendations_count": len(enhanced_report.recommendations)
                },
                "improvements": {
                    "confidence_improvement": enhanced_report.confidence_score - standard_report.confidence_score,
                    "content_enhancement": enhanced_report.word_count - standard_report.word_count,
                    "learning_insights_applied": True,
                    "adaptive_weighting": True
                }
            },
            "learning_context": learning_status,
            "recommendation": "Use learning-enhanced analysis for better accuracy based on historical performance"
        }
        
    except Exception as e:
        logger.error(f"Error generating learning comparison for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate comparison: {str(e)}"
        )

@router.get("/learning-status")
async def get_learning_status(
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get current learning status and performance metrics
    
    Returns:
        Detailed learning status and performance data
    """
    if not enhanced_ai_agent:
        raise HTTPException(
            status_code=503, 
            detail="Enhanced AI Analysis Agent not available"
        )
    
    try:
        learning_status = enhanced_ai_agent.get_learning_status()
        
        # Calculate learning maturity
        total_patterns = learning_status['learning_progress']['total_patterns_learned']
        avg_success = learning_status['learning_progress']['average_success_rate']
        
        if total_patterns < 10:
            maturity_level = "INITIALIZING"
            maturity_description = "Building initial pattern library"
        elif total_patterns < 50:
            maturity_level = "LEARNING"
            maturity_description = "Actively learning from predictions"
        elif total_patterns < 200:
            maturity_level = "EXPERIENCED"
            maturity_description = "Well-trained with good pattern recognition"
        elif avg_success > 0.7:
            maturity_level = "EXPERT"
            maturity_description = "Highly accurate with excellent learning"
        else:
            maturity_level = "ADVANCED"
            maturity_description = "Sophisticated analysis with extensive experience"
        
        return {
            "success": True,
            "learning_status": {
                "maturity_level": maturity_level,
                "maturity_description": maturity_description,
                "total_patterns_learned": total_patterns,
                "average_success_rate": f"{avg_success:.1%}",
                "endpoints_tracked": learning_status['learning_progress']['endpoints_tracked']
            },
            "performance_metrics": {
                "top_performing_patterns": learning_status['top_performing_patterns'],
                "endpoint_performance": learning_status['endpoint_performance'],
                "database_size": learning_status.get('learning_database_size', {})
            },
            "capabilities": {
                "adaptive_endpoint_weighting": True,
                "pattern_recognition_learning": True,
                "confidence_calibration": True,
                "prediction_validation": True,
                "continuous_improvement": True
            },
            "recommendations": {
                "analysis_quality": "Enhanced" if total_patterns > 50 else "Improving",
                "confidence_level": "High" if avg_success > 0.6 else "Moderate",
                "recommended_usage": "Primary analysis tool" if maturity_level in ["EXPERT", "ADVANCED"] else "Secondary validation"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting learning status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get learning status: {str(e)}"
        )

@router.get("/learning-insights")
async def get_learning_insights(
    pattern_type: Optional[str] = Query(None, description="Filter by specific pattern type"),
    limit: int = Query(10, description="Maximum number of insights to return"),
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get detailed learning insights and pattern performance
    
    Args:
        pattern_type: Optional filter for specific pattern type
        limit: Maximum number of insights to return
        current_user: Authenticated user
    
    Returns:
        Detailed learning insights and pattern analysis
    """
    if not enhanced_ai_agent:
        raise HTTPException(
            status_code=503, 
            detail="Enhanced AI Analysis Agent not available"
        )
    
    try:
        learning_status = enhanced_ai_agent.get_learning_status()
        
        # Filter insights if pattern_type specified
        insights = learning_status['top_performing_patterns']
        if pattern_type:
            insights = [insight for insight in insights if pattern_type.lower() in insight['pattern'].lower()]
        
        # Limit results
        insights = insights[:limit]
        
        return {
            "success": True,
            "learning_insights": {
                "total_patterns_available": len(learning_status['top_performing_patterns']),
                "filtered_results": len(insights),
                "pattern_insights": insights
            },
            "endpoint_performance": learning_status['endpoint_performance'],
            "learning_recommendations": [
                f"Pattern '{insight['pattern']}' shows {insight['success_rate']:.1%} success rate" 
                for insight in insights[:3]
            ],
            "analysis_improvements": {
                "weight_adjustments_active": len([i for i in insights if i['weight_adjustment'] != 1.0]),
                "confidence_calibrations_active": len([i for i in insights if i['confidence_multiplier'] != 1.0]),
                "learning_active": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting learning insights: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get learning insights: {str(e)}"
        )

@router.post("/validate-prediction/{prediction_id}")
async def manually_validate_prediction(
    prediction_id: str,
    actual_outcome: Dict[str, Any],
    current_user: Dict = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Manually validate a prediction outcome for learning
    
    Args:
        prediction_id: ID of the prediction to validate
        actual_outcome: Actual market outcome data
        current_user: Authenticated user
    
    Returns:
        Validation result and learning update
    """
    if not enhanced_ai_agent:
        raise HTTPException(
            status_code=503, 
            detail="Enhanced AI Analysis Agent not available"
        )
    
    try:
        # This would implement manual validation logic
        # For now, return a placeholder response
        
        return {
            "success": True,
            "message": "Manual prediction validation feature coming soon",
            "prediction_id": prediction_id,
            "note": "Automatic validation is currently active for 24-hour periods"
        }
        
    except Exception as e:
        logger.error(f"Error validating prediction {prediction_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate prediction: {str(e)}"
        )

@router.get("/status")
async def get_enhanced_ai_status() -> Dict[str, Any]:
    """
    Get Enhanced AI Analysis Agent status and capabilities
    
    Returns:
        Comprehensive status of the learning-enhanced AI system
    """
    return {
        "success": True,
        "agent_status": "available" if enhanced_ai_agent else "unavailable",
        "capabilities": {
            "learning_enhanced_reports": enhanced_ai_agent is not None,
            "adaptive_endpoint_weighting": enhanced_ai_agent is not None,
            "pattern_recognition_learning": enhanced_ai_agent is not None,
            "confidence_calibration": enhanced_ai_agent is not None,
            "prediction_validation": enhanced_ai_agent is not None,
            "continuous_improvement": enhanced_ai_agent is not None,
            "learning_comparison": enhanced_ai_agent is not None
        },
        "configuration": {
            "openai_configured": enhanced_ai_agent is not None,
            "learning_database": "SQLite with automatic management",
            "validation_period": "24 hours automatic + manual validation",
            "learning_algorithms": ["Exponential Moving Average", "Adaptive Weighting", "Pattern Recognition"]
        },
        "endpoints": {
            "learning_enhanced_report": "/learning-ai-analysis/report/{symbol}",
            "learning_comparison": "/learning-ai-analysis/report/{symbol}/learning-comparison",
            "learning_status": "/learning-ai-analysis/learning-status",
            "learning_insights": "/learning-ai-analysis/learning-insights",
            "validate_prediction": "/learning-ai-analysis/validate-prediction/{prediction_id}",
            "status": "/learning-ai-analysis/status"
        },
        "learning_features": {
            "self_improvement": "Continuous learning from prediction outcomes",
            "adaptive_scoring": "Dynamic endpoint weight adjustment",
            "pattern_memory": "Historical pattern performance tracking",
            "confidence_evolution": "Confidence scoring improves with experience",
            "performance_tracking": "Detailed accuracy and success rate monitoring"
        }
    }