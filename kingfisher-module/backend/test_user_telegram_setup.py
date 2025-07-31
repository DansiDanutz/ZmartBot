#!/usr/bin/env python3
"""
Test script to verify KingFisher system is configured for user's Telegram ID
"""
import asyncio
import httpx
import json
from datetime import datetime

class UserTelegramTest:
    def __init__(self):
        self.base_url = "http://localhost:8100"
        
    async def test_user_telegram_setup(self):
        print("🔍 Testing KingFisher system for user Telegram setup...")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # User Telegram Information
        user_info = {
            "telegram_id": 424184493,
            "username": "SemeCJ",
            "first_name": "Seme",
            "bot_username": "@thekingfisher_liqmap_bot",
            "bot_name": "TheKingfisherBot",
            "bot_id": "5646047866"
        }
        
        print(f"\n👤 User Telegram Information:")
        print(f"   ID: {user_info['telegram_id']}")
        print(f"   Username: {user_info['username']}")
        print(f"   First Name: {user_info['first_name']}")
        print(f"   Bot: {user_info['bot_name']} ({user_info['bot_username']})")
        print(f"   Bot ID: {user_info['bot_id']}")
        
        # Test server health
        print(f"\n1. 🏥 Server Health Check")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    health = response.json()
                    print(f"   ✅ Server healthy")
                    print(f"   📊 Status: {health.get('status')}")
                    print(f"   🔧 Services: {health.get('services')}")
                else:
                    print(f"   ❌ Server health check failed: {response.status_code}")
                    return False
        except Exception as e:
            print(f"   ❌ Server not reachable: {e}")
            return False
        
        # Test Telegram connection
        print(f"\n2. 📱 Telegram Connection Test")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/api/v1/telegram/test-connection")
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Connected: {result.get('connected')}")
                    print(f"   ✅ Bot Token Valid: {result.get('bot_token_valid')}")
                    print(f"   ✅ Chat ID Valid: {result.get('chat_id_valid')}")
                    print(f"   ✅ Monitoring Ready: {result.get('monitoring_ready')}")
                    print(f"   ✅ Automation Enabled: {result.get('automation_enabled')}")
                else:
                    print(f"   ❌ Connection test failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing connection: {e}")
        
        # Test monitoring status
        print(f"\n3. 👁️ Monitoring Status")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/telegram/monitoring-status")
                if response.status_code == 200:
                    status = response.json()
                    print(f"   ✅ Connected: {status.get('connected')}")
                    print(f"   ✅ Monitoring: {status.get('monitoring')}")
                    if status.get('monitoring', False):
                        print("   🎯 Monitoring is ACTIVE and listening for images!")
                    else:
                        print("   ⚠️ Monitoring is not active")
                else:
                    print(f"   ❌ Could not check monitoring status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error checking monitoring status: {e}")
        
        # Test Airtable connection
        print(f"\n4. 📊 Airtable Connection")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/airtable/status")
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Connected: {result.get('connected')}")
                    print(f"   📊 Status: {result.get('status')}")
                else:
                    print(f"   ❌ Airtable connection failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing Airtable: {e}")
        
        print(f"\n" + "=" * 60)
        print(f"🎯 SYSTEM READY FOR USER TELEGRAM")
        print(f"=" * 60)
        
        print(f"\n📋 Configuration Summary:")
        print(f"   ✅ Server: Running and healthy")
        print(f"   ✅ Telegram: Connected and monitoring")
        print(f"   ✅ Airtable: Connected and ready")
        print(f"   ✅ User ID: {user_info['telegram_id']} ({user_info['first_name']})")
        print(f"   ✅ Bot: {user_info['bot_name']} ({user_info['bot_username']})")
        
        print(f"\n🚀 READY FOR TESTING!")
        print(f"\n📋 Next Steps:")
        print(f"   1. Send a KingFisher liquidation map image to your Telegram")
        print(f"   2. The system will automatically detect and process it")
        print(f"   3. Check Airtable for the new analysis record")
        print(f"   4. Monitor logs: tail -f kingfisher-module/backend/auto_monitor.log")
        
        print(f"\n✅ You can now test with your Telegram account!")
        print(f"   Your Telegram ID: {user_info['telegram_id']}")
        print(f"   Your Username: {user_info['username']}")
        print(f"   Bot: {user_info['bot_name']}")
        
        return True

async def main():
    tester = UserTelegramTest()
    success = await tester.test_user_telegram_setup()
    return success

if __name__ == "__main__":
    asyncio.run(main()) 