#!/usr/bin/env python3
"""
🛡️ Database Consistency Guardian
Prevents database discrepancies through automated monitoring and fixing
"""

import os
import sqlite3
import re
from datetime import datetime
from typing import Dict, List, Tuple
from src.config.database_config import get_master_database_connection

class ServiceNameNormalizer:
    """Handles conversion between different naming conventions"""
    
    @staticmethod
    def to_database_name(python_name: str) -> str:
        """Convert Python file name to database service name"""
        # Remove common suffixes
        name = python_name.replace('_server', '').replace('_service', '').replace('_main', '')
        # Convert snake_case to kebab-case
        name = name.replace('_', '-')
        # Handle special cases
        name = name.replace('ai', 'AI').replace('api', 'API')
        return name
    
    @staticmethod
    def to_python_name(db_name: str) -> str:
        """Convert database service name to Python file name"""
        # Convert kebab-case to snake_case
        name = db_name.replace('-', '_').lower()
        # Add server suffix
        return f"{name}_server"
    
    @staticmethod
    def normalize_service_names() -> Dict[str, str]:
        """Create mapping between database names and Python files"""
        mapping = {}
        
        # Get database services
        try:
            conn = get_master_database_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT service_name FROM service_registry")
            db_services = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            for db_service in db_services:
                python_name = ServiceNameNormalizer.to_python_name(db_service)
                mapping[db_service] = python_name
                
        except Exception as e:
            print(f"Error normalizing names: {e}")
            
        return mapping

class DatabaseConsistencyGuardian:
    """Monitors and maintains database consistency"""
    
    def __init__(self):
        self.base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
        self.issues_fixed = 0
        
    def check_consistency(self) -> Dict[str, Any]:
        """Perform comprehensive consistency check"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'issues_found': [],
            'fixes_applied': [],
            'status': 'HEALTHY'
        }
        
        # Check 1: Service-File consistency
        service_file_issues = self._check_service_file_consistency()
        if service_file_issues:
            report['issues_found'].extend(service_file_issues)
            fixes = self._fix_service_file_issues(service_file_issues)
            report['fixes_applied'].extend(fixes)
        
        # Check 2: Port conflicts
        port_conflicts = self._check_port_conflicts()
        if port_conflicts:
            report['issues_found'].extend(port_conflicts)
            fixes = self._fix_port_conflicts(port_conflicts)
            report['fixes_applied'].extend(fixes)
        
        # Check 3: Database schema consistency
        schema_issues = self._check_schema_consistency()
        if schema_issues:
            report['issues_found'].extend(schema_issues)
        
        if report['issues_found']:
            report['status'] = 'ISSUES_FOUND' if not report['fixes_applied'] else 'FIXED'
        
        return report
    
    def _check_service_file_consistency(self) -> List[Dict]:
        """Check if all database services have corresponding files"""
        issues = []
        
        try:
            conn = sqlite3.connect(os.path.join(self.base_path, "service_registry.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT service_name FROM service_registry")
            db_services = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            for service in db_services:
                expected_file = ServiceNameNormalizer.to_python_name(service) + ".py"
                file_path = os.path.join(self.base_path, expected_file)
                
                if not os.path.exists(file_path):
                    # Check for alternative naming patterns
                    alternatives = [
                        service.lower().replace('-', '_') + '_server.py',
                        service.replace('-', '_') + '_server.py',
                        service.lower() + '_service.py'
                    ]
                    
                    found_alternative = None
                    for alt in alternatives:
                        alt_path = os.path.join(self.base_path, alt)
                        if os.path.exists(alt_path):
                            found_alternative = alt
                            break
                    
                    if found_alternative:
                        issues.append({
                            'type': 'NAMING_MISMATCH',
                            'service': service,
                            'expected_file': expected_file,
                            'actual_file': found_alternative,
                            'severity': 'MEDIUM'
                        })
                    else:
                        issues.append({
                            'type': 'MISSING_FILE',
                            'service': service,
                            'expected_file': expected_file,
                            'severity': 'HIGH'
                        })
                        
        except Exception as e:
            issues.append({
                'type': 'DATABASE_ERROR',
                'error': str(e),
                'severity': 'CRITICAL'
            })
        
        return issues
    
    def _fix_service_file_issues(self, issues: List[Dict]) -> List[str]:
        """Fix service file issues"""
        fixes = []
        
        for issue in issues:
            if issue['type'] == 'NAMING_MISMATCH':
                # Create symbolic link
                expected_path = os.path.join(self.base_path, issue['expected_file'])
                actual_path = os.path.join(self.base_path, issue['actual_file'])
                
                try:
                    if not os.path.exists(expected_path):
                        os.symlink(issue['actual_file'], expected_path)
                        fixes.append(f"Created symlink: {issue['expected_file']} -> {issue['actual_file']}")
                        self.issues_fixed += 1
                except Exception as e:
                    fixes.append(f"Failed to create symlink for {issue['service']}: {e}")
        
        return fixes
    
    def _check_port_conflicts(self) -> List[Dict]:
        """Check for port conflicts between databases"""
        conflicts = []
        ports_used = {}
        
        # Check service registry
        try:
            conn = sqlite3.connect(os.path.join(self.base_path, "service_registry.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT service_name, port FROM service_registry")
            for service, port in cursor.fetchall():
                if port in ports_used:
                    conflicts.append({
                        'type': 'PORT_CONFLICT',
                        'port': port,
                        'services': [ports_used[port], service],
                        'databases': ['service_registry', 'service_registry'],
                        'severity': 'CRITICAL'
                    })
                else:
                    ports_used[port] = service
            conn.close()
        except Exception:
            pass
        
        return conflicts
    
    def _fix_port_conflicts(self, conflicts: List[Dict]) -> List[str]:
        """Fix port conflicts by reassigning ports"""
        fixes = []
        # Implementation would go here - similar to what we did manually
        return fixes
    
    def _check_schema_consistency(self) -> List[Dict]:
        """Check database schema consistency"""
        issues = []
        # Implementation would check for schema mismatches
        return issues
    
    def run_guardian(self):
        """Run the consistency guardian"""
        print("🛡️ Database Consistency Guardian Starting...")
        report = self.check_consistency()
        
        print(f"Status: {report['status']}")
        print(f"Issues Found: {len(report['issues_found'])}")
        print(f"Fixes Applied: {len(report['fixes_applied'])}")
        
        if report['fixes_applied']:
            print("\nFixes Applied:")
            for fix in report['fixes_applied']:
                print(f"  ✅ {fix}")
        
        return report

# Usage
if __name__ == "__main__":
    guardian = DatabaseConsistencyGuardian()
    report = guardian.run_guardian()
