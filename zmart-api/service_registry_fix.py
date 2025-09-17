#!/usr/bin/env python3
"""
Service Registry Database Fix - Master Level 3 Registry System
Created: 2025-08-31
Purpose: Fix service registry chaos and create unified Level 3 certified service registry
Level: 3 (Authority System)
Port: 8902
Passport: SERVICE-REGISTRY-FIX-8902-L3
Owner: zmartbot-system
Status: AUTHORITY
"""

import os
import sys
import sqlite3
import json
import glob
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, jsonify, request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceRegistryFix:
    """Master Service Registry Database Fix and Level 3 Integration"""
    
    def __init__(self, port=8902):
        self.port = port
        self.app = Flask(__name__)
        self.root_dir = Path(".")
        self.master_registry = self.root_dir / "service_registry_master" / "master_service_registry.db"
        
        # Ensure directory exists
        self.master_registry.parent.mkdir(exist_ok=True)
        
        self.setup_master_database()
        self.setup_routes()
    
    def setup_master_database(self):
        """Setup the definitive master service registry database"""
        conn = sqlite3.connect(self.master_registry)
        cursor = conn.cursor()
        
        # Master Services Registry with Level 3 support
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE NOT NULL,
                passport_id TEXT UNIQUE NOT NULL,
                port INTEGER,
                service_type TEXT NOT NULL,
                service_level INTEGER DEFAULT 1,
                certification_status TEXT DEFAULT 'UNCERTIFIED',
                cert_id TEXT,
                status TEXT DEFAULT 'DISCOVERED',
                health_endpoint TEXT,
                start_command TEXT,
                stop_command TEXT,
                file_path TEXT,
                mdc_file_path TEXT,
                dependencies TEXT,
                description TEXT,
                owner TEXT DEFAULT 'zmartbot-system',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_health_check TIMESTAMP,
                cert_issued_at TIMESTAMP,
                cert_expires_at TIMESTAMP,
                audit_score INTEGER DEFAULT 0,
                uptime_percentage REAL DEFAULT 0.0,
                performance_score INTEGER DEFAULT 0,
                security_score INTEGER DEFAULT 0,
                reliability_score INTEGER DEFAULT 0,
                compliance_score INTEGER DEFAULT 0
            )
        """)
        
        # Service Categories for organization
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT UNIQUE,
                description TEXT,
                level_requirement INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Registry Consolidation Log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registry_consolidation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_database TEXT,
                services_migrated INTEGER,
                operation_type TEXT,
                status TEXT,
                error_log TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Service Dependencies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                depends_on TEXT,
                dependency_type TEXT,
                required BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Insert default categories
        self.setup_default_categories()
    
    def setup_default_categories(self):
        """Setup default service categories"""
        conn = sqlite3.connect(self.master_registry)
        cursor = conn.cursor()
        
        categories = [
            ("core", "Core system services - Level 3 required", 3),
            ("backend", "Backend API services", 2),
            ("frontend", "Frontend dashboard services", 2),
            ("monitoring", "System monitoring services", 2),
            ("security", "Security and authentication services - Level 3 required", 3),
            ("orchestration", "Service orchestration and management - Level 3 required", 3),
            ("data", "Data processing and storage services", 2),
            ("library", "Library components and utilities", 1),
            ("daemon", "Background daemon services", 2),
            ("authority", "Authority and certification services - Level 3 required", 3),
            ("governance", "Governance and compliance services - Level 3 required", 3)
        ]
        
        for category, description, level in categories:
            cursor.execute("""
                INSERT OR REPLACE INTO service_categories (category_name, description, level_requirement)
                VALUES (?, ?, ?)
            """, (category, description, level))
        
        conn.commit()
        conn.close()
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "service": "service-registry-fix",
                "port": self.port,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/consolidate-all')
        def consolidate_all():
            """Consolidate all service registries into master database"""
            try:
                result = self.consolidate_all_registries()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/master-registry')
        def get_master_registry():
            """Get all services in master registry"""
            try:
                services = self.get_all_services()
                return jsonify({
                    "total_services": len(services),
                    "services": services
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/level3-candidates')
        def get_level3_candidates():
            """Get services eligible for Level 3 certification"""
            try:
                candidates = self.get_level3_candidates()
                return jsonify({
                    "total_candidates": len(candidates),
                    "candidates": candidates
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/fix-status')
        def get_fix_status():
            """Get overall registry fix status"""
            try:
                status = self.get_registry_fix_status()
                return jsonify(status)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def consolidate_all_registries(self) -> Dict:
        """Consolidate all service registries into master database"""
        logger.info("Starting comprehensive service registry consolidation...")
        
        consolidated_services = 0
        errors = []
        source_databases = []
        
        # 1. Consolidate from GOODDatabase.db
        good_services = self.migrate_from_good_database()
        consolidated_services += good_services
        source_databases.append(("GOODDatabase.db", good_services))
        
        # 2. Consolidate from consolidated registry
        consolidated_registry_services = self.migrate_from_consolidated_registry() 
        consolidated_services += consolidated_registry_services
        source_databases.append(("consolidated_registry.db", consolidated_registry_services))
        
        # 3. Find and consolidate from other service registries
        other_registries = self.find_other_service_registries()
        for registry_path in other_registries:
            try:
                migrated = self.migrate_from_registry(registry_path)
                consolidated_services += migrated
                source_databases.append((registry_path, migrated))
            except Exception as e:
                error_msg = f"Error migrating {registry_path}: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # 4. Update service levels and prepare for certification
        level3_candidates = self.prepare_level3_candidates()
        
        # Log consolidation
        self.log_consolidation("COMPLETE_CONSOLIDATION", source_databases, errors)
        
        return {
            "status": "completed" if not errors else "completed_with_errors",
            "total_services_consolidated": consolidated_services,
            "source_databases": len(source_databases),
            "databases_processed": source_databases,
            "level3_candidates": level3_candidates,
            "errors": errors,
            "master_registry_path": str(self.master_registry),
            "timestamp": datetime.now().isoformat()
        }
    
    def migrate_from_good_database(self) -> int:
        """Migrate services from GOODDatabase.db"""
        try:
            good_conn = sqlite3.connect('../GOODDatabase.db')
            good_cursor = good_conn.cursor()
            
            master_conn = sqlite3.connect(self.master_registry)
            master_cursor = master_conn.cursor()
            
            good_cursor.execute("SELECT service_name, passport_id, port, service_type, status, file_path, notes FROM services")
            services = good_cursor.fetchall()
            
            migrated = 0
            for service in services:
                try:
                    # Determine service level based on passport
                    service_level = 3 if service[1] and '-L3' in service[1] else (2 if service[1] and '-L2' in service[1] else 1)
                    
                    master_cursor.execute("""
                        INSERT OR REPLACE INTO master_services 
                        (service_name, passport_id, port, service_type, service_level, status, 
                         file_path, description, health_endpoint)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        service[0], service[1], service[2], service[3], service_level,
                        service[4], service[5], service[6], 
                        f"http://127.0.0.1:{service[2]}/health" if service[2] else None
                    ))
                    migrated += 1
                except Exception as e:
                    logger.error(f"Error migrating service {service[0]}: {e}")
            
            master_conn.commit()
            good_conn.close()
            master_conn.close()
            
            logger.info(f"✅ Migrated {migrated} services from GOODDatabase.db")
            return migrated
            
        except Exception as e:
            logger.error(f"Error migrating from GOODDatabase.db: {e}")
            return 0
    
    def migrate_from_consolidated_registry(self) -> int:
        """Migrate additional services from consolidated registry"""
        try:
            consolidated_conn = sqlite3.connect('registries/consolidated_registry.db')
            consolidated_cursor = consolidated_conn.cursor()
            
            master_conn = sqlite3.connect(self.master_registry)
            master_cursor = master_conn.cursor()
            
            # Get services not already in master registry
            consolidated_cursor.execute("""
                SELECT service_name, service_type, port, status, source_file 
                FROM services_registry
            """)
            services = consolidated_cursor.fetchall()
            
            migrated = 0
            for service in services:
                try:
                    # Check if already exists
                    master_cursor.execute("SELECT id FROM master_services WHERE service_name = ?", (service[0],))
                    if master_cursor.fetchone():
                        continue  # Skip duplicates
                    
                    # Generate passport for non-GOODDatabase services
                    passport_id = f"{service[0].upper().replace('-', '_')}-{service[2] or 'NOPORT'}-L1"
                    
                    master_cursor.execute("""
                        INSERT INTO master_services 
                        (service_name, passport_id, port, service_type, service_level, status, 
                         file_path, health_endpoint)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        service[0], passport_id, service[2], service[1], 1,
                        service[3] or 'DISCOVERED', service[4],
                        f"http://127.0.0.1:{service[2]}/health" if service[2] else None
                    ))
                    migrated += 1
                except Exception as e:
                    logger.error(f"Error migrating consolidated service {service[0]}: {e}")
            
            master_conn.commit()
            consolidated_conn.close()
            master_conn.close()
            
            logger.info(f"✅ Migrated {migrated} additional services from consolidated registry")
            return migrated
            
        except Exception as e:
            logger.error(f"Error migrating from consolidated registry: {e}")
            return 0
    
    def find_other_service_registries(self) -> List[str]:
        """Find other service registry databases"""
        registry_files = []
        patterns = ["**/service_registry.db", "**/services.db", "**/registry.db"]
        
        for pattern in patterns:
            for file_path in glob.glob(pattern, recursive=True):
                if "backups" not in file_path and "master_service_registry.db" not in file_path:
                    registry_files.append(file_path)
        
        return registry_files
    
    def migrate_from_registry(self, registry_path: str) -> int:
        """Migrate services from individual registry database"""
        try:
            if not os.path.exists(registry_path) or os.path.getsize(registry_path) == 0:
                return 0
                
            source_conn = sqlite3.connect(registry_path)
            source_cursor = source_conn.cursor()
            
            # Get table names
            source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in source_cursor.fetchall()]
            
            master_conn = sqlite3.connect(self.master_registry)
            master_cursor = master_conn.cursor()
            
            migrated = 0
            for table in tables:
                if 'service' in table.lower():
                    migrated += self.migrate_service_table(source_cursor, master_cursor, table)
            
            master_conn.commit()
            source_conn.close()
            master_conn.close()
            
            return migrated
            
        except Exception as e:
            logger.error(f"Error migrating from {registry_path}: {e}")
            return 0
    
    def migrate_service_table(self, source_cursor, master_cursor, table_name: str) -> int:
        """Migrate service table data"""
        try:
            source_cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = source_cursor.fetchall()
            columns = [col[1] for col in columns_info]
            
            source_cursor.execute(f"SELECT * FROM {table_name}")
            rows = source_cursor.fetchall()
            
            migrated = 0
            for row in rows:
                try:
                    data_dict = dict(zip(columns, row))
                    
                    service_name = data_dict.get('service_name') or data_dict.get('name')
                    if not service_name:
                        continue
                    
                    # Check if already exists
                    master_cursor.execute("SELECT id FROM master_services WHERE service_name = ?", (service_name,))
                    if master_cursor.fetchone():
                        continue
                    
                    # Generate passport if not exists
                    passport_id = data_dict.get('passport_id') or f"{service_name.upper().replace('-', '_')}-L1"
                    
                    master_cursor.execute("""
                        INSERT INTO master_services 
                        (service_name, passport_id, port, service_type, status, file_path, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        service_name,
                        passport_id,
                        data_dict.get('port'),
                        data_dict.get('service_type') or data_dict.get('kind') or 'unknown',
                        data_dict.get('status') or 'DISCOVERED',
                        data_dict.get('file_path'),
                        data_dict.get('description') or data_dict.get('notes')
                    ))
                    migrated += 1
                    
                except Exception as e:
                    logger.error(f"Error migrating service row: {e}")
            
            return migrated
            
        except Exception as e:
            logger.error(f"Error migrating table {table_name}: {e}")
            return 0
    
    def prepare_level3_candidates(self) -> int:
        """Identify and prepare Level 3 certification candidates"""
        conn = sqlite3.connect(self.master_registry)
        cursor = conn.cursor()
        
        # Update services that should be Level 3 based on service type and existing passports
        level3_categories = ['authority', 'governance', 'orchestration', 'security', 'core']
        
        for category in level3_categories:
            cursor.execute("""
                UPDATE master_services 
                SET service_level = 3, certification_status = 'CANDIDATE'
                WHERE service_type = ? AND service_level < 3
            """, (category,))
        
        # Update services with L3 passports
        cursor.execute("""
            UPDATE master_services 
            SET service_level = 3, certification_status = 'CANDIDATE'
            WHERE passport_id LIKE '%-L3' OR passport_id LIKE '%CERT%'
        """)
        
        # Count Level 3 candidates
        cursor.execute("""
            SELECT COUNT(*) FROM master_services 
            WHERE service_level = 3 OR certification_status = 'CANDIDATE'
        """)
        candidates = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return candidates
    
    def get_all_services(self) -> List[Dict]:
        """Get all services from master registry"""
        conn = sqlite3.connect(self.master_registry)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT service_name, passport_id, port, service_type, service_level,
                   certification_status, status, description, created_at
            FROM master_services
            ORDER BY service_level DESC, service_name
        """)
        
        services = []
        for row in cursor.fetchall():
            services.append({
                'service_name': row[0],
                'passport_id': row[1],
                'port': row[2],
                'service_type': row[3],
                'service_level': row[4],
                'certification_status': row[5],
                'status': row[6],
                'description': row[7],
                'created_at': row[8]
            })
        
        conn.close()
        return services
    
    def get_level3_candidates(self) -> List[Dict]:
        """Get services eligible for Level 3 certification"""
        conn = sqlite3.connect(self.master_registry)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT service_name, passport_id, port, service_type, certification_status, 
                   audit_score, mdc_file_path
            FROM master_services 
            WHERE service_level = 3 OR certification_status = 'CANDIDATE'
            ORDER BY audit_score DESC
        """)
        
        candidates = []
        for row in cursor.fetchall():
            # Check if MDC file exists
            mdc_exists = self.check_mdc_file_exists(row[0])
            
            candidates.append({
                'service_name': row[0],
                'passport_id': row[1], 
                'port': row[2],
                'service_type': row[3],
                'certification_status': row[4],
                'audit_score': row[5],
                'mdc_file_path': row[6],
                'mdc_exists': mdc_exists,
                'ready_for_certification': mdc_exists and row[2] is not None
            })
        
        conn.close()
        return candidates
    
    def check_mdc_file_exists(self, service_name: str) -> bool:
        """Check if MDC file exists for service"""
        mdc_patterns = [
            f"**/*{service_name}*.mdc",
            f"**/{service_name}.mdc",
            f"**/{service_name.title()}*.mdc"
        ]
        
        for pattern in mdc_patterns:
            mdc_files = list(Path(".").glob(pattern))
            if mdc_files:
                return True
        return False
    
    def get_registry_fix_status(self) -> Dict:
        """Get comprehensive registry fix status"""
        conn = sqlite3.connect(self.master_registry)
        cursor = conn.cursor()
        
        # Service counts by level
        cursor.execute("""
            SELECT service_level, COUNT(*) 
            FROM master_services 
            GROUP BY service_level
        """)
        level_counts = dict(cursor.fetchall())
        
        # Certification status counts
        cursor.execute("""
            SELECT certification_status, COUNT(*)
            FROM master_services
            GROUP BY certification_status
        """)
        cert_status_counts = dict(cursor.fetchall())
        
        # Service type distribution
        cursor.execute("""
            SELECT service_type, COUNT(*)
            FROM master_services
            GROUP BY service_type
            ORDER BY COUNT(*) DESC
        """)
        type_distribution = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "master_registry_path": str(self.master_registry),
            "service_level_distribution": level_counts,
            "certification_status_distribution": cert_status_counts,
            "service_type_distribution": type_distribution,
            "total_services": sum(level_counts.values()),
            "level3_candidates": level_counts.get(3, 0),
            "last_updated": datetime.now().isoformat()
        }
    
    def log_consolidation(self, operation: str, databases: List[tuple], errors: List[str]):
        """Log consolidation operation"""
        conn = sqlite3.connect(self.master_registry)
        cursor = conn.cursor()
        
        for db_path, services_count in databases:
            cursor.execute("""
                INSERT INTO registry_consolidation 
                (source_database, services_migrated, operation_type, status, error_log)
                VALUES (?, ?, ?, ?, ?)
            """, (
                db_path, services_count, operation,
                'SUCCESS' if not errors else 'WARNING',
                json.dumps(errors) if errors else None
            ))
        
        conn.commit()
        conn.close()
    
    def run(self):
        """Run the service registry fix system"""
        logger.info(f"Starting Service Registry Fix Authority on port {self.port}")
        logger.info("Master Service Registry Database Fix System Ready")
        
        try:
            self.app.run(host='127.0.0.1', port=self.port, debug=False)
        except KeyboardInterrupt:
            logger.info("Service Registry Fix stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Service Registry Database Fix - Level 3 System")
    parser.add_argument('--port', type=int, default=8902, help='Service port')
    parser.add_argument('--service', action='store_true', help='Run as service')
    parser.add_argument('--fix', action='store_true', help='Run complete registry fix')
    parser.add_argument('--status', action='store_true', help='Show current registry status')
    
    args = parser.parse_args()
    
    registry_fix = ServiceRegistryFix(port=args.port)
    
    if args.fix:
        result = registry_fix.consolidate_all_registries()
        print(f"Registry Fix Result: {json.dumps(result, indent=2)}")
    elif args.status:
        status = registry_fix.get_registry_fix_status()
        print(f"Registry Status: {json.dumps(status, indent=2)}")
    elif args.service:
        registry_fix.run()
    else:
        print("Service Registry Database Fix - Level 3 System")
        print("Commands:")
        print("  --service  : Run as API service")
        print("  --fix      : Run complete registry consolidation fix")
        print("  --status   : Show current registry status")

if __name__ == "__main__":
    main()