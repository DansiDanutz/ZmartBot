#!/usr/bin/env python3
"""
Test script to diagnose Telegram image processing issue
Specifically for the "Pengu Liquidation Map" problem
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.telegram_service import TelegramService
from src.services.image_processing_service import ImageProcessingService
from src.services.airtable_service import AirtableService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramDiagnosticTester:
    """Diagnostic tester for Telegram image processing"""
    
    def __init__(self):
        self.telegram_service = TelegramService()
        self.image_processor = ImageProcessingService()
        self.airtable_service = AirtableService()
    
    async def run_diagnostic(self):
        """Run comprehensive diagnostic"""
        logger.info("🔍 Starting Telegram diagnostic for Pengu Liquidation Map issue")
        
        results = {
            "telegram_connection": False,
            "telegram_monitoring": False,
            "image_processing": False,
            "airtable_connection": False,
            "airtable_integration": False,
            "issues": []
        }
        
        # 1. Test Telegram Connection
        logger.info("1. Testing Telegram connection...")
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
        
        # 2. Test Telegram Monitoring
        logger.info("2. Testing Telegram monitoring...")
        try:
            if results["telegram_connection"]:
                monitoring_started = await self.telegram_service.start_monitoring()
                if monitoring_started:
                    results["telegram_monitoring"] = True
                    logger.info("✅ Telegram monitoring started")
                else:
                    results["issues"].append("Telegram monitoring failed to start")
                    logger.error("❌ Telegram monitoring failed to start")
            else:
                results["issues"].append("Cannot test monitoring - Telegram not connected")
        except Exception as e:
            results["issues"].append(f"Telegram monitoring error: {e}")
            logger.error(f"❌ Telegram monitoring error: {e}")
        
        # 3. Test Image Processing
        logger.info("3. Testing image processing...")
        try:
            # Create a test image path (you can replace this with an actual image)
            test_image_path = "test_images/sample_liquidation_map.jpg"
            
            if os.path.exists(test_image_path):
                analysis_result = await self.image_processor.process_image(test_image_path)
                if analysis_result:
                    results["image_processing"] = True
                    logger.info("✅ Image processing successful")
                    logger.info(f"   Analysis result: {analysis_result.get('symbol', 'Unknown')}")
                else:
                    results["issues"].append("Image processing returned no result")
                    logger.error("❌ Image processing returned no result")
            else:
                results["issues"].append(f"Test image not found: {test_image_path}")
                logger.warning(f"⚠️ Test image not found: {test_image_path}")
        except Exception as e:
            results["issues"].append(f"Image processing error: {e}")
            logger.error(f"❌ Image processing error: {e}")
        
        # 4. Test Airtable Connection
        logger.info("4. Testing Airtable connection...")
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
        
        # 5. Test Airtable Integration
        logger.info("5. Testing Airtable integration...")
        try:
            if results["airtable_connection"] and results["image_processing"]:
                # Test storing a sample analysis
                sample_analysis = {
                    "symbol": "PENGUUSDT",
                    "liquidation_clusters": [{"price": 0.123, "size": 1000}],
                    "long_term_ratios": "24h: 65%, 48h: 70%",
                    "short_term_ratios": "24h: 35%, 48h: 30%",
                    "rsi_heatmap": "Bullish",
                    "significance_score": 0.8
                }
                
                stored = await self.airtable_service.store_image_analysis(sample_analysis)
                if stored:
                    results["airtable_integration"] = True
                    logger.info("✅ Airtable integration successful")
                else:
                    results["issues"].append("Airtable integration failed")
                    logger.error("❌ Airtable integration failed")
            else:
                results["issues"].append("Cannot test Airtable integration - prerequisites not met")
        except Exception as e:
            results["issues"].append(f"Airtable integration error: {e}")
            logger.error(f"❌ Airtable integration error: {e}")
        
        # 6. Check Telegram Configuration
        logger.info("6. Checking Telegram configuration...")
        try:
            bot_token = self.telegram_service.bot_token
            chat_id = self.telegram_service.chat_id
            kingfisher_bot_id = self.telegram_service.kingfisher_bot_id
            
            logger.info(f"   Bot Token: {'✅ Set' if bot_token else '❌ Not set'}")
            logger.info(f"   Chat ID: {'✅ Set' if chat_id else '❌ Not set'}")
            logger.info(f"   KingFisher Bot ID: {kingfisher_bot_id}")
            logger.info(f"   Automation Enabled: {self.telegram_service.automation_enabled}")
            logger.info(f"   Monitoring Active: {self.telegram_service.monitoring_active}")
            
            if not bot_token or not chat_id:
                results["issues"].append("Telegram configuration incomplete")
                
        except Exception as e:
            results["issues"].append(f"Configuration check error: {e}")
            logger.error(f"❌ Configuration check error: {e}")
        
        # 7. Summary
        logger.info("7. Diagnostic Summary:")
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
        
        # 8. Recommendations
        logger.info("\n💡 Recommendations:")
        
        if not results["telegram_connection"]:
            logger.info("   • Check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
            logger.info("   • Verify bot token is valid and bot has necessary permissions")
        
        if not results["telegram_monitoring"]:
            logger.info("   • Check if KingFisher bot is sending messages to the monitored channel")
            logger.info("   • Verify the bot ID and channel configuration")
        
        if not results["image_processing"]:
            logger.info("   • Ensure image processing service is properly configured")
            logger.info("   • Check if test images are available")
        
        if not results["airtable_connection"]:
            logger.info("   • Check Airtable API key and base configuration")
            logger.info("   • Verify network connectivity to Airtable")
        
        if not results["airtable_integration"]:
            logger.info("   • Check Airtable table structure and field names")
            logger.info("   • Verify permissions for creating/updating records")
        
        logger.info("\n🎯 Next Steps:")
        logger.info("   1. If Telegram connection fails: Check environment variables")
        logger.info("   2. If monitoring fails: Verify the KingFisher bot is active")
        logger.info("   3. If image processing fails: Check image format and processing service")
        logger.info("   4. If Airtable fails: Check API key and table configuration")
        logger.info("   5. Test with a real image: curl -X POST http://localhost:8100/api/v1/images/process")
        
        return results

async def main():
    """Main function"""
    tester = TelegramDiagnosticTester()
    results = await tester.run_diagnostic()
    
    # Return results for potential further processing
    return results

if __name__ == "__main__":
    asyncio.run(main()) 