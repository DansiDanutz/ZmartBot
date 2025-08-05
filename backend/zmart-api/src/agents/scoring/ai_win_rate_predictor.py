#!/usr/bin/env python3
"""
AI-Powered Win Rate Predictor - ZmartBot
Uses smart models (ChatGPT, DeepSeek, etc.) to predict win rates from agent data

Each agent uses AI to analyze their data and predict win rates with detailed reports:
- KingFisher: AI analyzes liquidation clusters for win rate prediction
- Cryptometer: AI analyzes 17 endpoints for win rate prediction  
- RiskMetric: AI analyzes Cowen methodology for win rate prediction
"""

import asyncio
import logging
import json
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AIModel(Enum):
    """Available AI models for win rate prediction"""
    OPENAI_GPT4 = "gpt-4"
    OPENAI_GPT35 = "gpt-3.5-turbo"
    DEEPSEEK = "deepseek-chat"
    ANTHROPIC_CLAUDE = "claude-3"
    GOOGLE_GEMINI = "gemini-pro"

@dataclass
class AIWinRatePrediction:
    """AI-generated win rate prediction with detailed analysis"""
    symbol: str
    agent_type: str  # kingfisher, cryptometer, riskmetric
    ai_model: str
    win_rate_prediction: float  # 0-100 scale
    confidence: float  # 0-1 scale
    direction: str  # long, short, neutral
    timeframe: str  # 24h, 7d, 1m
    reasoning: str
    data_summary: Dict[str, Any]
    ai_analysis: str
    timestamp: datetime

@dataclass
class MultiTimeframeAIPrediction:
    """AI predictions across multiple timeframes"""
    symbol: str
    agent_type: str
    short_term_24h: AIWinRatePrediction
    medium_term_7d: AIWinRatePrediction
    long_term_1m: AIWinRatePrediction
    overall_confidence: float
    best_opportunity: AIWinRatePrediction
    timestamp: datetime

