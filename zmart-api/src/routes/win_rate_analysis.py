#!/usr/bin/env python3
"""
Win Rate Analysis API Routes
API endpoints for multi-timeframe win rate analysis and predictions

WIN RATE CORRELATION RULE:
- Score = Win Rate Percentage (80 points = 80% win rate)
- Multi-timeframe analysis: 24h, 7d, 1m
- 95%+ = Exceptional opportunity (All in trade)
- 90%+ = Infrequent opportunity (High confidence)
- 80%+ = Good opportunity (Enter trade)
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from ..agents.scoring.win_rate_scoring_standard import (
    win_rate_standard,
    TimeFrame,
    TradeDirection,
    TradeOpportunity
)
from ..services.integrated_scoring_system import IntegratedScoringSystem

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/win-rate", tags=["Win Rate Analysis"])

# Initialize integrated scoring system
integrated_scoring = IntegratedScoringSystem()

# Pydantic models for request/response validation
class TimeframeWinRateData(BaseModel):
    """Win rate data for a specific timeframe"""
    long_win_rate: float = Field(..., ge=0, le=100, description="Long position win rate percentage")
    short_win_rate: float = Field(..., ge=0, le=100, description="Short position win rate percentage")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in the prediction")
    reasoning: Optional[str] = Field(None, description="Reasoning for the win rate")

class MultiTimeframeWinRateRequest(BaseModel):
    """Request model for multi-timeframe win rate analysis"""
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSDT)")
    short_term_24h: TimeframeWinRateData = Field(..., description="24-hour win rate data")
    medium_term_7d: TimeframeWinRateData = Field(..., description="7-day win rate data")
    long_term_1m: TimeframeWinRateData = Field(..., description="1-month win rate data")

class AgentWinRateRequest(BaseModel):
    """Request model for agent-specific win rate analysis"""
    symbol: str = Field(..., description="Trading symbol")
    kingfisher_timeframes: Optional[Dict[str, TimeframeWinRateData]] = Field(None, description="KingFisher timeframe data")
    cryptometer_timeframes: Optional[Dict[str, TimeframeWinRateData]] = Field(None, description="Cryptometer timeframe data")
    riskmetric_timeframes: Optional[Dict[str, TimeframeWinRateData]] = Field(None, description="RiskMetric timeframe data")

@router.post("/analyze")
async def analyze_win_rate(request: MultiTimeframeWinRateRequest):
    """
    Analyze win rate across multiple timeframes
    
    This endpoint performs comprehensive win rate analysis across three timeframes:
    - 24h (short-term): Day trading opportunities
    - 7d (medium-term): Swing trading opportunities  
    - 1m (long-term): Position trading opportunities
    
    Returns detailed analysis with trading recommendations based on win rate percentages.
    """
    try:
        logger.info(f"🎯 Analyzing win rate for {request.symbol}")
        
        # Convert Pydantic models to dictionaries
        short_term_data = request.short_term_24h.dict()
        medium_term_data = request.medium_term_7d.dict()
        long_term_data = request.long_term_1m.dict()
        
        # Create multi-timeframe analysis
        analysis = win_rate_standard.create_multi_timeframe_analysis(
            symbol=request.symbol,
            short_term_data=short_term_data,
            medium_term_data=medium_term_data,
            long_term_data=long_term_data
        )
        
        # Get trading recommendations
        recommendations = win_rate_standard.get_trading_recommendations(analysis)
        
        # Format response
        response = {
            'symbol': analysis.symbol,
            'analysis': {
                'short_term_24h': {
                    'direction': analysis.short_term.direction.value,
                    'win_rate': analysis.short_term.win_rate_percentage,
                    'opportunity_level': analysis.short_term.opportunity_level.value,
                    'confidence': analysis.short_term.confidence,
                    'reasoning': analysis.short_term.reasoning
                },
                'medium_term_7d': {
                    'direction': analysis.medium_term.direction.value,
                    'win_rate': analysis.medium_term.win_rate_percentage,
                    'opportunity_level': analysis.medium_term.opportunity_level.value,
                    'confidence': analysis.medium_term.confidence,
                    'reasoning': analysis.medium_term.reasoning
                },
                'long_term_1m': {
                    'direction': analysis.long_term.direction.value,
                    'win_rate': analysis.long_term.win_rate_percentage,
                    'opportunity_level': analysis.long_term.opportunity_level.value,
                    'confidence': analysis.long_term.confidence,
                    'reasoning': analysis.long_term.reasoning
                }
            },
            'summary': {
                'dominant_direction': analysis.dominant_direction.value,
                'best_opportunity': {
                    'timeframe': analysis.best_opportunity.timeframe.value,
                    'direction': analysis.best_opportunity.direction.value,
                    'win_rate': analysis.best_opportunity.win_rate_percentage,
                    'opportunity_level': analysis.best_opportunity.opportunity_level.value
                },
                'overall_confidence': analysis.overall_confidence
            },
            'trading_recommendations': recommendations,
            'report': win_rate_standard.format_analysis_report(analysis),
            'timestamp': analysis.timestamp.isoformat()
        }
        
        logger.info(f"✅ Win rate analysis completed for {request.symbol}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error analyzing win rate for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing win rate: {str(e)}")

@router.post("/agents/analyze")
async def analyze_agent_win_rates(request: AgentWinRateRequest):
    """
    Analyze win rates from multiple agents with dynamic weighting
    
    This endpoint accepts win rate data from KingFisher, Cryptometer, and RiskMetric agents,
    applies dynamic weighting based on data quality and market conditions, and returns
    a comprehensive analysis with trading recommendations.
    """
    try:
        logger.info(f"🎯 Analyzing agent win rates for {request.symbol}")
        
        # Check if dynamic agent is available and start if needed
        if integrated_scoring.dynamic_agent is not None:
            if hasattr(integrated_scoring.dynamic_agent, 'status') and integrated_scoring.dynamic_agent.status != "running":
                await integrated_scoring.dynamic_agent.start()
        else:
            # Try to initialize the dynamic agent
            try:
                from ..agents.scoring.dynamic_scoring_agent import DynamicScoringAgent
                integrated_scoring.dynamic_agent = DynamicScoringAgent()
                if hasattr(integrated_scoring.dynamic_agent, 'start'):
                    await integrated_scoring.dynamic_agent.start()
            except ImportError:
                logger.warning("Dynamic scoring agent not available, using fallback method")
        
        # Convert timeframe data to the expected format
        kingfisher_timeframes = None
        if request.kingfisher_timeframes:
            kingfisher_timeframes = {
                tf: data.dict() for tf, data in request.kingfisher_timeframes.items()
            }
        
        cryptometer_timeframes = None
        if request.cryptometer_timeframes:
            cryptometer_timeframes = {
                tf: data.dict() for tf, data in request.cryptometer_timeframes.items()
            }
        
        riskmetric_timeframes = None
        if request.riskmetric_timeframes:
            riskmetric_timeframes = {
                tf: data.dict() for tf, data in request.riskmetric_timeframes.items()
            }
        
        # Calculate dynamic weighted win rate
        if integrated_scoring.dynamic_agent is not None and hasattr(integrated_scoring.dynamic_agent, 'calculate_multi_timeframe_win_rate'):
            result = await integrated_scoring.dynamic_agent.calculate_multi_timeframe_win_rate(
                symbol=request.symbol,
                kingfisher_timeframes=kingfisher_timeframes,
                cryptometer_timeframes=cryptometer_timeframes,
                riskmetric_timeframes=riskmetric_timeframes
            )
            
            # Format response with dynamic agent result
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
                'opportunity_classification': win_rate_standard.classify_opportunity(result.final_score).value,
                'multi_timeframe_analysis': {
                    'analysis': result.multi_timeframe_analysis.__dict__ if result.multi_timeframe_analysis else None,
                    'report': win_rate_standard.format_analysis_report(result.multi_timeframe_analysis) if result.multi_timeframe_analysis else None
                },
                'trading_recommendations': result.trading_recommendations,
                'timestamp': result.timestamp.isoformat()
            }
            final_win_rate = result.final_score
        else:
            # Fallback when dynamic agent is not available
            from datetime import datetime
            
            # Calculate simple average of all available win rates
            all_scores = []
            
            # Extract scores from timeframe data
            for tf_data in [kingfisher_timeframes, cryptometer_timeframes, riskmetric_timeframes]:
                if tf_data:
                    for timeframe, data in tf_data.items():
                        if data and 'win_rate' in data:
                            all_scores.append(data['win_rate'])
                        elif data and 'score' in data:
                            all_scores.append(data['score'])
            
            # Calculate average win rate
            if all_scores:
                final_win_rate = sum(all_scores) / len(all_scores)
            else:
                final_win_rate = 50.0
            
            # Determine signal based on win rate
            if final_win_rate >= 80:
                signal = 'STRONG_BUY'
            elif final_win_rate >= 70:
                signal = 'BUY'
            elif final_win_rate >= 30:
                signal = 'NEUTRAL'
            elif final_win_rate >= 20:
                signal = 'SELL'
            else:
                signal = 'STRONG_SELL'
            
            # Format fallback response
            response = {
                'symbol': request.symbol,
                'final_win_rate': final_win_rate,
                'signal': signal,
                'confidence': 0.5,
                'market_condition': 'normal',
                'dynamic_weights': {
                    'kingfisher': 0.30,
                    'cryptometer': 0.50,
                    'riskmetric': 0.20,
                    'reasoning': 'Using static weights (dynamic agent unavailable)',
                    'weight_confidence': 0.5
                },
                'opportunity_classification': win_rate_standard.classify_opportunity(final_win_rate).value,
                'multi_timeframe_analysis': {
                    'analysis': None,
                    'report': None
                },
                'trading_recommendations': [],
                'timestamp': datetime.now().isoformat()
            }
        
        logger.info(f"✅ Agent win rate analysis completed for {request.symbol}: {response['final_win_rate']:.1f}%")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error analyzing agent win rates for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing agent win rates: {str(e)}")

@router.get("/opportunity-levels")
async def get_opportunity_levels():
    """
    Get available opportunity levels and their descriptions
    
    Returns information about how win rates are classified into opportunity levels
    for trading decision making.
    """
    return {
        "opportunity_levels": [
            {
                "level": "exceptional",
                "win_rate_range": "95-100%",
                "description": "All in trade - Exceptional opportunity with very high win rate",
                "position_size": "100%",
                "risk_level": "LOW"
            },
            {
                "level": "infrequent", 
                "win_rate_range": "90-94%",
                "description": "High confidence trade - Infrequent opportunity with excellent win rate",
                "position_size": "70%",
                "risk_level": "LOW"
            },
            {
                "level": "good",
                "win_rate_range": "80-89%",
                "description": "Enter trade with confidence - Good opportunity with strong win rate",
                "position_size": "40%",
                "risk_level": "MEDIUM"
            },
            {
                "level": "moderate",
                "win_rate_range": "70-79%",
                "description": "Consider trade carefully - Moderate opportunity",
                "position_size": "20%",
                "risk_level": "MEDIUM"
            },
            {
                "level": "weak",
                "win_rate_range": "60-69%",
                "description": "Exercise caution - Weak opportunity",
                "position_size": "10%",
                "risk_level": "HIGH"
            },
            {
                "level": "avoid",
                "win_rate_range": "0-59%",
                "description": "Avoid trade - Win rate too low for profitable trading",
                "position_size": "0%",
                "risk_level": "VERY_HIGH"
            }
        ]
    }

@router.get("/timeframes")
async def get_timeframes():
    """
    Get available timeframes for win rate analysis
    
    Returns information about the three timeframes used for multi-timeframe analysis.
    """
    return {
        "timeframes": [
            {
                "code": "24h",
                "name": "Short-term",
                "description": "24-hour analysis for day trading opportunities",
                "typical_hold_time": "Hours to 1 day",
                "weight_in_analysis": "40%"
            },
            {
                "code": "7d", 
                "name": "Medium-term",
                "description": "7-day analysis for swing trading opportunities",
                "typical_hold_time": "Days to 1 week",
                "weight_in_analysis": "35%"
            },
            {
                "code": "1m",
                "name": "Long-term", 
                "description": "1-month analysis for position trading opportunities",
                "typical_hold_time": "Weeks to 1 month",
                "weight_in_analysis": "25%"
            }
        ]
    }

@router.get("/validate/{win_rate}")
async def validate_win_rate(
    win_rate: float,
    timeframe: str = Query("24h", description="Timeframe for validation"),
    direction: str = Query("long", description="Trading direction")
):
    """
    Validate and classify a win rate percentage
    
    Takes a win rate percentage and returns its classification, opportunity level,
    and trading recommendations.
    """
    try:
        # Validate win rate range
        if not (0 <= win_rate <= 100):
            raise HTTPException(status_code=400, detail="Win rate must be between 0 and 100")
        
        # Classify opportunity
        opportunity = win_rate_standard.classify_opportunity(win_rate)
        
        # Generate recommendations
        if opportunity == TradeOpportunity.EXCEPTIONAL:
            position_size = 1.0
            risk_level = "LOW"
            recommendation = "ALL IN - Exceptional opportunity"
        elif opportunity == TradeOpportunity.INFREQUENT:
            position_size = 0.7
            risk_level = "LOW"
            recommendation = "HIGH CONFIDENCE - Enter with large position"
        elif opportunity == TradeOpportunity.GOOD:
            position_size = 0.4
            risk_level = "MEDIUM"
            recommendation = "GOOD OPPORTUNITY - Enter trade"
        elif opportunity == TradeOpportunity.MODERATE:
            position_size = 0.2
            risk_level = "MEDIUM"
            recommendation = "MODERATE - Consider carefully"
        elif opportunity == TradeOpportunity.WEAK:
            position_size = 0.1
            risk_level = "HIGH"
            recommendation = "WEAK - Exercise caution"
        else:
            position_size = 0.0
            risk_level = "VERY_HIGH"
            recommendation = "AVOID - Win rate too low"
        
        return {
            "win_rate": win_rate,
            "timeframe": timeframe,
            "direction": direction,
            "opportunity_level": opportunity.value,
            "position_size": position_size,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "is_tradeable": win_rate >= 60.0,
            "is_high_confidence": win_rate >= 90.0,
            "is_exceptional": win_rate >= 95.0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error validating win rate {win_rate}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error validating win rate: {str(e)}")

@router.post("/compare")
async def compare_win_rates(
    win_rates: List[Dict[str, Any]] = Body(..., description="List of win rate scenarios to compare")
):
    """
    Compare multiple win rate scenarios
    
    Takes a list of win rate scenarios and returns a comparison with rankings
    and recommendations for each scenario.
    """
    try:
        logger.info(f"🔍 Comparing {len(win_rates)} win rate scenarios")
        
        comparisons = []
        
        for i, scenario in enumerate(win_rates):
            win_rate = scenario.get('win_rate', 50.0)
            symbol = scenario.get('symbol', f'SCENARIO_{i+1}')
            timeframe = scenario.get('timeframe', '24h')
            direction = scenario.get('direction', 'long')
            
            # Classify opportunity
            opportunity = win_rate_standard.classify_opportunity(win_rate)
            
            comparisons.append({
                'rank': 0,  # Will be calculated below
                'symbol': symbol,
                'win_rate': win_rate,
                'timeframe': timeframe,
                'direction': direction,
                'opportunity_level': opportunity.value,
                'score': win_rate,  # Used for ranking
                'is_tradeable': win_rate >= 60.0,
                'is_exceptional': win_rate >= 95.0
            })
        
        # Sort by win rate (descending) and assign ranks
        comparisons.sort(key=lambda x: x['score'], reverse=True)
        for i, comparison in enumerate(comparisons):
            comparison['rank'] = i + 1
        
        # Find best opportunities
        exceptional_opportunities = [c for c in comparisons if c['is_exceptional']]
        tradeable_opportunities = [c for c in comparisons if c['is_tradeable']]
        
        return {
            'total_scenarios': len(win_rates),
            'comparisons': comparisons,
            'summary': {
                'best_opportunity': comparisons[0] if comparisons else None,
                'exceptional_count': len(exceptional_opportunities),
                'tradeable_count': len(tradeable_opportunities),
                'average_win_rate': sum(c['win_rate'] for c in comparisons) / len(comparisons) if comparisons else 0
            },
            'recommendations': {
                'top_3': comparisons[:3],
                'exceptional_opportunities': exceptional_opportunities,
                'avoid_scenarios': [c for c in comparisons if not c['is_tradeable']]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error comparing win rates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error comparing win rates: {str(e)}")

@router.get("/standards")
async def get_win_rate_standards():
    """
    Get the win rate correlation standards and rules
    
    Returns the complete set of rules and standards used for win rate analysis
    and trading decision making.
    """
    return {
        "win_rate_standards": {
            "correlation_rule": "Score = Win Rate Percentage (80 points = 80% win rate)",
            "timeframes": {
                "short_term": "24h - Day trading opportunities",
                "medium_term": "7d - Swing trading opportunities", 
                "long_term": "1m - Position trading opportunities"
            },
            "opportunity_levels": {
                "exceptional": {
                    "threshold": "95%+",
                    "action": "All in trade",
                    "description": "Exceptional opportunity with very high probability"
                },
                "infrequent": {
                    "threshold": "90%+", 
                    "action": "High confidence trade",
                    "description": "Infrequent opportunity with excellent win rate"
                },
                "good": {
                    "threshold": "80%+",
                    "action": "Enter trade",
                    "description": "Good opportunity with strong win rate"
                }
            },
            "trading_rules": {
                "minimum_tradeable": "60% win rate",
                "high_confidence": "90% win rate",
                "exceptional": "95% win rate",
                "position_sizing": "Based on win rate percentage and opportunity level"
            },
            "agent_requirements": {
                "kingfisher": "Must provide liquidation-based win rate predictions",
                "cryptometer": "Must provide multi-timeframe market analysis win rates",
                "riskmetric": "Must provide risk-adjusted win rate assessments",
                "all_agents": "Must support 24h, 7d, 1m timeframe analysis"
            }
        }
    }

# Add router tags for better API documentation
router.tags = ["Win Rate Analysis", "Trading Predictions", "Multi-Timeframe Analysis"]