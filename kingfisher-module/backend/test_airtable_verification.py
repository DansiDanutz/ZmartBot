#!/usr/bin/env python3
"""
Airtable Verification Test
Verifies the Airtable base and table existence
"""

import asyncio
import httpx
import json
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def verify_airtable_setup():
    """Verify Airtable base and table setup"""
    
    print("🔍 Verifying Airtable Setup")
    print("=" * 50)
    
    # Configuration
    base_id = "appAs9sZH7OmtYaTJ"
    api_key = "patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835"
    table_name = "CursorTable"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Check if base exists
        print("\n1️⃣ Checking Base Existence...")
        try:
            response = await client.get(f"https://api.airtable.com/v0/meta/bases/{base_id}/tables", headers=headers)
            if response.status_code == 200:
                tables = response.json()
                print("✅ Base exists and accessible")
                print(f"   Base ID: {base_id}")
                print(f"   Available tables: {[table['name'] for table in tables.get('tables', [])]}")
                
                # Check if CursorTable exists
                table_names = [table['name'] for table in tables.get('tables', [])]
                if table_name in table_names:
                    print(f"✅ Table '{table_name}' exists")
                else:
                    print(f"❌ Table '{table_name}' does not exist")
                    print(f"   Available tables: {table_names}")
                    print("\n🔧 To create the table, go to:")
                    print(f"   https://airtable.com/{base_id}")
                    print("   And create a table named 'CursorTable'")
            else:
                print(f"❌ Base access failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error checking base: {e}")
        
        # Test 2: Try to access the specific table
        print("\n2️⃣ Testing Table Access...")
        try:
            response = await client.get(f"https://api.airtable.com/v0/{base_id}/{table_name}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print("✅ Table accessible")
                print(f"   Records count: {len(data.get('records', []))}")
            elif response.status_code == 404:
                print(f"❌ Table '{table_name}' not found")
                print("   The table needs to be created in the Airtable base")
            else:
                print(f"❌ Table access failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error accessing table: {e}")
        
        # Test 3: Try to create a test record
        print("\n3️⃣ Testing Record Creation...")
        try:
            test_record = {
                "records": [{
                    "fields": {
                        "Image ID": "test_verification_001",
                        "Symbol": "BTCUSDT",
                        "Timestamp": "2025-07-29T19:30:00Z",
                        "Significance Score": 0.85,
                        "Market Sentiment": "bearish",
                        "Confidence": 0.92,
                        "Liquidation Clusters": json.dumps([{"x": 100, "y": 200, "density": 0.8}]),
                        "Toxic Flow": 0.45,
                        "Image Path": "/test/path/image.jpg",
                        "Analysis Data": json.dumps({"test": "verification"}),
                        "Alert Level": "High",
                        "Status": "Active"
                    }
                }]
            }
            
            response = await client.post(
                f"https://api.airtable.com/v0/{base_id}/{table_name}",
                headers=headers,
                json=test_record
            )
            
            if response.status_code == 200:
                print("✅ Test record created successfully")
                result = response.json()
                print(f"   Created record ID: {result.get('records', [{}])[0].get('id', 'N/A')}")
            else:
                print(f"❌ Failed to create test record: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error creating test record: {e}")
        
        print("\n" + "=" * 50)
        print("📋 VERIFICATION SUMMARY")
        print("=" * 50)
        print("🔧 Base ID: appAs9sZH7OmtYaTJ")
        print("📋 Table Name: CursorTable")
        print("🔑 API Key: patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835")
        print("\n🌐 Access your Airtable base at:")
        print(f"   https://airtable.com/{base_id}")
        print("\n📊 If the table doesn't exist, create it with these fields:")
        print("   - Image ID (Single line text)")
        print("   - Symbol (Single line text)")
        print("   - Timestamp (Date)")
        print("   - Significance Score (Number)")
        print("   - Market Sentiment (Single select: Bullish/Bearish/Neutral)")
        print("   - Confidence (Number)")
        print("   - Liquidation Clusters (Long text)")
        print("   - Toxic Flow (Number)")
        print("   - Image Path (Single line text)")
        print("   - Analysis Data (Long text)")
        print("   - Alert Level (Single select: High/Medium/Low)")
        print("   - Status (Single select: Active/Inactive)")

if __name__ == "__main__":
    asyncio.run(verify_airtable_setup()) 