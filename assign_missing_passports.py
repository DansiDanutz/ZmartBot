#!/usr/bin/env python3
"""
Assign Passports to Services Missing Passport IDs
"""

import sqlite3
import json
import hashlib
import secrets
from datetime import datetime

# Database path
DB_PATH = "zmart-api/src/data/service_registry.db"

# Services that need passports (from our analysis)
SERVICES_NEEDING_PASSPORTS = [
    {"name": "background-mdc-agent", "type": "SRV", "port": 8091, "status": "DISCOVERED"},
    {"name": "binance-worker", "type": "SRV", "port": 8304, "status": "DISCOVERED"},
    {"name": "cryptometer-service", "type": "SRV", "port": 8093, "status": "DISCOVERED"},
    {"name": "explainability-service", "type": "SRV", "port": 8099, "status": "DISCOVERED"},
    {"name": "grok-x-module", "type": "SRV", "port": 8092, "status": "DISCOVERED"},
    {"name": "historical-data-service", "type": "SRV", "port": 8094, "status": "DISCOVERED"},
    {"name": "market-data-service", "type": "SRV", "port": 8095, "status": "DISCOVERED"},
    {"name": "mdc-dashboard", "type": "SRV", "port": 8090, "status": "ACTIVE"},
    {"name": "pattern-recognition-service", "type": "SRV", "port": 8096, "status": "DISCOVERED"},
    {"name": "scoring-service", "type": "SRV", "port": 8098, "status": "DISCOVERED"},
    {"name": "sentiment-analysis-service", "type": "SRV", "port": 8097, "status": "DISCOVERED"},
    {"name": "servicelog-service", "type": "SRV", "port": 8750, "status": "ACTIVE"}
]

def generate_passport_id(service_name: str, service_type: str) -> str:
    """Generate unique Passport ID with format: ZMBT-{TYPE}-{DATE}-{HASH}"""
    date_str = datetime.now().strftime("%Y%m%d")
    
    # Generate unique hash
    hash_input = f"{service_name}-{service_type}-{datetime.now().isoformat()}-{secrets.token_hex(8)}"
    hash_obj = hashlib.sha256(hash_input.encode())
    unique_hash = hash_obj.hexdigest()[:6].upper()
    
    passport_id = f"ZMBT-{service_type.upper()}-{date_str}-{unique_hash}"
    return passport_id

def assign_missing_passports():
    """Assign passports to services that don't have them"""
    print("🛂 Assigning Passports to Services Missing Passport IDs")
    print("=" * 60)
    
    # Connect to database
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 30000")
        cursor = conn.cursor()
        
        successful = 0
        failed = 0
        
        for service in SERVICES_NEEDING_PASSPORTS:
            try:
                # Check if service already has a passport
                cursor.execute("""
                    SELECT passport_id FROM service_registry 
                    WHERE service_name = ? AND port = ?
                """, (service["name"], service["port"]))
                
                existing = cursor.fetchone()
                if existing and existing[0] and existing[0] != 'N/A':
                    print(f"⚠️  {service['name']} already has Passport ID: {existing[0]}")
                    continue
                
                # Generate passport ID
                passport_id = generate_passport_id(service["name"], service["type"])
                
                # Update service with passport ID
                cursor.execute("""
                    UPDATE service_registry 
                    SET passport_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE service_name = ? AND port = ?
                """, (passport_id, service["name"], service["port"]))
                
                # Log the passport assignment
                cursor.execute("""
                    INSERT INTO service_events (
                        service_name, event_type, data, created_at
                    ) VALUES (?, 'PASSPORT_ASSIGNED', ?, CURRENT_TIMESTAMP)
                """, (service["name"], json.dumps({
                    "passport_id": passport_id,
                    "assigned_by": "SYSTEM",
                    "reason": "Missing passport assignment"
                })))
                
                print(f"✅ {service['name']} (Port {service['port']}) -> {passport_id}")
                successful += 1
                
            except Exception as e:
                print(f"❌ Failed to assign passport to {service['name']}: {e}")
                failed += 1
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"🎯 Passport Assignment Complete:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📊 Total Processed: {len(SERVICES_NEEDING_PASSPORTS)}")
        
        # Show final status
        print("\n📋 Final Status Check:")
        cursor.execute("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN passport_id IS NOT NULL AND passport_id != 'N/A' THEN 1 END) as with_passports,
                   COUNT(CASE WHEN passport_id IS NULL OR passport_id = 'N/A' THEN 1 END) as without_passports
            FROM service_registry
        """)
        
        stats = cursor.fetchone()
        print(f"   📊 Total Services: {stats[0]}")
        print(f"   ✅ With Passports: {stats[1]}")
        print(f"   ❌ Without Passports: {stats[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    assign_missing_passports()
