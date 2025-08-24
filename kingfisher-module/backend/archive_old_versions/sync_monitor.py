#!/usr/bin/env python3
"""
SYNC MONITOR - Using synchronous approach
"""

from telethon.sync import TelegramClient, events
from datetime import datetime
import requests

# Credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable
BASE_URL = "https://api.airtable.com/v0/appAs9sZH7OmtYaTJ/tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'

print("="*50)
print("SYNC KINGFISHER MONITOR")
print("="*50)

# Use sync client
with TelegramClient('fresh_session', API_ID, API_HASH) as client:
    print("✅ Connected!")
    
    me = client.get_me()
    print(f"✅ Logged in as: {me.first_name} (@{me.username})")
    
    @client.on(events.NewMessage(incoming=True))
    def handler(event):
        if event.photo:
            print(f"\n🖼️ IMAGE at {datetime.now().strftime('%H:%M:%S')}")
            
            # Download
            filename = f"kg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            event.download_media(filename)
            print(f"💾 Saved: {filename}")
            
            # Airtable
            headers = {
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'fields': {
                    'Symbol': 'ETH',
                    'Liquidation_Map': f'KingFisher {datetime.now()}',
                    'MarketPrice': 3395.63,
                    'Last_update': datetime.now().isoformat()
                }
            }
            
            response = requests.post(BASE_URL, headers=headers, json=data)
            
            if response.status_code == 200:
                print("✅ Saved to Airtable!")
            else:
                print(f"❌ Error: {response.status_code}")
            
            print("="*50)
    
    print("\n🟢 READY - Generate your image!")
    print("Press Ctrl+C to stop")
    
    client.run_until_disconnected()