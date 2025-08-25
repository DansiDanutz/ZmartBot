#!/usr/bin/env python3
"""
FINAL MONITOR - Single focused script that works
"""

import asyncio
import requests
import json
from datetime import datetime
from telethon import TelegramClient, events

# Telegram credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable configuration
BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

client = TelegramClient('fresh_session', API_ID, API_HASH)

def update_airtable(symbol, image_type="liquidation_map"):
    """Update or create Airtable record for symbol"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Build report
    report = f"""🎯 KINGFISHER ANALYSIS - {symbol}
Type: {image_type.replace('_', ' ').title()}
Time: {timestamp}
Status: Processed from Telegram"""
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Check if symbol exists
    params = {'filterByFormula': f"{{Symbol}} = '{symbol}'", 'maxRecords': 1}
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    fields = {
        'Symbol': symbol,
        'Liquidation_Map': report,
        'Last_update': timestamp,
        'MarketPrice': 100.0
    }
    
    if response.status_code == 200 and response.json().get('records'):
        # Update existing
        record_id = response.json()['records'][0]['id']
        response = requests.patch(
            f"{BASE_URL}/{record_id}",
            headers=headers,
            json={'fields': fields}
        )
        print(f"✅ Updated {symbol}")
    else:
        # Create new
        response = requests.post(
            BASE_URL,
            headers=headers,
            json={'records': [{'fields': fields}]}
        )
        print(f"✅ Created {symbol}")
    
    return response.status_code in [200, 201]

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Handle incoming messages with images"""
    if not event.photo:
        return
    
    print(f"\n🖼️ Image detected at {datetime.now().strftime('%H:%M:%S')}")
    
    # Download image
    filename = f"kg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    await event.download_media(filename)
    print(f"💾 Saved: {filename}")
    
    # Extract symbol from caption or default
    caption = (event.raw_text or "").upper()
    
    # Check for symbols in caption
    symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'DOT', 'PENGU', 
              'AVAX', 'LINK', 'LTC', 'BNB', 'MATIC', 'UNI', 'ATOM']
    
    detected_symbol = 'ETH'  # default
    for symbol in symbols:
        if symbol in caption:
            detected_symbol = symbol
            break
    
    print(f"🎯 Symbol: {detected_symbol}")
    
    # Update Airtable
    if update_airtable(detected_symbol):
        await event.reply(f"✅ Processed {detected_symbol}")

async def main():
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name}")
    print("🟢 READY - Send images!\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())