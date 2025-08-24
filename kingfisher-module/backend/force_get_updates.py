#!/usr/bin/env python3
"""
Force get all Telegram updates
"""

import requests
import json
from datetime import datetime

BOT_TOKEN = "7995587461:AAELuQHeziFE4hZ1tlJ3d53-y5xQgeSoZHI"

print("="*60)
print("🔄 FORCING UPDATE CHECK")
print("="*60)

# Clear any webhook first (in case it's blocking updates)
print("Clearing webhook...")
webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
response = requests.get(webhook_url)
print(f"Webhook cleared: {response.json()}")

# Now get updates with different offset
print("\nGetting all available updates...")

# Try with negative offset to get last updates
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

# Try different approaches
attempts = [
    {"offset": -1, "limit": 100},  # Get last 100
    {"offset": 0, "limit": 100},   # Get from beginning
    {},                             # Get default
]

all_chats = {}

for i, params in enumerate(attempts, 1):
    print(f"\nAttempt {i}: {params}")
    response = requests.get(url, params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        
        if data['ok'] and data['result']:
            print(f"✅ Found {len(data['result'])} updates")
            
            for update in data['result']:
                # Extract chat from any type of update
                chat = None
                update_type = None
                
                if 'message' in update:
                    chat = update['message']['chat']
                    update_type = 'message'
                    msg_text = update['message'].get('text', '')
                    print(f"\n📨 Message Update:")
                    print(f"   Update ID: {update['update_id']}")
                    print(f"   Chat ID: {chat['id']}")
                    print(f"   Chat Type: {chat['type']}")
                    print(f"   Chat Name: {chat.get('title', chat.get('first_name', 'Unknown'))}")
                    if msg_text:
                        print(f"   Text: {msg_text[:50]}")
                
                elif 'my_chat_member' in update:
                    chat = update['my_chat_member']['chat']
                    update_type = 'bot_status_change'
                    print(f"\n🤖 Bot Status Change:")
                    print(f"   Update ID: {update['update_id']}")
                    print(f"   Chat ID: {chat['id']}")
                    print(f"   Chat Type: {chat['type']}")
                    print(f"   Chat Name: {chat.get('title', chat.get('first_name', 'Unknown'))}")
                    
                    # Check new status
                    new_status = update['my_chat_member'].get('new_chat_member', {}).get('status')
                    print(f"   New Status: {new_status}")
                    if new_status == 'member':
                        print(f"   ✅ BOT WAS ADDED TO THIS CHAT!")
                
                elif 'channel_post' in update:
                    chat = update['channel_post']['chat']
                    update_type = 'channel_post'
                    print(f"\n📢 Channel Post:")
                    print(f"   Chat ID: {chat['id']}")
                    print(f"   Channel: {chat.get('title')}")
                
                if chat and chat['id'] not in all_chats:
                    all_chats[chat['id']] = {
                        'type': chat['type'],
                        'name': chat.get('title', chat.get('first_name', 'Unknown')),
                        'update_type': update_type
                    }
        else:
            print(f"No updates in this attempt")

print("\n" + "="*60)
print("📊 SUMMARY OF ALL CHATS FOUND:")
print("="*60)

if all_chats:
    for chat_id, info in all_chats.items():
        print(f"\n{'🏠 GROUP' if info['type'] in ['group', 'supergroup'] else '👤 PRIVATE' if info['type'] == 'private' else '📢 CHANNEL'}")
        print(f"   Chat ID: {chat_id}")
        print(f"   Name: {info['name']}")
        print(f"   Type: {info['type']}")
        
        if info['type'] in ['group', 'supergroup']:
            print(f"   ✅ USE THIS FOR KINGFISHER: {chat_id}")
            print(f"   Add to .env: TELEGRAM_CHAT_ID={chat_id}")
else:
    print("❌ No chats found at all!")
    print("\nTroubleshooting:")
    print("1. Make sure you sent /start to @ZmartTradingBot first")
    print("2. Then add the bot to your group")
    print("3. Send a message in the group")
    print("4. The bot must be online to receive updates")

print("\n" + "="*60)