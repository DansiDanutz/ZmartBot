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
from datetime import datetime, timedelta
import uuid
import sys
from pathlib import Path

# AI Win Rate Predictor temporarily disabled - using unified scoring system
# from src.agents.scoring.ai_win_rate_predictor import (
#     ai_predictor,
#     AIModel,
#     AIWinRatePrediction,
#     MultiTimeframeAIPrediction
# )

# Add learning system import
sys.path.append(str(Path(__file__).parent.parent.parent))
try:
    from src.learning.self_learning_system import learning_system, Prediction
    LEARNING_AVAILABLE = True
except ImportError:
    LEARNING_AVAILABLE = False
    learning_system = None

logger = logging.getLogger(__name__)

class KingFisherService:
    """KingFisher liquidation analysis service with AI win rate prediction"""
    
    def __init__(self):
        self.service_name = "kingfisher_service"
        self.ai_predictor = None  # Temporarily disabled
        self.learning_enabled = LEARNING_AVAILABLE
        self.prediction_history = []  # Track predictions for learning
        logger.info(f"KingFisher Service initialized (AI temporarily disabled)")
    
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
            
            # Add AI win rate prediction (mock implementation)
            ai_prediction = await self._get_ai_win_rate_prediction(symbol, liquidation_data)
            liquidation_data['ai_win_rate_prediction'] = ai_prediction
            
            # Apply self-learning correction if available
            if self.learning_enabled and learning_system and ai_prediction:
                learning_features = self._create_learning_features(symbol, liquidation_data, ai_prediction)
                
                # Get learning correction for win rate
                corrected_win_rate, learning_confidence = await learning_system.get_learning_correction(
                    agent_name="KingFisherService",
                    prediction_type="win_rate",
                    features=learning_features,
                    original_prediction=ai_prediction['win_rate_prediction']
                )
                
                # Apply learning correction
                blend_factor = learning_confidence * 0.2  # Max 20% influence
                final_win_rate = (ai_prediction['win_rate_prediction'] * (1 - blend_factor) + 
                                corrected_win_rate * blend_factor)
                
                # Update the prediction with learned correction
                ai_prediction['win_rate_prediction'] = final_win_rate
                ai_prediction['confidence'] = min(1.0, ai_prediction['confidence'] + learning_confidence * 0.1)
                
                logger.debug(f"Applied learning correction to KingFisher win rate: {ai_prediction['win_rate_prediction']:.1f}")
                
                # Record prediction for future learning
                await self._record_prediction(symbol, ai_prediction, learning_features)
            
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
            
            if not multi_prediction:
                return {'symbol': symbol, 'error': 'Failed to get AI prediction'}
            
            return {
                'symbol': symbol,
                'short_term_24h': {
                    'win_rate': multi_prediction['timeframes']['24h']['win_rate'],
                    'confidence': multi_prediction['timeframes']['24h']['confidence'],
                    'direction': 'neutral',
                    'reasoning': 'Mock KingFisher analysis'
                },
                'medium_term_7d': {
                    'win_rate': multi_prediction['timeframes']['7d']['win_rate'],
                    'confidence': multi_prediction['timeframes']['7d']['confidence'],
                    'direction': 'neutral',
                    'reasoning': 'Mock KingFisher analysis'
                },
                'long_term_1m': {
                    'win_rate': multi_prediction['timeframes']['1m']['win_rate'],
                    'confidence': multi_prediction['timeframes']['1m']['confidence'],
                    'direction': 'neutral',
                    'reasoning': 'Mock KingFisher analysis'
                },
                'overall_confidence': multi_prediction['overall_confidence'],
                'best_opportunity': {
                    'timeframe': '7d',
                    'win_rate': multi_prediction['timeframes']['7d']['win_rate'],
                    'direction': 'neutral'
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting multi-timeframe win rate for {symbol}: {str(e)}")
            return {'symbol': symbol, 'error': str(e)}
    
    async def _get_ai_win_rate_prediction(self, symbol: str, liquidation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get AI win rate prediction for KingFisher liquidation analysis (mock implementation)"""
        try:
            # Mock prediction for now
            return {
                'win_rate_prediction': 0.65,
                'confidence': 0.75,
                'direction': 'neutral',
                'model_type': 'kingfisher_liquidation',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting AI win rate prediction for {symbol}: {str(e)}")
            return None
    
    async def _get_multi_timeframe_ai_prediction(self, symbol: str, liquidation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get multi-timeframe AI prediction for KingFisher liquidation analysis (mock implementation)"""
        try:
            # Mock multi-timeframe prediction
            return {
                'timeframes': {
                    '24h': {'win_rate': 0.65, 'confidence': 0.75},
                    '7d': {'win_rate': 0.70, 'confidence': 0.80},
                    '1m': {'win_rate': 0.60, 'confidence': 0.70}
                },
                'overall_win_rate': 0.65,
                'overall_confidence': 0.75,
                'direction': 'neutral',
                'model_type': 'kingfisher_multi_timeframe',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting multi-timeframe AI prediction for {symbol}: {str(e)}")
            return None
    
    def _create_learning_features(self, symbol: str, liquidation_data: Dict[str, Any], 
                                ai_prediction: Any) -> Dict[str, Any]:
        """Create feature dictionary for machine learning"""
        analysis = liquidation_data.get('liquidation_analysis', {})
        
        features = {
            # Liquidation analysis features
            'short_liquidations': float(analysis.get('short_liquidations', 0.0)),
            'long_liquidations': float(analysis.get('long_liquidations', 0.0)),
            'net_liquidations': float(analysis.get('net_liquidations', 0.0)),
            'liquidation_score': float(analysis.get('liquidation_score', 0.0)),
            'cluster_strength': float(analysis.get('cluster_strength', 0.0)),
            'liquidation_ratio': float(analysis.get('liquidation_ratio', 0.0)),
            'toxic_order_flow': bool(analysis.get('toxic_order_flow', False)),
            
            # Position characteristics
            'position': analysis.get('position', 'neutral'),
            
            # AI prediction features
            'ai_win_rate': float(ai_prediction.win_rate_prediction) if ai_prediction else 0.0,
            'ai_confidence': float(ai_prediction.confidence) if ai_prediction else 0.0,
            'ai_direction': ai_prediction.direction if ai_prediction else 'neutral',
            
            # Symbol characteristics
            'symbol_hash': hash(symbol) % 1000,
            
            # Temporal features
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'is_weekend': datetime.now().weekday() >= 5,
            
            # Market context (would be enhanced with real market data)
            'volatility_estimate': 0.5,  # Placeholder
            'trend_estimate': 0.5,       # Placeholder
        }
        
        return features
    
    async def _record_prediction(self, symbol: str, ai_prediction: Any, features: Dict[str, Any]):
        """Record prediction for future learning"""
        if not self.learning_enabled or not learning_system or not ai_prediction:
            return
        
        prediction_id = str(uuid.uuid4())
        
        prediction = Prediction(
            agent_name="KingFisherService",
            symbol=symbol,
            prediction_type="win_rate",
            predicted_value=ai_prediction.win_rate_prediction,
            confidence=ai_prediction.confidence,
            features=features,
            timestamp=datetime.now(),
            prediction_id=prediction_id
        )
        
        # Record prediction for future learning
        await learning_system.record_prediction(prediction)
        
        # Store in local history
        self.prediction_history.append({
            'prediction_id': prediction_id,
            'symbol': symbol,
            'win_rate': ai_prediction.win_rate_prediction,
            'timestamp': datetime.now(),
            'direction': ai_prediction.direction
        })
        
        # Keep history limited
        if len(self.prediction_history) > 1000:
            self.prediction_history = self.prediction_history[-500:]
    
    async def record_outcome(self, symbol: str, actual_win_rate: float, 
                           outcome_timestamp: Optional[datetime] = None) -> bool:
        """Record actual outcome for learning"""
        if not self.learning_enabled or not learning_system:
            return False
        
        outcomes_recorded = 0
        
        # Find recent predictions for this symbol
        for record in reversed(self.prediction_history):
            if record['symbol'] == symbol:
                time_diff = (outcome_timestamp or datetime.now()) - record['timestamp']
                
                # Check if outcome is within reasonable time window
                if timedelta(minutes=30) <= time_diff <= timedelta(hours=48):
                    success = await learning_system.record_outcome(
                        record['prediction_id'],
                        actual_win_rate,
                        outcome_timestamp
                    )
                    
                    if success:
                        outcomes_recorded += 1
                        logger.info(f"KingFisher recorded outcome for {symbol}: "
                                  f"predicted={record['win_rate']:.1f}%, actual={actual_win_rate:.1f}%")
                        break
        
        return outcomes_recorded > 0
    
    async def get_learning_performance(self) -> Dict[str, Any]:
        """Get learning performance metrics"""
        if not self.learning_enabled or not learning_system:
            return {'learning_enabled': False}
        
        performance = await learning_system.get_agent_performance("KingFisherService")
        insights = await learning_system.get_learning_insights("KingFisherService")
        
        return {
            'learning_enabled': True,
            'performance': performance,
            'insights': insights,
            'predictions_tracked': len(self.prediction_history),
            'service_name': self.service_name
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        learning_perf = await self.get_learning_performance() if self.learning_enabled else {}
        
        return {
            'service': self.service_name,
            'status': 'healthy',
            'ai_integration': 'active',
            'learning_enabled': self.learning_enabled,
            'learning_performance': learning_perf,
            'timestamp': datetime.now().isoformat()
        }

# Create global instance
kingfisher_service = KingFisherService()