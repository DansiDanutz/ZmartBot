#!/usr/bin/env python3
"""
Unified Scoring API Routes
Clean API endpoints for the unified scoring system

This replaces all scattered scoring routes with a single, organized interface.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel, Field
from datetime import datetime

from ..services.unified_scoring_system import (
    unified_scoring_system, 
    UnifiedScoringSystem,
    MarketCondition,
    ScoringSource
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/scoring", tags=["Unified Scoring"])

# Pydantic models for request/response validation
class MarketConditionUpdate(BaseModel):
    """Request model for market condition updates"""
    condition: str = Field(..., description="Market condition (bull_market, bear_market, sideways, high_volatility, low_volatility, normal)")

class ReliabilityUpdate(BaseModel):
    """Request model for reliability score updates"""
    source: str = Field(..., description="Scoring source (kingfisher, cryptometer, riskmetric)")
    score: float = Field(..., ge=0, le=1, description="Reliability score (0-1)")

class ManualScoreRequest(BaseModel):
    """Request model for manual score input"""
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSDT)")
    kingfisher_score: Optional[float] = Field(None, ge=0, le=100, description="KingFisher 100-point score")
    cryptometer_score: Optional[float] = Field(None, ge=0, le=100, description="Cryptometer 100-point score")
    riskmetric_score: Optional[float] = Field(None, ge=0, le=100, description="RiskMetric 100-point score")

@router.get("/health")
async def get_scoring_health():
    """Get unified scoring system health status"""
    try:
        return unified_scoring_system.get_system_health()
    except Exception as e:
        logger.error(f"Error getting scoring health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/score/{symbol}")
async def get_comprehensive_score(
    symbol: str,
    include_history: bool = Query(False, description="Include scoring history"),
    history_limit: int = Query(10, ge=1, le=50, description="Number of history entries to include")
):
    """
    Get comprehensive score for a symbol using all available sources
    
    This endpoint automatically fetches scores from all three systems:
    - KingFisher: Liquidation analysis (30% base weight)
    - Cryptometer: Market analysis (50% base weight)  
    - RiskMetric: Risk assessment (20% base weight)
    
    The system applies dynamic weighting based on:
    - Data quality and freshness
    - Market conditions
    - Historical reliability
    
    Returns:
        - final_score: 0-100 point final score
        - signal: Trading signal recommendation
        - confidence: Overall confidence (0-1)
        - dynamic_weights: Current weight distribution
        - component_scores: Individual system scores and metadata
    """
    try:
        logger.info(f"🎯 Getting comprehensive score for {symbol}")
        
        # Get comprehensive score
        result = await unified_scoring_system.get_comprehensive_score(symbol)
        
        # Convert to dictionary
        response = result.to_dict()
        
        # Add history if requested
        if include_history:
            history = unified_scoring_system.get_scoring_history(symbol, history_limit)
            response['history'] = history
        
        logger.info(f"✅ Comprehensive score returned for {symbol}: {result.final_score:.1f}/100")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error getting comprehensive score for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating score: {str(e)}")

@router.get("/scores/batch")
async def get_batch_scores(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    include_details: bool = Query(False, description="Include detailed component scores")
):
    """
    Get scores for multiple symbols in batch
    
    Args:
        symbols: Comma-separated list of symbols (e.g., "BTCUSDT,ETHUSDT,SOLUSDT")
        include_details: Whether to include detailed component scores
        
    Returns:
        Dictionary with symbol -> score mapping
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        results = {}
        
        for symbol in symbol_list:
            try:
                result = await unified_scoring_system.get_comprehensive_score(symbol)
                results[symbol] = {
                    'final_score': result.final_score,
                    'signal': result.signal,
                    'confidence': result.confidence,
                    'market_condition': result.market_condition.value
                }
                
                if include_details:
                    results[symbol]['component_scores'] = {
                        source: score.to_dict() 
                        for source, score in result.component_scores.items()
                    }
                    
            except Exception as e:
                logger.warning(f"Failed to get score for {symbol}: {e}")
                results[symbol] = {
                    'error': str(e),
                    'final_score': 50.0,
                    'signal': 'Hold',
                    'confidence': 0.0
                }
        
        return {
            'batch_results': results,
            'total_symbols': len(symbol_list),
            'successful_scores': len([r for r in results.values() if 'error' not in r]),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error in batch scoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in batch scoring: {str(e)}")

@router.get("/history/{symbol}")
async def get_scoring_history(
    symbol: str,
    limit: int = Query(10, ge=1, le=100, description="Number of history entries to return")
):
    """
    Get scoring history for a symbol
    
    Returns the last N scoring results for the specified symbol
    """
    try:
        history = unified_scoring_system.get_scoring_history(symbol, limit)
        return {
            'symbol': symbol,
            'history': history,
            'count': len(history),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting history for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/market-condition")
async def update_market_condition(request: MarketConditionUpdate):
    """
    Update market condition for dynamic weighting
    
    Market conditions affect how weights are distributed:
    - high_volatility: Boosts KingFisher weight
    - bull_market: Boosts Cryptometer weight
    - bear_market: Boosts RiskMetric weight
    """
    try:
        # Validate market condition
        try:
            condition = MarketCondition(request.condition)
        except ValueError:
            valid_conditions = [c.value for c in MarketCondition]
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid market condition. Valid options: {valid_conditions}"
            )
        
        # Update market condition
        unified_scoring_system.set_market_condition(condition)
        
        logger.info(f"✅ Market condition updated to: {condition.value}")
        return {
            'status': 'success',
            'market_condition': condition.value,
            'timestamp': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating market condition: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reliability")
async def update_reliability_score(request: ReliabilityUpdate):
    """
    Update reliability score for a scoring source
    
    Reliability scores affect dynamic weighting:
    - Higher reliability = higher weight
    - Lower reliability = lower weight
    """
    try:
        # Validate source
        try:
            source = ScoringSource(request.source)
        except ValueError:
            valid_sources = [s.value for s in ScoringSource]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source. Valid options: {valid_sources}"
            )
        
        # Update reliability score
        unified_scoring_system.update_reliability_score(source, request.score)
        
        logger.info(f"✅ Reliability score updated for {source.value}: {request.score}")
        return {
            'status': 'success',
            'source': source.value,
            'reliability_score': request.score,
            'timestamp': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating reliability score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/manual")
async def calculate_manual_score(request: ManualScoreRequest):
    """
    Calculate score using manually provided component scores
    
    This endpoint allows you to input scores manually and see how they would be weighted
    """
    try:
        # Create mock component scores
        component_scores = {}
        
        if request.kingfisher_score is not None:
            from ..services.unified_scoring_system import ComponentScore, ScoringSource
            component_scores['kingfisher'] = ComponentScore(
                source=ScoringSource.KINGFISHER,
                score=request.kingfisher_score,
                confidence=0.85,
                data_quality=0.9,
                data_age_minutes=1.0,
                metadata={'manual_input': True},
                timestamp=datetime.now()
            )
        
        if request.cryptometer_score is not None:
            component_scores['cryptometer'] = ComponentScore(
                source=ScoringSource.CRYPTOMETER,
                score=request.cryptometer_score,
                confidence=0.80,
                data_quality=0.85,
                data_age_minutes=1.0,
                metadata={'manual_input': True},
                timestamp=datetime.now()
            )
        
        if request.riskmetric_score is not None:
            component_scores['riskmetric'] = ComponentScore(
                source=ScoringSource.RISKMETRIC,
                score=request.riskmetric_score,
                confidence=0.90,
                data_quality=0.95,
                data_age_minutes=1.0,
                metadata={'manual_input': True},
                timestamp=datetime.now()
            )
        
        if not component_scores:
            raise HTTPException(
                status_code=400,
                detail="At least one component score must be provided"
            )
        
        # Calculate dynamic weights
        dynamic_weights = unified_scoring_system._calculate_dynamic_weights(component_scores)
        
        # Calculate final score
        final_score = unified_scoring_system._calculate_weighted_score(component_scores, dynamic_weights)
        
        # Determine signal
        signal = unified_scoring_system._determine_signal(final_score)
        
        # Calculate confidence
        confidence = unified_scoring_system._calculate_overall_confidence(component_scores, dynamic_weights)
        
        return {
            'symbol': request.symbol,
            'final_score': final_score,
            'signal': signal,
            'confidence': confidence,
            'market_condition': unified_scoring_system.current_market_condition.value,
            'dynamic_weights': dynamic_weights.to_dict(),
            'component_scores': {
                source: score.to_dict() 
                for source, score in component_scores.items()
            },
            'manual_input': True,
            'timestamp': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error calculating manual score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_scoring_statistics():
    """
    Get scoring system statistics and performance metrics
    """
    try:
        health = unified_scoring_system.get_system_health()
        
        # Calculate additional statistics
        total_history_entries = sum(
            len(history) for history in unified_scoring_system.scoring_history.values()
        )
        
        symbols_with_history = len(unified_scoring_system.scoring_history)
        
        return {
            'system_health': health,
            'statistics': {
                'total_history_entries': total_history_entries,
                'symbols_with_history': symbols_with_history,
                'average_history_per_symbol': round(total_history_entries / max(symbols_with_history, 1), 1)
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history/{symbol}")
async def clear_scoring_history(symbol: str):
    """
    Clear scoring history for a symbol
    """
    try:
        if symbol in unified_scoring_system.scoring_history:
            del unified_scoring_system.scoring_history[symbol]
            logger.info(f"✅ Cleared scoring history for {symbol}")
            return {
                'status': 'success',
                'message': f'Scoring history cleared for {symbol}',
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'success',
                'message': f'No history found for {symbol}',
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ Error clearing history for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
