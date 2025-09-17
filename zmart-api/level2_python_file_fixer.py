#!/usr/bin/env python3
"""
Level 2 Python File Fixer - Critical Compliance Remediation
Created: 2025-08-31
Purpose: Fix all Level 2 services missing Python file paths - CRITICAL SYSTEM ISSUE
Level: 3 (Authority System)
Port: 8909
Passport: L2-PYTHON-FIXER-8909-L3
Owner: zmartbot-system
Status: AUTHORITY
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Level2PythonFileFixer:
    """Critical system to fix Level 2 services missing Python file paths"""
    
    def __init__(self, port=8909):
        self.port = port
        self.app = Flask(__name__)
        self.root_dir = Path(".")
        self.level2_db = self.root_dir / "Level2.db"
        
        # Python file patterns to search
        self.python_patterns = ["*.py", "**/*.py"]
        
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "service": "level2-python-file-fixer",
                "port": self.port,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/fix-all')
        def fix_all():
            """Fix all Level 2 services missing Python files"""
            try:
                result = self.fix_all_level2_python_files()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/scan-python-files')
        def scan_python_files():
            """Scan and catalog all Python files"""
            try:
                result = self.scan_all_python_files()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/level2-status')
        def level2_status():
            """Get Level 2 services status"""
            try:
                result = self.get_level2_status()
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def fix_all_level2_python_files(self) -> Dict:
        """Fix all Level 2 services missing Python file paths"""
        logger.info("🚨 CRITICAL: Starting Level 2 Python file path remediation...")
        
        # Get all Level 2 services
        level2_services = self.get_level2_services()
        logger.info(f"Found {len(level2_services)} Level 2 services to check")
        
        # Scan all Python files
        python_files = self.scan_all_python_files()
        logger.info(f"Found {len(python_files['files'])} Python files in system")
        
        fixes_applied = []
        services_fixed = 0
        services_failed = []
        
        for service in level2_services:
            service_name = service['service_name']
            current_file_path = service.get('file_path')
            
            # Skip if already has valid file path
            if current_file_path and Path(current_file_path).exists():
                continue
            
            # Find matching Python file
            python_file = self.find_python_file_for_service(service_name, python_files['files'])
            
            if python_file:
                # Update database with found Python file
                success = self.update_service_python_path(service_name, python_file)
                if success:
                    fixes_applied.append({
                        "service_name": service_name,
                        "old_path": current_file_path,
                        "new_path": python_file,
                        "fix_type": "PYTHON_FILE_ASSIGNED"
                    })
                    services_fixed += 1
                else:
                    services_failed.append({
                        "service_name": service_name,
                        "reason": "Database update failed"
                    })
            else:
                # No matching Python file found - this is a critical issue
                services_failed.append({
                    "service_name": service_name,
                    "reason": "No matching Python file found",
                    "recommendation": "Service may need implementation or removal"
                })
        
        return {
            "status": "completed",
            "critical_issue": "Level 2 services without Python files",
            "total_level2_services": len(level2_services),
            "services_fixed": services_fixed,
            "services_failed": len(services_failed),
            "fixes_applied": fixes_applied[:20],  # Limit output
            "failed_services": services_failed,
            "next_steps": [
                "Review failed services for manual intervention",
                "Create missing Python files for valid services", 
                "Consider removing invalid service entries"
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    def scan_all_python_files(self) -> Dict:
        """Scan and catalog all Python files in the system"""
        python_files = []
        
        for pattern in self.python_patterns:
            for py_file in Path(".").glob(pattern):
                if py_file.is_file() and not self.should_skip_file(py_file):
                    python_files.append({
                        "path": str(py_file),
                        "name": py_file.stem,
                        "size": py_file.stat().st_size,
                        "modified": datetime.fromtimestamp(py_file.stat().st_mtime).isoformat()
                    })
        
        # Sort by modification time (newest first)
        python_files.sort(key=lambda x: x['modified'], reverse=True)
        
        return {
            "total_files": len(python_files),
            "files": python_files,
            "scan_timestamp": datetime.now().isoformat()
        }
    
    def should_skip_file(self, py_file: Path) -> bool:
        """Check if Python file should be skipped"""
        skip_patterns = [
            # Virtual environment files
            'venv/', 'env/', '.venv/', 'site-packages/',
            # Test files (unless service-specific)
            '__pycache__/', '.pytest_cache/',
            # System files
            '.git/', '.DS_Store',
            # Library files
            'node_modules/', 'build/', 'dist/'
        ]
        
        file_str = str(py_file)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def find_python_file_for_service(self, service_name: str, python_files: List[Dict]) -> Optional[str]:
        """Find matching Python file for service"""
        # Clean service name for matching
        clean_service_name = service_name.lower().replace('-', '_').replace(' ', '_')
        
        # Direct name matches (highest priority)
        for py_file in python_files:
            file_name = Path(py_file['path']).stem.lower()
            
            # Exact match
            if file_name == clean_service_name:
                return py_file['path']
            
            # Service name contains file name
            if clean_service_name in file_name or file_name in clean_service_name:
                return py_file['path']
        
        # Pattern-based matches (lower priority)
        service_keywords = clean_service_name.split('_')
        
        for py_file in python_files:
            file_name = Path(py_file['path']).stem.lower()
            
            # Check if multiple keywords match
            matches = sum(1 for keyword in service_keywords if keyword in file_name)
            if matches >= 2:  # At least 2 keywords match
                return py_file['path']
        
        # Special service mappings
        service_mappings = {
            'zmart-api': ['main.py', 'api.py', 'app.py', 'server.py'],
            'zmart-dashboard': ['dashboard.py', 'frontend.py', 'ui.py'],
            'master-orchestration-agent': ['orchestration.py', 'master_orchestration.py'],
            'port-manager-service': ['port_manager.py', 'ports.py'],
            'mysymbols': ['symbols.py', 'my_symbols.py', 'mysymbols.py'],
            'binance': ['binance.py', 'binance_client.py'],
            'kucoin': ['kucoin.py', 'kucoin_client.py'],
        }
        
        if clean_service_name.replace('_', '-') in service_mappings:
            for candidate_name in service_mappings[clean_service_name.replace('_', '-')]:
                for py_file in python_files:
                    if candidate_name in py_file['path'].lower():
                        return py_file['path']
        
        return None
    
    def update_service_python_path(self, service_name: str, python_path: str) -> bool:
        """Update service with Python file path"""
        try:
            conn = sqlite3.connect(self.level2_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE level2_active_services 
                SET file_path = ?, updated_at = ?
                WHERE service_name = ?
            """, (python_path, datetime.now(), service_name))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if success:
                logger.info(f"✅ Updated {service_name} with Python file: {python_path}")
            else:
                logger.error(f"❌ Failed to update {service_name} - service not found")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error updating {service_name}: {e}")
            return False
    
    def get_level2_services(self) -> List[Dict]:
        """Get all Level 2 services"""
        try:
            conn = sqlite3.connect(self.level2_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, passport_id, port, service_type, file_path, mdc_file_path
                FROM level2_active_services
                ORDER BY service_name
            """)
            
            services = []
            for row in cursor.fetchall():
                services.append({
                    'service_name': row[0],
                    'passport_id': row[1],
                    'port': row[2],
                    'service_type': row[3],
                    'file_path': row[4],
                    'mdc_file_path': row[5]
                })
            
            conn.close()
            return services
        except Exception as e:
            logger.error(f"Error getting Level 2 services: {e}")
            return []
    
    def get_level2_status(self) -> Dict:
        """Get current Level 2 compliance status"""
        services = self.get_level2_services()
        
        missing_python = 0
        missing_mdc = 0
        fully_compliant = 0
        
        for service in services:
            python_missing = not service.get('file_path') or not Path(service['file_path']).exists() if service.get('file_path') else True
            mdc_missing = not service.get('mdc_file_path') or not Path(service['mdc_file_path']).exists() if service.get('mdc_file_path') else True
            
            if python_missing:
                missing_python += 1
            if mdc_missing:
                missing_mdc += 1
            if not python_missing and not mdc_missing:
                fully_compliant += 1
        
        compliance_percentage = (fully_compliant / len(services) * 100) if services else 0
        
        return {
            "total_level2_services": len(services),
            "missing_python_files": missing_python,
            "missing_mdc_files": missing_mdc,
            "fully_compliant": fully_compliant,
            "compliance_percentage": round(compliance_percentage, 2),
            "critical_issue": missing_python == len(services),
            "status": "CRITICAL" if compliance_percentage < 50 else "WARNING" if compliance_percentage < 90 else "GOOD",
            "timestamp": datetime.now().isoformat()
        }
    
    def run(self):
        """Run the Level 2 Python file fixer service"""
        logger.info(f"Starting Level 2 Python File Fixer on port {self.port}")
        logger.info("🚨 CRITICAL COMPLIANCE REMEDIATION SYSTEM READY")
        
        try:
            self.app.run(host='127.0.0.1', port=self.port, debug=False)
        except KeyboardInterrupt:
            logger.info("Level 2 Python File Fixer stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Level 2 Python File Fixer")
    parser.add_argument('--port', type=int, default=8909, help='Service port')
    parser.add_argument('--service', action='store_true', help='Run as service')
    parser.add_argument('--fix', action='store_true', help='Fix all Level 2 Python file issues')
    parser.add_argument('--scan', action='store_true', help='Scan all Python files')
    parser.add_argument('--status', action='store_true', help='Check Level 2 status')
    
    args = parser.parse_args()
    
    fixer = Level2PythonFileFixer(port=args.port)
    
    if args.fix:
        result = fixer.fix_all_level2_python_files()
        print(f"🚨 CRITICAL FIX RESULTS: {json.dumps(result, indent=2)}")
    elif args.scan:
        result = fixer.scan_all_python_files()
        print(f"Python Files Scan: {json.dumps(result, indent=2)}")
    elif args.status:
        result = fixer.get_level2_status()
        print(f"Level 2 Status: {json.dumps(result, indent=2)}")
    elif args.service:
        fixer.run()
    else:
        print("Level 2 Python File Fixer - CRITICAL COMPLIANCE REMEDIATION")
        print("Commands:")
        print("  --service    : Run as API service")
        print("  --fix        : Fix all Level 2 Python file issues")
        print("  --scan       : Scan all Python files in system")
        print("  --status     : Check Level 2 compliance status")

if __name__ == "__main__":
    main()