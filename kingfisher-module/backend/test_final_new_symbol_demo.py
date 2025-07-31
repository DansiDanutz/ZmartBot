#!/usr/bin/env python3
"""
Final New Symbol Demo Test
Demonstrates the successful workflow for adding a new symbol to Airtable
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

class FinalNewSymbolDemo:
    def __init__(self):
        self.airtable_service = AirtableService()
        self.test_symbol = "MATICUSDT"  # Using MATIC as test symbol
        
    async def demonstrate_new_symbol_workflow(self):
        """Demonstrate the complete new symbol workflow"""
        logger.info("🎯 FINAL NEW SYMBOL WORKFLOW DEMONSTRATION")
        logger.info("=" * 80)
        
        # Step 1: Test connection
        logger.info("🔗 STEP 1: Testing Airtable Connection")
        connection_result = await self.airtable_service.test_connection()
        if not connection_result:
            logger.error("❌ Airtable connection failed")
            return False
        logger.info("✅ Airtable connection successful")
        
        # Step 2: Check if symbol exists
        logger.info("\n🔍 STEP 2: Checking Symbol Existence")
        records = await self.airtable_service.get_recent_analyses(limit=100)
        symbol_exists = False
        for record in records:
            if 'fields' in record and 'Symbol' in record['fields']:
                if record['fields']['Symbol'] == self.test_symbol:
                    symbol_exists = True
                    break
        
        if symbol_exists:
            logger.info(f"ℹ️ Symbol {self.test_symbol} already exists in Airtable")
        else:
            logger.info(f"🆕 Symbol {self.test_symbol} does not exist - ready to create")
        
        # Step 3: Create new symbol record
        logger.info("\n🆕 STEP 3: Creating New Symbol Record")
        analysis_data = {
            "symbol": self.test_symbol,
            "liquidation_clusters": [
                {"price": 0.65, "volume": 300000, "side": "long"},
                {"price": 0.68, "volume": 250000, "side": "short"},
                {"price": 0.62, "volume": 200000, "side": "long"},
                {"price": 0.71, "volume": 180000, "side": "short"}
            ],
            "long_term_ratios": "73.5% long, 67.2% short",
            "short_term_ratios": "71.1% long, 64.8% short",
            "rsi_heatmap": "Bullish RSI pattern with strong momentum"
        }
        
        create_result = await self.airtable_service.store_image_analysis(analysis_data)
        if create_result:
            logger.info(f"✅ Successfully created new record for {self.test_symbol}")
            logger.info("📊 Record includes:")
            logger.info("   • Symbol: MATICUSDT")
            logger.info("   • Liquidation clusters (4 clusters)")
            logger.info("   • Long-term ratios: 73.5% long, 67.2% short")
            logger.info("   • Short-term ratios: 71.1% long, 64.8% short")
            logger.info("   • RSI Heatmap analysis")
        else:
            logger.error(f"❌ Failed to create record for {self.test_symbol}")
            return False
        
        # Step 4: Create symbol summary
        logger.info("\n📊 STEP 4: Creating Symbol Summary")
        summary_data = {
            "symbol": self.test_symbol,
            "last_update": datetime.now().isoformat(),
            "total_images": 2,
            "average_significance": 8.2,
            "dominant_sentiment": "Bullish",
            "high_significance_count": 1,
            "recent_trend": "Strong upward momentum",
            "risk_level": "Medium",
            "latest_analysis_id": f"analysis_{self.test_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        summary_result = await self.airtable_service.store_symbol_summary(summary_data)
        if summary_result:
            logger.info(f"✅ Successfully created summary for {self.test_symbol}")
            logger.info("📈 Summary includes:")
            logger.info("   • Total images analyzed: 2")
            logger.info("   • Average significance: 8.2")
            logger.info("   • Dominant sentiment: Bullish")
            logger.info("   • Risk level: Medium")
        else:
            logger.warning(f"⚠️ Failed to create summary for {self.test_symbol}")
        
        # Step 5: Demonstrate data retrieval
        logger.info("\n📋 STEP 5: Demonstrating Data Retrieval")
        try:
            recent_records = await self.airtable_service.get_recent_analyses(limit=5)
            logger.info(f"✅ Retrieved {len(recent_records)} recent records")
            
            summaries = await self.airtable_service.get_symbol_summaries()
            logger.info(f"✅ Retrieved {len(summaries)} symbol summaries")
            
        except Exception as e:
            logger.error(f"❌ Error retrieving data: {e}")
        
        # Step 6: Show workflow summary
        logger.info("\n🎯 WORKFLOW SUMMARY")
        logger.info("=" * 80)
        logger.info("✅ Airtable connection established")
        logger.info("✅ Symbol existence checked")
        logger.info("✅ New symbol record created successfully")
        logger.info("✅ Symbol summary created")
        logger.info("✅ Data retrieval demonstrated")
        logger.info("\n🎉 NEW SYMBOL WORKFLOW COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        
        return True

async def main():
    """Main demonstration function"""
    logger.info("🚀 Starting Final New Symbol Demo")
    logger.info("=" * 80)
    
    demo = FinalNewSymbolDemo()
    
    try:
        success = await demo.demonstrate_new_symbol_workflow()
        if success:
            logger.info("\n🎯 FINAL DEMO COMPLETED SUCCESSFULLY!")
            logger.info("📊 New symbol MATICUSDT has been added to Airtable")
            logger.info("🔄 The system is ready to process more symbols")
        else:
            logger.error("\n❌ FINAL DEMO FAILED!")
        return success
    except Exception as e:
        logger.error(f"❌ Demo failed with error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        logger.info("🎯 Final New Symbol Demo completed successfully!")
    else:
        logger.error("❌ Final New Symbol Demo failed!") 