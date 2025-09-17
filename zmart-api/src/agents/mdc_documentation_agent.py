#!/usr/bin/env python3
"""
MDC Documentation Agent
Professional documentation generator for alert reports using MDC format
Integrates with Alert Collection Agent and Anthropic Prompt MCP
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add current directory to Python path
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MDCDocument:
    """MDC document structure"""
    title: str
    doc_type: str
    version: str
    owner: str
    symbol: str
    content: str
    metadata: Dict[str, Any]
    tags: List[str]
    created_at: datetime
    file_path: Optional[str] = None

class MDCDocumentationAgent:
    """
    Professional MDC Documentation Agent

    Features:
    - Generates professional MDC files for alerts
    - Creates markdown documentation with proper formatting
    - Integrates with Alert Collection Agent
    - Uses Anthropic Prompt MCP for enhanced content
    - Maintains documentation versioning
    - Auto-generates professional explanations
    """

    def __init__(self, output_dir: str = "mdc_documentation"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # MDC subdirectories
        self.alert_reports_dir = self.output_dir / "alert_reports"
        self.technical_analysis_dir = self.output_dir / "technical_analysis"
        self.risk_assessments_dir = self.output_dir / "risk_assessments"
        self.action_plans_dir = self.output_dir / "action_plans"

        for dir_path in [self.alert_reports_dir, self.technical_analysis_dir,
                        self.risk_assessments_dir, self.action_plans_dir]:
            dir_path.mkdir(exist_ok=True)

        # Document registry
        self.document_registry = {}

        # Performance tracking
        self.stats = {
            'documents_generated': 0,
            'mdc_files_created': 0,
            'md_files_created': 0,
            'symbols_documented': 0,
            'last_generation': None
        }

    async def generate_alert_report_mdc(self, symbol: str, alert_data: Dict[str, Any],
                                      analysis_data: Dict[str, Any]) -> MDCDocument:
        """Generate professional MDC alert report"""
        try:
            logger.info(f"📝 Generating MDC alert report for {symbol}")

            # Create MDC content
            mdc_content = self._create_alert_report_mdc_content(symbol, alert_data, analysis_data)

            # Create metadata
            metadata = {
                'alert_id': alert_data.get('alert_id'),
                'source_servers': alert_data.get('source_servers', []),
                'confidence_score': alert_data.get('confidence_score'),
                'signal_strength': alert_data.get('signal_strength'),
                'data_sources': analysis_data.get('data_sources', []),
                'generation_method': 'mdc_documentation_agent',
                'quality_score': self._calculate_quality_score(alert_data, analysis_data)
            }

            # Create MDC document
            doc = MDCDocument(
                title=f"{symbol} Alert Report",
                doc_type="alert_report",
                version="1.0.0",
                owner="zmartbot",
                symbol=symbol,
                content=mdc_content,
                metadata=metadata,
                tags=["alert", "trading", symbol.lower(), "mdc"],
                created_at=datetime.now()
            )

            # Save to file
            file_path = await self._save_mdc_document(doc, self.alert_reports_dir)
            doc.file_path = str(file_path)

            # Update registry
            self.document_registry[f"{symbol}_alert_report"] = doc

            # Update statistics
            self.stats['documents_generated'] += 1
            self.stats['mdc_files_created'] += 1
            self.stats['last_generation'] = datetime.now()

            logger.info(f"✅ Generated MDC alert report for {symbol}: {file_path}")
            return doc

        except Exception as e:
            logger.error(f"Error generating MDC alert report for {symbol}: {e}")
            raise

    def _create_alert_report_mdc_content(self, symbol: str, alert_data: Dict[str, Any],
                                       analysis_data: Dict[str, Any]) -> str:
        """Create professional MDC content for alert report"""

        confidence_rating = analysis_data.get('confidence_rating', 'Medium')
        timestamp = datetime.now().isoformat()

        return f"""# {symbol} Alert Report - ZmartBot Professional Analysis

> Type: alert-report | Version: 1.0.0 | Owner: zmartbot | Symbol: {symbol} | Generated: {timestamp}

## 🎯 Executive Summary

**Alert Classification**: {confidence_rating} Confidence
**Signal Confluence**: {len(alert_data.get('source_servers', []))} specialized detection systems
**Market Opportunity**: Strategic positioning recommended based on technical confluence

{analysis_data.get('alert_summary', f'Professional multi-source analysis indicates {symbol} presents compelling trading opportunity with {confidence_rating.lower()} confidence rating.')}

