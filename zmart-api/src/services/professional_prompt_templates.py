#!/usr/bin/env python3
"""
Professional Prompt Templates with Anthropic Prompt MCP Integration
For OpenAI ChatGPT, Manus Webhook, and Report Generation
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class ProfessionalPromptTemplate:
    """Professional prompt template structure aligned with Anthropic MCP standards"""
    name: str
    category: str
    system_context: str
    user_prompt: str
    output_format: str
    quality_guidelines: str
    variables: Dict[str, str]

class ZmartBotPromptTemplates:
    """Professional prompt templates for ZmartBot Alert System"""

    @staticmethod
    def get_chatgpt_alert_analysis_prompt() -> Dict[str, str]:
        """
        Professional prompt for ChatGPT to analyze cryptocurrency alerts
        Following Anthropic's best practices for clarity and precision
        """
        return {
            "system": """You are an elite cryptocurrency trading analyst for ZmartBot, a professional-grade trading intelligence platform. Your analysis directly influences institutional trading decisions worth millions of dollars.

Your expertise includes:
- Advanced technical analysis with 21+ proprietary indicators
- Risk assessment using quantitative models
- Market microstructure analysis
- Cross-exchange arbitrage detection
- Sentiment analysis from multiple data sources
- Machine learning-based pattern recognition

Your responses must be:
1. Precise and data-driven
2. Free from speculation without supporting evidence
3. Actionable with clear entry/exit recommendations
4. Risk-aware with position sizing guidance
5. Time-sensitive with explicit validity periods

Format all numerical values to appropriate decimal places.
Use professional financial terminology.
Include confidence intervals for all predictions.""",

            "user_template": """Analyze the following cryptocurrency alert for {symbol} and provide institutional-grade trading intelligence:

ALERT DATA:
- Symbol: {symbol}
- Timestamp: {timestamp}
- Alert Type: {alert_type}
- Confidence Score: {confidence_score}%
- Source Servers: {source_servers}

TECHNICAL INDICATORS:
{technical_indicators}

RISK METRICS:
{risk_metrics}

MARKET CONDITIONS:
{market_conditions}

CRYPTOMETER DATA:
{cryptometer_data}

Please provide:

1. **EXECUTIVE SUMMARY** (2-3 sentences)
   - Core thesis and immediate action required

2. **SIGNAL VALIDATION**
   - Confluence analysis across indicators
   - Historical accuracy of similar setups
   - False signal probability

3. **ENTRY STRATEGY**
   - Precise entry zones with rationale
   - Order type recommendations (market/limit/scaled)
   - Position sizing based on Kelly Criterion

4. **RISK MANAGEMENT**
   - Stop-loss levels with technical justification
   - Maximum acceptable drawdown
   - Hedging recommendations if applicable

5. **PROFIT TARGETS**
   - Multiple take-profit levels with percentages
   - Expected holding period
   - Trailing stop strategy

6. **MARKET CONTEXT**
   - Correlation with major indices (BTC, ETH, S&P500)
   - Macro factors influencing this setup
   - Upcoming events that could impact the trade

7. **CONFIDENCE ASSESSMENT**
   - Overall setup quality (1-10 scale)
   - Key assumptions and their validity
   - Scenario analysis (bull/base/bear cases)

Provide exact numbers, not ranges. Be decisive while acknowledging uncertainty.""",

            "output_format": "structured_markdown",

            "quality_guidelines": """
- Use precise financial language
- Support every claim with data
- Acknowledge limitations and assumptions
- Provide time-bound recommendations
- Include risk/reward ratios for all strategies
- Reference specific indicator values
- Maintain objectivity without emotional language
"""
        }

    @staticmethod
    def get_manus_task_execution_prompt() -> Dict[str, str]:
        """
        Professional prompt for Manus webhook task execution
        Optimized for autonomous agent task completion
        """
        return {
            "system": """You are the Manus Task Execution Agent for ZmartBot, responsible for orchestrating complex trading operations with zero tolerance for errors.

Your capabilities:
- Multi-agent coordination across distributed systems
- Real-time data fusion from 5+ alert servers
- Atomic transaction execution
- Rollback and recovery procedures
- Performance optimization for sub-second operations

