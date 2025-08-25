#!/usr/bin/env python3
"""
QUICK MONITOR - Fast and simple
"""

import asyncio
import requests
import json
from datetime import datetime, timezone
from telethon import TelegramClient, events
import sys

# Your credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable
BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

print("="*60)
print("🚀 QUICK KINGFISHER MONITOR")
print("="*60)

# Use the most recent session
client = TelegramClient('kingfisher_ready', API_ID, API_HASH)

def update_airtable(symbol: str, image_type: str) -> bool:
    """Quick Airtable update"""
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Simple field mapping
    field = "Liquidation_Map"  # Default field
    if "rsi" in image_type.lower():
        field = "RSI_Heatmap"
    elif "long" in image_type.lower():
        field = "LiqRatios_long_term"
    elif "short" in image_type.lower():
        field = "LiqRatios_short_term"
    
    # Create simple report
    report = f"KingFisher {image_type} for {symbol} at {timestamp}"
    
    # Update
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    fields_data = {
        "Symbol": symbol,
        "MarketPrice": 100.0,
        "Last_update": timestamp,
        field: report
    }
    
    try:
        # Try to create new record (simpler)
        response = requests.post(
            BASE_URL,
            headers=headers,
            json={'fields': fields_data}
        )
        
        if response.status_code == 200:
            print(f"✅ Added {symbol} to Airtable field: {field}")
            return True
        else:
            # Try to find and update
            params = {'filterByFormula': f"{{Symbol}} = '{symbol}'"}
            response = requests.get(BASE_URL, headers=headers, params=params)
            
            if response.status_code == 200 and response.json().get('records'):
                record_id = response.json()['records'][0]['id']
                response = requests.patch(
                    f"{BASE_URL}/{record_id}",
                    headers=headers,
                    json={'fields': fields_data}
                )
                if response.status_code == 200:
                    print(f"✅ Updated {symbol} in Airtable field: {field}")
                    return True
        
        print(f"❌ Airtable error: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Handle new messages"""
    try:
        if event.photo:
            print(f"\n🖼️ IMAGE DETECTED at {datetime.now().strftime('%H:%M:%S')}")
            
            # Simple processing
            caption = (event.raw_text or "").upper()
            
            # Guess symbol
            symbol = "ETH"  # default
            for s in ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA']:
                if s in caption:
                    symbol = s
                    break
            
            # Guess type
            image_type = "liquidation_map"
            if "RSI" in caption:
                image_type = "rsi_heatmap"
            elif "LONG" in caption:
                image_type = "long_term"
            elif "SHORT" in caption:
                image_type = "short_term"
            
            print(f"📊 Processing: {symbol} - {image_type}")
            
            # Download
            filename = f"kingfisher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            await event.download_media(filename)
            print(f"💾 Saved: {filename}")
            
            # Update Airtable
            update_airtable(symbol, image_type)
            
            print("="*50)
    except Exception as e:
        print(f"Handler error: {e}")

async def main():
    """Main function with timeout"""
    print("\n🔌 Connecting (10 second timeout)...")
    
    try:
        # Start with timeout
        await asyncio.wait_for(client.start(), timeout=10)
        
        # Check if authorized
        if await client.is_user_authorized():
            print("✅ Connected successfully!")
            
            try:
                me = await asyncio.wait_for(client.get_me(), timeout=5)
                print(f"👤 Logged in as: {me.first_name}")
            except:
                print("👤 Logged in (couldn't get user info)")
            
            print("\n" + "="*60)
            print("🟢 MONITOR ACTIVE")
            print("="*60)
            print("Generate your KingFisher image now!")
            print("Images will be:")
            print("  • Downloaded locally")
            print("  • Stored in Airtable")
            print("-"*60)
            
            # Run forever
            await client.run_until_disconnected()
            
        else:
            print("❌ Not authorized - need to login")
            print("\nQuick fix:")
            print("1. Delete kingfisher_ready.session file")
            print("2. Run: python web_telegram_login.py")
            
    except asyncio.TimeoutError:
        print("❌ Connection timeout!")
        print("\nTry:")
        print("1. Check internet connection")
        print("2. Delete .session files and login again")
        print("3. Try: python web_telegram_login.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTry deleting session files and starting fresh")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Stopped")