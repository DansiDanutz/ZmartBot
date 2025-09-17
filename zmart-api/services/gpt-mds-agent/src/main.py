#!/usr/bin/env python3
"""
GptMDSagentService - Main Entry Point
=====================================
GPT-powered MDC/MDS document processing and generation service
"""

import os
import sys
import asyncio
import signal
import argparse
from pathlib import Path
from typing import Optional
import structlog

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from api.server import create_server, GptMDSagentServer

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class GptMDSagentService:
    """
    Main service class for GptMDSagentService
    """
    
    def __init__(self):
        self.server: Optional[GptMDSagentServer] = None
        self.shutdown_event = asyncio.Event()
        
    async def start(self, 
                   host: str = "0.0.0.0",
                   port: int = 8700,
                   openai_api_key: Optional[str] = None,
                   registry_url: str = "http://localhost:8610"):
        """Start the service"""
        try:
            logger.info("Starting GptMDSagentService",
                       host=host,
                       port=port,
                       registry_url=registry_url)
            
            # Create and start server
            self.server = await create_server(
                host=host,
                port=port,
                openai_api_key=openai_api_key,
                registry_url=registry_url
            )
            
            # Setup signal handlers
            self._setup_signal_handlers()
            
            # Start the server
            await self.server.start()
            
        except Exception as e:
            logger.error("Failed to start GptMDSagentService", error=str(e))
            raise
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def stop(self):
        """Stop the service"""
        try:
            logger.info("Stopping GptMDSagentService")
            
            if self.server:
                await self.server.stop()
            
            logger.info("GptMDSagentService stopped")
            
        except Exception as e:
            logger.error("Error stopping GptMDSagentService", error=str(e))
    
    async def run(self, 
                 host: str = "0.0.0.0",
                 port: int = 8700,
                 openai_api_key: Optional[str] = None,
                 registry_url: str = "http://localhost:8610"):
        """Run the service with graceful shutdown"""
        try:
            # Start the service
            await self.start(host, port, openai_api_key, registry_url)
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error("Service error", error=str(e))
        finally:
            # Stop the service
            await self.stop()

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="GptMDSagentService - GPT-powered MDC/MDS document processing"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8700,
        help="Port to bind to (default: 8700)"
    )
    
    parser.add_argument(
        "--openai-api-key",
        help="OpenAI API key (or set OPENAI_API_KEY environment variable)"
    )
    
    parser.add_argument(
        "--registry-url",
        default="http://localhost:8610",
        help="ZmartBot service registry URL (default: http://localhost:8610)"
    )
    
    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="GptMDSagentService v1.0.0"
    )
    
    return parser.parse_args()

def load_config(config_path: str) -> dict:
    """Load configuration from file"""
    import yaml
    
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        return {}

def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Set log level
    import logging
    logging.basicConfig(level=getattr(logging, args.log_level))
    
    # Load configuration if provided
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Get OpenAI API key
    openai_api_key = (
        args.openai_api_key or 
        config.get("openai_api_key") or 
        os.getenv("OPENAI_API_KEY")
    )
    
    if not openai_api_key:
        logger.error("OpenAI API key is required. Set OPENAI_API_KEY environment variable or use --openai-api-key")
        sys.exit(1)
    
    # Get other configuration
    host = config.get("host", args.host)
    port = config.get("port", args.port)
    registry_url = config.get("registry_url", args.registry_url)
    
    # Create and run service
    service = GptMDSagentService()
    
    try:
        asyncio.run(service.run(
            host=host,
            port=port,
            openai_api_key=openai_api_key,
            registry_url=registry_url
        ))
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error("Service failed", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
