#!/usr/bin/env python3
"""
🎯 Unified Pattern Recognition API Server
Main server for the complete pattern analysis system
"""

from flask import Flask, jsonify
from flask_cors import CORS
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
import asyncio
from threading import Thread

# Add paths for imports
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import routes
from src.routes.unified_pattern_routes import unified_pattern_bp

# Import data manager
from DataManagementLibrary.core.data_manager import DataManager, get_data_manager

# Import pattern agent
from src.agents.unified_pattern_agent import UnifiedPatternAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== Flask Application ====================

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'zmartbot-unified-pattern-system')
    app.config['JSON_SORT_KEYS'] = False
    
    # Register blueprints
    app.register_blueprint(unified_pattern_bp, url_prefix='/api/patterns')
    
    # ==================== Root Routes ====================
    
    @app.route('/', methods=['GET'])
    def home():
        """Home route with system information"""
        return jsonify({
            "service": "Unified Pattern Recognition System",
            "version": "1.0.0",
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "pattern_analysis": "/api/patterns/analyze/<symbol>",
                "pattern_detection": "/api/patterns/detect",
                "win_rates": "/api/patterns/winrate/<symbol>",
                "statistics": "/api/patterns/statistics/<symbol>",
                "report": "/api/patterns/report/<symbol>",
                "batch_analysis": "/api/patterns/batch/analyze",
                "learning": "/api/patterns/learn/outcome",
                "health": "/api/patterns/health",
                "status": "/api/patterns/status"
            },
            "documentation": "https://github.com/zmartbot/pattern-recognition",
            "data_sources": [
                "RiskMetric (Benjamin Cowen Risk Bands)",
                "Cryptometer (17 Endpoints)",
                "Kingfisher (Liquidation Analysis)"
            ]
        })
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        try:
            # Check data manager
            dm = get_data_manager()
            stats = dm.get_statistics()
            
            # Check pattern agent
            agent = UnifiedPatternAgent()
            
            return jsonify({
                "status": "healthy",
                "components": {
                    "api": "operational",
                    "data_manager": "operational",
                    "pattern_agent": "operational",
                    "database": "operational"
                },
                "data_stats": {
                    "total_entries": stats.get("total_entries", 0),
                    "symbols": len(stats.get("symbols", [])),
                    "last_update": datetime.now().isoformat()
                },
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 503
    
    @app.route('/api/data/stats', methods=['GET'])
    def data_statistics():
        """Get data library statistics"""
        try:
            dm = get_data_manager()
            stats = dm.get_statistics()
            
            return jsonify({
                "success": True,
                "statistics": stats,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting data statistics: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/data/symbols', methods=['GET'])
    def list_symbols():
        """List all available symbols"""
        try:
            dm = get_data_manager()
            stats = dm.get_statistics()
            symbols = stats.get("symbols", [])
            
            # Get latest data for each symbol
            symbol_info = []
            for symbol in symbols:
                latest = dm.get_latest(symbol)
                if latest:
                    symbol_info.append({
                        "symbol": symbol,
                        "last_update": latest.timestamp.isoformat(),
                        "data_type": latest.data_type.value,
                        "source": latest.source.value
                    })
                else:
                    symbol_info.append({
                        "symbol": symbol,
                        "last_update": None,
                        "data_type": None,
                        "source": None
                    })
            
            return jsonify({
                "success": True,
                "symbols": symbol_info,
                "total": len(symbols),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error listing symbols: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """404 error handler"""
        return jsonify({
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 error handler"""
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }), 500
    
    return app

# ==================== Background Tasks ====================

class PatternMonitor:
    """Background pattern monitoring service"""
    
    def __init__(self):
        self.running = False
        self.agent = UnifiedPatternAgent()
        self.dm = get_data_manager()
        self.monitor_interval = 60  # seconds
    
    def start(self):
        """Start monitoring"""
        self.running = True
        thread = Thread(target=self._monitor_loop, daemon=True)
        thread.start()
        logger.info("🔍 Pattern monitoring started")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("🛑 Pattern monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Get list of symbols to monitor
                stats = self.dm.get_statistics()
                symbols = stats.get("symbols", [])
                
                for symbol in symbols[:5]:  # Limit to top 5 for performance
                    asyncio.run(self._analyze_symbol(symbol))
                
                # Wait before next cycle
                asyncio.run(asyncio.sleep(self.monitor_interval))
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                asyncio.run(asyncio.sleep(10))  # Wait before retry
    
    async def _analyze_symbol(self, symbol: str):
        """Analyze a single symbol"""
        try:
            # Fetch latest data (placeholder - would need actual data fetching)
            result = await self.agent.analyze_symbol(symbol, {})
            
            # Store pattern analysis
            self.dm.import_pattern_data({
                "symbol": symbol,
                "pattern_score": result.pattern_score,
                "signal_strength": result.signal_strength,
                "confidence_level": result.confidence_level,
                "detected_patterns": len(result.detected_patterns),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✅ Analyzed {symbol}: Score {result.pattern_score:.1f}")
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")

# ==================== Main Execution ====================

def main():
    """Main server execution"""
    print("\n" + "="*60)
    print("🎯 UNIFIED PATTERN RECOGNITION SYSTEM")
    print("="*60)
    
    # Initialize data manager
    print("\n📊 Initializing Data Manager...")
    dm = get_data_manager(str(Path.home() / "Desktop" / "ZmartBot" / "DataLibrary"))
    stats = dm.get_statistics()
    print(f"  ✅ Data Manager ready")
    print(f"  • Total entries: {stats.get('total_entries', 0)}")
    print(f"  • Symbols: {len(stats.get('symbols', []))}")
    
    # Initialize pattern agent
    print("\n🤖 Initializing Pattern Agent...")
    agent = UnifiedPatternAgent()
    print(f"  ✅ Pattern Agent ready")
    
    # Create Flask app
    print("\n🌐 Starting API Server...")
    app = create_app()
    
    # Start pattern monitoring
    print("\n🔍 Starting Pattern Monitor...")
    monitor = PatternMonitor()
    monitor.start()
    print(f"  ✅ Monitoring active")
    
    # Server configuration
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5556))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print("\n" + "="*60)
    print(f"🚀 Server starting on http://{host}:{port}")
    print("="*60)
    
    print("\n📍 Available Endpoints:")
    print(f"  • Home: http://localhost:{port}/")
    print(f"  • Health: http://localhost:{port}/health")
    print(f"  • Pattern Analysis: http://localhost:{port}/api/patterns/analyze/<symbol>")
    print(f"  • Win Rates: http://localhost:{port}/api/patterns/winrate/<symbol>")
    print(f"  • Reports: http://localhost:{port}/api/patterns/report/<symbol>")
    print(f"  • Data Stats: http://localhost:{port}/api/data/stats")
    print(f"  • Symbols: http://localhost:{port}/api/data/symbols")
    
    print("\n✨ System ready for pattern recognition!\n")
    
    try:
        # Run the Flask app
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False  # Disable reloader to prevent duplicate monitoring
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
        monitor.stop()
        print("✅ Server stopped gracefully")

if __name__ == "__main__":
    main()