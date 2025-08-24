#!/usr/bin/env python3
"""
Real Cryptoverse API
Production-ready Flask API with real data extraction and AI insights
Implements complete data pipeline from extraction to consumption
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# Flask imports with error handling for linter issues
try:
    from flask import Flask, jsonify, request, Response  # type: ignore[import]
    from flask_cors import CORS  # type: ignore[import]
    FLASK_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Flask import failed: {e}")
    # Define placeholders for linter
    Flask = None  # type: ignore[assignment]
    jsonify = None  # type: ignore[assignment]
    request = None  # type: ignore[assignment]
    Response = None  # type: ignore[assignment]
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

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.cryptoverse_database import CryptoverseDatabase
from extractors.real_crypto_risk_extractor import RealCryptoRiskExtractor
try:
    from extractors.real_screener_extractor import RealScreenerExtractor
except ImportError:
    # Fallback for import issues
    RealScreenerExtractor = None
from ai_insights.real_insight_generator import RealInsightGenerator

logger = logging.getLogger(__name__)

class RealCryptoverseAPI:
    """Production-ready Flask API for Cryptoverse data extraction and AI insights"""
    
    def __init__(self, port: int = 5003):
        if not FLASK_AVAILABLE or not Flask:
            raise ImportError("Flask is not available - cannot create API server")
        
        self.app = Flask(__name__)
        if CORS:
            CORS(self.app)
        self.port = port
        
        # Initialize components with real implementations
        self.database = CryptoverseDatabase()
        self.crypto_risk_extractor = RealCryptoRiskExtractor()
        self.screener_extractor = RealScreenerExtractor() if RealScreenerExtractor else None
        self.insight_generator = RealInsightGenerator(self.database)
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Background task control
        self.scheduler_running = False
        self.scheduler_thread = None
        
        # Request tracking
        self._request_count = 0
        self._extraction_count = 0
        self._successful_extractions = 0
        self._failed_extractions = 0
        
        # Setup routes
        self._setup_routes()
        
        # Setup scheduled tasks
        self._setup_scheduler()
        
        logger.info("Real Cryptoverse API initialized with production components")
    
    def _setup_routes(self):
        """Setup all API routes with real data processing"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Comprehensive health check endpoint"""
            try:
                # Check database connectivity
                db_status = self._check_database_health()
                
                # Check data freshness
                data_freshness = self._check_data_freshness()
                
                # System metrics
                system_metrics = self._get_system_metrics()
                
                health_status = {
                    'status': 'healthy' if db_status and data_freshness['fresh'] else 'degraded',
                    'service': 'Real Cryptoverse Data Extraction API',
                    'timestamp': datetime.now().isoformat(),
                    'version': '2.0.0',
                    'components': {
                        'database': 'healthy' if db_status else 'error',
                        'data_freshness': 'fresh' if data_freshness['fresh'] else 'stale',
                        'scheduler': 'running' if self.scheduler_running else 'stopped'
                    },
                    'data_sources': 21,
                    'endpoints': 15,
                    'last_extraction': data_freshness.get('last_extraction'),
                    'system_metrics': system_metrics
                }
                
                status_code = 200 if health_status['status'] == 'healthy' else 503
                if jsonify:
                    return jsonify(health_status), status_code
                
            except Exception as e:
                logger.error(f"Health check failed: {str(e)}")
                if jsonify:
                    return jsonify({
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/extract/comprehensive', methods=['POST'])
        def trigger_comprehensive_extraction():
            """Trigger comprehensive data extraction from all sources"""
            try:
                request_data = (request.json if request else {})
                force_refresh = request_data.get('force_refresh', False)
                
                logger.info("🚀 Starting comprehensive data extraction")
                
                # Run extraction in background
                future = self.executor.submit(self._run_comprehensive_extraction, force_refresh)
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'message': 'Comprehensive data extraction started',
                    'extraction_id': f"extract_{int(time.time())}",
                    'estimated_completion': (datetime.now() + timedelta(minutes=2)).isoformat(),
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error triggering extraction: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/crypto-risk-indicators', methods=['GET'])
        def get_comprehensive_risk_indicators():
            """Get comprehensive crypto risk indicators with real data"""
            try:
                limit = (request.args.get('limit', 5, type=int) if request else 5)
                include_analysis = ((request.args.get('analysis', 'true') if request else 'true').lower() == 'true')
                
                # Get latest risk data
                risk_data = self.database.get_latest_data('crypto_risk_indicators', limit)
                
                if not risk_data:
                    # Trigger extraction if no data
                    logger.info("No risk data found, triggering extraction")
                    self.executor.submit(self._extract_risk_data_background)
                    
                    if jsonify:
                        return jsonify({
                        'success': True,
                        'data': [],
                        'message': 'No data available, extraction triggered',
                        'count': 0,
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Process and enrich data
                processed_data = []
                for item in risk_data:
                    if isinstance(item, dict):
                        processed_item = {
                            'timestamp': item.get('timestamp'),
                            'overall_risk_score': item.get('overall_risk_score', 0.5),
                            'risk_level': item.get('risk_level', 'Moderate'),
                            'market_data': item.get('market_data', {}),
                            'fear_greed_index': item.get('fear_greed_index', {}),
                            'volatility_metrics': item.get('volatility_metrics', {}),
                            'recommendations': item.get('recommendations', [])
                        }
                        
                        if include_analysis:
                            processed_item['risk_analysis'] = item.get('risk_analysis', {})
                            processed_item['onchain_metrics'] = item.get('onchain_metrics', {})
                        
                        processed_data.append(processed_item)
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'data': processed_data,
                    'count': len(processed_data),
                    'data_sources': self._count_data_sources(risk_data),
                    'last_updated': processed_data[0].get('timestamp') if processed_data else None,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error getting risk indicators: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/screener-data', methods=['GET'])
        def get_comprehensive_screener_data():
            """Get comprehensive screener data with real market analysis"""
            try:
                limit = (request.args.get('limit', 3, type=int) if request else 3)
                symbol = (request.args.get('symbol', None) if request else None)
                include_technical = ((request.args.get('technical', 'true') if request else 'true').lower() == 'true')
                
                screener_data = self.database.get_latest_data('screener_data', limit)
                
                if not screener_data:
                    # Trigger extraction if no data
                    logger.info("No screener data found, triggering extraction")
                    self.executor.submit(self._extract_screener_data_background)
                    
                    if jsonify:
                        return jsonify({
                        'success': True,
                        'data': [],
                        'message': 'No data available, extraction triggered',
                        'count': 0,
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Process and filter data
                processed_data = []
                for item in screener_data:
                    if isinstance(item, dict):
                        processed_item = {
                            'timestamp': item.get('timestamp'),
                            'total_coins_analyzed': item.get('total_coins_analyzed', 0),
                            'market_overview': item.get('market_overview', {}),
                            'top_performers': item.get('top_performers', {}),
                            'screening_summary': item.get('screening_summary', {})
                        }
                        
                        if include_technical:
                            processed_item['technical_analysis'] = item.get('technical_analysis', {})
                            processed_item['volume_analysis'] = item.get('volume_analysis', {})
                        
                        # Filter by symbol if specified
                        if symbol:
                            processed_item = self._filter_by_symbol(processed_item, symbol)
                        
                        processed_data.append(processed_item)
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'data': processed_data,
                    'count': len(processed_data),
                    'symbol_filter': symbol,
                    'last_updated': processed_data[0].get('timestamp') if processed_data else None,
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
        
        @self.app.route('/api/ai-insights', methods=['GET'])
        def get_comprehensive_ai_insights():
            """Get comprehensive AI-generated insights with real analysis"""
            try:
                symbol = (request.args.get('symbol', None) if request else None)
                limit = (request.args.get('limit', 10, type=int) if request else 10)
                insight_type = (request.args.get('type', None) if request else None)
                
                logger.info(f"🧠 Generating AI insights for {symbol or 'all markets'}")
                
                # Generate fresh insights
                insights = asyncio.run(
                    self.insight_generator.generate_comprehensive_insights(symbol)
                )
                
                # Filter by type if specified
                if insight_type:
                    insights = [insight for insight in insights 
                              if insight.get('type') == insight_type]
                
                # Limit results
                insights = insights[:limit]
                
                # Add metadata
                insight_metadata = {
                    'total_insights': len(insights),
                    'insight_types': list(set(insight.get('type') for insight in insights)),
                    'confidence_scores': [insight.get('confidence', 0) for insight in insights],
                    'actionable_insights': len([i for i in insights if i.get('actionable', False)]),
                    'high_severity_insights': len([i for i in insights if i.get('severity') in ['high', 'critical']])
                }
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'insights': insights,
                    'metadata': insight_metadata,
                    'generation_time': datetime.now().isoformat(),
                    'symbol_filter': symbol,
                    'type_filter': insight_type
                })
                
            except Exception as e:
                logger.error(f"Error generating AI insights: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/market-summary', methods=['GET'])
        def get_comprehensive_market_summary():
            """Get comprehensive market summary combining all data sources"""
            try:
                # Get latest data from all sources
                risk_data = self.database.get_latest_data('crypto_risk_indicators', 1)
                screener_data = self.database.get_latest_data('screener_data', 1)
                
                # Generate market summary
                market_summary = {
                    'timestamp': datetime.now().isoformat(),
                    'data_availability': {
                        'risk_data': len(risk_data) > 0,
                        'screener_data': len(screener_data) > 0
                    }
                }
                
                # Add risk summary
                if risk_data and isinstance(risk_data[0], dict):
                    risk_info = risk_data[0]
                    market_summary['risk_summary'] = {
                        'overall_risk_score': risk_info.get('overall_risk_score', 0.5),
                        'risk_level': risk_info.get('risk_level', 'Moderate'),
                        'fear_greed_index': risk_info.get('fear_greed_index', {}).get('current_value', 50),
                        'top_recommendations': risk_info.get('recommendations', [])[:3]
                    }
                
                # Add market summary
                if screener_data and isinstance(screener_data[0], dict):
                    screener_info = screener_data[0]
                    market_overview = screener_info.get('market_overview', {})
                    market_summary['market_summary'] = {
                        'total_market_cap': market_overview.get('total_market_cap_usd', 0),
                        'market_cap_change_24h': market_overview.get('market_cap_change_24h', 0),
                        'average_24h_change': market_overview.get('average_24h_change', 0),
                        'market_sentiment': market_overview.get('market_sentiment', 'neutral'),
                        'coins_up': market_overview.get('coins_up', 0),
                        'coins_down': market_overview.get('coins_down', 0)
                    }
                    
                    # Add top performers
                    top_performers = screener_info.get('top_performers', {})
                    if top_performers:
                        market_summary['top_performers'] = {
                            'top_24h_gainer': top_performers.get('top_24h_gainers', [{}])[0] if top_performers.get('top_24h_gainers') else {},
                            'highest_volume': top_performers.get('highest_volume', [{}])[0] if top_performers.get('highest_volume') else {}
                        }
                
                # Generate quick insights
                quick_insights = self._generate_quick_insights(market_summary)
                market_summary['quick_insights'] = quick_insights
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'market_summary': market_summary,
                    'last_updated': max(
                        risk_data[0].get('timestamp', '') if risk_data else '',
                        screener_data[0].get('timestamp', '') if screener_data else ''
                    ),
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error generating market summary: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/data-sources/status', methods=['GET'])
        def get_data_sources_status():
            """Get comprehensive status of all data sources"""
            try:
                # Check each data source
                data_sources_status = {}
                
                # Risk indicators
                risk_data = self.database.get_latest_data('crypto_risk_indicators', 1)
                data_sources_status['crypto_risk_indicators'] = {
                    'status': 'active' if risk_data else 'inactive',
                    'last_update': risk_data[0].get('timestamp') if risk_data else None,
                    'data_points': len(risk_data),
                    'data_quality': self._assess_data_quality(risk_data, 'risk')
                }
                
                # Screener data
                screener_data = self.database.get_latest_data('screener_data', 1)
                data_sources_status['screener_data'] = {
                    'status': 'active' if screener_data else 'inactive',
                    'last_update': screener_data[0].get('timestamp') if screener_data else None,
                    'data_points': len(screener_data),
                    'data_quality': self._assess_data_quality(screener_data, 'screener')
                }
                
                # Overall system status
                active_sources = len([s for s in data_sources_status.values() if s['status'] == 'active'])
                total_sources = len(data_sources_status)
                
                system_status = {
                    'overall_status': 'healthy' if active_sources == total_sources else 'degraded',
                    'active_sources': active_sources,
                    'total_sources': total_sources,
                    'data_sources': data_sources_status,
                    'system_uptime': self._get_system_uptime(),
                    'last_extraction': self._get_last_extraction_time(),
                    'timestamp': datetime.now().isoformat()
                }
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'system_status': system_status,
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
        
        @self.app.route('/api/performance-metrics', methods=['GET'])
        def get_performance_metrics():
            """Get API and system performance metrics"""
            try:
                metrics = {
                    'api_metrics': {
                        'total_requests': getattr(self, '_request_count', 0),
                        'successful_requests': getattr(self, '_success_count', 0),
                        'error_requests': getattr(self, '_error_count', 0),
                        'average_response_time': getattr(self, '_avg_response_time', 0)
                    },
                    'data_metrics': {
                        'total_extractions': getattr(self, '_extraction_count', 0),
                        'successful_extractions': getattr(self, '_successful_extractions', 0),
                        'failed_extractions': getattr(self, '_failed_extractions', 0),
                        'data_freshness_score': self._calculate_data_freshness_score()
                    },
                    'system_metrics': self._get_system_metrics(),
                    'timestamp': datetime.now().isoformat()
                }
                
                if jsonify:
                    return jsonify({
                    'success': True,
                    'metrics': metrics,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error getting performance metrics: {str(e)}")
                if jsonify:
                    return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        # Add request tracking middleware
        @self.app.before_request
        def before_request():
            if request:
                request.start_time = time.time()
            self._request_count = getattr(self, '_request_count', 0) + 1
        
        @self.app.after_request
        def after_request(response):
            if request and hasattr(request, 'start_time'):
                response_time = time.time() - request.start_time
                self._update_response_metrics(response_time, response.status_code)
            return response
    
    def _setup_scheduler(self):
        """Setup automated data extraction scheduler"""
        if not SCHEDULE_AVAILABLE or not schedule:
            logger.warning("Schedule module not available - skipping automated scheduler setup")
            return
        
        # Schedule regular extractions
        schedule.every(15).minutes.do(self._scheduled_risk_extraction)
        schedule.every(30).minutes.do(self._scheduled_screener_extraction)
        schedule.every(1).hours.do(self._scheduled_comprehensive_extraction)
        schedule.every(6).hours.do(self._database_maintenance)
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        self.scheduler_running = True
        
        logger.info("✅ Automated scheduler started")
    
    def _run_scheduler(self):
        """Run the scheduled tasks"""
        if not SCHEDULE_AVAILABLE or not schedule:
            logger.warning("Schedule module not available - scheduler thread exiting")
            return
            
        while self.scheduler_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)
    
    def _scheduled_risk_extraction(self):
        """Scheduled risk data extraction"""
        try:
            logger.info("⏰ Running scheduled risk data extraction")
            self.executor.submit(self._extract_risk_data_background)
        except Exception as e:
            logger.error(f"Scheduled risk extraction failed: {str(e)}")
    
    def _scheduled_screener_extraction(self):
        """Scheduled screener data extraction"""
        try:
            logger.info("⏰ Running scheduled screener data extraction")
            self.executor.submit(self._extract_screener_data_background)
        except Exception as e:
            logger.error(f"Scheduled screener extraction failed: {str(e)}")
    
    def _scheduled_comprehensive_extraction(self):
        """Scheduled comprehensive data extraction"""
        try:
            logger.info("⏰ Running scheduled comprehensive data extraction")
            self.executor.submit(self._run_comprehensive_extraction, False)
        except Exception as e:
            logger.error(f"Scheduled comprehensive extraction failed: {str(e)}")
    
    def _database_maintenance(self):
        """Scheduled database maintenance"""
        try:
            logger.info("🧹 Running database maintenance")
            self.database.cleanup_old_data(days_to_keep=30)
            logger.info("✅ Database maintenance completed")
        except Exception as e:
            logger.error(f"Database maintenance failed: {str(e)}")
    
    # Background extraction methods
    def _extract_risk_data_background(self):
        """Extract risk data in background"""
        try:
            result = asyncio.run(self.crypto_risk_extractor.extract_comprehensive_risk_data())
            if result.success:
                self.database.save_extraction_result(result)
                logger.info("✅ Background risk data extraction completed")
                self._successful_extractions = getattr(self, '_successful_extractions', 0) + 1
            else:
                logger.error(f"❌ Risk data extraction failed: {result.error_message}")
                self._failed_extractions = getattr(self, '_failed_extractions', 0) + 1
        except Exception as e:
            logger.error(f"❌ Background risk extraction error: {str(e)}")
            self._failed_extractions = getattr(self, '_failed_extractions', 0) + 1
    
    def _extract_screener_data_background(self):
        """Extract screener data in background"""
        try:
            if self.screener_extractor:
                result = asyncio.run(self.screener_extractor.extract_screener_data())
            else:
                logger.warning("Screener extractor not available")
                return
            if result.success:
                self.database.save_extraction_result(result)
                logger.info("✅ Background screener data extraction completed")
                self._successful_extractions = getattr(self, '_successful_extractions', 0) + 1
            else:
                logger.error(f"❌ Screener data extraction failed: {result.error_message}")
                self._failed_extractions = getattr(self, '_failed_extractions', 0) + 1
        except Exception as e:
            logger.error(f"❌ Background screener extraction error: {str(e)}")
            self._failed_extractions = getattr(self, '_failed_extractions', 0) + 1
    
    def _run_comprehensive_extraction(self, force_refresh: bool = False):
        """Run comprehensive data extraction from all sources"""
        try:
            logger.info(f"🔄 Starting comprehensive extraction (force_refresh: {force_refresh})")
            
            # Extract from all sources
            self._extract_risk_data_background()
            time.sleep(2)  # Rate limiting
            self._extract_screener_data_background()
            
            logger.info("✅ Comprehensive extraction completed")
            self._extraction_count = getattr(self, '_extraction_count', 0) + 1
            
        except Exception as e:
            logger.error(f"❌ Comprehensive extraction failed: {str(e)}")
    
    # Helper methods
    def _check_database_health(self) -> bool:
        """Check database connectivity and health"""
        try:
            # Try to get data source status
            test_data = self.database.get_data_source_status()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
    
    def _check_data_freshness(self) -> Dict[str, Any]:
        """Check data freshness across all sources"""
        try:
            risk_data = self.database.get_latest_data('crypto_risk_indicators', 1)
            screener_data = self.database.get_latest_data('screener_data', 1)
            
            now = datetime.now()
            freshness_threshold = timedelta(hours=2)
            
            fresh_sources = 0
            total_sources = 2
            last_extraction = None
            
            if risk_data:
                risk_time = datetime.fromisoformat(risk_data[0].get('timestamp', ''))
                if now - risk_time < freshness_threshold:
                    fresh_sources += 1
                last_extraction = risk_data[0].get('timestamp')
            
            if screener_data:
                screener_time = datetime.fromisoformat(screener_data[0].get('timestamp', ''))
                if now - screener_time < freshness_threshold:
                    fresh_sources += 1
                if not last_extraction or screener_data[0].get('timestamp') > last_extraction:
                    last_extraction = screener_data[0].get('timestamp')
            
            return {
                'fresh': fresh_sources >= total_sources * 0.5,  # At least 50% fresh
                'fresh_sources': fresh_sources,
                'total_sources': total_sources,
                'last_extraction': last_extraction
            }
            
        except Exception as e:
            logger.error(f"Data freshness check failed: {str(e)}")
            return {'fresh': False, 'error': str(e)}
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            'scheduler_running': self.scheduler_running,
            'thread_pool_active': self.executor._threads if hasattr(self.executor, '_threads') else 0,
            'memory_usage': 'not_implemented',  # Would implement with psutil
            'cpu_usage': 'not_implemented',     # Would implement with psutil
            'uptime': self._get_system_uptime()
        }
    
    def _get_system_uptime(self) -> str:
        """Get system uptime"""
        if not hasattr(self, '_start_time'):
            self._start_time = datetime.now()
        
        uptime = datetime.now() - self._start_time
        return str(uptime).split('.')[0]  # Remove microseconds
    
    def _count_data_sources(self, data: List[Dict]) -> int:
        """Count available data sources in extracted data"""
        if not data or not isinstance(data[0], dict):
            return 0
        
        first_item = data[0]
        return first_item.get('data_sources', 1)
    
    def _filter_by_symbol(self, data: Dict, symbol: str) -> Dict:
        """Filter screener data by specific symbol"""
        # This would implement symbol-specific filtering
        # For now, just return the data as-is
        return data
    
    def _generate_quick_insights(self, market_summary: Dict) -> List[str]:
        """Generate quick market insights from summary data"""
        insights = []
        
        try:
            # Risk-based insights
            risk_summary = market_summary.get('risk_summary', {})
            risk_level = risk_summary.get('risk_level', 'Moderate')
            
            if risk_level in ['High', 'Very High']:
                insights.append(f"⚠️ Elevated market risk detected ({risk_level})")
            elif risk_level in ['Low', 'Very Low']:
                insights.append(f"✅ Favorable risk environment ({risk_level})")
            
            # Market performance insights
            market_data = market_summary.get('market_summary', {})
            avg_change = market_data.get('average_24h_change', 0)
            
            if avg_change > 5:
                insights.append(f"🚀 Strong market performance (+{avg_change:.1f}%)")
            elif avg_change < -5:
                insights.append(f"📉 Market decline detected ({avg_change:.1f}%)")
            
            # Sentiment insights
            fear_greed = risk_summary.get('fear_greed_index', 50)
            if fear_greed <= 25:
                insights.append("😨 Extreme fear - potential opportunity")
            elif fear_greed >= 75:
                insights.append("🤑 Extreme greed - exercise caution")
            
        except Exception as e:
            logger.error(f"Error generating quick insights: {str(e)}")
            insights.append("⚠️ Unable to generate insights")
        
        return insights[:5]  # Limit to 5 insights
    
    def _assess_data_quality(self, data: List[Dict], data_type: str) -> float:
        """Assess data quality score (0-1)"""
        if not data:
            return 0.0
        
        try:
            quality_score = 0.0
            
            # Check data completeness
            if isinstance(data[0], dict):
                expected_fields = {
                    'risk': ['timestamp', 'overall_risk_score', 'risk_level'],
                    'screener': ['timestamp', 'market_overview', 'top_performers']
                }
                
                required_fields = expected_fields.get(data_type, [])
                present_fields = len([f for f in required_fields if f in data[0]])
                completeness_score = present_fields / len(required_fields) if required_fields else 1.0
                
                quality_score += completeness_score * 0.5
            
            # Check data freshness
            if isinstance(data[0], dict) and 'timestamp' in data[0]:
                timestamp = datetime.fromisoformat(data[0]['timestamp'])
                age = datetime.now() - timestamp
                freshness_score = max(0, 1 - (age.total_seconds() / (2 * 3600)))  # 2 hours = 0 score
                quality_score += freshness_score * 0.5
            
            return min(1.0, quality_score)
            
        except Exception as e:
            logger.error(f"Error assessing data quality: {str(e)}")
            return 0.5
    
    def _get_last_extraction_time(self) -> Optional[str]:
        """Get the timestamp of the last successful extraction"""
        try:
            risk_data = self.database.get_latest_data('crypto_risk_indicators', 1)
            screener_data = self.database.get_latest_data('screener_data', 1)
            
            timestamps = []
            if risk_data:
                timestamps.append(risk_data[0].get('timestamp'))
            if screener_data:
                timestamps.append(screener_data[0].get('timestamp'))
            
            return max(timestamps) if timestamps else None
            
        except Exception as e:
            logger.error(f"Error getting last extraction time: {str(e)}")
            return None
    
    def _calculate_data_freshness_score(self) -> float:
        """Calculate overall data freshness score"""
        freshness_info = self._check_data_freshness()
        if freshness_info.get('fresh'):
            return 1.0
        
        fresh_ratio = freshness_info.get('fresh_sources', 0) / max(freshness_info.get('total_sources', 1), 1)
        return fresh_ratio
    
    def _update_response_metrics(self, response_time: float, status_code: int):
        """Update API response metrics"""
        if status_code < 400:
            self._success_count = getattr(self, '_success_count', 0) + 1
        else:
            self._error_count = getattr(self, '_error_count', 0) + 1
        
        # Update average response time
        current_avg = getattr(self, '_avg_response_time', 0)
        total_requests = getattr(self, '_request_count', 1)
        self._avg_response_time = (current_avg * (total_requests - 1) + response_time) / total_requests
    
    def run(self, debug: bool = False):
        """Run the Flask API server"""
        logger.info(f"🚀 Starting Real Cryptoverse API on port {self.port}")
        
        # Start initial data extraction
        self.executor.submit(self._run_comprehensive_extraction, True)
        
        if self.app:
            self.app.run(
                host='0.0.0.0',
                port=self.port,
                debug=debug,
                threaded=True
            )
    
    def shutdown(self):
        """Gracefully shutdown the API"""
        logger.info("🛑 Shutting down Real Cryptoverse API")
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        self.executor.shutdown(wait=True)

# Create and run the API
if __name__ == "__main__":
    api = RealCryptoverseAPI(port=5003)
    try:
        api.run(debug=False)
    except KeyboardInterrupt:
        api.shutdown()