#!/usr/bin/env python3
"""
Clear all data from Airtable KingFisher table
WARNING: This will delete ALL records - use with caution!
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv
import time

load_dotenv()

# Airtable configuration
BASE_ID = os.getenv("AIRTABLE_BASE_ID", "appAs9sZH7OmtYaTJ")
TABLE_ID = os.getenv("AIRTABLE_TABLE_ID", "tblWxTJClUcLS2E0J")
API_KEY = os.getenv("AIRTABLE_API_KEY", "patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835")
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

async def get_all_records():
    """Fetch all records from Airtable"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    all_records = []
    offset = None
    
    async with httpx.AsyncClient() as client:
        while True:
            params = {}
            if offset:
                params["offset"] = offset
            
            response = await client.get(BASE_URL, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get("records", [])
                all_records.extend(records)
                
                # Check if there are more records
                offset = data.get("offset")
                if not offset:
                    break
                    
                # Rate limit protection
                time.sleep(0.2)
            else:
                print(f"Error fetching records: {response.status_code} - {response.text}")
                break
    
    return all_records

async def delete_records(record_ids):
    """Delete records by their IDs"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    deleted_count = 0
    
    async with httpx.AsyncClient() as client:
        # Airtable allows batch deletion of up to 10 records at a time
        for i in range(0, len(record_ids), 10):
            batch = record_ids[i:i+10]
            
            # Format the delete request
            params = "&".join([f"records[]={rid}" for rid in batch])
            delete_url = f"{BASE_URL}?{params}"
            
            response = await client.delete(delete_url, headers=headers)
            
            if response.status_code == 200:
                deleted_count += len(batch)
                print(f"✅ Deleted batch of {len(batch)} records (Total: {deleted_count}/{len(record_ids)})")
            else:
                print(f"❌ Error deleting batch: {response.status_code} - {response.text}")
            
            # Rate limit protection
            time.sleep(0.2)
    
    return deleted_count

async def clear_all_data():
    """Main function to clear all Airtable data"""
    print("="*60)
    print("🗑️  AIRTABLE DATA CLEANER")
    print("="*60)
    print(f"📊 Base ID: {BASE_ID}")
    print(f"📋 Table ID: {TABLE_ID}")
    print("="*60)
    
    # Fetch all records
    print("\n📥 Fetching all records...")
    records = await get_all_records()
    
    if not records:
        print("✅ No records found - table is already empty!")
        return
    
    print(f"\n📊 Found {len(records)} records")
    
    # Show sample of data to be deleted
    print("\n📋 Sample of records to be deleted:")
    for i, record in enumerate(records[:5]):
        fields = record.get("fields", {})
        symbol = fields.get("Symbol", "Unknown")
        print(f"  - {symbol}")
    
    if len(records) > 5:
        print(f"  ... and {len(records) - 5} more")
    
    # Confirm deletion
    print("\n" + "⚠️ " * 10)
    print("WARNING: This will DELETE ALL RECORDS from the Airtable!")
    print("⚠️ " * 10)
    
    confirm = input("\n❓ Are you sure you want to delete all records? (type 'YES' to confirm): ")
    
    if confirm != "YES":
        print("❌ Deletion cancelled")
        return
    
    # Extract record IDs
    record_ids = [record["id"] for record in records]
    
    # Delete all records
    print(f"\n🗑️  Deleting {len(record_ids)} records...")
    deleted = await delete_records(record_ids)
    
    print("\n" + "="*60)
    print(f"✅ COMPLETE: Deleted {deleted} records")
    print("📋 Airtable table is now empty and ready for fresh data!")
    print("="*60)

async def main():
    """Main entry point"""
    try:
        await clear_all_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Tips:")
        print("  1. Check your API credentials in .env")
        print("  2. Verify the Base ID and Table ID")
        print("  3. Ensure you have write permissions")

if __name__ == "__main__":
    asyncio.run(main())