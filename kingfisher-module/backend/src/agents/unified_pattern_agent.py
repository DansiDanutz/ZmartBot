#!/usr/bin/env python3
"""
🎯 Unified Pattern Recognition Agent - Master Pattern Analyzer
Integrates RiskMetric, Cryptometer, and Kingfisher data sources
to identify patterns and provide comprehensive trading insights
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import statistics
from pathlib import Path
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# ==================== Data Models ====================

class DataSource(Enum):
    """Available data sources"""
    RISKMETRIC = "riskmetric"      # Benjamin Cowen risk bands
    CRYPTOMETER = "cryptometer"     # 17 endpoint analysis
    KINGFISHER = "kingfisher"       # Liquidation maps & heatmaps
    COMBINED = "combined"           # All sources combined

class PatternType(Enum):
    """Pattern classification types"""
    # Liquidation Patterns
    LIQUIDATION_CASCADE = "liquidation_cascade"
    LIQUIDATION_SQUEEZE = "liquidation_squeeze"
    LIQUIDATION_DIVERGENCE = "liquidation_divergence"
    
    # Risk Band Patterns
    RISK_BAND_TOUCH = "risk_band_touch"
    RISK_BAND_BREAKOUT = "risk_band_breakout"
    RISK_BAND_REVERSAL = "risk_band_reversal"
    
    # Market Structure Patterns
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"
    TREND_CONTINUATION = "trend_continuation"
    TREND_REVERSAL = "trend_reversal"
    
    # Volume Patterns
    VOLUME_SPIKE = "volume_spike"
    VOLUME_DIVERGENCE = "volume_divergence"
    VOLUME_CLUSTER = "volume_cluster"
    
    # Composite Patterns
    MULTI_SOURCE_CONFLUENCE = "multi_source_confluence"
    DIVERGENT_SIGNALS = "divergent_signals"

class PatternStrength(Enum):
    """Pattern strength levels"""
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4
    EXTREME = 5

class MarketPhase(Enum):
    """Market cycle phases"""
    ACCUMULATION = "accumulation"
    MARKUP = "markup"
    DISTRIBUTION = "distribution"
    MARKDOWN = "markdown"
    UNCERTAINTY = "uncertainty"

@dataclass
class PatternSignal:
    """Individual pattern detection result"""
    pattern_type: PatternType
    strength: PatternStrength
    confidence: float  # 0-100
    direction: str  # "long", "short", "neutral"
    timeframe: str  # "1h", "4h", "1d", "1w"
    source: DataSource
    detected_at: datetime
    expires_at: datetime
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: List[float] = field(default_factory=list)
    risk_reward_ratio: Optional[float] = None
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntegratedPattern:
    """Pattern that combines multiple sources"""
    pattern_id: str
    primary_pattern: PatternSignal
    supporting_patterns: List[PatternSignal]
    confluence_score: float  # 0-100
    combined_strength: PatternStrength
    market_phase: MarketPhase
    win_rate_estimate: Dict[str, float]  # {"24h": 75.5, "7d": 68.2, "1m": 71.0}
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

@dataclass
class PatternAnalysisResult:
    """Complete pattern analysis result"""
    symbol: str
    timestamp: datetime
    
    # Pattern Detection
    detected_patterns: List[PatternSignal]
    integrated_patterns: List[IntegratedPattern]
    pattern_clusters: List[Dict[str, Any]]
    
    # Scoring & Signals
    pattern_score: float  # 0-100
    signal_strength: str  # "strong_buy", "buy", "neutral", "sell", "strong_sell"
    confidence_level: float  # 0-100
    
    # Win Rate Analysis
    win_rates: Dict[str, Dict[str, float]]  # timeframe -> {"long": x, "short": y}
    historical_accuracy: float
    
    # Risk Metrics
    risk_score: float  # 0-100
    max_drawdown_risk: float
    liquidation_risk: float
    
    # Market Context
    market_phase: MarketPhase
    volatility_regime: str
    trend_strength: float
    
    # Recommendations
    entry_zones: List[Dict[str, Any]]
    exit_targets: List[Dict[str, Any]]
    position_sizing: float
    risk_management: Dict[str, Any]
    
    # Professional Report
    executive_summary: str
    technical_analysis: str
    pattern_narrative: str

# ==================== Pattern Detection Engine ====================

class PatternDetectionEngine:
    """Core pattern detection algorithms"""
    
    @staticmethod
    def detect_liquidation_patterns(data: Dict[str, Any]) -> List[PatternSignal]:
        """Detect patterns from liquidation data"""
        patterns = []
        
        try:
            # Extract liquidation metrics
            long_liq = float(data.get('long_liquidations', 0))
            short_liq = float(data.get('short_liquidations', 0))
            total_liq = long_liq + short_liq
            
            if total_liq > 0:
                long_ratio = long_liq / total_liq
                short_ratio = short_liq / total_liq
                
                # Liquidation Cascade Pattern
                if long_ratio > 0.7:
                    patterns.append(PatternSignal(
                        pattern_type=PatternType.LIQUIDATION_CASCADE,
                        strength=PatternStrength.STRONG if long_ratio > 0.8 else PatternStrength.MODERATE,
                        confidence=long_ratio * 100,
                        direction="long",
                        timeframe="4h",
                        source=DataSource.KINGFISHER,
                        detected_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(hours=4),
                        notes="Heavy long liquidations detected - potential short squeeze setup"
                    ))
                
                elif short_ratio > 0.7:
                    patterns.append(PatternSignal(
                        pattern_type=PatternType.LIQUIDATION_CASCADE,
                        strength=PatternStrength.STRONG if short_ratio > 0.8 else PatternStrength.MODERATE,
                        confidence=short_ratio * 100,
                        direction="short",
                        timeframe="4h",
                        source=DataSource.KINGFISHER,
                        detected_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(hours=4),
                        notes="Heavy short liquidations detected - potential long squeeze setup"
                    ))
                
                # Liquidation Squeeze Pattern
                if abs(long_ratio - short_ratio) < 0.1:  # Balanced liquidations
                    patterns.append(PatternSignal(
                        pattern_type=PatternType.LIQUIDATION_SQUEEZE,
                        strength=PatternStrength.MODERATE,
                        confidence=70,
                        direction="neutral",
                        timeframe="1d",
                        source=DataSource.KINGFISHER,
                        detected_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(days=1),
                        notes="Balanced liquidations - market indecision, wait for breakout"
                    ))
        
        except Exception as e:
            logger.error(f"Error detecting liquidation patterns: {e}")
        
        return patterns
    
    @staticmethod
    def detect_risk_band_patterns(data: Dict[str, Any]) -> List[PatternSignal]:
        """Detect patterns from RiskMetric data"""
        patterns = []
        
        try:
            risk_value = float(data.get('risk_metric', 0.5))
            price = float(data.get('current_price', 0))
            lower_band = float(data.get('lower_band', 0))
            upper_band = float(data.get('upper_band', 0))
            
            if price and lower_band and upper_band:
                # Calculate position in range
                range_size = upper_band - lower_band
                price_position = (price - lower_band) / range_size if range_size > 0 else 0.5
                
                # Risk Band Touch Pattern
                if price_position < 0.1:  # Near lower band
                    patterns.append(PatternSignal(
                        pattern_type=PatternType.RISK_BAND_TOUCH,
                        strength=PatternStrength.STRONG,
                        confidence=90 - (price_position * 100),
                        direction="long",
                        timeframe="1d",
                        source=DataSource.RISKMETRIC,
                        detected_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(days=3),
                        entry_price=price,
                        stop_loss=lower_band * 0.98,
                        take_profit=[lower_band + range_size * 0.25, lower_band + range_size * 0.5],
                        notes=f"Price near lower risk band at {risk_value:.2f} risk level"
                    ))
                
                elif price_position > 0.9:  # Near upper band
                    patterns.append(PatternSignal(
                        pattern_type=PatternType.RISK_BAND_TOUCH,
                        strength=PatternStrength.STRONG,
                        confidence=90 - ((1 - price_position) * 100),
                        direction="short",
                        timeframe="1d",
                        source=DataSource.RISKMETRIC,
                        detected_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(days=3),
                        entry_price=price,
                        stop_loss=upper_band * 1.02,
                        take_profit=[upper_band - range_size * 0.25, upper_band - range_size * 0.5],
                        notes=f"Price near upper risk band at {risk_value:.2f} risk level"
                    ))
                
                # Risk Band Breakout Pattern
                if price > upper_band:
                    patterns.append(PatternSignal(
                        pattern_type=PatternType.RISK_BAND_BREAKOUT,
                        strength=PatternStrength.VERY_STRONG,
                        confidence=85,
                        direction="long",
                        timeframe="1w",
                        source=DataSource.RISKMETRIC,
                        detected_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(weeks=1),
                        notes="Breakout above upper risk band - strong bullish signal"
                    ))
                
                elif price < lower_band:
                    patterns.append(PatternSignal(
                        pattern_type=PatternType.RISK_BAND_BREAKOUT,
                        strength=PatternStrength.VERY_STRONG,
                        confidence=85,
                        direction="short",
                        timeframe="1w",
                        source=DataSource.RISKMETRIC,
                        detected_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(weeks=1),
                        notes="Breakdown below lower risk band - strong bearish signal"
                    ))
        
        except Exception as e:
            logger.error(f"Error detecting risk band patterns: {e}")
        
        return patterns
    
    @staticmethod
    def detect_cryptometer_patterns(data: Dict[str, Any]) -> List[PatternSignal]:
        """Detect patterns from Cryptometer data"""
        patterns = []
        
        try:
            # Extract key metrics
            fear_greed = float(data.get('fear_greed_index', 50))
            funding_rate = float(data.get('funding_rate', 0))
            open_interest = float(data.get('open_interest_change', 0))
            volume_change = float(data.get('volume_24h_change', 0))
            
            # Volume Spike Pattern
            if abs(volume_change) > 50:
                patterns.append(PatternSignal(
                    pattern_type=PatternType.VOLUME_SPIKE,
                    strength=PatternStrength.STRONG if abs(volume_change) > 100 else PatternStrength.MODERATE,
                    confidence=min(abs(volume_change), 95),
                    direction="long" if volume_change > 0 else "short",
                    timeframe="4h",
                    source=DataSource.CRYPTOMETER,
                    detected_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=8),
                    notes=f"Volume spike of {volume_change:.1f}% detected"
                ))
            
            # Market Structure Patterns based on Fear & Greed
            if fear_greed < 20:
                patterns.append(PatternSignal(
                    pattern_type=PatternType.ACCUMULATION,
                    strength=PatternStrength.STRONG,
                    confidence=80,
                    direction="long",
                    timeframe="1w",
                    source=DataSource.CRYPTOMETER,
                    detected_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(weeks=2),
                    notes="Extreme fear detected - potential accumulation zone"
                ))
            
            elif fear_greed > 80:
                patterns.append(PatternSignal(
                    pattern_type=PatternType.DISTRIBUTION,
                    strength=PatternStrength.STRONG,
                    confidence=80,
                    direction="short",
                    timeframe="1w",
                    source=DataSource.CRYPTOMETER,
                    detected_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(weeks=2),
                    notes="Extreme greed detected - potential distribution zone"
                ))
            
            # Funding Rate Divergence
            if abs(funding_rate) > 0.05:  # High funding rate
                patterns.append(PatternSignal(
                    pattern_type=PatternType.VOLUME_DIVERGENCE,
                    strength=PatternStrength.MODERATE,
                    confidence=70,
                    direction="short" if funding_rate > 0 else "long",
                    timeframe="1d",
                    source=DataSource.CRYPTOMETER,
                    detected_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=2),
                    notes=f"High funding rate {funding_rate:.3f}% - potential reversal"
                ))
        
        except Exception as e:
            logger.error(f"Error detecting cryptometer patterns: {e}")
        
        return patterns

# ==================== Main Unified Pattern Agent ====================

class UnifiedPatternAgent:
    """
    Unified Pattern Recognition Agent
    Integrates all data sources to identify high-probability trading patterns
    """
    
    def __init__(self):
        """Initialize the Unified Pattern Agent"""
        self.detection_engine = PatternDetectionEngine()
        self.pattern_history = defaultdict(lambda: deque(maxlen=100))
        self.performance_tracker = {}
        
        # API configurations
        self.airtable_key = os.getenv('AIRTABLE_API_KEY')
        self.airtable_base = os.getenv('AIRTABLE_BASE_ID', 'appAs9sZH7OmtYaTJ')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        # Pattern weights for scoring
        self.pattern_weights = {
            PatternType.LIQUIDATION_CASCADE: 0.25,
            PatternType.LIQUIDATION_SQUEEZE: 0.20,
            PatternType.RISK_BAND_TOUCH: 0.20,
            PatternType.RISK_BAND_BREAKOUT: 0.15,
            PatternType.VOLUME_SPIKE: 0.10,
            PatternType.ACCUMULATION: 0.05,
            PatternType.DISTRIBUTION: 0.05
        }
        
        logger.info("🎯 Unified Pattern Agent initialized")
    
    async def analyze_symbol(self, symbol: str, data_sources: Dict[str, Any]) -> PatternAnalysisResult:
        """
        Perform comprehensive pattern analysis for a symbol
        
        Args:
            symbol: Trading symbol (e.g., "BTC-USDT")
            data_sources: Dictionary containing data from all sources
                {
                    "riskmetric": {...},
                    "cryptometer": {...},
                    "kingfisher": {...}
                }
        
        Returns:
            PatternAnalysisResult with complete analysis
        """
        logger.info(f"🔍 Analyzing patterns for {symbol}")
        
        # Detect patterns from each source
        all_patterns = []
        
        # Kingfisher patterns (liquidation data)
        if "kingfisher" in data_sources:
            kingfisher_patterns = self.detection_engine.detect_liquidation_patterns(
                data_sources["kingfisher"]
            )
            all_patterns.extend(kingfisher_patterns)
        
        # RiskMetric patterns (risk bands)
        if "riskmetric" in data_sources:
            riskmetric_patterns = self.detection_engine.detect_risk_band_patterns(
                data_sources["riskmetric"]
            )
            all_patterns.extend(riskmetric_patterns)
        
        # Cryptometer patterns (market metrics)
        if "cryptometer" in data_sources:
            cryptometer_patterns = self.detection_engine.detect_cryptometer_patterns(
                data_sources["cryptometer"]
            )
            all_patterns.extend(cryptometer_patterns)
        
        # Find pattern confluences and create integrated patterns
        integrated_patterns = self._integrate_patterns(all_patterns)
        
        # Calculate pattern score
        pattern_score = self._calculate_pattern_score(all_patterns, integrated_patterns)
        
        # Determine signal strength
        signal_strength = self._determine_signal_strength(pattern_score, integrated_patterns)
        
        # Calculate win rates
        win_rates = self._calculate_win_rates(all_patterns, integrated_patterns)
        
        # Assess risk
        risk_metrics = self._assess_risk(all_patterns, data_sources)
        
        # Determine market phase
        market_phase = self._determine_market_phase(all_patterns, data_sources)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            integrated_patterns, win_rates, risk_metrics, market_phase
        )
        
        # Generate professional reports
        reports = await self._generate_reports(
            symbol, all_patterns, integrated_patterns, win_rates, risk_metrics, market_phase
        )
        
        # Store patterns for learning
        self._store_patterns(symbol, all_patterns)
        
        return PatternAnalysisResult(
            symbol=symbol,
            timestamp=datetime.now(),
            detected_patterns=all_patterns,
            integrated_patterns=integrated_patterns,
            pattern_clusters=self._cluster_patterns(all_patterns),
            pattern_score=pattern_score,
            signal_strength=signal_strength,
            confidence_level=self._calculate_confidence(all_patterns, integrated_patterns),
            win_rates=win_rates,
            historical_accuracy=self._get_historical_accuracy(symbol),
            risk_score=risk_metrics["risk_score"],
            max_drawdown_risk=risk_metrics["max_drawdown"],
            liquidation_risk=risk_metrics["liquidation_risk"],
            market_phase=market_phase,
            volatility_regime=risk_metrics["volatility_regime"],
            trend_strength=self._calculate_trend_strength(data_sources),
            entry_zones=recommendations["entry_zones"],
            exit_targets=recommendations["exit_targets"],
            position_sizing=recommendations["position_size"],
            risk_management=recommendations["risk_management"],
            executive_summary=reports["executive_summary"],
            technical_analysis=reports["technical_analysis"],
            pattern_narrative=reports["pattern_narrative"]
        )
    
    def _integrate_patterns(self, patterns: List[PatternSignal]) -> List[IntegratedPattern]:
        """Find pattern confluences and create integrated patterns"""
        integrated = []
        
        # Group patterns by direction and timeframe
        grouped = defaultdict(list)
        for pattern in patterns:
            key = (pattern.direction, pattern.timeframe)
            grouped[key].append(pattern)
        
        # Create integrated patterns for groups with multiple signals
        for (direction, timeframe), group_patterns in grouped.items():
            if len(group_patterns) >= 2:  # At least 2 patterns for confluence
                # Calculate confluence score
                sources = set(p.source for p in group_patterns)
                confluence_score = len(sources) / 3 * 100  # 3 total sources
                
                # Determine combined strength
                avg_strength = statistics.mean(p.strength.value for p in group_patterns)
                combined_strength = PatternStrength(min(5, int(avg_strength + len(sources) - 1)))
                
                # Estimate win rates
                win_rate_estimate = {
                    "24h": 50 + confluence_score * 0.3,
                    "7d": 45 + confluence_score * 0.25,
                    "1m": 40 + confluence_score * 0.2
                }
                
                integrated.append(IntegratedPattern(
                    pattern_id=f"INT_{datetime.now().timestamp()}",
                    primary_pattern=max(group_patterns, key=lambda p: p.confidence),
                    supporting_patterns=group_patterns[1:],
                    confluence_score=confluence_score,
                    combined_strength=combined_strength,
                    market_phase=MarketPhase.UNCERTAINTY,  # Will be updated
                    win_rate_estimate=win_rate_estimate,
                    risk_assessment={"confluence_count": len(group_patterns)},
                    recommendations=[
                        f"Multiple {direction} signals detected",
                        f"Confluence from {len(sources)} data sources"
                    ],
                    timestamp=datetime.now()
                ))
        
        return integrated
    
    def _calculate_pattern_score(self, patterns: List[PatternSignal], 
                                integrated: List[IntegratedPattern]) -> float:
        """Calculate overall pattern score (0-100)"""
        if not patterns and not integrated:
            return 0
        
        # Base score from individual patterns
        pattern_score = 0
        for pattern in patterns:
            weight = self.pattern_weights.get(pattern.pattern_type, 0.05)
            pattern_score += pattern.confidence * weight * pattern.strength.value / 5
        
        # Bonus for integrated patterns
        for int_pattern in integrated:
            pattern_score += int_pattern.confluence_score * 0.2
        
        return min(100, pattern_score)
    
    def _determine_signal_strength(self, score: float, 
                                  integrated: List[IntegratedPattern]) -> str:
        """Determine trading signal strength"""
        # Check for strong integrated patterns
        if integrated:
            max_confluence = max(p.confluence_score for p in integrated)
            if max_confluence > 80 and score > 70:
                direction = integrated[0].primary_pattern.direction
                return f"strong_{direction}"
        
        # Score-based determination
        if score >= 80:
            return "strong_buy"
        elif score >= 60:
            return "buy"
        elif score >= 40:
            return "neutral"
        elif score >= 20:
            return "sell"
        else:
            return "strong_sell"
    
    def _calculate_win_rates(self, patterns: List[PatternSignal], 
                           integrated: List[IntegratedPattern]) -> Dict[str, Dict[str, float]]:
        """Calculate win rates for different timeframes"""
        win_rates = {
            "24h": {"long": 50.0, "short": 50.0},
            "7d": {"long": 50.0, "short": 50.0},
            "1m": {"long": 50.0, "short": 50.0}
        }
        
        # Adjust based on pattern signals
        for pattern in patterns:
            adjustment = pattern.confidence * 0.1
            if pattern.direction == "long":
                for tf in win_rates:
                    win_rates[tf]["long"] = min(95, win_rates[tf]["long"] + adjustment)
                    win_rates[tf]["short"] = 100 - win_rates[tf]["long"]
            elif pattern.direction == "short":
                for tf in win_rates:
                    win_rates[tf]["short"] = min(95, win_rates[tf]["short"] + adjustment)
                    win_rates[tf]["long"] = 100 - win_rates[tf]["short"]
        
        # Apply integrated pattern adjustments
        for int_pattern in integrated:
            for tf, rate in int_pattern.win_rate_estimate.items():
                if int_pattern.primary_pattern.direction == "long":
                    win_rates[tf]["long"] = rate
                    win_rates[tf]["short"] = 100 - rate
                else:
                    win_rates[tf]["short"] = rate
                    win_rates[tf]["long"] = 100 - rate
        
        return win_rates
    
    def _assess_risk(self, patterns: List[PatternSignal], 
                    data_sources: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk metrics"""
        risk_score = 50  # Baseline
        
        # Adjust based on pattern conflicts
        directions = [p.direction for p in patterns]
        if directions:
            conflict_ratio = 1 - (directions.count(max(set(directions), key=directions.count)) / len(directions))
            risk_score += conflict_ratio * 30
        
        # Liquidation risk from Kingfisher
        liquidation_risk = 0
        if "kingfisher" in data_sources:
            total_liq = data_sources["kingfisher"].get("total_liquidations", 0)
            if total_liq > 1000000:  # $1M+ liquidations
                liquidation_risk = min(95, total_liq / 10000000 * 100)
        
        # Volatility assessment
        volatility_regime = "normal"
        if "cryptometer" in data_sources:
            volatility = data_sources["cryptometer"].get("volatility_24h", 0)
            if volatility > 5:
                volatility_regime = "high"
            elif volatility > 10:
                volatility_regime = "extreme"
        
        return {
            "risk_score": min(100, risk_score),
            "max_drawdown": 15.0,  # Default conservative estimate
            "liquidation_risk": liquidation_risk,
            "volatility_regime": volatility_regime
        }
    
    def _determine_market_phase(self, patterns: List[PatternSignal], 
                               data_sources: Dict[str, Any]) -> MarketPhase:
        """Determine current market phase"""
        # Check for accumulation/distribution patterns
        for pattern in patterns:
            if pattern.pattern_type == PatternType.ACCUMULATION:
                return MarketPhase.ACCUMULATION
            elif pattern.pattern_type == PatternType.DISTRIBUTION:
                return MarketPhase.DISTRIBUTION
        
        # Check risk metric level
        if "riskmetric" in data_sources:
            risk_value = data_sources["riskmetric"].get("risk_metric", 0.5)
            if risk_value < 0.3:
                return MarketPhase.ACCUMULATION
            elif risk_value > 0.7:
                return MarketPhase.DISTRIBUTION
            elif 0.4 < risk_value < 0.6:
                return MarketPhase.MARKUP
        
        return MarketPhase.UNCERTAINTY
    
    def _generate_recommendations(self, integrated: List[IntegratedPattern],
                                 win_rates: Dict, risk_metrics: Dict,
                                 market_phase: MarketPhase) -> Dict[str, Any]:
        """Generate trading recommendations"""
        recommendations = {
            "entry_zones": [],
            "exit_targets": [],
            "position_size": 0.02,  # 2% default
            "risk_management": {}
        }
        
        # Adjust position size based on confidence
        if integrated:
            max_confluence = max(p.confluence_score for p in integrated)
            recommendations["position_size"] = min(0.05, 0.01 + max_confluence / 2500)
        
        # Entry zones from patterns
        for pattern in integrated:
            if pattern.primary_pattern.entry_price:
                recommendations["entry_zones"].append({
                    "price": pattern.primary_pattern.entry_price,
                    "confidence": pattern.confluence_score,
                    "timeframe": pattern.primary_pattern.timeframe
                })
        
        # Risk management
        recommendations["risk_management"] = {
            "stop_loss_percentage": 2 + risk_metrics["risk_score"] / 20,
            "max_position_size": 0.05,
            "use_trailing_stop": risk_metrics["volatility_regime"] == "high",
            "scaling_strategy": "pyramid" if market_phase == MarketPhase.MARKUP else "fixed"
        }
        
        return recommendations
    
    async def _generate_reports(self, symbol: str, patterns: List[PatternSignal],
                               integrated: List[IntegratedPattern], win_rates: Dict,
                               risk_metrics: Dict, market_phase: MarketPhase) -> Dict[str, str]:
        """Generate professional analysis reports"""
        
        executive_summary = f"""
        **{symbol} Pattern Analysis Report**
        
        **Pattern Detection Summary:**
        - Detected {len(patterns)} individual patterns
        - Found {len(integrated)} integrated high-confidence patterns
        - Market Phase: {market_phase.value.upper()}
        - Risk Level: {risk_metrics['risk_score']:.1f}/100
        
        **Win Rate Projections:**
        - 24H: {win_rates['24h']['long']:.1f}% Long / {win_rates['24h']['short']:.1f}% Short
        - 7D: {win_rates['7d']['long']:.1f}% Long / {win_rates['7d']['short']:.1f}% Short
        - 1M: {win_rates['1m']['long']:.1f}% Long / {win_rates['1m']['short']:.1f}% Short
        """
        
        technical_analysis = self._generate_technical_analysis(patterns, integrated)
        pattern_narrative = self._generate_pattern_narrative(patterns, integrated, market_phase)
        
        return {
            "executive_summary": executive_summary,
            "technical_analysis": technical_analysis,
            "pattern_narrative": pattern_narrative
        }
    
    def _generate_technical_analysis(self, patterns: List[PatternSignal],
                                    integrated: List[IntegratedPattern]) -> str:
        """Generate technical analysis section"""
        analysis = "**Technical Pattern Analysis:**\n\n"
        
        # Group patterns by type
        by_type = defaultdict(list)
        for pattern in patterns:
            by_type[pattern.pattern_type].append(pattern)
        
        for pattern_type, type_patterns in by_type.items():
            avg_confidence = statistics.mean(p.confidence for p in type_patterns)
            analysis += f"- **{pattern_type.value}**: {len(type_patterns)} occurrences, "
            analysis += f"{avg_confidence:.1f}% average confidence\n"
        
        if integrated:
            analysis += "\n**Confluence Patterns:**\n"
            for int_pattern in integrated:
                analysis += f"- {int_pattern.combined_strength.name} confluence: "
                analysis += f"{int_pattern.confluence_score:.1f}% score\n"
        
        return analysis
    
    def _generate_pattern_narrative(self, patterns: List[PatternSignal],
                                   integrated: List[IntegratedPattern],
                                   market_phase: MarketPhase) -> str:
        """Generate narrative explanation of patterns"""
        narrative = f"""
        **Market Pattern Narrative:**
        
        The market is currently in the {market_phase.value} phase based on pattern analysis.
        """
        
        if integrated:
            primary = integrated[0]
            narrative += f"""
            
            A strong {primary.combined_strength.name.lower()} pattern confluence has been detected,
            with {len(primary.supporting_patterns) + 1} confirming signals across multiple data sources.
            This suggests a {primary.primary_pattern.direction} bias with {primary.confluence_score:.1f}% confidence.
            """
        
        # Add pattern-specific insights
        liquidation_patterns = [p for p in patterns if "liquidation" in p.pattern_type.value]
        if liquidation_patterns:
            narrative += """
            
            Liquidation analysis reveals significant positioning imbalances that could trigger
            cascade events. Traders should monitor key liquidation levels closely.
            """
        
        risk_patterns = [p for p in patterns if "risk_band" in p.pattern_type.value]
        if risk_patterns:
            narrative += """
            
            Risk band analysis indicates the market is at a critical juncture. Historical data
            suggests strong mean reversion tendencies at these levels.
            """
        
        return narrative
    
    def _cluster_patterns(self, patterns: List[PatternSignal]) -> List[Dict[str, Any]]:
        """Cluster related patterns together"""
        clusters = []
        
        # Simple clustering by timeframe and direction
        grouped = defaultdict(list)
        for pattern in patterns:
            key = (pattern.timeframe, pattern.direction)
            grouped[key].append(pattern)
        
        for (timeframe, direction), group in grouped.items():
            if len(group) > 1:
                clusters.append({
                    "timeframe": timeframe,
                    "direction": direction,
                    "pattern_count": len(group),
                    "patterns": [p.pattern_type.value for p in group],
                    "avg_confidence": statistics.mean(p.confidence for p in group)
                })
        
        return clusters
    
    def _calculate_confidence(self, patterns: List[PatternSignal],
                            integrated: List[IntegratedPattern]) -> float:
        """Calculate overall confidence level"""
        if not patterns:
            return 0
        
        # Base confidence from patterns
        base_confidence = statistics.mean(p.confidence for p in patterns)
        
        # Boost for integrated patterns
        if integrated:
            confluence_boost = max(p.confluence_score for p in integrated) * 0.2
            base_confidence = min(100, base_confidence + confluence_boost)
        
        return base_confidence
    
    def _get_historical_accuracy(self, symbol: str) -> float:
        """Get historical accuracy for this symbol"""
        # TODO: Implement historical tracking
        return 75.0  # Default placeholder
    
    def _calculate_trend_strength(self, data_sources: Dict[str, Any]) -> float:
        """Calculate trend strength from available data"""
        trend_strength = 50.0  # Neutral baseline
        
        # Adjust based on risk metric
        if "riskmetric" in data_sources:
            risk_value = data_sources["riskmetric"].get("risk_metric", 0.5)
            if risk_value < 0.3 or risk_value > 0.7:
                trend_strength += 20
        
        # Adjust based on funding rate
        if "cryptometer" in data_sources:
            funding = abs(data_sources["cryptometer"].get("funding_rate", 0))
            trend_strength += min(30, funding * 500)
        
        return min(100, trend_strength)
    
    def _store_patterns(self, symbol: str, patterns: List[PatternSignal]):
        """Store patterns for learning and analysis"""
        for pattern in patterns:
            self.pattern_history[symbol].append({
                "pattern": pattern,
                "timestamp": datetime.now()
            })
    
    async def update_pattern_performance(self, symbol: str, pattern_id: str, 
                                        actual_outcome: Dict[str, Any]):
        """Update pattern performance for learning"""
        # TODO: Implement performance tracking
        pass
    
    async def get_pattern_statistics(self, symbol: str) -> Dict[str, Any]:
        """Get pattern statistics for a symbol"""
        history = self.pattern_history.get(symbol, [])
        
        if not history:
            return {"message": "No pattern history available"}
        
        # Calculate statistics
        pattern_counts = defaultdict(int)
        confidence_scores = []
        
        for entry in history:
            pattern = entry["pattern"]
            pattern_counts[pattern.pattern_type.value] += 1
            confidence_scores.append(pattern.confidence)
        
        return {
            "total_patterns": len(history),
            "pattern_distribution": dict(pattern_counts),
            "average_confidence": statistics.mean(confidence_scores) if confidence_scores else 0,
            "most_common_pattern": max(pattern_counts.items(), key=lambda x: x[1])[0] if pattern_counts else None
        }

