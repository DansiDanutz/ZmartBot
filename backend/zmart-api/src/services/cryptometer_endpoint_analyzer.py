#!/usr/bin/env python3
"""
Cryptometer Endpoint-by-Endpoint Analyzer
Analyzes each Cryptometer API endpoint individually and provides calibrated scoring
"""

import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import asyncio
import aiohttp
import numpy as np

from ..config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class EndpointScore:
    """Individual endpoint scoring result"""
    endpoint: str
    raw_data: Dict[str, Any]
    score: float  # 0-100 percentage
    confidence: float  # 0-1
    patterns: List[str]
    analysis: str
    success: bool
    error: Optional[str] = None

@dataclass
class CryptometerAnalysis:
    """Complete Cryptometer analysis with endpoint breakdown"""
    symbol: str
    endpoint_scores: List[EndpointScore]
    calibrated_score: float  # Final calibrated score 0-100%
    confidence: float
    direction: str
    analysis_summary: str
    timestamp: datetime

class CryptometerEndpointAnalyzer:
    """
    Analyzes each Cryptometer endpoint individually and calibrates the results
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.CRYPTOMETER_API_KEY
        self.base_url = "https://api.cryptometer.io"
        
        # All 17 Cryptometer endpoints with their analysis weights
        self.endpoints = {
            # Working endpoints (confirmed from documentation)
            'coinlist': {
                'url': 'coinlist/',
                'params': {'e': 'binance'},
                'weight': 2,
                'description': 'Available trading pairs validation'
            },
            'tickerlist': {
                'url': 'tickerlist/',
                'params': {'e': 'binance'},
                'weight': 5,
                'description': 'Real-time pricing overview'
            },
            'ticker': {
                'url': 'ticker/',
                'params': {'e': 'binance', 'market_pair': '{symbol}-USDT'},
                'weight': 8,
                'description': 'Detailed price action analysis'
            },
            'cryptocurrency_info': {
                'url': 'cryptocurrency-info/',
                'params': {'e': 'binance', 'filter': 'all'},
                'weight': 6,
                'description': 'Market fundamentals'
            },
            'coin_info': {
                'url': 'coininfo/',
                'params': {},
                'weight': 4,
                'description': 'Coin-specific metrics'
            },
            'tickerlist_pro': {
                'url': 'tickerlist-pro/',
                'params': {'e': 'binance'},
                'weight': 7,
                'description': 'Advanced market metrics'
            },
            # Fixed endpoints based on documentation
            'ai_screener': {
                'url': 'ai-screener/',
                'params': {'type': 'latest'},
                'weight': 15,
                'description': 'AI-powered trade analysis'
            },
            'ohlcv': {
                'url': 'ohlcv/',
                'params': {'e': 'binance', 'pair': '{symbol}-USDT', 'timeframe': '4h'},
                'weight': 10,
                'description': 'Candlestick pattern analysis'
            },
            '24h_trade_volume_v2': {
                'url': '24h-trade-volume-v2/',
                'params': {'pair': '{symbol}-USDT', 'e': 'binance'},
                'weight': 8,
                'description': 'Volume trend analysis'
            },
            'ls_ratio': {
                'url': 'ls-ratio/',
                'params': {'e': 'binance_futures', 'pair': '{symbol}-usdt', 'timeframe': '4h'},
                'weight': 12,
                'description': 'Long/Short sentiment analysis'
            },
            'liquidation_data_v2': {
                'url': 'liquidation-data-v2/',
                'params': {'symbol': '{symbol_lower}'},
                'weight': 11,
                'description': 'Liquidation pattern analysis'
            },
            'trend_indicator_v3': {
                'url': 'trend-indicator-v3/',
                'params': {},
                'weight': 9,
                'description': 'Multi-timeframe trend analysis'
            },
            'rapid_movements': {
                'url': 'rapid-movements/',
                'params': {},
                'weight': 6,
                'description': 'Momentum breakout analysis'
            },
            'forex_rates': {
                'url': 'forex-rates/',
                'params': {'source': 'USD'},
                'weight': 4,
                'description': 'USD correlation analysis'
            },
            'ai_screener_analysis': {
                'url': 'ai-screener-analysis/',
                'params': {'symbol': '{symbol}'},
                'weight': 3,
                'description': 'AI screener historical analysis'
            },
            'large_trades_activity': {
                'url': 'large-trades-activity/',
                'params': {'e': 'binance'},
                'weight': 5,
                'description': 'Large trades activity'
            },
            'xtrades': {
                'url': 'xtrades/',
                'params': {'symbol': '{symbol_lower}', 'e': 'binance'},
                'weight': 7,
                'description': 'Whale trades analysis'
            }
        }
        
        logger.info(f"CryptometerEndpointAnalyzer initialized with {len(self.endpoints)} endpoints")
    
    async def analyze_symbol_complete(self, symbol: str) -> CryptometerAnalysis:
        """
        Complete analysis of a symbol across all Cryptometer endpoints
        Returns calibrated percentage score
        """
        logger.info(f"Starting complete Cryptometer analysis for {symbol}")
        
        # Analyze each endpoint with rate limiting (1 second between calls)
        endpoint_scores = []
        
        async with aiohttp.ClientSession() as session:
            # Sequential execution with delays to avoid rate limiting
            for i, (endpoint_name, config) in enumerate(self.endpoints.items()):
                if i > 0:  # Add delay between requests (except first)
                    await asyncio.sleep(1.0)  # 1 second delay
                
                logger.info(f"Analyzing endpoint {i+1}/17: {endpoint_name}")
                result = await self._analyze_endpoint(session, symbol, endpoint_name, config)
                
                if isinstance(result, Exception):
                    logger.error(f"Endpoint {endpoint_name} analysis error: {result}")
                elif result:
                    endpoint_scores.append(result)

        
        # Calibrate final score using Agent
        calibrated_result = self._calibrate_scores(symbol, endpoint_scores)
        
        analysis = CryptometerAnalysis(
            symbol=symbol,
            endpoint_scores=endpoint_scores,
            calibrated_score=calibrated_result['score'],
            confidence=calibrated_result['confidence'],
            direction=calibrated_result['direction'],
            analysis_summary=calibrated_result['summary'],
            timestamp=datetime.now()
        )
        
        logger.info(f"Complete analysis for {symbol}: {analysis.calibrated_score:.1f}% ({analysis.direction})")
        return analysis
    
    async def _analyze_endpoint(self, session: aiohttp.ClientSession, symbol: str, endpoint_name: str, config: Dict) -> Optional[EndpointScore]:
        """Analyze individual endpoint and return score"""
        try:
            # Prepare URL and parameters
            url = f"{self.base_url}/{config['url']}"
            params = config['params'].copy()
            params['api_key'] = self.api_key
            
            # Replace symbol placeholders
            for key, value in params.items():
                if isinstance(value, str):
                    if '{symbol}' in value:
                        params[key] = value.replace('{symbol}', symbol)
                    elif '{symbol_lower}' in value:
                        params[key] = value.replace('{symbol_lower}', symbol.lower())
            
            # Make API call
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    raw_data = await response.json()
                    
                    # Handle different response formats (some endpoints return arrays)
                    if isinstance(raw_data, list):
                        # Convert list to dict format for consistent processing
                        data = {'data': raw_data, 'success': 'true'}
                    elif isinstance(raw_data, dict):
                        data = raw_data
                    else:
                        data = {'raw': raw_data, 'success': 'true'}
                    
                    # Check for API errors
                    if isinstance(data, dict) and data.get('success') == 'false':
                        logger.warning(f"Endpoint {endpoint_name} API error: {data.get('error', 'Unknown error')}")
                        return EndpointScore(
                            endpoint=endpoint_name,
                            raw_data=data,
                            score=0.0,
                            confidence=0.0,
                            patterns=[],
                            analysis=f"API error: {data.get('error', 'Unknown error')}",
                            success=False,
                            error=data.get('error', 'Unknown error')
                        )
                    
                    # Analyze the endpoint data
                    score_result = self._score_endpoint_data(endpoint_name, data, config, symbol)
                    
                    return EndpointScore(
                        endpoint=endpoint_name,
                        raw_data=data,
                        score=score_result['score'],
                        confidence=score_result['confidence'],
                        patterns=score_result['patterns'],
                        analysis=score_result['analysis'],
                        success=True
                    )
                else:
                    logger.warning(f"Endpoint {endpoint_name} returned status {response.status}")
                    return EndpointScore(
                        endpoint=endpoint_name,
                        raw_data={},
                        score=0.0,
                        confidence=0.0,
                        patterns=[],
                        analysis=f"API error: status {response.status}",
                        success=False,
                        error=f"HTTP {response.status}"
                    )
        
        except Exception as e:
            logger.error(f"Error analyzing endpoint {endpoint_name}: {e}")
            return EndpointScore(
                endpoint=endpoint_name,
                raw_data={},
                score=0.0,
                confidence=0.0,
                patterns=[],
                analysis=f"Error: {str(e)}",
                success=False,
                error=str(e)
            )
    
    def _score_endpoint_data(self, endpoint_name: str, data: Dict, config: Dict, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Score individual endpoint data based on its type"""
        
        # Map new endpoint names to scoring functions
        if endpoint_name == 'ai_screener':
            return self._score_ai_screener(data, symbol)
        elif endpoint_name == 'ohlcv':
            return self._score_ohlcv_candles(data)
        elif endpoint_name == '24h_trade_volume_v2':
            return self._score_volume_data(data)
        elif endpoint_name == 'ls_ratio':
            return self._score_ls_ratio(data)
        elif endpoint_name == 'liquidation_data_v2':
            return self._score_liquidation_data(data)
        elif endpoint_name == 'trend_indicator_v3':
            return self._score_trend_indicator(data)
        elif endpoint_name == 'ticker':
            return self._score_ticker_data(data)
        elif endpoint_name == 'rapid_movements':
            return self._score_rapid_movement(data)
        elif endpoint_name == 'forex_rates':
            return self._score_forex_correlation(data)
        elif endpoint_name == 'ai_screener_analysis':
            return self._score_social_sentiment(data)  # Similar analysis type
        elif endpoint_name == 'xtrades':
            return self._score_whale_activity(data)
        elif endpoint_name == 'large_trades_activity':
            return self._score_whale_activity(data)  # Similar to whale activity
        else:
            # Generic scoring for other endpoints
            return self._score_generic_endpoint(data, endpoint_name)
    
    def _score_ai_screener(self, data: Dict, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Score AI Screener endpoint"""
        if not data.get('data'):
            return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'No AI screener data'}
        
        # Handle different response formats
        ai_data = data['data']
        if isinstance(ai_data, list):
            if len(ai_data) == 0:
                return {'score': 50.0, 'confidence': 0.2, 'patterns': ['no_trades'], 'analysis': 'No recent AI trades'}
            trades = ai_data
        elif isinstance(ai_data, dict):
            # Check if it contains trades or signals
            if 'trades' in ai_data:
                trades = ai_data['trades']
            elif 'signals' in ai_data:
                trades = ai_data['signals']
            else:
                # Single trade/signal object
                trades = [ai_data]
        else:
            trades = [ai_data]
        
        if not trades or len(trades) == 0:
            return {'score': 50.0, 'confidence': 0.2, 'patterns': ['no_trades'], 'analysis': 'No recent AI trades'}
        
        # Filter trades for the specific symbol if provided
        symbol_trades = []
        all_trades = []
        
        for t in trades:
            if isinstance(t, dict):
                all_trades.append(t)
                # Check if this trade matches our symbol
                trade_symbol = t.get('symbol', '').upper()
                trade_pair = t.get('pair', '').upper()
                
                if symbol and (trade_symbol == symbol.upper() or 
                              f"{symbol.upper()}-USDT" in trade_pair or 
                              f"{symbol.upper()}USDT" in trade_pair):
                    symbol_trades.append(t)
        
        # Use symbol-specific trades if available, otherwise use all trades for general AI performance
        target_trades = symbol_trades if symbol_trades else all_trades[-20:]  # Last 20 trades for general performance
        
        if not target_trades:
            # No trades for this symbol, but AI is active - neutral score
            return {'score': 50.0, 'confidence': 0.3, 'patterns': ['no_symbol_trades'], 
                   'analysis': f'AI active ({len(all_trades)} trades), no {symbol or "target"} trades'}
        
        # Calculate success rate and PnL from available data
        profitable_count = 0
        total_pnl = 0
        valid_trades = 0
        open_trades = 0
        
        for t in target_trades:
            pnl = float(t.get('pnl', 0))
            status = t.get('status', '').lower()
            
            if status == 'open':
                open_trades += 1
                # For open trades, consider current unrealized PnL
                if pnl > 0:
                    profitable_count += 1
            elif status == 'closed':
                # Only count closed trades for final statistics
                if pnl > 0:
                    profitable_count += 1
                total_pnl += pnl
                valid_trades += 1
        
        # If we have no closed trades, use open trades for assessment
        if valid_trades == 0 and open_trades > 0:
            valid_trades = len(target_trades)
            total_pnl = sum(float(t.get('pnl', 0)) for t in target_trades)
        
        if valid_trades == 0:
            return {'score': 50.0, 'confidence': 0.2, 'patterns': ['no_valid_trades'], 'analysis': 'No valid AI trade data'}
        
        success_rate = profitable_count / valid_trades
        avg_pnl = total_pnl / valid_trades
        
        # Score based on performance (calibrated for realistic AI performance)
        if success_rate >= 0.80 and avg_pnl > 3.0:
            score = 85.0
            patterns = ['exceptional_ai_performance']
            analysis = f"Exceptional AI: {success_rate*100:.1f}% win, {avg_pnl:.1f}% avg PnL ({valid_trades} trades)"
        elif success_rate >= 0.70 and avg_pnl > 2.0:
            score = 75.0
            patterns = ['strong_ai_performance']
            analysis = f"Strong AI: {success_rate*100:.1f}% win, {avg_pnl:.1f}% avg PnL ({valid_trades} trades)"
        elif success_rate >= 0.60 and avg_pnl > 0.5:
            score = 65.0
            patterns = ['good_ai_performance']
            analysis = f"Good AI: {success_rate*100:.1f}% win, {avg_pnl:.1f}% avg PnL ({valid_trades} trades)"
        elif success_rate >= 0.50:
            score = 55.0
            patterns = ['moderate_ai_performance']
            analysis = f"Moderate AI: {success_rate*100:.1f}% win, {avg_pnl:.1f}% avg PnL ({valid_trades} trades)"
        else:
            score = 40.0
            patterns = ['weak_ai_performance']
            analysis = f"Weak AI: {success_rate*100:.1f}% win, {avg_pnl:.1f}% avg PnL ({valid_trades} trades)"
        
        # Add pattern for open trades
        if open_trades > 0:
            patterns.append(f'{open_trades}_open_trades')
        
        confidence = min(0.9, (success_rate * 0.6) + (min(valid_trades, 10) / 10 * 0.4))
        return {'score': score, 'confidence': confidence, 'patterns': patterns, 'analysis': analysis}
    
    def _score_ohlcv_candles(self, data: Dict) -> Dict[str, Any]:
        """Score OHLCV candles endpoint"""
        if not data.get('success') or not data.get('data'):
            return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'No OHLCV data'}
        
        candles = data['data']
        if len(candles) < 10:
            return {'score': 45.0, 'confidence': 0.2, 'patterns': ['insufficient_data'], 'analysis': 'Insufficient candle data'}
        
        # Analyze recent price action
        recent_candles = candles[-10:]
        closes = [float(c['close']) for c in recent_candles]
        volumes = [float(c['volume']) for c in recent_candles]
        
        # Calculate trend and volatility
        price_change = (closes[-1] - closes[0]) / closes[0] * 100
        volume_trend = (volumes[-1] - volumes[0]) / volumes[0] * 100 if volumes[0] > 0 else 0
        
        patterns = []
        if abs(price_change) > 5:
            patterns.append('strong_price_movement')
        if volume_trend > 50:
            patterns.append('volume_surge')
        if price_change > 2 and volume_trend > 20:
            patterns.append('bullish_breakout')
        elif price_change < -2 and volume_trend > 20:
            patterns.append('bearish_breakdown')
        
        # Score based on patterns
        if len(patterns) >= 2:
            score = 70.0
            confidence = 0.7
        elif len(patterns) == 1:
            score = 55.0
            confidence = 0.5
        else:
            score = 45.0
            confidence = 0.3
        
        analysis = f"Price: {price_change:+.2f}%, Volume: {volume_trend:+.1f}%, Patterns: {len(patterns)}"
        return {'score': score, 'confidence': confidence, 'patterns': patterns, 'analysis': analysis}
    
    def _score_volume_data(self, data: Dict) -> Dict[str, Any]:
        """Score 24h trading volume endpoint"""
        if not data.get('data'):
            return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'No volume data'}
        
        # Handle list or dict format
        volume_data = data['data']
        if isinstance(volume_data, list):
            if len(volume_data) == 0:
                return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'Empty volume data'}
            volume_info = volume_data[0]  # Use first item
        else:
            volume_info = volume_data
        
        # Extract volume data with multiple possible field names
        buy_volume = float(volume_info.get('buy', volume_info.get('buy_volume', 0)))
        sell_volume = float(volume_info.get('sell', volume_info.get('sell_volume', 0)))
        total_volume = buy_volume + sell_volume
        
        if total_volume == 0:
            return {'score': 40.0, 'confidence': 0.2, 'patterns': ['no_volume'], 'analysis': 'No volume data available'}
        
        # Calculate buy/sell ratio
        buy_ratio = buy_volume / total_volume if total_volume > 0 else 0.5
        
        patterns = []
        if buy_ratio > 0.7:
            patterns.append('strong_buying_pressure')
            score = 75.0
        elif buy_ratio > 0.6:
            patterns.append('buying_pressure')
            score = 65.0
        elif buy_ratio < 0.3:
            patterns.append('strong_selling_pressure')
            score = 35.0
        elif buy_ratio < 0.4:
            patterns.append('selling_pressure')
            score = 45.0
        else:
            patterns.append('balanced_volume')
            score = 55.0
        
        confidence = min(0.8, total_volume / 1000000 + 0.3)  # Volume-based confidence
        analysis = f"Buy: {buy_volume:.0f}, Sell: {sell_volume:.0f}, Ratio: {buy_ratio:.2f}"
        
        return {'score': score, 'confidence': confidence, 'patterns': patterns, 'analysis': analysis}
    
    def _score_ls_ratio(self, data: Dict) -> Dict[str, Any]:
        """Score Long/Short ratio endpoint"""
        if not data.get('data'):
            return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'No L/S ratio data'}
        
        # Handle list or dict format
        ls_data = data['data']
        if isinstance(ls_data, list):
            if len(ls_data) == 0:
                return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'Empty L/S ratio data'}
            ls_info = ls_data[0]  # Use first item
        else:
            ls_info = ls_data
        
        # Extract ratio with multiple possible field names
        ratio = float(ls_info.get('ratio', ls_info.get('ls_ratio', 1.0)))
        buy_pct = float(ls_info.get('buy', ls_info.get('long_percentage', 50.0)))
        sell_pct = float(ls_info.get('sell', ls_info.get('short_percentage', 50.0)))
        
        patterns = []
        # Contrarian analysis - extreme ratios suggest reversals
        if ratio > 3.0 or buy_pct > 75:
            patterns.append('extreme_long_bias')
            score = 75.0  # Contrarian short signal
            analysis = f"Extreme long bias (ratio: {ratio:.2f}, long: {buy_pct:.1f}%) - contrarian short opportunity"
        elif ratio < 0.3 or sell_pct > 75:
            patterns.append('extreme_short_bias')
            score = 75.0  # Contrarian long signal
            analysis = f"Extreme short bias (ratio: {ratio:.2f}, short: {sell_pct:.1f}%) - contrarian long opportunity"
        elif ratio > 2.0 or ratio < 0.5:
            patterns.append('high_sentiment_bias')
            score = 60.0
            analysis = f"High sentiment bias (ratio: {ratio:.2f}) - moderate contrarian signal"
        elif 0.8 < ratio < 1.2:
            patterns.append('balanced_sentiment')
            score = 45.0
            analysis = f"Balanced sentiment (ratio: {ratio:.2f}) - no clear bias"
        else:
            patterns.append('moderate_bias')
            score = 50.0
            analysis = f"Moderate bias (ratio: {ratio:.2f})"
        
        confidence = min(0.8, abs(ratio - 1.0) / 2.0 + 0.2)
        return {'score': score, 'confidence': confidence, 'patterns': patterns, 'analysis': analysis}
    
    def _score_liquidation_data(self, data: Dict) -> Dict[str, Any]:
        """Score liquidation data endpoint"""
        if not data.get('data'):
            return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'No liquidation data'}
        
        # Handle list or dict format
        liq_data = data['data']
        if isinstance(liq_data, list):
            if len(liq_data) == 0:
                return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'Empty liquidation data'}
            liq_info = liq_data[0]  # Use first item
        else:
            liq_info = liq_data
        
        # Extract liquidation data with multiple possible field names
        # Handle different exchange formats
        total_liq = 0
        long_liq = 0
        short_liq = 0
        
        # Check for different data formats
        if isinstance(liq_info, dict):
            # Format 1: Direct values
            total_liq = float(liq_info.get('liquidation_volume_24h', 0))
            long_liq = float(liq_info.get('long_liquidations', liq_info.get('longs', 0)))
            short_liq = float(liq_info.get('short_liquidations', liq_info.get('shorts', 0)))
            
            # Format 2: Exchange-specific format (binance_futures, etc.)
            if total_liq == 0:
                for exchange in ['binance_futures', 'bybit', 'deribit', 'bitmex']:
                    if exchange in liq_info:
                        exchange_data = liq_info[exchange]
                        long_liq += float(exchange_data.get('longs', 0))
                        short_liq += float(exchange_data.get('shorts', 0))
                total_liq = long_liq + short_liq
        
        patterns = []
        if total_liq > 100000000:  # >$100M
            patterns.append('massive_liquidations')
            score = 85.0
        elif total_liq > 50000000:  # $50-100M
            patterns.append('high_liquidations')
            score = 70.0
        elif total_liq > 10000000:  # $10-50M
            patterns.append('moderate_liquidations')
            score = 55.0
        elif total_liq > 1000000:  # $1-10M
            patterns.append('normal_liquidations')
            score = 50.0
        else:
            patterns.append('low_liquidations')
            score = 45.0
        
        # Direction bias
        if long_liq > short_liq * 2:
            patterns.append('long_squeeze')
            analysis = f"Long squeeze: ${total_liq/1e6:.1f}M liquidated (${long_liq/1e6:.1f}M longs)"
        elif short_liq > long_liq * 2:
            patterns.append('short_squeeze')
            analysis = f"Short squeeze: ${total_liq/1e6:.1f}M liquidated (${short_liq/1e6:.1f}M shorts)"
        else:
            analysis = f"Balanced liquidations: ${total_liq/1e6:.1f}M total"
        
        confidence = min(0.9, total_liq / 50000000 + 0.1)
        return {'score': score, 'confidence': confidence, 'patterns': patterns, 'analysis': analysis}
    
    def _score_trend_indicator(self, data: Dict) -> Dict[str, Any]:
        """Score trend indicator endpoint"""
        if not data.get('data'):
            return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'No trend data'}
        
        # Handle list or dict format
        trend_data = data['data']
        if isinstance(trend_data, list):
            if len(trend_data) == 0:
                return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'Empty trend data'}
            trend_info = trend_data[0]  # Use first item
        else:
            trend_info = trend_data
        
        # Extract trend data with multiple possible field names
        trend_score = float(trend_info.get('trend_score', trend_info.get('score', 50)))
        buy_pressure = float(trend_info.get('buy_pressure', trend_info.get('buy', 50)))
        sell_pressure = float(trend_info.get('sell_pressure', trend_info.get('sell', 50)))
        
        patterns = []
        trend_direction = "neutral"
        if trend_score > 70:
            patterns.append('strong_uptrend')
            trend_direction = "strong uptrend"
            score = 75.0
        elif trend_score > 60:
            patterns.append('uptrend')
            trend_direction = "uptrend"
            score = 65.0
        elif trend_score < 30:
            patterns.append('strong_downtrend')
            trend_direction = "strong downtrend"
            score = 75.0  # High volatility opportunity
        elif trend_score < 40:
            patterns.append('downtrend')
            trend_direction = "downtrend"
            score = 60.0
        else:
            patterns.append('sideways')
            trend_direction = "sideways"
            score = 45.0
        
        # Factor in buy/sell pressure
        pressure_diff = abs(buy_pressure - sell_pressure)
        if pressure_diff > 20:
            patterns.append('strong_pressure_imbalance')
            score += 5
        
        trend_strength = abs(trend_score - 50) / 50
        confidence = max(0.3, trend_strength)
        analysis = f"{trend_direction} trend (score: {trend_score:.1f}, buy: {buy_pressure:.1f}, sell: {sell_pressure:.1f})"
        
        return {'score': score, 'confidence': confidence, 'patterns': patterns, 'analysis': analysis}
    
    def _score_ticker_data(self, data: Dict) -> Dict[str, Any]:
        """Score ticker endpoint"""
        if not data.get('data'):
            return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'No ticker data'}
        
        # Handle list response format
        ticker_data = data['data']
        if isinstance(ticker_data, list) and len(ticker_data) > 0:
            ticker = ticker_data[0]  # Use first ticker
        elif isinstance(ticker_data, dict):
            ticker = ticker_data
        else:
            return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'Invalid ticker data format'}
        
        # Extract price change and volume with multiple possible field names
        price_change_24h = float(ticker.get('change_24h', ticker.get('price_change_24h', 0)))
        volume_24h = float(ticker.get('volume_24', ticker.get('volume_24h', 0)))
        
        patterns = []
        if abs(price_change_24h) > 10:
            patterns.append('high_volatility')
            score = 70.0
        elif abs(price_change_24h) > 5:
            patterns.append('moderate_volatility')
            score = 60.0
        else:
            patterns.append('low_volatility')
            score = 45.0
        
        if volume_24h > 1000000:  # >$1M volume
            patterns.append('high_volume')
            score += 10
        
        confidence = min(0.7, abs(price_change_24h) / 20 + 0.3)
        analysis = f"24h change: {price_change_24h:+.2f}%, Volume: ${volume_24h/1e6:.1f}M"
        
        return {'score': min(score, 100.0), 'confidence': confidence, 'patterns': patterns, 'analysis': analysis}
    
    def _score_generic_endpoint(self, data: Dict, endpoint_name: str) -> Dict[str, Any]:
        """Generic scoring for endpoints without specific analysis"""
        # Check if we have any data (more flexible than just checking 'success')
        has_data = False
        if data.get('data'):
            has_data = True
        elif isinstance(data, dict) and len(data) > 1:  # More than just success field
            has_data = True
        elif data.get('success') == 'true':
            has_data = True
        
        if has_data:
            score = 50.0
            confidence = 0.3
            patterns = ['data_available']
            analysis = f"{endpoint_name}: Data available"
        else:
            score = 0.0
            confidence = 0.0
            patterns = ['no_data']
            analysis = f"{endpoint_name}: No data available"
        
        return {'score': score, 'confidence': confidence, 'patterns': patterns, 'analysis': analysis}
    
    def _score_rapid_movement(self, data: Dict) -> Dict[str, Any]:
        """Score rapid movement endpoint"""
        if not data.get('data'):
            return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'No rapid movement data'}
        
        # Handle list or dict format
        movements_data = data['data']
        if isinstance(movements_data, list):
            movements = movements_data
        elif isinstance(movements_data, dict) and 'movements' in movements_data:
            movements = movements_data['movements']
        else:
            movements = [movements_data]  # Single movement object
        
        if not movements or len(movements) == 0:
            return {'score': 30.0, 'confidence': 0.2, 'patterns': ['no_movements'], 'analysis': 'No rapid movements detected'}
        
        # Analyze recent movements
        total_change = 0
        count = 0
        for m in movements[-5:]:  # Last 5 movements
            if isinstance(m, dict):
                change = float(m.get('change_detected', m.get('change', m.get('price_change', 0))))
                total_change += change
                count += 1
        
        avg_change = total_change / max(1, count)
        
        patterns = []
        if avg_change > 15:
            patterns.append('massive_pump')
            score = 85.0
        elif avg_change > 10:
            patterns.append('strong_pump')
            score = 70.0
        elif avg_change > 5:
            patterns.append('moderate_pump')
            score = 60.0
        elif avg_change < -15:
            patterns.append('massive_dump')
            score = 85.0
        elif avg_change < -10:
            patterns.append('strong_dump')
            score = 70.0
        elif avg_change < -5:
            patterns.append('moderate_dump')
            score = 60.0
        else:
            patterns.append('stable_movement')
            score = 45.0
        
        confidence = min(0.9, abs(avg_change) / 20 + 0.3)
        analysis = f"Average movement: {avg_change:+.2f}% ({len(movements)} movements)"
        
        return {'score': score, 'confidence': confidence, 'patterns': patterns, 'analysis': analysis}
    
    def _score_forex_correlation(self, data: Dict) -> Dict[str, Any]:
        """Score forex correlation endpoint"""
        if not data.get('data'):
            return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'No forex data'}
        
        # Handle list or dict format
        forex_data = data['data']
        if isinstance(forex_data, list):
            if len(forex_data) == 0:
                return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'Empty forex data'}
            forex_info = forex_data[0]  # Use first item
        else:
            forex_info = forex_data
        
        # Extract forex data with multiple possible field names
        # For forex rates endpoint, we look for USD rate or calculate USD strength
        usd_rate = float(forex_info.get('rate', forex_info.get('usd_rate', 1.0)))
        symbol = forex_info.get('symbol', 'USD')
        
        # Calculate relative USD strength (simplified)
        if symbol == 'USD':
            usd_strength = 100.0  # Base value
        else:
            # For other currencies, inverse relationship
            usd_strength = 100.0 / max(0.01, usd_rate) if usd_rate != 0 else 100.0
        
        patterns = []
        # USD strength affects crypto inversely
        if usd_strength > 105 or (symbol != 'USD' and usd_rate < 0.95):
            patterns.append('strong_usd')
            score = 35.0  # Bearish for crypto
        elif usd_strength < 95 or (symbol != 'USD' and usd_rate > 1.05):
            patterns.append('weak_usd')
            score = 65.0  # Bullish for crypto
        else:
            patterns.append('neutral_usd')
            score = 50.0
        
        # Base confidence on data availability
        confidence = 0.5 if symbol == 'USD' else 0.4
        
        analysis = f"USD analysis: {symbol}={usd_rate:.4f}, strength: {usd_strength:.1f}"
        return {'score': score, 'confidence': confidence, 'patterns': patterns, 'analysis': analysis}
    
    def _score_social_sentiment(self, data: Dict) -> Dict[str, Any]:
        """Score social sentiment endpoint"""
        if not data.get('data'):
            return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'No social sentiment data'}
        
        # Handle list or dict format
        sentiment_data = data['data']
        if isinstance(sentiment_data, list):
            if len(sentiment_data) == 0:
                return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'Empty sentiment data'}
            sentiment_info = sentiment_data[0]  # Use first item
        else:
            sentiment_info = sentiment_data
        
        # Extract sentiment with multiple possible field names
        sentiment = float(sentiment_info.get('sentiment_score', sentiment_info.get('sentiment', sentiment_info.get('score', 0))))
        
        if sentiment > 0.7:
            score = 70.0
            patterns = ['very_positive_sentiment']
        elif sentiment > 0.3:
            score = 60.0
            patterns = ['positive_sentiment']
        elif sentiment < -0.3:
            score = 40.0
            patterns = ['negative_sentiment']
        else:
            score = 50.0
            patterns = ['neutral_sentiment']
        
        analysis = f"Social sentiment: {sentiment:.2f}"
        return {'score': score, 'confidence': abs(sentiment), 'patterns': patterns, 'analysis': analysis}
    
    def _score_whale_activity(self, data: Dict) -> Dict[str, Any]:
        """Score whale activity endpoint"""
        if not data.get('data'):
            return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'No whale activity data'}
        
        # Handle list or dict format
        whale_data = data['data']
        if isinstance(whale_data, list):
            if len(whale_data) == 0:
                return {'score': 0.0, 'confidence': 0.0, 'patterns': [], 'analysis': 'Empty whale activity data'}
            
            # Calculate from list of whale trades
            total_whale_volume = 0
            trade_count = 0
            for w in whale_data[-10:]:  # Last 10 trades
                if isinstance(w, dict):
                    trade_value = float(w.get('total', w.get('value', w.get('size', 0))))
                    total_whale_volume += trade_value
                    trade_count += 1
            
            avg_trade_size = total_whale_volume / max(1, trade_count)
        else:
            # Single object format
            total_whale_volume = float(whale_data.get('total_volume_24h', whale_data.get('volume', 0)))
            avg_trade_size = float(whale_data.get('avg_trade_size', whale_data.get('average_size', total_whale_volume)))
        
        patterns = []
        if total_whale_volume > 100000000:  # >$100M
            patterns.append('massive_whale_activity')
            score = 80.0
        elif total_whale_volume > 50000000:  # $50-100M
            patterns.append('high_whale_activity')
            score = 70.0
        elif total_whale_volume > 10000000:  # $10-50M
            patterns.append('moderate_whale_activity')
            score = 60.0
        elif total_whale_volume > 1000000:  # $1-10M
            patterns.append('normal_whale_activity')
            score = 50.0
        else:
            patterns.append('low_whale_activity')
            score = 45.0
        
        # Large individual trades
        if avg_trade_size > 10000000:  # >$10M per trade
            patterns.append('mega_whale_trades')
            score += 10
        elif avg_trade_size > 1000000:  # >$1M per trade
            patterns.append('large_whale_trades')
            score += 5
        
        confidence = min(0.8, total_whale_volume / 100000000 + 0.2)
        analysis = f"Whale volume: ${total_whale_volume/1e6:.1f}M, Avg trade: ${avg_trade_size/1e6:.1f}M"
        
        return {'score': min(score, 100.0), 'confidence': confidence, 'patterns': patterns, 'analysis': analysis}
    
    def _calibrate_scores(self, symbol: str, endpoint_scores: List[EndpointScore]) -> Dict[str, Any]:
        """
        Calibration Agent: Combines all endpoint scores into final calibrated percentage
        """
        if not endpoint_scores:
            return {
                'score': 0.0,
                'confidence': 0.0,
                'direction': 'NEUTRAL',
                'summary': 'No endpoint data available'
            }
        
        # STEP 1: Calculate total possible weight and successful weight
        total_possible_weight = sum(config['weight'] for config in self.endpoints.values())  # Should be 100
        successful_weight = 0.0
        successful_endpoints = 0
        
        # First pass: identify successful endpoints and their original weights
        successful_endpoint_data = []
        for endpoint_score in endpoint_scores:
            if endpoint_score.success:
                endpoint_config = self.endpoints.get(endpoint_score.endpoint, {'weight': 1})
                original_weight = endpoint_config['weight']
                successful_weight += original_weight
                successful_endpoints += 1
                successful_endpoint_data.append({
                    'score': endpoint_score.score,
                    'original_weight': original_weight,
                    'patterns': endpoint_score.patterns,
                    'endpoint': endpoint_score.endpoint
                })
        
        # STEP 2: Dynamically redistribute weights to maintain 100 total
        # Calculate redistribution factor to normalize successful weights to 100
        if successful_weight > 0:
            weight_redistribution_factor = 100.0 / successful_weight
            logger.info(f"Weight redistribution: {successful_weight:.1f} -> 100.0 (factor: {weight_redistribution_factor:.3f})")
        else:
            weight_redistribution_factor = 1.0
        
        # STEP 3: Calculate weighted average with redistributed weights
        total_weighted_score = 0.0
        total_redistributed_weight = 0.0
        
        # Direction analysis
        long_signals = 0
        short_signals = 0
        
        for endpoint_data in successful_endpoint_data:
            # Apply redistribution factor to maintain 100 total weight
            redistributed_weight = endpoint_data['original_weight'] * weight_redistribution_factor
            
            total_weighted_score += endpoint_data['score'] * redistributed_weight
            total_redistributed_weight += redistributed_weight
            
            # Analyze patterns for direction
            for pattern in endpoint_data['patterns']:
                if any(x in pattern for x in ['bullish', 'long', 'positive', 'strong_trend']):
                    long_signals += 1
                elif any(x in pattern for x in ['bearish', 'short', 'negative', 'contrarian']):
                    short_signals += 1
        
        if total_redistributed_weight == 0:
            return {
                'score': 0.0,
                'confidence': 0.0,
                'direction': 'NEUTRAL',
                'summary': 'No successful endpoint analysis'
            }
        
        # Base calibrated score (should now be properly weighted to 100)
        base_score = total_weighted_score / total_redistributed_weight
        
        # Apply calibration adjustments
        calibrated_score = self._apply_calibration_curve(base_score, successful_endpoints, len(self.endpoints))
        
        # Determine direction
        if long_signals > short_signals + 2:
            direction = 'LONG'
        elif short_signals > long_signals + 2:
            direction = 'SHORT'
        else:
            direction = 'NEUTRAL'
        
        # Calculate overall confidence
        avg_confidence = np.mean([es.confidence for es in endpoint_scores if es.success])
        data_coverage = successful_endpoints / len(self.endpoints)
        overall_confidence = (avg_confidence + data_coverage) / 2
        
        # Generate summary
        summary = self._generate_analysis_summary(symbol, endpoint_scores, calibrated_score, direction)
        
        return {
            'score': calibrated_score,
            'confidence': overall_confidence,
            'direction': direction,
            'summary': summary
        }
    
    def _apply_calibration_curve(self, base_score: float, successful_endpoints: int, total_endpoints: int) -> float:
        """
        Apply calibration curve to ensure realistic score distribution
        Most scores should be 40-70%, with 80%+ being rare
        """
        # Data coverage penalty
        coverage_ratio = successful_endpoints / total_endpoints
        coverage_penalty = (1.0 - coverage_ratio) * 20  # Up to 20 point penalty
        
        # Apply sigmoid-like curve to compress high scores
        adjusted_score = base_score - coverage_penalty
        
        # Calibration curve: compress scores above 70
        if adjusted_score > 70:
            excess = adjusted_score - 70
            # Compress excess by 50%
            calibrated_score = 70 + (excess * 0.5)
        else:
            calibrated_score = adjusted_score
        
        # Ensure bounds
        return max(0.0, min(100.0, calibrated_score))
    
    def _generate_analysis_summary(self, symbol: str, endpoint_scores: List[EndpointScore], score: float, direction: str) -> str:
        """Generate human-readable analysis summary"""
        successful = len([es for es in endpoint_scores if es.success])
        total = len(endpoint_scores)
        
        # Key patterns
        all_patterns = []
        for es in endpoint_scores:
            all_patterns.extend(es.patterns)
        
        pattern_counts = {}
        for pattern in all_patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        top_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        summary = f"{symbol} Analysis: {score:.1f}% score from {successful}/{total} endpoints. "
        summary += f"Direction: {direction}. "
        
        if top_patterns:
            pattern_text = ", ".join([f"{p[0]} ({p[1]}x)" for p in top_patterns])
            summary += f"Key patterns: {pattern_text}."
        
        return summary