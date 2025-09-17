#!/usr/bin/env python3

import sqlite3
import os
from pathlib import Path

print('🔍 MATCHING EXISTING MDC FILES TO MISSING SERVICES')
print('=' * 60)

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

# Find services that are missing MDC files
missing_mdc_services = []
for service_name, port, passport_id in db_services:
    if service_name not in existing_mdc_files:
        missing_mdc_services.append(service_name)

print(f'❌ Services missing MDC files: {len(missing_mdc_services)}')
print()

# Now try to match existing MDC files to missing services
print('🔍 ANALYZING POTENTIAL MATCHES:')
print('=' * 40)

potential_matches = []

for missing_service in missing_mdc_services:
    print(f'\n🔍 Looking for MDC file for: {missing_service}')
    
    # Try different matching strategies
    matches = []
    
    # Strategy 1: Exact substring match
    for mdc_file in existing_mdc_files:
        if missing_service.lower() in mdc_file.lower() or mdc_file.lower() in missing_service.lower():
            matches.append(mdc_file)
    
    # Strategy 2: Word-based matching
    missing_words = missing_service.replace('-', ' ').replace('_', ' ').split()
    for mdc_file in existing_mdc_files:
        mdc_words = mdc_file.replace('-', ' ').replace('_', ' ').split()
        common_words = set(missing_words) & set(mdc_words)
        if len(common_words) >= 1:  # At least one word in common
            if mdc_file not in matches:
                matches.append(mdc_file)
    
    if matches:
        print(f'  ✅ Potential matches found: {matches}')
        potential_matches.append((missing_service, matches))
    else:
        print(f'  ❌ No obvious matches found')

print(f'\n📋 SUMMARY OF POTENTIAL MATCHES:')
print('=' * 40)
for missing_service, matches in potential_matches:
    print(f'{missing_service} → {matches}')
