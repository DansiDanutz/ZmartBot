#!/usr/bin/env python3
"""
KINGFISHER FINAL - Simple and working
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

client = TelegramClient('fresh_session', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.photo:
        return
    
    print(f"\n{'='*60}")
    print(f"🖼️ IMAGE DETECTED - {datetime.now().strftime('%H:%M:%S')}")
    
    # Get chat
    chat = await event.get_chat()
    chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
    print(f"From: {chat_name}")
    
    # Download
    filename = f"kg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    await event.download_media(filename)
    print(f"Saved: {filename}")
    
    # Get caption to detect symbol
    caption = (event.text or "").upper()
    
    # Detect symbol - check for BTC, SOL, etc.
    symbol = "ETH"  # default
    if "BTC" in caption or "BITCOIN" in caption:
        symbol = "BTC"
    elif "SOL" in caption or "SOLANA" in caption:
        symbol = "SOL"
    elif "XRP" in caption:
        symbol = "XRP"
    
    print(f"Symbol: {symbol}")
    
    # Detect type and field
    field = "Liquidation_Map"  # default
    if "RSI" in caption:
        field = "RSI_Heatmap"
    elif "LONG" in caption and "TERM" in caption:
        field = "LiqRatios_long_term"
    elif "SHORT" in caption and "TERM" in caption:
        field = "LiqRatios_short_term"
    
    print(f"Field: {field}")
    
    # Update Airtable
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    timestamp = datetime.now().isoformat()
    
    # Create data
    data = {
        'fields': {
            'Symbol': symbol,
            field: f'KingFisher {symbol} - {timestamp}',
            'MarketPrice': 100.0,
            'Last_update': timestamp
        }
    }
    
    # Try to create new record
    response = requests.post(BASE_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"✅ SAVED: {symbol} in {field}")
    else:
        # If exists, update it
        params = {'filterByFormula': f"{{Symbol}} = '{symbol}'"}
        get_resp = requests.get(BASE_URL, headers=headers, params=params)
        
        if get_resp.status_code == 200 and get_resp.json().get('records'):
            record_id = get_resp.json()['records'][0]['id']
            update_resp = requests.patch(
                f"{BASE_URL}/{record_id}",
                headers=headers,
                json={'fields': data['fields']}
            )
            if update_resp.status_code == 200:
                print(f"✅ UPDATED: {symbol} in {field}")
            else:
                print(f"❌ Failed: {update_resp.status_code}")
    
    print("="*60)

async def main():
    await client.start()
    me = await client.get_me()
    print(f"Connected as: {me.first_name}")
    print("="*60)
    print("READY - Generate your KingFisher image")
    print("Include symbol in caption (BTC, SOL, etc.)")
    print("="*60)
    await client.run_until_disconnected()

asyncio.run(main())