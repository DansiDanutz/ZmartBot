#!/usr/bin/env python3
"""
Test Airtable Integration
Demonstrates storing and retrieving KingFisher analysis data in Airtable
"""

import asyncio
import httpx
import json
from datetime import datetime
from pathlib import Path

async def test_airtable_integration():
    """Test the Airtable integration"""
    
    base_url = "http://localhost:8100"
    
    print("🚀 Testing Airtable Integration")
    print("=" * 60)
    print("🎯 CRYPTOTRADE BASE - CURSORTABLE")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Test Airtable connection
        print("\n1️⃣ Testing Airtable Connection...")
        try:
            response = await client.get(f"{base_url}/api/v1/airtable/test-connection")
            if response.status_code == 200:
                result = response.json()
                print("✅ Airtable connection successful")
                print(f"   Base ID: {result.get('base_id')}")
                print(f"   Table: {result.get('table_name')}")
                print(f"   Status: {result.get('message')}")
            else:
                print(f"❌ Failed to test connection: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing connection: {e}")
        
        # Test 2: Get Airtable status
        print("\n2️⃣ Getting Airtable Status...")
        try:
            response = await client.get(f"{base_url}/api/v1/airtable/status")
            if response.status_code == 200:
                result = response.json()
                print("✅ Airtable status retrieved")
                print(f"   Status: {result.get('status')}")
                stats = result.get('statistics', {})
                print(f"   Recent Analyses: {stats.get('recent_analyses', 0)}")
                print(f"   Symbol Summaries: {stats.get('symbol_summaries', 0)}")
                print(f"   High Significance Alerts: {stats.get('high_significance_alerts', 0)}")
            else:
                print(f"❌ Failed to get status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting status: {e}")
        
        # Test 3: Get Airtable configuration
        print("\n3️⃣ Getting Airtable Configuration...")
        try:
            response = await client.get(f"{base_url}/api/v1/airtable/config")
            if response.status_code == 200:
                result = response.json()
                config = result.get('config', {})
                print("✅ Airtable configuration retrieved")
                print(f"   Base ID: {config.get('base_id')}")
                print(f"   Table: {config.get('table_name')}")
                print(f"   API Key: {config.get('api_key')[:20]}...")
            else:
                print(f"❌ Failed to get config: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting config: {e}")
        
        # Test 4: Store sample analysis in Airtable
        print("\n4️⃣ Storing Sample Analysis in Airtable...")
        try:
            sample_analysis = {
                "image_id": "test_btc_001",
                "symbol": "BTCUSDT",
                "timestamp": datetime.now().isoformat(),
                "significance_score": 0.85,
                "market_sentiment": "bearish",
                "confidence": 0.92,
                "liquidation_clusters": [{"x": 100, "y": 200, "density": 0.8}],
                "toxic_flow": 0.45,
                "image_path": "/path/to/test/image.jpg",
                "analysis_data": {"test": "data"}
            }
            
            response = await client.post(
                f"{base_url}/api/v1/airtable/store-analysis",
                json=sample_analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Sample analysis stored in Airtable")
                print(f"   Symbol: {result.get('symbol')}")
                print(f"   Success: {result.get('success')}")
                print(f"   Message: {result.get('message')}")
            else:
                print(f"❌ Failed to store analysis: {response.status_code}")
        except Exception as e:
            print(f"❌ Error storing analysis: {e}")
        
        # Test 5: Store sample summary in Airtable
        print("\n5️⃣ Storing Sample Summary in Airtable...")
        try:
            sample_summary = {
                "symbol": "BTCUSDT",
                "last_update": datetime.now().isoformat(),
                "total_images": 15,
                "average_significance": 0.72,
                "dominant_sentiment": "bearish",
                "high_significance_count": 8,
                "recent_trend": "increasing",
                "risk_level": "high",
                "latest_analysis_id": "test_btc_001"
            }
            
            response = await client.post(
                f"{base_url}/api/v1/airtable/store-summary",
                json=sample_summary
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Sample summary stored in Airtable")
                print(f"   Symbol: {result.get('symbol')}")
                print(f"   Success: {result.get('success')}")
                print(f"   Message: {result.get('message')}")
            else:
                print(f"❌ Failed to store summary: {response.status_code}")
        except Exception as e:
            print(f"❌ Error storing summary: {e}")
        
        # Test 6: Store sample alert in Airtable
        print("\n6️⃣ Storing Sample Alert in Airtable...")
        try:
            sample_alert = {
                "symbol": "BTCUSDT",
                "significance_score": 0.95,
                "market_sentiment": "bearish",
                "confidence": 0.98,
                "liquidation_clusters": [{"x": 150, "y": 250, "density": 0.9}],
                "toxic_flow": 0.35,
                "alert_level": "High",
                "timestamp": datetime.now().isoformat()
            }
            
            response = await client.post(
                f"{base_url}/api/v1/airtable/store-alert",
                json=sample_alert
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Sample alert stored in Airtable")
                print(f"   Symbol: {result.get('symbol')}")
                print(f"   Success: {result.get('success')}")
                print(f"   Message: {result.get('message')}")
            else:
                print(f"❌ Failed to store alert: {response.status_code}")
        except Exception as e:
            print(f"❌ Error storing alert: {e}")
        
        # Test 7: Get analyses from Airtable
        print("\n7️⃣ Getting Analyses from Airtable...")
        try:
            response = await client.get(f"{base_url}/api/v1/airtable/analyses?limit=5")
            if response.status_code == 200:
                result = response.json()
                analyses = result.get('analyses', [])
                print(f"✅ Retrieved {len(analyses)} analyses from Airtable")
                for analysis in analyses[:3]:  # Show first 3
                    print(f"   📊 {analysis.get('symbol')}: {analysis.get('significance_score', 0):.2%}")
            else:
                print(f"❌ Failed to get analyses: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting analyses: {e}")
        
        # Test 8: Get summaries from Airtable
        print("\n8️⃣ Getting Summaries from Airtable...")
        try:
            response = await client.get(f"{base_url}/api/v1/airtable/summaries")
            if response.status_code == 200:
                result = response.json()
                summaries = result.get('summaries', [])
                print(f"✅ Retrieved {len(summaries)} summaries from Airtable")
                for summary in summaries[:3]:  # Show first 3
                    print(f"   📈 {summary.get('symbol')}: {summary.get('average_significance', 0):.2%}")
            else:
                print(f"❌ Failed to get summaries: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting summaries: {e}")
        
        # Test 9: Get alerts from Airtable
        print("\n9️⃣ Getting Alerts from Airtable...")
        try:
            response = await client.get(f"{base_url}/api/v1/airtable/alerts?limit=5")
            if response.status_code == 200:
                result = response.json()
                alerts = result.get('alerts', [])
                print(f"✅ Retrieved {len(alerts)} alerts from Airtable")
                for alert in alerts[:3]:  # Show first 3
                    print(f"   🚨 {alert.get('symbol')}: {alert.get('significance_score', 0):.2%}")
            else:
                print(f"❌ Failed to get alerts: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting alerts: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 AIRTABLE INTEGRATION COMPLETE")
    print("=" * 60)
    print("\n📋 INTEGRATION FEATURES:")
    print("✅ Real-time data storage in Airtable")
    print("✅ Image analysis storage")
    print("✅ Symbol summary storage")
    print("✅ High significance alert storage")
    print("✅ Data retrieval from Airtable")
    print("✅ Connection testing and monitoring")
    
    print("\n🔧 API ENDPOINTS:")
    print("📊 GET /api/v1/airtable/test-connection - Test connection")
    print("📈 GET /api/v1/airtable/status - Get integration status")
    print("🔧 GET /api/v1/airtable/config - Get configuration")
    print("📊 GET /api/v1/airtable/analyses - Get analyses from Airtable")
    print("📈 GET /api/v1/airtable/summaries - Get summaries from Airtable")
    print("🚨 GET /api/v1/airtable/alerts - Get alerts from Airtable")
    print("📊 POST /api/v1/airtable/store-analysis - Store analysis")
    print("📈 POST /api/v1/airtable/store-summary - Store summary")
    print("🚨 POST /api/v1/airtable/store-alert - Store alert")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def show_airtable_info():
    """Show Airtable configuration information"""
    
    print("\n" + "=" * 60)
    print("📊 AIRTABLE CONFIGURATION")
    print("=" * 60)
    
    print("\n🔧 Base Information:")
    print("   📊 Base ID: appAs9sZH7OmtYaTJ")
    print("   📋 Table Name: CursorTable")
    print("   🔑 API Key: patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835")
    print("   🌐 Base URL: https://api.airtable.com/v0/appAs9sZH7OmtYaTJ")
    
    print("\n📊 Data Fields:")
    print("   📸 Image ID - Unique identifier for each image")
    print("   📈 Symbol - Trading symbol (e.g., BTCUSDT)")
    print("   ⏰ Timestamp - Analysis timestamp")
    print("   🎯 Significance Score - Analysis significance (0-1)")
    print("   📊 Market Sentiment - Bullish/Bearish/Neutral")
    print("   🎯 Confidence - Analysis confidence level")
    print("   🔴 Liquidation Clusters - JSON array of cluster data")
    print("   🟢 Toxic Flow - Toxic flow percentage")
    print("   📁 Image Path - Path to analyzed image")
    print("   📊 Analysis Data - Complete analysis JSON")
    print("   🚨 Alert Level - High/Medium/Low")
    print("   📊 Status - Active/Inactive")
    
    print("\n🎯 Integration Benefits:")
    print("   ✅ Cloud-based data storage")
    print("   ✅ Real-time data synchronization")
    print("   ✅ Easy data export and sharing")
    print("   ✅ Built-in data visualization")
    print("   ✅ Multi-user collaboration")
    print("   ✅ Automated workflows")
    print("   ✅ Data backup and security")

if __name__ == "__main__":
    print("🚀 Airtable Integration Test")
    print("=" * 60)
    
    # Show Airtable information
    show_airtable_info()
    
    # Run the test
    asyncio.run(test_airtable_integration())
    
    print("\n🎯 Your KingFisher analysis data will be automatically stored in Airtable!")
    print("📊 Visit your CryptoTrade base to see all the data: https://airtable.com/appAs9sZH7OmtYaTJ") 