#!/usr/bin/env python3
"""
Direct Airtable Service Test
Tests the Airtable service directly without going through the API
"""

import asyncio
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_airtable_service():
    """Test the Airtable service directly"""
    
    print("🧪 Testing Airtable Service Directly")
    print("=" * 50)
    
    try:
        from services.airtable_service import AirtableService
        
        # Create service instance
        airtable_service = AirtableService()
        
        # Test 1: Test connection
        print("\n1️⃣ Testing Airtable Connection...")
        connected = await airtable_service.test_connection()
        if connected:
            print("✅ Airtable connection successful")
        else:
            print("❌ Airtable connection failed")
        
        # Test 2: Store sample analysis
        print("\n2️⃣ Storing Sample Analysis...")
        sample_analysis = {
            "symbol": "BTCUSDT",
            "liquidation_clusters": [{"x": 100, "y": 200, "density": 0.8}],
            "long_term_ratios": "0.75, 0.82, 0.91",
            "short_term_ratios": "0.45, 0.52, 0.68",
            "rsi_heatmap": "RSI data for BTCUSDT",
            "lie_heatmap": "Liquidation heatmap data",
            "summary": "BTCUSDT showing bearish liquidation patterns with high significance"
        }
        
        success = await airtable_service.store_image_analysis(sample_analysis)
        if success:
            print("✅ Sample analysis stored successfully")
        else:
            print("❌ Failed to store sample analysis")
        
        # Test 3: Get recent analyses
        print("\n3️⃣ Getting Recent Analyses...")
        analyses = await airtable_service.get_recent_analyses(limit=5)
        print(f"✅ Retrieved {len(analyses)} recent analyses")
        
        # Test 4: Store symbol summary
        print("\n4️⃣ Storing Symbol Summary...")
        sample_summary = {
            "symbol": "BTCUSDT",
            "last_update": "2025-07-29T19:21:00Z",
            "total_images": 10,
            "average_significance": 0.75,
            "dominant_sentiment": "bearish",
            "high_significance_count": 3,
            "recent_trend": "declining",
            "risk_level": "high",
            "latest_analysis_id": "test_btc_001"
        }
        
        success = await airtable_service.store_symbol_summary(sample_summary)
        if success:
            print("✅ Symbol summary stored successfully")
        else:
            print("❌ Failed to store symbol summary")
        
        print("\n🎉 Direct Airtable service test completed!")
        
    except Exception as e:
        print(f"❌ Error testing Airtable service: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_airtable_service()) 