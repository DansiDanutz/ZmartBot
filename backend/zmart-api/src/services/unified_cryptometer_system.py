"""
Unified Cryptometer System - Complete Implementation
====================================================

This module combines all the best elements from:
1. Our existing multi-model AI system
2. The Complete Implementation Guide
3. The Quick-Start Implementation Guide

Features:
- Symbol-specific learning agents
- 18 Cryptometer endpoints with enhanced configurations
- Dynamic pattern weighting based on performance
- Multi-timeframe analysis (24h, 7d, 30d)
- Comprehensive outcome tracking and attribution
- Self-learning with continuous improvement
- Multi-model AI integration (OpenAI + Local models)
- Production-ready monitoring and optimization

Author: ZmartBot AI System
Version: 2.0 (Unified Implementation)
"""

import asyncio
import aiohttp
import time
import logging
import json
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import uuid

from src.config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class Pattern:
    """Enhanced pattern representation"""
    pattern_id: str
    pattern_type: str
    direction: str  # 'bullish', 'bearish', 'neutral'
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    timeframe: str
    detected_at: datetime
    market_conditions: Dict[str, Any]
    contributing_endpoints: List[str]
    weight: float = 1.0

@dataclass
class TradingSignal:
    """Enhanced trading signal with multi-timeframe targets"""
    signal_id: str
    symbol: str
    timestamp: datetime
    pattern: Pattern
    direction: str
    current_price: float
    targets: Dict[str, Dict[str, float]]  # timeframe -> {target, stop_loss, confidence}
    market_data: Dict[str, Any]
    expected_outcomes: Dict[str, float]

@dataclass
class SignalOutcome:
    """Comprehensive outcome tracking"""
    signal_id: str
    outcome_type: str  # 'success', 'failure', 'incomplete'
    timeframe: str
    actual_return: float
    time_to_outcome: timedelta
    max_favorable_excursion: float
    max_adverse_excursion: float
    pattern_attribution: Dict[str, float]
    market_conditions_at_exit: Dict[str, Any]

class SymbolLearningAgent:
    """Individual learning agent per symbol as recommended by the guides"""
    
    def __init__(self, symbol: str, db_path: Optional[str] = None):
        self.symbol = symbol
        self.db_path = db_path or f"learning_data_{symbol.replace('/', '_')}.db"
        self.pattern_weights: Dict[str, float] = {}
        self.pattern_performance: Dict[str, Dict[str, Any]] = {}
        self.learning_rate = 0.1
        self.target_success_rate = 0.6  # 60% as recommended
        
        self._init_database()
        self._load_learned_patterns()
    
    def _init_database(self):
        """Initialize symbol-specific learning database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pattern_performance (
                    pattern_type TEXT,
                    total_signals INTEGER DEFAULT 0,
                    successful_signals INTEGER DEFAULT 0,
                    total_return REAL DEFAULT 0.0,
                    avg_return REAL DEFAULT 0.0,
                    success_rate REAL DEFAULT 0.5,
                    weight REAL DEFAULT 1.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (pattern_type)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS signal_outcomes (
                    signal_id TEXT PRIMARY KEY,
                    pattern_type TEXT,
                    timeframe TEXT,
                    outcome_type TEXT,
                    actual_return REAL,
                    time_to_outcome INTEGER,
                    max_favorable REAL,
                    max_adverse REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_conditions (
                    timestamp TIMESTAMP,
                    market_regime TEXT,
                    volatility_level TEXT,
                    trend_strength REAL,
                    sentiment_score REAL,
                    PRIMARY KEY (timestamp)
                )
            """)
    
    def _load_learned_patterns(self):
        """Load previously learned pattern weights"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT pattern_type, weight, success_rate, avg_return FROM pattern_performance")
            for row in cursor.fetchall():
                pattern_type, weight, success_rate, avg_return = row
                self.pattern_weights[pattern_type] = weight
                self.pattern_performance[pattern_type] = {
                    'weight': weight,
                    'success_rate': success_rate,
                    'avg_return': avg_return
                }
    
    def update_pattern_performance(self, outcome: SignalOutcome):
        """Update pattern performance based on outcome - core learning mechanism"""
        pattern_type = outcome.signal_id.split('_')[1]  # Extract pattern type from signal_id
        
        if pattern_type not in self.pattern_performance:
            self.pattern_performance[pattern_type] = {
                'weight': 1.0,
                'success_rate': 0.5,
                'avg_return': 0.0,
                'total_signals': 0,
                'successful_signals': 0,
                'total_return': 0.0
            }
        
        perf = self.pattern_performance[pattern_type]
        perf['total_signals'] += 1
        perf['total_return'] += outcome.actual_return
        
        if outcome.outcome_type == 'success':
            perf['successful_signals'] += 1
        
        # Update metrics
        perf['success_rate'] = perf['successful_signals'] / perf['total_signals']
        perf['avg_return'] = perf['total_return'] / perf['total_signals']
        
        # Dynamic weight calculation based on performance
        performance_factor = perf['success_rate'] / self.target_success_rate
        return_factor = max(0.1, 1 + perf['avg_return'])
        
        new_weight = performance_factor * return_factor
        perf['weight'] = (perf['weight'] * (1 - self.learning_rate) + 
                         new_weight * self.learning_rate)
        
        self.pattern_weights[pattern_type] = perf['weight']
        
        # Persist to database
        self._save_pattern_performance(pattern_type, perf)
        self._save_signal_outcome(outcome)
        
        logger.info(f"Updated {self.symbol} pattern {pattern_type}: "
                   f"weight={perf['weight']:.3f}, success_rate={perf['success_rate']:.3f}")
    
    def _save_pattern_performance(self, pattern_type: str, perf: Dict[str, Any]):
        """Save pattern performance to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO pattern_performance 
                (pattern_type, total_signals, successful_signals, total_return, 
                 avg_return, success_rate, weight, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (pattern_type, perf['total_signals'], perf['successful_signals'],
                  perf['total_return'], perf['avg_return'], perf['success_rate'],
                  perf['weight'], datetime.now()))
    
    def _save_signal_outcome(self, outcome: SignalOutcome):
        """Save signal outcome to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO signal_outcomes 
                (signal_id, pattern_type, timeframe, outcome_type, actual_return,
                 time_to_outcome, max_favorable, max_adverse, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (outcome.signal_id, outcome.signal_id.split('_')[1], outcome.timeframe,
                  outcome.outcome_type, outcome.actual_return, 
                  int(outcome.time_to_outcome.total_seconds()),
                  outcome.max_favorable_excursion, outcome.max_adverse_excursion,
                  datetime.now()))
    
    def should_generate_signal(self, pattern: Pattern) -> bool:
        """Decide if pattern should generate signal based on learning"""
        weight = self.pattern_weights.get(pattern.pattern_type, 1.0)
        adjusted_confidence = pattern.confidence * weight
        
        # Dynamic threshold based on recent performance
        threshold = 0.5  # Base threshold
        if pattern.pattern_type in self.pattern_performance:
            success_rate = self.pattern_performance[pattern.pattern_type]['success_rate']
            if success_rate > 0.7:
                threshold = 0.4  # Lower threshold for high-performing patterns
            elif success_rate < 0.4:
                threshold = 0.7  # Higher threshold for poor-performing patterns
        
        return adjusted_confidence > threshold
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary for this symbol"""
        return {
            'symbol': self.symbol,
            'total_patterns': len(self.pattern_performance),
            'pattern_performance': self.pattern_performance,
            'pattern_weights': self.pattern_weights,
            'learning_rate': self.learning_rate,
            'target_success_rate': self.target_success_rate
        }

