#!/usr/bin/env python3
"""
Manus AI Webhook Routes
API endpoints for handling Manus AI webhooks and integration
"""

from fastapi import APIRouter, Request, HTTPException, Header, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import logging
import json
from datetime import datetime

from ..services.manus_webhook_service import manus_webhook_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks/manus", tags=["Manus Webhooks"])

@router.post("/")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_manus_signature: Optional[str] = Header(None)
):
    """
    Receive and process webhook events from Manus AI

    Args:
        request: FastAPI request object
        background_tasks: FastAPI background tasks
        x_manus_signature: Webhook signature for verification

    Returns:
        Acknowledgment response
    """
    try:
        # Get raw body for signature verification
        body = await request.body()

        # Verify webhook signature if provided
        if x_manus_signature:
            if not manus_webhook_service.verify_webhook_signature(body, x_manus_signature):
                logger.warning("Invalid webhook signature")
                raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse webhook payload
        payload = await request.json()

        logger.info(f"Received Manus webhook: {payload.get('event', 'unknown')}")

        # Process webhook in background to return quickly
        background_tasks.add_task(
            process_webhook_async,
            payload
        )

        return JSONResponse(
            status_code=200,
            content={
                'status': 'received',
                'message': 'Webhook received and queued for processing',
                'timestamp': datetime.now().isoformat()
            }
        )

    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_webhook_async(payload: Dict[str, Any]):
    """
    Process webhook asynchronously

    Args:
        payload: Webhook event data
    """
    try:
        result = manus_webhook_service.process_webhook_event(payload)
        logger.info(f"Webhook processed: {result}")
    except Exception as e:
        logger.error(f"Error in async webhook processing: {e}")

