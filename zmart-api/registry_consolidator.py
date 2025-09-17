#!/usr/bin/env python3
"""
Registry Database Consolidator - ZmartBot System Organization
Created: 2025-08-31
Purpose: Consolidate all registry databases into a single, well-organized system
Level: 2 (Production Ready)
Port: 8898
Passport: REGO-CONSOLIDATOR-8898-L2
Owner: zmartbot-system
Status: ACTIVE
"""

import os
import sys
import sqlite3
import json
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegistryConsolidator:
    """Consolidate all registry databases into organized structure"""
    
    def __init__(self, port=8898):
        self.port = port
        self.app = Flask(__name__)
        self.root_dir = Path(".")
        self.consolidated_db = self.root_dir / "registries" / "consolidated_registry.db"
        self.backup_dir = self.root_dir / "registries" / "backups"
        
        # Ensure directories exist
        self.consolidated_db.parent.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Registry file patterns found in system
        self.registry_patterns = [
            "**/*registry*.db",
            "**/*Registry*.db", 
            "**/registry.db",
            "**/*database*registry*.db",
            "**/GOODDatabase.db",  # Critical: Main services database
            "**/*Database*.db",    # Other database files
            "**/*_db.db",          # Alternative database naming
            "**/*service*.db"      # Service-related databases
        ]
        
        self.setup_consolidated_database()
        self.setup_routes()
    
    def setup_consolidated_database(self):
        """Setup consolidated registry database with proper schema"""
        conn = sqlite3.connect(self.consolidated_db)
        cursor = conn.cursor()
        
        # Main services registry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS services_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE,
                service_type TEXT,
                port INTEGER,
                status TEXT DEFAULT 'inactive',
                pid INTEGER,
                start_command TEXT,
                stop_command TEXT,
                health_endpoint TEXT,
                dependencies TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_file TEXT
            )
        """)
        
        # Ports registry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ports_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                port INTEGER UNIQUE,
                service_name TEXT,
                status TEXT DEFAULT 'available',
                reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """)
        
        # Process registry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS process_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pid INTEGER,
                service_name TEXT,
                command TEXT,
                status TEXT,
                start_time TIMESTAMP,
                cpu_usage REAL,
                memory_usage REAL,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Configuration registry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                config_key TEXT,
                config_value TEXT,
                config_type TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(service_name, config_key)
            )
        """)
        
        # API endpoints registry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS endpoints_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                endpoint_path TEXT,
                method TEXT,
                description TEXT,
                port INTEGER,
                status TEXT DEFAULT 'active',
                last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Consolidation log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consolidation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT,
                source_file TEXT,
                target_table TEXT,
                records_migrated INTEGER,
                status TEXT,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "service": "registry-consolidator",
                "port": self.port,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/scan')
        def scan_registries():
            """Scan for all registry databases"""
            try:
                registries = self.scan_registry_files()
                return jsonify({
                    "total_found": len(registries),
                    "registries": registries
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/consolidate')
        def consolidate_all():
            """Consolidate all registry databases"""
            try:
                results = self.consolidate_registries()
                return jsonify(results)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/status')
        def consolidation_status():
            """Get consolidation status"""
            try:
                status = self.get_consolidation_status()
                return jsonify(status)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/backup')
        def backup_registries():
            """Backup all registry files"""
            try:
                results = self.backup_registry_files()
                return jsonify(results)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def scan_registry_files(self) -> List[Dict]:
        """Scan for all registry database files"""
        registry_files = []
        seen_files = set()
        
        for pattern in self.registry_patterns:
            for file_path in glob.glob(pattern, recursive=True):
                if file_path not in seen_files and file_path.endswith('.db'):
                    seen_files.add(file_path)
                    
                    file_info = {
                        "path": file_path,
                        "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat() if os.path.exists(file_path) else None,
                        "tables": self.get_database_tables(file_path)
                    }
                    registry_files.append(file_info)
        
        return sorted(registry_files, key=lambda x: x['path'])
    
    def get_database_tables(self, db_path: str) -> List[str]:
        """Get table names from database"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception as e:
            logger.error(f"Error reading tables from {db_path}: {e}")
            return []
    
    def backup_registry_files(self) -> Dict:
        """Backup all registry files before consolidation"""
        registries = self.scan_registry_files()
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_count = 0
        
        for registry in registries:
            try:
                source = Path(registry['path'])
                backup_name = f"{source.stem}_{backup_timestamp}{source.suffix}"
                backup_path = self.backup_dir / backup_name
                
                # Copy file
                import shutil
                shutil.copy2(source, backup_path)
                backup_count += 1
                
            except Exception as e:
                logger.error(f"Error backing up {registry['path']}: {e}")
        
        return {
            "status": "completed",
            "backed_up": backup_count,
            "total_found": len(registries),
            "backup_directory": str(self.backup_dir),
            "timestamp": backup_timestamp
        }
    
    def consolidate_registries(self) -> Dict:
        """Consolidate all registry databases into unified system"""
        registries = self.scan_registry_files()
        consolidated_records = 0
        errors = []
        
        # First backup existing files
        backup_results = self.backup_registry_files()
        
        conn = sqlite3.connect(self.consolidated_db)
        cursor = conn.cursor()
        
        for registry in registries:
            try:
                source_conn = sqlite3.connect(registry['path'])
                source_cursor = source_conn.cursor()
                
                # Migrate based on table structure
                for table in registry['tables']:
                    records_migrated = self.migrate_table(source_cursor, cursor, table, registry['path'])
                    consolidated_records += records_migrated
                    
                    # Log migration
                    cursor.execute("""
                        INSERT INTO consolidation_log (operation, source_file, target_table, records_migrated, status)
                        VALUES (?, ?, ?, ?, ?)
                    """, ("MIGRATE", registry['path'], table, records_migrated, "SUCCESS"))
                
                source_conn.close()
                
            except Exception as e:
                error_msg = f"Error consolidating {registry['path']}: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
                
                # Log error
                cursor.execute("""
                    INSERT INTO consolidation_log (operation, source_file, status, error_message)
                    VALUES (?, ?, ?, ?)
                """, ("MIGRATE", registry['path'], "ERROR", str(e)))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "completed" if not errors else "completed_with_errors",
            "consolidated_records": consolidated_records,
            "processed_registries": len(registries),
            "backup_info": backup_results,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    
    def migrate_table(self, source_cursor, target_cursor, table_name: str, source_file: str) -> int:
        """Migrate table data based on known patterns"""
        try:
            # Get table structure
            source_cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = source_cursor.fetchall()
            columns = [col[1] for col in columns_info]
            
            # Get all data
            source_cursor.execute(f"SELECT * FROM {table_name}")
            rows = source_cursor.fetchall()
            
            migrated_count = 0
            
            # Migrate based on table patterns
            if 'service' in table_name.lower():
                migrated_count = self.migrate_services(target_cursor, rows, columns, source_file)
            elif 'port' in table_name.lower():
                migrated_count = self.migrate_ports(target_cursor, rows, columns)
            elif 'process' in table_name.lower():
                migrated_count = self.migrate_processes(target_cursor, rows, columns)
            elif 'config' in table_name.lower():
                migrated_count = self.migrate_configs(target_cursor, rows, columns)
            elif 'endpoint' in table_name.lower() or 'api' in table_name.lower():
                migrated_count = self.migrate_endpoints(target_cursor, rows, columns)
            else:
                # Generic migration to config_registry
                migrated_count = self.migrate_generic(target_cursor, rows, columns, table_name, source_file)
            
            return migrated_count
            
        except Exception as e:
            logger.error(f"Error migrating table {table_name}: {e}")
            return 0
    
    def migrate_services(self, cursor, rows, columns, source_file) -> int:
        """Migrate service-related data"""
        migrated = 0
        for row in rows:
            try:
                data_dict = dict(zip(columns, row))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO services_registry 
                    (service_name, service_type, port, status, pid, start_command, stop_command, health_endpoint, source_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data_dict.get('service_name', data_dict.get('name', 'unknown')),
                    data_dict.get('service_type', data_dict.get('type', 'unknown')),
                    data_dict.get('port'),
                    data_dict.get('status', 'unknown'),
                    data_dict.get('pid'),
                    data_dict.get('start_command', data_dict.get('command')),
                    data_dict.get('stop_command'),
                    data_dict.get('health_endpoint'),
                    source_file
                ))
                migrated += 1
            except Exception as e:
                logger.error(f"Error migrating service row: {e}")
        return migrated
    
    def migrate_ports(self, cursor, rows, columns) -> int:
        """Migrate port-related data"""
        migrated = 0
        for row in rows:
            try:
                data_dict = dict(zip(columns, row))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO ports_registry 
                    (port, service_name, status, description)
                    VALUES (?, ?, ?, ?)
                """, (
                    data_dict.get('port'),
                    data_dict.get('service_name', data_dict.get('service')),
                    data_dict.get('status', 'available'),
                    data_dict.get('description', data_dict.get('notes'))
                ))
                migrated += 1
            except Exception as e:
                logger.error(f"Error migrating port row: {e}")
        return migrated
    
    def migrate_processes(self, cursor, rows, columns) -> int:
        """Migrate process-related data"""
        migrated = 0
        for row in rows:
            try:
                data_dict = dict(zip(columns, row))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO process_registry 
                    (pid, service_name, command, status, start_time, cpu_usage, memory_usage)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    data_dict.get('pid'),
                    data_dict.get('service_name', data_dict.get('service')),
                    data_dict.get('command'),
                    data_dict.get('status', 'unknown'),
                    data_dict.get('start_time'),
                    data_dict.get('cpu_usage'),
                    data_dict.get('memory_usage')
                ))
                migrated += 1
            except Exception as e:
                logger.error(f"Error migrating process row: {e}")
        return migrated
    
    def migrate_configs(self, cursor, rows, columns) -> int:
        """Migrate configuration data"""
        migrated = 0
        for row in rows:
            try:
                data_dict = dict(zip(columns, row))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO config_registry 
                    (service_name, config_key, config_value, config_type)
                    VALUES (?, ?, ?, ?)
                """, (
                    data_dict.get('service_name', data_dict.get('service', 'unknown')),
                    data_dict.get('config_key', data_dict.get('key')),
                    data_dict.get('config_value', data_dict.get('value')),
                    data_dict.get('config_type', data_dict.get('type', 'string'))
                ))
                migrated += 1
            except Exception as e:
                logger.error(f"Error migrating config row: {e}")
        return migrated
    
    def migrate_endpoints(self, cursor, rows, columns) -> int:
        """Migrate API endpoint data"""
        migrated = 0
        for row in rows:
            try:
                data_dict = dict(zip(columns, row))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO endpoints_registry 
                    (service_name, endpoint_path, method, description, port, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data_dict.get('service_name', data_dict.get('service')),
                    data_dict.get('endpoint_path', data_dict.get('path')),
                    data_dict.get('method', 'GET'),
                    data_dict.get('description'),
                    data_dict.get('port'),
                    data_dict.get('status', 'active')
                ))
                migrated += 1
            except Exception as e:
                logger.error(f"Error migrating endpoint row: {e}")
        return migrated
    
    def migrate_generic(self, cursor, rows, columns, table_name, source_file) -> int:
        """Generic migration to config_registry for unknown table types"""
        migrated = 0
        for row in rows:
            try:
                data_dict = dict(zip(columns, row))
                
                # Store as JSON configuration
                cursor.execute("""
                    INSERT OR REPLACE INTO config_registry 
                    (service_name, config_key, config_value, config_type)
                    VALUES (?, ?, ?, ?)
                """, (
                    f"legacy_{table_name}",
                    f"record_{migrated}",
                    json.dumps(data_dict),
                    "json"
                ))
                migrated += 1
            except Exception as e:
                logger.error(f"Error migrating generic row: {e}")
        return migrated
    
    def get_consolidation_status(self) -> Dict:
        """Get current consolidation status"""
        try:
            conn = sqlite3.connect(self.consolidated_db)
            cursor = conn.cursor()
            
            # Get table counts
            tables_status = {}
            for table in ['services_registry', 'ports_registry', 'process_registry', 'config_registry', 'endpoints_registry']:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                tables_status[table] = cursor.fetchone()[0]
            
            # Get recent consolidation logs
            cursor.execute("""
                SELECT operation, source_file, records_migrated, status, timestamp 
                FROM consolidation_log 
                ORDER BY timestamp DESC 
                LIMIT 10
            """)
            recent_logs = [
                {
                    "operation": row[0],
                    "source_file": row[1], 
                    "records_migrated": row[2],
                    "status": row[3],
                    "timestamp": row[4]
                }
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            registry_files = self.scan_registry_files()
            
            return {
                "consolidated_database": str(self.consolidated_db),
                "table_counts": tables_status,
                "total_records": sum(tables_status.values()),
                "source_registries_found": len(registry_files),
                "recent_operations": recent_logs,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "status": "ERROR"}
    
    def run(self):
        """Run the consolidation service"""
        logger.info(f"Starting Registry Consolidator Service on port {self.port}")
        
        # Initial scan and status
        registries = self.scan_registry_files()
        logger.info(f"Found {len(registries)} registry databases to consolidate")
        
        try:
            self.app.run(host='127.0.0.1', port=self.port, debug=False)
        except KeyboardInterrupt:
            logger.info("Registry Consolidator Service stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Registry Database Consolidator")
    parser.add_argument('--port', type=int, default=8898, help='Service port')
    parser.add_argument('--consolidate', action='store_true', help='Run consolidation immediately')
    parser.add_argument('--service', action='store_true', help='Run as service')
    
    args = parser.parse_args()
    
    consolidator = RegistryConsolidator(port=args.port)
    
    if args.consolidate:
        logger.info("Running immediate consolidation...")
        results = consolidator.consolidate_registries()
        logger.info(f"Consolidation completed: {results}")
    
    if args.service:
        consolidator.run()
    else:
        print("Registry Database Consolidator")
        print("Options:")
        print("  --consolidate  : Run immediate consolidation")
        print("  --service      : Run as API service")
        print(f"  --port {args.port}    : Specify port (default: 8898)")

if __name__ == "__main__":
    main()