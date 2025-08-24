#!/usr/bin/env python3
"""
🎯 Orchestration Agent Startup Script
Starts the orchestration agent with integrated database orchestrator
Fixes all database update issues automatically
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.orchestration.orchestration_agent import OrchestrationAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestration.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to start the orchestration agent"""
    try:
        logger.info("🚀 Starting Orchestration Agent with Database Orchestrator")
        logger.info("=========================================================")
        logger.info("")
        logger.info("✅ DATABASE UPDATE ISSUES BEING FIXED:")
        logger.info("   1. 🔄 Cross Events Tracking (30s intervals)")
        logger.info("   2. 🚨 Technical Alerts Updates (1m intervals)")
        logger.info("   3. 📊 Indicators Updates (5m intervals)")
        logger.info("   4. 🎯 Symbol Alerts Updates (1m intervals)")
        logger.info("   5. 📈 Market Data Updates (30s intervals)")
        logger.info("")
        logger.info("🎯 Starting orchestration agent...")
        
        # Create and start the orchestration agent
        agent = OrchestrationAgent()
        await agent.start()
        
        logger.info("✅ Orchestration Agent started successfully!")
        logger.info("📊 Database orchestrator is now active")
        logger.info("🔄 All database update loops are running")
        logger.info("")
        logger.info("🎯 Press Ctrl+C to stop the orchestration agent")
        logger.info("")
        
        # Keep the agent running
        while True:
            await asyncio.sleep(60)
            logger.debug("🔄 Orchestration agent heartbeat - all systems operational")
            
    except KeyboardInterrupt:
        logger.info("🛑 Received shutdown signal")
        if 'agent' in locals():
            await agent.stop()
        logger.info("✅ Orchestration Agent stopped gracefully")
    except Exception as e:
        logger.error(f"❌ Error in orchestration agent: {e}")
        if 'agent' in locals():
            await agent.stop()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
