#!/usr/bin/env python3
"""
Quick fix for Telegram monitoring issue
"""

import asyncio
import httpx
import json

async def fix_telegram_monitoring():
    """Fix the Telegram monitoring issue"""
    base_url = "http://localhost:8100"
    
    print("🔧 Fixing Telegram monitoring issue...")
    
    # 1. Check current status
    print("\n1. Checking current status...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/v1/telegram/monitoring-status")
            if response.status_code == 200:
                status = response.json()
                print(f"   Connected: {status.get('connected', False)}")
                print(f"   Monitoring: {status.get('monitoring', False)}")
            else:
                print("   ❌ Could not check status")
    except Exception as e:
        print(f"   ❌ Error checking status: {e}")
    
    # 2. Start monitoring
    print("\n2. Starting Telegram monitoring...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/api/v1/telegram/start-monitoring")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result.get('message', 'Monitoring started')}")
            else:
                print(f"   ❌ Failed to start monitoring: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error starting monitoring: {e}")
    
    # 3. Check status again
    print("\n3. Checking status after fix...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/v1/telegram/monitoring-status")
            if response.status_code == 200:
                status = response.json()
                print(f"   Connected: {status.get('connected', False)}")
                print(f"   Monitoring: {status.get('monitoring', False)}")
                
                if status.get('monitoring', False):
                    print("   ✅ Monitoring is now active!")
                else:
                    print("   ❌ Monitoring still not active")
            else:
                print("   ❌ Could not check status")
    except Exception as e:
        print(f"   ❌ Error checking status: {e}")
    
    # 4. Test connection
    print("\n4. Testing Telegram connection...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/api/v1/telegram/test-connection")
            if response.status_code == 200:
                result = response.json()
                print(f"   Connected: {result.get('connected', False)}")
                print(f"   Bot Token Valid: {result.get('bot_token_valid', False)}")
                print(f"   Chat ID Valid: {result.get('chat_id_valid', False)}")
                print(f"   Monitoring Ready: {result.get('monitoring_ready', False)}")
                print(f"   Automation Enabled: {result.get('automation_enabled', False)}")
            else:
                print(f"   ❌ Connection test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing connection: {e}")
    
    print("\n🎯 Next Steps:")
    print("   1. Send a new image to the Telegram channel")
    print("   2. Monitor logs: tail -f auto_monitor.log")
    print("   3. Check Airtable for new records")
    print("   4. If still not working, restart the server")

if __name__ == "__main__":
    asyncio.run(fix_telegram_monitoring()) 