# ==================== API Interface ====================

async def analyze_symbol_patterns(symbol: str, 
                                 riskmetric_data: Optional[Dict] = None,
                                 cryptometer_data: Optional[Dict] = None,
                                 kingfisher_data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Main API function to analyze patterns for a symbol
    
    Args:
        symbol: Trading symbol
        riskmetric_data: Data from RiskMetric agent
        cryptometer_data: Data from Cryptometer agent
        kingfisher_data: Data from Kingfisher module
    
    Returns:
        Complete pattern analysis
    """
    agent = UnifiedPatternAgent()
    
    # Prepare data sources
    data_sources = {}
    if riskmetric_data:
        data_sources["riskmetric"] = riskmetric_data
    if cryptometer_data:
        data_sources["cryptometer"] = cryptometer_data
    if kingfisher_data:
        data_sources["kingfisher"] = kingfisher_data
    
    # Run analysis
    result = await agent.analyze_symbol(symbol, data_sources)
    
    # Convert to dictionary for API response
    return asdict(result)

# ==================== Self-Learning Component ====================

class PatternLearningModule:
    """Machine learning module for pattern recognition improvement"""
    
    def __init__(self):
        self.model = None  # TODO: Implement ML model
        self.training_data = []
        
    async def learn_from_outcome(self, pattern: PatternSignal, outcome: Dict[str, Any]):
        """Learn from pattern outcomes"""
        # TODO: Implement learning algorithm
        pass
    
    async def predict_pattern_success(self, pattern: PatternSignal) -> float:
        """Predict pattern success probability"""
        # TODO: Implement prediction
        return 0.75  # Placeholder

if __name__ == "__main__":
    # Test the agent
    async def test():
        # Sample data
        test_data = {
            "riskmetric": {
                "risk_metric": 0.25,
                "current_price": 50000,
                "lower_band": 45000,
                "upper_band": 55000
            },
            "cryptometer": {
                "fear_greed_index": 35,
                "funding_rate": 0.01,
                "open_interest_change": 15,
                "volume_24h_change": 75,
                "volatility_24h": 3.5
            },
            "kingfisher": {
                "long_liquidations": 2500000,
                "short_liquidations": 8500000,
                "total_liquidations": 11000000
            }
        }
        
        result = await analyze_symbol_patterns(
            "BTC-USDT",
            test_data["riskmetric"],
            test_data["cryptometer"],
            test_data["kingfisher"]
        )
        
        print(json.dumps(result, indent=2, default=str))
    
    asyncio.run(test())