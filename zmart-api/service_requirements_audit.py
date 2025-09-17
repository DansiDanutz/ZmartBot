#!/usr/bin/env python3
"""
Service Requirements Audit - Level 2/3 Compliance Checker
Created: 2025-08-31
Purpose: Comprehensive audit of all services for Level 2/3 requirements compliance
Level: 3 (Authority System)
Port: 8908
Passport: SERVICE-REQ-AUDIT-8908-L3
Owner: zmartbot-system
Status: AUTHORITY
"""

import os
import sys
import sqlite3
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from flask import Flask, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceRequirementsAudit:
    """Comprehensive audit system for Level 2/3 requirements compliance"""
    
    def __init__(self, port=8908):
        self.port = port
        self.app = Flask(__name__)
        self.root_dir = Path(".")
        
        # Database paths
        self.level1_db = self.root_dir / "Level1.db"
        self.level2_db = self.root_dir / "Level2.db"
        self.level3_db = self.root_dir / "Level3.db"
        self.cert_db = self.root_dir / "CERT.db"
        
        # Common Python file extensions and patterns
        self.python_patterns = ["*.py", "**/*.py"]
        self.mdc_patterns = ["*.mdc", "**/*.mdc", ".cursor/rules/*.mdc"]
        
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "service": "service-requirements-audit",
                "port": self.port,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/audit-all')
        def audit_all():
            """Run complete requirements audit"""
            try:
                result = self.run_complete_audit()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/audit-level2')
        def audit_level2():
            """Audit Level 2 requirements specifically"""
            try:
                result = self.audit_level2_requirements()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/audit-files')
        def audit_files():
            """Audit file existence for all services"""
            try:
                result = self.audit_file_existence()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/fix-issues')
        def fix_issues():
            """Auto-fix common issues where possible"""
            try:
                result = self.auto_fix_common_issues()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def run_complete_audit(self) -> Dict:
        """Run comprehensive audit of all services"""
        logger.info("Starting comprehensive service requirements audit...")
        
        # Get all services from all levels
        level1_services = self.get_level1_services()
        level2_services = self.get_level2_services()
        level3_services = self.get_level3_services()
        cert_services = self.get_cert_services()
        
        # Audit each level
        level1_audit = self.audit_level1_services(level1_services)
        level2_audit = self.audit_level2_services(level2_services)
        level3_audit = self.audit_level3_services(level3_services)
        cert_audit = self.audit_cert_services(cert_services)
        
        # File existence audit
        file_audit = self.audit_file_existence()
        
        # Calculate overall compliance
        total_services = len(level1_services) + len(level2_services) + len(level3_services)
        compliant_services = (level1_audit['compliant_count'] + 
                            level2_audit['compliant_count'] + 
                            level3_audit['compliant_count'])
        
        overall_compliance = (compliant_services / total_services * 100) if total_services > 0 else 0
        
        return {
            "audit_timestamp": datetime.now().isoformat(),
            "overall_compliance_percentage": round(overall_compliance, 2),
            "total_services_audited": total_services,
            "compliant_services": compliant_services,
            "non_compliant_services": total_services - compliant_services,
            
            "level_breakdown": {
                "level1_discovery": {
                    "total": len(level1_services),
                    "compliant": level1_audit['compliant_count'],
                    "issues": level1_audit['issues']
                },
                "level2_active": {
                    "total": len(level2_services),
                    "compliant": level2_audit['compliant_count'],
                    "issues": level2_audit['issues']
                },
                "level3_certified": {
                    "total": len(level3_services),
                    "compliant": level3_audit['compliant_count'],
                    "issues": level3_audit['issues']
                }
            },
            
            "file_audit": file_audit,
            "cert_audit": cert_audit,
            
            "critical_issues": self.identify_critical_issues(level2_audit, level3_audit),
            "recommendations": self.generate_recommendations(level1_audit, level2_audit, level3_audit)
        }
    
    def audit_level2_requirements(self) -> Dict:
        """Detailed audit of Level 2 requirements compliance"""
        level2_services = self.get_level2_services()
        return self.audit_level2_services(level2_services)
    
    def audit_level1_services(self, services: List[Dict]) -> Dict:
        """Audit Level 1 discovery services"""
        issues = []
        compliant_count = 0
        
        for service in services:
            service_issues = []
            
            # Level 1 just needs to exist in discovery
            # Main issue would be missing basic information
            if not service.get('file_path'):
                service_issues.append("No file path identified")
            
            if not service.get('estimated_type'):
                service_issues.append("Service type not estimated")
            
            if not service.get('discovery_source'):
                service_issues.append("Discovery source not recorded")
            
            if not service_issues:
                compliant_count += 1
            else:
                issues.append({
                    "service_name": service['service_name'],
                    "issues": service_issues
                })
        
        return {
            "compliant_count": compliant_count,
            "total_count": len(services),
            "compliance_percentage": (compliant_count / len(services) * 100) if services else 0,
            "issues": issues
        }
    
    def audit_level2_services(self, services: List[Dict]) -> Dict:
        """Audit Level 2 active services for compliance"""
        issues = []
        compliant_count = 0
        
        for service in services:
            service_issues = []
            
            # Level 2 Requirement 1: Python file exists and functional
            python_file = service.get('file_path')
            if not python_file:
                service_issues.append("No Python file path specified")
            elif not Path(python_file).exists():
                service_issues.append(f"Python file does not exist: {python_file}")
            
            # Level 2 Requirement 2: MDC file assigned and documented
            mdc_file = service.get('mdc_file_path')
            if not mdc_file:
                # Try to find MDC file
                mdc_found = self.find_mdc_file(service['service_name'])
                if not mdc_found:
                    service_issues.append("No MDC file found or assigned")
            elif not Path(mdc_file).exists():
                service_issues.append(f"MDC file does not exist: {mdc_file}")
            
            # Level 2 Requirement 3: Passport ID assigned (format: SERVICE-NAME-PORT-L2)
            passport_id = service.get('passport_id')
            if not passport_id:
                service_issues.append("No passport ID assigned")
            elif not self.validate_level2_passport_format(passport_id):
                service_issues.append(f"Invalid Level 2 passport format: {passport_id}")
            
            # Additional checks
            if not service.get('port'):
                service_issues.append("No port assigned")
            
            if not service.get('service_type'):
                service_issues.append("No service type specified")
            
            if not service_issues:
                compliant_count += 1
            else:
                issues.append({
                    "service_name": service['service_name'],
                    "passport_id": passport_id,
                    "port": service.get('port'),
                    "issues": service_issues
                })
        
        return {
            "compliant_count": compliant_count,
            "total_count": len(services),
            "compliance_percentage": (compliant_count / len(services) * 100) if services else 0,
            "issues": issues
        }
    
    def audit_level3_services(self, services: List[Dict]) -> Dict:
        """Audit Level 3 certified services"""
        issues = []
        compliant_count = 0
        
        for service in services:
            service_issues = []
            
            # Level 3 inherits all Level 2 requirements plus additional ones
            # For now, just check basic structure since Level 3 is newly implemented
            
            if not service.get('cert_id'):
                service_issues.append("No certification ID assigned")
            
            if not service.get('cert_status'):
                service_issues.append("No certification status")
            
            if not service_issues:
                compliant_count += 1
            else:
                issues.append({
                    "service_name": service['service_name'],
                    "cert_id": service.get('cert_id'),
                    "issues": service_issues
                })
        
        return {
            "compliant_count": compliant_count,
            "total_count": len(services),
            "compliance_percentage": (compliant_count / len(services) * 100) if services else 0,
            "issues": issues
        }
    
    def audit_cert_services(self, services: List[Dict]) -> Dict:
        """Audit CERT database consistency"""
        return {
            "total_certified": len(services),
            "sequential_integrity": self.check_cert_sequential_integrity(services),
            "cert_database_consistent": True  # Placeholder for more detailed checks
        }
    
    def audit_file_existence(self) -> Dict:
        """Comprehensive file existence audit"""
        logger.info("Auditing file existence across all services...")
        
        # Get all Python files in the project
        python_files = set()
        for pattern in self.python_patterns:
            python_files.update(Path(".").glob(pattern))
        
        # Get all MDC files
        mdc_files = set()
        for pattern in self.mdc_patterns:
            mdc_files.update(Path(".").glob(pattern))
        
        # Get all services from databases
        all_services = []
        all_services.extend(self.get_level1_services())
        all_services.extend(self.get_level2_services())
        all_services.extend(self.get_level3_services())
        
        # Audit file assignments
        python_file_issues = []
        mdc_file_issues = []
        orphaned_files = list(python_files)  # Start with all files, remove assigned ones
        
        for service in all_services:
            service_name = service['service_name']
            
            # Check Python file
            python_path = service.get('file_path')
            if python_path:
                python_file = Path(python_path)
                if not python_file.exists():
                    python_file_issues.append({
                        "service": service_name,
                        "file": str(python_path),
                        "issue": "File does not exist"
                    })
                else:
                    # Remove from orphaned list
                    if python_file in orphaned_files:
                        orphaned_files.remove(python_file)
            
            # Check MDC file
            mdc_path = service.get('mdc_file_path')
            if not mdc_path:
                # Try to find matching MDC file
                found_mdc = self.find_mdc_file(service_name)
                if not found_mdc:
                    mdc_file_issues.append({
                        "service": service_name,
                        "issue": "No MDC file assigned or found"
                    })
            else:
                mdc_file = Path(mdc_path)
                if not mdc_file.exists():
                    mdc_file_issues.append({
                        "service": service_name,
                        "file": str(mdc_path),
                        "issue": "MDC file does not exist"
                    })
        
        return {
            "total_python_files": len(python_files),
            "total_mdc_files": len(mdc_files),
            "total_services": len(all_services),
            "python_file_issues": python_file_issues,
            "mdc_file_issues": mdc_file_issues,
            "orphaned_python_files": [str(f) for f in orphaned_files[:10]],  # Limit output
            "orphaned_files_count": len(orphaned_files)
        }
    
    def find_mdc_file(self, service_name: str) -> Optional[str]:
        """Find MDC file for a service"""
        search_patterns = [
            f"**/*{service_name}*.mdc",
            f"**/{service_name}.mdc",
            f".cursor/rules/{service_name}.mdc",
            f".cursor/rules/*{service_name}*.mdc"
        ]
        
        for pattern in search_patterns:
            matches = list(Path(".").glob(pattern))
            if matches:
                return str(matches[0])  # Return first match
        
        return None
    
    def validate_level2_passport_format(self, passport_id: str) -> bool:
        """Validate Level 2 passport format: SERVICE-NAME-PORT-L2"""
        if not passport_id:
            return False
        
        # Should end with -L2
        if not passport_id.endswith('-L2'):
            return False
        
        # Should have at least 3 parts when split by -
        parts = passport_id.split('-')
        if len(parts) < 3:
            return False
        
        # Port should be numeric (second to last part)
        try:
            int(parts[-2])
            return True
        except (ValueError, IndexError):
            return False
    
    def check_cert_sequential_integrity(self, cert_services: List[Dict]) -> bool:
        """Check if CERT IDs are sequential"""
        if not cert_services:
            return True
        
        cert_numbers = []
        for service in cert_services:
            cert_id = service.get('cert_id', '')
            if cert_id.startswith('CERT'):
                try:
                    number = int(cert_id[4:])  # Remove 'CERT' prefix
                    cert_numbers.append(number)
                except ValueError:
                    return False
        
        cert_numbers.sort()
        expected = list(range(1, len(cert_numbers) + 1))
        return cert_numbers == expected
    
    def identify_critical_issues(self, level2_audit: Dict, level3_audit: Dict) -> List[Dict]:
        """Identify critical issues that need immediate attention"""
        critical_issues = []
        
        # Level 2 issues are critical as these are active production services
        for issue in level2_audit.get('issues', []):
            if any(critical in str(issue['issues']) for critical in ['Python file does not exist', 'No passport ID']):
                critical_issues.append({
                    "level": "CRITICAL",
                    "service": issue['service_name'],
                    "issues": issue['issues'],
                    "impact": "Level 2 service non-compliance affects production readiness"
                })
        
        return critical_issues
    
    def generate_recommendations(self, level1_audit: Dict, level2_audit: Dict, level3_audit: Dict) -> List[str]:
        """Generate recommendations based on audit results"""
        recommendations = []
        
        if level2_audit['compliance_percentage'] < 90:
            recommendations.append(f"Level 2 compliance is {level2_audit['compliance_percentage']:.1f}% - prioritize fixing Level 2 issues")
        
        if level1_audit['total_count'] > 100:
            recommendations.append(f"High number of Level 1 discovery services ({level1_audit['total_count']}) - consider promoting eligible services")
        
        recommendations.append("Run automated fixes for common issues using /api/fix-issues endpoint")
        recommendations.append("Implement regular compliance monitoring schedule")
        
        return recommendations
    
    def auto_fix_common_issues(self) -> Dict:
        """Automatically fix common issues where possible"""
        fixes_applied = []
        errors = []
        
        try:
            # Fix 1: Auto-assign missing MDC file paths for Level 2 services
            level2_services = self.get_level2_services()
            mdc_fixes = 0
            
            for service in level2_services:
                if not service.get('mdc_file_path'):
                    mdc_file = self.find_mdc_file(service['service_name'])
                    if mdc_file:
                        # Update database with found MDC file
                        self.update_service_mdc_path(service['service_name'], mdc_file)
                        mdc_fixes += 1
                        fixes_applied.append(f"Assigned MDC file to {service['service_name']}: {mdc_file}")
            
            return {
                "status": "completed",
                "fixes_applied": len(fixes_applied),
                "mdc_file_fixes": mdc_fixes,
                "fixes": fixes_applied[:10],  # Limit output
                "errors": errors
            }
            
        except Exception as e:
            errors.append(str(e))
            return {
                "status": "partial",
                "fixes_applied": len(fixes_applied),
                "fixes": fixes_applied,
                "errors": errors
            }
    
    def update_service_mdc_path(self, service_name: str, mdc_path: str):
        """Update service with MDC file path"""
        try:
            conn = sqlite3.connect(self.level2_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE level2_active_services 
                SET mdc_file_path = ?, updated_at = ?
                WHERE service_name = ?
            """, (mdc_path, datetime.now(), service_name))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating MDC path for {service_name}: {e}")
    
    # Database helper methods
    def get_level1_services(self) -> List[Dict]:
        """Get all Level 1 discovery services"""
        try:
            conn = sqlite3.connect(self.level1_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, file_path, estimated_type, discovery_source, status
                FROM level1_discovery_services
            """)
            
            services = []
            for row in cursor.fetchall():
                services.append({
                    'service_name': row[0],
                    'file_path': row[1],
                    'estimated_type': row[2],
                    'discovery_source': row[3],
                    'status': row[4]
                })
            
            conn.close()
            return services
        except Exception as e:
            logger.error(f"Error getting Level 1 services: {e}")
            return []
    
    def get_level2_services(self) -> List[Dict]:
        """Get all Level 2 active services"""
        try:
            conn = sqlite3.connect(self.level2_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, passport_id, port, service_type, status,
                       file_path, mdc_file_path, health_endpoint, description
                FROM level2_active_services
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
                    'mdc_file_path': row[6],
                    'health_endpoint': row[7],
                    'description': row[8]
                })
            
            conn.close()
            return services
        except Exception as e:
            logger.error(f"Error getting Level 2 services: {e}")
            return []
    
    def get_level3_services(self) -> List[Dict]:
        """Get all Level 3 certified services"""
        try:
            conn = sqlite3.connect(self.level3_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, passport_id, cert_id, port, service_type, cert_status
                FROM level3_certified_services
            """)
            
            services = []
            for row in cursor.fetchall():
                services.append({
                    'service_name': row[0],
                    'passport_id': row[1],
                    'cert_id': row[2],
                    'port': row[3],
                    'service_type': row[4],
                    'cert_status': row[5]
                })
            
            conn.close()
            return services
        except Exception as e:
            logger.error(f"Error getting Level 3 services: {e}")
            return []
    
    def get_cert_services(self) -> List[Dict]:
        """Get all certified services from CERT database"""
        try:
            conn = sqlite3.connect(self.cert_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cert_id, cert_number, service_name, passport_id, port
                FROM cert_registry
            """)
            
            services = []
            for row in cursor.fetchall():
                services.append({
                    'cert_id': row[0],
                    'cert_number': row[1],
                    'service_name': row[2],
                    'passport_id': row[3],
                    'port': row[4]
                })
            
            conn.close()
            return services
        except Exception as e:
            logger.error(f"Error getting CERT services: {e}")
            return []
    
    def run(self):
        """Run the service requirements audit service"""
        logger.info(f"Starting Service Requirements Audit on port {self.port}")
        logger.info("Comprehensive Level 2/3 Requirements Compliance System Ready")
        
        try:
            self.app.run(host='127.0.0.1', port=self.port, debug=False)
        except KeyboardInterrupt:
            logger.info("Service Requirements Audit stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Service Requirements Audit")
    parser.add_argument('--port', type=int, default=8908, help='Service port')
    parser.add_argument('--service', action='store_true', help='Run as service')
    parser.add_argument('--audit', action='store_true', help='Run complete audit')
    parser.add_argument('--audit-level2', action='store_true', help='Audit Level 2 only')
    parser.add_argument('--fix', action='store_true', help='Auto-fix issues')
    
    args = parser.parse_args()
    
    audit_service = ServiceRequirementsAudit(port=args.port)
    
    if args.audit:
        result = audit_service.run_complete_audit()
        print(f"Complete Audit Results: {json.dumps(result, indent=2)}")
    elif args.audit_level2:
        result = audit_service.audit_level2_requirements()
        print(f"Level 2 Audit Results: {json.dumps(result, indent=2)}")
    elif args.fix:
        result = audit_service.auto_fix_common_issues()
        print(f"Auto-fix Results: {json.dumps(result, indent=2)}")
    elif args.service:
        audit_service.run()
    else:
        print("Service Requirements Audit")
        print("Commands:")
        print("  --service      : Run as API service")
        print("  --audit        : Run complete audit")
        print("  --audit-level2 : Audit Level 2 requirements only")
        print("  --fix          : Auto-fix common issues")

if __name__ == "__main__":
    main()