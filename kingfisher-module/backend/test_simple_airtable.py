#!/usr/bin/env python3
"""
Simple Airtable Test
Tests with minimal fields to avoid validation issues
"""

import asyncio
import httpx
import json
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_simple_airtable():
    """Test Airtable with minimal fields"""
    
    print("🧪 Simple Airtable Test")
    print("=" * 40)
    
    # Configuration
    base_id = "appAs9sZH7OmtYaTJ"
    api_key = "patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835"
    table_name = "KingFisher"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Store minimal record
        print("\n1️⃣ Testing Minimal Record...")
        try:
            minimal_record = {
                "records": [{
                    "fields": {
                        "Symbol": "BTCUSDT"
                    }
                }]
            }
            
            response = await client.post(
                f"https://api.airtable.com/v0/{base_id}/{table_name}",
                headers=headers,
                json=minimal_record
            )
            
            if response.status_code == 200:
                print("✅ Minimal record created successfully")
                result = response.json()
                print(f"   Record ID: {result.get('records', [{}])[0].get('id', 'N/A')}")
            else:
                print(f"❌ Failed to create minimal record: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error creating minimal record: {e}")
        
        # Test 2: Store record with text fields
        print("\n2️⃣ Testing Text Fields...")
        try:
            text_record = {
                "records": [{
                    "fields": {
                        "Symbol": "ETHUSDT",
                        "Liquidation_Map": "Test liquidation map data",
                        "LiqRatios_long_term": "0.75, 0.82, 0.91",
                        "LiqRatios_short_term": "0.45, 0.52, 0.68",
                        "RSI_Heatmap": "RSI heatmap data for ETHUSDT",
                        "Lie_Heatmap": "Liquidation heatmap data for ETHUSDT"
                    }
                }]
            }
            
            response = await client.post(
                f"https://api.airtable.com/v0/{base_id}/{table_name}",
                headers=headers,
                json=text_record
            )
            
            if response.status_code == 200:
                print("✅ Text record created successfully")
                result = response.json()
                print(f"   Record ID: {result.get('records', [{}])[0].get('id', 'N/A')}")
            else:
                print(f"❌ Failed to create text record: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error creating text record: {e}")
        
        # Test 3: Get existing records
        print("\n3️⃣ Getting Existing Records...")
        try:
            response = await client.get(f"https://api.airtable.com/v0/{base_id}/{table_name}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                print(f"✅ Retrieved {len(records)} records")
                
                if records:
                    print("\n📋 Latest Records:")
                    for i, record in enumerate(records[-3:], 1):  # Show last 3 records
                        fields = record.get('fields', {})
                        symbol = fields.get('Symbol', 'Unknown')
                        print(f"   {i}. {symbol} (ID: {record.get('id', 'N/A')})")
            else:
                print(f"❌ Failed to get records: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error getting records: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_airtable()) 