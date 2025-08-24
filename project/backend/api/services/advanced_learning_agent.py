#!/usr/bin/env python3
"""
Advanced Self-Learning Agent with Historical Pattern Integration
Combines real-time learning with historical pattern analysis for maximum accuracy
"""

import logging
import uuid
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

from src.services.learning_agent import SelfLearningAgent, AnalysisPrediction, MarketOutcome
from src.services.historical_pattern_database import (
    HistoricalPatternDatabase, HistoricalPattern, TimeFrame, Direction,
    TopPattern, PatternStatistics
)
from src.services.cryptometer_data_types import CryptometerAnalysis, EndpointScore

logger = logging.getLogger(__name__)

class AdvancedLearningAgent(SelfLearningAgent):
    """
    Advanced Learning Agent that combines real-time learning with historical patterns
    """
    
    def __init__(self, learning_db_path: str = "learning_data.db", historical_db_path: str = "historical_patterns.db"):
        """Initialize Advanced Learning Agent with historical pattern integration"""
        super().__init__(learning_db_path)
        
        # Initialize historical pattern database
        self.historical_db = HistoricalPatternDatabase(historical_db_path)
        
        # Timeframe mappings
        self.timeframe_hours = {
            TimeFrame.H24_48: 36,  # Average of 24-48h
            TimeFrame.DAYS_7: 168,  # 7 days in hours
            TimeFrame.MONTH_1: 720  # 30 days in hours
        }
        
        logger.info("Advanced Learning Agent initialized with historical pattern integration")
    
    async def store_analysis_with_historical_context(self, analysis: CryptometerAnalysis, store_prediction: bool = True) -> str:
        """
        Store analysis with historical context and return prediction ID
        """
        prediction_id = str(uuid.uuid4())
        
        # Store standard prediction
        if store_prediction:
            prediction = AnalysisPrediction(
                id=prediction_id,
                symbol=analysis.symbol,
                timestamp=datetime.now(),
                predicted_direction=analysis.signal,  # Use signal instead of direction
                predicted_score=analysis.total_score,  # Use total_score instead of calibrated_score
                confidence=analysis.confidence,
                endpoint_scores={es.endpoint_name: es.score for es in analysis.endpoint_scores if es.confidence > 0.5},  # Use endpoint_name and confidence check
                patterns_identified=[],  # EndpointScore doesn't have patterns attribute
                recommendations=["Historical analysis integrated", "Multi-timeframe validation applied"],
                price_at_prediction=None  # Will be fetched separately
            )
            
            self.store_prediction(prediction)
        
        # Store endpoint data for historical analysis
        await self._store_endpoint_historical_data(analysis)
        
        # Schedule multi-timeframe validation
        for timeframe in TimeFrame:
            delay_hours = self.timeframe_hours[timeframe]
            asyncio.create_task(
                self._schedule_historical_validation(prediction_id, analysis, timeframe, delay_hours * 3600)
            )
        
        logger.info(f"Stored analysis with historical context for {analysis.symbol}, prediction ID: {prediction_id}")
        return prediction_id
    
    async def _store_endpoint_historical_data(self, analysis: CryptometerAnalysis):
        """Store endpoint performance data for historical tracking"""
        for endpoint_score in analysis.endpoint_scores:
            if endpoint_score.confidence > 0.5:  # Use confidence check instead of success
                # Update endpoint historical performance
                await self._update_endpoint_historical_performance(
                    endpoint_score.endpoint_name,  # Use endpoint_name instead of endpoint
                    analysis.symbol,
                    endpoint_score.score,
                    []  # EndpointScore doesn't have patterns attribute
                )
    
    async def _update_endpoint_historical_performance(self, endpoint_name: str, symbol: str, score: float, patterns: List[str]):
        """Update historical performance tracking for an endpoint"""
        import sqlite3
        
        conn = sqlite3.connect(self.historical_db.db_path)
        cursor = conn.cursor()
        
        for timeframe in TimeFrame:
            for direction in Direction:
                # Check if record exists
                cursor.execute('''
                    SELECT total_predictions, successful_predictions, avg_accuracy_score, weight_multiplier
                    FROM endpoint_historical_performance
                    WHERE endpoint_name = ? AND symbol = ? AND timeframe = ? AND direction = ?
                ''', (endpoint_name, symbol, timeframe.value, direction.value))
                
                result = cursor.fetchone()
                
                if result:
                    total_pred, successful_pred, avg_accuracy, weight_mult = result
                    
                    # Update with exponential moving average
                    total_pred += 1
                    if score > 50:  # Consider scores > 50 as successful
                        successful_pred += 1
                    
                    alpha = 0.1
                    avg_accuracy = (1 - alpha) * avg_accuracy + alpha * (score / 100.0)
                    
                    win_rate = successful_pred / total_pred
                    reliability_score = min(1.0, (total_pred / 50.0) * win_rate)
                    
                    # Adjust weight multiplier based on performance
                    if win_rate > 0.7:
                        weight_mult = min(2.0, weight_mult * 1.02)
                    elif win_rate < 0.3:
                        weight_mult = max(0.5, weight_mult * 0.98)
                    
                    cursor.execute('''
                        UPDATE endpoint_historical_performance
                        SET total_predictions = ?, successful_predictions = ?, win_rate = ?,
                            avg_accuracy_score = ?, reliability_score = ?, weight_multiplier = ?,
                            last_updated = ?
                        WHERE endpoint_name = ? AND symbol = ? AND timeframe = ? AND direction = ?
                    ''', (
                        total_pred, successful_pred, win_rate, avg_accuracy, reliability_score,
                        weight_mult, datetime.now().isoformat(),
                        endpoint_name, symbol, timeframe.value, direction.value
                    ))
                else:
                    # Create new record
                    win_rate = 1.0 if score > 50 else 0.0
                    cursor.execute('''
                        INSERT INTO endpoint_historical_performance
                        (id, endpoint_name, symbol, timeframe, direction, total_predictions,
                         successful_predictions, win_rate, avg_accuracy_score, reliability_score,
                         weight_multiplier, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        f"{endpoint_name}_{symbol}_{timeframe.value}_{direction.value}",
                        endpoint_name, symbol, timeframe.value, direction.value,
                        1, 1 if score > 50 else 0, win_rate, score / 100.0,
                        0.02, 1.0, datetime.now().isoformat()
                    ))
        
        conn.commit()
        conn.close()
    
    async def _schedule_historical_validation(self, prediction_id: str, analysis: CryptometerAnalysis, 
                                            timeframe: TimeFrame, delay_seconds: int):
        """Schedule historical pattern validation for a specific timeframe"""
        await asyncio.sleep(delay_seconds)
        
        try:
            # Get price at prediction and current price
            price_at_prediction = await self._get_price_at_time(analysis.symbol, datetime.now() - timedelta(seconds=delay_seconds))
            current_price = await self._get_current_price(analysis.symbol)
            
            if price_at_prediction and current_price:
                # Calculate price change
                price_change = ((current_price - price_at_prediction) / price_at_prediction) * 100
                
                # Determine outcome
                if abs(price_change) < 1:
                    final_outcome = 'BREAKEVEN'
                    win_rate_score = 0.5
                elif (analysis.signal == 'LONG' and price_change > 0) or (analysis.signal == 'SHORT' and price_change < 0):  # Use signal instead of direction
                    final_outcome = 'WIN'
                    win_rate_score = min(1.0, abs(price_change) / 10.0)  # Scale based on profit
                else:
                    final_outcome = 'LOSS'
                    win_rate_score = max(0.0, 1.0 - abs(price_change) / 10.0)  # Scale based on loss
                
                # Create historical pattern
                historical_pattern = HistoricalPattern(
                    id=f"{prediction_id}_{timeframe.value}",
                    symbol=analysis.symbol,
                    timestamp=datetime.now() - timedelta(seconds=delay_seconds),
                    direction=Direction(analysis.signal),  # Use signal instead of direction
                    timeframe=timeframe,
                    endpoint_scores={es.endpoint_name: es.score for es in analysis.endpoint_scores if es.confidence > 0.5},
                    endpoint_patterns={},  # EndpointScore doesn't have patterns
                    price_at_entry=price_at_prediction,
                    volume_data={},  # Could be enhanced with volume data
                    market_conditions={},  # Could be enhanced with market conditions
                    price_changes={timeframe.value: price_change},
                    max_profit=max(0, price_change) if analysis.signal == 'LONG' else max(0, -price_change),
                    max_drawdown=min(0, price_change) if analysis.signal == 'LONG' else min(0, -price_change),
                    final_outcome=final_outcome,
                    win_rate_score=win_rate_score,
                    confidence_at_entry=analysis.confidence,
                    patterns_identified=[],  # EndpointScore doesn't have patterns,
                    trigger_conditions=self._extract_trigger_conditions(analysis)
                )
                
                # Store historical pattern
                self.historical_db.store_historical_pattern(historical_pattern)
                
                logger.info(f"Stored historical pattern for {analysis.symbol} {timeframe.value} with outcome {final_outcome}")
        
        except Exception as e:
            logger.error(f"Error in historical validation for {prediction_id} {timeframe.value}: {e}")
    
    def _extract_trigger_conditions(self, analysis: CryptometerAnalysis) -> Dict[str, Any]:
        """Extract trigger conditions from analysis"""
        return {
            'calibrated_score': analysis.total_score,  # Use total_score instead of calibrated_score
            'confidence': analysis.confidence,
            'successful_endpoints': len([es for es in analysis.endpoint_scores if es.confidence > 0.5]),  # Use confidence check
            'total_endpoints': len(analysis.endpoint_scores),
            'direction': analysis.signal,  # Use signal instead of direction
            'endpoint_scores': {es.endpoint_name: es.score for es in analysis.endpoint_scores if es.confidence > 0.5}  # Use endpoint_name and confidence
        }
    
    async def _get_price_at_time(self, symbol: str, timestamp: datetime) -> Optional[float]:
        """Get price at a specific time (placeholder - would integrate with price API)"""
        # This would integrate with a historical price API
        # For now, return a placeholder
        return None
    
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price (placeholder - would integrate with price API)"""
        # This would integrate with a real-time price API
        # For now, return a placeholder
        return None
    
    def get_historical_enhanced_weights(self, symbol: str, endpoint_scores: Dict[str, float], 
                                      direction: str, timeframe: TimeFrame) -> Dict[str, float]:
        """Get weights enhanced by historical pattern analysis"""
        # Get base adaptive weights
        base_weights = self.get_adaptive_weights(symbol, endpoint_scores)
        
        # Get historical weights from pattern database
        historical_weights = self._get_historical_endpoint_weights(symbol, direction, timeframe)
        
        # Combine weights (70% historical, 30% adaptive)
        enhanced_weights = {}
        for endpoint, base_weight in base_weights.items():
            historical_weight = historical_weights.get(endpoint, 1.0)
            enhanced_weight = 0.7 * historical_weight + 0.3 * base_weight
            enhanced_weights[endpoint] = enhanced_weight
        
        # Normalize weights
        total_weight = sum(enhanced_weights.values())
        if total_weight > 0:
            enhanced_weights = {k: v / total_weight for k, v in enhanced_weights.items()}
        
        return enhanced_weights
    
    def _get_historical_endpoint_weights(self, symbol: str, direction: str, timeframe: TimeFrame) -> Dict[str, float]:
        """Get endpoint weights based on historical performance"""
        import sqlite3
        
        conn = sqlite3.connect(self.historical_db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT endpoint_name, weight_multiplier FROM endpoint_historical_performance
            WHERE symbol = ? AND direction = ? AND timeframe = ?
        ''', (symbol, direction, timeframe.value))
        
        weights = dict(cursor.fetchall())
        conn.close()
        
        return weights
    
    def get_pattern_probability_analysis(self, symbol: str, patterns: List[str], 
                                       direction: str, timeframe: TimeFrame) -> Dict[str, Any]:
        """Get comprehensive probability analysis based on historical patterns"""
        direction_enum = Direction(direction)
        
        # Get top patterns for this combination
        top_patterns = self.historical_db.get_top_patterns(symbol, direction_enum, timeframe)
        
        # Calculate probability scores for current patterns
        probability_scores = []
        matching_patterns = []
        
        for pattern in patterns:
            prob_score = self.historical_db.get_pattern_probability_score(
                symbol, [pattern], direction_enum, timeframe
            )
            if prob_score > 0.5:  # Only include patterns with above-average probability
                probability_scores.append(prob_score)
                matching_patterns.append(pattern)
        
        # Calculate overall probability
        if probability_scores:
            overall_probability = float(np.mean(probability_scores))
            confidence_level = min(1.0, len(matching_patterns) / 5.0)  # Higher confidence with more matching patterns
        else:
            overall_probability = 0.5  # Neutral
            confidence_level = 0.1
        
        return {
            'overall_probability': overall_probability,
            'confidence_level': confidence_level,
            'matching_patterns': matching_patterns,
            'pattern_scores': dict(zip(matching_patterns, probability_scores)),
            'top_historical_patterns': [
                {
                    'rank': tp.rank,
                    'pattern': tp.pattern_signature,
                    'win_rate': tp.win_rate,
                    'probability_score': tp.probability_score,
                    'total_trades': tp.total_trades,
                    'confidence_rating': tp.confidence_rating
                }
                for tp in top_patterns[:5]
            ],
            'recommendation': self._get_probability_recommendation(overall_probability, confidence_level)
        }
    
    def _get_probability_recommendation(self, probability: float, confidence: float) -> str:
        """Get trading recommendation based on probability and confidence"""
        if confidence < 0.3:
            return "INSUFFICIENT_DATA - Collect more historical patterns"
        elif probability >= 0.8 and confidence >= 0.7:
            return "STRONG_BUY/SELL - High probability with good confidence"
        elif probability >= 0.7 and confidence >= 0.5:
            return "MODERATE_BUY/SELL - Good probability with moderate confidence"
        elif probability >= 0.6:
            return "WEAK_BUY/SELL - Above average probability"
        elif probability <= 0.4 and confidence >= 0.5:
            return "AVOID - Below average probability with good confidence"
        else:
            return "NEUTRAL - Probability near random"
    
    def get_comprehensive_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive analysis combining real-time learning and historical patterns"""
        # Get base learning summary
        learning_summary = self.get_learning_summary()
        
        # Get historical analysis
        historical_analysis = self.historical_db.get_historical_analysis(symbol)
        
        # Combine analyses
        comprehensive_analysis = {
            'symbol': symbol,
            'learning_status': learning_summary,
            'historical_analysis': historical_analysis,
            'combined_insights': self._generate_combined_insights(learning_summary, historical_analysis),
            'reliability_assessment': self._assess_combined_reliability(learning_summary, historical_analysis),
            'trading_recommendations': self._generate_trading_recommendations(symbol, historical_analysis)
        }
        
        return comprehensive_analysis
    
    def _generate_combined_insights(self, learning_summary: Dict[str, Any], historical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights by combining learning and historical data"""
        return {
            'data_maturity': historical_analysis['overall_statistics']['data_maturity'],
            'learning_experience': learning_summary['learning_progress']['total_patterns_learned'],
            'combined_confidence': (
                learning_summary['learning_progress']['average_success_rate'] * 0.4 +
                historical_analysis['overall_statistics']['overall_win_rate'] * 0.6
            ),
            'recommendation': "Use both real-time learning and historical patterns for best results"
        }
    
    def _assess_combined_reliability(self, learning_summary: Dict[str, Any], historical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess combined reliability of learning and historical data"""
        learning_reliability = learning_summary['learning_progress']['average_success_rate']
        historical_reliability = historical_analysis['reliability_assessment']['reliability_score']
        
        combined_reliability = (learning_reliability * 0.4) + (historical_reliability * 0.6)
        
        return {
            'combined_reliability_score': combined_reliability,
            'assessment': 'HIGH' if combined_reliability > 0.7 else 'MEDIUM' if combined_reliability > 0.5 else 'LOW',
            'recommendation': 'Reliable for trading decisions' if combined_reliability > 0.6 else 'Use with additional analysis'
        }
    
    def _generate_trading_recommendations(self, symbol: str, historical_analysis: Dict[str, Any]) -> List[str]:
        """Generate trading recommendations based on historical analysis"""
        recommendations = []
        
        for timeframe_name, timeframe_data in historical_analysis['timeframes'].items():
            long_patterns = timeframe_data['long_patterns']
            short_patterns = timeframe_data['short_patterns']
            
            if long_patterns and long_patterns[0].win_rate > 0.7:
                recommendations.append(f"Strong LONG signals for {timeframe_name} timeframe (win rate: {long_patterns[0].win_rate:.1%})")
            
            if short_patterns and short_patterns[0].win_rate > 0.7:
                recommendations.append(f"Strong SHORT signals for {timeframe_name} timeframe (win rate: {short_patterns[0].win_rate:.1%})")
        
        if not recommendations:
            recommendations.append("No strong historical patterns found - use additional analysis")
        
        return recommendations
    
    def get_database_status(self) -> Dict[str, Any]:
        """Get status of both learning and historical databases"""
        learning_status = self.get_learning_summary()
        historical_stats = self.historical_db.get_database_stats()
        
        return {
            'learning_database': learning_status,
            'historical_database': historical_stats,
            'combined_status': {
                'total_data_points': (
                    learning_status.get('learning_database_size', {}).get('predictions', 0) +
                    historical_stats.get('historical_patterns_count', 0)
                ),
                'symbols_tracked': historical_stats.get('symbols_tracked', 0),
                'maturity_level': 'ADVANCED' if historical_stats.get('historical_patterns_count', 0) > 100 else 'DEVELOPING'
            }
        }