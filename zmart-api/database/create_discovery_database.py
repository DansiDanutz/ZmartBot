#!/usr/bin/env python3
"""
Create discovery_registry.db for Level 1 services
This completes the 3-database architecture:
- Level 1: discovery_registry.db (services without passports)
- Level 2: passport_registry.db (services with passports) 
- Level 3: service_registry.db (registered & certified services)
"""

import sqlite3
import os
import glob
from datetime import datetime
from pathlib import Path

def find_all_python_services():
    """Find all .py services in the entire ZMARTbot folder with corresponding MDC files"""
    base_path = "/Users/dansidanutz/Desktop/ZmartBot"  # Scan entire ZMARTbot folder
    mdc_rules_path = "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules"
    
    python_services_with_mdc = []
    
    exclude_patterns = [
        '*/venv/*', '*/.*', '*/__pycache__/*', '*/node_modules/*',
        '*/system_backups/*', '*/Documentation/*', '*/backups/*',
        '*test*.py', '*debug*.py', '*create_*.py', '*setup*.py'
    ]
    
    print(f"🔍 Scanning entire ZMARTbot folder: {base_path}")
    print(f"🔍 Looking for MDC files in: {mdc_rules_path}")
    
    # Find all .py files in the entire ZMARTbot folder
    for root, dirs, files in os.walk(base_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(pattern.replace('*/', '') in d for pattern in exclude_patterns)]
        
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                
                # Skip excluded files
                if any(pattern.replace('*', '') in full_path for pattern in exclude_patterns):
                    continue
                
                service_name = Path(file).stem
                
                # Check if corresponding MDC file exists
                mdc_file_path = os.path.join(mdc_rules_path, f"{service_name}.mdc")
                
                if os.path.exists(mdc_file_path):
                    python_services_with_mdc.append({
                        'service_name': service_name,
                        'python_file_path': full_path,
                        'mdc_file_path': mdc_file_path
                    })
                    print(f"  ✅ {service_name} - Has MDC file")
                else:
                    print(f"  ❌ {service_name} - No MDC file (not added to database)")
    
    print(f"\n🔍 Found {len(python_services_with_mdc)} Python services WITH MDC files")
    return python_services_with_mdc

def get_services_with_passports():
    """Get list of services that have passports"""
    passport_db = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/data/passport_registry.db"
    
    if not os.path.exists(passport_db):
        return []
    
    conn = sqlite3.connect(passport_db)
    cursor = conn.cursor()
    
    cursor.execute("SELECT service_name FROM passport_registry WHERE status = 'ACTIVE'")
    services_with_passports = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return services_with_passports

def create_discovery_database():
    """Create discovery_registry.db for Level 1 services"""
    
    # Database path
    db_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/discovery_registry.db"
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create discovery table with enhanced schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discovery_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT UNIQUE NOT NULL,
            discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'DISCOVERED',
            has_mdc_file BOOLEAN DEFAULT 0,
            has_python_file BOOLEAN DEFAULT 1,
            python_file_path TEXT,
            mdc_file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Get all Python services with MDC files (only services that should be in discovery database)
    all_services_with_mdc = find_all_python_services()
    print(f"🔍 Found {len(all_services_with_mdc)} Python services WITH MDC files")
    
    # Get services with passports (to exclude from discovery)
    services_with_passports = get_services_with_passports()
    print(f"🎫 Found {len(services_with_passports)} services with passports")
    
    # Discovery services = Services with MDC files - Services with passports
    discovery_services = [s for s in all_services_with_mdc if s['service_name'] not in services_with_passports]
    
    print(f"📊 Discovery services (Level 1): {len(discovery_services)}")
    print("\n🔍 DISCOVERY SERVICES (WITH MDC, NO PASSPORTS):")
    
    # Insert each discovery service
    for service_data in discovery_services:
        service_name = service_data['service_name']
        python_file_path = service_data['python_file_path']
        mdc_file_path = service_data['mdc_file_path']
        
        cursor.execute('''
            INSERT OR REPLACE INTO discovery_services 
            (service_name, discovered_date, status, has_mdc_file, has_python_file, python_file_path, mdc_file_path) 
            VALUES (?, ?, 'DISCOVERED', 1, 1, ?, ?)
        ''', (service_name, datetime.now(), python_file_path, mdc_file_path))
        
        print(f"  ✅ {service_name} - Python: {python_file_path}")
    
    # Commit and get count
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM discovery_services")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n🎯 DISCOVERY_REGISTRY.DB CREATED SUCCESSFULLY!")
    print(f"📊 Total discovery services: {count}")
    print(f"✅ Level 1 database complete!")
    
    return count

if __name__ == "__main__":
    create_discovery_database()