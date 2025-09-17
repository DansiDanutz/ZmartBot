#!/usr/bin/env python3
"""
Populate Passport Registry Database from Service Registry
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Database paths
SERVICE_REGISTRY_PATH = "zmart-api/src/data/service_registry.db"
PASSPORT_REGISTRY_PATH = "zmart-api/data/passport_registry.db"

def create_passport_registry_table():
    """Create the passport_registry table if it doesn't exist"""
    try:
        conn = sqlite3.connect(PASSPORT_REGISTRY_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passport_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                passport_id TEXT NOT NULL UNIQUE,
                service_name TEXT NOT NULL,
                service_type TEXT NOT NULL,
                port INTEGER NOT NULL,
                status TEXT DEFAULT 'ACTIVE',
                description TEXT,
                metadata JSON,
                created_by TEXT DEFAULT 'SYSTEM',
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Passport registry table created/verified")
        
    except Exception as e:
        print(f"❌ Error creating passport registry table: {e}")

def populate_passport_registry():
    """Populate passport registry from service registry"""
    print("🛂 Populating Passport Registry from Service Registry")
    print("=" * 60)
    
    try:
        # Connect to service registry
        service_conn = sqlite3.connect(SERVICE_REGISTRY_PATH)
        service_cursor = service_conn.cursor()
        
        # Get all services with passport IDs
        service_cursor.execute("""
            SELECT service_name, kind, port, passport_id, status, description, created_at
            FROM service_registry 
            WHERE passport_id IS NOT NULL AND passport_id != 'N/A'
            ORDER BY service_name
        """)
        
        services = service_cursor.fetchall()
        service_conn.close()
        
        print(f"📊 Found {len(services)} services with passport IDs")
        
        # Connect to passport registry
        passport_conn = sqlite3.connect(PASSPORT_REGISTRY_PATH)
        passport_cursor = passport_conn.cursor()
        
        successful = 0
        failed = 0
        
        for service in services:
            service_name, kind, port, passport_id, status, description, created_at = service
            
            try:
                # Check if already exists
                passport_cursor.execute("""
                    SELECT passport_id FROM passport_registry 
                    WHERE service_name = ? OR passport_id = ?
                """, (service_name, passport_id))
                
                existing = passport_cursor.fetchone()
                if existing:
                    print(f"⚠️  {service_name} already exists in passport registry")
                    continue
                
                # Insert service into passport registry
                passport_cursor.execute("""
                    INSERT INTO passport_registry (
                        passport_id, service_name, service_type, port, status, 
                        description, metadata, created_by, registered_at, activated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    passport_id, service_name, kind.upper(), port, status,
                    description or f"{service_name} service",
                    json.dumps({"source": "service_registry", "auto_populated": True}),
                    "SYSTEM", created_at or datetime.now().isoformat(), 
                    datetime.now().isoformat()
                ))
                
                print(f"✅ {service_name} -> {passport_id}")
                successful += 1
                
            except Exception as e:
                print(f"❌ Failed to add {service_name}: {e}")
                failed += 1
        
        # Commit changes
        passport_conn.commit()
        passport_conn.close()
        
        print("\n" + "=" * 60)
        print(f"🎯 Passport Registry Population Complete:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📊 Total Processed: {len(services)}")
        
        # Verify population
        verify_population()
        
    except Exception as e:
        print(f"❌ Error populating passport registry: {e}")

def verify_population():
    """Verify the passport registry was populated correctly"""
    try:
        conn = sqlite3.connect(PASSPORT_REGISTRY_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM passport_registry")
        count = cursor.fetchone()[0]
        
        print(f"\n📋 Verification:")
        print(f"   📊 Total services in passport registry: {count}")
        
        if count > 0:
            print("   ✅ Passport registry successfully populated!")
        else:
            print("   ❌ Passport registry is still empty")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verifying population: {e}")

if __name__ == "__main__":
    create_passport_registry_table()
    populate_passport_registry()
