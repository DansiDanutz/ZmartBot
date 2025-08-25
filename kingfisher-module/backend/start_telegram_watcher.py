#!/usr/bin/env python3
"""
Start the Telegram Watcher for KingFisher
Monitors Telegram channels for KingFisher images using user account
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.telegram_watcher_service import TelegramWatcherService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to run the Telegram watcher"""
    
    print("="*60)
    print("🚀 KINGFISHER TELEGRAM WATCHER")
    print("="*60)
    print("📱 Using Telethon (MTProto) for user account access")
    print("👀 Monitoring configured Telegram chats/channels")
    print("🎯 Auto-detecting and processing KingFisher images")
    print("📊 Storing results in correct Airtable fields")
    print("="*60)
    
    # Create watcher instance
    watcher = TelegramWatcherService()
    
    try:
        # Start watching
        await watcher.start()
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopping watcher...")
        await watcher.stop()
        print("✅ Watcher stopped gracefully")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await watcher.stop()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())