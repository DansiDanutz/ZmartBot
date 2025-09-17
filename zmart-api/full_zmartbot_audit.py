#!/usr/bin/env python3
"""
🚀 COMPLETE ZmartBot Ecosystem Audit
Scans the ENTIRE ZmartBot folder structure for all services, databases, and components
"""

import os
import sqlite3
import glob
from pathlib import Path
import json
import subprocess

def scan_directory_structure():
    """Scan the complete ZmartBot directory structure"""
    base_path = "/Users/dansidanutz/Desktop/ZmartBot"
    
    print("🔍 COMPLETE ZMARTBOT DIRECTORY SCAN")
    print("=" * 70)
    
    # Find all directories
    all_dirs = []
    for root, dirs, files in os.walk(base_path):
        # Skip hidden, backup, and venv directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   not d.startswith('__pycache__') and 
                   not d.startswith('venv') and 
                   not d.startswith('node_modules') and
                   not d.startswith('system_backups')]
        all_dirs.append(root)
    
    print(f"📁 Total directories scanned: {len(all_dirs)}")
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   not d.startswith('__pycache__') and 
                   not d.startswith('venv') and 
                   not d.startswith('node_modules') and
                   not d.startswith('system_backups')]
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                python_files.append(os.path.join(root, file))
    
    print(f"🐍 Total Python files: {len(python_files)}")
    
    # Find all MDC files
    mdc_files = []
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   not d.startswith('system_backups')]
        for file in files:
            if file.endswith('.mdc'):
                mdc_files.append(os.path.join(root, file))
    
    print(f"📄 Total MDC files: {len(mdc_files)}")
    
    # Find all databases
    db_files = []
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('system_backups')]
        for file in files:
            if file.endswith('.db'):
                db_files.append(os.path.join(root, file))
    
    print(f"🗄️ Total database files: {len(db_files)}")
    
    return {
        'directories': all_dirs,
        'python_files': python_files,
        'mdc_files': mdc_files,
        'db_files': db_files
    }

def analyze_all_databases(db_files):
    """Analyze all database files in the ZmartBot ecosystem"""
    print(f"\n🗄️ DATABASE ANALYSIS")
    print("-" * 50)
    
    database_summary = {
        'service_registries': [],
        'passport_registries': [],
        'port_registries': [],
        'other_databases': []
    }
    
    for db_file in db_files:
        db_name = os.path.basename(db_file)
        relative_path = db_file.replace("/Users/dansidanutz/Desktop/ZmartBot/", "")
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Categorize databases
            if 'service_registry' in tables:
                cursor.execute("SELECT COUNT(*) FROM service_registry")
                count = cursor.fetchone()[0]
                database_summary['service_registries'].append({
                    'file': relative_path,
                    'count': count,
                    'tables': tables
                })
            elif 'passport_registry' in tables:
                cursor.execute("SELECT COUNT(*) FROM passport_registry")
                count = cursor.fetchone()[0]
                database_summary['passport_registries'].append({
                    'file': relative_path,
                    'count': count,
                    'tables': tables
                })
            elif any('port' in table for table in tables):
                database_summary['port_registries'].append({
                    'file': relative_path,
                    'tables': tables
                })
            else:
                database_summary['other_databases'].append({
                    'file': relative_path,
                    'tables': tables
                })
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error reading {relative_path}: {e}")
    
    # Print database summary
    print(f"📊 Service Registry Databases: {len(database_summary['service_registries'])}")
    for db in database_summary['service_registries']:
        print(f"  • {db['file']} ({db['count']} services)")
    
    print(f"🎫 Passport Registry Databases: {len(database_summary['passport_registries'])}")
    for db in database_summary['passport_registries']:
        print(f"  • {db['file']} ({db['count']} passports)")
    
    print(f"🔌 Port Registry Databases: {len(database_summary['port_registries'])}")
    for db in database_summary['port_registries']:
        print(f"  • {db['file']}")
    
    print(f"💾 Other Databases: {len(database_summary['other_databases'])}")
    for db in database_summary['other_databases'][:10]:  # Show first 10
        print(f"  • {db['file']} (Tables: {', '.join(db['tables'][:3])})")
    
    return database_summary

def extract_service_names(files, file_type):
    """Extract unique service names from files"""
    service_names = set()
    
    for file_path in files:
        filename = os.path.basename(file_path)
        
        if file_type == 'python':
            # Extract service names from Python files
            if any(keyword in filename for keyword in ['server', 'service', 'agent', 'manager']):
                service_name = filename.replace('.py', '')
                service_names.add(service_name)
        elif file_type == 'mdc':
            service_name = filename.replace('.mdc', '')
            service_names.add(service_name)
    
    return service_names

def get_all_level_3_services(database_summary):
    """Get all Level 3 services from all service registries"""
    all_level_3 = []
    
    for db_info in database_summary['service_registries']:
        db_path = f"/Users/dansidanutz/Desktop/ZmartBot/{db_info['file']}"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT service_name, service_type, port, status FROM service_registry WHERE status = 'CERTIFIED'")
            rows = cursor.fetchall()
            for row in rows:
                all_level_3.append({
                    'name': row[0],
                    'type': row[1],
                    'port': row[2],
                    'status': row[3],
                    'database': db_info['file']
                })
            conn.close()
        except Exception as e:
            print(f"❌ Error reading Level 3 services from {db_info['file']}: {e}")
    
    return all_level_3

