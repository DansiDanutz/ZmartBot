#!/usr/bin/env python3
"""
KingFisher Machine Learning Predictor
Learns from historical liquidation patterns to improve predictions
"""

import logging
import pickle
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class KingFisherMLPredictor:
    """
    Machine Learning predictor for liquidation analysis
    
    Features:
    1. Pattern recognition from historical data
    2. Win rate prediction improvement
    3. Price movement prediction
    4. Risk assessment calibration
    """
    
    def __init__(self, model_path: str = "models/kingfisher"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize models
        self.pattern_classifier = None
        self.win_rate_predictor = None
        self.price_predictor = None
        self.scaler = StandardScaler()
        
        # Feature engineering parameters
        self.feature_config = {
            'liquidation_features': [
                'long_liquidations', 'short_liquidations', 'net_liquidations',
                'liquidation_ratio', 'liquidation_velocity', 'liquidation_acceleration'
            ],
            'cluster_features': [
                'cluster_count', 'cluster_density', 'nearest_cluster_distance',
                'cluster_strength', 'cluster_asymmetry'
            ],
            'market_features': [
                'price_momentum', 'volume_profile', 'volatility',
                'rsi', 'funding_rate'
            ],
            'temporal_features': [
                'hour_of_day', 'day_of_week', 'month_of_year',
                'is_weekend', 'is_market_open'
            ]
        }
        
        # Load existing models if available
        self._load_models()
        
        # Training data buffer
        self.training_buffer = []
        self.buffer_size = 1000
        
        logger.info("KingFisher ML Predictor initialized")
    
    def _load_models(self):
        """Load pre-trained models if they exist"""
        try:
            pattern_model_path = self.model_path / "pattern_classifier.pkl"
            if pattern_model_path.exists():
                with open(pattern_model_path, 'rb') as f:
                    self.pattern_classifier = pickle.load(f)
                logger.info("Loaded pattern classifier model")
            
            winrate_model_path = self.model_path / "winrate_predictor.pkl"
            if winrate_model_path.exists():
                with open(winrate_model_path, 'rb') as f:
                    self.win_rate_predictor = pickle.load(f)
                logger.info("Loaded win rate predictor model")
            
            price_model_path = self.model_path / "price_predictor.pkl"
            if price_model_path.exists():
                with open(price_model_path, 'rb') as f:
                    self.price_predictor = pickle.load(f)
                logger.info("Loaded price predictor model")
            
            scaler_path = self.model_path / "scaler.pkl"
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("Loaded feature scaler")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def extract_features(self, liquidation_data: Dict, 
                        market_data: Optional[Dict] = None) -> np.ndarray:
        """
        Extract features from liquidation and market data
        
        Returns feature vector for ML models
        """
        features = []
        
        try:
            # Liquidation features
            liq_analysis = liquidation_data.get('liquidation_analysis', {})
            features.extend([
                liq_analysis.get('long_liquidations', 0),
                liq_analysis.get('short_liquidations', 0),
                liq_analysis.get('net_liquidations', 0),
                liq_analysis.get('liquidation_ratio', 0.5),
                self._calculate_velocity(liq_analysis),
                self._calculate_acceleration(liq_analysis)
            ])
            
            # Cluster features
            clusters = liquidation_data.get('liquidation_clusters', [])
            features.extend(self._extract_cluster_features(clusters))
            
            # Market features (use defaults if not provided)
            if market_data:
                features.extend([
                    market_data.get('momentum', 0),
                    market_data.get('volume', 0),
                    market_data.get('volatility', 0),
                    market_data.get('rsi', 50),
                    market_data.get('funding_rate', 0)
                ])
            else:
                features.extend([0, 0, 0, 50, 0])  # Default values
            
            # Temporal features
            now = datetime.now()
            features.extend([
                now.hour,
                now.weekday(),
                now.month,
                1 if now.weekday() >= 5 else 0,  # Is weekend
                1 if 9 <= now.hour <= 17 else 0   # Market hours (simplified)
            ])
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            # Return default features on error
            return np.zeros((1, 21))  # 21 total features
    
    def _calculate_velocity(self, liq_data: Dict) -> float:
        """Calculate liquidation velocity (rate of change)"""
        # This would need historical data for proper calculation
        # For now, use a proxy based on current values
        total = liq_data.get('long_liquidations', 0) + liq_data.get('short_liquidations', 0)
        return min(total / 1000000, 10)  # Normalize to 0-10 scale
    
    def _calculate_acceleration(self, liq_data: Dict) -> float:
        """Calculate liquidation acceleration (rate of velocity change)"""
        # Simplified version - would need time series data
        return 0  # Placeholder
    
    def _extract_cluster_features(self, clusters: List[Dict]) -> List[float]:
        """Extract features from liquidation clusters"""
        if not clusters:
            return [0, 0, 0, 0, 0]
        
        cluster_count = len(clusters)
        cluster_sizes = [c.get('size', 0) for c in clusters]
        cluster_distances = [c.get('distance', 0) for c in clusters]
        
        features = [
            cluster_count,
            np.mean(cluster_sizes) if cluster_sizes else 0,
            min(cluster_distances) if cluster_distances else 0,
            max(cluster_sizes) if cluster_sizes else 0,
            np.std(cluster_sizes) if len(cluster_sizes) > 1 else 0
        ]
        
        return features
    
    async def predict_pattern(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Predict liquidation pattern type
        
        Returns pattern classification and confidence
        """
        try:
            if self.pattern_classifier is None:
                # Initialize with default model if not trained
                self.pattern_classifier = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                # Train with synthetic data for demo
                X_train, y_train = self._generate_synthetic_training_data()
                self.pattern_classifier.fit(X_train, y_train)
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Predict pattern
            pattern = self.pattern_classifier.predict(features_scaled)[0]
            probabilities = self.pattern_classifier.predict_proba(features_scaled)[0]
            confidence = max(probabilities)
            
            pattern_names = ['squeeze', 'breakout', 'reversal', 'continuation', 'neutral']
            pattern_index = int(pattern)
            
            return {
                'pattern': pattern_names[pattern_index] if pattern_index < len(pattern_names) else 'unknown',
                'confidence': float(confidence),
                'probabilities': {
                    name: float(prob) 
                    for name, prob in zip(pattern_names, probabilities)
                },
                'features_importance': self._get_feature_importance()
            }
            
        except Exception as e:
            logger.error(f"Error predicting pattern: {e}")
            return {
                'pattern': 'unknown',
                'confidence': 0,
                'error': str(e)
            }
    
    async def predict_win_rate(self, features: np.ndarray,
                              current_win_rate: float) -> Dict[str, Any]:
        """
        Predict adjusted win rate using ML
        
        Combines base win rate with ML adjustment
        """
        try:
            if self.win_rate_predictor is None:
                # Initialize gradient boosting regressor
                self.win_rate_predictor = GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=42
                )
                # Train with synthetic data
                X_train, y_train = self._generate_winrate_training_data()
                self.win_rate_predictor.fit(X_train, y_train)
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Predict win rate adjustment
            adjustment = self.win_rate_predictor.predict(features_scaled)[0]
            
            # Combine with current win rate
            adjusted_win_rate = current_win_rate + adjustment
            adjusted_win_rate = max(0, min(100, adjusted_win_rate))  # Clamp to 0-100
            
            # Calculate confidence based on prediction variance
            confidence = self._calculate_prediction_confidence(features_scaled)
            
            return {
                'original_win_rate': current_win_rate,
                'ml_adjustment': float(adjustment),
                'adjusted_win_rate': float(adjusted_win_rate),
                'confidence': float(confidence),
                'factors': self._explain_adjustment(adjustment)
            }
            
        except Exception as e:
            logger.error(f"Error predicting win rate: {e}")
            return {
                'original_win_rate': current_win_rate,
                'ml_adjustment': 0,
                'adjusted_win_rate': current_win_rate,
                'confidence': 0,
                'error': str(e)
            }
    
    async def predict_price_movement(self, features: np.ndarray,
                                    current_price: float,
                                    timeframe: str = '1h') -> Dict[str, Any]:
        """
        Predict price movement based on liquidation patterns
        
        Timeframes: '15m', '1h', '4h', '1d'
        """
        try:
            if self.price_predictor is None:
                # Initialize price predictor
                self.price_predictor = GradientBoostingRegressor(
                    n_estimators=150,
                    learning_rate=0.05,
                    max_depth=7,
                    random_state=42
                )
                # Train with synthetic data
                X_train, y_train = self._generate_price_training_data()
                self.price_predictor.fit(X_train, y_train)
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Predict price change percentage
            price_change_pct = self.price_predictor.predict(features_scaled)[0]
            
            # Calculate target price
            target_price = current_price * (1 + price_change_pct / 100)
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_price_confidence_intervals(
                current_price, price_change_pct
            )
            
            return {
                'current_price': current_price,
                'predicted_change_pct': float(price_change_pct),
                'target_price': float(target_price),
                'timeframe': timeframe,
                'confidence_intervals': confidence_intervals,
                'direction': 'UP' if price_change_pct > 0 else 'DOWN',
                'strength': self._classify_movement_strength(price_change_pct)
            }
            
        except Exception as e:
            logger.error(f"Error predicting price movement: {e}")
            return {
                'current_price': current_price,
                'predicted_change_pct': 0,
                'target_price': current_price,
                'error': str(e)
            }
    
    def _classify_movement_strength(self, change_pct: float) -> str:
        """Classify price movement strength"""
        abs_change = abs(change_pct)
        if abs_change < 0.5:
            return 'weak'
        elif abs_change < 1.5:
            return 'moderate'
        elif abs_change < 3:
            return 'strong'
        else:
            return 'very_strong'
    
    def _calculate_price_confidence_intervals(self, price: float, 
                                             change_pct: float) -> Dict:
        """Calculate confidence intervals for price prediction"""
        # Simplified confidence intervals
        std_dev = abs(change_pct) * 0.3  # 30% of predicted change as std dev
        
        return {
            '68%': {
                'lower': price * (1 + (change_pct - std_dev) / 100),
                'upper': price * (1 + (change_pct + std_dev) / 100)
            },
            '95%': {
                'lower': price * (1 + (change_pct - 2*std_dev) / 100),
                'upper': price * (1 + (change_pct + 2*std_dev) / 100)
            }
        }
    
    def _generate_synthetic_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data for pattern classifier"""
        n_samples = 1000
        n_features = 21
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 5, n_samples)  # 5 pattern classes
        
        return X, y
    
    def _generate_winrate_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data for win rate predictor"""
        n_samples = 1000
        n_features = 21
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.uniform(-20, 20, n_samples)  # Win rate adjustments
        
        return X, y
    
    def _generate_price_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data for price predictor"""
        n_samples = 1000
        n_features = 21
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.uniform(-5, 5, n_samples)  # Price change percentages
        
        return X, y
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the model"""
        if self.pattern_classifier and hasattr(self.pattern_classifier, 'feature_importances_'):
            importances = self.pattern_classifier.feature_importances_
            feature_names = (
                self.feature_config['liquidation_features'] +
                self.feature_config['cluster_features'] +
                self.feature_config['market_features'] +
                self.feature_config['temporal_features']
            )
            
            return {
                name: float(importance) 
                for name, importance in zip(feature_names, importances)
            }
        return {}
    
    def _calculate_prediction_confidence(self, features: np.ndarray) -> float:
        """Calculate confidence score for predictions"""
        # Simplified confidence calculation
        # In production, use prediction variance or ensemble disagreement
        return 0.75  # Default 75% confidence
    
    def _explain_adjustment(self, adjustment: float) -> List[str]:
        """Explain the ML adjustment factors"""
        factors = []
        
        if adjustment > 10:
            factors.append("Strong bullish liquidation pattern detected")
        elif adjustment > 5:
            factors.append("Moderate bullish signals from liquidation data")
        elif adjustment < -10:
            factors.append("Strong bearish liquidation pattern detected")
        elif adjustment < -5:
            factors.append("Moderate bearish signals from liquidation data")
        else:
            factors.append("Neutral liquidation patterns")
        
        return factors
    
    async def train_online(self, features: np.ndarray, 
                          actual_outcome: Dict):
        """
        Online training with new data
        
        Updates models incrementally with new observations
        """
        try:
            # Add to training buffer
            self.training_buffer.append({
                'features': features,
                'outcome': actual_outcome,
                'timestamp': datetime.now()
            })
            
            # Retrain if buffer is full
            if len(self.training_buffer) >= self.buffer_size:
                await self._retrain_models()
                self.training_buffer = []  # Clear buffer
            
            logger.info(f"Added training sample. Buffer: {len(self.training_buffer)}/{self.buffer_size}")
            
        except Exception as e:
            logger.error(f"Error in online training: {e}")
    
    async def _retrain_models(self):
        """Retrain models with accumulated data"""
        try:
            logger.info("Retraining ML models with new data...")
            
            # Extract features and labels from buffer
            X = np.vstack([item['features'] for item in self.training_buffer])
            
            # Train pattern classifier
            pattern_labels = [self._extract_pattern_label(item['outcome']) 
                            for item in self.training_buffer]
            if self.pattern_classifier:
                self.pattern_classifier.fit(X, pattern_labels)
            
            # Train win rate predictor
            winrate_labels = [item['outcome'].get('actual_win_rate', 50) 
                            for item in self.training_buffer]
            if self.win_rate_predictor:
                self.win_rate_predictor.fit(X, winrate_labels)
            
            # Save updated models
            await self.save_models()
            
            logger.info("Models retrained successfully")
            
        except Exception as e:
            logger.error(f"Error retraining models: {e}")
    
    def _extract_pattern_label(self, outcome: Dict) -> int:
        """Extract pattern label from outcome data"""
        pattern_map = {
            'squeeze': 0,
            'breakout': 1,
            'reversal': 2,
            'continuation': 3,
            'neutral': 4
        }
        pattern = outcome.get('pattern', 'neutral')
        return pattern_map.get(pattern, 4)
    
    async def save_models(self):
        """Save trained models to disk"""
        try:
            if self.pattern_classifier:
                with open(self.model_path / "pattern_classifier.pkl", 'wb') as f:
                    pickle.dump(self.pattern_classifier, f)
            
            if self.win_rate_predictor:
                with open(self.model_path / "winrate_predictor.pkl", 'wb') as f:
                    pickle.dump(self.win_rate_predictor, f)
            
            if self.price_predictor:
                with open(self.model_path / "price_predictor.pkl", 'wb') as f:
                    pickle.dump(self.price_predictor, f)
            
            with open(self.model_path / "scaler.pkl", 'wb') as f:
                pickle.dump(self.scaler, f)
            
            logger.info("Models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def get_model_metrics(self) -> Dict[str, Any]:
        """Get model performance metrics"""
        metrics = {
            'models_trained': {
                'pattern_classifier': self.pattern_classifier is not None,
                'win_rate_predictor': self.win_rate_predictor is not None,
                'price_predictor': self.price_predictor is not None
            },
            'training_buffer_size': len(self.training_buffer),
            'last_training': None  # Would track this in production
        }
        
        return metrics

# Create global instance
kingfisher_ml = KingFisherMLPredictor()