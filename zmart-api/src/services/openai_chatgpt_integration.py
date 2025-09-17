#!/usr/bin/env python3
"""
OpenAI ChatGPT Integration for ZmartBot Alert System
Professional-grade integration with GPT-4 for advanced trading analysis
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import aiohttp
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ChatGPTAnalysisResult:
    """Structure for ChatGPT analysis results"""
    symbol: str
    timestamp: datetime
    executive_summary: str
    signal_validation: Dict[str, Any]
    entry_strategy: Dict[str, Any]
    risk_management: Dict[str, Any]
    profit_targets: Dict[str, Any]
    market_context: Dict[str, Any]
    confidence_assessment: Dict[str, Any]
    raw_response: str
    tokens_used: int
    response_time_ms: int
    quality_score: float


class OpenAIChatGPTIntegration:
    """
    Professional OpenAI ChatGPT integration for ZmartBot

    Features:
    - GPT-4 for advanced trading analysis
    - Professional prompt templates
    - Structured response parsing
    - Quality validation
    - Error handling and retries
    - Token usage optimization
    """

    def __init__(self):
        """Initialize OpenAI ChatGPT integration"""
        self.api_key = os.getenv('OPENAI_API_KEY')

        if not self.api_key:
            logger.warning("OpenAI API key not found - ChatGPT integration disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("✅ OpenAI ChatGPT integration initialized")

        # Configuration
        self.model = "gpt-4-turbo-preview"  # Use latest GPT-4 model
        self.max_tokens = 4000
        self.temperature = 0.7  # Balance between creativity and consistency
        self.api_url = "https://api.openai.com/v1/chat/completions"

        # Import professional templates
        try:
            from src.services.professional_prompt_templates import ZmartBotPromptTemplates
            self.templates = ZmartBotPromptTemplates()
            logger.info("✅ Professional prompt templates loaded")
        except ImportError:
            logger.error("Could not import professional prompt templates")
            self.templates = None

        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'total_tokens_used': 0,
            'average_response_time_ms': 0,
            'average_quality_score': 0
        }

    async def analyze_alert_with_chatgpt(
        self,
        symbol: str,
        alert_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        risk_data: Optional[Dict[str, Any]] = None,
        cryptometer_data: Optional[Dict[str, Any]] = None
    ) -> Optional[ChatGPTAnalysisResult]:
        """
        Analyze cryptocurrency alert using ChatGPT with professional prompts

        Args:
            symbol: Trading symbol (e.g., 'BTC', 'ETH')
            alert_data: Alert information from collection system
            technical_data: Technical indicators and analysis
            risk_data: RiskMetric data if available
            cryptometer_data: Cryptometer predictions if available

        Returns:
            ChatGPTAnalysisResult with comprehensive trading intelligence
        """
        if not self.enabled:
            logger.warning("ChatGPT integration not enabled")
            return None

        start_time = datetime.now()
        self.metrics['total_requests'] += 1

        try:
            # Prepare professional prompt
            prompt = self._prepare_professional_prompt(
                symbol, alert_data, technical_data, risk_data, cryptometer_data
            )

            # Make API request to ChatGPT
            response = await self._call_chatgpt_api(prompt)

            if not response:
                self.metrics['failed_analyses'] += 1
                return None

            # Parse structured response
            analysis_result = self._parse_chatgpt_response(symbol, response, start_time)

            # Validate quality
            quality_score = self._validate_analysis_quality(analysis_result)
            analysis_result.quality_score = quality_score

            # Update metrics
            self._update_metrics(analysis_result)

            logger.info(f"✅ ChatGPT analysis completed for {symbol} - Quality: {quality_score:.2f}")
            return analysis_result

        except Exception as e:
            logger.error(f"Error in ChatGPT analysis for {symbol}: {e}")
            self.metrics['failed_analyses'] += 1
            return None

    def _prepare_professional_prompt(
        self,
        symbol: str,
        alert_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        risk_data: Optional[Dict[str, Any]],
        cryptometer_data: Optional[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Prepare professional prompt for ChatGPT"""

        if not self.templates:
            # Fallback to basic prompt
            return self._prepare_basic_prompt(symbol, alert_data, technical_data)

        # Get professional template
        chatgpt_template = self.templates.get_chatgpt_alert_analysis_prompt()

        # Prepare variables for template
        variables = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'alert_type': alert_data.get('alert_type', 'Signal Alert'),
            'confidence_score': f"{alert_data.get('confidence_score', 0) * 100:.1f}",
            'source_servers': ', '.join(alert_data.get('source_servers', ['unknown'])),
            'technical_indicators': technical_data or {},
            'risk_metrics': risk_data or {'current_risk': 'N/A', 'max_drawdown': 'N/A'},
            'market_conditions': alert_data.get('market_conditions', {'trend': 'unknown'}),
            'cryptometer_data': cryptometer_data or {'short_term': 'N/A', 'medium_term': 'N/A', 'long_term': 'N/A'}
        }

        # Render the prompt
        user_prompt = self.templates.render_prompt(chatgpt_template, variables)

        return {
            'system': chatgpt_template['system'],
            'user': user_prompt
        }

    def _prepare_basic_prompt(
        self,
        symbol: str,
        alert_data: Dict[str, Any],
        technical_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Prepare basic prompt as fallback"""
        return {
            'system': "You are a professional cryptocurrency trading analyst.",
            'user': f"""Analyze this {symbol} alert:

Alert Data: {json.dumps(alert_data, indent=2)}
Technical Data: {json.dumps(technical_data, indent=2)}

Provide trading recommendations with entry, exit, and risk management strategies."""
        }

    async def _call_chatgpt_api(self, prompt: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Make API call to OpenAI ChatGPT"""

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': prompt['system']},
                {'role': 'user', 'content': prompt['user']}
            ],
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'response_format': {'type': 'text'}  # Ensure text response
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:

                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"ChatGPT API error: {response.status} - {error_text}")
                        return None

                    data = await response.json()
                    return data

        except asyncio.TimeoutError:
            logger.error("ChatGPT API request timed out")
            return None
        except Exception as e:
            logger.error(f"ChatGPT API request failed: {e}")
            return None

    def _parse_chatgpt_response(
        self,
        symbol: str,
        response: Dict[str, Any],
        start_time: datetime
    ) -> ChatGPTAnalysisResult:
        """Parse ChatGPT response into structured result"""

        # Extract the actual response text
        response_text = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        tokens_used = response.get('usage', {}).get('total_tokens', 0)

        # Calculate response time
        response_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        # Parse structured sections from response
        parsed_data = self._extract_sections_from_response(response_text)

        return ChatGPTAnalysisResult(
            symbol=symbol,
            timestamp=datetime.now(),
            executive_summary=parsed_data.get('executive_summary', ''),
            signal_validation=parsed_data.get('signal_validation', {}),
            entry_strategy=parsed_data.get('entry_strategy', {}),
            risk_management=parsed_data.get('risk_management', {}),
            profit_targets=parsed_data.get('profit_targets', {}),
            market_context=parsed_data.get('market_context', {}),
            confidence_assessment=parsed_data.get('confidence_assessment', {}),
            raw_response=response_text,
            tokens_used=tokens_used,
            response_time_ms=response_time_ms,
            quality_score=0.0  # Will be set by validation
        )

    def _extract_sections_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract structured sections from ChatGPT response"""

        sections = {
            'executive_summary': '',
            'signal_validation': {},
            'entry_strategy': {},
            'risk_management': {},
            'profit_targets': {},
            'market_context': {},
            'confidence_assessment': {}
        }

        # Simple extraction based on section headers
        # In production, use more sophisticated parsing

        current_section = None
        current_content = []

        for line in response_text.split('\n'):
            # Check for section headers
            if '**EXECUTIVE SUMMARY**' in line or '## Executive Summary' in line:
                current_section = 'executive_summary'
                current_content = []
            elif '**SIGNAL VALIDATION**' in line or '## Signal Validation' in line:
                current_section = 'signal_validation'
                current_content = []
            elif '**ENTRY STRATEGY**' in line or '## Entry Strategy' in line:
                current_section = 'entry_strategy'
                current_content = []
            elif '**RISK MANAGEMENT**' in line or '## Risk Management' in line:
                current_section = 'risk_management'
                current_content = []
            elif '**PROFIT TARGETS**' in line or '## Profit Targets' in line:
                current_section = 'profit_targets'
                current_content = []
            elif '**MARKET CONTEXT**' in line or '## Market Context' in line:
                current_section = 'market_context'
                current_content = []
            elif '**CONFIDENCE ASSESSMENT**' in line or '## Confidence Assessment' in line:
                current_section = 'confidence_assessment'
                current_content = []
            elif current_section:
                current_content.append(line)

                # Store accumulated content
                if current_section == 'executive_summary':
                    sections[current_section] = '\n'.join(current_content).strip()
                else:
                    # For other sections, try to parse as structured data
                    content = '\n'.join(current_content).strip()
                    if content:
                        sections[current_section] = self._parse_section_content(content)

        return sections

    def _parse_section_content(self, content: str) -> Dict[str, Any]:
        """Parse section content into structured data"""

        result = {}

        # Parse bullet points and key-value pairs
        for line in content.split('\n'):
            if ':' in line:
                key_value = line.split(':', 1)
                if len(key_value) == 2:
                    key = key_value[0].strip().replace('-', '').replace('*', '').strip()
                    value = key_value[1].strip()
                    result[key.lower().replace(' ', '_')] = value

        return result if result else {'content': content}

    def _validate_analysis_quality(self, analysis: ChatGPTAnalysisResult) -> float:
        """Validate the quality of ChatGPT analysis"""

        quality_score = 0.0
        checks_passed = 0
        total_checks = 7

        # Check for required sections
        if analysis.executive_summary and len(analysis.executive_summary) > 50:
            checks_passed += 1
        if analysis.signal_validation:
            checks_passed += 1
        if analysis.entry_strategy:
            checks_passed += 1
        if analysis.risk_management:
            checks_passed += 1
        if analysis.profit_targets:
            checks_passed += 1
        if analysis.market_context:
            checks_passed += 1
        if analysis.confidence_assessment:
            checks_passed += 1

        quality_score = checks_passed / total_checks

        # Adjust for response quality
        if analysis.tokens_used > 1000:  # Good detailed response
            quality_score = min(1.0, quality_score + 0.1)
        if analysis.response_time_ms < 5000:  # Fast response
            quality_score = min(1.0, quality_score + 0.05)

        return quality_score

    def _update_metrics(self, analysis: ChatGPTAnalysisResult):
        """Update performance metrics"""

        self.metrics['successful_analyses'] += 1
        self.metrics['total_tokens_used'] += analysis.tokens_used

        # Update rolling averages
        total = self.metrics['successful_analyses']

        self.metrics['average_response_time_ms'] = (
            (self.metrics['average_response_time_ms'] * (total - 1) + analysis.response_time_ms) / total
        )

        self.metrics['average_quality_score'] = (
            (self.metrics['average_quality_score'] * (total - 1) + analysis.quality_score) / total
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.metrics

    async def generate_trading_report(
        self,
        symbol: str,
        analysis: ChatGPTAnalysisResult
    ) -> str:
        """Generate professional trading report from ChatGPT analysis"""

        report = f"""# {symbol} Trading Intelligence Report - Powered by GPT-4

