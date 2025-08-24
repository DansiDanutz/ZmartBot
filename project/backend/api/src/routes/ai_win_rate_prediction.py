#!/usr/bin/env python3
"""
AI-Powered Win Rate Prediction API Routes
Uses smart models (ChatGPT, DeepSeek, etc.) to predict win rates from agent data

Each agent uses AI to analyze their data and predict win rates with detailed reports:
- KingFisher: AI analyzes liquidation clusters for win rate prediction
- Cryptometer: AI analyzes 17 endpoints for win rate prediction  
- RiskMetric: AI analyzes Cowen methodology for win rate prediction
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from ..agents.scoring.ai_win_rate_predictor import (
    ai_predictor,
    AIModel,
    AIWinRatePrediction,
    MultiTimeframeAIPrediction
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai-prediction", tags=["AI Win Rate Prediction"])

# Pydantic models for request/response validation
class KingFisherData(BaseModel):
    """KingFisher liquidation data for AI analysis"""
    liquidation_cluster_strength: Optional[float] = Field(None, ge=0, le=1, description="Liquidation cluster strength (0-1)")
    cluster_position: Optional[str] = Field(None, description="Cluster position: 'above', 'below', or 'neutral'")
    toxic_order_flow: Optional[float] = Field(None, ge=0, le=1, description="Toxic order flow intensity (0-1)")
    flow_direction: Optional[str] = Field(None, description="Flow direction: 'buy', 'sell', or 'neutral'")
    liquidation_map_available: Optional[bool] = Field(False, description="Whether liquidation map is available")
    toxic_flow_available: Optional[bool] = Field(False, description="Whether toxic flow data is available")
    short_long_ratios: Optional[Dict[str, float]] = Field({}, description="Short/Long liquidation ratios")
    historical_matches: Optional[int] = Field(0, description="Number of historical pattern matches")
    market_volatility: Optional[float] = Field(0.0, ge=0, le=1, description="Market volatility level (0-1)")

class CryptometerData(BaseModel):
    """Cryptometer 17-endpoint data for AI analysis"""
    endpoints_analyzed: Optional[int] = Field(17, description="Number of endpoints analyzed")
    technical_indicators: Optional[Dict[str, Any]] = Field({}, description="Technical indicators data")
    market_sentiment: Optional[Dict[str, Any]] = Field({}, description="Market sentiment analysis")
    volume_analysis: Optional[Dict[str, Any]] = Field({}, description="Volume analysis data")
    momentum_indicators: Optional[Dict[str, Any]] = Field({}, description="Momentum indicators data")
    trend_analysis: Optional[Dict[str, Any]] = Field({}, description="Trend analysis data")
    support_resistance: Optional[Dict[str, Any]] = Field({}, description="Support/resistance levels")
    volatility_metrics: Optional[Dict[str, Any]] = Field({}, description="Volatility metrics")
    correlation_data: Optional[Dict[str, Any]] = Field({}, description="Correlation analysis data")
    market_structure: Optional[Dict[str, Any]] = Field({}, description="Market structure analysis")

class RiskMetricData(BaseModel):
    """RiskMetric Cowen methodology data for AI analysis"""
    current_risk_level: Optional[float] = Field(None, ge=0, le=1, description="Current risk level (0-1)")
    risk_band: Optional[str] = Field(None, description="Risk band: 'low', 'medium', 'high'")
    market_cycle: Optional[str] = Field(None, description="Market cycle position")
    time_spent_in_risk: Optional[float] = Field(None, ge=0, le=1, description="Time spent in current risk band (0-1)")
    risk_momentum: Optional[float] = Field(None, ge=-1, le=1, description="Risk momentum (-1 to 1)")
    historical_risk_data: Optional[Dict[str, Any]] = Field({}, description="Historical risk data")
    cowen_metrics: Optional[Dict[str, Any]] = Field({}, description="Benjamin Cowen methodology metrics")
    volatility_analysis: Optional[Dict[str, Any]] = Field({}, description="Volatility analysis")
    correlation_analysis: Optional[Dict[str, Any]] = Field({}, description="Correlation analysis")
    risk_band_matches: Optional[int] = Field(0, description="Number of historical risk band matches")

class AIWinRateRequest(BaseModel):
    """Request model for AI win rate prediction"""
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSDT)")
    agent_type: str = Field(..., description="Agent type: 'kingfisher', 'cryptometer', or 'riskmetric'")
    ai_model: Optional[str] = Field("gpt-4", description="AI model to use: 'gpt-4', 'gpt-3.5-turbo', 'deepseek-chat', 'claude-3'")
    kingfisher_data: Optional[KingFisherData] = Field(None, description="KingFisher data for analysis")
    cryptometer_data: Optional[CryptometerData] = Field(None, description="Cryptometer data for analysis")
    riskmetric_data: Optional[RiskMetricData] = Field(None, description="RiskMetric data for analysis")

class MultiTimeframeAIRequest(BaseModel):
    """Request model for multi-timeframe AI prediction"""
    symbol: str = Field(..., description="Trading symbol")
    agent_type: str = Field(..., description="Agent type")
    ai_model: Optional[str] = Field("gpt-4", description="AI model to use")
    agent_data: Dict[str, Any] = Field(..., description="Agent data for analysis")

@router.post("/predict")
async def predict_ai_win_rate(request: AIWinRateRequest):
    """
    Use AI to predict win rate from agent data
    
    This endpoint uses smart models (ChatGPT, DeepSeek, etc.) to analyze agent data
    and predict win rates with detailed reasoning and confidence levels.
    
    Supported AI Models:
    - OpenAI GPT-4: Most advanced analysis
    - OpenAI GPT-3.5: Fast analysis
    - DeepSeek: Alternative AI model
    - Anthropic Claude: High-quality reasoning
    """
    try:
        logger.info(f"🤖 Starting AI win rate prediction for {request.symbol} ({request.agent_type})")
        
        # Convert AI model string to enum
        ai_model = None
        if request.ai_model == "gpt-4":
            ai_model = AIModel.OPENAI_GPT4
        elif request.ai_model == "gpt-3.5-turbo":
            ai_model = AIModel.OPENAI_GPT35
        elif request.ai_model == "deepseek-chat":
            ai_model = AIModel.DEEPSEEK
        elif request.ai_model == "claude-3":
            ai_model = AIModel.ANTHROPIC_CLAUDE
        else:
            ai_model = AIModel.OPENAI_GPT4  # Default
        
        # Convert Pydantic models to dictionaries
        kingfisher_data = request.kingfisher_data.dict() if request.kingfisher_data else None
        cryptometer_data = request.cryptometer_data.dict() if request.cryptometer_data else None
        riskmetric_data = request.riskmetric_data.dict() if request.riskmetric_data else None
        
        # Predict based on agent type
        if request.agent_type == "kingfisher":
            if not kingfisher_data:
                raise HTTPException(status_code=400, detail="KingFisher data is required for KingFisher analysis")
            prediction = await ai_predictor.predict_kingfisher_win_rate(
                request.symbol, kingfisher_data, ai_model
            )
        elif request.agent_type == "cryptometer":
            if not cryptometer_data:
                raise HTTPException(status_code=400, detail="Cryptometer data is required for Cryptometer analysis")
            prediction = await ai_predictor.predict_cryptometer_win_rate(
                request.symbol, cryptometer_data, ai_model
            )
        elif request.agent_type == "riskmetric":
            if not riskmetric_data:
                raise HTTPException(status_code=400, detail="RiskMetric data is required for RiskMetric analysis")
            prediction = await ai_predictor.predict_riskmetric_win_rate(
                request.symbol, riskmetric_data, ai_model
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {request.agent_type}")
        
        # Format response
        response = {
            'symbol': prediction.symbol,
            'agent_type': prediction.agent_type,
            'ai_model': prediction.ai_model,
            'win_rate_prediction': prediction.win_rate_prediction,
            'confidence': prediction.confidence,
            'direction': prediction.direction,
            'timeframe': prediction.timeframe,
            'reasoning': prediction.reasoning,
            'data_summary': prediction.data_summary,
            'ai_analysis': prediction.ai_analysis,
            'timestamp': prediction.timestamp.isoformat(),
            'opportunity_level': _classify_opportunity(prediction.win_rate_prediction),
            'trading_recommendation': _generate_trading_recommendation(prediction)
        }
        
        logger.info(f"✅ AI prediction completed for {request.symbol}: {prediction.win_rate_prediction:.1f}% win rate")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in AI win rate prediction for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in AI prediction: {str(e)}")

@router.post("/predict/multi-timeframe")
async def predict_multi_timeframe_ai_win_rate(request: MultiTimeframeAIRequest):
    """
    Use AI to predict win rates across multiple timeframes
    
    This endpoint analyzes the same agent data across 24h, 7d, and 1m timeframes
    to provide comprehensive win rate predictions with detailed reasoning.
    """
    try:
        logger.info(f"🤖 Starting multi-timeframe AI prediction for {request.symbol} ({request.agent_type})")
        
        # Convert AI model string to enum
        ai_model = None
        if request.ai_model == "gpt-4":
            ai_model = AIModel.OPENAI_GPT4
        elif request.ai_model == "gpt-3.5-turbo":
            ai_model = AIModel.OPENAI_GPT35
        elif request.ai_model == "deepseek-chat":
            ai_model = AIModel.DEEPSEEK
        elif request.ai_model == "claude-3":
            ai_model = AIModel.ANTHROPIC_CLAUDE
        else:
            ai_model = AIModel.OPENAI_GPT4  # Default
        
        # Predict multi-timeframe
        prediction = await ai_predictor.predict_multi_timeframe_win_rate(
            request.symbol, request.agent_type, request.agent_data, ai_model
        )
        
        # Format response
        response = {
            'symbol': prediction.symbol,
            'agent_type': prediction.agent_type,
            'overall_confidence': prediction.overall_confidence,
            'best_opportunity': {
                'timeframe': prediction.best_opportunity.timeframe,
                'win_rate': prediction.best_opportunity.win_rate_prediction,
                'direction': prediction.best_opportunity.direction,
                'confidence': prediction.best_opportunity.confidence,
                'reasoning': prediction.best_opportunity.reasoning
            },
            'timeframes': {
                'short_term_24h': {
                    'win_rate': prediction.short_term_24h.win_rate_prediction,
                    'direction': prediction.short_term_24h.direction,
                    'confidence': prediction.short_term_24h.confidence,
                    'reasoning': prediction.short_term_24h.reasoning
                },
                'medium_term_7d': {
                    'win_rate': prediction.medium_term_7d.win_rate_prediction,
                    'direction': prediction.medium_term_7d.direction,
                    'confidence': prediction.medium_term_7d.confidence,
                    'reasoning': prediction.medium_term_7d.reasoning
                },
                'long_term_1m': {
                    'win_rate': prediction.long_term_1m.win_rate_prediction,
                    'direction': prediction.long_term_1m.direction,
                    'confidence': prediction.long_term_1m.confidence,
                    'reasoning': prediction.long_term_1m.reasoning
                }
            },
            'ai_model': prediction.short_term_24h.ai_model,
            'timestamp': prediction.timestamp.isoformat()
        }
        
        logger.info(f"✅ Multi-timeframe AI prediction completed for {request.symbol}: Best {prediction.best_opportunity.timeframe} at {prediction.best_opportunity.win_rate_prediction:.1f}%")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in multi-timeframe AI prediction for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in multi-timeframe AI prediction: {str(e)}")

@router.get("/models")
async def get_available_ai_models():
    """
    Get available AI models for win rate prediction
    
    Returns information about all supported AI models and their capabilities
    for win rate prediction analysis.
    """
    return {
        "available_models": [
            {
                "model": "gpt-4",
                "provider": "OpenAI",
                "description": "Most advanced AI model for comprehensive analysis",
                "best_for": "Complex liquidation and technical analysis",
                "response_time": "2-5 seconds",
                "max_tokens": 2000
            },
            {
                "model": "gpt-3.5-turbo",
                "provider": "OpenAI",
                "description": "Fast and efficient AI model for quick analysis",
                "best_for": "Rapid win rate predictions",
                "response_time": "1-3 seconds",
                "max_tokens": 2000
            },
            {
                "model": "deepseek-chat",
                "provider": "DeepSeek",
                "description": "Alternative AI model with strong analytical capabilities",
                "best_for": "Technical analysis and pattern recognition",
                "response_time": "2-4 seconds",
                "max_tokens": 2000
            },
            {
                "model": "claude-3",
                "provider": "Anthropic",
                "description": "High-quality reasoning and detailed analysis",
                "best_for": "Complex risk analysis and detailed explanations",
                "response_time": "3-6 seconds",
                "max_tokens": 2000
            }
        ],
        "default_model": "gpt-4",
        "recommendations": {
            "kingfisher": "gpt-4 or claude-3 for liquidation analysis",
            "cryptometer": "gpt-4 or deepseek-chat for technical analysis",
            "riskmetric": "claude-3 or gpt-4 for risk analysis"
        }
    }

@router.get("/test/kingfisher")
async def test_kingfisher_ai_prediction(
    symbol: str = Query("BTCUSDT", description="Trading symbol"),
    cluster_strength: float = Query(0.8, ge=0, le=1, description="Liquidation cluster strength"),
    position: str = Query("below", description="Cluster position"),
    ai_model: str = Query("gpt-4", description="AI model to use")
):
    """
    Test KingFisher AI prediction with sample data
    
    This endpoint allows testing of the KingFisher AI prediction
    with various liquidation cluster parameters.
    """
    try:
        logger.info(f"🧪 Testing KingFisher AI prediction for {symbol}")
        
        # Create test data
        test_data = {
            "liquidation_cluster_strength": cluster_strength,
            "cluster_position": position,
            "toxic_order_flow": 0.7,
            "flow_direction": "sell",
            "liquidation_map_available": True,
            "toxic_flow_available": True,
            "short_long_ratios": {"short": 0.6, "long": 0.4},
            "historical_matches": 15,
            "market_volatility": 0.8
        }
        
        # Convert AI model string to enum
        model = AIModel.OPENAI_GPT4 if ai_model == "gpt-4" else AIModel.OPENAI_GPT35
        
        # Get AI prediction
        prediction = await ai_predictor.predict_kingfisher_win_rate(symbol, test_data, model)
        
        return {
            'test_type': 'kingfisher_ai_prediction',
            'symbol': symbol,
            'input_parameters': {
                'cluster_strength': cluster_strength,
                'position': position,
                'ai_model': ai_model
            },
            'prediction': {
                'win_rate': prediction.win_rate_prediction,
                'confidence': prediction.confidence,
                'direction': prediction.direction,
                'timeframe': prediction.timeframe,
                'reasoning': prediction.reasoning,
                'ai_model': prediction.ai_model
            },
            'opportunity_level': _classify_opportunity(prediction.win_rate_prediction),
            'trading_recommendation': _generate_trading_recommendation(prediction)
        }
        
    except Exception as e:
        logger.error(f"❌ Error testing KingFisher AI prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error testing KingFisher AI: {str(e)}")

@router.get("/test/cryptometer")
async def test_cryptometer_ai_prediction(
    symbol: str = Query("ETHUSDT", description="Trading symbol"),
    ai_model: str = Query("gpt-4", description="AI model to use")
):
    """
    Test Cryptometer AI prediction with sample data
    
    This endpoint allows testing of the Cryptometer AI prediction
    with sample 17-endpoint technical analysis data.
    """
    try:
        logger.info(f"🧪 Testing Cryptometer AI prediction for {symbol}")
        
        # Create test data
        test_data = {
            "endpoints_analyzed": 17,
            "technical_indicators": {
                "rsi": 65.5,
                "macd": {"signal": "bullish", "strength": 0.7},
                "bollinger_bands": {"position": "upper", "squeeze": False},
                "moving_averages": {"golden_cross": True, "death_cross": False}
            },
            "market_sentiment": {
                "overall_sentiment": "bullish",
                "confidence": 0.8,
                "social_volume": "high"
            },
            "volume_analysis": {
                "volume_trend": "increasing",
                "volume_ratio": 1.2,
                "unusual_volume": True
            },
            "momentum_indicators": {
                "stochastic": {"k": 75, "d": 70},
                "cci": 120,
                "williams_r": -25
            },
            "trend_analysis": {
                "primary_trend": "bullish",
                "secondary_trend": "sideways",
                "trend_strength": 0.8
            },
            "support_resistance": {
                "support_levels": [42000, 41500, 41000],
                "resistance_levels": [43000, 43500, 44000],
                "current_position": "near_resistance"
            },
            "volatility_metrics": {
                "atr": 2500,
                "volatility_ratio": 1.1,
                "volatility_regime": "high"
            },
            "correlation_data": {
                "btc_correlation": 0.85,
                "market_correlation": 0.72,
                "sector_correlation": 0.68
            },
            "market_structure": {
                "market_structure": "bullish",
                "higher_highs": True,
                "higher_lows": True,
                "breakout_potential": "high"
            }
        }
        
        # Convert AI model string to enum
        model = AIModel.OPENAI_GPT4 if ai_model == "gpt-4" else AIModel.OPENAI_GPT35
        
        # Get AI prediction
        prediction = await ai_predictor.predict_cryptometer_win_rate(symbol, test_data, model)
        
        return {
            'test_type': 'cryptometer_ai_prediction',
            'symbol': symbol,
            'input_parameters': {
                'endpoints_analyzed': 17,
                'ai_model': ai_model
            },
            'prediction': {
                'win_rate': prediction.win_rate_prediction,
                'confidence': prediction.confidence,
                'direction': prediction.direction,
                'timeframe': prediction.timeframe,
                'reasoning': prediction.reasoning,
                'ai_model': prediction.ai_model
            },
            'opportunity_level': _classify_opportunity(prediction.win_rate_prediction),
            'trading_recommendation': _generate_trading_recommendation(prediction)
        }
        
    except Exception as e:
        logger.error(f"❌ Error testing Cryptometer AI prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error testing Cryptometer AI: {str(e)}")

@router.get("/test/riskmetric")
async def test_riskmetric_ai_prediction(
    symbol: str = Query("ADAUSDT", description="Trading symbol"),
    risk_level: float = Query(0.15, ge=0, le=1, description="Current risk level"),
    time_in_risk: float = Query(0.05, ge=0, le=1, description="Time spent in risk band"),
    ai_model: str = Query("claude-3", description="AI model to use")
):
    """
    Test RiskMetric AI prediction with sample data
    
    This endpoint allows testing of the RiskMetric AI prediction
    with sample Cowen methodology risk data.
    """
    try:
        logger.info(f"🧪 Testing RiskMetric AI prediction for {symbol}")
        
        # Create test data
        test_data = {
            "current_risk_level": risk_level,
            "risk_band": "low" if risk_level < 0.25 else "medium" if risk_level < 0.75 else "high",
            "market_cycle": "accumulation" if risk_level < 0.25 else "markup" if risk_level < 0.75 else "distribution",
            "time_spent_in_risk": time_in_risk,
            "risk_momentum": -0.12,
            "historical_risk_data": {
                "risk_band_history": [0.2, 0.18, 0.15, 0.12, 0.15],
                "time_in_band_history": [0.1, 0.08, 0.05, 0.03, 0.05],
                "risk_volatility": 0.05
            },
            "cowen_metrics": {
                "risk_band_position": "low_risk",
                "market_cycle_position": "early_cycle",
                "risk_momentum": "decreasing",
                "historical_patterns": "bullish"
            },
            "volatility_analysis": {
                "volatility_regime": "low",
                "volatility_trend": "decreasing",
                "volatility_ratio": 0.8
            },
            "correlation_analysis": {
                "btc_correlation": 0.75,
                "market_correlation": 0.68,
                "risk_correlation": -0.85
            },
            "risk_band_matches": 8
        }
        
        # Convert AI model string to enum
        model = AIModel.ANTHROPIC_CLAUDE if ai_model == "claude-3" else AIModel.OPENAI_GPT4
        
        # Get AI prediction
        prediction = await ai_predictor.predict_riskmetric_win_rate(symbol, test_data, model)
        
        return {
            'test_type': 'riskmetric_ai_prediction',
            'symbol': symbol,
            'input_parameters': {
                'risk_level': risk_level,
                'time_in_risk': time_in_risk,
                'ai_model': ai_model
            },
            'prediction': {
                'win_rate': prediction.win_rate_prediction,
                'confidence': prediction.confidence,
                'direction': prediction.direction,
                'timeframe': prediction.timeframe,
                'reasoning': prediction.reasoning,
                'ai_model': prediction.ai_model
            },
            'opportunity_level': _classify_opportunity(prediction.win_rate_prediction),
            'trading_recommendation': _generate_trading_recommendation(prediction)
        }
        
    except Exception as e:
        logger.error(f"❌ Error testing RiskMetric AI prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error testing RiskMetric AI: {str(e)}")

# Helper functions
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

def _generate_trading_recommendation(prediction: AIWinRatePrediction) -> Dict[str, Any]:
    """Generate trading recommendation based on AI prediction"""
    
    if prediction.win_rate_prediction >= 90.0:
        return {
            "action": "STRONG_ENTRY",
            "position_size": "100%",
            "risk_level": "LOW",
            "reasoning": f"Exceptional opportunity with {prediction.win_rate_prediction:.1f}% win rate"
        }
    elif prediction.win_rate_prediction >= 80.0:
        return {
            "action": "ENTER_TRADE",
            "position_size": "70%",
            "risk_level": "LOW",
            "reasoning": f"Good opportunity with {prediction.win_rate_prediction:.1f}% win rate"
        }
    elif prediction.win_rate_prediction >= 70.0:
        return {
            "action": "CONSIDER_TRADE",
            "position_size": "40%",
            "risk_level": "MEDIUM",
            "reasoning": f"Moderate opportunity with {prediction.win_rate_prediction:.1f}% win rate"
        }
    elif prediction.win_rate_prediction >= 60.0:
        return {
            "action": "CAUTIOUS_ENTRY",
            "position_size": "20%",
            "risk_level": "HIGH",
            "reasoning": f"Weak opportunity with {prediction.win_rate_prediction:.1f}% win rate"
        }
    else:
        return {
            "action": "AVOID_TRADE",
            "position_size": "0%",
            "risk_level": "VERY_HIGH",
            "reasoning": f"Poor opportunity with {prediction.win_rate_prediction:.1f}% win rate"
        }

# Add router tags for better API documentation
router.tags = ["AI Win Rate Prediction", "Smart Model Analysis", "Agent AI Integration"] 