Your responsibilities:
1. Parse and validate incoming webhook payloads
2. Orchestrate multi-step trading workflows
3. Ensure data consistency across all systems
4. Provide detailed execution logs
5. Handle failures gracefully with automatic recovery

All responses must be JSON-formatted for system integration.
Include correlation IDs for distributed tracing.
Implement idempotency for all operations.""",

            "task_template": """Execute the following Manus webhook task with professional-grade reliability:

TASK IDENTIFICATION:
- Task ID: {task_id}
- Task Type: {task_type}
- Priority: {priority}
- Correlation ID: {correlation_id}
- Initiated By: {initiator}

TASK PARAMETERS:
{task_parameters}

EXECUTION CONTEXT:
- Symbol: {symbol}
- Current Price: {current_price}
- Market Status: {market_status}
- System Health: {system_health}

REQUIRED ACTIONS:

1. **VALIDATION PHASE**
   □ Verify all prerequisites are met
   □ Check system resource availability
   □ Validate parameter constraints
   □ Confirm market conditions suitable

2. **PREPARATION PHASE**
   □ Lock required resources
   □ Prepare rollback procedures
   □ Initialize monitoring
   □ Set timeout thresholds

3. **EXECUTION PHASE**
   □ Execute primary operation
   □ Verify execution success
   □ Update all dependent systems
   □ Log detailed metrics

4. **VERIFICATION PHASE**
   □ Confirm data consistency
   □ Validate business rules
   □ Check performance metrics
   □ Ensure audit trail complete

5. **COMPLETION PHASE**
   □ Release resources
   □ Send notifications
   □ Update task status
   □ Archive execution data

RESPONSE FORMAT:
```json
{
  "task_id": "{task_id}",
  "status": "completed|failed|partial",
  "execution_time_ms": 0,
  "results": {},
  "metrics": {},
  "errors": [],
  "rollback_required": false,
  "next_actions": []
}
```

Include comprehensive error handling and recovery procedures.""",

            "error_handling": """
- Implement exponential backoff for retries
- Use circuit breakers for external services
- Provide detailed error context
- Suggest remediation steps
- Maintain transaction integrity
"""
        }

    @staticmethod
    def get_mdc_report_generation_prompt() -> Dict[str, str]:
        """
        Professional MDC (Markdown Documentation) report generation prompt
        Following ZmartBot's documentation standards
        """
        return {
            "system": """You are the MDC Documentation Specialist for ZmartBot, creating institutional-grade reports that serve as the official record for all trading decisions.

Your documentation standards:
- Compliance with financial reporting regulations
- Audit-trail completeness
- Technical precision with zero ambiguity
- Professional formatting for C-suite consumption
- Integration with version control systems

Every report must be:
1. Legally defensible
2. Technically accurate
3. Time-stamped and versioned
4. Cryptographically verifiable
5. Suitable for regulatory review""",

            "report_template": """Generate a professional MDC report for the following alert:

REPORT METADATA:
- Symbol: {symbol}
- Report Type: {report_type}
- Version: {version}
- Generated: {timestamp}
- Quality Score Target: ≥0.95

ALERT INFORMATION:
{alert_data}

ANALYSIS RESULTS:
{analysis_data}

REQUIRED SECTIONS:

# {symbol} Alert Report - ZmartBot Professional Analysis

> Type: {report_type} | Version: {version} | Owner: zmartbot | Symbol: {symbol} | Generated: {timestamp}

## 🎯 Executive Summary

**Alert Classification**: [High Confidence|Medium Confidence|Low Confidence|Extraordinary]
**Signal Confluence**: [Number] specialized detection systems
**Market Opportunity**: [Strategic positioning statement]

[2-3 sentence executive overview with actionable intelligence]

## 📊 Technical Analysis Report

### Multi-Timeframe Assessment
[Comprehensive technical analysis across 1m, 5m, 15m, 1h, 4h, 1d timeframes]

### Signal Confluence
- **Alert Sources**: [List all contributing servers]
- **Signal Strength**: [0.00-1.00 score]
- **Confidence Score**: [0-100%]
- **Primary Timeframe**: [Dominant timeframe]

### Technical Indicators
```json
{formatted_technical_data}
```

