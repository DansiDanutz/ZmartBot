#!/usr/bin/env python3
"""
Self-Learning Cryptometer Agent
Advanced ML agent that learns from historical cryptometer data to improve predictions
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
from collections import defaultdict, deque
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LearningMetrics:
    """Learning performance metrics"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    prediction_count: int
    last_updated: datetime

@dataclass
class PatternInsight:
    """Pattern learning insights"""
    pattern_type: str
    timeframe: str
    success_rate: float
    confidence_threshold: float
    market_conditions: Dict[str, Any]
    sample_size: int

class SelfLearningCryptometerAgent:
    """
    Self-learning agent that improves cryptometer predictions through historical analysis

    Features:
    - Pattern success rate learning
    - Market condition adaptation
    - Prediction accuracy tracking
    - Dynamic confidence adjustment
    - Historical performance analysis
    """

    def __init__(self, db_path: str = "data/self_learning_cryptometer.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)

        # Learning parameters
        self.learning_window_days = 30
        self.min_sample_size = 10
        self.confidence_threshold = 0.7

        # Pattern tracking
        self.pattern_history = defaultdict(list)
        self.prediction_history = deque(maxlen=1000)
        self.market_condition_weights = {}

        # Performance metrics
        self.learning_metrics = LearningMetrics(
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            prediction_count=0,
            last_updated=datetime.now()
        )

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for learning data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS prediction_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        predicted_score REAL NOT NULL,
                        actual_outcome REAL,
                        prediction_timestamp TIMESTAMP NOT NULL,
                        outcome_timestamp TIMESTAMP,
                        market_conditions TEXT,
                        pattern_type TEXT,
                        confidence_score REAL,
                        success BOOLEAN
                    )
                ''')

                conn.execute('''
                    CREATE TABLE IF NOT EXISTS pattern_insights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_type TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        success_rate REAL NOT NULL,
                        confidence_threshold REAL NOT NULL,
                        market_conditions TEXT,
                        sample_size INTEGER NOT NULL,
                        last_updated TIMESTAMP NOT NULL,
                        UNIQUE(pattern_type, timeframe)
                    )
                ''')

                conn.execute('''
                    CREATE TABLE IF NOT EXISTS learning_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        accuracy REAL NOT NULL,
                        precision REAL NOT NULL,
                        recall REAL NOT NULL,
                        f1_score REAL NOT NULL,
                        prediction_count INTEGER NOT NULL,
                        timestamp TIMESTAMP NOT NULL
                    )
                ''')

                logger.info("✅ Self-learning database initialized")

        except Exception as e:
            logger.error(f"❌ Error initializing database: {e}")

    async def learn_from_prediction(self, symbol: str, timeframe: str,
                                  predicted_score: float, actual_outcome: float,
                                  pattern_type: str, market_conditions: Dict[str, Any]) -> bool:
        """
        Learn from a prediction result to improve future accuracy
        """
        try:
            prediction_success = self._evaluate_prediction_success(predicted_score, actual_outcome)

            # Store prediction history
            await self._store_prediction_result(
                symbol, timeframe, predicted_score, actual_outcome,
                pattern_type, market_conditions, prediction_success
            )

            # Update pattern insights
            await self._update_pattern_insights(pattern_type, timeframe, prediction_success, market_conditions)

            # Update learning metrics
            await self._update_learning_metrics()

            logger.info(f"📚 Learned from {symbol} {timeframe} prediction: {'✅' if prediction_success else '❌'}")
            return True

        except Exception as e:
            logger.error(f"❌ Error learning from prediction: {e}")
            return False

    def _evaluate_prediction_success(self, predicted_score: float, actual_outcome: float) -> bool:
        """Evaluate if a prediction was successful based on thresholds"""
        # Define success criteria based on score ranges
        if predicted_score >= 80:  # High confidence prediction
            return actual_outcome >= 70  # Should achieve at least 70% of target
        elif predicted_score >= 60:  # Medium confidence
            return actual_outcome >= 50
        else:  # Low confidence
            return actual_outcome >= 30

    async def _store_prediction_result(self, symbol: str, timeframe: str, predicted_score: float,
                                     actual_outcome: float, pattern_type: str,
                                     market_conditions: Dict[str, Any], success: bool):
        """Store prediction result in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO prediction_history
                    (symbol, timeframe, predicted_score, actual_outcome, prediction_timestamp,
                     outcome_timestamp, market_conditions, pattern_type, confidence_score, success)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, timeframe, predicted_score, actual_outcome,
                    datetime.now().isoformat(), datetime.now().isoformat(),
                    json.dumps(market_conditions), pattern_type,
                    predicted_score / 100.0, success
                ))

        except Exception as e:
            logger.error(f"❌ Error storing prediction result: {e}")

    async def _update_pattern_insights(self, pattern_type: str, timeframe: str,
                                     success: bool, market_conditions: Dict[str, Any]):
        """Update pattern success rates and insights"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get current pattern data
                cursor = conn.execute('''
                    SELECT success_rate, sample_size FROM pattern_insights
                    WHERE pattern_type = ? AND timeframe = ?
                ''', (pattern_type, timeframe))

                result = cursor.fetchone()

                if result:
                    # Update existing pattern
                    current_success_rate, sample_size = result
                    new_sample_size = sample_size + 1
                    new_success_rate = ((current_success_rate * sample_size) + (1 if success else 0)) / new_sample_size

                    conn.execute('''
                        UPDATE pattern_insights
                        SET success_rate = ?, sample_size = ?, last_updated = ?
                        WHERE pattern_type = ? AND timeframe = ?
                    ''', (new_success_rate, new_sample_size, datetime.now().isoformat(), pattern_type, timeframe))
                else:
                    # Create new pattern insight
                    conn.execute('''
                        INSERT INTO pattern_insights
                        (pattern_type, timeframe, success_rate, confidence_threshold,
                         market_conditions, sample_size, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        pattern_type, timeframe, 1.0 if success else 0.0, self.confidence_threshold,
                        json.dumps(market_conditions), 1, datetime.now().isoformat()
                    ))

        except Exception as e:
            logger.error(f"❌ Error updating pattern insights: {e}")

    async def _update_learning_metrics(self):
        """Update overall learning performance metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Calculate metrics from recent predictions
                cursor = conn.execute('''
                    SELECT predicted_score, actual_outcome, success
                    FROM prediction_history
                    WHERE prediction_timestamp > ?
                    ORDER BY prediction_timestamp DESC
                    LIMIT 100
                ''', ((datetime.now() - timedelta(days=self.learning_window_days)).isoformat(),))

                results = cursor.fetchall()

                if len(results) >= self.min_sample_size:
                    predictions = [(r[0], r[1], r[2]) for r in results]

                    # Calculate accuracy
                    correct_predictions = sum(1 for _, _, success in predictions if success)
                    accuracy = correct_predictions / len(predictions)

                    # Calculate precision, recall, F1 (binary classification)
                    true_positives = sum(1 for pred, actual, success in predictions
                                       if pred >= 70 and success)
                    false_positives = sum(1 for pred, actual, success in predictions
                                        if pred >= 70 and not success)
                    false_negatives = sum(1 for pred, actual, success in predictions
                                        if pred < 70 and success)

                    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
                    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
                    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

                    # Update metrics
                    self.learning_metrics = LearningMetrics(
                        accuracy=accuracy,
                        precision=precision,
                        recall=recall,
                        f1_score=f1_score,
                        prediction_count=len(predictions),
                        last_updated=datetime.now()
                    )

                    # Store in database
                    conn.execute('''
                        INSERT INTO learning_metrics
                        (accuracy, precision, recall, f1_score, prediction_count, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (accuracy, precision, recall, f1_score, len(predictions), datetime.now().isoformat()))

                    logger.info(f"📊 Learning metrics updated: Accuracy={accuracy:.3f}, F1={f1_score:.3f}")

        except Exception as e:
            logger.error(f"❌ Error updating learning metrics: {e}")

    async def get_pattern_confidence(self, pattern_type: str, timeframe: str) -> float:
        """Get learned confidence for a specific pattern type and timeframe"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT success_rate, sample_size FROM pattern_insights
                    WHERE pattern_type = ? AND timeframe = ?
                ''', (pattern_type, timeframe))

                result = cursor.fetchone()

                if result and result[1] >= self.min_sample_size:
                    success_rate, sample_size = result
                    # Adjust confidence based on sample size
                    confidence = success_rate * min(1.0, sample_size / 50.0)
                    return confidence

                # Default confidence for new patterns
                return 0.5

        except Exception as e:
            logger.error(f"❌ Error getting pattern confidence: {e}")
            return 0.5

    async def enhance_prediction(self, original_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance a cryptometer prediction using learned insights
        """
        try:
            symbol = original_prediction.get('symbol', '')
            timeframe_data = {}

            # Enhance each timeframe prediction
            for timeframe in ['short_term', 'medium_term', 'long_term']:
                tf_data = original_prediction.get(timeframe, {})
                if tf_data:
                    enhanced_data = await self._enhance_timeframe_prediction(tf_data, timeframe)
                    timeframe_data[timeframe] = enhanced_data

            # Create enhanced prediction
            enhanced_prediction = {
                **original_prediction,
                **timeframe_data,
                'enhanced_by_learning': True,
                'learning_metrics': asdict(self.learning_metrics),
                'enhancement_timestamp': datetime.now().isoformat()
            }

            logger.info(f"🧠 Enhanced prediction for {symbol} using learned insights")
            return enhanced_prediction

        except Exception as e:
            logger.error(f"❌ Error enhancing prediction: {e}")
            return original_prediction

    async def _enhance_timeframe_prediction(self, timeframe_data: Dict[str, Any], timeframe: str) -> Dict[str, Any]:
        """Enhance prediction for a specific timeframe"""
        try:
            patterns = timeframe_data.get('patterns', [])
            enhanced_patterns = []

            for pattern in patterns:
                pattern_type = pattern.get('type', '')

                # Get learned confidence for this pattern
                learned_confidence = await self.get_pattern_confidence(pattern_type, timeframe)

                # Adjust pattern confidence based on learning
                original_confidence = pattern.get('confidence', 0.5)
                enhanced_confidence = (original_confidence + learned_confidence) / 2

                enhanced_pattern = {
                    **pattern,
                    'confidence': enhanced_confidence,
                    'learned_confidence': learned_confidence,
                    'original_confidence': original_confidence,
                    'enhanced': True
                }

                enhanced_patterns.append(enhanced_pattern)

            # Recalculate score based on enhanced patterns
            if enhanced_patterns:
                enhanced_score = self._recalculate_score(enhanced_patterns)
            else:
                enhanced_score = timeframe_data.get('score', 0)

            return {
                **timeframe_data,
                'patterns': enhanced_patterns,
                'score': enhanced_score,
                'original_score': timeframe_data.get('score', 0),
                'enhancement_applied': True
            }

        except Exception as e:
            logger.error(f"❌ Error enhancing timeframe prediction: {e}")
            return timeframe_data

    def _recalculate_score(self, enhanced_patterns: List[Dict[str, Any]]) -> float:
        """Recalculate score based on enhanced pattern confidences"""
        if not enhanced_patterns:
            return 0

        total_weighted_score = 0
        total_weight = 0

        for pattern in enhanced_patterns:
            confidence = pattern.get('confidence', 0.5)
            weight = confidence
            score_contribution = confidence * 100  # Convert to 0-100 scale

            total_weighted_score += score_contribution * weight
            total_weight += weight

        if total_weight > 0:
            return min(100, total_weighted_score / total_weight)
        return 0

    async def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status and metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get total predictions
                cursor = conn.execute('SELECT COUNT(*) FROM prediction_history')
                total_predictions = cursor.fetchone()[0]

                # Get pattern insights count
                cursor = conn.execute('SELECT COUNT(*) FROM pattern_insights')
                pattern_insights_count = cursor.fetchone()[0]

                # Get recent success rate
                cursor = conn.execute('''
                    SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END)
                    FROM prediction_history
                    WHERE prediction_timestamp > ?
                ''', ((datetime.now() - timedelta(days=7)).isoformat(),))

                recent_success_rate = cursor.fetchone()[0] or 0

            return {
                'status': 'active',
                'learning_metrics': asdict(self.learning_metrics),
                'total_predictions': total_predictions,
                'pattern_insights_count': pattern_insights_count,
                'recent_success_rate': recent_success_rate,
                'learning_window_days': self.learning_window_days,
                'min_sample_size': self.min_sample_size,
                'database_path': str(self.db_path),
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error getting learning status: {e}")
            return {'status': 'error', 'error': str(e)}

# Global instance
_self_learning_agent = None

def get_self_learning_agent() -> SelfLearningCryptometerAgent:
    """Get or create the self-learning agent instance"""
    global _self_learning_agent
    if _self_learning_agent is None:
        _self_learning_agent = SelfLearningCryptometerAgent()
    return _self_learning_agent

async def enhance_cryptometer_prediction(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to enhance a cryptometer prediction with learning
    """
    agent = get_self_learning_agent()
    return await agent.enhance_prediction(prediction)

async def learn_from_cryptometer_result(symbol: str, timeframe: str, predicted_score: float,
                                      actual_outcome: float, pattern_type: str,
                                      market_conditions: Dict[str, Any]) -> bool:
    """
    Convenience function to feed learning data to the agent
    """
    agent = get_self_learning_agent()
    return await agent.learn_from_prediction(
        symbol, timeframe, predicted_score, actual_outcome, pattern_type, market_conditions
    )