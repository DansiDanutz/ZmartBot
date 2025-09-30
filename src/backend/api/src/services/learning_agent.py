#!/usr/bin/env python3
"""
Self-Learning AI Analysis Agent
Continuously improves analysis quality by learning from past predictions and market outcomes
"""

import json
import sqlite3
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import pickle

from src.config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class AnalysisPrediction:
    """Stores an analysis prediction for later validation"""
    id: str
    symbol: str
    timestamp: datetime
    predicted_direction: str  # 'LONG', 'SHORT', 'NEUTRAL'
    predicted_score: float
    confidence: float
    endpoint_scores: Dict[str, float]
    patterns_identified: List[str]
    recommendations: List[str]
    price_at_prediction: Optional[float] = None
    
@dataclass
class MarketOutcome:
    """Stores actual market outcome for validation"""
    prediction_id: str
    symbol: str
    price_changes: Dict[str, float]  # '1h', '4h', '24h', '7d'
    actual_direction: str
    outcome_timestamp: datetime
    accuracy_score: float  # 0.0 to 1.0
    
@dataclass
class LearningInsight:
    """Stores learned insights from analysis patterns"""
    pattern_type: str
    success_rate: float
    avg_accuracy: float
    best_timeframes: List[str]
    common_conditions: Dict[str, Any]
    weight_adjustment: float
    confidence_multiplier: float
    last_updated: datetime

