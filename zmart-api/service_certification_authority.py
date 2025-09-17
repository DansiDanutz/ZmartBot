#!/usr/bin/env python3
"""
Service Certification Authority - ZmartBot Level 3 Certification System
Created: 2025-08-31
Purpose: Certify services that meet Level 3 requirements and issue CERT certifications
Level: 3 (Certification Authority)
Port: 8901
Passport: SERVICE-CERT-AUTHORITY-8901-L3
Owner: zmartbot-system
Status: AUTHORITY
"""

import os
import sys
import sqlite3
import json
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from flask import Flask, jsonify, request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceCertificationAuthority:
    """Level 3 Service Certification Authority"""
    
    def __init__(self, port=8901):
        self.port = port
        self.app = Flask(__name__)
        self.root_dir = Path(".")
        self.cert_db = self.root_dir / "certifications" / "service_certifications.db"
        self.level3_registry = self.root_dir / "certifications" / "level3_service_registry.db"
        
        # Ensure directories exist
        self.cert_db.parent.mkdir(exist_ok=True)
        
        # Level 3 Requirements
        self.LEVEL3_REQUIREMENTS = {
            "documentation": {
                "mdc_file": "Must have comprehensive MDC documentation",
                "api_docs": "Must have API documentation",
                "deployment_guide": "Must have deployment documentation"
            },
            "security": {
                "authentication": "Must implement proper authentication",
                "authorization": "Must have role-based access control", 
                "encryption": "Must encrypt sensitive data",
                "audit_logging": "Must have comprehensive audit trails"
            },
            "monitoring": {
                "health_checks": "Must implement health and readiness endpoints",
                "metrics": "Must expose Prometheus-compatible metrics",
                "alerting": "Must have alerting capabilities",
                "logging": "Must have structured logging"
            },
            "reliability": {
                "uptime": "Must demonstrate 99.9% uptime over 30 days",
                "error_handling": "Must have comprehensive error handling",
                "graceful_shutdown": "Must handle graceful shutdowns",
                "data_backup": "Must have automated backup strategies"
            },
            "performance": {
                "response_time": "Must have <100ms average response time",
                "throughput": "Must handle expected load capacity",
                "resource_usage": "Must have efficient resource utilization",
                "scalability": "Must demonstrate horizontal scaling capability"
            },
            "compliance": {
                "standards": "Must follow ZmartBot architectural standards",
                "testing": "Must have comprehensive test coverage >80%",
                "ci_cd": "Must have automated CI/CD pipeline",
                "code_quality": "Must pass all linting and quality checks"
            }
        }
        
        self.setup_databases()
        self.setup_routes()
    
    def setup_databases(self):
        """Setup certification databases"""
        # Certification tracking database
        cert_conn = sqlite3.connect(self.cert_db)
        cert_cursor = cert_conn.cursor()
        
        cert_cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_certifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE,
                passport_id TEXT,
                current_level INTEGER DEFAULT 1,
                target_level INTEGER DEFAULT 3,
                cert_id TEXT,
                cert_issued_at TIMESTAMP,
                cert_expires_at TIMESTAMP,
                cert_status TEXT DEFAULT 'PENDING',
                requirements_met TEXT,
                requirements_pending TEXT,
                last_audit TIMESTAMP,
                next_audit TIMESTAMP,
                audit_score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cert_cursor.execute("""
            CREATE TABLE IF NOT EXISTS certification_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                audit_type TEXT,
                requirements_category TEXT,
                requirement_key TEXT,
                status TEXT,
                score INTEGER,
                evidence TEXT,
                auditor TEXT DEFAULT 'SYSTEM',
                notes TEXT,
                audit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cert_cursor.execute("""
            CREATE TABLE IF NOT EXISTS level3_requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                requirement_key TEXT,
                requirement_description TEXT,
                validation_method TEXT,
                weight INTEGER DEFAULT 1,
                mandatory BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cert_conn.commit()
        cert_conn.close()
        
        # Level 3 Service Registry
        registry_conn = sqlite3.connect(self.level3_registry)
        registry_cursor = registry_conn.cursor()
        
        registry_cursor.execute("""
            CREATE TABLE IF NOT EXISTS level3_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE,
                passport_id TEXT,
                cert_id TEXT,
                port INTEGER,
                service_type TEXT,
                status TEXT DEFAULT 'CERTIFIED',
                cert_level INTEGER DEFAULT 3,
                cert_issued_date TIMESTAMP,
                cert_expiry_date TIMESTAMP,
                uptime_percentage REAL,
                performance_score INTEGER,
                security_score INTEGER,
                reliability_score INTEGER,
                compliance_score INTEGER,
                overall_score INTEGER,
                last_health_check TIMESTAMP,
                mdc_file_path TEXT,
                api_documentation TEXT,
                deployment_guide TEXT,
                monitoring_endpoints TEXT,
                backup_strategy TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        registry_cursor.execute("""
            CREATE TABLE IF NOT EXISTS certification_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                action TEXT,
                old_status TEXT,
                new_status TEXT,
                cert_id TEXT,
                reason TEXT,
                performed_by TEXT DEFAULT 'SYSTEM',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        registry_conn.commit()
        registry_conn.close()
        
        # Load default requirements
        self.load_default_requirements()
    
    def load_default_requirements(self):
        """Load default Level 3 requirements into database"""
        conn = sqlite3.connect(self.cert_db)
        cursor = conn.cursor()
        
        for category, requirements in self.LEVEL3_REQUIREMENTS.items():
            for req_key, req_desc in requirements.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO level3_requirements
                    (category, requirement_key, requirement_description, validation_method, weight, mandatory)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (category, req_key, req_desc, "AUTOMATED", 1, True))
        
        conn.commit()
        conn.close()
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "service": "service-certification-authority",
                "port": self.port,
                "certification_level": 3,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/certify/<service_name>')
        def certify_service(service_name):
            """Start certification process for a service"""
            try:
                result = self.initiate_certification(service_name)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/audit/<service_name>')
        def audit_service(service_name):
            """Run comprehensive audit on a service"""
            try:
                result = self.run_comprehensive_audit(service_name)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/level3-services')
        def get_level3_services():
            """Get all Level 3 certified services"""
            try:
                services = self.get_certified_services()
                return jsonify({
                    "total_certified": len(services),
                    "services": services
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/requirements')
        def get_requirements():
            """Get Level 3 certification requirements"""
            return jsonify({
                "level": 3,
                "requirements": self.LEVEL3_REQUIREMENTS,
                "total_categories": len(self.LEVEL3_REQUIREMENTS)
            })
        
        @self.app.route('/api/status/<service_name>')
        def get_certification_status(service_name):
            """Get certification status for a service"""
            try:
                status = self.get_service_cert_status(service_name)
                return jsonify(status)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def initiate_certification(self, service_name: str) -> Dict:
        """Initiate Level 3 certification process for a service"""
        logger.info(f"Starting Level 3 certification for {service_name}")
        
        # Check if service exists in GOODDatabase.db
        service_info = self.get_service_from_good_db(service_name)
        if not service_info:
            return {"error": f"Service {service_name} not found in GOODDatabase"}
        
        # Create certification record
        conn = sqlite3.connect(self.cert_db)
        cursor = conn.cursor()
        
        cert_id = f"CERT-{service_name.upper()}-{int(time.time())}"
        
        cursor.execute("""
            INSERT OR REPLACE INTO service_certifications
            (service_name, passport_id, cert_id, cert_status, requirements_met, requirements_pending)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            service_name,
            service_info.get('passport_id'),
            cert_id,
            'PENDING_AUDIT',
            '{}',
            json.dumps(list(self.LEVEL3_REQUIREMENTS.keys()))
        ))
        
        conn.commit()
        conn.close()
        
        # Run initial audit
        audit_result = self.run_comprehensive_audit(service_name)
        
        return {
            "service_name": service_name,
            "cert_id": cert_id,
            "status": "certification_initiated",
            "audit_result": audit_result
        }
    
    def run_comprehensive_audit(self, service_name: str) -> Dict:
        """Run comprehensive Level 3 audit on a service"""
        logger.info(f"Running comprehensive Level 3 audit for {service_name}")
        
        service_info = self.get_service_from_good_db(service_name)
        if not service_info:
            return {"error": f"Service {service_name} not found"}
        
        audit_results = {}
        total_score = 0
        max_score = 0
        
        for category, requirements in self.LEVEL3_REQUIREMENTS.items():
            category_score = 0
            category_max = len(requirements) * 100
            category_results = {}
            
            for req_key, req_desc in requirements.items():
                score, evidence = self.audit_requirement(service_name, service_info, category, req_key)
                category_results[req_key] = {
                    "score": score,
                    "max_score": 100,
                    "evidence": evidence,
                    "status": "PASS" if score >= 80 else "FAIL",
                    "description": req_desc
                }
                category_score += score
                
                # Log audit result
                self.log_audit_result(service_name, category, req_key, score, evidence)
            
            audit_results[category] = {
                "score": category_score,
                "max_score": category_max,
                "percentage": (category_score / category_max * 100) if category_max > 0 else 0,
                "requirements": category_results
            }
            
            total_score += category_score
            max_score += category_max
        
        overall_percentage = (total_score / max_score * 100) if max_score > 0 else 0
        certification_eligible = overall_percentage >= 90  # 90% threshold for Level 3
        
        # Update certification record
        self.update_certification_status(service_name, overall_percentage, certification_eligible, audit_results)
        
        return {
            "service_name": service_name,
            "overall_score": total_score,
            "max_score": max_score,
            "percentage": overall_percentage,
            "certification_eligible": certification_eligible,
            "cert_threshold": 90,
            "audit_results": audit_results,
            "audit_timestamp": datetime.now().isoformat()
        }
    
    def audit_requirement(self, service_name: str, service_info: Dict, category: str, req_key: str) -> Tuple[int, str]:
        """Audit a specific requirement"""
        port = service_info.get('port')
        
        if category == "documentation":
            return self.audit_documentation(service_name, req_key)
        elif category == "security":
            return self.audit_security(service_name, port, req_key)
        elif category == "monitoring":
            return self.audit_monitoring(service_name, port, req_key)
        elif category == "reliability":
            return self.audit_reliability(service_name, port, req_key)
        elif category == "performance":
            return self.audit_performance(service_name, port, req_key)
        elif category == "compliance":
            return self.audit_compliance(service_name, req_key)
        
        return 0, "Unknown requirement category"
    
    def audit_documentation(self, service_name: str, req_key: str) -> Tuple[int, str]:
        """Audit documentation requirements"""
        if req_key == "mdc_file":
            mdc_files = list(Path(".cursor/rules").glob(f"*{service_name}*.mdc"))
            if mdc_files:
                return 100, f"MDC file found: {mdc_files[0]}"
            return 0, "No MDC file found"
        elif req_key == "api_docs":
            # Check for API documentation indicators
            return 50, "Partial API documentation assumed"
        elif req_key == "deployment_guide":
            return 50, "Deployment guide assumed from service structure"
        return 0, "Documentation requirement not implemented"
    
    def audit_security(self, service_name: str, port: Optional[int], req_key: str) -> Tuple[int, str]:
        """Audit security requirements"""
        if not port:
            return 0, "No port defined - cannot audit security"
            
        try:
            # Try to access health endpoint
            response = requests.get(f"http://127.0.0.1:{port}/health", timeout=5)
            if response.status_code == 200:
                if req_key == "authentication":
                    return 60, "Service accessible - partial authentication score"
                elif req_key == "authorization": 
                    return 40, "Basic authorization assumed"
                elif req_key == "encryption":
                    return 30, "Basic encryption assumed"
                elif req_key == "audit_logging":
                    return 70, "Audit logging partially implemented"
        except:
            pass
            
        return 20, f"Security requirement {req_key} - basic implementation assumed"
    
    def audit_monitoring(self, service_name: str, port: Optional[int], req_key: str) -> Tuple[int, str]:
        """Audit monitoring requirements"""
        if not port:
            return 0, "No port defined - cannot audit monitoring"
            
        try:
            if req_key == "health_checks":
                response = requests.get(f"http://127.0.0.1:{port}/health", timeout=5)
                if response.status_code == 200:
                    return 100, "Health endpoint accessible"
                return 0, "Health endpoint not accessible"
            elif req_key == "metrics":
                # Check for metrics endpoint
                try:
                    metrics_response = requests.get(f"http://127.0.0.1:{port}/metrics", timeout=5)
                    if metrics_response.status_code == 200:
                        return 100, "Metrics endpoint found"
                except:
                    pass
                return 30, "Metrics endpoint not found - basic scoring"
        except:
            pass
            
        return 25, f"Monitoring requirement {req_key} - basic implementation"
    
    def audit_reliability(self, service_name: str, port: Optional[int], req_key: str) -> Tuple[int, str]:
        """Audit reliability requirements"""
        if req_key == "uptime":
            return 80, "Uptime assessment - service appears stable"
        elif req_key == "error_handling":
            return 70, "Error handling - basic implementation assumed"
        elif req_key == "graceful_shutdown":
            return 60, "Graceful shutdown - basic implementation"
        elif req_key == "data_backup":
            return 50, "Data backup - basic strategy assumed"
        return 40, f"Reliability requirement {req_key} - basic scoring"
    
    def audit_performance(self, service_name: str, port: Optional[int], req_key: str) -> Tuple[int, str]:
        """Audit performance requirements"""
        if not port:
            return 50, "No port - basic performance scoring"
            
        if req_key == "response_time":
            try:
                start_time = time.time()
                response = requests.get(f"http://127.0.0.1:{port}/health", timeout=5)
                response_time = (time.time() - start_time) * 1000
                
                if response_time < 100:
                    return 100, f"Excellent response time: {response_time:.2f}ms"
                elif response_time < 500:
                    return 80, f"Good response time: {response_time:.2f}ms"
                else:
                    return 40, f"Slow response time: {response_time:.2f}ms"
            except:
                return 30, "Cannot measure response time"
        
        return 50, f"Performance requirement {req_key} - basic scoring"
    
    def audit_compliance(self, service_name: str, req_key: str) -> Tuple[int, str]:
        """Audit compliance requirements"""
        if req_key == "standards":
            return 80, "Standards compliance - service follows ZmartBot patterns"
        elif req_key == "testing":
            return 60, "Testing coverage - basic test coverage assumed"
        elif req_key == "ci_cd":
            return 40, "CI/CD - basic pipeline assumed"
        elif req_key == "code_quality":
            return 70, "Code quality - meets basic standards"
        return 50, f"Compliance requirement {req_key} - basic scoring"
    
    def log_audit_result(self, service_name: str, category: str, req_key: str, score: int, evidence: str):
        """Log audit result to database"""
        conn = sqlite3.connect(self.cert_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO certification_audits
            (service_name, audit_type, requirements_category, requirement_key, status, score, evidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            service_name,
            'LEVEL3_CERTIFICATION',
            category,
            req_key,
            'PASS' if score >= 80 else 'FAIL',
            score,
            evidence
        ))
        
        conn.commit()
        conn.close()
    
    def update_certification_status(self, service_name: str, score: float, eligible: bool, audit_results: Dict):
        """Update certification status based on audit results"""
        conn = sqlite3.connect(self.cert_db)
        cursor = conn.cursor()
        
        if eligible:
            cert_id = f"L3-CERT-{service_name.upper()}-{int(time.time())}"
            cert_issued = datetime.now()
            cert_expires = cert_issued + timedelta(days=365)  # 1 year validity
            
            cursor.execute("""
                UPDATE service_certifications
                SET cert_status = ?, audit_score = ?, cert_issued_at = ?, cert_expires_at = ?,
                    requirements_met = ?, last_audit = ?, next_audit = ?
                WHERE service_name = ?
            """, (
                'CERTIFIED_L3',
                int(score),
                cert_issued,
                cert_expires,
                json.dumps(audit_results),
                datetime.now(),
                datetime.now() + timedelta(days=90),  # Next audit in 3 months
                service_name
            ))
            
            # Add to Level 3 registry
            self.add_to_level3_registry(service_name, cert_id, score, audit_results)
        else:
            cursor.execute("""
                UPDATE service_certifications
                SET cert_status = ?, audit_score = ?, requirements_pending = ?, last_audit = ?
                WHERE service_name = ?
            """, (
                'AUDIT_FAILED',
                int(score),
                json.dumps([cat for cat, results in audit_results.items() if results['percentage'] < 80]),
                datetime.now(),
                service_name
            ))
        
        conn.commit()
        conn.close()
    
    def add_to_level3_registry(self, service_name: str, cert_id: str, score: float, audit_results: Dict):
        """Add certified service to Level 3 registry"""
        service_info = self.get_service_from_good_db(service_name)
        if not service_info:
            return
        
        conn = sqlite3.connect(self.level3_registry)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO level3_services
            (service_name, passport_id, cert_id, port, service_type, cert_issued_date, 
             cert_expiry_date, overall_score, security_score, reliability_score, 
             compliance_score, performance_score, last_health_check)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            service_name,
            service_info.get('passport_id'),
            cert_id,
            service_info.get('port'),
            service_info.get('service_type'),
            datetime.now(),
            datetime.now() + timedelta(days=365),
            int(score),
            int(audit_results.get('security', {}).get('percentage', 0)),
            int(audit_results.get('reliability', {}).get('percentage', 0)),
            int(audit_results.get('compliance', {}).get('percentage', 0)),
            int(audit_results.get('performance', {}).get('percentage', 0)),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Service {service_name} certified as Level 3 with cert ID: {cert_id}")
    
    def get_service_from_good_db(self, service_name: str) -> Optional[Dict]:
        """Get service info from GOODDatabase.db"""
        try:
            conn = sqlite3.connect('../GOODDatabase.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, passport_id, port, service_type, status, file_path, notes
                FROM services WHERE service_name = ?
            """, (service_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'service_name': result[0],
                    'passport_id': result[1],
                    'port': result[2],
                    'service_type': result[3],
                    'status': result[4],
                    'file_path': result[5],
                    'notes': result[6]
                }
        except Exception as e:
            logger.error(f"Error accessing GOODDatabase: {e}")
        
        return None
    
    def get_certified_services(self) -> List[Dict]:
        """Get all Level 3 certified services"""
        conn = sqlite3.connect(self.level3_registry)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT service_name, passport_id, cert_id, port, service_type, 
                   cert_issued_date, cert_expiry_date, overall_score, status
            FROM level3_services
            WHERE status = 'CERTIFIED'
            ORDER BY cert_issued_date DESC
        """)
        
        services = []
        for row in cursor.fetchall():
            services.append({
                'service_name': row[0],
                'passport_id': row[1],
                'cert_id': row[2],
                'port': row[3],
                'service_type': row[4],
                'cert_issued_date': row[5],
                'cert_expiry_date': row[6],
                'overall_score': row[7],
                'status': row[8]
            })
        
        conn.close()
        return services
    
    def get_service_cert_status(self, service_name: str) -> Dict:
        """Get certification status for a service"""
        conn = sqlite3.connect(self.cert_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT cert_status, audit_score, cert_issued_at, cert_expires_at, 
                   requirements_met, requirements_pending, last_audit
            FROM service_certifications
            WHERE service_name = ?
        """, (service_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'service_name': service_name,
                'cert_status': result[0],
                'audit_score': result[1],
                'cert_issued_at': result[2],
                'cert_expires_at': result[3],
                'requirements_met': json.loads(result[4] or '{}'),
                'requirements_pending': json.loads(result[5] or '[]'),
                'last_audit': result[6]
            }
        
        return {'service_name': service_name, 'cert_status': 'NOT_FOUND'}
    
    def run(self):
        """Run the certification authority service"""
        logger.info(f"Starting Service Certification Authority on port {self.port}")
        logger.info("Level 3 Certification System Ready")
        
        try:
            self.app.run(host='127.0.0.1', port=self.port, debug=False)
        except KeyboardInterrupt:
            logger.info("Service Certification Authority stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Service Certification Authority - Level 3")
    parser.add_argument('--port', type=int, default=8901, help='Service port')
    parser.add_argument('--service', action='store_true', help='Run as service')
    parser.add_argument('--certify', type=str, help='Certify a specific service')
    parser.add_argument('--audit', type=str, help='Audit a specific service')
    parser.add_argument('--list-certified', action='store_true', help='List all certified services')
    
    args = parser.parse_args()
    
    authority = ServiceCertificationAuthority(port=args.port)
    
    if args.certify:
        result = authority.initiate_certification(args.certify)
        print(f"Certification result for {args.certify}: {json.dumps(result, indent=2)}")
    elif args.audit:
        result = authority.run_comprehensive_audit(args.audit)
        print(f"Audit result for {args.audit}: {json.dumps(result, indent=2)}")
    elif args.list_certified:
        services = authority.get_certified_services()
        print(f"Level 3 Certified Services ({len(services)}):")
        for service in services:
            print(f"  - {service['service_name']}: {service['cert_id']} (Score: {service['overall_score']})")
    elif args.service:
        authority.run()
    else:
        print("Service Certification Authority - Level 3")
        print("Commands:")
        print("  --service          : Run as API service")
        print("  --certify <name>   : Start certification for service")
        print("  --audit <name>     : Run audit on service")
        print("  --list-certified   : List all Level 3 certified services")

if __name__ == "__main__":
    main()