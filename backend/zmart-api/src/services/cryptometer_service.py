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
from typing import Dict, List, Any, Tuple
import statistics

# Import enhanced rate limiter
from src.utils.enhanced_rate_limiter import global_rate_limiter, rate_limited_request

# Import AI win rate predictor
from src.agents.scoring.ai_win_rate_predictor import (
    ai_predictor,
    AIModel,
    AIWinRatePrediction,
    MultiTimeframeAIPrediction
)

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
            self.client = openai.OpenAI()
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
    """
    
    def __init__(self, api_key: str = "k77U187e08zGf4I3SLz3sYzTEyM2KNoJ9i1N4xg2"):
        self.api_key = api_key
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
        
        # All working endpoints with descriptions
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
                'params': {'e': 'binance', 'pair': '{symbol}-USDT'},
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
                'params': {},
                'description': 'Advanced trend analysis indicators',
                'weight': 15
            },
            'forex_rates': {
                'url': 'forex-rates/',
                'params': {'source': 'USD'},
                'description': 'Currency exchange rates for conversion',
                'weight': 3
            },
            'ls_ratio': {
                'url': 'ls-ratio/',
                'params': {'e': 'binance_futures', 'pair': '{symbol}-usdt', 'timeframe': '4h'},
                'description': 'Long/Short ratio analysis',
                'weight': 12
            },
            'open_interest': {
                'url': 'open-interest/',
                'params': {'e': 'binance_futures', 'market_pair': '{symbol}-USDT'},
                'description': 'Futures open interest data',
                'weight': 9
            },
            'liquidation_data_v2': {
                'url': 'liquidation-data-v2/',
                'params': {'symbol': '{symbol}'},
                'description': 'Liquidation cluster analysis',
                'weight': 14
            },
            'rapid_movements': {
                'url': 'rapid-movements/',
                'params': {},
                'description': 'Rapid price movement alerts',
                'weight': 7
            },
            'ai_screener': {
                'url': 'ai-screener/',
                'params': {},
                'description': 'AI-powered market screening',
                'weight': 16
            },
            'ai_screener_analysis': {
                'url': 'ai-screener-analysis/',
                'params': {'symbol': '{symbol}'},
                'description': 'Detailed AI analysis for specific symbol',
                'weight': 18
            }
        }
    
    async def _safe_request(self, url: str, params: dict, endpoint_name: str) -> Tuple[dict, bool]:
        """Make safe API request with enhanced rate limiting and error handling"""
        try:
            # Add API key to params
            params['api_key'] = self.api_key
            
            # Define the request function
            def make_request():
                return self.session.get(url, params=params, timeout=30)
            
            # Execute with enhanced rate limiting
            response, success = await rate_limited_request('cryptometer', make_request)
            
            if success and response and response.status_code == 200:
                try:
                    return response.json(), True
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error for {endpoint_name}: {e}")
                    return {}, False
            elif response and response.status_code == 429:
                logger.warning(f"Rate limited for {endpoint_name} (429), enhanced rate limiter will handle backoff")
                return {}, False
            else:
                status = response.status_code if response else 'No response'
                logger.warning(f"API request failed for {endpoint_name}: {status}")
                return {}, False
                
        except Exception as e:
            logger.error(f"Error in API request for {endpoint_name}: {e}")
            return {}, False
    
    async def collect_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Collect comprehensive data for a symbol from all endpoints"""
        try:
            symbol_data: Dict[str, Any] = {'symbol': symbol}
            
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
    
    async def get_cryptometer_win_rate(self, symbol: str) -> Dict[str, Any]:
        """Get Cryptometer win rate prediction using AI analysis of 17 endpoints"""
        try:
            # Collect comprehensive data from all endpoints
            symbol_data = await self.collect_symbol_data(symbol)
            
            # Get AI win rate prediction
            ai_prediction = await self._get_ai_win_rate_prediction(symbol, symbol_data)
            
            return {
                'symbol': symbol,
                'win_rate_prediction': ai_prediction.win_rate_prediction,
                'confidence': ai_prediction.confidence,
                'direction': ai_prediction.direction,
                'reasoning': ai_prediction.reasoning,
                'ai_analysis': ai_prediction.ai_analysis,
                'data_summary': ai_prediction.data_summary,
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
            
            return {
                'symbol': symbol,
                'short_term_24h': {
                    'win_rate': multi_prediction.short_term_24h.win_rate_prediction,
                    'confidence': multi_prediction.short_term_24h.confidence,
                    'direction': multi_prediction.short_term_24h.direction,
                    'reasoning': multi_prediction.short_term_24h.reasoning
                },
                'medium_term_7d': {
                    'win_rate': multi_prediction.medium_term_7d.win_rate_prediction,
                    'confidence': multi_prediction.medium_term_7d.confidence,
                    'direction': multi_prediction.medium_term_7d.direction,
                    'reasoning': multi_prediction.medium_term_7d.reasoning
                },
                'long_term_1m': {
                    'win_rate': multi_prediction.long_term_1m.win_rate_prediction,
                    'confidence': multi_prediction.long_term_1m.confidence,
                    'direction': multi_prediction.long_term_1m.direction,
                    'reasoning': multi_prediction.long_term_1m.reasoning
                },
                'overall_confidence': multi_prediction.overall_confidence,
                'best_opportunity': {
                    'timeframe': multi_prediction.best_opportunity.timeframe,
                    'win_rate': multi_prediction.best_opportunity.win_rate_prediction,
                    'direction': multi_prediction.best_opportunity.direction
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting multi-timeframe win rate for {symbol}: {str(e)}")
            return {'symbol': symbol, 'error': str(e)}
    
    async def _get_ai_win_rate_prediction(self, symbol: str, cryptometer_data: Dict[str, Any]) -> AIWinRatePrediction:
        """Get AI win rate prediction for Cryptometer 17-endpoint analysis"""
        try:
            return await ai_predictor.predict_cryptometer_win_rate(
                symbol=symbol,
                cryptometer_data=cryptometer_data,
                model=AIModel.OPENAI_GPT4
            )
        except Exception as e:
            logger.error(f"Error getting AI win rate prediction for {symbol}: {str(e)}")
            # Return fallback prediction
            return ai_predictor._create_fallback_prediction(symbol, "cryptometer", f"AI error: {str(e)}")
    
    async def _get_multi_timeframe_ai_prediction(self, symbol: str, cryptometer_data: Dict[str, Any]) -> MultiTimeframeAIPrediction:
        """Get multi-timeframe AI prediction for Cryptometer 17-endpoint analysis"""
        try:
            return await ai_predictor.predict_multi_timeframe_win_rate(
                symbol=symbol,
                agent_type="cryptometer",
                agent_data=cryptometer_data,
                model=AIModel.OPENAI_GPT4
            )
        except Exception as e:
            logger.error(f"Error getting multi-timeframe AI prediction for {symbol}: {str(e)}")
            # Return fallback prediction
            return ai_predictor._create_fallback_multi_prediction(symbol, "cryptometer")

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