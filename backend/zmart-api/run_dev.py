#!/usr/bin/env python3
"""
Zmart Trading Bot Platform - Development Server
FastAPI development server with hot reload
"""
import uvicorn
import logging
from src.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)

logger = logging.getLogger(__name__)

def main():
    """Start the development server"""
    try:
        logger.info("Starting Zmart Trading Bot Platform development server")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Debug mode: {settings.DEBUG}")
        logger.info(f"Host: {settings.HOST}")
        logger.info(f"Port: {settings.PORT}")
        
        # Start the server
        uvicorn.run(
            "src.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=True,
            reload_dirs=["src"],
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        logger.info("Make sure all dependencies are installed and database services are running")
        raise

if __name__ == "__main__":
    main() 