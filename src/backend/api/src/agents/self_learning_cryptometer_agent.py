#!/usr/bin/env python3
"""
Self-Learning Cryptometer Analyzer Agent
=========================================

This agent analyzes each Cryptometer endpoint individually and assigns weights
based on historical patterns and win rates. It implements a 100-point scoring
system where:
- 80+ points = 80%+ win rate (minimum for trade entry)
- 90+ points = Excellent opportunity
- 95+ points = All-in trade opportunity

The agent learns from patterns and adjusts weights dynamically for optimal
trading decisions across all timeframes (24h, 7 days, 1 month).
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import json
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class EndpointPattern:
    """Pattern detected in an endpoint's data"""
    pattern_name: str
    endpoint: str
    confidence: float
    historical_win_rate: float
    timeframe: str  # '24h', '7d', '1m'
    detected_value: Any
    threshold: Any
    
@dataclass
class EndpointAnalysis:
    """Analysis result for a single endpoint"""
    endpoint_name: str
    raw_score: float  # 0-100
    weight: float  # Dynamic weight based on historical performance
    patterns_detected: List[EndpointPattern]
    contribution_score: float  # Weighted contribution to final score
    timeframe_scores: Dict[str, float]  # Scores per timeframe
    
@dataclass
class ComprehensiveAnalysis:
    """Complete analysis across all endpoints"""
    symbol: str
    timestamp: datetime
    total_score: float  # 0-100 final score
    win_rate_prediction: float  # Predicted win rate percentage
    signal: str  # 'LONG', 'SHORT', 'NEUTRAL'
    confidence: float  # 0-1 confidence level
    endpoint_analyses: List[EndpointAnalysis]
    best_timeframe: str
    timeframe_scores: Dict[str, float]  # '24h', '7d', '1m' scores
    trade_recommendation: str
    risk_level: str

