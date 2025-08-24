#!/usr/bin/env python3
"""
Check what's in Airtable
"""

import requests
import json

# Airtable
BASE_URL = "https://api.airtable.com/v0/appAs9sZH7OmtYaTJ/tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

print("="*60)
print("📊 CHECKING AIRTABLE DATA")
print("="*60)

response = requests.get(BASE_URL, headers=headers)

if response.status_code == 200:
    data = response.json()
    records = data.get('records', [])
    
    print(f"Found {len(records)} records:\n")
    
    for record in records:
        fields = record['fields']
        print(f"Symbol: {fields.get('Symbol', 'N/A')}")
        print(f"ID: {record['id']}")
        
        # Check which fields have data
        print("Fields with data:")
        for field_name, value in fields.items():
            if field_name != 'Symbol':
                if value:
                    # Show first 100 chars of value
                    value_str = str(value)[:100]
                    print(f"  • {field_name}: {value_str}...")
        
        print("-"*60)
else:
    print(f"Error: {response.status_code}")
    print(response.text)