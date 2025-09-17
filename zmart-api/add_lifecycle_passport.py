#!/usr/bin/env python3
"""
Add ServiceLifecycleManager to passport registry with port assignment
"""

import sqlite3
import os
from datetime import datetime
import uuid

def add_lifecycle_manager_to_passport():
    """Add ServiceLifecycleManager to passport registry"""
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Connect to passport registry database
    passport_db_path = 'data/passport_registry.db'
    
    # Create the database and table if they don't exist
    conn = sqlite3.connect(passport_db_path)
    cursor = conn.cursor()
    
    # Create passport_registry table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passport_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT UNIQUE NOT NULL,
            port INTEGER UNIQUE NOT NULL,
            passport_id TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            service_type TEXT DEFAULT 'backend',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Generate passport ID for ServiceLifecycleManager
    passport_id = f"ZMBT-SLM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    # Service details
    service_name = "service-lifecycle-manager"
    port = 8920
    service_type = "backend"
    description = "Dynamic Service Lifecycle Validation and Management System"
    
    try:
        # Insert ServiceLifecycleManager into passport registry
        cursor.execute('''
            INSERT OR REPLACE INTO passport_registry 
            (passport_id, service_name, service_type, port, status, description, created_by, registered_at, activated_at, last_seen)
            VALUES (?, ?, ?, ?, 'ACTIVE', ?, 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (passport_id, service_name, service_type, port, description))
        
        conn.commit()
        
        print(f"✅ Successfully added ServiceLifecycleManager to passport registry:")
        print(f"   📛 Service Name: {service_name}")
        print(f"   🔌 Port: {port}")
        print(f"   🎫 Passport ID: {passport_id}")
        print(f"   📋 Status: ACTIVE")
        print(f"   🏷️ Type: {service_type}")
        
        # Verify the insertion
        cursor.execute("SELECT * FROM passport_registry WHERE service_name = ?", (service_name,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Verification successful - Service exists in passport registry")
        else:
            print(f"❌ Verification failed - Service not found in passport registry")
            
    except sqlite3.IntegrityError as e:
        if "port" in str(e).lower():
            print(f"❌ Port {port} is already assigned to another service")
            # Find available port
            cursor.execute("SELECT port FROM passport_registry ORDER BY port")
            used_ports = [row[0] for row in cursor.fetchall()]
            available_port = 8920
            while available_port in used_ports:
                available_port += 1
            print(f"💡 Suggested available port: {available_port}")
        else:
            print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Error adding service to passport registry: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    add_lifecycle_manager_to_passport()