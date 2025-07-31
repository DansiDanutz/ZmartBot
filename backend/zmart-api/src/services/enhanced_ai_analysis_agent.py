#!/usr/bin/env python3
"""
Enhanced Self-Learning AI Analysis Agent
Integrates self-learning capabilities with AI report generation for continuous improvement
"""

import openai
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import requests
import asyncio

from src.config.settings import settings
from src.services.ai_analysis_agent import AIAnalysisAgent, AnalysisReport
from src.services.learning_agent import SelfLearningAgent, AnalysisPrediction, MarketOutcome
from src.services.cryptometer_endpoint_analyzer import CryptometerAnalysis

logger = logging.getLogger(__name__)

class EnhancedAIAnalysisAgent(AIAnalysisAgent):
    """
    Enhanced AI Analysis Agent with Self-Learning Capabilities
    Continuously improves analysis quality by learning from past predictions
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, learning_db_path: str = "learning_data.db"):
        """Initialize the Enhanced AI Analysis Agent with learning capabilities"""
        super().__init__(openai_api_key)
        
        # Initialize learning agent
        self.learning_agent = SelfLearningAgent(learning_db_path)
        
        # Price tracking for validation
        self.price_cache: Dict[str, Dict[str, float]] = {}
        
        logger.info("EnhancedAIAnalysisAgent initialized with self-learning capabilities")
    
    async def generate_learning_enhanced_report(self, symbol: str, store_prediction: bool = True) -> AnalysisReport:
        """
        Generate analysis report enhanced by learning from past performance
        """
        logger.info(f"Generating learning-enhanced AI analysis report for {symbol}")
        
        # Step 1: Get base Cryptometer analysis
        cryptometer_analysis = await self.cryptometer_analyzer.analyze_symbol_complete(symbol)
        
        # Step 2: Apply learning enhancements
        enhanced_analysis = await self._apply_learning_enhancements(cryptometer_analysis)
        
        # Step 3: Prepare enhanced data for AI
        analysis_data = self._prepare_enhanced_analysis_data(enhanced_analysis, cryptometer_analysis)
        
        # Step 4: Generate AI report with learning context
        report_content = await self._generate_learning_enhanced_report(symbol, analysis_data)
        
        # Step 5: Extract components and create report
        summary, recommendations, risk_factors = self._extract_report_components(report_content)
        confidence_score = self._calculate_enhanced_confidence_score(enhanced_analysis, cryptometer_analysis)
        word_count = len(report_content.split())
        
        report = AnalysisReport(
            symbol=symbol,
            report_content=report_content,
            summary=summary,
            recommendations=recommendations,
            risk_factors=risk_factors,
            confidence_score=confidence_score,
            timestamp=datetime.now(),
            word_count=word_count
        )
        
        # Step 6: Store prediction for learning (if enabled)
        if store_prediction:
            await self._store_prediction_for_learning(report, enhanced_analysis, cryptometer_analysis)
        
        logger.info(f"Generated learning-enhanced {word_count} word report for {symbol} with {confidence_score:.1f}% confidence")
        return report
    
    async def _apply_learning_enhancements(self, analysis: CryptometerAnalysis) -> Dict[str, Any]:
        """Apply learning enhancements to the analysis"""
        
        # Get endpoint scores
        endpoint_scores = {es.endpoint: es.score for es in analysis.endpoint_scores if es.success}
        
        # Get adaptive weights from learning
        adaptive_weights = self.learning_agent.get_adaptive_weights(analysis.symbol, endpoint_scores)
        
        # Apply adaptive weights to recalculate score
        enhanced_score = 0.0
        total_weight = 0.0
        
        for endpoint, score in endpoint_scores.items():
            weight = adaptive_weights.get(endpoint, 1.0)
            enhanced_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            enhanced_score = enhanced_score / total_weight
        else:
            enhanced_score = analysis.calibrated_score
        
        # Collect patterns for learning enhancement
        all_patterns = []
        for es in analysis.endpoint_scores:
            all_patterns.extend(es.patterns)
        
        # Get enhanced confidence
        enhanced_confidence = self.learning_agent.get_enhanced_confidence(all_patterns, analysis.confidence)
        
        return {
            'original_score': analysis.calibrated_score,
            'enhanced_score': enhanced_score,
            'original_confidence': analysis.confidence,
            'enhanced_confidence': enhanced_confidence,
            'adaptive_weights': adaptive_weights,
            'patterns': all_patterns,
            'learning_insights': self._get_relevant_learning_insights(all_patterns)
        }
    
    def _get_relevant_learning_insights(self, patterns: List[str]) -> Dict[str, Any]:
        """Get relevant learning insights for current patterns"""
        insights = {}
        
        for pattern in patterns:
            if pattern in self.learning_agent.learning_insights:
                insight = self.learning_agent.learning_insights[pattern]
                insights[pattern] = {
                    'success_rate': insight.success_rate,
                    'weight_adjustment': insight.weight_adjustment,
                    'confidence_multiplier': insight.confidence_multiplier,
                    'avg_accuracy': insight.avg_accuracy
                }
        
        return insights
    
    def _prepare_enhanced_analysis_data(self, enhanced_analysis: Dict[str, Any], original_analysis: CryptometerAnalysis) -> Dict[str, Any]:
        """Prepare enhanced analysis data for AI generation"""
        
        # Get base data
        base_data = self._prepare_analysis_data(original_analysis)
        
        # Add learning enhancements
        base_data.update({
            'learning_enhancements': {
                'original_score': enhanced_analysis['original_score'],
                'enhanced_score': enhanced_analysis['enhanced_score'],
                'score_improvement': enhanced_analysis['enhanced_score'] - enhanced_analysis['original_score'],
                'confidence_enhancement': enhanced_analysis['enhanced_confidence'] - enhanced_analysis['original_confidence'],
                'adaptive_weights_applied': len(enhanced_analysis['adaptive_weights']),
                'learning_insights_count': len(enhanced_analysis['learning_insights'])
            },
            'learning_insights': enhanced_analysis['learning_insights'],
            'adaptive_weights': enhanced_analysis['adaptive_weights'],
            'patterns_with_history': enhanced_analysis['patterns']
        })
        
        # Add learning summary
        learning_summary = self.learning_agent.get_learning_summary()
        base_data['learning_context'] = {
            'total_patterns_learned': learning_summary['learning_progress']['total_patterns_learned'],
            'average_success_rate': learning_summary['learning_progress']['average_success_rate'],
            'analysis_experience_level': self._calculate_experience_level(learning_summary)
        }
        
        return base_data
    
    def _calculate_experience_level(self, learning_summary: Dict[str, Any]) -> str:
        """Calculate the AI's experience level based on learning data"""
        total_patterns = learning_summary['learning_progress']['total_patterns_learned']
        avg_success = learning_summary['learning_progress']['average_success_rate']
        
        if total_patterns < 10:
            return "NOVICE"
        elif total_patterns < 50:
            return "LEARNING"
        elif total_patterns < 200:
            return "EXPERIENCED"
        elif avg_success > 0.7:
            return "EXPERT"
        else:
            return "ADVANCED"
    
    async def _generate_learning_enhanced_report(self, symbol: str, analysis_data: Dict[str, Any]) -> str:
        """Generate AI report with learning context"""
        
        # Enhanced system prompt that includes learning context
        system_prompt = f"""You are a professional cryptocurrency technical analyst with advanced self-learning capabilities. You have analyzed {analysis_data['learning_context']['total_patterns_learned']} patterns with an average success rate of {analysis_data['learning_context']['average_success_rate']:.1%}.

Your analysis experience level: {analysis_data['learning_context']['analysis_experience_level']}

You continuously learn from past predictions and improve your analysis quality. Your reports should:
- Be professional and detailed (1000-1500 words)
- Incorporate learning insights from past performance
- Mention confidence levels based on historical accuracy
- Highlight patterns that have shown strong performance
- Include adaptive scoring based on endpoint performance
- Provide specific trading recommendations with risk management
- Reference your learning experience when relevant

Your current analysis benefits from:
- Adaptive endpoint weighting based on {analysis_data['learning_enhancements']['adaptive_weights_applied']} learned performance metrics
- {analysis_data['learning_enhancements']['learning_insights_count']} pattern insights from historical data
- Score enhancement of {analysis_data['learning_enhancements']['score_improvement']:+.1f} points based on learning
- Confidence adjustment of {analysis_data['learning_enhancements']['confidence_enhancement']:+.3f} based on pattern history"""

        user_prompt = f"""Generate a comprehensive technical analysis report for {symbol}/USDT using your self-learning enhanced analysis:

ENHANCED ANALYSIS RESULTS:
- Original Score: {analysis_data['learning_enhancements']['original_score']:.1f}%
- Learning-Enhanced Score: {analysis_data['learning_enhancements']['enhanced_score']:.1f}%
- Score Improvement: {analysis_data['learning_enhancements']['score_improvement']:+.1f} points
- Confidence Enhancement: {analysis_data['learning_enhancements']['confidence_enhancement']:+.3f}

LEARNING INSIGHTS APPLIED:
{json.dumps(analysis_data['learning_insights'], indent=2)}

ADAPTIVE ENDPOINT WEIGHTS:
{json.dumps(analysis_data['adaptive_weights'], indent=2)}

CRYPTOMETER ENDPOINT ANALYSIS:
{json.dumps(analysis_data['endpoint_categories'], indent=2)}

LEARNING CONTEXT:
- Analysis Experience: {analysis_data['learning_context']['analysis_experience_level']}
- Patterns Learned: {analysis_data['learning_context']['total_patterns_learned']}
- Historical Success Rate: {analysis_data['learning_context']['average_success_rate']:.1%}

Please structure your report with:
1. Executive Summary (mention learning enhancements)
2. Learning-Enhanced Market Analysis
3. Adaptive Endpoint Performance Review
4. Pattern Recognition Insights
5. Historical Performance Context
6. Risk Assessment with Learning Adjustments
7. Trading Recommendations (confidence-weighted)
8. Learning-Based Confidence Assessment

Focus on how your learning experience enhances this specific analysis and mention specific insights from historical pattern performance."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2800,
                temperature=0.6,  # Slightly lower for more consistent learning-based analysis
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            report_content = response.choices[0].message.content
            if not report_content:
                raise ValueError("OpenAI returned empty response")
            
            logger.info(f"Successfully generated learning-enhanced AI report for {symbol}")
            return report_content
            
        except Exception as e:
            logger.error(f"Error generating learning-enhanced AI report for {symbol}: {e}")
            # Fallback to enhanced template
            return self._generate_enhanced_fallback_report(symbol, analysis_data)
    
    def _generate_enhanced_fallback_report(self, symbol: str, analysis_data: Dict[str, Any]) -> str:
        """Generate enhanced fallback report with learning context"""
        
        experience_level = analysis_data['learning_context']['analysis_experience_level']
        enhanced_score = analysis_data['learning_enhancements']['enhanced_score']
        score_improvement = analysis_data['learning_enhancements']['score_improvement']
        
        return f"""# {symbol}/USDT Learning-Enhanced Technical Analysis Report

