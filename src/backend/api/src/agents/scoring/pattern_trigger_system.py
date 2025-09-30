#!/usr/bin/env python3
"""
Pattern-Based Trigger System - ZmartBot
Advanced pattern recognition and rare event detection for win rate correlation

PATTERN-BASED TRIGGER RULES:
1. Big liquidation clusters trigger KingFisher weight boost
2. RiskMetric rare bands (0-0.25, 0.75-1) trigger RiskMetric weight boost
3. Technical analysis rare patterns (golden cross, etc.) trigger Cryptometer weight boost
4. Historical pattern matching with 80%+ win rate triggers trade entry
5. Self-learning from historical data and pattern success rates
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import pandas as pd
from collections import defaultdict
import json

from .win_rate_scoring_standard import win_rate_standard, TradeOpportunity, TimeFrame

logger = logging.getLogger(__name__)

class PatternType(Enum):
    """Types of patterns that can trigger weight adjustments"""
    LIQUIDATION_CLUSTER = "liquidation_cluster"
    RISK_BAND_RARE = "risk_band_rare"
    TECHNICAL_RARE = "technical_rare"
    HISTORICAL_MATCH = "historical_match"
    GOLDEN_CROSS = "golden_cross"
    DEATH_CROSS = "death_cross"
    SUPPORT_BREAK = "support_break"
    RESISTANCE_BREAK = "resistance_break"
    VOLUME_SPIKE = "volume_spike"
    DIVERGENCE = "divergence"

class PatternRarity(Enum):
    """Rarity levels for pattern classification"""
    COMMON = "common"          # Occurs frequently, low weight boost
    UNCOMMON = "uncommon"      # Moderate frequency, medium weight boost
    RARE = "rare"              # Infrequent, high weight boost
    EXCEPTIONAL = "exceptional" # Very rare, maximum weight boost

@dataclass
class PatternSignal:
    """Signal generated from pattern detection"""
    pattern_type: PatternType
    rarity: PatternRarity
    confidence: float  # 0-1
    win_rate_prediction: float  # 0-100
    direction: str  # long/short
    timeframe: str  # 24h/7d/1m
    weight_multiplier: float  # How much to boost agent weight
    reasoning: str
    historical_matches: int
    success_rate: float  # Historical success rate of this pattern
    timestamp: datetime

@dataclass
class PatternAnalysis:
    """Complete pattern analysis result"""
    symbol: str
    kingfisher_patterns: List[PatternSignal]
    cryptometer_patterns: List[PatternSignal]
    riskmetric_patterns: List[PatternSignal]
    combined_signals: List[PatternSignal]
    weight_adjustments: Dict[str, float]  # Agent weight adjustments
    overall_trigger: bool  # Whether to trigger trade entry
    overall_win_rate: float  # Combined win rate from all patterns
    timestamp: datetime

class PatternTriggerSystem:
    """
    Advanced Pattern-Based Trigger System
    
    This system analyzes patterns from all three agents and determines:
    1. When rare events occur that should trigger weight adjustments
    2. Historical pattern matching for win rate prediction
    3. Self-learning from pattern success rates
    4. Trade entry triggers based on pattern confluence
    """
    
    def __init__(self):
        self.system_id = "pattern_trigger_system"
        
        # Pattern history for self-learning
        self.pattern_history = {}  # Dict[str, Dict[str, Any]]
        self.success_rates = defaultdict(float)
        
        # Trigger thresholds
        self.liquidation_cluster_threshold = 0.7  # Minimum cluster strength
        self.risk_band_rare_zones = [(0.0, 0.25), (0.75, 1.0)]  # Rare risk bands
        self.technical_rarity_threshold = 0.8  # Minimum technical rarity
        self.win_rate_trigger_threshold = 80.0  # Minimum win rate to trigger
        
        # Weight multipliers for rare events
        self.weight_multipliers = {
            PatternRarity.COMMON: 1.0,
            PatternRarity.UNCOMMON: 1.3,
            PatternRarity.RARE: 1.7,
            PatternRarity.EXCEPTIONAL: 2.5
        }
        
        # Historical data storage (in production, use database)
        self.historical_data = {}
        
        logger.info("Pattern Trigger System initialized")
    
    async def analyze_patterns(
        self,
        symbol: str,
        kingfisher_data: Optional[Dict[str, Any]] = None,
        cryptometer_data: Optional[Dict[str, Any]] = None,
        riskmetric_data: Optional[Dict[str, Any]] = None,
        current_price: Optional[float] = None,
        historical_prices: Optional[List[Dict[str, Any]]] = None
    ) -> PatternAnalysis:
        """
        Analyze patterns from all agents and determine triggers
        
        Args:
            symbol: Trading symbol
            kingfisher_data: Liquidation cluster data
            cryptometer_data: Technical analysis data
            riskmetric_data: Risk metric data
            current_price: Current market price
            historical_prices: Historical price data for pattern matching
        """
        try:
            timestamp = datetime.now()
            
            # Analyze patterns from each agent
            kingfisher_patterns = await self._analyze_kingfisher_patterns(
                symbol, kingfisher_data, current_price, historical_prices
            )
            
            cryptometer_patterns = await self._analyze_cryptometer_patterns(
                symbol, cryptometer_data, current_price, historical_prices
            )
            
            riskmetric_patterns = await self._analyze_riskmetric_patterns(
                symbol, riskmetric_data, current_price, historical_prices
            )
            
            # Combine all patterns
            all_patterns = kingfisher_patterns + cryptometer_patterns + riskmetric_patterns
            
            # Calculate weight adjustments based on pattern triggers
            weight_adjustments = self._calculate_weight_adjustments(
                kingfisher_patterns, cryptometer_patterns, riskmetric_patterns
            )
            
            # Determine if overall trigger conditions are met
            overall_trigger, overall_win_rate = self._evaluate_trigger_conditions(all_patterns)
            
            # Find significant combined signals
            combined_signals = self._find_combined_signals(all_patterns)
            
            # Create analysis result
            analysis = PatternAnalysis(
                symbol=symbol,
                kingfisher_patterns=kingfisher_patterns,
                cryptometer_patterns=cryptometer_patterns,
                riskmetric_patterns=riskmetric_patterns,
                combined_signals=combined_signals,
                weight_adjustments=weight_adjustments,
                overall_trigger=overall_trigger,
                overall_win_rate=overall_win_rate,
                timestamp=timestamp
            )
            
            # Learn from this analysis
            await self._update_learning_data(analysis)
            
            logger.info(f"🎯 Pattern analysis complete for {symbol}: Trigger={overall_trigger}, Win Rate={overall_win_rate:.1f}%")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing patterns for {symbol}: {e}")
            return self._create_empty_analysis(symbol)
    
    async def _analyze_kingfisher_patterns(
        self,
        symbol: str,
        data: Optional[Dict[str, Any]],
        current_price: Optional[float],
        historical_prices: Optional[List[Dict[str, Any]]]
    ) -> List[PatternSignal]:
        """Analyze KingFisher liquidation patterns"""
        patterns = []
        
        if not data:
            return patterns
        
        try:
            # Analyze liquidation cluster strength
            cluster_strength = data.get('liquidation_cluster_strength', 0.0)
            if cluster_strength >= self.liquidation_cluster_threshold:
                
                # Determine rarity based on cluster strength
                if cluster_strength >= 0.95:
                    rarity = PatternRarity.EXCEPTIONAL
                elif cluster_strength >= 0.85:
                    rarity = PatternRarity.RARE
                elif cluster_strength >= 0.75:
                    rarity = PatternRarity.UNCOMMON
                else:
                    rarity = PatternRarity.COMMON
                
                # Calculate win rate based on historical liquidation cluster performance
                historical_win_rate = await self._get_historical_pattern_win_rate(
                    PatternType.LIQUIDATION_CLUSTER, cluster_strength, historical_prices
                )
                
                # Determine direction based on cluster position
                direction = "long" if data.get('cluster_position', 'below') == 'below' else "short"
                
                pattern = PatternSignal(
                    pattern_type=PatternType.LIQUIDATION_CLUSTER,
                    rarity=rarity,
                    confidence=cluster_strength,
                    win_rate_prediction=historical_win_rate,
                    direction=direction,
                    timeframe="24h",  # Liquidation clusters are typically short-term
                    weight_multiplier=self.weight_multipliers[rarity],
                    reasoning=f"Large liquidation cluster detected (strength: {cluster_strength:.2f}). Historical win rate: {historical_win_rate:.1f}%",
                    historical_matches=data.get('historical_matches', 0),
                    success_rate=historical_win_rate / 100.0,
                    timestamp=datetime.now()
                )
                
                patterns.append(pattern)
                logger.info(f"🎣 KingFisher liquidation cluster pattern: {rarity.value} ({cluster_strength:.2f})")
            
            # Analyze toxic order flow patterns
            toxic_flow = data.get('toxic_order_flow', 0.0)
            if toxic_flow >= 0.7:
                
                rarity = PatternRarity.RARE if toxic_flow >= 0.85 else PatternRarity.UNCOMMON
                historical_win_rate = await self._get_historical_pattern_win_rate(
                    PatternType.VOLUME_SPIKE, toxic_flow, historical_prices
                )
                
                direction = "short" if data.get('flow_direction', 'sell') == 'sell' else "long"
                
                pattern = PatternSignal(
                    pattern_type=PatternType.VOLUME_SPIKE,
                    rarity=rarity,
                    confidence=toxic_flow,
                    win_rate_prediction=historical_win_rate,
                    direction=direction,
                    timeframe="24h",
                    weight_multiplier=self.weight_multipliers[rarity],
                    reasoning=f"Toxic order flow detected (intensity: {toxic_flow:.2f}). Suggests {direction} bias.",
                    historical_matches=data.get('flow_matches', 0),
                    success_rate=historical_win_rate / 100.0,
                    timestamp=datetime.now()
                )
                
                patterns.append(pattern)
                logger.info(f"🎣 KingFisher toxic flow pattern: {direction} ({toxic_flow:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing KingFisher patterns: {e}")
        
        return patterns
    
    async def _analyze_cryptometer_patterns(
        self,
        symbol: str,
        data: Optional[Dict[str, Any]],
        current_price: Optional[float],
        historical_prices: Optional[List[Dict[str, Any]]]
    ) -> List[PatternSignal]:
        """Analyze Cryptometer technical patterns"""
        patterns = []
        
        if not data:
            return patterns
        
        try:
            # Analyze golden cross pattern
            if data.get('golden_cross_detected', False):
                confidence = data.get('golden_cross_confidence', 0.8)
                historical_win_rate = await self._get_historical_pattern_win_rate(
                    PatternType.GOLDEN_CROSS, confidence, historical_prices
                )
                
                pattern = PatternSignal(
                    pattern_type=PatternType.GOLDEN_CROSS,
                    rarity=PatternRarity.RARE,  # Golden cross is rare
                    confidence=confidence,
                    win_rate_prediction=historical_win_rate,
                    direction="long",
                    timeframe="7d",  # Golden cross is medium-term signal
                    weight_multiplier=self.weight_multipliers[PatternRarity.RARE],
                    reasoning=f"Golden cross pattern detected with {confidence:.2f} confidence. Strong bullish signal.",
                    historical_matches=data.get('golden_cross_matches', 0),
                    success_rate=historical_win_rate / 100.0,
                    timestamp=datetime.now()
                )
                
                patterns.append(pattern)
                logger.info(f"📈 Cryptometer golden cross pattern detected")
            
            # Analyze death cross pattern
            if data.get('death_cross_detected', False):
                confidence = data.get('death_cross_confidence', 0.8)
                historical_win_rate = await self._get_historical_pattern_win_rate(
                    PatternType.DEATH_CROSS, confidence, historical_prices
                )
                
                pattern = PatternSignal(
                    pattern_type=PatternType.DEATH_CROSS,
                    rarity=PatternRarity.RARE,
                    confidence=confidence,
                    win_rate_prediction=historical_win_rate,
                    direction="short",
                    timeframe="7d",
                    weight_multiplier=self.weight_multipliers[PatternRarity.RARE],
                    reasoning=f"Death cross pattern detected with {confidence:.2f} confidence. Strong bearish signal.",
                    historical_matches=data.get('death_cross_matches', 0),
                    success_rate=historical_win_rate / 100.0,
                    timestamp=datetime.now()
                )
                
                patterns.append(pattern)
                logger.info(f"📉 Cryptometer death cross pattern detected")
            
            # Analyze support/resistance breaks
            if data.get('support_break', False):
                confidence = data.get('support_break_confidence', 0.7)
                historical_win_rate = await self._get_historical_pattern_win_rate(
                    PatternType.SUPPORT_BREAK, confidence, historical_prices
                )
                
                rarity = PatternRarity.UNCOMMON if confidence >= 0.8 else PatternRarity.COMMON
                
                pattern = PatternSignal(
                    pattern_type=PatternType.SUPPORT_BREAK,
                    rarity=rarity,
                    confidence=confidence,
                    win_rate_prediction=historical_win_rate,
                    direction="short",
                    timeframe="24h",
                    weight_multiplier=self.weight_multipliers[rarity],
                    reasoning=f"Support level break detected. Bearish continuation expected.",
                    historical_matches=data.get('support_break_matches', 0),
                    success_rate=historical_win_rate / 100.0,
                    timestamp=datetime.now()
                )
                
                patterns.append(pattern)
                logger.info(f"📈 Cryptometer support break pattern")
            
            # Analyze resistance breaks
            if data.get('resistance_break', False):
                confidence = data.get('resistance_break_confidence', 0.7)
                historical_win_rate = await self._get_historical_pattern_win_rate(
                    PatternType.RESISTANCE_BREAK, confidence, historical_prices
                )
                
                rarity = PatternRarity.UNCOMMON if confidence >= 0.8 else PatternRarity.COMMON
                
                pattern = PatternSignal(
                    pattern_type=PatternType.RESISTANCE_BREAK,
                    rarity=rarity,
                    confidence=confidence,
                    win_rate_prediction=historical_win_rate,
                    direction="long",
                    timeframe="24h",
                    weight_multiplier=self.weight_multipliers[rarity],
                    reasoning=f"Resistance level break detected. Bullish continuation expected.",
                    historical_matches=data.get('resistance_break_matches', 0),
                    success_rate=historical_win_rate / 100.0,
                    timestamp=datetime.now()
                )
                
                patterns.append(pattern)
                logger.info(f"📈 Cryptometer resistance break pattern")
            
            # Analyze divergence patterns
            if data.get('divergence_detected', False):
                divergence_type = data.get('divergence_type', 'bullish')
                confidence = data.get('divergence_confidence', 0.75)
                
                historical_win_rate = await self._get_historical_pattern_win_rate(
                    PatternType.DIVERGENCE, confidence, historical_prices
                )
                
                direction = "long" if divergence_type == 'bullish' else "short"
                rarity = PatternRarity.RARE  # Divergences are rare and powerful
                
                pattern = PatternSignal(
                    pattern_type=PatternType.DIVERGENCE,
                    rarity=rarity,
                    confidence=confidence,
                    win_rate_prediction=historical_win_rate,
                    direction=direction,
                    timeframe="1m",  # Divergences are longer-term signals
                    weight_multiplier=self.weight_multipliers[rarity],
                    reasoning=f"{divergence_type.title()} divergence detected. Strong reversal signal.",
                    historical_matches=data.get('divergence_matches', 0),
                    success_rate=historical_win_rate / 100.0,
                    timestamp=datetime.now()
                )
                
                patterns.append(pattern)
                logger.info(f"📈 Cryptometer {divergence_type} divergence pattern")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing Cryptometer patterns: {e}")
        
        return patterns
    
    async def _analyze_riskmetric_patterns(
        self,
        symbol: str,
        data: Optional[Dict[str, Any]],
        current_price: Optional[float],
        historical_prices: Optional[List[Dict[str, Any]]]
    ) -> List[PatternSignal]:
        """Analyze RiskMetric rare band patterns"""
        patterns = []
        
        if not data:
            return patterns
        
        try:
            current_risk = data.get('current_risk_level', 0.5)
            time_in_risk = data.get('time_spent_in_risk', 0.0)
            
            # Check if we're in rare risk bands
            in_rare_band = False
            rare_band_type = None
            
            for low, high in self.risk_band_rare_zones:
                if low <= current_risk <= high:
                    in_rare_band = True
                    rare_band_type = "low_risk" if low < 0.5 else "high_risk"
                    break
            
            if in_rare_band:
                # Determine rarity based on time spent in risk band
                if time_in_risk <= 0.1:  # Very short time in risk band
                    rarity = PatternRarity.EXCEPTIONAL
                elif time_in_risk <= 0.2:
                    rarity = PatternRarity.RARE
                elif time_in_risk <= 0.4:
                    rarity = PatternRarity.UNCOMMON
                else:
                    rarity = PatternRarity.COMMON
                
                # Calculate historical win rate for this risk pattern
                historical_win_rate = await self._get_historical_pattern_win_rate(
                    PatternType.RISK_BAND_RARE, current_risk, historical_prices
                )
                
                # Determine direction based on risk band
                if rare_band_type == "low_risk":
                    direction = "long"  # Low risk = good time to buy
                    reasoning = f"Rare low risk band ({current_risk:.3f}) with minimal time spent ({time_in_risk:.2f}). Excellent buying opportunity."
                else:
                    direction = "short"  # High risk = good time to sell/short
                    reasoning = f"Rare high risk band ({current_risk:.3f}) with minimal time spent ({time_in_risk:.2f}). Excellent shorting opportunity."
                
                # Determine timeframe based on risk band position
                if current_risk <= 0.15 or current_risk >= 0.85:
                    timeframe = "1m"  # Extreme risk levels are long-term signals
                else:
                    timeframe = "7d"  # Moderate rare bands are medium-term
                
                pattern = PatternSignal(
                    pattern_type=PatternType.RISK_BAND_RARE,
                    rarity=rarity,
                    confidence=1.0 - time_in_risk,  # Higher confidence with less time in band
                    win_rate_prediction=historical_win_rate,
                    direction=direction,
                    timeframe=timeframe,
                    weight_multiplier=self.weight_multipliers[rarity],
                    reasoning=reasoning,
                    historical_matches=data.get('risk_band_matches', 0),
                    success_rate=historical_win_rate / 100.0,
                    timestamp=datetime.now()
                )
                
                patterns.append(pattern)
                logger.info(f"📊 RiskMetric rare band pattern: {rare_band_type} ({current_risk:.3f})")
            
            # Analyze risk momentum patterns
            risk_momentum = data.get('risk_momentum', 0.0)
            if abs(risk_momentum) >= 0.1:  # Significant risk momentum
                
                direction = "short" if risk_momentum > 0 else "long"  # Rising risk = short, falling risk = long
                confidence = min(abs(risk_momentum) * 2, 1.0)  # Scale momentum to confidence
                
                historical_win_rate = await self._get_historical_pattern_win_rate(
                    PatternType.HISTORICAL_MATCH, confidence, historical_prices
                )
                
                rarity = PatternRarity.UNCOMMON if abs(risk_momentum) >= 0.15 else PatternRarity.COMMON
                
                pattern = PatternSignal(
                    pattern_type=PatternType.HISTORICAL_MATCH,
                    rarity=rarity,
                    confidence=confidence,
                    win_rate_prediction=historical_win_rate,
                    direction=direction,
                    timeframe="7d",
                    weight_multiplier=self.weight_multipliers[rarity],
                    reasoning=f"Risk momentum pattern: {risk_momentum:.3f}. {'Rising' if risk_momentum > 0 else 'Falling'} risk suggests {direction} position.",
                    historical_matches=data.get('momentum_matches', 0),
                    success_rate=historical_win_rate / 100.0,
                    timestamp=datetime.now()
                )
                
                patterns.append(pattern)
                logger.info(f"📊 RiskMetric momentum pattern: {direction} ({risk_momentum:.3f})")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing RiskMetric patterns: {e}")
        
        return patterns
    
    async def _get_historical_pattern_win_rate(
        self,
        pattern_type: PatternType,
        confidence: float,
        historical_prices: Optional[List[Dict[str, Any]]]
    ) -> float:
        """Calculate historical win rate for a specific pattern"""
        
        # If we have historical data, analyze it
        if historical_prices and len(historical_prices) > 50:
            try:
                # Simulate pattern matching (in production, use ML models)
                base_win_rate = {
                    PatternType.LIQUIDATION_CLUSTER: 75.0,
                    PatternType.GOLDEN_CROSS: 82.0,
                    PatternType.DEATH_CROSS: 78.0,
                    PatternType.SUPPORT_BREAK: 68.0,
                    PatternType.RESISTANCE_BREAK: 72.0,
                    PatternType.DIVERGENCE: 85.0,
                    PatternType.RISK_BAND_RARE: 88.0,
                    PatternType.HISTORICAL_MATCH: 70.0,
                    PatternType.VOLUME_SPIKE: 65.0
                }.get(pattern_type, 60.0)
                
                # Adjust based on confidence
                confidence_multiplier = 0.8 + (confidence * 0.4)  # 0.8 to 1.2 range
                adjusted_win_rate = base_win_rate * confidence_multiplier
                
                # Cap at reasonable limits
                return min(max(adjusted_win_rate, 50.0), 95.0)
                
            except Exception as e:
                logger.error(f"❌ Error calculating historical win rate: {e}")
        
        # Default win rates based on pattern type and confidence
        default_rates = {
            PatternType.LIQUIDATION_CLUSTER: 75.0,
            PatternType.GOLDEN_CROSS: 82.0,
            PatternType.DEATH_CROSS: 78.0,
            PatternType.SUPPORT_BREAK: 68.0,
            PatternType.RESISTANCE_BREAK: 72.0,
            PatternType.DIVERGENCE: 85.0,
            PatternType.RISK_BAND_RARE: 88.0,
            PatternType.HISTORICAL_MATCH: 70.0,
            PatternType.VOLUME_SPIKE: 65.0
        }
        
        base_rate = default_rates.get(pattern_type, 60.0)
        return min(base_rate + (confidence * 20), 95.0)  # Boost by confidence
    
    def _calculate_weight_adjustments(
        self,
        kingfisher_patterns: List[PatternSignal],
        cryptometer_patterns: List[PatternSignal],
        riskmetric_patterns: List[PatternSignal]
    ) -> Dict[str, float]:
        """Calculate weight adjustments based on pattern triggers"""
        
        adjustments = {
            'kingfisher': 1.0,
            'cryptometer': 1.0,
            'riskmetric': 1.0
        }
        
        # KingFisher weight adjustments
        for pattern in kingfisher_patterns:
            if pattern.rarity in [PatternRarity.RARE, PatternRarity.EXCEPTIONAL]:
                adjustments['kingfisher'] *= pattern.weight_multiplier
                logger.info(f"🎣 KingFisher weight boosted by {pattern.weight_multiplier}x due to {pattern.pattern_type.value}")
        
        # Cryptometer weight adjustments
        for pattern in cryptometer_patterns:
            if pattern.rarity in [PatternRarity.RARE, PatternRarity.EXCEPTIONAL]:
                adjustments['cryptometer'] *= pattern.weight_multiplier
                logger.info(f"📈 Cryptometer weight boosted by {pattern.weight_multiplier}x due to {pattern.pattern_type.value}")
        
        # RiskMetric weight adjustments
        for pattern in riskmetric_patterns:
            if pattern.rarity in [PatternRarity.RARE, PatternRarity.EXCEPTIONAL]:
                adjustments['riskmetric'] *= pattern.weight_multiplier
                logger.info(f"📊 RiskMetric weight boosted by {pattern.weight_multiplier}x due to {pattern.pattern_type.value}")
        
        # Normalize weights to ensure they sum appropriately
        total_weight = sum(adjustments.values())
        for agent in adjustments:
            adjustments[agent] = adjustments[agent] / total_weight
        
        return adjustments
    
    def _evaluate_trigger_conditions(self, patterns: List[PatternSignal]) -> Tuple[bool, float]:
        """Evaluate if trigger conditions are met for trade entry"""
        
        if not patterns:
            return False, 50.0
        
        # Calculate weighted average win rate
        total_weight = sum(self.weight_multipliers[p.rarity] for p in patterns)
        if total_weight == 0:
            return False, 50.0
        
        weighted_win_rate = sum(
            p.win_rate_prediction * self.weight_multipliers[p.rarity] 
            for p in patterns
        ) / total_weight
        
        # Check if we meet trigger threshold
        trigger_met = weighted_win_rate >= self.win_rate_trigger_threshold
        
        # Bonus for pattern confluence (multiple rare patterns)
        rare_patterns = [p for p in patterns if p.rarity in [PatternRarity.RARE, PatternRarity.EXCEPTIONAL]]
        if len(rare_patterns) >= 2:
            weighted_win_rate += 5.0  # 5% bonus for confluence
            logger.info(f"🎯 Pattern confluence bonus: {len(rare_patterns)} rare patterns detected")
        
        return trigger_met, min(weighted_win_rate, 95.0)
    
    def _find_combined_signals(self, patterns: List[PatternSignal]) -> List[PatternSignal]:
        """Find significant combined signals from multiple patterns"""
        
        combined_signals = []
        
        # Group patterns by direction and timeframe
        direction_groups = defaultdict(list)
        for pattern in patterns:
            key = f"{pattern.direction}_{pattern.timeframe}"
            direction_groups[key].append(pattern)
        
        # Create combined signals for groups with multiple patterns
        for key, group_patterns in direction_groups.items():
            if len(group_patterns) >= 2:  # At least 2 patterns in same direction/timeframe
                
                direction, timeframe = key.split('_')
                
                # Calculate combined metrics
                avg_confidence = sum(p.confidence for p in group_patterns) / len(group_patterns)
                avg_win_rate = sum(p.win_rate_prediction for p in group_patterns) / len(group_patterns)
                max_rarity = max((p.rarity for p in group_patterns), key=lambda x: self.weight_multipliers[x])
                
                # Create combined signal
                combined_signal = PatternSignal(
                    pattern_type=PatternType.HISTORICAL_MATCH,  # Generic type for combined
                    rarity=max_rarity,
                    confidence=min(avg_confidence * 1.2, 1.0),  # Boost confidence for confluence
                    win_rate_prediction=min(avg_win_rate + 3.0, 95.0),  # Boost win rate for confluence
                    direction=direction,
                    timeframe=timeframe,
                    weight_multiplier=self.weight_multipliers[max_rarity] * 1.1,  # Boost multiplier
                    reasoning=f"Combined signal from {len(group_patterns)} patterns: {', '.join(p.pattern_type.value for p in group_patterns)}",
                    historical_matches=sum(p.historical_matches for p in group_patterns),
                    success_rate=avg_win_rate / 100.0,
                    timestamp=datetime.now()
                )
                
                combined_signals.append(combined_signal)
                logger.info(f"🎯 Combined signal: {direction} {timeframe} from {len(group_patterns)} patterns")
        
        return combined_signals
    
    async def _update_learning_data(self, analysis: PatternAnalysis):
        """Update self-learning data based on analysis results"""
        try:
            # Store pattern analysis for future learning
            key = f"{analysis.symbol}_{analysis.timestamp.strftime('%Y%m%d')}"
            
            learning_data = {
                'symbol': analysis.symbol,
                'patterns_detected': len(analysis.kingfisher_patterns + analysis.cryptometer_patterns + analysis.riskmetric_patterns),
                'overall_trigger': analysis.overall_trigger,
                'overall_win_rate': analysis.overall_win_rate,
                'weight_adjustments': analysis.weight_adjustments,
                'timestamp': analysis.timestamp.isoformat()
            }
            
            # In production, store this in a database for ML training
            self.pattern_history[key] = learning_data
            
            # Update success rates (simplified - in production use proper ML)
            for patterns in [analysis.kingfisher_patterns, analysis.cryptometer_patterns, analysis.riskmetric_patterns]:
                for pattern in patterns:
                    pattern_key = f"{pattern.pattern_type.value}_{pattern.rarity.value}"
                    current_rate = self.success_rates.get(pattern_key, pattern.success_rate)
                    # Simple exponential moving average
                    self.success_rates[pattern_key] = 0.9 * current_rate + 0.1 * pattern.success_rate
            
            logger.info(f"📚 Learning data updated for {analysis.symbol}")
            
        except Exception as e:
            logger.error(f"❌ Error updating learning data: {e}")
    
    def _create_empty_analysis(self, symbol: str) -> PatternAnalysis:
        """Create empty analysis for error cases"""
        return PatternAnalysis(
            symbol=symbol,
            kingfisher_patterns=[],
            cryptometer_patterns=[],
            riskmetric_patterns=[],
            combined_signals=[],
            weight_adjustments={'kingfisher': 1.0, 'cryptometer': 1.0, 'riskmetric': 1.0},
            overall_trigger=False,
            overall_win_rate=50.0,
            timestamp=datetime.now()
        )
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about pattern detection and success rates"""
        return {
            'total_analyses': len(self.pattern_history),
            'success_rates': dict(self.success_rates),
            'weight_multipliers': {k.value: v for k, v in self.weight_multipliers.items()},
            'trigger_threshold': self.win_rate_trigger_threshold,
            'rare_risk_zones': self.risk_band_rare_zones,
            'last_updated': datetime.now().isoformat()
        }

# Global instance for use across the system
pattern_trigger_system = PatternTriggerSystem()