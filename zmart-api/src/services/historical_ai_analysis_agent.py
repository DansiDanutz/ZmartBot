#!/usr/bin/env python3
"""
Historical AI Analysis Agent
Advanced AI analysis with historical pattern integration and multi-timeframe win rate analysis
"""

import openai
import logging
import uuid
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from src.config.settings import settings
from src.services.enhanced_ai_analysis_agent import EnhancedAIAnalysisAgent
from src.services.advanced_learning_agent import AdvancedLearningAgent
from src.services.historical_pattern_database import TimeFrame, Direction
from src.services.cryptometer_data_types import CryptometerAnalysis

logger = logging.getLogger(__name__)

class HistoricalAIAnalysisAgent(EnhancedAIAnalysisAgent):
    """
    Historical AI Analysis Agent with comprehensive pattern analysis and win rate predictions
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize Historical AI Analysis Agent"""
        super().__init__(openai_api_key)
        
        # Initialize advanced learning agent with historical database
        self.advanced_learning_agent = AdvancedLearningAgent()
        
        logger.info("Historical AI Analysis Agent initialized")
    
    async def generate_historical_enhanced_report(self, symbol: str, store_prediction: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report with historical pattern integration
        """
        logger.info(f"Generating historical-enhanced AI analysis for {symbol}")
        
        # Step 1: Get base Cryptometer analysis
        cryptometer_analysis = await self.cryptometer_analyzer.analyze_symbol(symbol)
        
        # Step 2: Store analysis with historical context
        prediction_id = await self.advanced_learning_agent.store_analysis_with_historical_context(
            cryptometer_analysis, store_prediction
        )
        
        # Step 3: Get multi-timeframe historical analysis
        multi_timeframe_analysis = await self._get_multi_timeframe_analysis(symbol, cryptometer_analysis)
        
        # Step 4: Get comprehensive historical insights
        comprehensive_analysis = self.advanced_learning_agent.get_comprehensive_analysis(symbol)
        
        # Step 5: Generate AI report with historical context
        report_content = await self._generate_historical_ai_report(
            symbol, cryptometer_analysis, multi_timeframe_analysis, comprehensive_analysis
        )
        
        # Step 6: Calculate enhanced confidence with historical data
        enhanced_confidence = self._calculate_historical_confidence(
            cryptometer_analysis, multi_timeframe_analysis, comprehensive_analysis
        )
        
        return {
            'symbol': symbol,
            'prediction_id': prediction_id,
            'report_content': report_content,
            'confidence_score': enhanced_confidence,
            'word_count': len(report_content.split()),
            'timestamp': datetime.now().isoformat(),
            'cryptometer_analysis': {
                'calibrated_score': cryptometer_analysis.total_score,
                'direction': cryptometer_analysis.signal,
                'confidence': cryptometer_analysis.confidence,
                'successful_endpoints': len(cryptometer_analysis.endpoint_scores)
            },
            'multi_timeframe_analysis': multi_timeframe_analysis,
            'historical_insights': comprehensive_analysis,
            'analysis_type': 'historical_enhanced_ai_analysis'
        }
    
    async def _get_multi_timeframe_analysis(self, symbol: str, analysis: CryptometerAnalysis) -> Dict[str, Any]:
        """Get analysis for all supported timeframes"""
        multi_timeframe = {}
        
        # Extract patterns from endpoint data
        patterns = []
        for es in analysis.endpoint_scores:
            if 'patterns' in es.data:
                patterns.extend(es.data['patterns'])
            elif 'pattern' in es.data:
                patterns.append(es.data['pattern'])
        
        for timeframe in TimeFrame:
            for direction in Direction:
                if direction.value == analysis.signal or direction == Direction.NEUTRAL:
                    # Get probability analysis for this timeframe/direction
                    prob_analysis = self.advanced_learning_agent.get_pattern_probability_analysis(
                        symbol, patterns, direction.value, timeframe
                    )
                    
                    # Get historical weights
                    endpoint_scores = {es.endpoint_name: es.score for es in analysis.endpoint_scores if es.confidence > 0.5}
                    historical_weights = self.advanced_learning_agent.get_historical_enhanced_weights(
                        symbol, endpoint_scores, direction.value, timeframe
                    )
                    
                    multi_timeframe[f"{timeframe.value}_{direction.value}"] = {
                        'timeframe': timeframe.value,
                        'direction': direction.value,
                        'probability_analysis': prob_analysis,
                        'historical_weights': historical_weights,
                        'win_rate_prediction': prob_analysis['overall_probability'],
                        'confidence_level': prob_analysis['confidence_level'],
                        'recommendation': prob_analysis['recommendation']
                    }
        
        return multi_timeframe
    
    async def _generate_historical_ai_report(self, symbol: str, cryptometer_analysis: CryptometerAnalysis,
                                           multi_timeframe_analysis: Dict[str, Any], 
                                           comprehensive_analysis: Dict[str, Any]) -> str:
        """Generate AI report with comprehensive historical analysis"""
        
        # Prepare historical context for AI
        historical_context = self._prepare_historical_context(
            symbol, cryptometer_analysis, multi_timeframe_analysis, comprehensive_analysis
        )
        
        # Enhanced system prompt with historical capabilities
        system_prompt = f"""You are an advanced cryptocurrency technical analyst with access to comprehensive historical pattern databases and multi-timeframe analysis capabilities.

Your analysis capabilities include:
- Historical pattern recognition with win rate calculations
- Multi-timeframe analysis (24h-48h, 7 days, 1 month)
- Probability-based scoring from proven successful patterns
- Top 10 historical patterns for both LONG and SHORT positions
- Real-time learning integration with historical validation

Historical Database Status:
- Total Historical Patterns: {comprehensive_analysis['historical_analysis']['overall_statistics']['total_historical_patterns']}
- Overall Win Rate: {comprehensive_analysis['historical_analysis']['overall_statistics']['overall_win_rate']:.1%}
- Data Maturity: {comprehensive_analysis['historical_analysis']['overall_statistics']['data_maturity']}
- Reliability Assessment: {comprehensive_analysis['historical_analysis']['reliability_assessment']['assessment']}

Your reports should be professional, detailed (1200-1800 words), and include:
- Executive summary with historical context
- Multi-timeframe probability analysis
- Historical pattern validation
- Win rate predictions for different timeframes
- Risk assessment based on historical drawdowns
- Specific trading recommendations with probability scores"""

        user_prompt = f"""Generate a comprehensive historical-enhanced technical analysis report for {symbol}/USDT:

CURRENT CRYPTOMETER ANALYSIS:
- Calibrated Score: {cryptometer_analysis.total_score:.1f}%
- Direction: {cryptometer_analysis.signal}
- Confidence: {cryptometer_analysis.confidence:.3f}
- Successful Endpoints: {len(cryptometer_analysis.endpoint_scores)}/17

MULTI-TIMEFRAME HISTORICAL ANALYSIS:
{json.dumps(multi_timeframe_analysis, indent=2)}

HISTORICAL PATTERN INSIGHTS:
{json.dumps(historical_context, indent=2)}

COMPREHENSIVE ANALYSIS:
- Learning Experience: {comprehensive_analysis['learning_status']['learning_progress']['total_patterns_learned']} patterns
- Historical Reliability: {comprehensive_analysis['reliability_assessment']['combined_reliability_score']:.1%}
- Data Maturity: {comprehensive_analysis['historical_analysis']['overall_statistics']['data_maturity']}

Please structure your report with:
1. Executive Summary (include historical validation)
2. Multi-Timeframe Win Rate Analysis
   - 24h-48h Probability Assessment
   - 7-Day Pattern Analysis
   - 1-Month Historical Trends
3. Historical Pattern Validation
4. Top Performing Patterns Analysis
5. Probability-Based Risk Assessment
6. Trading Recommendations by Timeframe
7. Historical Confidence Assessment

Focus on specific win rate probabilities, historical pattern validation, and multi-timeframe trading strategies based on proven historical success."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=3200,
                temperature=0.5,  # Lower temperature for more consistent historical analysis
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            report_content = response.choices[0].message.content
            if not report_content:
                raise ValueError("OpenAI returned empty response")
            
            logger.info(f"Generated historical AI report for {symbol}")
            return report_content
            
        except Exception as e:
            logger.error(f"Error generating historical AI report for {symbol}: {e}")
            return self._generate_historical_fallback_report(symbol, multi_timeframe_analysis, comprehensive_analysis)
    
    def _prepare_historical_context(self, symbol: str, cryptometer_analysis: CryptometerAnalysis,
                                   multi_timeframe_analysis: Dict[str, Any], 
                                   comprehensive_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare historical context for AI analysis"""
        
        # Extract top patterns for each timeframe
        top_patterns_summary = {}
        
        for timeframe_name, timeframe_data in comprehensive_analysis['historical_analysis']['timeframes'].items():
            long_patterns = timeframe_data['long_patterns'][:3]  # Top 3
            short_patterns = timeframe_data['short_patterns'][:3]  # Top 3
            
            top_patterns_summary[timeframe_name] = {
                'top_long_patterns': [
                    {
                        'pattern': p.pattern_signature,
                        'win_rate': p.win_rate,
                        'total_trades': p.total_trades,
                        'avg_profit': p.avg_profit_percent,
                        'probability_score': p.probability_score,
                        'confidence_rating': p.confidence_rating
                    } for p in long_patterns
                ],
                'top_short_patterns': [
                    {
                        'pattern': p.pattern_signature,
                        'win_rate': p.win_rate,
                        'total_trades': p.total_trades,
                        'avg_profit': p.avg_profit_percent,
                        'probability_score': p.probability_score,
                        'confidence_rating': p.confidence_rating
                    } for p in short_patterns
                ]
            }
        
        return {
            'symbol_reliability': comprehensive_analysis['reliability_assessment'],
            'top_patterns_by_timeframe': top_patterns_summary,
            'overall_statistics': comprehensive_analysis['historical_analysis']['overall_statistics'],
            'trading_recommendations': comprehensive_analysis['trading_recommendations'],
            'combined_insights': comprehensive_analysis['combined_insights']
        }
    
    def _calculate_historical_confidence(self, cryptometer_analysis: CryptometerAnalysis,
                                       multi_timeframe_analysis: Dict[str, Any],
                                       comprehensive_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score enhanced by historical data"""
        
        # Base confidence from Cryptometer
        base_confidence = cryptometer_analysis.confidence * 100
        
        # Historical reliability factor
        historical_reliability = comprehensive_analysis['reliability_assessment']['combined_reliability_score']
        
        # Multi-timeframe confidence average
        timeframe_confidences = []
        for tf_key, tf_data in multi_timeframe_analysis.items():
            if tf_data['direction'] == cryptometer_analysis.signal:
                tf_confidence = tf_data['confidence_level'] * tf_data['win_rate_prediction']
                timeframe_confidences.append(tf_confidence)
        
        avg_timeframe_confidence = np.mean(timeframe_confidences) * 100 if timeframe_confidences else 50.0
        
        # Data maturity bonus
        data_maturity = comprehensive_analysis['historical_analysis']['overall_statistics']['data_maturity']
        maturity_bonus = {'HIGH': 10, 'MEDIUM': 5, 'LOW': 0, 'NONE': -10}.get(data_maturity, 0)
        
        # Calculate final confidence
        final_confidence = (
            base_confidence * 0.4 +  # 40% from current analysis
            (historical_reliability * 100) * 0.3 +  # 30% from historical reliability
            avg_timeframe_confidence * 0.3  # 30% from timeframe analysis
        ) + maturity_bonus
        
        return min(95.0, max(10.0, final_confidence))
    
    def _generate_historical_fallback_report(self, symbol: str, multi_timeframe_analysis: Dict[str, Any],
                                           comprehensive_analysis: Dict[str, Any]) -> str:
        """Generate fallback report with historical data"""
        
        reliability_score = comprehensive_analysis['reliability_assessment']['combined_reliability_score']
        data_maturity = comprehensive_analysis['historical_analysis']['overall_statistics']['data_maturity']
        
        # Get best timeframe analysis
        best_timeframe = None
        best_probability = 0.0
        
        for tf_key, tf_data in multi_timeframe_analysis.items():
            if tf_data['win_rate_prediction'] > best_probability:
                best_probability = tf_data['win_rate_prediction']
                best_timeframe = tf_data
        
        timeframe_name = best_timeframe['timeframe'] if best_timeframe else 'N/A'
        direction_name = best_timeframe['direction'] if best_timeframe else 'N/A'
        confidence_level = f"{best_timeframe['confidence_level']:.1%}" if best_timeframe else 'N/A'
        recommendation = best_timeframe['recommendation'] if best_timeframe else 'Insufficient data'
        
        return f"""# {symbol}/USDT Historical-Enhanced Technical Analysis Report

## Executive Summary

Based on comprehensive historical pattern analysis with {data_maturity.lower()} data maturity, {symbol}/USDT shows a combined reliability score of {reliability_score:.1%}.

## Multi-Timeframe Analysis

### Best Performing Timeframe: {timeframe_name}
- Win Rate Prediction: {best_probability:.1%}
- Direction: {direction_name}
- Confidence Level: {confidence_level}
- Recommendation: {recommendation}

## Historical Pattern Validation

The analysis incorporates {comprehensive_analysis['historical_analysis']['overall_statistics']['total_historical_patterns']} historical patterns with an overall win rate of {comprehensive_analysis['historical_analysis']['overall_statistics']['overall_win_rate']:.1%}.

## Risk Assessment

Historical data shows average profit of {comprehensive_analysis['historical_analysis']['overall_statistics']['avg_profit']:.2f}% and average loss of {comprehensive_analysis['historical_analysis']['overall_statistics']['avg_loss']:.2f}%.

## Trading Recommendations

{chr(10).join(comprehensive_analysis['trading_recommendations'])}

## Confidence Assessment

This analysis benefits from {data_maturity.lower()} historical data maturity with {reliability_score:.1%} combined reliability.

*Note: Full AI analysis temporarily unavailable. Historical pattern analysis active.*"""
    
    async def get_symbol_historical_summary(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive historical summary for a symbol"""
        comprehensive_analysis = self.advanced_learning_agent.get_comprehensive_analysis(symbol)
        database_status = self.advanced_learning_agent.get_database_status()
        
        return {
            'symbol': symbol,
            'historical_summary': comprehensive_analysis,
            'database_status': database_status,
            'timeframe_coverage': {
                '24h-48h': len(comprehensive_analysis['historical_analysis']['timeframes'].get('24h-48h', {}).get('long_patterns', [])),
                '7d': len(comprehensive_analysis['historical_analysis']['timeframes'].get('7d', {}).get('long_patterns', [])),
                '1m': len(comprehensive_analysis['historical_analysis']['timeframes'].get('1m', {}).get('long_patterns', []))
            },
            'reliability_assessment': comprehensive_analysis['reliability_assessment'],
            'recommendations': comprehensive_analysis['trading_recommendations']
        }
    
    async def get_top_patterns_analysis(self, symbol: str, direction: str = "LONG", timeframe: str = "7d") -> Dict[str, Any]:
        """Get detailed analysis of top patterns for specific parameters"""
        try:
            direction_enum = Direction(direction)
            timeframe_enum = TimeFrame(timeframe)
            
            top_patterns = self.advanced_learning_agent.historical_db.get_top_patterns(
                symbol, direction_enum, timeframe_enum
            )
            
            # Get current patterns from latest analysis
            current_analysis = await self.cryptometer_analyzer.analyze_symbol(symbol)
            # Extract patterns from endpoint data
            current_patterns = []
            for es in current_analysis.endpoint_scores:
                if 'patterns' in es.data:
                    current_patterns.extend(es.data['patterns'])
                elif 'pattern' in es.data:
                    current_patterns.append(es.data['pattern'])
            
            # Find matching patterns
            matching_patterns = []
            for pattern in top_patterns:
                if any(cp in pattern.pattern_signature for cp in current_patterns):
                    matching_patterns.append(pattern)
            
            return {
                'symbol': symbol,
                'direction': direction,
                'timeframe': timeframe,
                'top_patterns': [
                    {
                        'rank': p.rank,
                        'pattern': p.pattern_signature,
                        'win_rate': p.win_rate,
                        'total_trades': p.total_trades,
                        'avg_profit_percent': p.avg_profit_percent,
                        'probability_score': p.probability_score,
                        'confidence_rating': p.confidence_rating,
                        'last_success': p.last_success.isoformat()
                    } for p in top_patterns
                ],
                'matching_current_patterns': [
                    {
                        'rank': p.rank,
                        'pattern': p.pattern_signature,
                        'win_rate': p.win_rate,
                        'probability_score': p.probability_score
                    } for p in matching_patterns
                ],
                'analysis_recommendation': self._get_pattern_recommendation(matching_patterns)
            }
        
        except Exception as e:
            logger.error(f"Error getting top patterns analysis: {e}")
            return {'error': str(e)}
    
    def _get_pattern_recommendation(self, matching_patterns: List) -> str:
        """Get recommendation based on matching patterns"""
        if not matching_patterns:
            return "No historical patterns match current analysis - proceed with caution"
        
        avg_win_rate = np.mean([p.win_rate for p in matching_patterns])
        avg_probability = np.mean([p.probability_score for p in matching_patterns])
        
        if avg_win_rate >= 0.8 and avg_probability >= 0.7:
            return f"STRONG SIGNAL - {len(matching_patterns)} matching patterns with {avg_win_rate:.1%} avg win rate"
        elif avg_win_rate >= 0.6 and avg_probability >= 0.5:
            return f"MODERATE SIGNAL - {len(matching_patterns)} matching patterns with {avg_win_rate:.1%} avg win rate"
        else:
            return f"WEAK SIGNAL - {len(matching_patterns)} matching patterns with {avg_win_rate:.1%} avg win rate"