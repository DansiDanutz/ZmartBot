#!/usr/bin/env python3
"""
ZmartBot Direct Database Passport Assignment Script
Assign Passport IDs directly via database to avoid API concurrency issues
"""

import sqlite3
import json
import hashlib
import secrets
from datetime import datetime

# Database path
DB_PATH = "/Users/dansidanutz/Desktop/ZmartBot/data/passport_registry.db"

# Services to register (from Master Orchestration Agent)
SERVICES_TO_REGISTER = [
    {"name": "system-protection-service", "type": "PROTECTION", "port": 8999, "description": "Critical system protection and security service"},
    {"name": "optimization-claude-service", "type": "SRV", "port": 8998, "description": "Advanced context optimization service"},
    {"name": "snapshot-service", "type": "SRV", "port": 8085, "description": "Comprehensive disaster recovery and snapshot service"},
    {"name": "passport-service", "type": "SRV", "port": 8620, "description": "Service registration and identity management"},
    {"name": "api-keys-manager-service", "type": "SRV", "port": 8006, "description": "API key management and security service"},
    {"name": "binance", "type": "SRV", "port": 8303, "description": "Binance exchange integration service"},
    {"name": "kingfisher-module", "type": "SRV", "port": 8100, "description": "Advanced trading analysis and signal processing"},
    {"name": "kucoin", "type": "SRV", "port": 8302, "description": "KuCoin exchange integration service"},
    {"name": "master-orchestration-agent", "type": "AGT", "port": 8002, "description": "Central system orchestration controller"},
    {"name": "mdc-orchestration-agent", "type": "AGT", "port": 8615, "description": "MDC documentation orchestration service"},
    {"name": "my-symbols-extended-service", "type": "SRV", "port": 8005, "description": "Extended symbol management and analysis"},
    {"name": "mysymbols", "type": "API", "port": 8201, "description": "Internal symbol management API"},
    {"name": "port-manager-service", "type": "AGT", "port": 8610, "description": "Dynamic port allocation and management"},
    {"name": "test-analytics-service", "type": "SRV", "port": 8003, "description": "Analytics testing and validation service"},
    {"name": "test-service", "type": "SRV", "port": 8301, "description": "General testing and validation service"},
    {"name": "test-websocket-service", "type": "SRV", "port": 8004, "description": "WebSocket testing and validation service"},
    {"name": "zmart-analytics", "type": "SRV", "port": 8007, "description": "Advanced analytics and data processing"},
    {"name": "zmart-api", "type": "API", "port": 8000, "description": "Main API server and trading platform core"},
    {"name": "zmart-dashboard", "type": "SRV", "port": 3400, "description": "Web dashboard and user interface"},
    {"name": "zmart-notification", "type": "SRV", "port": 8008, "description": "Notification and alerting service"},
    {"name": "zmart-websocket", "type": "SRV", "port": 8009, "description": "Real-time WebSocket communication service"},
    {"name": "zmart_alert_system", "type": "SRV", "port": 8012, "description": "Alert system and notification management"},
    {"name": "zmart_backtesting", "type": "ENG", "port": 8013, "description": "Trading strategy backtesting engine"},
    {"name": "zmart_data_warehouse", "type": "DB", "port": 8015, "description": "Data warehouse and storage management"},
    {"name": "zmart_machine_learning", "type": "ENG", "port": 8014, "description": "Machine learning and AI processing"},
    {"name": "zmart_risk_management", "type": "SRV", "port": 8010, "description": "Risk assessment and management system"},
    {"name": "zmart_technical_analysis", "type": "ENG", "port": 8011, "description": "Technical analysis and indicator processing"}
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

def register_services_direct():
    """Register all services directly to the database"""
    print("🛂 ZmartBot Direct Passport Assignment")
    print("=" * 50)
    
    # Connect to database
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 30000")
        cursor = conn.cursor()
        
        successful = 0
        failed = 0
        
        for service in SERVICES_TO_REGISTER:
            try:
                # Check if already exists
                cursor.execute("""
                    SELECT passport_id, status FROM passport_registry 
                    WHERE service_name = ? AND port = ?
                """, (service["name"], service["port"]))
                
                existing = cursor.fetchone()
                if existing:
                    print(f"⚠️  {service['name']} already exists with Passport ID: {existing[0]} (Status: {existing[1]})")
                    continue
                
                # Generate passport ID
                passport_id = generate_passport_id(service["name"], service["type"])
                
                # Insert service
                cursor.execute("""
                    INSERT INTO passport_registry (
                        passport_id, service_name, service_type, port, status, 
                        description, metadata, created_by, registered_at
                    ) VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, 'DIRECT_ASSIGNMENT', CURRENT_TIMESTAMP)
                """, (
                    passport_id, service["name"], service["type"], 
                    service["port"], service["description"], 
                    json.dumps({"auto_assigned": True, "category": service["type"], "owner": "zmartbot"})
                ))
                
                # Log audit entry
                cursor.execute("""
                    INSERT INTO passport_audit_log (passport_id, action, details, timestamp)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (passport_id, "DIRECT_REGISTERED", json.dumps({
                    "service_name": service["name"],
                    "service_type": service["type"],
                    "port": service["port"]
                })))
                
                print(f"🛂 ✅ PASSPORT ASSIGNED: {service['name']} → {passport_id} (Port: {service['port']})")
                successful += 1
                
            except sqlite3.Error as e:
                print(f"❌ Failed to register {service['name']}: {str(e)}")
                failed += 1
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        print("-" * 50)
        print(f"📊 Registration Summary:")
        print(f"✅ Successfully registered: {successful}")
        print(f"❌ Failed registrations: {failed}")
        print(f"📋 Total services processed: {len(SERVICES_TO_REGISTER)}")
        
        # Show final count
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM passport_registry WHERE status != 'REVOKED'")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM passport_registry WHERE status = 'ACTIVE'")
        active = cursor.fetchone()[0]
        conn.close()
        
        print(f"📊 Total registered services in system: {total}")
        print(f"📊 Active services: {active}")
        print("\n🎉 Direct passport assignment complete!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    register_services_direct()