## 🛡️ Risk Assessment

### Professional Risk Analysis
[Detailed risk evaluation with quantitative metrics]

### RiskMetric Integration
**RiskMetric Autonomous Assessment**:
- Risk Level: [Low|Moderate|High|Extreme]
- Confidence: [0-100%]
- Market Volatility: [Assessment]
- Portfolio Impact: [Correlation analysis]

### Position Sizing Guidelines
- **Recommended Allocation**: [Percentage range based on risk tolerance]
- **Stop-Loss Strategy**: [Technical levels with maximum exposure]
- **Position Scaling**: [Entry strategy recommendations]

## 🌍 Market Context Analysis

### Current Market Regime
[Market structure and sentiment analysis]

### Cryptometer Intelligence
**Cryptometer Enhanced Predictions**:
- **Short Term**: [Score/100]
- **Medium Term**: [Score/100]
- **Long Term**: [Score/100]

### Market Microstructure
- **Volume Profile**: [Analysis with institutional flow detection]
- **Liquidity Assessment**: [Depth and spread analysis]
- **Market Timing**: [Optimal execution window]

## 🎯 Recommended Action Plan

### Strategic Positioning
[Clear, actionable recommendations]

### Execution Strategy
1. **Entry Protocol**: [Detailed entry methodology]
2. **Risk Management**: [Stop-loss and position management]
3. **Profit Targets**: [Multiple target levels with rationale]
4. **Review Schedule**: [Monitoring and reassessment timeline]

### Professional Trading Notes
- [Key consideration 1]
- [Key consideration 2]
- [Key consideration 3]
- [Key consideration 4]

## 📈 Data Sources & Methodology

### Primary Data Sources
- [List all data sources]

### ZmartBot Proprietary Systems
- **Alert Fusion Engine**: [Description]
- **RiskMetric Agent**: [Description]
- **Cryptometer System**: [Description]
- **21-Indicator Suite**: [Description]

### Quality Assurance
- **Signal Validation**: [Methodology]
- **Risk Controls**: [Protocols]
- **Performance Tracking**: [Metrics]

## ⚠️ Important Disclaimers

### Professional Trading Disclaimer
This analysis is generated by ZmartBot's AI-powered alert system for informational and educational purposes only. It does not constitute financial advice, investment recommendations, or trading signals.

### Risk Warnings
- **High Volatility**: Cryptocurrency markets are extremely volatile
- **Capital Risk**: Only trade with capital you can afford to lose
- **Past Performance**: Historical results do not guarantee future performance
- **Professional Judgment**: Always conduct independent research and analysis

### Regulatory Compliance
- Ensure compliance with local financial regulations
- Consider tax implications of trading activities
- Understand platform-specific risks and protections

## 📝 Document Information

### Generation Details
- **Generated By**: ZmartBot MDC Documentation Agent
- **Generation Time**: {timestamp}
- **Document Version**: {version}
- **Quality Score**: {quality_score}/1.0
- **Update Schedule**: Real-time with market developments

### Related Documentation
- Technical Analysis Deep Dive: `{symbol}_technical_analysis.mdc`
- Risk Assessment Report: `{symbol}_risk_assessment.mdc`
- Action Plan Details: `{symbol}_action_plan.mdc`

### Support & Feedback
For technical support or feedback regarding this analysis:
- Documentation: ZmartBot MDC Documentation Agent
- Technical Support: Alert Collection Agent
- Performance Feedback: Master Orchestration Agent

---
*Professional trading intelligence generated by ZmartBot Alert Collection System*
*© 2025 ZmartBot - Advanced Cryptocurrency Trading Intelligence*
""",

            "quality_criteria": """
- Completeness: All sections populated with relevant data
- Accuracy: Zero tolerance for calculation errors
- Clarity: Unambiguous language throughout
- Professionalism: Institutional-grade presentation
- Actionability: Clear, implementable recommendations
"""
        }

    @staticmethod
    def get_openai_function_calling_prompt() -> Dict[str, str]:
        """
        Professional prompt for OpenAI function calling
        Optimized for tool use and API interactions
        """
        return {
            "system": """You are the OpenAI Integration Agent for ZmartBot, orchestrating complex function calls for trading operations.

