from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from src.services.score_tracking_service import ScoreTrackingService

router = APIRouter(prefix="/api/v1/score-tracking", tags=["Score Tracking"])
logger = logging.getLogger(__name__)

# Initialize service
score_tracking_service = ScoreTrackingService()

@router.post("/record")
async def record_daily_score(
    symbol: str,
    current_price: float,
    risk_value: float,
    risk_band: str,
    base_score: float,
    coefficient_value: float,
    total_score: float,
    risk_bands_data: Dict[str, Any],
    life_age_days: int,
    base_score_components: Optional[Dict[str, Any]] = None,
    coefficient_calculation: Optional[Dict[str, Any]] = None
):
    """
    Record daily score tracking data for a symbol
    """
    try:
        success = await score_tracking_service.record_daily_score(
            symbol=symbol,
            current_price=current_price,
            risk_value=risk_value,
            risk_band=risk_band,
            base_score=base_score,
            coefficient_value=coefficient_value,
            total_score=total_score,
            risk_bands_data=risk_bands_data,
            life_age_days=life_age_days,
            base_score_components=base_score_components,
            coefficient_calculation=coefficient_calculation
        )
        
        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "message": f"Score tracking recorded successfully for {symbol}",
                    "symbol": symbol,
                    "date": datetime.utcnow().date().isoformat()
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to record score tracking")
            
    except Exception as e:
        logger.error(f"Error recording daily score for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/history/{symbol}")
async def get_score_history(
    symbol: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records")
):
    """
    Get score history for a symbol
    """
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        history = await score_tracking_service.get_score_history(
            symbol=symbol,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "symbol": symbol,
                "history": history,
                "count": len(history),
                "start_date": start_date,
                "end_date": end_date
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting score history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/analytics/{symbol}")
async def get_score_analytics(
    symbol: str,
    period_type: str = Query("daily", description="Period type: daily, weekly, monthly"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get comprehensive score analytics for a symbol
    """
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Validate period type
        if period_type not in ["daily", "weekly", "monthly"]:
            raise HTTPException(status_code=400, detail="Invalid period_type. Must be daily, weekly, or monthly")
        
        analytics = await score_tracking_service.get_score_analytics(
            symbol=symbol,
            period_type=period_type,
            start_date=start_dt,
            end_date=end_dt
        )
        
        return JSONResponse(
            status_code=200,
            content=analytics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting score analytics for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/comparative")
async def get_comparative_analysis(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Compare score performance across multiple symbols
    """
    try:
        # Parse symbols
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        
        if not symbol_list:
            raise HTTPException(status_code=400, detail="At least one symbol must be provided")
        
        if len(symbol_list) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 symbols allowed for comparison")
        
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        comparative_data = await score_tracking_service.get_comparative_analysis(
            symbols=symbol_list,
            start_date=start_dt,
            end_date=end_dt
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "symbols": symbol_list,
                "start_date": start_date,
                "end_date": end_date,
                "comparative_analysis": comparative_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting comparative analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/summary")
async def get_score_summary():
    """
    Get summary of all tracked symbols
    """
    try:
        # This would need to be implemented in the service
        # For now, return a placeholder
        return JSONResponse(
            status_code=200,
            content={
                "message": "Score tracking summary endpoint - to be implemented",
                "tracked_symbols": [],
                "total_records": 0,
                "date_range": {
                    "earliest": None,
                    "latest": None
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting score summary: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/history/{symbol}")
async def delete_score_history(
    symbol: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Delete score history for a symbol (admin only)
    """
    try:
        # Check if user is admin (placeholder for future implementation)
        # if not current_user.is_admin:
        #     raise HTTPException(status_code=403, detail="Admin access required")
        
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # This would need to be implemented in the service
        # For now, return a placeholder
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Score history deletion for {symbol} - to be implemented",
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting score history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
