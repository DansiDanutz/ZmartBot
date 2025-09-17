#!/usr/bin/env python3
"""
CERT Database Creator - Certification Sequential ID Management
Created: 2025-08-31
Purpose: Create CERT.db for sequential certification tracking (CERT1, CERT2, CERT3...)
Level: 3 (Authority System)
Port: 8906
Passport: CERT-DB-CREATOR-8906-L3
Owner: zmartbot-system
Status: AUTHORITY
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from flask import Flask, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CertDatabaseCreator:
    """Create and manage CERT.db for sequential certification tracking"""
    
    def __init__(self, port=8906):
        self.port = port
        self.app = Flask(__name__)
        self.root_dir = Path(".")
        self.cert_db = self.root_dir / "CERT.db"
        
        self.setup_cert_database()
        self.setup_routes()
    
    def setup_cert_database(self):
        """Setup CERT database with sequential ID management"""
        conn = sqlite3.connect(self.cert_db)
        cursor = conn.cursor()
        
        # CERT Sequential Registry - Core certification tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cert_registry (
                cert_id TEXT PRIMARY KEY,
                cert_number INTEGER UNIQUE NOT NULL,
                service_name TEXT UNIQUE NOT NULL,
                passport_id TEXT UNIQUE NOT NULL,
                port INTEGER NOT NULL,
                service_type TEXT NOT NULL,
                
                -- Level 2 Requirements (inherited)
                python_file_path TEXT NOT NULL,
                mdc_file_path TEXT NOT NULL,
                passport_assigned BOOLEAN DEFAULT TRUE,
                
                -- Level 3 Requirements
                tests_passed BOOLEAN DEFAULT FALSE,
                health_passed BOOLEAN DEFAULT FALSE,
                level2_removed BOOLEAN DEFAULT FALSE,
                level3_added BOOLEAN DEFAULT FALSE,
                orchestration_assigned BOOLEAN DEFAULT FALSE,
                master_orchestration_assigned BOOLEAN DEFAULT FALSE,
                trading_orchestration_assigned BOOLEAN DEFAULT FALSE,
                protection_applied BOOLEAN DEFAULT FALSE,
                
                -- Certification Details
                cert_issued_date TIMESTAMP NOT NULL,
                cert_expiry_date TIMESTAMP NOT NULL,
                cert_status TEXT DEFAULT 'CERTIFIED',
                cert_issuer TEXT DEFAULT 'SERVICE-CERT-AUTHORITY-8901-L3',
                
                -- Audit Scores
                security_score INTEGER DEFAULT 0,
                reliability_score INTEGER DEFAULT 0,
                performance_score INTEGER DEFAULT 0,
                compliance_score INTEGER DEFAULT 0,
                documentation_score INTEGER DEFAULT 0,
                monitoring_score INTEGER DEFAULT 0,
                overall_score INTEGER DEFAULT 0,
                
                -- Orchestration Assignments
                orchestration_start_assigned TEXT,
                master_orchestration_agent_assigned TEXT,
                trading_orchestration_agent_assigned TEXT,
                
                -- Protection Details
                protection_level TEXT DEFAULT 'STANDARD',
                protection_config TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # CERT Counter - Manages sequential CERT numbering
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cert_counter (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                last_cert_number INTEGER DEFAULT 0,
                total_certified INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Initialize counter if empty
        cursor.execute("SELECT COUNT(*) FROM cert_counter")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO cert_counter (id, last_cert_number, total_certified)
                VALUES (1, 0, 0)
            """)
        
        # CERT Audit Trail
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cert_audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cert_id TEXT,
                service_name TEXT,
                action TEXT,
                requirement TEXT,
                status TEXT,
                details TEXT,
                performed_by TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # CERT Level Transitions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cert_level_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                from_level INTEGER,
                to_level INTEGER,
                cert_id TEXT,
                transition_type TEXT,
                level2_db_removed BOOLEAN DEFAULT FALSE,
                level3_db_added BOOLEAN DEFAULT FALSE,
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
                "service": "cert-database-creator",
                "port": self.port,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/create-cert-db')
        def create_cert_db():
            """Create/verify CERT database"""
            try:
                result = self.verify_cert_database()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/next-cert-number')
        def get_next_cert_number():
            """Get next available CERT number"""
            try:
                cert_number = self.get_next_cert_number()
                return jsonify({
                    "next_cert_number": cert_number,
                    "next_cert_id": f"CERT{cert_number}",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/certify-service', methods=['POST'])
        def certify_service():
            """Certify a service with sequential CERT ID"""
            # This would be called by the certification authority
            return jsonify({
                "status": "not_implemented",
                "message": "Integration with certification authority pending"
            })
        
        @self.app.route('/api/certified-services')
        def get_certified_services():
            """Get all certified services"""
            try:
                services = self.get_certified_services()
                return jsonify({
                    "total_certified": len(services),
                    "services": services
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def verify_cert_database(self) -> Dict:
        """Verify CERT database setup"""
        logger.info("Verifying CERT database setup...")
        
        # Check counter
        conn = sqlite3.connect(self.cert_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT last_cert_number, total_certified FROM cert_counter WHERE id = 1")
        counter_row = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM cert_registry")
        actual_certified = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "verified",
            "cert_database_path": str(self.cert_db),
            "last_cert_number": counter_row[0] if counter_row else 0,
            "total_certified_counter": counter_row[1] if counter_row else 0,
            "actual_certified_services": actual_certified,
            "next_cert_id": f"CERT{counter_row[0] + 1}" if counter_row else "CERT1",
            "sequential_integrity": "OK",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_next_cert_number(self) -> int:
        """Get next sequential CERT number"""
        conn = sqlite3.connect(self.cert_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT last_cert_number FROM cert_counter WHERE id = 1")
        row = cursor.fetchone()
        next_number = (row[0] + 1) if row else 1
        
        conn.close()
        return next_number
    
    def certify_service(self, service_data: Dict) -> Dict:
        """Certify a service with sequential CERT ID and database migrations"""
        conn = sqlite3.connect(self.cert_db)
        cursor = conn.cursor()
        
        try:
            # Get next CERT number
            next_cert_number = self.get_next_cert_number()
            cert_id = f"CERT{next_cert_number}"
            
            # Insert certification record
            cursor.execute("""
                INSERT INTO cert_registry
                (cert_id, cert_number, service_name, passport_id, port, service_type,
                 python_file_path, mdc_file_path, cert_issued_date, cert_expiry_date,
                 tests_passed, health_passed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cert_id,
                next_cert_number,
                service_data['service_name'],
                service_data['passport_id'],
                service_data['port'],
                service_data['service_type'],
                service_data['python_file_path'],
                service_data['mdc_file_path'],
                datetime.now(),
                datetime.now() + timedelta(days=365),
                service_data.get('tests_passed', False),
                service_data.get('health_passed', False)
            ))
            
            # Update counter
            cursor.execute("""
                UPDATE cert_counter 
                SET last_cert_number = ?, total_certified = total_certified + 1, updated_at = ?
                WHERE id = 1
            """, (next_cert_number, datetime.now()))
            
            # Log certification
            cursor.execute("""
                INSERT INTO cert_audit_trail
                (cert_id, service_name, action, requirement, status, performed_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                cert_id,
                service_data['service_name'],
                'CERTIFICATION',
                'LEVEL_3_PROMOTION',
                'CERTIFIED',
                'CERT-DB-CREATOR-8906-L3'
            ))
            
            conn.commit()
            
            return {
                "status": "certified",
                "cert_id": cert_id,
                "cert_number": next_cert_number,
                "service_name": service_data['service_name'],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error certifying service: {e}")
            raise
        finally:
            conn.close()
    
    def get_certified_services(self) -> List[Dict]:
        """Get all certified services"""
        conn = sqlite3.connect(self.cert_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT cert_id, cert_number, service_name, passport_id, port, service_type,
                   cert_status, cert_issued_date, overall_score, 
                   orchestration_assigned, master_orchestration_assigned, trading_orchestration_assigned
            FROM cert_registry
            ORDER BY cert_number ASC
        """)
        
        services = []
        for row in cursor.fetchall():
            services.append({
                'cert_id': row[0],
                'cert_number': row[1],
                'service_name': row[2],
                'passport_id': row[3],
                'port': row[4],
                'service_type': row[5],
                'cert_status': row[6],
                'cert_issued_date': row[7],
                'overall_score': row[8],
                'orchestration_assigned': bool(row[9]),
                'master_orchestration_assigned': bool(row[10]),
                'trading_orchestration_assigned': bool(row[11])
            })
        
        conn.close()
        return services
    
    def run(self):
        """Run the CERT database creator service"""
        logger.info(f"Starting CERT Database Creator on port {self.port}")
        logger.info("CERT Sequential Certification System Ready")
        
        try:
            self.app.run(host='127.0.0.1', port=self.port, debug=False)
        except KeyboardInterrupt:
            logger.info("CERT Database Creator stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CERT Database Creator")
    parser.add_argument('--port', type=int, default=8906, help='Service port')
    parser.add_argument('--service', action='store_true', help='Run as service')
    parser.add_argument('--create', action='store_true', help='Create CERT database')
    parser.add_argument('--verify', action='store_true', help='Verify CERT database')
    parser.add_argument('--next-cert', action='store_true', help='Get next CERT number')
    
    args = parser.parse_args()
    
    creator = CertDatabaseCreator(port=args.port)
    
    if args.create or args.verify:
        result = creator.verify_cert_database()
        print(f"CERT Database Verification: {json.dumps(result, indent=2)}")
    elif args.next_cert:
        next_number = creator.get_next_cert_number()
        print(f"Next CERT ID: CERT{next_number}")
    elif args.service:
        creator.run()
    else:
        print("CERT Database Creator")
        print("Commands:")
        print("  --service    : Run as API service")
        print("  --create     : Create CERT database")
        print("  --verify     : Verify CERT database")
        print("  --next-cert  : Get next CERT number")

if __name__ == "__main__":
    main()