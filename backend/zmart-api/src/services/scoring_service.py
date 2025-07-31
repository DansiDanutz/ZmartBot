#!/usr/bin/env python3
"""
Multi-Timeframe AI Scoring Service
Based on Cryptometer_Complete_AI_System from Documentation folder

This service provides:
- Multi-timeframe analysis (SHORT/MEDIUM/LONG)
- AI-powered decision making
- Realistic win-rate scoring
- Dynamic pattern recognition
- Professional-grade trading signals
"""

import numpy as np
import pandas as pd
from datetime import datetime
import json
import time
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

from .cryptometer_service import get_cryptometer_service

# Configure logging
logger = logging.getLogger(__name__)

class MarketCondition(Enum):
    """Market condition classifications"""
    BULL_MARKET = "bull"
    BEAR_MARKET = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_vol"
    LOW_VOLATILITY = "low_vol"

@dataclass
class MultiTimeframeScore:
    """Multi-timeframe scoring result"""
    symbol: str
    short_term: Dict[str, Any]  # 24-48h analysis
    medium_term: Dict[str, Any]  # 1 week analysis
    long_term: Dict[str, Any]    # 1 month+ analysis
    ai_recommendation: Dict[str, Any]  # AI agent decision
    timestamp: datetime

@dataclass
class TradingSignal:
    """Trading signal with multi-timeframe context"""
    symbol: str
    action: str  # ALL_IN, AGGRESSIVE, MODERATE, CONSERVATIVE, AVOID
    timeframe: str  # SHORT, MEDIUM, LONG
    score: float  # 0-100
    signal: str  # LONG, SHORT, NEUTRAL
    position_size: str  # MAXIMUM, LARGE, MEDIUM, SMALL, NONE
    reasoning: str
    risk_level: str  # LOW, MEDIUM, HIGH
    timestamp: datetime

