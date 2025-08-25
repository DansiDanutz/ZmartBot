#!/usr/bin/env python3
"""
KINGFISHER WORKING VERSION
"""

import asyncio
from telethon.sync import TelegramClient, events
from datetime import datetime
import requests
import sys

# Credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable
BASE_URL = "https://api.airtable.com/v0/appAs9sZH7OmtYaTJ/tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'

print("Starting KingFisher Monitor...")

try:
    with TelegramClient('fresh_session', API_ID, API_HASH) as client:
        print(f"✅ Connected as: {client.get_me().first_name}")
        print("="*50)
        print("READY - Generate your KingFisher image")
        print("="*50)
        
        @client.on(events.NewMessage(incoming=True))
        async def handler(event):
            if event.photo:
                print(f"\n🖼️ IMAGE - {datetime.now().strftime('%H:%M:%S')}")
                
                # Download
                filename = f"kg_{datetime.now().strftime('%H%M%S')}.jpg"
                await event.download_media(filename)
                print(f"Saved: {filename}")
                
                # Detect symbol from caption
                caption = (event.text or "").upper()
                symbol = "ETH"
                
                # Check for symbols
                for s in ['BTC', 'SOL', 'XRP', 'DOGE', 'ADA']:
                    if s in caption:
                        symbol = s
                        break
                
                print(f"Symbol: {symbol}")
                
                # Update Airtable
                headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
                data = {
                    'fields': {
                        'Symbol': symbol,
                        'Liquidation_Map': f'KingFisher {symbol} - {datetime.now()}',
                        'MarketPrice': 100.0,
                        'Last_update': datetime.now().isoformat()
                    }
                }
                
                response = requests.post(BASE_URL, headers=headers, json=data)
                
                if response.status_code == 200:
                    print(f"✅ SAVED: {symbol}")
                else:
                    # Try update
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
                            print(f"✅ UPDATED: {symbol}")
                
                print("="*50)
        
        print("Monitoring... (Press Ctrl+C to stop)")
        client.run_until_disconnected()
        
except Exception as e:
    print(f"Error: {e}")
    print("\nTry running: python fresh_login.py")
    sys.exit(1)