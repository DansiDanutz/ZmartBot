#!/usr/bin/env python3
"""
Simple diagnostic test for Telegram and Airtable connectivity
Focuses on the core issue: why "Pengu Liquidation Map" wasn't processed
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.telegram_service import TelegramService
from src.services.airtable_service import AirtableService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleTelegramDiagnostic:
    """Simple diagnostic for Telegram and Airtable connectivity"""
    
    def __init__(self):
        self.telegram_service = TelegramService()
        self.airtable_service = AirtableService()
    
    async def run_diagnostic(self):
        """Run simple diagnostic"""
        logger.info("🔍 Starting simple diagnostic for Pengu Liquidation Map issue")
        
        results = {
            "telegram_connection": False,
            "telegram_config": False,
            "airtable_connection": False,
            "airtable_integration": False,
            "issues": []
        }
        
        # 1. Check Telegram Configuration
        logger.info("1. Checking Telegram configuration...")
        try:
            bot_token = self.telegram_service.bot_token
            chat_id = self.telegram_service.chat_id
            kingfisher_bot_id = self.telegram_service.kingfisher_bot_id
            
            logger.info(f"   Bot Token: {'✅ Set' if bot_token else '❌ Not set'}")
            logger.info(f"   Chat ID: {'✅ Set' if chat_id else '❌ Not set'}")
            logger.info(f"   KingFisher Bot ID: {kingfisher_bot_id}")
            logger.info(f"   Automation Enabled: {self.telegram_service.automation_enabled}")
            
            if bot_token and chat_id:
                results["telegram_config"] = True
                logger.info("✅ Telegram configuration looks good")
            else:
                results["issues"].append("Telegram configuration incomplete")
                logger.error("❌ Telegram configuration incomplete")
                
        except Exception as e:
            results["issues"].append(f"Configuration check error: {e}")
            logger.error(f"❌ Configuration check error: {e}")
        
        # 2. Test Telegram Connection
        logger.info("2. Testing Telegram connection...")
        try:
            telegram_connected = await self.telegram_service.initialize()
            if telegram_connected:
                results["telegram_connection"] = True
                logger.info("✅ Telegram connection successful")
            else:
                results["issues"].append("Telegram connection failed")
                logger.error("❌ Telegram connection failed")
        except Exception as e:
            results["issues"].append(f"Telegram connection error: {e}")
            logger.error(f"❌ Telegram connection error: {e}")
        
        # 3. Test Airtable Connection
        logger.info("3. Testing Airtable connection...")
        try:
            airtable_connected = await self.airtable_service.test_connection()
            if airtable_connected:
                results["airtable_connection"] = True
                logger.info("✅ Airtable connection successful")
            else:
                results["issues"].append("Airtable connection failed")
                logger.error("❌ Airtable connection failed")
        except Exception as e:
            results["issues"].append(f"Airtable connection error: {e}")
            logger.error(f"❌ Airtable connection error: {e}")
        
        # 4. Test Airtable Integration
        logger.info("4. Testing Airtable integration...")
        try:
            if results["airtable_connection"]:
                # Test storing a sample analysis
                sample_analysis = {
                    "symbol": "PENGUUSDT",
                    "liquidation_clusters": [{"price": 0.123, "size": 1000}],
                    "long_term_ratios": "24h: 65%, 48h: 70%",
                    "short_term_ratios": "24h: 35%, 48h: 30%",
                    "rsi_heatmap": "Bullish"
                }
                
                stored = await self.airtable_service.store_image_analysis(sample_analysis)
                if stored:
                    results["airtable_integration"] = True
                    logger.info("✅ Airtable integration successful")
                else:
                    results["issues"].append("Airtable integration failed")
                    logger.error("❌ Airtable integration failed")
            else:
                results["issues"].append("Cannot test Airtable integration - connection failed")
        except Exception as e:
            results["issues"].append(f"Airtable integration error: {e}")
            logger.error(f"❌ Airtable integration error: {e}")
        
        # 5. Check Server Status
        logger.info("5. Checking server status...")
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8100/health")
                if response.status_code == 200:
                    health_data = response.json()
                    logger.info(f"✅ Server healthy: {health_data.get('status', 'unknown')}")
                    logger.info(f"   Telegram service: {health_data.get('services', {}).get('telegram', False)}")
                else:
                    results["issues"].append("Server health check failed")
                    logger.error("❌ Server health check failed")
        except Exception as e:
            results["issues"].append(f"Server check error: {e}")
            logger.error(f"❌ Server check error: {e}")
        
        # 6. Summary
        logger.info("6. Diagnostic Summary:")
        logger.info("=" * 50)
        
        total_tests = len([k for k in results.keys() if k != "issues"])
        passed_tests = len([k for k in results.keys() if k != "issues" and results[k]])
        
        logger.info(f"📊 Tests Passed: {passed_tests}/{total_tests}")
        
        for test, result in results.items():
            if test != "issues":
                status = "✅ PASS" if result else "❌ FAIL"
                logger.info(f"   {test}: {status}")
        
        if results["issues"]:
            logger.info("\n🚨 Issues Found:")
            for issue in results["issues"]:
                logger.info(f"   • {issue}")
        else:
            logger.info("\n✅ No issues found!")
        
        # 7. Analysis of Pengu Issue
        logger.info("\n🔍 Analysis of 'Pengu Liquidation Map' Issue:")
        
        if not results["telegram_connection"]:
            logger.info("   • Telegram connection failed - images won't be detected")
            logger.info("   • Solution: Check bot token and chat ID configuration")
        
        if not results["telegram_config"]:
            logger.info("   • Telegram not configured - no monitoring possible")
            logger.info("   • Solution: Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        
        if not results["airtable_connection"]:
            logger.info("   • Airtable connection failed - analysis won't be stored")
            logger.info("   • Solution: Check Airtable API key and base configuration")
        
        if not results["airtable_integration"]:
            logger.info("   • Airtable integration failed - data won't be saved")
            logger.info("   • Solution: Check table structure and permissions")
        
        if all([results["telegram_connection"], results["airtable_connection"], results["airtable_integration"]]):
            logger.info("   • All services working - issue might be with image source")
            logger.info("   • Possible causes:")
            logger.info("     - Image not sent to monitored channel")
            logger.info("     - Image not from KingFisher bot")
            logger.info("     - Image format not supported")
            logger.info("     - Image processing failed")
        
        # 8. Recommendations
        logger.info("\n💡 Recommendations:")
        
        if not results["telegram_config"]:
            logger.info("   • Create .env file with Telegram configuration")
            logger.info("   • Copy from env.example and fill in your values")
        
        if not results["telegram_connection"]:
            logger.info("   • Verify bot token is valid")
            logger.info("   • Check if bot has necessary permissions")
            logger.info("   • Test bot manually in Telegram")
        
        if not results["airtable_connection"]:
            logger.info("   • Check Airtable API key in environment")
            logger.info("   • Verify base ID and table name")
            logger.info("   • Test Airtable API manually")
        
        logger.info("\n🎯 Next Steps:")
        logger.info("   1. Check if Pengu image was sent to the correct channel")
        logger.info("   2. Verify the image was from KingFisher bot")
        logger.info("   3. Test with a manual image upload")
        logger.info("   4. Check server logs for any error messages")
        logger.info("   5. Monitor real-time with: tail -f auto_monitor.log")
        
        return results

async def main():
    """Main function"""
    tester = SimpleTelegramDiagnostic()
    results = await tester.run_diagnostic()
    
    return results

if __name__ == "__main__":
    asyncio.run(main()) 