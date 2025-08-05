#!/usr/bin/env python3
"""
KingFisher Service - AI-Powered Win Rate Prediction
Service for KingFisher liquidation analysis with AI win rate predictions

AI INTEGRATION:
- Uses AI models to predict win rates from liquidation analysis
- Multi-timeframe win rate predictions (24h, 7d, 1m)
- Converts liquidation clusters to win rate percentages
- Provides detailed AI analysis reports
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.agents.scoring.ai_win_rate_predictor import (
    ai_predictor,
    AIModel,
    AIWinRatePrediction,
    MultiTimeframeAIPrediction
)

logger = logging.getLogger(__name__)

class KingFisherService:
    """KingFisher liquidation analysis service with AI win rate prediction"""
    
    def __init__(self):
        self.service_name = "kingfisher_service"
        self.ai_predictor = ai_predictor
        logger.info("KingFisher Service with AI integration initialized")
    
    async def analyze_liquidation_data(self, symbol: str) -> Dict[str, Any]:
        """Analyze liquidation data for a symbol"""
        try:
            # This would integrate with actual KingFisher data
            # For now, return structured response
            liquidation_data = {
                'symbol': symbol,
                'liquidation_analysis': {
                    'short_liquidations': 0.0,
                    'long_liquidations': 0.0,
                    'net_liquidations': 0.0,
                    'liquidation_score': 0.0,
                    'cluster_strength': 0.8,
                    'position': 'below',
                    'toxic_order_flow': True,
                    'liquidation_ratio': 0.65
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Add AI win rate prediction
            ai_prediction = await self._get_ai_win_rate_prediction(symbol, liquidation_data)
            liquidation_data['ai_win_rate_prediction'] = ai_prediction
            
            return liquidation_data
        except Exception as e:
            logger.error(f"Error analyzing liquidation data for {symbol}: {str(e)}")
            return {'symbol': symbol, 'error': str(e)}
    
    async def get_kingfisher_score(self, symbol: str) -> Dict[str, Any]:
        """Get KingFisher scoring component with AI win rate prediction"""
        try:
            analysis = await self.analyze_liquidation_data(symbol)
            
            # Get AI win rate prediction
            ai_prediction = analysis.get('ai_win_rate_prediction')
            if ai_prediction:
                win_rate = ai_prediction.win_rate_prediction
                confidence = ai_prediction.confidence
                direction = ai_prediction.direction
                reasoning = ai_prediction.reasoning
            else:
                # Fallback to traditional scoring
                liquidation_score = analysis.get('liquidation_analysis', {}).get('liquidation_score', 0.0)
                win_rate = liquidation_score * 100  # Convert to percentage
                confidence = 0.5
                direction = 'neutral'
                reasoning = 'Traditional liquidation analysis'
            
            return {
                'symbol': symbol,
                'win_rate_prediction': win_rate,
                'confidence': confidence,
                'direction': direction,
                'reasoning': reasoning,
                'ai_analysis': ai_prediction.ai_analysis if ai_prediction else None,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting KingFisher score for {symbol}: {str(e)}")
            return {'symbol': symbol, 'win_rate_prediction': 0.0, 'error': str(e)}
    
    async def get_multi_timeframe_win_rate(self, symbol: str) -> Dict[str, Any]:
        """Get multi-timeframe win rate predictions using AI"""
        try:
            analysis = await self.analyze_liquidation_data(symbol)
            
            # Get multi-timeframe AI prediction
            multi_prediction = await self._get_multi_timeframe_ai_prediction(symbol, analysis)
            
            return {
                'symbol': symbol,
                'short_term_24h': {
                    'win_rate': multi_prediction.short_term_24h.win_rate_prediction,
                    'confidence': multi_prediction.short_term_24h.confidence,
                    'direction': multi_prediction.short_term_24h.direction,
                    'reasoning': multi_prediction.short_term_24h.reasoning
                },
                'medium_term_7d': {
                    'win_rate': multi_prediction.medium_term_7d.win_rate_prediction,
                    'confidence': multi_prediction.medium_term_7d.confidence,
                    'direction': multi_prediction.medium_term_7d.direction,
                    'reasoning': multi_prediction.medium_term_7d.reasoning
                },
                'long_term_1m': {
                    'win_rate': multi_prediction.long_term_1m.win_rate_prediction,
                    'confidence': multi_prediction.long_term_1m.confidence,
                    'direction': multi_prediction.long_term_1m.direction,
                    'reasoning': multi_prediction.long_term_1m.reasoning
                },
                'overall_confidence': multi_prediction.overall_confidence,
                'best_opportunity': {
                    'timeframe': multi_prediction.best_opportunity.timeframe,
                    'win_rate': multi_prediction.best_opportunity.win_rate_prediction,
                    'direction': multi_prediction.best_opportunity.direction
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting multi-timeframe win rate for {symbol}: {str(e)}")
            return {'symbol': symbol, 'error': str(e)}
    
    async def _get_ai_win_rate_prediction(self, symbol: str, liquidation_data: Dict[str, Any]) -> AIWinRatePrediction:
        """Get AI win rate prediction for KingFisher liquidation analysis"""
        try:
            return await self.ai_predictor.predict_kingfisher_win_rate(
                symbol=symbol,
                liquidation_data=liquidation_data,
                model=AIModel.OPENAI_GPT4
            )
        except Exception as e:
            logger.error(f"Error getting AI win rate prediction for {symbol}: {str(e)}")
            # Return fallback prediction
            return self.ai_predictor._create_fallback_prediction(symbol, "kingfisher", f"AI error: {str(e)}")
    
    async def _get_multi_timeframe_ai_prediction(self, symbol: str, liquidation_data: Dict[str, Any]) -> MultiTimeframeAIPrediction:
        """Get multi-timeframe AI prediction for KingFisher liquidation analysis"""
        try:
            return await self.ai_predictor.predict_multi_timeframe_win_rate(
                symbol=symbol,
                agent_type="kingfisher",
                agent_data=liquidation_data,
                model=AIModel.OPENAI_GPT4
            )
        except Exception as e:
            logger.error(f"Error getting multi-timeframe AI prediction for {symbol}: {str(e)}")
            # Return fallback prediction
            return self.ai_predictor._create_fallback_multi_prediction(symbol, "kingfisher")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            'service': self.service_name,
            'status': 'healthy',
            'ai_integration': 'active',
            'timestamp': datetime.now().isoformat()
        }