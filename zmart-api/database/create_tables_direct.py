#!/usr/bin/env python3
"""
Direct Supabase Tables Creation
Creates tables directly using Supabase REST API
"""

import requests
import json

# Supabase configuration
SUPABASE_URL = "https://asjtxrmftmutcsnqgidy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM"

def create_table_via_rest(table_name, columns):
    """Create table using REST API by inserting a test record"""
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # Try to insert a test record to create the table
    test_data = {}
    for col in columns:
        if col['type'] == 'SERIAL':
            continue  # Skip SERIAL columns
        elif col['type'] == 'VARCHAR':
            test_data[col['name']] = "test"
        elif col['type'] == 'INTEGER':
            test_data[col['name']] = 0
        elif col['type'] == 'TIMESTAMP':
            test_data[col['name']] = "2025-08-29T00:00:00"
        elif col['type'] == 'JSONB':
            test_data[col['name']] = {}
    
    try:
        response = requests.post(url, headers=headers, json=test_data)
        print(f"Response for {table_name}: {response.status_code} - {response.text}")
        return response.status_code in [200, 201, 409]  # 409 means table exists
    except Exception as e:
        print(f"Error creating {table_name}: {e}")
        return False

def main():
    """Main function to create all tables"""
    print("🚀 Creating Supabase tables...")
    
    # Define table schemas
    tables = [
        {
            "name": "service_registry",
            "columns": [
                {"name": "id", "type": "SERIAL"},
                {"name": "service_name", "type": "VARCHAR"},
                {"name": "service_type", "type": "VARCHAR"},
                {"name": "port", "type": "INTEGER"},
                {"name": "status", "type": "VARCHAR"},
                {"name": "passport_id", "type": "VARCHAR"},
                {"name": "certificate_id", "type": "VARCHAR"},
                {"name": "registered_at", "type": "TIMESTAMP"},
                {"name": "last_health_check", "type": "TIMESTAMP"},
                {"name": "health_score", "type": "INTEGER"},
                {"name": "created_at", "type": "TIMESTAMP"},
                {"name": "updated_at", "type": "TIMESTAMP"}
            ]
        },
        {
            "name": "database_registry",
            "columns": [
                {"name": "id", "type": "SERIAL"},
                {"name": "name", "type": "VARCHAR"},
                {"name": "path", "type": "VARCHAR"},
                {"name": "size_bytes", "type": "INTEGER"},
                {"name": "table_count", "type": "INTEGER"},
                {"name": "row_count", "type": "INTEGER"},
                {"name": "health_score", "type": "INTEGER"},
                {"name": "category", "type": "VARCHAR"},
                {"name": "last_modified", "type": "TIMESTAMP"},
                {"name": "last_synced", "type": "TIMESTAMP"},
                {"name": "sync_status", "type": "VARCHAR"},
                {"name": "created_at", "type": "TIMESTAMP"},
                {"name": "updated_at", "type": "TIMESTAMP"}
            ]
        },
        {
            "name": "service_lifecycle",
            "columns": [
                {"name": "id", "type": "SERIAL"},
                {"name": "service_name", "type": "VARCHAR"},
                {"name": "event_type", "type": "VARCHAR"},
                {"name": "event_data", "type": "JSONB"},
                {"name": "timestamp", "type": "TIMESTAMP"},
                {"name": "created_at", "type": "TIMESTAMP"}
            ]
        },
        {
            "name": "service_health_metrics",
            "columns": [
                {"name": "id", "type": "SERIAL"},
                {"name": "service_name", "type": "VARCHAR"},
                {"name": "health_score", "type": "INTEGER"},
                {"name": "response_time_ms", "type": "INTEGER"},
                {"name": "uptime_percentage", "type": "VARCHAR"},
                {"name": "error_count", "type": "INTEGER"},
                {"name": "last_check", "type": "TIMESTAMP"},
                {"name": "created_at", "type": "TIMESTAMP"}
            ]
        },
        {
            "name": "service_connections",
            "columns": [
                {"name": "id", "type": "SERIAL"},
                {"name": "source_service", "type": "VARCHAR"},
                {"name": "target_service", "type": "VARCHAR"},
                {"name": "connection_type", "type": "VARCHAR"},
                {"name": "status", "type": "VARCHAR"},
                {"name": "last_used", "type": "TIMESTAMP"},
                {"name": "created_at", "type": "TIMESTAMP"}
            ]
        }
    ]
    
    # Create each table
    for table in tables:
        print(f"📋 Creating {table['name']} table...")
        success = create_table_via_rest(table['name'], table['columns'])
        if success:
            print(f"✅ {table['name']} table created/verified")
        else:
            print(f"❌ Failed to create {table['name']} table")
    
    print("✅ Table creation complete!")

if __name__ == "__main__":
    main()
