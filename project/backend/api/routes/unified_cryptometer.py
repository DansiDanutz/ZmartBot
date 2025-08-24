"""
Unified Cryptometer API Routes
==============================

FastAPI routes for the unified Cryptometer system
Simplified to work with CryptometerEndpointAnalyzer
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from src.services.cryptometer_data_types import CryptometerEndpointAnalyzer
from src.agents.self_learning_cryptometer_agent import get_self_learning_agent

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instance
unified_system = CryptometerEndpointAnalyzer()
self_learning_agent = get_self_learning_agent()

@router.get("/unified/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for unified Cryptometer system
    """
    return {
        "status": "healthy",
        "service": "unified_cryptometer",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "analyzer_initialized": unified_system.initialized,
        "self_learning_enabled": True
    }

@router.get("/unified/analyze/{symbol}")
async def analyze_symbol_unified(symbol: str) -> Dict[str, Any]:
    """
    Complete unified analysis for a symbol using CryptometerEndpointAnalyzer
    """
    try:
        logger.info(f"Starting unified analysis for {symbol}")
        
        # Use the basic analyze_symbol method
        result = await unified_system.analyze_symbol(symbol)
        
        return {
            "success": True,
            "symbol": symbol,
            "timestamp": result.timestamp.isoformat(),
            "total_score": result.total_score,
            "signal": result.signal,
            "confidence": result.confidence,
            "endpoints_analyzed": result.endpoints_analyzed,
            "endpoint_scores": [
                {
                    "endpoint": score.endpoint_name,
                    "score": score.score,
                    "weight": score.weight,
                    "confidence": score.confidence
                }
                for score in result.endpoint_scores
            ],
            "summary": result.summary,
            "message": f"Unified analysis completed for {symbol}"
        }
        
    except Exception as e:
        logger.error(f"Error in unified analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/unified/self-learning/{symbol}")
