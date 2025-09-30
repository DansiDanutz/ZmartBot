#!/usr/bin/env python3
"""
Check Airtable Fields
Examines existing records to see what fields are available
"""

import asyncio
import httpx
import json

async def check_airtable_fields():
    """Check what fields exist in the Airtable table"""
    
    print("🔍 Checking Airtable Fields")
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
        try:
            response = await client.get(f"https://api.airtable.com/v0/{base_id}/{table_name}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                print(f"✅ Retrieved {len(records)} records")
                
                if records:
                    print("\n📋 Available Fields:")
                    # Get fields from the first record
                    first_record = records[0]
                    fields = first_record.get('fields', {})
                    
                    for field_name, field_value in fields.items():
                        print(f"   • {field_name}: {type(field_value).__name__}")
                    
                    print(f"\n📋 Sample Record:")
                    print(f"   Symbol: {fields.get('Symbol', 'N/A')}")
                    print(f"   MarketPrice: {fields.get('MarketPrice', 'N/A')}")
                    print(f"   Liquidation_Map: {fields.get('Liquidation_Map', 'N/A')}")
                    print(f"   LiqRatios_long_term: {fields.get('LiqRatios_long_term', 'N/A')}")
                    print(f"   LiqRatios_short_term: {fields.get('LiqRatios_short_term', 'N/A')}")
                    print(f"   RSI_Heatmap: {fields.get('RSI_Heatmap', 'N/A')}")
                    
                    # Check for heatmap-related fields
                    heatmap_fields = [k for k in fields.keys() if 'heatmap' in k.lower() or 'heat' in k.lower()]
                    if heatmap_fields:
                        print(f"\n🔥 Heatmap-related fields:")
                        for field in heatmap_fields:
                            print(f"   • {field}")
                    else:
                        print(f"\n❌ No heatmap-related fields found")
                        
            else:
                print(f"❌ Failed to get records: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error checking fields: {e}")

if __name__ == "__main__":
    asyncio.run(check_airtable_fields()) 