## Executive Summary

Based on my self-learning analysis system with {analysis_data['learning_context']['analysis_experience_level'].lower()} experience level, {symbol}/USDT shows a learning-enhanced score of {enhanced_score:.1f}% (improved by {score_improvement:+.1f} points through adaptive learning).

## Learning-Enhanced Analysis

My analysis incorporates insights from {analysis_data['learning_context']['total_patterns_learned']} previously analyzed patterns with a historical success rate of {analysis_data['learning_context']['average_success_rate']:.1%}.

### Adaptive Enhancements Applied:
- Endpoint weight adjustments based on historical performance
- Pattern recognition improvements from past analysis outcomes
- Confidence calibration using learned accuracy metrics

## Current Market Assessment

The enhanced analysis indicates {analysis_data['direction'].lower()} market sentiment with improved confidence through learning-based adjustments.

## Learning-Based Recommendations

Based on historical pattern performance and adaptive scoring:
1. Position sizing should reflect the {enhanced_score:.1f}% confidence level
2. Risk management protocols enhanced by learning insights
3. Entry/exit strategies optimized through pattern recognition

## Confidence Assessment

This analysis benefits from {experience_level.lower()} level learning experience, providing enhanced reliability compared to standard analysis methods.

*Note: This analysis incorporates self-learning enhancements. Full AI analysis temporarily unavailable.*"""
    
    async def _store_prediction_for_learning(self, report: AnalysisReport, enhanced_analysis: Dict[str, Any], original_analysis: CryptometerAnalysis):
        """Store prediction for future learning validation"""
        
        # Get current price for validation tracking
        current_price = await self._get_current_price(report.symbol)
        
        # Create prediction record
        prediction = AnalysisPrediction(
            id=str(uuid.uuid4()),
            symbol=report.symbol,
            timestamp=report.timestamp,
            predicted_direction=original_analysis.direction,
            predicted_score=enhanced_analysis['enhanced_score'],
            confidence=enhanced_analysis['enhanced_confidence'],
            endpoint_scores={es.endpoint: es.score for es in original_analysis.endpoint_scores if es.success},
            patterns_identified=enhanced_analysis['patterns'],
            recommendations=report.recommendations,
            price_at_prediction=current_price
        )
        
        # Store prediction
        self.learning_agent.store_prediction(prediction)
        
        # Schedule validation check (in production, this would be handled by a background task)
        asyncio.create_task(self._schedule_prediction_validation(prediction.id, 24 * 3600))  # 24 hours
    
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for the symbol"""
        try:
            # Use a free API to get current price (example with CoinGecko)
            symbol_map = {'ETH': 'ethereum', 'BTC': 'bitcoin', 'ADA': 'cardano', 'SOL': 'solana'}
            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get(coin_id, {}).get('usd')
        except Exception as e:
            logger.warning(f"Could not fetch current price for {symbol}: {e}")
        
        return None
    
    async def _schedule_prediction_validation(self, prediction_id: str, delay_seconds: int):
        """Schedule prediction validation after a delay"""
        await asyncio.sleep(delay_seconds)
        
        try:
            # Get the original prediction
            import sqlite3
            conn = sqlite3.connect(self.learning_agent.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM predictions WHERE id = ?', (prediction_id,))
            prediction_row = cursor.fetchone()
            
            if prediction_row:
                _, symbol, timestamp_str, predicted_direction, predicted_score, confidence, _, _, _, price_at_prediction = prediction_row
                
                # Get current price
                current_price = await self._get_current_price(symbol)
                
                if current_price and price_at_prediction:
                    # Calculate price change
                    price_change = ((current_price - price_at_prediction) / price_at_prediction) * 100
                    
                    # Determine actual direction
                    if price_change > 2:
                        actual_direction = 'LONG'
                    elif price_change < -2:
                        actual_direction = 'SHORT'
                    else:
                        actual_direction = 'NEUTRAL'
                    
                    # Calculate accuracy
                    direction_accuracy = 1.0 if predicted_direction == actual_direction else 0.0
                    score_accuracy = max(0.0, 1.0 - abs(predicted_score - (50 + price_change)) / 50)
                    overall_accuracy = (direction_accuracy + score_accuracy) / 2
                    
                    # Create outcome
                    outcome = MarketOutcome(
                        prediction_id=prediction_id,
                        symbol=symbol,
                        price_changes={'24h': price_change},
                        actual_direction=actual_direction,
                        outcome_timestamp=datetime.now(),
                        accuracy_score=overall_accuracy
                    )
                    
                    # Validate and learn
                    self.learning_agent.validate_prediction(outcome)
                    
                    logger.info(f"Validated prediction {prediction_id} with accuracy {overall_accuracy:.3f}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error validating prediction {prediction_id}: {e}")
    
    def _calculate_enhanced_confidence_score(self, enhanced_analysis: Dict[str, Any], original_analysis: CryptometerAnalysis) -> float:
        """Calculate enhanced confidence score incorporating learning"""
        
        # Base confidence from original analysis
        base_confidence = self._calculate_confidence_score(original_analysis)
        
        # Apply learning enhancement
        enhanced_confidence = enhanced_analysis['enhanced_confidence'] * 100
        
        # Combine with learning context
        learning_summary = self.learning_agent.get_learning_summary()
        experience_factor = min(1.2, 1.0 + (learning_summary['learning_progress']['total_patterns_learned'] / 1000))
        
        final_confidence = (base_confidence * 0.6) + (enhanced_confidence * 0.4)
        final_confidence *= experience_factor
        
        return min(98.0, max(15.0, final_confidence))
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status and performance"""
        return self.learning_agent.get_learning_summary()