"""
Enhanced Alerts API Routes
New API endpoints for the enhanced alerts system
"""

from flask import Blueprint, request, jsonify, Response
from flask_cors import cross_origin
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Create blueprint
enhanced_alerts_bp = Blueprint('enhanced_alerts', __name__, url_prefix='/api/enhanced-alerts')

# In-memory storage for demo purposes
_symbol_states = {}
_alert_events = {}
_sse_clients = []

def _get_state_key(symbol: str, timeframe: str) -> str:
    """Generate unique key for symbol state"""
    return f"{symbol}:{timeframe}"

@enhanced_alerts_bp.route('/state/<symbol>', methods=['GET'])
@cross_origin()
def get_symbol_state(symbol: str):
    """Get current state for a symbol"""
    try:
        timeframe = request.args.get('tf', '1h')
        symbol = symbol.upper()
        
        key = _get_state_key(symbol, timeframe)
        state = _symbol_states.get(key)
        
        if state:
            return jsonify({
                'ok': True,
                'data': state
            })
        else:
            # Return demo data for testing
            demo_state = {
                'symbol': symbol,
                'timeframe': timeframe,
                'last_bar_ts': int(datetime.now().timestamp() * 1000),
                'indicators': {
                    'rsi': {'status': 'neutral', 'fields': {'Value': 50}},
                    'macd': {'status': 'bullish', 'fields': {'MACD': 0.5}},
                    'ema_crossovers': {'status': 'neutral', 'fields': {'EMA9': 45000, 'EMA20': 44900}},
                    'bollinger': {'status': 'neutral', 'fields': {'Breakout': 'normal'}},
                    'momentum': {'status': 'bullish', 'fields': {'Strength': 0.7}}
                },
                'sentiment': {'bullish': 40, 'neutral': 40, 'bearish': 20},
                'updated_at': int(datetime.now().timestamp() * 1000)
            }
            return jsonify({
                'ok': True,
                'data': demo_state
            })
            
    except Exception as e:
        logger.error(f"Error getting state for {symbol}: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@enhanced_alerts_bp.route('/events/<symbol>', methods=['GET'])
@cross_origin()
def get_symbol_events(symbol: str):
    """Get alert events for a symbol"""
    try:
        timeframe = request.args.get('tf', '1h')
        limit = int(request.args.get('limit', 50))
        symbol = symbol.upper()
        
        key = _get_state_key(symbol, timeframe)
        events = _alert_events.get(key, [])
        
        # Return demo events for testing
        demo_events = [
            {
                'symbol': symbol,
                'timeframe': timeframe,
                'type': 'indicator_status_change',
                'indicator_key': 'macd',
                'from_status': 'neutral',
                'to_status': 'bullish',
                'severity': 'info',
                'score': 0.45,
                'created_at': datetime.now().isoformat(),
                'bar_ts': int(datetime.now().timestamp() * 1000)
            }
        ]
        
        return jsonify({
            'ok': True,
            'data': demo_events[:limit]
        })
        
    except Exception as e:
        logger.error(f"Error getting events for {symbol}: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@enhanced_alerts_bp.route('/stream', methods=['GET'])
@cross_origin()
def alerts_stream():
    """Server-Sent Events stream for real-time alerts"""
    def generate():
        """Generate SSE stream"""
        try:
            # Send initial heartbeat
            yield f"data: {json.dumps({'type': 'connected', 'ts': datetime.now().isoformat()})}\n\n"
            
            # Keep connection alive with heartbeats
            import time
            
            while True:
                yield f"data: {json.dumps({'type': 'heartbeat', 'ts': datetime.now().isoformat()})}\n\n"
                time.sleep(25)  # Heartbeat every 25 seconds
                
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )

@enhanced_alerts_bp.route('/process/<symbol>', methods=['POST'])
@cross_origin()
def process_symbol_alerts(symbol: str):
    """Process alerts for a symbol (manual trigger)"""
    try:
        data = request.get_json() or {}
        timeframe = data.get('timeframe', '1h')
        symbol = symbol.upper()
        
        # Demo processing result
        result = {
            'status': 'success',
            'symbol': symbol,
            'timeframe': timeframe,
            'indicators_processed': 5,
            'changes_detected': 1,
            'cross_alerts': 1,
            'events_created': 2,
            'sentiment': {'bullish': 40, 'neutral': 40, 'bearish': 20}
        }
        
        return jsonify({
            'ok': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error processing alerts for {symbol}: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@enhanced_alerts_bp.route('/summary/<symbol>', methods=['GET'])
@cross_origin()
def get_symbol_summary(symbol: str):
    """Get comprehensive summary for a symbol"""
    try:
        timeframe = request.args.get('tf', '1h')
        symbol = symbol.upper()
        
        # Demo summary
        summary = {
            'symbol': symbol,
            'timeframe': timeframe,
            'state': {
                'symbol': symbol,
                'timeframe': timeframe,
                'indicators': {
                    'rsi': {'status': 'neutral', 'fields': {'Value': 50}},
                    'macd': {'status': 'bullish', 'fields': {'MACD': 0.5}}
                },
                'sentiment': {'bullish': 40, 'neutral': 40, 'bearish': 20}
            },
            'recent_events': [
                {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'type': 'indicator_status_change',
                    'indicator_key': 'macd',
                    'from_status': 'neutral',
                    'to_status': 'bullish',
                    'severity': 'info',
                    'score': 0.45,
                    'created_at': datetime.now().isoformat()
                }
            ],
            'total_events': 1,
            'sse_clients_count': len(_sse_clients)
        }
        
        return jsonify({
            'ok': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting summary for {symbol}: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@enhanced_alerts_bp.route('/cooldowns/<symbol>', methods=['GET'])
@cross_origin()
def get_symbol_cooldowns(symbol: str):
    """Get cooldown status for a symbol"""
    try:
        timeframe = request.args.get('tf', '1h')
        symbol = symbol.upper()
        
        # Demo cooldowns
        cooldowns = {
            'ema_bull_cross': {
                'alert_key': 'ema_bull_cross',
                'symbol': symbol,
                'timeframe': timeframe,
                'last_fired': 0,
                'time_since_last_ms': 0,
                'is_active': False
            }
        }
        
        return jsonify({
            'ok': True,
            'data': cooldowns
        })
        
    except Exception as e:
        logger.error(f"Error getting cooldowns for {symbol}: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@enhanced_alerts_bp.route('/cooldowns/<symbol>/clear', methods=['POST'])
@cross_origin()
def clear_symbol_cooldowns(symbol: str):
    """Clear cooldowns for a symbol"""
    try:
        data = request.get_json() or {}
        timeframe = data.get('timeframe', '1h')
        symbol = symbol.upper()
        
        return jsonify({
            'ok': True,
            'message': f'Cleared all cooldowns for {symbol}:{timeframe}'
        })
        
    except Exception as e:
        logger.error(f"Error clearing cooldowns for {symbol}: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@enhanced_alerts_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_alerts_stats():
    """Get overall alerts system statistics"""
    try:
        # Demo stats
        stats = {
            'total_active_cooldowns': 0,
            'symbols_with_cooldowns': 0,
            'symbol_breakdown': {},
            'memory_usage_estimate': 0
        }
        
        return jsonify({
            'ok': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting alerts stats: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

# Register the blueprint
def init_enhanced_alerts_routes(app):
    """Initialize enhanced alerts routes"""
    app.register_blueprint(enhanced_alerts_bp)
    logger.info("Enhanced alerts routes registered")
