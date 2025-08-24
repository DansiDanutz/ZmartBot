#!/usr/bin/env python3
"""
Complete Cryptometer AI Trading System - Multi-Timeframe Agent with AI Win Rate Prediction
Based on Cryptometer_Complete_AI_System from Documentation folder

This system provides:
- Multi-timeframe analysis (SHORT/MEDIUM/LONG)
- AI-powered decision making
- Realistic win-rate scoring
- Dynamic pattern recognition
- Professional-grade trading signals
- AI-Powered Win Rate Prediction from 17 endpoints
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
try:
    import openai
except ImportError:
    openai = None
import os
import time
import logging
import asyncio
from typing import Dict, List, Any, Tuple, Optional
import statistics

# Import enhanced rate limiter, quota manager, and price movement trigger
from src.utils.enhanced_rate_limiter import global_rate_limiter, rate_limited_request
from src.utils.cryptometer_quota_manager import (
    can_make_cryptometer_request,
    record_cryptometer_request,
    get_cryptometer_quota_status
)
from src.utils.price_movement_trigger import (
    should_trigger_cryptometer_analysis,
    get_price_trigger_status
)

# AI Win Rate Predictor temporarily disabled - using unified scoring system
# from src.agents.scoring.ai_win_rate_predictor import (
#     ai_predictor,
#     AIModel,
#     AIWinRatePrediction,
#     MultiTimeframeAIPrediction
# )

# Load settings for env-based configuration
from src.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if openai is None:
    logger.warning("OpenAI package not available. AI features will be disabled.")

class MultiTimeframeAIAgent:
    """
    AI Agent for Multi-Timeframe Trading Analysis
    Analyzes SHORT (24-48h), MEDIUM (1 week), LONG (1 month+) simultaneously
    """
    
    def __init__(self):
        if openai is not None:
            try:
                self.client = openai.OpenAI()
            except Exception:
                # If OpenAI fails to initialize (no API key), continue without it
                self.client = None
        else:
            self.client = None
        
        # Timeframe-specific pattern success rates
        self.timeframe_patterns = {
            # SHORT TERM (24-48h) - Scalping/Day Trading
            'short': {
                'ai_screener_momentum': 0.85,      # AI momentum signals
                'volume_spike_breakout': 0.82,     # Volume spike breakouts
                'rapid_movement_follow': 0.78,     # Rapid movement follow-through
                'liquidation_bounce': 0.75,        # Liquidation bounces
                'ohlcv_intraday_pattern': 0.72,    # Intraday patterns
                'ls_ratio_extreme_short': 0.70,    # Extreme sentiment reversals
                'trend_acceleration': 0.68,        # Trend acceleration
                'support_resistance_touch': 0.65   # S/R level touches
            },
            
            # MEDIUM TERM (1 week) - Swing Trading  
            'medium': {
                'ai_screener_swing': 0.75,         # AI swing signals
                'trend_continuation': 0.72,        # Trend continuation
                'volume_accumulation': 0.70,       # Volume accumulation
                'ohlcv_swing_pattern': 0.68,       # Swing patterns
                'ls_ratio_moderate': 0.65,         # Moderate sentiment
                'liquidation_reversal': 0.63,      # Liquidation reversals
                'breakout_confirmation': 0.60,     # Breakout confirmations
                'fibonacci_levels': 0.58           # Fibonacci retracements
            },
            
            # LONG TERM (1 month+) - Position Trading
            'long': {
                'ai_screener_position': 0.65,      # AI position signals
                'trend_major': 0.62,               # Major trend analysis
                'volume_institutional': 0.60,      # Institutional volume
                'ohlcv_monthly_pattern': 0.58,     # Monthly patterns
                'fundamental_confluence': 0.55,    # Fundamental analysis
                'market_cycle': 0.53,              # Market cycle position
                'macro_correlation': 0.50,         # Macro correlations
                'long_term_support': 0.48          # Long-term S/R levels
            }
        }
        
        # Timeframe-specific confluence multipliers
        self.timeframe_multipliers = {
            'short': {
                1: 1.0, 2: 1.15, 3: 1.30, 4: 1.45, 5: 1.60, 6: 1.75, 7: 1.90, 8: 2.0
            },
            'medium': {
                1: 1.0, 2: 1.10, 3: 1.22, 4: 1.35, 5: 1.50, 6: 1.65, 7: 1.80, 8: 1.95
            },
            'long': {
                1: 1.0, 2: 1.08, 3: 1.18, 4: 1.28, 5: 1.40, 6: 1.52, 7: 1.65, 8: 1.78
            }
        }
        
        # Market condition adjustments per timeframe
        self.market_adjustments = {
            'short': {
                'high_volatility': 1.05,    # Short-term benefits from volatility
                'low_volume': 0.90,         # Needs volume for scalping
                'news_events': 1.10,        # News creates short-term opportunities
                'market_hours': 1.00        # Always active in crypto
            },
            'medium': {
                'trending_market': 1.08,    # Swing trading loves trends
                'sideways_market': 0.85,    # Harder to swing trade sideways
                'volume_consistent': 1.05,  # Consistent volume helps swings
                'news_impact': 0.95        # News can disrupt swings
            },
            'long': {
                'bull_market': 1.12,        # Position trading loves bull markets
                'bear_market': 0.75,        # Harder to position trade in bears
                'institutional_flow': 1.15, # Institutional money helps
                'macro_stability': 1.08     # Macro stability helps long-term
            }
        }
    
    def analyze_multi_timeframe(self, symbol_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze symbol across all 3 timeframes simultaneously"""
        try:
            symbol = symbol_data.get('symbol', 'UNKNOWN')
            
            # Analyze each timeframe
            short_analysis = self._analyze_short_term(symbol_data)
            medium_analysis = self._analyze_medium_term(symbol_data)
            long_analysis = self._analyze_long_term(symbol_data)
            
            # AI Agent decision making
            ai_recommendation = self._ai_agent_decision(symbol, short_analysis, medium_analysis, long_analysis)
            
            return {
                'symbol': symbol,
                'short_term': short_analysis,
                'medium_term': medium_analysis,
                'long_term': long_analysis,
                'ai_recommendation': ai_recommendation,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe analysis: {e}")
            return {
                'symbol': symbol_data.get('symbol', 'UNKNOWN'),
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _analyze_short_term(self, symbol_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze SHORT term (24-48h) - Scalping/Day Trading patterns"""
        try:
            patterns = []
            timeframe = 'short'
            
            # AI Screener momentum analysis
            ai_data = symbol_data.get('ai_screener', {})
            if ai_data and ai_data.get('success'):
                ai_score = ai_data.get('data', {}).get('score', 0)
                if ai_score > 80:
                    patterns.append({
                        'type': 'ai_screener_momentum',
                        'confidence': 0.85,
                        'description': f'AI momentum signal: {ai_score}%'
                    })
            
            # Volume spike analysis
            volume_data = symbol_data.get('volume_analysis', {})
            if volume_data and volume_data.get('success'):
                volume_change = volume_data.get('data', {}).get('volume_change_24h', 0)
                if volume_change > 50:  # 50% volume spike
                    patterns.append({
                        'type': 'volume_spike_breakout',
                        'confidence': 0.82,
                        'description': f'Volume spike: +{volume_change:.1f}%'
                    })
            
            # Rapid movement analysis
            rapid_data = symbol_data.get('rapid_movements', {})
            if rapid_data and rapid_data.get('success'):
                movements = rapid_data.get('data', [])
                if len(movements) > 0:
                    patterns.append({
                        'type': 'rapid_movement_follow',
                        'confidence': 0.78,
                        'description': f'Rapid movements detected: {len(movements)}'
                    })
            
            # Liquidation analysis
            liq_data = symbol_data.get('liquidation_data', {})
            if liq_data and liq_data.get('success'):
                liquidations = liq_data.get('data', {}).get('liquidations_24h', 0)
                if liquidations > 1000000:  # $1M+ liquidations
                    patterns.append({
                        'type': 'liquidation_bounce',
                        'confidence': 0.75,
                        'description': f'Liquidation bounce: ${liquidations/1000000:.1f}M'
                    })
            
            # Calculate confluence and score
            confluence = self._calculate_timeframe_confluence(patterns, timeframe)
            
            return {
                'timeframe': 'SHORT (24-48h)',
                'patterns': patterns,
                'confluence': confluence,
                'score': confluence.get('final_score', 0),
                'signal': confluence.get('signal', 'NEUTRAL'),
                'trade_type': 'SCALP_TRADE'
            }
            
        except Exception as e:
            logger.error(f"Error in short-term analysis: {e}")
            return {
                'timeframe': 'SHORT (24-48h)',
                'patterns': [],
                'confluence': {'final_score': 0, 'signal': 'NEUTRAL'},
                'score': 0,
                'signal': 'NEUTRAL',
                'trade_type': 'SCALP_TRADE',
                'error': str(e)
            }
    
    def _analyze_medium_term(self, symbol_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze MEDIUM term (1 week) - Swing Trading patterns"""
        try:
            patterns = []
            timeframe = 'medium'
            
            # AI Screener swing analysis
            ai_data = symbol_data.get('ai_screener', {})
            if ai_data and ai_data.get('success'):
                ai_score = ai_data.get('data', {}).get('score', 0)
                if 70 < ai_score <= 85:
                    patterns.append({
                        'type': 'ai_screener_swing',
                        'confidence': 0.75,
                        'description': f'AI swing signal: {ai_score}%'
                    })
            
            # Trend continuation analysis
            trend_data = symbol_data.get('trend_indicators', {})
            if trend_data and trend_data.get('success'):
                trend_strength = trend_data.get('data', {}).get('trend_strength', 0)
                if trend_strength > 0.6:
                    patterns.append({
                        'type': 'trend_continuation',
                        'confidence': 0.72,
                        'description': f'Trend continuation: {trend_strength:.2f}'
                    })
            
            # Volume accumulation analysis
            volume_data = symbol_data.get('volume_analysis', {})
            if volume_data and volume_data.get('success'):
                volume_trend = volume_data.get('data', {}).get('volume_trend_7d', 0)
                if volume_trend > 20:  # 20% volume increase over 7 days
                    patterns.append({
                        'type': 'volume_accumulation',
                        'confidence': 0.70,
                        'description': f'Volume accumulation: +{volume_trend:.1f}%'
                    })
            
            # Long/Short ratio analysis
            ls_data = symbol_data.get('ls_ratio', {})
            if ls_data and ls_data.get('success'):
                ls_ratio = ls_data.get('data', {}).get('ratio', 1.0)
                if 0.8 < ls_ratio < 1.2:  # Moderate sentiment
                    patterns.append({
                        'type': 'ls_ratio_moderate',
                        'confidence': 0.65,
                        'description': f'Moderate sentiment: {ls_ratio:.2f}'
                    })
            
            # Calculate confluence and score
            confluence = self._calculate_timeframe_confluence(patterns, timeframe)
            
            return {
                'timeframe': 'MEDIUM (1 week)',
                'patterns': patterns,
                'confluence': confluence,
                'score': confluence.get('final_score', 0),
                'signal': confluence.get('signal', 'NEUTRAL'),
                'trade_type': 'SWING_TRADE'
            }
            
        except Exception as e:
            logger.error(f"Error in medium-term analysis: {e}")
            return {
                'timeframe': 'MEDIUM (1 week)',
                'patterns': [],
                'confluence': {'final_score': 0, 'signal': 'NEUTRAL'},
                'score': 0,
                'signal': 'NEUTRAL',
                'trade_type': 'SWING_TRADE',
                'error': str(e)
            }
    
    def _analyze_long_term(self, symbol_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze LONG term (1 month+) - Position Trading patterns"""
        try:
            patterns = []
            timeframe = 'long'
            
            # AI Screener position analysis
            ai_data = symbol_data.get('ai_screener', {})
            if ai_data and ai_data.get('success'):
                ai_score = ai_data.get('data', {}).get('score', 0)
                if ai_score <= 70:  # Lower scores for long-term
                    patterns.append({
                        'type': 'ai_screener_position',
                        'confidence': 0.65,
                        'description': f'AI position signal: {ai_score}%'
                    })
            
            # Major trend analysis
            trend_data = symbol_data.get('trend_indicators', {})
            if trend_data and trend_data.get('success'):
                major_trend = trend_data.get('data', {}).get('major_trend', 0)
                if abs(major_trend) > 0.4:
                    patterns.append({
                        'type': 'trend_major',
                        'confidence': 0.62,
                        'description': f'Major trend: {major_trend:.2f}'
                    })
            
            # Institutional volume analysis
            volume_data = symbol_data.get('volume_analysis', {})
            if volume_data and volume_data.get('success'):
                institutional_volume = volume_data.get('data', {}).get('institutional_volume', 0)
                if institutional_volume > 1000000:  # $1M+ institutional volume
                    patterns.append({
                        'type': 'volume_institutional',
                        'confidence': 0.60,
                        'description': f'Institutional volume: ${institutional_volume/1000000:.1f}M'
                    })
            
            # Market cycle analysis
            market_data = symbol_data.get('market_analysis', {})
            if market_data and market_data.get('success'):
                cycle_position = market_data.get('data', {}).get('cycle_position', 'unknown')
                if cycle_position in ['accumulation', 'markup']:
                    patterns.append({
                        'type': 'market_cycle',
                        'confidence': 0.53,
                        'description': f'Market cycle: {cycle_position}'
                    })
            
            # Calculate confluence and score
            confluence = self._calculate_timeframe_confluence(patterns, timeframe)
            
            return {
                'timeframe': 'LONG (1 month+)',
                'patterns': patterns,
                'confluence': confluence,
                'score': confluence.get('final_score', 0),
                'signal': confluence.get('signal', 'NEUTRAL'),
                'trade_type': 'POSITION_TRADE'
            }
            
        except Exception as e:
            logger.error(f"Error in long-term analysis: {e}")
            return {
                'timeframe': 'LONG (1 month+)',
                'patterns': [],
                'confluence': {'final_score': 0, 'signal': 'NEUTRAL'},
                'score': 0,
                'signal': 'NEUTRAL',
                'trade_type': 'POSITION_TRADE',
                'error': str(e)
            }
    
    def _calculate_timeframe_confluence(self, patterns: List[Dict], timeframe: str) -> Dict[str, Any]:
        """Calculate confluence score for a specific timeframe"""
        try:
            if not patterns:
                return {'final_score': 0, 'signal': 'NEUTRAL', 'confluence_count': 0}
            
            # Calculate base score from patterns
            base_scores = []
            for pattern in patterns:
                pattern_type = pattern['type']
                confidence = pattern['confidence']
                base_rate = self.timeframe_patterns[timeframe].get(pattern_type, 0.5)
                base_scores.append(base_rate * confidence)
            
            # Calculate confluence multiplier
            confluence_count = len(patterns)
            multiplier = self.timeframe_multipliers[timeframe].get(confluence_count, 1.0)
            
            # Calculate final score
            if base_scores:
                avg_base_score = np.mean(base_scores)
                final_score = min(100, avg_base_score * multiplier * 100)
            else:
                final_score = 0
            
            # Determine signal
            if final_score >= 90:
                signal = 'LONG'
            elif final_score >= 80:
                signal = 'LONG'
            elif final_score >= 70:
                signal = 'NEUTRAL'
            elif final_score >= 60:
                signal = 'SHORT'
            else:
                signal = 'SHORT'
            
            return {
                'final_score': final_score,
                'signal': signal,
                'confluence_count': confluence_count,
                'base_scores': base_scores,
                'multiplier': multiplier
            }
            
        except Exception as e:
            logger.error(f"Error calculating confluence: {e}")
            return {'final_score': 0, 'signal': 'NEUTRAL', 'confluence_count': 0}
    
    def _ai_agent_decision(self, symbol: str, short: Dict, medium: Dict, long: Dict) -> Dict[str, Any]:
        """AI Agent makes final decision based on multi-timeframe analysis"""
        try:
            short_score = short.get('score', 0)
            medium_score = medium.get('score', 0)
            long_score = long.get('score', 0)
            
            # Find best opportunity
            opportunities = [
                {'timeframe': 'SHORT', 'score': short_score, 'analysis': short},
                {'timeframe': 'MEDIUM', 'score': medium_score, 'analysis': medium},
                {'timeframe': 'LONG', 'score': long_score, 'analysis': long}
            ]
            
            # Sort by score (highest first)
            opportunities.sort(key=lambda x: x['score'], reverse=True)
            
            best_opportunity = opportunities[0]
            second_best = opportunities[1] if len(opportunities) > 1 else None
            
            # Determine primary recommendation
            if best_opportunity['score'] >= 95:
                action = 'ALL_IN'
                position_size = 'MAXIMUM'
                reasoning = f"Exceptional {best_opportunity['timeframe']} setup ({best_opportunity['score']:.1f}% win rate)"
            elif best_opportunity['score'] >= 90:
                action = 'AGGRESSIVE'
                position_size = 'LARGE'
                reasoning = f"Strong {best_opportunity['timeframe']} opportunity ({best_opportunity['score']:.1f}% win rate)"
            elif best_opportunity['score'] >= 80:
                action = 'MODERATE'
                position_size = 'MEDIUM'
                reasoning = f"Good {best_opportunity['timeframe']} setup ({best_opportunity['score']:.1f}% win rate)"
            elif best_opportunity['score'] >= 70:
                action = 'CONSERVATIVE'
                position_size = 'SMALL'
                reasoning = f"Moderate {best_opportunity['timeframe']} opportunity ({best_opportunity['score']:.1f}% win rate)"
            else:
                action = 'AVOID'
                position_size = 'NONE'
                reasoning = f"No strong opportunities (best: {best_opportunity['score']:.1f}%)"
            
            # Risk assessment
            risk_level = self._assess_multi_timeframe_risk(short_score, medium_score, long_score)
            
            return {
                'primary_recommendation': {
                    'action': action,
                    'timeframe': best_opportunity['timeframe'],
                    'score': best_opportunity['score'],
                    'signal': best_opportunity['analysis'].get('signal', 'NEUTRAL'),
                    'position_size': position_size,
                    'reasoning': reasoning
                },
                'all_timeframes': {
                    'short': short,
                    'medium': medium,
                    'long': long
                },
                'risk_assessment': risk_level,
                'opportunity_ranking': opportunities
            }
            
        except Exception as e:
            logger.error(f"Error in AI agent decision: {e}")
            return {
                'primary_recommendation': {
                    'action': 'AVOID',
                    'timeframe': 'UNKNOWN',
                    'score': 0,
                    'signal': 'NEUTRAL',
                    'position_size': 'NONE',
                    'reasoning': f"Error in analysis: {str(e)}"
                },
                'all_timeframes': {
                    'short': short,
                    'medium': medium,
                    'long': long
                },
                'risk_assessment': 'HIGH',
                'opportunity_ranking': []
            }
    
    def _assess_multi_timeframe_risk(self, short_score: float, medium_score: float, long_score: float) -> str:
        """Assess risk based on score variance across timeframes"""
        try:
            scores = [short_score, medium_score, long_score]
            variance = np.var(scores)
            
            if variance < 100:  # Low variance
                return 'LOW'
            elif variance < 400:  # Medium variance
                return 'MEDIUM'
            else:  # High variance
                return 'HIGH'
                
        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
            return 'HIGH'

class MultiTimeframeCryptometerSystem:
    """
    Complete Cryptometer AI Trading System with Multi-Timeframe Analysis
    Enhanced with caching and optimized rate limiting
    """
    
    def __init__(self, api_key: Optional[str] = None):
        # Resolve API key from explicit arg, environment, or settings
        resolved_key = (
            api_key
            or os.getenv("CRYPTOMETER_API_KEY")
            or getattr(settings, "CRYPTOMETER_API_KEY", None)
        )
        if not resolved_key:
            logger.warning("CRYPTOMETER_API_KEY not configured; Cryptometer requests may fail.")
        self.api_key = resolved_key or ""
        self.base_url = "https://api.cryptometer.io"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Cryptometer-MultiTimeframe/1.0',
            'Accept': 'application/json'
        })
        
        # Rate limiting configuration
        self.request_delay = 1.0  # 1 second between requests
        self.max_retries = 3
        self.retry_delay = 2.0
        self.last_request_time = 0
        
        # AI Agent for multi-timeframe analysis
        self.ai_agent = MultiTimeframeAIAgent()
        
        # 💾 ENHANCED CACHING: Smart caching for ranging markets
        self.cache = {}  # Simple memory cache
        self.cache_ttl = {
            'ticker': 30,                    # 30 seconds
            'tickerlist': 60,                 # 1 minute
            'ls_ratio': 120,                  # 2 minutes
            'open_interest': 180,             # 3 minutes
            'liquidation_data_v2': 60,        # 1 minute
            'ai_screener': 300,               # 5 minutes
            'trend_indicator_v3': 300,        # 5 minutes
            'coinlist': 3600,                 # 1 hour
            'cryptocurrency_info': 1800,      # 30 minutes
            'coin_info': 900,                 # 15 minutes
            'full_analysis': 600,             # 10 minutes for ranging markets
            'default': 60                     # Default 1 minute
        }
        self.fallback_data = {}  # Fallback storage for rate limit scenarios
        
        # All working endpoints with CORRECT parameter names from API documentation
        self.endpoints = {
            'coinlist': {
                'url': 'coinlist/',
                'params': {'e': 'binance'},
                'description': 'List of available trading pairs',
                'weight': 2
            },
            'tickerlist': {
                'url': 'tickerlist/',
                'params': {'e': 'binance'},
                'description': 'Real-time pricing data for all pairs',
                'weight': 5
            },
            'ticker': {
                'url': 'ticker/',
                'params': {'e': 'binance', 'market_pair': '{symbol}-USDT'},  # Fixed: market_pair instead of pair
                'description': 'Single ticker with detailed price data',
                'weight': 8
            },
            'cryptocurrency_info': {
                'url': 'cryptocurrency-info/',
                'params': {'e': 'binance', 'filter': 'all'},
                'description': 'Comprehensive cryptocurrency information',
                'weight': 6
            },
            'coin_info': {
                'url': 'coininfo/',
                'params': {},
                'description': 'Individual coin market data and metrics',
                'weight': 4
            },
            'tickerlist_pro': {
                'url': 'tickerlist-pro/',
                'params': {'e': 'binance'},
                'description': 'Professional ticker data with USD conversion',
                'weight': 10
            },
            'trend_indicator_v3': {
                'url': 'trend-indicator-v3/',
                'params': {},  # Only API key needed
                'description': 'Advanced trend analysis indicators',
                'weight': 15
            },
            'ls_ratio': {
                'url': 'ls-ratio/',
                'params': {'e': 'binance_futures', 'pair': '{symbol}-usdt', 'timeframe': '4h'},  # Lowercase pair format
                'description': 'Long/Short ratio analysis',
                'weight': 12
            },
            'open_interest': {
                'url': 'open-interest/',
                'params': {'e': 'binance_futures', 'market_pair': '{symbol}USDT'},  # No hyphen for futures
                'description': 'Futures open interest data',
                'weight': 9
            },
            'liquidation_data_v2': {
                'url': 'liquidation-data-v2/',
                'params': {'symbol': '{symbol}'},  # Lowercase symbol only
                'description': 'Liquidation cluster analysis',
                'weight': 14
            },
            'rapid_movements': {
                'url': 'rapid-movements/',
                'params': {},  # Only API key needed
                'description': 'Rapid price movement alerts',
                'weight': 7
            },
            'ai_screener': {
                'url': 'ai-screener/',
                'params': {},  # Only API key needed
                'description': 'AI-powered market screening',
                'weight': 16
            },
            'ai_screener_analysis': {
                'url': 'ai-screener-analysis/',
                'params': {'symbol': '{symbol}'},
                'description': 'Detailed AI analysis for specific symbol (may return no updates)',
                'weight': 18
            },
            'forex_rates': {
                'url': 'forex-rates/',
                'params': {'source': 'USD'},
                'description': 'Foreign exchange rates',
                'weight': 3
            },
            'account_info': {
                'url': 'info/',
                'params': {},
                'description': 'API account information and usage',
                'weight': 1
            }
        }
    
    def _get_cache_key(self, endpoint_name: str, params: dict) -> str:
        """Generate cache key for endpoint and params"""
        import hashlib
        # Remove API key from cache key
        cache_params = {k: v for k, v in params.items() if k != 'api_key'}
        key_str = f"{endpoint_name}:{json.dumps(cache_params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str, endpoint_name: str) -> Optional[dict]:
        """Get data from cache if not expired"""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            ttl = self.cache_ttl.get(endpoint_name, self.cache_ttl['default'])
            age = time.time() - entry['timestamp']
            if age < ttl:
                logger.debug(f"Cache hit for {endpoint_name} (age: {age:.1f}s)")
                return entry['data']
        return None
    
    def _set_cache(self, cache_key: str, data: dict):
        """Store data in cache"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
        # Also update fallback
        self.fallback_data[cache_key] = data

    async def _safe_request(self, url: str, params: dict, endpoint_name: str) -> Tuple[dict, bool]:
        """Make safe API request with STRICT quota protection, rate limiting, caching, and error handling"""
        try:
            # 🔐 STEP 1: Check quota BEFORE making any request
            service_name = f"cryptometer_{endpoint_name}"
            if not can_make_cryptometer_request(service=service_name, priority=self._get_endpoint_priority(endpoint_name)):
                logger.warning(f"🚫 QUOTA BLOCKED: {endpoint_name} - Daily/Monthly limit reached")
                # 💡 ENHANCEMENT: Use cached/fallback data instead of errors
                cache_key = self._get_cache_key(endpoint_name, params)
                
                # Try fresh cache first (within TTL)
                cached_data = self._get_from_cache(cache_key, endpoint_name)
                if cached_data is not None:
                    logger.info(f"✅ Using fresh cached data for quota-blocked request: {endpoint_name}")
                    return cached_data, True
                
                # Try fallback data (expired cache)
                if cache_key in self.fallback_data:
                    logger.info(f"📦 Using fallback data for quota-blocked request: {endpoint_name}")
                    return self.fallback_data[cache_key], True
                return {}, False
            
            # Generate cache key
            cache_key = self._get_cache_key(endpoint_name, params)
            
            # Check cache first
            cached_data = self._get_from_cache(cache_key, endpoint_name)
            if cached_data is not None:
                return cached_data, True
            
            # Add API key to params
            params['api_key'] = self.api_key
            
            # Define the request function
            def make_request():
                return self.session.get(url, params=params, timeout=30)
            
            # Execute with enhanced rate limiting
            response, success = await rate_limited_request('cryptometer', make_request)
            
            if success and response and response.status_code == 200:
                try:
                    data = response.json()
                    
                    # 🔐 STEP 2: Record successful request in quota manager
                    record_cryptometer_request(service=service_name, success=True)
                    
                    # Cache successful response
                    self._set_cache(cache_key, data)
                    
                    logger.debug(f"✅ Cryptometer API success: {endpoint_name}")
                    return data, True
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error for {endpoint_name}: {e}")
                    # Don't record failed JSON parsing as API usage
                    return {}, False
                    
            elif response and response.status_code == 429:
                logger.warning(f"⏳ Rate limited for {endpoint_name} (429), checking fallback")
                # Record the attempt (rate limited = still an API call)
                record_cryptometer_request(service=service_name, success=False)
                
                # Try fallback data
                if cache_key in self.fallback_data:
                    logger.info(f"📦 Using fallback data for {endpoint_name}")
                    return self.fallback_data[cache_key], True
                return {}, False
                
            else:
                status = response.status_code if response else 'No response'
                logger.warning(f"❌ API request failed for {endpoint_name}: {status}")
                
                # Record failed request if we got a response (server responded = API call made)
                if response:
                    record_cryptometer_request(service=service_name, success=False)
                
                # Try fallback on any failure
                if cache_key in self.fallback_data:
                    logger.info(f"📦 Using fallback data for {endpoint_name} after error")
                    return self.fallback_data[cache_key], True
                return {}, False
                
        except Exception as e:
            logger.error(f"Error in API request for {endpoint_name}: {e}")
            # Try fallback on exception
            cache_key = self._get_cache_key(endpoint_name, params)
            if cache_key in self.fallback_data:
                logger.info(f"📦 Using fallback data after exception: {endpoint_name}")
                return self.fallback_data[cache_key], True
            return {}, False
    
    def _get_endpoint_priority(self, endpoint_name: str) -> int:
        """Get priority for specific Cryptometer endpoint"""
        # Higher priority = more important
        endpoint_priorities = {
            # Core trading signals - HIGHEST PRIORITY
            'trend_indicator_v3': 10,       # Most critical for trading
            'ls_ratio': 9,                  # Long/Short ratio
            'open_interest': 8,             # Market sentiment
            'liquidation_data_v2': 8,       # Risk assessment
            
            # Market data - HIGH PRIORITY  
            'ticker': 7,                    # Price data
            'tickerlist': 6,                # Multiple symbols
            'tickerlist_pro': 6,            # Enhanced ticker data
            
            # Analysis data - MEDIUM PRIORITY
            'rapid_movements': 5,           # Volatility analysis
            'ai_screener': 5,               # AI-powered screening
            'ai_screener_analysis': 5,      # AI analysis
            
            # General data - LOW PRIORITY
            'coinlist': 3,                  # Coin information
            'cryptocurrency_info': 3,       # Coin details
            'coin_info': 3,                 # Basic info
            'forex_rates': 2,               # Currency rates
            'account_info': 1,              # Account status
        }
        
        return endpoint_priorities.get(endpoint_name, 4)  # Default medium-low priority
    
    def _should_analyze_symbol(self, symbol: str, current_price: float = None, volume: float = None) -> Tuple[bool, bool]:
        """
        🎯 SMART TRIGGER: Check if symbol should be analyzed based on price movement
        Returns (should_analyze, is_ranging) tuple
        """
        try:
            # If we have current price data, use the movement trigger system
            if current_price is not None and volume is not None:
                should_analyze = should_trigger_cryptometer_analysis(symbol, current_price, volume)
                if not should_analyze:
                    logger.info(f"🔇 {symbol} - Price movement trigger says NO API calls needed (ranging/insufficient movement)")
                    return False, True  # Not analyze, is ranging
                else:
                    logger.info(f"🎯 {symbol} - Price movement trigger says ANALYZE (significant movement detected)")
                    return True, False  # Analyze, not ranging
            
            # Fallback: Check trigger status without new price data
            trigger_status = get_price_trigger_status(symbol)
            if trigger_status.get('status') == 'no_data':
                # No historical data, allow analysis (first time)
                logger.info(f"🆕 {symbol} - First analysis (no price history)")
                return True, False
            
            # Default to allowing analysis if we can't determine movement
            return True, False
            
        except Exception as e:
            logger.error(f"❌ Error checking movement trigger for {symbol}: {e}")
            return True, False  # On error, allow analysis to be safe

    async def collect_symbol_data(self, symbol: str, current_price: float = None, volume: float = None) -> Dict[str, Any]:
        """Collect comprehensive data for a symbol from all endpoints with smart triggering and intelligent caching"""
        try:
            # 🎯 STEP 1: Check if we should analyze this symbol based on price movement
            should_analyze, is_ranging = self._should_analyze_symbol(symbol, current_price, volume)
            
            if not should_analyze:
                # 💡 RANGING MARKET: Try to use cached data instead of returning empty results
                cache_key = self._get_cache_key('full_analysis', {'symbol': symbol})
                cached_data = self._get_from_cache(cache_key, 'full_analysis')
                
                if cached_data:
                    logger.info(f"✅ {symbol} - Using fresh cached analysis (ranging market detected)")
                    cached_data['cache_info'] = {
                        'cached': True,
                        'reason': 'ranging_market',
                        'status': 'fresh_cache_used',
                        'timestamp': datetime.now().isoformat()
                    }
                    return cached_data
                
                # Try fallback data (expired cache)  
                if cache_key in self.fallback_data:
                    logger.info(f"📦 {symbol} - Using fallback analysis data (ranging market, no fresh cache)")
                    fallback_data = self.fallback_data[cache_key].copy()
                    fallback_data['cache_info'] = {
                        'cached': True,
                        'reason': 'ranging_market',
                        'status': 'fallback_cache_used',
                        'timestamp': datetime.now().isoformat()
                    }
                    return fallback_data
                
                # No cache available - return minimal response
                logger.info(f"🔇 {symbol} - Skipping analysis (ranging market, no cache available)")
                return {
                    'symbol': symbol,
                    'status': 'analysis_suppressed',
                    'reason': 'ranging_market_no_cache',
                    'is_ranging': True,
                    'timestamp': datetime.now().isoformat()
                }
            
            # 🎯 STEP 2: Proceed with analysis - movement detected or first analysis
            logger.info(f"✅ {symbol} - Starting Cryptometer analysis (movement detected)")
            symbol_data: Dict[str, Any] = {'symbol': symbol, 'is_ranging': is_ranging}
            
            # Collect data from all endpoints
            for endpoint_name, config in self.endpoints.items():
                try:
                    url = f"{self.base_url}/{config['url']}"
                    params = config['params'].copy()
                    
                    # Replace symbol placeholder
                    for key, value in params.items():
                        if isinstance(value, str) and '{symbol}' in value:
                            params[key] = value.replace('{symbol}', symbol)
                    
                    data, success = await self._safe_request(url, params, endpoint_name)
                    
                    symbol_data[endpoint_name] = {
                        'success': success,
                        'data': data if success else {},
                        'endpoint': endpoint_name,
                        'description': config['description']
                    }
                    
                except Exception as e:
                    logger.warning(f"Error collecting {endpoint_name} for {symbol}: {e}")
                    symbol_data[endpoint_name] = {
                        'success': False,
                        'data': {},
                        'error': str(e),
                        'endpoint': endpoint_name,
                        'description': config['description']
                    }
            
            # 💾 Cache the full analysis result for ranging market scenarios
            cache_key = self._get_cache_key('full_analysis', {'symbol': symbol})
            symbol_data['cache_info'] = {
                'cached': False,
                'reason': 'fresh_analysis',
                'status': 'new_data_collected',
                'timestamp': datetime.now().isoformat()
            }
            self._set_cache(cache_key, symbol_data)
            
            return symbol_data
            
        except Exception as e:
            logger.error(f"Error collecting symbol data for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}
    
    async def analyze_multi_timeframe_symbol(self, symbol: str) -> Dict[str, Any]:
        """Analyze a symbol using multi-timeframe AI agent"""
        try:
            # Collect comprehensive data
            symbol_data = await self.collect_symbol_data(symbol)
            
            # Run multi-timeframe analysis
            analysis_result = self.ai_agent.analyze_multi_timeframe(symbol_data)
            
            # Add AI win rate prediction
            ai_prediction = await self._get_ai_win_rate_prediction(symbol, symbol_data)
            analysis_result['ai_win_rate_prediction'] = ai_prediction
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def batch_collect_symbols(self, symbols: List[str], priority_endpoints: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Batch collect data for multiple symbols with intelligent caching
        
        Args:
            symbols: List of symbols to process
            priority_endpoints: Optional list of specific endpoints to use
        """
        results: Dict[str, Any] = {}
        
        # Use priority endpoints if specified, otherwise use all
        endpoints_to_use = priority_endpoints if priority_endpoints else list(self.endpoints.keys())
        
        for symbol in symbols:
            symbol_data: Dict[str, Any] = {'symbol': symbol}
            
            for endpoint_name in endpoints_to_use:
                if endpoint_name not in self.endpoints:
                    continue
                    
                config = self.endpoints[endpoint_name]
                url = f"{self.base_url}/{config['url']}"
                params = config['params'].copy()
                
                # Replace symbol placeholder with proper formatting
                for key, value in params.items():
                    if isinstance(value, str) and '{symbol}' in value:
                        # Special handling for different endpoints
                        if endpoint_name == 'liquidation_data_v2':
                            # Use lowercase symbol only (btc, eth, etc.)
                            formatted_symbol = symbol.lower()
                        elif endpoint_name == 'ls_ratio':
                            # Use lowercase for ls_ratio
                            formatted_symbol = symbol.lower()
                        elif endpoint_name == 'open_interest':
                            # Use uppercase for futures (BTCUSDT format)
                            formatted_symbol = symbol.upper()
                        else:
                            # Default to uppercase
                            formatted_symbol = symbol.upper()
                        params[key] = value.replace('{symbol}', formatted_symbol)
                
                # This will use cache if available
                data, success = await self._safe_request(url, params, endpoint_name)
                
                symbol_data[endpoint_name] = {
                    'success': success,
                    'data': data if success else {},
                    'cached': self._get_from_cache(
                        self._get_cache_key(endpoint_name, params), 
                        endpoint_name
                    ) is not None
                }
            
            results[symbol] = symbol_data
            
            # Small delay between symbols to respect rate limits
            await asyncio.sleep(0.1)
        
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        fallback_entries = len(self.fallback_data)
        
        # Count fresh vs stale entries
        fresh = 0
        stale = 0
        current_time = time.time()
        
        for key, entry in self.cache.items():
            # Try to determine endpoint from key
            endpoint = 'default'
            for ep_name in self.endpoints.keys():
                if ep_name in str(key):
                    endpoint = ep_name
                    break
            
            ttl = self.cache_ttl.get(endpoint, self.cache_ttl['default'])
            age = current_time - entry['timestamp']
            
            if age < ttl:
                fresh += 1
            else:
                stale += 1
        
        return {
            'total_entries': total_entries,
            'fresh_entries': fresh,
            'stale_entries': stale,
            'fallback_entries': fallback_entries,
            'cache_hit_rate': f"{(fresh / total_entries * 100) if total_entries > 0 else 0:.1f}%"
        }
    
    def clear_stale_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        keys_to_remove = []
        
        for key, entry in self.cache.items():
            # Try to determine endpoint
            endpoint = 'default'
            for ep_name in self.endpoints.keys():
                if ep_name in str(key):
                    endpoint = ep_name
                    break
            
            ttl = self.cache_ttl.get(endpoint, self.cache_ttl['default'])
            age = current_time - entry['timestamp']
            
            if age > ttl:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
        
        if keys_to_remove:
            logger.info(f"Cleared {len(keys_to_remove)} stale cache entries")

    async def get_cryptometer_win_rate(self, symbol: str) -> Dict[str, Any]:
        """Get Cryptometer win rate prediction using AI analysis of 17 endpoints"""
        try:
            # Collect comprehensive data from all endpoints
            symbol_data = await self.collect_symbol_data(symbol)
            
            # Get AI win rate prediction
            ai_prediction = await self._get_ai_win_rate_prediction(symbol, symbol_data)
            
            if not ai_prediction:
                return {'symbol': symbol, 'error': 'Failed to get AI prediction'}
            
            return {
                'symbol': symbol,
                'win_rate_prediction': ai_prediction['win_rate_prediction'],
                'confidence': ai_prediction['confidence'],
                'direction': ai_prediction['direction'],
                'reasoning': 'Mock Cryptometer analysis',
                'ai_analysis': 'Mock AI analysis',
                'data_summary': 'Mock data summary',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting Cryptometer win rate for {symbol}: {str(e)}")
            return {'symbol': symbol, 'win_rate_prediction': 0.0, 'error': str(e)}
    
    async def get_multi_timeframe_win_rate(self, symbol: str) -> Dict[str, Any]:
        """Get multi-timeframe win rate predictions using AI analysis"""
        try:
            # Collect comprehensive data
            symbol_data = await self.collect_symbol_data(symbol)
            
            # Get multi-timeframe AI prediction
            multi_prediction = await self._get_multi_timeframe_ai_prediction(symbol, symbol_data)
            
            if not multi_prediction:
                return {'symbol': symbol, 'error': 'Failed to get multi-timeframe AI prediction'}
            
            return {
                'symbol': symbol,
                'short_term_24h': {
                    'win_rate': multi_prediction['timeframes']['24h']['win_rate'],
                    'confidence': multi_prediction['timeframes']['24h']['confidence'],
                    'direction': 'neutral',
                    'reasoning': 'Mock Cryptometer analysis'
                },
                'medium_term_7d': {
                    'win_rate': multi_prediction['timeframes']['7d']['win_rate'],
                    'confidence': multi_prediction['timeframes']['7d']['confidence'],
                    'direction': 'neutral',
                    'reasoning': 'Mock Cryptometer analysis'
                },
                'long_term_1m': {
                    'win_rate': multi_prediction['timeframes']['1m']['win_rate'],
                    'confidence': multi_prediction['timeframes']['1m']['confidence'],
                    'direction': 'neutral',
                    'reasoning': 'Mock Cryptometer analysis'
                },
                'overall_confidence': multi_prediction['overall_confidence'],
                'best_opportunity': {
                    'timeframe': '7d',
                    'win_rate': multi_prediction['timeframes']['7d']['win_rate'],
                    'direction': 'neutral'
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting multi-timeframe win rate for {symbol}: {str(e)}")
            return {'symbol': symbol, 'error': str(e)}
    
    async def _get_ai_win_rate_prediction(self, symbol: str, cryptometer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get AI win rate prediction for Cryptometer 17-endpoint analysis (mock implementation)"""
        try:
            # Mock prediction for now
            return {
                'win_rate_prediction': 0.70,
                'confidence': 0.80,
                'direction': 'neutral',
                'model_type': 'cryptometer_17_endpoint',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting AI win rate prediction for {symbol}: {str(e)}")
            return None
    
    async def _get_multi_timeframe_ai_prediction(self, symbol: str, cryptometer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get multi-timeframe AI prediction for Cryptometer 17-endpoint analysis (mock implementation)"""
        try:
            # Mock multi-timeframe prediction
            return {
                'timeframes': {
                    '24h': {'win_rate': 0.70, 'confidence': 0.80},
                    '7d': {'win_rate': 0.75, 'confidence': 0.85},
                    '1m': {'win_rate': 0.65, 'confidence': 0.75}
                },
                'overall_win_rate': 0.70,
                'overall_confidence': 0.80,
                'direction': 'neutral',
                'model_type': 'cryptometer_multi_timeframe',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting multi-timeframe AI prediction for {symbol}: {str(e)}")
            return None

# Global instance
_cryptometer_system = None

async def get_cryptometer_service() -> MultiTimeframeCryptometerSystem:
    """Get or create Cryptometer AI system instance"""
    global _cryptometer_system
    if _cryptometer_system is None:
        _cryptometer_system = MultiTimeframeCryptometerSystem()
    return _cryptometer_system

async def run_multi_timeframe_analysis(symbols: List[str]) -> List[Dict[str, Any]]:
    """Run multi-timeframe analysis for multiple symbols"""
    try:
        system = MultiTimeframeCryptometerSystem()
        results = []
        
        for symbol in symbols:
            result = await system.analyze_multi_timeframe_symbol(symbol)
            results.append(result)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in multi-timeframe analysis: {e}")
        return []

def display_multi_timeframe_results(results: List[Dict[str, Any]]):
    """Display multi-timeframe analysis results"""
    for result in results:
        symbol = result.get('symbol', 'UNKNOWN')
        ai_rec = result.get('ai_recommendation', {})
        primary = ai_rec.get('primary_recommendation', {})
        
        print(f"\n🎯 {symbol} Multi-Timeframe Analysis:")
        print(f"   Action: {primary.get('action', 'UNKNOWN')}")
        print(f"   Timeframe: {primary.get('timeframe', 'UNKNOWN')}")
        print(f"   Score: {primary.get('score', 0):.1f}/100")
        print(f"   Signal: {primary.get('signal', 'NEUTRAL')}")
        print(f"   Position: {primary.get('position_size', 'NONE')}")
        print(f"   Reasoning: {primary.get('reasoning', 'No reasoning available')}") 