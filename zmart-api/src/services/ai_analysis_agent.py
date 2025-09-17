#!/usr/bin/env python3
"""
AI-Powered Technical Analysis Report Generator
Uses ChatGPT-4 Mini to generate comprehensive technical analysis reports based on Cryptometer endpoint data
"""

import openai
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import json

from src.config.settings import settings
from src.services.cryptometer_data_types import CryptometerEndpointAnalyzer, CryptometerAnalysis

logger = logging.getLogger(__name__)

@dataclass
class AnalysisReport:
    """AI-generated technical analysis report"""
    symbol: str
    report_content: str
    summary: str
    recommendations: List[str]
    risk_factors: List[str]
    confidence_score: float
    timestamp: datetime
    word_count: int

class AIAnalysisAgent:
    """
    AI-Powered Technical Analysis Agent
    Generates comprehensive technical analysis reports using ChatGPT-4 Mini
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the AI Analysis Agent"""
        self.openai_api_key = openai_api_key or settings.OPENAI_API_KEY
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for AI analysis")
        
        # Initialize OpenAI client
        openai.api_key = self.openai_api_key
        try:
            self.client = openai.OpenAI(api_key=self.openai_api_key)
        except TypeError:
            # Fallback for older OpenAI library versions
            self.client = None
        
        # Initialize Cryptometer analyzer
        self.cryptometer_analyzer = CryptometerEndpointAnalyzer()
        
        logger.info("AIAnalysisAgent initialized with ChatGPT-4 Mini")
    
    async def generate_comprehensive_report(self, symbol: str) -> AnalysisReport:
        """
        Generate a comprehensive technical analysis report for a symbol
        """
        logger.info(f"Generating comprehensive AI analysis report for {symbol}")
        
        # Step 1: Get Cryptometer endpoint analysis
        cryptometer_analysis = await self.cryptometer_analyzer.analyze_symbol(symbol)  # Use analyze_symbol instead
        
        # Step 2: Prepare data for AI analysis
        analysis_data = self._prepare_analysis_data(cryptometer_analysis)
        
        # Step 3: Generate AI report
        report_content = await self._generate_ai_report(symbol, analysis_data)
        
        # Step 4: Extract key components
        summary, recommendations, risk_factors = self._extract_report_components(report_content)
        
        # Step 5: Calculate confidence score
        confidence_score = self._calculate_confidence_score(cryptometer_analysis)
        
        # Step 6: Count words
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
        
        logger.info(f"Generated {word_count} word analysis report for {symbol} with {confidence_score:.1f}% confidence")
        return report
    
    def _prepare_analysis_data(self, analysis: CryptometerAnalysis) -> Dict[str, Any]:
        """Prepare endpoint data for AI analysis"""
        
        # Organize endpoint data by category
        endpoint_data = {
            'market_data': [],
            'volume_analysis': [],
            'liquidation_data': [],
            'sentiment_indicators': [],
            'technical_indicators': [],
            'whale_activity': []
        }
        
        # Categorize endpoints
        for endpoint_score in analysis.endpoint_scores:
            endpoint_name = endpoint_score.endpoint_name  # Use endpoint_name
            data = {
                'name': endpoint_name,
                'score': endpoint_score.score,
                'confidence': endpoint_score.confidence,
                'weight': endpoint_score.weight,  # Use weight instead of analysis
                'data': endpoint_score.data,  # Use data instead of patterns
                'success': endpoint_score.confidence > 0.5  # Calculate success from confidence
            }
            
            # Categorize by endpoint type
            if endpoint_name in ['ticker', 'ohlcv', 'cryptocurrency_info', 'coin_info']:
                endpoint_data['market_data'].append(data)
            elif endpoint_name in ['24h_trade_volume_v2', 'tickerlist', 'tickerlist_pro']:
                endpoint_data['volume_analysis'].append(data)
            elif endpoint_name in ['liquidation_data_v2', 'ls_ratio']:
                endpoint_data['liquidation_data'].append(data)
            elif endpoint_name in ['ai_screener', 'ai_screener_analysis', 'trend_indicator_v3']:
                endpoint_data['sentiment_indicators'].append(data)
            elif endpoint_name in ['rapid_movements', 'forex_rates']:
                endpoint_data['technical_indicators'].append(data)
            elif endpoint_name in ['large_trades_activity', 'xtrades']:
                endpoint_data['whale_activity'].append(data)
        
        return {
            'symbol': analysis.symbol,
            'overall_score': analysis.total_score,  # Use total_score instead of calibrated_score
            'confidence': analysis.confidence,
            'direction': analysis.signal,  # Use signal instead of direction
            'summary': analysis.summary,  # Use summary instead of analysis_summary
            'endpoint_categories': endpoint_data,
            'successful_endpoints': len([es for es in analysis.endpoint_scores if es.confidence > 0.5]),  # Use confidence check
            'total_endpoints': len(analysis.endpoint_scores),
            'timestamp': analysis.timestamp.isoformat()
        }
    
    async def _generate_ai_report(self, symbol: str, analysis_data: Dict[str, Any]) -> str:
        """Generate AI-powered technical analysis report using ChatGPT-4 Mini"""
        
        # Create comprehensive prompt
        system_prompt = """You are a professional cryptocurrency technical analyst with expertise in market analysis and trading strategies. You will generate comprehensive technical analysis reports based on multi-endpoint market data.

Your reports should be:
- Professional and detailed (1000-1500 words)
- Based on factual data provided
- Include specific trading recommendations
- Assess risk factors comprehensively
- Use proper financial terminology
- Structure with clear sections and subheadings
- Include specific price levels and percentages when relevant"""

        user_prompt = f"""Generate a comprehensive technical analysis report for {symbol}/USDT based on the following Cryptometer API endpoint analysis:

OVERALL ANALYSIS:
- Final Score: {analysis_data['overall_score']:.1f}%
- Confidence: {analysis_data['confidence']:.2f}
- Direction: {analysis_data['direction']}
- Successful Endpoints: {analysis_data['successful_endpoints']}/{analysis_data['total_endpoints']}

ENDPOINT ANALYSIS BY CATEGORY:

MARKET DATA:
{json.dumps(analysis_data['endpoint_categories']['market_data'], indent=2)}

VOLUME ANALYSIS:
{json.dumps(analysis_data['endpoint_categories']['volume_analysis'], indent=2)}

LIQUIDATION DATA:
{json.dumps(analysis_data['endpoint_categories']['liquidation_data'], indent=2)}

SENTIMENT INDICATORS:
{json.dumps(analysis_data['endpoint_categories']['sentiment_indicators'], indent=2)}

TECHNICAL INDICATORS:
{json.dumps(analysis_data['endpoint_categories']['technical_indicators'], indent=2)}

WHALE ACTIVITY:
{json.dumps(analysis_data['endpoint_categories']['whale_activity'], indent=2)}

Please structure your report with the following sections:
1. Executive Summary
2. Current Market Conditions
3. Technical Analysis Breakdown
4. Volume and Liquidity Assessment
5. Sentiment and Positioning Analysis
6. Risk Assessment
7. Trading Recommendations
8. Conclusion

Focus on actionable insights and specific trading guidance. The report should be 1000-1500 words and professional in tone."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # ChatGPT-4 Mini
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            report_content = response.choices[0].message.content
            if not report_content:
                raise ValueError("OpenAI returned empty response")
            
            logger.info(f"Successfully generated AI report for {symbol}")
            return report_content
            
        except Exception as e:
            logger.error(f"Error generating AI report for {symbol}: {e}")
            # Fallback to template-based report
            return self._generate_fallback_report(symbol, analysis_data)
    
    def _generate_fallback_report(self, symbol: str, analysis_data: Dict[str, Any]) -> str:
        """Generate fallback report if AI fails"""
        
        return f"""# {symbol}/USDT Technical Analysis Report

