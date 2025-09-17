#!/usr/bin/env python3
"""
🔍 DATABASE VERIFICATION FOR CURSOR
Proves the correct database path and service counts
"""

import os
import sqlite3
from datetime import datetime

def main():
    print("🔍 DATABASE VERIFICATION FOR CURSOR")
    print("=" * 70)
    print(f"🕐 Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
    
    # Test all potential databases
    databases = [
        ("MASTER DATABASE (CORRECT)", "src/data/service_registry.db"),
        ("OLD CERT.db (WRONG)", "CERT.db"),
        ("Authentication DB", "authentication.db"),
        ("Backup DB", "database/master_database_registry.db")
    ]
    
    for db_name, db_path in databases:
        full_path = os.path.join(base_path, db_path)
        print(f"📁 {db_name}")
        print(f"   Path: {db_path}")
        
        if not os.path.exists(full_path):
            print("   Status: ❌ NOT FOUND")
            print()
            continue
            
        try:
            conn = sqlite3.connect(full_path)
            cursor = conn.cursor()
            
            # Check for service_registry table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='service_registry'")
            has_service_registry = cursor.fetchone() is not None
            
            if has_service_registry:
                # Get service counts
                cursor.execute("SELECT certification_level, COUNT(*) FROM service_registry GROUP BY certification_level")
                levels = dict(cursor.fetchall())
                
                cursor.execute("SELECT COUNT(*) FROM service_registry WHERE passport_id IS NOT NULL AND passport_id != ''")
                services_with_passports = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM service_registry")
                total_services = cursor.fetchone()[0]
                
                print(f"   Status: ✅ HAS service_registry table")
                print(f"   Total Services: {total_services}")
                print(f"   Level 1: {levels.get(1, 0)}")
                print(f"   Level 2: {levels.get(2, 0)}")
                print(f"   Level 3: {levels.get(3, 0)}")
                print(f"   Services with Passports: {services_with_passports}")
                
                if db_path == "src/data/service_registry.db":
                    print("   🎯 THIS IS THE CORRECT DATABASE FOR CURSOR TO USE!")
                
            else:
                # Check what tables it has
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"   Status: ❌ NO service_registry table")
                print(f"   Tables found: {', '.join(tables[:5])}")
                
                if 'cert_registry' in tables:
                    cursor.execute("SELECT COUNT(*) FROM cert_registry")
                    count = cursor.fetchone()[0]
                    print(f"   Old cert_registry: {count} services (OBSOLETE)")
            
            conn.close()
            
        except Exception as e:
            print(f"   Status: ❌ ERROR: {e}")
        
        print()
    
    # Show the exact query Cursor should use
    print("🎯 CURSOR INTEGRATION GUIDE")
    print("-" * 70)
    print("✅ CORRECT DATABASE: src/data/service_registry.db")
    print("✅ CORRECT TABLE: service_registry")
    print()
    print("📋 VERIFICATION QUERIES:")
    print("   Total services: SELECT COUNT(*) FROM service_registry")
    print("   Level 3 services: SELECT COUNT(*) FROM service_registry WHERE certification_level = 3")
    print("   Services with passports: SELECT COUNT(*) FROM service_registry WHERE passport_id IS NOT NULL")
    print()
    print("🚨 EXPECTED RESULTS:")
    print("   Total Services: 64")
    print("   Level 3 Services: 43") 
    print("   Services with Passports: 63")
    print()
    print("❌ DATABASES TO AVOID:")
    print("   CERT.db (only has 5 services - OBSOLETE)")
    print("   authentication.db (wrong structure)")
    print()
    
    # Create a simple test file for Cursor
    test_query = """
-- CURSOR DATABASE TEST QUERY
-- Use this to verify you're using the correct database
SELECT 
    certification_level,
    COUNT(*) as service_count
FROM service_registry 
GROUP BY certification_level
ORDER BY certification_level DESC;

-- Expected results:
-- Level 3: 43 services
-- Level 2: 20 services  
-- Level 1: 1 service
-- Total: 64 services
"""
    
    with open(os.path.join(base_path, ".cursor", "TEST_QUERY.sql"), "w") as f:
        f.write(test_query)
    
    print("📄 Created .cursor/TEST_QUERY.sql for verification")
    print("=" * 70)

if __name__ == "__main__":
    main()