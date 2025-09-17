#!/usr/bin/env python3
"""
🚀 ZmartBot Comprehensive System Debug Script
Checks all service levels according to EXACT definitions:

Level 1 (Discovery): MDC and/or Python file, NO port, NO passport, NO system interaction
Level 2 (Active/Passport): MDC + Python + PORT + PASSPORT + system interaction  
Level 3 (Registered/Certified): All Level 2 + certification requirements
"""

import os
import sqlite3
import glob
from pathlib import Path
import json
from typing import Dict, List, Any

class ZmartBotSystemDebugger:
    def __init__(self):
        self.base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
        self.services = {
            'level_1_discovery': [],
            'level_2_active': [],
            'level_3_certified': []
        }
        
    def find_all_mdc_files(self) -> List[str]:
        """Find all MDC files in the system"""
        mdc_files = []
        cursor_rules_path = os.path.join(self.base_path, ".cursor", "rules")
        if os.path.exists(cursor_rules_path):
            mdc_files.extend(glob.glob(os.path.join(cursor_rules_path, "*.mdc")))
        return mdc_files
    
    def find_all_python_services(self) -> List[str]:
        """Find all Python service files"""
        python_files = []
        
        # Main directory Python files
        for file in glob.glob(os.path.join(self.base_path, "*_server.py")):
            python_files.append(file)
        for file in glob.glob(os.path.join(self.base_path, "*_service*.py")):
            python_files.append(file)
        for file in glob.glob(os.path.join(self.base_path, "*_agent.py")):
            python_files.append(file)
            
        # Services directory
        services_path = os.path.join(self.base_path, "src", "services")
        if os.path.exists(services_path):
            for file in glob.glob(os.path.join(services_path, "*.py")):
                if not file.endswith("__init__.py"):
                    python_files.append(file)
                    
        return python_files
    
    def check_service_registry_db(self) -> Dict[str, Any]:
        """Check Level 3 (CERTIFIED) services from service_registry.db"""
        certified_services = {}
        try:
            conn = sqlite3.connect(os.path.join(self.base_path, "service_registry.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT service_name, service_type, port, status FROM service_registry WHERE status = 'CERTIFIED'")
            rows = cursor.fetchall()
            for row in rows:
                certified_services[row[0]] = {
                    'service_type': row[1],
                    'port': row[2],
                    'status': row[3],
                    'level': 3
                }
            conn.close()
        except Exception as e:
            print(f"❌ Error checking service registry: {e}")
        return certified_services
    
    def check_port_assignments(self) -> Dict[str, int]:
        """Check port assignments (Level 2+ services)"""
        port_assignments = {}
        
        # Check port_registry.db if exists
        port_db_path = os.path.join(self.base_path, "zmart-api", "port_registry.db")
        if os.path.exists(port_db_path):
            try:
                conn = sqlite3.connect(port_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"🔍 Port registry tables: {tables}")
                conn.close()
            except Exception as e:
                print(f"❌ Error checking port registry: {e}")
        
        # Also check running services (alternative way to detect ports)
        # This would require additional logic to scan running processes
        
        return port_assignments
    
    def extract_service_name_from_path(self, file_path: str) -> str:
        """Extract service name from file path"""
        filename = os.path.basename(file_path)
        if filename.endswith('.mdc'):
            return filename[:-4]  # Remove .mdc
        elif filename.endswith('.py'):
            return filename[:-3]  # Remove .py
        return filename
    
    def analyze_all_services(self):
        """Comprehensive analysis of all services"""
        print("🚀 Starting ZmartBot Comprehensive System Debug")
        print("=" * 60)
        
        # Get Level 3 (CERTIFIED) services from database
        certified_services = self.check_service_registry_db()
        print(f"📊 Level 3 (CERTIFIED) Services Found: {len(certified_services)}")
        for service_name, details in certified_services.items():
            print(f"  ✅ {service_name} (Port: {details['port']}, Type: {details['service_type']})")
            self.services['level_3_certified'].append({
                'name': service_name,
                'port': details['port'],
                'type': details['service_type'],
                'has_mdc': False,  # Will update below
                'has_python': False  # Will update below
            })
        
        # Find all MDC files
        mdc_files = self.find_all_mdc_files()
        print(f"\n📄 Total MDC Files Found: {len(mdc_files)}")
        
        # Find all Python service files  
        python_files = self.find_all_python_services()
        print(f"🐍 Total Python Service Files Found: {len(python_files)}")
        
        # Analyze service levels
        all_service_names = set()
        
        # Add service names from MDC files
        for mdc_file in mdc_files:
            service_name = self.extract_service_name_from_path(mdc_file)
            all_service_names.add(service_name)
            
        # Add service names from Python files
        for py_file in python_files:
            service_name = self.extract_service_name_from_path(py_file)
            all_service_names.add(service_name)
        
        print(f"\n🔍 Total Unique Service Names Identified: {len(all_service_names)}")
        
        # Classify each service
        for service_name in all_service_names:
            has_mdc = any(service_name in mdc_file for mdc_file in mdc_files)
            has_python = any(service_name in py_file for py_file in python_files)
            is_certified = service_name in certified_services
            
            if is_certified:
                # Already added to Level 3
                # Update MDC and Python flags
                for service in self.services['level_3_certified']:
                    if service['name'] == service_name:
                        service['has_mdc'] = has_mdc
                        service['has_python'] = has_python
                        break
            elif has_mdc and has_python:
                # Potentially Level 2 (need to check for port/passport)
                # For now, classify as Level 2 if not certified
                self.services['level_2_active'].append({
                    'name': service_name,
                    'has_mdc': has_mdc,
                    'has_python': has_python,
                    'needs_port_check': True
                })
            elif has_mdc or has_python:
                # Level 1 (Discovery)
                self.services['level_1_discovery'].append({
                    'name': service_name,
                    'has_mdc': has_mdc,
                    'has_python': has_python
                })
        
        print("\n" + "=" * 60)
        print("📊 FINAL SYSTEM STATUS REPORT")
        print("=" * 60)
        
        print(f"🔍 Level 1 (Discovery): {len(self.services['level_1_discovery'])} services")
        for service in self.services['level_1_discovery']:
            mdc_status = "✅" if service['has_mdc'] else "❌"
            py_status = "✅" if service['has_python'] else "❌"
            print(f"  • {service['name']} (MDC: {mdc_status}, Python: {py_status})")
        
        print(f"\n🎫 Level 2 (Active/Passport): {len(self.services['level_2_active'])} services")
        for service in self.services['level_2_active']:
            print(f"  • {service['name']} (Needs port/passport verification)")
        
        print(f"\n🏆 Level 3 (Certified/Registered): {len(self.services['level_3_certified'])} services")
        for service in self.services['level_3_certified']:
            mdc_status = "✅" if service['has_mdc'] else "❌"
            py_status = "✅" if service['has_python'] else "❌"
            print(f"  • {service['name']} (Port: {service['port']}, MDC: {mdc_status}, Python: {py_status})")
        
        print("\n" + "=" * 60)
        print("🎯 SUMMARY")
        print("=" * 60)
        total_services = len(self.services['level_1_discovery']) + len(self.services['level_2_active']) + len(self.services['level_3_certified'])
        print(f"Total Services: {total_services}")
        print(f"Level 1 (Discovery): {len(self.services['level_1_discovery'])}")
        print(f"Level 2 (Active/Passport): {len(self.services['level_2_active'])}")
        print(f"Level 3 (Certified/Registered): {len(self.services['level_3_certified'])}")
        
        return self.services

if __name__ == "__main__":
    debugger = ZmartBotSystemDebugger()
    results = debugger.analyze_all_services()