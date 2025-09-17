#!/usr/bin/env python3
"""
Enhanced Cryptometer Service with Self-Learning
Wraps existing Cryptometer functionality with machine learning capabilities
Learns from prediction accuracy to improve future scoring
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import sys
from pathlib import Path
import numpy as np

# Add learning system import
sys.path.append(str(Path(__file__).parent.parent.parent))
try:
    from src.learning.self_learning_system import learning_system, Prediction
    LEARNING_AVAILABLE = True
except ImportError:
    LEARNING_AVAILABLE = False
    learning_system = None

# Import existing Cryptometer service or create mock
try:
    from src.services.cryptometer_service import MultiTimeframeCryptometerSystem
    CryptometerService = MultiTimeframeCryptometerSystem  # type: ignore
except ImportError:
    # Create mock CryptometerService for testing
    class CryptometerService:
        def __init__(self):
            pass
        
        async def get_data(self, endpoint: str, symbol: str) -> Dict[str, Any]:
            # Mock data for testing
            import random
            random.seed(hash(symbol + endpoint) % 1000)
            
            mock_data = {
                'ticker': {
                    'price': random.uniform(20000, 120000),
                    'price_change_24h': random.uniform(-10, 10),
                    'volume_24h': random.uniform(1000000, 50000000),
                },
                'ls_ratio': {
                    'long_short_ratio': random.uniform(0.5, 2.5),
                    'long_percentage': random.uniform(30, 70),
                },
                'liquidation_data_v2': {
                    'liquidation_ratio': random.uniform(0.3, 0.8),
                    'total_liquidations': random.uniform(1000000, 100000000),
                },
                'trend_indicator_v3': {
                    'trend_strength': random.uniform(0.2, 0.9),
                    'direction': random.choice(['bullish', 'bearish', 'neutral']),
                },
                'ai_screener': {
                    'signal': random.choice(['bullish', 'bearish', 'neutral']),
                    'confidence': random.uniform(0.5, 0.95),
                },
                'open_interest': {
                    'open_interest': random.uniform(1000000000, 10000000000),
                    'open_interest_change': random.uniform(-20, 20),
                }
            }
            
            return mock_data.get(endpoint, {'error': f'Unknown endpoint: {endpoint}'})
        
        async def get_health_status(self) -> Dict[str, Any]:
            return {
                'service': 'mock_cryptometer_service',
                'status': 'healthy',
                'mock': True,
                'timestamp': datetime.now().isoformat()
            }

logger = logging.getLogger(__name__)

class EnhancedCryptometerService:
    """
    Enhanced Cryptometer service with self-learning capabilities
    Wraps the existing CryptometerService with machine learning
    """
    
    def __init__(self):
        self.base_service = CryptometerService()
        self.service_name = "enhanced_cryptometer_service"
        self.learning_enabled = LEARNING_AVAILABLE
        self.prediction_history = []  # Track predictions for learning
        logger.info(f"Enhanced Cryptometer Service initialized (Learning: {self.learning_enabled})")
    
    async def get_enhanced_analysis(self, symbol: str, endpoint: str = 'all') -> Dict[str, Any]:
        """
        Get enhanced analysis with self-learning corrections
        
        Args:
            symbol: Trading symbol
            endpoint: Specific endpoint or 'all' for comprehensive analysis
            
        Returns:
            Enhanced analysis with learning corrections
        """
        try:
            # Get base analysis from existing service
            if endpoint == 'all':
                base_analysis = await self._get_comprehensive_analysis(symbol)
            else:
                base_analysis = await self._get_single_endpoint_analysis(symbol, endpoint)
            
            # Apply self-learning enhancement
            if self.learning_enabled and learning_system:
                enhanced_analysis = await self._apply_learning_enhancement(symbol, base_analysis, endpoint)
                return enhanced_analysis
            
            return base_analysis
            
        except Exception as e:
            logger.error(f"Error in enhanced analysis for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    async def _get_comprehensive_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive analysis from multiple endpoints"""
        analysis = {
            'symbol': symbol,
            'comprehensive_score': 0.0,
            'confidence': 0.0,
            'endpoint_scores': {},
            'insights': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Key endpoints for comprehensive analysis
        key_endpoints = [
            'ticker', 'ls_ratio', 'liquidation_data_v2', 
            'trend_indicator_v3', 'ai_screener', 'open_interest'
        ]
        
        scores = []
        confidences = []
        
        for endpoint in key_endpoints:
            try:
                endpoint_data = await self.base_service.get_data(endpoint, symbol)
                
                # Convert endpoint data to score (simplified logic)
                score = self._convert_endpoint_to_score(endpoint, endpoint_data)
                confidence = self._estimate_endpoint_confidence(endpoint, endpoint_data)
                
                analysis['endpoint_scores'][endpoint] = {
                    'score': score,
                    'confidence': confidence,
                    'data': endpoint_data
                }
                
                scores.append(score)
                confidences.append(confidence)
                
            except Exception as e:
                logger.warning(f"Error getting {endpoint} for {symbol}: {e}")
                continue
        
        # Calculate comprehensive metrics
        if scores:
            analysis['comprehensive_score'] = float(np.mean(scores))
            analysis['confidence'] = float(np.mean(confidences))
            
            # Generate insights
            analysis['insights'] = self._generate_insights(symbol, analysis['endpoint_scores'])
        
        return analysis
    
    async def _get_single_endpoint_analysis(self, symbol: str, endpoint: str) -> Dict[str, Any]:
        """Get analysis for a single endpoint"""
        try:
            endpoint_data = await self.base_service.get_data(endpoint, symbol)
            
            score = self._convert_endpoint_to_score(endpoint, endpoint_data)
            confidence = self._estimate_endpoint_confidence(endpoint, endpoint_data)
            
            return {
                'symbol': symbol,
                'endpoint': endpoint,
                'score': score,
                'confidence': confidence,
                'data': endpoint_data,
                'insights': [f"Analysis based on {endpoint} endpoint"],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting {endpoint} for {symbol}: {e}")
            return {
                'symbol': symbol,
                'endpoint': endpoint,
                'score': 0.0,
                'confidence': 0.0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _convert_endpoint_to_score(self, endpoint: str, data: Dict[str, Any]) -> float:
        """Convert endpoint data to a 0-100 score"""
        if not data or 'error' in data:
            return 0.0
        
        # Endpoint-specific scoring logic
        if endpoint == 'ticker':
            # Use price change as score indicator
            change_24h = data.get('price_change_24h', 0)
            return max(0, min(100, 50 + change_24h * 2))  # Center at 50, scale by 2x
            
        elif endpoint == 'ls_ratio':
            # Long/Short ratio scoring
            ls_ratio = data.get('long_short_ratio', 1.0)
            if ls_ratio > 1.5:
                return 75.0  # Bullish
            elif ls_ratio > 1.2:
                return 65.0
            elif ls_ratio > 0.8:
                return 50.0  # Neutral
            elif ls_ratio > 0.6:
                return 35.0
            else:
                return 25.0  # Bearish
                
        elif endpoint == 'liquidation_data_v2':
            # Liquidation-based scoring
            liquidation_ratio = data.get('liquidation_ratio', 0.5)
            return liquidation_ratio * 100
            
        elif endpoint == 'trend_indicator_v3':
            # Trend strength scoring
            trend_strength = data.get('trend_strength', 0.5)
            return trend_strength * 100
            
        elif endpoint == 'ai_screener':
            # AI screener confidence
            ai_confidence = data.get('confidence', 0.5)
            signal = data.get('signal', 'neutral')
            base_score = ai_confidence * 100
            
            if signal == 'bullish':
                return min(100, base_score + 10)
            elif signal == 'bearish':
                return max(0, base_score - 10)
            else:
                return base_score
                
        elif endpoint == 'open_interest':
            # Open interest change
            oi_change = data.get('open_interest_change', 0)
            return max(0, min(100, 50 + oi_change * 50))
        
        # Default scoring
        return 50.0
    
    def _estimate_endpoint_confidence(self, endpoint: str, data: Dict[str, Any]) -> float:
        """Estimate confidence for endpoint data"""
        if not data or 'error' in data:
            return 0.0
        
        # Endpoint-specific confidence estimation
        confidence_levels = {
            'ticker': 0.9,           # High confidence for price data
            'ls_ratio': 0.8,         # Good confidence for position data
            'liquidation_data_v2': 0.85,  # High confidence for liquidations
            'trend_indicator_v3': 0.7,    # Moderate confidence for trends
            'ai_screener': 0.75,          # Good confidence for AI
            'open_interest': 0.8          # Good confidence for OI
        }
        
        base_confidence = confidence_levels.get(endpoint, 0.6)
        
        # Adjust based on data quality indicators
        if 'confidence' in data:
            # Use provided confidence if available
            provided_confidence = data['confidence']
            return (base_confidence + provided_confidence) / 2
        
        return base_confidence
    
    def _generate_insights(self, symbol: str, endpoint_scores: Dict[str, Dict]) -> List[str]:
        """Generate insights from endpoint analysis"""
        insights = []
        
        # Analyze score distribution
        scores = [ep['score'] for ep in endpoint_scores.values() if 'score' in ep]
        
        if scores:
            avg_score = np.mean(scores)
            score_std = np.std(scores)
            
            if avg_score > 70:
                insights.append(f"Strong bullish consensus with average score of {avg_score:.1f}")
            elif avg_score < 30:
                insights.append(f"Strong bearish consensus with average score of {avg_score:.1f}")
            else:
                insights.append(f"Mixed signals with average score of {avg_score:.1f}")
            
            if score_std < 10:
                insights.append("High agreement across all indicators")
            elif score_std > 25:
                insights.append("Significant disagreement between indicators - exercise caution")
            
            # Endpoint-specific insights
            for endpoint, ep_data in endpoint_scores.items():
                if ep_data['score'] > 75:
                    insights.append(f"{endpoint.replace('_', ' ').title()} shows strong bullish signal")
                elif ep_data['score'] < 25:
                    insights.append(f"{endpoint.replace('_', ' ').title()} shows strong bearish signal")
        
        return insights[:5]  # Limit to top 5 insights
    
    async def _apply_learning_enhancement(self, symbol: str, base_analysis: Dict[str, Any], 
                                        endpoint: str) -> Dict[str, Any]:
        """Apply self-learning enhancement to base analysis"""
        try:
            # Create learning features
            learning_features = self._create_learning_features(symbol, base_analysis, endpoint)
            
            # Get learning correction for score
            original_score = base_analysis.get('comprehensive_score') or base_analysis.get('score', 0.0)
            
            # Check if learning system has the method before calling
            if learning_system and hasattr(learning_system, 'get_learning_correction'):
                corrected_score, learning_confidence = await learning_system.get_learning_correction(
                    agent_name="EnhancedCryptometerService",
                    prediction_type="score",
                    features=learning_features,
                    original_prediction=original_score
                )
            else:
                corrected_score = original_score
                learning_confidence = 0.0
            
            # Original call (removed):
            # corrected_score, learning_confidence = await learning_system.get_learning_correction(
            #     agent_name="EnhancedCryptometerService",
            #     prediction_type="score",
            #     features=learning_features,
            #     original_prediction=original_score
            # )
            
            # Apply learning correction
            blend_factor = learning_confidence * 0.25  # Max 25% influence
            final_score = (original_score * (1 - blend_factor) + corrected_score * blend_factor)
            
            # Update analysis with enhanced data
            enhanced_analysis = base_analysis.copy()
            
            if 'comprehensive_score' in enhanced_analysis:
                enhanced_analysis['original_score'] = original_score
                enhanced_analysis['comprehensive_score'] = final_score
            else:
                enhanced_analysis['original_score'] = original_score
                enhanced_analysis['score'] = final_score
            
            enhanced_analysis['learning_applied'] = True
            enhanced_analysis['learning_confidence'] = learning_confidence
            enhanced_analysis['learning_correction'] = corrected_score - original_score
            
            # Enhance confidence if learning is confident
            if 'confidence' in enhanced_analysis:
                enhanced_analysis['confidence'] = min(1.0, enhanced_analysis['confidence'] + learning_confidence * 0.1)
            
            logger.debug(f"Applied learning enhancement to {symbol}: {original_score:.1f} -> {final_score:.1f}")
            
            # Record prediction for future learning
            await self._record_prediction(symbol, final_score, learning_features, endpoint)
            
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Error applying learning enhancement: {e}")
            return base_analysis
    
    def _create_learning_features(self, symbol: str, analysis: Dict[str, Any], endpoint: str) -> Dict[str, Any]:
        """Create learning features from analysis"""
        features = {
            # Basic analysis features
            'original_score': analysis.get('comprehensive_score') or analysis.get('score', 0.0),
            'confidence': analysis.get('confidence', 0.0),
            'endpoint_type': endpoint,
            
            # Symbol characteristics
            'symbol_hash': hash(symbol) % 1000,
            
            # Temporal features
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'is_weekend': datetime.now().weekday() >= 5,
            
            # Endpoint scoring features
            'endpoint_count': 1 if endpoint != 'all' else len(analysis.get('endpoint_scores', {})),
        }
        
        # Add endpoint-specific features
        if endpoint == 'all' and 'endpoint_scores' in analysis:
            endpoint_scores = analysis['endpoint_scores']
            
            for ep, ep_data in endpoint_scores.items():
                features[f'{ep}_score'] = ep_data.get('score', 0.0)
                features[f'{ep}_confidence'] = ep_data.get('confidence', 0.0)
            
            # Score statistics
            scores = [ep['score'] for ep in endpoint_scores.values() if 'score' in ep]
            if scores:
                features['score_mean'] = float(np.mean(scores))
                features['score_std'] = float(np.std(scores))
                features['score_min'] = float(np.min(scores))
                features['score_max'] = float(np.max(scores))
        
        return features
    
    async def _record_prediction(self, symbol: str, predicted_score: float, 
                               features: Dict[str, Any], endpoint: str):
        """Record prediction for future learning"""
        if not self.learning_enabled or not learning_system:
            return
        
        prediction_id = str(uuid.uuid4())
        
        prediction = Prediction(
            agent_name="EnhancedCryptometerService",
            symbol=symbol,
            prediction_type="score",
            predicted_value=predicted_score,
            confidence=features.get('confidence', 0.5),
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
            'score': predicted_score,
            'endpoint': endpoint,
            'timestamp': datetime.now()
        })
        
        # Keep history limited
        if len(self.prediction_history) > 1000:
            self.prediction_history = self.prediction_history[-500:]
    
    async def record_outcome(self, symbol: str, actual_score: float, 
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
                if timedelta(minutes=15) <= time_diff <= timedelta(hours=24):
                    success = await learning_system.record_outcome(
                        record['prediction_id'],
                        actual_score,
                        outcome_timestamp
                    )
                    
                    if success:
                        outcomes_recorded += 1
                        logger.info(f"Cryptometer recorded outcome for {symbol}: "
                                  f"predicted={record['score']:.1f}, actual={actual_score:.1f}")
                        break
        
        return outcomes_recorded > 0
    
    async def get_learning_performance(self) -> Dict[str, Any]:
        """Get learning performance metrics"""
        if not self.learning_enabled or not learning_system:
            return {'learning_enabled': False}
        
        performance = await learning_system.get_agent_performance("EnhancedCryptometerService")
        insights = await learning_system.get_learning_insights("EnhancedCryptometerService")
        
        return {
            'learning_enabled': True,
            'performance': performance,
            'insights': insights,
            'predictions_tracked': len(self.prediction_history),
            'service_name': self.service_name
        }
    
    # Delegate methods to base service
    async def get_data(self, endpoint: str, symbol: str) -> Dict[str, Any]:
        """Get data from specific endpoint (delegates to base service)"""
        return await self.base_service.get_data(endpoint, symbol)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get enhanced service health status"""
        base_health = await self.base_service.get_health_status()
        learning_perf = await self.get_learning_performance() if self.learning_enabled else {}
        
        return {
            **base_health,
            'service': self.service_name,
            'enhanced_features': True,
            'learning_enabled': self.learning_enabled,
            'learning_performance': learning_perf,
            'base_service_status': base_health.get('status', 'unknown')
        }

# Create global instance
enhanced_cryptometer_service = EnhancedCryptometerService()