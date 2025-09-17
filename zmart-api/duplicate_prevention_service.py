#!/usr/bin/env python3
"""
Duplicate Prevention Service - Prevent Level 3 promotion violations
Created: 2025-08-31
Purpose: Validate services before Level 3 promotion to prevent duplicates
"""

import sqlite3
from pathlib import Path
from typing import Dict, Optional

class DuplicatePreventionService:
    """Service to prevent duplicate violations in Level 3 promotions"""
    
    def __init__(self):
        self.level3_db = Path("Level3.db")
    
    def validate_service_for_promotion(self, service_name: str, python_file: str) -> Dict:
        """
        Validate a service before Level 3 promotion
        Returns validation result with any violations found
        """
        violations = []
        
        # Check for exact service name duplicate
        if self._check_exact_name_duplicate(service_name):
            violations.append({
                "type": "EXACT_DUPLICATE",
                "message": f"Service '{service_name}' already exists in Level 3"
            })
        
        # Check for normalized name conflicts
        conflict = self._check_normalized_name_conflict(service_name)
        if conflict:
            violations.append({
                "type": "NORMALIZED_NAME_CONFLICT",
                "message": f"Service '{service_name}' conflicts with existing '{conflict}' (normalized names identical)"
            })
        
        # Check for Python file sharing
        file_conflict = self._check_python_file_conflict(python_file)
        if file_conflict:
            violations.append({
                "type": "PYTHON_FILE_SHARING",
                "message": f"Python file '{python_file}' already used by service '{file_conflict}'"
            })
        
        return {
            "service_name": service_name,
            "python_file": python_file,
            "valid": len(violations) == 0,
            "violations": violations,
            "can_promote": len(violations) == 0
        }
    
    def _check_exact_name_duplicate(self, service_name: str) -> bool:
        """Check if exact service name already exists"""
        conn = sqlite3.connect(self.level3_db)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM level3_certified_services WHERE service_name = ?', (service_name,))
        result = cursor.fetchone() is not None
        conn.close()
        return result
    
    def _check_normalized_name_conflict(self, service_name: str) -> Optional[str]:
        """Check if normalized service name conflicts with existing services"""
        normalized_current = service_name.lower().replace('-', '').replace('_', '')
        
        conn = sqlite3.connect(self.level3_db)
        cursor = conn.cursor()
        cursor.execute('SELECT service_name FROM level3_certified_services')
        all_services = cursor.fetchall()
        conn.close()
        
        for (existing_name,) in all_services:
            normalized_existing = existing_name.lower().replace('-', '').replace('_', '')
            if normalized_current == normalized_existing and service_name != existing_name:
                return existing_name
        
        return None
    
    def _check_python_file_conflict(self, python_file: str) -> Optional[str]:
        """Check if Python file is already used by another service"""
        if not python_file:
            return None
            
        conn = sqlite3.connect(self.level3_db)
        cursor = conn.cursor()
        cursor.execute('SELECT service_name FROM level3_certified_services WHERE file_path = ?', (python_file,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_all_violations(self) -> Dict:
        """Get all current violations in Level 3 database"""
        conn = sqlite3.connect(self.level3_db)
        cursor = conn.cursor()
        cursor.execute('SELECT service_name, cert_id, port, file_path FROM level3_certified_services ORDER BY service_name')
        services = cursor.fetchall()
        conn.close()
        
        # Check for Python file sharing
        file_violations = {}
        for service_name, cert_id, port, file_path in services:
            if file_path in file_violations:
                file_violations[file_path].append((service_name, cert_id, port))
            else:
                file_violations[file_path] = [(service_name, cert_id, port)]
        
        # Filter to only violations (multiple services per file)
        file_violations = {k: v for k, v in file_violations.items() if len(v) > 1}
        
        # Check for name conflicts
        name_violations = {}
        for service_name, cert_id, port, file_path in services:
            normalized = service_name.lower().replace('-', '').replace('_', '')
            if normalized in name_violations:
                name_violations[normalized].append((service_name, cert_id, port))
            else:
                name_violations[normalized] = [(service_name, cert_id, port)]
        
        # Filter to only violations (multiple services per normalized name)
        name_violations = {k: v for k, v in name_violations.items() if len(v) > 1}
        
        return {
            "total_services": len(services),
            "python_file_violations": file_violations,
            "name_conflicts": name_violations,
            "clean": len(file_violations) == 0 and len(name_violations) == 0
        }

def main():
    """CLI interface for duplicate prevention"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Duplicate Prevention Service")
    parser.add_argument('--validate', nargs=2, metavar=('SERVICE_NAME', 'PYTHON_FILE'),
                       help='Validate service for promotion')
    parser.add_argument('--check-all', action='store_true',
                       help='Check all current violations')
    
    args = parser.parse_args()
    
    service = DuplicatePreventionService()
    
    if args.validate:
        service_name, python_file = args.validate
        result = service.validate_service_for_promotion(service_name, python_file)
        print(json.dumps(result, indent=2))
    elif args.check_all:
        result = service.get_all_violations()
        print(json.dumps(result, indent=2))
    else:
        print("Duplicate Prevention Service")
        print("Commands:")
        print("  --validate SERVICE_NAME PYTHON_FILE : Validate service for promotion")
        print("  --check-all                         : Check all current violations")

if __name__ == "__main__":
    main()