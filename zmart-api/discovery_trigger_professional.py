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
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize the discovery database with proper schema"""
        try:
            conn = sqlite3.connect(self.discovery_db)
            cursor = conn.cursor()
            
            # Create discovery services table if it doesn't exist
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
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_service_name ON discovery_services(service_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_python_path ON discovery_services(python_file_path)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON discovery_services(status)')
            
            conn.commit()
            conn.close()
            logger.debug("✅ Discovery database initialized")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def log_operation(self, operation: str, success: bool, details: Dict[str, Any]):
        """Log operation with full audit trail"""
        self.metrics["operations"] += 1
        if success:
            self.metrics["success"] += 1
            logger.info(f"✅ {operation} SUCCESS: {details}")
        else:
            self.metrics["failed"] += 1
            logger.error(f"❌ {operation} FAILED: {details}")
        
        # Write audit log entry
        self.write_audit_log(operation, success, details)
    
    def write_audit_log(self, operation: str, success: bool, details: Dict[str, Any]):
        """Write detailed audit log entry"""
        try:
            audit_log_path = '/Users/dansidanutz/Desktop/ZmartBot/zmart-api/logs/discovery_audit.log'
            with open(audit_log_path, 'a') as audit_file:
                audit_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "operation": operation,
                    "success": success,
                    "details": details,
                    "metrics": self.get_metrics()
                }
                audit_file.write(json.dumps(audit_entry) + '\n')
        except Exception as e:
            logger.warning(f"⚠️ Failed to write audit log: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        uptime = time.time() - self.metrics["start_time"]
        success_rate = (self.metrics["success"] / max(self.metrics["operations"], 1)) * 100
        
        return {
            "total_operations": self.metrics["operations"],
            "successful_operations": self.metrics["success"],
            "failed_operations": self.metrics["failed"],
            "success_rate_percent": round(success_rate, 2),
            "uptime_seconds": round(uptime, 2)
        }
    
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
            
            # Validate database integrity
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            if integrity_result != 'ok':
                logger.error(f"❌ Database integrity check failed: {integrity_result}")
                conn.close()
                return False
            
            conn.close()
            logger.debug("✅ Database integrity validated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database integrity check failed: {e}")
            return False

    def check_duplicates(self, service_name: str, python_file_path: str) -> Optional[str]:
        """Check for ALL types of duplicates - returns error message if duplicate found"""
        try:
            conn = sqlite3.connect(self.discovery_db)
            cursor = conn.cursor()
            
            # Check 1: Service name already exists
            cursor.execute("SELECT COUNT(*) FROM discovery_services WHERE service_name = ?", (service_name,))
            name_count = cursor.fetchone()[0]
            
            if name_count > 0:
                conn.close()
                return f"DUPLICATE SERVICE NAME: {service_name} already exists in discovery database"
            
            # Check 2: Same Python file path with different name (CRITICAL)
            cursor.execute("SELECT service_name FROM discovery_services WHERE python_file_path = ?", (python_file_path,))
            existing_service = cursor.fetchone()
            
            if existing_service:
                conn.close()
                return f"DUPLICATE PYTHON FILE: {python_file_path} already exists with name '{existing_service[0]}'"
            
            conn.close()
            return None  # No duplicates found
            
        except Exception as e:
            logger.error(f"❌ Error checking duplicates: {e}")
            return f"Database error during duplicate check: {e}"

    def has_passport(self, service_name: str) -> bool:
        """Check if service has passport"""
        if not os.path.exists(self.passport_db):
            return False
        
        try:
            conn = sqlite3.connect(self.passport_db)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM passport_registry WHERE service_name = ? AND status = 'ACTIVE'", (service_name,))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception as e:
            logger.warning(f"⚠️ Error checking passport for {service_name}: {e}")
            return False

    def find_python_file(self, service_name: str) -> Optional[str]:
        """Find Python file with given name in ZmartBot folder"""
        exclude_dirs = ['venv', 'node_modules', '__pycache__', '.git', 'system_backups', 'Documentation', 'backups']
        
        try:
            for root, dirs, files in os.walk(self.zmartbot_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(excl in d for excl in exclude_dirs)]
                
                for file in files:
                    if file == f"{service_name}.py":
                        return os.path.join(root, file)
        except Exception as e:
            logger.error(f"❌ Error searching for Python file {service_name}: {e}")
        
        return None

    def check_service_for_discovery(self, file_path: str) -> Dict[str, Any]:
        """Check if a specific file should be added to discovery database"""
        operation_start = time.time()
        
        # Validate inputs
        if not file_path or not isinstance(file_path, str):
            result = {"success": False, "error": "Invalid file path provided", "file_path": file_path}
            self.log_operation("VALIDATE_INPUT", False, result)
            return result
        
        if not os.path.exists(file_path):
            result = {"success": False, "error": f"File not found: {file_path}", "file_path": file_path}
            self.log_operation("FILE_EXISTS", False, result)
            return result
        
        # Validate database integrity
        if not self.validate_database_integrity():
            result = {"success": False, "error": "Database integrity validation failed", "file_path": file_path}
            self.log_operation("DATABASE_INTEGRITY", False, result)
            return result
        
        # Determine service name from file path
        try:
            if file_path.endswith('.py'):
                service_name = Path(file_path).stem
                python_file_path = file_path
                mdc_file_path = os.path.join(self.mdc_rules_path, f"{service_name}.mdc")
                
                if not os.path.exists(mdc_file_path):
                    result = {"success": False, "error": f"Python file exists but no MDC file for {service_name}", "service_name": service_name, "python_path": python_file_path}
                    self.log_operation("MDC_MISSING", False, result)
                    return result
                    
            elif file_path.endswith('.mdc'):
                service_name = Path(file_path).stem
                mdc_file_path = file_path
                
                python_file_path = self.find_python_file(service_name)
                if not python_file_path:
                    result = {"success": False, "error": f"MDC file exists but no Python file for {service_name}", "service_name": service_name, "mdc_path": mdc_file_path}
                    self.log_operation("PYTHON_MISSING", False, result)
                    return result
            else:
                result = {"success": False, "error": f"Unsupported file type: {file_path}", "file_path": file_path}
                self.log_operation("UNSUPPORTED_FILE", False, result)
                return result
        except Exception as e:
            result = {"success": False, "error": f"File path processing error: {e}", "file_path": file_path}
            self.log_operation("FILE_PROCESSING", False, result)
            return result
        
        # Check if service has passport (exclude if it does)
        if self.has_passport(service_name):
            result = {"success": True, "skipped": True, "reason": f"{service_name} has passport, not adding to discovery database", "service_name": service_name}
            self.log_operation("HAS_PASSPORT", True, result)
            return result
        
        # Check for duplicates
        duplicate_error = self.check_duplicates(service_name, python_file_path)
        if duplicate_error:
            result = {"success": False, "error": duplicate_error, "service_name": service_name, "python_path": python_file_path}
            self.log_operation("DUPLICATE_CHECK", False, result)
            return result
        
        # Add to discovery database
        try:
            conn = sqlite3.connect(self.discovery_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO discovery_services 
                (service_name, discovered_date, status, has_mdc_file, has_python_file, python_file_path, mdc_file_path, updated_at) 
                VALUES (?, ?, 'DISCOVERED', 1, 1, ?, ?, ?)
            ''', (service_name, datetime.now(), python_file_path, mdc_file_path, datetime.now()))
            
            conn.commit()
            conn.close()
            
            operation_time = (time.time() - operation_start) * 1000
            result = {
                "success": True,
                "service_name": service_name,
                "python_file_path": python_file_path,
                "mdc_file_path": mdc_file_path,
                "operation_time_ms": round(operation_time, 2)
            }
            
            self.log_operation("ADD_TO_DATABASE", True, result)
            return result
            
        except Exception as e:
            result = {"success": False, "error": f"Database insertion failed: {e}", "service_name": service_name}
            self.log_operation("DATABASE_INSERT", False, result)
            return result

    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get discovery database statistics"""
        try:
            conn = sqlite3.connect(self.discovery_db)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM discovery_services')
            total_services = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM discovery_services WHERE status = "DISCOVERED"')
            discovered_services = cursor.fetchone()[0]
            
            cursor.execute('SELECT MAX(updated_at) FROM discovery_services')
            last_updated = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_services": total_services,
                "discovered_services": discovered_services,
                "last_updated": last_updated,
                "database_path": self.discovery_db
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting discovery stats: {e}")
            return {"error": str(e)}

