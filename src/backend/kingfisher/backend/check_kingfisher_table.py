#!/usr/bin/env python3
"""
Check KingFisher Table Fields
"""

import asyncio
import httpx
import json

async def check_kingfisher_table():
    """Check the KingFisher table structure"""
    
    print("🔍 Checking KingFisher Table Structure")
    print("=" * 50)
    
    # Configuration
    base_id = "appAs9sZH7OmtYaTJ"
    api_key = "patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835"
    table_name = "KingFisher"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        
        # Get table schema
        print("\n1️⃣ Getting Table Schema...")
        try:
            response = await client.get(f"https://api.airtable.com/v0/meta/bases/{base_id}/tables", headers=headers)
            if response.status_code == 200:
                tables = response.json()
                kingfisher_table = None
                
                for table in tables.get('tables', []):
                    if table['name'] == table_name:
                        kingfisher_table = table
                        break
                
                if kingfisher_table:
                    print("✅ KingFisher table found")
                    print(f"   Table ID: {kingfisher_table.get('id')}")
                    print(f"   Table Name: {kingfisher_table.get('name')}")
                    
                    fields = kingfisher_table.get('fields', [])
                    print(f"\n📊 Available Fields ({len(fields)}):")
                    for field in fields:
                        field_name = field.get('name', 'Unknown')
                        field_type = field.get('type', 'Unknown')
                        print(f"   • {field_name} ({field_type})")
                    
                    # Store field names for reference
                    field_names = [field.get('name') for field in fields]
                    print(f"\n📝 Field names for API: {field_names}")
                    
                else:
                    print("❌ KingFisher table not found")
            else:
                print(f"❌ Failed to get table schema: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error getting table schema: {e}")
        
        # Try to get existing records
        print("\n2️⃣ Getting Existing Records...")
        try:
            response = await client.get(f"https://api.airtable.com/v0/{base_id}/{table_name}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                print(f"✅ Found {len(records)} existing records")
                
                if records:
                    print("\n📋 Sample Record Structure:")
                    sample_record = records[0]
                    fields = sample_record.get('fields', {})
                    for field_name, field_value in fields.items():
                        print(f"   • {field_name}: {field_value}")
            else:
                print(f"❌ Failed to get records: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error getting records: {e}")

if __name__ == "__main__":
    asyncio.run(check_kingfisher_table()) 