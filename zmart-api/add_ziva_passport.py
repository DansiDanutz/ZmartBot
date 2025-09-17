#!/usr/bin/env python3
"""
Add ZIVA Agent to Passport Registry
"""

import sqlite3
from datetime import datetime
import uuid
import sys
from pathlib import Path

def add_ziva_to_passport():
    """Add ZIVA Agent to passport registry"""
    
    # Database path
    passport_db = Path("data/passport_registry.db")
    
    if not passport_db.exists():
        print(f"❌ Passport database not found at {passport_db}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(passport_db)
        cursor = conn.cursor()
        
        # Generate passport details
        passport_id = f"ZMBT-ZIVA-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        service_name = "ziva_agent"
        service_type = "integrity"
        port = 8930
        description = "ZIVA - ZmartBot Integrity Violation Agent: Senior-level system-wide consistency and optimization engine"
        
        # Check if ZIVA already exists
        cursor.execute("SELECT passport_id FROM passport_registry WHERE service_name = ?", (service_name,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"📋 ZIVA already has passport: {existing[0]}")
            conn.close()
            return True
        
        # Insert ZIVA into passport registry
        cursor.execute('''
            INSERT INTO passport_registry 
            (passport_id, service_name, service_type, port, status, description)
            VALUES (?, ?, ?, ?, 'ACTIVE', ?)
        ''', (passport_id, service_name, service_type, port, description))
        
        conn.commit()
        conn.close()
        
        print(f"✅ ZIVA Agent successfully added to passport registry:")
        print(f"   Passport ID: {passport_id}")
        print(f"   Service: {service_name}")
        print(f"   Type: {service_type}")
        print(f"   Port: {port}")
        print(f"   Status: ACTIVE")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding ZIVA to passport registry: {e}")
        return False

if __name__ == "__main__":
    success = add_ziva_to_passport()
    sys.exit(0 if success else 1)