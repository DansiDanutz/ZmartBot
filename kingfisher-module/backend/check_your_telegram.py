#!/usr/bin/env python3
"""
Check YOUR Telegram for KingFisher images
"""

import requests
import json
from datetime import datetime

BOT_TOKEN = "7995587461:AAELuQHeziFE4hZ1tlJ3d53-y5xQgeSoZHI"
YOUR_CHAT_ID = 424184493

def check_your_messages():
    """Check for messages from you"""
    
    print("="*60)
    print("🔍 CHECKING YOUR TELEGRAM MESSAGES")
    print("="*60)
    print(f"Your Chat ID: {YOUR_CHAT_ID}")
    print(f"Your Username: @SemeCJ")
    print("="*60)
    
    # Get updates
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        if data['ok'] and data['result']:
            print(f"\n✅ Found {len(data['result'])} updates\n")
            
            for update in data['result'][-5:]:  # Last 5 updates
                if 'message' in update:
                    msg = update['message']
                    
                    # Check if it's from you
                    if msg.get('from', {}).get('id') == YOUR_CHAT_ID:
                        print(f"📱 Message from YOU:")
                        print(f"   Time: {datetime.fromtimestamp(msg['date'])}")
                        
                        if 'photo' in msg:
                            print(f"   🖼️ PHOTO DETECTED!")
                            print(f"   Caption: {msg.get('caption', 'No caption')}")
                            
                            # This is a KingFisher image!
                            if 'caption' in msg:
                                caption = msg['caption'].upper()
                                # Try to extract symbol
                                for symbol in ['BTC', 'ETH', 'SOL', 'PENGU', 'XRP', 'DOGE']:
                                    if symbol in caption:
                                        print(f"   📊 Symbol detected: {symbol}")
                                        break
                        
                        if 'text' in msg:
                            print(f"   Text: {msg['text'][:100]}")
                        
                        print("-"*40)
        else:
            print("❌ No updates found")
            print("\nTo receive images:")
            print("1. Send the KingFisher image to @ZmartTradingBot")
            print("2. Or forward the image from KingFisher channel to the bot")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    check_your_messages()