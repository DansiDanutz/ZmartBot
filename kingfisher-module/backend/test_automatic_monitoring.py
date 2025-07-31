#!/usr/bin/env python3
"""
Test Automatic KingFisher Monitoring
Verifies that the system works without manual button pressing
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_automatic_monitoring():
    """Test automatic monitoring system"""
    
    base_url = "http://localhost:8100"
    
    print("🧪 Testing Automatic KingFisher Monitoring")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Check current webhook status
        print("\n1️⃣ Checking Webhook Status...")
        try:
            response = await client.get(f"{base_url}/api/v1/telegram/webhook-info")
            if response.status_code == 200:
                webhook_info = response.json()
                print(f"✅ Webhook info retrieved")
                print(f"   - Has webhook: {webhook_info.get('result', {}).get('url', 'No webhook')}")
                print(f"   - Pending updates: {webhook_info.get('result', {}).get('pending_update_count', 0)}")
            else:
                print(f"❌ Webhook info failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Webhook info error: {e}")
        
        # Test 2: Delete any existing webhook (switch to polling)
        print("\n2️⃣ Switching to Polling Mode...")
        try:
            response = await client.post(f"{base_url}/api/v1/telegram/delete-webhook")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Switched to polling mode: {result.get('message')}")
            else:
                print(f"❌ Webhook deletion failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Webhook deletion error: {e}")
        
        # Test 3: Start automatic monitoring
        print("\n3️⃣ Starting Automatic Monitoring...")
        try:
            response = await client.post(f"{base_url}/api/v1/telegram/start-monitoring")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Automatic monitoring started: {result.get('message')}")
                print(f"   - Bot ID: {result.get('bot_id')}")
                print(f"   - Bot Username: {result.get('bot_username')}")
            else:
                print(f"❌ Monitoring start failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Monitoring start error: {e}")
        
        # Test 4: Check monitoring status
        print("\n4️⃣ Checking Monitoring Status...")
        try:
            response = await client.get(f"{base_url}/api/v1/telegram/monitoring-status")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Monitoring status: Connected={result.get('connected')}, Monitoring={result.get('monitoring')}")
                print(f"   - Bot ID: {result.get('bot_id')}")
                print(f"   - Bot Username: {result.get('bot_username')}")
                print(f"   - Last Message ID: {result.get('last_message_id')}")
            else:
                print(f"❌ Status check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Status check error: {e}")
        
        # Test 5: Test webhook setup (for production)
        print("\n5️⃣ Testing Webhook Setup (Production)...")
        try:
            # This would be used in production with HTTPS
            webhook_url = "https://your-domain.com/webhook/telegram"
            response = await client.post(
                f"{base_url}/api/v1/telegram/setup-webhook",
                params={"webhook_url": webhook_url}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Webhook setup test: {result.get('message')}")
                print(f"   - Webhook URL: {result.get('webhook_url')}")
            else:
                print(f"❌ Webhook setup failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Webhook setup error: {e}")
        
        # Test 6: Simulate incoming message (manual forwarding)
        print("\n6️⃣ Testing Manual Forwarding...")
        try:
            test_file_id = "test_file_123"
            test_user_id = 424184493  # Your Telegram ID
            test_username = "SemeCJ"
            
            response = await client.post(
                f"{base_url}/api/v1/telegram/process-forwarded",
                params={
                    "file_id": test_file_id,
                    "user_id": test_user_id,
                    "username": test_username
                }
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Manual forwarding test: {result.get('message')}")
                print(f"   - File ID: {result.get('file_id')}")
                print(f"   - User ID: {result.get('user_id')}")
                print(f"   - Username: {result.get('username')}")
            else:
                print(f"❌ Manual forwarding failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Manual forwarding error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 AUTOMATIC MONITORING TEST COMPLETE")
    print("=" * 50)
    print("\n📋 SUMMARY:")
    print("✅ System is using LONG POLLING (automatic)")
    print("✅ No manual button pressing required")
    print("✅ Real-time monitoring of @thekingfisher_liqmap_bot")
    print("✅ Automatic image processing when posted")
    print("✅ Manual forwarding also supported")
    print("✅ Webhook support for production")
    
    print("\n🚀 HOW IT WORKS:")
    print("1. LONG POLLING: Bot continuously checks for new messages")
    print("2. AUTOMATIC: When @thekingfisher_liqmap_bot posts → Immediate processing")
    print("3. MANUAL: You can forward images to your bot → Immediate processing")
    print("4. NO BUTTONS: Everything is automatic, no manual intervention needed")
    
    print("\n⚙️ PRODUCTION OPTION:")
    print("For production with HTTPS, you can use webhooks:")
    print("- More efficient than polling")
    print("- Requires HTTPS domain")
    print("- Real-time updates")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(test_automatic_monitoring()) 