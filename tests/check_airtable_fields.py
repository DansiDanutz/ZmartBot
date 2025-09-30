#!/usr/bin/env python3
"""
Check Airtable fields to understand the actual schema
"""

import httpx
import json

def check_airtable_fields():
    api_key = "patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835"
    base_id = "appAs9sZH7OmtYaTJ"
    table_name = "KingFisher"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        with httpx.Client() as client:
            # Get a sample record to see all fields
            response = client.get(
                f"https://api.airtable.com/v0/{base_id}/{table_name}",
                headers=headers,
                params={"maxRecords": 1}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('records'):
                    record = result['records'][0]
                    fields = record.get('fields', {})
                    
                    print("📊 Available Airtable Fields:")
                    print("=" * 40)
                    
                    for field_name, field_value in fields.items():
                        print(f"✅ {field_name}: {type(field_value).__name__}")
                        if isinstance(field_value, str) and len(field_value) > 100:
                            print(f"   Preview: {field_value[:100]}...")
                        else:
                            print(f"   Value: {field_value}")
                    
                    print(f"\n📝 Total fields: {len(fields)}")
                    print(f"🆔 Record ID: {record.get('id')}")
                    
                    # Check for specific fields we need
                    required_fields = [
                        "Symbol", "Liquidation_Map", "LiqRatios_long_term", 
                        "LiqRatios_short_term", "RSI_Heatmap", "Liq_Heatmap", 
                        "Result", "24h48h", "7days", "1Month", 
                        "Score(24h48h_7Days_1Month)"
                    ]
                    
                    print(f"\n🔍 Checking Required Fields:")
                    print("=" * 40)
                    
                    for field in required_fields:
                        if field in fields:
                            print(f"✅ {field}")
                        else:
                            print(f"❌ {field} - MISSING")
                    
                else:
                    print("❌ No records found in table")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_airtable_fields() 