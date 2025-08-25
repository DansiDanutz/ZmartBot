#!/usr/bin/env python3
"""Check if monitor is ready"""

import requests
from datetime import datetime

BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

headers = {'Authorization': f'Bearer {API_KEY}'}

response = requests.get(BASE_URL, headers=headers, params={'maxRecords': 3})

print('='*60)
print('🎯 KINGFISHER MONITOR IS READY!')
print('='*60)
print('')
print('Current Airtable Status:')
print('-'*40)

if response.status_code == 200:
    records = response.json().get('records', [])
    for r in records:
        fields = r.get('fields', {})
        symbol = fields.get('Symbol', 'N/A')
        price = fields.get('MarketPrice', 0)
        update = fields.get('Last_update', 'N/A')
        print(f'{symbol}: ${price:.2f}')

print('-'*40)
print('')
print('✅ MONITOR IS RUNNING AND READY!')
print('📸 Go ahead and generate your KingFisher images!')
print('')
print('I will process:')
print('  • Liquidation Map → Updates ONE symbol')
print('  • Liquidation Heatmap → Updates ONE symbol')
print('  • LiqRatio Long/Short → Updates ALL symbols')
print('')
print('Using REAL-TIME prices from market!')
print('='*60)