#!/usr/bin/env python3
"""
Learning Performance Tracking Routes
API endpoints for monitoring and analyzing self-learning system performance
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add learning system import
sys.path.append(str(Path(__file__).parent.parent.parent))
try:
    from src.learning.self_learning_system import learning_system
    LEARNING_AVAILABLE = True
except ImportError:
    LEARNING_AVAILABLE = False
    learning_system = None

# Import enhanced services
try:
    from src.agents.master_scoring_agent import master_scoring_agent
    from src.services.kingfisher_service import KingFisherService
    from src.services.enhanced_cryptometer_service import enhanced_cryptometer_service
    from src.services.unified_riskmetric import unified_riskmetric as enhanced_riskmetric_service
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/learning", tags=["Learning Performance"])

@router.get("/status")
async def get_learning_status() -> Dict[str, Any]:
    """Get overall learning system status"""
    if not LEARNING_AVAILABLE:
        return {
            "learning_enabled": False,
            "error": "Learning system not available",
            "timestamp": datetime.now().isoformat()
        }
    
    return {
        "learning_enabled": True,
        "agents_available": AGENTS_AVAILABLE,
        "system_operational": True,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/performance/overview")
async def get_performance_overview() -> Dict[str, Any]:
    """Get performance overview for all agents"""
    if not LEARNING_AVAILABLE or not learning_system:
        raise HTTPException(status_code=503, detail="Learning system not available")
    
    try:
        agents = [
            "MasterScoringAgent",
            "KingFisherService", 
            "EnhancedCryptometerService",
            "EnhancedRiskMetricService"
        ]
        
        overview = {
            "agents": {},
            "summary": {
                "total_agents": len(agents),
                "learning_agents": 0,
                "avg_accuracy": 0.0,
                "total_predictions": 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        total_accuracy = 0.0
        learning_count = 0
        total_predictions = 0
        
        for agent_name in agents:
            try:
                performance = await learning_system.get_agent_performance(agent_name)
                insights = await learning_system.get_learning_insights(agent_name)
                
                if performance:
                    overview["agents"][agent_name] = {
                        "performance": {
                            "accuracy": performance.accuracy,
                            "total_predictions": performance.total_predictions,
                            "improvement_rate": performance.improvement_rate,
                            "confidence_calibration": performance.confidence_calibration
                        },
                        "insights": insights,
                        "status": "learning" if performance.total_predictions > 0 else "waiting_data"
                    }
                    
                    if performance.total_predictions > 0:
                        total_accuracy += performance.accuracy
                        learning_count += 1
                        total_predictions += performance.total_predictions
                else:
                    overview["agents"][agent_name] = {
                        "status": "no_data",
                        "message": "No learning data available yet"
                    }
                    
            except Exception as e:
                logger.warning(f"Error getting performance for {agent_name}: {e}")
                overview["agents"][agent_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Calculate summary
        if learning_count > 0:
            overview["summary"]["avg_accuracy"] = total_accuracy / learning_count
            overview["summary"]["learning_agents"] = learning_count
            overview["summary"]["total_predictions"] = total_predictions
        
        return overview
        
    except Exception as e:
        logger.error(f"Error getting performance overview: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting performance overview: {str(e)}")

@router.get("/performance/{agent_name}")
async def get_agent_performance(agent_name: str) -> Dict[str, Any]:
    """Get detailed performance for a specific agent"""
    if not LEARNING_AVAILABLE or not learning_system:
        raise HTTPException(status_code=503, detail="Learning system not available")
    
    try:
        performance = await learning_system.get_agent_performance(agent_name)
        insights = await learning_system.get_learning_insights(agent_name)
        
        if not performance:
            return {
                "agent_name": agent_name,
                "status": "no_data",
                "message": "No performance data available for this agent",
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "agent_name": agent_name,
            "performance": {
                "accuracy": performance.accuracy,
                "precision": performance.precision,
                "recall": performance.recall,
                "avg_error": performance.avg_error,
                "improvement_rate": performance.improvement_rate,
                "confidence_calibration": performance.confidence_calibration,
                "total_predictions": performance.total_predictions,
                "last_updated": performance.last_updated.isoformat()
            },
            "insights": insights,
            "status": "active",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting performance for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting agent performance: {str(e)}")

@router.get("/predictions/recent")
async def get_recent_predictions(
    agent_name: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    include_outcomes: bool = True
) -> Dict[str, Any]:
    """Get recent predictions from learning system"""
    if not LEARNING_AVAILABLE or not learning_system:
        raise HTTPException(status_code=503, detail="Learning system not available")
    
    try:
        # Export learning data (this would be enhanced to filter by agent and limit)
        if agent_name:
            data = await learning_system.export_learning_data(agent_name)
        else:
            data = await learning_system.export_learning_data()
        
        predictions = data.get('predictions', [])
        
        # Sort by timestamp (newest first) and limit
        predictions_sorted = sorted(predictions, key=lambda x: x[7], reverse=True)[:limit]
        
        # Format predictions
        formatted_predictions = []
        for pred in predictions_sorted:
            prediction_data = {
                "prediction_id": pred[1],
                "agent_name": pred[2],
                "symbol": pred[3],
                "prediction_type": pred[4],
                "predicted_value": pred[5],
                "confidence": pred[6],
                "timestamp": pred[7],
                "has_outcome": pred[8] is not None
            }
            
            if include_outcomes and pred[8] is not None:
                prediction_data.update({
                    "actual_value": pred[8],
                    "outcome_timestamp": pred[9],
                    "accuracy": pred[10],
                    "error": pred[11]
                })
            
            formatted_predictions.append(prediction_data)
        
        return {
            "predictions": formatted_predictions,
            "total_count": len(predictions),
            "returned_count": len(formatted_predictions),
            "agent_filter": agent_name,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting recent predictions: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting predictions: {str(e)}")

@router.post("/outcome/record")
async def record_outcome(
    agent_name: str,
    symbol: str,
    actual_value: float,
    outcome_timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """Record an outcome for learning (manual entry)"""
    if not LEARNING_AVAILABLE or not learning_system:
        raise HTTPException(status_code=503, detail="Learning system not available")
    
    try:
        # Parse timestamp if provided
        outcome_dt = datetime.fromisoformat(outcome_timestamp) if outcome_timestamp else datetime.now()
        
        # Try to record outcome through the appropriate agent
        recorded = False
        
        if agent_name == "MasterScoringAgent":
            recorded = await master_scoring_agent.record_outcome(symbol, actual_value, outcome_dt)
        elif agent_name == "KingFisherService":
            kingfisher_service = KingFisherService()
            recorded = await kingfisher_service.record_outcome(symbol, actual_value, outcome_dt)
        elif agent_name == "EnhancedCryptometerService":
            recorded = await enhanced_cryptometer_service.record_outcome(symbol, actual_value, outcome_dt)
        elif agent_name == "EnhancedRiskMetricService":
            # UnifiedRiskMetric doesn't have record_outcome yet, skip for now
            recorded = False
            logger.info(f"Skipping outcome recording for UnifiedRiskMetric - method not implemented")
        
        if recorded:
            return {
                "success": True,
                "message": f"Outcome recorded for {agent_name} - {symbol}",
                "agent_name": agent_name,
                "symbol": symbol,
                "actual_value": actual_value,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": f"No matching prediction found or agent not available",
                "agent_name": agent_name,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error recording outcome: {e}")
        raise HTTPException(status_code=500, detail=f"Error recording outcome: {str(e)}")

@router.get("/analytics/learning_curve/{agent_name}")
async def get_learning_curve(agent_name: str) -> Dict[str, Any]:
    """Get learning curve analytics for an agent"""
    if not LEARNING_AVAILABLE or not learning_system:
        raise HTTPException(status_code=503, detail="Learning system not available")
    
    try:
        # Get raw prediction data
        data = await learning_system.export_learning_data(agent_name)
        predictions = data.get('predictions', [])
        
        # Filter predictions with outcomes
        completed_predictions = [p for p in predictions if p[8] is not None]
        
        if not completed_predictions:
            return {
                "agent_name": agent_name,
                "learning_curve": [],
                "message": "No completed predictions available for learning curve",
                "timestamp": datetime.now().isoformat()
            }
        
        # Sort by timestamp
        completed_predictions.sort(key=lambda x: x[7])
        
        # Calculate rolling accuracy
        learning_curve = []
        window_size = 20  # Rolling window
        
        for i in range(window_size, len(completed_predictions) + 1):
            window_predictions = completed_predictions[i-window_size:i]
            accuracies = [p[10] for p in window_predictions if p[10] is not None]
            
            if accuracies:
                learning_curve.append({
                    "prediction_count": i,
                    "rolling_accuracy": sum(accuracies) / len(accuracies),
                    "window_size": len(accuracies),
                    "timestamp": window_predictions[-1][7]
                })
        
        return {
            "agent_name": agent_name,
            "learning_curve": learning_curve,
            "total_predictions": len(completed_predictions),
            "window_size": window_size,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting learning curve for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting learning curve: {str(e)}")

@router.get("/analytics/accuracy_by_symbol/{agent_name}")
async def get_accuracy_by_symbol(agent_name: str) -> Dict[str, Any]:
    """Get accuracy breakdown by symbol for an agent"""
    if not LEARNING_AVAILABLE or not learning_system:
        raise HTTPException(status_code=503, detail="Learning system not available")
    
    try:
        # Get raw prediction data
        data = await learning_system.export_learning_data(agent_name)
        predictions = data.get('predictions', [])
        
        # Group by symbol and calculate accuracy
        symbol_stats = {}
        
        for pred in predictions:
            if pred[8] is not None and pred[10] is not None:  # Has outcome and accuracy
                symbol = pred[3]
                accuracy = pred[10]
                
                if symbol not in symbol_stats:
                    symbol_stats[symbol] = {
                        'total_predictions': 0,
                        'total_accuracy': 0.0,
                        'predictions': []
                    }
                
                symbol_stats[symbol]['total_predictions'] += 1
                symbol_stats[symbol]['total_accuracy'] += accuracy
                symbol_stats[symbol]['predictions'].append({
                    'predicted_value': pred[5],
                    'actual_value': pred[8],
                    'accuracy': accuracy,
                    'timestamp': pred[7]
                })
        
        # Calculate averages
        symbol_results = {}
        for symbol, stats in symbol_stats.items():
            if stats['total_predictions'] > 0:
                symbol_results[symbol] = {
                    'avg_accuracy': stats['total_accuracy'] / stats['total_predictions'],
                    'prediction_count': stats['total_predictions'],
                    'recent_predictions': stats['predictions'][-5:]  # Last 5
                }
        
        return {
            "agent_name": agent_name,
            "symbol_accuracy": symbol_results,
            "total_symbols": len(symbol_results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting accuracy by symbol for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting symbol accuracy: {str(e)}")

@router.get("/health")
async def get_learning_health() -> Dict[str, Any]:
    """Get comprehensive health status of learning system"""
    if not LEARNING_AVAILABLE or not learning_system:
        return {
            "status": "unavailable",
            "learning_enabled": False,
            "message": "Learning system not available",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Get basic system info
        overview = await get_performance_overview()
        
        # Calculate health metrics
        total_agents = overview["summary"]["total_agents"]
        learning_agents = overview["summary"]["learning_agents"]
        avg_accuracy = overview["summary"]["avg_accuracy"]
        
        # Determine overall health
        health_status = "excellent"
        if avg_accuracy < 0.5:
            health_status = "poor"
        elif avg_accuracy < 0.65:
            health_status = "fair"
        elif avg_accuracy < 0.75:
            health_status = "good"
        
        learning_ratio = learning_agents / total_agents if total_agents > 0 else 0
        
        return {
            "status": health_status,
            "learning_enabled": True,
            "metrics": {
                "total_agents": total_agents,
                "learning_agents": learning_agents,
                "learning_ratio": learning_ratio,
                "avg_accuracy": avg_accuracy,
                "total_predictions": overview["summary"]["total_predictions"]
            },
            "agents_status": {
                agent: data.get("status", "unknown") 
                for agent, data in overview["agents"].items()
            },
            "recommendations": [
                "System is learning effectively" if health_status == "excellent"
                else f"Consider reviewing {health_status} performing agents",
                f"{learning_agents}/{total_agents} agents are actively learning",
                "Learning data collection is operational" if learning_agents > 0 
                else "Waiting for prediction data to start learning"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting learning health: {e}")
        return {
            "status": "error",
            "learning_enabled": True,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }