#!/usr/bin/env python3
"""
Real Airtable New Symbol Test
Tests the complete workflow for adding a new symbol to Airtable
"""

import asyncio
import sys
import os
from datetime import datetime
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.airtable_service import AirtableService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealAirtableNewSymbolTester:
    def __init__(self):
        self.airtable_service = AirtableService()
        self.test_symbol = "AVAXUSDT"  # Using AVAX as test symbol
        
    async def test_airtable_connection(self):
        """Test Airtable connection"""
        logger.info("🔗 Testing Airtable connection...")
        try:
            connection_result = await self.airtable_service.test_connection()
            if connection_result:
                logger.info("✅ Airtable connection successful")
                return True
            else:
                logger.error("❌ Airtable connection failed")
                return False
        except Exception as e:
            logger.error(f"❌ Airtable connection error: {e}")
            return False
    
    async def test_symbol_exists(self):
        """Check if test symbol exists in Airtable"""
        logger.info(f"🔍 Checking if {self.test_symbol} exists in Airtable...")
        try:
            # Get all records to check for symbol
            records = await self.airtable_service.get_recent_analyses(limit=100)
            
            symbol_exists = False
            for record in records:
                if 'fields' in record and 'Symbol' in record['fields']:
                    if record['fields']['Symbol'] == self.test_symbol:
                        symbol_exists = True
                        logger.info(f"✅ Symbol {self.test_symbol} already exists in Airtable")
                        break
            
            if not symbol_exists:
                logger.info(f"🆕 Symbol {self.test_symbol} does not exist - ready to create")
            
            return symbol_exists
        except Exception as e:
            logger.error(f"❌ Error checking symbol existence: {e}")
            return False
    
    async def test_create_new_symbol_record(self):
        """Test creating a new symbol record using store_image_analysis"""
        logger.info(f"🆕 Creating new symbol record for {self.test_symbol}...")
        
        # Simulate analysis data using the correct format
        analysis_data = {
            "symbol": self.test_symbol,
            "liquidation_clusters": [
                {"price": 182.00, "volume": 1500000, "side": "long"},
                {"price": 188.50, "volume": 1200000, "side": "short"},
                {"price": 179.25, "volume": 800000, "side": "long"},
                {"price": 192.00, "volume": 900000, "side": "short"}
            ],
            "long_term_ratios": "75.5% long, 68.2% short",
            "short_term_ratios": "72.1% long, 65.8% short",
            "rsi_heatmap": "Bullish RSI pattern detected",
            "lie_heatmap": "Strong liquidation clusters identified",
            "summary": f"Professional analysis for {self.test_symbol} - Strong bullish momentum with clear liquidation clusters identified."
        }
        
        try:
            # Create new record using store_image_analysis
            result = await self.airtable_service.store_image_analysis(analysis_data)
            if result:
                logger.info(f"✅ Successfully created new record for {self.test_symbol}")
                return True
            else:
                logger.error(f"❌ Failed to create record for {self.test_symbol}")
                return False
        except Exception as e:
            logger.error(f"❌ Error creating record: {e}")
            return False
    
    async def test_create_symbol_summary(self):
        """Test creating a symbol summary"""
        logger.info(f"📊 Creating symbol summary for {self.test_symbol}...")
        
        summary_data = {
            "symbol": self.test_symbol,
            "last_update": datetime.now().isoformat(),
            "total_images": 3,
            "average_significance": 8.5,
            "dominant_sentiment": "Bullish",
            "high_significance_count": 2,
            "recent_trend": "Strong upward momentum",
            "risk_level": "Medium",
            "latest_analysis_id": f"analysis_{self.test_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        try:
            result = await self.airtable_service.store_symbol_summary(summary_data)
            if result:
                logger.info(f"✅ Successfully created summary for {self.test_symbol}")
                return True
            else:
                logger.error(f"❌ Failed to create summary for {self.test_symbol}")
                return False
        except Exception as e:
            logger.error(f"❌ Error creating summary: {e}")
            return False
    
    async def test_verify_new_record(self):
        """Verify the newly created record"""
        logger.info(f"🔍 Verifying new record for {self.test_symbol}...")
        try:
            records = await self.airtable_service.get_recent_analyses(limit=10)
            
            new_record = None
            for record in records:
                if 'fields' in record and 'Symbol' in record['fields']:
                    if record['fields']['Symbol'] == self.test_symbol:
                        new_record = record
                        break
            
            if new_record:
                logger.info("✅ New record verified successfully")
                logger.info(f"📊 Record ID: {new_record.get('id', 'N/A')}")
                logger.info(f"📈 Symbol: {new_record['fields'].get('Symbol', 'N/A')}")
                logger.info(f"📅 Timestamp: {new_record.get('createdTime', 'N/A')}")
                return True
            else:
                logger.error("❌ New record not found")
                return False
        except Exception as e:
            logger.error(f"❌ Error verifying record: {e}")
            return False
    
    async def test_get_symbol_summaries(self):
        """Test getting symbol summaries"""
        logger.info("📊 Testing get symbol summaries...")
        try:
            summaries = await self.airtable_service.get_symbol_summaries()
            if summaries:
                logger.info(f"✅ Retrieved {len(summaries)} symbol summaries")
                return True
            else:
                logger.info("ℹ️ No symbol summaries found")
                return True  # Not an error, just no data
        except Exception as e:
            logger.error(f"❌ Error getting symbol summaries: {e}")
            return False
    
    async def test_complete_workflow(self):
        """Run the complete new symbol workflow"""
        logger.info("🚀 Starting complete new symbol workflow test...")
        
        results = {
            "connection": False,
            "symbol_check": False,
            "create_record": False,
            "create_summary": False,
            "verify_record": False,
            "get_summaries": False
        }
        
        # Step 1: Test connection
        logger.info("=" * 80)
        logger.info("STEP 1: Testing Airtable Connection")
        logger.info("=" * 80)
        results["connection"] = await self.test_airtable_connection()
        
        if not results["connection"]:
            logger.error("❌ Cannot proceed without Airtable connection")
            return results
        
        # Step 2: Check if symbol exists
        logger.info("=" * 80)
        logger.info("STEP 2: Checking Symbol Existence")
        logger.info("=" * 80)
        results["symbol_check"] = await self.test_symbol_exists()
        
        # Step 3: Create new record
        logger.info("=" * 80)
        logger.info("STEP 3: Creating New Symbol Record")
        logger.info("=" * 80)
        results["create_record"] = await self.test_create_new_symbol_record()
        
        if not results["create_record"]:
            logger.error("❌ Cannot proceed without creating record")
            return results
        
        # Step 4: Create symbol summary
        logger.info("=" * 80)
        logger.info("STEP 4: Creating Symbol Summary")
        logger.info("=" * 80)
        results["create_summary"] = await self.test_create_symbol_summary()
        
        # Step 5: Verify new record
        logger.info("=" * 80)
        logger.info("STEP 5: Verifying New Record")
        logger.info("=" * 80)
        results["verify_record"] = await self.test_verify_new_record()
        
        # Step 6: Test getting summaries
        logger.info("=" * 80)
        logger.info("STEP 6: Testing Get Symbol Summaries")
        logger.info("=" * 80)
        results["get_summaries"] = await self.test_get_symbol_summaries()
        
        return results
    
    def print_summary(self, results):
        """Print test summary"""
        logger.info("=" * 80)
        logger.info("🎯 NEW SYMBOL AIRTABLE WORKFLOW TEST SUMMARY")
        logger.info("=" * 80)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        logger.info(f"📊 Test Symbol: {self.test_symbol}")
        logger.info(f"📈 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {total_tests - passed_tests}")
        logger.info(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        logger.info("\n📋 Detailed Results:")
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        if passed_tests == total_tests:
            logger.info("\n🎉 ALL TESTS PASSED! New symbol workflow is working perfectly!")
        else:
            logger.info(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please check the logs above.")
        
        logger.info("=" * 80)

async def main():
    """Main test function"""
    logger.info("🚀 Starting Real Airtable New Symbol Test")
    logger.info("=" * 80)
    
    tester = RealAirtableNewSymbolTester()
    
    try:
        # Run complete workflow
        results = await tester.test_complete_workflow()
        
        # Print summary
        tester.print_summary(results)
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        logger.info("🎯 Real Airtable New Symbol Test completed successfully!")
    else:
        logger.error("❌ Real Airtable New Symbol Test failed!") 