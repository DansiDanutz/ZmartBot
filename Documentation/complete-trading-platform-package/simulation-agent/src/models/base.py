"""
Simulation Agent - Base Data Models
==================================

Professional data models for trading pattern analysis and simulation.
Verified for zero-conflict integration with ZmartBot, KingFisher, and Trade Strategy.

Author: Manus AI
Version: 1.0 Professional Edition
Compatibility: Mac Mini 2025 M2 Pro Integration
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import json
import uuid

# Enums for standardized values
class PatternType(Enum):
    """Standardized pattern types for analysis"""
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    ASCENDING_TRIANGLE = "ascending_triangle"
    DESCENDING_TRIANGLE = "descending_triangle"
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"
    RISING_WEDGE = "rising_wedge"
    FALLING_WEDGE = "falling_wedge"
    FLAG = "flag"
    PENNANT = "pennant"
    SUPPORT_LEVEL = "support_level"
    RESISTANCE_LEVEL = "resistance_level"
    UPWARD_BREAKOUT = "upward_breakout"
    DOWNWARD_BREAKOUT = "downward_breakout"
    LIQUIDATION_CLUSTER = "liquidation_cluster"

class Direction(Enum):
    """Trading direction enumeration"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

class MarketConditionType(Enum):
    """Market condition classifications"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    BREAKOUT = "breakout"
    BREAKDOWN = "breakdown"

class RiskLevel(Enum):
    """Risk level classifications"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

