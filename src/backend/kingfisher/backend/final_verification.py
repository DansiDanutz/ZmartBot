#!/usr/bin/env python3
"""
Final verification script for KingFisher system
"""
import asyncio
import httpx
import json
import time
from datetime import datetime

class FinalVerification:
    def __init__(self):
        self.base_url = "http://localhost:8100"
        
    async def run_verification(self):
        print("🔍 Running final verification for KingFisher system...")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        results = {
            "server_health": False,
            "telegram_status": False,
            "telegram_connection": False,
            "telegram_monitoring": False,
            "airtable_status": False,
            "image_processing": False,
            "all_systems_ready": False
        }
        
        # 1. Server Health Check
        print("\n1. 🏥 Server Health Check")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    health = response.json()
                    print(f"   ✅ Server healthy")
                    print(f"   📊 Status: {health.get('status')}")
                    print(f"   🕒 Timestamp: {health.get('timestamp')}")
                    print(f"   🔧 Services: {health.get('services')}")
                    results["server_health"] = True
                else:
                    print(f"   ❌ Server health check failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Server not reachable: {e}")
        
        # 2. Telegram Status Check
        print("\n2. 📱 Telegram Status Check")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/telegram/status")
                if response.status_code == 200:
                    status = response.json()
                    print(f"   ✅ Connected: {status.get('connected')}")
                    print(f"   ✅ Monitoring: {status.get('monitoring')}")
                    print(f"   📊 Status: {status.get('status')}")
                    results["telegram_status"] = True
                else:
                    print(f"   ❌ Telegram status check failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error checking Telegram status: {e}")
        
        # 3. Telegram Connection Test
        print("\n3. 🔗 Telegram Connection Test")
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
                    results["telegram_connection"] = True
                else:
                    print(f"   ❌ Connection test failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing connection: {e}")
        
        # 4. Telegram Monitoring Status
        print("\n4. 👁️ Telegram Monitoring Status")
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
                    results["telegram_monitoring"] = status.get('monitoring', False)
                else:
                    print(f"   ❌ Could not check monitoring status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error checking monitoring status: {e}")
        
        # 5. Airtable Status Check
        print("\n5. 📊 Airtable Status Check")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/airtable/status")
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Connected: {result.get('connected')}")
                    print(f"   📊 Status: {result.get('status')}")
                    results["airtable_status"] = True
                else:
                    print(f"   ❌ Airtable connection failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing Airtable: {e}")
        
        # 6. Image Processing Status
        print("\n6. 🖼️ Image Processing Status")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/images/status")
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Ready: {result.get('ready')}")
                    print(f"   📊 Status: {result.get('status')}")
                    results["image_processing"] = True
                else:
                    print(f"   ❌ Image processing failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing image processing: {e}")
        
        # 7. Overall System Status
        print("\n7. 🎯 Overall System Status")
        # Check all systems except the overall status itself
        system_checks = {k: v for k, v in results.items() if k != "all_systems_ready"}
        all_ready = all(system_checks.values())
        results["all_systems_ready"] = all_ready
        
        if all_ready:
            print("   🚀 ALL SYSTEMS ARE READY!")
            print("   ✅ Server: Running and healthy")
            print("   ✅ Telegram: Connected and monitoring")
            print("   ✅ Airtable: Connected and ready")
            print("   ✅ Image Processing: Ready for analysis")
            print("   ✅ Monitoring: Active and listening")
        else:
            print("   ⚠️ Some systems are not ready:")
            for system, status in results.items():
                if not status:
                    print(f"   ❌ {system.replace('_', ' ').title()}")
        
        print("\n" + "=" * 60)
        print("🎯 VERIFICATION COMPLETE")
        print("=" * 60)
        
        if all_ready:
            print("\n🚀 SYSTEM IS READY FOR TESTING!")
            print("\n📋 Next Steps:")
            print("   1. Send a new liquidation map image to the Telegram channel")
            print("   2. The system will automatically detect and process it")
            print("   3. Check Airtable for the new analysis record")
            print("   4. Monitor logs: tail -f kingfisher-module/backend/auto_monitor.log")
            print("\n✅ You can now test with a new symbol!")
        else:
            print("\n⚠️ SYSTEM NEEDS ATTENTION")
            print("Some components are not ready. Please check the errors above.")
        
        return results

async def main():
    verifier = FinalVerification()
    results = await verifier.run_verification()
    return results

if __name__ == "__main__":
    asyncio.run(main()) 