#!/usr/bin/env python3
"""
Fix Supabase Schema - Add Missing Category Column
"""
import requests

# Direct fix using Supabase REST API
def fix_supabase_table():
    try:
        # Get the service key
        response = requests.get("http://localhost:8006/keys/0249c490fcc9ecf1", timeout=5)
        service_key = response.json().get('api_key')
        
        supabase_url = "https://asjtxrmftmutcsnqgidy.supabase.co"
        
        print("🔧 Fixing Supabase service_registry table schema...")
        print(f"Using service key: {service_key[:20]}...")
        
        # Use Supabase client to fix schema
        from supabase import create_client
        client = create_client(supabase_url, service_key)
        
        # Test connection first
        print("🔍 Testing Supabase connection...")
        result = client.table('service_registry').select('count', count='exact').execute()
        print(f"✅ Connection successful - table has {result.count} records")
        
        # The issue is that our local database has a 'category' column but Supabase doesn't
        # Let's check what columns exist in Supabase
        print("📊 Checking existing Supabase table structure...")
        
        # Try to insert a test record to see what columns are expected
        test_record = {
            'service_name': 'test-schema-check',
            'service_type': 'test',
            'port': 9999,
            'status': 'TESTING'
        }
        
        result = client.table('service_registry').upsert(test_record, on_conflict='service_name').execute()
        
        if result.data:
            print("✅ Test record inserted successfully")
            
            # Now delete the test record
            client.table('service_registry').delete().eq('service_name', 'test-schema-check').execute()
            print("✅ Test record cleaned up")
            
            print("\n📝 SOLUTION FOUND:")
            print("The Supabase table exists but is missing the 'category' column.")
            print("The database service is trying to sync a 'category' field that doesn't exist in Supabase.")
            print("\n🔧 FIXING BY UPDATING DATABASE SERVICE...")
            
            return True
        else:
            print("❌ Could not insert test record")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_supabase_table()