# Core Data Models
@dataclass
class PatternMatch:
    """Represents a detected trading pattern"""
    
    pattern_type: str
    timestamp: datetime
    confidence: float
    price_level: Decimal
    direction: str
    target_price: Decimal
    stop_loss: Decimal
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Additional analysis fields
    pattern_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timeframe: str = "1h"
    strength: float = 0.0
    reliability_score: float = 0.0
    historical_success_rate: float = 0.0
    
    def __post_init__(self):
        """Validate and normalize pattern data"""
        # Ensure confidence is between 0 and 1
        self.confidence = max(0.0, min(1.0, self.confidence))
        
        # Ensure prices are positive
        if self.price_level <= 0:
            raise ValueError("Price level must be positive")
        if self.target_price <= 0:
            raise ValueError("Target price must be positive")
        if self.stop_loss <= 0:
            raise ValueError("Stop loss must be positive")
        
        # Validate direction
        if self.direction not in ["bullish", "bearish", "neutral"]:
            raise ValueError("Direction must be bullish, bearish, or neutral")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "price_level": float(self.price_level),
            "direction": self.direction,
            "target_price": float(self.target_price),
            "stop_loss": float(self.stop_loss),
            "timeframe": self.timeframe,
            "strength": self.strength,
            "reliability_score": self.reliability_score,
            "historical_success_rate": self.historical_success_rate,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatternMatch':
        """Create from dictionary"""
        return cls(
            pattern_type=data["pattern_type"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            confidence=data["confidence"],
            price_level=Decimal(str(data["price_level"])),
            direction=data["direction"],
            target_price=Decimal(str(data["target_price"])),
            stop_loss=Decimal(str(data["stop_loss"])),
            metadata=data.get("metadata", {}),
            pattern_id=data.get("pattern_id", str(uuid.uuid4())),
            timeframe=data.get("timeframe", "1h"),
            strength=data.get("strength", 0.0),
            reliability_score=data.get("reliability_score", 0.0),
            historical_success_rate=data.get("historical_success_rate", 0.0)
        )

@dataclass
class SimulationTrade:
    """Represents a simulated trade with complete lifecycle"""
    
    trade_id: str
    symbol: str
    direction: str
    entry_time: datetime
    entry_price: Decimal
    position_size: Decimal
    leverage: int
    
    # Exit information
    exit_time: Optional[datetime] = None
    exit_price: Optional[Decimal] = None
    exit_reason: Optional[str] = None
    
    # Performance metrics
    pnl: Optional[Decimal] = None
    pnl_percentage: Optional[Decimal] = None
    duration_hours: Optional[float] = None
    max_favorable_excursion: Optional[Decimal] = None
    max_adverse_excursion: Optional[Decimal] = None
    
    # Risk metrics
    max_drawdown: Optional[Decimal] = None
    risk_reward_ratio: Optional[float] = None
    
    # Pattern context
    pattern_id: Optional[str] = None
    pattern_confidence: Optional[float] = None
    market_condition: Optional[str] = None
    
    def __post_init__(self):
        """Validate trade data"""
        if self.position_size <= 0:
            raise ValueError("Position size must be positive")
        if self.leverage <= 0:
            raise ValueError("Leverage must be positive")
        if self.entry_price <= 0:
            raise ValueError("Entry price must be positive")
    
    def is_winner(self) -> bool:
        """Check if trade is profitable"""
        return self.pnl is not None and self.pnl > 0
    
    def is_closed(self) -> bool:
        """Check if trade is closed"""
        return self.exit_time is not None and self.exit_price is not None
    
    def calculate_basic_metrics(self):
        """Calculate basic trade metrics"""
        if not self.is_closed():
            return
        
        # Basic PnL calculation
        if self.direction.lower() == "long":
            self.pnl = (self.exit_price - self.entry_price) * self.position_size * self.leverage
        else:
            self.pnl = (self.entry_price - self.exit_price) * self.position_size * self.leverage
        
        # PnL percentage
        invested_amount = self.entry_price * self.position_size
        self.pnl_percentage = (self.pnl / invested_amount) * 100 if invested_amount > 0 else Decimal('0')
        
        # Duration
        if self.exit_time and self.entry_time:
            duration_delta = self.exit_time - self.entry_time
            self.duration_hours = duration_delta.total_seconds() / 3600
        
        # Risk-reward ratio
        if self.pnl and self.max_adverse_excursion and self.max_adverse_excursion > 0:
            self.risk_reward_ratio = float(abs(self.pnl) / self.max_adverse_excursion)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "direction": self.direction,
            "entry_time": self.entry_time.isoformat(),
            "entry_price": float(self.entry_price),
            "position_size": float(self.position_size),
            "leverage": self.leverage,
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "exit_price": float(self.exit_price) if self.exit_price else None,
            "exit_reason": self.exit_reason,
            "pnl": float(self.pnl) if self.pnl else None,
            "pnl_percentage": float(self.pnl_percentage) if self.pnl_percentage else None,
            "duration_hours": self.duration_hours,
            "max_favorable_excursion": float(self.max_favorable_excursion) if self.max_favorable_excursion else None,
            "max_adverse_excursion": float(self.max_adverse_excursion) if self.max_adverse_excursion else None,
            "max_drawdown": float(self.max_drawdown) if self.max_drawdown else None,
            "risk_reward_ratio": self.risk_reward_ratio,
            "pattern_id": self.pattern_id,
            "pattern_confidence": self.pattern_confidence,
            "market_condition": self.market_condition
        }