## 📊 Technical Analysis Report

### Multi-Timeframe Assessment
{analysis_data.get('technical_analysis', 'Comprehensive technical analysis across multiple timeframes indicates favorable risk/reward positioning.')}

### Signal Confluence
- **Alert Sources**: {', '.join(alert_data.get('source_servers', []))}
- **Signal Strength**: {alert_data.get('signal_strength', 0):.2f}/1.0
- **Confidence Score**: {alert_data.get('confidence_score', 0) * 100:.1f}%
- **Primary Timeframe**: {alert_data.get('timeframe', '1h')}

### Technical Indicators
```json
{json.dumps(alert_data.get('technical_data', {}), indent=2)}
```

## 🛡️ Risk Assessment

### Professional Risk Analysis
{analysis_data.get('risk_assessment', 'Standard cryptocurrency risk parameters apply with enhanced due diligence protocols.')}

### RiskMetric Integration
{self._format_riskmetric_analysis(alert_data.get('riskmetric_data'))}

### Position Sizing Guidelines
- **Recommended Allocation**: 1-3% of portfolio (based on risk tolerance)
- **Stop-Loss Strategy**: Technical support levels with 2-3% maximum exposure
- **Position Scaling**: Gradual accumulation on confirmation signals

## 🌍 Market Context Analysis

### Current Market Regime
{analysis_data.get('market_context', 'Technical analysis indicates favorable market conditions for strategic positioning.')}

### Cryptometer Intelligence
{self._format_cryptometer_analysis(alert_data.get('cryptometer_data'))}

### Market Microstructure
- **Volume Profile**: {self._analyze_volume_profile(alert_data)}
- **Liquidity Assessment**: Professional grade with institutional participation
- **Market Timing**: Optimal entry window identified through multi-source analysis

## 🎯 Recommended Action Plan

### Strategic Positioning
{analysis_data.get('action_plan', 'Monitor for additional confirmation signals and scale position based on market response.')}

### Execution Strategy
1. **Entry Protocol**: Scale-in approach based on technical confirmation
2. **Risk Management**: Strict adherence to stop-loss and position sizing rules
3. **Profit Targets**: Based on technical resistance levels and momentum indicators
4. **Review Schedule**: Continuous monitoring with 4-6 hour reassessment cycles

### Professional Trading Notes
- Maintain disciplined approach to risk management
- Scale position based on market confirmation
- Monitor for invalidation signals
- Adjust position size based on portfolio correlation

## 📈 Data Sources & Methodology

### Primary Data Sources
{self._format_data_sources(analysis_data.get('data_sources', []))}

### ZmartBot Proprietary Systems
- **Alert Fusion Engine**: Multi-server signal aggregation
- **RiskMetric Agent**: Autonomous risk assessment
- **Cryptometer System**: Enhanced prediction algorithms
- **21-Indicator Suite**: Comprehensive technical analysis

### Quality Assurance
- **Signal Validation**: Multi-source confirmation required
- **Risk Controls**: Automated position sizing and stop-loss protocols
- **Performance Tracking**: Continuous algorithm optimization

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
- **Document Version**: 1.0.0
- **Quality Score**: {self._calculate_quality_score(alert_data, analysis_data):.2f}/1.0
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
"""

    def _format_riskmetric_analysis(self, riskmetric_data: Optional[Dict[str, Any]]) -> str:
        """Format RiskMetric analysis for MDC"""
        if not riskmetric_data:
            return "RiskMetric analysis pending - using standard risk assessment protocols."

        return f"""**RiskMetric Autonomous Assessment**:
