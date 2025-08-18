#!/usr/bin/env python3
"""
Grok-X-Module FastAPI Routes
Production integration with real APIs and database storage
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

from ..services.grok_x_production_service import GrokXProductionService, GrokXSignal, GrokXAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/grok-x", tags=["Grok-X Module"])

# Initialize production service
grok_service = GrokXProductionService()

# Pydantic models for API requests/responses
class AnalysisRequest(BaseModel):
    symbols: List[str]
    keywords: Optional[List[str]] = None
    max_tweets: int = 50

class SignalResponse(BaseModel):
    id: str
    symbol: str
    action: str
    confidence: float
    sentiment: float
    risk_level: str
    entry_price_min: float
    entry_price_max: float
    stop_loss: float
    take_profit: float
    reasoning: str
    timestamp: str
    source: str
    status: str

class AnalysisResponse(BaseModel):
    id: str
    symbols: List[str]
    overall_sentiment: float
    confidence: float
    sentiment_label: str
    key_insights: List[str]
    market_implications: str
    processing_time: float
    timestamp: str
    social_data: Dict[str, Any]

class GrokXResponse(BaseModel):
    analysis: AnalysisResponse
    signals: List[SignalResponse]
    social_data: Dict[str, Any]
    metrics: Dict[str, Any]
    timestamp: str

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "grok-x-module",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/status")
async def get_status():
    """Get service status and statistics"""
    try:
        # Get database statistics
        conn = grok_service.db_path
        import sqlite3
        db_conn = sqlite3.connect(conn)
        cursor = db_conn.cursor()
        
        # Count signals
        cursor.execute("SELECT COUNT(*) FROM grok_x_signals")
        signal_count = cursor.fetchone()[0]
        
        # Count analysis
        cursor.execute("SELECT COUNT(*) FROM grok_x_analysis")
        analysis_count = cursor.fetchone()[0]
        
        # Get latest analysis
        cursor.execute("SELECT timestamp FROM grok_x_analysis ORDER BY timestamp DESC LIMIT 1")
        latest_analysis = cursor.fetchone()
        latest_timestamp = latest_analysis[0] if latest_analysis else None
        
        db_conn.close()
        
        return {
            "status": "operational",
            "database": {
                "signals_count": signal_count,
                "analysis_count": analysis_count,
                "latest_analysis": latest_timestamp
            },
            "api_limits": {
                "x_api_calls": grok_service.x_api_calls,
                "grok_api_calls": grok_service.grok_api_calls
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.post("/analyze", response_model=GrokXResponse)
async def analyze_symbols(request: AnalysisRequest):
    """Analyze symbols using Grok-X-Module"""
    
    try:
        logger.info(f"🔍 Starting analysis for symbols: {request.symbols}")
        
        # Run production analysis
        result = await grok_service.run_production_analysis(request.symbols)
        
        logger.info(f"✅ Analysis completed for {len(request.symbols)} symbols")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/signals", response_model=List[SignalResponse])
async def get_signals(limit: int = 50, symbol: Optional[str] = None, status: Optional[str] = None):
    """Get trading signals from database"""
    
    try:
        import sqlite3
        conn = sqlite3.connect(grok_service.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM grok_x_signals WHERE 1=1"
        params = []
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to SignalResponse objects
        signals = []
        for row in rows:
            signal = SignalResponse(
                id=row[0],
                symbol=row[1],
                action=row[2],
                confidence=row[3],
                sentiment=row[4],
                risk_level=row[5],
                entry_price_min=row[6],
                entry_price_max=row[7],
                stop_loss=row[8],
                take_profit=row[9],
                reasoning=row[10],
                timestamp=row[11],
                source=row[12],
                status=row[13]
            )
            signals.append(signal)
        
        conn.close()
        
        return signals
        
    except Exception as e:
        logger.error(f"❌ Failed to get signals: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get signals: {str(e)}")

@router.get("/analysis", response_model=List[AnalysisResponse])
async def get_analysis(limit: int = 20):
    """Get analysis results from database"""
    
    try:
        import sqlite3
        import json
        conn = sqlite3.connect(grok_service.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, symbols, overall_sentiment, confidence, sentiment_label,
                   key_insights, market_implications, processing_time, timestamp, social_data
            FROM grok_x_analysis 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        
        # Convert to AnalysisResponse objects
        analysis_list = []
        for row in rows:
            analysis = AnalysisResponse(
                id=row[0],
                symbols=json.loads(row[1]),
                overall_sentiment=row[2],
                confidence=row[3],
                sentiment_label=row[4],
                key_insights=json.loads(row[5]),
                market_implications=row[6],
                processing_time=row[7],
                timestamp=row[8],
                social_data=json.loads(row[9])
            )
            analysis_list.append(analysis)
        
        conn.close()
        
        return analysis_list
        
    except Exception as e:
        logger.error(f"❌ Failed to get analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")

@router.get("/signals/{symbol}")
async def get_signals_by_symbol(symbol: str, limit: int = 20):
    """Get signals for a specific symbol"""
    
    try:
        import sqlite3
        conn = sqlite3.connect(grok_service.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM grok_x_signals 
            WHERE symbol = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (symbol.upper(), limit))
        
        rows = cursor.fetchall()
        
        signals = []
        for row in rows:
            signal = {
                "id": row[0],
                "symbol": row[1],
                "action": row[2],
                "confidence": row[3],
                "sentiment": row[4],
                "risk_level": row[5],
                "entry_price_min": row[6],
                "entry_price_max": row[7],
                "stop_loss": row[8],
                "take_profit": row[9],
                "reasoning": row[10],
                "timestamp": row[11],
                "source": row[12],
                "status": row[13]
            }
            signals.append(signal)
        
        conn.close()
        
        return {
            "symbol": symbol.upper(),
            "signals": signals,
            "count": len(signals),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get signals for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get signals: {str(e)}")

@router.post("/monitor")
async def start_monitoring(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start continuous monitoring for symbols"""
    
    try:
        logger.info(f"🔄 Starting continuous monitoring for: {request.symbols}")
        
        # Add monitoring task to background
        background_tasks.add_task(
            run_continuous_monitoring,
            symbols=request.symbols,
            interval_minutes=30
        )
        
        return {
            "status": "monitoring_started",
            "symbols": request.symbols,
            "interval_minutes": 30,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to start monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")

async def run_continuous_monitoring(symbols: List[str], interval_minutes: int = 30):
    """Background task for continuous monitoring"""
    
    logger.info(f"🔄 Starting continuous monitoring for {symbols}")
    
    while True:
        try:
            # Run analysis
            result = await grok_service.run_production_analysis(symbols)
            
            # Log results
            logger.info(f"📊 Monitoring cycle completed:")
            logger.info(f"   Sentiment: {result['metrics']['overall_sentiment']:.3f}")
            logger.info(f"   Signals: {result['metrics']['signal_count']}")
            
            # Check for alerts
            if abs(result['metrics']['overall_sentiment']) > 0.7:
                logger.warning(f"🚨 ALERT: Extreme sentiment detected!")
            
            if result['metrics']['signal_count'] > 0:
                logger.info(f"📈 ALERT: {result['metrics']['signal_count']} trading signals generated!")
            
            # Wait for next cycle
            await asyncio.sleep(interval_minutes * 60)
            
        except Exception as e:
            logger.error(f"❌ Monitoring cycle failed: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

@router.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    
    try:
        import sqlite3
        conn = sqlite3.connect(grok_service.db_path)
        cursor = conn.cursor()
        
        # Get signal statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_signals,
                COUNT(CASE WHEN action = 'BUY' THEN 1 END) as buy_signals,
                COUNT(CASE WHEN action = 'SELL' THEN 1 END) as sell_signals,
                COUNT(CASE WHEN action = 'HOLD' THEN 1 END) as hold_signals,
                AVG(confidence) as avg_confidence,
                AVG(sentiment) as avg_sentiment
            FROM grok_x_signals
        """)
        
        signal_stats = cursor.fetchone()
        
        # Get analysis statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_analysis,
                AVG(overall_sentiment) as avg_sentiment,
                AVG(confidence) as avg_confidence,
                AVG(processing_time) as avg_processing_time
            FROM grok_x_analysis
        """)
        
        analysis_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "signals": {
                "total": signal_stats[0],
                "buy_signals": signal_stats[1],
                "sell_signals": signal_stats[2],
                "hold_signals": signal_stats[3],
                "avg_confidence": signal_stats[4],
                "avg_sentiment": signal_stats[5]
            },
            "analysis": {
                "total": analysis_stats[0],
                "avg_sentiment": analysis_stats[1],
                "avg_confidence": analysis_stats[2],
                "avg_processing_time": analysis_stats[3]
            },
            "api_usage": {
                "x_api_calls": grok_service.x_api_calls,
                "grok_api_calls": grok_service.grok_api_calls
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.delete("/signals/{signal_id}")
async def delete_signal(signal_id: str):
    """Delete a specific signal"""
    
    try:
        import sqlite3
        conn = sqlite3.connect(grok_service.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM grok_x_signals WHERE id = ?", (signal_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Signal not found")
        
        conn.commit()
        conn.close()
        
        return {
            "status": "deleted",
            "signal_id": signal_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete signal: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete signal: {str(e)}")

@router.put("/signals/{signal_id}/status")
async def update_signal_status(signal_id: str, status: str):
    """Update signal status"""
    
    try:
        import sqlite3
        conn = sqlite3.connect(grok_service.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE grok_x_signals SET status = ? WHERE id = ?", (status, signal_id))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Signal not found")
        
        conn.commit()
        conn.close()
        
        return {
            "status": "updated",
            "signal_id": signal_id,
            "new_status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update signal status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update signal status: {str(e)}") 