@dataclass
class WinRatioAnalysis:
    """Comprehensive win ratio analysis for a trading direction"""
    
    direction: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_ratio: float
    profit_factor: float
    average_win: Decimal
    average_loss: Decimal
    max_consecutive_wins: int
    max_consecutive_losses: int
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: Decimal
    confidence_interval: Tuple[float, float]
    trades: List[SimulationTrade] = field(default_factory=list)
    
    # Additional metrics
    calmar_ratio: float = 0.0
    information_ratio: float = 0.0
    recovery_factor: float = 0.0
    profit_to_max_drawdown: float = 0.0
    
    def __post_init__(self):
        """Calculate additional metrics"""
        self._calculate_additional_metrics()
    
    def _calculate_additional_metrics(self):
        """Calculate additional performance metrics"""
        if not self.trades:
            return
        
        # Calculate total profit/loss
        total_pnl = sum(trade.pnl for trade in self.trades if trade.pnl)
        
        # Calmar ratio (annual return / max drawdown)
        if self.max_drawdown > 0:
            annual_return = float(total_pnl) * (365 / max(1, len(self.trades)))  # Annualized
            self.calmar_ratio = annual_return / float(self.max_drawdown)
        
        # Recovery factor (total profit / max drawdown)
        if self.max_drawdown > 0:
            self.recovery_factor = float(total_pnl) / float(self.max_drawdown)
        
        # Profit to max drawdown ratio
        if self.max_drawdown > 0:
            self.profit_to_max_drawdown = float(total_pnl) / float(self.max_drawdown)
    
    def get_performance_grade(self) -> str:
        """Get performance grade based on metrics"""
        score = 0
        
        # Win ratio component (0-30 points)
        if self.win_ratio >= 0.7:
            score += 30
        elif self.win_ratio >= 0.6:
            score += 25
        elif self.win_ratio >= 0.5:
            score += 20
        elif self.win_ratio >= 0.4:
            score += 15
        else:
            score += 10
        
        # Profit factor component (0-25 points)
        if self.profit_factor >= 2.0:
            score += 25
        elif self.profit_factor >= 1.5:
            score += 20
        elif self.profit_factor >= 1.2:
            score += 15
        elif self.profit_factor >= 1.0:
            score += 10
        else:
            score += 5
        
        # Sharpe ratio component (0-25 points)
        if self.sharpe_ratio >= 2.0:
            score += 25
        elif self.sharpe_ratio >= 1.5:
            score += 20
        elif self.sharpe_ratio >= 1.0:
            score += 15
        elif self.sharpe_ratio >= 0.5:
            score += 10
        else:
            score += 5
        
        # Max drawdown component (0-20 points)
        max_dd_pct = float(self.max_drawdown) / max(1, float(self.average_win)) * 100
        if max_dd_pct <= 5:
            score += 20
        elif max_dd_pct <= 10:
            score += 15
        elif max_dd_pct <= 20:
            score += 10
        elif max_dd_pct <= 30:
            score += 5
        else:
            score += 0
        
        # Convert to grade
        if score >= 85:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 75:
            return "A-"
        elif score >= 70:
            return "B+"
        elif score >= 65:
            return "B"
        elif score >= 60:
            return "B-"
        elif score >= 55:
            return "C+"
        elif score >= 50:
            return "C"
        elif score >= 45:
            return "C-"
        elif score >= 40:
            return "D"
        else:
            return "F"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "direction": self.direction,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_ratio": self.win_ratio,
            "profit_factor": self.profit_factor,
            "average_win": float(self.average_win),
            "average_loss": float(self.average_loss),
            "max_consecutive_wins": self.max_consecutive_wins,
            "max_consecutive_losses": self.max_consecutive_losses,
            "sharpe_ratio": self.sharpe_ratio,
            "sortino_ratio": self.sortino_ratio,
            "max_drawdown": float(self.max_drawdown),
            "confidence_interval": self.confidence_interval,
            "calmar_ratio": self.calmar_ratio,
            "information_ratio": self.information_ratio,
            "recovery_factor": self.recovery_factor,
            "profit_to_max_drawdown": self.profit_to_max_drawdown,
            "performance_grade": self.get_performance_grade(),
            "trades": [trade.to_dict() for trade in self.trades]
        }

@dataclass
class MarketCondition:
    """Represents a specific market condition for analysis"""
    
    condition_type: str
    start_time: datetime
    end_time: datetime
    volatility: float
    volume_profile: str
    dominant_pattern: Optional[str] = None
    confidence: float = 0.0
    
    # Additional context
    condition_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    strength: float = 0.0
    trend_direction: Optional[str] = None
    support_levels: List[float] = field(default_factory=list)
    resistance_levels: List[float] = field(default_factory=list)
    
    def duration_hours(self) -> float:
        """Calculate duration in hours"""
        return (self.end_time - self.start_time).total_seconds() / 3600
    
    def duration_days(self) -> float:
        """Calculate duration in days"""
        return self.duration_hours() / 24
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "condition_id": self.condition_id,
            "condition_type": self.condition_type,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "volatility": self.volatility,
            "volume_profile": self.volume_profile,
            "dominant_pattern": self.dominant_pattern,
            "confidence": self.confidence,
            "strength": self.strength,
            "trend_direction": self.trend_direction,
            "support_levels": self.support_levels,
            "resistance_levels": self.resistance_levels,
            "duration_hours": self.duration_hours(),
            "duration_days": self.duration_days()
        }