class MultiTimeframeScoringService:
    """
    Multi-Timeframe AI Scoring Service
    Analyzes symbols across SHORT (24-48h), MEDIUM (1 week), LONG (1 month+) timeframes
    """
    
    def __init__(self):
        self.max_total_score = 100.0
        
        # Risk bands based on multi-timeframe analysis
        self.risk_bands = {
            "royal_flush": {"min_score": 95, "max_score": 100, "description": "Royal Flush - ALL-IN opportunity"},
            "poker_aces": {"min_score": 90, "max_score": 94, "description": "Poker Aces - Maximum position"},
            "good_hand": {"min_score": 80, "max_score": 89, "description": "Good Hand - Take the trade"},
            "fold": {"min_score": 0, "max_score": 79, "description": "Fold - Wait for better setup"}
        }
    
    async def analyze_symbol_multi_timeframe(self, symbol: str) -> Optional[MultiTimeframeScore]:
        """Analyze a symbol using multi-timeframe AI agent"""
        try:
            # Get Cryptometer service
            cryptometer_service = await get_cryptometer_service()
            
            # Run multi-timeframe analysis
            analysis_result = cryptometer_service.analyze_multi_timeframe_symbol(symbol)
            
            if 'error' in analysis_result:
                logger.error(f"Error analyzing {symbol}: {analysis_result['error']}")
                return None
            
            # Create multi-timeframe score
            score = MultiTimeframeScore(
                symbol=symbol,
                short_term=analysis_result.get('short_term', {}),
                medium_term=analysis_result.get('medium_term', {}),
                long_term=analysis_result.get('long_term', {}),
                ai_recommendation=analysis_result.get('ai_recommendation', {}),
                timestamp=datetime.utcnow()
            )
            
            return score
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe analysis for {symbol}: {e}")
            return None
    
    async def get_trading_signal(self, symbol: str) -> Optional[TradingSignal]:
        """Get trading signal with multi-timeframe context"""
        try:
            # Analyze symbol
            score = await self.analyze_symbol_multi_timeframe(symbol)
            
            if not score:
                return None
            
            # Extract AI recommendation
            ai_rec = score.ai_recommendation.get('primary_recommendation', {})
            risk_assessment = score.ai_recommendation.get('risk_assessment', 'HIGH')
            
            # Create trading signal
            signal = TradingSignal(
                symbol=symbol,
                action=ai_rec.get('action', 'AVOID'),
                timeframe=ai_rec.get('timeframe', 'UNKNOWN'),
                score=ai_rec.get('score', 0),
                signal=ai_rec.get('signal', 'NEUTRAL'),
                position_size=ai_rec.get('position_size', 'NONE'),
                reasoning=ai_rec.get('reasoning', 'No reasoning available'),
                risk_level=risk_assessment,
                timestamp=datetime.utcnow()
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error getting trading signal for {symbol}: {e}")
            return None
    
    async def analyze_multiple_symbols(self, symbols: List[str]) -> List[MultiTimeframeScore]:
        """Analyze multiple symbols using multi-timeframe analysis"""
        try:
            results = []
            
            for symbol in symbols:
                score = await self.analyze_symbol_multi_timeframe(symbol)
                if score:
                    results.append(score)
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing multiple symbols: {e}")
            return []
    
    def get_risk_band(self, score: float) -> str:
        """Get risk band based on score"""
        for band_name, band_config in self.risk_bands.items():
            if band_config['min_score'] <= score <= band_config['max_score']:
                return band_name
        return "fold"
    
    def format_analysis_result(self, score: MultiTimeframeScore) -> Dict[str, Any]:
        """Format analysis result for API response"""
        try:
            ai_rec = score.ai_recommendation.get('primary_recommendation', {})
            risk_band = self.get_risk_band(ai_rec.get('score', 0))
            
            return {
                'symbol': score.symbol,
                'analysis': {
                    'short_term': {
                        'timeframe': score.short_term.get('timeframe', 'SHORT (24-48h)'),
                        'score': score.short_term.get('score', 0),
                        'signal': score.short_term.get('signal', 'NEUTRAL'),
                        'trade_type': score.short_term.get('trade_type', 'SCALP_TRADE'),
                        'patterns': len(score.short_term.get('patterns', []))
                    },
                    'medium_term': {
                        'timeframe': score.medium_term.get('timeframe', 'MEDIUM (1 week)'),
                        'score': score.medium_term.get('score', 0),
                        'signal': score.medium_term.get('signal', 'NEUTRAL'),
                        'trade_type': score.medium_term.get('trade_type', 'SWING_TRADE'),
                        'patterns': len(score.medium_term.get('patterns', []))
                    },
                    'long_term': {
                        'timeframe': score.long_term.get('timeframe', 'LONG (1 month+)'),
                        'score': score.long_term.get('score', 0),
                        'signal': score.long_term.get('signal', 'NEUTRAL'),
                        'trade_type': score.long_term.get('trade_type', 'POSITION_TRADE'),
                        'patterns': len(score.long_term.get('patterns', []))
                    }
                },
                'ai_recommendation': {
                    'action': ai_rec.get('action', 'AVOID'),
                    'timeframe': ai_rec.get('timeframe', 'UNKNOWN'),
                    'score': ai_rec.get('score', 0),
                    'signal': ai_rec.get('signal', 'NEUTRAL'),
                    'position_size': ai_rec.get('position_size', 'NONE'),
                    'reasoning': ai_rec.get('reasoning', 'No reasoning available'),
                    'risk_level': score.ai_recommendation.get('risk_assessment', 'HIGH')
                },
                'risk_band': risk_band,
                'risk_band_description': self.risk_bands.get(risk_band, {}).get('description', 'Unknown'),
                'timestamp': score.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error formatting analysis result: {e}")
            return {
                'symbol': score.symbol,
                'error': str(e),
                'timestamp': score.timestamp.isoformat()
            }

# Global service instance
_scoring_service = None

async def get_scoring_service() -> MultiTimeframeScoringService:
    """Get or create scoring service instance"""
    global _scoring_service
    if _scoring_service is None:
        _scoring_service = MultiTimeframeScoringService()
    return _scoring_service

async def analyze_symbol_scoring(symbol: str) -> Optional[Dict[str, Any]]:
    """Analyze symbol using multi-timeframe scoring"""
    try:
        service = await get_scoring_service()
        score = await service.analyze_symbol_multi_timeframe(symbol)
        
        if score:
            return service.format_analysis_result(score)
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error in symbol scoring analysis: {e}")
        return None

async def get_trading_signal(symbol: str) -> Optional[Dict[str, Any]]:
    """Get trading signal for a symbol"""
    try:
        service = await get_scoring_service()
        signal = await service.get_trading_signal(symbol)
        
        if signal:
            return {
                'symbol': signal.symbol,
                'action': signal.action,
                'timeframe': signal.timeframe,
                'score': signal.score,
                'signal': signal.signal,
                'position_size': signal.position_size,
                'reasoning': signal.reasoning,
                'risk_level': signal.risk_level,
                'timestamp': signal.timestamp.isoformat()
            }
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error getting trading signal: {e}")
        return None

async def analyze_multiple_symbols_scoring(symbols: List[str]) -> List[Dict[str, Any]]:
    """Analyze multiple symbols using multi-timeframe scoring"""
    try:
        service = await get_scoring_service()
        scores = await service.analyze_multiple_symbols(symbols)
        
        results = []
        for score in scores:
            formatted_result = service.format_analysis_result(score)
            results.append(formatted_result)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in multiple symbols scoring: {e}")
        return [] 