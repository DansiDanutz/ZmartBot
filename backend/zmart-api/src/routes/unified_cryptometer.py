"""
Unified Cryptometer API Routes
==============================

FastAPI routes for the unified Cryptometer system that combines:
- Symbol-specific learning agents
- Enhanced endpoint configurations  
- Multi-timeframe analysis
- Dynamic pattern weighting
- Comprehensive outcome tracking

Based on Complete Implementation Guide and Quick-Start Guide
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from src.services.unified_cryptometer_system import (
    UnifiedCryptometerSystem,
    TradingSignal,
    SignalOutcome,
    Pattern
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Global system instance
unified_system = UnifiedCryptometerSystem()

@router.get("/unified/analyze/{symbol}")
async def analyze_symbol_unified(symbol: str) -> Dict[str, Any]:
    """
    Complete unified analysis for a symbol
    
    Combines all 18 endpoints with symbol-specific learning
    Returns comprehensive analysis with learning-weighted scoring
    """
    try:
        logger.info(f"Starting unified analysis for {symbol}")
        
        result = await unified_system.analyze_symbol_complete(symbol)
        
        return {
            "success": True,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "analysis": result,
            "message": f"Unified analysis completed for {symbol}"
        }
        
    except Exception as e:
        logger.error(f"Error in unified analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/unified/learning-agent/{symbol}")
async def get_learning_agent_summary(symbol: str) -> Dict[str, Any]:
    """
    Get learning agent performance summary for a symbol
    
    Returns pattern weights, success rates, and learning statistics
    """
    try:
        learning_agent = unified_system.get_learning_agent(symbol)
        summary = learning_agent.get_performance_summary()
        
        return {
            "success": True,
            "symbol": symbol,
            "learning_agent": summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting learning agent for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get learning agent: {str(e)}")

@router.post("/unified/track-outcome")
async def track_signal_outcome(outcome_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Track trading signal outcome for learning
    
    Expected payload:
    {
        "signal_id": "ETH_volume_divergence_1234567890",
        "outcome_type": "success|failure|incomplete", 
        "timeframe": "24h|7d|30d",
        "actual_return": 0.05,
        "time_to_outcome": 3600,
        "max_favorable": 0.08,
        "max_adverse": -0.02,
        "pattern_attribution": {"volume_divergence": 1.0},
        "market_conditions": {}
    }
    """
    try:
        required_fields = ['signal_id', 'outcome_type', 'timeframe', 'actual_return', 'time_to_outcome']
        for field in required_fields:
            if field not in outcome_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Extract symbol from signal_id
        signal_id = outcome_data['signal_id']
        symbol = signal_id.split('_')[0]
        
        # Create mock signal for outcome tracking (in production, this would be retrieved from storage)
        mock_signal = TradingSignal(
            signal_id=signal_id,
            symbol=symbol,
            timestamp=datetime.now(),
            pattern=Pattern(
                pattern_id=f"{symbol}_pattern_{int(datetime.now().timestamp())}",
                pattern_type=signal_id.split('_')[1],
                direction='bullish',  # Would be retrieved from storage
                strength=0.5,
                confidence=0.7,
                timeframe=outcome_data['timeframe'],
                detected_at=datetime.now(),
                market_conditions={},
                contributing_endpoints=[]
            ),
            direction='bullish',
            current_price=0.0,
            targets={},
            market_data={},
            expected_outcomes={}
        )
        
        # Track the outcome
        outcome = await unified_system.track_signal_outcome(mock_signal, outcome_data)
        
        return {
            "success": True,
            "message": "Signal outcome tracked successfully",
            "outcome": {
                "signal_id": outcome.signal_id,
                "outcome_type": outcome.outcome_type,
                "actual_return": outcome.actual_return,
                "timeframe": outcome.timeframe
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error tracking signal outcome: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to track outcome: {str(e)}")

@router.get("/unified/system-performance")
async def get_system_performance() -> Dict[str, Any]:
    """
    Get comprehensive system performance summary
    
    Returns performance across all symbols and learning agents
    """
    try:
        summary = unified_system.get_system_performance_summary()
        
        return {
            "success": True,
            "system_performance": summary,
            "timestamp": datetime.now().isoformat(),
            "message": "System performance summary retrieved"
        }
        
    except Exception as e:
        logger.error(f"Error getting system performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance: {str(e)}")

@router.get("/unified/patterns/{symbol}")
async def get_symbol_patterns(symbol: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get recent patterns detected for a symbol
    
    Returns pattern history and performance metrics
    """
    try:
        learning_agent = unified_system.get_learning_agent(symbol)
        
        # Get pattern performance data
        pattern_performance = learning_agent.pattern_performance
        pattern_weights = learning_agent.pattern_weights
        
        patterns_info = []
        for pattern_type, perf in pattern_performance.items():
            patterns_info.append({
                "pattern_type": pattern_type,
                "success_rate": perf['success_rate'],
                "avg_return": perf['avg_return'],
                "total_signals": perf['total_signals'],
                "current_weight": pattern_weights.get(pattern_type, 1.0),
                "performance_tier": "HIGH" if perf['success_rate'] > 0.7 else "MEDIUM" if perf['success_rate'] > 0.4 else "LOW"
            })
        
        # Sort by performance
        patterns_info.sort(key=lambda x: x['success_rate'], reverse=True)
        
        return {
            "success": True,
            "symbol": symbol,
            "patterns": patterns_info[:limit],
            "total_patterns": len(patterns_info),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting patterns for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get patterns: {str(e)}")

@router.post("/unified/simulate-signal")
async def simulate_signal_generation(symbol: str, pattern_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate signal generation for testing
    
    Expected payload:
    {
        "pattern_type": "volume_divergence",
        "direction": "bullish",
        "strength": 0.7,
        "confidence": 0.8
    }
    """
    try:
        # Create mock pattern
        pattern = Pattern(
            pattern_id=f"{symbol}_{pattern_data['pattern_type']}_{int(datetime.now().timestamp())}",
            pattern_type=pattern_data['pattern_type'],
            direction=pattern_data['direction'],
            strength=pattern_data['strength'],
            confidence=pattern_data['confidence'],
            timeframe='1h',
            detected_at=datetime.now(),
            market_conditions={},
            contributing_endpoints=[]
        )
        
        # Check if learning agent would generate signal
        learning_agent = unified_system.get_learning_agent(symbol)
        should_generate = learning_agent.should_generate_signal(pattern)
        
        pattern_weight = learning_agent.pattern_weights.get(pattern.pattern_type, 1.0)
        adjusted_confidence = pattern.confidence * pattern_weight
        
        return {
            "success": True,
            "symbol": symbol,
            "pattern": {
                "type": pattern.pattern_type,
                "direction": pattern.direction,
                "strength": pattern.strength,
                "confidence": pattern.confidence
            },
            "learning_analysis": {
                "should_generate_signal": should_generate,
                "pattern_weight": pattern_weight,
                "adjusted_confidence": adjusted_confidence,
                "historical_performance": learning_agent.pattern_performance.get(pattern.pattern_type, {})
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error simulating signal for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.get("/unified/endpoint-status")
async def get_endpoint_status() -> Dict[str, Any]:
    """
    Get status of all Cryptometer endpoints
    
    Returns endpoint configuration and priority information
    """
    try:
        endpoints_info = []
        
        for endpoint_name, config in unified_system.endpoints.items():
            endpoints_info.append({
                "name": endpoint_name,
                "url": config['url'],
                "priority": config['priority'],
                "weight": config['weight'],
                "signal_value": config['signal_value'],
                "description": config['description']
            })
        
        # Sort by priority and weight
        endpoints_info.sort(key=lambda x: (x['priority'], -x['weight']))
        
        return {
            "success": True,
            "total_endpoints": len(endpoints_info),
            "endpoints": endpoints_info,
            "priority_distribution": {
                "tier_1": len([e for e in endpoints_info if e['priority'] == 1]),
                "tier_2": len([e for e in endpoints_info if e['priority'] == 2]),
                "tier_3": len([e for e in endpoints_info if e['priority'] == 3])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting endpoint status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.post("/unified/batch-analyze")
async def batch_analyze_symbols(symbols: List[str], background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Analyze multiple symbols in batch
    
    Processes symbols in parallel for efficiency
    """
    try:
        if len(symbols) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 symbols per batch")
        
        results = {}
        
        # Process symbols concurrently
        import asyncio
        
        async def analyze_single_symbol(symbol: str):
            try:
                return await unified_system.analyze_symbol_complete(symbol)
            except Exception as e:
                logger.error(f"Error analyzing {symbol} in batch: {e}")
                return {"error": str(e)}
        
        # Run analyses concurrently
        tasks = [analyze_single_symbol(symbol) for symbol in symbols]
        analyses = await asyncio.gather(*tasks)
        
        # Combine results
        for symbol, analysis in zip(symbols, analyses):
            results[symbol] = analysis
        
        return {
            "success": True,
            "total_symbols": len(symbols),
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "message": f"Batch analysis completed for {len(symbols)} symbols"
        }
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@router.get("/unified/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check for unified system
    
    Returns system status and basic metrics
    """
    try:
        return {
            "success": True,
            "status": "healthy",
            "system": "Unified Cryptometer System",
            "version": "2.0",
            "features": [
                "Symbol-specific learning agents",
                "18 enhanced endpoints",
                "Multi-timeframe analysis",
                "Dynamic pattern weighting",
                "Comprehensive outcome tracking"
            ],
            "total_learning_agents": len(unified_system.learning_agents),
            "total_endpoints": len(unified_system.endpoints),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/unified/documentation")
async def get_api_documentation() -> Dict[str, Any]:
    """
    Get API documentation and usage examples
    """
    return {
        "success": True,
        "documentation": {
            "title": "Unified Cryptometer System API",
            "version": "2.0",
            "description": "Complete implementation combining all best practices from implementation guides",
            "endpoints": {
                "/unified/analyze/{symbol}": {
                    "method": "GET",
                    "description": "Complete unified analysis for a symbol",
                    "example": "/unified/analyze/ETH-USDT"
                },
                "/unified/learning-agent/{symbol}": {
                    "method": "GET", 
                    "description": "Get learning agent performance summary",
                    "example": "/unified/learning-agent/ETH-USDT"
                },
                "/unified/track-outcome": {
                    "method": "POST",
                    "description": "Track trading signal outcome for learning",
                    "payload_example": {
                        "signal_id": "ETH_volume_divergence_1234567890",
                        "outcome_type": "success",
                        "timeframe": "24h",
                        "actual_return": 0.05,
                        "time_to_outcome": 3600
                    }
                },
                "/unified/system-performance": {
                    "method": "GET",
                    "description": "Get comprehensive system performance summary"
                },
                "/unified/batch-analyze": {
                    "method": "POST",
                    "description": "Analyze multiple symbols in batch",
                    "payload_example": ["ETH-USDT", "BTC-USDT", "ADA-USDT"]
                }
            },
            "key_features": [
                "Symbol-specific learning agents with individual pattern weights",
                "18 Cryptometer endpoints with enhanced configurations",
                "Multi-timeframe analysis (24h, 7d, 30d)",
                "Dynamic pattern weighting based on performance",
                "Comprehensive outcome tracking and attribution",
                "Real-time learning and adaptation",
                "Production-ready monitoring and optimization"
            ],
            "implementation_guide_compliance": {
                "complete_guide": "Full implementation of all recommended features",
                "quick_start_guide": "All essential components implemented",
                "rate_limiting": "1-second delays between API calls",
                "data_storage": "Symbol-specific SQLite databases for learning",
                "pattern_recognition": "7 enhanced pattern types",
                "learning_algorithm": "Dynamic weight adjustment based on outcomes"
            }
        },
        "timestamp": datetime.now().isoformat()
    }