## Executive Summary

Based on comprehensive analysis of {analysis_data['successful_endpoints']} out of {analysis_data['total_endpoints']} Cryptometer API endpoints, {symbol}/USDT shows a calibrated score of {analysis_data['overall_score']:.1f}% with {analysis_data['direction'].lower()} market sentiment.

## Current Market Conditions

The analysis indicates {analysis_data['direction'].lower()} market conditions with a confidence level of {analysis_data['confidence']:.2f}. Multiple endpoint analysis reveals mixed signals across different market indicators.

## Technical Analysis Breakdown

Market data endpoints show varying performance levels, with price action and volume indicators providing key insights into current market structure.

## Risk Assessment

Current market conditions present moderate risk levels. Traders should implement appropriate risk management strategies.

## Trading Recommendations

Based on the {analysis_data['overall_score']:.1f}% overall score, consider conservative position sizing and strict risk management protocols.

## Conclusion

The analysis suggests a cautious approach to {symbol}/USDT trading given current market conditions.

*Note: This is a fallback report. Full AI analysis temporarily unavailable.*"""
    
    def _extract_report_components(self, report_content: str) -> tuple[str, List[str], List[str]]:
        """Extract summary, recommendations, and risk factors from report"""
        
        lines = report_content.split('\n')
        
        # Extract summary (first few sentences)
        summary_lines = []
        for line in lines:
            if line.strip() and not line.startswith('#'):
                summary_lines.append(line.strip())
                if len(' '.join(summary_lines)) > 200:
                    break
        summary = ' '.join(summary_lines)[:300] + "..."
        
        # Extract recommendations (look for recommendation sections)
        recommendations = []
        in_recommendations = False
        for line in lines:
            if 'recommendation' in line.lower() or 'trading' in line.lower():
                in_recommendations = True
            elif in_recommendations and line.strip().startswith('-'):
                recommendations.append(line.strip()[1:].strip())
            elif in_recommendations and line.strip().startswith('#'):
                in_recommendations = False
        
        # Extract risk factors
        risk_factors = []
        in_risk = False
        for line in lines:
            if 'risk' in line.lower():
                in_risk = True
            elif in_risk and line.strip().startswith('-'):
                risk_factors.append(line.strip()[1:].strip())
            elif in_risk and line.strip().startswith('#'):
                in_risk = False
        
        return summary, recommendations, risk_factors
    
    def _calculate_confidence_score(self, analysis: CryptometerAnalysis) -> float:
        """Calculate confidence score based on analysis quality"""
        
        # Base confidence from endpoint coverage
        coverage_confidence = (len([es for es in analysis.endpoint_scores if es.confidence > 0.5]) / 
                             len(analysis.endpoint_scores)) * 100  # Use confidence check instead of success
        
        # Adjust based on overall analysis confidence
        analysis_confidence = analysis.confidence * 100
        
        # Combined confidence (weighted average)
        final_confidence = (coverage_confidence * 0.6) + (analysis_confidence * 0.4)
        
        return min(95.0, max(20.0, final_confidence))