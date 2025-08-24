#!/usr/bin/env python3
"""
Get your new group chat ID
"""

import requests
import json

BOT_TOKEN = "7995587461:AAELuQHeziFE4hZ1tlJ3d53-y5xQgeSoZHI"

def get_chat_updates():
    """Get all recent updates to find the group chat ID"""
    
    print("="*60)
    print("🔍 FINDING YOUR GROUP CHAT ID")
    print("="*60)
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        if data['ok'] and data['result']:
            print(f"\n✅ Found {len(data['result'])} updates\n")
            
            group_chats = set()
            
            for update in data['result']:
                if 'message' in update:
                    msg = update['message']
                    chat = msg.get('chat', {})
                    
                    # Check if it's a group chat
                    if chat.get('type') in ['group', 'supergroup']:
                        chat_id = chat.get('id')
                        chat_title = chat.get('title', 'Unnamed')
                        group_chats.add((chat_id, chat_title))
                        
                        print(f"📱 GROUP FOUND:")
                        print(f"   Chat ID: {chat_id}")
                        print(f"   Title: {chat_title}")
                        print(f"   Type: {chat.get('type')}")
                        
                        # Check latest message
                        if 'text' in msg:
                            print(f"   Latest message: {msg['text'][:50]}")
                        if 'new_chat_member' in msg:
                            print(f"   Bot was added to this group!")
                        
                        print("-"*40)
            
            if group_chats:
                print("\n🎯 SUMMARY:")
                print("Use one of these Chat IDs in your configuration:")
                for chat_id, title in group_chats:
                    print(f"   {chat_id} = {title}")
            else:
                print("❌ No group chats found!")
                print("\nMake sure to:")
                print("1. Add @ZmartTradingBot to your group")
                print("2. Send a message in the group")
                print("3. Run this script again")
        else:
            print("❌ No updates found")
            print("\nTo set up:")
            print("1. Create a group chat")
            print("2. Add @ZmartTradingBot to the group")
            print("3. Send any message in the group")
            print("4. Run this script again")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    get_chat_updates()