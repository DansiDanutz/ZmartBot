"""Main application entry point for the Symbol Alerts System."""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager

from src.core.engine import AlertEngine
from src.integrations.trading_bot_connector import TradingBotConnector
from src.integrations.api_server import AlertAPIServer
from src.integrations.websocket_server import WebSocketServer
from src.utils.logging_config import setup_logging
from config.settings import get_settings
from config.database import init_database, close_database

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global instances
alert_engine = None
trading_connector = None
api_server = None
websocket_server = None


async def startup():
    """Application startup."""
    global alert_engine, trading_connector, api_server, websocket_server
    
    logger.info("Starting Symbol Alerts System...")
    
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized")
        
        # Initialize core components
        alert_engine = AlertEngine()
        await alert_engine.initialize()
        logger.info("Alert Engine initialized")
        
        # Initialize trading connector
        trading_connector = TradingBotConnector()
        logger.info("Trading Bot Connector initialized")
        
        # Initialize API server
        api_server = AlertAPIServer(alert_engine, trading_connector)
        logger.info("API Server initialized")
        
        # Initialize WebSocket server
        websocket_server = WebSocketServer(alert_engine)
        logger.info("WebSocket Server initialized")
        
        # Start services
        await alert_engine.start()
        logger.info("Alert Engine started")
        
        # Start servers
        settings = get_settings()
        
        # Start WebSocket server
        await websocket_server.start_server(
            settings.websocket.host,
            settings.websocket.port
        )
        logger.info(f"WebSocket server started on {settings.websocket.host}:{settings.websocket.port}")
        
        # Start API server (this will block)
        logger.info(f"Starting API server on {settings.api.host}:{settings.api.port}")
        await api_server.start_server(settings.api.host, settings.api.port)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        await shutdown()
        sys.exit(1)


async def shutdown():
    """Application shutdown."""
    global alert_engine, trading_connector, api_server, websocket_server
    
    logger.info("Shutting down Symbol Alerts System...")
    
    try:
        # Stop WebSocket server
        if websocket_server:
            await websocket_server.stop_server()
            logger.info("WebSocket server stopped")
        
        # Stop trading connector
        if trading_connector:
            await trading_connector.shutdown()
            logger.info("Trading connector stopped")
        
        # Stop alert engine
        if alert_engine:
            await alert_engine.stop()
            logger.info("Alert engine stopped")
        
        # Close database
        await close_database()
        logger.info("Database connections closed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("Shutdown complete")


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    asyncio.create_task(shutdown())


async def main():
    """Main application function."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await startup()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await shutdown()


if __name__ == "__main__":
    # Run the application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

