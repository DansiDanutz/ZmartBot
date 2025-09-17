#!/usr/bin/env python3
"""
Cryptometer API Routes - Multi-Timeframe AI System
Based on Cryptometer_Complete_AI_System from Documentation folder
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from src.services.cryptometer_service import get_cryptometer_service, MultiTimeframeCryptometerSystem
# Scoring service temporarily disabled - using unified scoring system
# from src.services.scoring_service import get_scoring_service, analyze_symbol_scoring

# Mock scoring service functions
async def get_scoring_service():
    """Mock scoring service"""
    return MockScoringService()

def analyze_symbol_scoring(symbol: str):
    """Mock symbol scoring analysis"""
    return {
        'symbol': symbol,
        'score': 75.0,
        'confidence': 0.8,
        'signal': 'Buy',
        'timestamp': datetime.utcnow().isoformat()
    }

class MockScoringService:
    """Mock scoring service for compatibility"""
    
    async def analyze_symbol_multi_timeframe(self, symbol: str):
        return {
            'symbol': symbol,
            'analysis': 'Mock analysis',
            'ai_recommendation': {'action': 'Hold', 'score': 75.0},
            'risk_band': 'Medium',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def format_analysis_result(self, score):
        return score
    
    async def get_trading_signal(self, symbol: str):
        class MockSignal:
            def __init__(self):
                self.symbol = symbol
                self.action = 'Hold'
                self.timeframe = '24h'
                self.score = 75.0
                self.signal = 'NEUTRAL'
                self.position_size = 'NONE'
                self.reasoning = 'Mock signal'
                self.risk_level = 'MEDIUM'
                self.timestamp = datetime.utcnow()
        
        return MockSignal()
    
    async def analyze_multiple_symbols(self, symbols: list):
        """Mock multiple symbol analysis"""
        results = []
        for symbol in symbols:
            results.append({
                'symbol': symbol,
                'score': 75.0,
                'confidence': 0.8,
                'signal': 'Hold',
                'timestamp': datetime.utcnow().isoformat()
            })
        return results

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/cryptometer", tags=["cryptometer"])

# Pydantic models
class SymbolDataResponse(BaseModel):
    """Response model for symbol data"""
    symbol: str
    endpoints: Dict[str, Any]
    summary: Dict[str, Any]
    timestamp: str

class MarketAnalysisResponse(BaseModel):
    """Response model for market analysis"""
    symbol: str
    analysis: Dict[str, Any]
    ai_recommendation: Dict[str, Any]
    risk_band: str
    risk_band_description: str
    timestamp: str

class TradingSignalResponse(BaseModel):
    """Response model for trading signal"""
    symbol: str
    action: str
    timeframe: str
    score: float
    signal: str
    position_size: str
    reasoning: str
    risk_level: str
    timestamp: str

class CryptometerResponse(BaseModel):
    """Generic Cryptometer response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

