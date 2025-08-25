#!/usr/bin/env python3
"""
Service Registration Validation Script
Prevents duplicate service registration by checking ports, names, and existing services
"""

import sqlite3
import subprocess
import sys
from pathlib import Path

class ServiceRegistrationValidator:
    def __init__(self):
        self.project_root = Path("/Users/dansidanutz/Desktop/ZmartBot")
        self.port_registry_db = self.project_root / "zmart-api" / "port_registry.db"
        self.service_registry_db = self.project_root / "zmart-api" / "src" / "data" / "service_registry.db"
        self.mdc_dir = self.project_root / ".cursor" / "rules"
        
        # Standardized service name mapping
        self.service_name_mapping = {
            'zmart_orchestration': 'master_orchestration_agent',
            'zmart_dashboard': 'zmart-dashboard',
            'zmart_api': 'zmart-api',
            'my_symbols': 'mysymbols',
            'api_keys_manager': 'api-keys-manager-service',
            'zmart_analytics': 'zmart-analytics',
            'zmart_notification': 'zmart-notification',
            'zmart_websocket': 'zmart-websocket'
        }
    
    def check_port_conflict(self, port):
        """Check if port is already assigned"""
        try:
            conn = sqlite3.connect(self.port_registry_db)
            cursor = conn.cursor()
            cursor.execute("SELECT service_name, status, pid FROM port_assignments WHERE port = ?", (port,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                service_name, status, pid = result
                print(f"❌ PORT CONFLICT: Port {port} already assigned to '{service_name}' (Status: {status}, PID: {pid})")
                return True
            else:
                print(f"✅ Port {port} is available")
                return False
        except Exception as e:
            print(f"⚠️ Error checking port registry: {e}")
            return False
    
    def check_service_name_conflict(self, service_name, port):
        """Check for existing services with similar names or same port"""
        try:
            conn = sqlite3.connect(self.service_registry_db)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT service_name, kind, port, status 
                FROM service_registry 
                WHERE service_name LIKE ? OR port = ?
            """, (f'%{service_name}%', port))
            results = cursor.fetchall()
            conn.close()
            
            if results:
                print(f"❌ SERVICE NAME CONFLICT: Found existing services:")
                for service_name_existing, kind, port_existing, status in results:
                    print(f"   - '{service_name_existing}' ({kind}) - Port {port_existing} - Status: {status}")
                return True
            else:
                print(f"✅ Service name '{service_name}' is available")
                return False
        except Exception as e:
            print(f"⚠️ Error checking service registry: {e}")
            return False
    
    def check_mdc_file_duplication(self, service_name, port):
        """Check for existing MDC files"""
        try:
            # Check for service name in MDC files
            service_files = list(self.mdc_dir.glob(f"*{service_name}*"))
            port_files = list(self.mdc_dir.glob(f"*{port}*"))
            
            if service_files or port_files:
                print(f"❌ MDC FILE DUPLICATION: Found existing MDC files:")
                for file in service_files + port_files:
                    print(f"   - {file.name}")
                return True
            else:
                print(f"✅ No existing MDC files found for '{service_name}' or port {port}")
                return False
        except Exception as e:
            print(f"⚠️ Error checking MDC files: {e}")
            return False
    
    def check_process_running(self, service_name):
        """Check if service process is already running"""
        try:
            result = subprocess.run(
                ['ps', 'aux'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            lines = result.stdout.split('\n')
            matching_lines = [line for line in lines if service_name.lower() in line.lower() and 'grep' not in line and 'validate_service_registration' not in line]
            
            if matching_lines:
                print(f"❌ PROCESS RUNNING: Found running processes for '{service_name}':")
                for line in matching_lines[:3]:  # Show first 3 matches
                    print(f"   - {line.strip()}")
                return True
            else:
                print(f"✅ No running processes found for '{service_name}'")
                return False
        except Exception as e:
            print(f"⚠️ Error checking processes: {e}")
            return False
    
    def check_service_name_mapping(self, service_name):
        """Check if service name should be mapped to existing service"""
        if service_name in self.service_name_mapping:
            mapped_name = self.service_name_mapping[service_name]
            print(f"⚠️ SERVICE NAME MAPPING: '{service_name}' should be mapped to '{mapped_name}'")
            return mapped_name
        return None
    
    def validate_service_registration(self, service_name, port):
        """Perform all validation checks"""
        print(f"🔍 Validating service registration for '{service_name}' on port {port}")
        print("=" * 60)
        
        conflicts = []
        
        # Check service name mapping
        mapped_name = self.check_service_name_mapping(service_name)
        if mapped_name:
            conflicts.append(f"Service name mapping conflict: {service_name} → {mapped_name}")
        
        # Check port conflict
        if self.check_port_conflict(port):
            conflicts.append(f"Port {port} already assigned")
        
        # Check service name conflict
        if self.check_service_name_conflict(service_name, port):
            conflicts.append(f"Service name '{service_name}' conflicts with existing services")
        
        # Check MDC file duplication
        if self.check_mdc_file_duplication(service_name, port):
            conflicts.append(f"MDC files already exist for '{service_name}' or port {port}")
        
        # Check process running
        if self.check_process_running(service_name):
            conflicts.append(f"Process already running for '{service_name}'")
        
        print("=" * 60)
        
        if conflicts:
            print("❌ VALIDATION FAILED: Found conflicts:")
            for conflict in conflicts:
                print(f"   - {conflict}")
            print("\n💡 RECOMMENDATIONS:")
            print("   1. Use existing service if it's the same functionality")
            print("   2. Choose a different port if service is different")
            print("   3. Choose a different service name if needed")
            print("   4. Stop existing process if replacing service")
            return False
        else:
            print("✅ VALIDATION PASSED: Service can be registered safely")
            return True

def main():
    if len(sys.argv) != 3:
        print("Usage: python validate_service_registration.py <service_name> <port>")
        print("Example: python validate_service_registration.py zmart_risk_management 8010")
        sys.exit(1)
    
    service_name = sys.argv[1]
    port = int(sys.argv[2])
    
    validator = ServiceRegistrationValidator()
    success = validator.validate_service_registration(service_name, port)
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
