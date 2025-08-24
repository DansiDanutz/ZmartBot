#!/usr/bin/env python3
"""
Clean up duplicate ETH records from Airtable
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
print("🧹 CLEANING UP DUPLICATE ETH RECORDS")
print("="*60)

# Get all records
response = requests.get(BASE_URL, headers=headers)

if response.status_code == 200:
    data = response.json()
    records = data.get('records', [])
    
    print(f"Found {len(records)} total records")
    
    # Find ETH records
    eth_records = []
    for record in records:
        if record['fields'].get('Symbol') == 'ETH':
            eth_records.append(record)
    
    print(f"Found {len(eth_records)} ETH records")
    
    if len(eth_records) > 1:
        print("\nDeleting duplicate ETH records...")
        
        # Keep only the first one, delete the rest
        for record in eth_records[1:]:
            record_id = record['id']
            delete_url = f"{BASE_URL}?records[]={record_id}"
            
            del_response = requests.delete(delete_url, headers=headers)
            
            if del_response.status_code == 200:
                print(f"✅ Deleted duplicate: {record_id}")
            else:
                print(f"❌ Failed to delete: {record_id}")
        
        print(f"\n✅ Cleanup complete! Kept 1 ETH record, deleted {len(eth_records)-1} duplicates")
    else:
        print("✅ No duplicates found")
    
    # Show remaining records
    print("\n📊 Remaining records:")
    response = requests.get(BASE_URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        records = data.get('records', [])
        for record in records:
            print(f"  • {record['fields'].get('Symbol', 'N/A')}")
    
else:
    print(f"Error: {response.status_code}")