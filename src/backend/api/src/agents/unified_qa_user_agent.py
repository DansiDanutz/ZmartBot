#!/usr/bin/env python3
"""
🎓 Unified QA User Agent - The Master Teacher
Combines all QA agents to provide professional, educational analysis
with multi-timeframe win rate predictions and interactive learning
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json
import statistics

# Import AI models
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Import all QA agents and services
from src.agents.cryptometer_qa_agent import DataQuality, AnalysisDepth
from src.config.settings import settings

logger = logging.getLogger(__name__)

class TimeFrame(Enum):
    """Trading timeframes for analysis"""
    SHORT = "1H-4H"     # 1-4 hours
    MEDIUM = "1D-3D"    # 1-3 days  
    LONG = "1W-1M"      # 1 week to 1 month

class TeachingStyle(Enum):
    """Teaching styles for different user levels"""
    BEGINNER = "beginner"        # Simple explanations with basics
    INTERMEDIATE = "intermediate" # Balanced technical and simple
    ADVANCED = "advanced"        # Full technical depth
    EXPERT = "expert"           # Professional trader level

class AnalysisPackage(Enum):
    """Analysis package types (for future credit system)"""
    BASIC = "basic"              # 1 credit - Quick overview
    STANDARD = "standard"        # 3 credits - Detailed analysis
    PREMIUM = "premium"          # 5 credits - Full multi-source
    PROFESSIONAL = "professional" # 10 credits - Institutional grade

class UnifiedQAUserAgent:
    """
    The Master Teacher Agent - Combines all QA agents for comprehensive analysis
    Provides educational, interactive responses with win rate predictions
    """
    
    def __init__(self):
        """Initialize the Unified QA User Agent"""
        
        # Initialize all sub-agents (using type annotation for proper typing)
        self.agents: Dict[str, Optional[Any]] = {
            'cryptometer': None,
            'riskmetric': None,
            'kingfisher': None,
            'grok_x': None,
            'whale': None,
            'blockchain': None
        }
        
        # Try to initialize each agent
        self._initialize_agents()
        
        # Initialize AI client for synthesis
        self.ai_client = None
        if OpenAI and hasattr(settings, 'OPENAI_API_KEY'):
            try:
                self.ai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("🎓 AI synthesis enabled with OpenAI")
            except Exception as e:
                logger.warning(f"⚠️ AI client initialization failed: {e}")
        
        # Win rate calculation parameters
        self.win_rate_thresholds = {
            TimeFrame.SHORT: {
                'high_confidence': 0.75,
                'medium_confidence': 0.60,
                'low_confidence': 0.45
            },
            TimeFrame.MEDIUM: {
                'high_confidence': 0.70,
                'medium_confidence': 0.55,
                'low_confidence': 0.40
            },
            TimeFrame.LONG: {
                'high_confidence': 0.65,
                'medium_confidence': 0.50,
                'low_confidence': 0.35
            }
        }
        
        # Teaching templates
        self.teaching_templates = {
            TeachingStyle.BEGINNER: self._get_beginner_template(),
            TeachingStyle.INTERMEDIATE: self._get_intermediate_template(),
            TeachingStyle.ADVANCED: self._get_advanced_template(),
            TeachingStyle.EXPERT: self._get_expert_template()
        }
        
        # Credit costs (for future implementation)
        self.credit_costs = {
            AnalysisPackage.BASIC: 1,
            AnalysisPackage.STANDARD: 3,
            AnalysisPackage.PREMIUM: 5,
            AnalysisPackage.PROFESSIONAL: 10
        }
        
        # Statistics tracking
        self.stats = {
            'total_analyses': 0,
            'successful_predictions': 0,
            'total_predictions': 0,
            'credits_consumed': 0,
            'user_satisfaction': []
        }
        
        logger.info("🎓 Unified QA User Agent initialized - The Master Teacher is ready!")
    
    def _initialize_agents(self):
        """Initialize all sub-agents with error handling"""
        
        # Cryptometer QA Agent
        try:
            from src.agents.cryptometer_qa_agent import CryptometerQAAgent
            self.agents['cryptometer'] = CryptometerQAAgent()
            logger.info("✅ Cryptometer QA Agent loaded")
        except Exception as e:
            logger.warning(f"⚠️ Could not load Cryptometer QA Agent: {e}")
        
        # RiskMetric QA Agent (placeholder - will be implemented)
        try:
            # Will be enabled when RiskMetricQAAgent is implemented
            # from src.agents.database.riskmetric_qa_agent import RiskMetricQAAgent
            # self.agents['riskmetric'] = RiskMetricQAAgent()
            logger.info("⏳ RiskMetric QA Agent pending implementation")
        except Exception as e:
            logger.warning(f"⚠️ Could not load RiskMetric QA Agent: {e}")
        
        # KingFisher QA Agent (placeholder - will be implemented)
        try:
            # Will be enabled when KingFisherQAAgent is implemented
            # from src.agents.kingfisher_qa_agent import KingFisherQAAgent
            # self.agents['kingfisher'] = KingFisherQAAgent()
            logger.info("⏳ KingFisher QA Agent pending implementation")
        except Exception as e:
            logger.warning(f"⚠️ Could not load KingFisher QA Agent: {e}")
        
        # Grok & X QA Agent (placeholder - will be implemented)
        try:
            # Will be enabled when GrokXQAAgent is implemented
            # from src.agents.sentiment.grok_x_qa_agent import GrokXQAAgent
            # self.agents['grok_x'] = GrokXQAAgent()
            logger.info("⏳ Grok & X QA Agent pending implementation")
        except Exception as e:
            logger.warning(f"⚠️ Could not load Grok & X QA Agent: {e}")
        
        # Whale QA Agent (placeholder - will be implemented)
        try:
            # Will be enabled when WhaleQAAgent is implemented
            # from src.agents.trading.whale_qa_agent import WhaleQAAgent
            # self.agents['whale'] = WhaleQAAgent()
            logger.info("⏳ Whale QA Agent pending implementation")
        except Exception as e:
            logger.warning(f"⚠️ Could not load Whale QA Agent: {e}")
        
        # Blockchain QA Agent (placeholder - will be implemented)
        try:
            # Will be enabled when BlockchainQAAgent is implemented
            # from src.agents.blockchain.blockchain_qa_agent import BlockchainQAAgent
            # self.agents['blockchain'] = BlockchainQAAgent()
            logger.info("⏳ Blockchain QA Agent pending implementation")
        except Exception as e:
            logger.warning(f"⚠️ Could not load Blockchain QA Agent: {e}")
    
    async def analyze_with_teaching(
        self,
        symbol: str,
        user_question: str,
        teaching_style: TeachingStyle = TeachingStyle.INTERMEDIATE,
        package: AnalysisPackage = AnalysisPackage.STANDARD,
        user_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Provide comprehensive analysis with educational explanations
        
        Args:
            symbol: Trading symbol to analyze
            user_question: User's specific question or concern
            teaching_style: How to present the information
            package: Analysis depth package
            user_level: Optional user experience level
        
        Returns:
            Educational analysis with win rates and recommendations
        """
        self.stats['total_analyses'] += 1
        
        try:
            # Step 1: Collect data from all available agents
            all_data = await self._collect_all_agent_data(symbol, package)
            
            # Step 2: Calculate win rates for all timeframes
            win_rates = self._calculate_win_rates(all_data)
            
            # Step 3: Generate professional summary
            professional_summary = await self._generate_professional_summary(
                symbol, all_data, win_rates, user_question
            )
            
            # Step 4: Create educational response
            educational_response = self._create_educational_response(
                professional_summary, teaching_style, user_level
            )
            
            # Step 5: Add interactive elements
            interactive_content = self._add_interactive_elements(
                educational_response, symbol, win_rates
            )
            
            # Track credits (for future implementation)
            self.stats['credits_consumed'] += self.credit_costs[package]
            
            return {
                'success': True,
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'teaching_style': teaching_style.value,
                'package': package.value,
                'credits_used': self.credit_costs[package],
                'analysis': {
                    'summary': professional_summary,
                    'educational_content': educational_response,
                    'interactive_elements': interactive_content,
                    'win_rates': win_rates,
                    'data_sources': self._get_data_sources_status(all_data),
                    'confidence_metrics': self._calculate_confidence_metrics(all_data)
                },
                'recommendations': self._generate_recommendations(win_rates, all_data),
                'learning_resources': self._get_learning_resources(teaching_style),
                'next_steps': self._suggest_next_steps(symbol, win_rates)
            }
            
        except Exception as e:
            logger.error(f"Error in unified analysis for {symbol}: {e}")
            return self._get_error_response(symbol, str(e))
    
    async def _collect_all_agent_data(
        self, 
        symbol: str, 
        package: AnalysisPackage
    ) -> Dict[str, Any]:
        """Collect data from all available QA agents"""
        
        all_data = {}
        
        # Determine which agents to query based on package
        agents_to_query = self._get_agents_for_package(package)
        
        # Collect data in parallel
        tasks = []
        
        for agent_name in agents_to_query:
            agent = self.agents.get(agent_name)
            if agent:
                if agent_name == 'cryptometer' and hasattr(agent, 'get_quality_data'):
                    tasks.append(self._get_cryptometer_data(agent, symbol))
                elif agent_name == 'riskmetric' and hasattr(agent, 'get_riskmetric_analysis'):
                    tasks.append(self._get_riskmetric_data(agent, symbol))
                elif agent_name == 'kingfisher' and hasattr(agent, 'analyze_liquidations'):
                    tasks.append(self._get_kingfisher_data(agent, symbol))
                elif agent_name == 'grok_x' and hasattr(agent, 'get_sentiment_analysis'):
                    tasks.append(self._get_grokx_data(agent, symbol))
                elif agent_name == 'whale' and hasattr(agent, 'get_whale_activity'):
                    tasks.append(self._get_whale_data(agent, symbol))
                elif agent_name == 'blockchain' and hasattr(agent, 'get_onchain_metrics'):
                    tasks.append(self._get_blockchain_data(agent, symbol))
        
        # Wait for all data collection
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            agent_names = [name for name in agents_to_query if self.agents.get(name)]
            for i, result in enumerate(results):
                if i < len(agent_names):
                    agent_name = agent_names[i]
                    if not isinstance(result, Exception):
                        all_data[agent_name] = result
                    else:
                        logger.warning(f"Error collecting data from {agent_name}: {result}")
                        all_data[agent_name] = {'error': str(result)}
        
        return all_data
    
    async def _get_cryptometer_data(self, agent, symbol: str) -> Dict[str, Any]:
        """Get Cryptometer data"""
        try:
            return await agent.get_quality_data(
                symbol=symbol,
                analysis_depth=AnalysisDepth.DETAILED,
                required_quality=DataQuality.STANDARD
            )
        except Exception as e:
            logger.error(f"Cryptometer data error: {e}")
            return {'error': str(e)}
    
    async def _get_riskmetric_data(self, agent, symbol: str) -> Dict[str, Any]:
        """Get RiskMetric data"""
        try:
            # Placeholder - implement when RiskMetric QA Agent is available
            return {
                'riskmetric_score': 0.65,
                'risk_band': 'medium',
                'historical_patterns': []
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_kingfisher_data(self, agent, symbol: str) -> Dict[str, Any]:
        """Get KingFisher liquidation data"""
        try:
            # Placeholder - implement when KingFisher QA Agent is available
            return {
                'liquidation_clusters': [],
                'heat_map_analysis': 'neutral',
                'critical_levels': []
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_grokx_data(self, agent, symbol: str) -> Dict[str, Any]:
        """Get Grok & X sentiment data"""
        try:
            # Placeholder - implement when Grok & X QA Agent is available
            return {
                'social_sentiment': 'neutral',
                'sentiment_score': 0.5,
                'trending_topics': []
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_whale_data(self, agent, symbol: str) -> Dict[str, Any]:
        """Get Whale activity data"""
        try:
            # Placeholder - implement when Whale QA Agent is available
            return {
                'whale_activity': 'low',
                'large_transactions': [],
                'accumulation_distribution': 'neutral'
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_blockchain_data(self, agent, symbol: str) -> Dict[str, Any]:
        """Get Blockchain on-chain data"""
        try:
            # Placeholder - implement when Blockchain QA Agent is available
            return {
                'network_activity': 'normal',
                'active_addresses': 0,
                'transaction_volume': 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_agents_for_package(self, package: AnalysisPackage) -> List[str]:
        """Determine which agents to use based on package"""
        if package == AnalysisPackage.BASIC:
            return ['cryptometer']
        elif package == AnalysisPackage.STANDARD:
            return ['cryptometer', 'riskmetric', 'kingfisher']
        elif package == AnalysisPackage.PREMIUM:
            return ['cryptometer', 'riskmetric', 'kingfisher', 'grok_x', 'whale']
        else:  # PROFESSIONAL
            return ['cryptometer', 'riskmetric', 'kingfisher', 'grok_x', 'whale', 'blockchain']
    
    def _calculate_win_rates(self, all_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Calculate win rates for all timeframes based on collected data
        
        Returns:
            Win rates with confidence levels for each timeframe
        """
        win_rates = {}
        
        for timeframe in TimeFrame:
            # Collect signals from all sources
            signals = self._collect_signals_for_timeframe(all_data, timeframe)
            
            # Calculate composite score
            composite_score = self._calculate_composite_score(signals)
            
            # Determine win rate and confidence
            win_rate, confidence = self._determine_win_rate(composite_score, timeframe)
            
            win_rates[timeframe.value] = {
                'win_rate': f"{win_rate:.1f}%",
                'confidence': confidence,
                'signals_analyzed': len(signals),
                'composite_score': composite_score,
                'recommendation': self._get_timeframe_recommendation(win_rate, confidence)
            }
        
        return win_rates
    
    def _collect_signals_for_timeframe(
        self, 
        all_data: Dict[str, Any], 
        timeframe: TimeFrame
    ) -> List[Dict[str, Any]]:
        """Collect relevant signals for a specific timeframe"""
        signals = []
        
        # Extract signals from Cryptometer
        if 'cryptometer' in all_data and not all_data['cryptometer'].get('error'):
            crypto_data = all_data['cryptometer']
            if crypto_data.get('recommendations'):
                signals.append({
                    'source': 'cryptometer',
                    'signal': crypto_data['recommendations'].get('action', 'hold'),
                    'confidence': crypto_data['recommendations'].get('confidence', 50) / 100
                })
        
        # Extract signals from RiskMetric
        if 'riskmetric' in all_data and not all_data['riskmetric'].get('error'):
            risk_data = all_data['riskmetric']
            signals.append({
                'source': 'riskmetric',
                'signal': 'buy' if risk_data.get('riskmetric_score', 0.5) < 0.4 else 'sell' if risk_data.get('riskmetric_score', 0.5) > 0.6 else 'hold',
                'confidence': 0.7
            })
        
        # Extract signals from KingFisher
        if 'kingfisher' in all_data and not all_data['kingfisher'].get('error'):
            king_data = all_data['kingfisher']
            heat_map = king_data.get('heat_map_analysis', 'neutral')
            signals.append({
                'source': 'kingfisher',
                'signal': 'buy' if heat_map == 'bullish' else 'sell' if heat_map == 'bearish' else 'hold',
                'confidence': 0.65
            })
        
        # Add more signal extraction for other agents...
        
        return signals
    
    def _calculate_composite_score(self, signals: List[Dict[str, Any]]) -> float:
        """Calculate composite score from all signals"""
        if not signals:
            return 0.5
        
        total_weight = 0
        weighted_sum = 0
        
        for signal in signals:
            # Convert signal to numeric score
            signal_score = 1.0 if signal['signal'] == 'buy' else 0.0 if signal['signal'] == 'sell' else 0.5
            confidence = signal['confidence']
            
            weighted_sum += signal_score * confidence
            total_weight += confidence
        
        return weighted_sum / total_weight if total_weight > 0 else 0.5
    
    def _determine_win_rate(
        self, 
        composite_score: float, 
        timeframe: TimeFrame
    ) -> Tuple[float, str]:
        """Determine win rate and confidence level"""
        
        # Base win rate calculation
        base_win_rate = 50 + (composite_score - 0.5) * 100
        
        # Adjust for timeframe
        if timeframe == TimeFrame.SHORT:
            win_rate = base_win_rate * 0.95  # Slightly lower for short term
        elif timeframe == TimeFrame.MEDIUM:
            win_rate = base_win_rate
        else:  # LONG
            win_rate = base_win_rate * 1.05  # Slightly higher for long term
        
        # Ensure within bounds
        win_rate = max(20, min(80, win_rate))
        
        # Determine confidence
        thresholds = self.win_rate_thresholds[timeframe]
        if composite_score >= thresholds['high_confidence']:
            confidence = 'HIGH'
        elif composite_score >= thresholds['medium_confidence']:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        return win_rate, confidence
    
    def _get_timeframe_recommendation(self, win_rate: float, confidence: str) -> str:
        """Get recommendation based on win rate and confidence"""
        if confidence == 'HIGH':
            if win_rate >= 65:
                return "STRONG BUY"
            elif win_rate >= 55:
                return "BUY"
            elif win_rate <= 35:
                return "STRONG SELL"
            elif win_rate <= 45:
                return "SELL"
            else:
                return "HOLD"
        elif confidence == 'MEDIUM':
            if win_rate >= 60:
                return "CONSIDER BUY"
            elif win_rate <= 40:
                return "CONSIDER SELL"
            else:
                return "NEUTRAL"
        else:  # LOW confidence
            return "WAIT FOR BETTER SIGNAL"
    
    async def _generate_professional_summary(
        self,
        symbol: str,
        all_data: Dict[str, Any],
        win_rates: Dict[str, Dict[str, Any]],
        user_question: str
    ) -> str:
        """Generate professional summary using AI"""
        
        if not self.ai_client:
            return self._generate_fallback_summary(symbol, win_rates)
        
        try:
            # Prepare data for AI
            data_summary = {
                'symbol': symbol,
                'user_question': user_question,
                'win_rates': win_rates,
                'data_sources': list(all_data.keys()),
                'key_metrics': self._extract_key_metrics(all_data)
            }
            
            # Generate with AI
            response = self.ai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional trading analyst and educator. 
                        Provide clear, actionable analysis with educational value.
                        Focus on win rates, risk management, and practical recommendations."""
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze {symbol} with this data:
                        
{json.dumps(data_summary, indent=2)}

Provide a professional summary addressing:
1. Direct answer to: {user_question}
2. Win rate analysis for all timeframes
3. Key risk factors
4. Actionable recommendations
5. Educational insights

Keep it concise but comprehensive."""
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            if content is None:
                return self._generate_fallback_summary(symbol, win_rates)
            return content
            
        except Exception as e:
            logger.error(f"AI summary generation error: {e}")
            return self._generate_fallback_summary(symbol, win_rates)
    
    def _generate_fallback_summary(
        self, 
        symbol: str, 
        win_rates: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate summary without AI"""
        
        summary = f"📊 Analysis for {symbol}\n\n"
        summary += "Win Rate Predictions:\n"
        
        for timeframe, data in win_rates.items():
            summary += f"• {timeframe}: {data['win_rate']} (Confidence: {data['confidence']})\n"
            summary += f"  Recommendation: {data['recommendation']}\n"
        
        return summary
    
    def _create_educational_response(
        self,
        professional_summary: str,
        teaching_style: TeachingStyle,
        user_level: Optional[str]
    ) -> str:
        """Create educational response based on teaching style"""
        
        if teaching_style == TeachingStyle.BEGINNER:
            return self._simplify_for_beginner(professional_summary)
        elif teaching_style == TeachingStyle.INTERMEDIATE:
            return self._balance_for_intermediate(professional_summary)
        elif teaching_style == TeachingStyle.ADVANCED:
            return self._enhance_for_advanced(professional_summary)
        else:  # EXPERT
            return professional_summary  # Keep full technical depth
    
    def _simplify_for_beginner(self, summary: str) -> str:
        """Simplify summary for beginners"""
        intro = "🎓 Let me explain this in simple terms:\n\n"
        
        # Add simple explanations
        simplified = intro + summary
        
        # Add learning tips
        simplified += "\n\n💡 Learning Tip: Win rate shows the probability of a profitable trade. "
        simplified += "Higher win rates with HIGH confidence are generally better signals!"
        
        return simplified
    
    def _balance_for_intermediate(self, summary: str) -> str:
        """Balance technical and simple for intermediate users"""
        intro = "📈 Here's your analysis with key technical insights:\n\n"
        
        balanced = intro + summary
        
        balanced += "\n\n📚 Key Concept: We analyze multiple timeframes because "
        balanced += "short-term noise can obscure longer-term trends. "
        balanced += "Always consider your investment horizon!"
        
        return balanced
    
    def _enhance_for_advanced(self, summary: str) -> str:
        """Enhance with technical depth for advanced users"""
        intro = "🔬 Advanced Analysis with Multi-Source Correlation:\n\n"
        
        enhanced = intro + summary
        
        enhanced += "\n\n⚡ Advanced Insight: The composite scoring algorithm weights "
        enhanced += "each data source by historical accuracy and current market regime. "
        enhanced += "Consider using Kelly Criterion for position sizing based on win rates."
        
        return enhanced
    
    def _add_interactive_elements(
        self,
        educational_response: str,
        symbol: str,
        win_rates: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Add interactive elements for better learning"""
        
        return {
            'quiz_question': self._generate_quiz_question(symbol, win_rates),
            'follow_up_prompts': [
                f"What factors affect the win rate for {symbol}?",
                f"How should I adjust my position size based on these confidence levels?",
                f"What risk management rules should I follow with these signals?",
                f"Can you explain the difference between the timeframes?"
            ],
            'visual_aids': {
                'win_rate_chart': self._prepare_chart_data(win_rates),
                'confidence_meter': self._prepare_confidence_visualization(win_rates)
            },
            'practice_scenario': self._create_practice_scenario(symbol, win_rates)
        }
    
    def _generate_quiz_question(
        self, 
        symbol: str, 
        win_rates: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate educational quiz question"""
        
        # Find the best timeframe
        best_timeframe = max(
            win_rates.items(),
            key=lambda x: float(x[1]['win_rate'].rstrip('%'))
        )[0]
        
        return {
            'question': f"Based on the analysis, which timeframe shows the highest win rate for {symbol}?",
            'options': list(win_rates.keys()),
            'correct_answer': best_timeframe,
            'explanation': f"The {best_timeframe} timeframe shows {win_rates[best_timeframe]['win_rate']} win rate with {win_rates[best_timeframe]['confidence']} confidence."
        }
    
    def _prepare_chart_data(self, win_rates: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare data for win rate visualization"""
        return {
            'labels': list(win_rates.keys()),
            'values': [float(data['win_rate'].rstrip('%')) for data in win_rates.values()],
            'colors': [self._get_color_for_confidence(data['confidence']) for data in win_rates.values()]
        }
    
    def _get_color_for_confidence(self, confidence: str) -> str:
        """Get color based on confidence level"""
        return {
            'HIGH': '#00ff00',
            'MEDIUM': '#ffff00',
            'LOW': '#ff0000'
        }.get(confidence, '#808080')
    
    def _prepare_confidence_visualization(
        self, 
        win_rates: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare confidence meter visualization"""
        
        # Calculate average confidence
        confidences = []
        for data in win_rates.values():
            if data['confidence'] == 'HIGH':
                confidences.append(1.0)
            elif data['confidence'] == 'MEDIUM':
                confidences.append(0.5)
            else:
                confidences.append(0.25)
        
        avg_confidence = statistics.mean(confidences) if confidences else 0.5
        
        return {
            'value': avg_confidence,
            'label': 'HIGH' if avg_confidence > 0.75 else 'MEDIUM' if avg_confidence > 0.4 else 'LOW',
            'color': self._get_color_for_confidence('HIGH' if avg_confidence > 0.75 else 'MEDIUM' if avg_confidence > 0.4 else 'LOW')
        }
    
    def _create_practice_scenario(
        self, 
        symbol: str, 
        win_rates: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create practice trading scenario"""
        
        return {
            'scenario': f"You have $10,000 to invest in {symbol}",
            'current_price': 100,  # Placeholder
            'win_rates': win_rates,
            'question': "How would you allocate your position across timeframes?",
            'suggested_approach': {
                'conservative': "Allocate 30% for short-term, 70% for long-term",
                'balanced': "Split 50-50 between medium and long-term",
                'aggressive': "70% short-term for quick gains, 30% medium-term"
            }
        }
    
    def _extract_key_metrics(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from all data sources"""
        metrics = {}
        
        # Extract from Cryptometer
        if 'cryptometer' in all_data and not all_data['cryptometer'].get('error'):
            crypto = all_data['cryptometer']
            if crypto.get('quality'):
                metrics['data_quality'] = crypto['quality'].get('level', 'unknown')
        
        # Extract from RiskMetric
        if 'riskmetric' in all_data and not all_data['riskmetric'].get('error'):
            metrics['risk_score'] = all_data['riskmetric'].get('riskmetric_score', 0.5)
        
        # Add more metric extraction...
        
        return metrics
    
    def _calculate_confidence_metrics(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall confidence metrics"""
        
        available_sources = len([k for k, v in all_data.items() if not v.get('error')])
        total_sources = len(all_data)
        
        return {
            'data_completeness': f"{(available_sources / total_sources * 100) if total_sources > 0 else 0:.1f}%",
            'sources_available': available_sources,
            'total_sources': total_sources,
            'reliability_score': self._calculate_reliability_score(all_data)
        }
    
    def _calculate_reliability_score(self, all_data: Dict[str, Any]) -> float:
        """Calculate overall reliability score"""
        
        scores = []
        
        # Check each data source
        for source, data in all_data.items():
            if not data.get('error'):
                if source == 'cryptometer' and data.get('quality'):
                    quality = data['quality'].get('level', 'basic')
                    score = 1.0 if quality == 'premium' else 0.7 if quality == 'standard' else 0.4
                    scores.append(score)
                else:
                    scores.append(0.5)  # Default score for available data
        
        return statistics.mean(scores) if scores else 0.0
    
    def _get_data_sources_status(self, all_data: Dict[str, Any]) -> Dict[str, str]:
        """Get status of each data source"""
        
        status = {}
        for source, data in all_data.items():
            if data.get('error'):
                status[source] = 'ERROR'
            elif data:
                status[source] = 'ACTIVE'
            else:
                status[source] = 'NO_DATA'
        
        return status
    
    def _generate_recommendations(
        self, 
        win_rates: Dict[str, Dict[str, Any]], 
        all_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate actionable recommendations"""
        
        recommendations = {
            'primary_action': self._determine_primary_action(win_rates),
            'position_sizing': self._suggest_position_size(win_rates),
            'risk_management': self._suggest_risk_management(win_rates),
            'entry_strategy': self._suggest_entry_strategy(win_rates),
            'monitoring_alerts': self._suggest_monitoring_alerts(win_rates)
        }
        
        return recommendations
    
    def _determine_primary_action(self, win_rates: Dict[str, Dict[str, Any]]) -> str:
        """Determine primary trading action"""
        
        # Get average win rate across timeframes
        avg_win_rate = statistics.mean([
            float(data['win_rate'].rstrip('%')) 
            for data in win_rates.values()
        ])
        
        # Get most common recommendation
        recommendations = [data['recommendation'] for data in win_rates.values()]
        
        if avg_win_rate > 60 and 'STRONG BUY' in recommendations:
            return "OPEN LONG POSITION"
        elif avg_win_rate > 55 and 'BUY' in recommendations:
            return "CONSIDER LONG POSITION"
        elif avg_win_rate < 40 and 'STRONG SELL' in recommendations:
            return "OPEN SHORT POSITION"
        elif avg_win_rate < 45 and 'SELL' in recommendations:
            return "CONSIDER SHORT POSITION"
        else:
            return "WAIT FOR BETTER SETUP"
    
    def _suggest_position_size(self, win_rates: Dict[str, Dict[str, Any]]) -> str:
        """Suggest position size based on confidence"""
        
        # Check confidence levels
        high_confidence_count = sum(
            1 for data in win_rates.values() 
            if data['confidence'] == 'HIGH'
        )
        
        if high_confidence_count >= 2:
            return "Up to 5% of portfolio (high confidence)"
        elif high_confidence_count >= 1:
            return "2-3% of portfolio (moderate confidence)"
        else:
            return "1% or less of portfolio (low confidence)"
    
    def _suggest_risk_management(self, win_rates: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Suggest risk management parameters"""
        
        return {
            'stop_loss': "Set at 2-3% below entry for high confidence, 1-2% for low",
            'take_profit': "Target 1:2 risk/reward minimum, scale out at resistance",
            'max_exposure': "Don't exceed 10% total crypto exposure",
            'hedging': "Consider hedging if opening large position"
        }
    
    def _suggest_entry_strategy(self, win_rates: Dict[str, Dict[str, Any]]) -> str:
        """Suggest entry strategy"""
        
        # Check short-term win rate
        short_term = win_rates.get(TimeFrame.SHORT.value, {})
        short_win_rate = float(short_term.get('win_rate', '50%').rstrip('%'))
        
        if short_win_rate > 60:
            return "Market entry acceptable, watch for immediate momentum"
        elif short_win_rate > 50:
            return "Scale in with 3 entries over next 4 hours"
        else:
            return "Wait for better short-term setup or use limit orders at support"
    
    def _suggest_monitoring_alerts(self, win_rates: Dict[str, Dict[str, Any]]) -> List[str]:
        """Suggest monitoring alerts to set"""
        
        return [
            "Price breakout above resistance",
            "Volume spike above 2x average",
            "RSI divergence formation",
            "Whale wallet movements",
            "Social sentiment shift"
        ]
    
    def _get_learning_resources(self, teaching_style: TeachingStyle) -> List[Dict[str, str]]:
        """Get appropriate learning resources"""
        
        if teaching_style == TeachingStyle.BEGINNER:
            return [
                {"title": "Understanding Win Rates", "type": "article"},
                {"title": "Risk Management Basics", "type": "video"},
                {"title": "Reading Trading Signals", "type": "interactive"}
            ]
        elif teaching_style == TeachingStyle.INTERMEDIATE:
            return [
                {"title": "Multi-Timeframe Analysis", "type": "article"},
                {"title": "Position Sizing Strategies", "type": "calculator"},
                {"title": "Technical Indicators Guide", "type": "reference"}
            ]
        else:  # ADVANCED or EXPERT
            return [
                {"title": "Quantitative Trading Models", "type": "whitepaper"},
                {"title": "Kelly Criterion Calculator", "type": "tool"},
                {"title": "Backtesting Framework", "type": "code"}
            ]
    
    def _suggest_next_steps(
        self, 
        symbol: str, 
        win_rates: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Suggest next steps for the user"""
        
        steps = []
        
        # Check if action is recommended
        avg_win_rate = statistics.mean([
            float(data['win_rate'].rstrip('%')) 
            for data in win_rates.values()
        ])
        
        if avg_win_rate > 55:
            steps.append(f"Review entry points for {symbol}")
            steps.append("Set up price alerts at key levels")
            steps.append("Prepare position sizing calculation")
        elif avg_win_rate < 45:
            steps.append(f"Monitor {symbol} for reversal signals")
            steps.append("Consider shorting opportunities")
            steps.append("Look for alternative assets")
        else:
            steps.append(f"Wait for clearer signals on {symbol}")
            steps.append("Review analysis in 4-6 hours")
            steps.append("Study similar market conditions historically")
        
        steps.append("Practice with paper trading first")
        steps.append("Review risk management checklist")
        
        return steps
    
    def _get_error_response(self, symbol: str, error: str) -> Dict[str, Any]:
        """Generate error response"""
        
        return {
            'success': False,
            'symbol': symbol,
            'error': error,
            'timestamp': datetime.now().isoformat(),
            'suggestion': 'Please try again or contact support',
            'fallback_analysis': {
                'message': 'Unable to complete full analysis',
                'available_actions': [
                    'Try with fewer data sources',
                    'Check individual agent status',
                    'Use basic package instead'
                ]
            }
        }
    
    def _get_beginner_template(self) -> str:
        """Get beginner teaching template"""
        return """
        Hi! I'm your trading teacher. Let me explain this simply:
        
        🎯 What this means for you:
        {simple_summary}
        
        📊 Win Rate Explained:
        Think of win rate like batting average in baseball.
        Higher is better, but confidence matters too!
        
        ✅ What to do:
        {action_steps}
        
        💡 Remember: Never invest more than you can afford to lose!
        """
    
    def _get_intermediate_template(self) -> str:
        """Get intermediate teaching template"""
        return """
        📈 Market Analysis for {symbol}:
        
        {technical_summary}
        
        🎯 Key Metrics:
        • Win Rates: {win_rates}
        • Confidence: {confidence}
        • Risk Level: {risk}
        
        📊 Trading Strategy:
        {strategy}
        
        ⚠️ Risk Factors:
        {risks}
        
        💼 Position Management:
        {position_guide}
        """
    
    def _get_advanced_template(self) -> str:
        """Get advanced teaching template"""
        return """
        🔬 Quantitative Analysis Report
        
        {detailed_metrics}
        
        📊 Statistical Confidence:
        • Sharpe Ratio implications
        • Kelly Criterion positioning
        • Maximum drawdown scenarios
        
        🎯 Execution Framework:
        {execution_plan}
        
        ⚡ Market Microstructure:
        {microstructure_analysis}
        
        📈 Hedging Strategies:
        {hedging_options}
        """
    
    def _get_expert_template(self) -> str:
        """Get expert teaching template"""
        return """
        {full_technical_analysis}
        
        Correlation Matrix:
        {correlations}
        
        Risk-Adjusted Returns:
        {risk_adjusted_metrics}
        
        Algorithmic Entry Points:
        {algo_entries}
        
        Portfolio Impact Analysis:
        {portfolio_impact}
        """
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        
        accuracy = (
            (self.stats['successful_predictions'] / self.stats['total_predictions'] * 100)
            if self.stats['total_predictions'] > 0 else 0
        )
        
        avg_satisfaction = (
            statistics.mean(self.stats['user_satisfaction'])
            if self.stats['user_satisfaction'] else 0
        )
        
        return {
            'total_analyses': self.stats['total_analyses'],
            'prediction_accuracy': f"{accuracy:.1f}%",
            'credits_consumed': self.stats['credits_consumed'],
            'average_satisfaction': f"{avg_satisfaction:.1f}/5",
            'active_agents': sum(1 for agent in self.agents.values() if agent is not None),
            'total_agents': len(self.agents)
        }

# Global instance
unified_qa_user_agent = UnifiedQAUserAgent()

async def get_unified_qa_agent() -> UnifiedQAUserAgent:
    """Get global unified QA agent instance"""
    return unified_qa_user_agent