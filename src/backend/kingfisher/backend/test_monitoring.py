#!/usr/bin/env python3
"""
Test script for KingFisher monitoring system
"""

import asyncio
import httpx
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_monitoring():
    """Test the monitoring system"""
    print("🧪 Testing KingFisher Monitoring System...")
    print("=" * 50)
    
    base_url = "http://localhost:8100"
    
    # Test 1: Server Health
    print("1️⃣ Testing server health...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server healthy: {data.get('status', 'unknown')}")
            else:
                print(f"❌ Server unhealthy: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Airtable Connection
    print("2️⃣ Testing Airtable connection...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/api/v1/airtable/status")
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                print(f"✅ Airtable status: {status}")
            else:
                print(f"❌ Airtable connection failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot check Airtable: {e}")
        return False
    
    # Test 3: Image Processing
    print("3️⃣ Testing image processing...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/api/v1/enhanced-analysis/process-kingfisher-image",
                data={
                    "symbol": "TESTUSDT",
                    "image_id": "test_monitoring_123",
                    "significance_score": 0.85,
                    "market_sentiment": "bullish",
                    "total_clusters": 4,
                    "total_flow_area": 2800
                },
                files={
                    "liquidation_map_image": ("test_map.jpg", b"test_image_data"),
                    "liquidation_heatmap_image": ("test_heatmap.jpg", b"test_image_data")
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Image processing successful: {result.get('message', 'Unknown')}")
            else:
                print(f"❌ Image processing failed: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error testing image processing: {e}")
        return False
    
    print("=" * 50)
    print("🎉 All tests passed! Monitoring system is ready.")
    print("🚀 You can now run: ./start_monitoring.sh")
    return True

async def main():
    """Main function"""
    success = await test_monitoring()
    if not success:
        print("❌ Some tests failed. Please check the server and try again.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 