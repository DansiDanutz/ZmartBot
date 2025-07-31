#!/usr/bin/env python3
"""
Simple Airtable New Symbol Test
Tests adding a new symbol to Airtable with basic fields only
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

class SimpleAirtableNewSymbolTester:
    def __init__(self):
        self.airtable_service = AirtableService()
        self.test_symbol = "DOTUSDT"  # Using DOT as test symbol
        
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
    
    async def test_get_existing_records(self):
        """Test getting existing records"""
        logger.info("📊 Testing get recent analyses...")
        try:
            records = await self.airtable_service.get_recent_analyses(limit=5)
            logger.info(f"✅ Retrieved {len(records)} existing records")
            
            # Show some sample data
            if records:
                logger.info("📋 Sample records:")
                for i, record in enumerate(records[:3]):
                    if 'fields' in record:
                        symbol = record['fields'].get('Symbol', 'Unknown')
                        logger.info(f"   {i+1}. Symbol: {symbol}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Error getting records: {e}")
            return False
    
    async def test_create_simple_record(self):
        """Test creating a simple record with minimal fields"""
        logger.info(f"🆕 Creating simple record for {self.test_symbol}...")
        
        # Use only basic fields that are known to work
        analysis_data = {
            "symbol": self.test_symbol,
            "liquidation_clusters": [
                {"price": 6.50, "volume": 500000, "side": "long"},
                {"price": 6.80, "volume": 400000, "side": "short"}
            ],
            "long_term_ratios": "70.0% long, 65.0% short",
            "short_term_ratios": "68.0% long, 62.0% short",
            "rsi_heatmap": "Neutral RSI pattern"
        }
        
        try:
            result = await self.airtable_service.store_image_analysis(analysis_data)
            if result:
                logger.info(f"✅ Successfully created record for {self.test_symbol}")
                return True
            else:
                logger.error(f"❌ Failed to create record for {self.test_symbol}")
                return False
        except Exception as e:
            logger.error(f"❌ Error creating record: {e}")
            return False
    
    async def test_verify_record_created(self):
        """Verify the record was created"""
        logger.info(f"🔍 Verifying record for {self.test_symbol}...")
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
                return True
            else:
                logger.error("❌ New record not found")
                return False
        except Exception as e:
            logger.error(f"❌ Error verifying record: {e}")
            return False
    
    async def test_complete_workflow(self):
        """Run the complete simple workflow"""
        logger.info("🚀 Starting simple new symbol workflow test...")
        
        results = {
            "connection": False,
            "get_records": False,
            "create_record": False,
            "verify_record": False
        }
        
        # Step 1: Test connection
        logger.info("=" * 80)
        logger.info("STEP 1: Testing Airtable Connection")
        logger.info("=" * 80)
        results["connection"] = await self.test_airtable_connection()
        
        if not results["connection"]:
            logger.error("❌ Cannot proceed without Airtable connection")
            return results
        
        # Step 2: Get existing records
        logger.info("=" * 80)
        logger.info("STEP 2: Getting Existing Records")
        logger.info("=" * 80)
        results["get_records"] = await self.test_get_existing_records()
        
        # Step 3: Create new record
        logger.info("=" * 80)
        logger.info("STEP 3: Creating New Symbol Record")
        logger.info("=" * 80)
        results["create_record"] = await self.test_create_simple_record()
        
        if not results["create_record"]:
            logger.error("❌ Cannot proceed without creating record")
            return results
        
        # Step 4: Verify new record
        logger.info("=" * 80)
        logger.info("STEP 4: Verifying New Record")
        logger.info("=" * 80)
        results["verify_record"] = await self.test_verify_record_created()
        
        return results
    
    def print_summary(self, results):
        """Print test summary"""
        logger.info("=" * 80)
        logger.info("🎯 SIMPLE NEW SYMBOL AIRTABLE TEST SUMMARY")
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
            logger.info("\n🎉 ALL TESTS PASSED! Simple new symbol workflow is working!")
        else:
            logger.info(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please check the logs above.")
        
        logger.info("=" * 80)

async def main():
    """Main test function"""
    logger.info("🚀 Starting Simple Airtable New Symbol Test")
    logger.info("=" * 80)
    
    tester = SimpleAirtableNewSymbolTester()
    
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
        logger.info("🎯 Simple Airtable New Symbol Test completed successfully!")
    else:
        logger.error("❌ Simple Airtable New Symbol Test failed!") 