class UnifiedCryptometerSystem:
    """
    Unified Cryptometer System - Production Implementation
    
    Combines all best practices from implementation guides:
    - Symbol-specific learning agents
    - Enhanced endpoint configurations
    - Multi-timeframe analysis
    - Dynamic pattern weighting
    - Comprehensive outcome tracking
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.CRYPTOMETER_API_KEY
        self.base_url = "https://api.cryptometer.io"
        self.rate_limit = 1.0  # 1 second as mandated by guides
        
        # Symbol-specific learning agents
        self.learning_agents: Dict[str, SymbolLearningAgent] = {}
        
        # Enhanced endpoint configurations from guides
        self.endpoints = self._get_enhanced_endpoint_config()
        
        # Pattern detection system
        self.pattern_detector = EnhancedPatternDetector()
        
        # Signal generation system
        self.signal_generator = UnifiedSignalGenerator()
        
        # Outcome tracking system
        self.outcome_tracker = ComprehensiveOutcomeTracker()
        
        logger.info("Unified Cryptometer System initialized with enhanced capabilities")
    
    def _get_enhanced_endpoint_config(self) -> Dict[str, Dict[str, Any]]:
        """Enhanced endpoint configuration combining all guides"""
        return {
            # TIER 1: Critical Signal Generation (Guide Priority)
            'volume_flow': {
                'url': '/volume-flow/',
                'params': {'timeframe': '1h'},
                'priority': 1,
                'weight': 15,
                'signal_value': 'high',
                'description': 'Primary money flow analysis - highest signal value'
            },
            'ls_ratio': {
                'url': '/ls-ratio/',
                'params': {'e': 'binance_futures', 'pair': '{symbol}', 'timeframe': '1h'},
                'priority': 1,
                'weight': 14,
                'signal_value': 'high',
                'description': 'Market sentiment and positioning analysis'
            },
            'liquidation_data_v2': {
                'url': '/liquidation-data-v2/',
                'params': {'symbol': '{symbol_base}'},
                'priority': 1,
                'weight': 13,
                'signal_value': 'high',
                'description': 'Market stress and reversal indicators'
            },
            'trend_indicator_v3': {
                'url': '/trend-indicator-v3/',
                'params': {},
                'priority': 1,
                'weight': 12,
                'signal_value': 'high',
                'description': 'Advanced trend analysis and momentum'
            },
            'ohlcv': {
                'url': '/ohlcv/',
                'params': {'e': 'binance', 'pair': '{symbol}', 'timeframe': '1h'},
                'priority': 1,
                'weight': 11,
                'signal_value': 'high',
                'description': 'Foundation price data for technical analysis'
            },
            
            # TIER 2: Supporting Analysis
            'ai_screener': {
                'url': '/ai-screener/',
                'params': {'type': 'full'},
                'priority': 2,
                'weight': 10,
                'signal_value': 'medium',
                'description': 'AI-driven comprehensive market analysis'
            },
            'ai_screener_analysis': {
                'url': '/ai-screener-analysis/',
                'params': {'symbol': '{symbol_base}'},
                'priority': 2,
                'weight': 9,
                'signal_value': 'medium',
                'description': 'Symbol-specific AI analysis and recommendations'
            },
            'large_trades_activity': {
                'url': '/large-trades-activity/',
                'params': {'e': 'binance', 'pair': '{symbol}'},
                'priority': 2,
                'weight': 8,
                'signal_value': 'medium',
                'description': 'Institutional activity and market impact'
            },
            'xtrades': {
                'url': '/xtrades/',
                'params': {'e': 'binance', 'symbol': '{symbol_base}'},
                'priority': 2,
                'weight': 7,
                'signal_value': 'medium',
                'description': 'Whale trades and large transaction tracking'
            },
            'volatility_index': {
                'url': '/volatility-index/',
                'params': {'e': 'binance', 'timeframe': '1h'},
                'priority': 2,
                'weight': 6,
                'signal_value': 'medium',
                'description': 'Market volatility measurement and risk assessment'
            },
            
            # TIER 3: Market Context
            'rapid_movements': {
                'url': '/rapid-movements/',
                'params': {},
                'priority': 3,
                'weight': 5,
                'signal_value': 'low',
                'description': 'Sudden price movement and breakout detection'
            },
            'tickerlist_pro': {
                'url': '/tickerlist-pro/',
                'params': {'e': 'binance'},
                'priority': 3,
                'weight': 4,
                'signal_value': 'low',
                'description': 'Comprehensive market data for context'
            },
            '24h_trade_volume_v2': {
                'url': '/24h-trade-volume-v2/',
                'params': {'pair': '{symbol}', 'e': 'binance'},
                'priority': 3,
                'weight': 3,
                'signal_value': 'low',
                'description': 'Trading volume analysis and patterns'
            },
            'coinlist': {
                'url': '/coinlist/',
                'params': {'e': 'binance'},
                'priority': 3,
                'weight': 2,
                'signal_value': 'low',
                'description': 'Available trading pairs and market structure'
            },
            'cryptocurrency_info': {
                'url': '/cryptocurrency-info/',
                'params': {'algorithm': 'DeFi', 'e': 'binance'},
                'priority': 3,
                'weight': 2,
                'signal_value': 'low',
                'description': 'Fundamental cryptocurrency information'
            },
            'coin_info': {
                'url': '/coininfo/',
                'params': {},
                'priority': 3,
                'weight': 1,
                'signal_value': 'low',
                'description': 'General cryptocurrency market data'
            },
            'forex_rates': {
                'url': '/forex-rates/',
                'params': {'source': 'USD'},
                'priority': 3,
                'weight': 1,
                'signal_value': 'low',
                'description': 'Currency conversion rates for global context'
            },
            'ticker': {
                'url': '/ticker/',
                'params': {'e': 'binance', 'pair': '{symbol}'},
                'priority': 3,
                'weight': 1,
                'signal_value': 'low',
                'description': 'Real-time ticker information'
            }
        }
    
    def get_learning_agent(self, symbol: str) -> SymbolLearningAgent:
        """Get or create symbol-specific learning agent"""
        if symbol not in self.learning_agents:
            self.learning_agents[symbol] = SymbolLearningAgent(symbol)
            logger.info(f"Created new learning agent for {symbol}")
        return self.learning_agents[symbol]
    
    async def analyze_symbol_complete(self, symbol: str) -> Dict[str, Any]:
        """Complete symbol analysis with learning integration"""
        logger.info(f"Starting unified analysis for {symbol}")
        start_time = time.time()
        
        # Get symbol-specific learning agent
        learning_agent = self.get_learning_agent(symbol)
        
        # Collect data from all endpoints
        endpoint_data = await self._collect_all_endpoint_data(symbol)
        
        # Detect patterns using enhanced detection
        patterns = await self.pattern_detector.detect_patterns(symbol, endpoint_data)
        
        # Filter patterns based on learning
        filtered_patterns = []
        for pattern in patterns:
            if learning_agent.should_generate_signal(pattern):
                filtered_patterns.append(pattern)
            else:
                logger.debug(f"Pattern {pattern.pattern_type} filtered out by learning agent")
        
        # Generate signals from filtered patterns
        signals = []
        for pattern in filtered_patterns:
            signal = await self.signal_generator.generate_signal(symbol, pattern, endpoint_data)
            if signal:
                signals.append(signal)
        
        # Calculate unified score
        unified_score = self._calculate_unified_score(filtered_patterns, endpoint_data, learning_agent)
        
        processing_time = time.time() - start_time
        
        result = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'processing_time': processing_time,
            'endpoint_data': endpoint_data,
            'detected_patterns': len(patterns),
            'filtered_patterns': len(filtered_patterns),
            'generated_signals': len(signals),
            'unified_score': unified_score,
            'signals': signals,
            'learning_agent_summary': learning_agent.get_performance_summary(),
            'recommendation': self._generate_recommendation(unified_score, signals)
        }
        
        logger.info(f"Completed unified analysis for {symbol}: "
                   f"score={unified_score:.1f}%, signals={len(signals)}, time={processing_time:.2f}s")
        
        return result
    
    async def _collect_all_endpoint_data(self, symbol: str) -> Dict[str, Any]:
        """Collect data from all endpoints with proper rate limiting"""
        endpoint_data = {}
        successful_endpoints = 0
        
        for endpoint_name, config in self.endpoints.items():
            try:
                # Prepare parameters with symbol substitution
                params = self._substitute_symbol_params(config['params'], symbol)
                
                # Make API request
                success, data, processing_time = await self._make_request(
                    config['url'], params, endpoint_name
                )
                
                if success:
                    endpoint_data[endpoint_name] = {
                        'data': data,
                        'success': True,
                        'processing_time': processing_time,
                        'priority': config['priority'],
                        'weight': config['weight']
                    }
                    successful_endpoints += 1
                else:
                    endpoint_data[endpoint_name] = {
                        'data': None,
                        'success': False,
                        'error': data,
                        'processing_time': processing_time,
                        'priority': config['priority'],
                        'weight': config['weight']
                    }
                
                # Rate limiting - CRITICAL as per guides
                await asyncio.sleep(self.rate_limit)
                
            except Exception as e:
                logger.error(f"Error collecting data from {endpoint_name}: {e}")
                endpoint_data[endpoint_name] = {
                    'data': None,
                    'success': False,
                    'error': str(e),
                    'processing_time': 0,
                    'priority': config['priority'],
                    'weight': config['weight']
                }
        
        logger.info(f"Collected data from {successful_endpoints}/{len(self.endpoints)} endpoints for {symbol}")
        return endpoint_data
    
    def _substitute_symbol_params(self, params: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Substitute symbol placeholders in parameters"""
        substituted = params.copy()
        symbol_base = symbol.split('-')[0] if '-' in symbol else symbol.split('/')[0]
        
        for key, value in substituted.items():
            if isinstance(value, str):
                value = value.replace('{symbol}', symbol)
                value = value.replace('{symbol_base}', symbol_base.lower())
                substituted[key] = value
        
        return substituted
    
    async def _make_request(self, url: str, params: Dict[str, Any], endpoint_name: str) -> Tuple[bool, Any, float]:
        """Make API request with enhanced error handling"""
        start_time = time.time()
        
        try:
            full_url = f"{self.base_url}{url}"
            params['api_key'] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                async with session.get(full_url, params=params, timeout=10) as response:
                    processing_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return True, data, processing_time
                    else:
                        error_text = await response.text()
                        return False, f"HTTP {response.status}: {error_text}", processing_time
                        
        except Exception as e:
            processing_time = time.time() - start_time
            return False, str(e), processing_time
    
    def _calculate_unified_score(self, patterns: List[Pattern], endpoint_data: Dict[str, Any], 
                                learning_agent: SymbolLearningAgent) -> float:
        """Calculate unified score incorporating learning weights"""
        if not patterns:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for pattern in patterns:
            # Get learned weight for this pattern type
            learned_weight = learning_agent.pattern_weights.get(pattern.pattern_type, 1.0)
            
            # Calculate pattern contribution
            pattern_score = pattern.strength * pattern.confidence * learned_weight
            pattern_weight = pattern.weight * learned_weight
            
            total_weighted_score += pattern_score * pattern_weight
            total_weight += pattern_weight
        
        if total_weight == 0:
            return 0.0
        
        # Normalize to 0-100 scale
        unified_score = (total_weighted_score / total_weight) * 100
        return min(100.0, max(0.0, unified_score))
    
    def _generate_recommendation(self, score: float, signals: List[TradingSignal]) -> Dict[str, Any]:
        """Generate trading recommendation based on unified analysis"""
        if score >= 75:
            action = "STRONG_BUY" if any(s.direction == 'bullish' for s in signals) else "STRONG_SELL"
            confidence = "HIGH"
        elif score >= 60:
            action = "BUY" if any(s.direction == 'bullish' for s in signals) else "SELL"
            confidence = "MEDIUM"
        elif score >= 40:
            action = "WEAK_BUY" if any(s.direction == 'bullish' for s in signals) else "WEAK_SELL"
            confidence = "LOW"
        else:
            action = "HOLD"
            confidence = "VERY_LOW"
        
        return {
            'action': action,
            'confidence': confidence,
            'score': score,
            'signal_count': len(signals),
            'risk_level': 'HIGH' if score > 80 or score < 20 else 'MEDIUM' if score > 60 or score < 40 else 'LOW'
        }
    
    async def track_signal_outcome(self, signal: TradingSignal, outcome_data: Dict[str, Any]) -> SignalOutcome:
        """Track signal outcome and update learning"""
        outcome = SignalOutcome(
            signal_id=signal.signal_id,
            outcome_type=outcome_data['outcome_type'],
            timeframe=outcome_data['timeframe'],
            actual_return=outcome_data['actual_return'],
            time_to_outcome=timedelta(seconds=outcome_data['time_to_outcome']),
            max_favorable_excursion=outcome_data.get('max_favorable', 0.0),
            max_adverse_excursion=outcome_data.get('max_adverse', 0.0),
            pattern_attribution=outcome_data.get('pattern_attribution', {}),
            market_conditions_at_exit=outcome_data.get('market_conditions', {})
        )
        
        # Update learning agent
        learning_agent = self.get_learning_agent(signal.symbol)
        learning_agent.update_pattern_performance(outcome)
        
        logger.info(f"Tracked outcome for signal {signal.signal_id}: {outcome.outcome_type}")
        return outcome
    
    def get_system_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive system performance summary"""
        summary = {
            'total_symbols': len(self.learning_agents),
            'total_endpoints': len(self.endpoints),
            'learning_agents': {},
            'system_metrics': {
                'avg_success_rate': 0.0,
                'total_signals_processed': 0,
                'best_performing_patterns': {},
                'worst_performing_patterns': {}
            }
        }
        
        total_success_rates = []
        total_signals = 0
        all_pattern_performance = {}
        
        for symbol, agent in self.learning_agents.items():
            agent_summary = agent.get_performance_summary()
            summary['learning_agents'][symbol] = agent_summary
            
            # Aggregate metrics
            for pattern_type, perf in agent.pattern_performance.items():
                total_signals += perf['total_signals']
                total_success_rates.append(perf['success_rate'])
                
                if pattern_type not in all_pattern_performance:
                    all_pattern_performance[pattern_type] = []
                all_pattern_performance[pattern_type].append(perf['success_rate'])
        
        # Calculate system-wide metrics
        if total_success_rates:
            summary['system_metrics']['avg_success_rate'] = np.mean(total_success_rates)
        summary['system_metrics']['total_signals_processed'] = total_signals
        
        # Identify best and worst performing patterns
        for pattern_type, success_rates in all_pattern_performance.items():
            avg_success_rate = np.mean(success_rates)
            if avg_success_rate > 0.7:
                summary['system_metrics']['best_performing_patterns'][pattern_type] = avg_success_rate
            elif avg_success_rate < 0.4:
                summary['system_metrics']['worst_performing_patterns'][pattern_type] = avg_success_rate
        
        return summary

# Enhanced Pattern Detection System
class EnhancedPatternDetector:
    """Enhanced pattern detection incorporating guide recommendations"""
    
    def __init__(self):
        self.pattern_types = [
            'volume_divergence',
            'sentiment_extreme', 
            'liquidation_cascade',
            'trend_reversal',
            'momentum_breakout',
            'institutional_accumulation',
            'volatility_compression'
        ]
    
    async def detect_patterns(self, symbol: str, endpoint_data: Dict[str, Any]) -> List[Pattern]:
        """Detect all patterns from endpoint data"""
        patterns = []
        
        for pattern_type in self.pattern_types:
            try:
                pattern = await self._detect_pattern(pattern_type, symbol, endpoint_data)
                if pattern:
                    patterns.append(pattern)
            except Exception as e:
                logger.error(f"Error detecting pattern {pattern_type} for {symbol}: {e}")
        
        return patterns
    
    async def _detect_pattern(self, pattern_type: str, symbol: str, 
                            endpoint_data: Dict[str, Any]) -> Optional[Pattern]:
        """Detect specific pattern type"""
        detector_map = {
            'volume_divergence': self._detect_volume_divergence,
            'sentiment_extreme': self._detect_sentiment_extreme,
            'liquidation_cascade': self._detect_liquidation_cascade,
            'trend_reversal': self._detect_trend_reversal,
            'momentum_breakout': self._detect_momentum_breakout,
            'institutional_accumulation': self._detect_institutional_accumulation,
            'volatility_compression': self._detect_volatility_compression
        }
        
        detector = detector_map.get(pattern_type)
        if detector:
            return await detector(symbol, endpoint_data)
        return None
    
    async def _detect_volume_divergence(self, symbol: str, endpoint_data: Dict[str, Any]) -> Optional[Pattern]:
        """Detect volume flow divergence pattern"""
        volume_data = endpoint_data.get('volume_flow', {}).get('data')
        ohlcv_data = endpoint_data.get('ohlcv', {}).get('data')
        
        if not volume_data or not ohlcv_data:
            return None
        
        # Simplified divergence detection - can be enhanced
        try:
            net_flow = volume_data.get('net_flow', 0)
            price_change = ohlcv_data.get('change_24h', 0)
            
            # Check for divergence
            if (net_flow > 0 and price_change < -2) or (net_flow < 0 and price_change > 2):
                strength = min(1.0, (abs(net_flow) + abs(price_change)) / 100)
                confidence = 0.7
                direction = 'bullish' if net_flow > 0 else 'bearish'
                
                return Pattern(
                    pattern_id=f"{symbol}_volume_divergence_{int(time.time())}",
                    pattern_type='volume_divergence',
                    direction=direction,
                    strength=strength,
                    confidence=confidence,
                    timeframe='1h',
                    detected_at=datetime.now(),
                    market_conditions={'net_flow': net_flow, 'price_change': price_change},
                    contributing_endpoints=['volume_flow', 'ohlcv']
                )
        except Exception as e:
            logger.error(f"Error in volume divergence detection: {e}")
        
        return None
    
    async def _detect_sentiment_extreme(self, symbol: str, endpoint_data: Dict[str, Any]) -> Optional[Pattern]:
        """Detect extreme sentiment positioning"""
        ls_data = endpoint_data.get('ls_ratio', {}).get('data')
        
        if not ls_data:
            return None
        
        try:
            long_pct = ls_data.get('long_percentage', 50)
            
            if long_pct > 80:  # Extreme long positioning
                return Pattern(
                    pattern_id=f"{symbol}_sentiment_extreme_{int(time.time())}",
                    pattern_type='sentiment_extreme',
                    direction='bearish',  # Contrarian signal
                    strength=min(1.0, (long_pct - 80) / 20),
                    confidence=0.8,
                    timeframe='1h',
                    detected_at=datetime.now(),
                    market_conditions={'long_percentage': long_pct},
                    contributing_endpoints=['ls_ratio']
                )
            elif long_pct < 20:  # Extreme short positioning
                return Pattern(
                    pattern_id=f"{symbol}_sentiment_extreme_{int(time.time())}",
                    pattern_type='sentiment_extreme',
                    direction='bullish',  # Contrarian signal
                    strength=min(1.0, (20 - long_pct) / 20),
                    confidence=0.8,
                    timeframe='1h',
                    detected_at=datetime.now(),
                    market_conditions={'long_percentage': long_pct},
                    contributing_endpoints=['ls_ratio']
                )
        except Exception as e:
            logger.error(f"Error in sentiment extreme detection: {e}")
        
        return None
    
    async def _detect_liquidation_cascade(self, symbol: str, endpoint_data: Dict[str, Any]) -> Optional[Pattern]:
        """Detect liquidation cascade patterns"""
        liq_data = endpoint_data.get('liquidation_data_v2', {}).get('data')
        
        if not liq_data:
            return None
        
        try:
            # Simplified cascade detection
            total_liq = liq_data.get('total_liquidations', 0)
            liq_ratio = liq_data.get('long_short_ratio', 1)
            
            if total_liq > 1000000:  # Significant liquidation volume
                direction = 'bullish' if liq_ratio > 2 else 'bearish'  # More shorts liquidated = bullish
                strength = min(1.0, total_liq / 10000000)  # Normalize to 10M
                
                return Pattern(
                    pattern_id=f"{symbol}_liquidation_cascade_{int(time.time())}",
                    pattern_type='liquidation_cascade',
                    direction=direction,
                    strength=strength,
                    confidence=0.75,
                    timeframe='1h',
                    detected_at=datetime.now(),
                    market_conditions={'total_liquidations': total_liq, 'ratio': liq_ratio},
                    contributing_endpoints=['liquidation_data_v2']
                )
        except Exception as e:
            logger.error(f"Error in liquidation cascade detection: {e}")
        
        return None
    
    async def _detect_trend_reversal(self, symbol: str, endpoint_data: Dict[str, Any]) -> Optional[Pattern]:
        """Detect trend reversal patterns"""
        trend_data = endpoint_data.get('trend_indicator_v3', {}).get('data')
        
        if not trend_data:
            return None
        
        try:
            trend_score = trend_data.get('trend_score', 50)
            buy_pressure = trend_data.get('buy_pressure', 50)
            sell_pressure = trend_data.get('sell_pressure', 50)
            
            # Detect potential reversal conditions
            if trend_score < 30 and buy_pressure > 60:  # Oversold with buying pressure
                return Pattern(
                    pattern_id=f"{symbol}_trend_reversal_{int(time.time())}",
                    pattern_type='trend_reversal',
                    direction='bullish',
                    strength=min(1.0, (60 - trend_score) / 60),
                    confidence=0.65,
                    timeframe='1h',
                    detected_at=datetime.now(),
                    market_conditions={'trend_score': trend_score, 'buy_pressure': buy_pressure},
                    contributing_endpoints=['trend_indicator_v3']
                )
            elif trend_score > 70 and sell_pressure > 60:  # Overbought with selling pressure
                return Pattern(
                    pattern_id=f"{symbol}_trend_reversal_{int(time.time())}",
                    pattern_type='trend_reversal',
                    direction='bearish',
                    strength=min(1.0, (trend_score - 40) / 60),
                    confidence=0.65,
                    timeframe='1h',
                    detected_at=datetime.now(),
                    market_conditions={'trend_score': trend_score, 'sell_pressure': sell_pressure},
                    contributing_endpoints=['trend_indicator_v3']
                )
        except Exception as e:
            logger.error(f"Error in trend reversal detection: {e}")
        
        return None
    
    async def _detect_momentum_breakout(self, symbol: str, endpoint_data: Dict[str, Any]) -> Optional[Pattern]:
        """Detect momentum breakout patterns"""
        rapid_data = endpoint_data.get('rapid_movements', {}).get('data')
        volume_data = endpoint_data.get('volume_flow', {}).get('data')
        
        if not rapid_data or not volume_data:
            return None
        
        try:
            # Simplified breakout detection
            price_change = rapid_data.get('price_change_5m', 0)
            volume_surge = volume_data.get('volume_change', 0)
            
            if abs(price_change) > 3 and volume_surge > 50:  # Significant price move with volume
                direction = 'bullish' if price_change > 0 else 'bearish'
                strength = min(1.0, (abs(price_change) + volume_surge) / 100)
                
                return Pattern(
                    pattern_id=f"{symbol}_momentum_breakout_{int(time.time())}",
                    pattern_type='momentum_breakout',
                    direction=direction,
                    strength=strength,
                    confidence=0.7,
                    timeframe='5m',
                    detected_at=datetime.now(),
                    market_conditions={'price_change': price_change, 'volume_surge': volume_surge},
                    contributing_endpoints=['rapid_movements', 'volume_flow']
                )
        except Exception as e:
            logger.error(f"Error in momentum breakout detection: {e}")
        
        return None
    
    async def _detect_institutional_accumulation(self, symbol: str, endpoint_data: Dict[str, Any]) -> Optional[Pattern]:
        """Detect institutional accumulation patterns"""
        whale_data = endpoint_data.get('xtrades', {}).get('data')
        large_trades_data = endpoint_data.get('large_trades_activity', {}).get('data')
        
        if not whale_data and not large_trades_data:
            return None
        
        try:
            # Simplified institutional activity detection
            if whale_data:
                whale_volume = whale_data.get('total_volume', 0)
                whale_buy_ratio = whale_data.get('buy_sell_ratio', 0.5)
            else:
                whale_volume = 0
                whale_buy_ratio = 0.5
            
            if large_trades_data:
                large_volume = large_trades_data.get('total_volume', 0)
                large_buy_ratio = large_trades_data.get('buy_ratio', 0.5)
            else:
                large_volume = 0
                large_buy_ratio = 0.5
            
            total_institutional_volume = whale_volume + large_volume
            avg_buy_ratio = (whale_buy_ratio + large_buy_ratio) / 2
            
            if total_institutional_volume > 1000000 and avg_buy_ratio > 0.6:  # Strong buying
                return Pattern(
                    pattern_id=f"{symbol}_institutional_accumulation_{int(time.time())}",
                    pattern_type='institutional_accumulation',
                    direction='bullish',
                    strength=min(1.0, total_institutional_volume / 10000000),
                    confidence=0.8,
                    timeframe='1h',
                    detected_at=datetime.now(),
                    market_conditions={'institutional_volume': total_institutional_volume, 'buy_ratio': avg_buy_ratio},
                    contributing_endpoints=['xtrades', 'large_trades_activity']
                )
        except Exception as e:
            logger.error(f"Error in institutional accumulation detection: {e}")
        
        return None
    
    async def _detect_volatility_compression(self, symbol: str, endpoint_data: Dict[str, Any]) -> Optional[Pattern]:
        """Detect volatility compression patterns"""
        vol_data = endpoint_data.get('volatility_index', {}).get('data')
        
        if not vol_data:
            return None
        
        try:
            current_vol = vol_data.get('volatility', 50)
            vol_percentile = vol_data.get('volatility_percentile', 50)
            
            # Low volatility often precedes high volatility
            if current_vol < 20 and vol_percentile < 25:
                return Pattern(
                    pattern_id=f"{symbol}_volatility_compression_{int(time.time())}",
                    pattern_type='volatility_compression',
                    direction='neutral',  # Direction uncertain, but movement expected
                    strength=min(1.0, (25 - vol_percentile) / 25),
                    confidence=0.6,
                    timeframe='1h',
                    detected_at=datetime.now(),
                    market_conditions={'volatility': current_vol, 'percentile': vol_percentile},
                    contributing_endpoints=['volatility_index']
                )
        except Exception as e:
            logger.error(f"Error in volatility compression detection: {e}")
        
        return None

# Unified Signal Generation System
class UnifiedSignalGenerator:
    """Unified signal generation with multi-timeframe targets"""
    
    def __init__(self):
        self.timeframes = ['24h', '7d', '30d']  # As recommended by guides
        self.timeframe_multipliers = {
            '24h': 0.5,
            '7d': 1.0,
            '30d': 2.0
        }
    
    async def generate_signal(self, symbol: str, pattern: Pattern, 
                            endpoint_data: Dict[str, Any]) -> Optional[TradingSignal]:
        """Generate trading signal from pattern"""
        try:
            ohlcv_data = endpoint_data.get('ohlcv', {}).get('data', {})
            current_price = ohlcv_data.get('close', 0)
            
            if current_price == 0:
                logger.warning(f"No price data available for {symbol}")
                return None
            
            # Calculate multi-timeframe targets
            targets = {}
            for timeframe in self.timeframes:
                targets[timeframe] = self._calculate_target(pattern, timeframe)
            
            # Generate expected outcomes
            expected_outcomes = self._calculate_expected_outcomes(pattern, targets)
            
            signal = TradingSignal(
                signal_id=f"{symbol}_{pattern.pattern_type}_{int(time.time())}",
                symbol=symbol,
                timestamp=datetime.now(),
                pattern=pattern,
                direction=pattern.direction,
                current_price=current_price,
                targets=targets,
                market_data=endpoint_data,
                expected_outcomes=expected_outcomes
            )
            
            logger.info(f"Generated signal for {symbol}: {pattern.pattern_type} ({pattern.direction})")
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None
    
    def _calculate_target(self, pattern: Pattern, timeframe: str) -> Dict[str, float]:
        """Calculate target, stop loss, and confidence for timeframe"""
        base_target = pattern.strength * 0.02  # 2% per strength point
        multiplier = self.timeframe_multipliers[timeframe]
        
        target_return = base_target * multiplier
        stop_loss = target_return * -0.5  # 50% of target as stop loss
        confidence = pattern.confidence * (1 - (multiplier - 1) * 0.1)  # Reduce confidence for longer timeframes
        
        return {
            'target_return': target_return,
            'stop_loss': stop_loss,
            'confidence': max(0.1, confidence)
        }
    
    def _calculate_expected_outcomes(self, pattern: Pattern, targets: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate expected outcomes for each timeframe"""
        expected_outcomes = {}
        
        for timeframe, target_info in targets.items():
            # Simple expected value calculation
            success_probability = target_info['confidence']
            expected_return = (success_probability * target_info['target_return'] + 
                             (1 - success_probability) * target_info['stop_loss'])
            expected_outcomes[timeframe] = expected_return
        
        return expected_outcomes

