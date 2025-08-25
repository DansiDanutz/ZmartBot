#!/usr/bin/env python3
"""
Check Airtable schema - what fields exist
"""

import asyncio
import httpx
import json

# Airtable
BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
API_KEY = "patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835"

async def check_schema():
    """Get the actual fields from Airtable"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("Checking Airtable fields...")
    
    # First, try to get the schema
    async with httpx.AsyncClient() as client:
        # Get one record to see the fields
        response = await client.get(
            f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}",
            headers=headers,
            params={"maxRecords": 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Try to create a dummy record to see error message with field names
            test_data = {
                "records": [{
                    "fields": {
                        "Symbol": "TEST",
                        "Last_Updated": "test"  # This will fail and show us valid fields
                    }
                }]
            }
            
            response2 = await client.post(
                f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}",
                headers=headers,
                json=test_data
            )
            
            print(f"Error response: {response2.text}")
            
            # Now try with correct fields based on what we know
            test_data2 = {
                "records": [{
                    "fields": {
                        "Symbol": "TEST",
                        "Liquidation_Map": "Test data",
                        "LiqRatios_long_term": "Test",
                        "LiqRatios_short_term": "Test",
                        "RSI_Heatmap": "Test",
                        "Liquidation_Heatmap": "Test"
                    }
                }]
            }
            
            response3 = await client.post(
                f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}",
                headers=headers,
                json=test_data2
            )
            
            if response3.status_code in [200, 201]:
                print("✅ Successfully created test record with these fields:")
                print("- Symbol")
                print("- Liquidation_Map")
                print("- LiqRatios_long_term")
                print("- LiqRatios_short_term")
                print("- RSI_Heatmap")
                print("- Liquidation_Heatmap")
                
                # Delete the test record
                result = response3.json()
                if result.get("records"):
                    record_id = result["records"][0]["id"]
                    await client.delete(
                        f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}?records[]={record_id}",
                        headers=headers
                    )
                    print("✅ Test record deleted")
            else:
                print(f"Field test failed: {response3.text}")

asyncio.run(check_schema())