@router.post("/register")
async def register_webhook(
    events: Optional[List[str]] = None,
    webhook_url: Optional[str] = None
):
    """
    Register a new webhook with Manus AI

    Args:
        events: List of event types to subscribe to
        webhook_url: Optional custom webhook URL (defaults to configured URL)

    Returns:
        Webhook registration details
    """
    try:
        # Override webhook URL if provided
        if webhook_url:
            manus_webhook_service.webhook_url = webhook_url

        result = manus_webhook_service.register_webhook(events)

        return JSONResponse(
            status_code=200,
            content={
                'status': 'success',
                'message': 'Webhook registered successfully',
                'webhook': result
            }
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error registering webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/unregister/{webhook_id}")
async def unregister_webhook(webhook_id: str):
    """
    Unregister a webhook from Manus AI

    Args:
        webhook_id: The webhook ID to unregister

    Returns:
        Unregistration status
    """
    try:
        success = manus_webhook_service.unregister_webhook(webhook_id)

        if success:
            return JSONResponse(
                status_code=200,
                content={
                    'status': 'success',
                    'message': f'Webhook {webhook_id} unregistered successfully'
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to unregister webhook {webhook_id}"
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error unregistering webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_webhook_status():
    """
    Get current webhook configuration and status

    Returns:
        Webhook status information
    """
    try:
        status = manus_webhook_service.get_webhook_status()

        return JSONResponse(
            status_code=200,
            content={
                'status': 'success',
                'data': status,
                'timestamp': datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error getting webhook status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test")
async def test_webhook():
    """
    Test webhook configuration by sending a test event

    Returns:
        Test result
    """
    try:
        # Create a test task to trigger webhook
        test_task = {
            'name': 'Test Task',
            'description': 'Testing Manus webhook integration',
            'parameters': {
                'test': True,
                'timestamp': datetime.now().isoformat()
            }
        }

        result = manus_webhook_service.create_task(test_task)

        return JSONResponse(
            status_code=200,
            content={
                'status': 'success',
                'message': 'Test task created successfully',
                'task': result,
                'note': 'Check webhook endpoint for incoming events'
            }
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error testing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks")
async def create_manus_task(task_data: Dict[str, Any]):
    """
    Create a new task in Manus AI

    Args:
        task_data: Task configuration and parameters

    Returns:
        Created task details
    """
    try:
        result = manus_webhook_service.create_task(task_data)

        return JSONResponse(
            status_code=201,
            content={
                'status': 'success',
                'message': 'Task created successfully',
                'task': result
            }
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/riskmetric/status")
async def get_riskmetric_status():
    """
    Get comprehensive RISKMETRIC autonomous system status

    Returns:
        Complete status of the autonomous RISKMETRIC system
    """
    try:
        import subprocess
        import json as json_lib
        from pathlib import Path

        # Get health check status
        try:
            result = subprocess.run(['python3', 'check_system_health.py'],
                                 capture_output=True, text=True, timeout=10,
                                 cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')
            health_status = "healthy" if result.returncode == 0 else "issues"
        except Exception:
            health_status = "unknown"

        # Get background agent status
        try:
            agent_result = subprocess.run(['python3', 'services/cryptoverse_background_agent.py', '--status'],
                                       capture_output=True, text=True, timeout=5,
                                       cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')
            agent_status = json_lib.loads(agent_result.stdout) if agent_result.stdout else {"running": False}
        except Exception:
            agent_status = {"running": False}

        # Check extracted risk grids
        risk_grids_dir = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/extracted_risk_grids')
        risk_grids_count = len(list(risk_grids_dir.glob("*.json"))) if risk_grids_dir.exists() else 0

        return JSONResponse(
            status_code=200,
            content={
                'status': 'success',
                'riskmetric_system': {
                    'autonomous_scraper': {
                        'status': 'active' if agent_status.get('running') else 'inactive',
                        'background_agent': agent_status,
                        'update_interval': '72 hours',
                        'scraping_method': 'MCP Browser + IntoTheCryptoverse',
                        'symbols_supported': 25
                    },
                    'data_status': {
                        'health': health_status,
                        'risk_grids_available': risk_grids_count,
                        'supabase_sync': 'enabled',
                        'atomic_operations': 'enabled'
                    },
                    'capabilities': {
                        'real_time_scraping': True,
                        'all_25_symbols': True,
                        'supabase_sync': True,
                        'atomic_operations': True,
                        'auto_update_72h': True,
                        'zero_manual_intervention': True,
                        'self_healing': True
                    },
                    'webhook_integration': {
                        'enabled': True,
                        'risk_analysis_endpoint': '/api/riskmetric/{symbol}',
                        'status_endpoint': '/api/webhooks/manus/riskmetric/status',
                        'force_update_endpoint': '/api/webhooks/manus/riskmetric/force-update'
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error getting RISKMETRIC status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/riskmetric/force-update")
async def force_riskmetric_update():
    """
    Force an immediate RISKMETRIC update cycle

    Returns:
        Update initiation status
    """
    try:
        import subprocess

        # Trigger immediate update by running the production scraper
        result = subprocess.Popen(['python3', 'cryptoverse_mcp_production.py'],
                                cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')

        return JSONResponse(
            status_code=202,
            content={
                'status': 'success',
                'message': 'RISKMETRIC force update initiated',
                'process_id': result.pid,
                'note': 'Update running in background. Check status endpoint for progress.',
                'estimated_completion': '2-3 minutes',
                'timestamp': datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error forcing RISKMETRIC update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/riskmetric/{symbol}")
async def get_symbol_riskmetric(symbol: str):
    """
    Get RISKMETRIC data for a specific symbol via webhook integration

    Args:
        symbol: Cryptocurrency symbol (e.g., BTC, ETH)

    Returns:
        Risk metric data for the specified symbol
    """
    try:
        # Call the RISKMETRIC service directly
        result = manus_webhook_service._call_riskmetric(symbol.upper())

        return JSONResponse(
            status_code=200,
            content={
                'status': 'success',
                'data': result,
                'timestamp': datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error getting RISKMETRIC for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cryptometer/status")
async def get_cryptometer_status():
    """
    Get comprehensive Cryptometer autonomous system status

    Returns:
        Complete status of the autonomous Cryptometer system
    """
    try:
        import subprocess
        import json as json_lib
        from pathlib import Path

        # Get health check status
        try:
            result = subprocess.run(['python3', 'check_system_health.py'],
                                 capture_output=True, text=True, timeout=10,
                                 cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')
            health_status = "healthy" if result.returncode == 0 else "issues"
        except Exception:
            health_status = "unknown"

        # Get background agent status
        try:
            agent_result = subprocess.run(['python3', 'services/cryptometer_background_agent.py', 'status'],
                                       capture_output=True, text=True, timeout=5,
                                       cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')
            agent_status = json_lib.loads(agent_result.stdout) if agent_result.stdout else {"running": False}
        except Exception:
            agent_status = {"running": False}

        # Check extracted cryptometer data
        data_dir = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/extracted_cryptometer_data')
        data_files_count = len(list(data_dir.glob("*.json"))) if data_dir.exists() else 0

        return JSONResponse(
            status_code=200,
            content={
                'status': 'success',
                'cryptometer_system': {
                    'autonomous_scraper': {
                        'status': 'active' if agent_status.get('running') else 'inactive',
                        'background_agent': agent_status,
                        'update_interval_hours': 24,
                        'multi_timeframe_analysis': True,
                        'ai_powered': True,
                        'symbols_supported': 25
                    },
                    'data_status': {
                        'health': health_status,
                        'data_files_available': data_files_count,
                        'api_configured': bool(os.getenv('CRYPTOMETER_API_KEY')),
                        'endpoints_available': 17
                    },
                    'capabilities': {
                        'multi_timeframe_analysis': True,
                        'all_25_symbols': True,
                        'ai_powered_analysis': True,
                        'win_rate_predictions': True,
                        'autonomous_updates_24h': True,
                        'zero_manual_intervention': True,
                        'real_time_api_access': bool(os.getenv('CRYPTOMETER_API_KEY')),
                        'self_healing': True
                    },
                    'webhook_integration': {
                        'enabled': True,
                        'analysis_endpoint': '/api/cryptometer/{symbol}',
                        'status_endpoint': '/api/webhooks/manus/cryptometer/status',
                        'force_update_endpoint': '/api/webhooks/manus/cryptometer/force-update'
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error getting Cryptometer status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cryptometer/force-update")
async def force_cryptometer_update():
    """
    Force an immediate Cryptometer update cycle

    Returns:
        Update initiation status
    """
    try:
        import subprocess

        # Trigger immediate update by running the autonomous system
        result = subprocess.Popen(['python3', 'cryptometer_autonomous_system.py'],
                                cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')

        return JSONResponse(
            status_code=202,
            content={
                'status': 'success',
                'message': 'Cryptometer force update initiated',
                'process_id': result.pid,
                'note': 'Update running in background. Check status endpoint for progress.',
                'estimated_completion': '3-5 minutes',
                'timestamp': datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error forcing Cryptometer update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cryptometer/{symbol}")
async def get_symbol_cryptometer(symbol: str):
    """
    Get Cryptometer data for a specific symbol via webhook integration

    Args:
        symbol: Cryptocurrency symbol (e.g., BTC, ETH)

    Returns:
        Cryptometer analysis data for the specified symbol
    """
    try:
        # Call the Cryptometer service directly
        result = manus_webhook_service._call_cryptometer(symbol.upper())

        return JSONResponse(
            status_code=200,
            content={
                'status': 'success',
                'data': result,
                'timestamp': datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error getting Cryptometer for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))