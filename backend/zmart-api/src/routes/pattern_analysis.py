#!/usr/bin/env python3
"""
Pattern Analysis API Routes
Advanced pattern recognition and rare event detection for trading decisions

PATTERN-BASED TRIGGER RULES:
1. Big liquidation clusters trigger KingFisher weight boost
2. RiskMetric rare bands (0-0.25, 0.75-1) trigger RiskMetric weight boost
3. Technical rare patterns (golden cross, etc.) trigger Cryptometer weight boost
4. Historical pattern matching with 80%+ win rate triggers trade entry
5. Self-learning from historical data and pattern success rates
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from ..agents.scoring.pattern_trigger_system import (
    pattern_trigger_system,
    PatternType,
    PatternRarity
)
from ..services.integrated_scoring_system import IntegratedScoringSystem

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/pattern-analysis", tags=["Pattern Analysis"])

# Initialize integrated scoring system
integrated_scoring = IntegratedScoringSystem()

# Pydantic models for request/response validation
class KingFisherPatternData(BaseModel):
    """KingFisher liquidation pattern data"""
    liquidation_cluster_strength: Optional[float] = Field(None, ge=0, le=1, description="Liquidation cluster strength (0-1)")
    cluster_position: Optional[str] = Field(None, description="Cluster position: 'above' or 'below'")
    toxic_order_flow: Optional[float] = Field(None, ge=0, le=1, description="Toxic order flow intensity (0-1)")
    flow_direction: Optional[str] = Field(None, description="Flow direction: 'buy' or 'sell'")
    historical_matches: Optional[int] = Field(0, description="Number of historical pattern matches")
    flow_matches: Optional[int] = Field(0, description="Number of flow pattern matches")

class CryptometerPatternData(BaseModel):
    """Cryptometer technical pattern data"""
    golden_cross_detected: Optional[bool] = Field(False, description="Golden cross pattern detected")
    golden_cross_confidence: Optional[float] = Field(None, ge=0, le=1, description="Golden cross confidence")
    death_cross_detected: Optional[bool] = Field(False, description="Death cross pattern detected")
    death_cross_confidence: Optional[float] = Field(None, ge=0, le=1, description="Death cross confidence")
    support_break: Optional[bool] = Field(False, description="Support level break detected")
    support_break_confidence: Optional[float] = Field(None, ge=0, le=1, description="Support break confidence")
    resistance_break: Optional[bool] = Field(False, description="Resistance level break detected")
    resistance_break_confidence: Optional[float] = Field(None, ge=0, le=1, description="Resistance break confidence")
    divergence_detected: Optional[bool] = Field(False, description="Divergence pattern detected")
    divergence_type: Optional[str] = Field(None, description="Divergence type: 'bullish' or 'bearish'")
    divergence_confidence: Optional[float] = Field(None, ge=0, le=1, description="Divergence confidence")
    golden_cross_matches: Optional[int] = Field(0, description="Historical golden cross matches")
    death_cross_matches: Optional[int] = Field(0, description="Historical death cross matches")
    support_break_matches: Optional[int] = Field(0, description="Historical support break matches")
    resistance_break_matches: Optional[int] = Field(0, description="Historical resistance break matches")
    divergence_matches: Optional[int] = Field(0, description="Historical divergence matches")

class RiskMetricPatternData(BaseModel):
    """RiskMetric rare band pattern data"""
    current_risk_level: Optional[float] = Field(None, ge=0, le=1, description="Current risk level (0-1)")
    time_spent_in_risk: Optional[float] = Field(None, ge=0, le=1, description="Time spent in current risk band (0-1)")
    risk_momentum: Optional[float] = Field(None, ge=-1, le=1, description="Risk momentum (-1 to 1)")
    risk_band_matches: Optional[int] = Field(0, description="Historical risk band matches")
    momentum_matches: Optional[int] = Field(0, description="Historical momentum matches")

class HistoricalPriceData(BaseModel):
    """Historical price data point"""
    timestamp: str = Field(..., description="Timestamp in ISO format")
    open: float = Field(..., description="Open price")
    high: float = Field(..., description="High price")
    low: float = Field(..., description="Low price")
    close: float = Field(..., description="Close price")
    volume: Optional[float] = Field(None, description="Volume")

class PatternAnalysisRequest(BaseModel):
    """Request model for comprehensive pattern analysis"""
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSDT)")
    current_price: Optional[float] = Field(None, description="Current market price")
    kingfisher_data: Optional[KingFisherPatternData] = Field(None, description="KingFisher pattern data")
    cryptometer_data: Optional[CryptometerPatternData] = Field(None, description="Cryptometer pattern data")
    riskmetric_data: Optional[RiskMetricPatternData] = Field(None, description="RiskMetric pattern data")
    historical_prices: Optional[List[HistoricalPriceData]] = Field(None, description="Historical price data")

@router.post("/analyze")
async def analyze_patterns(request: PatternAnalysisRequest):
    """
    Perform comprehensive pattern analysis with rare event detection
    
    This endpoint analyzes patterns from all three agents and determines:
    1. When rare events occur that should trigger weight adjustments
    2. Historical pattern matching for win rate prediction
    3. Self-learning from pattern success rates
    4. Trade entry triggers based on pattern confluence
    
    PATTERN TRIGGERS:
    - Big liquidation clusters → KingFisher weight boost
    - Rare risk bands (0-0.25, 0.75-1) → RiskMetric weight boost
    - Technical rare patterns → Cryptometer weight boost
    - 80%+ win rate patterns → Trade entry trigger
    """
    try:
        logger.info(f"🎯 Starting pattern analysis for {request.symbol}")
        
        # Convert Pydantic models to dictionaries
        kingfisher_data = request.kingfisher_data.dict() if request.kingfisher_data else None
        cryptometer_data = request.cryptometer_data.dict() if request.cryptometer_data else None
        riskmetric_data = request.riskmetric_data.dict() if request.riskmetric_data else None
        
        # Convert historical prices
        historical_prices = None
        if request.historical_prices:
            historical_prices = [price.dict() for price in request.historical_prices]
        
        # Perform pattern analysis
        pattern_analysis = await pattern_trigger_system.analyze_patterns(
            symbol=request.symbol,
            kingfisher_data=kingfisher_data,
            cryptometer_data=cryptometer_data,
            riskmetric_data=riskmetric_data,
            current_price=request.current_price,
            historical_prices=historical_prices
        )
        
        # Format response
        response = {
            'symbol': pattern_analysis.symbol,
            'pattern_analysis': {
                'kingfisher_patterns': [
                    {
                        'pattern_type': p.pattern_type.value,
                        'rarity': p.rarity.value,
                        'confidence': p.confidence,
                        'win_rate_prediction': p.win_rate_prediction,
                        'direction': p.direction,
                        'timeframe': p.timeframe,
                        'weight_multiplier': p.weight_multiplier,
                        'reasoning': p.reasoning,
                        'historical_matches': p.historical_matches,
                        'success_rate': p.success_rate
                    } for p in pattern_analysis.kingfisher_patterns
                ],
                'cryptometer_patterns': [
                    {
                        'pattern_type': p.pattern_type.value,
                        'rarity': p.rarity.value,
                        'confidence': p.confidence,
                        'win_rate_prediction': p.win_rate_prediction,
                        'direction': p.direction,
                        'timeframe': p.timeframe,
                        'weight_multiplier': p.weight_multiplier,
                        'reasoning': p.reasoning,
                        'historical_matches': p.historical_matches,
                        'success_rate': p.success_rate
                    } for p in pattern_analysis.cryptometer_patterns
                ],
                'riskmetric_patterns': [
                    {
                        'pattern_type': p.pattern_type.value,
                        'rarity': p.rarity.value,
                        'confidence': p.confidence,
                        'win_rate_prediction': p.win_rate_prediction,
                        'direction': p.direction,
                        'timeframe': p.timeframe,
                        'weight_multiplier': p.weight_multiplier,
                        'reasoning': p.reasoning,
                        'historical_matches': p.historical_matches,
                        'success_rate': p.success_rate
                    } for p in pattern_analysis.riskmetric_patterns
                ],
                'combined_signals': [
                    {
                        'pattern_type': p.pattern_type.value,
                        'rarity': p.rarity.value,
                        'confidence': p.confidence,
                        'win_rate_prediction': p.win_rate_prediction,
                        'direction': p.direction,
                        'timeframe': p.timeframe,
                        'weight_multiplier': p.weight_multiplier,
                        'reasoning': p.reasoning,
                        'historical_matches': p.historical_matches,
                        'success_rate': p.success_rate
                    } for p in pattern_analysis.combined_signals
                ]
            },
            'weight_adjustments': pattern_analysis.weight_adjustments,
            'trigger_analysis': {
                'overall_trigger': pattern_analysis.overall_trigger,
                'overall_win_rate': pattern_analysis.overall_win_rate,
                'trigger_reason': 'Pattern confluence and win rate threshold met' if pattern_analysis.overall_trigger else 'Insufficient pattern strength or win rate below threshold'
            },
            'recommendations': {
                'should_trade': pattern_analysis.overall_trigger,
                'recommended_direction': _get_dominant_direction(pattern_analysis),
                'confidence_level': _calculate_overall_confidence(pattern_analysis),
                'risk_level': _assess_risk_level(pattern_analysis)
            },
            'timestamp': pattern_analysis.timestamp.isoformat()
        }
        
        logger.info(f"✅ Pattern analysis completed for {request.symbol}: Trigger={pattern_analysis.overall_trigger}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error analyzing patterns for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing patterns: {str(e)}")

@router.post("/scoring/pattern-based")
async def calculate_pattern_based_score(request: PatternAnalysisRequest):
    """
    Calculate win rate score using pattern-based triggers
    
    This endpoint combines pattern analysis with dynamic scoring to produce
    a final win rate score that accounts for rare event detection and
    historical pattern matching.
    """
    try:
        logger.info(f"🎯 Starting pattern-based scoring for {request.symbol}")
        
        # Start the dynamic agent if needed
        if integrated_scoring.dynamic_agent.status != "running":
            await integrated_scoring.dynamic_agent.start()
        
        # Convert data
        kingfisher_data = request.kingfisher_data.dict() if request.kingfisher_data else None
        cryptometer_data = request.cryptometer_data.dict() if request.cryptometer_data else None
        riskmetric_data = request.riskmetric_data.dict() if request.riskmetric_data else None
        historical_prices = [p.dict() for p in request.historical_prices] if request.historical_prices else None
        
        # Calculate pattern-based score
        result = await integrated_scoring.dynamic_agent.calculate_pattern_based_score(
            symbol=request.symbol,
            kingfisher_data=kingfisher_data,
            cryptometer_data=cryptometer_data,
            riskmetric_data=riskmetric_data,
            current_price=request.current_price,
            historical_prices=historical_prices
        )
        
        # Format response
        response = {
            'symbol': result.symbol,
            'final_win_rate': result.final_score,
            'signal': result.signal,
            'confidence': result.overall_confidence,
            'market_condition': result.market_condition.value,
            'dynamic_weights': {
                'kingfisher': result.dynamic_weights.kingfisher_weight,
                'cryptometer': result.dynamic_weights.cryptometer_weight,
                'riskmetric': result.dynamic_weights.riskmetric_weight,
                'reasoning': result.dynamic_weights.reasoning,
                'weight_confidence': result.dynamic_weights.confidence
            },
            'individual_scores': {
                'kingfisher': result.kingfisher_data.score if result.kingfisher_data else None,
                'cryptometer': result.cryptometer_data.score if result.cryptometer_data else None,
                'riskmetric': result.riskmetric_data.score if result.riskmetric_data else None
            },
            'opportunity_classification': _classify_opportunity(result.final_score),
            'trading_recommendations': result.trading_recommendations,
            'timestamp': result.timestamp.isoformat()
        }
        
        logger.info(f"✅ Pattern-based scoring completed for {request.symbol}: {result.final_score:.1f}% win rate")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in pattern-based scoring for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in pattern-based scoring: {str(e)}")

@router.get("/patterns/types")
async def get_pattern_types():
    """
    Get available pattern types and their descriptions
    
    Returns information about all pattern types that can be detected
    by the pattern analysis system.
    """
    return {
        "pattern_types": [
            {
                "type": "liquidation_cluster",
                "agent": "kingfisher",
                "description": "Large liquidation clusters indicating potential price movement",
                "trigger_condition": "Cluster strength >= 0.7",
                "typical_win_rate": "75-85%",
                "timeframe": "24h"
            },
            {
                "type": "golden_cross",
                "agent": "cryptometer", 
                "description": "50-day MA crosses above 200-day MA (bullish signal)",
                "trigger_condition": "Confirmed cross with high confidence",
                "typical_win_rate": "80-90%",
                "timeframe": "7d-1m"
            },
            {
                "type": "death_cross",
                "agent": "cryptometer",
                "description": "50-day MA crosses below 200-day MA (bearish signal)",
                "trigger_condition": "Confirmed cross with high confidence",
                "typical_win_rate": "75-85%",
                "timeframe": "7d-1m"
            },
            {
                "type": "risk_band_rare",
                "agent": "riskmetric",
                "description": "Asset in rare risk bands (0-0.25 or 0.75-1.0)",
                "trigger_condition": "Risk level in rare zone with minimal time spent",
                "typical_win_rate": "85-95%",
                "timeframe": "7d-1m"
            },
            {
                "type": "support_break",
                "agent": "cryptometer",
                "description": "Price breaks below major support level",
                "trigger_condition": "Confirmed break with volume",
                "typical_win_rate": "65-75%",
                "timeframe": "24h-7d"
            },
            {
                "type": "resistance_break",
                "agent": "cryptometer",
                "description": "Price breaks above major resistance level",
                "trigger_condition": "Confirmed break with volume",
                "typical_win_rate": "70-80%",
                "timeframe": "24h-7d"
            },
            {
                "type": "divergence",
                "agent": "cryptometer",
                "description": "Price and indicator divergence (reversal signal)",
                "trigger_condition": "Clear divergence pattern confirmed",
                "typical_win_rate": "80-90%",
                "timeframe": "1m"
            },
            {
                "type": "volume_spike",
                "agent": "kingfisher",
                "description": "Unusual volume spike indicating institutional activity",
                "trigger_condition": "Volume spike >= 70% above average",
                "typical_win_rate": "60-70%",
                "timeframe": "24h"
            }
        ]
    }

@router.get("/patterns/rarity-levels")
async def get_rarity_levels():
    """
    Get pattern rarity levels and their weight multipliers
    
    Returns information about how pattern rarity affects weight adjustments
    and trading decisions.
    """
    return {
        "rarity_levels": [
            {
                "level": "common",
                "weight_multiplier": 1.0,
                "description": "Frequently occurring patterns with standard reliability",
                "frequency": "Daily to weekly",
                "impact": "Minimal weight adjustment"
            },
            {
                "level": "uncommon",
                "weight_multiplier": 1.3,
                "description": "Moderately rare patterns with increased reliability",
                "frequency": "Weekly to bi-weekly",
                "impact": "Moderate weight boost (30%)"
            },
            {
                "level": "rare",
                "weight_multiplier": 1.7,
                "description": "Infrequent patterns with high reliability",
                "frequency": "Monthly or less",
                "impact": "Significant weight boost (70%)"
            },
            {
                "level": "exceptional",
                "weight_multiplier": 2.5,
                "description": "Very rare patterns with exceptional reliability",
                "frequency": "Quarterly or less",
                "impact": "Maximum weight boost (150%)"
            }
        ]
    }

@router.get("/statistics")
async def get_pattern_statistics():
    """
    Get pattern detection statistics and success rates
    
    Returns statistics about pattern detection performance and
    historical success rates for self-learning validation.
    """
    try:
        stats = pattern_trigger_system.get_pattern_statistics()
        return {
            'pattern_statistics': stats,
            'system_health': {
                'total_analyses_performed': stats.get('total_analyses', 0),
                'learning_data_points': len(stats.get('success_rates', {})),
                'trigger_threshold': stats.get('trigger_threshold', 80.0),
                'system_status': 'operational'
            }
        }
    except Exception as e:
        logger.error(f"❌ Error getting pattern statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

@router.post("/test/liquidation-cluster")
async def test_liquidation_cluster(
    symbol: str = Body(..., description="Trading symbol"),
    cluster_strength: float = Body(..., ge=0, le=1, description="Cluster strength (0-1)"),
    position: str = Body("below", description="Cluster position: 'above' or 'below'")
):
    """
    Test liquidation cluster pattern detection
    
    This endpoint allows testing of the KingFisher liquidation cluster
    pattern detection with various parameters.
    """
    try:
        test_data = {
            'liquidation_cluster_strength': cluster_strength,
            'cluster_position': position,
            'historical_matches': 10
        }
        
        analysis = await pattern_trigger_system.analyze_patterns(
            symbol=symbol,
            kingfisher_data=test_data
        )
        
        return {
            'test_result': 'liquidation_cluster',
            'symbol': symbol,
            'input_parameters': {
                'cluster_strength': cluster_strength,
                'position': position
            },
            'detected_patterns': len(analysis.kingfisher_patterns),
            'patterns': [
                {
                    'type': p.pattern_type.value,
                    'rarity': p.rarity.value,
                    'win_rate': p.win_rate_prediction,
                    'direction': p.direction,
                    'weight_multiplier': p.weight_multiplier
                } for p in analysis.kingfisher_patterns
            ],
            'weight_adjustment': analysis.weight_adjustments.get('kingfisher', 1.0),
            'trigger_activated': analysis.overall_trigger
        }
        
    except Exception as e:
        logger.error(f"❌ Error testing liquidation cluster: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error testing pattern: {str(e)}")

@router.post("/test/risk-band")
async def test_risk_band(
    symbol: str = Body(..., description="Trading symbol"),
    risk_level: float = Body(..., ge=0, le=1, description="Risk level (0-1)"),
    time_in_risk: float = Body(0.1, ge=0, le=1, description="Time spent in risk band (0-1)")
):
    """
    Test risk band rare pattern detection
    
    This endpoint allows testing of the RiskMetric rare risk band
    pattern detection with various parameters.
    """
    try:
        test_data = {
            'current_risk_level': risk_level,
            'time_spent_in_risk': time_in_risk,
            'risk_band_matches': 5
        }
        
        analysis = await pattern_trigger_system.analyze_patterns(
            symbol=symbol,
            riskmetric_data=test_data
        )
        
        return {
            'test_result': 'risk_band_rare',
            'symbol': symbol,
            'input_parameters': {
                'risk_level': risk_level,
                'time_in_risk': time_in_risk
            },
            'detected_patterns': len(analysis.riskmetric_patterns),
            'patterns': [
                {
                    'type': p.pattern_type.value,
                    'rarity': p.rarity.value,
                    'win_rate': p.win_rate_prediction,
                    'direction': p.direction,
                    'weight_multiplier': p.weight_multiplier
                } for p in analysis.riskmetric_patterns
            ],
            'weight_adjustment': analysis.weight_adjustments.get('riskmetric', 1.0),
            'trigger_activated': analysis.overall_trigger
        }
        
    except Exception as e:
        logger.error(f"❌ Error testing risk band: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error testing pattern: {str(e)}")

# Helper functions
def _get_dominant_direction(pattern_analysis) -> str:
    """Get dominant direction from pattern analysis"""
    all_patterns = (
        pattern_analysis.kingfisher_patterns + 
        pattern_analysis.cryptometer_patterns + 
        pattern_analysis.riskmetric_patterns +
        pattern_analysis.combined_signals
    )
    
    if not all_patterns:
        return "neutral"
    
    long_weight = sum(p.confidence for p in all_patterns if p.direction == "long")
    short_weight = sum(p.confidence for p in all_patterns if p.direction == "short")
    
    if abs(long_weight - short_weight) < 0.1:
        return "neutral"
    
    return "long" if long_weight > short_weight else "short"

def _calculate_overall_confidence(pattern_analysis) -> float:
    """Calculate overall confidence from pattern analysis"""
    all_patterns = (
        pattern_analysis.kingfisher_patterns + 
        pattern_analysis.cryptometer_patterns + 
        pattern_analysis.riskmetric_patterns +
        pattern_analysis.combined_signals
    )
    
    if not all_patterns:
        return 0.5
    
    return sum(p.confidence for p in all_patterns) / len(all_patterns)

def _assess_risk_level(pattern_analysis) -> str:
    """Assess risk level based on pattern analysis"""
    if pattern_analysis.overall_win_rate >= 90.0:
        return "LOW"
    elif pattern_analysis.overall_win_rate >= 80.0:
        return "MEDIUM"
    elif pattern_analysis.overall_win_rate >= 70.0:
        return "HIGH"
    else:
        return "VERY_HIGH"

def _classify_opportunity(win_rate: float) -> str:
    """Classify opportunity based on win rate"""
    if win_rate >= 95.0:
        return "exceptional"
    elif win_rate >= 90.0:
        return "infrequent"
    elif win_rate >= 80.0:
        return "good"
    elif win_rate >= 70.0:
        return "moderate"
    elif win_rate >= 60.0:
        return "weak"
    else:
        return "avoid"

# Add router tags for better API documentation
router.tags = ["Pattern Analysis", "Rare Event Detection", "Historical Pattern Matching"]