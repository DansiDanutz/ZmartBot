#!/usr/bin/env python3
"""
KingFisher Q&A Agent
Intelligent agent that answers user questions by querying the KingFisher database
Similar to RiskMetric agent but for liquidation and technical analysis data
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.database.kingfisher_database import kingfisher_db

logger = logging.getLogger(__name__)

class KingFisherQAAgent:
    """
    Intelligent Q&A agent for KingFisher data
    Answers natural language questions about liquidation analysis, win rates, and trading recommendations
    """
    
    def __init__(self):
        self.db = kingfisher_db
        self.query_patterns = self._initialize_query_patterns()
        logger.info("KingFisher Q&A Agent initialized")
    
    def _initialize_query_patterns(self) -> Dict[str, Dict]:
        """Initialize patterns for understanding user queries"""
        return {
            'win_rate': {
                'patterns': [
                    r'what.*win rate.*(\w+)',
                    r'win rate.*for.*(\w+)',
                    r'(\w+).*win rate',
                    r'long.*short.*rate.*(\w+)',
                    r'probability.*win.*(\w+)'
                ],
                'handler': self._handle_win_rate_query
            },
            'support_resistance': {
                'patterns': [
                    r'support.*resistance.*(\w+)',
                    r'key levels.*(\w+)',
                    r'(\w+).*support',
                    r'(\w+).*resistance',
                    r'price levels.*(\w+)'
                ],
                'handler': self._handle_support_resistance_query
            },
            'liquidation': {
                'patterns': [
                    r'liquidation.*(\w+)',
                    r'(\w+).*liquidation',
                    r'cluster.*(\w+)',
                    r'liquidation zones.*(\w+)',
                    r'where.*liquidations.*(\w+)'
                ],
                'handler': self._handle_liquidation_query
            },
            'recommendation': {
                'patterns': [
                    r'recommend.*(\w+)',
                    r'should.*(?:buy|sell|long|short).*(\w+)',
                    r'what.*do.*(\w+)',
                    r'trading.*advice.*(\w+)',
                    r'position.*(\w+)'
                ],
                'handler': self._handle_recommendation_query
            },
            'risk': {
                'patterns': [
                    r'risk.*(\w+)',
                    r'(\w+).*risk',
                    r'how risky.*(\w+)',
                    r'safe.*trade.*(\w+)',
                    r'danger.*(\w+)'
                ],
                'handler': self._handle_risk_query
            },
            'indicators': {
                'patterns': [
                    r'(?:lpi|mbr|ppi|rsi).*(\w+)',
                    r'(\w+).*indicators',
                    r'technical.*(\w+)',
                    r'momentum.*(\w+)',
                    r'indicators.*(\w+)'
                ],
                'handler': self._handle_indicators_query
            },
            'patterns': {
                'patterns': [
                    r'pattern.*(\w+)',
                    r'(\w+).*pattern',
                    r'divergence.*(\w+)',
                    r'trend.*(\w+)',
                    r'formation.*(\w+)'
                ],
                'handler': self._handle_patterns_query
            },
            'targets': {
                'patterns': [
                    r'target.*(\w+)',
                    r'(\w+).*target',
                    r'take profit.*(\w+)',
                    r'stop loss.*(\w+)',
                    r'entry.*(\w+)'
                ],
                'handler': self._handle_targets_query
            },
            'comparison': {
                'patterns': [
                    r'compare.*(\w+).*(?:and|vs).*(\w+)',
                    r'(\w+).*vs.*(\w+)',
                    r'difference.*(\w+).*(\w+)',
                    r'better.*(\w+).*or.*(\w+)'
                ],
                'handler': self._handle_comparison_query
            },
            'summary': {
                'patterns': [
                    r'summary.*(\w+)',
                    r'(\w+).*summary',
                    r'overview.*(\w+)',
                    r'brief.*(\w+)',
                    r'explain.*(\w+)'
                ],
                'handler': self._handle_summary_query
            }
        }
    
    async def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a user question by analyzing intent and querying the database
        
        Args:
            question: Natural language question from user
            
        Returns:
            Dict containing answer and supporting data
        """
        start_time = datetime.now()
        
        try:
            # Normalize question
            question_lower = question.lower().strip()
            
            # Extract symbols from question
            symbols = self._extract_symbols(question_lower)
            
            # Determine query type and handle
            query_type, handler = self._determine_query_type(question_lower)
            
            if handler:
                response = await handler(question_lower, symbols)
            else:
                response = await self._handle_general_query(question_lower, symbols)
            
            # Calculate response time
            response_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Store query for learning
            self.db.store_user_query(
                query=question,
                response=json.dumps(response),
                query_type=query_type,
                symbols=symbols,
                response_time_ms=response_time_ms
            )
            
            return {
                'success': True,
                'question': question,
                'answer': response.get('answer', ''),
                'data': response.get('data', {}),
                'confidence': response.get('confidence', 0.8),
                'response_time_ms': response_time_ms,
                'query_type': query_type,
                'symbols': symbols
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'success': False,
                'question': question,
                'answer': f"I encountered an error processing your question: {str(e)}",
                'error': str(e)
            }
    
    def _extract_symbols(self, text: str) -> List[str]:
        """Extract cryptocurrency symbols from text"""
        # Common crypto symbols
        known_symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'AVAX', 'MATIC', 'LINK', 'UNI']
        
        symbols = []
        text_upper = text.upper()
        
        for symbol in known_symbols:
            if symbol in text_upper:
                symbols.append(symbol)
        
        # Also look for patterns like "bitcoin" -> "BTC"
        symbol_mapping = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH',
            'solana': 'SOL',
            'ripple': 'XRP',
            'cardano': 'ADA',
            'polkadot': 'DOT',
            'avalanche': 'AVAX',
            'polygon': 'MATIC',
            'chainlink': 'LINK',
            'uniswap': 'UNI'
        }
        
        for name, symbol in symbol_mapping.items():
            if name in text and symbol not in symbols:
                symbols.append(symbol)
        
        return symbols
    
    def _determine_query_type(self, question: str) -> tuple:
        """Determine the type of query and get appropriate handler"""
        for query_type, config in self.query_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, question, re.IGNORECASE):
                    return query_type, config['handler']
        
        return 'general', None
    
    async def _handle_win_rate_query(self, question: str, symbols: List[str]) -> Dict[str, Any]:
        """Handle win rate queries"""
        if not symbols:
            return {
                'answer': "Please specify a symbol to check win rates for (e.g., BTC, ETH, SOL).",
                'data': {}
            }
        
        symbol = symbols[0]
        
        # Determine timeframe from question
        timeframe = '24h'  # default
        if '7' in question or 'week' in question:
            timeframe = '7d'
        elif 'month' in question or '30' in question:
            timeframe = '1m'
        
        # Get win rates from database
        win_rates = self.db.get_win_rates(symbol, timeframe)
        
        if not win_rates:
            return {
                'answer': f"No win rate data available for {symbol}.",
                'data': {}
            }
        
        # Format response
        long_rate = win_rates.get(f'win_rate_{timeframe}_long', win_rates.get('win_rate_24h_long', 0))
        short_rate = win_rates.get(f'win_rate_{timeframe}_short', win_rates.get('win_rate_24h_short', 0))
        confidence = win_rates.get('overall_confidence', 0)
        
        answer = f"""📊 **{symbol} Win Rates ({timeframe})**

• **Long Position**: {long_rate:.1f}%
• **Short Position**: {short_rate:.1f}%
• **Confidence**: {confidence*100:.0f}%

{'🟢 **Recommendation**: Consider LONG positions' if long_rate > 60 else '🔴 **Recommendation**: Consider SHORT positions' if short_rate > 60 else '⚪ **Recommendation**: No clear edge, wait for better setup'}

The {timeframe} analysis shows {'strong bullish momentum' if long_rate > 70 else 'bullish bias' if long_rate > 55 else 'bearish pressure' if short_rate > 55 else 'neutral conditions'} for {symbol}."""
        
        return {
            'answer': answer,
            'data': win_rates,
            'confidence': confidence
        }
    
    async def _handle_support_resistance_query(self, question: str, symbols: List[str]) -> Dict[str, Any]:
        """Handle support and resistance level queries"""
        if not symbols:
            return {
                'answer': "Please specify a symbol to check support and resistance levels.",
                'data': {}
            }
        
        symbol = symbols[0]
        levels = self.db.get_support_resistance_levels(symbol)
        
        if not levels:
            return {
                'answer': f"No support/resistance levels found for {symbol}.",
                'data': {}
            }
        
        # Get latest price
        latest = self.db.get_latest_analysis(symbol)
        current_price = latest.get('current_price', 0) if latest else 0
        
        # Separate support and resistance
        support_levels = [l for l in levels if l['level_type'] == 'support'][:3]
        resistance_levels = [l for l in levels if l['level_type'] == 'resistance'][:3]
        
        answer = f"""📍 **{symbol} Key Levels** (Current: ${current_price:,.2f})

**🔻 Support Levels:**
"""
        for level in support_levels:
            distance = ((current_price - level['price_level']) / current_price) * 100 if current_price else 0
            answer += f"• ${level['price_level']:,.2f} (-{abs(distance):.1f}%) - Strength: {level['strength']:.0%}\n"
        
        answer += "\n**🔺 Resistance Levels:**\n"
        for level in resistance_levels:
            distance = ((level['price_level'] - current_price) / current_price) * 100 if current_price else 0
            answer += f"• ${level['price_level']:,.2f} (+{distance:.1f}%) - Strength: {level['strength']:.0%}\n"
        
        answer += f"\n💡 **Trading Tip**: Watch for reactions at these levels. Strong levels often act as reversal points."
        
        return {
            'answer': answer,
            'data': {
                'support': support_levels,
                'resistance': resistance_levels,
                'current_price': current_price
            }
        }
    
    async def _handle_liquidation_query(self, question: str, symbols: List[str]) -> Dict[str, Any]:
        """Handle liquidation cluster queries"""
        if not symbols:
            return {
                'answer': "Please specify a symbol to check liquidation clusters.",
                'data': {}
            }
        
        symbol = symbols[0]
        clusters = self.db.get_liquidation_clusters(symbol, limit=5)
        
        if not clusters:
            return {
                'answer': f"No liquidation cluster data available for {symbol}.",
                'data': {}
            }
        
        # Get current price
        latest = self.db.get_latest_analysis(symbol)
        current_price = latest.get('current_price', 0) if latest else 0
        
        answer = f"""💥 **{symbol} Liquidation Clusters** (Current: ${current_price:,.2f})

**Major Liquidation Zones:**
"""
        
        for cluster in clusters[:5]:
            price = cluster['price_level']
            size = cluster['cluster_size']
            distance = ((price - current_price) / current_price) * 100 if current_price else 0
            direction = "above" if distance > 0 else "below"
            
            answer += f"""
• **${price:,.2f}** ({abs(distance):.1f}% {direction})
  - Size: {size:,.0f} positions
  - Risk: {cluster.get('risk_assessment', 'N/A')}
  - Type: {cluster.get('cluster_type', 'N/A').title()}
"""
        
        answer += "\n⚠️ **Warning**: Large liquidation clusters can trigger cascade effects when breached."
        
        return {
            'answer': answer,
            'data': {
                'clusters': clusters,
                'current_price': current_price
            }
        }
    
    async def _handle_recommendation_query(self, question: str, symbols: List[str]) -> Dict[str, Any]:
        """Handle trading recommendation queries"""
        if not symbols:
            return {
                'answer': "Please specify a symbol for trading recommendations.",
                'data': {}
            }
        
        symbol = symbols[0]
        latest = self.db.get_latest_analysis(symbol)
        
        if not latest:
            return {
                'answer': f"No analysis data available for {symbol}.",
                'data': {}
            }
        
        # Get trading targets
        targets = self.db.get_trading_targets(symbol)
        
        answer = f"""🎯 **Trading Recommendation for {symbol}**

**Current Price**: ${latest.get('current_price', 0):,.2f}
**Overall Score**: {latest.get('overall_score', 0):.0f}/100
**Risk Level**: {latest.get('risk_level', 'N/A').upper()}

**📊 Win Rates:**
• 24h: Long {latest.get('win_rate_24h_long', 0):.0f}% | Short {latest.get('win_rate_24h_short', 0):.0f}%
• 7d: Long {latest.get('win_rate_7d_long', 0):.0f}% | Short {latest.get('win_rate_7d_short', 0):.0f}%
• 1m: Long {latest.get('win_rate_1m_long', 0):.0f}% | Short {latest.get('win_rate_1m_short', 0):.0f}%

**🎯 Recommendation**: {latest.get('recommendation', 'No clear recommendation')}
**Best Timeframe**: {latest.get('best_timeframe', 'N/A')}
**Best Position**: {latest.get('best_position', 'N/A').upper()}

**Position Sizing**: {latest.get('position_size_recommendation', 'Use standard 1-2% risk')}
"""
        
        if targets:
            answer += "\n**📍 Trading Targets:**\n"
            for target in targets[:2]:
                answer += f"""
{target['position_type'].upper()} Setup ({target['timeframe']}):
• Entry: ${target['entry_price']:,.2f}
• Stop Loss: ${target['stop_loss']:,.2f}
• Target 1: ${target['target_1']:,.2f}
• R:R Ratio: {target.get('risk_reward_ratio', 0):.1f}
"""
        
        return {
            'answer': answer,
            'data': {
                'analysis': latest,
                'targets': targets
            },
            'confidence': latest.get('overall_confidence', 0.5)
        }
    
    async def _handle_risk_query(self, question: str, symbols: List[str]) -> Dict[str, Any]:
        """Handle risk assessment queries"""
        if not symbols:
            return {
                'answer': "Please specify a symbol for risk assessment.",
                'data': {}
            }
        
        symbol = symbols[0]
        latest = self.db.get_latest_analysis(symbol)
        
        if not latest:
            return {
                'answer': f"No risk data available for {symbol}.",
                'data': {}
            }
        
        risk_level = latest.get('risk_level', 'unknown')
        risk_score = latest.get('risk_score', 0)
        volatility = latest.get('volatility_index', 0)
        
        answer = f"""⚠️ **Risk Assessment for {symbol}**

**Risk Level**: {risk_level.upper()} ({risk_score*100:.0f}/100)
**Volatility Index**: {volatility:.2f}
**Confidence**: {latest.get('overall_confidence', 0)*100:.0f}%

**Risk Factors:**
• Long Concentration: {latest.get('long_concentration', 0)*100:.1f}%
• Short Concentration: {latest.get('short_concentration', 0)*100:.1f}%
• LPI (Liquidation Pressure): {latest.get('lpi', 0):.1f}/10
• Market Balance Ratio: {latest.get('mbr', 0):.2f}

**Risk Management Advice:**
"""
        
        if risk_level == 'high':
            answer += "🔴 HIGH RISK - Reduce position size, use tight stops, or avoid trading"
        elif risk_level == 'medium':
            answer += "🟡 MODERATE RISK - Use standard position sizing with careful monitoring"
        else:
            answer += "🟢 LOW RISK - Safe for standard or slightly increased position sizing"
        
        answer += f"""

**Recommended Position Size**: {latest.get('position_size_recommendation', '1-2% of portfolio')}"""
        
        return {
            'answer': answer,
            'data': {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'volatility': volatility,
                'full_analysis': latest
            }
        }
    
    async def _handle_indicators_query(self, question: str, symbols: List[str]) -> Dict[str, Any]:
        """Handle technical indicators queries"""
        if not symbols:
            return {
                'answer': "Please specify a symbol for technical indicators.",
                'data': {}
            }
        
        symbol = symbols[0]
        latest = self.db.get_latest_analysis(symbol)
        
        if not latest:
            return {
                'answer': f"No indicator data available for {symbol}.",
                'data': {}
            }
        
        answer = f"""📈 **Technical Indicators for {symbol}**

**Custom KingFisher Indicators:**
• **LPI** (Liquidation Pressure Index): {latest.get('lpi', 0):.1f}/10
  - {self._interpret_lpi(latest.get('lpi', 0))}

• **MBR** (Market Balance Ratio): {latest.get('mbr', 0):.2f}
  - {self._interpret_mbr(latest.get('mbr', 0))}

• **PPI** (Price Position Index): {latest.get('ppi', 0):.1f}/10
  - {self._interpret_ppi(latest.get('ppi', 0))}

**Standard Indicators:**
• **RSI**: {latest.get('rsi', 50):.0f}
  - {self._interpret_rsi(latest.get('rsi', 50))}

• **Momentum Score**: {latest.get('momentum_score', 0.5)*100:.0f}%
  - {self._interpret_momentum(latest.get('momentum_score', 0.5))}

**Overall Sentiment**: {latest.get('overall_sentiment', 'neutral').upper()}"""
        
        return {
            'answer': answer,
            'data': {
                'lpi': latest.get('lpi', 0),
                'mbr': latest.get('mbr', 0),
                'ppi': latest.get('ppi', 0),
                'rsi': latest.get('rsi', 50),
                'momentum': latest.get('momentum_score', 0.5)
            }
        }
    
    async def _handle_patterns_query(self, question: str, symbols: List[str]) -> Dict[str, Any]:
        """Handle market pattern queries"""
        if not symbols:
            return {
                'answer': "Please specify a symbol to check market patterns.",
                'data': {}
            }
        
        symbol = symbols[0]
        patterns = self.db.get_market_patterns(symbol)
        
        if not patterns:
            return {
                'answer': f"No market patterns detected for {symbol}.",
                'data': {}
            }
        
        answer = f"""🔍 **Market Patterns for {symbol}**

**Detected Patterns:**
"""
        
        for pattern in patterns[:5]:
            answer += f"""
• **{pattern['pattern_type'].replace('_', ' ').title()}**
  - Strength: {pattern['pattern_strength']*100:.0f}%
  - Confidence: {pattern['confidence']*100:.0f}%
  - Expected Move: {pattern.get('expected_move', 0):.1f}% {pattern.get('expected_direction', '').upper()}
  - Timeframe: {pattern['timeframe']}
  - {pattern.get('description', '')}
"""
        
        return {
            'answer': answer,
            'data': {'patterns': patterns}
        }
    
    async def _handle_targets_query(self, question: str, symbols: List[str]) -> Dict[str, Any]:
        """Handle trading targets queries"""
        if not symbols:
            return {
                'answer': "Please specify a symbol for trading targets.",
                'data': {}
            }
        
        symbol = symbols[0]
        targets = self.db.get_trading_targets(symbol)
        
        if not targets:
            return {
                'answer': f"No trading targets available for {symbol}.",
                'data': {}
            }
        
        # Get current price
        latest = self.db.get_latest_analysis(symbol)
        current_price = latest.get('current_price', 0) if latest else 0
        
        answer = f"""🎯 **Trading Targets for {symbol}** (Current: ${current_price:,.2f})

"""
        
        for target in targets[:3]:
            answer += f"""**{target['position_type'].upper()} - {target['timeframe']}**
• Entry: ${target['entry_price']:,.2f}
• Stop Loss: ${target['stop_loss']:,.2f} ({abs((target['stop_loss']-target['entry_price'])/target['entry_price']*100):.1f}%)
• Target 1: ${target['target_1']:,.2f} (+{((target['target_1']-target['entry_price'])/target['entry_price']*100):.1f}%)
• Target 2: ${target['target_2']:,.2f} (+{((target['target_2']-target['entry_price'])/target['entry_price']*100):.1f}%)
• Target 3: ${target['target_3']:,.2f} (+{((target['target_3']-target['entry_price'])/target['entry_price']*100):.1f}%)
• Risk:Reward: 1:{target.get('risk_reward_ratio', 0):.1f}
• Win Probability: {target.get('win_probability', 0)*100:.0f}%

"""
        
        return {
            'answer': answer,
            'data': {'targets': targets, 'current_price': current_price}
        }
    
    async def _handle_comparison_query(self, question: str, symbols: List[str]) -> Dict[str, Any]:
        """Handle comparison queries between symbols"""
        if len(symbols) < 2:
            return {
                'answer': "Please specify at least two symbols to compare (e.g., BTC vs ETH).",
                'data': {}
            }
        
        symbol1, symbol2 = symbols[0], symbols[1]
        
        # Get latest analysis for both
        analysis1 = self.db.get_latest_analysis(symbol1)
        analysis2 = self.db.get_latest_analysis(symbol2)
        
        if not analysis1 or not analysis2:
            return {
                'answer': f"Missing data for comparison. Ensure both {symbol1} and {symbol2} have been analyzed.",
                'data': {}
            }
        
        answer = f"""⚖️ **Comparison: {symbol1} vs {symbol2}**

**Overall Scores:**
• {symbol1}: {analysis1.get('overall_score', 0):.0f}/100
• {symbol2}: {analysis2.get('overall_score', 0):.0f}/100
**Winner**: {"🏆 " + symbol1 if analysis1.get('overall_score', 0) > analysis2.get('overall_score', 0) else "🏆 " + symbol2}

**Win Rates (24h):**
• {symbol1}: Long {analysis1.get('win_rate_24h_long', 0):.0f}% | Short {analysis1.get('win_rate_24h_short', 0):.0f}%
• {symbol2}: Long {analysis2.get('win_rate_24h_long', 0):.0f}% | Short {analysis2.get('win_rate_24h_short', 0):.0f}%

**Risk Levels:**
• {symbol1}: {analysis1.get('risk_level', 'N/A').upper()} ({analysis1.get('risk_score', 0)*100:.0f}%)
• {symbol2}: {analysis2.get('risk_level', 'N/A').upper()} ({analysis2.get('risk_score', 0)*100:.0f}%)

**Confidence:**
• {symbol1}: {analysis1.get('overall_confidence', 0)*100:.0f}%
• {symbol2}: {analysis2.get('overall_confidence', 0)*100:.0f}%

**Recommendation:**
"""
        
        if analysis1.get('overall_score', 0) > analysis2.get('overall_score', 0):
            answer += f"✅ {symbol1} shows better trading opportunity with higher score and "
            if analysis1.get('risk_score', 1) < analysis2.get('risk_score', 1):
                answer += "lower risk."
            else:
                answer += "but consider the higher risk."
        else:
            answer += f"✅ {symbol2} shows better trading opportunity with higher score and "
            if analysis2.get('risk_score', 1) < analysis1.get('risk_score', 1):
                answer += "lower risk."
            else:
                answer += "but consider the higher risk."
        
        return {
            'answer': answer,
            'data': {
                symbol1: analysis1,
                symbol2: analysis2
            }
        }
    
    async def _handle_summary_query(self, question: str, symbols: List[str]) -> Dict[str, Any]:
        """Handle summary queries"""
        if not symbols:
            return {
                'answer': "Please specify a symbol for analysis summary.",
                'data': {}
            }
        
        symbol = symbols[0]
        latest = self.db.get_latest_analysis(symbol)
        
        if not latest:
            return {
                'answer': f"No analysis data available for {symbol}.",
                'data': {}
            }
        
        # Get executive summary if available
        executive_summary = latest.get('executive_summary', '')
        
        if executive_summary:
            answer = f"""📊 **{symbol} Analysis Summary**

{executive_summary}

**Key Metrics:**
• Overall Score: {latest.get('overall_score', 0):.0f}/100
• Risk Level: {latest.get('risk_level', 'N/A').upper()}
• Best Position: {latest.get('best_position', 'N/A').upper()}
• Confidence: {latest.get('overall_confidence', 0)*100:.0f}%"""
        else:
            # Generate summary from data
            answer = f"""📊 **{symbol} Analysis Summary**

**Current Price**: ${latest.get('current_price', 0):,.2f}

**Market Assessment**:
{symbol} is showing {latest.get('overall_sentiment', 'neutral')} sentiment with {latest.get('risk_level', 'moderate')} risk conditions.

**Win Rates**:
• Short-term (24h): Long {latest.get('win_rate_24h_long', 0):.0f}% vs Short {latest.get('win_rate_24h_short', 0):.0f}%
• Medium-term (7d): Long {latest.get('win_rate_7d_long', 0):.0f}% vs Short {latest.get('win_rate_7d_short', 0):.0f}%
• Long-term (1m): Long {latest.get('win_rate_1m_long', 0):.0f}% vs Short {latest.get('win_rate_1m_short', 0):.0f}%

**Trading Recommendation**:
{latest.get('recommendation', 'No specific recommendation available')}

**Risk Management**:
Position Size: {latest.get('position_size_recommendation', 'Standard 1-2% of portfolio')}
Confidence Level: {latest.get('overall_confidence', 0)*100:.0f}%"""
        
        return {
            'answer': answer,
            'data': latest,
            'confidence': latest.get('overall_confidence', 0.5)
        }
    
    async def _handle_general_query(self, question: str, symbols: List[str]) -> Dict[str, Any]:
        """Handle general queries that don't match specific patterns"""
        if not symbols:
            return {
                'answer': """I can help you with KingFisher liquidation analysis data. Try asking:

• "What's the win rate for BTC?"
• "Show me support and resistance for ETH"
• "Where are the liquidation clusters for SOL?"
• "Should I go long or short on XRP?"
• "What's the risk level for ADA?"
• "Compare BTC vs ETH"
• "Show me trading targets for DOT"

Please include a symbol in your question.""",
                'data': {}
            }
        
        # If symbols are provided, give a summary
        symbol = symbols[0]
        return await self._handle_summary_query(question, symbols)
    
    # Helper methods for interpretation
    def _interpret_lpi(self, lpi: float) -> str:
        if lpi > 8:
            return "🔴 Extreme liquidation pressure - high cascade risk"
        elif lpi > 6:
            return "🟡 High liquidation pressure - significant risk"
        elif lpi > 4:
            return "⚪ Moderate liquidation pressure"
        else:
            return "🟢 Low liquidation pressure - stable"
    
    def _interpret_mbr(self, mbr: float) -> str:
        if mbr > 1.5:
            return "🔴 Retail overleveraged vs institutions"
        elif mbr > 1.2:
            return "🟡 Slight retail bias"
        elif mbr < 0.8:
            return "🟢 Institutional accumulation"
        else:
            return "⚪ Balanced retail/institutional"
    
    def _interpret_ppi(self, ppi: float) -> str:
        if ppi > 8:
            return "🔴 Overextended to upside"
        elif ppi > 6:
            return "🟡 Upper range positioning"
        elif ppi < 4:
            return "🟢 Lower range - potential bounce"
        else:
            return "⚪ Mid-range positioning"
    
    def _interpret_rsi(self, rsi: float) -> str:
        if rsi > 70:
            return "🔴 Overbought - potential reversal"
        elif rsi < 30:
            return "🟢 Oversold - potential bounce"
        else:
            return "⚪ Neutral momentum"
    
    def _interpret_momentum(self, momentum: float) -> str:
        if momentum > 0.7:
            return "🟢 Strong bullish momentum"
        elif momentum < 0.3:
            return "🔴 Strong bearish momentum"
        else:
            return "⚪ Neutral momentum"

# Create global instance
kingfisher_qa_agent = KingFisherQAAgent()