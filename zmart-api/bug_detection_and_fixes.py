#!/usr/bin/env python3
"""
🔧 ZmartBot Bug Detection and Comprehensive Fix System
Identifies and fixes all implementation issues, bugs, and conflicts
"""

import os
import sqlite3
import glob
import subprocess
import json
import ast
import re
from pathlib import Path

class ZmartBotBugFixer:
    def __init__(self):
        self.base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
        self.fixes_applied = []
        self.bugs_found = []
        self.port_conflicts = {}
        
    def detect_port_conflicts(self):
        """Detect and fix port conflicts between services"""
        print("🔍 DETECTING PORT CONFLICTS")
        print("-" * 50)
        
        port_usage = {}
        conflicts = []
        
        # Check service registry
        try:
            conn = sqlite3.connect(os.path.join(self.base_path, "service_registry.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT service_name, port, status FROM service_registry")
            for service, port, status in cursor.fetchall():
                if port in port_usage:
                    conflicts.append({
                        'port': port,
                        'services': [port_usage[port], {'name': service, 'db': 'service_registry', 'status': status}],
                        'severity': 'CRITICAL'
                    })
                else:
                    port_usage[port] = {'name': service, 'db': 'service_registry', 'status': status}
            conn.close()
        except Exception as e:
            self.bugs_found.append(f"❌ Cannot access service_registry.db: {e}")
        
        # Check passport registry
        try:
            conn = sqlite3.connect(os.path.join(self.base_path, "data/passport_registry.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT service_name, port, status FROM passport_registry")
            for service, port, status in cursor.fetchall():
                if port in port_usage:
                    # Check if it's the same service with different naming
                    existing_service = port_usage[port]['name'].lower().replace('-', '_')
                    current_service = service.lower().replace('-', '_')
                    
                    if existing_service != current_service and 'alert' not in existing_service and 'alert' not in current_service:
                        conflicts.append({
                            'port': port,
                            'services': [port_usage[port], {'name': service, 'db': 'passport_registry', 'status': status}],
                            'severity': 'CRITICAL'
                        })
                    elif existing_service == current_service:
                        # Same service in both databases - this is OK
                        pass
                    else:
                        conflicts.append({
                            'port': port,
                            'services': [port_usage[port], {'name': service, 'db': 'passport_registry', 'status': status}],
                            'severity': 'WARNING'
                        })
                else:
                    port_usage[port] = {'name': service, 'db': 'passport_registry', 'status': status}
            conn.close()
        except Exception as e:
            self.bugs_found.append(f"❌ Cannot access passport_registry.db: {e}")
        
        print(f"Found {len(conflicts)} port conflicts:")
        for conflict in conflicts:
            print(f"  🚨 Port {conflict['port']}: {conflict['services'][0]['name']} vs {conflict['services'][1]['name']}")
            print(f"     ({conflict['services'][0]['db']} vs {conflict['services'][1]['db']})")
        
        return conflicts
    
    def fix_port_conflicts(self, conflicts):
        """Fix detected port conflicts by reassigning ports"""
        print(f"\n🔧 FIXING PORT CONFLICTS")
        print("-" * 50)
        
        # Port reassignment strategy
        next_available_port = 8020
        used_ports = set()
        
        # Get all currently used ports
        try:
            conn = sqlite3.connect(os.path.join(self.base_path, "service_registry.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT port FROM service_registry")
            used_ports.update(row[0] for row in cursor.fetchall())
            conn.close()
            
            conn = sqlite3.connect(os.path.join(self.base_path, "data/passport_registry.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT port FROM passport_registry")
            used_ports.update(row[0] for row in cursor.fetchall())
            conn.close()
        except Exception as e:
            print(f"❌ Error getting used ports: {e}")
            return False
        
        fixes_made = 0
        for conflict in conflicts:
            if conflict['severity'] == 'CRITICAL':
                port = conflict['port']
                services = conflict['services']
                
                # Find next available port
                while next_available_port in used_ports:
                    next_available_port += 1
                
                # Decide which service to reassign (prefer passport registry)
                service_to_reassign = None
                for service in services:
                    if service['db'] == 'passport_registry':
                        service_to_reassign = service
                        break
                
                if not service_to_reassign:
                    service_to_reassign = services[1]  # Reassign second one found
                
                try:
                    # Update the database
                    db_path = os.path.join(self.base_path, "data/passport_registry.db") if service_to_reassign['db'] == 'passport_registry' else os.path.join(self.base_path, "service_registry.db")
                    table_name = service_to_reassign['db'].replace('_registry', '').replace('service_', 'service_')
                    
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute(f"UPDATE {table_name} SET port = ? WHERE service_name = ?", 
                                 (next_available_port, service_to_reassign['name']))
                    conn.commit()
                    conn.close()
                    
                    print(f"  ✅ Reassigned {service_to_reassign['name']} from port {port} to {next_available_port}")
                    self.fixes_applied.append(f"Port conflict resolved: {service_to_reassign['name']} moved to port {next_available_port}")
                    
                    used_ports.add(next_available_port)
                    next_available_port += 1
                    fixes_made += 1
                    
                except Exception as e:
                    print(f"❌ Failed to reassign {service_to_reassign['name']}: {e}")
                    self.bugs_found.append(f"Port conflict fix failed for {service_to_reassign['name']}: {e}")
        
        return fixes_made > 0
    
    def detect_broken_imports(self):
        """Detect broken imports and missing dependencies"""
        print(f"\n🔍 DETECTING BROKEN IMPORTS")
        print("-" * 50)
        
        broken_imports = []
        
        # Check key Python files
        key_files = [
            'trading_orchestration_agent.py',
            'messi_alerts_server.py',
            'pele_alerts_server.py', 
            'maradona_alerts_server.py',
            'live_alerts_server.py',
            'whale_alerts_server.py',
            'cryptometer_service_main.py',
            'kingfisher_server.py'
        ]
        
        for file in key_files:
            file_path = os.path.join(self.base_path, file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Extract imports
                    import_lines = re.findall(r'^(?:from|import)\s+([^\s]+)', content, re.MULTILINE)
                    
                    for imp in import_lines:
                        # Check if it's a local import
                        if imp.startswith('.') or imp in ['os', 'sys', 'json', 'sqlite3', 'datetime', 'time']:
                            continue
                            
                        # Try to import it
                        try:
                            subprocess.run(['python3', '-c', f'import {imp}'], 
                                         check=True, capture_output=True, timeout=3)
                        except subprocess.CalledProcessError:
                            broken_imports.append(f"❌ {file}: Cannot import '{imp}'")
                        except subprocess.TimeoutExpired:
                            pass
                            
                except Exception as e:
                    broken_imports.append(f"❌ {file}: File read error - {e}")
            else:
                broken_imports.append(f"⚠️ Missing critical file: {file}")
        
        print(f"Found {len(broken_imports)} import issues:")
        for issue in broken_imports:
            print(f"  {issue}")
        
        return broken_imports
    
    def detect_configuration_errors(self):
        """Detect configuration inconsistencies and errors"""
        print(f"\n🔍 DETECTING CONFIGURATION ERRORS")
        print("-" * 50)
        
        config_errors = []
        
        # Check for missing environment files
        env_files = ['.env', '.env.example']
        for env_file in env_files:
            env_path = os.path.join(self.base_path, env_file)
            if not os.path.exists(env_path):
                config_errors.append(f"⚠️ Missing environment file: {env_file}")
        
        # Check service files for hardcoded values
        service_files = glob.glob(os.path.join(self.base_path, "*_server.py"))
        
        for service_file in service_files:
            try:
                with open(service_file, 'r') as f:
                    content = f.read()
                
                # Check for hardcoded localhost
                if 'localhost' in content and 'host=' not in content:
                    config_errors.append(f"⚠️ {os.path.basename(service_file)}: Hardcoded localhost found")
                
                # Check for hardcoded API keys (basic patterns)
                if re.search(r'["\'][a-zA-Z0-9]{20,}["\']', content):
                    possible_keys = re.findall(r'["\']([a-zA-Z0-9]{20,})["\']', content)
                    for key in possible_keys:
                        if len(key) > 30 and key not in ['your_api_key_here', 'placeholder']:
                            config_errors.append(f"🚨 {os.path.basename(service_file)}: Possible hardcoded API key")
                            break
                
            except Exception as e:
                config_errors.append(f"❌ {os.path.basename(service_file)}: Cannot analyze - {e}")
        
        print(f"Found {len(config_errors)} configuration issues:")
        for error in config_errors:
            print(f"  {error}")
        
        return config_errors
    
    def detect_missing_health_endpoints(self):
        """Detect services missing health check endpoints"""
        print(f"\n🔍 DETECTING MISSING HEALTH ENDPOINTS")
        print("-" * 50)
        
        missing_health = []
        
        # Check all server files for health endpoints
        server_files = glob.glob(os.path.join(self.base_path, "*_server.py"))
        
        for server_file in server_files:
            try:
                with open(server_file, 'r') as f:
                    content = f.read()
                
                # Check for health endpoint patterns
                has_health = any(pattern in content.lower() for pattern in [
                    '/health', '/ping', '/status', 'health_check', 'get_health'
                ])
                
                if not has_health:
                    service_name = os.path.basename(server_file).replace('_server.py', '')
                    missing_health.append(f"⚠️ {service_name}: Missing health endpoint")
                    
            except Exception as e:
                missing_health.append(f"❌ {os.path.basename(server_file)}: Cannot analyze - {e}")
        
        print(f"Found {len(missing_health)} services without health endpoints:")
        for issue in missing_health:
            print(f"  {issue}")
        
        return missing_health
    
    def detect_database_inconsistencies(self):
        """Detect inconsistencies between databases"""
        print(f"\n🔍 DETECTING DATABASE INCONSISTENCIES")
        print("-" * 50)
        
        inconsistencies = []
        
        # Get all services from service registry
        service_registry_services = set()
        try:
            conn = sqlite3.connect(os.path.join(self.base_path, "service_registry.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT service_name FROM service_registry")
            service_registry_services = {row[0].lower().replace('-', '_') for row in cursor.fetchall()}
            conn.close()
        except Exception as e:
            inconsistencies.append(f"❌ Cannot read service_registry.db: {e}")
        
        # Check if Level 3 services have corresponding Python files
        for service in service_registry_services:
            possible_files = [
                f"{service}.py",
                f"{service}_server.py", 
                f"{service}_service.py",
                f"{service}_main.py"
            ]
            
            has_file = False
            for possible_file in possible_files:
                if os.path.exists(os.path.join(self.base_path, possible_file)):
                    has_file = True
                    break
            
            if not has_file:
                inconsistencies.append(f"⚠️ Level 3 service '{service}' has no corresponding Python file")
        
        print(f"Found {len(inconsistencies)} database inconsistencies:")
        for issue in inconsistencies:
            print(f"  {issue}")
        
        return inconsistencies
    
    def generate_comprehensive_bug_report(self):
        """Run all bug detection and generate comprehensive report"""
        print("🔍 STARTING COMPREHENSIVE BUG DETECTION")
        print("=" * 70)
        
        # Run all detections
        port_conflicts = self.detect_port_conflicts()
        broken_imports = self.detect_broken_imports() 
        config_errors = self.detect_configuration_errors()
        missing_health = self.detect_missing_health_endpoints()
        db_inconsistencies = self.detect_database_inconsistencies()
        
        # Apply fixes
        if port_conflicts:
            self.fix_port_conflicts(port_conflicts)
        
        # Generate summary
        print(f"\n{'='*70}")
        print("🎯 COMPREHENSIVE BUG DETECTION SUMMARY")
        print(f"{'='*70}")
        
        total_issues = len(port_conflicts) + len(broken_imports) + len(config_errors) + len(missing_health) + len(db_inconsistencies)
        
        print(f"📊 ISSUES DETECTED:")
        print(f"  🚨 Port Conflicts: {len(port_conflicts)}")
        print(f"  📦 Broken Imports: {len(broken_imports)}")
        print(f"  ⚙️ Configuration Errors: {len(config_errors)}")
        print(f"  🏥 Missing Health Endpoints: {len(missing_health)}")
        print(f"  🗄️ Database Inconsistencies: {len(db_inconsistencies)}")
        print(f"  📊 Total Issues: {total_issues}")
        
        print(f"\n🔧 FIXES APPLIED:")
        if self.fixes_applied:
            for fix in self.fixes_applied:
                print(f"  ✅ {fix}")
        else:
            print("  ℹ️ No automated fixes available")
        
        print(f"\n🚨 REMAINING ISSUES REQUIRING MANUAL ATTENTION:")
        all_remaining = broken_imports + config_errors + missing_health + db_inconsistencies + self.bugs_found
        
        if all_remaining:
            critical_issues = [issue for issue in all_remaining if "🚨" in issue or "❌" in issue]
            warning_issues = [issue for issue in all_remaining if "⚠️" in issue]
            
            if critical_issues:
                print("  🚨 CRITICAL:")
                for issue in critical_issues[:10]:  # Show first 10
                    print(f"    {issue}")
                if len(critical_issues) > 10:
                    print(f"    ... and {len(critical_issues) - 10} more critical issues")
            
            if warning_issues:
                print("  ⚠️ WARNINGS:")
                for issue in warning_issues[:10]:  # Show first 10
                    print(f"    {issue}")
                if len(warning_issues) > 10:
                    print(f"    ... and {len(warning_issues) - 10} more warnings")
        else:
            print("  🎉 No remaining issues found!")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if total_issues > 10:
            print("  1. 🚨 Focus on critical issues first")
            print("  2. 🔧 Fix import and dependency issues")
            print("  3. 🏥 Add health endpoints to all services")
        elif total_issues > 5:
            print("  1. 📈 System is in good shape overall")
            print("  2. 🧹 Address remaining warnings")
            print("  3. 🔄 Regular monitoring recommended")
        else:
            print("  1. 🎉 System is in excellent condition!")
            print("  2. 📊 Continue regular maintenance")
        
        return {
            'total_issues': total_issues,
            'fixes_applied': len(self.fixes_applied),
            'port_conflicts': len(port_conflicts),
            'broken_imports': len(broken_imports),
            'config_errors': len(config_errors),
            'missing_health': len(missing_health),
            'db_inconsistencies': len(db_inconsistencies)
        }

def main():
    fixer = ZmartBotBugFixer()
    results = fixer.generate_comprehensive_bug_report()
    return results

if __name__ == "__main__":
    results = main()