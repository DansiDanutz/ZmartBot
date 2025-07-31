#!/usr/bin/env python3
"""
KingFisher Auto-Monitor Script
Monitors system health and processes real symbols only (no test data)
"""

import asyncio
import httpx
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KingFisherAutoMonitor:
    def __init__(self):
        self.base_url = "http://localhost:8100"
        self.last_check_time = datetime.now()
        self.processed_images = set()
        self.monitoring_active = True
        
    async def check_server_health(self) -> bool:
        """Check if KingFisher server is running"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Server healthy: {data.get('status', 'unknown')}")
                    return True
                else:
                    logger.error(f"❌ Server unhealthy: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to server: {e}")
            return False
    
    async def check_airtable_connection(self) -> bool:
        """Check Airtable connection status"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/v1/airtable/status")
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    logger.info(f"📊 Airtable status: {status}")
                    return status == 'connected'
                else:
                    logger.error(f"❌ Airtable connection failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Cannot check Airtable: {e}")
            return False
    
    async def get_recent_analyses(self) -> List[Dict]:
        """Get recent analyses from Airtable"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/v1/airtable/analyses")
                if response.status_code == 200:
                    data = response.json()
                    return data.get('analyses', [])
                else:
                    logger.error(f"❌ Failed to get analyses: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"❌ Error getting analyses: {e}")
            return []
    
    async def monitor_loop(self):
        """Main monitoring loop - only monitors system health"""
        logger.info("🚀 Starting KingFisher Auto-Monitor...")
        logger.info("📊 Monitoring system health every 30 seconds")
        logger.info("⚠️  NO TEST SYMBOLS - Waiting for real Telegram input")
        
        while self.monitoring_active:
            try:
                # Check server health
                server_healthy = await self.check_server_health()
                if not server_healthy:
                    logger.warning("⚠️ Server not healthy, waiting 30 seconds...")
                    await asyncio.sleep(30)
                    continue
                
                # Check Airtable connection
                airtable_connected = await self.check_airtable_connection()
                if not airtable_connected:
                    logger.warning("⚠️ Airtable not connected, waiting 30 seconds...")
                    await asyncio.sleep(30)
                    continue
                
                # Get recent analyses to show activity
                analyses = await self.get_recent_analyses()
                if analyses:
                    logger.info(f"📈 Found {len(analyses)} recent analyses in Airtable")
                    # Show last 3 symbols processed
                    recent_symbols = [a.get('Symbol', 'Unknown') for a in analyses[:3]]
                    logger.info(f"🎯 Recent symbols: {', '.join(recent_symbols)}")
                else:
                    logger.info("📭 No recent analyses found")
                
                logger.info("✅ System healthy - Ready for real symbol processing")
                logger.info("💡 To process a symbol, use: curl -X POST http://localhost:8100/api/v1/enhanced-analysis/process-kingfisher-image ...")
                
                # Wait 30 seconds before next check
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("🛑 Auto-monitor stopped by user")
                self.monitoring_active = False
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def run_continuous_monitoring(self):
        """Run continuous monitoring with error handling"""
        while self.monitoring_active:
            try:
                await self.monitor_loop()
            except Exception as e:
                logger.error(f"❌ Critical error in monitoring: {e}")
                logger.info("🔄 Restarting monitor in 60 seconds...")
                await asyncio.sleep(60)

async def main():
    """Main function"""
    monitor = KingFisherAutoMonitor()
    
    print("=" * 60)
    print("🎯 KingFisher Auto-Monitor")
    print("=" * 60)
    print("📊 Monitoring system health every 30 seconds")
    print("⚠️  NO TEST SYMBOLS - Only real Telegram input processed")
    print("📝 Logs saved to: auto_monitor.log")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        await monitor.run_continuous_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Auto-monitor stopped")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 