#!/usr/bin/env python3
"""
Indicators History API Routes
Provides access to the comprehensive indicators history database
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import json
import base64
from io import BytesIO

from ..database.indicators_history_database import get_indicators_database, IndicatorSnapshot
from ..services.indicators_collector_service import get_indicators_collector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/indicators-history", tags=["Indicators History"])

@router.get("/status")
async def get_system_status():
    """Get system status and statistics"""
    try:
        db = get_indicators_database()
        collector = await get_indicators_collector()
        
        db_stats = db.get_database_stats()
        collection_stats = collector.get_collection_stats()
        
        return {
            'ok': True,
            'status': 'operational' if collection_stats['is_running'] else 'stopped',
            'database': db_stats,
            'collector': collection_stats,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-collection")
async def start_collection(background_tasks: BackgroundTasks):
    """Start the indicators collection service"""
    try:
        collector = await get_indicators_collector()
        
        if collector.is_running:
            return {
                'ok': True,
                'message': 'Collection service is already running',
                'status': 'running'
            }
        
        # Start collection in background
        background_tasks.add_task(collector.start)
        
        return {
            'ok': True,
            'message': 'Indicators collection service started',
            'status': 'starting'
        }
        
    except Exception as e:
        logger.error(f"Error starting collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-collection")
async def stop_collection():
    """Stop the indicators collection service"""
    try:
        collector = await get_indicators_collector()
        await collector.stop()
        
        return {
            'ok': True,
            'message': 'Indicators collection service stopped',
            'status': 'stopped'
        }
        
    except Exception as e:
        logger.error(f"Error stopping collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbols")
async def get_tracked_symbols():
    """Get list of all tracked symbols"""
    try:
        db = get_indicators_database()
        symbols = db.get_tracked_symbols()
        
        return {
            'ok': True,
            'symbols': symbols,
            'count': len(symbols)
        }
        
    except Exception as e:
        logger.error(f"Error getting tracked symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/symbols/{symbol}")
async def add_symbol(symbol: str):
    """Add a new symbol to track"""
    try:
        db = get_indicators_database()
        success = db.add_symbol(symbol.upper())
        
        if success:
            return {
                'ok': True,
                'message': f'Symbol {symbol.upper()} added to tracking',
                'symbol': symbol.upper()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to add symbol {symbol}")
        
    except Exception as e:
        logger.error(f"Error adding symbol {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/snapshots/{symbol}")
async def get_symbol_snapshots(
    symbol: str,
    timeframe: Optional[str] = Query(None, description="Timeframe filter (15m, 1h, 4h, 1d)"),
    hours: Optional[int] = Query(24, description="Number of hours to look back"),
    limit: Optional[int] = Query(100, description="Maximum number of snapshots")
):
    """Get indicator snapshots for a symbol"""
    try:
        db = get_indicators_database()
        
        # Calculate time range
        start_time = datetime.now() - timedelta(hours=hours) if hours else None
        
        snapshots = db.get_snapshots(
            symbol=symbol.upper(),
            timeframe=timeframe,
            start_time=start_time,
            limit=limit
        )
        
        # Convert to JSON-serializable format
        snapshots_data = []
        for snapshot in snapshots:
            snapshot_dict = {
                'id': snapshot.id,
                'symbol': snapshot.symbol,
                'timestamp': snapshot.timestamp.isoformat(),
                'timeframe': snapshot.timeframe,
                'indicators': {
                    'rsi': snapshot.rsi,
                    'rsi_14': snapshot.rsi_14,
                    'macd': {
                        'macd': snapshot.macd,
                        'signal': snapshot.macd_signal,
                        'histogram': snapshot.macd_histogram
                    },
                    'emas': {
                        'ema_9': snapshot.ema_9,
                        'ema_21': snapshot.ema_21,
                        'ema_50': snapshot.ema_50,
                        'ema_200': snapshot.ema_200
                    },
                    'smas': {
                        'sma_20': snapshot.sma_20,
                        'sma_50': snapshot.sma_50
                    },
                    'bollinger_bands': {
                        'upper': snapshot.bollinger_upper,
                        'middle': snapshot.bollinger_middle,
                        'lower': snapshot.bollinger_lower
                    },
                    'stochastic': {
                        'k': snapshot.stochastic_k,
                        'd': snapshot.stochastic_d
                    },
                    'others': {
                        'atr': snapshot.atr,
                        'adx': snapshot.adx,
                        'cci': snapshot.cci,
                        'williams_r': snapshot.williams_r,
                        'parabolic_sar': snapshot.parabolic_sar
                    }
                },
                'market_data': {
                    'price': snapshot.price,
                    'volume': snapshot.volume,
                    'volume_24h': snapshot.volume_24h,
                    'market_cap': snapshot.market_cap
                },
                'pattern_analysis': {
                    'trend_direction': snapshot.trend_direction,
                    'support_level': snapshot.support_level,
                    'resistance_level': snapshot.resistance_level,
                    'pattern_detected': snapshot.pattern_detected,
                    'signal_strength': snapshot.signal_strength
                },
                'screenshot_available': bool(snapshot.screenshot_path),
                'data_source': snapshot.data_source,
                'created_at': snapshot.created_at.isoformat() if snapshot.created_at else None
            }
            snapshots_data.append(snapshot_dict)
        
        return {
            'ok': True,
            'symbol': symbol.upper(),
            'timeframe': timeframe,
            'snapshots': snapshots_data,
            'count': len(snapshots_data),
            'query': {
                'hours_back': hours,
                'limit': limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting snapshots for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/snapshots/{symbol}/latest")
async def get_latest_snapshot(symbol: str, timeframe: str = "1h"):
    """Get the latest snapshot for a symbol"""
    try:
        db = get_indicators_database()
        
        snapshots = db.get_snapshots(
            symbol=symbol.upper(),
            timeframe=timeframe,
            limit=1
        )
        
        if not snapshots:
            raise HTTPException(status_code=404, detail=f"No snapshots found for {symbol}")
        
        snapshot = snapshots[0]
        
        return {
            'ok': True,
            'symbol': symbol.upper(),
            'timeframe': timeframe,
            'snapshot': {
                'id': snapshot.id,
                'timestamp': snapshot.timestamp.isoformat(),
                'indicators': {
                    'rsi': snapshot.rsi,
                    'macd': snapshot.macd,
                    'price': snapshot.price,
                    'trend_direction': snapshot.trend_direction,
                    'signal_strength': snapshot.signal_strength
                },
                'screenshot_available': bool(snapshot.screenshot_path),
                'data_source': snapshot.data_source
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting latest snapshot for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/screenshots/{symbol}")
async def get_symbol_screenshots(
    symbol: str,
    hours: Optional[int] = Query(24, description="Number of hours to look back")
):
    """Get available screenshots for a symbol"""
    try:
        db = get_indicators_database()
        
        start_time = datetime.now() - timedelta(hours=hours) if hours else None
        
        snapshots = db.get_snapshots(
            symbol=symbol.upper(),
            start_time=start_time,
            limit=50
        )
        
        # Filter snapshots with screenshots
        screenshots = []
        for snapshot in snapshots:
            if snapshot.screenshot_path or snapshot.screenshot_base64:
                screenshots.append({
                    'id': snapshot.id,
                    'timestamp': snapshot.timestamp.isoformat(),
                    'timeframe': snapshot.timeframe,
                    'screenshot_path': snapshot.screenshot_path,
                    'metadata': snapshot.screenshot_metadata,
                    'has_base64': bool(snapshot.screenshot_base64)
                })
        
        return {
            'ok': True,
            'symbol': symbol.upper(),
            'screenshots': screenshots,
            'count': len(screenshots)
        }
        
    except Exception as e:
        logger.error(f"Error getting screenshots for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/screenshots/{symbol}/latest")
async def get_latest_screenshot(symbol: str, format: str = Query("path", enum=["path", "base64", "file"])):
    """Get the latest screenshot for a symbol"""
    try:
        db = get_indicators_database()
        
        snapshots = db.get_snapshots(symbol=symbol.upper(), limit=20)
        
        # Find latest snapshot with screenshot
        screenshot_snapshot = None
        for snapshot in snapshots:
            if snapshot.screenshot_path or snapshot.screenshot_base64:
                screenshot_snapshot = snapshot
                break
        
        if not screenshot_snapshot:
            raise HTTPException(status_code=404, detail=f"No screenshots found for {symbol}")
        
        if format == "file" and screenshot_snapshot.screenshot_path:
            # Return file directly
            return FileResponse(
                screenshot_snapshot.screenshot_path,
                media_type="image/png",
                filename=f"{symbol}_latest_indicators.png"
            )
        
        elif format == "base64" and screenshot_snapshot.screenshot_base64:
            return {
                'ok': True,
                'symbol': symbol.upper(),
                'timestamp': screenshot_snapshot.timestamp.isoformat(),
                'format': 'base64',
                'data': screenshot_snapshot.screenshot_base64,
                'metadata': screenshot_snapshot.screenshot_metadata
            }
        
        else:
            return {
                'ok': True,
                'symbol': symbol.upper(),
                'timestamp': screenshot_snapshot.timestamp.isoformat(),
                'format': 'path',
                'screenshot_path': screenshot_snapshot.screenshot_path,
                'metadata': screenshot_snapshot.screenshot_metadata
            }
        
    except Exception as e:
        logger.error(f"Error getting latest screenshot for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/patterns/{symbol}")
async def analyze_patterns(
    symbol: str,
    hours: Optional[int] = Query(168, description="Number of hours to analyze (default: 7 days)"),
    min_confidence: Optional[float] = Query(0.7, description="Minimum confidence score")
):
    """Analyze patterns for a symbol using historical indicator data"""
    try:
        db = get_indicators_database()
        
        start_time = datetime.now() - timedelta(hours=hours)
        
        snapshots = db.get_snapshots(
            symbol=symbol.upper(),
            timeframe="1h",
            start_time=start_time,
            limit=200
        )
        
        if len(snapshots) < 20:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient data for pattern analysis (need 20+ snapshots, have {len(snapshots)})"
            )
        
        # Simple pattern detection
        patterns = []
        
        # RSI divergence detection
        rsi_values = [s.rsi for s in reversed(snapshots) if s.rsi]
        prices = [s.price for s in reversed(snapshots) if s.price]
        
        if len(rsi_values) >= 10 and len(prices) >= 10:
            # Check for bullish divergence (price down, RSI up)
            recent_rsi = rsi_values[-5:]
            recent_prices = prices[-5:]
            
            if (recent_prices[-1] < recent_prices[0] and 
                recent_rsi[-1] > recent_rsi[0] and 
                recent_rsi[-1] < 40):
                
                patterns.append({
                    'type': 'bullish_rsi_divergence',
                    'confidence': 0.75,
                    'description': 'Price declining while RSI rising (bullish divergence)',
                    'timeframe': '1h',
                    'detected_at': snapshots[0].timestamp.isoformat()
                })
        
        # MACD crossover detection
        macd_values = [(s.macd, s.macd_signal) for s in reversed(snapshots) 
                      if s.macd and s.macd_signal]
        
        if len(macd_values) >= 3:
            for i in range(1, len(macd_values)):
                prev_macd, prev_signal = macd_values[i-1]
                curr_macd, curr_signal = macd_values[i]
                
                # Bullish crossover
                if prev_macd <= prev_signal and curr_macd > curr_signal:
                    patterns.append({
                        'type': 'macd_bullish_crossover',
                        'confidence': 0.8,
                        'description': 'MACD line crossed above signal line',
                        'timeframe': '1h',
                        'detected_at': snapshots[len(snapshots)-i-1].timestamp.isoformat()
                    })
                
                # Bearish crossover
                elif prev_macd >= prev_signal and curr_macd < curr_signal:
                    patterns.append({
                        'type': 'macd_bearish_crossover',
                        'confidence': 0.8,
                        'description': 'MACD line crossed below signal line',
                        'timeframe': '1h',
                        'detected_at': snapshots[len(snapshots)-i-1].timestamp.isoformat()
                    })
        
        # Filter by confidence
        filtered_patterns = [p for p in patterns if p['confidence'] >= min_confidence]
        
        return {
            'ok': True,
            'symbol': symbol.upper(),
            'analysis_period_hours': hours,
            'snapshots_analyzed': len(snapshots),
            'patterns_detected': len(filtered_patterns),
            'patterns': filtered_patterns,
            'metadata': {
                'min_confidence': min_confidence,
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing patterns for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup")
async def cleanup_old_data(days: Optional[int] = Query(30, description="Days of data to keep")):
    """Cleanup old indicator data"""
    try:
        db = get_indicators_database()
        db.cleanup_old_data(days_to_keep=days)
        
        return {
            'ok': True,
            'message': f'Cleaned up data older than {days} days',
            'days_kept': days
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/{symbol}")
async def export_symbol_data(
    symbol: str,
    format: str = Query("json", enum=["json", "csv"]),
    hours: Optional[int] = Query(168, description="Number of hours to export")
):
    """Export symbol data for external analysis"""
    try:
        db = get_indicators_database()
        
        start_time = datetime.now() - timedelta(hours=hours) if hours else None
        
        snapshots = db.get_snapshots(
            symbol=symbol.upper(),
            start_time=start_time,
            limit=1000
        )
        
        if format == "csv":
            # Convert to CSV format
            import pandas as pd
            
            data = []
            for snapshot in snapshots:
                data.append({
                    'timestamp': snapshot.timestamp,
                    'symbol': snapshot.symbol,
                    'timeframe': snapshot.timeframe,
                    'price': snapshot.price,
                    'rsi': snapshot.rsi,
                    'macd': snapshot.macd,
                    'macd_signal': snapshot.macd_signal,
                    'ema_21': snapshot.ema_21,
                    'sma_20': snapshot.sma_20,
                    'bollinger_upper': snapshot.bollinger_upper,
                    'bollinger_lower': snapshot.bollinger_lower,
                    'trend_direction': snapshot.trend_direction,
                    'signal_strength': snapshot.signal_strength
                })
            
            df = pd.DataFrame(data)
            csv_content = df.to_csv(index=False)
            
            return {
                'ok': True,
                'format': 'csv',
                'symbol': symbol.upper(),
                'records': len(data),
                'data': csv_content
            }
        
        else:
            # JSON format
            data = []
            for snapshot in snapshots:
                data.append({
                    'timestamp': snapshot.timestamp.isoformat(),
                    'symbol': snapshot.symbol,
                    'timeframe': snapshot.timeframe,
                    'indicators': {
                        'rsi': snapshot.rsi,
                        'macd': snapshot.macd,
                        'price': snapshot.price,
                        'trend': snapshot.trend_direction
                    }
                })
            
            return {
                'ok': True,
                'format': 'json',
                'symbol': symbol.upper(),
                'records': len(data),
                'data': data
            }
        
    except Exception as e:
        logger.error(f"Error exporting data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))