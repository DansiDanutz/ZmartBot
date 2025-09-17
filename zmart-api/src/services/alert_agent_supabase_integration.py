#!/usr/bin/env python3
"""
Alert Agent Supabase Integration Service
Enhanced service with Anthropic Prompt MCP integration for professional alert management
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import aiohttp

# Add current directory to Python path
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Supabase client with fallback
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    logger.warning("Supabase not available - using local storage only")
    SUPABASE_AVAILABLE = False

@dataclass
class PromptTemplate:
    """Anthropic Prompt MCP template structure"""
    name: str
    template_type: str
    content: str
    variables: Dict[str, str]
    example_usage: str
    performance_rating: float = 0.0
    usage_count: int = 0

class AlertAgentSupabaseIntegration:
    """
    Enhanced Alert Agent with Supabase integration and Anthropic Prompt MCP

    Features:
    - Professional Supabase database integration
    - Anthropic Prompt MCP for enhanced prompting
    - Advanced MDC documentation generation
    - Manus extraordinary analysis integration
    - Real-time alert synchronization
    - Performance analytics and monitoring
    """

    def __init__(self, config_path: str = "alert_agent_config.json"):
        self.config = self._load_config(config_path)

        # Supabase configuration
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
        self.supabase_client: Optional[Client] = None

        # Anthropic Prompt MCP integration
        self.prompt_templates: Dict[str, PromptTemplate] = {}
        self.templates_loaded = False

        # Initialize connections
        self._init_supabase()

        # Performance tracking
        self.performance_metrics = {
            'supabase_operations': 0,
            'prompt_generations': 0,
            'mdc_documents_created': 0,
            'manus_reports_generated': 0,
            'last_sync': None,
            'errors': 0
        }

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load enhanced configuration"""
        default_config = {
            'supabase_enabled': True,
            'mcp_prompting_enabled': True,
            'manus_integration_enabled': True,
            'batch_size': 50,
            'sync_interval_minutes': 5,
            'prompt_optimization_enabled': True,
            'performance_tracking_enabled': True,
            'mdc_auto_generation': True
        }

        try:
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
        except Exception as e:
            logger.warning(f"Could not load config: {e}")

        return default_config

    def _init_supabase(self):
        """Initialize Supabase client"""
        if not SUPABASE_AVAILABLE or not self.config['supabase_enabled']:
            logger.warning("Supabase integration disabled")
            return

        if not self.supabase_url or not self.supabase_key:
            logger.error("Missing Supabase credentials")
            return

        try:
            self.supabase_client = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Supabase client initialized successfully")

            # Load prompt templates - will be loaded on first use
            self.templates_loaded = False

        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")

    async def _load_prompt_templates(self):
        """Load prompt templates from Supabase"""
        if not self.supabase_client:
            return

        try:
            response = self.supabase_client.table('prompt_templates').select('*').eq('is_active', True).execute()

            for template_data in response.data:
                template = PromptTemplate(
                    name=template_data['template_name'],
                    template_type=template_data['template_type'],
                    content=template_data['template_content'],
                    variables=template_data.get('variables', {}),
                    example_usage=template_data.get('example_usage', ''),
                    performance_rating=template_data.get('performance_rating', 0.0),
                    usage_count=template_data.get('usage_count', 0)
                )
                self.prompt_templates[template.name] = template

            logger.info(f"✅ Loaded {len(self.prompt_templates)} prompt templates")

        except Exception as e:
            logger.error(f"Error loading prompt templates: {e}")

    async def sync_alert_to_supabase(self, alert_data: Dict[str, Any]) -> bool:
        """Sync alert data to Supabase"""
        if not self.supabase_client:
            return False

        try:
            # Prepare alert data for Supabase
            supabase_alert = {
                'alert_id': alert_data['alert_id'],
                'symbol': alert_data['symbol'],
                'alert_type': alert_data['alert_type'],
                'source_server': alert_data['source_server'],
                'timestamp': alert_data['timestamp'],
                'timeframe': alert_data.get('timeframe'),
                'signal_strength': alert_data.get('signal_strength'),
                'confidence_score': alert_data.get('confidence_score'),
                'technical_data': alert_data.get('technical_data', {}),
                'riskmetric_data': alert_data.get('riskmetric_data'),
                'cryptometer_data': alert_data.get('cryptometer_data'),
                'market_conditions': alert_data.get('market_conditions', {}),
                'action_recommendation': alert_data.get('action_recommendation'),
                'priority_level': alert_data.get('priority_level'),
                'status': alert_data.get('status', 'collected')
            }

            # Insert or update alert
            response = self.supabase_client.table('alert_collections').upsert(
                supabase_alert,
                on_conflict='alert_id'
            ).execute()

            if response.data:
                self.performance_metrics['supabase_operations'] += 1
                logger.debug(f"✅ Synced alert {alert_data['alert_id']} to Supabase")
                return True

        except Exception as e:
            logger.error(f"Error syncing alert to Supabase: {e}")
            self.performance_metrics['errors'] += 1

        return False

    async def sync_alert_report_to_supabase(self, report_data: Dict[str, Any]) -> bool:
        """Sync alert report to Supabase"""
        if not self.supabase_client:
            return False

        try:
            # Prepare report data for Supabase
            supabase_report = {
                'symbol': report_data['symbol'],
                'alert_summary': report_data['alert_summary'],
                'technical_analysis': report_data.get('technical_analysis'),
                'risk_assessment': report_data.get('risk_assessment'),
                'market_context': report_data.get('market_context'),
                'action_plan': report_data.get('action_plan'),
                'confidence_rating': report_data.get('confidence_rating'),
                'mdc_content': report_data.get('mdc_content'),
                'md_content': report_data.get('md_content'),
                'data_sources': report_data.get('data_sources', []),
                'is_active': True
            }

            # Deactivate old reports for this symbol
            self.supabase_client.table('alert_reports').update({
                'is_active': False
            }).eq('symbol', report_data['symbol']).eq('is_active', True).execute()

            # Insert new report
            response = self.supabase_client.table('alert_reports').insert(
                supabase_report
            ).execute()

            if response.data:
                self.performance_metrics['supabase_operations'] += 1
                logger.debug(f"✅ Synced report for {report_data['symbol']} to Supabase")
                return True

        except Exception as e:
            logger.error(f"Error syncing report to Supabase: {e}")
            self.performance_metrics['errors'] += 1

        return False

    async def generate_mdc_content_with_mcp(self, symbol: str, alert_data: Dict[str, Any],
                                          analysis_data: Dict[str, Any]) -> str:
        """Generate MDC content using Anthropic Prompt MCP"""
        try:
            # Ensure templates are loaded
            if not self.templates_loaded:
                await self._load_prompt_templates()
                self.templates_loaded = True

            # Get MDC generation template
            template = self.prompt_templates.get('mdc_alert_report')
            if not template:
                logger.warning("MDC template not found, using fallback")
                return self._generate_fallback_mdc(symbol, alert_data, analysis_data)

            # Prepare template variables
            variables = {
                'symbol': symbol,
                'version': '1.0.0',
                'owner': 'zmartbot',
                'timestamp': datetime.now().isoformat(),
                'alert_summary': analysis_data.get('alert_summary', ''),
                'technical_analysis': analysis_data.get('technical_analysis', ''),
                'risk_assessment': analysis_data.get('risk_assessment', ''),
                'market_context': analysis_data.get('market_context', ''),
                'action_plan': analysis_data.get('action_plan', ''),
                'data_sources': json.dumps(analysis_data.get('data_sources', [])),
                'confidence_rating': analysis_data.get('confidence_rating', 'Medium')
            }

            # Generate MDC content using template
            mdc_content = self._render_template(template.content, variables)

            # Update template usage statistics
            await self._update_template_usage(template.name)

            self.performance_metrics['mdc_documents_created'] += 1
            logger.info(f"✅ Generated MDC content for {symbol} using MCP")

            return mdc_content

        except Exception as e:
            logger.error(f"Error generating MDC content with MCP: {e}")
            return self._generate_fallback_mdc(symbol, alert_data, analysis_data)

    def _render_template(self, template_content: str, variables: Dict[str, str]) -> str:
        """Render template with variables using simple substitution"""
        try:
            rendered = template_content
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                rendered = rendered.replace(placeholder, str(value))
            return rendered
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return template_content

    async def _update_template_usage(self, template_name: str):
        """Update template usage statistics"""
        if not self.supabase_client:
            return

        try:
            self.supabase_client.table('prompt_templates').update({
                'usage_count': self.prompt_templates[template_name].usage_count + 1,
                'updated_at': datetime.now().isoformat()
            }).eq('template_name', template_name).execute()

            # Update local cache
            if template_name in self.prompt_templates:
                self.prompt_templates[template_name].usage_count += 1

        except Exception as e:
            logger.error(f"Error updating template usage: {e}")

    def _generate_fallback_mdc(self, symbol: str, alert_data: Dict[str, Any],
                              analysis_data: Dict[str, Any]) -> str:
        """Generate fallback MDC content using professional templates"""
        # Import professional templates
        try:
            from src.services.professional_prompt_templates import ZmartBotPromptTemplates
            templates = ZmartBotPromptTemplates()
            mdc_template = templates.get_mdc_report_generation_prompt()

            # Prepare variables for template
            variables = {
                'symbol': symbol,
                'report_type': 'alert-report',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat(),
                'alert_data': json.dumps(alert_data, indent=2),
                'analysis_data': json.dumps(analysis_data, indent=2),
                'quality_score': '0.95',
                'formatted_technical_data': json.dumps(
                    analysis_data.get('technical_data', {}), indent=2
                )
            }

            # Render the professional template
            rendered_content = templates.render_prompt(mdc_template, variables)

            # If rendering successful, use it; otherwise fall back to simple version
            if rendered_content:
                return rendered_content
        except Exception as e:
            logger.warning(f"Could not use professional template: {e}")

        # Simple fallback if professional template fails
        return f"""# {symbol} Alert Report - ZmartBot Professional Analysis

> Type: alert-report | Version: 1.0.0 | Owner: zmartbot | Generated: {datetime.now().isoformat()}

## Executive Summary

{analysis_data.get('alert_summary', f'Professional analysis for {symbol} based on multi-source alert fusion.')}

## Technical Analysis

{analysis_data.get('technical_analysis', 'Technical analysis based on ZmartBot proprietary indicators.')}

## Risk Assessment

{analysis_data.get('risk_assessment', 'Standard risk assessment protocols applied.')}

## Market Context

{analysis_data.get('market_context', 'Current market conditions analyzed for optimal positioning.')}

## Recommended Actions

{analysis_data.get('action_plan', 'Monitor for confirmation signals and maintain risk management protocols.')}

## Data Sources

- ZmartBot Alert Collection Agent
- Multi-server alert fusion
- Technical analysis suite

---
*Generated by ZmartBot Alert Collection Agent | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    async def generate_manus_prompt_with_mcp(self, alert_data: Dict[str, Any]) -> str:
        """Generate Manus analysis prompt using Anthropic Prompt MCP"""
        try:
            # Ensure templates are loaded
            if not self.templates_loaded:
                await self._load_prompt_templates()
                self.templates_loaded = True

            # Get Manus analysis template
            template = self.prompt_templates.get('manus_extraordinary_analysis')
            if not template:
                logger.warning("Manus template not found, using fallback")
                return self._generate_fallback_manus_prompt(alert_data)

            # Prepare template variables
            variables = {
                'symbol': alert_data.get('symbol', ''),
                'confidence_score': str(alert_data.get('confidence_score', 0) * 100),
                'signal_strength': str(alert_data.get('signal_strength', 0)),
                'source_server': alert_data.get('source_server', ''),
                'timeframe': alert_data.get('timeframe', ''),
                'technical_data': json.dumps(alert_data.get('technical_data', {}), indent=2),
                'riskmetric_data': json.dumps(alert_data.get('riskmetric_data', {}), indent=2),
                'cryptometer_data': json.dumps(alert_data.get('cryptometer_data', {}), indent=2),
                'market_conditions': json.dumps(alert_data.get('market_conditions', {}), indent=2)
            }

            # Generate prompt using template
            manus_prompt = self._render_template(template.content, variables)

            # Update template usage
            await self._update_template_usage(template.name)

            self.performance_metrics['prompt_generations'] += 1
            logger.info(f"✅ Generated Manus prompt for {alert_data.get('symbol')} using MCP")

            return manus_prompt

        except Exception as e:
            logger.error(f"Error generating Manus prompt with MCP: {e}")
            return self._generate_fallback_manus_prompt(alert_data)

    def _generate_fallback_manus_prompt(self, alert_data: Dict[str, Any]) -> str:
        """Generate fallback Manus prompt using professional templates"""
        # Import professional templates
        try:
            from src.services.professional_prompt_templates import ZmartBotPromptTemplates
            templates = ZmartBotPromptTemplates()
            manus_template = templates.get_manus_task_execution_prompt()

            # Prepare variables for Manus task
            variables = {
                'task_id': f"alert_{alert_data.get('symbol', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'task_type': 'extraordinary_alert_analysis',
                'priority': 'HIGH' if alert_data.get('confidence_score', 0) > 0.85 else 'MEDIUM',
                'correlation_id': f"corr_{alert_data.get('symbol', '')}_{int(datetime.now().timestamp())}",
                'initiator': 'alert_collection_agent',
                'task_parameters': json.dumps({
                    'confidence_score': alert_data.get('confidence_score', 0),
                    'signal_strength': alert_data.get('signal_strength', 0),
                    'source_server': alert_data.get('source_server', ''),
                    'timeframe': alert_data.get('timeframe', ''),
                    'technical_data': alert_data.get('technical_data', {}),
                    'riskmetric_data': alert_data.get('riskmetric_data', {}),
                    'cryptometer_data': alert_data.get('cryptometer_data', {})
                }, indent=2),
                'symbol': alert_data.get('symbol', ''),
                'current_price': alert_data.get('current_price', 'N/A'),
                'market_status': 'OPEN',  # Would be determined dynamically
                'system_health': 'HEALTHY'  # Would be checked dynamically
            }

            # Render the professional Manus template
            rendered_prompt = templates.render_prompt(manus_template, variables)

            # If rendering successful, use it; otherwise fall back to simple version
            if rendered_prompt:
                return rendered_prompt
        except Exception as e:
            logger.warning(f"Could not use professional Manus template: {e}")

        # Simple fallback if professional template fails
        return f"""Generate extraordinary trading intelligence for {alert_data.get('symbol')}.

