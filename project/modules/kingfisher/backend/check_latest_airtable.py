#!/usr/bin/env python3
"""
Check latest Airtable updates
"""

import requests
import json
from datetime import datetime

# Airtable config
BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

print("="*60)
print("🔍 CHECKING LATEST AIRTABLE UPDATES")
print("="*60)

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Get all records, sorted by most recent
params = {
    'maxRecords': 10,
    'sort[0][field]': 'Symbol',
    'sort[0][direction]': 'asc'
}

response = requests.get(BASE_URL, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    records = data.get('records', [])
    
    if records:
        print(f"\n✅ Found {len(records)} records\n")
        
        for record in records:
            fields = record.get('fields', {})
            symbol = fields.get('Symbol', 'N/A')
            
            print(f"📊 {symbol}")
            print(f"   Market Price: {fields.get('MarketPrice', 'N/A')}")
            print(f"   24h-48h: {fields.get('24h48h', 'N/A')}")
            print(f"   7 Days: {fields.get('7days', 'N/A')}")
            print(f"   1 Month: {fields.get('1Month', 'N/A')}")
            
            # Check if has liquidation map
            liq_map = fields.get('Liquidation_Map', '')
            if liq_map:
                print(f"   📝 Report: {len(liq_map)} characters")
                # Check if recently updated (look for today's date in report)
                today = datetime.now().strftime('%Y-%m-%d')
                if today in liq_map:
                    print(f"   ✅ UPDATED TODAY!")
            
            print("-"*40)
    else:
        print("❌ No records found")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

print("\n🔗 View in Airtable:")
print(f"https://airtable.com/{BASE_ID}/{TABLE_ID}/viwGUti60TnU6GWXh")
print("="*60)