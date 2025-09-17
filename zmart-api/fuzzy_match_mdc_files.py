#!/usr/bin/env python3

import sqlite3
import os
from pathlib import Path
from difflib import SequenceMatcher

def similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

print('🔍 FUZZY MATCHING MDC FILES TO MISSING SERVICES')
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

# Find services that are missing MDC files (exact match)
missing_services = []
for service_name, port, passport_id in db_services:
    if service_name not in existing_mdc_files:
        missing_services.append(service_name)

print(f'❌ Services missing exact MDC matches: {len(missing_services)}')
print()

# For each missing service, find the closest MDC file
print('🎯 FUZZY MATCHES (similarity > 0.6):')
print('-' * 60)

for missing_service in missing_services:
    best_matches = []
    
    for mdc_file in existing_mdc_files:
        sim = similarity(missing_service, mdc_file)
        if sim > 0.6:  # Only show matches with >60% similarity
            best_matches.append((mdc_file, sim))
    
    # Sort by similarity (highest first)
    best_matches.sort(key=lambda x: x[1], reverse=True)
    
    if best_matches:
        print(f'\n🔍 {missing_service}:')
        for mdc_file, sim in best_matches[:3]:  # Show top 3 matches
            print(f'   → {mdc_file} (similarity: {sim:.2f})')
    else:
        print(f'\n❌ {missing_service}: No close matches found')

print('\n' + '=' * 60)
print('💡 SUGGESTED RENAMES:')
print('-' * 60)

# Suggest renames for high-confidence matches
for missing_service in missing_services:
    best_matches = []
    
    for mdc_file in existing_mdc_files:
        sim = similarity(missing_service, mdc_file)
        if sim > 0.7:  # Higher threshold for suggestions
            best_matches.append((mdc_file, sim))
    
    best_matches.sort(key=lambda x: x[1], reverse=True)
    
    if best_matches:
        best_match, sim = best_matches[0]
        print(f'{best_match}.mdc → {missing_service}.mdc (confidence: {sim:.2f})')
