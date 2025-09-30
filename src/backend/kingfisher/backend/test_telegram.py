#!/usr/bin/env python3
"""
Test Telegram credentials
"""

import asyncio
import httpx
import os

async def test_telegram():
    """Test Telegram bot connection"""
    
    # Your credentials
    bot_token = "7995587461:AAELuQHeziFE4hZ1tlJ3d53-y5xQgeSoZHI"
    chat_id = "-1002891569616"
    
    print("🧪 Testing Telegram Bot Connection...")
    
    try:
        # Test 1: Check bot info
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.telegram.org/bot{bot_token}/getMe")
            
            if response.status_code == 200:
                bot_info = response.json()
                print(f"✅ Bot connected: {bot_info['result']['username']}")
                print(f"📝 Bot name: {bot_info['result']['first_name']}")
            else:
                print(f"❌ Bot connection failed: {response.text}")
                return
        
        # Test 2: Send test message
        test_message = f"🧪 <b>KingFisher Test</b>\n\n✅ Connection successful!\n⏰ Test from KingFisher module"
        
        data = {
            'chat_id': chat_id,
            'text': test_message,
            'parse_mode': 'HTML'
        }
        
        async with httpx.AsyncClient() as client2:
            response = await client2.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test message sent successfully!")
            print(f"📨 Message ID: {result['result']['message_id']}")
            print(f"💬 Chat ID: {result['result']['chat']['id']}")
        else:
            print(f"❌ Failed to send message: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_telegram()) 