Alert Details:
- Confidence: {alert_data.get('confidence_score', 0) * 100:.1f}%
- Signal Strength: {alert_data.get('signal_strength', 0):.2f}
- Source: {alert_data.get('source_server')}
- Timeframe: {alert_data.get('timeframe')}

Technical Data: {json.dumps(alert_data.get('technical_data', {}), indent=2)}

Provide institutional-grade analysis with:
1. Market microstructure analysis
2. Risk-adjusted return calculations
3. Strategic positioning recommendations
4. Market timing insights
5. Portfolio implications

Focus on actionable intelligence for professional traders."""

    async def store_manus_report_to_supabase(self, symbol: str, alert_id: str,
                                           manus_prompt: str, manus_response: str,
                                           extraordinary_score: float,
                                           processing_metrics: Dict[str, Any]) -> bool:
        """Store Manus extraordinary report to Supabase"""
        if not self.supabase_client:
            return False

        try:
            manus_report = {
                'symbol': symbol,
                'alert_id': alert_id,
                'manus_prompt': manus_prompt,
                'manus_response': manus_response,
                'extraordinary_score': extraordinary_score,
                'prompt_tokens': processing_metrics.get('prompt_tokens', 0),
                'response_tokens': processing_metrics.get('response_tokens', 0),
                'processing_time_ms': processing_metrics.get('processing_time_ms', 0),
                'status': 'completed'
            }

            response = self.supabase_client.table('manus_extraordinary_reports').insert(
                manus_report
            ).execute()

            if response.data:
                self.performance_metrics['manus_reports_generated'] += 1
                self.performance_metrics['supabase_operations'] += 1
                logger.info(f"✅ Stored Manus report for {symbol} in Supabase")
                return True

        except Exception as e:
            logger.error(f"Error storing Manus report: {e}")
            self.performance_metrics['errors'] += 1

        return False

    async def update_symbol_coverage(self, symbol: str, alert_confidence: float):
        """Update symbol coverage status in Supabase"""
        if not self.supabase_client:
            return

        try:
            coverage_data = {
                'symbol': symbol,
                'last_alert_time': datetime.now().isoformat(),
                'alert_count': 1,  # This would be incremented properly in a real implementation
                'best_alert_confidence': alert_confidence,
                'status': 'covered',
                'coverage_quality_score': alert_confidence
            }

            self.supabase_client.table('symbol_coverage').upsert(
                coverage_data,
                on_conflict='symbol'
            ).execute()

            logger.debug(f"✅ Updated coverage for {symbol}")

        except Exception as e:
            logger.error(f"Error updating symbol coverage: {e}")

    async def get_active_alert_for_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get active alert report for symbol from Supabase"""
        if not self.supabase_client:
            return None

        try:
            response = self.supabase_client.table('alert_reports').select('*').eq(
                'symbol', symbol.upper()
            ).eq('is_active', True).order('created_at', desc=True).limit(1).execute()

            if response.data:
                return response.data[0]

        except Exception as e:
            logger.error(f"Error getting alert for {symbol}: {e}")

        return None

    async def get_symbols_needing_alerts(self) -> List[str]:
        """Get symbols that need new alerts"""
        if not self.supabase_client:
            return []

        try:
            # Get symbols without recent alerts
            response = self.supabase_client.table('symbol_coverage').select('symbol').or_(
                'status.eq.needs_alert,'
                f'last_alert_time.lt.{(datetime.now() - timedelta(hours=24)).isoformat()}'
            ).execute()

            return [row['symbol'] for row in response.data]

        except Exception as e:
            logger.error(f"Error getting symbols needing alerts: {e}")
            return []

    async def get_performance_analytics(self) -> Dict[str, Any]:
        """Get comprehensive performance analytics"""
        analytics = {
            'current_metrics': self.performance_metrics,
            'supabase_status': self.supabase_client is not None,
            'template_count': len(self.prompt_templates),
            'last_sync': self.performance_metrics.get('last_sync'),
            'error_rate': 0
        }

        if self.supabase_client:
            try:
                # Get recent statistics
                response = self.supabase_client.table('alert_agent_statistics').select('*').order(
                    'timestamp', desc=True
                ).limit(10).execute()

                if response.data:
                    analytics['recent_stats'] = response.data

                # Get symbol coverage summary
                coverage_response = self.supabase_client.table('symbol_coverage_status').select('*').execute()
                if coverage_response.data:
                    analytics['symbol_coverage'] = len(coverage_response.data)

                # Calculate error rate
                total_operations = self.performance_metrics['supabase_operations']
                if total_operations > 0:
                    analytics['error_rate'] = self.performance_metrics['errors'] / total_operations

            except Exception as e:
                logger.error(f"Error getting performance analytics: {e}")

        return analytics

    async def sync_performance_stats_to_supabase(self):
        """Sync performance statistics to Supabase"""
        if not self.supabase_client:
            return

        try:
            stats_data = {
                'alerts_collected': self.performance_metrics.get('alerts_collected', 0),
                'alerts_processed': self.performance_metrics.get('alerts_processed', 0),
                'reports_generated': self.performance_metrics.get('reports_generated', 0),
                'manus_reports': self.performance_metrics['manus_reports_generated'],
                'symbols_covered': self.performance_metrics.get('symbols_covered', 0),
                'mdc_documents_created': self.performance_metrics['mdc_documents_created'],
                'success_rate': 1.0 - (self.performance_metrics['errors'] / max(self.performance_metrics['supabase_operations'], 1)),
                'performance_metrics': {
                    'supabase_operations': self.performance_metrics['supabase_operations'],
                    'prompt_generations': self.performance_metrics['prompt_generations'],
                    'errors': self.performance_metrics['errors']
                }
            }

            self.supabase_client.table('alert_agent_statistics').insert(stats_data).execute()
            self.performance_metrics['last_sync'] = datetime.now()

            logger.debug("✅ Synced performance stats to Supabase")

        except Exception as e:
            logger.error(f"Error syncing performance stats: {e}")

    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status and capabilities"""
        return {
            'service': 'alert_agent_supabase_integration',
            'supabase_available': SUPABASE_AVAILABLE,
            'supabase_connected': self.supabase_client is not None,
            'mcp_prompting_enabled': self.config['mcp_prompting_enabled'],
            'prompt_templates_loaded': len(self.prompt_templates),
            'manus_integration_enabled': self.config['manus_integration_enabled'],
            'performance_metrics': self.performance_metrics,
            'config': self.config,
            'last_updated': datetime.now().isoformat()
        }

# Global instance
_supabase_integration = None

def get_alert_agent_supabase_integration() -> AlertAgentSupabaseIntegration:
    """Get or create the Supabase integration instance"""
    global _supabase_integration
    if _supabase_integration is None:
        _supabase_integration = AlertAgentSupabaseIntegration()
    return _supabase_integration

async def test_integration():
    """Test the Supabase integration"""
    integration = AlertAgentSupabaseIntegration()

    print("🔄 Testing Alert Agent Supabase Integration...")

    # Test status
    status = integration.get_integration_status()
    print(f"✅ Integration Status: {json.dumps(status, indent=2)}")

    # Test prompt templates
    if integration.prompt_templates:
        print(f"✅ Loaded {len(integration.prompt_templates)} prompt templates")
        for name, template in integration.prompt_templates.items():
            print(f"  - {name}: {template.template_type}")

    # Test analytics
    analytics = await integration.get_performance_analytics()
    print(f"✅ Performance Analytics: {json.dumps(analytics, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_integration())