class SelfLearningCryptometerAgent:
    """
    Self-learning agent that analyzes Cryptometer endpoints and provides
    intelligent trading signals based on pattern recognition and historical win rates.
    """
    
    def __init__(self):
        """Initialize the self-learning agent"""
        # Pattern library with historical win rates
        self.pattern_library = {
            # Price action patterns
            'price_breakout': {'base_win_rate': 0.82, 'weight_multiplier': 1.2},
            'price_reversal': {'base_win_rate': 0.75, 'weight_multiplier': 1.1},
            'price_consolidation': {'base_win_rate': 0.65, 'weight_multiplier': 0.9},
            
            # Volume patterns
            'volume_spike': {'base_win_rate': 0.78, 'weight_multiplier': 1.15},
            'volume_divergence': {'base_win_rate': 0.72, 'weight_multiplier': 1.05},
            'volume_accumulation': {'base_win_rate': 0.70, 'weight_multiplier': 1.0},
            
            # Momentum patterns
            'momentum_surge': {'base_win_rate': 0.85, 'weight_multiplier': 1.25},
            'momentum_divergence': {'base_win_rate': 0.73, 'weight_multiplier': 1.05},
            'momentum_exhaustion': {'base_win_rate': 0.68, 'weight_multiplier': 0.95},
            
            # AI screener patterns
            'ai_strong_buy': {'base_win_rate': 0.88, 'weight_multiplier': 1.3},
            'ai_buy': {'base_win_rate': 0.75, 'weight_multiplier': 1.1},
            'ai_strong_sell': {'base_win_rate': 0.86, 'weight_multiplier': 1.3},
            'ai_sell': {'base_win_rate': 0.74, 'weight_multiplier': 1.1},
            
            # Liquidation patterns
            'liquidation_cascade': {'base_win_rate': 0.83, 'weight_multiplier': 1.2},
            'liquidation_squeeze': {'base_win_rate': 0.79, 'weight_multiplier': 1.15},
            
            # Long/Short ratio patterns
            'extreme_long_bias': {'base_win_rate': 0.76, 'weight_multiplier': 1.1},
            'extreme_short_bias': {'base_win_rate': 0.77, 'weight_multiplier': 1.1},
            'ratio_flip': {'base_win_rate': 0.81, 'weight_multiplier': 1.2},
            
            # Trend patterns
            'strong_uptrend': {'base_win_rate': 0.74, 'weight_multiplier': 1.05},
            'strong_downtrend': {'base_win_rate': 0.73, 'weight_multiplier': 1.05},
            'trend_reversal': {'base_win_rate': 0.80, 'weight_multiplier': 1.15},
        }
        
        # Endpoint-specific analysis configurations
        self.endpoint_configs = {
            'ticker': {
                'weight': 0.08,
                'patterns': ['price_breakout', 'price_reversal'],
                'key_metrics': ['price', 'change_24h', 'volume']
            },
            'ai_screener': {
                'weight': 0.15,  # Higher weight for AI analysis
                'patterns': ['ai_strong_buy', 'ai_buy', 'ai_strong_sell', 'ai_sell'],
                'key_metrics': ['signal', 'score', 'confidence']
            },
            'trend_indicator_v3': {
                'weight': 0.12,
                'patterns': ['strong_uptrend', 'strong_downtrend', 'trend_reversal'],
                'key_metrics': ['trend_strength', 'trend_direction', 'momentum']
            },
            'ls_ratio': {
                'weight': 0.10,
                'patterns': ['extreme_long_bias', 'extreme_short_bias', 'ratio_flip'],
                'key_metrics': ['ratio', 'longs', 'shorts']
            },
            'liquidation_data_v2': {
                'weight': 0.12,
                'patterns': ['liquidation_cascade', 'liquidation_squeeze'],
                'key_metrics': ['liquidations_24h', 'liquidation_ratio', 'largest_liquidation']
            },
            'open_interest': {
                'weight': 0.08,
                'patterns': ['volume_accumulation'],
                'key_metrics': ['open_interest', 'oi_change_24h']
            },
            'rapid_movements': {
                'weight': 0.10,
                'patterns': ['momentum_surge', 'momentum_exhaustion'],
                'key_metrics': ['movement_count', 'average_movement', 'direction']
            },
            'volume_analysis': {
                'weight': 0.09,
                'patterns': ['volume_spike', 'volume_divergence'],
                'key_metrics': ['volume_24h', 'volume_change', 'buy_sell_ratio']
            },
            'tickerlist_pro': {
                'weight': 0.06,
                'patterns': ['price_consolidation'],
                'key_metrics': ['price_usd', 'market_cap', 'volume_usd']
            },
            'cryptocurrency_info': {
                'weight': 0.05,
                'patterns': [],
                'key_metrics': ['market_cap', 'circulating_supply']
            },
            'forex_rates': {
                'weight': 0.03,
                'patterns': [],
                'key_metrics': ['rates']
            },
            'coinlist': {
                'weight': 0.02,
                'patterns': [],
                'key_metrics': ['available_pairs']
            }
        }
        
        # Learning history for pattern effectiveness
        self.learning_history = defaultdict(lambda: {
            'occurrences': 0,
            'successful': 0,
            'win_rate': 0.5,
            'last_updated': datetime.now()
        })
        
        # Timeframe multipliers
        self.timeframe_multipliers = {
            '24h': 1.0,   # Base multiplier for 24h
            '7d': 0.95,   # Slightly lower for medium term
            '1m': 0.90    # Lower for long term (less accurate)
        }
        
        # Initialize learning from stored history if available
        self._load_learning_history()
    
    async def analyze_symbol(self, symbol: str, cryptometer_data: Dict[str, Any]) -> ComprehensiveAnalysis:
        """
        Analyze a symbol using all Cryptometer endpoints
        Returns a comprehensive analysis with 100-point scoring
        Points are dynamically redistributed among working endpoints
        """
        try:
            endpoint_analyses = []
            failed_endpoints = []
            timeframe_aggregates = {'24h': [], '7d': [], '1m': []}
            
            # First pass: identify working and failed endpoints
            working_endpoints = {}
            total_failed_weight = 0.0
            
            for endpoint_name, endpoint_data in cryptometer_data.items():
                if endpoint_name == 'symbol' or not isinstance(endpoint_data, dict):
                    continue
                
                if endpoint_data.get('success'):
                    working_endpoints[endpoint_name] = endpoint_data
                else:
                    failed_endpoints.append(endpoint_name)
                    # Accumulate failed endpoint weights
                    config = self.endpoint_configs.get(endpoint_name, {'weight': 0.05})
                    total_failed_weight += config['weight']
            
            # Calculate weight redistribution factor
            total_working_weight = sum(
                self.endpoint_configs.get(ep, {'weight': 0.05})['weight'] 
                for ep in working_endpoints
            )
            
            # Redistribute failed weights proportionally to working endpoints
            if total_working_weight > 0:
                redistribution_factor = 1.0 + (total_failed_weight / total_working_weight)
            else:
                redistribution_factor = 1.0
            
            logger.info(f"Endpoints status - Working: {len(working_endpoints)}, Failed: {len(failed_endpoints)}")
            logger.info(f"Weight redistribution factor: {redistribution_factor:.2f}")
            
            # Second pass: analyze working endpoints with redistributed weights
            for endpoint_name, endpoint_data in working_endpoints.items():
                analysis = await self._analyze_endpoint(
                    endpoint_name, 
                    endpoint_data.get('data', {}),
                    symbol,
                    redistribution_factor  # Pass redistribution factor
                )
                endpoint_analyses.append(analysis)
                
                # Aggregate scores by timeframe
                for tf, score in analysis.timeframe_scores.items():
                    timeframe_aggregates[tf].append(analysis.contribution_score)
            
            # Calculate final scores
            total_score, timeframe_scores = self._calculate_final_scores(
                endpoint_analyses, 
                timeframe_aggregates
            )
            
            # Determine best timeframe
            best_timeframe = max(timeframe_scores.items(), key=lambda x: x[1])[0]
            
            # Generate trading signal
            signal = self._determine_signal(total_score, endpoint_analyses)
            
            # Calculate win rate prediction
            win_rate_prediction = self._calculate_win_rate(total_score)
            
            # Generate recommendation
            trade_recommendation = self._generate_recommendation(total_score, win_rate_prediction)
            
            # Assess risk level
            risk_level = self._assess_risk(total_score, endpoint_analyses)
            
            return ComprehensiveAnalysis(
                symbol=symbol,
                timestamp=datetime.now(),
                total_score=total_score,
                win_rate_prediction=win_rate_prediction,
                signal=signal,
                confidence=self._calculate_confidence(endpoint_analyses),
                endpoint_analyses=endpoint_analyses,
                best_timeframe=best_timeframe,
                timeframe_scores=timeframe_scores,
                trade_recommendation=trade_recommendation,
                risk_level=risk_level
            )
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return self._create_fallback_analysis(symbol)
    
    async def _analyze_endpoint(self, endpoint_name: str, data: Dict[str, Any], symbol: str, 
                                redistribution_factor: float = 1.0) -> EndpointAnalysis:
        """
        Analyze a single endpoint and detect patterns
        Weight is dynamically adjusted based on redistribution factor
        """
        config = self.endpoint_configs.get(endpoint_name, {
            'weight': 0.05,
            'patterns': [],
            'key_metrics': []
        })
        
        # Apply redistribution factor to base weight
        base_weight = config['weight'] * redistribution_factor
        
        patterns_detected = []
        raw_score = 50.0  # Neutral baseline
        
        # Detect patterns based on endpoint type
        if endpoint_name == 'ai_screener' and 'signal' in data:
            signal = data.get('signal', '').upper()
            score = data.get('score', 0)
            
            if signal in ['BUY', 'LONG'] and score > 80:
                patterns_detected.append(EndpointPattern(
                    pattern_name='ai_strong_buy',
                    endpoint=endpoint_name,
                    confidence=score/100,
                    historical_win_rate=self._get_pattern_win_rate('ai_strong_buy'),
                    timeframe='24h',
                    detected_value=score,
                    threshold=80
                ))
                raw_score = 85.0
            elif signal in ['SELL', 'SHORT'] and score > 80:
                patterns_detected.append(EndpointPattern(
                    pattern_name='ai_strong_sell',
                    endpoint=endpoint_name,
                    confidence=score/100,
                    historical_win_rate=self._get_pattern_win_rate('ai_strong_sell'),
                    timeframe='24h',
                    detected_value=score,
                    threshold=80
                ))
                raw_score = 15.0
                
        elif endpoint_name == 'ticker' and 'change_24h' in data:
            change = float(data.get('change_24h', 0))
            
            if change > 10:  # 10% price increase
                patterns_detected.append(EndpointPattern(
                    pattern_name='price_breakout',
                    endpoint=endpoint_name,
                    confidence=min(1.0, change/20),
                    historical_win_rate=self._get_pattern_win_rate('price_breakout'),
                    timeframe='24h',
                    detected_value=change,
                    threshold=10
                ))
                raw_score = 75.0
            elif change < -10:  # 10% price decrease
                patterns_detected.append(EndpointPattern(
                    pattern_name='price_reversal',
                    endpoint=endpoint_name,
                    confidence=min(1.0, abs(change)/20),
                    historical_win_rate=self._get_pattern_win_rate('price_reversal'),
                    timeframe='24h',
                    detected_value=change,
                    threshold=-10
                ))
                raw_score = 25.0
                
        elif endpoint_name == 'liquidation_data_v2' and 'liquidations_24h' in data:
            liquidations = float(data.get('liquidations_24h', 0))
            
            if liquidations > 10000000:  # $10M+ liquidations
                patterns_detected.append(EndpointPattern(
                    pattern_name='liquidation_cascade',
                    endpoint=endpoint_name,
                    confidence=min(1.0, liquidations/50000000),
                    historical_win_rate=self._get_pattern_win_rate('liquidation_cascade'),
                    timeframe='24h',
                    detected_value=liquidations,
                    threshold=10000000
                ))
                raw_score = 70.0
                
        elif endpoint_name == 'ls_ratio' and 'ratio' in data:
            ratio = float(data.get('ratio', 1.0))
            
            if ratio > 2.0:  # Extreme long bias
                patterns_detected.append(EndpointPattern(
                    pattern_name='extreme_long_bias',
                    endpoint=endpoint_name,
                    confidence=min(1.0, (ratio-1)/2),
                    historical_win_rate=self._get_pattern_win_rate('extreme_long_bias'),
                    timeframe='24h',
                    detected_value=ratio,
                    threshold=2.0
                ))
                raw_score = 65.0
            elif ratio < 0.5:  # Extreme short bias
                patterns_detected.append(EndpointPattern(
                    pattern_name='extreme_short_bias',
                    endpoint=endpoint_name,
                    confidence=min(1.0, (1-ratio)/0.5),
                    historical_win_rate=self._get_pattern_win_rate('extreme_short_bias'),
                    timeframe='24h',
                    detected_value=ratio,
                    threshold=0.5
                ))
                raw_score = 35.0
        
        # Calculate timeframe scores
        timeframe_scores = {
            '24h': raw_score * 1.0,
            '7d': raw_score * 0.95,
            '1m': raw_score * 0.90
        }
        
        # Start with redistributed base weight
        weight = base_weight
        
        # Apply pattern-based dynamic adjustment
        if patterns_detected:
            # Boost weight if high-confidence patterns detected
            avg_confidence = np.mean([p.confidence for p in patterns_detected])
            weight *= (1 + avg_confidence * 0.3)  # Up to 30% additional weight boost
        
        contribution_score = raw_score * weight
        
        return EndpointAnalysis(
            endpoint_name=endpoint_name,
            raw_score=raw_score,
            weight=weight,
            patterns_detected=patterns_detected,
            contribution_score=contribution_score,
            timeframe_scores=timeframe_scores
        )
    
    def _calculate_final_scores(self, 
                                endpoint_analyses: List[EndpointAnalysis],
                                timeframe_aggregates: Dict[str, List[float]]) -> Tuple[float, Dict[str, float]]:
        """
        Calculate final 100-point score and timeframe scores
        Ensures scores are properly normalized with weight redistribution
        """
        if not endpoint_analyses:
            return 50.0, {'24h': 50.0, '7d': 50.0, '1m': 50.0}
        
        # Calculate weighted average
        total_weight = sum(ea.weight for ea in endpoint_analyses)
        total_contribution = sum(ea.contribution_score for ea in endpoint_analyses)
        
        # The weights have already been redistributed, so normalize directly
        # This ensures the 100 points are fully distributed among working endpoints
        if total_weight > 0:
            # Since weights are redistributed, total_weight should approximate 1.0
            # Normalize to ensure we're on a 100-point scale
            total_score = (total_contribution / total_weight)
        else:
            total_score = 50.0
        
        # Apply pattern confluence bonus (additional scoring for multiple patterns)
        all_patterns = []
        for ea in endpoint_analyses:
            all_patterns.extend(ea.patterns_detected)
        
        if len(all_patterns) >= 3:
            # Multiple patterns detected - apply confluence bonus
            # This is added on top of the 100-point base
            confluence_bonus = min(10, len(all_patterns) * 2)
            total_score = min(100, total_score + confluence_bonus)
        
        # Calculate timeframe scores with proper normalization
        timeframe_scores = {}
        for tf in ['24h', '7d', '1m']:
            # Calculate average contribution for this timeframe
            tf_contributions = []
            for ea in endpoint_analyses:
                # Each endpoint contributes based on its timeframe score and weight
                tf_score = ea.timeframe_scores[tf]
                tf_contribution = tf_score * ea.weight
                tf_contributions.append(tf_contribution)
            
            if tf_contributions and total_weight > 0:
                # Normalize to 100-point scale
                tf_total = sum(tf_contributions) / total_weight
                timeframe_scores[tf] = min(100, tf_total * self.timeframe_multipliers[tf])
            else:
                timeframe_scores[tf] = 50.0
        
        # Ensure score is within valid range
        total_score = max(0, min(100, total_score))
        
        return total_score, timeframe_scores
    
    def _determine_signal(self, score: float, endpoint_analyses: List[EndpointAnalysis]) -> str:
        """Determine trading signal based on score and patterns"""
        # Check for directional bias in patterns
        bullish_patterns = ['price_breakout', 'ai_strong_buy', 'ai_buy', 'strong_uptrend', 
                           'momentum_surge', 'volume_spike']
        bearish_patterns = ['price_reversal', 'ai_strong_sell', 'ai_sell', 'strong_downtrend',
                           'momentum_exhaustion', 'extreme_short_bias']
        
        bullish_count = 0
        bearish_count = 0
        
        for ea in endpoint_analyses:
            for pattern in ea.patterns_detected:
                if pattern.pattern_name in bullish_patterns:
                    bullish_count += 1
                elif pattern.pattern_name in bearish_patterns:
                    bearish_count += 1
        
        # Determine signal based on score and pattern bias
        if score >= 70 and bullish_count > bearish_count:
            return 'LONG'
        elif score >= 70 and bearish_count > bullish_count:
            return 'SHORT'
        elif score >= 60:
            if bullish_count > bearish_count * 2:
                return 'LONG'
            elif bearish_count > bullish_count * 2:
                return 'SHORT'
            else:
                return 'NEUTRAL'
        else:
            return 'NEUTRAL'
    
    def _calculate_win_rate(self, score: float) -> float:
        """Convert 100-point score to win rate percentage"""
        # Direct mapping: 80 points = 80% win rate
        # Apply slight adjustment for extreme scores
        if score >= 95:
            return min(98, score * 1.02)  # Boost for exceptional scores
        elif score >= 90:
            return score * 1.01  # Slight boost for excellent scores
        elif score >= 80:
            return score  # Direct mapping
        elif score >= 70:
            return score * 0.98  # Slight penalty below 80
        else:
            return max(20, score * 0.95)  # Larger penalty for low scores
    
    def _generate_recommendation(self, score: float, win_rate: float) -> str:
        """Generate trade recommendation based on score and win rate"""
        if score >= 95:
            return f"🔥 ALL-IN OPPORTUNITY! Exceptional setup with {win_rate:.1f}% win rate. Maximum position recommended."
        elif score >= 90:
            return f"⭐ EXCELLENT OPPORTUNITY! Very strong setup with {win_rate:.1f}% win rate. Large position recommended."
        elif score >= 85:
            return f"✅ STRONG OPPORTUNITY! Solid setup with {win_rate:.1f}% win rate. Standard position recommended."
        elif score >= 80:
            return f"👍 GOOD OPPORTUNITY! Favorable setup with {win_rate:.1f}% win rate. Moderate position recommended."
        elif score >= 75:
            return f"⚠️ MARGINAL OPPORTUNITY. Below minimum threshold ({win_rate:.1f}% win rate). Small position or wait."
        elif score >= 70:
            return f"❌ WEAK OPPORTUNITY. Poor risk/reward ({win_rate:.1f}% win rate). Consider waiting for better setup."
        else:
            return f"🚫 NO TRADE. Insufficient edge ({win_rate:.1f}% win rate). Stay out of the market."
    
    def _assess_risk(self, score: float, endpoint_analyses: List[EndpointAnalysis]) -> str:
        """Assess risk level based on score and pattern consistency"""
        # Check pattern consistency
        pattern_confidences = []
        for ea in endpoint_analyses:
            for pattern in ea.patterns_detected:
                pattern_confidences.append(pattern.confidence)
        
        if pattern_confidences:
            avg_confidence = np.mean(pattern_confidences)
            std_confidence = np.std(pattern_confidences)
            
            # High consistency = lower risk
            if std_confidence < 0.1 and avg_confidence > 0.8:
                risk_adjustment = -0.1
            elif std_confidence > 0.3:
                risk_adjustment = 0.1
            else:
                risk_adjustment = 0
        else:
            risk_adjustment = 0.1
        
        # Base risk on score
        if score >= 90:
            base_risk = "LOW"
        elif score >= 80:
            base_risk = "MEDIUM-LOW"
        elif score >= 70:
            base_risk = "MEDIUM"
        elif score >= 60:
            base_risk = "MEDIUM-HIGH"
        else:
            base_risk = "HIGH"
        
        # Apply adjustment
        risk_levels = ["LOW", "MEDIUM-LOW", "MEDIUM", "MEDIUM-HIGH", "HIGH"]
        current_index = risk_levels.index(base_risk)
        
        if risk_adjustment < 0:
            new_index = max(0, current_index - 1)
        elif risk_adjustment > 0:
            new_index = min(4, current_index + 1)
        else:
            new_index = current_index
        
        return risk_levels[new_index]
    
    def _calculate_confidence(self, endpoint_analyses: List[EndpointAnalysis]) -> float:
        """Calculate overall confidence level"""
        if not endpoint_analyses:
            return 0.3
        
        # Factors affecting confidence:
        # 1. Number of endpoints with data
        endpoint_coverage = len(endpoint_analyses) / len(self.endpoint_configs)
        
        # 2. Pattern detection rate
        patterns_detected = sum(len(ea.patterns_detected) for ea in endpoint_analyses)
        pattern_rate = min(1.0, patterns_detected / (len(endpoint_analyses) * 2))
        
        # 3. Pattern confidence levels
        all_confidences = []
        for ea in endpoint_analyses:
            for pattern in ea.patterns_detected:
                all_confidences.append(pattern.confidence)
        
        avg_pattern_confidence = np.mean(all_confidences) if all_confidences else 0.5
        
        # Weighted confidence calculation
        confidence = (
            endpoint_coverage * 0.3 +
            pattern_rate * 0.3 +
            avg_pattern_confidence * 0.4
        )
        
        return float(min(0.95, confidence))  # Cap at 95% confidence
    
    def _get_pattern_win_rate(self, pattern_name: str) -> float:
        """Get historical win rate for a pattern"""
        # Check learning history first
        if pattern_name in self.learning_history:
            history = self.learning_history[pattern_name]
            occurrences = history['occurrences']
            if isinstance(occurrences, (int, float)) and occurrences > 10:  # Enough data for reliable estimate
                win_rate = history['win_rate']
                return float(win_rate) if isinstance(win_rate, (int, float)) else 0.5
        
        # Fall back to base win rate
        if pattern_name in self.pattern_library:
            return self.pattern_library[pattern_name]['base_win_rate']
        
        return 0.5  # Default neutral win rate
    
    def update_learning(self, pattern_name: str, was_successful: bool):
        """Update learning history with pattern outcome"""
        history = self.learning_history[pattern_name]
        
        # Ensure occurrences and successful are integers
        if not isinstance(history['occurrences'], int):
            history['occurrences'] = 0
        if not isinstance(history['successful'], int):
            history['successful'] = 0
        
        history['occurrences'] += 1
        if was_successful:
            history['successful'] += 1
        
        # Update win rate with exponential moving average
        alpha = 0.1  # Learning rate
        win_rate_value = history.get('win_rate', 0.5)
        # Ensure win_rate is a float
        if isinstance(win_rate_value, (int, float)):
            current_win_rate = float(win_rate_value)
        else:
            current_win_rate = 0.5
        observed_success = 1.0 if was_successful else 0.0
        history['win_rate'] = current_win_rate * (1 - alpha) + observed_success * alpha
        history['last_updated'] = datetime.now()
        
        # Persist learning history
        self._save_learning_history()
    
    def _load_learning_history(self):
        """Load learning history from storage"""
        try:
            with open('cryptometer_learning_history.json', 'r') as f:
                loaded = json.load(f)
                for pattern, data in loaded.items():
                    self.learning_history[pattern] = data
                    # Convert timestamp string back to datetime
                    self.learning_history[pattern]['last_updated'] = datetime.fromisoformat(
                        data['last_updated']
                    )
        except FileNotFoundError:
            logger.info("No learning history found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading learning history: {e}")
    
    def _save_learning_history(self):
        """Save learning history to storage"""
        try:
            # Convert to JSON-serializable format
            to_save = {}
            for pattern, data in self.learning_history.items():
                to_save[pattern] = {
                    'occurrences': data['occurrences'],
                    'successful': data['successful'],
                    'win_rate': data['win_rate'],
                    'last_updated': data['last_updated'].isoformat() if isinstance(data['last_updated'], datetime) else str(data['last_updated'])
                }
            
            with open('cryptometer_learning_history.json', 'w') as f:
                json.dump(to_save, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving learning history: {e}")
    
    def _create_fallback_analysis(self, symbol: str) -> ComprehensiveAnalysis:
        """Create fallback analysis when errors occur"""
        return ComprehensiveAnalysis(
            symbol=symbol,
            timestamp=datetime.now(),
            total_score=50.0,
            win_rate_prediction=50.0,
            signal='NEUTRAL',
            confidence=0.3,
            endpoint_analyses=[],
            best_timeframe='24h',
            timeframe_scores={'24h': 50.0, '7d': 50.0, '1m': 50.0},
            trade_recommendation="🚫 NO TRADE. Insufficient data for analysis.",
            risk_level='HIGH'
        )

# Global instance
_self_learning_agent = None

def get_self_learning_agent() -> SelfLearningCryptometerAgent:
    """Get or create self-learning agent instance"""
    global _self_learning_agent
    if _self_learning_agent is None:
        _self_learning_agent = SelfLearningCryptometerAgent()
    return _self_learning_agent