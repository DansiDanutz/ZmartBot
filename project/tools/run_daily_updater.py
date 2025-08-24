#!/usr/bin/env python3
"""
Daily Price Updater Runner
Standalone script to run daily price updates
Can be scheduled with cron or systemd
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.daily_price_updater import get_daily_updater

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/dansidanutz/Desktop/ZmartBot/Symbol_Price_history_data/logs/daily_updater.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to run daily update"""
    try:
        logger.info("🌅 Starting daily price updater...")
        
        # Get the updater
        updater = await get_daily_updater()
        
        # Run the daily update
        await updater.run_daily_update()
        
        logger.info("✅ Daily price updater completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Daily price updater failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