# Comprehensive Outcome Tracking System
class ComprehensiveOutcomeTracker:
    """Comprehensive outcome tracking for learning feedback"""
    
    def __init__(self):
        self.tracked_signals: Dict[str, Dict[str, Any]] = {}
    
    def start_tracking_signal(self, signal: TradingSignal):
        """Start tracking a signal's performance"""
        self.tracked_signals[signal.signal_id] = {
            'signal': signal,
            'start_time': datetime.now(),
            'start_price': signal.current_price,
            'max_favorable': 0.0,
            'max_adverse': 0.0,
            'price_history': [(datetime.now(), signal.current_price)]
        }
        logger.info(f"Started tracking signal {signal.signal_id}")
    
    def update_signal_tracking(self, signal_id: str, current_price: float):
        """Update signal tracking with new price data"""
        if signal_id not in self.tracked_signals:
            return
        
        tracking_data = self.tracked_signals[signal_id]
        signal = tracking_data['signal']
        start_price = tracking_data['start_price']
        
        # Calculate current return
        if signal.direction == 'bullish':
            current_return = (current_price - start_price) / start_price
        else:
            current_return = (start_price - current_price) / start_price
        
        # Update max favorable/adverse excursions
        tracking_data['max_favorable'] = max(tracking_data['max_favorable'], current_return)
        tracking_data['max_adverse'] = min(tracking_data['max_adverse'], current_return)
        
        # Add to price history
        tracking_data['price_history'].append((datetime.now(), current_price))
        
        # Check if any targets hit
        for timeframe, target_info in signal.targets.items():
            if current_return >= target_info['target_return']:
                self._finalize_signal_outcome(signal_id, 'success', timeframe, current_return)
                return
            elif current_return <= target_info['stop_loss']:
                self._finalize_signal_outcome(signal_id, 'failure', timeframe, current_return)
                return
    
    def _finalize_signal_outcome(self, signal_id: str, outcome_type: str, 
                                timeframe: str, final_return: float):
        """Finalize signal outcome and remove from tracking"""
        if signal_id not in self.tracked_signals:
            return
        
        tracking_data = self.tracked_signals[signal_id]
        time_to_outcome = datetime.now() - tracking_data['start_time']
        
        outcome_data = {
            'outcome_type': outcome_type,
            'timeframe': timeframe,
            'actual_return': final_return,
            'time_to_outcome': int(time_to_outcome.total_seconds()),
            'max_favorable': tracking_data['max_favorable'],
            'max_adverse': tracking_data['max_adverse'],
            'pattern_attribution': {tracking_data['signal'].pattern.pattern_type: 1.0},
            'market_conditions': {}
        }
        
        logger.info(f"Finalized outcome for {signal_id}: {outcome_type} ({final_return:.3f})")
        
        # Remove from tracking
        del self.tracked_signals[signal_id]
        
        return outcome_data
    
    def get_tracking_summary(self) -> Dict[str, Any]:
        """Get summary of currently tracked signals"""
        return {
            'total_tracked': len(self.tracked_signals),
            'tracked_signals': list(self.tracked_signals.keys()),
            'avg_tracking_time': self._calculate_avg_tracking_time()
        }
    
    def _calculate_avg_tracking_time(self) -> float:
        """Calculate average tracking time for active signals"""
        if not self.tracked_signals:
            return 0.0
        
        total_time = 0.0
        for tracking_data in self.tracked_signals.values():
            time_diff = datetime.now() - tracking_data['start_time']
            total_time += time_diff.total_seconds()
        
        return total_time / len(self.tracked_signals)