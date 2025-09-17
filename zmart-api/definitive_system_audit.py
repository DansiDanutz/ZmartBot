#!/usr/bin/env python3
"""
🚀 ZmartBot Definitive System Audit Script
FINAL AUTHORITY on service levels - uses ACTUAL database schemas and exact definitions
"""

import os
import sqlite3
import glob
from pathlib import Path
import json

def main():
    print("🚀 ZMARTBOT DEFINITIVE SYSTEM AUDIT")
    print("=" * 70)
    print("📋 Using EXACT service level definitions:")
    print("  Level 1 (Discovery): MDC and/or Python file, NO port, NO passport")
    print("  Level 2 (Active/Passport): MDC + Python + PORT + PASSPORT")  
    print("  Level 3 (Registered/Certified): Level 2 + all certification requirements")
    print("=" * 70)
    
    base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
    
    # ========================================
    # LEVEL 3 (CERTIFIED/REGISTERED) SERVICES 
    # ========================================
    print("\n🏆 LEVEL 3 (CERTIFIED/REGISTERED) SERVICES")
    print("-" * 50)
    
    level_3_services = []
    try:
        # Use the correct master database path
        master_db_path = os.path.join(base_path, "src", "data", "service_registry.db")
        conn = sqlite3.connect(master_db_path)
        cursor = conn.cursor()
        
        # Use correct column names and Level 3 criteria
        cursor.execute("""
            SELECT service_name, kind, port, passport_id, python_file_path 
            FROM service_registry 
            WHERE certification_level = 3
            ORDER BY service_name
        """)
        rows = cursor.fetchall()
        
        for row in rows:
            service_name, kind, port, passport_id, python_file = row
            
            # Check if all Level 3 requirements are met
            mdc_file = os.path.join(base_path, ".cursor", "rules", f"{service_name}.mdc")
            yaml_file = os.path.join(base_path, f"{service_name}.yaml")
            
            has_mdc = os.path.exists(mdc_file)
            has_yaml = os.path.exists(yaml_file)
            has_passport = bool(passport_id)
            has_python = bool(python_file) and os.path.exists(os.path.join(base_path, python_file)) if python_file else False
            
            level_3_services.append({
                'name': service_name,
                'type': kind or 'backend',
                'port': port,
                'passport_id': passport_id,
                'python_file': python_file,
                'has_mdc': has_mdc,
                'has_yaml': has_yaml,
                'has_passport': has_passport,
                'has_python': has_python,
                'fully_compliant': has_mdc and has_yaml and has_passport
            })
        conn.close()
        
        print(f"✅ Found {len(level_3_services)} Level 3 (CERTIFIED) services:")
        
        fully_compliant = 0
        for i, service in enumerate(level_3_services, 1):
            mdc_status = "✅" if service['has_mdc'] else "❌"
            yaml_status = "✅" if service['has_yaml'] else "❌"
            passport_status = "✅" if service['has_passport'] else "❌"
            
            if service['fully_compliant']:
                fully_compliant += 1
                compliance_status = "✅ FULLY COMPLIANT"
            else:
                compliance_status = "⚠️  PARTIAL"
            
            print(f"  {i:2d}. {service['name']:<25} (Port: {service['port']:<4}, MDC: {mdc_status}, YAML: {yaml_status}, Passport: {passport_status}) {compliance_status}")
        
        print(f"\n📊 Level 3 Compliance Summary:")
        print(f"   Total Level 3 Services: {len(level_3_services)}")
        print(f"   Fully Compliant: {fully_compliant}")
        print(f"   Partial Compliance: {len(level_3_services) - fully_compliant}")
            
    except Exception as e:
        print(f"❌ Error reading service registry: {e}")
        print(f"   Tried database path: {master_db_path}")
        print(f"   Database exists: {os.path.exists(master_db_path)}")
    
    # ========================================
    # LEVEL 2 (ACTIVE/PASSPORT) SERVICES
    # ========================================  
    print(f"\n🎫 LEVEL 2 (ACTIVE/PASSPORT) SERVICES")
    print("-" * 50)
    
    level_2_services = []
    try:
        # Use the correct master database path
        master_db_path = os.path.join(base_path, "src", "data", "service_registry.db")
        conn = sqlite3.connect(master_db_path)
        cursor = conn.cursor()
        
        # Get all Level 2 services
        cursor.execute("""
            SELECT service_name, kind, port, passport_id, python_file_path 
            FROM service_registry 
            WHERE certification_level = 2
            ORDER BY service_name
        """)
        rows = cursor.fetchall()
        
        for row in rows:
            service_name, kind, port, passport_id, python_file = row
            
            # Check Level 2 requirements
            mdc_file = os.path.join(base_path, ".cursor", "rules", f"{service_name}.mdc")
            has_mdc = os.path.exists(mdc_file)
            has_passport = bool(passport_id)
            has_python = bool(python_file) and os.path.exists(os.path.join(base_path, python_file)) if python_file else False
            
            level_2_services.append({
                'name': service_name,
                'port': port,
                'passport_id': passport_id,
                'python_file': python_file,
                'has_mdc': has_mdc,
                'has_passport': has_passport,
                'has_python': has_python
            })
        conn.close()
        
        print(f"✅ Found {len(level_2_services)} Level 2 (ACTIVE) services:")
        for i, service in enumerate(level_2_services, 1):
            mdc_status = "✅" if service['has_mdc'] else "❌"
            python_status = "✅" if service['has_python'] else "❌"
            passport_status = "✅" if service['has_passport'] else "❌"
            
            print(f"  {i:2d}. {service['name']:<25} (Port: {service['port']:<4}, MDC: {mdc_status}, Python: {python_status}, Passport: {passport_status})")
            
    except Exception as e:
        print(f"❌ Error reading Level 2 services: {e}")
    
    # ========================================
    # LEVEL 1 (DISCOVERY) SERVICES
    # ========================================
    print(f"\n🔍 LEVEL 1 (DISCOVERY) SERVICES")
    print("-" * 50)
    
    # Find all MDC files
    mdc_files = []
    cursor_rules_path = os.path.join(base_path, ".cursor", "rules")
    if os.path.exists(cursor_rules_path):
        mdc_files = glob.glob(os.path.join(cursor_rules_path, "*.mdc"))
    
    # Find all Python service files
    python_files = []
    for pattern in ["*_server.py", "*_service*.py", "*_agent.py"]:
        python_files.extend(glob.glob(os.path.join(base_path, pattern)))
    
    # Also check src/services directory
    services_path = os.path.join(base_path, "src", "services")
    if os.path.exists(services_path):
        python_files.extend([f for f in glob.glob(os.path.join(services_path, "*.py")) 
                           if not f.endswith("__init__.py")])
    
    # Get all unique service names
    all_service_names = set()
    
    # Extract from MDC files
    for mdc_file in mdc_files:
        service_name = os.path.basename(mdc_file)[:-4]  # Remove .mdc
        all_service_names.add(service_name)
    
    # Extract from Python files  
    for py_file in python_files:
        service_name = os.path.basename(py_file)[:-3]  # Remove .py
        all_service_names.add(service_name)
    
    # Filter out Level 3 and Level 2 services
    level_3_names = {service['name'] for service in level_3_services}
    level_2_names = {service['name'] for service in level_2_services}
    
    level_1_services = []
    for service_name in all_service_names:
        # Skip if already classified as Level 2 or 3
        if service_name in level_3_names or service_name in level_2_names:
            continue
            
        # Check for corresponding files
        has_mdc = any(service_name in mdc_file for mdc_file in mdc_files)
        has_python = any(service_name in py_file for py_file in python_files)
        
        if has_mdc or has_python:
            level_1_services.append({
                'name': service_name,
                'has_mdc': has_mdc,
                'has_python': has_python
            })
    
    # Sort level 1 services alphabetically
    level_1_services.sort(key=lambda x: x['name'])
    
    print(f"✅ Found {len(level_1_services)} Level 1 (DISCOVERY) services:")
    
    # Show first 20 for brevity
    for i, service in enumerate(level_1_services[:20], 1):
        mdc_status = "✅" if service['has_mdc'] else "❌"  
        py_status = "✅" if service['has_python'] else "❌"
        print(f"  {i:2d}. {service['name']:<30} (MDC: {mdc_status}, Python: {py_status})")
    
    if len(level_1_services) > 20:
        print(f"  ... and {len(level_1_services) - 20} more services")
    
    # ========================================
    # FINAL SUMMARY
    # ========================================
    print(f"\n{'='*70}")
    print("🎯 DEFINITIVE SYSTEM SUMMARY")
    print(f"{'='*70}")
    
    # Get actual service counts from database
    try:
        master_db_path = os.path.join(base_path, "src", "data", "service_registry.db")
        conn = sqlite3.connect(master_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT certification_level, COUNT(*) FROM service_registry GROUP BY certification_level")
        db_levels = dict(cursor.fetchall())
        
        cursor.execute("SELECT COUNT(*) FROM service_registry")
        total_from_db = cursor.fetchone()[0]
        
        conn.close()
        
        level1_count = db_levels.get(1, 0)
        level2_count = db_levels.get(2, 0)
        level3_count = db_levels.get(3, 0)
        
    except:
        level1_count = len(level_1_services)
        level2_count = len(level_2_services) if 'level_2_services' in locals() else 0
        level3_count = len(level_3_services)
        total_from_db = level1_count + level2_count + level3_count
    
    print(f"📊 TOTAL SERVICES: {total_from_db}")
    print(f"🔍 Level 1 (Discovery):       {level1_count:3d} services")
    print(f"🎫 Level 2 (Active/Passport): {level2_count:3d} services") 
    print(f"🏆 Level 3 (Certified):       {level3_count:3d} services")
    
    print(f"\n📋 SERVICE BREAKDOWN:")
    print(f"  • Total MDC Files:           {len(mdc_files)}")
    print(f"  • Total Python Service Files: {len(python_files)}")
    print(f"  • Unique Service Names:      {len(all_service_names)}")
    
    # Check for missing components in Level 3 services
    print(f"\n🔍 LEVEL 3 SERVICE VALIDATION:")
    for service in level_3_services:
        # Check if Level 3 services have corresponding MDC and Python files
        has_matching_files = any(service['name'].lower().replace('-', '_') in py_file.lower() 
                               for py_file in python_files)
        status = "✅" if has_matching_files else "⚠️"
        print(f"  {status} {service['name']} - File validation")
    
    return {
        'level_1': len(level_1_services),
        'level_2': len(level_2_services), 
        'level_3': len(level_3_services),
        'total': total_from_db
    }

if __name__ == "__main__":
    results = main()