class SelfLearningAgent:
    """
    Self-Learning AI Agent that improves analysis quality over time
    """
    
    def __init__(self, learning_db_path: str = "learning_data.db"):
        """Initialize the Self-Learning Agent"""
        self.db_path = learning_db_path
        self.learning_insights: Dict[str, LearningInsight] = {}
        self.endpoint_performance: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.pattern_library: Dict[str, Dict[str, Any]] = {}
        
        # Initialize database
        self._init_database()
        
        # Load existing learning data
        self._load_learning_data()
        
        logger.info("SelfLearningAgent initialized with learning database")
    
    def _init_database(self):
        """Initialize SQLite database for learning data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id TEXT PRIMARY KEY,
                symbol TEXT,
                timestamp TEXT,
                predicted_direction TEXT,
                predicted_score REAL,
                confidence REAL,
                endpoint_scores TEXT,
                patterns_identified TEXT,
                recommendations TEXT,
                price_at_prediction REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outcomes (
                prediction_id TEXT,
                symbol TEXT,
                price_changes TEXT,
                actual_direction TEXT,
                outcome_timestamp TEXT,
                accuracy_score REAL,
                FOREIGN KEY (prediction_id) REFERENCES predictions (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_insights (
                pattern_type TEXT PRIMARY KEY,
                success_rate REAL,
                avg_accuracy REAL,
                best_timeframes TEXT,
                common_conditions TEXT,
                weight_adjustment REAL,
                confidence_multiplier REAL,
                last_updated TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS endpoint_performance (
                endpoint_name TEXT,
                symbol TEXT,
                avg_accuracy REAL,
                success_count INTEGER,
                total_count INTEGER,
                weight_multiplier REAL,
                last_updated TEXT,
                PRIMARY KEY (endpoint_name, symbol)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Learning database initialized")
    
    def _load_learning_data(self):
        """Load existing learning data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load learning insights
        cursor.execute('SELECT * FROM learning_insights')
        for row in cursor.fetchall():
            pattern_type, success_rate, avg_accuracy, best_timeframes, common_conditions, weight_adj, conf_mult, last_updated = row
            
            self.learning_insights[pattern_type] = LearningInsight(
                pattern_type=pattern_type,
                success_rate=success_rate,
                avg_accuracy=avg_accuracy,
                best_timeframes=json.loads(best_timeframes),
                common_conditions=json.loads(common_conditions),
                weight_adjustment=weight_adj,
                confidence_multiplier=conf_mult,
                last_updated=datetime.fromisoformat(last_updated)
            )
        
        # Load endpoint performance
        cursor.execute('SELECT * FROM endpoint_performance')
        for row in cursor.fetchall():
            endpoint_name, symbol, avg_accuracy, success_count, total_count, weight_mult, last_updated = row
            
            if endpoint_name not in self.endpoint_performance:
                self.endpoint_performance[endpoint_name] = {}
            
            self.endpoint_performance[endpoint_name][symbol] = {
                'avg_accuracy': avg_accuracy,
                'success_count': success_count,
                'total_count': total_count,
                'weight_multiplier': weight_mult,
                'last_updated': last_updated
            }
        
        conn.close()
        logger.info(f"Loaded {len(self.learning_insights)} learning insights and endpoint performance data")
    
    def store_prediction(self, prediction: AnalysisPrediction):
        """Store a prediction for later validation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO predictions 
            (id, symbol, timestamp, predicted_direction, predicted_score, confidence, 
             endpoint_scores, patterns_identified, recommendations, price_at_prediction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction.id,
            prediction.symbol,
            prediction.timestamp.isoformat(),
            prediction.predicted_direction,
            prediction.predicted_score,
            prediction.confidence,
            json.dumps(prediction.endpoint_scores),
            json.dumps(prediction.patterns_identified),
            json.dumps(prediction.recommendations),
            prediction.price_at_prediction
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Stored prediction {prediction.id} for {prediction.symbol}")
    
    def validate_prediction(self, outcome: MarketOutcome):
        """Validate a prediction against actual market outcome and learn from it"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store the outcome
        cursor.execute('''
            INSERT INTO outcomes 
            (prediction_id, symbol, price_changes, actual_direction, outcome_timestamp, accuracy_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            outcome.prediction_id,
            outcome.symbol,
            json.dumps(outcome.price_changes),
            outcome.actual_direction,
            outcome.outcome_timestamp.isoformat(),
            outcome.accuracy_score
        ))
        
        # Get the original prediction
        cursor.execute('SELECT * FROM predictions WHERE id = ?', (outcome.prediction_id,))
        prediction_row = cursor.fetchone()
        
        if prediction_row:
            # Extract prediction data
            _, symbol, timestamp, predicted_direction, predicted_score, confidence, endpoint_scores_json, patterns_json, _, _ = prediction_row
            
            endpoint_scores = json.loads(endpoint_scores_json)
            patterns = json.loads(patterns_json)
            
            # Update learning insights
            self._update_learning_insights(patterns, outcome.accuracy_score, outcome.actual_direction)
            
            # Update endpoint performance
            self._update_endpoint_performance(endpoint_scores, outcome.accuracy_score, symbol)
            
            # Learn from prediction patterns
            self._learn_from_prediction_outcome(
                predicted_direction, predicted_score, confidence,
                outcome.actual_direction, outcome.accuracy_score, patterns
            )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Validated prediction {outcome.prediction_id} with accuracy {outcome.accuracy_score:.3f}")
    
    def _update_learning_insights(self, patterns: List[str], accuracy: float, actual_direction: str):
        """Update learning insights based on pattern performance"""
        for pattern in patterns:
            if pattern in self.learning_insights:
                insight = self.learning_insights[pattern]
                
                # Update success rate using exponential moving average
                alpha = 0.1  # Learning rate
                insight.success_rate = (1 - alpha) * insight.success_rate + alpha * accuracy
                insight.avg_accuracy = (1 - alpha) * insight.avg_accuracy + alpha * accuracy
                
                # Adjust weight based on performance
                if accuracy > 0.7:
                    insight.weight_adjustment = min(2.0, insight.weight_adjustment * 1.05)
                elif accuracy < 0.3:
                    insight.weight_adjustment = max(0.5, insight.weight_adjustment * 0.95)
                
                # Adjust confidence multiplier
                if accuracy > 0.8:
                    insight.confidence_multiplier = min(1.5, insight.confidence_multiplier * 1.02)
                elif accuracy < 0.2:
                    insight.confidence_multiplier = max(0.7, insight.confidence_multiplier * 0.98)
                
                insight.last_updated = datetime.now()
            else:
                # Create new insight
                self.learning_insights[pattern] = LearningInsight(
                    pattern_type=pattern,
                    success_rate=accuracy,
                    avg_accuracy=accuracy,
                    best_timeframes=['24h'],  # Default
                    common_conditions={},
                    weight_adjustment=1.0,
                    confidence_multiplier=1.0,
                    last_updated=datetime.now()
                )
        
        # Save insights to database
        self._save_learning_insights()
    
    def _update_endpoint_performance(self, endpoint_scores: Dict[str, float], accuracy: float, symbol: str):
        """Update endpoint performance tracking"""
        for endpoint_name, score in endpoint_scores.items():
            if endpoint_name not in self.endpoint_performance:
                self.endpoint_performance[endpoint_name] = {}
            
            if symbol not in self.endpoint_performance[endpoint_name]:
                self.endpoint_performance[endpoint_name][symbol] = {
                    'avg_accuracy': accuracy,
                    'success_count': 1 if accuracy > 0.5 else 0,
                    'total_count': 1,
                    'weight_multiplier': 1.0,
                    'last_updated': datetime.now().isoformat()
                }
            else:
                perf = self.endpoint_performance[endpoint_name][symbol]
                
                # Update with exponential moving average
                alpha = 0.15
                perf['avg_accuracy'] = (1 - alpha) * perf['avg_accuracy'] + alpha * accuracy
                perf['total_count'] += 1
                
                if accuracy > 0.5:
                    perf['success_count'] += 1
                
                # Adjust weight multiplier based on performance
                if perf['avg_accuracy'] > 0.7:
                    perf['weight_multiplier'] = min(1.5, perf['weight_multiplier'] * 1.03)
                elif perf['avg_accuracy'] < 0.3:
                    perf['weight_multiplier'] = max(0.6, perf['weight_multiplier'] * 0.97)
                
                perf['last_updated'] = datetime.now().isoformat()
        
        # Save to database
        self._save_endpoint_performance()
    
    def _learn_from_prediction_outcome(self, predicted_direction: str, predicted_score: float, 
                                     confidence: float, actual_direction: str, accuracy: float, patterns: List[str]):
        """Learn from the relationship between predictions and outcomes"""
        
        # Create pattern combinations for learning
        pattern_combinations = []
        for i in range(len(patterns)):
            for j in range(i + 1, len(patterns)):
                pattern_combinations.append(f"{patterns[i]}+{patterns[j]}")
        
        # Learn from direction accuracy
        direction_key = f"direction_{predicted_direction.lower()}"
        direction_accuracy = 1.0 if predicted_direction == actual_direction else 0.0
        
        if direction_key not in self.pattern_library:
            self.pattern_library[direction_key] = {
                'success_rate': direction_accuracy,
                'total_predictions': 1,
                'score_correlation': predicted_score,
                'confidence_correlation': confidence
            }
        else:
            lib = self.pattern_library[direction_key]
            lib['total_predictions'] += 1
            alpha = 0.1
            lib['success_rate'] = (1 - alpha) * lib['success_rate'] + alpha * direction_accuracy
            lib['score_correlation'] = (1 - alpha) * lib['score_correlation'] + alpha * predicted_score
            lib['confidence_correlation'] = (1 - alpha) * lib['confidence_correlation'] + alpha * confidence
        
        logger.debug(f"Updated learning from prediction: {predicted_direction} -> {actual_direction} (accuracy: {accuracy:.3f})")
    
    def get_adaptive_weights(self, symbol: str, endpoint_scores: Dict[str, float]) -> Dict[str, float]:
        """Get adaptive weights based on learned endpoint performance"""
        adaptive_weights = {}
        
        for endpoint_name, original_score in endpoint_scores.items():
            base_weight = 1.0
            
            # Apply learned weight multiplier if available
            if (endpoint_name in self.endpoint_performance and 
                symbol in self.endpoint_performance[endpoint_name]):
                
                perf = self.endpoint_performance[endpoint_name][symbol]
                weight_multiplier = perf['weight_multiplier']
                
                # Consider accuracy in weight adjustment
                accuracy_factor = max(0.5, min(1.5, perf['avg_accuracy'] * 2))
                base_weight = weight_multiplier * accuracy_factor
            
            adaptive_weights[endpoint_name] = base_weight
        
        # Normalize weights
        total_weight = sum(adaptive_weights.values())
        if total_weight > 0:
            adaptive_weights = {k: v / total_weight for k, v in adaptive_weights.items()}
        
        return adaptive_weights
    
    def get_enhanced_confidence(self, patterns: List[str], base_confidence: float) -> float:
        """Get enhanced confidence based on learned pattern performance"""
        confidence_multipliers = []
        
        for pattern in patterns:
            if pattern in self.learning_insights:
                insight = self.learning_insights[pattern]
                confidence_multipliers.append(insight.confidence_multiplier)
        
        if confidence_multipliers:
            avg_multiplier = float(np.mean(confidence_multipliers))
            enhanced_confidence = base_confidence * avg_multiplier
            return float(min(0.95, max(0.05, enhanced_confidence)))
        
        return base_confidence
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning progress and insights"""
        total_insights = len(self.learning_insights)
        avg_success_rate = float(np.mean([insight.success_rate for insight in self.learning_insights.values()])) if total_insights > 0 else 0.0
        
        # Get top performing patterns
        top_patterns = sorted(
            self.learning_insights.items(),
            key=lambda x: x[1].success_rate,
            reverse=True
        )[:5]
        
        # Get endpoint performance summary
        endpoint_summary = {}
        for endpoint_name, symbols in self.endpoint_performance.items():
            avg_accuracy = float(np.mean([data['avg_accuracy'] for data in symbols.values()]))
            total_predictions = sum([data['total_count'] for data in symbols.values()])
            
            endpoint_summary[endpoint_name] = {
                'avg_accuracy': avg_accuracy,
                'total_predictions': total_predictions,
                'symbols_tracked': len(symbols)
            }
        
        return {
            'learning_progress': {
                'total_patterns_learned': total_insights,
                'average_success_rate': avg_success_rate,
                'endpoints_tracked': len(self.endpoint_performance)
            },
            'top_performing_patterns': [
                {
                    'pattern': pattern,
                    'success_rate': insight.success_rate,
                    'weight_adjustment': insight.weight_adjustment,
                    'confidence_multiplier': insight.confidence_multiplier
                }
                for pattern, insight in top_patterns
            ],
            'endpoint_performance': endpoint_summary,
            'learning_database_size': self._get_database_size()
        }
    
    def _save_learning_insights(self):
        """Save learning insights to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pattern_type, insight in self.learning_insights.items():
            cursor.execute('''
                INSERT OR REPLACE INTO learning_insights 
                (pattern_type, success_rate, avg_accuracy, best_timeframes, common_conditions, 
                 weight_adjustment, confidence_multiplier, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern_type,
                insight.success_rate,
                insight.avg_accuracy,
                json.dumps(insight.best_timeframes),
                json.dumps(insight.common_conditions),
                insight.weight_adjustment,
                insight.confidence_multiplier,
                insight.last_updated.isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def _save_endpoint_performance(self):
        """Save endpoint performance to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for endpoint_name, symbols in self.endpoint_performance.items():
            for symbol, perf in symbols.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO endpoint_performance 
                    (endpoint_name, symbol, avg_accuracy, success_count, total_count, weight_multiplier, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    endpoint_name, symbol, perf['avg_accuracy'], perf['success_count'],
                    perf['total_count'], perf['weight_multiplier'], perf['last_updated']
                ))
        
        conn.commit()
        conn.close()
    
    def _get_database_size(self) -> Dict[str, int]:
        """Get database size statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sizes = {}
        for table in ['predictions', 'outcomes', 'learning_insights', 'endpoint_performance']:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            sizes[table] = cursor.fetchone()[0]
        
        conn.close()
        return sizes