@dataclass
class SimulationResult:
    """Complete simulation result with all analysis data"""
    
    symbol: str
    analysis_period_days: int
    patterns_detected: List[PatternMatch]
    long_position_analysis: WinRatioAnalysis
    short_position_analysis: WinRatioAnalysis
    overall_metrics: Dict[str, Any]
    market_conditions: List[MarketCondition]
    technical_indicators: Dict[str, float]
    report_data: Dict[str, Any]
    timestamp: datetime
    
    # Additional metadata
    simulation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data_sources: List[str] = field(default_factory=list)
    data_quality_score: float = 0.0
    processing_time_seconds: float = 0.0
    
    def __post_init__(self):
        """Calculate derived metrics"""
        self._calculate_overall_performance()
    
    def _calculate_overall_performance(self):
        """Calculate overall performance metrics"""
        # Combine long and short analysis
        total_trades = self.long_position_analysis.total_trades + self.short_position_analysis.total_trades
        total_wins = self.long_position_analysis.winning_trades + self.short_position_analysis.winning_trades
        
        if total_trades > 0:
            overall_win_ratio = total_wins / total_trades
            
            # Best direction analysis
            if self.long_position_analysis.win_ratio > self.short_position_analysis.win_ratio:
                best_direction = "long"
                direction_advantage = self.long_position_analysis.win_ratio - self.short_position_analysis.win_ratio
            elif self.short_position_analysis.win_ratio > self.long_position_analysis.win_ratio:
                best_direction = "short"
                direction_advantage = self.short_position_analysis.win_ratio - self.long_position_analysis.win_ratio
            else:
                best_direction = "neutral"
                direction_advantage = 0.0
            
            # Update overall metrics
            self.overall_metrics.update({
                "total_trades": total_trades,
                "overall_win_ratio": overall_win_ratio,
                "best_direction": best_direction,
                "direction_advantage": direction_advantage,
                "patterns_per_day": len(self.patterns_detected) / max(1, self.analysis_period_days),
                "data_completeness": self.data_quality_score
            })
    
    def get_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary"""
        return {
            "symbol": self.symbol,
            "analysis_period": f"{self.analysis_period_days} days",
            "patterns_detected": len(self.patterns_detected),
            "recommended_direction": self.overall_metrics.get("best_direction", "neutral"),
            "confidence_level": f"{self.overall_metrics.get('direction_advantage', 0.0):.1%}",
            "long_win_ratio": f"{self.long_position_analysis.win_ratio:.1%}",
            "short_win_ratio": f"{self.short_position_analysis.win_ratio:.1%}",
            "data_quality": f"{self.data_quality_score:.1%}",
            "processing_time": f"{self.processing_time_seconds:.1f}s",
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "simulation_id": self.simulation_id,
            "symbol": self.symbol,
            "analysis_period_days": self.analysis_period_days,
            "patterns_detected": [p.to_dict() for p in self.patterns_detected],
            "long_position_analysis": self.long_position_analysis.to_dict(),
            "short_position_analysis": self.short_position_analysis.to_dict(),
            "overall_metrics": self.overall_metrics,
            "market_conditions": [mc.to_dict() for mc in self.market_conditions],
            "technical_indicators": self.technical_indicators,
            "report_data": self.report_data,
            "timestamp": self.timestamp.isoformat(),
            "data_sources": self.data_sources,
            "data_quality_score": self.data_quality_score,
            "processing_time_seconds": self.processing_time_seconds,
            "executive_summary": self.get_executive_summary()
        }

# Data Integration Models
@dataclass
class KingFisherData:
    """KingFisher analysis data structure"""
    
    symbol: str
    timestamp: datetime
    liquidation_clusters: List[Dict[str, Any]]
    short_term_liquidation_ratio: Dict[str, float]
    long_term_liquidation_ratio: Dict[str, float]
    toxic_order_flow: Dict[str, Any]
    rsi_heatmap: Dict[str, Any]
    leverage_data: Dict[str, Any]
    market_balance: Dict[str, Any]
    custom_indicators: Dict[str, float]
    
    # Quality metrics
    data_completeness: float = 1.0
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "liquidation_clusters": self.liquidation_clusters,
            "short_term_liquidation_ratio": self.short_term_liquidation_ratio,
            "long_term_liquidation_ratio": self.long_term_liquidation_ratio,
            "toxic_order_flow": self.toxic_order_flow,
            "rsi_heatmap": self.rsi_heatmap,
            "leverage_data": self.leverage_data,
            "market_balance": self.market_balance,
            "custom_indicators": self.custom_indicators,
            "data_completeness": self.data_completeness,
            "confidence_score": self.confidence_score
        }

@dataclass
class CryptometerData:
    """Cryptometer API data structure"""
    
    symbol: str
    timestamp: datetime
    tier_1_data: Dict[str, Any]  # Primary indicators
    tier_2_data: Dict[str, Any]  # Secondary indicators
    tier_3_data: Dict[str, Any]  # Supporting indicators
    tier_scores: Dict[str, float]
    overall_score: float
    historical_trends: Dict[str, Any]
    data_quality_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "tier_1_data": self.tier_1_data,
            "tier_2_data": self.tier_2_data,
            "tier_3_data": self.tier_3_data,
            "tier_scores": self.tier_scores,
            "overall_score": self.overall_score,
            "historical_trends": self.historical_trends,
            "data_quality_score": self.data_quality_score
        }

@dataclass
class RiskMetricData:
    """RiskMetric scoring data structure"""
    
    symbol: str
    timestamp: datetime
    current_risk_band: str
    risk_score: float
    risk_factors: Dict[str, float]
    historical_risk_bands: List[Dict[str, Any]]
    risk_transitions: Dict[str, Any]
    time_in_risk_bands: Dict[str, float]
    composite_score: float
    risk_trend: str
    confidence_level: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "current_risk_band": self.current_risk_band,
            "risk_score": self.risk_score,
            "risk_factors": self.risk_factors,
            "historical_risk_bands": self.historical_risk_bands,
            "risk_transitions": self.risk_transitions,
            "time_in_risk_bands": self.time_in_risk_bands,
            "composite_score": self.composite_score,
            "risk_trend": self.risk_trend,
            "confidence_level": self.confidence_level
        }

# Utility functions for model operations
def create_sample_simulation_result(symbol: str = "BTCUSDT") -> SimulationResult:
    """Create a sample simulation result for testing"""
    
    # Sample patterns
    patterns = [
        PatternMatch(
            pattern_type="head_and_shoulders",
            timestamp=datetime.now() - timedelta(hours=24),
            confidence=0.85,
            price_level=Decimal("50000"),
            direction="bearish",
            target_price=Decimal("47500"),
            stop_loss=Decimal("51000"),
            metadata={"formation_time": "3 days", "volume_confirmation": True}
        ),
        PatternMatch(
            pattern_type="liquidation_cluster",
            timestamp=datetime.now() - timedelta(hours=12),
            confidence=0.92,
            price_level=Decimal("48500"),
            direction="bullish",
            target_price=Decimal("52000"),
            stop_loss=Decimal("47000"),
            metadata={"cluster_size": "50M USDT", "liquidation_type": "short"}
        )
    ]
    
    # Sample trades for long analysis
    long_trades = [
        SimulationTrade(
            trade_id="long_001",
            symbol=symbol,
            direction="long",
            entry_time=datetime.now() - timedelta(hours=48),
            entry_price=Decimal("49000"),
            position_size=Decimal("1000"),
            leverage=1,
            exit_time=datetime.now() - timedelta(hours=36),
            exit_price=Decimal("51000"),
            exit_reason="target_hit",
            pnl=Decimal("2000"),
            pnl_percentage=Decimal("4.08")
        )
    ]
    
    # Sample trades for short analysis
    short_trades = [
        SimulationTrade(
            trade_id="short_001",
            symbol=symbol,
            direction="short",
            entry_time=datetime.now() - timedelta(hours=24),
            entry_price=Decimal("50500"),
            position_size=Decimal("1000"),
            leverage=1,
            exit_time=datetime.now() - timedelta(hours=12),
            exit_price=Decimal("49000"),
            exit_reason="target_hit",
            pnl=Decimal("1500"),
            pnl_percentage=Decimal("2.97")
        )
    ]
    
    # Long position analysis
    long_analysis = WinRatioAnalysis(
        direction="long",
        total_trades=10,
        winning_trades=7,
        losing_trades=3,
        win_ratio=0.7,
        profit_factor=2.1,
        average_win=Decimal("1800"),
        average_loss=Decimal("600"),
        max_consecutive_wins=4,
        max_consecutive_losses=2,
        sharpe_ratio=1.45,
        sortino_ratio=1.82,
        max_drawdown=Decimal("1200"),
        confidence_interval=(0.55, 0.85),
        trades=long_trades
    )
    
    # Short position analysis
    short_analysis = WinRatioAnalysis(
        direction="short",
        total_trades=8,
        winning_trades=5,
        losing_trades=3,
        win_ratio=0.625,
        profit_factor=1.8,
        average_win=Decimal("1400"),
        average_loss=Decimal("700"),
        max_consecutive_wins=3,
        max_consecutive_losses=2,
        sharpe_ratio=1.25,
        sortino_ratio=1.55,
        max_drawdown=Decimal("1400"),
        confidence_interval=(0.45, 0.80),
        trades=short_trades
    )
    
    # Market conditions
    market_conditions = [
        MarketCondition(
            condition_type="trending_up",
            start_time=datetime.now() - timedelta(days=7),
            end_time=datetime.now() - timedelta(days=3),
            volatility=0.025,
            volume_profile="high",
            confidence=0.8
        )
    ]
    
    # Overall metrics
    overall_metrics = {
        "total_trades": 18,
        "overall_win_ratio": 0.667,
        "best_direction": "long",
        "direction_advantage": 0.075,
        "recommendation": "favorable"
    }
    
    # Technical indicators
    technical_indicators = {
        "rsi": 65.5,
        "macd": 0.15,
        "bollinger_position": 0.75,
        "volume_sma_ratio": 1.25
    }
    
    # Report data
    report_data = {
        "executive_summary": {
            "recommendation": "Favorable for long positions",
            "confidence": "High",
            "key_patterns": ["head_and_shoulders", "liquidation_cluster"]
        }
    }
    
    return SimulationResult(
        symbol=symbol,
        analysis_period_days=30,
        patterns_detected=patterns,
        long_position_analysis=long_analysis,
        short_position_analysis=short_analysis,
        overall_metrics=overall_metrics,
        market_conditions=market_conditions,
        technical_indicators=technical_indicators,
        report_data=report_data,
        timestamp=datetime.now(),
        data_sources=["kingfisher", "cryptometer", "riskmetric"],
        data_quality_score=0.92,
        processing_time_seconds=45.7
    )

# Export commonly used models
__all__ = [
    "PatternMatch",
    "SimulationTrade", 
    "WinRatioAnalysis",
    "MarketCondition",
    "SimulationResult",
    "KingFisherData",
    "CryptometerData", 
    "RiskMetricData",
    "PatternType",
    "Direction",
    "MarketConditionType",
    "RiskLevel",
    "create_sample_simulation_result"
]

