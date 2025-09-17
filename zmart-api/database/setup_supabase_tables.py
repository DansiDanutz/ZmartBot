#!/usr/bin/env python3
"""
Supabase Tables Setup Script
Creates the necessary tables for ZmartBot service registry in Supabase
"""

import os
import sys
from supabase import create_client, Client
import json

# Supabase configuration
SUPABASE_URL = "https://asjtxrmftmutcsnqgidy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM"

def create_supabase_client() -> Client:
    """Create and return Supabase client"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client created successfully")
        return supabase
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return None

def execute_sql_via_http(sql: str) -> bool:
    """Execute SQL via HTTP request to Supabase"""
    import requests
    
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {"sql": sql}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Response: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ HTTP request failed: {e}")
        return False

def create_tables_manually():
    """Create tables using direct HTTP requests"""
    print("🔧 Creating tables manually via HTTP...")
    
    # Service Registry table
    service_registry_sql = """
    CREATE TABLE IF NOT EXISTS service_registry (
        id SERIAL PRIMARY KEY,
        service_name VARCHAR(255) NOT NULL UNIQUE,
        service_type VARCHAR(100) DEFAULT 'unknown',
        port INTEGER,
        status VARCHAR(50) DEFAULT 'ACTIVE',
        passport_id VARCHAR(100),
        certificate_id VARCHAR(100),
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_health_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        health_score INTEGER DEFAULT 100,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Database Registry table
    database_registry_sql = """
    CREATE TABLE IF NOT EXISTS database_registry (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        path TEXT NOT NULL,
        size_bytes BIGINT DEFAULT 0,
        table_count INTEGER DEFAULT 0,
        row_count INTEGER DEFAULT 0,
        health_score INTEGER DEFAULT 0,
        category VARCHAR(100) DEFAULT 'unknown',
        last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sync_status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Service Lifecycle table
    service_lifecycle_sql = """
    CREATE TABLE IF NOT EXISTS service_lifecycle (
        id SERIAL PRIMARY KEY,
        service_name VARCHAR(255) NOT NULL,
        event_type VARCHAR(50) NOT NULL,
        event_data JSONB,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Service Health Metrics table
    service_health_sql = """
    CREATE TABLE IF NOT EXISTS service_health_metrics (
        id SERIAL PRIMARY KEY,
        service_name VARCHAR(255) NOT NULL,
        health_score INTEGER NOT NULL,
        response_time_ms INTEGER,
        uptime_percentage DECIMAL(5,2),
        error_count INTEGER DEFAULT 0,
        last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Service Connections table
    service_connections_sql = """
    CREATE TABLE IF NOT EXISTS service_connections (
        id SERIAL PRIMARY KEY,
        source_service VARCHAR(255) NOT NULL,
        target_service VARCHAR(255) NOT NULL,
        connection_type VARCHAR(50) DEFAULT 'api',
        status VARCHAR(50) DEFAULT 'active',
        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    tables = [
        ("service_registry", service_registry_sql),
        ("database_registry", database_registry_sql),
        ("service_lifecycle", service_lifecycle_sql),
        ("service_health_metrics", service_health_sql),
        ("service_connections", service_connections_sql)
    ]
    
    for table_name, sql in tables:
        print(f"📋 Creating {table_name} table...")
        if execute_sql_via_http(sql):
            print(f"✅ {table_name} table created successfully")
        else:
            print(f"❌ Failed to create {table_name} table")

def test_table_access():
    """Test if tables are accessible"""
    print("🧪 Testing table access...")
    
    # Test service_registry table
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/service_registry?select=count",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )
        if response.status_code == 200:
            print("✅ service_registry table is accessible")
        else:
            print(f"❌ service_registry table not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing service_registry: {e}")

def main():
    """Main function"""
    print("🚀 Starting Supabase tables setup...")
    
    # Try to create tables
    create_tables_manually()
    
    # Test access
    test_table_access()
    
    print("✅ Setup complete!")

if __name__ == "__main__":
    main()
