"""
Symbol Management API Routes
Comprehensive REST API endpoints for the ZmartBot Symbol Management Module
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import logging

from src.core.symbol_manager import SymbolManager
from src.core.portfolio_manager import PortfolioManager
from src.core.scoring_engine import ScoringEngine
from src.core.signal_processor import SignalProcessor
from src.models.symbol_models import Symbol, PortfolioComposition, SymbolScore, Signal

logger = logging.getLogger(__name__)

# Create blueprint
symbol_bp = Blueprint('symbol', __name__)

# Initialize managers
symbol_manager = SymbolManager()
portfolio_manager = PortfolioManager()
scoring_engine = ScoringEngine()
signal_processor = SignalProcessor()

# =====================================================
# PORTFOLIO MANAGEMENT ENDPOINTS
# =====================================================

@symbol_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Get current portfolio composition"""
    try:
        portfolio = symbol_manager.get_current_portfolio()
        return jsonify({
            'success': True,
            'portfolio': portfolio,
            'count': len(portfolio)
        })
    except Exception as e:
        logger.error(f"Error in get_portfolio: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/portfolio/statistics', methods=['GET'])
def get_portfolio_statistics():
    """Get comprehensive portfolio statistics"""
    try:
        stats = symbol_manager.get_portfolio_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error in get_portfolio_statistics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/portfolio/metrics', methods=['GET'])
def get_portfolio_metrics():
    """Get detailed portfolio metrics and analytics"""
    try:
        metrics = portfolio_manager.calculate_portfolio_metrics()
        return jsonify({
            'success': True,
            'metrics': metrics
        })
    except Exception as e:
        logger.error(f"Error in get_portfolio_metrics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/portfolio/performance-attribution', methods=['GET'])
def get_performance_attribution():
    """Get portfolio performance attribution analysis"""
    try:
        days = request.args.get('days', 30, type=int)
        attribution = portfolio_manager.get_portfolio_performance_attribution(days)
        return jsonify({
            'success': True,
            'attribution': attribution
        })
    except Exception as e:
        logger.error(f"Error in get_performance_attribution: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/portfolio/optimize-weights', methods=['POST'])
def optimize_portfolio_weights():
    """Optimize portfolio weights"""
    try:
        optimization = portfolio_manager.optimize_portfolio_weights()
        return jsonify({
            'success': True,
            'optimization': optimization
        })
    except Exception as e:
        logger.error(f"Error in optimize_portfolio_weights: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/portfolio/rebalance', methods=['POST'])
def rebalance_portfolio():
    """Rebalance portfolio based on optimized weights"""
    try:
        rebalance_result = portfolio_manager.rebalance_portfolio()
        return jsonify({
            'success': True,
            'rebalance_result': rebalance_result
        })
    except Exception as e:
        logger.error(f"Error in rebalance_portfolio: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/portfolio/replacement-candidates', methods=['GET'])
def get_replacement_candidates():
    """Get symbols that are candidates for replacement"""
    try:
        candidates = symbol_manager.get_replacement_candidates()
        return jsonify({
            'success': True,
            'candidates': candidates,
            'count': len(candidates)
        })
    except Exception as e:
        logger.error(f"Error in get_replacement_candidates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/portfolio/history', methods=['GET'])
def get_portfolio_history():
    """Get portfolio change history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = symbol_manager.get_portfolio_history(limit)
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })
    except Exception as e:
        logger.error(f"Error in get_portfolio_history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# SYMBOL MANAGEMENT ENDPOINTS
# =====================================================

@symbol_bp.route('/symbols', methods=['GET'])
def get_symbols():
    """Get eligible symbols for management"""
    try:
        limit = request.args.get('limit', 50, type=int)
        symbols = symbol_manager.get_eligible_symbols(limit)
        return jsonify({
            'success': True,
            'symbols': symbols,
            'count': len(symbols)
        })
    except Exception as e:
        logger.error(f"Error in get_symbols: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/symbols/<symbol_id>', methods=['GET'])
def get_symbol_details(symbol_id):
    """Get detailed information about a specific symbol"""
    try:
        symbol = Symbol.query.filter_by(id=symbol_id).first()
        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol not found'}), 404
        
        # Get latest scores
        latest_scores = SymbolScore.query.filter_by(symbol_id=symbol.id).order_by(
            SymbolScore.calculation_timestamp.desc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'symbol': symbol.to_dict(),
            'latest_scores': [score.to_dict() for score in latest_scores]
        })
    except Exception as e:
        logger.error(f"Error in get_symbol_details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/portfolio/add-symbol', methods=['POST'])
def add_symbol_to_portfolio():
    """Add a symbol to the portfolio"""
    try:
        data = request.get_json()
        if not data or 'symbol_id' not in data:
            return jsonify({'success': False, 'error': 'symbol_id is required'}), 400
        
        result = symbol_manager.add_symbol_to_portfolio(
            symbol_id=data['symbol_id'],
            reason=data.get('reason', 'Manual addition'),
            user=data.get('user', 'api_user')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in add_symbol_to_portfolio: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/portfolio/remove-symbol', methods=['POST'])
def remove_symbol_from_portfolio():
    """Remove a symbol from the portfolio"""
    try:
        data = request.get_json()
        if not data or 'symbol_id' not in data:
            return jsonify({'success': False, 'error': 'symbol_id is required'}), 400
        
        result = symbol_manager.remove_symbol_from_portfolio(
            symbol_id=data['symbol_id'],
            reason=data.get('reason', 'Manual removal'),
            user=data.get('user', 'api_user')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in remove_symbol_from_portfolio: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/portfolio/replace-symbol', methods=['POST'])
def replace_symbol():
    """Replace one symbol with another in the portfolio"""
    try:
        data = request.get_json()
        if not data or 'old_symbol_id' not in data or 'new_symbol_id' not in data:
            return jsonify({
                'success': False, 
                'error': 'old_symbol_id and new_symbol_id are required'
            }), 400
        
        result = symbol_manager.replace_symbol(
            old_symbol_id=data['old_symbol_id'],
            new_symbol_id=data['new_symbol_id'],
            reason=data.get('reason', 'Manual replacement'),
            user=data.get('user', 'api_user')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in replace_symbol: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# SCORING SYSTEM ENDPOINTS
# =====================================================

@symbol_bp.route('/scoring/calculate', methods=['POST'])
def calculate_scores():
    """Calculate scores for all symbols or a specific symbol"""
    try:
        data = request.get_json() or {}
        symbol_id = data.get('symbol_id')
        
        result = scoring_engine.calculate_all_scores(symbol_id)
        return jsonify({
            'success': True,
            'calculation_result': result
        })
    except Exception as e:
        logger.error(f"Error in calculate_scores: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/scoring/rankings', methods=['GET'])
def get_symbol_rankings():
    """Get symbol rankings based on scores"""
    try:
        algorithm_type = request.args.get('algorithm_type', 'COMPOSITE')
        limit = request.args.get('limit', 50, type=int)
        
        rankings = scoring_engine.get_symbol_rankings(algorithm_type, limit)
        return jsonify({
            'success': True,
            'rankings': rankings,
            'algorithm_type': algorithm_type,
            'count': len(rankings)
        })
    except Exception as e:
        logger.error(f"Error in get_symbol_rankings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/scoring/symbol/<symbol_id>/scores', methods=['GET'])
def get_symbol_scores(symbol_id):
    """Get all scores for a specific symbol"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        scores = SymbolScore.query.filter_by(symbol_id=symbol_id).order_by(
            SymbolScore.calculation_timestamp.desc()
        ).limit(limit).all()
        
        return jsonify({
            'success': True,
            'symbol_id': symbol_id,
            'scores': [score.to_dict() for score in scores],
            'count': len(scores)
        })
    except Exception as e:
        logger.error(f"Error in get_symbol_scores: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# SIGNAL PROCESSING ENDPOINTS
# =====================================================

@symbol_bp.route('/signals', methods=['POST'])
def submit_signal():
    """Submit a new trading signal for processing"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body is required'}), 400
        
        result = signal_processor.process_signal(data)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in submit_signal: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/signals/pending', methods=['GET'])
def get_pending_signals():
    """Get pending signals awaiting processing"""
    try:
        limit = request.args.get('limit', 50, type=int)
        signals = signal_processor.get_pending_signals(limit)
        return jsonify({
            'success': True,
            'signals': signals,
            'count': len(signals)
        })
    except Exception as e:
        logger.error(f"Error in get_pending_signals: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/signals/processed', methods=['GET'])
def get_processed_signals():
    """Get recently processed signals"""
    try:
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        signals = signal_processor.get_processed_signals(hours, limit)
        return jsonify({
            'success': True,
            'signals': signals,
            'count': len(signals),
            'hours': hours
        })
    except Exception as e:
        logger.error(f"Error in get_processed_signals: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/signals/statistics', methods=['GET'])
def get_signal_statistics():
    """Get signal processing statistics"""
    try:
        days = request.args.get('days', 7, type=int)
        stats = signal_processor.get_signal_statistics(days)
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error in get_signal_statistics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/signals/cleanup', methods=['POST'])
def cleanup_signals():
    """Clean up expired signals"""
    try:
        result = signal_processor.cleanup_expired_signals()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in cleanup_signals: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@symbol_bp.route('/signals/reprocess-failed', methods=['POST'])
def reprocess_failed_signals():
    """Reprocess failed signals"""
    try:
        data = request.get_json() or {}
        max_retries = data.get('max_retries', 3)
        
        result = signal_processor.reprocess_failed_signals(max_retries)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in reprocess_failed_signals: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# SYSTEM STATUS AND HEALTH ENDPOINTS
# =====================================================

@symbol_bp.route('/health', methods=['GET'])
def health_check():
    """System health check"""
    try:
        # Check database connectivity
        portfolio_count = PortfolioComposition.query.filter_by(status='Active').count()
        symbol_count = Symbol.query.filter_by(is_eligible_for_management=True).count()
        
        # Check recent activity
        recent_scores = SymbolScore.query.filter(
            SymbolScore.calculation_timestamp >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
        ).count()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'system_info': {
                'active_portfolio_symbols': portfolio_count,
                'eligible_symbols': symbol_count,
                'scores_calculated_today': recent_scores
            }
        })
    except Exception as e:
        logger.error(f"Error in health_check: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@symbol_bp.route('/status', methods=['GET'])
def get_system_status():
    """Get comprehensive system status"""
    try:
        # Portfolio status
        portfolio_stats = symbol_manager.get_portfolio_statistics()
        
        # Signal processing status
        signal_stats = signal_processor.get_signal_statistics(1)  # Last 24 hours
        
        # Scoring status
        recent_scores = SymbolScore.query.filter(
            SymbolScore.calculation_timestamp >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
        ).count()
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'portfolio_status': portfolio_stats,
            'signal_processing_status': signal_stats,
            'scoring_status': {
                'scores_calculated_today': recent_scores
            }
        })
    except Exception as e:
        logger.error(f"Error in get_system_status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================================================
# UTILITY ENDPOINTS
# =====================================================

@symbol_bp.route('/initialize-sample-data', methods=['POST'])
def initialize_sample_data():
    """Initialize sample data for testing (development only)"""
    try:
        from src.utils.sample_data import initialize_sample_data as init_data
        result = init_data()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in initialize_sample_data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers
@symbol_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@symbol_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'success': False, 'error': 'Method not allowed'}), 405

@symbol_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

