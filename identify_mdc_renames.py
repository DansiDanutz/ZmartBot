#!/usr/bin/env python3

import sqlite3
import os
from pathlib import Path

print('🔍 ANALYZING MDC FILE RENAMING NEEDS')
print('=' * 50)

# Get all services with passports from database
conn = sqlite3.connect('src/data/service_registry.db')
cursor = conn.cursor()
cursor.execute('SELECT service_name, port, passport_id FROM service_registry WHERE passport_id IS NOT NULL')
db_services = cursor.fetchall()
conn.close()

# Get all existing MDC files
mdc_dir = Path('.cursor/rules')
existing_mdc_files = [f.stem for f in mdc_dir.glob('*.mdc')]  # Get filenames without extension

print(f'📊 Total services with passports: {len(db_services)}')
print(f'📁 Total existing MDC files: {len(existing_mdc_files)}')
print()

# Analyze which services need MDC files renamed
services_needing_rename = []
services_with_correct_names = []
services_missing_mdc = []

for service_name, port, passport_id in db_services:
    # Check if there's an exact match
    if service_name in existing_mdc_files:
        services_with_correct_names.append(service_name)
    else:
        # Check if there's a similar MDC file that might need renaming
        found_similar = False
        for mdc_file in existing_mdc_files:
            # Check for common naming patterns
            if (service_name.lower() in mdc_file.lower() or 
                mdc_file.lower() in service_name.lower() or
                service_name.replace('_', '').replace('-', '').lower() in mdc_file.lower() or
                mdc_file.replace('_', '').replace('-', '').lower() in service_name.lower()):
                services_needing_rename.append((service_name, mdc_file))
                found_similar = True
                break
        
        if not found_similar:
            services_missing_mdc.append(service_name)

print(f'✅ Services with correctly named MDC files: {len(services_with_correct_names)}')
print(f'🔄 Services needing MDC files renamed: {len(services_needing_rename)}')
print(f'❌ Services completely missing MDC files: {len(services_missing_mdc)}')
print()

if services_needing_rename:
    print('🔄 MDC FILES THAT NEED RENAMING:')
    print('-' * 40)
    for i, (service_name, current_mdc) in enumerate(services_needing_rename, 1):
        print(f'  {i:2d}. Service: {service_name}')
        print(f'       Current MDC: {current_mdc}.mdc')
        print(f'       Should be: {service_name}.mdc')
        print()

if services_missing_mdc:
    print('❌ SERVICES COMPLETELY MISSING MDC FILES:')
    print('-' * 40)
    for i, service_name in enumerate(services_missing_mdc, 1):
        print(f'  {i:2d}. {service_name}')
    print()

if services_with_correct_names:
    print('✅ SERVICES WITH CORRECT MDC NAMES:')
    print('-' * 40)
    for i, service_name in enumerate(services_with_correct_names, 1):
        print(f'  {i:2d}. {service_name}')
    print()

# Show summary of what needs to be done
print('📋 SUMMARY OF ACTIONS NEEDED:')
print('=' * 50)
if services_needing_rename:
    print(f'🔄 Need to rename {len(services_needing_rename)} MDC files')
    print('   These files exist but have incorrect names')
if services_missing_mdc:
    print(f'❌ Need to create {len(services_missing_mdc)} new MDC files')
    print('   These services have no corresponding MDC file at all')
if not services_needing_rename and not services_missing_mdc:
    print('✅ All services have correctly named MDC files!')
