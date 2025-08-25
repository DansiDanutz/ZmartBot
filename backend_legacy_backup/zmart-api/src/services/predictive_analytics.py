#!/usr/bin/env python3
"""
Predictive Analytics System
Implements predictive analytics for win rate forecasting and market prediction
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

from src.config.settings import settings
from src.services.calibrated_scoring_service import CalibratedScoringService
from src.services.neural_network_optimizer import NeuralNetworkOptimizer

logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    """Prediction result structure"""
    target: str
    predicted_value: float
    confidence: float
    timestamp: datetime
    features_used: List[str]
    model_used: str
    accuracy_score: float

@dataclass
class MarketPrediction:
    """Market prediction structure"""
    symbol: str
    price_direction: str  # up, down, sideways
    price_change_percent: float
    volatility_prediction: float
    volume_prediction: float
    confidence: float
    timeframe: str
    timestamp: datetime

class PredictiveAnalytics:
    """
    Predictive analytics system for win rate forecasting and market prediction
    """
    
    def __init__(self):
        """Initialize the predictive analytics system"""
        self.integrated_scoring = CalibratedScoringService()
        self.neural_network_optimizer = NeuralNetworkOptimizer()
        
        # Machine learning models
        self.win_rate_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.market_predictor = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.volatility_predictor = LinearRegression()
        
        # Data preprocessing
        self.scaler = StandardScaler()
        
        # Training data
        self.training_data: Dict[str, pd.DataFrame] = {}
        self.model_performance: Dict[str, Dict[str, float]] = {}
        
        # Prediction history
        self.prediction_history: List[PredictionResult] = []
        self.market_predictions: List[MarketPrediction] = []
        
        # Performance tracking
        self.performance_metrics = {
            'win_rate_accuracy': 0.0,
            'market_prediction_accuracy': 0.0,
            'volatility_prediction_accuracy': 0.0,
            'total_predictions': 0,
            'successful_predictions': 0,
            'last_training': None,
            'model_versions': []
        }
        
        # Feature engineering
        self.feature_columns = [
            'market_regime', 'volatility', 'trend_strength', 'volume_trend',
            'sentiment_score', 'confidence_level', 'risk_score', 'correlation_risk',
            'liquidation_pressure', 'whale_activity', 'technical_indicators',
            'fundamental_metrics', 'market_sentiment', 'news_sentiment',
            'social_sentiment', 'institutional_flow', 'retail_flow'
        ]
        
        logger.info("Predictive Analytics System initialized")
    
    async def collect_training_data(self, symbol: str, days: int = 90) -> pd.DataFrame:
        """Collect training data for predictive models"""
        try:
            logger.info(f"Collecting training data for {symbol} over {days} days")
            
            # Simulate historical data collection
            data = []
            
            for day in range(days):
                # Generate historical data point
                data_point = await self._generate_historical_data_point(symbol, day)
                data.append(data_point)
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Store training data
            self.training_data[symbol] = df
            
            logger.info(f"Collected {len(df)} training data points for {symbol}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error collecting training data for {symbol}: {e}")
            raise
    
    async def _generate_historical_data_point(self, symbol: str, day_offset: int) -> Dict[str, Any]:
        """Generate historical data point for training"""
        try:
            # Simulate realistic market data
            timestamp = datetime.now() - timedelta(days=day_offset)
            
            # Market features
            market_regime = np.random.choice(['trending_bullish', 'trending_bearish', 'ranging_volatile', 'ranging_stable'])
            volatility = np.random.uniform(0.1, 0.8)
            trend_strength = np.random.uniform(0.0, 1.0)
            volume_trend = np.random.uniform(0.5, 2.0)
            
            # Sentiment features
            sentiment_score = np.random.uniform(0.0, 1.0)
            confidence_level = np.random.uniform(0.3, 0.9)
            risk_score = np.random.uniform(0.1, 0.9)
            correlation_risk = np.random.uniform(0.1, 0.8)
            
            # Market-specific features
            liquidation_pressure = np.random.uniform(0.0, 1.0)
            whale_activity = np.random.uniform(0.0, 1.0)
            technical_indicators = np.random.uniform(0.0, 1.0)
            fundamental_metrics = np.random.uniform(0.0, 1.0)
            market_sentiment = np.random.uniform(0.0, 1.0)
            news_sentiment = np.random.uniform(0.0, 1.0)
            social_sentiment = np.random.uniform(0.0, 1.0)
            institutional_flow = np.random.uniform(-1.0, 1.0)
            retail_flow = np.random.uniform(-1.0, 1.0)
            
            # Target variables (what we want to predict)
            actual_win_rate = np.random.uniform(0.4, 0.8)
            price_change = np.random.uniform(-0.1, 0.1)
            volatility_change = np.random.uniform(-0.2, 0.2)
            
            return {
                'timestamp': timestamp,
                'symbol': symbol,
                'market_regime': market_regime,
                'volatility': volatility,
                'trend_strength': trend_strength,
                'volume_trend': volume_trend,
                'sentiment_score': sentiment_score,
                'confidence_level': confidence_level,
                'risk_score': risk_score,
                'correlation_risk': correlation_risk,
                'liquidation_pressure': liquidation_pressure,
                'whale_activity': whale_activity,
                'technical_indicators': technical_indicators,
                'fundamental_metrics': fundamental_metrics,
                'market_sentiment': market_sentiment,
                'news_sentiment': news_sentiment,
                'social_sentiment': social_sentiment,
                'institutional_flow': institutional_flow,
                'retail_flow': retail_flow,
                'actual_win_rate': actual_win_rate,
                'price_change': price_change,
                'volatility_change': volatility_change
            }
            
        except Exception as e:
            logger.error(f"Error generating historical data point: {e}")
            raise
    
    async def train_win_rate_predictor(self, symbol: str):
        """Train win rate prediction model"""
        try:
            logger.info(f"Training win rate predictor for {symbol}")
            
            if symbol not in self.training_data:
                await self.collect_training_data(symbol)
            
            df = self.training_data[symbol]
            
            # Prepare features
            feature_columns = [col for col in self.feature_columns if col in df.columns]
            X = df[feature_columns].values
            y = df['actual_win_rate'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.win_rate_predictor.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.win_rate_predictor.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Store performance
            self.model_performance['win_rate_predictor'] = {
                'mse': float(mse),
                'r2_score': float(r2),
                'accuracy': float(r2)
            }
            
            self.performance_metrics['win_rate_accuracy'] = r2
            self.performance_metrics['last_training'] = datetime.now()
            
            logger.info(f"Win rate predictor trained - R² Score: {r2:.4f}, MSE: {mse:.4f}")
            
        except Exception as e:
            logger.error(f"Error training win rate predictor: {e}")
            raise
    
    async def train_market_predictor(self, symbol: str):
        """Train market prediction model"""
        try:
            logger.info(f"Training market predictor for {symbol}")
            
            if symbol not in self.training_data:
                await self.collect_training_data(symbol)
            
            df = self.training_data[symbol]
            
            # Prepare features
            feature_columns = [col for col in self.feature_columns if col in df.columns]
            X = df[feature_columns].values
            y = df['price_change'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.market_predictor.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.market_predictor.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Store performance
            self.model_performance['market_predictor'] = {
                'mse': float(mse),
                'r2_score': float(r2),
                'accuracy': float(r2)
            }
            
            self.performance_metrics['market_prediction_accuracy'] = r2
            
            logger.info(f"Market predictor trained - R² Score: {r2:.4f}, MSE: {mse:.4f}")
            
        except Exception as e:
            logger.error(f"Error training market predictor: {e}")
            raise
    
    async def train_volatility_predictor(self, symbol: str):
        """Train volatility prediction model"""
        try:
            logger.info(f"Training volatility predictor for {symbol}")
            
            if symbol not in self.training_data:
                await self.collect_training_data(symbol)
            
            df = self.training_data[symbol]
            
            # Prepare features
            feature_columns = [col for col in self.feature_columns if col in df.columns]
            X = df[feature_columns].values
            y = df['volatility_change'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.volatility_predictor.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.volatility_predictor.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Store performance
            self.model_performance['volatility_predictor'] = {
                'mse': float(mse),
                'r2_score': float(r2),
                'accuracy': float(r2)
            }
            
            self.performance_metrics['volatility_prediction_accuracy'] = r2
            
            logger.info(f"Volatility predictor trained - R² Score: {r2:.4f}, MSE: {mse:.4f}")
            
        except Exception as e:
            logger.error(f"Error training volatility predictor: {e}")
            raise
    
    async def predict_win_rate(self, symbol: str, market_features: Dict[str, float]) -> PredictionResult:
        """Predict win rate for a symbol"""
        try:
            # Prepare features
            feature_vector = []
            for feature in self.feature_columns:
                feature_vector.append(market_features.get(feature, 0.0))
            
            # Scale features
            X_scaled = self.scaler.transform(np.array([feature_vector]))
            
            # Make prediction
            predicted_win_rate = self.win_rate_predictor.predict(X_scaled)[0]
            
            # Calculate confidence based on model performance
            confidence = min(1.0, max(0.0, self.performance_metrics['win_rate_accuracy']))
            
            # Create prediction result
            result = PredictionResult(
                target='win_rate',
                predicted_value=predicted_win_rate,
                confidence=confidence,
                timestamp=datetime.now(),
                features_used=self.feature_columns,
                model_used='RandomForestRegressor',
                accuracy_score=self.performance_metrics['win_rate_accuracy']
            )
            
            # Store prediction
            self.prediction_history.append(result)
            self.performance_metrics['total_predictions'] += 1
            
            logger.info(f"Win rate prediction for {symbol}: {predicted_win_rate:.4f} (confidence: {confidence:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting win rate for {symbol}: {e}")
            raise
    
    async def predict_market_movement(self, symbol: str, market_features: Dict[str, float]) -> MarketPrediction:
        """Predict market movement for a symbol"""
        try:
            # Prepare features
            feature_vector = []
            for feature in self.feature_columns:
                feature_vector.append(market_features.get(feature, 0.0))
            
            # Scale features
            X_scaled = self.scaler.transform(np.array([feature_vector]))
            
            # Make predictions
            price_change = self.market_predictor.predict(X_scaled)[0]
            volatility_change = self.volatility_predictor.predict(X_scaled)[0]
            
            # Determine price direction
            if price_change > 0.02:
                direction = 'up'
            elif price_change < -0.02:
                direction = 'down'
            else:
                direction = 'sideways'
            
            # Calculate confidence
            confidence = min(1.0, max(0.0, self.performance_metrics['market_prediction_accuracy']))
            
            # Create market prediction
            prediction = MarketPrediction(
                symbol=symbol,
                price_direction=direction,
                price_change_percent=price_change * 100,
                volatility_prediction=volatility_change,
                volume_prediction=market_features.get('volume_trend', 1.0),
                confidence=confidence,
                timeframe='24h',
                timestamp=datetime.now()
            )
            
            # Store prediction
            self.market_predictions.append(prediction)
            
            logger.info(f"Market prediction for {symbol}: {direction} ({price_change*100:.2f}%) (confidence: {confidence:.2f})")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting market movement for {symbol}: {e}")
            raise
    
    async def get_comprehensive_prediction(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive prediction for a symbol"""
        try:
            # Get current market features
            market_features = await self._get_current_market_features(symbol)
            
            # Make predictions
            win_rate_prediction = await self.predict_win_rate(symbol, market_features)
            market_prediction = await self.predict_market_movement(symbol, market_features)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'win_rate_prediction': {
                    'predicted_win_rate': win_rate_prediction.predicted_value,
                    'confidence': win_rate_prediction.confidence,
                    'accuracy_score': win_rate_prediction.accuracy_score
                },
                'market_prediction': {
                    'price_direction': market_prediction.price_direction,
                    'price_change_percent': market_prediction.price_change_percent,
                    'volatility_prediction': market_prediction.volatility_prediction,
                    'volume_prediction': market_prediction.volume_prediction,
                    'confidence': market_prediction.confidence
                },
                'market_features': market_features,
                'recommendations': await self._generate_prediction_recommendations(
                    win_rate_prediction, market_prediction
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive prediction for {symbol}: {e}")
            raise
    
    async def _get_current_market_features(self, symbol: str) -> Dict[str, float]:
        """Get current market features for prediction"""
        try:
            # Simulate current market features
            features = {
                'market_regime': np.random.choice([0, 1, 2, 3]),  # Encoded regime
                'volatility': np.random.uniform(0.1, 0.8),
                'trend_strength': np.random.uniform(0.0, 1.0),
                'volume_trend': np.random.uniform(0.5, 2.0),
                'sentiment_score': np.random.uniform(0.0, 1.0),
                'confidence_level': np.random.uniform(0.3, 0.9),
                'risk_score': np.random.uniform(0.1, 0.9),
                'correlation_risk': np.random.uniform(0.1, 0.8),
                'liquidation_pressure': np.random.uniform(0.0, 1.0),
                'whale_activity': np.random.uniform(0.0, 1.0),
                'technical_indicators': np.random.uniform(0.0, 1.0),
                'fundamental_metrics': np.random.uniform(0.0, 1.0),
                'market_sentiment': np.random.uniform(0.0, 1.0),
                'news_sentiment': np.random.uniform(0.0, 1.0),
                'social_sentiment': np.random.uniform(0.0, 1.0),
                'institutional_flow': np.random.uniform(-1.0, 1.0),
                'retail_flow': np.random.uniform(-1.0, 1.0)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error getting current market features: {e}")
            return {}
    
    async def _generate_prediction_recommendations(self, win_rate_prediction: PredictionResult, 
                                                 market_prediction: MarketPrediction) -> List[str]:
        """Generate recommendations based on predictions"""
        recommendations = []
        
        # Win rate based recommendations
        if win_rate_prediction.predicted_value > 0.7:
            recommendations.append("High predicted win rate - consider larger position sizes")
        elif win_rate_prediction.predicted_value < 0.5:
            recommendations.append("Low predicted win rate - use smaller position sizes and tight stops")
        
        # Market direction based recommendations
        if market_prediction.price_direction == 'up':
            recommendations.append("Bullish market prediction - focus on long positions")
        elif market_prediction.price_direction == 'down':
            recommendations.append("Bearish market prediction - focus on short positions")
        else:
            recommendations.append("Sideways market prediction - use range trading strategies")
        
        # Volatility based recommendations
        if market_prediction.volatility_prediction > 0.1:
            recommendations.append("High volatility prediction - use wider stops and smaller positions")
        elif market_prediction.volatility_prediction < -0.05:
            recommendations.append("Low volatility prediction - consider tighter stops")
        
        # Confidence based recommendations
        if win_rate_prediction.confidence < 0.6:
            recommendations.append("Low prediction confidence - use conservative position sizing")
        
        return recommendations
    
    async def get_predictive_analytics_report(self) -> Dict[str, Any]:
        """Get comprehensive predictive analytics report"""
        return {
            'model_performance': {
                'win_rate_predictor': self.model_performance.get('win_rate_predictor', {}),
                'market_predictor': self.model_performance.get('market_predictor', {}),
                'volatility_predictor': self.model_performance.get('volatility_predictor', {})
            },
            'performance_metrics': {
                'win_rate_accuracy': self.performance_metrics['win_rate_accuracy'],
                'market_prediction_accuracy': self.performance_metrics['market_prediction_accuracy'],
                'volatility_prediction_accuracy': self.performance_metrics['volatility_prediction_accuracy'],
                'total_predictions': self.performance_metrics['total_predictions'],
                'successful_predictions': self.performance_metrics['successful_predictions'],
                'last_training': self.performance_metrics['last_training'].isoformat() if self.performance_metrics['last_training'] else None
            },
            'training_data': {
                'symbols_trained': list(self.training_data.keys()),
                'total_data_points': sum(len(df) for df in self.training_data.values()),
                'feature_columns': self.feature_columns
            },
            'prediction_history': {
                'total_predictions': len(self.prediction_history),
                'recent_predictions': len(self.prediction_history[-10:]) if self.prediction_history else 0,
                'market_predictions': len(self.market_predictions)
            },
            'timestamp': datetime.now().isoformat()
        }

# Global instance
predictive_analytics = PredictiveAnalytics() 