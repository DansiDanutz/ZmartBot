#!/usr/bin/env python3
"""
Calibrated Scoring Service - Individual Component Scoring
Integrates the calibrated win-rate system for realistic scoring

Components:
- KingFisher: Independent liquidation analysis scoring
- Cryptometer: Calibrated win-rate based scoring (95-100 = exceptional)
- RiskMetric: Independent risk-based scoring
- Aggregation: Flexible for future implementation
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
import statistics
import asyncio
from dataclasses import dataclass

from ..config.settings import settings


# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ComponentScore:
    """Individual component score"""
    component: str
    score: float
    win_rate: float
    direction: str
    confidence: float
    patterns: List[Dict[str, Any]]
    analysis_details: Dict[str, Any]
    timestamp: datetime

@dataclass
class IndependentScores:
    """Collection of independent component scores"""
    kingfisher: Optional[ComponentScore]
    cryptometer: Optional[ComponentScore]
    
    symbol: str
    timestamp: datetime
    
    def get_available_scores(self) -> Dict[str, ComponentScore]:
        """Get all available component scores"""
        scores = {}
        if self.kingfisher:
            scores['kingfisher'] = self.kingfisher
        if self.cryptometer:
            scores['cryptometer'] = self.cryptometer

        return scores

class CalibratedCryptometerEngine:
    """
    Calibrated Cryptometer scoring engine
    Based on realistic win-rate expectations from Documentation/Cryptometer_Final_Package/calibrated_win_rate_system.py
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.CRYPTOMETER_API_KEY
        self.base_url = "https://api.cryptometer.io"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ZmartBot-Calibrated/1.0',
            'Accept': 'application/json'
        })
        
        # REALISTIC pattern success rates (from calibrated system)
        self.pattern_success_rates = {
            # AI Screener patterns (conservative)
            'ai_screener_exceptional': 0.68,  # Only when >90% AI success rate
            'ai_screener_high': 0.62,         # When 80-90% AI success rate  
            'ai_screener_medium': 0.58,       # When 70-80% AI success rate
            'ai_screener_low': 0.52,          # When 60-70% AI success rate
            
            # Volume patterns (realistic)
            'volume_breakout_strong': 0.65,   # Strong volume confirmation
            'volume_breakout_moderate': 0.58, # Moderate volume
            'volume_divergence': 0.55,        # Volume divergence signals
            
            # Long/Short ratio patterns (contrarian)
            'ls_ratio_extreme': 0.64,         # Very extreme ratios (>2.0 or <0.3)
            'ls_ratio_high': 0.58,            # High ratios (1.5-2.0 or 0.3-0.5)
            'ls_ratio_moderate': 0.52,        # Moderate ratios
            
            # Liquidation patterns
            'liquidation_massive': 0.62,      # >$50M liquidations
            'liquidation_high': 0.58,         # $10-50M liquidations
            'liquidation_moderate': 0.54,     # $1-10M liquidations
            
            # Technical patterns (conservative)
            'trend_very_strong': 0.64,        # Multiple timeframe confirmation
            'trend_strong': 0.60,             # Single timeframe strong trend
            'trend_moderate': 0.56,           # Moderate trend signals
            
            # OHLCV patterns (realistic)
            'ohlcv_strong_breakout': 0.63,    # Clear breakout with volume
            'ohlcv_moderate_pattern': 0.57,   # Standard patterns
            'ohlcv_support_resistance': 0.61, # Key level bounces
            
            # Rapid movement patterns
            'rapid_strong_follow': 0.59,      # Strong momentum follow-through
            'rapid_moderate': 0.54,           # Moderate movements
            
            # Forex correlation
            'forex_strong_correlation': 0.56, # Strong USD correlation
            'forex_moderate': 0.52            # Moderate correlation
        }
        
        # REALISTIC confluence multipliers (conservative)
        self.confluence_multipliers = {
            1: 1.0,    # Single signal (base rate)
            2: 1.05,   # Two signals (+5%)
            3: 1.12,   # Three signals (+12%) - starts to be interesting
            4: 1.20,   # Four signals (+20%) - good confluence
            5: 1.30,   # Five signals (+30%) - strong confluence (80%+ territory)
            6: 1.42,   # Six signals (+42%) - very strong (90%+ territory)
            7: 1.55,   # Seven signals (+55%) - exceptional (95%+ territory)
            8: 1.65,   # Eight+ signals - extremely rare
        }
        
        # Market condition adjustments
        self.market_condition_adjustments = {
            'high_volatility': 0.92,    # Reduce scores by 8% in high vol
            'low_volume': 0.95,         # Reduce scores by 5% in low volume
            'sideways_market': 0.90,    # Reduce scores by 10% in sideways
            'news_uncertainty': 0.88,   # Reduce scores by 12% during news
        }
        
        logger.info("CalibratedCryptometerEngine initialized with realistic pattern database")
    
    async def get_symbol_score(self, symbol: str) -> ComponentScore:
        """Get calibrated Cryptometer score for symbol"""
        try:
            # Collect data from multiple Cryptometer endpoints
            symbol_data = await self._collect_cryptometer_data(symbol)
            
            # Analyze patterns with realistic expectations
            analysis = self._analyze_realistic_patterns(symbol_data)
            
            # Create component score
            score = ComponentScore(
                component="cryptometer",
                score=analysis['final_score'],
                win_rate=analysis['final_win_rate'],
                direction=analysis['direction'],
                confidence=analysis['confidence'],
                patterns=analysis['pattern_signals'],
                analysis_details=analysis['detailed_analysis'],
                timestamp=datetime.now()
            )
            
            logger.info(f"Cryptometer score for {symbol}: {score.score:.1f}/100 ({score.win_rate*100:.1f}% win rate) - {score.direction}")
            return score
            
        except Exception as e:
            logger.error(f"Error getting Cryptometer score for {symbol}: {e}")
            # Return neutral score on error
            return ComponentScore(
                component="cryptometer",
                score=50.0,
                win_rate=0.5,
                direction="NEUTRAL",
                confidence=0.0,
                patterns=[],
                analysis_details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    async def _collect_cryptometer_data(self, symbol: str) -> Dict[str, Any]:
        """Collect data from Cryptometer API endpoints"""
        data = {"symbol": symbol, "data": {}}
        
        try:
            # AI Screener
            ai_data = await self._call_endpoint(f"ai_screener_v3/{symbol}-USDT")
            if ai_data and ai_data.get('success'):
                data['data']['ai_screener'] = ai_data
            
            # OHLCV Candles
            ohlcv_data = await self._call_endpoint(f"ohlcv_candles/{symbol}-USDT")
            if ohlcv_data and ohlcv_data.get('success'):
                data['data']['ohlcv_candles'] = ohlcv_data
            
            # Volume data
            volume_data = await self._call_endpoint(f"24h_trading_volume/{symbol}-USDT")
            if volume_data and volume_data.get('success'):
                data['data']['24h_trading_volume'] = volume_data
            
            # Long/Short ratio
            ls_data = await self._call_endpoint(f"ls_ratio/{symbol}-USDT")
            if ls_data and ls_data.get('success'):
                data['data']['ls_ratio'] = ls_data
            
            # Liquidation data
            liq_data = await self._call_endpoint(f"liquidation_data_v2/{symbol}-USDT")
            if liq_data and liq_data.get('success'):
                data['data']['liquidation_data_v2'] = liq_data
            
            # Trend indicator
            trend_data = await self._call_endpoint(f"trend_indicator_v3/{symbol}-USDT")
            if trend_data and trend_data.get('success'):
                data['data']['trend_indicator_v3'] = trend_data
            
        except Exception as e:
            logger.error(f"Error collecting Cryptometer data for {symbol}: {e}")
        
        return data
    
    async def _call_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Call Cryptometer API endpoint"""
        try:
            url = f"{self.base_url}/{endpoint}"
            params = {"api_key": self.api_key}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.debug(f"Error calling endpoint {endpoint}: {e}")
            return {}
    
    def _analyze_realistic_patterns(self, symbol_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns with realistic success rate expectations"""
        symbol = symbol_data['symbol']
        
        # Extract and analyze each data source with conservative approach
        pattern_signals = []
        detailed_analysis = {}
        
        # 1. AI Screener Analysis (conservative)
        ai_analysis = self._analyze_ai_screener_realistic(symbol_data.get('data', {}).get('ai_screener'))
        if ai_analysis['signal_strength'] > 0:
            pattern_signals.append(ai_analysis)
            detailed_analysis['ai_screener'] = ai_analysis
        
        # 2. OHLCV Pattern Analysis (conservative)
        ohlcv_analysis = self._analyze_ohlcv_realistic(symbol_data.get('data', {}).get('ohlcv_candles'))
        if ohlcv_analysis['signal_strength'] > 0:
            pattern_signals.append(ohlcv_analysis)
            detailed_analysis['ohlcv_patterns'] = ohlcv_analysis
        
        # 3. Volume Analysis (conservative)
        volume_analysis = self._analyze_volume_realistic(symbol_data.get('data', {}).get('24h_trading_volume'))
        if volume_analysis['signal_strength'] > 0:
            pattern_signals.append(volume_analysis)
            detailed_analysis['volume_patterns'] = volume_analysis
        
        # 4. Long/Short Ratio Analysis (conservative)
        ls_analysis = self._analyze_ls_ratio_realistic(symbol_data.get('data', {}).get('ls_ratio'))
        if ls_analysis['signal_strength'] > 0:
            pattern_signals.append(ls_analysis)
            detailed_analysis['ls_ratio_patterns'] = ls_analysis
        
        # 5. Liquidation Pattern Analysis (conservative)
        liq_analysis = self._analyze_liquidation_realistic(symbol_data.get('data', {}).get('liquidation_data_v2'))
        if liq_analysis['signal_strength'] > 0:
            pattern_signals.append(liq_analysis)
            detailed_analysis['liquidation_patterns'] = liq_analysis
        
        # 6. Trend Indicator Analysis (conservative)
        trend_analysis = self._analyze_trend_realistic(symbol_data.get('data', {}).get('trend_indicator_v3'))
        if trend_analysis['signal_strength'] > 0:
            pattern_signals.append(trend_analysis)
            detailed_analysis['trend_patterns'] = trend_analysis
        
        # Calculate realistic confluence and win rate
        confluence_analysis = self._calculate_realistic_confluence(pattern_signals)
        
        return {
            'symbol': symbol,
            'pattern_signals': pattern_signals,
            'detailed_analysis': detailed_analysis,
            'final_win_rate': confluence_analysis['final_win_rate'],
            'final_score': confluence_analysis['final_score'],
            'direction': confluence_analysis['direction'],
            'confidence': confluence_analysis['confidence'],
            'signal_count': len(pattern_signals),
        }
    
    def _analyze_ai_screener_realistic(self, ai_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze AI screener with realistic expectations"""
        if not ai_data or not ai_data.get('data'):
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        trades = ai_data['data']
        if not trades:
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        # Calculate historical success rate
        profitable_trades = [t for t in trades if float(t.get('pnl', 0)) > 0]
        success_rate = len(profitable_trades) / len(trades) if trades else 0
        
        # Calculate average PnL
        pnls = [float(t.get('pnl', 0)) for t in trades]
        avg_pnl = np.mean(pnls) if pnls else 0
        
        # Realistic signal strength and base win rate
        if success_rate >= 0.90 and avg_pnl > 2.0:  # Exceptional AI performance
            signal_strength = 0.8
            base_win_rate = self.pattern_success_rates['ai_screener_exceptional']
            pattern_type = 'ai_screener_exceptional'
        elif success_rate >= 0.80 and avg_pnl > 1.0:  # High AI performance
            signal_strength = 0.6
            base_win_rate = self.pattern_success_rates['ai_screener_high']
            pattern_type = 'ai_screener_high'
        elif success_rate >= 0.70 and avg_pnl > 0.5:  # Medium AI performance
            signal_strength = 0.4
            base_win_rate = self.pattern_success_rates['ai_screener_medium']
            pattern_type = 'ai_screener_medium'
        elif success_rate >= 0.60:  # Low AI performance
            signal_strength = 0.2
            base_win_rate = self.pattern_success_rates['ai_screener_low']
            pattern_type = 'ai_screener_low'
        else:
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        # Determine direction based on recent trades
        recent_pnl = np.mean(pnls[-5:]) if len(pnls) >= 5 else avg_pnl
        direction = 'LONG' if recent_pnl > 0 else 'SHORT'
        
        return {
            'signal_strength': signal_strength,
            'direction': direction,
            'win_rate': base_win_rate,
            'pattern_type': pattern_type,
            'success_rate': success_rate,
            'avg_pnl': avg_pnl,
            'trade_count': len(trades)
        }
    
    def _analyze_ohlcv_realistic(self, ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze OHLCV patterns with realistic expectations"""
        if not ohlcv_data or not ohlcv_data.get('data'):
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        candles = ohlcv_data['data']
        if len(candles) < 20:
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        # Extract OHLCV data
        closes = [float(c['close']) for c in candles[-20:]]
        volumes = [float(c['volume']) for c in candles[-20:]]
        highs = [float(c['high']) for c in candles[-20:]]
        lows = [float(c['low']) for c in candles[-20:]]
        
        # Calculate trend and breakout signals
        recent_trend = (closes[-1] - closes[0]) / closes[0] * 100
        volume_trend = (volumes[-1] - volumes[0]) / volumes[0] * 100 if volumes and volumes[0] > 0 else 0
        
        # Strong breakout pattern
        if abs(recent_trend) > 5 and volume_trend > 50:
            signal_strength = 0.7
            base_win_rate = self.pattern_success_rates['ohlcv_strong_breakout']
            pattern_type = 'ohlcv_strong_breakout'
        # Support/resistance bounce
        elif abs(recent_trend) > 2 and volume_trend > 20:
            signal_strength = 0.5
            base_win_rate = self.pattern_success_rates['ohlcv_support_resistance']
            pattern_type = 'ohlcv_support_resistance'
        # Moderate pattern
        elif abs(recent_trend) > 1:
            signal_strength = 0.3
            base_win_rate = self.pattern_success_rates['ohlcv_moderate_pattern']
            pattern_type = 'ohlcv_moderate_pattern'
        else:
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        direction = 'LONG' if recent_trend > 0 else 'SHORT'
        
        return {
            'signal_strength': signal_strength,
            'direction': direction,
            'win_rate': base_win_rate,
            'pattern_type': pattern_type,
            'recent_trend': recent_trend,
            'volume_trend': volume_trend
        }
    
    def _analyze_volume_realistic(self, volume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze volume patterns with realistic expectations"""
        if not volume_data or not volume_data.get('data'):
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        data = volume_data['data']
        volume_24h = float(data.get('volume_24h', 0))
        volume_avg = float(data.get('volume_avg_7d', volume_24h))
        
        if volume_avg == 0:
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        volume_ratio = volume_24h / volume_avg
        
        # Strong volume breakout
        if volume_ratio > 3.0:
            signal_strength = 0.6
            base_win_rate = self.pattern_success_rates['volume_breakout_strong']
            pattern_type = 'volume_breakout_strong'
        # Moderate volume increase
        elif volume_ratio > 1.5:
            signal_strength = 0.4
            base_win_rate = self.pattern_success_rates['volume_breakout_moderate']
            pattern_type = 'volume_breakout_moderate'
        # Volume divergence
        elif volume_ratio < 0.5:
            signal_strength = 0.2
            base_win_rate = self.pattern_success_rates['volume_divergence']
            pattern_type = 'volume_divergence'
        else:
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        # Direction based on volume context (simplified)
        direction = 'LONG' if volume_ratio > 1.0 else 'SHORT'
        
        return {
            'signal_strength': signal_strength,
            'direction': direction,
            'win_rate': base_win_rate,
            'pattern_type': pattern_type,
            'volume_ratio': volume_ratio
        }
    
    def _analyze_ls_ratio_realistic(self, ls_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Long/Short ratio with realistic expectations"""
        if not ls_data or not ls_data.get('data'):
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        ratio = float(ls_data['data'].get('ratio', 1.0))
        
        # Extreme ratios (contrarian signals)
        if ratio > 2.0 or ratio < 0.3:
            signal_strength = 0.6
            base_win_rate = self.pattern_success_rates['ls_ratio_extreme']
            pattern_type = 'ls_ratio_extreme'
        # High ratios
        elif ratio > 1.5 or ratio < 0.5:
            signal_strength = 0.4
            base_win_rate = self.pattern_success_rates['ls_ratio_high']
            pattern_type = 'ls_ratio_high'
        # Moderate ratios
        elif ratio > 1.2 or ratio < 0.8:
            signal_strength = 0.2
            base_win_rate = self.pattern_success_rates['ls_ratio_moderate']
            pattern_type = 'ls_ratio_moderate'
        else:
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        # Contrarian direction
        direction = 'SHORT' if ratio > 1.0 else 'LONG'
        
        return {
            'signal_strength': signal_strength,
            'direction': direction,
            'win_rate': base_win_rate,
            'pattern_type': pattern_type,
            'ls_ratio': ratio
        }
    
    def _analyze_liquidation_realistic(self, liq_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze liquidation patterns with realistic expectations"""
        if not liq_data or not liq_data.get('data'):
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        data = liq_data['data']
        liq_volume = float(data.get('liquidation_volume_24h', 0))
        
        # Massive liquidations
        if liq_volume > 50000000:  # >$50M
            signal_strength = 0.6
            base_win_rate = self.pattern_success_rates['liquidation_massive']
            pattern_type = 'liquidation_massive'
        # High liquidations
        elif liq_volume > 10000000:  # $10-50M
            signal_strength = 0.4
            base_win_rate = self.pattern_success_rates['liquidation_high']
            pattern_type = 'liquidation_high'
        # Moderate liquidations
        elif liq_volume > 1000000:  # $1-10M
            signal_strength = 0.2
            base_win_rate = self.pattern_success_rates['liquidation_moderate']
            pattern_type = 'liquidation_moderate'
        else:
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        # Direction based on liquidation type
        long_liq = float(data.get('long_liquidations', 0))
        short_liq = float(data.get('short_liquidations', 0))
        
        if long_liq > short_liq:
            direction = 'LONG'  # Bounce after long liquidations
        else:
            direction = 'SHORT'  # Continuation after short liquidations
        
        return {
            'signal_strength': signal_strength,
            'direction': direction,
            'win_rate': base_win_rate,
            'pattern_type': pattern_type,
            'liquidation_volume': liq_volume
        }
    
    def _analyze_trend_realistic(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trend indicators with realistic expectations"""
        if not trend_data or not trend_data.get('data'):
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        data = trend_data['data']
        trend_strength = float(data.get('trend_strength', 0))
        trend_direction = data.get('trend_direction', 'NEUTRAL')
        
        # Very strong trend
        if trend_strength > 0.8:
            signal_strength = 0.7
            base_win_rate = self.pattern_success_rates['trend_very_strong']
            pattern_type = 'trend_very_strong'
        # Strong trend
        elif trend_strength > 0.6:
            signal_strength = 0.5
            base_win_rate = self.pattern_success_rates['trend_strong']
            pattern_type = 'trend_strong'
        # Moderate trend
        elif trend_strength > 0.4:
            signal_strength = 0.3
            base_win_rate = self.pattern_success_rates['trend_moderate']
            pattern_type = 'trend_moderate'
        else:
            return {'signal_strength': 0, 'direction': 'NEUTRAL', 'win_rate': 0.5}
        
        direction = trend_direction if trend_direction in ['LONG', 'SHORT'] else 'NEUTRAL'
        
        return {
            'signal_strength': signal_strength,
            'direction': direction,
            'win_rate': base_win_rate,
            'pattern_type': pattern_type,
            'trend_strength': trend_strength
        }
    
    def _calculate_realistic_confluence(self, pattern_signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate realistic confluence and final win rate"""
        if not pattern_signals:
            return {
                'final_win_rate': 0.5,
                'final_score': 50.0,
                'direction': 'NEUTRAL',
                'confidence': 0.0
            }
        
        # Calculate base win rate from strongest patterns
        base_rates = [p['win_rate'] for p in pattern_signals]
        base_win_rate = max(base_rates)
        
        # Apply confluence multiplier
        signal_count = len(pattern_signals)
        confluence_multiplier = self.confluence_multipliers.get(signal_count, 1.0)
        
        # Calculate final win rate
        final_win_rate = min(base_win_rate * confluence_multiplier, 0.98)  # Cap at 98%
        
        # Convert to 0-100 scale
        final_score = final_win_rate * 100
        
        # Determine direction by majority vote
        directions = [p['direction'] for p in pattern_signals if p['direction'] != 'NEUTRAL']
        if directions:
            long_count = directions.count('LONG')
            short_count = directions.count('SHORT')
            if long_count > short_count:
                direction = 'LONG'
            elif short_count > long_count:
                direction = 'SHORT'
            else:
                direction = 'NEUTRAL'
        else:
            direction = 'NEUTRAL'
        
        # Calculate confidence based on signal strength consensus
        strengths = [p['signal_strength'] for p in pattern_signals]
        confidence = np.mean(strengths) if strengths else 0.0
        
        return {
            'final_win_rate': final_win_rate,
            'final_score': final_score,
            'direction': direction,
            'confidence': confidence,
            'signal_count': signal_count,
            'confluence_multiplier': confluence_multiplier
        }

class KingFisherScoringEngine:
    """
    KingFisher independent scoring engine
    Placeholder for liquidation analysis scoring
    """
    
    def __init__(self):
        logger.info("KingFisherScoringEngine initialized")
    
    async def get_symbol_score(self, symbol: str) -> ComponentScore:
        """Get KingFisher liquidation analysis score for symbol"""
        try:
            # TODO: Implement actual KingFisher analysis
            # For now, return placeholder score
            score = ComponentScore(
                component="kingfisher",
                score=75.0,  # Placeholder
                win_rate=0.75,
                direction="NEUTRAL",
                confidence=0.5,
                patterns=[{"type": "placeholder", "description": "KingFisher analysis pending"}],
                analysis_details={"status": "pending_implementation"},
                timestamp=datetime.now()
            )
            
            logger.info(f"KingFisher score for {symbol}: {score.score:.1f}/100 (placeholder)")
            return score
            
        except Exception as e:
            logger.error(f"Error getting KingFisher score for {symbol}: {e}")
            return ComponentScore(
                component="kingfisher",
                score=50.0,
                win_rate=0.5,
                direction="NEUTRAL",
                confidence=0.0,
                patterns=[],
                analysis_details={"error": str(e)},
                timestamp=datetime.now()
            )



class CalibratedScoringService:
    """
    Main calibrated scoring service providing independent component scores
    """
    
    def __init__(self):
        self.cryptometer_engine = CalibratedCryptometerEngine()
        self.kingfisher_engine = KingFisherScoringEngine()

        
        logger.info("CalibratedScoringService initialized with independent scoring engines")
    
    async def get_independent_scores(self, symbol: str) -> IndependentScores:
        """Get independent scores from all components"""
        logger.info(f"Getting independent scores for {symbol}")
        
        # Get scores from all components in parallel
        tasks = [
            self.cryptometer_engine.get_symbol_score(symbol),
            self.kingfisher_engine.get_symbol_score(symbol),

        ]
        
        try:
            cryptometer_score, kingfisher_score = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions and ensure proper types
            final_cryptometer_score: Optional[ComponentScore] = None
            final_kingfisher_score: Optional[ComponentScore] = None
            
            if isinstance(cryptometer_score, Exception):
                logger.error(f"Cryptometer scoring error: {cryptometer_score}")
            elif isinstance(cryptometer_score, ComponentScore):
                final_cryptometer_score = cryptometer_score
            
            if isinstance(kingfisher_score, Exception):
                logger.error(f"KingFisher scoring error: {kingfisher_score}")
            elif isinstance(kingfisher_score, ComponentScore):
                final_kingfisher_score = kingfisher_score
            
            scores = IndependentScores(
                kingfisher=final_kingfisher_score,
                cryptometer=final_cryptometer_score,
                symbol=symbol,
                timestamp=datetime.now()
            )
            
            logger.info(f"Independent scores for {symbol} completed")
            return scores
            
        except Exception as e:
            logger.error(f"Error getting independent scores for {symbol}: {e}")
            # Return empty scores on error
            return IndependentScores(
                kingfisher=None,
                cryptometer=None,
                symbol=symbol,
                timestamp=datetime.now()
            )
    
    def display_scores(self, scores: IndependentScores):
        """Display independent scores in a formatted way"""
        print(f"\n{'='*60}")
        print(f"🎯 INDEPENDENT COMPONENT SCORES - {scores.symbol}")
        print(f"{'='*60}")
        
        available_scores = scores.get_available_scores()
        
        if not available_scores:
            print("❌ No scores available")
            return
        
        for component, score in available_scores.items():
            print(f"\n🔹 {component.upper()}:")
            print(f"   Score: {score.score:.1f}/100")
            print(f"   Win Rate: {score.win_rate*100:.1f}%")
            print(f"   Direction: {score.direction}")
            print(f"   Confidence: {score.confidence:.2f}")
            print(f"   Patterns: {len(score.patterns)}")
            
            # Score interpretation
            if score.score >= 95:
                interpretation = "🟢 EXCEPTIONAL (95%+ - Royal Flush)"
            elif score.score >= 90:
                interpretation = "🟢 ALL-IN (90-94% - Very Rare)"
            elif score.score >= 80:
                interpretation = "🟢 TAKE TRADE (80-89% - Rare)"
            elif score.score >= 70:
                interpretation = "🟡 MODERATE (70-79%)"
            elif score.score >= 60:
                interpretation = "🟠 WEAK (60-69%)"
            else:
                interpretation = "🔴 AVOID (<60%)"
            
            print(f"   Status: {interpretation}")
        
        print(f"\n📊 AGGREGATION: Ready for flexible implementation")
        print(f"⏰ Analysis Time: {scores.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")