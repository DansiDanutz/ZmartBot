#!/usr/bin/env python3
"""
KingFisher Q&A API Routes
Provides API endpoints for querying KingFisher analysis data
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.kingfisher_qa_agent import kingfisher_qa_agent
from src.database.kingfisher_database import kingfisher_db

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/kingfisher",
    tags=["KingFisher Q&A"],
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
    Ask a natural language question about KingFisher trading data
    
    Examples:
    - "What's the win rate for BTC?"
    - "Show me support and resistance levels for ETH"
    - "Where are the liquidation clusters for SOL?"
    - "Should I go long or short on XRP?"
    - "What's the risk level for ADA?"
    - "Compare BTC vs ETH"
    """
    try:
        logger.info(f"Received question: {request.question}")
        
        # Process question with Q&A agent
        result = await kingfisher_qa_agent.answer_question(request.question)
        
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
    Get the latest KingFisher analysis for a symbol
    
    Args:
        symbol: Trading symbol (e.g., BTC, ETH, SOL)
    """
    try:
        analysis = kingfisher_db.get_latest_analysis(symbol.upper())
        
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

@router.get("/win-rates/{symbol}")
async def get_win_rates(
    symbol: str,
    timeframe: str = Query(default="24h", regex="^(24h|7d|1m)$")
):
    """
    Get win rates for a symbol and timeframe
    
    Args:
        symbol: Trading symbol
        timeframe: Time period (24h, 7d, or 1m)
    """
    try:
        win_rates = kingfisher_db.get_win_rates(symbol.upper(), timeframe)
        
        if win_rates:
            return {
                'success': True,
                'symbol': symbol.upper(),
                'timeframe': timeframe,
                'win_rates': win_rates,
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No win rate data for {symbol}"
            )
            
    except Exception as e:
        logger.error(f"Error getting win rates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/support-resistance/{symbol}")
async def get_support_resistance(
    symbol: str,
    timeframe: Optional[str] = Query(default=None, regex="^(24h|7d|1m)$")
):
    """
    Get support and resistance levels for a symbol
    
    Args:
        symbol: Trading symbol
        timeframe: Optional time period filter
    """
    try:
        levels = kingfisher_db.get_support_resistance_levels(
            symbol.upper(), 
            timeframe
        )
        
        if levels:
            return {
                'success': True,
                'symbol': symbol.upper(),
                'timeframe': timeframe,
                'levels': levels,
                'count': len(levels),
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No support/resistance levels for {symbol}"
            )
            
    except Exception as e:
        logger.error(f"Error getting levels: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/liquidation-clusters/{symbol}")
async def get_liquidation_clusters(
    symbol: str,
    limit: int = Query(default=10, ge=1, le=50)
):
    """
    Get liquidation clusters for a symbol
    
    Args:
        symbol: Trading symbol
        limit: Maximum number of clusters to return
    """
    try:
        clusters = kingfisher_db.get_liquidation_clusters(
            symbol.upper(),
            limit
        )
        
        if clusters:
            return {
                'success': True,
                'symbol': symbol.upper(),
                'clusters': clusters,
                'count': len(clusters),
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No liquidation clusters for {symbol}"
            )
            
    except Exception as e:
        logger.error(f"Error getting clusters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trading-targets/{symbol}")
async def get_trading_targets(
    symbol: str,
    position_type: Optional[str] = Query(default=None, regex="^(long|short)$")
):
    """
    Get trading targets for a symbol
    
    Args:
        symbol: Trading symbol
        position_type: Optional filter for long or short positions
    """
    try:
        targets = kingfisher_db.get_trading_targets(
            symbol.upper(),
            position_type
        )
        
        if targets:
            return {
                'success': True,
                'symbol': symbol.upper(),
                'position_type': position_type,
                'targets': targets,
                'count': len(targets),
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No trading targets for {symbol}"
            )
            
    except Exception as e:
        logger.error(f"Error getting targets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-patterns/{symbol}")
async def get_market_patterns(symbol: str):
    """
    Get detected market patterns for a symbol
    
    Args:
        symbol: Trading symbol
    """
    try:
        patterns = kingfisher_db.get_market_patterns(symbol.upper())
        
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
    Store a new KingFisher analysis in the database
    
    This endpoint is typically called by the KingFisher workflow controller
    after processing images and generating analysis.
    """
    try:
        # Store complete analysis
        analysis_id = kingfisher_db.store_complete_analysis(request.analysis_data)
        
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
    min_confidence: Optional[float] = Query(default=None, ge=0, le=1),
    risk_level: Optional[str] = Query(default=None, regex="^(low|medium|high)$"),
    sentiment: Optional[str] = Query(default=None, regex="^(bullish|bearish|neutral)$"),
    limit: int = Query(default=10, ge=1, le=100)
):
    """
    Search for analyses with flexible criteria
    
    Args:
        symbol: Optional symbol filter
        min_confidence: Minimum confidence level
        risk_level: Risk level filter
        sentiment: Sentiment filter
        limit: Maximum results to return
    """
    try:
        # Build search criteria
        search_params = {'limit': limit}
        
        if symbol:
            search_params['symbol'] = symbol.upper()
        if min_confidence is not None:
            search_params['min_confidence'] = min_confidence
        if risk_level:
            search_params['risk_level'] = risk_level
        if sentiment:
            search_params['sentiment'] = sentiment
        
        # Search database
        results = kingfisher_db.search_analyses(**search_params)
        
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

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the KingFisher Q&A service
    """
    try:
        # Test database connection
        test_result = kingfisher_db.get_latest_analysis('BTC')
        db_connected = test_result is not None or True  # DB works even if no data
        
        return {
            'status': 'healthy',
            'service': 'KingFisher Q&A API',
            'database_connected': db_connected,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'service': 'KingFisher Q&A API',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# Export router
__all__ = ['router']