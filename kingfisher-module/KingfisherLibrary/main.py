#!/usr/bin/env python3
"""
KingfisherLibrary Main Module
Complete self-learning orchestration system
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from .orchestration.self_learning_orchestrator import SelfLearningKingOrchestrator
from .config.settings import KingfisherConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kingfisher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('KingfisherLibrary')


class KingfisherSystem:
    """Main Kingfisher System Controller"""
    
    def __init__(self, config_path: str = None):
        """Initialize Kingfisher System
        
        Args:
            config_path: Path to configuration file
        """
        self.config = KingfisherConfig(config_path)
        self.orchestrator = None
        self.is_running = False
        
    async def start(self, enable_ml: bool = True):
        """Start the Kingfisher system
        
        Args:
            enable_ml: Enable machine learning features
        """
        logger.info("Starting Kingfisher System...")
        logger.info(f"Version: 2.0.0")
        logger.info(f"ML Enabled: {enable_ml}")
        
        # Initialize orchestrator
        self.orchestrator = SelfLearningKingOrchestrator()
        self.orchestrator.optimization_enabled = enable_ml
        
        # Display startup banner
        self._display_banner()
        
        # Start orchestrator
        self.is_running = True
        try:
            await self.orchestrator.start()
        except KeyboardInterrupt:
            logger.info("Shutdown requested...")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the Kingfisher system"""
        if self.orchestrator:
            self.orchestrator.stop()
        self.is_running = False
        logger.info("Kingfisher System stopped")
    
    def _display_banner(self):
        """Display startup banner"""
        banner = """
        ╔══════════════════════════════════════════════════════════════╗
        ║                                                              ║
        ║     👑 KINGFISHER TRADING AUTOMATION SYSTEM v2.0 👑         ║
        ║                                                              ║
        ║     🧠 Self-Learning Orchestration Engine                   ║
        ║     📊 6-Step Automated Pipeline                            ║
        ║     🎯 ML-Optimized Execution                               ║
        ║     🔄 Real-time Pattern Recognition                        ║
        ║                                                              ║
        ║     API: http://localhost:5555                              ║
        ║     Dashboard: Open ml_orchestrator_dashboard.html          ║
        ║                                                              ║
        ╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    @staticmethod
    def run():
        """Run the Kingfisher system (entry point)"""
        system = KingfisherSystem()
        asyncio.run(system.start())


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kingfisher Trading Automation System')
    parser.add_argument('--no-ml', action='store_true', help='Disable ML features')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--version', action='version', version='2.0.0')
    
    args = parser.parse_args()
    
    system = KingfisherSystem(args.config)
    asyncio.run(system.start(enable_ml=not args.no_ml))


if __name__ == '__main__':
    main()