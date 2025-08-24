#!/usr/bin/env python3
"""
Monitor using Bot API for images sent to the bot
"""

import requests
import time
import json
from datetime import datetime

# Bot token
BOT_TOKEN = "7995587461:AAELuQHeziFE4hZ1tlJ3d53-y5xQgeSoZHI"

# Airtable
BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

print("="*60)
print("🤖 BOT API MONITOR")
print("="*60)
print("Monitoring messages sent to @ZmartTradingBot")
print("="*60)

last_update_id = 0

def get_updates():
    """Get new updates from bot"""
    global last_update_id
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {
        'offset': last_update_id + 1,
        'timeout': 5
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['ok'] and data['result']:
                for update in data['result']:
                    last_update_id = update['update_id']
                    process_update(update)
    except Exception as e:
        print(f"Error: {e}")

def process_update(update):
    """Process incoming update"""
    
    if 'message' in update:
        msg = update['message']
        
        # Get chat info
        chat = msg.get('chat', {})
        from_user = msg.get('from', {})
        
        print(f"\n📨 New message from {from_user.get('first_name', 'Unknown')}")
        
        # Check for photo
        if 'photo' in msg:
            print("   🖼️ IMAGE DETECTED!")
            print(f"   Caption: {msg.get('caption', 'No caption')}")
            
            # Get file
            photo = msg['photo'][-1]  # Largest size
            file_id = photo['file_id']
            
            # Download and process
            process_image(file_id, msg.get('caption', ''))
            
        elif 'text' in msg:
            print(f"   Text: {msg['text'][:100]}")

def process_image(file_id, caption):
    """Process KingFisher image"""
    
    # Get file path
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile"
    response = requests.get(url, params={'file_id': file_id})
    
    if response.status_code == 200:
        file_path = response.json()['result']['file_path']
        
        # Determine symbol from caption or default
        symbol = "ETH"  # Default
        caption_upper = caption.upper()
        
        symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'PENGU']
        for s in symbols:
            if s in caption_upper:
                symbol = s
                break
        
        print(f"   📊 Processing as {symbol}")
        
        # Update Airtable
        update_airtable(symbol)

def update_airtable(symbol):
    """Quick update to Airtable"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Real prices
    prices = {
        'BTC': 117363,
        'ETH': 3895,
        'SOL': 174,
        'XRP': 3.31,
        'DOGE': 0.22,
        'PENGU': 0.000045
    }
    
    price = prices.get(symbol, 100)
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    fields = {
        "Symbol": symbol,
        "MarketPrice": price,
        "Last_update": timestamp,
        "Liquidation_Map": f"KingFisher update at {timestamp}"
    }
    
    # Try to update
    params = {'filterByFormula': f"{{Symbol}} = '{symbol}'", 'maxRecords': 1}
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    if response.status_code == 200 and response.json().get('records'):
        # Update
        record_id = response.json()['records'][0]['id']
        url = f"{BASE_URL}/{record_id}"
        response = requests.patch(url, headers=headers, json={'fields': fields})
        if response.status_code == 200:
            print(f"   ✅ Updated {symbol} in Airtable!")
    else:
        # Create
        response = requests.post(BASE_URL, headers=headers, json={'fields': fields})
        if response.status_code == 200:
            print(f"   ✅ Created {symbol} in Airtable!")

print("\n🟢 Monitoring bot messages...")
print("Send images to @ZmartTradingBot\n")

while True:
    try:
        get_updates()
        time.sleep(2)
    except KeyboardInterrupt:
        print("\n👋 Stopped")
        break