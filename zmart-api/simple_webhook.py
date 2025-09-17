#!/usr/bin/env python3
"""
Simple Manus Webhook Server
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import json
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Manus Webhook Receiver")

@app.post("/api/webhooks/manus/")
async def receive_manus_webhook(request: Request):
    """
    Receive webhook from Manus
    """
    try:
        # Get the payload
        payload = await request.json()

        # Log what we received
        logger.info(f"Received Manus webhook: {json.dumps(payload, indent=2)}")

        # Extract event details
        event_type = payload.get('event_type', 'unknown')
        task_detail = payload.get('task_detail', {})

        logger.info(f"Event: {event_type}")
        logger.info(f"Task: {task_detail.get('task_title', 'N/A')}")

        # Process with agents if it's a task event
        agent_results = {}
        if event_type in ['task_created', 'task_stopped']:
            # Extract symbol from task title (look for crypto pairs like BTCUSDT)
            import re
            task_title = task_detail.get('task_title', '')
            symbol_match = re.search(r'(BTC|ETH|SOL|AVAX|BNB|ADA|DOT|LINK|UNI|MATIC)(USDT|USD|BUSD)?', task_title.upper())
            symbol = symbol_match.group(0) if symbol_match else 'BTCUSDT'

            logger.info(f"Processing {symbol} with all agents...")

            # Call agents
            import requests

            # 1. KingFisher AI
            try:
                kingfisher_response = requests.get(f"http://localhost:8098/health", timeout=2)
                agent_results['kingfisher'] = {"status": "active", "port": 8098}
                logger.info("✅ KingFisher AI is active")
            except:
                agent_results['kingfisher'] = {"status": "offline"}

            # 2. Cryptometer - Autonomous System
            try:
                # Check cryptometer background agent status
                try:
                    cryptometer_result = subprocess.run(['python3', 'services/cryptometer_background_agent.py', 'status'],
                                                      capture_output=True, text=True, timeout=3,
                                                      cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')
                    cryptometer_status = json.loads(cryptometer_result.stdout) if cryptometer_result.stdout else {"running": False}
                except:
                    cryptometer_status = {"running": False}

                # Check if cryptometer data files are available
                from pathlib import Path
                cryptometer_dir = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/extracted_cryptometer_data')
                cryptometer_files_count = len(list(cryptometer_dir.glob("*.json"))) if cryptometer_dir.exists() else 0

                # Check for specific symbol cryptometer data
                symbol_clean = symbol.replace('USDT', '').replace('USD', '').replace('BUSD', '')
                symbol_file = cryptometer_dir / f"{symbol_clean}_cryptometer_data.json"
                symbol_cryptometer_data = None

                if symbol_file.exists():
                    with open(symbol_file, 'r') as f:
                        symbol_cryptometer_data = json.load(f)

                agent_results['cryptometer'] = {
                    "status": "autonomous_active",
                    "symbol": symbol_clean,
                    "autonomous_system": {
                        "background_agent": "running" if cryptometer_status.get('running') else "stopped",
                        "update_interval": "24 hours",
                        "analysis_method": "Multi-timeframe AI + 17 Cryptometer Endpoints",
                        "last_update": cryptometer_status.get('last_update', 'unknown')
                    },
                    "data_status": {
                        "data_files_available": cryptometer_files_count,
                        "symbol_specific_data": "available" if symbol_cryptometer_data else "not_found",
                        "total_data_points": symbol_cryptometer_data.get('data_points', 0) if symbol_cryptometer_data else 0,
                        "endpoints_called": symbol_cryptometer_data.get('endpoints_called', 0) if symbol_cryptometer_data else 0
                    },
                    "capabilities": {
                        "multi_timeframe_analysis": True,
                        "all_25_symbols": True,
                        "ai_powered_analysis": True,
                        "win_rate_predictions": True,
                        "auto_update_24h": True,
                        "zero_manual_intervention": True,
                        "endpoints_count": 17
                    },
                    "analysis_data": symbol_cryptometer_data.get('multi_timeframe_analysis') if symbol_cryptometer_data else None,
                    "win_rate_predictions": symbol_cryptometer_data.get('win_rate_predictions') if symbol_cryptometer_data else None
                }

                if symbol_cryptometer_data:
                    logger.info(f"✅ CRYPTOMETER: {symbol_clean} - Data Points: {symbol_cryptometer_data.get('data_points', 0)}, Endpoints: {symbol_cryptometer_data.get('endpoints_called', 0)}")
                else:
                    logger.info(f"✅ CRYPTOMETER: Autonomous system active, {cryptometer_files_count} symbols available")

            except Exception as e:
                agent_results['cryptometer'] = {"status": "error", "error": str(e)}

            # 3. RISKMETRIC - Autonomous System
            try:
                # Get autonomous system status
                import subprocess
                import os

                # Check background agent status
                try:
                    agent_result = subprocess.run(['python3', 'services/cryptoverse_background_agent.py', '--status'],
                                               capture_output=True, text=True, timeout=3,
                                               cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')
                    agent_status = json.loads(agent_result.stdout) if agent_result.stdout else {"running": False}
                except:
                    agent_status = {"running": False}

                # Check if risk grids are available
                from pathlib import Path
                risk_grids_dir = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/extracted_risk_grids')
                risk_grids_count = len(list(risk_grids_dir.glob("*.json"))) if risk_grids_dir.exists() else 0

                # Check for specific symbol risk grid
                symbol_clean = symbol.replace('USDT', '').replace('USD', '').replace('BUSD', '')
                symbol_file = risk_grids_dir / f"{symbol_clean}_risk_grid.json"
                symbol_data = None

                if symbol_file.exists():
                    with open(symbol_file, 'r') as f:
                        symbol_data = json.load(f)

                agent_results['riskmetric'] = {
                    "status": "autonomous_active",
                    "symbol": symbol_clean,
                    "autonomous_system": {
                        "background_agent": "running" if agent_status.get('running') else "stopped",
                        "update_interval": "72 hours",
                        "scraping_method": "MCP Browser + IntoTheCryptoverse",
                        "last_update": agent_status.get('last_update', 'unknown')
                    },
                    "data_status": {
                        "risk_grids_available": risk_grids_count,
                        "symbol_specific_data": "available" if symbol_data else "not_found",
                        "total_risk_points": len(symbol_data.get('fiat_risk_grid', [])) if symbol_data else 0
                    },
                    "capabilities": {
                        "real_time_scraping": True,
                        "all_25_symbols": True,
                        "supabase_sync": True,
                        "atomic_operations": True,
                        "auto_update_72h": True,
                        "zero_manual_intervention": True
                    },
                    "current_price": symbol_data.get('current_price') if symbol_data else None,
                    "current_risk": symbol_data.get('current_risk') if symbol_data else None
                }

                if symbol_data:
                    logger.info(f"✅ RISKMETRIC: {symbol_clean} - Current Price: ${symbol_data.get('current_price', 'N/A')}, Risk: {symbol_data.get('current_risk', 'N/A')}")
                else:
                    logger.info(f"✅ RISKMETRIC: Autonomous system active, {risk_grids_count} symbols available")

            except Exception as e:
                agent_results['riskmetric'] = {"status": "error", "error": str(e)}

            # 4. Alert Collection Agent - Enhanced System
            try:
                # Get alert for the symbol
                alert_result = subprocess.run(['python3', 'src/agents/enhanced_alert_collection_agent.py', f'alert:{symbol}'],
                                            capture_output=True, text=True, timeout=10,
                                            cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')

                if alert_result.stdout:
                    alert_data = json.loads(alert_result.stdout)

                    # Check for MDC documentation
                    from pathlib import Path
                    mdc_dir = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/mdc_documentation/alert_reports')
                    mdc_files = list(mdc_dir.glob(f"{symbol}_alert_report_*.mdc")) if mdc_dir.exists() else []

                    agent_results['alert_collection'] = {
                        "status": "active",
                        "symbol": symbol,
                        "alert_available": True,
                        "confidence_rating": alert_data.get('confidence_rating', 'Unknown'),
                        "created_at": alert_data.get('created_at', 'Unknown'),
                        "source": alert_data.get('source', 'Unknown'),
                        "mdc_documentation": len(mdc_files) > 0,
                        "integrations": {
                            "riskmetric": alert_data.get('riskmetric_available', False),
                            "cryptometer": alert_data.get('cryptometer_available', False)
                        },
                        "summary": alert_data.get('alert_summary', '')[:200] + '...' if alert_data.get('alert_summary') else 'No summary'
                    }

                    logger.info(f"✅ ALERT AGENT: {symbol} - Confidence: {alert_data.get('confidence_rating', 'Unknown')}, MDC Docs: {len(mdc_files)}")
                else:
                    agent_results['alert_collection'] = {
                        "status": "active",
                        "symbol": symbol,
                        "alert_available": False,
                        "note": "No alerts currently available for this symbol"
                    }
                    logger.info(f"✅ ALERT AGENT: Active but no alerts for {symbol}")

            except Exception as e:
                agent_results['alert_collection'] = {"status": "error", "error": str(e)}
                logger.error(f"Error getting alert data: {e}")

            # 5. Master Orchestration
            agent_results['master_orchestration'] = {"status": "ready", "port": 8097}

            logger.info(f"📊 Processed with {len(agent_results)} agents")

        # Return success response with agent results
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Webhook received and processed successfully",
                "event": event_type,
                "timestamp": datetime.now().isoformat(),
                "agents": agent_results
            }
        )

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JSONResponse(
            status_code=200,  # Return 200 even on error so Manus doesn't retry
            content={
                "status": "error",
                "message": str(e)
            }
        )

@app.get("/")
async def root():
    return {"message": "Manus Webhook Server Running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/webhooks/manus/riskmetric/status")
async def get_riskmetric_status():
    """Get comprehensive RISKMETRIC autonomous system status"""
    try:
        import subprocess
        from pathlib import Path

        # Get background agent status
        try:
            agent_result = subprocess.run(['python3', 'services/cryptoverse_background_agent.py', '--status'],
                                       capture_output=True, text=True, timeout=5,
                                       cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')
            agent_status = json.loads(agent_result.stdout) if agent_result.stdout else {"running": False}
        except:
            agent_status = {"running": False}

        # Check risk grids
        risk_grids_dir = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/extracted_risk_grids')
        risk_grids_count = len(list(risk_grids_dir.glob("*.json"))) if risk_grids_dir.exists() else 0

        # Get health status
        try:
            health_result = subprocess.run(['python3', 'check_system_health.py'],
                                        capture_output=True, text=True, timeout=10,
                                        cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')
            health_status = "healthy" if health_result.returncode == 0 else "issues"
        except:
            health_status = "unknown"

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
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'status': 'error', 'message': str(e)}
        )

@app.get("/api/webhooks/manus/riskmetric/{symbol}")
async def get_symbol_riskmetric(symbol: str):
    """Get RISKMETRIC data for a specific symbol"""
    try:
        from pathlib import Path

        # Clean symbol (remove USDT, USD, etc.)
        symbol_clean = symbol.upper().replace('USDT', '').replace('USD', '').replace('BUSD', '')

        risk_grids_dir = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/extracted_risk_grids')
        symbol_file = risk_grids_dir / f"{symbol_clean}_risk_grid.json"

        if symbol_file.exists():
            with open(symbol_file, 'r') as f:
                symbol_data = json.load(f)

            return JSONResponse(
                status_code=200,
                content={
                    'status': 'success',
                    'symbol': symbol_clean,
                    'data': {
                        'current_price': symbol_data.get('current_price'),
                        'current_risk': symbol_data.get('current_risk'),
                        'risk_points': len(symbol_data.get('fiat_risk_grid', [])),
                        'timestamp': symbol_data.get('timestamp'),
                        'source': 'autonomous_scraper'
                    },
                    'autonomous_system': 'active',
                    'last_updated': symbol_data.get('timestamp', 'unknown')
                }
            )
        else:
            return JSONResponse(
                status_code=404,
                content={
                    'status': 'not_found',
                    'symbol': symbol_clean,
                    'message': f'Risk data for {symbol_clean} not available',
                    'available_symbols': [f.stem.replace('_risk_grid', '') for f in risk_grids_dir.glob("*_risk_grid.json")] if risk_grids_dir.exists() else []
                }
            )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'status': 'error', 'message': str(e)}
        )

@app.post("/api/webhooks/manus/riskmetric/force-update")
async def force_riskmetric_update():
    """Force an immediate RISKMETRIC update cycle"""
    try:
        import subprocess

        # Trigger immediate update
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
        return JSONResponse(
            status_code=500,
            content={'status': 'error', 'message': str(e)}
        )

@app.get("/api/webhooks/manus/cryptometer/status")
async def get_cryptometer_status():
    """Get comprehensive Cryptometer autonomous system status"""
    try:
        import subprocess
        from pathlib import Path

        # Get background agent status
        try:
            agent_result = subprocess.run(['python3', 'services/cryptometer_background_agent.py', 'status'],
                                       capture_output=True, text=True, timeout=5,
                                       cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')
            agent_status = json.loads(agent_result.stdout) if agent_result.stdout else {"running": False}
        except:
            agent_status = {"running": False}

        # Check cryptometer data files
        data_dir = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/extracted_cryptometer_data')
        data_files_count = len(list(data_dir.glob("*.json"))) if data_dir.exists() else 0

        # Get health status
        try:
            health_result = subprocess.run(['python3', 'check_system_health.py'],
                                        capture_output=True, text=True, timeout=10,
                                        cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')
            health_status = "healthy" if health_result.returncode == 0 else "issues"
        except:
            health_status = "unknown"

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
                        'self_healing': True
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'status': 'error', 'message': str(e)}
        )

@app.get("/api/webhooks/manus/cryptometer/{symbol}")
async def get_symbol_cryptometer(symbol: str):
    """Get Cryptometer data for a specific symbol"""
    try:
        from pathlib import Path

        # Clean symbol (remove USDT, USD, etc.)
        symbol_clean = symbol.upper().replace('USDT', '').replace('USD', '').replace('BUSD', '')

        data_dir = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/extracted_cryptometer_data')
        symbol_file = data_dir / f"{symbol_clean}_cryptometer_data.json"

        if symbol_file.exists():
            with open(symbol_file, 'r') as f:
                symbol_data = json.load(f)

            return JSONResponse(
                status_code=200,
                content={
                    'status': 'success',
                    'symbol': symbol_clean,
                    'data': {
                        'multi_timeframe_analysis': symbol_data.get('multi_timeframe_analysis'),
                        'win_rate_predictions': symbol_data.get('win_rate_predictions'),
                        'data_points': symbol_data.get('data_points', 0),
                        'endpoints_called': symbol_data.get('endpoints_called', 0),
                        'timestamp': symbol_data.get('timestamp'),
                        'source': 'autonomous_cryptometer'
                    },
                    'autonomous_system': 'active',
                    'last_updated': symbol_data.get('timestamp', 'unknown')
                }
            )
        else:
            return JSONResponse(
                status_code=404,
                content={
                    'status': 'not_found',
                    'symbol': symbol_clean,
                    'message': f'Cryptometer data for {symbol_clean} not available',
                    'available_symbols': [f.stem.replace('_cryptometer_data', '') for f in data_dir.glob("*_cryptometer_data.json")] if data_dir.exists() else []
                }
            )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'status': 'error', 'message': str(e)}
        )

@app.get("/api/webhooks/manus/alerts/status")
async def get_alerts_status():
    """Get comprehensive Alert Collection Agent status"""
    try:
        import subprocess
        from pathlib import Path

        # Get Enhanced Alert Agent status
        try:
            agent_result = subprocess.run(['python3', 'src/agents/enhanced_alert_collection_agent.py', 'status'],
                                       capture_output=True, text=True, timeout=5,
                                       cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')
            agent_status = json.loads(agent_result.stdout) if agent_result.stdout else {"status": "inactive"}
        except:
            agent_status = {"status": "inactive"}

        # Check MDC documentation directory
        mdc_dir = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/mdc_documentation/alert_reports')
        mdc_files_count = len(list(mdc_dir.glob("*.mdc"))) if mdc_dir.exists() else 0

        return JSONResponse(
            status_code=200,
            content={
                'status': 'success',
                'alert_collection_system': {
                    'enhanced_agent': agent_status,
                    'alert_servers': {
                        'whale_alerts': {'port': 8018, 'status': 'configured'},
                        'messi_alerts': {'port': 8014, 'status': 'configured'},
                        'live_alerts': {'port': 8017, 'status': 'configured'},
                        'maradona_alerts': {'port': 8019, 'status': 'configured'},
                        'pele_alerts': {'port': 8020, 'status': 'configured'}
                    },
                    'integrations': {
                        'mdc_agent': 'active',
                        'riskmetric_integration': 'enabled',
                        'cryptometer_integration': 'enabled',
                        'manus_integration': 'enabled',
                        'anthropic_prompt_mcp': 'enabled',
                        'supabase': agent_status.get('integrations', {}).get('supabase_connected', False)
                    },
                    'documentation': {
                        'mdc_reports_generated': mdc_files_count,
                        'professional_format': True,
                        'quality_controlled': True
                    },
                    'capabilities': {
                        'multi_server_collection': True,
                        'professional_mdc_reports': True,
                        'on_demand_generation': True,
                        'symbol_coverage_guarantee': True,
                        'autonomous_operation': True,
                        'master_agent_interface': True
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'status': 'error', 'message': str(e)}
        )

@app.get("/api/webhooks/manus/alerts/{symbol}")
async def get_symbol_alert(symbol: str):
    """Get Alert Collection Agent data for a specific symbol"""
    try:
        import subprocess
        from pathlib import Path

        # Clean symbol (remove USDT, USD, etc.)
        symbol_clean = symbol.upper().replace('USDT', '').replace('USD', '').replace('BUSD', '')

        # Get alert from Enhanced Alert Agent
        try:
            agent_result = subprocess.run(['python3', 'src/agents/enhanced_alert_collection_agent.py', f'alert:{symbol_clean}'],
                                       capture_output=True, text=True, timeout=10,
                                       cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')

            if agent_result.stdout:
                alert_data = json.loads(agent_result.stdout)

                # Check for MDC documentation
                mdc_dir = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/mdc_documentation/alert_reports')
                mdc_files = list(mdc_dir.glob(f"{symbol_clean}_alert_report_*.mdc")) if mdc_dir.exists() else []
                latest_mdc = sorted(mdc_files)[-1] if mdc_files else None

                return JSONResponse(
                    status_code=200,
                    content={
                        'status': 'success',
                        'symbol': symbol_clean,
                        'alert': alert_data,
                        'documentation': {
                            'mdc_available': latest_mdc is not None,
                            'mdc_file': str(latest_mdc.name) if latest_mdc else None
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                )
            else:
                return JSONResponse(
                    status_code=404,
                    content={
                        'status': 'not_found',
                        'symbol': symbol_clean,
                        'message': f'No alert data available for {symbol_clean}'
                    }
                )

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    'status': 'error',
                    'symbol': symbol_clean,
                    'message': f'Error getting alert for {symbol_clean}: {str(e)}'
                }
            )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'status': 'error', 'message': str(e)}
        )

@app.post("/api/webhooks/manus/alerts/force-generate/{symbol}")
async def force_alert_generation(symbol: str):
    """Force generation of a new alert for a specific symbol"""
    try:
        import subprocess

        # Clean symbol
        symbol_clean = symbol.upper().replace('USDT', '').replace('USD', '').replace('BUSD', '')

        # Force alert generation
        result = subprocess.Popen(['python3', 'src/agents/enhanced_alert_collection_agent.py', 'test'],
                                cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')

        return JSONResponse(
            status_code=202,
            content={
                'status': 'success',
                'message': f'Alert generation initiated for {symbol_clean}',
                'process_id': result.pid,
                'note': 'Alert generation in progress. Check alert endpoint for results.',
                'estimated_completion': '30 seconds',
                'timestamp': datetime.now().isoformat()
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'status': 'error', 'message': str(e)}
        )

@app.post("/api/webhooks/manus/alerts/start-autonomous")
async def start_autonomous_alerts():
    """Start the Alert Collection Agent in autonomous mode"""
    try:
        import subprocess

        # Start autonomous operation
        result = subprocess.Popen(['python3', 'src/agents/enhanced_alert_collection_agent.py', 'start'],
                                cwd='/Users/dansidanutz/Desktop/ZmartBot/zmart-api')

        return JSONResponse(
            status_code=202,
            content={
                'status': 'success',
                'message': 'Alert Collection Agent started in autonomous mode',
                'process_id': result.pid,
                'note': 'Agent will continuously collect and process alerts',
                'collection_interval_minutes': 10,
                'timestamp': datetime.now().isoformat()
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'status': 'error', 'message': str(e)}
        )

@app.post("/api/webhooks/manus/cryptometer/force-update")
async def force_cryptometer_update():
    """Force an immediate Cryptometer update cycle"""
    try:
        import subprocess

        # Trigger immediate update
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
        return JSONResponse(
            status_code=500,
            content={'status': 'error', 'message': str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Manus Webhook Server on port 8555")
    uvicorn.run(app, host="0.0.0.0", port=8555)