class AIWinRatePredictor:
    """
    AI-Powered Win Rate Predictor
    
    Uses smart models to analyze agent data and predict win rates:
    - KingFisher: Analyzes liquidation clusters for win rate prediction
    - Cryptometer: Analyzes 17 endpoints for win rate prediction
    - RiskMetric: Analyzes Cowen methodology for win rate prediction
    """
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}
        self.default_model = AIModel.OPENAI_GPT4
        self.session = None
        
        # Model-specific configurations
        self.model_configs = {
            AIModel.OPENAI_GPT4: {
                "api_url": "https://api.openai.com/v1/chat/completions",
                "headers": {"Authorization": f"Bearer {self.api_keys.get('openai', '')}"},
                "max_tokens": 2000
            },
            AIModel.DEEPSEEK: {
                "api_url": "https://api.deepseek.com/v1/chat/completions",
                "headers": {"Authorization": f"Bearer {self.api_keys.get('deepseek', '')}"},
                "max_tokens": 2000
            },
            AIModel.ANTHROPIC_CLAUDE: {
                "api_url": "https://api.anthropic.com/v1/messages",
                "headers": {"x-api-key": self.api_keys.get('anthropic', '')},
                "max_tokens": 2000
            }
        }
        
        logger.info("AI Win Rate Predictor initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, self_type, value, traceback):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def predict_kingfisher_win_rate(
        self, 
        symbol: str, 
        liquidation_data: Dict[str, Any],
        model: Optional[AIModel] = None
    ) -> AIWinRatePrediction:
        """
        Use AI to predict win rate from KingFisher liquidation analysis
        
        Analyzes liquidation clusters, toxic order flow, and market structure
        to predict win rates for both long and short positions.
        """
        try:
            model = model or self.default_model
            
            # Prepare data summary for AI
            data_summary = {
                "symbol": symbol,
                "liquidation_cluster_strength": liquidation_data.get('liquidation_cluster_strength', 0.0),
                "cluster_position": liquidation_data.get('cluster_position', 'neutral'),
                "toxic_order_flow": liquidation_data.get('toxic_order_flow', 0.0),
                "flow_direction": liquidation_data.get('flow_direction', 'neutral'),
                "liquidation_map_available": liquidation_data.get('liquidation_map_available', False),
                "toxic_flow_available": liquidation_data.get('toxic_flow_available', False),
                "short_long_ratios": liquidation_data.get('short_long_ratios', {}),
                "historical_matches": liquidation_data.get('historical_matches', 0),
                "market_volatility": liquidation_data.get('market_volatility', 0.0)
            }
            
            # Create AI prompt for KingFisher analysis
            prompt = self._create_kingfisher_prompt(symbol, data_summary)
            
            # Get AI prediction
            ai_response = await self._query_ai_model(model, prompt)
            
            # Parse AI response
            prediction = self._parse_kingfisher_response(ai_response, symbol, data_summary, model.value)
            
            logger.info(f"🎣 KingFisher AI prediction for {symbol}: {prediction.win_rate_prediction:.1f}% win rate")
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Error in KingFisher AI prediction for {symbol}: {e}")
            return self._create_fallback_prediction(symbol, "kingfisher", "AI analysis failed")
    
    async def predict_cryptometer_win_rate(
        self, 
        symbol: str, 
        cryptometer_data: Dict[str, Any],
        model: Optional[AIModel] = None
    ) -> AIWinRatePrediction:
        """
        Use AI to predict win rate from Cryptometer 17-endpoint analysis
        
        Analyzes technical indicators, market sentiment, and multi-timeframe data
        to predict win rates for both long and short positions.
        """
        try:
            model = model or self.default_model
            
            # Prepare data summary for AI
            data_summary = {
                "symbol": symbol,
                "endpoints_analyzed": cryptometer_data.get('endpoints_analyzed', 17),
                "technical_indicators": cryptometer_data.get('technical_indicators', {}),
                "market_sentiment": cryptometer_data.get('market_sentiment', {}),
                "volume_analysis": cryptometer_data.get('volume_analysis', {}),
                "momentum_indicators": cryptometer_data.get('momentum_indicators', {}),
                "trend_analysis": cryptometer_data.get('trend_analysis', {}),
                "support_resistance": cryptometer_data.get('support_resistance', {}),
                "volatility_metrics": cryptometer_data.get('volatility_metrics', {}),
                "correlation_data": cryptometer_data.get('correlation_data', {}),
                "market_structure": cryptometer_data.get('market_structure', {})
            }
            
            # Create AI prompt for Cryptometer analysis
            prompt = self._create_cryptometer_prompt(symbol, data_summary)
            
            # Get AI prediction
            ai_response = await self._query_ai_model(model, prompt)
            
            # Parse AI response
            prediction = self._parse_cryptometer_response(ai_response, symbol, data_summary, model.value)
            
            logger.info(f"📈 Cryptometer AI prediction for {symbol}: {prediction.win_rate_prediction:.1f}% win rate")
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Error in Cryptometer AI prediction for {symbol}: {e}")
            return self._create_fallback_prediction(symbol, "cryptometer", "AI analysis failed")
    
    async def predict_riskmetric_win_rate(
        self, 
        symbol: str, 
        riskmetric_data: Dict[str, Any],
        model: Optional[AIModel] = None
    ) -> AIWinRatePrediction:
        """
        Use AI to predict win rate from RiskMetric Cowen methodology
        
        Analyzes risk bands, market cycles, and Benjamin Cowen methodology
        to predict risk-adjusted win rates for both long and short positions.
        """
        try:
            model = model or self.default_model
            
            # Prepare data summary for AI
            data_summary = {
                "symbol": symbol,
                "current_risk_level": riskmetric_data.get('current_risk_level', 0.5),
                "risk_band": riskmetric_data.get('risk_band', 'medium'),
                "market_cycle": riskmetric_data.get('market_cycle', 'unknown'),
                "time_spent_in_risk": riskmetric_data.get('time_spent_in_risk', 0.0),
                "risk_momentum": riskmetric_data.get('risk_momentum', 0.0),
                "historical_risk_data": riskmetric_data.get('historical_risk_data', {}),
                "cowen_metrics": riskmetric_data.get('cowen_metrics', {}),
                "volatility_analysis": riskmetric_data.get('volatility_analysis', {}),
                "correlation_analysis": riskmetric_data.get('correlation_analysis', {}),
                "risk_band_matches": riskmetric_data.get('risk_band_matches', 0)
            }
            
            # Create AI prompt for RiskMetric analysis
            prompt = self._create_riskmetric_prompt(symbol, data_summary)
            
            # Get AI prediction
            ai_response = await self._query_ai_model(model, prompt)
            
            # Parse AI response
            prediction = self._parse_riskmetric_response(ai_response, symbol, data_summary, model.value)
            
            logger.info(f"📊 RiskMetric AI prediction for {symbol}: {prediction.win_rate_prediction:.1f}% win rate")
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Error in RiskMetric AI prediction for {symbol}: {e}")
            return self._create_fallback_prediction(symbol, "riskmetric", "AI analysis failed")
    
    async def predict_multi_timeframe_win_rate(
        self,
        symbol: str,
        agent_type: str,
        agent_data: Dict[str, Any],
        model: Optional[AIModel] = None
    ) -> MultiTimeframeAIPrediction:
        """
        Use AI to predict win rates across multiple timeframes
        
        Analyzes the same data across 24h, 7d, and 1m timeframes
        to provide comprehensive win rate predictions.
        """
        try:
            model = model or self.default_model
            
            # Predict for each timeframe
            short_term = await self._predict_timeframe(symbol, agent_type, agent_data, "24h", model)
            medium_term = await self._predict_timeframe(symbol, agent_type, agent_data, "7d", model)
            long_term = await self._predict_timeframe(symbol, agent_type, agent_data, "1m", model)
            
            # Calculate overall confidence
            confidences = [short_term.confidence, medium_term.confidence, long_term.confidence]
            overall_confidence = sum(confidences) / len(confidences)
            
            # Find best opportunity
            predictions = [short_term, medium_term, long_term]
            best_opportunity = max(predictions, key=lambda x: x.win_rate_prediction)
            
            result = MultiTimeframeAIPrediction(
                symbol=symbol,
                agent_type=agent_type,
                short_term_24h=short_term,
                medium_term_7d=medium_term,
                long_term_1m=long_term,
                overall_confidence=overall_confidence,
                best_opportunity=best_opportunity,
                timestamp=datetime.now()
            )
            
            logger.info(f"🤖 Multi-timeframe AI prediction for {symbol} ({agent_type}): Best {best_opportunity.timeframe} at {best_opportunity.win_rate_prediction:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in multi-timeframe AI prediction for {symbol}: {e}")
            return self._create_fallback_multi_prediction(symbol, agent_type)
    
    async def _predict_timeframe(
        self, 
        symbol: str, 
        agent_type: str, 
        agent_data: Dict[str, Any], 
        timeframe: str,
        model: AIModel
    ) -> AIWinRatePrediction:
        """Predict win rate for a specific timeframe"""
        
        if agent_type == "kingfisher":
            return await self.predict_kingfisher_win_rate(symbol, agent_data, model)
        elif agent_type == "cryptometer":
            return await self.predict_cryptometer_win_rate(symbol, agent_data, model)
        elif agent_type == "riskmetric":
            return await self.predict_riskmetric_win_rate(symbol, agent_data, model)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    
    def _create_kingfisher_prompt(self, symbol: str, data: Dict[str, Any]) -> str:
        """Create AI prompt for KingFisher liquidation analysis"""
        
        return f"""
You are an expert cryptocurrency trading analyst specializing in liquidation analysis and win rate prediction.

ANALYZE the following KingFisher liquidation data for {symbol} and predict the win rate percentage for trading:

DATA SUMMARY:
- Symbol: {symbol}
- Liquidation Cluster Strength: {data.get('liquidation_cluster_strength', 0.0):.2f}
- Cluster Position: {data.get('cluster_position', 'neutral')}
- Toxic Order Flow: {data.get('toxic_order_flow', 0.0):.2f}
- Flow Direction: {data.get('flow_direction', 'neutral')}
- Liquidation Map Available: {data.get('liquidation_map_available', False)}
- Toxic Flow Available: {data.get('toxic_flow_available', False)}
- Historical Matches: {data.get('historical_matches', 0)}
- Market Volatility: {data.get('market_volatility', 0.0):.2f}

TASK:
1. Analyze the liquidation cluster strength and position
2. Evaluate toxic order flow intensity and direction
3. Consider market volatility and historical patterns
4. Predict win rate percentage (0-100) for both long and short positions
5. Determine the optimal trading direction (long/short/neutral)
6. Assess confidence level (0-1) in your prediction
7. Provide detailed reasoning for your analysis

RESPONSE FORMAT (JSON):
{{
    "win_rate_prediction": 85.5,
    "confidence": 0.88,
    "direction": "long",
    "timeframe": "24h",
    "reasoning": "Detailed analysis of liquidation patterns...",
    "data_analysis": "Summary of key data points...",
    "risk_factors": "Potential risks and considerations..."
}}

Focus on liquidation cluster strength, toxic order flow patterns, and market structure to make accurate win rate predictions.
"""
    
    def _create_cryptometer_prompt(self, symbol: str, data: Dict[str, Any]) -> str:
        """Create AI prompt for Cryptometer technical analysis"""
        
        return f"""
You are an expert cryptocurrency trading analyst specializing in technical analysis and win rate prediction.

ANALYZE the following Cryptometer 17-endpoint data for {symbol} and predict the win rate percentage for trading:

DATA SUMMARY:
- Symbol: {symbol}
- Endpoints Analyzed: {data.get('endpoints_analyzed', 17)}
- Technical Indicators: {json.dumps(data.get('technical_indicators', {}), indent=2)}
- Market Sentiment: {json.dumps(data.get('market_sentiment', {}), indent=2)}
- Volume Analysis: {json.dumps(data.get('volume_analysis', {}), indent=2)}
- Momentum Indicators: {json.dumps(data.get('momentum_indicators', {}), indent=2)}
- Trend Analysis: {json.dumps(data.get('trend_analysis', {}), indent=2)}
- Support/Resistance: {json.dumps(data.get('support_resistance', {}), indent=2)}
- Volatility Metrics: {json.dumps(data.get('volatility_metrics', {}), indent=2)}
- Market Structure: {json.dumps(data.get('market_structure', {}), indent=2)}

TASK:
1. Analyze all 17 technical endpoints comprehensively
2. Evaluate market sentiment and volume patterns
3. Assess momentum and trend indicators
4. Consider support/resistance levels and volatility
5. Predict win rate percentage (0-100) for both long and short positions
6. Determine the optimal trading direction (long/short/neutral)
7. Assess confidence level (0-1) in your prediction
8. Provide detailed reasoning for your analysis

RESPONSE FORMAT (JSON):
{{
    "win_rate_prediction": 82.3,
    "confidence": 0.85,
    "direction": "short",
    "timeframe": "7d",
    "reasoning": "Detailed analysis of technical indicators...",
    "data_analysis": "Summary of key technical points...",
    "risk_factors": "Potential risks and considerations..."
}}

Focus on technical indicator convergence, market structure, and multi-timeframe analysis to make accurate win rate predictions.
"""
    
    def _create_riskmetric_prompt(self, symbol: str, data: Dict[str, Any]) -> str:
        """Create AI prompt for RiskMetric Cowen methodology analysis"""
        
        return f"""
You are an expert cryptocurrency trading analyst specializing in risk analysis and Benjamin Cowen methodology.

ANALYZE the following RiskMetric data for {symbol} and predict the win rate percentage for trading:

DATA SUMMARY:
- Symbol: {symbol}
- Current Risk Level: {data.get('current_risk_level', 0.5):.3f}
- Risk Band: {data.get('risk_band', 'medium')}
- Market Cycle: {data.get('market_cycle', 'unknown')}
- Time Spent in Risk: {data.get('time_spent_in_risk', 0.0):.3f}
- Risk Momentum: {data.get('risk_momentum', 0.0):.3f}
- Risk Band Matches: {data.get('risk_band_matches', 0)}
- Cowen Metrics: {json.dumps(data.get('cowen_metrics', {}), indent=2)}
- Volatility Analysis: {json.dumps(data.get('volatility_analysis', {}), indent=2)}
- Historical Risk Data: {json.dumps(data.get('historical_risk_data', {}), indent=2)}

TASK:
1. Analyze current risk level using Benjamin Cowen methodology
2. Evaluate risk band position and time spent in current band
3. Assess risk momentum and market cycle position
4. Consider historical risk patterns and volatility
5. Predict win rate percentage (0-100) for both long and short positions
6. Determine the optimal trading direction (long/short/neutral)
7. Assess confidence level (0-1) in your prediction
8. Provide detailed reasoning for your analysis

RESPONSE FORMAT (JSON):
{{
    "win_rate_prediction": 88.7,
    "confidence": 0.92,
    "direction": "long",
    "timeframe": "1m",
    "reasoning": "Detailed analysis of risk metrics...",
    "data_analysis": "Summary of key risk points...",
    "risk_factors": "Potential risks and considerations..."
}}

Focus on risk band analysis, market cycle positioning, and Cowen methodology to make accurate win rate predictions.
"""
    
    async def _query_ai_model(self, model: AIModel, prompt: str) -> str:
        """Query AI model for win rate prediction"""
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        config = self.model_configs.get(model, self.model_configs[self.default_model])
        
        try:
            if model == AIModel.OPENAI_GPT4 or model == AIModel.OPENAI_GPT35:
                return await self._query_openai(config, prompt, model.value)
            elif model == AIModel.DEEPSEEK:
                return await self._query_deepseek(config, prompt)
            elif model == AIModel.ANTHROPIC_CLAUDE:
                return await self._query_anthropic(config, prompt)
            else:
                # Fallback to OpenAI
                return await self._query_openai(config, prompt, AIModel.OPENAI_GPT4.value)
                
        except Exception as e:
            logger.error(f"❌ Error querying AI model {model.value}: {e}")
            # Return fallback response
            return self._create_fallback_ai_response()
    
    async def _query_openai(self, config: Dict[str, Any], prompt: str, model: str) -> str:
        """Query OpenAI API"""
        
        # Ensure session is initialized
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an expert cryptocurrency trading analyst. Provide accurate, data-driven win rate predictions in JSON format."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": config.get("max_tokens", 2000),
            "temperature": 0.3  # Low temperature for consistent predictions
        }
        
        async with self.session.post(
            config["api_url"],
            headers=config["headers"],
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"OpenAI API error: {response.status}")
    
    async def _query_deepseek(self, config: Dict[str, Any], prompt: str) -> str:
        """Query DeepSeek API"""
        
        # Ensure session is initialized
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are an expert cryptocurrency trading analyst. Provide accurate, data-driven win rate predictions in JSON format."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": config.get("max_tokens", 2000),
            "temperature": 0.3
        }
        
        async with self.session.post(
            config["api_url"],
            headers=config["headers"],
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"DeepSeek API error: {response.status}")
    
    async def _query_anthropic(self, config: Dict[str, Any], prompt: str) -> str:
        """Query Anthropic Claude API"""
        
        # Ensure session is initialized
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": config.get("max_tokens", 2000),
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with self.session.post(
            config["api_url"],
            headers=config["headers"],
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data["content"][0]["text"]
            else:
                raise Exception(f"Anthropic API error: {response.status}")
    
    def _parse_kingfisher_response(self, response: str, symbol: str, data: Dict[str, Any], model: str) -> AIWinRatePrediction:
        """Parse AI response for KingFisher prediction"""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            
            return AIWinRatePrediction(
                symbol=symbol,
                agent_type="kingfisher",
                ai_model=model,
                win_rate_prediction=parsed.get('win_rate_prediction', 50.0),
                confidence=parsed.get('confidence', 0.5),
                direction=parsed.get('direction', 'neutral'),
                timeframe=parsed.get('timeframe', '24h'),
                reasoning=parsed.get('reasoning', 'AI analysis completed'),
                data_summary=data,
                ai_analysis=response,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"❌ Error parsing KingFisher AI response: {e}")
            return self._create_fallback_prediction(symbol, "kingfisher", f"Parse error: {str(e)}")
    
    def _parse_cryptometer_response(self, response: str, symbol: str, data: Dict[str, Any], model: str) -> AIWinRatePrediction:
        """Parse AI response for Cryptometer prediction"""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            
            return AIWinRatePrediction(
                symbol=symbol,
                agent_type="cryptometer",
                ai_model=model,
                win_rate_prediction=parsed.get('win_rate_prediction', 50.0),
                confidence=parsed.get('confidence', 0.5),
                direction=parsed.get('direction', 'neutral'),
                timeframe=parsed.get('timeframe', '7d'),
                reasoning=parsed.get('reasoning', 'AI analysis completed'),
                data_summary=data,
                ai_analysis=response,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"❌ Error parsing Cryptometer AI response: {e}")
            return self._create_fallback_prediction(symbol, "cryptometer", f"Parse error: {str(e)}")
    
    def _parse_riskmetric_response(self, response: str, symbol: str, data: Dict[str, Any], model: str) -> AIWinRatePrediction:
        """Parse AI response for RiskMetric prediction"""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            
            return AIWinRatePrediction(
                symbol=symbol,
                agent_type="riskmetric",
                ai_model=model,
                win_rate_prediction=parsed.get('win_rate_prediction', 50.0),
                confidence=parsed.get('confidence', 0.5),
                direction=parsed.get('direction', 'neutral'),
                timeframe=parsed.get('timeframe', '1m'),
                reasoning=parsed.get('reasoning', 'AI analysis completed'),
                data_summary=data,
                ai_analysis=response,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"❌ Error parsing RiskMetric AI response: {e}")
            return self._create_fallback_prediction(symbol, "riskmetric", f"Parse error: {str(e)}")
    
    def _create_fallback_prediction(self, symbol: str, agent_type: str, reason: str) -> AIWinRatePrediction:
        """Create fallback prediction when AI analysis fails"""
        return AIWinRatePrediction(
            symbol=symbol,
            agent_type=agent_type,
            ai_model="fallback",
            win_rate_prediction=50.0,  # Neutral 50% win rate
            confidence=0.3,  # Low confidence
            direction="neutral",
            timeframe="24h",
            reasoning=f"Fallback prediction: {reason}",
            data_summary={},
            ai_analysis="AI analysis unavailable",
            timestamp=datetime.now()
        )
    
    def _create_fallback_multi_prediction(self, symbol: str, agent_type: str) -> MultiTimeframeAIPrediction:
        """Create fallback multi-timeframe prediction"""
        fallback = self._create_fallback_prediction(symbol, agent_type, "Multi-timeframe analysis failed")
        
        return MultiTimeframeAIPrediction(
            symbol=symbol,
            agent_type=agent_type,
            short_term_24h=fallback,
            medium_term_7d=fallback,
            long_term_1m=fallback,
            overall_confidence=0.3,
            best_opportunity=fallback,
            timestamp=datetime.now()
        )
    
    def _create_fallback_ai_response(self) -> str:
        """Create fallback AI response"""
        return '''
{
    "win_rate_prediction": 50.0,
    "confidence": 0.3,
    "direction": "neutral",
    "timeframe": "24h",
    "reasoning": "AI analysis unavailable - using fallback prediction",
    "data_analysis": "Unable to analyze data due to AI service issues",
    "risk_factors": "High uncertainty due to AI service unavailability"
}
'''

# Global instance for use across the system
ai_predictor = AIWinRatePredictor() 