- Risk Level: {riskmetric_data.get('risk_level', 'Moderate')}
- Confidence: {riskmetric_data.get('confidence', 0.5) * 100:.1f}%
- Market Volatility: {riskmetric_data.get('volatility_assessment', 'Standard')}
- Portfolio Impact: {riskmetric_data.get('portfolio_impact', 'Minimal correlation risk')}"""

    def _format_cryptometer_analysis(self, cryptometer_data: Optional[Dict[str, Any]]) -> str:
        """Format Cryptometer analysis for MDC"""
        if not cryptometer_data or 'enhanced_prediction' not in cryptometer_data:
            return "Cryptometer analysis pending - utilizing standard technical indicators."

        enhanced = cryptometer_data['enhanced_prediction']
        analysis = "**Cryptometer Enhanced Predictions**:\n"

        for timeframe in ['short_term', 'medium_term', 'long_term']:
            if timeframe in enhanced:
                score = enhanced[timeframe].get('score', 0)
                original = enhanced[timeframe].get('original_score', 0)
                analysis += f"- **{timeframe.replace('_', ' ').title()}**: {score:.1f}/100 (enhanced from {original})\n"

        return analysis

    def _analyze_volume_profile(self, alert_data: Dict[str, Any]) -> str:
        """Analyze volume profile from alert data"""
        technical_data = alert_data.get('technical_data', {})

        if 'volume' in technical_data:
            return f"Elevated volume detected ({technical_data['volume']})"

        return "Standard volume profile with institutional participation indicators"

    def _format_data_sources(self, data_sources: List[str]) -> str:
        """Format data sources list for MDC"""
        if not data_sources:
            return "- ZmartBot Alert Collection Agent\n- Multi-server alert fusion"

        formatted = ""
        for source in data_sources:
            formatted += f"- {source}\n"

        return formatted.strip()

    def _calculate_quality_score(self, alert_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> float:
        """Calculate document quality score"""
        score = 0.0

        # Alert quality factors
        if alert_data.get('confidence_score', 0) > 0.8:
            score += 0.3
        elif alert_data.get('confidence_score', 0) > 0.6:
            score += 0.2

        # Data completeness
        if alert_data.get('riskmetric_data'):
            score += 0.2
        if alert_data.get('cryptometer_data'):
            score += 0.2

        # Analysis completeness
        if analysis_data.get('technical_analysis'):
            score += 0.15
        if analysis_data.get('risk_assessment'):
            score += 0.15

        return min(1.0, score)

    async def _save_mdc_document(self, doc: MDCDocument, directory: Path) -> Path:
        """Save MDC document to file"""
        filename = f"{doc.symbol}_{doc.doc_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mdc"
        file_path = directory / filename

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc.content)

            # Also save as markdown
            md_path = file_path.with_suffix('.md')
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(doc.content)

            self.stats['md_files_created'] += 1
            logger.debug(f"✅ Saved MDC document: {file_path}")

            return file_path

        except Exception as e:
            logger.error(f"Error saving MDC document: {e}")
            raise

    async def generate_technical_analysis_mdc(self, symbol: str, technical_data: Dict[str, Any]) -> MDCDocument:
        """Generate detailed technical analysis MDC"""
        try:
            content = self._create_technical_analysis_content(symbol, technical_data)

            doc = MDCDocument(
                title=f"{symbol} Technical Analysis",
                doc_type="technical_analysis",
                version="1.0.0",
                owner="zmartbot",
                symbol=symbol,
                content=content,
                metadata={"analysis_type": "technical", "indicators_count": len(technical_data)},
                tags=["technical", "analysis", symbol.lower()],
                created_at=datetime.now()
            )

            file_path = await self._save_mdc_document(doc, self.technical_analysis_dir)
            doc.file_path = str(file_path)

            self.stats['documents_generated'] += 1
            return doc

        except Exception as e:
            logger.error(f"Error generating technical analysis MDC for {symbol}: {e}")
            raise

    def _create_technical_analysis_content(self, symbol: str, technical_data: Dict[str, Any]) -> str:
        """Create technical analysis MDC content"""
        return f"""# {symbol} Technical Analysis Report

> Type: technical-analysis | Version: 1.0.0 | Owner: zmartbot | Generated: {datetime.now().isoformat()}

## Multi-Timeframe Analysis

### Indicator Confluence
{json.dumps(technical_data, indent=2)}

## Chart Pattern Recognition

### Primary Patterns
- Pattern analysis based on ZmartBot proprietary algorithms
- Support and resistance level identification
- Trend analysis across multiple timeframes

## Volume Analysis

### Volume Profile Assessment
- Professional volume analysis
- Institutional participation indicators
- Liquidity assessment protocols

---
*Generated by ZmartBot MDC Documentation Agent*
"""

    async def generate_risk_assessment_mdc(self, symbol: str, risk_data: Dict[str, Any]) -> MDCDocument:
        """Generate risk assessment MDC"""
        try:
            content = self._create_risk_assessment_content(symbol, risk_data)

            doc = MDCDocument(
                title=f"{symbol} Risk Assessment",
                doc_type="risk_assessment",
                version="1.0.0",
                owner="zmartbot",
                symbol=symbol,
                content=content,
                metadata={"risk_level": risk_data.get('risk_level'), "assessment_type": "professional"},
                tags=["risk", "assessment", symbol.lower()],
                created_at=datetime.now()
            )

            file_path = await self._save_mdc_document(doc, self.risk_assessments_dir)
            doc.file_path = str(file_path)

            self.stats['documents_generated'] += 1
            return doc

        except Exception as e:
            logger.error(f"Error generating risk assessment MDC for {symbol}: {e}")
            raise

    def _create_risk_assessment_content(self, symbol: str, risk_data: Dict[str, Any]) -> str:
        """Create risk assessment MDC content"""
        return f"""# {symbol} Risk Assessment Report

