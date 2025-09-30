#!/usr/bin/env python3
"""
🎯 Cryptometer QA Agent
Ensures high-quality data delivery with AI-powered analysis and interpretation
Provides enterprise-grade data validation and enrichment for end users
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
from enum import Enum

# Import AI models for analysis
try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

# Import the enhanced Cryptometer service
from src.services.cryptometer_service import MultiTimeframeCryptometerSystem
from src.config.settings import settings

logger = logging.getLogger(__name__)

class DataQuality(Enum):
    """Data quality levels"""
    PREMIUM = "premium"      # Fresh API data with AI analysis
    STANDARD = "standard"    # Cached data with AI analysis
    BASIC = "basic"          # Fallback data with limited analysis
    INSUFFICIENT = "insufficient"  # Not enough data for analysis

class AnalysisDepth(Enum):
    """Analysis depth levels"""
    COMPREHENSIVE = "comprehensive"  # Full multi-model analysis
    DETAILED = "detailed"           # Single model deep analysis
    SUMMARY = "summary"            # Quick summary analysis
    BASIC = "basic"               # Basic interpretation

class CryptometerQAAgent:
    """
    QA Agent for Cryptometer data
    Ensures data quality and provides AI-powered interpretation
    """
    
    def __init__(self):
        """Initialize the QA Agent"""
        # Initialize Cryptometer service with caching
        api_key = settings.CRYPTOMETER_API_KEY if hasattr(settings, 'CRYPTOMETER_API_KEY') else "k77U187e08zGf4I3SLz3sYzTEyM2KNoJ9i1N4xg2"
        self.cryptometer = MultiTimeframeCryptometerSystem(api_key=api_key)
        
        # Initialize AI client for analysis
        self.ai_client = None
        if OpenAI and hasattr(settings, 'OPENAI_API_KEY'):
            try:
                self.ai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ AI analysis enabled with OpenAI")
            except Exception as e:
                logger.warning(f"⚠️ AI client initialization failed: {e}")
        
        # Quality thresholds
        self.quality_thresholds = {
            'min_endpoints': 5,        # Minimum endpoints for quality data
            'max_cache_age': 300,      # Maximum cache age for premium (5 min)
            'min_confidence': 0.7,     # Minimum confidence for recommendations
            'required_indicators': ['trend_indicator_v3', 'ls_ratio', 'ai_screener']
        }
        
        # Analysis templates for consistent output
        self.analysis_templates = {
            'market_overview': self._get_market_overview_template(),
            'trading_signals': self._get_trading_signals_template(),
            'risk_assessment': self._get_risk_assessment_template(),
            'technical_analysis': self._get_technical_analysis_template()
        }
        
        # Statistics tracking
        self.stats = {
            'total_requests': 0,
            'premium_deliveries': 0,
            'standard_deliveries': 0,
            'basic_deliveries': 0,
            'ai_analyses': 0,
            'cache_hits': 0
        }
        
        logger.info("🎯 Cryptometer QA Agent initialized")
    
    async def get_quality_data(
        self,
        symbol: str,
        analysis_depth: AnalysisDepth = AnalysisDepth.DETAILED,
        required_quality: DataQuality = DataQuality.STANDARD
    ) -> Dict[str, Any]:
        """
        Get quality-assured data with AI analysis
        
        Args:
            symbol: Trading symbol
            analysis_depth: Depth of AI analysis required
            required_quality: Minimum acceptable data quality
        
        Returns:
            Quality-assured data package with AI interpretation
        """
        self.stats['total_requests'] += 1
        
        try:
            # Step 1: Collect raw data
            raw_data = await self._collect_comprehensive_data(symbol)
            
            # Step 2: Assess data quality
            quality_assessment = self._assess_data_quality(raw_data)
            
            # Step 3: Check if quality meets requirements
            if not self._meets_quality_requirements(quality_assessment, required_quality):
                # Try to enhance data quality
                raw_data = await self._enhance_data_quality(symbol, raw_data)
                quality_assessment = self._assess_data_quality(raw_data)
            
            # Step 4: Perform AI analysis if available
            ai_analysis = await self._perform_ai_analysis(
                symbol, 
                raw_data, 
                analysis_depth
            )
            
            # Step 5: Package final result
            result = self._package_quality_data(
                symbol=symbol,
                raw_data=raw_data,
                quality_assessment=quality_assessment,
                ai_analysis=ai_analysis,
                analysis_depth=analysis_depth
            )
            
            # Update statistics
            self._update_statistics(quality_assessment['quality_level'])
            
            return result
            
        except Exception as e:
            logger.error(f"Error in quality data retrieval for {symbol}: {e}")
            return self._get_error_response(symbol, str(e))
    
    async def _collect_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """Collect comprehensive data from Cryptometer"""
        # Priority endpoints for quality data
        priority_endpoints = [
            'ticker',              # Current price
            'trend_indicator_v3',  # Trend analysis
            'ls_ratio',           # Long/Short ratio
            'ai_screener',        # AI signals
            'liquidation_data_v2', # Liquidations
            'open_interest',      # Open interest
            'rapid_movements'     # Rapid moves
        ]
        
        # Use batch collection with caching
        data = await self.cryptometer.batch_collect_symbols(
            symbols=[symbol],
            priority_endpoints=priority_endpoints
        )
        
        # Add cache statistics
        cache_stats = self.cryptometer.get_cache_stats()
        if cache_stats['fresh_entries'] > 0:
            self.stats['cache_hits'] += 1
        
        return data.get(symbol, {})
    
    def _assess_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of collected data"""
        # Count successful endpoints
        successful_endpoints = 0
        cached_endpoints = 0
        failed_endpoints = 0
        data_freshness = []
        
        for endpoint, result in data.items():
            if endpoint == 'symbol':
                continue
                
            if isinstance(result, dict):
                if result.get('success'):
                    successful_endpoints += 1
                    if result.get('cached'):
                        cached_endpoints += 1
                else:
                    failed_endpoints += 1
        
        # Determine quality level
        if successful_endpoints >= 7 and cached_endpoints <= 2:
            quality_level = DataQuality.PREMIUM
        elif successful_endpoints >= 5:
            quality_level = DataQuality.STANDARD
        elif successful_endpoints >= 3:
            quality_level = DataQuality.BASIC
        else:
            quality_level = DataQuality.INSUFFICIENT
        
        # Check for required indicators
        has_required = all(
            data.get(ind, {}).get('success', False) 
            for ind in self.quality_thresholds['required_indicators']
        )
        
        return {
            'quality_level': quality_level,
            'successful_endpoints': successful_endpoints,
            'cached_endpoints': cached_endpoints,
            'failed_endpoints': failed_endpoints,
            'has_required_indicators': has_required,
            'completeness': successful_endpoints / len(data) if data else 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _meets_quality_requirements(
        self, 
        assessment: Dict[str, Any], 
        required: DataQuality
    ) -> bool:
        """Check if data meets quality requirements"""
        quality_hierarchy = {
            DataQuality.PREMIUM: 3,
            DataQuality.STANDARD: 2,
            DataQuality.BASIC: 1,
            DataQuality.INSUFFICIENT: 0
        }
        
        current_level = quality_hierarchy[assessment['quality_level']]
        required_level = quality_hierarchy[required]
        
        return current_level >= required_level
    
    async def _enhance_data_quality(
        self, 
        symbol: str, 
        current_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Try to enhance data quality by fetching missing endpoints"""
        # Identify missing critical endpoints
        critical_endpoints = self.quality_thresholds['required_indicators']
        missing = []
        
        for endpoint in critical_endpoints:
            if not current_data.get(endpoint, {}).get('success'):
                missing.append(endpoint)
        
        if missing:
            logger.info(f"Enhancing data quality for {symbol}, fetching: {missing}")
            
            # Clear stale cache to force fresh data
            self.cryptometer.clear_stale_cache()
            
            # Fetch missing endpoints
            additional_data = await self.cryptometer.batch_collect_symbols(
                symbols=[symbol],
                priority_endpoints=missing
            )
            
            # Merge with current data
            if symbol in additional_data:
                current_data.update(additional_data[symbol])
        
        return current_data
    
    async def _perform_ai_analysis(
        self,
        symbol: str,
        data: Dict[str, Any],
        depth: AnalysisDepth
    ) -> Dict[str, Any]:
        """Perform AI-powered analysis of the data"""
        if not self.ai_client:
            return {'status': 'unavailable', 'message': 'AI analysis not configured'}
        
        try:
            self.stats['ai_analyses'] += 1
            
            # Prepare data summary for AI
            data_summary = self._prepare_data_summary(data)
            
            # Select appropriate prompt based on depth
            prompt = self._get_analysis_prompt(symbol, data_summary, depth)
            
            # Get AI analysis
            response = self.ai_client.chat.completions.create(
                model="gpt-4" if depth == AnalysisDepth.COMPREHENSIVE else "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for consistent analysis
                max_tokens=1000 if depth == AnalysisDepth.COMPREHENSIVE else 500
            )
            
            analysis_text = response.choices[0].message.content
            
            # Check if analysis_text is None
            if analysis_text is None:
                return {
                    'status': 'error',
                    'message': 'AI returned empty response',
                    'fallback': self._get_fallback_analysis(data)
                }
            
            # Parse and structure the analysis
            structured_analysis = self._structure_ai_analysis(analysis_text, depth)
            
            return {
                'status': 'success',
                'depth': depth.value,
                'analysis': structured_analysis,
                'model': response.model,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI analysis error for {symbol}: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'fallback': self._get_fallback_analysis(data)
            }
    
    def _prepare_data_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare a summary of data for AI analysis"""
        summary = {}
        
        # Extract key metrics
        if data.get('ticker', {}).get('success'):
            ticker_data = data['ticker']['data']
            if isinstance(ticker_data, list) and ticker_data:
                summary['price'] = ticker_data[0] if ticker_data else {}
        
        if data.get('trend_indicator_v3', {}).get('success'):
            summary['trend'] = data['trend_indicator_v3']['data']
        
        if data.get('ls_ratio', {}).get('success'):
            summary['ls_ratio'] = data['ls_ratio']['data']
        
        if data.get('ai_screener', {}).get('success'):
            summary['ai_signals'] = data['ai_screener']['data']
        
        if data.get('liquidation_data_v2', {}).get('success'):
            summary['liquidations'] = data['liquidation_data_v2']['data']
        
        return summary
    
    def _get_analysis_prompt(
        self, 
        symbol: str, 
        data_summary: Dict, 
        depth: AnalysisDepth
    ) -> str:
        """Generate appropriate analysis prompt based on depth"""
        if depth == AnalysisDepth.COMPREHENSIVE:
            return f"""
Perform a comprehensive analysis of {symbol} with the following data:

{json.dumps(data_summary, indent=2)}

Provide:
1. Market Overview (current state, trend, momentum)
2. Trading Signals (entry/exit recommendations with confidence levels)
3. Risk Assessment (key risks, support/resistance levels)
4. Technical Analysis (indicators interpretation)
5. Sentiment Analysis (market sentiment from L/S ratio and liquidations)
6. Short-term Outlook (next 24-48 hours)
7. Actionable Recommendations (specific actions for traders)

Format as structured JSON with clear sections.
"""
        
        elif depth == AnalysisDepth.DETAILED:
            return f"""
Analyze {symbol} trading data:

{json.dumps(data_summary, indent=2)}

Provide:
1. Current Market State (bullish/bearish/neutral with reasoning)
2. Key Trading Levels (support, resistance, entry/exit points)
3. Risk/Reward Assessment (potential upside vs downside)
4. Trading Recommendation (buy/sell/hold with confidence %)

Be concise but thorough. Format as structured JSON.
"""
        
        else:  # SUMMARY or BASIC
            return f"""
Quick analysis of {symbol}:

{json.dumps(data_summary, indent=2)}

Provide a brief summary with:
1. Market Direction (up/down/sideways)
2. Trading Signal (buy/sell/wait)
3. Risk Level (low/medium/high)
4. Key Price Levels

Keep it under 200 words. Format as simple JSON.
"""
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI analysis"""
        return """You are an expert cryptocurrency analyst providing high-quality, 
actionable analysis for professional traders. Your analysis should be:
- Data-driven and objective
- Clear and structured
- Risk-aware with proper disclaimers
- Formatted as valid JSON for easy parsing
- Based only on the provided data, no speculation

Always include confidence levels for your recommendations (0-100%).
If data is insufficient, clearly state limitations."""
    
    def _structure_ai_analysis(self, analysis_text: str, depth: AnalysisDepth) -> Dict:
        """Structure the AI analysis into a consistent format"""
        try:
            # Try to parse as JSON first
            if analysis_text.strip().startswith('{'):
                return json.loads(analysis_text)
        except:
            pass
        
        # Fallback to text parsing
        return {
            'raw_analysis': analysis_text,
            'depth': depth.value,
            'structured': False
        }
    
    def _get_fallback_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic fallback analysis without AI"""
        analysis: Dict[str, Any] = {
            'type': 'fallback',
            'summary': 'Basic analysis based on available data'
        }
        
        # Extract basic metrics
        if data.get('ticker', {}).get('success'):
            ticker_data = data['ticker']['data']
            if isinstance(ticker_data, list) and ticker_data:
                price_data = ticker_data[0] if ticker_data else {}
                analysis['price'] = {
                    'current': price_data.get('last'),
                    'change_24h': price_data.get('change_24h'),
                    'volume': price_data.get('volume_24')
                }
        
        if data.get('trend_indicator_v3', {}).get('success'):
            trend_data = data['trend_indicator_v3']['data']
            if isinstance(trend_data, list) and trend_data:
                trend = trend_data[0] if trend_data else {}
                analysis['trend'] = {
                    'score': trend.get('trend_score'),
                    'buy_pressure': trend.get('buy_pressure'),
                    'sell_pressure': trend.get('sell_pressure')
                }
        
        return analysis
    
    def _package_quality_data(
        self,
        symbol: str,
        raw_data: Dict[str, Any],
        quality_assessment: Dict[str, Any],
        ai_analysis: Dict[str, Any],
        analysis_depth: AnalysisDepth
    ) -> Dict[str, Any]:
        """Package all data into final quality-assured format"""
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'quality': {
                'level': quality_assessment['quality_level'].value,
                'completeness': quality_assessment['completeness'],
                'has_required_indicators': quality_assessment['has_required_indicators'],
                'successful_endpoints': quality_assessment['successful_endpoints'],
                'cached_endpoints': quality_assessment['cached_endpoints']
            },
            'data': self._clean_raw_data(raw_data),
            'analysis': ai_analysis,
            'recommendations': self._generate_recommendations(
                quality_assessment, 
                ai_analysis
            ),
            'metadata': {
                'analysis_depth': analysis_depth.value,
                'processing_time': datetime.now().isoformat(),
                'cache_stats': self.cryptometer.get_cache_stats()
            }
        }
    
    def _clean_raw_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and structure raw data for presentation"""
        cleaned = {}
        
        for endpoint, result in raw_data.items():
            if endpoint == 'symbol':
                continue
                
            if isinstance(result, dict) and result.get('success'):
                cleaned[endpoint] = {
                    'data': result.get('data'),
                    'cached': result.get('cached', False)
                }
        
        return cleaned
    
    def _generate_recommendations(
        self, 
        quality: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate final recommendations based on quality and analysis"""
        recommendations = {
            'data_reliability': 'high' if quality['quality_level'] == DataQuality.PREMIUM else 'medium',
            'analysis_confidence': 'high' if analysis.get('status') == 'success' else 'low'
        }
        
        if analysis.get('status') == 'success' and analysis.get('analysis'):
            # Extract key recommendations from AI analysis
            ai_data = analysis['analysis']
            if isinstance(ai_data, dict):
                recommendations.update({
                    'action': ai_data.get('action', 'hold'),
                    'confidence': ai_data.get('confidence', 50),
                    'risk_level': ai_data.get('risk_level', 'medium')
                })
        
        return recommendations
    
    def _update_statistics(self, quality_level: DataQuality):
        """Update delivery statistics"""
        if quality_level == DataQuality.PREMIUM:
            self.stats['premium_deliveries'] += 1
        elif quality_level == DataQuality.STANDARD:
            self.stats['standard_deliveries'] += 1
        elif quality_level == DataQuality.BASIC:
            self.stats['basic_deliveries'] += 1
    
    def _get_error_response(self, symbol: str, error: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            'symbol': symbol,
            'status': 'error',
            'error': error,
            'timestamp': datetime.now().isoformat(),
            'fallback': {
                'message': 'Unable to retrieve quality data',
                'suggestion': 'Please try again or use cached data'
            }
        }
    
    def _get_market_overview_template(self) -> str:
        """Template for market overview analysis"""
        return """
        Market Overview for {symbol}:
        - Current Price: {price}
        - 24h Change: {change_24h}%
        - Trend: {trend}
        - Market Sentiment: {sentiment}
        - Volume Analysis: {volume_analysis}
        """
    
    def _get_trading_signals_template(self) -> str:
        """Template for trading signals"""
        return """
        Trading Signals:
        - Signal: {signal_type}
        - Confidence: {confidence}%
        - Entry: {entry_price}
        - Target: {target_price}
        - Stop Loss: {stop_loss}
        - Risk/Reward: {risk_reward}
        """
    
    def _get_risk_assessment_template(self) -> str:
        """Template for risk assessment"""
        return """
        Risk Assessment:
        - Risk Level: {risk_level}
        - Key Risks: {key_risks}
        - Support Levels: {support_levels}
        - Resistance Levels: {resistance_levels}
        - Volatility: {volatility}
        """
    
    def _get_technical_analysis_template(self) -> str:
        """Template for technical analysis"""
        return """
        Technical Analysis:
        - Trend Indicator: {trend_score}
        - RSI: {rsi}
        - MACD: {macd}
        - Volume: {volume_analysis}
        - Pattern: {pattern}
        """
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get QA agent statistics"""
        total = self.stats['total_requests']
        
        return {
            'total_requests': total,
            'quality_distribution': {
                'premium': self.stats['premium_deliveries'],
                'standard': self.stats['standard_deliveries'],
                'basic': self.stats['basic_deliveries']
            },
            'ai_analyses': self.stats['ai_analyses'],
            'cache_hits': self.stats['cache_hits'],
            'premium_rate': f"{(self.stats['premium_deliveries'] / total * 100) if total > 0 else 0:.1f}%",
            'cache_hit_rate': f"{(self.stats['cache_hits'] / total * 100) if total > 0 else 0:.1f}%"
        }
    
    async def answer_question(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Answer natural language questions about trading data
        
        Args:
            question: Natural language question
            context: Optional context for the question
        
        Returns:
            Structured answer with data and confidence
        """
        import time
        start_time = time.time()
        
        try:
            # Parse the question to extract intent and symbols
            parsed = self._parse_question(question)
            
            if not parsed['symbols']:
                return {
                    'success': False,
                    'error': 'No trading symbol detected in question',
                    'question': question,
                    'answer': 'Please specify a trading symbol (e.g., BTC, ETH, SOL)',
                    'response_time_ms': int((time.time() - start_time) * 1000)
                }
            
            # Get quality data for the primary symbol
            symbol = parsed['symbols'][0]
            data = await self.get_quality_data(
                symbol=symbol,
                analysis_depth=AnalysisDepth.DETAILED,
                required_quality=DataQuality.STANDARD
            )
            
            # Generate answer based on query type
            answer = self._generate_answer(parsed, data)
            
            return {
                'success': True,
                'question': question,
                'answer': answer['text'],
                'data': answer.get('data'),
                'confidence': answer.get('confidence', 0.8),
                'query_type': parsed['query_type'],
                'symbols': parsed['symbols'],
                'response_time_ms': int((time.time() - start_time) * 1000)
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'success': False,
                'error': str(e),
                'question': question,
                'answer': f'Unable to process question: {str(e)}',
                'response_time_ms': int((time.time() - start_time) * 1000)
            }
    
    def _parse_question(self, question: str) -> Dict[str, Any]:
        """Parse natural language question to extract intent and entities"""
        question_lower = question.lower()
        
        # Extract symbols (common crypto symbols)
        symbols = []
        for symbol in ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'AVAX', 'LINK', 'UNI', 
                      'ATOM', 'FIL', 'ARB', 'OP', 'INJ', 'TIA', 'SEI']:
            if symbol.lower() in question_lower:
                symbols.append(symbol)
        
        # Determine query type
        query_type = 'general'
        if any(word in question_lower for word in ['prediction', 'predict', 'forecast', 'will']):
            query_type = 'prediction'
        elif any(word in question_lower for word in ['score', 'rating', 'rank']):
            query_type = 'score'
        elif any(word in question_lower for word in ['trend', 'trending', 'direction']):
            query_type = 'trend'
        elif any(word in question_lower for word in ['long/short', 'ls ratio', 'l/s', 'ratio']):
            query_type = 'ls_ratio'
        elif any(word in question_lower for word in ['liquidation', 'liquidated', 'liquids']):
            query_type = 'liquidation'
        elif any(word in question_lower for word in ['rapid', 'movement', 'pump', 'dump']):
            query_type = 'movement'
        elif any(word in question_lower for word in ['signal', 'buy', 'sell', 'trade']):
            query_type = 'signal'
        elif any(word in question_lower for word in ['risk', 'danger', 'safe']):
            query_type = 'risk'
        elif any(word in question_lower for word in ['compare', 'vs', 'versus', 'better']):
            query_type = 'comparison'
        
        return {
            'query_type': query_type,
            'symbols': symbols,
            'original_question': question
        }
    
    def _generate_answer(self, parsed: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate answer based on parsed question and data"""
        query_type = parsed['query_type']
        symbol = parsed['symbols'][0] if parsed['symbols'] else 'Unknown'
        
        # Extract AI analysis if available
        ai_analysis = data.get('analysis', {})
        quality_level = data.get('quality', {}).get('level', 'unknown')
        
        # Generate answer based on query type
        if query_type == 'prediction':
            if ai_analysis.get('status') == 'success':
                analysis_data = ai_analysis.get('analysis', {})
                return {
                    'text': f"AI prediction for {symbol}: {analysis_data.get('raw_analysis', 'Analysis in progress')}",
                    'data': analysis_data,
                    'confidence': 0.85
                }
            else:
                return {
                    'text': f"AI prediction for {symbol} is currently being processed. Data quality: {quality_level}",
                    'confidence': 0.5
                }
        
        elif query_type == 'score':
            recommendations = data.get('recommendations', {})
            return {
                'text': f"Score for {symbol}: Confidence {recommendations.get('confidence', 'N/A')}%, Risk Level: {recommendations.get('risk_level', 'medium')}",
                'data': recommendations,
                'confidence': 0.9
            }
        
        elif query_type == 'trend':
            trend_data = data.get('data', {}).get('trend_indicator_v3', {}).get('data')
            if trend_data:
                return {
                    'text': f"Trend for {symbol}: {self._interpret_trend(trend_data)}",
                    'data': trend_data,
                    'confidence': 0.8
                }
            else:
                return {'text': f"Trend data for {symbol} is not available", 'confidence': 0.3}
        
        elif query_type == 'ls_ratio':
            ls_data = data.get('data', {}).get('ls_ratio', {}).get('data')
            if ls_data:
                return {
                    'text': f"Long/Short ratio for {symbol}: {self._interpret_ls_ratio(ls_data)}",
                    'data': ls_data,
                    'confidence': 0.85
                }
            else:
                return {'text': f"L/S ratio data for {symbol} is not available", 'confidence': 0.3}
        
        elif query_type == 'signal':
            recommendations = data.get('recommendations', {})
            return {
                'text': f"Trading signal for {symbol}: {recommendations.get('action', 'HOLD').upper()} with {recommendations.get('confidence', 50)}% confidence",
                'data': recommendations,
                'confidence': float(recommendations.get('confidence', 50)) / 100
            }
        
        elif query_type == 'risk':
            recommendations = data.get('recommendations', {})
            risk_level = recommendations.get('risk_level', 'medium')
            return {
                'text': f"Risk assessment for {symbol}: {risk_level.upper()} risk. Data reliability: {recommendations.get('data_reliability', 'medium')}",
                'data': {'risk_level': risk_level},
                'confidence': 0.75
            }
        
        else:  # general query
            summary = f"Analysis for {symbol}: Data quality is {quality_level}. "
            if ai_analysis.get('status') == 'success':
                summary += "AI analysis available with recommendations."
            else:
                summary += "Basic data available for analysis."
            
            return {
                'text': summary,
                'data': data.get('data', {}),
                'confidence': 0.7
            }
    
    def _interpret_trend(self, trend_data: Any) -> str:
        """Interpret trend data into human-readable format"""
        if isinstance(trend_data, list) and trend_data:
            trend = trend_data[0] if trend_data else {}
            score = trend.get('trend_score', 0)
            if score > 70:
                return f"Strong UPTREND (score: {score})"
            elif score > 30:
                return f"NEUTRAL/SIDEWAYS (score: {score})"
            else:
                return f"Strong DOWNTREND (score: {score})"
        return "Unable to determine trend"
    
    def _interpret_ls_ratio(self, ls_data: Any) -> str:
        """Interpret L/S ratio data"""
        if isinstance(ls_data, dict):
            ratio = ls_data.get('ratio', 1.0)
            if ratio > 1.5:
                return f"Heavily LONG biased ({ratio:.2f}:1) - Bullish sentiment"
            elif ratio > 0.67:
                return f"BALANCED ({ratio:.2f}:1) - Neutral sentiment"
            else:
                return f"Heavily SHORT biased ({ratio:.2f}:1) - Bearish sentiment"
        return "Unable to determine L/S ratio"
    
    async def validate_and_enrich(
        self,
        symbol: str,
        existing_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate and enrich existing data with fresh analysis
        
        Args:
            symbol: Trading symbol
            existing_data: Optional existing data to validate/enrich
        
        Returns:
            Validated and enriched data package
        """
        # Get fresh quality data
        fresh_data = await self.get_quality_data(
            symbol=symbol,
            analysis_depth=AnalysisDepth.DETAILED,
            required_quality=DataQuality.STANDARD
        )
        
        if existing_data:
            # Compare and merge
            merged = self._merge_data_intelligently(existing_data, fresh_data)
            return merged
        
        return fresh_data
    
    def _merge_data_intelligently(
        self,
        existing: Dict[str, Any],
        fresh: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Intelligently merge existing and fresh data"""
        merged = fresh.copy()
        
        # Preserve valuable historical data
        if 'historical_context' in existing:
            merged['historical_context'] = existing['historical_context']
        
        # Add data comparison
        merged['data_evolution'] = {
            'previous_quality': existing.get('quality', {}).get('level'),
            'current_quality': fresh.get('quality', {}).get('level'),
            'improvement': fresh.get('quality', {}).get('completeness', 0) > 
                          existing.get('quality', {}).get('completeness', 0)
        }
        
        return merged

# Global instance
cryptometer_qa_agent = CryptometerQAAgent()

async def get_qa_agent() -> CryptometerQAAgent:
    """Get global QA agent instance"""
    return cryptometer_qa_agent