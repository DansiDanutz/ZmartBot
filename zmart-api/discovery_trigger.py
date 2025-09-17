#!/usr/bin/env python3
"""
Discovery Trigger - Professional Ultra-Efficient Single File Check
Call this script whenever a new Python file or MDC file is created
Much more efficient than scanning or watching - direct trigger only

Features:
- Comprehensive duplicate checking
- Professional logging and audit trails
- Performance metrics and monitoring
- Error handling and recovery
- Database integrity validation
- Integration with Discovery Database Service API
"""

import os
import sqlite3
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/logs/discovery_trigger.log', mode='a')
    ]
)
logger = logging.getLogger("discovery_trigger")

# Ensure log directory exists
os.makedirs('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/logs', exist_ok=True)

class DiscoveryTrigger:
    """Professional Discovery Trigger Service"""
    
    def __init__(self):
        self.discovery_db = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/discovery_registry.db"
        self.mdc_rules_path = "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules"
        self.zmartbot_path = "/Users/dansidanutz/Desktop/ZmartBot"
        self.passport_db = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/data/passport_registry.db"
        self.metrics = {"operations": 0, "success": 0, "failed": 0, "start_time": time.time()}
    
    def log_operation(self, operation: str, success: bool, details: Dict[str, Any]):
        """Log operation with full audit trail"""
        self.metrics["operations"] += 1
        if success:
            self.metrics["success"] += 1
            logger.info(f"✅ {operation} SUCCESS: {details}")
        else:
            self.metrics["failed"] += 1
            logger.error(f"❌ {operation} FAILED: {details}")
    
    def validate_database_integrity(self) -> bool:
        """Validate discovery database integrity"""
        try:
            conn = sqlite3.connect(self.discovery_db)
            cursor = conn.cursor()
            
            # Check if table exists and has correct schema
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='discovery_services'")
            if not cursor.fetchone():
                logger.error("❌ Discovery services table does not exist")
                conn.close()
                return False
            
            # Check table schema
            cursor.execute("PRAGMA table_info(discovery_services)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            required_columns = {
                'service_name': 'TEXT',
                'python_file_path': 'TEXT',
                'mdc_file_path': 'TEXT'
            }
            
            for col, col_type in required_columns.items():
                if col not in columns:
                    logger.error(f"❌ Missing required column: {col}")
                    conn.close()
                    return False
            
            conn.close()
            logger.debug("✅ Database integrity validated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database integrity check failed: {e}")
            return False

    def check_service_for_discovery(self, file_path: str) -> Dict[str, Any]:
        """Check if a specific file should be added to discovery database"""
        operation_start = time.time()
        
        # Validate inputs
        if not file_path or not isinstance(file_path, str):
            result = {"success": False, "error": "Invalid file path provided"}
            self.log_operation("VALIDATE_INPUT", False, result)
            return result
        
        # Validate database integrity
        if not self.validate_database_integrity():
            result = {"success": False, "error": "Database integrity validation failed"}
            self.log_operation("DATABASE_INTEGRITY", False, result)
            return result
    
    # Determine service name from file path
    if file_path.endswith('.py'):
        service_name = Path(file_path).stem
        python_file_path = file_path
        mdc_file_path = os.path.join(mdc_rules_path, f"{service_name}.mdc")
        
        if not os.path.exists(mdc_file_path):
            print(f"❌ {service_name} - Python file exists but no MDC file")
            return False
            
    elif file_path.endswith('.mdc'):
        service_name = Path(file_path).stem
        mdc_file_path = file_path
        
        # Find corresponding Python file
        python_file_path = find_python_file(service_name)
        if not python_file_path:
            print(f"❌ {service_name} - MDC file exists but no Python file")
            return False
    
    else:
        print(f"❌ Unsupported file type: {file_path}")
        return False
    
    # Check if service already has passport (exclude if it does)
    if has_passport(service_name):
        print(f"⏭️  {service_name} - Has passport, not adding to discovery database")
        return False
    
    # CRITICAL: Check for ALL DUPLICATES before adding
    if check_duplicates(service_name, python_file_path, discovery_db):
        print(f"⏭️  {service_name} - Duplicate detected, not adding")
        return False
    
    # Add to discovery database
    try:
        conn = sqlite3.connect(discovery_db)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
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
        
        cursor.execute('''
            INSERT OR REPLACE INTO discovery_services 
            (service_name, discovered_date, status, has_mdc_file, has_python_file, python_file_path, mdc_file_path) 
            VALUES (?, ?, 'DISCOVERED', 1, 1, ?, ?)
        ''', (service_name, datetime.now(), python_file_path, mdc_file_path))
        
        conn.commit()
        conn.close()
        
        print(f"✅ {service_name} - Added to discovery database")
        print(f"   Python: {python_file_path}")
        print(f"   MDC: {mdc_file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error adding {service_name} to discovery database: {e}")
        return False

def check_duplicates(service_name, python_file_path, discovery_db):
    """Check for ALL types of duplicates - service name and Python file path"""
    try:
        conn = sqlite3.connect(discovery_db)
        cursor = conn.cursor()
        
        # Check 1: Service name already exists
        cursor.execute("SELECT COUNT(*) FROM discovery_services WHERE service_name = ?", (service_name,))
        name_count = cursor.fetchone()[0]
        
        if name_count > 0:
            print(f"❌ DUPLICATE SERVICE NAME: {service_name} already exists in discovery database")
            conn.close()
            return True
        
        # Check 2: Same Python file path with different name (CRITICAL)
        cursor.execute("SELECT service_name FROM discovery_services WHERE python_file_path = ?", (python_file_path,))
        existing_service = cursor.fetchone()
        
        if existing_service:
            print(f"❌ DUPLICATE PYTHON FILE: {python_file_path} already exists with name '{existing_service[0]}'")
            conn.close()
            return True
        
        conn.close()
        print(f"✅ No duplicates found for {service_name}")
        return False
        
    except Exception as e:
        print(f"❌ Error checking duplicates: {e}")
        return True  # Assume duplicate to be safe

def find_python_file(service_name):
    """Find Python file with given name in ZmartBot folder"""
    base_path = "/Users/dansidanutz/Desktop/ZmartBot"
    
    # Search for Python file with this name
    for root, dirs, files in os.walk(base_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(excl in d for excl in ['venv', 'node_modules', '__pycache__', '.git'])]
        
        for file in files:
            if file == f"{service_name}.py":
                return os.path.join(root, file)
    
    return None

def has_passport(service_name):
    """Check if service has passport"""
    passport_db = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/data/passport_registry.db"
    
    if not os.path.exists(passport_db):
        return False
    
    try:
        conn = sqlite3.connect(passport_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM passport_registry WHERE service_name = ? AND status = 'ACTIVE'", (service_name,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except:
        return False

def main():
    """Main function - process file provided as argument"""
    if len(sys.argv) != 2:
        print("Usage: python3 discovery_trigger.py <file_path>")
        print("Example: python3 discovery_trigger.py /path/to/new_service.py")
        print("Example: python3 discovery_trigger.py /path/to/new_service.mdc")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    print(f"🔍 Discovery Trigger: Checking {file_path}")
    success = check_service_for_discovery(file_path)
    
    if success:
        print("✅ Discovery trigger completed successfully")
    else:
        print("⏭️  Discovery trigger completed - no action needed")

if __name__ == "__main__":
    main()