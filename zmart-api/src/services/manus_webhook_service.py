#!/usr/bin/env python3
"""
Manus AI Webhook Service
Handles webhook registration and processing for Manus AI integration
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import hmac
from fastapi import HTTPException
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class ManusWebhookService:
    """
    Manages Manus AI webhook configuration and processing
    """

    def __init__(self):
        self.api_key = os.getenv('MANUS_API_KEY', '')
        self.base_url = "https://api.manus.ai"
        self.webhook_url = os.getenv('MANUS_WEBHOOK_URL', 'http://localhost:8000/api/webhooks/manus')
        self.registered_webhooks = []

        # Integration services - ALL AGENTS AND SERVICES
        self.integrations = {
            # Core AI Services
            'kingfisher': {
                'url': "http://localhost:8098",
                'enabled': True,
                'type': 'ai_analysis'
            },
            'cryptometer': {
                'api_key': os.getenv('CRYPTOMETER_API_KEY', ''),
                'base_url': "https://api.cryptometer.io",
                'enabled': bool(os.getenv('CRYPTOMETER_API_KEY', '')),
                'type': 'market_data',
                'autonomous_system': True,
                'multi_timeframe_analysis': True,
                'supports_all_symbols': True,
                'update_interval_hours': 24,
                'ai_powered': True,
                'win_rate_predictions': True,
                'endpoints_count': 17
            },
            'riskmetric': {
                'url': "http://localhost:8000/api/riskmetric",
                'enabled': True,
                'type': 'risk_analysis',
                'autonomous_scraper': True,
                'supabase_sync': True,
                'supports_all_symbols': True
            },
            # AI Agents
            'unified_analysis': {
                'url': "http://localhost:8000/api/unified-analysis",
                'enabled': True,
                'type': 'comprehensive_analysis'
            },
            'multi_model_ai': {
                'url': "http://localhost:8000/api/multi-model",
                'enabled': True,
                'type': 'multi_model_prediction'
            },
            'sentiment_analysis': {
                'url': "http://localhost:8000/api/sentiment",
                'enabled': True,
                'type': 'sentiment_scoring'
            },
            'pattern_recognition': {
                'url': "http://localhost:8000/api/patterns",
                'enabled': True,
                'type': 'pattern_analysis'
            },
            # Trading Services
            'signal_center': {
                'url': "http://localhost:8000/api/signals",
                'enabled': True,
                'type': 'signal_generation'
            },
            'technical_analysis': {
                'url': "http://localhost:8000/api/technical",
                'enabled': True,
                'type': 'technical_indicators'
            },
            'scoring_service': {
                'url': "http://localhost:8000/api/scoring",
                'enabled': True,
                'type': 'scoring_system'
            },
            # Data Services
            'market_data': {
                'url': "http://localhost:8000/api/market-data",
                'enabled': True,
                'type': 'real_time_data'
            },
            'kucoin_service': {
                'url': "http://localhost:8000/api/kucoin",
                'enabled': True,
                'type': 'exchange_integration'
            },
            # Notification Services
            'telegram_alerts': {
                'enabled': bool(os.getenv('TELEGRAM_BOT_TOKEN', '')),
                'type': 'notifications'
            },
            # Advanced Features
            'neural_network': {
                'url': "http://localhost:8000/api/neural",
                'enabled': True,
                'type': 'ml_optimization'
            },
            'predictive_analytics': {
                'url': "http://localhost:8000/api/predictive",
                'enabled': True,
                'type': 'prediction'
            },
            'learning_agent': {
                'url': "http://localhost:8000/api/learning",
                'enabled': True,
                'type': 'self_learning'
            },
            # Master Control
            'master_orchestration': {
                'url': "http://localhost:8097",  # Master Orchestration Agent port
                'enabled': True,
                'type': 'master_control',
                'priority': 'CRITICAL'
            }
        }

        # Keep backward compatibility
        self.kingfisher_url = self.integrations['kingfisher']['url']
        self.cryptometer_api_key = self.integrations['cryptometer']['api_key']
        self.cryptometer_base_url = self.integrations['cryptometer']['base_url']
        self.riskmetric_enabled = self.integrations['riskmetric']['enabled']

        if not self.api_key:
            logger.warning("Manus API key not configured")

        logger.info(f"Manus Webhook Service initialized (Webhook URL: {self.webhook_url})")
        logger.info(f"KingFisher integration: {self.kingfisher_url}")
        logger.info(f"Cryptometer integration: {'Configured' if self.cryptometer_api_key else 'Not configured'}")

    def register_webhook(self, events: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Register a webhook with Manus AI

        Args:
            events: List of event types to subscribe to (optional)
                   Default: ['task.created', 'task.completed', 'task.failed']

        Returns:
            Webhook registration response
        """
        if not self.api_key:
            raise HTTPException(status_code=500, detail="Manus API key not configured")

        if events is None:
            events = ['task.created', 'task.completed', 'task.failed', 'task.updated']

        try:
            headers = {
                'API_KEY': self.api_key,  # Based on OpenAPI spec
                'Content-Type': 'application/json'
            }

            # Use the correct format as per Manus API specification
            payload = {
                'webhook': {
                    'url': self.webhook_url
                }
            }

            response = requests.post(
                f"{self.base_url}/v1/webhooks",
                headers=headers,
                json=payload
            )

            if response.status_code == 200 or response.status_code == 201:
                webhook_data = response.json()
                webhook_id = webhook_data.get('webhook_id')

                # Store webhook info
                webhook_info = {
                    'webhook_id': webhook_id,
                    'url': self.webhook_url,
                    'registered_at': datetime.now().isoformat()
                }
                self.registered_webhooks.append(webhook_info)

                logger.info(f"Successfully registered Manus webhook: {webhook_id}")
                return webhook_info
            else:
                logger.error(f"Failed to register webhook: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to register webhook: {response.text}"
                )

        except requests.exceptions.RequestException as e:
            logger.error(f"Error registering webhook: {e}")
            raise HTTPException(status_code=500, detail=f"Error registering webhook: {str(e)}")

    def unregister_webhook(self, webhook_id: str) -> bool:
        """
        Unregister a webhook from Manus AI

        Args:
            webhook_id: The webhook ID to unregister

        Returns:
            True if successful, False otherwise
        """
        if not self.api_key:
            logger.error("Manus API key not configured")
            return False

        try:
            headers = {
                'API_KEY': self.api_key,  # Based on OpenAPI spec
                'Content-Type': 'application/json'
            }

            response = requests.delete(
                f"{self.base_url}/v1/webhooks/{webhook_id}",
                headers=headers
            )

            if response.status_code == 200 or response.status_code == 204:
                logger.info(f"Successfully unregistered webhook: {webhook_id}")
                self.registered_webhooks = [
                    w for w in self.registered_webhooks
                    if w.get('webhook_id') != webhook_id
                ]
                return True
            else:
                logger.error(f"Failed to unregister webhook: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error unregistering webhook: {e}")
            return False

    def process_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming webhook event from Manus AI

        Args:
            event_data: The webhook event payload

        Returns:
            Processing result
        """
        try:
            event_type = event_data.get('event')
            task_id = event_data.get('task_id')
            timestamp = event_data.get('timestamp', datetime.now().isoformat())

            logger.info(f"Processing Manus webhook event: {event_type} for task {task_id}")

            # Handle different event types
            if event_type == 'task.created':
                return self._handle_task_created(event_data)
            elif event_type == 'task.completed':
                return self._handle_task_completed(event_data)
            elif event_type == 'task.failed':
                return self._handle_task_failed(event_data)
            elif event_type == 'task.updated':
                return self._handle_task_updated(event_data)
            else:
                logger.warning(f"Unknown event type: {event_type}")
                return {
                    'status': 'unknown',
                    'event_type': event_type,
                    'message': 'Unknown event type'
                }

        except Exception as e:
            logger.error(f"Error processing webhook event: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _handle_task_created(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task created event"""
        task_id = event_data.get('task_id')
        task_data = event_data.get('data', {})

        logger.info(f"Task created: {task_id}")

        # Store task information for tracking
        # You can integrate this with your database or task management system

        return {
            'status': 'processed',
            'event_type': 'task.created',
            'task_id': task_id,
            'message': 'Task creation acknowledged'
        }

    def _handle_task_completed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task completed event with KingFisher and Cryptometer integration"""
        task_id = event_data.get('task_id')
        result = event_data.get('result', {})

        logger.info(f"Task completed: {task_id}")

        # Process the completed task result with integrations
        integration_results = self._process_with_integrations(event_data)

        return {
            'status': 'processed',
            'event_type': 'task.completed',
            'task_id': task_id,
            'message': 'Task completion processed with integrations',
            'result_summary': {
                'success': True,
                'processed_at': datetime.now().isoformat(),
                'integrations': integration_results
            }
        }

    def _handle_task_failed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task failed event"""
        task_id = event_data.get('task_id')
        error = event_data.get('error', {})

        logger.error(f"Task failed: {task_id} - {error}")

        # Handle task failure
        # You might want to retry, alert, or take corrective action

        return {
            'status': 'processed',
            'event_type': 'task.failed',
            'task_id': task_id,
            'message': 'Task failure handled',
            'error_info': error
        }

    def _handle_task_updated(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task updated event"""
        task_id = event_data.get('task_id')
        updates = event_data.get('updates', {})

        logger.info(f"Task updated: {task_id}")

        return {
            'status': 'processed',
            'event_type': 'task.updated',
            'task_id': task_id,
            'message': 'Task update processed',
            'updates': updates
        }

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature for security

        Args:
            payload: The raw webhook payload
            signature: The signature from the webhook headers

        Returns:
            True if signature is valid
        """
        if not self.api_key:
            return False

        try:
            # Create HMAC signature using API key as secret
            expected_signature = hmac.new(
                self.api_key.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()

            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)

        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new task in Manus AI

        Args:
            task_data: Task configuration and parameters

        Returns:
            Task creation response
        """
        if not self.api_key:
            raise HTTPException(status_code=500, detail="Manus API key not configured")

        try:
            headers = {
                'API_KEY': self.api_key,  # Based on OpenAPI spec
                'Content-Type': 'application/json'
            }

            response = requests.post(
                f"{self.base_url}/v1/tasks",
                headers=headers,
                json=task_data
            )

            if response.status_code == 200 or response.status_code == 201:
                task_response = response.json()
                logger.info(f"Successfully created Manus task: {task_response.get('id')}")
                return task_response
            else:
                logger.error(f"Failed to create task: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to create task: {response.text}"
                )

        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating task: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

    def get_webhook_status(self) -> Dict[str, Any]:
        """
        Get current webhook configuration status

        Returns:
            Status information
        """
        return {
            'configured': bool(self.api_key),
            'webhook_url': self.webhook_url,
            'registered_webhooks': len(self.registered_webhooks),
            'webhooks': [
                {
                    'webhook_id': w.get('webhook_id'),
                    'url': w.get('url'),
                    'registered_at': w.get('registered_at')
                }
                for w in self.registered_webhooks
            ],
            'integrations': {
                'kingfisher': {'url': self.kingfisher_url, 'status': 'active'},
                'cryptometer': {'configured': bool(self.cryptometer_api_key), 'status': 'active' if self.cryptometer_api_key else 'inactive'},
                'riskmetric': {'enabled': self.riskmetric_enabled, 'status': 'active'}
            }
        }

    def _process_with_integrations(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook event with ALL integrated services and agents

        Args:
            event_data: The webhook event data

        Returns:
            Integration results from all services
        """
        integration_results = {}

        # Extract relevant data for analysis
        task_data = event_data.get('data', {})
        symbol = task_data.get('symbol', 'BTCUSDT')

        logger.info(f"🚀 Processing Manus webhook with ALL agents for {symbol}")

        # Process all enabled integrations
        for name, config in self.integrations.items():
            if config.get('enabled', False):
                try:
                    # Skip non-API services
                    if name == 'telegram_alerts':
                        # Handle telegram separately if needed
                        continue

                    # Call the appropriate integration
                    if name == 'kingfisher':
                        result = self._call_kingfisher(symbol, task_data)
                    elif name == 'cryptometer':
                        result = self._call_cryptometer(symbol)
                    elif name == 'riskmetric':
                        result = self._call_riskmetric(symbol)
                    elif name == 'master_orchestration':
                        result = self._call_master_orchestration(symbol, task_data)
                    else:
                        # Generic API call for other services
                        result = self._call_generic_service(name, config, symbol, task_data)

                    integration_results[name] = result
                    logger.info(f"✅ {name} analysis completed for {symbol}")

                except Exception as e:
                    logger.error(f"❌ {name} integration error: {e}")
                    integration_results[name] = {'error': str(e), 'status': 'failed'}

        # Send summary to Master Orchestration if critical event
        if event_data.get('priority') == 'high':
            self._notify_master_orchestration(integration_results)

        logger.info(f"📊 Completed processing with {len(integration_results)} integrations")
        return integration_results

    def _call_kingfisher(self, symbol: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call KingFisher AI for analysis"""
        try:
            response = requests.post(
                f"{self.kingfisher_url}/api/v1/kingfisher/analysis",
                json={
                    'symbol': symbol,
                    'task_data': task_data,
                    'source': 'manus_webhook'
                },
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'error', 'message': f"KingFisher returned {response.status_code}"}
        except Exception as e:
            logger.error(f"Error calling KingFisher: {e}")
            return {'status': 'error', 'message': str(e)}

    def _call_cryptometer(self, symbol: str) -> Dict[str, Any]:
        """Call Cryptometer autonomous system for comprehensive multi-timeframe analysis"""
        try:
            import subprocess
            import json as json_lib
            from pathlib import Path

            # Get autonomous system status first
            try:
                agent_result = subprocess.run(['python3', 'services/cryptometer_background_agent.py', 'status'],
                                           capture_output=True, text=True, timeout=5,
                                           cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')
                agent_status = json_lib.loads(agent_result.stdout) if agent_result.stdout else {"running": False}
            except Exception:
                agent_status = {"running": False}

            # Check for autonomous cryptometer data
            data_dir = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/extracted_cryptometer_data')
            symbol_clean = symbol.upper().replace('USDT', '').replace('USD', '').replace('BUSD', '')
            symbol_file = data_dir / f"{symbol_clean}_cryptometer_data.json"

            symbol_data = None
            if symbol_file.exists():
                with open(symbol_file, 'r') as f:
                    symbol_data = json_lib.load(f)

            # Try live API call if we have API key
            live_data = None
            if self.cryptometer_api_key:
                try:
                    headers = {
                        'x-api-key': self.cryptometer_api_key,
                        'Content-Type': 'application/json'
                    }
                    response = requests.get(
                        f"{self.cryptometer_base_url}/api/ai-screener",
                        params={'symbol': symbol},
                        headers=headers,
                        timeout=10
                    )
                    if response.status_code == 200:
                        live_data = response.json()
                except Exception as e:
                    logger.warning(f"Live Cryptometer API call failed: {e}")

            # Build comprehensive response
            return {
                'status': 'success',
                'symbol': symbol_clean,
                'autonomous_system': {
                    'status': 'active' if agent_status.get('running') else 'inactive',
                    'background_agent': agent_status,
                    'update_interval_hours': 24,
                    'multi_timeframe_analysis': True,
                    'ai_powered': True,
                    'last_update': agent_status.get('last_update', 'unknown')
                },
                'data_status': {
                    'symbol_specific_data': 'available' if symbol_data else 'not_found',
                    'live_api_data': 'available' if live_data else 'not_available',
                    'api_configured': bool(self.cryptometer_api_key)
                },
                'capabilities': {
                    'multi_timeframe_analysis': True,
                    'all_25_symbols': True,
                    'ai_powered_analysis': True,
                    'win_rate_predictions': True,
                    'autonomous_updates_24h': True,
                    'zero_manual_intervention': True,
                    'real_time_api_access': bool(self.cryptometer_api_key),
                    'endpoints_count': 17
                },
                'analysis_data': {
                    'autonomous_data': symbol_data.get('multi_timeframe_analysis') if symbol_data else None,
                    'win_rate_predictions': symbol_data.get('win_rate_predictions') if symbol_data else None,
                    'live_api_data': live_data,
                    'data_points': symbol_data.get('data_points', 0) if symbol_data else 0,
                    'endpoints_called': symbol_data.get('endpoints_called', 0) if symbol_data else 0
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in enhanced Cryptometer call: {e}")
            return {
                'status': 'error',
                'symbol': symbol,
                'error': str(e),
                'autonomous_system': 'error',
                'timestamp': datetime.now().isoformat()
            }

    def _call_riskmetric(self, symbol: str) -> Dict[str, Any]:
        """Call RiskMetric service for comprehensive risk analysis with autonomous system status"""
        try:
            # Get risk data for specific symbol
            response = requests.get(
                f"http://localhost:8000/api/riskmetric/{symbol}",
                timeout=10
            )

            if response.status_code == 200:
                risk_data = response.json()

                # Enhance with autonomous system status
                autonomous_status = self._get_riskmetric_autonomous_status()

                return {
                    'status': 'success',
                    'symbol': symbol,
                    'risk_data': risk_data,
                    'autonomous_system': autonomous_status,
                    'capabilities': {
                        'real_time_scraping': True,
                        'all_25_symbols': True,
                        'supabase_sync': True,
                        'atomic_operations': True,
                        'auto_update_72h': True
                    }
                }
            else:
                return {'status': 'error', 'message': f"RiskMetric returned {response.status_code}"}
        except Exception as e:
            logger.error(f"Error calling RiskMetric: {e}")
            return {'status': 'error', 'message': str(e)}

    def _get_riskmetric_autonomous_status(self) -> Dict[str, Any]:
        """Get status of the autonomous RISKMETRIC system"""
        try:
            # Check autonomous scraper status by calling health check
            import subprocess
            result = subprocess.run(['python3', 'check_system_health.py'],
                                 capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                # Parse health report for status
                return {
                    'status': 'active',
                    'health_check': 'passed',
                    'background_agent': 'running',
                    'last_health_check': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'unknown',
                    'health_check': 'failed',
                    'background_agent': 'unknown'
                }
        except Exception as e:
            logger.error(f"Error checking autonomous status: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _call_generic_service(self, name: str, config: Dict[str, Any], symbol: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic method to call any service API"""
        try:
            url = config.get('url')
            if not url:
                return {'status': 'no_url_configured'}

            # Prepare request based on service type
            service_type = config.get('type', '')

            if 'analysis' in service_type or 'prediction' in service_type:
                # POST request for analysis services
                response = requests.post(
                    f"{url}/analyze",
                    json={'symbol': symbol, 'data': task_data},
                    timeout=10
                )
            else:
                # GET request for data services
                response = requests.get(
                    f"{url}/{symbol}",
                    timeout=10
                )

            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'error', 'code': response.status_code}
        except Exception as e:
            logger.error(f"Error calling {name}: {e}")
            return {'status': 'error', 'message': str(e)}

    def _call_master_orchestration(self, symbol: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Master Orchestration Agent for coordination"""
        try:
            response = requests.post(
                f"{self.integrations['master_orchestration']['url']}/api/v1/orchestrate",
                json={
                    'symbol': symbol,
                    'task_data': task_data,
                    'source': 'manus_webhook',
                    'priority': 'high'
                },
                timeout=15
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'error', 'message': f"Master Orchestration returned {response.status_code}"}
        except Exception as e:
            logger.error(f"Error calling Master Orchestration: {e}")
            return {'status': 'error', 'message': str(e)}

    def _notify_master_orchestration(self, results: Dict[str, Any]) -> None:
        """Notify Master Orchestration of critical events"""
        try:
            requests.post(
                f"{self.integrations['master_orchestration']['url']}/api/v1/notify",
                json={
                    'event': 'manus_webhook_processed',
                    'results': results,
                    'timestamp': datetime.now().isoformat()
                },
                timeout=5
            )
            logger.info("Notified Master Orchestration of event processing")
        except Exception as e:
            logger.error(f"Failed to notify Master Orchestration: {e}")

# Create global instance
manus_webhook_service = ManusWebhookService()