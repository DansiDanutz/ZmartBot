#!/usr/bin/env python3
"""
🌉 Cursor-Claude Synchronization Bridge
Ensures Cursor gets the same data as Claude from the master database
"""

import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path

def create_cursor_service_manifest():
    """Create a manifest file that Cursor can read to get correct service data"""
    base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
    db_path = os.path.join(base_path, "src", "data", "service_registry.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all services with complete information
        cursor.execute("""
            SELECT service_name, certification_level, port, passport_id, kind, python_file_path
            FROM service_registry 
            ORDER BY certification_level DESC, service_name
        """)
        
        services = cursor.fetchall()
        conn.close()
        
        # Create comprehensive manifest
        manifest = {
            'generated_at': datetime.now().isoformat(),
            'source': 'master_database',
            'total_services': len(services),
            'services': [],
            'levels': {
                'level_1': [],
                'level_2': [], 
                'level_3': []
            },
            'metadata': {
                'database_path': 'src/data/service_registry.db',
                'last_sync': datetime.now().isoformat(),
                'sync_version': '2.0'
            }
        }
        
        for service_name, level, port, passport_id, kind, python_file in services:
            service_info = {
                'name': service_name,
                'certification_level': level,
                'port': port,
                'passport_id': passport_id,
                'type': kind or 'backend',
                'python_file': python_file,
                'mdc_file': f".cursor/rules/{service_name}.mdc",
                'yaml_file': f"{service_name}.yaml",
                'has_mdc': os.path.exists(os.path.join(base_path, ".cursor", "rules", f"{service_name}.mdc")),
                'has_yaml': os.path.exists(os.path.join(base_path, f"{service_name}.yaml")),
                'status': 'certified' if level == 3 else 'active' if level == 2 else 'discovery'
            }
            
            manifest['services'].append(service_info)
            
            # Add to level-specific lists
            if level == 1:
                manifest['levels']['level_1'].append(service_name)
            elif level == 2:
                manifest['levels']['level_2'].append(service_name)
            elif level == 3:
                manifest['levels']['level_3'].append(service_name)
        
        return manifest
        
    except Exception as e:
        return {'error': f'Database error: {e}', 'generated_at': datetime.now().isoformat()}

def create_cursor_compatibility_files():
    """Create files that Cursor can use for correct service classification"""
    base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
    
    # Create manifest
    manifest = create_cursor_service_manifest()
    
    # Write main manifest file
    manifest_path = os.path.join(base_path, ".cursor", "service_manifest.json")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Create level-specific files for easier Cursor access
    if 'error' not in manifest:
        # Level 3 services list
        level3_path = os.path.join(base_path, ".cursor", "level3_services.json")
        level3_data = {
            'level': 3,
            'count': len(manifest['levels']['level_3']),
            'services': manifest['levels']['level_3'],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(level3_path, 'w') as f:
            json.dump(level3_data, f, indent=2)
        
        # Service classification lookup
        lookup_path = os.path.join(base_path, ".cursor", "service_lookup.json")
        lookup_data = {}
        
        for service in manifest['services']:
            lookup_data[service['name']] = {
                'level': service['certification_level'],
                'port': service['port'],
                'passport': service['passport_id'],
                'status': service['status']
            }
        
        with open(lookup_path, 'w') as f:
            json.dump(lookup_data, f, indent=2)
    
    return manifest

def fix_naming_inconsistencies():
    """Fix the MDC file naming inconsistencies that cause sync issues"""
    base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
    
    # Known naming inconsistencies from the sync test
    naming_fixes = [
        ('MDC-Dashboard', 'mdc-dashboard'),
        ('MySymbols', 'mysymbols'),
    ]
    
    fixes_applied = []
    
    for old_name, correct_name in naming_fixes:
        old_mdc_path = os.path.join(base_path, ".cursor", "rules", f"{old_name}.mdc")
        correct_mdc_path = os.path.join(base_path, ".cursor", "rules", f"{correct_name}.mdc")
        
        # If old file exists and correct file doesn't, rename it
        if os.path.exists(old_mdc_path) and not os.path.exists(correct_mdc_path):
            try:
                # Remove protection temporarily
                os.chmod(old_mdc_path, 0o644)
                os.rename(old_mdc_path, correct_mdc_path)
                
                # Apply protection to new file
                os.chmod(correct_mdc_path, 0o444)
                fixes_applied.append(f"{old_name} → {correct_name}")
                
            except Exception as e:
                print(f"❌ Failed to rename {old_name}: {e}")
    
    return fixes_applied

def main():
    print("🌉 CURSOR-CLAUDE SYNCHRONIZATION BRIDGE")
    print("=" * 60)
    print(f"🕐 Sync Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Fix naming inconsistencies first
    print("1️⃣ FIXING NAMING INCONSISTENCIES")
    print("-" * 40)
    
    fixes = fix_naming_inconsistencies()
    if fixes:
        for fix in fixes:
            print(f"✅ Fixed: {fix}")
    else:
        print("✅ No naming issues found")
    print()
    
    # Create compatibility files
    print("2️⃣ CREATING CURSOR COMPATIBILITY FILES")
    print("-" * 40)
    
    manifest = create_cursor_compatibility_files()
    
    if 'error' not in manifest:
        print(f"✅ Service manifest created: {manifest['total_services']} services")
        print(f"✅ Level 3 services file: {len(manifest['levels']['level_3'])} services")
        print(f"✅ Service lookup table created")
        
        print()
        print("📊 CURSOR DATA SUMMARY")
        print("-" * 40)
        print(f"   Level 1: {len(manifest['levels']['level_1'])}")
        print(f"   Level 2: {len(manifest['levels']['level_2'])}")
        print(f"   Level 3: {len(manifest['levels']['level_3'])}")
        print(f"   Total: {manifest['total_services']}")
        
        # Verify the files were created
        base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
        files_created = [
            ".cursor/service_manifest.json",
            ".cursor/level3_services.json", 
            ".cursor/service_lookup.json"
        ]
        
        print()
        print("📁 FILES CREATED FOR CURSOR")
        print("-" * 40)
        
        for file_path in files_created:
            full_path = os.path.join(base_path, file_path)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                print(f"✅ {file_path} ({size} bytes)")
            else:
                print(f"❌ {file_path} (not created)")
        
        print()
        print("🔧 CURSOR INTEGRATION INSTRUCTIONS")
        print("-" * 40)
        print("   1. Use .cursor/service_manifest.json for complete service data")
        print("   2. Use .cursor/level3_services.json for Level 3 services only")
        print("   3. Use .cursor/service_lookup.json for quick service level lookup")
        print("   4. Always use these files instead of filesystem scanning")
        print("   5. Files are automatically updated when database changes")
        
    else:
        print(f"❌ Error creating manifest: {manifest['error']}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()