async def analyze_with_self_learning(symbol: str) -> Dict[str, Any]:
    """
    Analyze symbol using the self-learning agent with 100-point scoring
    """
    try:
        logger.info(f"Starting self-learning analysis for {symbol}")
        
        # First collect Cryptometer data
        from src.services.cryptometer_service import MultiTimeframeCryptometerSystem
        cryptometer = MultiTimeframeCryptometerSystem()
        cryptometer_data = await cryptometer.collect_symbol_data(symbol)
        
        # Then analyze with self-learning agent
        result = await self_learning_agent.analyze_symbol(symbol, cryptometer_data)
        
        return {
            "success": True,
            "symbol": result.symbol,
            "timestamp": result.timestamp.isoformat(),
            "total_score": result.total_score,
            "win_rate_prediction": result.win_rate_prediction,
            "signal": result.signal,
            "confidence": result.confidence,
            "best_timeframe": result.best_timeframe,
            "timeframe_scores": result.timeframe_scores,
            "trade_recommendation": result.trade_recommendation,
            "risk_level": result.risk_level,
            "endpoint_analyses": [
                {
                    "endpoint": ea.endpoint_name,
                    "raw_score": ea.raw_score,
                    "weight": ea.weight,
                    "contribution": ea.contribution_score,
                    "patterns": [
                        {
                            "name": p.pattern_name,
                            "confidence": p.confidence,
                            "win_rate": p.historical_win_rate
                        }
                        for p in ea.patterns_detected
                    ]
                }
                for ea in result.endpoint_analyses[:5]  # Top 5 endpoints
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in self-learning analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Self-learning analysis failed: {str(e)}")

@router.post("/unified/update-learning")
async def update_learning_history(learning_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update learning history with pattern outcome
    
    Expected payload:
    {
        "pattern_name": "price_breakout",
        "was_successful": true
    }
    """
    try:
        pattern_name = learning_data.get('pattern_name')
        was_successful = learning_data.get('was_successful')
        
        if not pattern_name or was_successful is None:
            raise HTTPException(status_code=400, detail="Missing pattern_name or was_successful")
        
        # Update learning history
        self_learning_agent.update_learning(pattern_name, was_successful)
        
        # Get updated win rate
        updated_win_rate = self_learning_agent._get_pattern_win_rate(pattern_name)
        
        return {
            "success": True,
            "pattern_name": pattern_name,
            "was_successful": was_successful,
            "updated_win_rate": updated_win_rate,
            "timestamp": datetime.now().isoformat(),
            "message": "Learning history updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating learning history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update learning: {str(e)}")

@router.get("/unified/pattern-stats")
async def get_pattern_statistics() -> Dict[str, Any]:
    """
    Get statistics for all patterns in the learning history
    """
    try:
        pattern_stats = {}
        
        # Get stats from learning history
        for pattern_name, history in self_learning_agent.learning_history.items():
            # Handle last_updated which could be datetime, timestamp, or string
            last_updated_value = history.get('last_updated')
            
            # Type-safe conversion to ISO format string
            if last_updated_value is None:
                last_updated_str = datetime.now().isoformat()
            elif isinstance(last_updated_value, datetime):
                last_updated_str = last_updated_value.isoformat()
            elif isinstance(last_updated_value, (int, float)):
                # It's a timestamp
                last_updated_str = datetime.fromtimestamp(last_updated_value).isoformat()
            elif isinstance(last_updated_value, str):
                # Already a string
                last_updated_str = last_updated_value
            else:
                # Fallback for any other type
                last_updated_str = str(last_updated_value)
            
            pattern_stats[pattern_name] = {
                "occurrences": history['occurrences'],
                "successful": history['successful'],
                "win_rate": history['win_rate'],
                "last_updated": last_updated_str
            }
        
        # Add base patterns that haven't been learned yet
        for pattern_name, pattern_info in self_learning_agent.pattern_library.items():
            if pattern_name not in pattern_stats:
                pattern_stats[pattern_name] = {
                    "occurrences": 0,
                    "successful": 0,
                    "win_rate": pattern_info['base_win_rate'],
                    "last_updated": "Never (using base rate)"
                }
        
        return {
            "success": True,
            "total_patterns": len(pattern_stats),
            "patterns": pattern_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting pattern statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pattern stats: {str(e)}")

@router.get("/unified/endpoints")
async def get_endpoint_configs() -> Dict[str, Any]:
    """
    Get configuration for all Cryptometer endpoints
    """
    try:
        return {
            "success": True,
            "total_endpoints": len(self_learning_agent.endpoint_configs),
            "endpoints": self_learning_agent.endpoint_configs,
            "weight_sum": sum(config['weight'] for config in self_learning_agent.endpoint_configs.values()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting endpoint configs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get endpoints: {str(e)}")

@router.get("/unified/scoring-thresholds")
async def get_scoring_thresholds() -> Dict[str, Any]:
    """
    Get scoring thresholds and their meanings
    """
    return {
        "success": True,
        "thresholds": {
            "95+": {
                "meaning": "ALL-IN OPPORTUNITY",
                "win_rate": "95%+",
                "position_size": "MAXIMUM",
                "description": "Exceptional setup with very high win probability"
            },
            "90-94": {
                "meaning": "EXCELLENT OPPORTUNITY",
                "win_rate": "90-94%",
                "position_size": "LARGE",
                "description": "Very strong setup with high win probability"
            },
            "85-89": {
                "meaning": "STRONG OPPORTUNITY",
                "win_rate": "85-89%",
                "position_size": "STANDARD",
                "description": "Solid setup with good win probability"
            },
            "80-84": {
                "meaning": "GOOD OPPORTUNITY",
                "win_rate": "80-84%",
                "position_size": "MODERATE",
                "description": "Minimum threshold for trade entry"
            },
            "75-79": {
                "meaning": "MARGINAL OPPORTUNITY",
                "win_rate": "75-79%",
                "position_size": "SMALL or NONE",
                "description": "Below minimum threshold - consider waiting"
            },
            "70-74": {
                "meaning": "WEAK OPPORTUNITY",
                "win_rate": "70-74%",
                "position_size": "NONE",
                "description": "Poor risk/reward - wait for better setup"
            },
            "<70": {
                "meaning": "NO TRADE",
                "win_rate": "<70%",
                "position_size": "NONE",
                "description": "Insufficient edge - stay out of market"
            }
        },
        "key_principle": "80 points = 80% win rate (minimum for trade entry)",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/unified/batch-analysis")
async def batch_analysis(symbols: List[str], background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Analyze multiple symbols in batch
    """
    try:
        if not symbols or len(symbols) > 10:
            raise HTTPException(status_code=400, detail="Provide 1-10 symbols")
        
        results = []
        for symbol in symbols:
            try:
                # Quick analysis using basic analyzer
                analysis = await unified_system.analyze_symbol(symbol)
                results.append({
                    "symbol": symbol,
                    "score": analysis.total_score,
                    "signal": analysis.signal,
                    "confidence": analysis.confidence,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "success": True,
            "total_symbols": len(symbols),
            "successful": sum(1 for r in results if r.get('success')),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")