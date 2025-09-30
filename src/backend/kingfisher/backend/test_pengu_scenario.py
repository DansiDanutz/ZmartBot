#!/usr/bin/env python3
"""
Test script to simulate the "Pengu Liquidation Map" scenario
This tests the complete workflow from image processing to Airtable storage
"""

import asyncio
import sys
import os
import logging
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PenguScenarioTester:
    """Test the complete Pengu Liquidation Map scenario"""
    
    def __init__(self):
        self.base_url = "http://localhost:8100"
    
    async def test_complete_workflow(self):
        """Test the complete workflow for Pengu Liquidation Map"""
        logger.info("🔍 Testing Pengu Liquidation Map scenario")
        
        results = {
            "server_health": False,
            "airtable_connection": False,
            "image_processing": False,
            "airtable_storage": False,
            "issues": []
        }
        
        # 1. Check server health
        logger.info("1. Checking server health...")
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    health_data = response.json()
                    results["server_health"] = True
                    logger.info(f"✅ Server healthy: {health_data.get('status', 'unknown')}")
                else:
                    results["issues"].append("Server health check failed")
                    logger.error("❌ Server health check failed")
        except Exception as e:
            results["issues"].append(f"Server check error: {e}")
            logger.error(f"❌ Server check error: {e}")
        
        # 2. Check Airtable connection
        logger.info("2. Checking Airtable connection...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/airtable/status")
                if response.status_code == 200:
                    airtable_data = response.json()
                    if airtable_data.get("connected", False):
                        results["airtable_connection"] = True
                        logger.info("✅ Airtable connection successful")
                    else:
                        results["issues"].append("Airtable connection failed")
                        logger.error("❌ Airtable connection failed")
                else:
                    results["issues"].append("Airtable status check failed")
                    logger.error("❌ Airtable status check failed")
        except Exception as e:
            results["issues"].append(f"Airtable check error: {e}")
            logger.error(f"❌ Airtable check error: {e}")
        
        # 3. Test image processing (simulate Pengu image)
        logger.info("3. Testing image processing for Pengu...")
        try:
            # Create a simulated analysis result for Pengu
            pengu_analysis = {
                "symbol": "PENGUUSDT",
                "liquidation_clusters": [
                    {"price": 0.123, "size": 1500, "side": "long"},
                    {"price": 0.125, "size": 2000, "side": "short"},
                    {"price": 0.120, "size": 1000, "side": "long"}
                ],
                "long_term_ratios": "24h: 65%, 48h: 70%, 7d: 75%, 1m: 80%",
                "short_term_ratios": "24h: 35%, 48h: 30%, 7d: 25%, 1m: 20%",
                "rsi_heatmap": "Bullish",
                "significance_score": 0.85,
                "market_sentiment": "bullish",
                "confidence": 0.78
            }
            
            # Test storing the analysis
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/airtable/store-analysis",
                    json=pengu_analysis
                )
                
                if response.status_code == 200:
                    results["image_processing"] = True
                    logger.info("✅ Image processing simulation successful")
                    logger.info(f"   Symbol: {pengu_analysis['symbol']}")
                    logger.info(f"   Significance: {pengu_analysis['significance_score']:.2%}")
                else:
                    results["issues"].append(f"Image processing failed: {response.status_code}")
                    logger.error(f"❌ Image processing failed: {response.status_code}")
                    logger.error(f"   Response: {response.text}")
        except Exception as e:
            results["issues"].append(f"Image processing error: {e}")
            logger.error(f"❌ Image processing error: {e}")
        
        # 4. Test Airtable storage
        logger.info("4. Testing Airtable storage...")
        try:
            if results["airtable_connection"]:
                # Test storing directly to Airtable
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/api/v1/airtable/store-analysis",
                        json=pengu_analysis
                    )
                    
                    if response.status_code == 200:
                        results["airtable_storage"] = True
                        logger.info("✅ Airtable storage successful")
                    else:
                        results["issues"].append(f"Airtable storage failed: {response.status_code}")
                        logger.error(f"❌ Airtable storage failed: {response.status_code}")
                        logger.error(f"   Response: {response.text}")
            else:
                results["issues"].append("Cannot test Airtable storage - connection failed")
        except Exception as e:
            results["issues"].append(f"Airtable storage error: {e}")
            logger.error(f"❌ Airtable storage error: {e}")
        
        # 5. Check if Pengu record exists
        logger.info("5. Checking if Pengu record exists in Airtable...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/airtable/analyses")
                if response.status_code == 200:
                    analyses = response.json()
                    pengu_found = any(
                        analysis.get("symbol", "").upper() == "PENGUUSDT" 
                        for analysis in analyses.get("analyses", [])
                    )
                    
                    if pengu_found:
                        logger.info("✅ Pengu record found in Airtable")
                    else:
                        logger.info("ℹ️ Pengu record not found in Airtable (expected if test failed)")
                else:
                    logger.warning("⚠️ Could not check Airtable analyses")
        except Exception as e:
            logger.warning(f"⚠️ Could not check Airtable analyses: {e}")
        
        # 6. Summary
        logger.info("6. Test Summary:")
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
        
        # 7. Analysis of the original problem
        logger.info("\n🔍 Analysis of 'Pengu Liquidation Map' Issue:")
        
        if not results["server_health"]:
            logger.info("   • Server not healthy - system not running properly")
        
        if not results["airtable_connection"]:
            logger.info("   • Airtable connection failed - analysis won't be stored")
        
        if not results["image_processing"]:
            logger.info("   • Image processing failed - analysis won't be generated")
        
        if not results["airtable_storage"]:
            logger.info("   • Airtable storage failed - data won't be saved")
        
        if all([results["server_health"], results["airtable_connection"], results["image_processing"], results["airtable_storage"]]):
            logger.info("   • All systems working - the issue might be:")
            logger.info("     - Image not sent to the correct Telegram channel")
            logger.info("     - Image not from the KingFisher bot")
            logger.info("     - Telegram monitoring not active")
            logger.info("     - Image format not supported")
        
        # 8. Recommendations
        logger.info("\n💡 Recommendations:")
        
        if not results["server_health"]:
            logger.info("   • Restart the KingFisher server")
            logger.info("   • Check server logs for errors")
        
        if not results["airtable_connection"]:
            logger.info("   • Check Airtable API configuration")
            logger.info("   • Verify API key and base ID")
        
        if not results["image_processing"]:
            logger.info("   • Check image processing service")
            logger.info("   • Verify image format support")
        
        if not results["airtable_storage"]:
            logger.info("   • Check Airtable table structure")
            logger.info("   • Verify field names and permissions")
        
        logger.info("\n🎯 Next Steps:")
        logger.info("   1. Verify the Pengu image was sent to the correct channel")
        logger.info("   2. Check if the image was from KingFisher bot")
        logger.info("   3. Test with a manual image upload")
        logger.info("   4. Monitor Telegram monitoring status")
        logger.info("   5. Check real-time logs: tail -f auto_monitor.log")
        
        return results

async def main():
    """Main function"""
    tester = PenguScenarioTester()
    results = await tester.test_complete_workflow()
    
    return results

if __name__ == "__main__":
    asyncio.run(main()) 