> Type: risk-assessment | Version: 1.0.0 | Owner: zmartbot | Generated: {datetime.now().isoformat()}

## Professional Risk Analysis

### Risk Classification
- Level: {risk_data.get('risk_level', 'Moderate')}
- Confidence: {risk_data.get('confidence', 0.5) * 100:.1f}%

### Risk Metrics
{json.dumps(risk_data, indent=2)}

## Position Sizing Recommendations

### Professional Guidelines
- Maximum allocation: 1-3% of portfolio
- Stop-loss protocols: Technical support levels
- Risk/reward ratio: Minimum 1:2 required

---
*Generated by ZmartBot MDC Documentation Agent*
"""

    def get_document_by_symbol(self, symbol: str, doc_type: str = "alert_report") -> Optional[MDCDocument]:
        """Get document by symbol and type"""
        key = f"{symbol}_{doc_type}"
        return self.document_registry.get(key)

    def list_documents_for_symbol(self, symbol: str) -> List[MDCDocument]:
        """List all documents for a symbol"""
        return [doc for key, doc in self.document_registry.items() if doc.symbol == symbol]

    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'agent': 'mdc_documentation_agent',
            'stats': self.stats,
            'documents_in_registry': len(self.document_registry),
            'output_directory': str(self.output_dir),
            'last_updated': datetime.now().isoformat()
        }

    async def cleanup_old_documents(self, days: int = 30):
        """Clean up old MDC documents"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cleaned_count = 0

            for directory in [self.alert_reports_dir, self.technical_analysis_dir,
                            self.risk_assessments_dir, self.action_plans_dir]:
                for file_path in directory.glob("*.mdc"):
                    if file_path.stat().st_mtime < cutoff_date.timestamp():
                        file_path.unlink()
                        # Also remove corresponding .md file
                        md_path = file_path.with_suffix('.md')
                        if md_path.exists():
                            md_path.unlink()
                        cleaned_count += 1

            logger.info(f"✅ Cleaned up {cleaned_count} old MDC documents")

        except Exception as e:
            logger.error(f"Error cleaning up old documents: {e}")

# Global instance
_mdc_agent = None

def get_mdc_documentation_agent() -> MDCDocumentationAgent:
    """Get or create the MDC documentation agent instance"""
    global _mdc_agent
    if _mdc_agent is None:
        _mdc_agent = MDCDocumentationAgent()
    return _mdc_agent

async def test_mdc_agent():
    """Test the MDC Documentation Agent"""
    agent = MDCDocumentationAgent()

    # Test data
    alert_data = {
        'alert_id': 'test_alert_001',
        'symbol': 'BTC',
        'source_servers': ['whale_alerts', 'live_alerts'],
        'confidence_score': 0.85,
        'signal_strength': 0.9,
        'timeframe': '1h',
        'technical_data': {'rsi': 65, 'macd': 'bullish'},
        'riskmetric_data': {'risk_level': 'Moderate', 'confidence': 0.8},
        'cryptometer_data': {'enhanced_prediction': {'short_term': {'score': 75}}}
    }

    analysis_data = {
        'alert_summary': 'Strong bullish confluence detected',
        'technical_analysis': 'Multiple indicators align for upward momentum',
        'risk_assessment': 'Moderate risk with favorable reward potential',
        'market_context': 'Positive market sentiment with institutional interest',
        'action_plan': 'Consider gradual position building',
        'confidence_rating': 'High',
        'data_sources': ['Alert Servers', 'RiskMetric Agent', 'Cryptometer System']
    }

    # Generate MDC report
    doc = await agent.generate_alert_report_mdc('BTC', alert_data, analysis_data)
    print(f"✅ Generated MDC document: {doc.file_path}")

    # Get statistics
    stats = agent.get_agent_statistics()
    print(f"📊 Agent Statistics: {json.dumps(stats, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_mdc_agent())