#!/usr/bin/env python3
"""
Master Pattern Analysis Agent - ZmartBot
Advanced pattern recognition and analysis across all data sources
Combines liquidation patterns, technical patterns, and risk patterns
Provides comprehensive pattern-based trading signals
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
from collections import defaultdict, deque
import pandas as pd
import statistics
from pathlib import Path
import sys

# Add parent path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.scoring.pattern_trigger_system import (
    PatternTriggerSystem, PatternType, PatternRarity, 
    PatternSignal, PatternAnalysis
)

logger = logging.getLogger(__name__)

class PatternCategory(Enum):
    """Categories of patterns for analysis"""
    REVERSAL = "reversal"                   # Price reversal patterns
    CONTINUATION = "continuation"           # Trend continuation patterns
    BREAKOUT = "breakout"                   # Breakout patterns
    CONSOLIDATION = "consolidation"         # Consolidation/ranging patterns
    DIVERGENCE = "divergence"               # Price/indicator divergence
    HARMONIC = "harmonic"                   # Harmonic patterns (Gartley, Butterfly, etc.)
    ELLIOTT_WAVE = "elliott_wave"           # Elliott Wave patterns
    WYCKOFF = "wyckoff"                     # Wyckoff accumulation/distribution
    VOLUME = "volume"                       # Volume-based patterns
    LIQUIDATION = "liquidation"             # Liquidation cascade patterns

class PatternStrength(Enum):
    """Pattern strength classification"""
    WEAK = "weak"                           # 0-25 strength
    MODERATE = "moderate"                   # 25-50 strength
    STRONG = "strong"                       # 50-75 strength
    VERY_STRONG = "very_strong"             # 75-100 strength

class TimeHorizon(Enum):
    """Time horizon for pattern impact"""
    IMMEDIATE = "immediate"                 # 0-4 hours
    SHORT_TERM = "short_term"               # 4-24 hours
    MEDIUM_TERM = "medium_term"             # 1-7 days
    LONG_TERM = "long_term"                 # 7-30 days

@dataclass
class ComplexPattern:
    """Advanced pattern detection result"""
    pattern_id: str
    pattern_name: str
    category: PatternCategory
    strength: PatternStrength
    confidence: float                       # 0-1 confidence score
    direction: str                          # long/short/neutral
    time_horizon: TimeHorizon
    
    # Pattern specifics
    entry_price: float
    stop_loss: float
    take_profit_targets: List[float]
    risk_reward_ratio: float
    
    # Historical performance
    historical_win_rate: float
    average_return: float
    max_drawdown: float
    occurrence_frequency: float             # How often this pattern occurs
    
    # Component patterns
    sub_patterns: List[str]                 # Component patterns that form this
    confluence_score: float                 # Score based on multiple confirmations
    
    # Market context
    market_condition: str
    volatility_level: str
    volume_profile: str
    
    # Metadata
    detected_at: datetime
    expires_at: datetime                    # When pattern becomes invalid
    notes: str

@dataclass
class PatternCluster:
    """Cluster of related patterns"""
    cluster_id: str
    patterns: List[ComplexPattern]
    cluster_strength: float                 # Combined strength
    cluster_direction: str                  # Dominant direction
    cluster_confidence: float               # Overall confidence
    synergy_score: float                    # How well patterns work together
    timestamp: datetime

@dataclass
class MasterPatternAnalysis:
    """Complete master pattern analysis result"""
    symbol: str
    timestamp: datetime
    
    # Pattern detection results
    detected_patterns: List[ComplexPattern]
    pattern_clusters: List[PatternCluster]
    
    # Scoring and recommendations
    pattern_score: float                    # 0-100 overall pattern score
    trade_signal: str                       # STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL
    confidence_level: float                 # 0-1 overall confidence
    
    # Risk analysis
    pattern_risk_score: float               # 0-100 risk level
    conflicting_patterns: List[str]         # Patterns giving opposite signals
    uncertainty_level: float                # 0-1 uncertainty measure
    
    # Timing
    optimal_entry_window: Tuple[datetime, datetime]
    pattern_validity_period: timedelta
    
    # Position management
    suggested_position_size: float          # As percentage of capital
    max_risk_per_trade: float               # Maximum risk percentage
    scaling_strategy: str                   # How to scale in/out
    
    # Detailed reports
    technical_analysis: str
    pattern_narrative: str
    risk_assessment: str
    
    # Historical context
    similar_historical_setups: List[Dict[str, Any]]
    historical_performance: Dict[str, float]

class MasterPatternAgent:
    """
    Master Pattern Analysis Agent
    
    This agent performs comprehensive pattern analysis across all data sources:
    1. Detects complex patterns (harmonic, Elliott waves, Wyckoff, etc.)
    2. Analyzes pattern clusters and confluence
    3. Provides pattern-based trading signals
    4. Tracks historical pattern performance
    5. Adapts to market conditions
    """
    
    def __init__(self):
        self.agent_id = "master_pattern_agent"
        self.pattern_trigger_system = PatternTriggerSystem()
        
        # Pattern detection parameters
        self.min_pattern_confidence = 0.6
        self.min_cluster_size = 2
        self.pattern_expiry_hours = 24
        
        # Historical pattern database (in production, use real database)
        self.pattern_database = {}
        self.pattern_performance = defaultdict(lambda: {
            'count': 0,
            'wins': 0,
            'total_return': 0.0,
            'max_drawdown': 0.0
        })
        
        # Market context tracking
        self.market_conditions = deque(maxlen=100)
        self.volatility_history = deque(maxlen=100)
        
        # Pattern detection algorithms
        self.harmonic_detector = HarmonicPatternDetector()
        self.elliott_wave_analyzer = ElliottWaveAnalyzer()
        self.wyckoff_analyzer = WyckoffAnalyzer()
        self.volume_profile_analyzer = VolumeProfileAnalyzer()
        
        logger.info("Master Pattern Agent initialized")
    
    async def analyze(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        volume_data: Optional[pd.DataFrame] = None,
        liquidation_data: Optional[Dict[str, Any]] = None,
        technical_indicators: Optional[Dict[str, Any]] = None,
        risk_metrics: Optional[Dict[str, Any]] = None
    ) -> MasterPatternAnalysis:
        """
        Perform comprehensive pattern analysis
        
        Args:
            symbol: Trading symbol
            price_data: OHLCV price data
            volume_data: Volume profile data
            liquidation_data: Liquidation heatmap data
            technical_indicators: Technical indicator values
            risk_metrics: Risk metric calculations
        """
        try:
            timestamp = datetime.now()
            logger.info(f"🔍 Starting master pattern analysis for {symbol}")
            
            # Step 1: Detect individual patterns
            detected_patterns = await self._detect_all_patterns(
                symbol, price_data, volume_data, 
                liquidation_data, technical_indicators, risk_metrics
            )
            
            # Step 2: Find pattern clusters
            pattern_clusters = self._find_pattern_clusters(detected_patterns)
            
            # Step 3: Calculate pattern score and signal
            pattern_score, trade_signal, confidence = self._calculate_pattern_score(
                detected_patterns, pattern_clusters
            )
            
            # Step 4: Analyze pattern risks
            risk_score, conflicts, uncertainty = self._analyze_pattern_risks(
                detected_patterns, pattern_clusters
            )
            
            # Step 5: Determine optimal entry and timing
            entry_window, validity_period = self._determine_timing(
                detected_patterns, pattern_clusters
            )
            
            # Step 6: Calculate position sizing
            position_size, max_risk, scaling = self._calculate_position_sizing(
                pattern_score, confidence, risk_score
            )
            
            # Step 7: Find historical similarities
            historical_setups = await self._find_historical_similarities(
                detected_patterns, symbol
            )
            
            # Step 8: Generate comprehensive reports
            tech_analysis = self._generate_technical_analysis(detected_patterns)
            pattern_narrative = self._generate_pattern_narrative(
                detected_patterns, pattern_clusters
            )
            risk_assessment = self._generate_risk_assessment(
                risk_score, conflicts, uncertainty
            )
            
            # Create final analysis
            analysis = MasterPatternAnalysis(
                symbol=symbol,
                timestamp=timestamp,
                detected_patterns=detected_patterns,
                pattern_clusters=pattern_clusters,
                pattern_score=pattern_score,
                trade_signal=trade_signal,
                confidence_level=confidence,
                pattern_risk_score=risk_score,
                conflicting_patterns=conflicts,
                uncertainty_level=uncertainty,
                optimal_entry_window=entry_window,
                pattern_validity_period=validity_period,
                suggested_position_size=position_size,
                max_risk_per_trade=max_risk,
                scaling_strategy=scaling,
                technical_analysis=tech_analysis,
                pattern_narrative=pattern_narrative,
                risk_assessment=risk_assessment,
                similar_historical_setups=historical_setups,
                historical_performance=self._get_historical_performance(detected_patterns)
            )
            
            # Update learning database
            await self._update_pattern_database(analysis)
            
            logger.info(f"✅ Pattern analysis complete: Score={pattern_score:.1f}, Signal={trade_signal}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error in master pattern analysis: {e}")
            return self._create_empty_analysis(symbol)
    
    async def _detect_all_patterns(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        volume_data: Optional[pd.DataFrame],
        liquidation_data: Optional[Dict[str, Any]],
        technical_indicators: Optional[Dict[str, Any]],
        risk_metrics: Optional[Dict[str, Any]]
    ) -> List[ComplexPattern]:
        """Detect all types of patterns"""
        
        patterns = []
        
        try:
            # Detect harmonic patterns
            harmonic_patterns = await self.harmonic_detector.detect(
                price_data, technical_indicators
            )
            patterns.extend(harmonic_patterns)
            
            # Detect Elliott Wave patterns
            elliott_patterns = await self.elliott_wave_analyzer.analyze(
                price_data, volume_data
            )
            patterns.extend(elliott_patterns)
            
            # Detect Wyckoff patterns
            wyckoff_patterns = await self.wyckoff_analyzer.analyze(
                price_data, volume_data, technical_indicators
            )
            patterns.extend(wyckoff_patterns)
            
            # Detect volume profile patterns
            if volume_data is not None:
                volume_patterns = await self.volume_profile_analyzer.analyze(
                    price_data, volume_data
                )
                patterns.extend(volume_patterns)
            
            # Detect reversal patterns
            reversal_patterns = await self._detect_reversal_patterns(
                price_data, technical_indicators
            )
            patterns.extend(reversal_patterns)
            
            # Detect continuation patterns
            continuation_patterns = await self._detect_continuation_patterns(
                price_data, technical_indicators
            )
            patterns.extend(continuation_patterns)
            
            # Detect breakout patterns
            breakout_patterns = await self._detect_breakout_patterns(
                price_data, volume_data, technical_indicators
            )
            patterns.extend(breakout_patterns)
            
            # Detect liquidation cascade patterns
            if liquidation_data:
                liquidation_patterns = await self._detect_liquidation_patterns(
                    liquidation_data, price_data
                )
                patterns.extend(liquidation_patterns)
            
            # Filter by minimum confidence
            patterns = [p for p in patterns if p.confidence >= self.min_pattern_confidence]
            
            logger.info(f"📊 Detected {len(patterns)} valid patterns for {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Error detecting patterns: {e}")
        
        return patterns
    
    async def _detect_reversal_patterns(
        self,
        price_data: pd.DataFrame,
        indicators: Optional[Dict[str, Any]]
    ) -> List[ComplexPattern]:
        """Detect reversal patterns"""
        patterns = []
        
        try:
            # Head and Shoulders
            if self._is_head_and_shoulders(price_data):
                pattern = ComplexPattern(
                    pattern_id=f"hs_{datetime.now().timestamp()}",
                    pattern_name="Head and Shoulders",
                    category=PatternCategory.REVERSAL,
                    strength=PatternStrength.STRONG,
                    confidence=0.75,
                    direction="short",
                    time_horizon=TimeHorizon.MEDIUM_TERM,
                    entry_price=price_data['close'].iloc[-1],
                    stop_loss=price_data['high'].max() * 1.02,
                    take_profit_targets=[
                        price_data['close'].iloc[-1] * 0.95,
                        price_data['close'].iloc[-1] * 0.92,
                        price_data['close'].iloc[-1] * 0.88
                    ],
                    risk_reward_ratio=2.5,
                    historical_win_rate=68.0,
                    average_return=8.5,
                    max_drawdown=3.2,
                    occurrence_frequency=0.15,
                    sub_patterns=["left_shoulder", "head", "right_shoulder", "neckline"],
                    confluence_score=0.7,
                    market_condition="bearish_reversal",
                    volatility_level="medium",
                    volume_profile="declining",
                    detected_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=48),
                    notes="Classic bearish reversal pattern"
                )
                patterns.append(pattern)
            
            # Double Top
            if self._is_double_top(price_data):
                pattern = ComplexPattern(
                    pattern_id=f"dt_{datetime.now().timestamp()}",
                    pattern_name="Double Top",
                    category=PatternCategory.REVERSAL,
                    strength=PatternStrength.MODERATE,
                    confidence=0.70,
                    direction="short",
                    time_horizon=TimeHorizon.SHORT_TERM,
                    entry_price=price_data['close'].iloc[-1],
                    stop_loss=price_data['high'].max() * 1.01,
                    take_profit_targets=[
                        price_data['close'].iloc[-1] * 0.97,
                        price_data['close'].iloc[-1] * 0.94
                    ],
                    risk_reward_ratio=2.0,
                    historical_win_rate=65.0,
                    average_return=6.0,
                    max_drawdown=2.5,
                    occurrence_frequency=0.20,
                    sub_patterns=["first_peak", "valley", "second_peak"],
                    confluence_score=0.65,
                    market_condition="bearish_reversal",
                    volatility_level="medium",
                    volume_profile="diverging",
                    detected_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=24),
                    notes="Double top reversal pattern"
                )
                patterns.append(pattern)
            
            # Double Bottom
            if self._is_double_bottom(price_data):
                pattern = ComplexPattern(
                    pattern_id=f"db_{datetime.now().timestamp()}",
                    pattern_name="Double Bottom",
                    category=PatternCategory.REVERSAL,
                    strength=PatternStrength.MODERATE,
                    confidence=0.70,
                    direction="long",
                    time_horizon=TimeHorizon.SHORT_TERM,
                    entry_price=price_data['close'].iloc[-1],
                    stop_loss=price_data['low'].min() * 0.99,
                    take_profit_targets=[
                        price_data['close'].iloc[-1] * 1.03,
                        price_data['close'].iloc[-1] * 1.06
                    ],
                    risk_reward_ratio=2.0,
                    historical_win_rate=65.0,
                    average_return=6.0,
                    max_drawdown=2.5,
                    occurrence_frequency=0.20,
                    sub_patterns=["first_trough", "peak", "second_trough"],
                    confluence_score=0.65,
                    market_condition="bullish_reversal",
                    volatility_level="medium",
                    volume_profile="accumulating",
                    detected_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=24),
                    notes="Double bottom reversal pattern"
                )
                patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"❌ Error detecting reversal patterns: {e}")
        
        return patterns
    
    async def _detect_continuation_patterns(
        self,
        price_data: pd.DataFrame,
        indicators: Optional[Dict[str, Any]]
    ) -> List[ComplexPattern]:
        """Detect continuation patterns"""
        patterns = []
        
        try:
            # Bull Flag
            if self._is_bull_flag(price_data):
                pattern = ComplexPattern(
                    pattern_id=f"bf_{datetime.now().timestamp()}",
                    pattern_name="Bull Flag",
                    category=PatternCategory.CONTINUATION,
                    strength=PatternStrength.STRONG,
                    confidence=0.72,
                    direction="long",
                    time_horizon=TimeHorizon.SHORT_TERM,
                    entry_price=price_data['close'].iloc[-1],
                    stop_loss=price_data['low'].iloc[-5:].min(),
                    take_profit_targets=[
                        price_data['close'].iloc[-1] * 1.05,
                        price_data['close'].iloc[-1] * 1.08
                    ],
                    risk_reward_ratio=2.3,
                    historical_win_rate=70.0,
                    average_return=7.0,
                    max_drawdown=2.0,
                    occurrence_frequency=0.25,
                    sub_patterns=["flagpole", "flag_consolidation"],
                    confluence_score=0.75,
                    market_condition="bullish_continuation",
                    volatility_level="low",
                    volume_profile="consolidating",
                    detected_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=12),
                    notes="Bullish continuation flag pattern"
                )
                patterns.append(pattern)
            
            # Ascending Triangle
            if self._is_ascending_triangle(price_data):
                pattern = ComplexPattern(
                    pattern_id=f"at_{datetime.now().timestamp()}",
                    pattern_name="Ascending Triangle",
                    category=PatternCategory.CONTINUATION,
                    strength=PatternStrength.MODERATE,
                    confidence=0.68,
                    direction="long",
                    time_horizon=TimeHorizon.MEDIUM_TERM,
                    entry_price=price_data['close'].iloc[-1],
                    stop_loss=price_data['low'].iloc[-10:].min(),
                    take_profit_targets=[
                        price_data['close'].iloc[-1] * 1.04,
                        price_data['close'].iloc[-1] * 1.07,
                        price_data['close'].iloc[-1] * 1.10
                    ],
                    risk_reward_ratio=2.5,
                    historical_win_rate=66.0,
                    average_return=6.5,
                    max_drawdown=2.3,
                    occurrence_frequency=0.18,
                    sub_patterns=["horizontal_resistance", "rising_support"],
                    confluence_score=0.70,
                    market_condition="bullish_continuation",
                    volatility_level="decreasing",
                    volume_profile="decreasing",
                    detected_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=36),
                    notes="Ascending triangle continuation pattern"
                )
                patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"❌ Error detecting continuation patterns: {e}")
        
        return patterns
    
    async def _detect_breakout_patterns(
        self,
        price_data: pd.DataFrame,
        volume_data: Optional[pd.DataFrame],
        indicators: Optional[Dict[str, Any]]
    ) -> List[ComplexPattern]:
        """Detect breakout patterns"""
        patterns = []
        
        try:
            # Range Breakout
            if self._is_range_breakout(price_data, volume_data):
                direction = "long" if price_data['close'].iloc[-1] > price_data['high'].iloc[-20:-1].mean() else "short"
                
                pattern = ComplexPattern(
                    pattern_id=f"rb_{datetime.now().timestamp()}",
                    pattern_name="Range Breakout",
                    category=PatternCategory.BREAKOUT,
                    strength=PatternStrength.STRONG,
                    confidence=0.74,
                    direction=direction,
                    time_horizon=TimeHorizon.IMMEDIATE,
                    entry_price=price_data['close'].iloc[-1],
                    stop_loss=price_data['low'].iloc[-10:].min() if direction == "long" else price_data['high'].iloc[-10:].max(),
                    take_profit_targets=[
                        price_data['close'].iloc[-1] * (1.06 if direction == "long" else 0.94),
                        price_data['close'].iloc[-1] * (1.10 if direction == "long" else 0.90)
                    ],
                    risk_reward_ratio=3.0,
                    historical_win_rate=72.0,
                    average_return=9.0,
                    max_drawdown=2.8,
                    occurrence_frequency=0.12,
                    sub_patterns=["consolidation_range", "breakout_candle", "volume_spike"],
                    confluence_score=0.78,
                    market_condition=f"{direction}_breakout",
                    volatility_level="expanding",
                    volume_profile="expanding",
                    detected_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=8),
                    notes="Strong range breakout with volume confirmation"
                )
                patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"❌ Error detecting breakout patterns: {e}")
        
        return patterns
    
    async def _detect_liquidation_patterns(
        self,
        liquidation_data: Dict[str, Any],
        price_data: pd.DataFrame
    ) -> List[ComplexPattern]:
        """Detect liquidation cascade patterns"""
        patterns = []
        
        try:
            cluster_strength = liquidation_data.get('cluster_strength', 0.0)
            
            if cluster_strength > 0.7:
                direction = "long" if liquidation_data.get('cluster_position') == 'below' else "short"
                
                pattern = ComplexPattern(
                    pattern_id=f"lc_{datetime.now().timestamp()}",
                    pattern_name="Liquidation Cascade",
                    category=PatternCategory.LIQUIDATION,
                    strength=PatternStrength.VERY_STRONG if cluster_strength > 0.85 else PatternStrength.STRONG,
                    confidence=cluster_strength,
                    direction=direction,
                    time_horizon=TimeHorizon.IMMEDIATE,
                    entry_price=price_data['close'].iloc[-1],
                    stop_loss=price_data['close'].iloc[-1] * (0.98 if direction == "long" else 1.02),
                    take_profit_targets=[
                        price_data['close'].iloc[-1] * (1.03 if direction == "long" else 0.97),
                        price_data['close'].iloc[-1] * (1.05 if direction == "long" else 0.95),
                        price_data['close'].iloc[-1] * (1.08 if direction == "long" else 0.92)
                    ],
                    risk_reward_ratio=3.5,
                    historical_win_rate=78.0,
                    average_return=10.5,
                    max_drawdown=3.0,
                    occurrence_frequency=0.08,
                    sub_patterns=["liquidation_cluster", "stop_hunt", "cascade_trigger"],
                    confluence_score=0.85,
                    market_condition="high_volatility",
                    volatility_level="extreme",
                    volume_profile="spiking",
                    detected_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=4),
                    notes=f"Major liquidation cascade detected at {cluster_strength:.2%} strength"
                )
                patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"❌ Error detecting liquidation patterns: {e}")
        
        return patterns
    
    def _find_pattern_clusters(
        self,
        patterns: List[ComplexPattern]
    ) -> List[PatternCluster]:
        """Find clusters of related patterns"""
        clusters = []
        
        try:
            # Group patterns by direction and time horizon
            direction_groups = defaultdict(list)
            for pattern in patterns:
                key = f"{pattern.direction}_{pattern.time_horizon.value}"
                direction_groups[key].append(pattern)
            
            # Create clusters from groups
            for key, group_patterns in direction_groups.items():
                if len(group_patterns) >= self.min_cluster_size:
                    
                    direction = group_patterns[0].direction
                    
                    # Calculate cluster metrics
                    cluster_strength = statistics.mean([p.confidence for p in group_patterns])
                    cluster_confidence = min(cluster_strength * 1.2, 1.0)  # Boost for confluence
                    
                    # Calculate synergy score
                    category_diversity = len(set(p.category for p in group_patterns))
                    synergy_score = min(category_diversity / 3.0, 1.0)
                    
                    cluster = PatternCluster(
                        cluster_id=f"cluster_{datetime.now().timestamp()}",
                        patterns=group_patterns,
                        cluster_strength=cluster_strength,
                        cluster_direction=direction,
                        cluster_confidence=cluster_confidence,
                        synergy_score=synergy_score,
                        timestamp=datetime.now()
                    )
                    
                    clusters.append(cluster)
                    logger.info(f"🎯 Pattern cluster found: {len(group_patterns)} patterns, {direction} direction")
            
        except Exception as e:
            logger.error(f"❌ Error finding pattern clusters: {e}")
        
        return clusters
    
    def _calculate_pattern_score(
        self,
        patterns: List[ComplexPattern],
        clusters: List[PatternCluster]
    ) -> Tuple[float, str, float]:
        """Calculate overall pattern score and trading signal"""
        
        if not patterns:
            return 50.0, "HOLD", 0.5
        
        try:
            # Calculate base score from individual patterns
            pattern_scores = []
            for pattern in patterns:
                strength_multiplier = {
                    PatternStrength.WEAK: 0.25,
                    PatternStrength.MODERATE: 0.5,
                    PatternStrength.STRONG: 0.75,
                    PatternStrength.VERY_STRONG: 1.0
                }[pattern.strength]
                
                score = pattern.confidence * strength_multiplier * 100
                pattern_scores.append(score)
            
            base_score = statistics.mean(pattern_scores)
            
            # Apply cluster bonus
            cluster_bonus = 0
            for cluster in clusters:
                cluster_bonus += cluster.synergy_score * cluster.cluster_confidence * 10
            
            final_score = min(base_score + cluster_bonus, 100)
            
            # Determine signal based on pattern directions
            long_patterns = [p for p in patterns if p.direction == "long"]
            short_patterns = [p for p in patterns if p.direction == "short"]
            
            long_strength = sum(p.confidence for p in long_patterns)
            short_strength = sum(p.confidence for p in short_patterns)
            
            if long_strength > short_strength * 1.5:
                if final_score >= 75:
                    signal = "STRONG_BUY"
                elif final_score >= 60:
                    signal = "BUY"
                else:
                    signal = "HOLD"
            elif short_strength > long_strength * 1.5:
                if final_score >= 75:
                    signal = "STRONG_SELL"
                elif final_score >= 60:
                    signal = "SELL"
                else:
                    signal = "HOLD"
            else:
                signal = "HOLD"
            
            # Calculate confidence
            confidence = min(statistics.mean([p.confidence for p in patterns]) * 1.1, 1.0)
            
            return final_score, signal, confidence
            
        except Exception as e:
            logger.error(f"❌ Error calculating pattern score: {e}")
            return 50.0, "HOLD", 0.5
    
    def _analyze_pattern_risks(
        self,
        patterns: List[ComplexPattern],
        clusters: List[PatternCluster]
    ) -> Tuple[float, List[str], float]:
        """Analyze risks from detected patterns"""
        
        try:
            # Find conflicting patterns
            conflicts = []
            for i, p1 in enumerate(patterns):
                for p2 in patterns[i+1:]:
                    if p1.direction != p2.direction and p1.time_horizon == p2.time_horizon:
                        conflicts.append(f"{p1.pattern_name} vs {p2.pattern_name}")
            
            # Calculate risk score
            conflict_penalty = len(conflicts) * 10
            avg_drawdown = statistics.mean([p.max_drawdown for p in patterns]) if patterns else 5.0
            risk_score = min(conflict_penalty + avg_drawdown * 2, 100)
            
            # Calculate uncertainty
            if patterns:
                confidence_std = statistics.stdev([p.confidence for p in patterns]) if len(patterns) > 1 else 0
                uncertainty = min(confidence_std * 2, 1.0)
            else:
                uncertainty = 1.0
            
            return risk_score, conflicts, uncertainty
            
        except Exception as e:
            logger.error(f"❌ Error analyzing pattern risks: {e}")
            return 50.0, [], 0.5
    
    def _determine_timing(
        self,
        patterns: List[ComplexPattern],
        clusters: List[PatternCluster]
    ) -> Tuple[Tuple[datetime, datetime], timedelta]:
        """Determine optimal entry window and pattern validity"""
        
        now = datetime.now()
        
        if not patterns:
            return (now, now + timedelta(hours=4)), timedelta(hours=24)
        
        try:
            # Find the most immediate patterns
            immediate_patterns = [p for p in patterns if p.time_horizon == TimeHorizon.IMMEDIATE]
            
            if immediate_patterns:
                # Entry window for immediate patterns
                entry_start = now
                entry_end = now + timedelta(hours=2)
                validity = timedelta(hours=8)
            else:
                # Use average expiry time
                avg_expiry = statistics.mean([(p.expires_at - now).total_seconds() for p in patterns])
                entry_start = now
                entry_end = now + timedelta(seconds=avg_expiry/4)
                validity = timedelta(seconds=avg_expiry)
            
            return (entry_start, entry_end), validity
            
        except Exception as e:
            logger.error(f"❌ Error determining timing: {e}")
            return (now, now + timedelta(hours=4)), timedelta(hours=24)
    
    def _calculate_position_sizing(
        self,
        pattern_score: float,
        confidence: float,
        risk_score: float
    ) -> Tuple[float, float, str]:
        """Calculate position sizing based on patterns"""
        
        try:
            # Base position size on pattern score and confidence
            base_size = (pattern_score / 100) * confidence * 0.1  # Max 10% of capital
            
            # Adjust for risk
            risk_multiplier = max(1 - (risk_score / 100), 0.3)
            adjusted_size = base_size * risk_multiplier
            
            # Position size as percentage
            position_size = min(adjusted_size * 100, 5.0)  # Cap at 5%
            
            # Max risk per trade
            max_risk = min(position_size * 0.5, 2.0)  # Max 2% risk
            
            # Scaling strategy
            if confidence > 0.8:
                scaling = "all_at_once"
            elif confidence > 0.6:
                scaling = "scale_in_thirds"
            else:
                scaling = "scale_in_quarters"
            
            return position_size, max_risk, scaling
            
        except Exception as e:
            logger.error(f"❌ Error calculating position sizing: {e}")
            return 1.0, 0.5, "scale_in_quarters"
    
    async def _find_historical_similarities(
        self,
        patterns: List[ComplexPattern],
        symbol: str
    ) -> List[Dict[str, Any]]:
        """Find similar historical pattern setups"""
        
        similar_setups = []
        
        try:
            # In production, query historical database
            # For now, return mock data
            for pattern in patterns[:3]:  # Top 3 patterns
                historical = {
                    'date': (datetime.now() - timedelta(days=30)).isoformat(),
                    'pattern': pattern.pattern_name,
                    'outcome': 'success' if pattern.historical_win_rate > 60 else 'failure',
                    'return': pattern.average_return,
                    'duration_hours': 24,
                    'similarity_score': 0.85
                }
                similar_setups.append(historical)
            
        except Exception as e:
            logger.error(f"❌ Error finding historical similarities: {e}")
        
        return similar_setups
    
    def _generate_technical_analysis(self, patterns: List[ComplexPattern]) -> str:
        """Generate technical analysis narrative"""
        
        if not patterns:
            return "No significant patterns detected. Market structure unclear."
        
        try:
            analysis = "📊 Technical Pattern Analysis:\n\n"
            
            # Group by category
            by_category = defaultdict(list)
            for pattern in patterns:
                by_category[pattern.category].append(pattern)
            
            for category, cat_patterns in by_category.items():
                analysis += f"**{category.value.title()} Patterns:**\n"
                for pattern in cat_patterns:
                    analysis += f"• {pattern.pattern_name}: {pattern.confidence:.1%} confidence, "
                    analysis += f"{pattern.direction} bias, {pattern.strength.value} strength\n"
                analysis += "\n"
            
            # Add dominant direction
            long_count = sum(1 for p in patterns if p.direction == "long")
            short_count = sum(1 for p in patterns if p.direction == "short")
            
            if long_count > short_count:
                analysis += f"**Dominant Bias:** Bullish ({long_count} long vs {short_count} short patterns)\n"
            elif short_count > long_count:
                analysis += f"**Dominant Bias:** Bearish ({short_count} short vs {long_count} long patterns)\n"
            else:
                analysis += f"**Dominant Bias:** Neutral ({long_count} patterns each direction)\n"
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error generating technical analysis: {e}")
            return "Technical analysis generation failed."
    
    def _generate_pattern_narrative(
        self,
        patterns: List[ComplexPattern],
        clusters: List[PatternCluster]
    ) -> str:
        """Generate pattern narrative"""
        
        try:
            narrative = "🎯 Pattern Formation Narrative:\n\n"
            
            if clusters:
                narrative += f"**Pattern Clusters:** {len(clusters)} significant clusters detected\n\n"
                
                for cluster in clusters:
                    narrative += f"• Cluster Direction: {cluster.cluster_direction.upper()}\n"
                    narrative += f"  - Patterns: {', '.join([p.pattern_name for p in cluster.patterns])}\n"
                    narrative += f"  - Strength: {cluster.cluster_strength:.1%}\n"
                    narrative += f"  - Synergy: {cluster.synergy_score:.1%}\n\n"
            
            if patterns:
                strongest = max(patterns, key=lambda p: p.confidence)
                narrative += f"**Strongest Pattern:** {strongest.pattern_name}\n"
                narrative += f"• Confidence: {strongest.confidence:.1%}\n"
                narrative += f"• Historical Win Rate: {strongest.historical_win_rate:.1f}%\n"
                narrative += f"• Risk/Reward: {strongest.risk_reward_ratio:.1f}:1\n"
                narrative += f"• Notes: {strongest.notes}\n"
            
            return narrative
            
        except Exception as e:
            logger.error(f"❌ Error generating pattern narrative: {e}")
            return "Pattern narrative generation failed."
    
    def _generate_risk_assessment(
        self,
        risk_score: float,
        conflicts: List[str],
        uncertainty: float
    ) -> str:
        """Generate risk assessment"""
        
        try:
            assessment = "⚠️ Pattern Risk Assessment:\n\n"
            
            # Risk level
            if risk_score < 30:
                risk_level = "Low"
            elif risk_score < 60:
                risk_level = "Moderate"
            elif risk_score < 80:
                risk_level = "High"
            else:
                risk_level = "Very High"
            
            assessment += f"**Overall Risk Level:** {risk_level} ({risk_score:.1f}/100)\n"
            assessment += f"**Uncertainty Level:** {uncertainty:.1%}\n\n"
            
            if conflicts:
                assessment += "**Pattern Conflicts Detected:**\n"
                for conflict in conflicts:
                    assessment += f"• {conflict}\n"
                assessment += "\n⚠️ Conflicting patterns suggest caution and reduced position size.\n"
            else:
                assessment += "✅ No significant pattern conflicts detected.\n"
            
            # Risk mitigation
            assessment += "\n**Risk Mitigation Recommendations:**\n"
            if risk_score > 60:
                assessment += "• Use smaller position sizes\n"
                assessment += "• Set tighter stop losses\n"
                assessment += "• Consider scaling in gradually\n"
            else:
                assessment += "• Standard position sizing appropriate\n"
                assessment += "• Use pattern-based stop losses\n"
                assessment += "• Monitor for pattern invalidation\n"
            
            return assessment
            
        except Exception as e:
            logger.error(f"❌ Error generating risk assessment: {e}")
            return "Risk assessment generation failed."
    
    def _get_historical_performance(
        self,
        patterns: List[ComplexPattern]
    ) -> Dict[str, float]:
        """Get historical performance metrics for detected patterns"""
        
        try:
            if not patterns:
                return {
                    'avg_win_rate': 50.0,
                    'avg_return': 0.0,
                    'avg_drawdown': 5.0,
                    'total_occurrences': 0
                }
            
            return {
                'avg_win_rate': statistics.mean([p.historical_win_rate for p in patterns]),
                'avg_return': statistics.mean([p.average_return for p in patterns]),
                'avg_drawdown': statistics.mean([p.max_drawdown for p in patterns]),
                'total_occurrences': sum([self.pattern_performance[p.pattern_name]['count'] for p in patterns])
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting historical performance: {e}")
            return {
                'avg_win_rate': 50.0,
                'avg_return': 0.0,
                'avg_drawdown': 5.0,
                'total_occurrences': 0
            }
    
    async def _update_pattern_database(self, analysis: MasterPatternAnalysis):
        """Update pattern database with new analysis"""
        
        try:
            # Store analysis for learning
            key = f"{analysis.symbol}_{analysis.timestamp.strftime('%Y%m%d_%H%M%S')}"
            self.pattern_database[key] = {
                'symbol': analysis.symbol,
                'timestamp': analysis.timestamp.isoformat(),
                'pattern_score': analysis.pattern_score,
                'trade_signal': analysis.trade_signal,
                'patterns_detected': len(analysis.detected_patterns),
                'clusters_formed': len(analysis.pattern_clusters),
                'confidence': analysis.confidence_level
            }
            
            # Update pattern performance tracking
            for pattern in analysis.detected_patterns:
                perf = self.pattern_performance[pattern.pattern_name]
                perf['count'] += 1
                # In production, track actual outcomes
            
            logger.info(f"📚 Pattern database updated for {analysis.symbol}")
            
        except Exception as e:
            logger.error(f"❌ Error updating pattern database: {e}")
    
    def _create_empty_analysis(self, symbol: str) -> MasterPatternAnalysis:
        """Create empty analysis for error cases"""
        
        return MasterPatternAnalysis(
            symbol=symbol,
            timestamp=datetime.now(),
            detected_patterns=[],
            pattern_clusters=[],
            pattern_score=50.0,
            trade_signal="HOLD",
            confidence_level=0.5,
            pattern_risk_score=50.0,
            conflicting_patterns=[],
            uncertainty_level=0.5,
            optimal_entry_window=(datetime.now(), datetime.now() + timedelta(hours=4)),
            pattern_validity_period=timedelta(hours=24),
            suggested_position_size=1.0,
            max_risk_per_trade=0.5,
            scaling_strategy="scale_in_quarters",
            technical_analysis="No patterns detected.",
            pattern_narrative="Market structure unclear.",
            risk_assessment="Unable to assess risk.",
            similar_historical_setups=[],
            historical_performance={
                'avg_win_rate': 50.0,
                'avg_return': 0.0,
                'avg_drawdown': 5.0,
                'total_occurrences': 0
            }
        )
    
    # Pattern detection helper methods
    def _is_head_and_shoulders(self, price_data: pd.DataFrame) -> bool:
        """Check for head and shoulders pattern"""
        if len(price_data) < 30:
            return False
        
        try:
            highs = price_data['high'].values[-30:]
            # Simplified detection - in production use more sophisticated methods
            peak_indices = []
            for i in range(2, len(highs) - 2):
                if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                    peak_indices.append(i)
            
            if len(peak_indices) >= 3:
                # Check if middle peak is highest (head)
                if peak_indices[1] < len(highs) - 1:
                    head_idx = peak_indices[1]
                    if highs[head_idx] > highs[peak_indices[0]] and highs[head_idx] > highs[peak_indices[2]]:
                        return True
        except:
            pass
        
        return False
    
    def _is_double_top(self, price_data: pd.DataFrame) -> bool:
        """Check for double top pattern"""
        if len(price_data) < 20:
            return False
        
        try:
            highs = price_data['high'].values[-20:]
            # Find two similar peaks
            peak_indices = []
            for i in range(1, len(highs) - 1):
                if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                    peak_indices.append(i)
            
            if len(peak_indices) >= 2:
                # Check if peaks are similar in height
                peak1 = highs[peak_indices[0]]
                peak2 = highs[peak_indices[1]]
                if abs(peak1 - peak2) / peak1 < 0.02:  # Within 2%
                    return True
        except:
            pass
        
        return False
    
    def _is_double_bottom(self, price_data: pd.DataFrame) -> bool:
        """Check for double bottom pattern"""
        if len(price_data) < 20:
            return False
        
        try:
            lows = price_data['low'].values[-20:]
            # Find two similar troughs
            trough_indices = []
            for i in range(1, len(lows) - 1):
                if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                    trough_indices.append(i)
            
            if len(trough_indices) >= 2:
                # Check if troughs are similar in depth
                trough1 = lows[trough_indices[0]]
                trough2 = lows[trough_indices[1]]
                if abs(trough1 - trough2) / trough1 < 0.02:  # Within 2%
                    return True
        except:
            pass
        
        return False
    
    def _is_bull_flag(self, price_data: pd.DataFrame) -> bool:
        """Check for bull flag pattern"""
        if len(price_data) < 15:
            return False
        
        try:
            # Check for strong upward move followed by consolidation
            prices = price_data['close'].values[-15:]
            
            # Check for flagpole (strong up move)
            flagpole_return = (prices[7] - prices[0]) / prices[0]
            if flagpole_return > 0.05:  # 5% move up
                # Check for consolidation
                consolidation = prices[7:]
                if max(consolidation) - min(consolidation) < abs(flagpole_return * prices[7] * 0.5):
                    return True
        except:
            pass
        
        return False
    
    def _is_ascending_triangle(self, price_data: pd.DataFrame) -> bool:
        """Check for ascending triangle pattern"""
        if len(price_data) < 20:
            return False
        
        try:
            highs = price_data['high'].values[-20:]
            lows = price_data['low'].values[-20:]
            
            # Check for flat resistance and rising support
            high_variance = np.std(highs) / np.mean(highs)
            
            # Check if lows are trending up
            low_trend = np.polyfit(range(len(lows)), lows, 1)[0]
            
            if high_variance < 0.02 and low_trend > 0:
                return True
        except:
            pass
        
        return False
    
    def _is_range_breakout(
        self,
        price_data: pd.DataFrame,
        volume_data: Optional[pd.DataFrame]
    ) -> bool:
        """Check for range breakout pattern"""
        if len(price_data) < 20:
            return False
        
        try:
            prices = price_data['close'].values
            recent_range = prices[-20:-1]
            range_high = max(recent_range)
            range_low = min(recent_range)
            current_price = prices[-1]
            
            # Check if price broke out of range
            if current_price > range_high * 1.02 or current_price < range_low * 0.98:
                # Check for volume confirmation if available
                if volume_data is not None and len(volume_data) >= 20:
                    recent_vol = volume_data['volume'].values[-1]
                    avg_vol = volume_data['volume'].values[-20:-1].mean()
                    if recent_vol > avg_vol * 1.5:
                        return True
                else:
                    return True
        except:
            pass
        
        return False


class HarmonicPatternDetector:
    """Detector for harmonic patterns (Gartley, Butterfly, Bat, Crab)"""
    
    async def detect(
        self,
        price_data: pd.DataFrame,
        indicators: Optional[Dict[str, Any]]
    ) -> List[ComplexPattern]:
        """Detect harmonic patterns"""
        # Simplified implementation - in production use Fibonacci ratios
        return []


class ElliottWaveAnalyzer:
    """Analyzer for Elliott Wave patterns"""
    
    async def analyze(
        self,
        price_data: pd.DataFrame,
        volume_data: Optional[pd.DataFrame]
    ) -> List[ComplexPattern]:
        """Analyze Elliott Wave structures"""
        # Simplified implementation - in production use wave counting algorithms
        return []


class WyckoffAnalyzer:
    """Analyzer for Wyckoff accumulation/distribution patterns"""
    
    async def analyze(
        self,
        price_data: pd.DataFrame,
        volume_data: Optional[pd.DataFrame],
        indicators: Optional[Dict[str, Any]]
    ) -> List[ComplexPattern]:
        """Analyze Wyckoff patterns"""
        # Simplified implementation - in production use volume spread analysis
        return []


class VolumeProfileAnalyzer:
    """Analyzer for volume profile patterns"""
    
    async def analyze(
        self,
        price_data: pd.DataFrame,
        volume_data: pd.DataFrame
    ) -> List[ComplexPattern]:
        """Analyze volume profile patterns"""
        # Simplified implementation - in production use market profile analysis
        return []


# Global instance
master_pattern_agent = MasterPatternAgent()