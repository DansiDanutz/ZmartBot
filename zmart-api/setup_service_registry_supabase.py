#!/usr/bin/env python3
"""
Setup Service Registry Table in Supabase
Creates the service registry table and related tables in Supabase
"""

import os
import sys
import asyncio
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://asjtxrmftmutcsnqgidy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM"

async def setup_service_registry_tables():
    """Set up service registry tables in Supabase"""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized")
        
        # Read the SQL script
        sql_file = "database/create_service_registry_table.sql"
        if not os.path.exists(sql_file):
            print(f"❌ SQL file not found: {sql_file}")
            return False
        
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        print("📋 SQL script loaded")
        
        # Split the SQL script into individual statements
        statements = []
        current_statement = ""
        
        for line in sql_script.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                current_statement += line + " "
                if line.endswith(';'):
                    statements.append(current_statement.strip())
                    current_statement = ""
        
        print(f"🔧 Found {len(statements)} SQL statements to execute")
        
        # Execute each statement
        success_count = 0
        for i, statement in enumerate(statements, 1):
            try:
                print(f"📝 Executing statement {i}/{len(statements)}...")
                
                # Execute the SQL statement
                result = supabase.rpc('exec', {
                    'sql': statement
                }).execute()
                
                print(f"✅ Statement {i} executed successfully")
                success_count += 1
                
            except Exception as e:
                print(f"❌ Statement {i} failed: {e}")
                # Continue with other statements
        
        print(f"🎯 Setup completed: {success_count}/{len(statements)} statements successful")
        
        # Verify the tables were created
        print("🔍 Verifying table creation...")
        
        # Check service_registry table
        try:
            result = supabase.table('service_registry').select('count', count='exact').execute()
            print("✅ service_registry table exists")
        except Exception as e:
            print(f"❌ service_registry table not found: {e}")
        
        # Check service_lifecycle table
        try:
            result = supabase.table('service_lifecycle').select('count', count='exact').execute()
            print("✅ service_lifecycle table exists")
        except Exception as e:
            print(f"❌ service_lifecycle table not found: {e}")
        
        # Check service_health_metrics table
        try:
            result = supabase.table('service_health_metrics').select('count', count='exact').execute()
            print("✅ service_health_metrics table exists")
        except Exception as e:
            print(f"❌ service_health_metrics table not found: {e}")
        
        # Check service_connections table
        try:
            result = supabase.table('service_connections').select('count', count='exact').execute()
            print("✅ service_connections table exists")
        except Exception as e:
            print(f"❌ service_connections table not found: {e}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

async def test_service_registry_sync():
    """Test the service registry sync functionality"""
    try:
        print("🧪 Testing service registry sync...")
        
        # Import the database service
        sys.path.append('database')
        from database_service import DatabaseService
        
        # Create a temporary database service instance
        db_service = DatabaseService(port=8901)  # Use different port for testing
        
        # Test getting service registry data
        services_data = await db_service.get_service_registry_data()
        print(f"📊 Found {len(services_data)} services in registry")
        
        # Show some sample data
        for i, service in enumerate(services_data[:5]):
            print(f"  {i+1}. {service['service_name']} - {service.get('certification_status', 'UNKNOWN')}")
        
        return len(services_data) > 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 Setting up Service Registry in Supabase...")
    print("=" * 50)
    
    # Step 1: Setup tables
    print("Step 1: Creating service registry tables...")
    setup_success = await setup_service_registry_tables()
    
    if setup_success:
        print("\n✅ Service registry tables created successfully!")
    else:
        print("\n❌ Failed to create service registry tables")
        return
    
    # Step 2: Test sync functionality
    print("\nStep 2: Testing service registry sync...")
    test_success = await test_service_registry_sync()
    
    if test_success:
        print("\n✅ Service registry sync test passed!")
    else:
        print("\n❌ Service registry sync test failed")
    
    print("\n" + "=" * 50)
    print("🎯 Service Registry Supabase Setup Complete!")
    print("\nNext steps:")
    print("1. Restart the database service to enable new endpoints")
    print("2. Use POST /api/services/sync-to-supabase to sync data")
    print("3. Use GET /api/services/registry/supabase to view data")

if __name__ == "__main__":
    asyncio.run(main())
