#!/usr/bin/env python3
"""
Cryptometer Q&A API Routes
Provides API endpoints for querying Cryptometer analysis data
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.cryptometer_qa_agent import cryptometer_qa_agent
from src.database.cryptometer_database import cryptometer_db

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/cryptometer",
    tags=["Cryptometer Q&A"],
    responses={404: {"description": "Not found"}}
)

# Request/Response models
class QuestionRequest(BaseModel):
    """Request model for natural language questions"""
    question: str = Field(..., description="Natural language question about trading data")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context for the question")

class QuestionResponse(BaseModel):
    """Response model for Q&A results"""
    success: bool
    question: str
    answer: str
    data: Optional[Dict[str, Any]] = None
    confidence: float = Field(default=0.8, ge=0, le=1)
    response_time_ms: int
    query_type: str
    symbols: List[str]
    timestamp: str

class AnalysisRequest(BaseModel):
    """Request model for storing new analysis"""
    symbol: str
    analysis_data: Dict[str, Any]

class AnalysisResponse(BaseModel):
    """Response model for analysis storage"""
    success: bool
    analysis_id: Optional[int] = None
    message: str
    timestamp: str

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a natural language question about Cryptometer trading data
    
    Examples:
    - "What's the AI prediction for BTC?"
    - "Show me the score for ETH"
    - "What's the trend for SOL?"
    - "Long/short ratio for XRP"
    - "Liquidation data for ADA"
    - "Any rapid movements?"
    - "Trading signals for DOT"
    - "Risk assessment for AVAX"
    - "Compare BTC vs ETH"
    """
    try:
        logger.info(f"Received question: {request.question}")
        
        # Process question with Q&A agent
        result = await cryptometer_qa_agent.answer_question(request.question)
        
        if result.get('success'):
            return QuestionResponse(
                success=True,
                question=result['question'],
                answer=result['answer'],
                data=result.get('data'),
                confidence=result.get('confidence', 0.8),
                response_time_ms=result.get('response_time_ms', 0),
                query_type=result.get('query_type', 'general'),
                symbols=result.get('symbols', []),
                timestamp=datetime.now().isoformat()
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Failed to process question')
            )
            
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{symbol}")
async def get_latest_analysis(symbol: str):
    """
    Get the latest Cryptometer analysis for a symbol
    
    Args:
        symbol: Trading symbol (e.g., BTC, ETH, SOL)
    """
    try:
        analysis = cryptometer_db.get_latest_analysis(symbol.upper())
        
        if analysis:
            return {
                'success': True,
                'symbol': symbol.upper(),
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No analysis found for {symbol}"
            )
            
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai-predictions/{symbol}")
async def get_ai_predictions(
    symbol: str,
    timeframe: Optional[str] = Query(default=None, description="Prediction timeframe")
):
    """
    Get AI predictions for a symbol
    
    Args:
        symbol: Trading symbol
        timeframe: Optional timeframe filter
    """
    try:
        predictions = cryptometer_db.get_ai_predictions(symbol.upper(), timeframe or "")
        
        if predictions:
            return {
                'success': True,
                'symbol': symbol.upper(),
                'timeframe': timeframe,
                'predictions': predictions,
                'count': len(predictions),
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No AI predictions for {symbol}"
            )
            
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends/{symbol}")
async def get_trend_indicators(
    symbol: str,
    timeframe: str = Query(default="1d", regex="^(1h|4h|1d|1w)$")
):
    """
    Get trend indicators for a symbol
    
    Args:
        symbol: Trading symbol
        timeframe: Time period (1h, 4h, 1d, 1w)
    """
    try:
        trends = cryptometer_db.get_trend_indicators(symbol.upper(), timeframe)
        
        if trends:
            return {
                'success': True,
                'symbol': symbol.upper(),
                'timeframe': timeframe,
                'trends': trends,
                'count': len(trends),
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No trend data for {symbol}"
            )
            
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rapid-movements")
async def get_rapid_movements(
    symbol: Optional[str] = Query(default=None),
    movement_type: Optional[str] = Query(default=None, regex="^(pump|dump|breakout|breakdown)$")
):
    """
    Get rapid market movements
    
    Args:
        symbol: Optional symbol filter
        movement_type: Optional movement type filter
    """
    try:
        movements = cryptometer_db.get_rapid_movements(symbol or "", movement_type or "")
        
        if movements:
            return {
                'success': True,
                'symbol': symbol,
                'movement_type': movement_type,
                'movements': movements,
                'count': len(movements),
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'success': True,
                'movements': [],
                'count': 0,
                'message': 'No rapid movements detected',
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error getting movements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trading-signals/{symbol}")
async def get_trading_signals(
    symbol: str,
    signal_type: Optional[str] = Query(default=None, regex="^(buy|sell|hold)$")
):
    """
    Get trading signals for a symbol
    
    Args:
        symbol: Trading symbol
        signal_type: Optional filter for signal type
    """
    try:
        signals = cryptometer_db.get_trading_signals(
            symbol.upper(),
            signal_type or ""
        )
        
        if signals:
            return {
                'success': True,
                'symbol': symbol.upper(),
                'signal_type': signal_type,
                'signals': signals,
                'count': len(signals),
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No trading signals for {symbol}"
            )
            
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-patterns/{symbol}")
async def get_market_patterns(symbol: str):
    """
    Get detected market patterns for a symbol
    
    Args:
        symbol: Trading symbol
    """
    try:
        patterns = cryptometer_db.get_market_patterns(symbol.upper())
        
        if patterns:
            return {
                'success': True,
                'symbol': symbol.upper(),
                'patterns': patterns,
                'count': len(patterns),
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No market patterns detected for {symbol}"
            )
            
    except Exception as e:
        logger.error(f"Error getting patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analysis", response_model=AnalysisResponse)
async def store_analysis(request: AnalysisRequest):
    """
    Store a new Cryptometer analysis in the database
    
    This endpoint is typically called by the Cryptometer service
    after collecting and processing data from all 17 endpoints.
    """
    try:
        # Store complete analysis
        analysis_id = cryptometer_db.store_complete_analysis(request.analysis_data)
        
        return AnalysisResponse(
            success=True,
            analysis_id=analysis_id,
            message=f"Analysis for {request.symbol} stored successfully",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error storing analysis: {e}")
        return AnalysisResponse(
            success=False,
            message=f"Failed to store analysis: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

@router.get("/search")
async def search_analyses(
    symbol: Optional[str] = None,
    min_score: Optional[float] = Query(default=None, ge=0, le=100),
    risk_level: Optional[str] = Query(default=None, regex="^(low|medium|high)$"),
    sentiment: Optional[str] = Query(default=None, regex="^(bullish|bearish|neutral)$"),
    position_type: Optional[str] = Query(default=None, regex="^(long|short)$"),
    limit: int = Query(default=10, ge=1, le=100)
):
    """
    Search for analyses with flexible criteria
    
    Args:
        symbol: Optional symbol filter
        min_score: Minimum overall score
        risk_level: Risk level filter
        sentiment: Sentiment filter
        position_type: Position type filter
        limit: Maximum results to return
    """
    try:
        # Build search criteria
        search_params = {'limit': limit}
        
        if symbol:
            search_params['symbol'] = symbol.upper()  # type: ignore
        if min_score is not None:
            search_params['min_score'] = min_score  # type: ignore
        if risk_level:
            search_params['risk_level'] = risk_level  # type: ignore
        if sentiment:
            search_params['sentiment'] = sentiment  # type: ignore
        if position_type:
            search_params['position_type'] = position_type  # type: ignore
        
        # Search database
        results = cryptometer_db.search_analyses(**search_params)
        
        return {
            'success': True,
            'criteria': search_params,
            'results': results,
            'count': len(results),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error searching analyses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/endpoint-data/{symbol}")
async def get_endpoint_data(
    symbol: str,
    endpoint_name: str = Query(..., description="Endpoint name (e.g., ticker, ls_ratio, ai_screener)")
):
    """
    Get raw endpoint data for a symbol
    
    Available endpoints:
    - coinlist, tickerlist, ticker, cryptocurrency_info
    - coin_info, tickerlist_pro, trend_indicator_v3
    - forex_rates, ls_ratio, open_interest
    - liquidation_data_v2, rapid_movements
    - ai_screener, ai_screener_analysis
    """
    try:
        data = cryptometer_db.get_endpoint_data(symbol.upper(), endpoint_name)
        
        if data:
            return {
                'success': True,
                'symbol': symbol.upper(),
                'endpoint': endpoint_name,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No {endpoint_name} data for {symbol}"
            )
            
    except Exception as e:
        logger.error(f"Error getting endpoint data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_historical_performance(
    symbol: Optional[str] = None,
    timeframe: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200)
):
    """
    Get historical prediction performance
    
    Args:
        symbol: Optional symbol filter
        timeframe: Optional timeframe filter
        limit: Maximum results to return
    """
    try:
        performance = cryptometer_db.get_historical_performance(symbol or "", timeframe or "")
        
        # Calculate accuracy
        if performance:
            correct = sum(1 for p in performance if p.get('was_correct'))
            accuracy = (correct / len(performance)) * 100 if performance else 0
        else:
            accuracy = 0
        
        return {
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'performance': performance[:limit],
            'accuracy': accuracy,
            'total_predictions': len(performance),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the Cryptometer Q&A service
    """
    try:
        # Test database connection
        test_result = cryptometer_db.get_latest_analysis('BTC')
        db_connected = test_result is not None or True  # DB works even if no data
        
        return {
            'status': 'healthy',
            'service': 'Cryptometer Q&A API',
            'database_connected': db_connected,
            'endpoints_available': 17,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'service': 'Cryptometer Q&A API',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# Export router
__all__ = ['router']