def print_usage():
    """Print usage information"""
    print("""
🔍 Discovery Trigger - Professional Service

USAGE:
    python3 discovery_trigger_professional.py <file_path>

EXAMPLES:
    # Trigger for new Python file
    python3 discovery_trigger_professional.py /path/to/new_service.py
    
    # Trigger for new MDC file
    python3 discovery_trigger_professional.py /path/to/new_service.mdc

FEATURES:
    ✅ Professional logging and audit trails
    ✅ Comprehensive duplicate checking
    ✅ Database integrity validation
    ✅ Performance metrics and monitoring
    ✅ Error handling and recovery

LOGS:
    - Service Log: /Users/dansidanutz/Desktop/ZmartBot/zmart-api/logs/discovery_trigger.log
    - Audit Log: /Users/dansidanutz/Desktop/ZmartBot/zmart-api/logs/discovery_audit.log
    """)

def main():
    """Main function - process file provided as argument"""
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help', 'help']:
        print_usage()
        sys.exit(0)
    
    if len(sys.argv) != 2:
        print("❌ Error: Exactly one file path argument required")
        print_usage()
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print(f"🚀 Discovery Trigger Professional - Starting")
    print(f"🔍 Processing file: {file_path}")
    print(f"📊 Log files: /Users/dansidanutz/Desktop/ZmartBot/zmart-api/logs/")
    print("")
    
    try:
        # Initialize discovery trigger service
        trigger_service = DiscoveryTrigger()
        
        # Process the file
        result = trigger_service.check_service_for_discovery(file_path)
        
        # Display results
        if result["success"]:
            if result.get("skipped"):
                print(f"⏭️  SKIPPED: {result['reason']}")
            else:
                print(f"✅ SUCCESS: Service '{result['service_name']}' added to discovery database")
                print(f"   📄 Python: {result['python_file_path']}")
                print(f"   📋 MDC: {result['mdc_file_path']}")
                print(f"   ⏱️  Processing time: {result['operation_time_ms']}ms")
        else:
            print(f"❌ FAILED: {result['error']}")
        
        # Display metrics
        metrics = trigger_service.get_metrics()
        print(f"\n📊 SESSION METRICS:")
        print(f"   Operations: {metrics['total_operations']}")
        print(f"   Success Rate: {metrics['success_rate_percent']}%")
        print(f"   Session Time: {metrics['uptime_seconds']}s")
        
        # Display discovery stats
        stats = trigger_service.get_discovery_stats()
        if "error" not in stats:
            print(f"\n🔍 DISCOVERY DATABASE STATS:")
            print(f"   Total Services: {stats['total_services']}")
            print(f"   Discovered Services: {stats['discovered_services']}")
            print(f"   Last Updated: {stats['last_updated'] or 'Never'}")
        
        # Exit with appropriate code
        sys.exit(0 if result["success"] else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Discovery Trigger interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        logger.error(f"Critical error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()