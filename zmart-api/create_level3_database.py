#!/usr/bin/env python3
"""
Level 3 Database Creator - Certified Services Registry with CERT Credentials
Created: 2025-08-31
Purpose: Create clean Level3.db for certified services with CERT credentials
Level: 3 (Authority System)
Port: 8905
Passport: LEVEL3-DB-CREATOR-8905-L3
Owner: zmartbot-system
Status: AUTHORITY
"""

import os
import sys
import sqlite3
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from flask import Flask, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Level3DatabaseCreator:
    """Create clean Level 3 database for certified services"""
    
    def __init__(self, port=8905):
        self.port = port
        self.app = Flask(__name__)
        self.root_dir = Path(".")
        self.level3_db = self.root_dir / "Level3.db"
        
        self.setup_level3_database()
        self.setup_routes()
    
    def setup_level3_database(self):
        """Setup clean Level 3 certified services database"""
        conn = sqlite3.connect(self.level3_db)
        cursor = conn.cursor()
        
        # Level 3 Certified Services with CERT Credentials
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level3_certified_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE NOT NULL,
                passport_id TEXT UNIQUE NOT NULL,
                cert_id TEXT UNIQUE NOT NULL,
                port INTEGER NOT NULL,
                service_type TEXT NOT NULL,
                certification_level INTEGER DEFAULT 3,
                cert_status TEXT DEFAULT 'CERTIFIED',
                cert_issued_date TIMESTAMP NOT NULL,
                cert_expiry_date TIMESTAMP NOT NULL,
                cert_issuer TEXT DEFAULT 'SERVICE-CERT-AUTHORITY-8901-L3',
                
                -- Service Details
                file_path TEXT,
                mdc_file_path TEXT NOT NULL,
                health_endpoint TEXT NOT NULL,
                metrics_endpoint TEXT,
                start_command TEXT,
                stop_command TEXT,
                description TEXT,
                owner TEXT DEFAULT 'zmartbot-system',
                
                -- Performance Metrics
                uptime_percentage REAL DEFAULT 99.9,
                avg_response_time INTEGER DEFAULT 0,
                throughput_capacity INTEGER DEFAULT 0,
                resource_efficiency_score INTEGER DEFAULT 0,
                
                -- Audit Scores (0-100 each)
                security_score INTEGER DEFAULT 0,
                reliability_score INTEGER DEFAULT 0,
                performance_score INTEGER DEFAULT 0,
                compliance_score INTEGER DEFAULT 0,
                documentation_score INTEGER DEFAULT 0,
                monitoring_score INTEGER DEFAULT 0,
                overall_score INTEGER DEFAULT 0,
                
                -- Operational Status
                operational_status TEXT DEFAULT 'PRODUCTION',
                last_health_check TIMESTAMP,
                last_audit TIMESTAMP,
                next_audit_due TIMESTAMP,
                
                -- Certification Management
                renewal_required BOOLEAN DEFAULT FALSE,
                compliance_issues TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Level 3 Certification History
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level3_cert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                cert_id TEXT,
                action TEXT,
                old_status TEXT,
                new_status TEXT,
                performed_by TEXT,
                reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Level 3 Audit Trail
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level3_audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                audit_type TEXT,
                category TEXT,
                requirement TEXT,
                result TEXT,
                score INTEGER,
                evidence TEXT,
                auditor TEXT,
                audit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Level 3 Compliance Monitoring
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS level3_compliance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                compliance_check TEXT,
                status TEXT,
                last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                next_check TIMESTAMP,
                violation_count INTEGER DEFAULT 0,
                compliance_percentage REAL DEFAULT 100.0
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
                "service": "level3-database-creator",
                "port": self.port,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/create-level3')
        def create_level3():
            """Create clean Level 3 database"""
            try:
                result = self.create_clean_level3_database()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/level3-services')
        def get_level3_services():
            """Get all Level 3 certified services"""
            try:
                services = self.get_level3_services()
                return jsonify({
                    "total_certified": len(services),
                    "services": services
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/promote-to-level3')
        def promote_to_level3():
            """Promote qualified services to Level 3"""
            try:
                result = self.promote_qualified_services()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def create_clean_level3_database(self) -> Dict:
        """Create clean Level 3 database for certified services"""
        logger.info("Creating clean Level 3 database...")
        
        # Get Level 3 candidates from certification authority
        level3_candidates = self.get_level3_candidates()
        
        # Get any existing certified services
        existing_certified = self.get_existing_certified_services()
        
        # Combine and populate
        all_level3 = level3_candidates + existing_certified
        
        # Remove duplicates
        seen_names = set()
        unique_level3 = []
        for service in all_level3:
            if service['service_name'] not in seen_names:
                seen_names.add(service['service_name'])
                unique_level3.append(service)
        
        # Populate Level 3 database
        self.populate_level3_database(unique_level3)
        
        return {
            "status": "completed",
            "total_level3_services": len(unique_level3),
            "candidates_found": len(level3_candidates),
            "existing_certified": len(existing_certified),
            "level3_database_path": str(self.level3_db),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_level3_candidates(self) -> List[Dict]:
        """Get Level 3 candidates from certification authority"""
        try:
            response = requests.get("http://127.0.0.1:8902/api/level3-candidates", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('candidates', [])
        except Exception as e:
            logger.error(f"Error getting Level 3 candidates: {e}")
        
        return []
    
    def get_existing_certified_services(self) -> List[Dict]:
        """Get existing certified services"""
        # For now, return empty - this will be populated as services get certified
        return []
    
    def populate_level3_database(self, level3_services: List[Dict]):
        """Populate Level 3 database"""
        conn = sqlite3.connect(self.level3_db)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM level3_certified_services")
        
        for service in level3_services:
            try:
                # Generate cert_id if not exists
                cert_id = f"L3-CERT-{service['service_name'].upper()}-{int(datetime.now().timestamp())}"
                
                cursor.execute("""
                    INSERT INTO level3_certified_services
                    (service_name, passport_id, cert_id, port, service_type, 
                     cert_issued_date, cert_expiry_date, file_path, 
                     mdc_file_path, health_endpoint, description, cert_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    service['service_name'],
                    service.get('passport_id', f"L3-{service['service_name'].upper()}"),
                    cert_id,
                    service.get('port'),
                    service.get('service_type', 'unknown'),
                    datetime.now(),
                    datetime.now() + timedelta(days=365),
                    service.get('file_path'),
                    service.get('mdc_file_path'),
                    f"http://127.0.0.1:{service['port']}/health" if service.get('port') else None,
                    service.get('description', 'Level 3 candidate service'),
                    'CANDIDATE' if not service.get('ready_for_certification') else 'READY_FOR_CERT'
                ))
                
            except Exception as e:
                logger.error(f"Error adding Level 3 service {service['service_name']}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Populated Level 3 database with {len(level3_services)} services")
    
    def get_level3_services(self) -> List[Dict]:
        """Get all Level 3 services"""
        conn = sqlite3.connect(self.level3_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT service_name, passport_id, cert_id, port, service_type,
                   cert_status, cert_issued_date, cert_expiry_date, overall_score
            FROM level3_certified_services
            ORDER BY overall_score DESC, cert_issued_date DESC
        """)
        
        services = []
        for row in cursor.fetchall():
            services.append({
                'service_name': row[0],
                'passport_id': row[1],
                'cert_id': row[2],
                'port': row[3],
                'service_type': row[4],
                'cert_status': row[5],
                'cert_issued_date': row[6],
                'cert_expiry_date': row[7],
                'overall_score': row[8]
            })
        
        conn.close()
        return services
    
    def promote_qualified_services(self) -> Dict:
        """Promote qualified services to Level 3"""
        # This would integrate with the certification authority
        # to automatically promote services that pass Level 3 audits
        return {
            "status": "not_implemented",
            "message": "Integration with certification authority pending"
        }
    
    def run(self):
        """Run the Level 3 database creator service"""
        logger.info(f"Starting Level 3 Database Creator on port {self.port}")
        logger.info("Level 3 Certified Services Database System Ready")
        
        try:
            self.app.run(host='127.0.0.1', port=self.port, debug=False)
        except KeyboardInterrupt:
            logger.info("Level 3 Database Creator stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Level 3 Database Creator")
    parser.add_argument('--port', type=int, default=8905, help='Service port')
    parser.add_argument('--service', action='store_true', help='Run as service')
    parser.add_argument('--create', action='store_true', help='Create Level 3 database')
    parser.add_argument('--analyze', action='store_true', help='Analyze certification status')
    
    args = parser.parse_args()
    
    creator = Level3DatabaseCreator(port=args.port)
    
    if args.create:
        result = creator.create_clean_level3_database()
        print(f"Level 3 Database Creation: {json.dumps(result, indent=2)}")
    elif args.analyze:
        analysis = creator.analyze_service_levels()
        print(f"Certification Analysis: {json.dumps(analysis, indent=2)}")
    elif args.service:
        creator.run()
    else:
        print("Level 3 Database Creator")
        print("Commands:")
        print("  --service   : Run as API service")
        print("  --create    : Create clean Level 3 database")
        print("  --analyze   : Analyze certification status")

if __name__ == "__main__":
    main()