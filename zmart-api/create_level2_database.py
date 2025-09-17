#!/usr/bin/env python3
"""
Level 2 Database Creator - Active Production Services Registry
Created: 2025-08-31
Purpose: Create clean Level2.db for active production services with documentation
Level: 3 (Authority System)
Port: 8904
Passport: LEVEL2-DB-CREATOR-8904-L3
Owner: zmartbot-system
Status: AUTHORITY
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from flask import Flask, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Level2DatabaseCreator:
    """Create clean Level 2 database for active production services"""
    
    def __init__(self, port=8904):
        self.port = port
        self.app = Flask(__name__)
        self.root_dir = Path(".")
        self.level2_db = self.root_dir / "Level2.db"
        
        self.setup_level2_database()
        self.setup_routes()
    
    def setup_level2_database(self):
        """Setup clean Level 2 active services database"""
        conn = sqlite3.connect(self.level2_db)
        cursor = conn.cursor()
        
        # Level 2 Active Production Services
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level2_active_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE NOT NULL,
                passport_id TEXT UNIQUE NOT NULL,
                port INTEGER NOT NULL,
                service_type TEXT NOT NULL,
                status TEXT DEFAULT 'ACTIVE',
                file_path TEXT,
                mdc_file_path TEXT,
                health_endpoint TEXT,
                start_command TEXT,
                stop_command TEXT,
                description TEXT,
                owner TEXT DEFAULT 'zmartbot-system',
                documentation_complete BOOLEAN DEFAULT FALSE,
                operational_status TEXT DEFAULT 'RUNNING',
                last_health_check TIMESTAMP,
                uptime_percentage REAL DEFAULT 0.0,
                response_time_avg INTEGER DEFAULT 0,
                activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Level 2 Service Health
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level2_health_monitoring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                health_status TEXT,
                response_time INTEGER,
                last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                error_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0
            )
        """)
        
        # Level 2 Documentation Tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level2_documentation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                mdc_exists BOOLEAN DEFAULT FALSE,
                api_docs_exists BOOLEAN DEFAULT FALSE,
                deployment_guide_exists BOOLEAN DEFAULT FALSE,
                documentation_score INTEGER DEFAULT 0,
                last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                "service": "level2-database-creator", 
                "port": self.port,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/create-level2')
        def create_level2():
            """Create clean Level 2 database"""
            try:
                result = self.create_clean_level2_database()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/level2-services')
        def get_level2_services():
            """Get all Level 2 active services"""
            try:
                services = self.get_level2_services()
                return jsonify({
                    "total_level2": len(services),
                    "services": services
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def create_clean_level2_database(self) -> Dict:
        """Create clean Level 2 database for active services"""
        logger.info("Creating clean Level 2 database...")
        
        # Get services from Passport Registry (these are Level 2+)
        passport_services = self.get_passport_services()
        
        # Get services from Service Registry (these are Level 2+) 
        service_registry_services = self.get_service_registry_services()
        
        # Get our new Level 2 services (with -L2 passports)
        level2_new_services = self.get_level2_new_services()
        
        # Combine all Level 2 services
        all_level2 = []
        all_level2.extend(passport_services)
        all_level2.extend(service_registry_services)
        all_level2.extend(level2_new_services)
        
        # Remove duplicates by service_name
        seen_names = set()
        unique_level2 = []
        for service in all_level2:
            if service['service_name'] not in seen_names:
                seen_names.add(service['service_name'])
                unique_level2.append(service)
        
        # Populate Level 2 database
        self.populate_level2_database(unique_level2)
        
        return {
            "status": "completed",
            "total_level2_services": len(unique_level2),
            "sources": {
                "passport_registry": len(passport_services),
                "service_registry": len(service_registry_services), 
                "new_level2_services": len(level2_new_services)
            },
            "level2_database_path": str(self.level2_db),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_passport_services(self) -> List[Dict]:
        """Get services from passport registry"""
        try:
            conn = sqlite3.connect('data/passport_registry.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, passport_id, port, service_type, status, file_path, description
                FROM passport_registry
            """)
            
            services = []
            for row in cursor.fetchall():
                services.append({
                    'service_name': row[0],
                    'passport_id': row[1],
                    'port': row[2],
                    'service_type': row[3],
                    'status': row[4] or 'ACTIVE',
                    'file_path': row[5],
                    'description': row[6],
                    'source': 'passport_registry'
                })
            
            conn.close()
            return services
            
        except Exception as e:
            logger.error(f"Error getting passport services: {e}")
            return []
    
    def get_service_registry_services(self) -> List[Dict]:
        """Get services from service registry"""
        try:
            conn = sqlite3.connect('src/data/service_registry.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, port, kind, status, start_cmd, health_url, description
                FROM service_registry
            """)
            
            services = []
            for row in cursor.fetchall():
                passport_id = f"SR-{row[0].upper().replace('-', '_')}-{row[1]}-L2"
                services.append({
                    'service_name': row[0],
                    'passport_id': passport_id,
                    'port': row[1],
                    'service_type': row[2],
                    'status': row[3] or 'ACTIVE',
                    'start_command': row[4],
                    'health_endpoint': row[5],
                    'description': row[6],
                    'source': 'service_registry'
                })
            
            conn.close()
            return services
            
        except Exception as e:
            logger.error(f"Error getting service registry services: {e}")
            return []
    
    def get_level2_new_services(self) -> List[Dict]:
        """Get our newly created Level 2 services"""
        try:
            conn = sqlite3.connect('../GOODDatabase.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, passport_id, port, service_type, status, file_path, notes
                FROM services 
                WHERE passport_id LIKE '%-L2'
            """)
            
            services = []
            for row in cursor.fetchall():
                services.append({
                    'service_name': row[0],
                    'passport_id': row[1],
                    'port': row[2],
                    'service_type': row[3],
                    'status': row[4],
                    'file_path': row[5],
                    'description': row[6],
                    'source': 'good_database_l2'
                })
            
            conn.close()
            return services
            
        except Exception as e:
            logger.error(f"Error getting Level 2 new services: {e}")
            return []
    
    def populate_level2_database(self, level2_services: List[Dict]):
        """Populate Level 2 database"""
        conn = sqlite3.connect(self.level2_db)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM level2_active_services")
        
        for service in level2_services:
            try:
                # Check if MDC file exists
                mdc_exists = self.check_mdc_exists(service['service_name'])
                
                cursor.execute("""
                    INSERT INTO level2_active_services
                    (service_name, passport_id, port, service_type, status, file_path,
                     health_endpoint, start_command, description, documentation_complete)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    service['service_name'],
                    service['passport_id'],
                    service['port'],
                    service['service_type'],
                    service['status'],
                    service.get('file_path'),
                    service.get('health_endpoint', f"http://127.0.0.1:{service['port']}/health" if service['port'] else None),
                    service.get('start_command'),
                    service.get('description'),
                    mdc_exists
                ))
                
            except Exception as e:
                logger.error(f"Error adding Level 2 service {service['service_name']}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Populated Level 2 database with {len(level2_services)} active services")
    
    def check_mdc_exists(self, service_name: str) -> bool:
        """Check if MDC file exists"""
        mdc_patterns = [
            f"**/*{service_name}*.mdc",
            f"**/{service_name}.mdc",
            f"**/{service_name.title()}*.mdc"
        ]
        
        for pattern in mdc_patterns:
            if list(Path(".").glob(pattern)):
                return True
        return False
    
    def get_level2_services(self) -> List[Dict]:
        """Get all Level 2 services"""
        conn = sqlite3.connect(self.level2_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT service_name, passport_id, port, service_type, status, 
                   documentation_complete, operational_status, activated_at
            FROM level2_active_services
            ORDER BY port
        """)
        
        services = []
        for row in cursor.fetchall():
            services.append({
                'service_name': row[0],
                'passport_id': row[1],
                'port': row[2],
                'service_type': row[3],
                'status': row[4],
                'documentation_complete': bool(row[5]),
                'operational_status': row[6],
                'activated_at': row[7]
            })
        
        conn.close()
        return services
    
    def run(self):
        """Run the Level 2 database creator service"""
        logger.info(f"Starting Level 2 Database Creator on port {self.port}")
        logger.info("Level 2 Active Services Database System Ready")
        
        try:
            self.app.run(host='127.0.0.1', port=self.port, debug=False)
        except KeyboardInterrupt:
            logger.info("Level 2 Database Creator stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Level 2 Database Creator")
    parser.add_argument('--port', type=int, default=8904, help='Service port')
    parser.add_argument('--service', action='store_true', help='Run as service')
    parser.add_argument('--create', action='store_true', help='Create Level 2 database')
    
    args = parser.parse_args()
    
    creator = Level2DatabaseCreator(port=args.port)
    
    if args.create:
        result = creator.create_clean_level2_database()
        print(f"Level 2 Database Creation: {json.dumps(result, indent=2)}")
    elif args.service:
        creator.run()
    else:
        print("Level 2 Database Creator")
        print("Commands:")
        print("  --service   : Run as API service")
        print("  --create    : Create clean Level 2 database")

if __name__ == "__main__":
    main()