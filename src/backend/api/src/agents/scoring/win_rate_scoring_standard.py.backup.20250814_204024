#!/usr/bin/env python3
"""
Win Rate Scoring Standard - ZmartBot
Universal scoring standard where score directly correlates to win rate percentage
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TimeFrame(Enum):
    """Trading timeframes for win rate analysis"""
    SHORT_TERM = "24h"      # 24 hours
    MEDIUM_TERM = "7d"      # 7 days  
    LONG_TERM = "1m"        # 1 month

class TradeDirection(Enum):
    """Trade direction for win rate prediction"""
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"

class TradeOpportunity(Enum):
    """Trade opportunity classification based on win rate"""
    EXCEPTIONAL = "exceptional"    # 95%+ win rate - All in trade
    INFREQUENT = "infrequent"     # 90%+ win rate - High confidence
    GOOD = "good"                 # 80%+ win rate - Good opportunity
    MODERATE = "moderate"         # 70%+ win rate - Moderate opportunity
    WEAK = "weak"                 # 60%+ win rate - Weak opportunity
    AVOID = "avoid"               # <60% win rate - Avoid trade

@dataclass
class WinRateScore:
    """Win rate score for a specific timeframe and direction"""
    timeframe: TimeFrame
    direction: TradeDirection
    score: float  # 0-100 (directly correlates to win rate percentage)
    win_rate_percentage: float  # Same as score (for clarity)
    confidence: float  # Confidence in the prediction (0-1)
    opportunity_level: TradeOpportunity
    reasoning: str
    timestamp: datetime

@dataclass
class MultiTimeframeWinRate:
    """Complete win rate analysis across all timeframes"""
    symbol: str
    short_term: WinRateScore  # 24h
    medium_term: WinRateScore  # 7d
    long_term: WinRateScore  # 1m
    overall_confidence: float
    dominant_direction: TradeDirection
    best_opportunity: WinRateScore
    timestamp: datetime

class WinRateScoringStandard:
    """
    Universal Win Rate Scoring Standard for all ZmartBot agents
    
    Core Principle: Score = Win Rate Percentage
    - 80 points = 80% win rate
    - 90 points = 90% win rate  
    - 95 points = 95% win rate
    
    Opportunity Levels:
    - 95%+ = Exceptional (All in trade)
    - 90%+ = Infrequent (High confidence)
    - 80%+ = Good (Enter trade)
    - 70%+ = Moderate (Consider trade)
    - 60%+ = Weak (Cautious)
    - <60% = Avoid (No trade)
    """
    
    def __init__(self):
        self.standard_version = "1.0"
        self.last_updated = datetime.now()
        logger.info("Win Rate Scoring Standard initialized")
    
    def classify_opportunity(self, win_rate: float) -> TradeOpportunity:
        """Classify trade opportunity based on win rate"""
        if win_rate >= 95.0:
            return TradeOpportunity.EXCEPTIONAL
        elif win_rate >= 90.0:
            return TradeOpportunity.INFREQUENT
        elif win_rate >= 80.0:
            return TradeOpportunity.GOOD
        elif win_rate >= 70.0:
            return TradeOpportunity.MODERATE
        elif win_rate >= 60.0:
            return TradeOpportunity.WEAK
        else:
            return TradeOpportunity.AVOID
    
    def determine_trade_direction(
        self, 
        long_score: float, 
        short_score: float, 
        neutral_threshold: float = 5.0
    ) -> TradeDirection:
        """Determine optimal trade direction based on win rates"""
        score_diff = abs(long_score - short_score)
        
        if score_diff <= neutral_threshold:
            return TradeDirection.NEUTRAL
        elif long_score > short_score:
            return TradeDirection.LONG
        else:
            return TradeDirection.SHORT
    
    def create_win_rate_score(
        self,
        timeframe: TimeFrame,
        long_win_rate: float,
        short_win_rate: float,
        confidence: float,
        reasoning: str = ""
    ) -> WinRateScore:
        """Create a win rate score for a specific timeframe"""
        
        # Determine best direction
        direction = self.determine_trade_direction(long_win_rate, short_win_rate)
        
        # Select score based on direction
        if direction == TradeDirection.LONG:
            score = long_win_rate
        elif direction == TradeDirection.SHORT:
            score = short_win_rate
        else:
            score = max(long_win_rate, short_win_rate)  # Best available
        
        # Ensure score is within valid range
        score = max(0.0, min(100.0, score))
        
        # Classify opportunity
        opportunity = self.classify_opportunity(score)
        
        # Generate reasoning if not provided
        if not reasoning:
            reasoning = self._generate_reasoning(timeframe, direction, score, opportunity)
        
        return WinRateScore(
            timeframe=timeframe,
            direction=direction,
            score=score,
            win_rate_percentage=score,  # Direct correlation
            confidence=confidence,
            opportunity_level=opportunity,
            reasoning=reasoning,
            timestamp=datetime.now()
        )
    
    def create_multi_timeframe_analysis(
        self,
        symbol: str,
        short_term_data: Dict[str, float],
        medium_term_data: Dict[str, float],
        long_term_data: Dict[str, float]
    ) -> MultiTimeframeWinRate:
        """Create complete multi-timeframe win rate analysis"""
        
        # Create individual timeframe scores
        short_term = self.create_win_rate_score(
            TimeFrame.SHORT_TERM,
            short_term_data.get('long_win_rate', 50.0),
            short_term_data.get('short_win_rate', 50.0),
            short_term_data.get('confidence', 0.7),
            str(short_term_data.get('reasoning', ''))
        )
        
        medium_term = self.create_win_rate_score(
            TimeFrame.MEDIUM_TERM,
            medium_term_data.get('long_win_rate', 50.0),
            medium_term_data.get('short_win_rate', 50.0),
            medium_term_data.get('confidence', 0.7),
            str(medium_term_data.get('reasoning', ''))
        )
        
        long_term = self.create_win_rate_score(
            TimeFrame.LONG_TERM,
            long_term_data.get('long_win_rate', 50.0),
            long_term_data.get('short_win_rate', 50.0),
            long_term_data.get('confidence', 0.7),
            str(long_term_data.get('reasoning', ''))
        )
        
        # Calculate overall confidence (weighted average)
        overall_confidence = (
            short_term.confidence * 0.4 +  # 24h has higher weight
            medium_term.confidence * 0.35 +  # 7d medium weight
            long_term.confidence * 0.25   # 1m lower weight
        )
        
        # Determine dominant direction
        directions = [short_term.direction, medium_term.direction, long_term.direction]
        direction_counts = {
            TradeDirection.LONG: directions.count(TradeDirection.LONG),
            TradeDirection.SHORT: directions.count(TradeDirection.SHORT),
            TradeDirection.NEUTRAL: directions.count(TradeDirection.NEUTRAL)
        }
        dominant_direction = max(direction_counts, key=lambda x: direction_counts[x])
        
        # Find best opportunity
        scores = [short_term, medium_term, long_term]
        best_opportunity = max(scores, key=lambda x: x.score)
        
        return MultiTimeframeWinRate(
            symbol=symbol,
            short_term=short_term,
            medium_term=medium_term,
            long_term=long_term,
            overall_confidence=overall_confidence,
            dominant_direction=dominant_direction,
            best_opportunity=best_opportunity,
            timestamp=datetime.now()
        )
    
    def _generate_reasoning(
        self,
        timeframe: TimeFrame,
        direction: TradeDirection,
        score: float,
        opportunity: TradeOpportunity
    ) -> str:
        """Generate reasoning for the win rate score"""
        
        timeframe_desc = {
            TimeFrame.SHORT_TERM: "24-hour",
            TimeFrame.MEDIUM_TERM: "7-day",
            TimeFrame.LONG_TERM: "1-month"
        }
        
        direction_desc = {
            TradeDirection.LONG: "long position",
            TradeDirection.SHORT: "short position",
            TradeDirection.NEUTRAL: "neutral stance"
        }
        
        opportunity_desc = {
            TradeOpportunity.EXCEPTIONAL: "EXCEPTIONAL opportunity - All in trade recommended",
            TradeOpportunity.INFREQUENT: "INFREQUENT opportunity - High confidence trade",
            TradeOpportunity.GOOD: "GOOD opportunity - Enter trade with confidence",
            TradeOpportunity.MODERATE: "MODERATE opportunity - Consider trade carefully",
            TradeOpportunity.WEAK: "WEAK opportunity - Exercise caution",
            TradeOpportunity.AVOID: "AVOID - Win rate too low for trading"
        }
        
        return (
            f"{timeframe_desc[timeframe]} analysis suggests {direction_desc[direction]} "
            f"with {score:.1f}% win rate. {opportunity_desc[opportunity]}."
        )
    
    def validate_win_rate_data(self, data: Dict[str, Any]) -> bool:
        """Validate win rate data structure"""
        required_fields = ['long_win_rate', 'short_win_rate', 'confidence']
        
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False
            
            value = data[field]
            if not isinstance(value, (int, float)):
                logger.error(f"Invalid type for {field}: {type(value)}")
                return False
            
            if field in ['long_win_rate', 'short_win_rate']:
                if not (0 <= value <= 100):
                    logger.error(f"Win rate {field} must be 0-100, got: {value}")
                    return False
            
            if field == 'confidence':
                if not (0 <= value <= 1):
                    logger.error(f"Confidence must be 0-1, got: {value}")
                    return False
        
        return True
    
    def get_trading_recommendations(self, analysis: MultiTimeframeWinRate) -> Dict[str, Any]:
        """Get actionable trading recommendations based on win rate analysis"""
        
        recommendations = {
            'symbol': analysis.symbol,
            'overall_recommendation': 'HOLD',
            'position_size': 0.0,
            'timeframe_recommendations': {},
            'risk_assessment': 'MEDIUM',
            'confidence': analysis.overall_confidence,
            'best_opportunity': {
                'timeframe': analysis.best_opportunity.timeframe.value,
                'direction': analysis.best_opportunity.direction.value,
                'win_rate': analysis.best_opportunity.win_rate_percentage,
                'opportunity_level': analysis.best_opportunity.opportunity_level.value
            }
        }
        
        # Analyze each timeframe
        for timeframe_score in [analysis.short_term, analysis.medium_term, analysis.long_term]:
            tf_name = timeframe_score.timeframe.value
            
            # Position size based on win rate and opportunity level
            if timeframe_score.opportunity_level == TradeOpportunity.EXCEPTIONAL:
                position_size = 1.0  # All in (100%)
                risk_level = 'LOW'
            elif timeframe_score.opportunity_level == TradeOpportunity.INFREQUENT:
                position_size = 0.7  # High confidence (70%)
                risk_level = 'LOW'
            elif timeframe_score.opportunity_level == TradeOpportunity.GOOD:
                position_size = 0.4  # Good opportunity (40%)
                risk_level = 'MEDIUM'
            elif timeframe_score.opportunity_level == TradeOpportunity.MODERATE:
                position_size = 0.2  # Moderate (20%)
                risk_level = 'MEDIUM'
            elif timeframe_score.opportunity_level == TradeOpportunity.WEAK:
                position_size = 0.1  # Weak (10%)
                risk_level = 'HIGH'
            else:
                position_size = 0.0  # Avoid
                risk_level = 'VERY_HIGH'
            
            recommendations['timeframe_recommendations'][tf_name] = {
                'direction': timeframe_score.direction.value,
                'win_rate': timeframe_score.win_rate_percentage,
                'position_size': position_size,
                'risk_level': risk_level,
                'opportunity_level': timeframe_score.opportunity_level.value,
                'reasoning': timeframe_score.reasoning
            }
        
        # Overall recommendation based on best opportunity
        best = analysis.best_opportunity
        if best.opportunity_level in [TradeOpportunity.EXCEPTIONAL, TradeOpportunity.INFREQUENT]:
            recommendations['overall_recommendation'] = f"STRONG_{best.direction.value.upper()}"
            recommendations['position_size'] = 0.7 if best.opportunity_level == TradeOpportunity.INFREQUENT else 1.0
            recommendations['risk_assessment'] = 'LOW'
        elif best.opportunity_level == TradeOpportunity.GOOD:
            recommendations['overall_recommendation'] = best.direction.value.upper()
            recommendations['position_size'] = 0.4
            recommendations['risk_assessment'] = 'MEDIUM'
        elif best.opportunity_level == TradeOpportunity.MODERATE:
            recommendations['overall_recommendation'] = f"WEAK_{best.direction.value.upper()}"
            recommendations['position_size'] = 0.2
            recommendations['risk_assessment'] = 'MEDIUM'
        else:
            recommendations['overall_recommendation'] = 'HOLD'
            recommendations['position_size'] = 0.0
            recommendations['risk_assessment'] = 'HIGH'
        
        return recommendations
    
    def format_analysis_report(self, analysis: MultiTimeframeWinRate) -> str:
        """Format a human-readable analysis report"""
        
        report = f"""
