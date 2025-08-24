from flask import Blueprint, jsonify, request
import sys
import os

# Add the parent directory to the path to import update_logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from update_logger import get_recent_updates, get_update_summary

update_logs_bp = Blueprint('update_logs', __name__)

@update_logs_bp.route('/api/v1/update-logs/<symbol>', methods=['GET'])
def get_symbol_update_logs(symbol):
    """Get recent update logs for a specific symbol"""
    try:
        limit = request.args.get('limit', 10, type=int)
        updates = get_recent_updates(symbol, limit)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'updates': updates,
            'count': len(updates)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@update_logs_bp.route('/api/v1/update-logs/summary/<symbol>', methods=['GET'])
def get_symbol_update_summary(symbol):
    """Get update summary for a specific symbol"""
    try:
        summary = get_update_summary(symbol)
        
        if summary:
            return jsonify({
                'success': True,
                'summary': summary
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No updates found for symbol'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@update_logs_bp.route('/api/v1/update-logs/recent', methods=['GET'])
def get_recent_all_updates():
    """Get recent update logs for all symbols"""
    try:
        limit = request.args.get('limit', 20, type=int)
        updates = get_recent_updates(None, limit)
        
        return jsonify({
            'success': True,
            'updates': updates,
            'count': len(updates)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
