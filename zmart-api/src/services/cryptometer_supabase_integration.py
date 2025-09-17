#!/usr/bin/env python3
"""
Cryptometer Supabase Integration Service
Handles syncing Cryptometer autonomous system data to Supabase database
"""

import asyncio
import json
import logging
import os
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from supabase import create_client, Client
except ImportError:
    logging.warning("Supabase client not available - using mock client")
    Client = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CryptometerSupabaseIntegration:
    """
    Handles syncing Cryptometer autonomous system data to Supabase
    """

    def __init__(self):
        # Initialize Supabase client
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')

        if self.supabase_url and self.supabase_key and Client:
            try:
                self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
                self.connected = True
                logger.info("✅ Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Supabase client: {e}")
                self.supabase = None
                self.connected = False
        else:
            logger.warning("⚠️ Supabase not configured - running in mock mode")
            self.supabase = None
            self.connected = False

    async def sync_symbol_analysis(self, symbol: str, analysis_data: Dict[str, Any]) -> bool:
        """
        Sync symbol analysis data to cryptometer_symbol_analysis table
        """
        try:
            if not self.connected:
                logger.debug(f"Mock sync: symbol analysis for {symbol}")
                return True

            # Extract analysis components
            ai_recommendation = analysis_data.get('ai_recommendation', {})
            primary_rec = ai_recommendation.get('primary_recommendation', {})

            # Prepare data for insertion
            sync_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'short_term_score': analysis_data.get('short_term', {}).get('score', 0),
                'medium_term_score': analysis_data.get('medium_term', {}).get('score', 0),
                'long_term_score': analysis_data.get('long_term', {}).get('score', 0),
                'ai_recommendation': ai_recommendation,
                'primary_timeframe': primary_rec.get('timeframe', 'UNKNOWN'),
                'primary_action': primary_rec.get('action', 'AVOID'),
                'position_size': primary_rec.get('position_size', 'NONE'),
                'reasoning': primary_rec.get('reasoning', ''),
                'data_points_collected': analysis_data.get('data_points', 0),
                'endpoints_called': analysis_data.get('endpoints_called', 0),
                'risk_level': ai_recommendation.get('risk_assessment', 'HIGH'),
                'confidence_score': self._calculate_confidence_score(analysis_data),
                'raw_analysis_data': analysis_data
            }

            # Check for existing entry today first
            today = datetime.now().date()
            existing = self.supabase.table('cryptometer_symbol_analysis')\
                .select('id')\
                .eq('symbol', symbol)\
                .gte('timestamp', f'{today}T00:00:00')\
                .lt('timestamp', f'{today}T23:59:59')\
                .execute()

            if existing.data:
                # Update existing record
                result = self.supabase.table('cryptometer_symbol_analysis')\
                    .update(sync_data)\
                    .eq('id', existing.data[0]['id'])\
                    .execute()
            else:
                # Insert new record
                result = self.supabase.table('cryptometer_symbol_analysis')\
                    .insert(sync_data)\
                    .execute()

            if result.data:
                logger.info(f"✅ Synced symbol analysis for {symbol}")
                return True
            else:
                logger.error(f"❌ Failed to sync symbol analysis for {symbol}")
                return False

        except Exception as e:
            logger.error(f"❌ Error syncing symbol analysis for {symbol}: {e}")
            return False

    async def sync_win_rate_predictions(self, symbol: str, win_rate_data: Dict[str, Any]) -> bool:
        """
        Sync win rate predictions to cryptometer_win_rates table
        """
        try:
            if not self.connected:
                logger.debug(f"Mock sync: win rates for {symbol}")
                return True

            # Extract win rate components
            short_term = win_rate_data.get('short_term_24h', {})
            medium_term = win_rate_data.get('medium_term_7d', {})
            long_term = win_rate_data.get('long_term_1m', {})
            best_opportunity = win_rate_data.get('best_opportunity', {})

            # Prepare data for insertion
            sync_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'short_term_24h_win_rate': short_term.get('win_rate', 0),
                'short_term_24h_confidence': short_term.get('confidence', 0),
                'short_term_direction': short_term.get('direction', 'neutral'),
                'medium_term_7d_win_rate': medium_term.get('win_rate', 0),
                'medium_term_7d_confidence': medium_term.get('confidence', 0),
                'medium_term_direction': medium_term.get('direction', 'neutral'),
                'long_term_1m_win_rate': long_term.get('win_rate', 0),
                'long_term_1m_confidence': long_term.get('confidence', 0),
                'long_term_direction': long_term.get('direction', 'neutral'),
                'overall_confidence': win_rate_data.get('overall_confidence', 0),
                'best_opportunity_timeframe': best_opportunity.get('timeframe', 'unknown'),
                'best_opportunity_win_rate': best_opportunity.get('win_rate', 0),
                'best_opportunity_direction': best_opportunity.get('direction', 'neutral'),
                'reasoning': win_rate_data.get('reasoning', '')
            }

            # Check for existing entry today first
            today = datetime.now().date()
            existing = self.supabase.table('cryptometer_win_rates')\
                .select('id')\
                .eq('symbol', symbol)\
                .gte('timestamp', f'{today}T00:00:00')\
                .lt('timestamp', f'{today}T23:59:59')\
                .execute()

            if existing.data:
                # Update existing record
                result = self.supabase.table('cryptometer_win_rates')\
                    .update(sync_data)\
                    .eq('id', existing.data[0]['id'])\
                    .execute()
            else:
                # Insert new record
                result = self.supabase.table('cryptometer_win_rates')\
                    .insert(sync_data)\
                    .execute()

            if result.data:
                logger.info(f"✅ Synced win rates for {symbol}")
                return True
            else:
                logger.error(f"❌ Failed to sync win rates for {symbol}")
                return False

        except Exception as e:
            logger.error(f"❌ Error syncing win rates for {symbol}: {e}")
            return False

    async def sync_endpoint_data(self, symbol: str, endpoint_results: Dict[str, Any]) -> bool:
        """
        Sync individual endpoint data to cryptometer_endpoint_data table
        """
        try:
            if not self.connected:
                logger.debug(f"Mock sync: endpoint data for {symbol}")
                return True

            # Process each endpoint result
            synced_count = 0
            for endpoint_name, endpoint_result in endpoint_results.items():
                if not isinstance(endpoint_result, dict):
                    continue

                sync_data = {
                    'symbol': symbol,
                    'endpoint_name': endpoint_name,
                    'timestamp': datetime.now().isoformat(),
                    'success': endpoint_result.get('success', False),
                    'response_data': endpoint_result.get('data', {}),
                    'error_message': endpoint_result.get('error'),
                    'data_points_extracted': len(endpoint_result.get('data', {})) if endpoint_result.get('data') else 0,
                    'cached': endpoint_result.get('cached', False),
                    'endpoint_description': endpoint_result.get('description', '')
                }

                result = self.supabase.table('cryptometer_endpoint_data').insert(sync_data).execute()

                if result.data:
                    synced_count += 1

            logger.info(f"✅ Synced {synced_count} endpoint results for {symbol}")
            return synced_count > 0

        except Exception as e:
            logger.error(f"❌ Error syncing endpoint data for {symbol}: {e}")
            return False

    async def sync_pattern_analysis(self, symbol: str, patterns_data: Dict[str, Any]) -> bool:
        """
        Sync pattern analysis to cryptometer_patterns table
        """
        try:
            if not self.connected:
                logger.debug(f"Mock sync: patterns for {symbol}")
                return True

            synced_count = 0

            # Process each timeframe's patterns
            for timeframe in ['short_term', 'medium_term', 'long_term']:
                timeframe_data = patterns_data.get(timeframe, {})
                patterns = timeframe_data.get('patterns', [])

                for pattern in patterns:
                    sync_data = {
                        'symbol': symbol,
                        'timeframe': timeframe.replace('_term', '').upper(),
                        'timestamp': datetime.now().isoformat(),
                        'pattern_type': pattern.get('type', 'unknown'),
                        'pattern_confidence': pattern.get('confidence', 0),
                        'pattern_description': pattern.get('description', ''),
                        'signal': timeframe_data.get('signal', 'NEUTRAL'),
                        'confluence_count': timeframe_data.get('confluence', {}).get('confluence_count', 1),
                        'confluence_multiplier': timeframe_data.get('confluence', {}).get('multiplier', 1.0),
                        'final_score': timeframe_data.get('score', 0),
                        'base_scores': timeframe_data.get('confluence', {}).get('base_scores', []),
                        'base_success_rate': pattern.get('confidence', 0),
                        'trade_type': timeframe_data.get('trade_type', 'UNKNOWN')
                    }

                    result = self.supabase.table('cryptometer_patterns').insert(sync_data).execute()

                    if result.data:
                        synced_count += 1

            logger.info(f"✅ Synced {synced_count} patterns for {symbol}")
            return synced_count > 0

        except Exception as e:
            logger.error(f"❌ Error syncing patterns for {symbol}: {e}")
            return False

    async def sync_system_status(self, status_data: Dict[str, Any]) -> bool:
        """
        Sync system status to cryptometer_system_status table
        """
        try:
            if not self.connected:
                logger.debug("Mock sync: system status")
                return True

            sync_data = {
                'timestamp': datetime.now().isoformat(),
                'agent_running': status_data.get('running', False),
                'last_successful_update': status_data.get('last_update'),
                'next_update_due': status_data.get('next_update'),
                'update_interval_hours': status_data.get('update_interval_hours', 24),
                'symbols_attempted': status_data.get('symbols_attempted', 0),
                'symbols_successful': status_data.get('symbols_successful', 0),
                'symbols_failed': status_data.get('symbols_failed', 0),
                'total_endpoints_called': status_data.get('total_endpoints_called', 0),
                'total_data_points': status_data.get('total_data_points', 0),
                'session_errors': status_data.get('errors', []),
                'failed_symbols': status_data.get('failed_symbols', []),
                'api_configured': status_data.get('api_configured', False),
                'autonomous_features': status_data.get('autonomous_features', {}),
                'system_health': status_data.get('system_health', 'unknown'),
                'session_duration_minutes': status_data.get('duration_minutes'),
                'session_started_at': status_data.get('started_at'),
                'session_completed_at': status_data.get('completed_at'),
                'session_id': status_data.get('session_id')
            }

            result = self.supabase.table('cryptometer_system_status').insert(sync_data).execute()

            if result.data:
                logger.info("✅ Synced system status")
                return True
            else:
                logger.error("❌ Failed to sync system status")
                return False

        except Exception as e:
            logger.error(f"❌ Error syncing system status: {e}")
            return False

    async def sync_daily_summary(self, symbol: str, summary_data: Dict[str, Any]) -> bool:
        """
        Sync daily summary to cryptometer_daily_summary table
        """
        try:
            if not self.connected:
                logger.debug(f"Mock sync: daily summary for {symbol}")
                return True

            ai_rec = summary_data.get('ai_recommendation', {})
            primary_rec = ai_rec.get('primary_recommendation', {})

            sync_data = {
                'symbol': symbol,
                'analysis_date': date.today().isoformat(),
                'best_timeframe': primary_rec.get('timeframe', 'UNKNOWN'),
                'best_score': primary_rec.get('score', 0),
                'best_action': primary_rec.get('action', 'AVOID'),
                'best_win_rate': 0,  # Will be updated separately
                'short_patterns_count': len(summary_data.get('short_term', {}).get('patterns', [])),
                'medium_patterns_count': len(summary_data.get('medium_term', {}).get('patterns', [])),
                'long_patterns_count': len(summary_data.get('long_term', {}).get('patterns', [])),
                'total_endpoints_called': summary_data.get('endpoints_called', 0),
                'total_data_points': summary_data.get('data_points', 0),
                'analysis_success': 'error' not in summary_data,
                'summary_data': summary_data
            }

            # Check for existing entry for today
            existing = self.supabase.table('cryptometer_daily_summary')\
                .select('id')\
                .eq('symbol', symbol)\
                .eq('analysis_date', sync_data['analysis_date'])\
                .execute()

            if existing.data:
                # Update existing record
                result = self.supabase.table('cryptometer_daily_summary')\
                    .update(sync_data)\
                    .eq('id', existing.data[0]['id'])\
                    .execute()
            else:
                # Insert new record
                result = self.supabase.table('cryptometer_daily_summary')\
                    .insert(sync_data)\
                    .execute()

            if result.data:
                logger.info(f"✅ Synced daily summary for {symbol}")
                return True
            else:
                logger.error(f"❌ Failed to sync daily summary for {symbol}")
                return False

        except Exception as e:
            logger.error(f"❌ Error syncing daily summary for {symbol}: {e}")
            return False

    async def sync_complete_symbol_data(self, symbol_data: Dict[str, Any]) -> bool:
        """
        Sync complete symbol data from autonomous system
        """
        try:
            symbol = symbol_data.get('symbol', 'UNKNOWN')
            logger.info(f"🔄 Starting complete sync for {symbol}")

            success_count = 0
            total_operations = 5

            # 1. Sync symbol analysis
            if 'multi_timeframe_analysis' in symbol_data:
                if await self.sync_symbol_analysis(symbol, symbol_data['multi_timeframe_analysis']):
                    success_count += 1

            # 2. Sync win rate predictions
            if 'win_rate_predictions' in symbol_data:
                if await self.sync_win_rate_predictions(symbol, symbol_data['win_rate_predictions']):
                    success_count += 1

            # 3. Sync endpoint data (from raw analysis)
            analysis_data = symbol_data.get('multi_timeframe_analysis', {})
            if analysis_data:
                # Extract endpoint data from analysis
                endpoint_results = {}
                for key, value in analysis_data.items():
                    if isinstance(value, dict) and 'success' in value:
                        endpoint_results[key] = value

                if endpoint_results and await self.sync_endpoint_data(symbol, endpoint_results):
                    success_count += 1

            # 4. Sync pattern analysis
            if analysis_data and await self.sync_pattern_analysis(symbol, analysis_data):
                success_count += 1

            # 5. Sync daily summary
            if await self.sync_daily_summary(symbol, symbol_data):
                success_count += 1

            success_rate = (success_count / total_operations) * 100
            logger.info(f"✅ Completed sync for {symbol}: {success_count}/{total_operations} operations successful ({success_rate:.1f}%)")

            return success_count >= (total_operations * 0.8)  # 80% success rate required

        except Exception as e:
            logger.error(f"❌ Error in complete sync for {symbol}: {e}")
            return False

    async def get_latest_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get latest analysis for a symbol from Supabase
        """
        try:
            if not self.connected:
                return None

            result = self.supabase.table('cryptometer_symbol_analysis')\
                .select('*')\
                .eq('symbol', symbol)\
                .order('timestamp', desc=True)\
                .limit(1)\
                .execute()

            if result.data:
                return result.data[0]

            return None

        except Exception as e:
            logger.error(f"❌ Error getting latest analysis for {symbol}: {e}")
            return None

    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get current system health from Supabase
        """
        try:
            if not self.connected:
                return {"status": "disconnected", "connected": False}

            # Get latest system status
            result = self.supabase.table('cryptometer_system_status')\
                .select('*')\
                .order('timestamp', desc=True)\
                .limit(1)\
                .execute()

            if result.data:
                status = result.data[0]
                return {
                    "status": "connected",
                    "connected": True,
                    "last_update": status.get('last_successful_update'),
                    "symbols_successful": status.get('symbols_successful', 0),
                    "symbols_failed": status.get('symbols_failed', 0),
                    "success_rate": (status.get('symbols_successful', 0) / max(status.get('symbols_attempted', 1), 1)) * 100,
                    "system_health": status.get('system_health', 'unknown')
                }

            return {"status": "no_data", "connected": True}

        except Exception as e:
            logger.error(f"❌ Error getting system health: {e}")
            return {"status": "error", "connected": False, "error": str(e)}

    def _calculate_confidence_score(self, analysis_data: Dict[str, Any]) -> float:
        """
        Calculate overall confidence score from analysis data
        """
        try:
            scores = []

            # Get timeframe scores
            for timeframe in ['short_term', 'medium_term', 'long_term']:
                tf_data = analysis_data.get(timeframe, {})
                if 'score' in tf_data:
                    scores.append(tf_data['score'] / 100.0)  # Convert to 0-1 scale

            # Get AI recommendation confidence
            ai_rec = analysis_data.get('ai_recommendation', {})
            if 'risk_assessment' in ai_rec:
                risk_level = ai_rec['risk_assessment']
                if risk_level == 'LOW':
                    scores.append(0.9)
                elif risk_level == 'MEDIUM':
                    scores.append(0.7)
                else:  # HIGH
                    scores.append(0.5)

            # Calculate average confidence
            if scores:
                return sum(scores) / len(scores)

            return 0.5  # Default medium confidence

        except Exception:
            return 0.5

# Global instance
_cryptometer_supabase = None

async def get_cryptometer_supabase() -> CryptometerSupabaseIntegration:
    """Get or create Cryptometer Supabase integration instance"""
    global _cryptometer_supabase
    if _cryptometer_supabase is None:
        _cryptometer_supabase = CryptometerSupabaseIntegration()
    return _cryptometer_supabase

async def sync_cryptometer_data_to_supabase(symbol_data: Dict[str, Any]) -> bool:
    """
    Convenience function to sync cryptometer data to Supabase
    """
    try:
        integration = await get_cryptometer_supabase()
        return await integration.sync_complete_symbol_data(symbol_data)
    except Exception as e:
        logger.error(f"❌ Error syncing to Supabase: {e}")
        return False