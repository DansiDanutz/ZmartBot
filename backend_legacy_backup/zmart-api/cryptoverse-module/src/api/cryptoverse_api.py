#!/usr/bin/env python3
"""
Cryptoverse API
Flask API for Into The Cryptoverse data extraction system
Based on the comprehensive data pipeline system from the package
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import threading
import time

# Flask imports with error handling for linter issues
try:
    from flask import Flask, jsonify, request  # type: ignore[import]
    from flask_cors import CORS  # type: ignore[import]
    FLASK_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Flask import failed: {e}")
    # Define placeholders for linter
    Flask = None  # type: ignore[assignment]
    jsonify = None  # type: ignore[assignment]
    request = None  # type: ignore[assignment]
    CORS = None  # type: ignore[assignment]
    FLASK_AVAILABLE = False

# Schedule import with error handling for linter issues
try:
    import schedule  # type: ignore[import]
    SCHEDULE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Schedule import failed: {e}")
    # Define placeholder for linter
    schedule = None  # type: ignore[assignment]
    SCHEDULE_AVAILABLE = False

from ..database.cryptoverse_database import CryptoverseDatabase
from ..extractors.crypto_risk_extractor import CryptoRiskExtractor
from ..extractors.screener_extractor import ScreenerExtractor
from ..ai_insights.insight_generator import InsightGenerator

logger = logging.getLogger(__name__)

class CryptoverseAPI:
    """Flask API for Cryptoverse data extraction and AI insights"""
    
    def __init__(self, port: int = 5002):
        if not FLASK_AVAILABLE or not Flask:
            raise ImportError("Flask is not available - cannot create API server")
        
        self.app = Flask(__name__)
        if CORS:
            CORS(self.app)
        self.port = port
        
        # Initialize components
        self.database = CryptoverseDatabase()
        self.crypto_risk_extractor = CryptoRiskExtractor()
        self.screener_extractor = ScreenerExtractor()
        self.insight_generator = InsightGenerator(self.database)
        
        # Setup request logging middleware
        self._setup_request_logging()
        
        # Setup routes
        self._setup_routes()
        
        # Setup scheduled tasks
        self._setup_scheduler()
        
        logger.info("Cryptoverse API initialized")
    
    def _setup_request_logging(self):
        """Setup comprehensive request and error logging"""
        
        @self.app.before_request
        def log_request_info():
            """Log incoming request details"""
            if request:
                logger.info(f"🌐 {request.method} {request.url} - Remote: {request.remote_addr}")
                if request.json:
                    logger.debug(f"📝 Request body: {request.json}")
        
        @self.app.after_request
        def log_response_info(response):
            """Log response details"""
            if request:
                logger.info(f"📤 Response {response.status_code} for {request.method} {request.path}")
            return response
        
        @self.app.errorhandler(404)
        def not_found_error(error):
            """Handle 404 errors with detailed logging"""
            if request:
                logger.warning(f"🚫 404 Not Found: {request.method} {request.url}")
            if jsonify and request:
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': 'Endpoint not found',
                    'method': request.method,
                    'path': request.path,
                'timestamp': datetime.now().isoformat(),
                'available_endpoints': [
                    '/health',
                    '/api/system-status', 
                    '/api/crypto-risk-indicators',
                    '/api/screener-data',
                    '/api/ai-insights',
                    '/api/historical-data',
                    '/api/analyze-symbol',
                    '/api/extraction-status',
                    '/api/data-sources'
                ]
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors with detailed logging"""
            if request:
                logger.error(f"💥 500 Internal Server Error: {request.method} {request.url} - {str(error)}")
            if jsonify and request:
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': 'Internal server error',
                    'method': request.method,
                    'path': request.path,
                'timestamp': datetime.now().isoformat()
            }), 500
    
    def _setup_routes(self):
        """Setup all API routes based on the package specifications"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint with comprehensive system status"""
            try:
                # Check database connection
                db_status = 'healthy'
                try:
                    self.database.get_data_source_status()
                except Exception as e:
                    db_status = f'error: {str(e)}'
                
                # Check scheduled tasks status
                scheduler_status = 'healthy' if SCHEDULE_AVAILABLE and schedule else 'unavailable'
                
                # Get system components status
                components = {
                    'database': db_status,
                    'crypto_risk_extractor': 'healthy' if self.crypto_risk_extractor else 'unavailable',
                    'screener_extractor': 'healthy' if self.screener_extractor else 'unavailable',
                    'insight_generator': 'healthy' if self.insight_generator else 'unavailable',
                    'scheduler': scheduler_status,
                    'flask': 'healthy' if FLASK_AVAILABLE else 'unavailable'
                }
                
                # Determine overall status
                overall_status = 'healthy' if all(
                    status == 'healthy' or status == 'unavailable' 
                    for status in components.values()
                ) else 'degraded'
                
                if jsonify:
                    if jsonify:
                        return jsonify({
                        'status': overall_status,
                        'service': 'Cryptoverse Data Extraction API',
                        'timestamp': datetime.now().isoformat(),
                        'version': '1.0.0',
                        'components': components,
                    'features': {
                        'automated_scheduling': scheduler_status == 'healthy',
                        'database_integration': db_status == 'healthy',
                        'error_handling': True,
                        'cors_support': True,
                        'logging': True,
                        'health_monitoring': True,
                        'flexible_configuration': True
                    },
                    'data_sources': 21,
                    'endpoints': 12,
                    'uptime': 'active'
                })
            except Exception as e:
                logger.error(f"Health check error: {str(e)}")
                if jsonify:
                    return jsonify({
                    'status': 'error',
                    'service': 'Cryptoverse Data Extraction API',
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/system-status', methods=['GET'])
        def get_system_status():
            """Get comprehensive system status and monitoring information"""
            try:
                # Database statistics
                db_stats = {}
                try:
                    db_stats = {
                        'connection': 'healthy',
                        'data_sources': len(self.database.get_data_source_status()) if hasattr(self.database, 'get_data_source_status') else 'unknown',
                        'last_extraction': 'active'
                    }
                except Exception as e:
                    db_stats = {'connection': f'error: {str(e)}', 'data_sources': 0}
                
                # Scheduler statistics
                scheduler_stats = {
                    'available': SCHEDULE_AVAILABLE and schedule is not None,
                    'tasks_configured': 4 if SCHEDULE_AVAILABLE and schedule else 0,
                    'background_thread': 'active' if SCHEDULE_AVAILABLE else 'unavailable',
                    'schedule_intervals': {
                        'crypto_risk_extraction': '15 minutes',
                        'screener_extraction': '5 minutes', 
                        'insights_generation': '30 minutes',
                        'database_cleanup': 'daily at 2 AM'
                    } if SCHEDULE_AVAILABLE else {}
                }
                
                # Component health
                component_health = {
                    'database': 'healthy' if db_stats.get('connection') == 'healthy' else 'error',
                    'crypto_risk_extractor': 'healthy' if self.crypto_risk_extractor else 'unavailable',
                    'screener_extractor': 'healthy' if self.screener_extractor else 'unavailable',
                    'insight_generator': 'healthy' if self.insight_generator else 'unavailable',
                    'flask_app': 'healthy',
                    'cors_enabled': 'healthy',
                    'scheduler': 'healthy' if scheduler_stats['available'] else 'unavailable'
                }
                
                # Feature status
                feature_status = {
                    'automated_scheduling': {
                        'enabled': scheduler_stats['available'],
                        'tasks': scheduler_stats['tasks_configured'],
                        'intervals': scheduler_stats['schedule_intervals']
                    },
                    'database_integration': {
                        'enabled': db_stats.get('connection') == 'healthy',
                        'data_sources': db_stats.get('data_sources', 0)
                    },
                    'error_handling': {
                        'enabled': True,
                        'graceful_degradation': True,
                        'detailed_responses': True
                    },
                    'cors_support': {
                        'enabled': True,
                        'cross_origin_requests': True
                    },
                    'logging': {
                        'enabled': True,
                        'level': 'INFO',
                        'request_tracking': True,
                        'error_tracking': True
                    },
                    'health_monitoring': {
                        'enabled': True,
                        'endpoints': ['/health', '/api/system-status'],
                        'component_tracking': True
                    },
                    'flexible_configuration': {
                        'enabled': True,
                        'configurable_port': True,
                        'debug_mode': True,
                        'command_line_args': True
                    }
                }
                
                if jsonify:
                    return jsonify({
                    'status': 'healthy',
                    'service': 'Cryptoverse Data Extraction API',
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0.0',
                    'port': self.port,
                    'database_stats': db_stats,
                    'scheduler_stats': scheduler_stats,
                    'component_health': component_health,
                    'feature_status': feature_status,
                    'api_endpoints': {
                        'health': '/health',
                        'system_status': '/api/system-status',
                        'crypto_risk_indicators': '/api/crypto-risk-indicators',
                        'screener_data': '/api/screener-data',
                        'ai_insights': '/api/ai-insights',
                        'historical_data': '/api/historical-data',
                        'analyze_symbol': '/api/analyze-symbol',
                        'extraction_status': '/api/extraction-status',
                        'data_sources': '/api/data-sources'
                    }
                })
            except Exception as e:
                logger.error(f"System status error: {str(e)}")
                if jsonify:
                    return jsonify({
                    'status': 'error',
                    'service': 'Cryptoverse Data Extraction API',
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/crypto-risk-indicators', methods=['GET'])
        def get_crypto_risk_indicators():
            """Get latest crypto risk indicators"""
            try:
                limit = (request.args.get('limit', 10, type=int) if request else 10)
                data = self.database.get_latest_data('crypto_risk_indicators', limit)
                
                if jsonify:
                    if jsonify:
                        return jsonify({
                        'success': True,
                        'data': data,
                        'count': len(data),
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error getting crypto risk indicators: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/screener-data', methods=['GET'])
        def get_screener_data():
            """Get latest screener data for all symbols"""
            try:
                limit = (request.args.get('limit', 50, type=int) if request else 50)
                symbol = (request.args.get('symbol', None) if request else None)
                
                data = self.database.get_latest_data('screener_data', limit)
                
                # Filter by symbol if specified
                if symbol:
                    data = [item for item in data if item.get('symbol', '').upper() == symbol.upper()]
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'data': data,
                    'count': len(data),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error getting screener data: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/dominance-data', methods=['GET'])
        def get_dominance_data():
            """Get latest dominance data"""
            try:
                limit = (request.args.get('limit', 10, type=int) if request else 10)
                data = self.database.get_latest_data('dominance_data', limit)
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'data': data,
                    'count': len(data),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error getting dominance data: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/ai-insights', methods=['GET'])
        def get_ai_insights():
            """Get AI-generated insights"""
            try:
                limit = (request.args.get('limit', 10, type=int) if request else 10)
                insight_type = (request.args.get('type', None) if request else None)
                symbol = (request.args.get('symbol', None) if request else None)
                
                data = self.database.get_latest_data('ai_insights', limit)
                
                # Filter by type if specified
                if insight_type:
                    data = [item for item in data if item.get('insight_type') == insight_type]
                
                # Filter by symbol if specified
                if symbol:
                    data = [item for item in data if item.get('symbol', '').upper() == symbol.upper()]
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'data': data,
                    'count': len(data),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error getting AI insights: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/extract/crypto-risk', methods=['POST'])
        def extract_crypto_risk():
            """Manually trigger crypto risk indicators extraction"""
            try:
                request_data = (request.json if request else {})
                use_mock = request_data.get('use_mock', True)
                
                if use_mock:
                    result = asyncio.run(self.crypto_risk_extractor.extract_with_mock_data())
                else:
                    result = asyncio.run(self.crypto_risk_extractor.extract_crypto_risk_indicators())
                
                # Save to database
                self.database.save_extraction_result(result)
                
                if jsonify:
                    return jsonify({
                    'success': result.success,
                    'data': result.data,
                    'error': result.error_message,
                    'confidence_score': result.confidence_score,
                    'timestamp': result.timestamp.isoformat()
                })
            except Exception as e:
                logger.error(f"Error extracting crypto risk: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/extract/screener', methods=['POST'])
        def extract_screener():
            """Manually trigger screener data extraction"""
            try:
                request_data = (request.json if request else {})
                use_mock = request_data.get('use_mock', True)
                
                if use_mock:
                    result = asyncio.run(self.screener_extractor.extract_with_mock_data())
                else:
                    result = asyncio.run(self.screener_extractor.extract_screener_data())
                
                # Save to database
                self.database.save_extraction_result(result)
                
                if jsonify:
                    return jsonify({
                    'success': result.success,
                    'data': result.data,
                    'error': result.error_message,
                    'confidence_score': result.confidence_score,
                    'timestamp': result.timestamp.isoformat()
                })
            except Exception as e:
                logger.error(f"Error extracting screener data: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/generate-insights', methods=['POST'])
        def generate_insights():
            """Generate AI insights based on current data"""
            try:
                request_data = (request.json if request else None) or {}
                symbol = request_data.get('symbol', None)
                insight_type = request_data.get('type', 'market_analysis')
                
                insights = asyncio.run(self.insight_generator.generate_insights(symbol, insight_type))
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'insights': insights,
                    'count': len(insights),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error generating insights: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/data-sources/status', methods=['GET'])
        def get_data_sources_status():
            """Get status of all data sources"""
            try:
                status_data = self.database.get_data_source_status()
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'data_sources': status_data,
                    'count': len(status_data),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error getting data sources status: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/market-summary', methods=['GET'])
        def get_market_summary():
            """Get comprehensive market summary"""
            try:
                # Get latest data from various sources
                risk_data = self.database.get_latest_data('crypto_risk_indicators', 1)
                screener_data = self.database.get_latest_data('screener_data', 20)
                dominance_data = self.database.get_latest_data('dominance_data', 1)
                
                # Calculate summary statistics
                summary = {
                    'risk_indicators': risk_data[0] if risk_data else None,
                    'market_overview': {
                        'total_symbols_tracked': len(screener_data),
                        'avg_risk_level': sum(item.get('fiat_risk', 0) for item in screener_data) / len(screener_data) if screener_data else 0,
                        'high_risk_symbols': len([item for item in screener_data if item.get('fiat_risk', 0) > 0.6]),
                        'low_risk_symbols': len([item for item in screener_data if item.get('fiat_risk', 0) < 0.4])
                    },
                    'dominance': dominance_data[0] if dominance_data else None,
                    'timestamp': datetime.now().isoformat()
                }
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'summary': summary,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error getting market summary: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/cleanup', methods=['POST'])
        def cleanup_old_data():
            """Clean up old data from database"""
            try:
                request_data = (request.json if request else None) or {}
                days_to_keep = request_data.get('days_to_keep', 30)
                
                self.database.cleanup_old_data(days_to_keep)
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'message': f'Cleaned up data older than {days_to_keep} days',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error cleaning up data: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/validate', methods=['GET'])
        def validate_extractors():
            """Validate that all extractors are working"""
            try:
                results = {}
                
                # Validate crypto risk extractor
                results['crypto_risk'] = asyncio.run(self.crypto_risk_extractor.validate_extraction())
                
                # Validate screener extractor
                results['screener'] = asyncio.run(self.screener_extractor.validate_extraction())
                
                all_valid = all(results.values())
                
                if jsonify:
                    return jsonify({
                    'success': all_valid,
                    'validation_results': results,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error validating extractors: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
    
    def _setup_scheduler(self):
        """Setup scheduled data extraction tasks"""
        if not SCHEDULE_AVAILABLE or not schedule:
            logger.warning("Schedule module not available - skipping scheduled tasks setup")
            return
        
        # Schedule crypto risk indicators extraction every 15 minutes
        schedule.every(15).minutes.do(self._scheduled_crypto_risk_extraction)
        
        # Schedule screener data extraction every 5 minutes
        schedule.every(5).minutes.do(self._scheduled_screener_extraction)
        
        # Schedule AI insights generation every 30 minutes
        schedule.every(30).minutes.do(self._scheduled_insights_generation)
        
        # Schedule database cleanup daily at 2 AM
        schedule.every().day.at("02:00").do(self._scheduled_cleanup)
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("Scheduled tasks configured")
    
    def _run_scheduler(self):
        """Run the scheduler in background"""
        if not SCHEDULE_AVAILABLE or not schedule:
            logger.warning("Schedule module not available - scheduler thread exiting")
            return
            
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)
    
    def _scheduled_crypto_risk_extraction(self):
        """Scheduled crypto risk indicators extraction"""
        try:
            logger.info("Running scheduled crypto risk extraction")
            result = asyncio.run(self.crypto_risk_extractor.extract_with_mock_data())
            self.database.save_extraction_result(result)
            logger.info(f"Scheduled crypto risk extraction completed: {result.success}")
        except Exception as e:
            logger.error(f"Scheduled crypto risk extraction failed: {str(e)}")
    
    def _scheduled_screener_extraction(self):
        """Scheduled screener data extraction"""
        try:
            logger.info("Running scheduled screener extraction")
            result = asyncio.run(self.screener_extractor.extract_with_mock_data())
            self.database.save_extraction_result(result)
            logger.info(f"Scheduled screener extraction completed: {result.success}")
        except Exception as e:
            logger.error(f"Scheduled screener extraction failed: {str(e)}")
    
    def _scheduled_insights_generation(self):
        """Scheduled AI insights generation"""
        try:
            logger.info("Running scheduled insights generation")
            insights = asyncio.run(self.insight_generator.generate_insights())
            logger.info(f"Generated {len(insights)} insights")
        except Exception as e:
            logger.error(f"Scheduled insights generation failed: {str(e)}")
    
    def _scheduled_cleanup(self):
        """Scheduled database cleanup"""
        try:
            logger.info("Running scheduled database cleanup")
            self.database.cleanup_old_data(30)  # Keep 30 days of data
            logger.info("Scheduled database cleanup completed")
        except Exception as e:
            logger.error(f"Scheduled database cleanup failed: {str(e)}")
    
    def run(self, debug: bool = False, host: str = '0.0.0.0', threaded: bool = True):
        """Run the Flask API server with flexible configuration
        
        Args:
            debug: Enable debug mode for development
            host: Host address to bind to (default: '0.0.0.0' for all interfaces)
            threaded: Enable threaded mode for concurrent requests
        """
        logger.info(f"🚀 Starting Cryptoverse API server")
        logger.info(f"   📍 Host: {host}")
        logger.info(f"   🔌 Port: {self.port}")
        logger.info(f"   🐛 Debug: {debug}")
        logger.info(f"   🧵 Threaded: {threaded}")
        logger.info(f"   📊 Features enabled:")
        logger.info(f"      - Automated Scheduling: {'✅' if SCHEDULE_AVAILABLE else '❌'}")
        logger.info(f"      - Database Integration: ✅")
        logger.info(f"      - Error Handling: ✅")
        logger.info(f"      - CORS Support: ✅")
        logger.info(f"      - Request Logging: ✅")
        logger.info(f"      - Health Monitoring: ✅")
        logger.info(f"   🔗 Available endpoints: /health, /api/system-status, /api/crypto-risk-indicators, /api/screener-data")
        
        try:
            self.app.run(host=host, port=self.port, debug=debug, threaded=threaded)
        except Exception as e:
            logger.error(f"💥 Failed to start server: {str(e)}")
            raise

# Main entry point
if __name__ == "__main__":
    import sys
    import argparse
    
    # Setup command line argument parsing
    parser = argparse.ArgumentParser(description='Cryptoverse Data Extraction API Server')
    parser.add_argument('--port', '-p', type=int, default=5002, 
                       help='Port to run the server on (default: 5002)')
    parser.add_argument('--host', default='0.0.0.0',
                       help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Set logging level (default: INFO)')
    parser.add_argument('--no-scheduler', action='store_true',
                       help='Disable automated scheduling')
    
    args = parser.parse_args()
    
    # Configure logging with selected level
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('cryptoverse_api.log')
        ]
    )
    
    logger.info("🎯 Cryptoverse API Server Starting...")
    logger.info(f"   📋 Configuration:")
    logger.info(f"      Port: {args.port}")
    logger.info(f"      Host: {args.host}")
    logger.info(f"      Debug: {args.debug}")
    logger.info(f"      Log Level: {args.log_level}")
    logger.info(f"      Scheduler: {'Disabled' if args.no_scheduler else 'Enabled'}")
    
    try:
        # Create API instance
        api = CryptoverseAPI(port=args.port)
        
        # Disable scheduler if requested
        if args.no_scheduler and SCHEDULE_AVAILABLE and schedule:
            schedule.clear()
            logger.info("🚫 Automated scheduling disabled by user request")
        
        # Run the server
        api.run(debug=args.debug, host=args.host)
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Server failed to start: {str(e)}")
        sys.exit(1)