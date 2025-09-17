from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from core.database import get_db_session
from services.zmarty_service import ZmartyService
from api.v1.auth import get_current_user_dependency
from schemas.zmarty import (
    ZmartyQueryRequest,
    ZmartyQueryResponse,
    ZmartyRequestResponse,
    ZmartyRatingRequest,
    TrendingQueryResponse
)
from models.database import User

router = APIRouter()

@router.post("/query", response_model=ZmartyQueryResponse)
async def zmarty_query(
    query_data: ZmartyQueryRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db_session)
):
    """Send a query to Zmarty AI assistant"""
    zmarty_service = ZmartyService(db)
    
    result = await zmarty_service.process_request(
        user_id=current_user.id,
        query=query_data.query,
        request_type=query_data.request_type,
        parameters=query_data.parameters
    )
    
    if not result["success"]:
        if result.get("error") == "insufficient_credits":
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "message": result["message"],
                    "required_credits": result.get("required_credits", 0)
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    
    return ZmartyQueryResponse(
        success=True,
        request_id=result["request_id"],
        response=result["response"],
        credits_used=result["credits_used"],
        processing_time=result["processing_time"]
    )

@router.get("/requests", response_model=List[ZmartyRequestResponse])
async def get_user_requests(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db_session)
):
    """Get user's Zmarty request history"""
    zmarty_service = ZmartyService(db)
    requests = await zmarty_service.get_user_requests(
        current_user.id, limit, offset, status
    )
    
    return [
        ZmartyRequestResponse(
            id=req.id,
            request_type=req.request_type,
            query=req.query,
            response=req.response,
            credits_cost=req.credits_cost,
            status=req.status,
            processing_time=req.processing_time,
            quality_score=req.quality_score,
            created_at=req.created_at,
            completed_at=req.completed_at
        )
        for req in requests
    ]

@router.get("/requests/{request_id}", response_model=ZmartyRequestResponse)
async def get_request_details(
    request_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db_session)
):
    """Get specific request details"""
    import uuid
    
    zmarty_service = ZmartyService(db)
    request = await zmarty_service.get_request_by_id(
        uuid.UUID(request_id), current_user.id
    )
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    return ZmartyRequestResponse(
        id=request.id,
        request_type=request.request_type,
        query=request.query,
        response=request.response,
        credits_cost=request.credits_cost,
        status=request.status,
        processing_time=request.processing_time,
        quality_score=request.quality_score,
        created_at=request.created_at,
        completed_at=request.completed_at
    )

@router.post("/rate/{request_id}")
async def rate_response(
    request_id: str,
    rating_data: ZmartyRatingRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db_session)
):
    """Rate a Zmarty response"""
    import uuid
    
    zmarty_service = ZmartyService(db)
    
    success = await zmarty_service.rate_response(
        uuid.UUID(request_id),
        current_user.id,
        rating_data.quality_score
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found or cannot be rated"
        )
    
    return {"message": "Rating submitted successfully"}

@router.get("/trending", response_model=List[TrendingQueryResponse])
async def get_trending_queries(
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session)
):
    """Get trending queries across all users"""
    zmarty_service = ZmartyService(db)
    trending = await zmarty_service.get_trending_queries(limit)
    
    return [
        TrendingQueryResponse(
            request_type=item["request_type"],
            count=item["count"],
            avg_rating=item["avg_rating"]
        )
        for item in trending
    ]

@router.post("/trading-analysis")
async def trading_analysis(
    analysis_data: Dict[str, Any],
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db_session)
):
    """Specialized trading analysis endpoint"""
    zmarty_service = ZmartyService(db)
    
    # Extract parameters
    symbol = analysis_data.get("symbol", "BTCUSDT")
    timeframe = analysis_data.get("timeframe", "1h")
    analysis_type = analysis_data.get("analysis_type", "technical")
    
    query = f"Provide detailed {analysis_type} analysis for {symbol} on {timeframe} timeframe"
    
    parameters = {
        "symbol": symbol,
        "timeframe": timeframe,
        "analysis_type": analysis_type,
        **analysis_data
    }
    
    result = await zmarty_service.process_request(
        user_id=current_user.id,
        query=query,
        request_type="trading_strategy",
        parameters=parameters
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

@router.post("/market-signals")
async def market_signals(
    signals_data: Dict[str, Any],
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db_session)
):
    """Get live market signals"""
    zmarty_service = ZmartyService(db)
    
    symbols = signals_data.get("symbols", ["BTCUSDT", "ETHUSDT"])
    timeframe = signals_data.get("timeframe", "15m")
    
    query = f"Generate live trading signals for {', '.join(symbols)} on {timeframe} timeframe"
    
    parameters = {
        "symbols": symbols,
        "timeframe": timeframe,
        "signal_type": "live",
        **signals_data
    }
    
    result = await zmarty_service.process_request(
        user_id=current_user.id,
        query=query,
        request_type="live_signals",
        parameters=parameters
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

@router.post("/ai-predictions")
async def ai_predictions(
    prediction_data: Dict[str, Any],
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db_session)
):
    """Get AI-powered price predictions"""
    zmarty_service = ZmartyService(db)
    
    symbol = prediction_data.get("symbol", "BTCUSDT")
    prediction_horizon = prediction_data.get("horizon", "24h")
    confidence_level = prediction_data.get("confidence", "medium")
    
    query = f"Predict price movement for {symbol} over {prediction_horizon} with {confidence_level} confidence"
    
    parameters = {
        "symbol": symbol,
        "prediction_horizon": prediction_horizon,
        "confidence_level": confidence_level,
        "include_probability": True,
        **prediction_data
    }
    
    result = await zmarty_service.process_request(
        user_id=current_user.id,
        query=query,
        request_type="ai_predictions",
        parameters=parameters
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

@router.get("/cost-estimate")
async def estimate_cost(
    request_type: str,
    query_length: int = 0,
    complexity: str = "medium",
    db: AsyncSession = Depends(get_db_session)
):
    """Estimate credit cost for a request"""
    zmarty_service = ZmartyService(db)
    
    parameters = {
        "complexity": complexity,
        "query_length": query_length
    }
    
    cost = await zmarty_service.calculate_request_cost(request_type, parameters)
    
    return {
        "request_type": request_type,
        "estimated_cost": cost,
        "parameters": parameters
    }