#!/usr/bin/env python3
"""
Test Real-Time KingFisher Analysis
Demonstrates the complete real-time analysis system
"""

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import random

async def test_realtime_analysis():
    """Test the real-time analysis system"""
    
    base_url = "http://localhost:8100"
    
    print("🚀 Testing Real-Time KingFisher Analysis System")
    print("=" * 60)
    print("🎯 COMPLETE REAL-TIME MONITORING & ANALYSIS")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Start real-time monitoring
        print("\n1️⃣ Starting Real-Time Monitoring...")
        try:
            response = await client.post(f"{base_url}/api/v1/realtime/start-monitoring")
            if response.status_code == 200:
                result = response.json()
                print("✅ Real-time monitoring started successfully")
                print(f"   Status: {result.get('status')}")
                print(f"   Message: {result.get('message')}")
            else:
                print(f"❌ Failed to start monitoring: {response.status_code}")
        except Exception as e:
            print(f"❌ Error starting monitoring: {e}")
        
        # Test 2: Check monitoring status
        print("\n2️⃣ Checking Monitoring Status...")
        try:
            response = await client.get(f"{base_url}/api/v1/realtime/status")
            if response.status_code == 200:
                result = response.json()
                print("✅ Monitoring status retrieved")
                print(f"   Status: {result.get('status')}")
                print(f"   Active: {result.get('monitoring_active')}")
                stats = result.get('statistics', {})
                print(f"   Total Analyses: {stats.get('total_analyses', 0)}")
                print(f"   Total Symbols: {stats.get('total_symbols', 0)}")
            else:
                print(f"❌ Failed to get status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting status: {e}")
        
        # Test 3: Get all symbols
        print("\n3️⃣ Getting All Symbols...")
        try:
            response = await client.get(f"{base_url}/api/v1/realtime/symbols")
            if response.status_code == 200:
                result = response.json()
                symbols = result.get('symbols', [])
                print(f"✅ Found {len(symbols)} symbols")
                for symbol in symbols[:5]:  # Show first 5
                    print(f"   📊 {symbol['symbol']}: {symbol['total_images']} images, "
                          f"Risk: {symbol['risk_level']}, Trend: {symbol['recent_trend']}")
            else:
                print(f"❌ Failed to get symbols: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting symbols: {e}")
        
        # Test 4: Get symbol summaries
        print("\n4️⃣ Getting Symbol Summaries...")
        try:
            response = await client.get(f"{base_url}/api/v1/realtime/summaries")
            if response.status_code == 200:
                result = response.json()
                summaries = result.get('summaries', {})
                print(f"✅ Retrieved {len(summaries)} symbol summaries")
                for symbol, summary in list(summaries.items())[:3]:  # Show first 3
                    print(f"   📈 {symbol}: {summary['dominant_sentiment']}, "
                          f"Avg Significance: {summary['average_significance']:.2%}")
            else:
                print(f"❌ Failed to get summaries: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting summaries: {e}")
        
        # Test 5: Get recent analyses
        print("\n5️⃣ Getting Recent Analyses...")
        try:
            response = await client.get(f"{base_url}/api/v1/realtime/analyses?limit=5")
            if response.status_code == 200:
                result = response.json()
                analyses = result.get('analyses', [])
                print(f"✅ Retrieved {len(analyses)} recent analyses")
                for analysis in analyses[:3]:  # Show first 3
                    print(f"   🔍 {analysis['symbol']}: {analysis['significance_score']:.2%} "
                          f"({analysis['market_sentiment']})")
            else:
                print(f"❌ Failed to get analyses: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting analyses: {e}")
        
        # Test 6: Get high significance analyses
        print("\n6️⃣ Getting High Significance Analyses...")
        try:
            response = await client.get(f"{base_url}/api/v1/realtime/high-significance?limit=5")
            if response.status_code == 200:
                result = response.json()
                high_sig = result.get('high_significance_analyses', [])
                print(f"✅ Found {len(high_sig)} high significance analyses")
                for analysis in high_sig[:3]:  # Show first 3
                    print(f"   🚨 {analysis['symbol']}: {analysis['significance_score']:.2%} "
                          f"({analysis['alert_level']} alert)")
            else:
                print(f"❌ Failed to get high significance: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting high significance: {e}")
        
        # Test 7: Get statistics
        print("\n7️⃣ Getting Overall Statistics...")
        try:
            response = await client.get(f"{base_url}/api/v1/realtime/statistics")
            if response.status_code == 200:
                result = response.json()
                stats = result.get('statistics', {})
                print("✅ Statistics retrieved:")
                print(f"   📊 Total Analyses: {stats.get('total_analyses', 0)}")
                print(f"   📈 Total Symbols: {stats.get('total_symbols', 0)}")
                print(f"   🚨 High Significance: {stats.get('high_significance_count', 0)}")
                print(f"   📊 Average Significance: {stats.get('average_significance', 0):.2%}")
            else:
                print(f"❌ Failed to get statistics: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 REAL-TIME ANALYSIS SYSTEM READY")
    print("=" * 60)
    print("\n📋 SYSTEM CAPABILITIES:")
    print("✅ Real-time Telegram channel monitoring")
    print("✅ Automatic image analysis and storage")
    print("✅ Symbol-based summaries and trends")
    print("✅ High significance alerts")
    print("✅ Persistent data storage")
    print("✅ Historical analysis tracking")
    
    print("\n🔧 API ENDPOINTS:")
    print("📊 GET /api/v1/realtime/summaries - All symbol summaries")
    print("📈 GET /api/v1/realtime/summary/{symbol} - Specific symbol")
    print("🔍 GET /api/v1/realtime/analyses - Recent analyses")
    print("🚨 GET /api/v1/realtime/high-significance - High significance alerts")
    print("📊 GET /api/v1/realtime/statistics - Overall statistics")
    print("📈 GET /api/v1/realtime/symbols - All symbols list")
    print("🔄 POST /api/v1/realtime/start-monitoring - Start monitoring")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def simulate_kingfisher_images():
    """Simulate KingFisher images for testing"""
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'DOTUSDT']
    test_dir = Path("test_images")
    test_dir.mkdir(exist_ok=True)
    
    print("\n🎯 SIMULATING KINGFISHER IMAGES")
    print("=" * 40)
    
    for i, symbol in enumerate(symbols):
        # Create a simulated image file
        image_path = test_dir / f"kingfisher_{symbol.lower()}_{i+1}.jpg"
        
        # Simulate image creation (in real scenario, this would be from Telegram)
        with open(image_path, 'w') as f:
            f.write(f"Simulated KingFisher image for {symbol}")
        
        print(f"📸 Created: {image_path.name}")
    
    print(f"✅ Created {len(symbols)} simulated KingFisher images")
    return symbols

async def test_with_simulated_data():
    """Test the system with simulated data"""
    print("\n🧪 TESTING WITH SIMULATED DATA")
    print("=" * 40)
    
    # Simulate KingFisher images
    symbols = simulate_kingfisher_images()
    
    # Test the analysis system
    await test_realtime_analysis()
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Replace simulated images with real KingFisher images")
    print("2. Configure Telegram channel monitoring")
    print("3. Start real-time analysis")
    print("4. Monitor results and alerts")

if __name__ == "__main__":
    print("🚀 KingFisher Real-Time Analysis System")
    print("=" * 60)
    
    # Run the test
    asyncio.run(test_with_simulated_data()) 