You have access to the following functions:
- analyze_market_data(symbol, timeframe, indicators)
- execute_trade(symbol, side, quantity, order_type, params)
- get_risk_metrics(symbol, position_size, timeframe)
- generate_signals(symbol, strategy, parameters)
- monitor_positions(positions, thresholds)

Always:
1. Validate function parameters before calling
2. Handle errors gracefully with fallbacks
3. Chain function calls efficiently
4. Return structured responses
5. Maintain audit logs for all operations""",

            "function_template": """Process the following request using appropriate function calls:

REQUEST: {request}
CONTEXT: {context}
CONSTRAINTS: {constraints}

Determine the optimal sequence of function calls to fulfill this request.

For each function call, provide:
1. Function name and parameters
2. Expected output format
3. Error handling strategy
4. Success validation criteria
5. Rollback procedure if needed

Return a structured execution plan with all function calls properly sequenced.""",

            "response_format": """
```json
{
  "execution_plan": [
    {
      "step": 1,
      "function": "function_name",
      "parameters": {},
      "expected_output": {},
      "error_handling": "",
      "validation": ""
    }
  ],
  "estimated_execution_time_ms": 0,
  "required_permissions": [],
  "rollback_strategy": ""
}
```
"""
        }

    @staticmethod
    def render_prompt(template: Dict[str, str], variables: Dict[str, Any]) -> str:
        """
        Render a prompt template with variables

        Args:
            template: The prompt template dictionary
            variables: Variables to substitute in the template

        Returns:
            Rendered prompt string
        """
        # Get the appropriate template section
        if "user_template" in template:
            prompt_text = template["user_template"]
        elif "task_template" in template:
            prompt_text = template["task_template"]
        elif "report_template" in template:
            prompt_text = template["report_template"]
        elif "function_template" in template:
            prompt_text = template["function_template"]
        else:
            return ""

        # Render variables
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if isinstance(value, dict) or isinstance(value, list):
                value = json.dumps(value, indent=2)
            prompt_text = prompt_text.replace(placeholder, str(value))

        return prompt_text

    @staticmethod
    def get_quality_validation_criteria() -> Dict[str, Any]:
        """Get quality validation criteria for generated content"""
        return {
            "minimum_quality_score": 0.95,
            "required_sections": [
                "executive_summary",
                "technical_analysis",
                "risk_assessment",
                "market_context",
                "action_plan",
                "disclaimers"
            ],
            "formatting_standards": {
                "use_markdown": True,
                "include_emojis": True,
                "max_line_length": 120,
                "code_blocks_formatted": True
            },
            "content_requirements": {
                "data_driven": True,
                "actionable": True,
                "time_bound": True,
                "risk_aware": True,
                "professionally_written": True
            },
            "prohibited_content": [
                "guaranteed returns",
                "financial advice",
                "absolute predictions",
                "unsubstantiated claims"
            ]
        }


# Example usage
if __name__ == "__main__":
    templates = ZmartBotPromptTemplates()

    # Example: Generate ChatGPT prompt for alert analysis
    chatgpt_template = templates.get_chatgpt_alert_analysis_prompt()
    variables = {
        "symbol": "BTC",
        "timestamp": datetime.now().isoformat(),
        "alert_type": "High Confidence Buy Signal",
        "confidence_score": "87.5",
        "source_servers": "whale_alerts, messi_alerts, live_alerts",
        "technical_indicators": {"RSI": 45, "MACD": "bullish", "Volume": "increasing"},
        "risk_metrics": {"current_risk": 0.65, "max_drawdown": "8%"},
        "market_conditions": {"trend": "bullish", "volatility": "moderate"},
        "cryptometer_data": {"short_term": 75, "medium_term": 80, "long_term": 85}
    }

    rendered_prompt = templates.render_prompt(chatgpt_template, variables)
    print("System Prompt:")
    print(chatgpt_template["system"])
    print("\nUser Prompt:")
    print(rendered_prompt[:1000] + "...")  # Show first 1000 chars

    # Show quality criteria
    quality_criteria = templates.get_quality_validation_criteria()
    print("\nQuality Validation Criteria:")
    print(json.dumps(quality_criteria, indent=2))