@router.get("/symbol/{symbol}", response_model=SymbolDataResponse)
async def get_symbol_data(symbol: str):
    """Get comprehensive data for a symbol from all Cryptometer endpoints"""
    try:
        logger.info(f"🔍 Collecting data for {symbol}")
        
        # Get Cryptometer service
        cryptometer_service = await get_cryptometer_service()
        
        # Collect comprehensive data
        symbol_data = await cryptometer_service.collect_symbol_data(symbol)
        
        if 'error' in symbol_data:
            raise HTTPException(status_code=500, detail=f"Error collecting data: {symbol_data['error']}")
        
        # Calculate summary
        endpoints = symbol_data
        successful_endpoints = sum(1 for endpoint in endpoints.values() 
                                 if isinstance(endpoint, dict) and endpoint.get('success', False))
        total_endpoints = len(endpoints)
        success_rate = (successful_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
        
        summary = {
            'total_endpoints': total_endpoints,
            'successful_endpoints': successful_endpoints,
            'success_rate': success_rate,
            'data_quality': success_rate / 100.0
        }
        
        return SymbolDataResponse(
            symbol=symbol,
            endpoints=endpoints,
            summary=summary,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting symbol data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{symbol}", response_model=MarketAnalysisResponse)
async def get_market_analysis(symbol: str):
    """Get multi-timeframe market analysis for a symbol"""
    try:
        logger.info(f"🔍 Analyzing {symbol} with multi-timeframe AI")
        
        # Get scoring service
        scoring_service = await get_scoring_service()
        
        # Analyze symbol
        score = await scoring_service.analyze_symbol_multi_timeframe(symbol)
        
        if not score:
            raise HTTPException(status_code=500, detail=f"Failed to analyze {symbol}")
        
        # Format result
        result = scoring_service.format_analysis_result(score)
        
        return MarketAnalysisResponse(
            symbol=result['symbol'],
            analysis=result['analysis'],
            ai_recommendation=result['ai_recommendation'],
            risk_band=result['risk_band'],
            risk_band_description=result['risk_band_description'],
            timestamp=result['timestamp']
        )
        
    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signal/{symbol}", response_model=TradingSignalResponse)
async def get_trading_signal(symbol: str):
    """Get trading signal for a symbol"""
    try:
        logger.info(f"🎯 Getting trading signal for {symbol}")
        
        # Get scoring service
        scoring_service = await get_scoring_service()
        
        # Get trading signal
        signal = await scoring_service.get_trading_signal(symbol)
        
        if not signal:
            raise HTTPException(status_code=500, detail=f"Failed to get trading signal for {symbol}")
        
        return TradingSignalResponse(
            symbol=signal.symbol,
            action=signal.action,
            timeframe=signal.timeframe,
            score=signal.score,
            signal=signal.signal,
            position_size=signal.position_size,
            reasoning=signal.reasoning,
            risk_level=signal.risk_level,
            timestamp=signal.timestamp.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting trading signal for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/endpoints", response_model=Dict[str, Any])
async def get_endpoints_info():
    """Get information about available Cryptometer endpoints"""
    try:
        # Get Cryptometer service
        cryptometer_service = await get_cryptometer_service()
        
        endpoints_info = {}
        for name, config in cryptometer_service.endpoints.items():
            endpoints_info[name] = {
                'url': config['url'],
                'description': config['description'],
                'weight': config['weight']
            }
        
        return {
            'endpoints': endpoints_info,
            'total_endpoints': len(endpoints_info),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting endpoints info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=CryptometerResponse)
async def get_health_status():
    """Get Cryptometer service health status"""
    try:
        # Get Cryptometer service
        cryptometer_service = await get_cryptometer_service()
        
        # Test basic functionality
        test_symbol = "BTC"
        symbol_data = await cryptometer_service.collect_symbol_data(test_symbol)
        
        successful_endpoints = sum(1 for endpoint in symbol_data.values() 
                                 if isinstance(endpoint, dict) and endpoint.get('success', False))
        
        health_status = {
            'status': 'healthy' if successful_endpoints > 0 else 'degraded',
            'successful_endpoints': successful_endpoints,
            'total_endpoints': len(symbol_data),
            'test_symbol': test_symbol
        }
        
        return CryptometerResponse(
            success=True,
            data=health_status,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error checking health status: {e}")
        return CryptometerResponse(
            success=False,
            error=str(e),
            timestamp=datetime.utcnow().isoformat()
        )

@router.post("/analyze-multiple", response_model=List[MarketAnalysisResponse])
async def analyze_multiple_symbols(symbols: List[str]):
    """Analyze multiple symbols using multi-timeframe AI"""
    try:
        logger.info(f"🔍 Analyzing multiple symbols: {symbols}")
        
        # Get scoring service
        scoring_service = await get_scoring_service()
        
        # Analyze symbols
        scores = await scoring_service.analyze_multiple_symbols(symbols)
        
        results = []
        for score in scores:
            result = scoring_service.format_analysis_result(score)
            results.append(MarketAnalysisResponse(
                symbol=result['symbol'],
                analysis=result['analysis'],
                ai_recommendation=result['ai_recommendation'],
                risk_band=result['risk_band'],
                risk_band_description=result['risk_band_description'],
                timestamp=result['timestamp']
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Error analyzing multiple symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scoring/{symbol}", response_model=Dict[str, Any])
async def get_symbol_scoring(symbol: str):
    """Get comprehensive scoring analysis for a symbol"""
    try:
        logger.info(f"📊 Getting scoring analysis for {symbol}")
        
        # Get scoring analysis
        analysis = analyze_symbol_scoring(symbol)
        
        if not analysis:
            raise HTTPException(status_code=500, detail=f"Failed to analyze {symbol}")
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error getting scoring for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 