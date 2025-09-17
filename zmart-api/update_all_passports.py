#!/usr/bin/env python3
"""
Update All Service Passport IDs
Ensures all services in the registry have their proper passport IDs
"""

import sqlite3
import os
from pathlib import Path

def update_all_passport_ids():
    """Update all services with their proper passport IDs"""
    
    # Database path
    db_path = Path(__file__).parent / "src" / "data" / "service_registry.db"
    
    # Service passport mapping from the dashboard
    passport_services = {
        'api-keys-manager-service': 'ZMBT-SRV-20250826-3B1EF4',
        'binance': 'ZMBT-SRV-20250826-7070E8', 
        'doctor-service': 'ZMBT-SRV-20250826-51B6B9',
        'kingfisher-module': 'ZMBT-SRV-20250826-5D5AA0',
        'kucoin': 'ZMBT-SRV-20250826-BAABBC',
        'master-orchestration-agent': 'ZMBT-AGT-20250826-430BAD',
        'mdc-orchestration-agent': 'ZMBT-AGT-20250826-CAD9CD',
        'my-symbols-extended-service': 'ZMBT-SRV-20250826-45620A',
        'mysymbols': 'ZMBT-API-20250826-108804',
        'optimization-claude-service': 'ZMBT-SRV-20250826-513E16',
        'passport-service': 'ZMBT-SRV-20250826-467E65',
        'port-manager-service': 'ZMBT-AGT-20250826-EBA047',
        'service-dashboard': 'ZMBT-FRE-20250826-D347BE',
        'snapshot-service': 'ZMBT-SRV-20250826-0D2B65',
        'system-protection-service': 'ZMBT-PROTECTION-20250826-2C0587',
        'test-analytics-service': 'ZMBT-SRV-20250826-11C2AA',
        'test-service': 'ZMBT-SRV-20250826-97C6AB',
        'test-websocket-service': 'ZMBT-SRV-20250826-B47240',
        'zmart-analytics': 'ZMBT-SRV-20250826-6E0D70',
        'zmart-api': 'ZMBT-API-20250826-2AF672',
        'zmart-dashboard': 'ZMBT-SRV-20250826-5E1452',
        'zmart-notification': 'ZMBT-SRV-20250826-337DFE',
        'zmart-websocket': 'ZMRT-SRV-20250826-6532E8',
        'zmart_alert_system': 'ZMBT-SRV-20250826-EADCA5',
        'zmart_backtesting': 'ZMBT-ENG-20250826-FB4140',
        'zmart_data_warehouse': 'ZMBT-DB-20250826-325722',
        'zmart_machine_learning': 'ZMBT-ENG-20250826-5C28B0',
        'zmart_risk_management': 'ZMBT-SRV-20250826-D05686',
        'zmart_technical_analysis': 'ZMBT-ENG-20250826-641E1D'
    }
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First check if passport_id column exists, add if not
        cursor.execute("PRAGMA table_info(service_registry)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'passport_id' not in columns:
            print("Adding passport_id column to service_registry table...")
            cursor.execute("ALTER TABLE service_registry ADD COLUMN passport_id TEXT")
        
        # Update all services with passport IDs
        updated_count = 0
        for service_name, passport_id in passport_services.items():
            cursor.execute("""
                UPDATE service_registry 
                SET passport_id = ? 
                WHERE service_name = ?
            """, (passport_id, service_name))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"✅ Updated {service_name} with passport {passport_id}")
            else:
                print(f"⚠️  Service {service_name} not found in registry")
        
        # Commit changes
        conn.commit()
        
        # Verify results
        cursor.execute("SELECT COUNT(*) FROM service_registry WHERE passport_id IS NOT NULL")
        total_passport_services = cursor.fetchone()[0]
        
        print(f"\n🎯 Update Complete:")
        print(f"   - Updated {updated_count} services")
        print(f"   - Total passport services: {total_passport_services}")
        
        # List all passport services
        cursor.execute("SELECT service_name, passport_id FROM service_registry WHERE passport_id IS NOT NULL ORDER BY service_name")
        passport_list = cursor.fetchall()
        
        print(f"\n📋 All Passport Services:")
        for service_name, passport_id in passport_list:
            print(f"   - {service_name}: {passport_id}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error updating passport IDs: {e}")
        return False

if __name__ == "__main__":
    success = update_all_passport_ids()
    if success:
        print("\n✅ All passport IDs updated successfully!")
        print("🔄 The Master Orchestration Agent will now recognize all passport services.")
    else:
        print("\n❌ Failed to update passport IDs.")