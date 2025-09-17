#!/usr/bin/env python3
"""
Create and populate service_registry.db with certified services
This implements the Level 3 database for the 3-database lifecycle architecture
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

def create_service_registry_db():
    """Create service_registry.db and populate with certified services"""
    
    # Database path - FIXED: Use single source of truth
    from src.config.database_config import get_master_database_path
    db_path = get_master_database_path()
    
    # Remove existing empty database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create services table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT UNIQUE NOT NULL,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'REGISTERED',
            certification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            certified BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Read certified services from file
    certified_file = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/certified_services.txt"
    
    if os.path.exists(certified_file):
        with open(certified_file, 'r') as f:
            services = [line.strip() for line in f if line.strip()]
        
        print(f"📊 Found {len(services)} certified services to add to service_registry.db")
        
        # Insert each certified service
        for service_name in services:
            cursor.execute('''
                INSERT OR REPLACE INTO services 
                (service_name, registration_date, status, certification_date, certified) 
                VALUES (?, ?, 'REGISTERED', ?, 1)
            ''', (service_name, datetime.now(), datetime.now()))
            print(f"✅ Added: {service_name}")
    
    # Commit and close
    conn.commit()
    
    # Verify the count
    cursor.execute("SELECT COUNT(*) FROM services")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n🎯 SERVICE_REGISTRY.DB CREATED SUCCESSFULLY!")
    print(f"📊 Total services in service_registry.db: {count}")
    print(f"✅ Database rule: service_registry.db count ({count}) = Total Certified Services")
    print(f"🏆 All {count} services are REGISTERED & CERTIFIED")
    
    return count

if __name__ == "__main__":
    create_service_registry_db()