#!/usr/bin/env python3

import sqlite3
import os
from pathlib import Path

print('🔍 FINDING EXISTING MDC FILES FOR MISSING SERVICES')
print('=' * 60)

# Get the 16 services that are missing MDC files
missing_services = [
    'api-keys-manager-service',
    'enhanced-mdc-monitor', 
    'grok-x-module',
    'kingfisher-ai',
    'market-data-service',
    'optimization-claude-service',
    'service-dashboard',
    'service-lifecycle-manager',
    'snapshot-service',
    'ziva-agent',
    'zmart_alert_system',
    'zmart_analytics',
    'zmart_data_warehouse',
    'zmart_machine_learning',
    'zmart_risk_management',
    'zmart_technical_analysis'
]

# Get all existing MDC files
mdc_dir = Path('.cursor/rules')
existing_mdc_files = [f.stem for f in mdc_dir.glob('*.mdc')]

print(f'📊 Missing services: {len(missing_services)}')
print(f'📁 Existing MDC files: {len(existing_mdc_files)}')
print()

# Find potential matches
potential_matches = []

for missing_service in missing_services:
    # Look for similar names
    matches = []
    for mdc_file in existing_mdc_files:
        # Check for exact matches with different naming conventions
        if (missing_service.replace('-', '_') == mdc_file.replace('-', '_') or
            missing_service.replace('_', '-') == mdc_file.replace('_', '-') or
            missing_service.lower() == mdc_file.lower() or
            missing_service.replace('-', '') == mdc_file.replace('-', '') or
            missing_service.replace('_', '') == mdc_file.replace('_', '')):
            matches.append(mdc_file)
        
        # Check for partial matches
        elif (missing_service in mdc_file.lower() or 
              mdc_file.lower() in missing_service or
              any(word in mdc_file.lower() for word in missing_service.split('-')) or
              any(word in mdc_file.lower() for word in missing_service.split('_'))):
            matches.append(mdc_file)
    
    if matches:
        potential_matches.append((missing_service, matches))

print('🎯 POTENTIAL MDC FILE MATCHES:')
print('=' * 60)

for missing_service, matches in potential_matches:
    print(f'\n🔍 {missing_service}:')
    for i, match in enumerate(matches, 1):
        print(f'  {i}. {match}.mdc')

print(f'\n📋 SUMMARY:')
print(f'  Services with potential matches: {len(potential_matches)}')
print(f'  Services without matches: {len(missing_services) - len(potential_matches)}')
