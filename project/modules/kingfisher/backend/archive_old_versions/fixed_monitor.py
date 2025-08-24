#!/usr/bin/env python3
"""
FIXED MONITOR - Corrected async handling
"""

import asyncio
from telethon import TelegramClient, events
from datetime import datetime
import requests

# Credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable
BASE_URL = "https://api.airtable.com/v0/appAs9sZH7OmtYaTJ/tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'

print("="*50)
print("FIXED KINGFISHER MONITOR")
print("="*50)

client = TelegramClient('fresh_session', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):  # Make sure it's async
    """Handle new messages"""
    if event.photo:
        print(f"\n🖼️ IMAGE DETECTED at {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Get chat info
            chat = await event.get_chat()
            chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
            print(f"📍 From: {chat_name}")
            
            # Download
            filename = f"kingfisher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            await event.download_media(filename)
            print(f"💾 Saved: {filename}")
            
            # Extract symbol from caption
            caption = (event.text or "").upper()
            symbol = "ETH"  # default
            
            for s in ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'DOT', 'AVAX']:
                if s in caption:
                    symbol = s
                    break
            
            print(f"📊 Symbol: {symbol}")
            
            # Determine field type
            field = "Liquidation_Map"  # default
            if "RSI" in caption and "HEATMAP" in caption:
                field = "RSI_Heatmap"
            elif "LONG" in caption and "TERM" in caption:
                field = "LiqRatios_long_term"
            elif "SHORT" in caption and "TERM" in caption:
                field = "LiqRatios_short_term"
            
            print(f"📁 Field: {field}")
            
            # Update Airtable
            headers = {
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json'
            }
            
            timestamp = datetime.now().isoformat()
            
            data = {
                'fields': {
                    'Symbol': symbol,
                    field: f'KingFisher {symbol} analysis - {timestamp}',
                    'MarketPrice': 100.0,
                    'Last_update': timestamp
                }
            }
            
            response = requests.post(BASE_URL, headers=headers, json=data)
            
            if response.status_code == 200:
                print("✅ SAVED TO AIRTABLE!")
                print(f"✅ Check Airtable: {symbol} in {field}")
            else:
                print(f"❌ Airtable error: {response.status_code}")
                # If create failed, try to update existing
                if response.status_code == 422:
                    print("Trying to update existing record...")
                    # Get existing record
                    params = {'filterByFormula': f"{{Symbol}} = '{symbol}'"}
                    get_response = requests.get(BASE_URL, headers=headers, params=params)
                    
                    if get_response.status_code == 200 and get_response.json().get('records'):
                        record_id = get_response.json()['records'][0]['id']
                        update_response = requests.patch(
                            f"{BASE_URL}/{record_id}",
                            headers=headers,
                            json={'fields': data['fields']}
                        )
                        if update_response.status_code == 200:
                            print("✅ Updated existing record!")
                        else:
                            print(f"Update failed: {update_response.text[:200]}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("="*50)

async def main():
    """Main function"""
    await client.start()
    
    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name} (@{me.username})")
    
    print("\n" + "="*50)
    print("🟢 MONITOR ACTIVE")
    print("="*50)
    print("📸 Generate your KingFisher image now!")
    print("The monitor will:")
    print("  • Detect the image")
    print("  • Download it")
    print("  • Save to Airtable")
    print("-"*50)
    print("Waiting for images...")
    
    await client.run_until_disconnected()

# Run the async function properly
asyncio.run(main())