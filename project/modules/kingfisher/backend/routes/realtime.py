#!/usr/bin/env python3
"""
Real-Time Analysis API Routes
Provides endpoints for symbol summaries, recent analyses, and statistics
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

router = APIRouter(prefix="/api/v1/realtime", tags=["Real-Time Analysis"])

@router.get("/summaries")
async def get_all_symbol_summaries():
    """Get summaries for all symbols"""
    try:
        from services.real_time_analyzer import RealTimeAnalyzer
        
        # Initialize analyzer (in production, this would be a singleton)
        analyzer = RealTimeAnalyzer()
        
        summaries = await analyzer.get_all_summaries()
        
        # Convert to JSON-serializable format
        result = {}
        for symbol, summary in summaries.items():
            result[symbol] = {
                'symbol': summary.symbol,
                'last_update': summary.last_update.isoformat(),
                'total_images': summary.total_images,
                'average_significance': summary.average_significance,
                'dominant_sentiment': summary.dominant_sentiment,
                'high_significance_count': summary.high_significance_count,
                'recent_trend': summary.recent_trend,
                'risk_level': summary.risk_level,
                'latest_analysis': {
                    'image_id': summary.latest_analysis.image_id,
                    'timestamp': summary.latest_analysis.timestamp.isoformat(),
                    'significance_score': summary.latest_analysis.significance_score,
                    'market_sentiment': summary.latest_analysis.market_sentiment,
                    'confidence': summary.latest_analysis.confidence,
                    'liquidation_clusters': summary.latest_analysis.liquidation_clusters,
                    'toxic_flow': summary.latest_analysis.toxic_flow
                } if summary.latest_analysis else None
            }
        
        return {
            "success": True,
            "summaries": result,
            "total_symbols": len(result),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summaries: {str(e)}")

@router.get("/summary/{symbol}")
async def get_symbol_summary(symbol: str):
    """Get summary for a specific symbol"""
    try:
        from services.real_time_analyzer import RealTimeAnalyzer
        
        analyzer = RealTimeAnalyzer()
        summary = await analyzer.get_symbol_summary(symbol)
        
        if not summary:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        return {
            "success": True,
            "summary": {
                'symbol': summary.symbol,
                'last_update': summary.last_update.isoformat(),
                'total_images': summary.total_images,
                'average_significance': summary.average_significance,
                'dominant_sentiment': summary.dominant_sentiment,
                'high_significance_count': summary.high_significance_count,
                'recent_trend': summary.recent_trend,
                'risk_level': summary.risk_level,
                'latest_analysis': {
                    'image_id': summary.latest_analysis.image_id,
                    'timestamp': summary.latest_analysis.timestamp.isoformat(),
                    'significance_score': summary.latest_analysis.significance_score,
                    'market_sentiment': summary.latest_analysis.market_sentiment,
                    'confidence': summary.latest_analysis.confidence,
                    'liquidation_clusters': summary.latest_analysis.liquidation_clusters,
                    'toxic_flow': summary.latest_analysis.toxic_flow
                } if summary.latest_analysis else None
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@router.get("/analyses")
async def get_recent_analyses(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(10, description="Number of recent analyses to return")
):
    """Get recent analyses for a symbol or all symbols"""
    try:
        from services.real_time_analyzer import RealTimeAnalyzer
        
        analyzer = RealTimeAnalyzer()
        analyses = await analyzer.get_recent_analyses(symbol=symbol, limit=limit)
        
        # Convert to JSON-serializable format
        result = []
        for analysis in analyses:
            result.append({
                'image_id': analysis.image_id,
                'symbol': analysis.symbol,
                'timestamp': analysis.timestamp.isoformat(),
                'significance_score': analysis.significance_score,
                'market_sentiment': analysis.market_sentiment,
                'confidence': analysis.confidence,
                'liquidation_clusters': analysis.liquidation_clusters,
                'toxic_flow': analysis.toxic_flow,
                'image_path': analysis.image_path,
                'analysis_data': analysis.analysis_data
            })
        
        return {
            "success": True,
            "analyses": result,
            "total_count": len(result),
            "symbol_filter": symbol,
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analyses: {str(e)}")

@router.get("/statistics")
async def get_analysis_statistics():
    """Get overall analysis statistics"""
    try:
        from services.real_time_analyzer import RealTimeAnalyzer
        
        analyzer = RealTimeAnalyzer()
        stats = await analyzer.get_statistics()
        
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.get("/status")
async def get_monitoring_status():
    """Get real-time monitoring status"""
    try:
        from services.real_time_analyzer import RealTimeAnalyzer
        
        analyzer = RealTimeAnalyzer()
        stats = await analyzer.get_statistics()
        
        return {
            "success": True,
            "status": "active",
            "monitoring_active": True,
            "last_check": datetime.now().isoformat(),
            "statistics": stats,
            "message": "Real-time monitoring is active"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.post("/start-monitoring")
async def start_real_time_monitoring():
    """Start real-time monitoring"""
    try:
        from services.real_time_analyzer import RealTimeAnalyzer
        from services.telegram_service import TelegramService
        from services.image_processing_service import ImageProcessingService
        
        # Initialize services
        telegram_service = TelegramService()
        image_processor = ImageProcessingService()
        analyzer = RealTimeAnalyzer()
        
        # Start monitoring
        await analyzer.start_monitoring(telegram_service, image_processor)
        
        return {
            "success": True,
            "message": "Real-time monitoring started",
            "status": "active",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")

@router.get("/symbols")
async def get_all_symbols():
    """Get list of all symbols with analyses"""
    try:
        from services.real_time_analyzer import RealTimeAnalyzer
        
        analyzer = RealTimeAnalyzer()
        summaries = await analyzer.get_all_summaries()
        
        symbols = []
        for symbol, summary in summaries.items():
            symbols.append({
                'symbol': symbol,
                'last_update': summary.last_update.isoformat(),
                'total_images': summary.total_images,
                'average_significance': summary.average_significance,
                'risk_level': summary.risk_level,
                'recent_trend': summary.recent_trend
            })
        
        # Sort by last update (most recent first)
        symbols.sort(key=lambda x: x['last_update'], reverse=True)
        
        return {
            "success": True,
            "symbols": symbols,
            "total_symbols": len(symbols),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get symbols: {str(e)}")

@router.get("/high-significance")
async def get_high_significance_analyses(
    limit: int = Query(10, description="Number of high significance analyses to return")
):
    """Get recent high significance analyses"""
    try:
        from services.real_time_analyzer import RealTimeAnalyzer
        
        analyzer = RealTimeAnalyzer()
        all_analyses = await analyzer.get_recent_analyses(limit=100)  # Get more to filter
        
        # Filter for high significance (>70%)
        high_significance = [
            analysis for analysis in all_analyses 
            if analysis.significance_score > 0.7
        ][:limit]
        
        # Convert to JSON-serializable format
        result = []
        for analysis in high_significance:
            result.append({
                'image_id': analysis.image_id,
                'symbol': analysis.symbol,
                'timestamp': analysis.timestamp.isoformat(),
                'significance_score': analysis.significance_score,
                'market_sentiment': analysis.market_sentiment,
                'confidence': analysis.confidence,
                'liquidation_clusters': analysis.liquidation_clusters,
                'toxic_flow': analysis.toxic_flow,
                'alert_level': 'high' if analysis.significance_score > 0.8 else 'medium'
            })
        
        return {
            "success": True,
            "high_significance_analyses": result,
            "total_count": len(result),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get high significance analyses: {str(e)}") 