🎯 WIN RATE ANALYSIS REPORT - {analysis.symbol}
{'=' * 50}

📊 MULTI-TIMEFRAME ANALYSIS:

🕐 SHORT-TERM (24h):
   Direction: {analysis.short_term.direction.value.upper()}
   Win Rate: {analysis.short_term.win_rate_percentage:.1f}%
   Opportunity: {analysis.short_term.opportunity_level.value.upper()}
   Confidence: {analysis.short_term.confidence:.2f}
   Reasoning: {analysis.short_term.reasoning}

📅 MEDIUM-TERM (7d):
   Direction: {analysis.medium_term.direction.value.upper()}
   Win Rate: {analysis.medium_term.win_rate_percentage:.1f}%
   Opportunity: {analysis.medium_term.opportunity_level.value.upper()}
   Confidence: {analysis.medium_term.confidence:.2f}
   Reasoning: {analysis.medium_term.reasoning}

📆 LONG-TERM (1m):
   Direction: {analysis.long_term.direction.value.upper()}
   Win Rate: {analysis.long_term.win_rate_percentage:.1f}%
   Opportunity: {analysis.long_term.opportunity_level.value.upper()}
   Confidence: {analysis.long_term.confidence:.2f}
   Reasoning: {analysis.long_term.reasoning}

🎯 SUMMARY:
   Dominant Direction: {analysis.dominant_direction.value.upper()}
   Best Opportunity: {analysis.best_opportunity.timeframe.value} ({analysis.best_opportunity.win_rate_percentage:.1f}%)
   Overall Confidence: {analysis.overall_confidence:.2f}

⭐ BEST TRADE SETUP:
   Timeframe: {analysis.best_opportunity.timeframe.value}
   Direction: {analysis.best_opportunity.direction.value.upper()}
   Win Rate: {analysis.best_opportunity.win_rate_percentage:.1f}%
   Level: {analysis.best_opportunity.opportunity_level.value.upper()}

Generated: {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report

# Global instance for use across all agents
win_rate_standard = WinRateScoringStandard()