## 📊 Executive Summary
{analysis.executive_summary}

## ✅ Signal Validation
{self._format_dict_as_markdown(analysis.signal_validation)}

## 📈 Entry Strategy
{self._format_dict_as_markdown(analysis.entry_strategy)}

## 🛡️ Risk Management
{self._format_dict_as_markdown(analysis.risk_management)}

## 🎯 Profit Targets
{self._format_dict_as_markdown(analysis.profit_targets)}

## 🌍 Market Context
{self._format_dict_as_markdown(analysis.market_context)}

## 📊 Confidence Assessment
{self._format_dict_as_markdown(analysis.confidence_assessment)}

---
*Analysis Quality Score: {analysis.quality_score:.2f}/1.0*
*Response Time: {analysis.response_time_ms}ms*
*Tokens Used: {analysis.tokens_used}*
*Generated: {analysis.timestamp.isoformat()}*
"""
        return report

    def _format_dict_as_markdown(self, data: Dict[str, Any]) -> str:
        """Format dictionary as markdown list"""

        if not data:
            return "No data available"

        lines = []
        for key, value in data.items():
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"- **{formatted_key}**: {value}")

        return '\n'.join(lines)


# Example usage and testing
if __name__ == "__main__":
    async def test_chatgpt_integration():
        """Test ChatGPT integration"""

        # Initialize integration
        chatgpt = OpenAIChatGPTIntegration()

        if not chatgpt.enabled:
            print("❌ ChatGPT integration not enabled - set OPENAI_API_KEY environment variable")
            return

        # Test data
        test_symbol = "BTC"
        test_alert = {
            'alert_type': 'High Confidence Buy Signal',
            'confidence_score': 0.875,
            'source_servers': ['whale_alerts', 'messi_alerts'],
            'market_conditions': {'trend': 'bullish', 'volatility': 'moderate'}
        }

        test_technical = {
            'RSI': 45,
            'MACD': 'bullish crossover',
            'Volume': 'increasing',
            'Support': 95000,
            'Resistance': 105000
        }

        test_risk = {
            'current_risk': 0.65,
            'max_drawdown': '8%',
            'var_95': '12%'
        }

        test_cryptometer = {
            'short_term': 75,
            'medium_term': 80,
            'long_term': 85
        }

        # Run analysis
        print(f"🔍 Analyzing {test_symbol} with ChatGPT...")
        result = await chatgpt.analyze_alert_with_chatgpt(
            test_symbol, test_alert, test_technical, test_risk, test_cryptometer
        )

        if result:
            # Generate report
            report = await chatgpt.generate_trading_report(test_symbol, result)
            print(report)

            # Show metrics
            metrics = chatgpt.get_metrics()
            print("\n📊 Performance Metrics:")
            print(json.dumps(metrics, indent=2))
        else:
            print("❌ Analysis failed")

    # Run test
    asyncio.run(test_chatgpt_integration())