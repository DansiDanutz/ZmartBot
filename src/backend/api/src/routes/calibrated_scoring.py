"""
Calibrated Scoring API Routes
Provides independent component scoring endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging
from datetime import datetime

from ..services.calibrated_scoring_service import CalibratedScoringService, IndependentScores, ComponentScore
from ..routes.auth import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calibrated-scoring", tags=["calibrated-scoring"])

# Initialize the calibrated scoring service
scoring_service = CalibratedScoringService()

@router.get("/symbol/{symbol}", response_model=Dict[str, Any])
async def get_independent_scores(
    symbol: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get independent scores from all components (KingFisher, Cryptometer, RiskMetric)
    
    Returns:
    - Individual scores for each component
    - Win rates and confidence levels
    - Pattern analysis details
    - No aggregation (flexible for future implementation)
    """
    try:
        logger.info(f"Getting independent scores for {symbol}")
        
        # Get independent scores
        scores = await scoring_service.get_independent_scores(symbol)
        
        # Convert to response format
        response = {
            "symbol": scores.symbol,
            "timestamp": scores.timestamp.isoformat(),
            "components": {}
        }
        
        # Add available component scores
        available_scores = scores.get_available_scores()
        
        for component, score in available_scores.items():
            response["components"][component] = {
                "score": score.score,
                "win_rate": score.win_rate,
                "direction": score.direction,
                "confidence": score.confidence,
                "patterns_count": len(score.patterns),
                "patterns": score.patterns,
                "analysis_details": score.analysis_details,
                "timestamp": score.timestamp.isoformat(),
                "interpretation": _get_score_interpretation(score.score)
            }
        
        # Add summary
        response["summary"] = {
            "available_components": list(available_scores.keys()),
            "total_components": len(available_scores),
            "aggregation_ready": len(available_scores) > 0,
            "note": "Individual component scores - aggregation flexible for future implementation"
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting independent scores for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing {symbol}: {str(e)}")

@router.get("/component/{component}/{symbol}", response_model=Dict[str, Any])
async def get_component_score(
    component: str,
    symbol: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get score from a specific component only
    
    Components:
    - cryptometer: Calibrated win-rate based scoring
    - kingfisher: Liquidation analysis scoring (placeholder)
    - riskmetric: Risk-based scoring (placeholder)
    """
    try:
        logger.info(f"Getting {component} score for {symbol}")
        
        # Validate component
        valid_components = ["cryptometer", "kingfisher", "riskmetric"]
        if component not in valid_components:
            raise HTTPException(status_code=400, detail=f"Invalid component. Must be one of: {valid_components}")
        
        # Get component score
        if component == "cryptometer":
            score = await scoring_service.cryptometer_engine.get_symbol_score(symbol)
        elif component == "kingfisher":
            score = await scoring_service.kingfisher_engine.get_symbol_score(symbol)
        elif component == "riskmetric":
            score = await scoring_service.riskmetric_engine.get_symbol_score(symbol)
        
        # Convert to response format
        response = {
            "symbol": symbol,
            "component": component,
            "score": score.score,
            "win_rate": score.win_rate,
            "direction": score.direction,
            "confidence": score.confidence,
            "patterns_count": len(score.patterns),
            "patterns": score.patterns,
            "analysis_details": score.analysis_details,
            "timestamp": score.timestamp.isoformat(),
            "interpretation": _get_score_interpretation(score.score)
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting {component} score for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing {symbol} with {component}: {str(e)}")

@router.get("/cryptometer/{symbol}/detailed", response_model=Dict[str, Any])
async def get_cryptometer_detailed_analysis(
    symbol: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get detailed Cryptometer analysis with pattern breakdown
    Shows the calibrated win-rate system in action
    """
    try:
        logger.info(f"Getting detailed Cryptometer analysis for {symbol}")
        
        # Get Cryptometer score with detailed analysis
        score = await scoring_service.cryptometer_engine.get_symbol_score(symbol)
        
        # Detailed response
        response = {
            "symbol": symbol,
            "component": "cryptometer",
            "calibrated_system": {
                "methodology": "Realistic win-rate scoring where 95-100 points = exceptional opportunity",
                "calibration": {
                    "95-100": "EXCEPTIONAL (Royal Flush) - <1% of time",
                    "90-94": "ALL-IN (Very Rare) - 1-3% of time", 
                    "80-89": "TAKE TRADE (Rare) - 5-10% of time",
                    "70-79": "MODERATE - Consider small position",
                    "60-69": "WEAK - Avoid",
                    "<60": "AVOID - Wait for better setup"
                }
            },
            "analysis": {
                "final_score": score.score,
                "win_rate": score.win_rate,
                "direction": score.direction,
                "confidence": score.confidence,
                "interpretation": _get_score_interpretation(score.score),
                "patterns_detected": len(score.patterns),
                "timestamp": score.timestamp.isoformat()
            },
            "patterns": score.patterns,
            "detailed_analysis": score.analysis_details,
            "trading_recommendation": _get_trading_recommendation(score.score, score.direction)
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting detailed Cryptometer analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing {symbol}: {str(e)}")

@router.get("/batch/{symbols}", response_model=Dict[str, Any])
async def get_batch_scores(
    symbols: str,  # Comma-separated list
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get independent scores for multiple symbols
    symbols: Comma-separated list (e.g., "BTC,ETH,SOL")
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        logger.info(f"Getting batch scores for {len(symbol_list)} symbols: {symbol_list}")
        
        results = {}
        
        for symbol in symbol_list:
            try:
                scores = await scoring_service.get_independent_scores(symbol)
                available_scores = scores.get_available_scores()
                
                results[symbol] = {
                    "timestamp": scores.timestamp.isoformat(),
                    "components": {}
                }
                
                for component, score in available_scores.items():
                    results[symbol]["components"][component] = {
                        "score": score.score,
                        "win_rate": score.win_rate,
                        "direction": score.direction,
                        "confidence": score.confidence,
                        "interpretation": _get_score_interpretation(score.score)
                    }
                
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                results[symbol] = {"error": str(e)}
        
        # Summary
        successful = len([r for r in results.values() if "error" not in r])
        failed = len(symbol_list) - successful
        
        response = {
            "symbols_requested": symbol_list,
            "results": results,
            "summary": {
                "total_symbols": len(symbol_list),
                "successful": successful,
                "failed": failed,
                "success_rate": successful / len(symbol_list) * 100 if symbol_list else 0
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in batch scoring: {e}")
        raise HTTPException(status_code=500, detail=f"Batch scoring error: {str(e)}")

@router.get("/system/status", response_model=Dict[str, Any])
async def get_system_status(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get calibrated scoring system status and configuration
    """
    try:
        response = {
            "system": "Calibrated Independent Scoring System",
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "cryptometer": {
                    "status": "active",
                    "description": "Calibrated win-rate based scoring (95-100 = exceptional)",
                    "methodology": "Realistic pattern success rates with confluence multipliers",
                    "api_endpoints": 6
                },
                "kingfisher": {
                    "status": "placeholder",
                    "description": "Liquidation analysis scoring",
                    "methodology": "Pending implementation"
                },
                "riskmetric": {
                    "status": "placeholder", 
                    "description": "Risk-based scoring",
                    "methodology": "Pending implementation"
                }
            },
            "scoring_philosophy": {
                "independent_scores": "Each component provides its own score independently",
                "no_fixed_aggregation": "Aggregation is flexible for future implementation",
                "realistic_calibration": "80%+ scores are rare trading opportunities",
                "win_rate_based": "Scores represent realistic win rate expectations"
            },
            "score_interpretation": {
                "95-100": "EXCEPTIONAL - Royal Flush (<1% of time)",
                "90-94": "ALL-IN - Very Rare (1-3% of time)",
                "80-89": "TAKE TRADE - Rare (5-10% of time)", 
                "70-79": "MODERATE - Consider small position",
                "60-69": "WEAK - Avoid",
                "<60": "AVOID - Wait for better setup"
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=f"System status error: {str(e)}")

def _get_score_interpretation(score: float) -> str:
    """Get interpretation for a score"""
    if score >= 95:
        return "EXCEPTIONAL (95%+ - Royal Flush)"
    elif score >= 90:
        return "ALL-IN (90-94% - Very Rare)"
    elif score >= 80:
        return "TAKE TRADE (80-89% - Rare)"
    elif score >= 70:
        return "MODERATE (70-79%)"
    elif score >= 60:
        return "WEAK (60-69%)"
    else:
        return "AVOID (<60%)"

def _get_trading_recommendation(score: float, direction: str) -> Dict[str, Any]:
    """Get trading recommendation based on score and direction"""
    if score >= 95:
        return {
            "action": "ALL_IN",
            "position_size": "MAXIMUM",
            "urgency": "IMMEDIATE",
            "description": f"Exceptional opportunity - {direction} with maximum position"
        }
    elif score >= 90:
        return {
            "action": "AGGRESSIVE",
            "position_size": "LARGE", 
            "urgency": "HIGH",
            "description": f"Very rare opportunity - {direction} with large position"
        }
    elif score >= 80:
        return {
            "action": "TAKE_TRADE",
            "position_size": "MEDIUM",
            "urgency": "MODERATE",
            "description": f"Good opportunity - {direction} with medium position"
        }
    elif score >= 70:
        return {
            "action": "CONSIDER",
            "position_size": "SMALL",
            "urgency": "LOW",
            "description": f"Moderate opportunity - {direction} with small position"
        }
    else:
        return {
            "action": "AVOID",
            "position_size": "NONE",
            "urgency": "NONE",
            "description": "Wait for better setup"
        }