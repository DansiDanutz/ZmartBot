#!/usr/bin/env python3
"""
SIMPLE MONITOR - Minimal code, maximum reliability
"""

import asyncio
from telethon import TelegramClient, events
from datetime import datetime
import requests
import json

# Credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable
BASE_URL = "https://api.airtable.com/v0/appAs9sZH7OmtYaTJ/tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'

print("="*50)
print("SIMPLE KINGFISHER MONITOR")
print("="*50)

client = TelegramClient('fresh_session', API_ID, API_HASH)

@client.on(events.NewMessage())
async def handler(event):
    """Handle any new message"""
    if event.photo:
        print(f"\n🖼️ IMAGE at {datetime.now().strftime('%H:%M:%S')}")
        
        # Download
        filename = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        await event.download_media(filename)
        print(f"💾 Saved: {filename}")
        
        # Simple Airtable update
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'fields': {
                'Symbol': 'ETH',
                'Liquidation_Map': f'KingFisher image at {datetime.now()}',
                'MarketPrice': 3395.63,
                'Last_update': datetime.now().isoformat()
            }
        }
        
        response = requests.post(BASE_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            print("✅ Saved to Airtable!")
        else:
            print(f"❌ Airtable error: {response.status_code}")
        
        print("="*50)

async def main():
    await client.start()
    print("✅ Connected!")
    print("Waiting for images...")
    await client.run_until_disconnected()

asyncio.run(main())