def get_all_level_2_services(database_summary):
    """Get all Level 2 services from all passport registries"""
    all_level_2 = []
    
    for db_info in database_summary['passport_registries']:
        db_path = f"/Users/dansidanutz/Desktop/ZmartBot/{db_info['file']}"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT service_name, service_type, port, status FROM passport_registry WHERE status = 'ACTIVE'")
            rows = cursor.fetchall()
            for row in rows:
                all_level_2.append({
                    'name': row[0],
                    'type': row[1],
                    'port': row[2],
                    'status': row[3],
                    'database': db_info['file']
                })
            conn.close()
        except Exception as e:
            print(f"❌ Error reading Level 2 services from {db_info['file']}: {e}")
    
    return all_level_2

def check_running_services():
    """Check which services are actually running"""
    print(f"\n🏃 RUNNING SERVICES CHECK")
    print("-" * 50)
    
    # Check common ports
    common_ports = [8000, 8006, 8012, 8014, 8015, 8016, 8017, 8018, 8087, 8093, 8098, 8105, 8113]
    running_services = []
    
    for port in common_ports:
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True, timeout=5)
            if result.stdout.strip():
                running_services.append(port)
        except:
            pass
    
    print(f"✅ Services running on ports: {running_services}")
    return running_services

def main():
    print("🚀 COMPLETE ZMARTBOT ECOSYSTEM AUDIT")
    print("=" * 70)
    print("📋 Scanning ENTIRE ZmartBot folder structure...")
    print("=" * 70)
    
    # Scan directory structure
    scan_results = scan_directory_structure()
    
    # Analyze databases
    database_summary = analyze_all_databases(scan_results['db_files'])
    
    # Get service names
    python_services = extract_service_names(scan_results['python_files'], 'python')
    mdc_services = extract_service_names(scan_results['mdc_files'], 'mdc')
    
    # Get certified services
    level_3_services = get_all_level_3_services(database_summary)
    level_2_services = get_all_level_2_services(database_summary)
    
    # Check running services
    running_services = check_running_services()
    
    # Calculate Level 1 services
    all_service_names = python_services.union(mdc_services)
    level_3_names = {service['name'] for service in level_3_services}
    level_2_names = {service['name'] for service in level_2_services}
    level_1_names = all_service_names - level_3_names - level_2_names
    
    print(f"\n{'='*70}")
    print("🎯 COMPLETE ECOSYSTEM SUMMARY")
    print(f"{'='*70}")
    
    print(f"📁 Directory Structure:")
    print(f"  • Total Directories: {len(scan_results['directories'])}")
    print(f"  • Python Files: {len(scan_results['python_files'])}")
    print(f"  • MDC Files: {len(scan_results['mdc_files'])}")
    print(f"  • Database Files: {len(scan_results['db_files'])}")
    
    print(f"\n🗄️ Database Summary:")
    print(f"  • Service Registries: {len(database_summary['service_registries'])}")
    print(f"  • Passport Registries: {len(database_summary['passport_registries'])}")
    print(f"  • Port Registries: {len(database_summary['port_registries'])}")
    print(f"  • Other Databases: {len(database_summary['other_databases'])}")
    
    print(f"\n📊 SERVICE LEVEL SUMMARY:")
    total_services = len(level_1_names) + len(level_2_services) + len(level_3_services)
    print(f"🎯 TOTAL SERVICES: {total_services}")
    print(f"🔍 Level 1 (Discovery): {len(level_1_names)} services")
    print(f"🎫 Level 2 (Active/Passport): {len(level_2_services)} services")
    print(f"🏆 Level 3 (Certified/Registered): {len(level_3_services)} services")
    
    print(f"\n🏆 LEVEL 3 (CERTIFIED) SERVICES:")
    for i, service in enumerate(level_3_services, 1):
        print(f"  {i:2d}. {service['name']:<20} (Port: {service['port']:<4}, Type: {service['type']}, DB: {os.path.basename(service['database'])})")
    
    print(f"\n🎫 LEVEL 2 (ACTIVE/PASSPORT) SERVICES:")
    for i, service in enumerate(level_2_services, 1):
        print(f"  {i:2d}. {service['name']:<20} (Port: {service['port']:<4}, Type: {service['type']}, DB: {os.path.basename(service['database'])})")
    
    print(f"\n🏃 RUNTIME STATUS:")
    print(f"  • Services Running: {len(running_services)} on ports {running_services}")
    
    print(f"\n🎯 ECOSYSTEM HEALTH:")
    health_score = ((len(level_3_services) * 3) + (len(level_2_services) * 2) + (len(level_1_names) * 1)) / total_services if total_services > 0 else 0
    print(f"  • Health Score: {health_score:.2f}/3.00")
    print(f"  • Certification Rate: {(len(level_3_services)/total_services*100):.1f}%")
    print(f"  • Active Rate: {((len(level_2_services)+len(level_3_services))/total_services*100):.1f}%")
    
    return {
        'total_services': total_services,
        'level_1': len(level_1_names),
        'level_2': len(level_2_services),
        'level_3': len(level_3_services),
        'databases': len(scan_results['db_files']),
        'running_services': len(running_services),
        'health_score': health_score
    }

if __name__ == "__main__":
    results = main()