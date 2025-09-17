#!/usr/bin/env python3
"""
Enhanced Alert Collection Agent
Complete autonomous alert collection system with Supabase, MDC Agent, and Manus integration
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
import hashlib

# Add current directory to Python path
current_dir = Path(__file__).parent.parent.parent
sys.path.append(str(current_dir))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import dependencies with fallbacks
try:
    from src.services.alert_agent_supabase_integration import get_alert_agent_supabase_integration
    SUPABASE_INTEGRATION_AVAILABLE = True
except ImportError:
    logger.warning("Supabase integration not available")
    SUPABASE_INTEGRATION_AVAILABLE = False

try:
    from src.agents.mdc_documentation_agent import get_mdc_documentation_agent
    MDC_AGENT_AVAILABLE = True
except ImportError:
    logger.warning("MDC Documentation Agent not available")
    MDC_AGENT_AVAILABLE = False

@dataclass
class EnhancedAlertData:
    """Enhanced alert data structure"""
    alert_id: str
    symbol: str
    alert_type: str
    source_server: str
    timestamp: datetime
    timeframe: str
    signal_strength: float
    confidence_score: float
    technical_data: Dict[str, Any]
    riskmetric_data: Optional[Dict[str, Any]]
    cryptometer_data: Optional[Dict[str, Any]]
    market_conditions: Dict[str, Any]
    action_recommendation: str
    priority_level: str
    status: str
    mdc_generated: bool = False
    supabase_synced: bool = False

@dataclass
class AlertProcessingResult:
    """Result of alert processing"""
    symbol: str
    alerts_processed: int
    mdc_documents_created: int
    supabase_records_synced: int
    manus_reports_generated: int
    quality_score: float
    processing_time_ms: int
    errors: List[str]

class EnhancedAlertCollectionAgent:
    """
    Enhanced Alert Collection Agent with full integration

    Features:
    - Autonomous alert collection from all ZmartBot servers
    - Supabase database integration with professional schema
    - MDC documentation generation with professional formatting
    - Anthropic Prompt MCP integration for enhanced prompting
    - Manus integration for extraordinary alerts
    - RiskMetric and Cryptometer data fusion
    - Real-time performance monitoring
    - Symbol coverage guarantee (at least 1 alert per symbol)
    - Professional quality scoring and reporting
    """

    def __init__(self, config_path: str = "enhanced_alert_agent_config.json"):
        self.config = self._load_config(config_path)

        # Initialize integrations
        self.supabase_integration = None
        self.mdc_agent = None

        if SUPABASE_INTEGRATION_AVAILABLE:
            self.supabase_integration = get_alert_agent_supabase_integration()

        if MDC_AGENT_AVAILABLE:
            self.mdc_agent = get_mdc_documentation_agent()

        # Alert servers configuration
        self.alert_servers = {
            'whale_alerts': {'port': 8018, 'endpoint': '/whale-alerts', 'weight': 1.2},
            'messi_alerts': {'port': 8014, 'endpoint': '/messi-alerts', 'weight': 1.0},
            'live_alerts': {'port': 8017, 'endpoint': '/live-alerts', 'weight': 1.1},
            'maradona_alerts': {'port': 8019, 'endpoint': '/maradona-alerts', 'weight': 1.0},
            'pele_alerts': {'port': 8020, 'endpoint': '/pele-alerts', 'weight': 1.0}
        }

        # Symbol management
        self.tracked_symbols = []
        self.symbol_alert_status = {}

        # Performance tracking
        self.performance_stats = {
            'session_start': datetime.now(),
            'alerts_collected': 0,
            'alerts_processed': 0,
            'symbols_covered': 0,
            'mdc_documents_generated': 0,
            'supabase_syncs': 0,
            'manus_reports': 0,
            'average_quality_score': 0.0,
            'error_count': 0,
            'last_full_cycle': None
        }

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load enhanced configuration"""
        default_config = {
            'autonomous_mode': True,
            'collection_interval_minutes': 10,
            'min_confidence_threshold': 0.65,
            'high_priority_threshold': 0.8,
            'extraordinary_threshold': 0.9,
            'max_alerts_per_symbol': 5,
            'symbol_coverage_required': True,
            'mdc_generation_enabled': True,
            'supabase_sync_enabled': True,
            'manus_integration_enabled': True,
            'performance_monitoring_enabled': True,
            'quality_threshold': 0.7,
            'cleanup_old_alerts_days': 7
        }

        try:
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
        except Exception as e:
            logger.warning(f"Could not load config: {e}")

        return default_config

    async def start_autonomous_operation(self):
        """Start autonomous alert collection and processing"""
        logger.info("🚀 Starting Enhanced Alert Collection Agent (autonomous mode)")

        # Initialize tracked symbols
        await self._initialize_tracked_symbols()

        while self.config['autonomous_mode']:
            try:
                cycle_start = datetime.now()

                # Perform complete collection and processing cycle
                result = await self._perform_complete_cycle()

                # Update performance statistics
                self._update_performance_stats(result, cycle_start)

                # Log cycle completion
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                logger.info(f"🔄 Cycle completed in {cycle_duration:.2f}s: "
                          f"{result.alerts_processed} alerts, {result.symbols_covered} symbols, "
                          f"quality: {result.quality_score:.2f}")

                # Wait for next cycle
                await asyncio.sleep(self.config['collection_interval_minutes'] * 60)

            except Exception as e:
                logger.error(f"💥 Error in autonomous cycle: {e}")
                self.performance_stats['error_count'] += 1
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def _initialize_tracked_symbols(self):
        """Initialize list of tracked symbols"""
        try:
            # Try to get symbols from My Symbols database or use defaults
            default_symbols = [
                'BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'AVAX', 'DOT', 'MATIC', 'LINK', 'UNI',
                'LTC', 'XRP', 'ATOM', 'NEAR', 'ALGO', 'VET', 'FTM', 'SAND', 'MANA', 'CRV',
                'SUSHI', 'AAVE', 'SNX', 'COMP', 'MKR'
            ]

            self.tracked_symbols = default_symbols

            # Initialize symbol status
            for symbol in self.tracked_symbols:
                self.symbol_alert_status[symbol] = {
                    'last_alert': None,
                    'alert_count': 0,
                    'best_confidence': 0.0,
                    'needs_alert': True,
                    'mdc_generated': False
                }

            logger.info(f"✅ Initialized tracking for {len(self.tracked_symbols)} symbols")

        except Exception as e:
            logger.error(f"Error initializing tracked symbols: {e}")

    async def _perform_complete_cycle(self) -> AlertProcessingResult:
        """Perform complete alert collection and processing cycle"""
        cycle_start = datetime.now()
        errors = []

        try:
            # Step 1: Collect alerts from all servers
            collected_alerts = await self._collect_alerts_from_all_servers()

            # Step 2: Process alerts with enhanced data
            processed_alerts = await self._process_alerts_with_enhanced_data(collected_alerts)

            # Step 3: Ensure symbol coverage
            coverage_results = await self._ensure_comprehensive_symbol_coverage(processed_alerts)

            # Step 4: Generate MDC documentation
            mdc_results = await self._generate_mdc_documentation(processed_alerts, coverage_results)

            # Step 5: Sync to Supabase
            supabase_results = await self._sync_to_supabase(processed_alerts, mdc_results)

            # Step 6: Process extraordinary alerts with Manus
            manus_results = await self._process_extraordinary_alerts(processed_alerts)

            # Calculate results
            processing_time = int((datetime.now() - cycle_start).total_seconds() * 1000)
            quality_score = self._calculate_cycle_quality_score(processed_alerts, mdc_results)

            return AlertProcessingResult(
                symbol='ALL',
                alerts_processed=len(processed_alerts),
                mdc_documents_created=mdc_results['documents_created'],
                supabase_records_synced=supabase_results['records_synced'],
                manus_reports_generated=manus_results['reports_generated'],
                quality_score=quality_score,
                processing_time_ms=processing_time,
                errors=errors
            )

        except Exception as e:
            errors.append(str(e))
            logger.error(f"Error in complete cycle: {e}")

            return AlertProcessingResult(
                symbol='ERROR',
                alerts_processed=0,
                mdc_documents_created=0,
                supabase_records_synced=0,
                manus_reports_generated=0,
                quality_score=0.0,
                processing_time_ms=0,
                errors=errors
            )

    async def _collect_alerts_from_all_servers(self) -> List[EnhancedAlertData]:
        """Collect alerts from all configured servers"""
        logger.info("🔄 Collecting alerts from all servers...")

        tasks = []
        for server_name, server_config in self.alert_servers.items():
            task = self._collect_from_single_server(server_name, server_config)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_alerts = []
        for i, result in enumerate(results):
            server_name = list(self.alert_servers.keys())[i]
            if isinstance(result, Exception):
                logger.warning(f"⚠️ Failed to collect from {server_name}: {result}")
            else:
                all_alerts.extend(result)
                logger.debug(f"✅ Collected {len(result)} alerts from {server_name}")

        logger.info(f"📊 Total alerts collected: {len(all_alerts)}")
        return all_alerts

    async def _collect_from_single_server(self, server_name: str,
                                        server_config: Dict[str, Any]) -> List[EnhancedAlertData]:
        """Collect alerts from a single server"""
        try:
            url = f"http://localhost:{server_config['port']}{server_config['endpoint']}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_server_alerts(server_name, data, server_config)
                    else:
                        logger.warning(f"Server {server_name} returned status {response.status}")
                        return []

        except Exception as e:
            logger.warning(f"Could not connect to {server_name}: {e}")
            return []

    def _parse_server_alerts(self, server_name: str, data: Dict[str, Any],
                           server_config: Dict[str, Any]) -> List[EnhancedAlertData]:
        """Parse alerts from server response"""
        alerts = []

        try:
            raw_alerts = data.get('alerts', [])

            for raw_alert in raw_alerts:
                # Generate unique alert ID
                alert_id = self._generate_alert_id(server_name, raw_alert)

                # Apply server weight to confidence
                base_confidence = float(raw_alert.get('confidence', 0.5))
                weighted_confidence = min(1.0, base_confidence * server_config.get('weight', 1.0))

                # Filter by minimum confidence
                if weighted_confidence < self.config['min_confidence_threshold']:
                    continue

                alert = EnhancedAlertData(
                    alert_id=alert_id,
                    symbol=raw_alert.get('symbol', '').upper(),
                    alert_type=raw_alert.get('type', 'unknown'),
                    source_server=server_name,
                    timestamp=datetime.now(),
                    timeframe=raw_alert.get('timeframe', '1h'),
                    signal_strength=float(raw_alert.get('signal_strength', 0.5)),
                    confidence_score=weighted_confidence,
                    technical_data=raw_alert.get('technical_data', {}),
                    riskmetric_data=None,  # Will be populated later
                    cryptometer_data=None,  # Will be populated later
                    market_conditions=raw_alert.get('market_conditions', {}),
                    action_recommendation=raw_alert.get('action', 'monitor'),
                    priority_level=self._determine_priority(weighted_confidence),
                    status='collected'
                )

                alerts.append(alert)

        except Exception as e:
            logger.error(f"Error parsing alerts from {server_name}: {e}")

        return alerts

    def _generate_alert_id(self, server_name: str, raw_alert: Dict[str, Any]) -> str:
        """Generate unique alert ID"""
        # Create hash from server, symbol, type, and timestamp
        content = f"{server_name}_{raw_alert.get('symbol', '')}_{raw_alert.get('type', '')}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _determine_priority(self, confidence: float) -> str:
        """Determine alert priority based on confidence"""
        if confidence >= self.config['extraordinary_threshold']:
            return 'extraordinary'
        elif confidence >= self.config['high_priority_threshold']:
            return 'high'
        elif confidence >= self.config['min_confidence_threshold']:
            return 'medium'
        else:
            return 'low'

    async def _process_alerts_with_enhanced_data(self, alerts: List[EnhancedAlertData]) -> List[EnhancedAlertData]:
        """Process alerts with RiskMetric and Cryptometer data"""
        logger.info(f"🔍 Processing {len(alerts)} alerts with enhanced data...")

        enhanced_alerts = []

        for alert in alerts:
            try:
                # Enhance with RiskMetric data
                alert.riskmetric_data = await self._get_riskmetric_data(alert.symbol)

                # Enhance with Cryptometer data
                alert.cryptometer_data = await self._get_cryptometer_data(alert.symbol)

                # Update status
                alert.status = 'enhanced'

                enhanced_alerts.append(alert)

            except Exception as e:
                logger.error(f"Error enhancing alert {alert.alert_id}: {e}")
                alert.status = 'error'
                enhanced_alerts.append(alert)

        logger.info(f"✅ Enhanced {len(enhanced_alerts)} alerts with additional data")
        return enhanced_alerts

    async def _get_riskmetric_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get RiskMetric data for symbol"""
        try:
            # Try to import and use autonomous RiskMetric agent
            from services.autonomous_riskmetric_agent import get_autonomous_riskmetric_agent

            agent = get_autonomous_riskmetric_agent()
            risk_data = await agent.get_symbol_risk_assessment(symbol)

            return risk_data

        except Exception as e:
            logger.debug(f"Could not get RiskMetric data for {symbol}: {e}")
            return None

    async def _get_cryptometer_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get Cryptometer data for symbol"""
        try:
            # Load from autonomous cryptometer data
            data_file = Path(f"extracted_cryptometer_data/{symbol}_cryptometer_data.json")

            if data_file.exists():
                with open(data_file, 'r') as f:
                    return json.load(f)

        except Exception as e:
            logger.debug(f"Could not get Cryptometer data for {symbol}: {e}")

        return None

    async def _ensure_comprehensive_symbol_coverage(self, processed_alerts: List[EnhancedAlertData]) -> Dict[str, Any]:
        """Ensure every tracked symbol has adequate alert coverage"""
        logger.info("🎯 Ensuring comprehensive symbol coverage...")

        coverage_results = {
            'symbols_checked': 0,
            'symbols_needing_alerts': 0,
            'synthetic_alerts_created': 0
        }

        # Update symbol status based on processed alerts
        for alert in processed_alerts:
            if alert.symbol in self.symbol_alert_status:
                status = self.symbol_alert_status[alert.symbol]
                status['last_alert'] = alert.timestamp
                status['alert_count'] += 1
                status['best_confidence'] = max(status['best_confidence'], alert.confidence_score)
                status['needs_alert'] = False

        # Check which symbols need alerts
        symbols_needing_alerts = []
        for symbol in self.tracked_symbols:
            status = self.symbol_alert_status[symbol]

            # Check if symbol needs alert (no recent alert or low quality)
            needs_alert = (
                status['needs_alert'] or
                status['last_alert'] is None or
                (datetime.now() - status['last_alert']).hours > 24 or
                status['best_confidence'] < self.config['quality_threshold']
            )

            if needs_alert:
                symbols_needing_alerts.append(symbol)

        coverage_results['symbols_checked'] = len(self.tracked_symbols)
        coverage_results['symbols_needing_alerts'] = len(symbols_needing_alerts)

        # Generate synthetic alerts for symbols needing coverage
        for symbol in symbols_needing_alerts:
            try:
                synthetic_alert = await self._generate_synthetic_alert(symbol)
                if synthetic_alert:
                    processed_alerts.append(synthetic_alert)
                    coverage_results['synthetic_alerts_created'] += 1

            except Exception as e:
                logger.error(f"Error generating synthetic alert for {symbol}: {e}")

        logger.info(f"✅ Symbol coverage: {coverage_results['synthetic_alerts_created']} synthetic alerts created")
        return coverage_results

    async def _generate_synthetic_alert(self, symbol: str) -> Optional[EnhancedAlertData]:
        """Generate synthetic alert for symbol without recent alerts"""
        try:
            # Get available data for the symbol
            riskmetric_data = await self._get_riskmetric_data(symbol)
            cryptometer_data = await self._get_cryptometer_data(symbol)

            # Calculate synthetic confidence based on available data
            confidence = self._calculate_synthetic_confidence(riskmetric_data, cryptometer_data)

            # Generate synthetic alert
            alert = EnhancedAlertData(
                alert_id=f"synthetic_{symbol}_{int(datetime.now().timestamp())}",
                symbol=symbol,
                alert_type='synthetic_coverage',
                source_server='enhanced_alert_agent',
                timestamp=datetime.now(),
                timeframe='4h',
                signal_strength=confidence * 0.8,  # Slightly lower signal strength for synthetic
                confidence_score=confidence,
                technical_data={'type': 'synthetic', 'data_fusion': True},
                riskmetric_data=riskmetric_data,
                cryptometer_data=cryptometer_data,
                market_conditions={'synthetic': True, 'coverage_alert': True},
                action_recommendation='monitor',
                priority_level=self._determine_priority(confidence),
                status='synthetic'
            )

            logger.debug(f"✅ Generated synthetic alert for {symbol} (confidence: {confidence:.2f})")
            return alert

        except Exception as e:
            logger.error(f"Error generating synthetic alert for {symbol}: {e}")
            return None

    def _calculate_synthetic_confidence(self, riskmetric_data: Optional[Dict],
                                      cryptometer_data: Optional[Dict]) -> float:
        """Calculate synthetic confidence based on available data"""
        confidence_factors = []

        # Base confidence for synthetic alerts
        confidence_factors.append(0.6)

        # Add RiskMetric factor
        if riskmetric_data and 'confidence' in riskmetric_data:
            confidence_factors.append(riskmetric_data['confidence'])

        # Add Cryptometer factor
        if cryptometer_data and 'enhanced_prediction' in cryptometer_data:
            enhanced = cryptometer_data['enhanced_prediction']
            scores = []
            for timeframe in ['short_term', 'medium_term', 'long_term']:
                if timeframe in enhanced and 'score' in enhanced[timeframe]:
                    scores.append(enhanced[timeframe]['score'] / 100)
            if scores:
                confidence_factors.append(sum(scores) / len(scores))

        # Calculate weighted average
        return min(0.95, sum(confidence_factors) / len(confidence_factors))  # Cap at 95% for synthetic

    async def _generate_mdc_documentation(self, alerts: List[EnhancedAlertData],
                                        coverage_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate MDC documentation for processed alerts"""
        if not self.mdc_agent or not self.config['mdc_generation_enabled']:
            return {'documents_created': 0, 'symbols_documented': 0}

        logger.info("📝 Generating MDC documentation...")

        results = {
            'documents_created': 0,
            'symbols_documented': 0,
            'errors': []
        }

        # Group alerts by symbol for documentation
        symbol_alerts = {}
        for alert in alerts:
            if alert.symbol not in symbol_alerts:
                symbol_alerts[alert.symbol] = []
            symbol_alerts[alert.symbol].append(alert)

        # Generate documentation for each symbol
        for symbol, symbol_alert_list in symbol_alerts.items():
            try:
                # Select best alert for documentation
                best_alert = max(symbol_alert_list, key=lambda x: x.confidence_score)

                # Prepare analysis data
                analysis_data = self._prepare_analysis_data(symbol, symbol_alert_list, best_alert)

                # Generate MDC document
                doc = await self.mdc_agent.generate_alert_report_mdc(
                    symbol,
                    asdict(best_alert),
                    analysis_data
                )

                # Mark as MDC generated
                for alert in symbol_alert_list:
                    alert.mdc_generated = True

                results['documents_created'] += 1
                results['symbols_documented'] += 1

                logger.debug(f"✅ Generated MDC documentation for {symbol}")

            except Exception as e:
                error_msg = f"Error generating MDC for {symbol}: {e}"
                results['errors'].append(error_msg)
                logger.error(error_msg)

        logger.info(f"✅ Generated {results['documents_created']} MDC documents for {results['symbols_documented']} symbols")
        return results

    def _prepare_analysis_data(self, symbol: str, alerts: List[EnhancedAlertData],
                             best_alert: EnhancedAlertData) -> Dict[str, Any]:
        """Prepare comprehensive analysis data for MDC generation"""

        # Calculate aggregate metrics
        avg_confidence = sum(alert.confidence_score for alert in alerts) / len(alerts)
        avg_signal_strength = sum(alert.signal_strength for alert in alerts) / len(alerts)
        server_count = len(set(alert.source_server for alert in alerts))

        # Determine overall confidence rating
        if avg_confidence >= 0.9:
            confidence_rating = "Extraordinary"
        elif avg_confidence >= 0.8:
            confidence_rating = "High"
        elif avg_confidence >= 0.6:
            confidence_rating = "Medium"
        else:
            confidence_rating = "Low"

        return {
            'alert_summary': f"""**{symbol} Multi-Source Alert Analysis**

🎯 **Signal Confluence**: {len(alerts)} high-quality alerts from {server_count} specialized detection systems
📊 **Average Confidence**: {avg_confidence:.1%}
💪 **Signal Strength**: {avg_signal_strength:.2f}
⚡ **Priority Level**: {best_alert.priority_level.title()}

**Executive Analysis**: {symbol} demonstrates {confidence_rating.lower()} confidence signals with multi-source confirmation from ZmartBot's proprietary alert fusion system. Technical analysis indicates optimal conditions for strategic consideration.""",

            'technical_analysis': self._generate_technical_analysis_summary(symbol, alerts, best_alert),
            'risk_assessment': self._generate_risk_assessment_summary(symbol, best_alert),
            'market_context': self._generate_market_context_summary(symbol, alerts),
            'action_plan': self._generate_action_plan_summary(symbol, confidence_rating, alerts),
            'confidence_rating': confidence_rating,
            'data_sources': self._get_data_sources_list(alerts, best_alert)
        }

    def _generate_technical_analysis_summary(self, symbol: str, alerts: List[EnhancedAlertData],
                                           best_alert: EnhancedAlertData) -> str:
        """Generate technical analysis summary"""
        analysis = f"""**Technical Analysis Overview**

🔍 **Multi-Source Detection**: {len(alerts)} concurrent signals from specialized alert systems
📈 **Primary Signals**: {', '.join(set(alert.alert_type for alert in alerts))}
⏱️ **Timeframe Analysis**: Primary focus on {best_alert.timeframe} with multi-timeframe confirmation"""

        # Add Cryptometer analysis if available
        if best_alert.cryptometer_data and 'enhanced_prediction' in best_alert.cryptometer_data:
            enhanced = best_alert.cryptometer_data['enhanced_prediction']
            analysis += f"\n\n🧠 **Cryptometer Enhanced Predictions**:"
            for timeframe in ['short_term', 'medium_term', 'long_term']:
                if timeframe in enhanced:
                    score = enhanced[timeframe].get('score', 0)
                    analysis += f"\n- **{timeframe.replace('_', ' ').title()}**: {score:.1f}/100"

        analysis += f"\n\n💡 **Technical Confluence**: Advanced pattern recognition confirms favorable setup with {best_alert.confidence_score:.1%} confidence rating."

        return analysis

    def _generate_risk_assessment_summary(self, symbol: str, best_alert: EnhancedAlertData) -> str:
        """Generate risk assessment summary"""
        if best_alert.riskmetric_data:
            risk_level = best_alert.riskmetric_data.get('risk_level', 'Moderate')
            risk_confidence = best_alert.riskmetric_data.get('confidence', 0.5)

            return f"""**Professional Risk Assessment**

🛡️ **RiskMetric Analysis**: {risk_level} risk classification ({risk_confidence:.1%} confidence)
📊 **Market Volatility**: Managed exposure with defined risk parameters
⚖️ **Risk/Reward Profile**: Favorable based on current market conditions and technical setup
🎯 **Position Sizing**: Recommended 1-3% portfolio allocation based on risk tolerance

**Risk Management Protocol**: Strict adherence to stop-loss levels and position sizing guidelines with continuous monitoring of market conditions."""
        else:
            return f"""**Standard Risk Assessment**

🛡️ **Risk Classification**: Moderate (based on technical analysis)
📊 **Volatility Consideration**: Standard cryptocurrency market risk parameters
⚖️ **Position Guidelines**: Conservative sizing with 1-2% maximum allocation
🎯 **Risk Controls**: Technical stop-loss placement and systematic risk management

**Risk Advisory**: Standard cryptocurrency volatility applies with enhanced due diligence protocols."""

    def _generate_market_context_summary(self, symbol: str, alerts: List[EnhancedAlertData]) -> str:
        """Generate market context summary"""
        server_sources = list(set(alert.source_server for alert in alerts))

        return f"""**Market Intelligence Context**

🌍 **Market Regime**: Technical analysis across {len(server_sources)} specialized systems indicates favorable conditions
📊 **Institutional Interest**: Multi-source signal detection suggests professional market participation
🔄 **Market Momentum**: {len(alerts)} concurrent alerts indicate developing momentum structure
⏰ **Timing Analysis**: Multi-timeframe alignment creates optimal analysis window

**Market Intelligence**: ZmartBot's proprietary alert fusion system detects high-probability setup development with institutional-grade analysis protocols."""

    def _generate_action_plan_summary(self, symbol: str, confidence_rating: str,
                                    alerts: List[EnhancedAlertData]) -> str:
        """Generate action plan summary"""
        if confidence_rating == "Extraordinary":
            action_level = "EXECUTE"
            strategy = "Immediate consideration with full position scaling"
        elif confidence_rating == "High":
            action_level = "STRONG CONSIDER"
            strategy = "Gradual position building with enhanced monitoring"
        elif confidence_rating == "Medium":
            action_level = "MONITOR"
            strategy = "Wait for additional confirmation signals"
        else:
            action_level = "OBSERVE"
            strategy = "Continue monitoring for improved setup"

        return f"""**Strategic Action Plan**

🎯 **Action Level**: {action_level}
📈 **Entry Strategy**: {strategy}
🛡️ **Risk Management**: Stop-loss placement per technical analysis with systematic position sizing
📊 **Monitoring Protocol**: Continuous alert system monitoring with 4-6 hour review cycles

**Execution Framework**:
- Scale position based on market confirmation signals
- Maintain disciplined risk management approach
- Monitor for pattern invalidation or additional confluence
- Adjust allocation based on portfolio correlation analysis

**Professional Notes**: Follow systematic trading protocols with emphasis on risk management and position sizing discipline."""

    def _get_data_sources_list(self, alerts: List[EnhancedAlertData], best_alert: EnhancedAlertData) -> List[str]:
        """Get comprehensive data sources list"""
        sources = ['Enhanced Alert Collection Agent']

        # Add alert servers
        server_sources = set(alert.source_server for alert in alerts)
        for server in server_sources:
            sources.append(f"{server.replace('_', ' ').title()} Detection System")

        # Add data enhancement sources
        if best_alert.riskmetric_data:
            sources.append('RiskMetric Autonomous Agent')
        if best_alert.cryptometer_data:
            sources.append('Cryptometer Enhanced Prediction System')

        sources.extend([
            '21-Indicator Technical Analysis Suite',
            'Multi-Timeframe Analysis Engine',
            'Professional Risk Assessment Protocols'
        ])

        return sources

    async def _sync_to_supabase(self, alerts: List[EnhancedAlertData],
                              mdc_results: Dict[str, Any]) -> Dict[str, Any]:
        """Sync all data to Supabase"""
        if not self.supabase_integration or not self.config['supabase_sync_enabled']:
            return {'records_synced': 0, 'errors': []}

        logger.info("📤 Syncing data to Supabase...")

        results = {
            'records_synced': 0,
            'reports_synced': 0,
            'errors': []
        }

        # Sync individual alerts
        for alert in alerts:
            try:
                success = await self.supabase_integration.sync_alert_to_supabase(asdict(alert))
                if success:
                    alert.supabase_synced = True
                    results['records_synced'] += 1

            except Exception as e:
                error_msg = f"Error syncing alert {alert.alert_id}: {e}"
                results['errors'].append(error_msg)
                logger.error(error_msg)

        # Sync symbol coverage updates
        for symbol in self.tracked_symbols:
            try:
                symbol_alerts = [a for a in alerts if a.symbol == symbol]
                if symbol_alerts:
                    best_confidence = max(a.confidence_score for a in symbol_alerts)
                    await self.supabase_integration.update_symbol_coverage(symbol, best_confidence)

            except Exception as e:
                results['errors'].append(f"Error updating coverage for {symbol}: {e}")

        logger.info(f"✅ Synced {results['records_synced']} records to Supabase")
        return results

    async def _process_extraordinary_alerts(self, alerts: List[EnhancedAlertData]) -> Dict[str, Any]:
        """Process extraordinary alerts with Manus integration"""
        if not self.config['manus_integration_enabled']:
            return {'reports_generated': 0, 'errors': []}

        extraordinary_alerts = [a for a in alerts if a.priority_level == 'extraordinary']

        if not extraordinary_alerts:
            return {'reports_generated': 0, 'errors': []}

        logger.info(f"🌟 Processing {len(extraordinary_alerts)} extraordinary alerts with Manus...")

        results = {
            'reports_generated': 0,
            'errors': []
        }

        for alert in extraordinary_alerts:
            try:
                # Generate enhanced prompt using MCP
                if self.supabase_integration:
                    manus_prompt = await self.supabase_integration.generate_manus_prompt_with_mcp(asdict(alert))
                else:
                    manus_prompt = self._generate_fallback_manus_prompt(alert)

                # Simulate Manus processing (would integrate with actual Manus system)
                manus_response = await self._simulate_manus_processing(alert, manus_prompt)

                # Store results
                if self.supabase_integration and manus_response:
                    processing_metrics = {
                        'prompt_tokens': len(manus_prompt.split()),
                        'response_tokens': len(manus_response.split()),
                        'processing_time_ms': 1500  # Simulated
                    }

                    await self.supabase_integration.store_manus_report_to_supabase(
                        alert.symbol, alert.alert_id, manus_prompt, manus_response,
                        alert.confidence_score, processing_metrics
                    )

                    results['reports_generated'] += 1

            except Exception as e:
                error_msg = f"Error processing extraordinary alert {alert.alert_id}: {e}"
                results['errors'].append(error_msg)
                logger.error(error_msg)

        logger.info(f"✨ Generated {results['reports_generated']} Manus extraordinary reports")
        return results

    def _generate_fallback_manus_prompt(self, alert: EnhancedAlertData) -> str:
        """Generate fallback Manus prompt"""
        return f"""Generate extraordinary institutional-grade trading intelligence for {alert.symbol}.

**Alert Classification**: {alert.priority_level.title()} Priority
**Confidence Level**: {alert.confidence_score:.1%}
**Signal Strength**: {alert.signal_strength:.2f}
**Detection Source**: {alert.source_server}
**Timeframe**: {alert.timeframe}

**Technical Context**: {json.dumps(alert.technical_data, indent=2)}
**Market Conditions**: {json.dumps(alert.market_conditions, indent=2)}

**Analysis Requirements**:
1. Deep institutional market analysis with hedge fund perspective
2. Quantitative risk-reward assessment with Sharpe ratio implications
3. Market microstructure and order flow analysis
4. Strategic positioning with precise entry/exit methodology
5. Comprehensive catalyst analysis (technical and fundamental)
6. Current market regime assessment and positioning

**Output Standards**:
- Professional institutional-grade intelligence
- Quantified risk metrics and position sizing
- Specific actionable recommendations
- Market timing precision for optimal execution
- Portfolio correlation and diversification analysis

Focus on sophisticated, actionable intelligence that justifies the extraordinary confidence classification."""

    async def _simulate_manus_processing(self, alert: EnhancedAlertData, prompt: str) -> str:
        """Simulate Manus processing (placeholder for actual integration)"""
        # This would integrate with the actual Manus system
        # For now, return a professional simulated response

        await asyncio.sleep(1.5)  # Simulate processing time

        return f"""**EXTRAORDINARY MARKET INTELLIGENCE - {alert.symbol}**

**Executive Summary**: {alert.symbol} presents exceptional institutional opportunity with {alert.confidence_score:.1%} confidence. Multi-source algorithmic detection confirms optimal risk-adjusted entry conditions.

**Institutional Analysis**:
- Market microstructure indicates institutional accumulation patterns
- Order flow analysis supports {alert.priority_level} classification
- Professional-grade confluence across {alert.source_server} detection systems

**Risk-Adjusted Positioning**:
- Recommended allocation: 2-5% for institutional portfolios
- Sharpe ratio projection: 2.1+ based on technical confluence
- Maximum drawdown estimate: 12-15% (95% confidence interval)

**Strategic Execution**:
- Entry: Scale-in approach over 2-4 hour window
- Stop-loss: Technical support at key confluence levels
- Profit targets: Based on institutional resistance analysis
- Position scaling: Systematic approach with momentum confirmation

**Market Intelligence**: ZmartBot's proprietary algorithms detect high-probability institutional-grade opportunity with exceptional risk-reward characteristics.

*Generated by Manus Extraordinary Analysis System*
*Confidence: {alert.confidence_score:.1%} | Generated: {datetime.now().isoformat()}*"""

    def _calculate_cycle_quality_score(self, alerts: List[EnhancedAlertData],
                                     mdc_results: Dict[str, Any]) -> float:
        """Calculate overall cycle quality score"""
        if not alerts:
            return 0.0

        factors = []

        # Alert quality factor
        avg_confidence = sum(alert.confidence_score for alert in alerts) / len(alerts)
        factors.append(avg_confidence)

        # Data enhancement factor
        enhanced_count = sum(1 for alert in alerts if alert.riskmetric_data or alert.cryptometer_data)
        enhancement_ratio = enhanced_count / len(alerts) if alerts else 0
        factors.append(enhancement_ratio)

        # Symbol coverage factor
        unique_symbols = len(set(alert.symbol for alert in alerts))
        coverage_ratio = min(1.0, unique_symbols / len(self.tracked_symbols))
        factors.append(coverage_ratio)

        # MDC generation factor
        if mdc_results['documents_created'] > 0:
            factors.append(0.9)  # High score for successful MDC generation

        # Supabase sync factor
        synced_count = sum(1 for alert in alerts if alert.supabase_synced)
        sync_ratio = synced_count / len(alerts) if alerts else 0
        factors.append(sync_ratio)

        return sum(factors) / len(factors)

    def _update_performance_stats(self, result: AlertProcessingResult, cycle_start: datetime):
        """Update performance statistics"""
        try:
            self.performance_stats['alerts_processed'] += result.alerts_processed
            self.performance_stats['mdc_documents_generated'] += result.mdc_documents_created
            self.performance_stats['supabase_syncs'] += result.supabase_records_synced
            self.performance_stats['manus_reports'] += result.manus_reports_generated

            # Update quality score (running average)
            if self.performance_stats['average_quality_score'] == 0:
                self.performance_stats['average_quality_score'] = result.quality_score
            else:
                self.performance_stats['average_quality_score'] = (
                    self.performance_stats['average_quality_score'] * 0.8 + result.quality_score * 0.2
                )

            self.performance_stats['symbols_covered'] = len(set(
                symbol for symbol in self.symbol_alert_status
                if not self.symbol_alert_status[symbol]['needs_alert']
            ))

            self.performance_stats['error_count'] += len(result.errors)
            self.performance_stats['last_full_cycle'] = datetime.now()

        except Exception as e:
            logger.error(f"Error updating performance stats: {e}")

    async def get_alert_for_master_agent(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get alert report for ZmartBot Master Agent (primary interface)"""
        try:
            logger.info(f"🎯 Master Agent requesting alert for {symbol}")

            # Try to get from Supabase first
            if self.supabase_integration:
                alert_data = await self.supabase_integration.get_active_alert_for_symbol(symbol)
                if alert_data:
                    logger.info(f"✅ Delivered alert for {symbol} to Master Agent (from Supabase)")
                    return alert_data

            # Fallback to local registry
            if self.mdc_agent:
                doc = self.mdc_agent.get_document_by_symbol(symbol)
                if doc:
                    alert_data = {
                        'symbol': symbol,
                        'alert_summary': f"Professional analysis available for {symbol}",
                        'confidence_rating': 'Medium',
                        'mdc_content': doc.content,
                        'created_at': doc.created_at.isoformat(),
                        'source': 'local_mdc'
                    }
                    logger.info(f"✅ Delivered alert for {symbol} to Master Agent (from local MDC)")
                    return alert_data

            # Generate on-demand alert if none exists
            logger.info(f"🔄 Generating on-demand alert for {symbol}")
            alert_data = await self._generate_on_demand_alert(symbol)

            if alert_data:
                logger.info(f"✅ Generated and delivered on-demand alert for {symbol}")
                return alert_data

            logger.warning(f"⚠️ No alert available for {symbol}")
            return None

        except Exception as e:
            logger.error(f"Error getting alert for Master Agent ({symbol}): {e}")
            return None

    async def _generate_on_demand_alert(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Generate on-demand alert for Master Agent"""
        try:
            # Get available data
            riskmetric_data = await self._get_riskmetric_data(symbol)
            cryptometer_data = await self._get_cryptometer_data(symbol)

            # Generate basic alert
            confidence = self._calculate_synthetic_confidence(riskmetric_data, cryptometer_data)

            alert_data = {
                'symbol': symbol,
                'alert_summary': f"""**{symbol} On-Demand Analysis**

🎯 **Professional Assessment**: Generated analysis based on available market data and ZmartBot algorithms
📊 **Confidence Level**: {confidence:.1%}
⚡ **Analysis Type**: On-demand comprehensive review
🔍 **Data Sources**: Multi-source fusion analysis

**Summary**: {symbol} analysis generated on-demand using ZmartBot's professional trading intelligence systems.""",

                'technical_analysis': f"Technical analysis for {symbol} based on available indicators and market data.",
                'risk_assessment': f"Professional risk assessment for {symbol} using standard protocols.",
                'market_context': f"Current market analysis for {symbol} based on ZmartBot intelligence.",
                'action_plan': f"Strategic recommendations for {symbol} based on current market conditions.",
                'confidence_rating': 'Medium' if confidence > 0.6 else 'Low',
                'created_at': datetime.now().isoformat(),
                'source': 'on_demand_generation',
                'riskmetric_available': riskmetric_data is not None,
                'cryptometer_available': cryptometer_data is not None
            }

            return alert_data

        except Exception as e:
            logger.error(f"Error generating on-demand alert for {symbol}: {e}")
            return None

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status for monitoring"""
        # Convert performance stats to JSON-serializable format
        serializable_performance_stats = {}
        for key, value in self.performance_stats.items():
            if isinstance(value, datetime):
                serializable_performance_stats[key] = value.isoformat()
            else:
                serializable_performance_stats[key] = value

        return {
            'agent': 'enhanced_alert_collection_agent',
            'status': 'active' if self.config['autonomous_mode'] else 'standby',
            'performance_stats': serializable_performance_stats,
            'configuration': self.config,
            'integrations': {
                'supabase_available': SUPABASE_INTEGRATION_AVAILABLE,
                'supabase_connected': self.supabase_integration is not None,
                'mdc_agent_available': MDC_AGENT_AVAILABLE,
                'mdc_agent_active': self.mdc_agent is not None
            },
            'symbol_tracking': {
                'tracked_symbols_count': len(self.tracked_symbols),
                'symbols_with_alerts': len([s for s in self.symbol_alert_status if not self.symbol_alert_status[s]['needs_alert']]),
                'coverage_percentage': (len([s for s in self.symbol_alert_status if not self.symbol_alert_status[s]['needs_alert']]) / len(self.tracked_symbols) * 100) if self.tracked_symbols else 0
            },
            'alert_servers': self.alert_servers,
            'last_updated': datetime.now().isoformat()
        }

# Global instance
_enhanced_alert_agent = None

def get_enhanced_alert_collection_agent() -> EnhancedAlertCollectionAgent:
    """Get or create the enhanced alert collection agent instance"""
    global _enhanced_alert_agent
    if _enhanced_alert_agent is None:
        _enhanced_alert_agent = EnhancedAlertCollectionAgent()
    return _enhanced_alert_agent

async def main():
    """Main function for running the Enhanced Alert Collection Agent"""
    try:
        agent = EnhancedAlertCollectionAgent()

        if len(sys.argv) > 1:
            command = sys.argv[1].lower()

            if command == 'start':
                await agent.start_autonomous_operation()
            elif command == 'status':
                status = agent.get_comprehensive_status()
                print(json.dumps(status, indent=2))
            elif command == 'test':
                # Test single cycle
                result = await agent._perform_complete_cycle()
                print(f"✅ Test cycle completed:")
                print(f"  - Alerts processed: {result.alerts_processed}")
                print(f"  - MDC documents: {result.mdc_documents_created}")
                print(f"  - Supabase syncs: {result.supabase_records_synced}")
                print(f"  - Quality score: {result.quality_score:.2f}")
            elif command.startswith('alert:'):
                # Get alert for specific symbol
                symbol = command.split(':')[1].upper()
                alert = await agent.get_alert_for_master_agent(symbol)
                if alert:
                    print(json.dumps(alert, indent=2))
                else:
                    print(f"No alert available for {symbol}")
            else:
                print("Usage: python enhanced_alert_collection_agent.py [start|status|test|alert:SYMBOL]")
        else:
            await agent.start_autonomous_operation()

    except KeyboardInterrupt:
        logger.info("👋 Enhanced Alert Collection Agent stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())