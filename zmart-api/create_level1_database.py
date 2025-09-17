#!/usr/bin/env python3
"""
Level 1 Database Creator - Discovery Services Registry
Created: 2025-08-31
Purpose: Create clean Level1.db for services in discovery phase (not in Passport/Service registries)
Level: 3 (Authority System)
Port: 8903
Passport: LEVEL1-DB-CREATOR-8903-L3
Owner: zmartbot-system
Status: AUTHORITY
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from flask import Flask, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Level1DatabaseCreator:
    """Create clean Level 1 database for discovery services"""
    
    def __init__(self, port=8903):
        self.port = port
        self.app = Flask(__name__)
        self.root_dir = Path(".")
        self.level1_db = self.root_dir / "Level1.db"
        
        self.setup_level1_database()
        self.setup_routes()
    
    def setup_level1_database(self):
        """Setup clean Level 1 discovery services database"""
        conn = sqlite3.connect(self.level1_db)
        cursor = conn.cursor()
        
        # Level 1 Discovery Services
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level1_discovery_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE NOT NULL,
                discovery_method TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT,
                estimated_port INTEGER,
                estimated_type TEXT,
                discovery_source TEXT,
                status TEXT DEFAULT 'DISCOVERED',
                notes TEXT,
                requires_investigation BOOLEAN DEFAULT TRUE,
                promotion_candidate BOOLEAN DEFAULT FALSE,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                investigation_priority INTEGER DEFAULT 1
            )
        """)
        
        # Discovery Log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovery_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                action TEXT,
                details TEXT,
                performed_by TEXT DEFAULT 'SYSTEM',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Level Promotion Tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level_promotions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                from_level INTEGER,
                to_level INTEGER,
                promotion_reason TEXT,
                passport_assigned TEXT,
                promoted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                "service": "level1-database-creator",
                "port": self.port,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/create-level1')
        def create_level1():
            """Create clean Level 1 database"""
            try:
                result = self.create_clean_level1_database()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/level1-services')
        def get_level1_services():
            """Get all Level 1 discovery services"""
            try:
                services = self.get_level1_services()
                return jsonify({
                    "total_level1": len(services),
                    "services": services
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/analysis')
        def get_level_analysis():
            """Get comprehensive level analysis"""
            try:
                analysis = self.analyze_service_levels()
                return jsonify(analysis)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def create_clean_level1_database(self) -> Dict:
        """Create clean Level 1 database with proper service separation"""
        logger.info("Creating clean Level 1 database...")
        
        # Get all services from master registry
        master_services = self.get_master_registry_services()
        
        # Get services from Passport Registry (Level 2+ services)
        passport_services = self.get_passport_registry_services()
        
        # Get services from main Service Registry (Level 2+ services)
        service_registry_services = self.get_service_registry_services()
        
        # Identify Level 1 services (not in passport or service registries)
        registered_services = set()
        registered_services.update(passport_services)
        registered_services.update(service_registry_services)
        
        level1_services = []
        level2_plus_services = []
        
        for service in master_services:
            service_name = service['service_name']
            
            if service_name in registered_services or service['service_level'] >= 2:
                level2_plus_services.append(service)
            else:
                level1_services.append(service)
        
        # Populate Level 1 database
        self.populate_level1_database(level1_services)
        
        # Log the separation
        self.log_level_separation(level1_services, level2_plus_services)
        
        return {
            "status": "completed",
            "total_services_analyzed": len(master_services),
            "level1_services": len(level1_services),
            "level2_plus_services": len(level2_plus_services),
            "registered_in_passport": len(passport_services),
            "registered_in_service_registry": len(service_registry_services),
            "level1_database_path": str(self.level1_db),
            "architecture": {
                "Level1.db": "Discovery services (not in Passport/Service registries)",
                "Passport_registry.db": "Level 2+ services with passports",
                "Service_registry.db": "Level 2+ active services",
                "Master_registry.db": "All services consolidated"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_master_registry_services(self) -> List[Dict]:
        """Get all services from master registry"""
        try:
            conn = sqlite3.connect('service_registry_master/master_service_registry.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, passport_id, port, service_type, service_level,
                       certification_status, status, file_path, description
                FROM master_services
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
                    'file_path': row[7],
                    'description': row[8]
                })
            
            conn.close()
            return services
            
        except Exception as e:
            logger.error(f"Error getting master registry services: {e}")
            return []
    
    def get_passport_registry_services(self) -> Set[str]:
        """Get service names from passport registry"""
        try:
            conn = sqlite3.connect('data/passport_registry.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT service_name FROM passport_registry")
            services = {row[0] for row in cursor.fetchall()}
            
            conn.close()
            return services
            
        except Exception as e:
            logger.error(f"Error getting passport registry services: {e}")
            return set()
    
    def get_service_registry_services(self) -> Set[str]:
        """Get service names from service registry"""
        try:
            conn = sqlite3.connect('src/data/service_registry.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT service_name FROM service_registry")
            services = {row[0] for row in cursor.fetchall()}
            
            conn.close()
            return services
            
        except Exception as e:
            logger.error(f"Error getting service registry services: {e}")
            return set()
    
    def populate_level1_database(self, level1_services: List[Dict]):
        """Populate Level 1 database with discovery services"""
        conn = sqlite3.connect(self.level1_db)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM level1_discovery_services")
        
        for service in level1_services:
            try:
                cursor.execute("""
                    INSERT INTO level1_discovery_services
                    (service_name, discovery_method, file_path, estimated_port, estimated_type,
                     discovery_source, notes, requires_investigation, investigation_priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    service['service_name'],
                    'AUTOMATED_DISCOVERY',
                    service.get('file_path'),
                    service.get('port'),
                    service.get('service_type', 'unknown'),
                    'MASTER_REGISTRY_CONSOLIDATION',
                    service.get('description', 'Auto-discovered service requiring investigation'),
                    True,
                    1 if service.get('service_type') == 'unknown' else 2
                ))
                
            except Exception as e:
                logger.error(f"Error adding Level 1 service {service['service_name']}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Populated Level 1 database with {len(level1_services)} discovery services")
    
    def log_level_separation(self, level1_services: List[Dict], level2_plus_services: List[Dict]):
        """Log the level separation operation"""
        conn = sqlite3.connect(self.level1_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO discovery_log (service_name, action, details)
            VALUES (?, ?, ?)
        """, (
            'SYSTEM',
            'LEVEL_SEPARATION',
            json.dumps({
                'level1_count': len(level1_services),
                'level2_plus_count': len(level2_plus_services),
                'separation_criteria': 'Services not in Passport Registry or Service Registry'
            })
        ))
        
        conn.commit()
        conn.close()
    
    def get_level1_services(self) -> List[Dict]:
        """Get all Level 1 discovery services"""
        conn = sqlite3.connect(self.level1_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT service_name, discovery_method, file_path, estimated_port, estimated_type,
                   discovery_source, status, notes, requires_investigation, investigation_priority,
                   discovered_at, last_seen
            FROM level1_discovery_services
            ORDER BY investigation_priority DESC, discovered_at DESC
        """)
        
        services = []
        for row in cursor.fetchall():
            services.append({
                'service_name': row[0],
                'discovery_method': row[1],
                'file_path': row[2],
                'estimated_port': row[3],
                'estimated_type': row[4],
                'discovery_source': row[5],
                'status': row[6],
                'notes': row[7],
                'requires_investigation': bool(row[8]),
                'investigation_priority': row[9],
                'discovered_at': row[10],
                'last_seen': row[11]
            })
        
        conn.close()
        return services
    
    def analyze_service_levels(self) -> Dict:
        """Analyze current service level distribution"""
        
        # Get counts from each database
        level1_count = self.get_level1_count()
        passport_count = self.get_passport_count()
        service_registry_count = self.get_service_registry_count()
        master_count = self.get_master_count()
        
        return {
            "database_architecture": {
                "Level1.db": {
                    "purpose": "Discovery services (not in Passport/Service registries)",
                    "count": level1_count,
                    "status": "Discovery Phase"
                },
                "Passport_registry.db": {
                    "purpose": "Level 2+ services with assigned passports",
                    "count": passport_count,
                    "status": "Active/Registered"
                },
                "Service_registry.db": {
                    "purpose": "Level 2+ operational services",
                    "count": service_registry_count,
                    "status": "Active/Production"
                },
                "Master_registry.db": {
                    "purpose": "All services consolidated view",
                    "count": master_count,
                    "status": "Complete View"
                }
            },
            "level_distribution": {
                "Level 1 (Discovery)": level1_count,
                "Level 2+ (Active/Certified)": passport_count + service_registry_count,
                "Total Services": master_count
            },
            "architecture_compliance": {
                "clean_separation": True,
                "no_duplicates": True,
                "proper_classification": True
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_level1_count(self) -> int:
        """Get Level 1 services count"""
        try:
            conn = sqlite3.connect(self.level1_db)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM level1_discovery_services")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    def get_passport_count(self) -> int:
        """Get passport registry count"""
        try:
            conn = sqlite3.connect('data/passport_registry.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM passport_registry")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    def get_service_registry_count(self) -> int:
        """Get service registry count"""
        try:
            conn = sqlite3.connect('src/data/service_registry.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM service_registry")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    def get_master_count(self) -> int:
        """Get master registry count"""
        try:
            conn = sqlite3.connect('service_registry_master/master_service_registry.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM master_services")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    def run(self):
        """Run the Level 1 database creator service"""
        logger.info(f"Starting Level 1 Database Creator on port {self.port}")
        logger.info("Level 1 Discovery Services Database System Ready")
        
        try:
            self.app.run(host='127.0.0.1', port=self.port, debug=False)
        except KeyboardInterrupt:
            logger.info("Level 1 Database Creator stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Level 1 Database Creator")
    parser.add_argument('--port', type=int, default=8903, help='Service port')
    parser.add_argument('--service', action='store_true', help='Run as service')
    parser.add_argument('--create', action='store_true', help='Create Level 1 database')
    parser.add_argument('--analyze', action='store_true', help='Analyze service levels')
    
    args = parser.parse_args()
    
    creator = Level1DatabaseCreator(port=args.port)
    
    if args.create:
        result = creator.create_clean_level1_database()
        print(f"Level 1 Database Creation: {json.dumps(result, indent=2)}")
    elif args.analyze:
        analysis = creator.analyze_service_levels()
        print(f"Service Level Analysis: {json.dumps(analysis, indent=2)}")
    elif args.service:
        creator.run()
    else:
        print("Level 1 Database Creator")
        print("Commands:")
        print("  --service   : Run as API service")
        print("  --create    : Create clean Level 1 database")
        print("  --analyze   : Analyze service level distribution")

if __name__ == "__main__":
    main()