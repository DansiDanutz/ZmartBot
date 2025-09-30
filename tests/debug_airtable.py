#!/usr/bin/env python3
"""
Debug Airtable update issues
"""

import httpx
import json

def debug_airtable_update():
    api_key = "patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835"
    base_id = "appAs9sZH7OmtYaTJ"
    table_name = "KingFisher"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        with httpx.Client() as client:
            # First, let's see what the current record looks like
            response = client.get(
                f"https://api.airtable.com/v0/{base_id}/{table_name}",
                headers=headers,
                params={"filterByFormula": "{Symbol}='ETHUSDT'"}
            )
            
            print("🔍 Current ETHUSDT Record:")
            print("=" * 50)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('records'):
                    record = result['records'][0]
                    print(f"Record ID: {record.get('id')}")
                    print(f"Fields: {json.dumps(record.get('fields', {}), indent=2)}")
                    
                    # Now try to update with a simple test
                    test_data = {
                        "fields": {
                            "Symbol": "ETHUSDT",
                            "Summary": {
                                "test": "This is a test update",
                                "timestamp": "2025-07-29T22:15:00"
                            }
                        }
                    }
                    
                    print(f"\n🔍 Testing Update with Data:")
                    print("=" * 50)
                    print(json.dumps(test_data, indent=2))
                    
                    update_response = client.patch(
                        f"https://api.airtable.com/v0/{base_id}/{table_name}/{record['id']}",
                        headers=headers,
                        json=test_data
                    )
                    
                    print(f"\n📊 Update Response:")
                    print("=" * 50)
                    print(f"Status Code: {update_response.status_code}")
                    print(f"Response: {update_response.text}")
                    
                    if update_response.status_code != 200:
                        print(f"\n❌ Update failed with status {update_response.status_code}")
                        print(f"Error details: {update_response.text}")
                    else:
                        print(f"\n✅ Update successful!")
                        
                else:
                    print("❌ No ETHUSDT record found")
            else:
                print(f"❌ Error getting record: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_airtable_update() 