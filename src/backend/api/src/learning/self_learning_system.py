#!/usr/bin/env python3
"""
Self-Learning System for ZmartBot Agents
Implements machine learning capabilities for all trading agents
Learns from prediction outcomes to improve accuracy over time
"""

import sqlite3
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncio
from collections import defaultdict
import pickle
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, precision_score, recall_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class Prediction:
    """Structure for storing predictions"""
    agent_name: str
    symbol: str
    prediction_type: str  # 'score', 'direction', 'win_rate', 'pattern'
    predicted_value: float
    confidence: float
    features: Dict[str, Any]  # Input features used for prediction
    timestamp: datetime
    prediction_id: str
    
    # Outcome tracking (filled later)
    actual_value: Optional[float] = None
    outcome_timestamp: Optional[datetime] = None
    accuracy: Optional[float] = None
    error: Optional[float] = None

@dataclass
class LearningMetrics:
    """Learning performance metrics"""
    agent_name: str
    total_predictions: int
    accuracy: float
    precision: float
    recall: float
    avg_error: float
    improvement_rate: float
    confidence_calibration: float
    last_updated: datetime

class SelfLearningSystem:
    """
    Self-learning system that helps all agents learn from their predictions
    Uses machine learning to improve prediction accuracy over time
    """
    
    def __init__(self, db_path: str = "data/learning_system.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Learning models for different agents
        self.models = {}
        self.scalers = {}
        self.feature_importance = defaultdict(dict)
        
        # Performance tracking
        self.performance_history = defaultdict(list)
        self.learning_metrics = {}
        
        # Learning parameters
        self.min_samples_to_learn = 50  # Minimum samples before learning
        self.retrain_interval = 100     # Retrain after N new samples
        self.confidence_threshold = 0.7  # Minimum confidence for learning
        
        self._init_database()
        logger.info("Self-Learning System initialized")
    
    def _init_database(self):
        """Initialize the learning database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id TEXT UNIQUE,
                agent_name TEXT,
                symbol TEXT,
                prediction_type TEXT,
                predicted_value REAL,
                confidence REAL,
                features TEXT,
                timestamp TEXT,
                actual_value REAL,
                outcome_timestamp TEXT,
                accuracy REAL,
                error REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Learning metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                total_predictions INTEGER,
                accuracy REAL,
                precision_score REAL,
                recall_score REAL,
                avg_error REAL,
                improvement_rate REAL,
                confidence_calibration REAL,
                last_updated TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Feature importance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_importance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                feature_name TEXT,
                importance REAL,
                prediction_type TEXT,
                last_updated TEXT
            )
        ''')
        
        # Model performance history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                accuracy REAL,
                error REAL,
                sample_count INTEGER,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Learning database initialized")
    
    async def record_prediction(self, prediction: Prediction) -> str:
        """
        Record a new prediction for future learning
        
        Args:
            prediction: Prediction object with all details
            
        Returns:
            Prediction ID for tracking
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO predictions 
                (prediction_id, agent_name, symbol, prediction_type, 
                 predicted_value, confidence, features, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction.prediction_id,
                prediction.agent_name,
                prediction.symbol,
                prediction.prediction_type,
                prediction.predicted_value,
                prediction.confidence,
                json.dumps(prediction.features),
                prediction.timestamp.isoformat()
            ))
            
            conn.commit()
            logger.debug(f"Recorded prediction {prediction.prediction_id} for {prediction.agent_name}")
            
        except Exception as e:
            logger.error(f"Error recording prediction: {e}")
            raise
        finally:
            conn.close()
        
        return prediction.prediction_id
    
    async def record_outcome(self, prediction_id: str, actual_value: float, 
                           outcome_timestamp: Optional[datetime] = None) -> bool:
        """
        Record the actual outcome for a prediction
        
        Args:
            prediction_id: ID of the prediction
            actual_value: The actual value that occurred
            outcome_timestamp: When the outcome was measured
            
        Returns:
            True if successful
        """
        if outcome_timestamp is None:
            outcome_timestamp = datetime.now()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get the prediction
            cursor.execute('''
                SELECT predicted_value, confidence, prediction_type 
                FROM predictions WHERE prediction_id = ?
            ''', (prediction_id,))
            
            result = cursor.fetchone()
            if not result:
                logger.warning(f"Prediction {prediction_id} not found")
                return False
            
            predicted_value, confidence, prediction_type = result
            
            # Calculate accuracy and error
            if prediction_type in ['score', 'win_rate']:
                # Regression metrics
                error = abs(actual_value - predicted_value)
                accuracy = max(0, 1 - error / 100)  # Convert to 0-1 scale
            else:
                # Classification metrics
                error = 0 if abs(actual_value - predicted_value) < 0.5 else 1
                accuracy = 1 - error
            
            # Update the prediction with outcome
            cursor.execute('''
                UPDATE predictions 
                SET actual_value = ?, outcome_timestamp = ?, 
                    accuracy = ?, error = ?
                WHERE prediction_id = ?
            ''', (actual_value, outcome_timestamp.isoformat(), 
                  accuracy, error, prediction_id))
            
            conn.commit()
            logger.debug(f"Recorded outcome for prediction {prediction_id}")
            
            # Trigger learning if enough samples
            await self._check_learning_trigger(cursor, prediction_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording outcome: {e}")
            return False
        finally:
            conn.close()
    
    async def _check_learning_trigger(self, cursor, prediction_id: str):
        """Check if we should trigger learning for this agent"""
        # Get agent name
        cursor.execute('SELECT agent_name FROM predictions WHERE prediction_id = ?', 
                      (prediction_id,))
        result = cursor.fetchone()
        if not result:
            return
        
        agent_name = result[0]
        
        # Count completed predictions for this agent
        cursor.execute('''
            SELECT COUNT(*) FROM predictions 
            WHERE agent_name = ? AND actual_value IS NOT NULL
        ''', (agent_name,))
        
        count = cursor.fetchone()[0]
        
        # Check if we should retrain
        if count >= self.min_samples_to_learn and count % self.retrain_interval == 0:
            logger.info(f"Triggering learning for {agent_name} with {count} samples")
            await self._train_agent_models(agent_name)
    
    async def _train_agent_models(self, agent_name: str):
        """Train machine learning models for an agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get completed predictions for this agent
            cursor.execute('''
                SELECT prediction_type, predicted_value, actual_value, 
                       confidence, features, accuracy, error
                FROM predictions 
                WHERE agent_name = ? AND actual_value IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 1000
            ''', (agent_name,))
            
            predictions = cursor.fetchall()
            
            if len(predictions) < self.min_samples_to_learn:
                logger.info(f"Not enough samples for {agent_name}: {len(predictions)}")
                return
            
            # Group by prediction type
            by_type = defaultdict(list)
            for pred in predictions:
                by_type[pred[0]].append(pred)
            
            # Train models for each prediction type
            for pred_type, type_predictions in by_type.items():
                if len(type_predictions) < 20:  # Minimum per type
                    continue
                
                await self._train_model_for_type(agent_name, pred_type, type_predictions)
            
            # Update learning metrics
            await self._update_learning_metrics(agent_name, predictions)
            
        except Exception as e:
            logger.error(f"Error training models for {agent_name}: {e}")
        finally:
            conn.close()
    
    async def _train_model_for_type(self, agent_name: str, pred_type: str, 
                                  predictions: List[Tuple]):
        """Train a specific model for prediction type"""
        try:
            # Extract features and targets
            X = []
            y_actual = []
            y_predicted = []
            confidences = []
            
            for pred in predictions:
                _, predicted, actual, confidence, features_json, accuracy, error = pred
                
                try:
                    features = json.loads(features_json)
                    # Convert features to numerical vector
                    feature_vector = self._extract_feature_vector(features)
                    
                    X.append(feature_vector)
                    y_actual.append(actual)
                    y_predicted.append(predicted)
                    confidences.append(confidence)
                    
                except Exception as e:
                    logger.debug(f"Error parsing features: {e}")
                    continue
            
            if len(X) < 10:
                logger.warning(f"Not enough valid samples for {agent_name}/{pred_type}")
                return
            
            X = np.array(X)
            y_actual = np.array(y_actual)
            y_predicted = np.array(y_predicted)
            confidences = np.array(confidences)
            
            # Initialize or get existing models
            model_key = f"{agent_name}_{pred_type}"
            
            # Train correction model (learns from prediction errors)
            if pred_type in ['score', 'win_rate']:
                # Regression for continuous values
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                correction_target = y_actual - y_predicted  # Error correction
            else:
                # Classification for discrete values
                model = RandomForestClassifier(n_estimators=100, random_state=42)
                correction_target = (y_actual == y_predicted).astype(int)  # Accuracy
            
            # Scale features
            if model_key not in self.scalers:
                self.scalers[model_key] = StandardScaler()
            
            X_scaled = self.scalers[model_key].fit_transform(X)
            
            # Train the model
            model.fit(X_scaled, correction_target)
            self.models[model_key] = model
            
            # Calculate feature importance
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[agent_name][pred_type] = model.feature_importances_
            
            # Evaluate model
            predictions_corrected = model.predict(X_scaled)
            
            if pred_type in ['score', 'win_rate']:
                mse = mean_squared_error(correction_target, predictions_corrected)
                logger.info(f"Trained {model_key} - MSE: {mse:.3f}")
            else:
                accuracy = accuracy_score(correction_target, predictions_corrected)
                logger.info(f"Trained {model_key} - Accuracy: {accuracy:.3f}")
            
            # Store model to disk
            model_file = self.db_path.parent / f"{model_key}_model.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump({
                    'model': model,
                    'scaler': self.scalers[model_key],
                    'feature_names': list(range(X.shape[1])),
                    'training_date': datetime.now().isoformat()
                }, f)
            
            logger.info(f"Trained and saved model for {agent_name}/{pred_type}")
            
        except Exception as e:
            logger.error(f"Error training model for {agent_name}/{pred_type}: {e}")
    
    def _extract_feature_vector(self, features: Dict[str, Any]) -> List[float]:
        """Convert feature dictionary to numerical vector"""
        vector = []
        
        # Common feature extraction logic
        for key, value in features.items():
            if isinstance(value, (int, float)):
                vector.append(float(value))
            elif isinstance(value, bool):
                vector.append(1.0 if value else 0.0)
            elif isinstance(value, str):
                # Simple string hashing for categorical features
                vector.append(float(hash(value) % 1000) / 1000)
            elif isinstance(value, list):
                # List features - take length and mean if numeric
                vector.append(float(len(value)))
                if value and isinstance(value[0], (int, float)):
                    vector.append(float(np.mean(value)))
                else:
                    vector.append(0.0)
            else:
                vector.append(0.0)
        
        # Ensure consistent vector length (pad or truncate to 50)
        if len(vector) < 50:
            vector.extend([0.0] * (50 - len(vector)))
        else:
            vector = vector[:50]
        
        return vector
    
    async def get_learning_correction(self, agent_name: str, prediction_type: str,
                                    features: Dict[str, Any], 
                                    original_prediction: float) -> Tuple[float, float]:
        """
        Get learning-based correction for a prediction
        
        Args:
            agent_name: Name of the agent
            prediction_type: Type of prediction
            features: Input features
            original_prediction: Original prediction value
            
        Returns:
            Tuple of (corrected_prediction, correction_confidence)
        """
        model_key = f"{agent_name}_{prediction_type}"
        
        if model_key not in self.models:
            # No trained model yet, return original
            return original_prediction, 0.0
        
        try:
            # Extract features
            feature_vector = self._extract_feature_vector(features)
            X = np.array([feature_vector])
            
            # Scale features
            if model_key in self.scalers:
                X_scaled = self.scalers[model_key].transform(X)
            else:
                X_scaled = X
            
            # Get model prediction (correction)
            model = self.models[model_key]
            correction = model.predict(X_scaled)[0]
            
            # Calculate confidence based on model performance
            correction_confidence = self._get_model_confidence(agent_name, prediction_type)
            
            # Apply correction
            if prediction_type in ['score', 'win_rate']:
                # For regression, correction is the error adjustment
                corrected_prediction = original_prediction + correction
            else:
                # For classification, use correction as confidence modifier
                corrected_prediction = original_prediction
            
            # Ensure bounds
            if prediction_type in ['score', 'win_rate']:
                corrected_prediction = max(0, min(100, corrected_prediction))
            
            logger.debug(f"Applied learning correction for {agent_name}/{prediction_type}: "
                        f"{original_prediction:.2f} -> {corrected_prediction:.2f}")
            
            return corrected_prediction, correction_confidence
            
        except Exception as e:
            logger.error(f"Error applying learning correction: {e}")
            return original_prediction, 0.0
    
    def _get_model_confidence(self, agent_name: str, prediction_type: str) -> float:
        """Get confidence level for a model based on historical performance"""
        if agent_name in self.learning_metrics:
            metrics = self.learning_metrics[agent_name]
            return min(metrics.accuracy * metrics.confidence_calibration, 0.9)
        
        return 0.5  # Default moderate confidence
    
    async def _update_learning_metrics(self, agent_name: str, predictions: List[Tuple]):
        """Update learning metrics for an agent"""
        try:
            if not predictions:
                return
            
            # Calculate metrics
            accuracies = [pred[5] for pred in predictions if pred[5] is not None]
            errors = [pred[6] for pred in predictions if pred[6] is not None]
            
            if not accuracies:
                return
            
            # Overall metrics
            accuracy = np.mean(accuracies)
            avg_error = np.mean(errors) if errors else 0
            
            # Calculate improvement rate (compare recent vs older predictions)
            recent_accuracy = np.mean(accuracies[:50]) if len(accuracies) >= 50 else accuracy
            older_accuracy = np.mean(accuracies[-50:]) if len(accuracies) >= 100 else accuracy
            improvement_rate = (recent_accuracy - older_accuracy) if older_accuracy > 0 else 0
            
            # Confidence calibration (how well confidence matches actual accuracy)
            confidences = [pred[3] for pred in predictions]
            confidence_calibration = 1.0 - abs(np.mean(confidences) - accuracy) if confidences else 1.0
            
            # Create metrics object
            metrics = LearningMetrics(
                agent_name=agent_name,
                total_predictions=len(predictions),
                accuracy=float(accuracy),
                precision=float(accuracy),  # Simplified for now
                recall=float(accuracy),     # Simplified for now
                avg_error=float(avg_error),
                improvement_rate=float(improvement_rate),
                confidence_calibration=float(confidence_calibration),
                last_updated=datetime.now()
            )
            
            self.learning_metrics[agent_name] = metrics
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO learning_metrics 
                (agent_name, total_predictions, accuracy, precision_score, 
                 recall_score, avg_error, improvement_rate, confidence_calibration, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_name, metrics.total_predictions, metrics.accuracy,
                metrics.precision, metrics.recall, metrics.avg_error,
                metrics.improvement_rate, metrics.confidence_calibration,
                metrics.last_updated.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated learning metrics for {agent_name}: "
                       f"Accuracy={accuracy:.3f}, Error={avg_error:.3f}")
            
        except Exception as e:
            logger.error(f"Error updating learning metrics: {e}")
    
    async def get_agent_performance(self, agent_name: str) -> Optional[LearningMetrics]:
        """Get learning performance for an agent"""
        if agent_name in self.learning_metrics:
            return self.learning_metrics[agent_name]
        
        # Try to load from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM learning_metrics 
            WHERE agent_name = ? 
            ORDER BY last_updated DESC LIMIT 1
        ''', (agent_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return LearningMetrics(
                agent_name=str(result[1]),
                total_predictions=int(result[2]),
                accuracy=float(result[3]),
                precision=float(result[4]),
                recall=float(result[5]),
                avg_error=float(result[6]),
                improvement_rate=float(result[7]),
                confidence_calibration=float(result[8]),
                last_updated=datetime.fromisoformat(str(result[9]))
            )
        
        return None
    
    async def get_learning_insights(self, agent_name: str) -> Dict[str, Any]:
        """Get learning insights and recommendations for an agent"""
        metrics = await self.get_agent_performance(agent_name)
        
        insights = {
            'agent_name': agent_name,
            'learning_status': 'No data available',
            'recommendations': [],
            'performance_trend': 'Unknown',
            'confidence_rating': 'Low'
        }
        
        if not metrics:
            insights['recommendations'].append('Need more prediction data to start learning')
            return insights
        
        # Analyze performance
        if metrics.accuracy > 0.8:
            insights['learning_status'] = 'Excellent - High accuracy achieved'
            insights['confidence_rating'] = 'High'
        elif metrics.accuracy > 0.7:
            insights['learning_status'] = 'Good - Moderate accuracy'
            insights['confidence_rating'] = 'Medium'
        elif metrics.accuracy > 0.6:
            insights['learning_status'] = 'Fair - Room for improvement'
            insights['confidence_rating'] = 'Medium'
        else:
            insights['learning_status'] = 'Poor - Needs attention'
            insights['confidence_rating'] = 'Low'
        
        # Performance trend
        if metrics.improvement_rate > 0.05:
            insights['performance_trend'] = 'Improving rapidly'
        elif metrics.improvement_rate > 0.01:
            insights['performance_trend'] = 'Slowly improving'
        elif metrics.improvement_rate > -0.01:
            insights['performance_trend'] = 'Stable'
        else:
            insights['performance_trend'] = 'Declining'
        
        # Recommendations
        if metrics.confidence_calibration < 0.7:
            insights['recommendations'].append('Improve confidence calibration')
        
        if metrics.avg_error > 10:
            insights['recommendations'].append('Focus on reducing prediction errors')
        
        if metrics.total_predictions < 100:
            insights['recommendations'].append('Collect more prediction data')
        
        if metrics.improvement_rate < 0:
            insights['recommendations'].append('Review and adjust prediction strategies')
        
        return insights
    
    async def export_learning_data(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Export learning data for analysis"""
        conn = sqlite3.connect(self.db_path)
        
        if agent_name:
            query = 'SELECT * FROM predictions WHERE agent_name = ?'
            params = (agent_name,)
        else:
            query = 'SELECT * FROM predictions'
            params = ()
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        predictions = cursor.fetchall()
        
        cursor.execute('SELECT * FROM learning_metrics')
        metrics = cursor.fetchall()
        
        conn.close()
        
        return {
            'predictions': predictions,
            'metrics': metrics,
            'export_timestamp': datetime.now().isoformat(),
            'total_predictions': len(predictions)
        }

# Create global instance
learning_system = SelfLearningSystem()