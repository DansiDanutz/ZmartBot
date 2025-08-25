#!/usr/bin/env python3
"""
RUN MONITOR - Simple and working
"""

from telethon.sync import TelegramClient, events
from datetime import datetime
import requests
import json

# Credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable
BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

print("="*60)
print("KINGFISHER MONITOR")
print("="*60)

with TelegramClient('fresh_session', API_ID, API_HASH) as client:
    me = client.get_me()
    print(f"✅ Connected as: {me.first_name}")
    
    @client.on(events.NewMessage(incoming=True))
    def handler(event):
        if event.photo:
            print(f"\n🖼️ IMAGE at {datetime.now().strftime('%H:%M:%S')}")
            
            # Download
            filename = f"kg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            event.download_media(filename)
            print(f"💾 Saved: {filename}")
            
            # Extract text
            text = (event.text or "").upper()
            
            # Detect symbol
            symbol = "ETH"
            for s in ['BTC', 'SOL', 'XRP', 'DOGE', 'ADA', 'DOT', 'PENGU']:
                if s in text:
                    symbol = s
                    break
            
            # Detect field
            field = "Liquidation_Map"
            if "RSI" in text:
                field = "RSI_Heatmap"
            elif "LONG" in text and "TERM" in text:
                field = "LiqRatios_long_term"
            elif "SHORT" in text and "TERM" in text:
                field = "LiqRatios_short_term"
            
            print(f"Symbol: {symbol}, Field: {field}")
            
            # Update Airtable
            headers = {
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'fields': {
                    'Symbol': symbol,
                    field: f'KingFisher {symbol} - {datetime.now()}',
                    'MarketPrice': 100.0,
                    'Last_update': datetime.now().isoformat()
                }
            }
            
            # Try to create
            response = requests.post(BASE_URL, headers=headers, json=data)
            
            if response.status_code == 200:
                print(f"✅ Created {symbol} in {field}")
            else:
                # Try to update
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
                        print(f"✅ Updated {symbol} in {field}")
            
            print("="*60)
    
    print("\n🟢 READY - Generate your KingFisher image!")
    print("="*60)
    
    client.run_until_disconnected()