#!/usr/bin/env python3

import sqlite3
import os
import shutil
from pathlib import Path
from difflib import SequenceMatcher

def similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

print('🔧 COMPREHENSIVE MDC FILE FIXING SCRIPT')
print('=' * 60)

# Get all services with passports from database
conn = sqlite3.connect('src/data/service_registry.db')
cursor = conn.cursor()
cursor.execute('SELECT service_name, port, passport_id FROM service_registry WHERE passport_id IS NOT NULL')
db_services = cursor.fetchall()
conn.close()

# Get all existing MDC files
mdc_dir = Path('.cursor/rules')
existing_mdc_files = [f.stem for f in mdc_dir.glob('*.mdc')]

print(f'📊 Total services with passports: {len(db_services)}')
print(f'📁 Total existing MDC files: {len(existing_mdc_files)}')
print()

# Find services that are missing MDC files
missing_services = []
matched_services = []

for service_name, port, passport_id in db_services:
    mdc_file = mdc_dir / f'{service_name}.mdc'
    if mdc_file.exists():
        matched_services.append(service_name)
    else:
        missing_services.append(service_name)

print(f'✅ Services with correctly named MDC files: {len(matched_services)}')
print(f'❌ Services missing MDC files: {len(missing_services)}')
print()

# Define manual mappings for high-confidence matches
manual_mappings = [
    ('API-Manager.mdc', 'api-keys-manager-service.mdc'),
    ('ClaudeMDCUpdate.mdc', 'mdc-orchestration-agent.mdc'),
    ('ClaudeProjectInstructions.mdc', 'optimization-claude-service.mdc'),
    ('ControlUI.mdc', 'service-dashboard.mdc'),
    ('Backend.mdc', 'snapshot-service.mdc'),
    ('BackendDoctorPack.mdc', 'background-mdc-agent.mdc'),
    ('AnalyticsServer.mdc', 'grok-x-module.mdc'),
    ('ZmartBotMethodology.mdc', 'historical-data-service.mdc'),
    ('ZmartDependencies.mdc', 'market-data-service.mdc'),
    ('ZmartBuildSystem.mdc', 'pattern-recognition-service.mdc'),
    ('ZmartDockerCompose.mdc', 'sentiment-analysis-service.mdc'),
    ('ZmartBotStopScript.mdc', 'scoring-service.mdc'),
    ('ZmartBotStartScript.mdc', 'explainability-service.mdc'),
    ('commands-denylist.mdc', 'service-lifecycle-manager.mdc'),
    ('YAMLValidator.mdc', 'enhanced-mdc-monitor.mdc'),
]

# Find fuzzy matches for remaining services
remaining_missing = [s for s in missing_services if s not in [m[1].replace('.mdc', '') for m in manual_mappings]]

print('🔍 MANUAL MAPPINGS TO APPLY:')
print('-' * 40)
for old_name, new_name in manual_mappings:
    print(f'  {old_name} → {new_name}')

print(f'\n🔍 REMAINING SERVICES NEEDING FUZZY MATCHING: {len(remaining_missing)}')
print('-' * 50)

# Find fuzzy matches for remaining services
fuzzy_matches = []
for missing_service in remaining_missing:
    best_matches = []
    for mdc_file in existing_mdc_files:
        if mdc_file not in [m[0].replace('.mdc', '') for m in manual_mappings]:
            sim = similarity(missing_service, mdc_file)
            if sim > 0.6:  # Higher threshold for confidence
                best_matches.append((mdc_file, sim))
    
    if best_matches:
        best_matches.sort(key=lambda x: x[1], reverse=True)
        best_match, sim = best_matches[0]
        if sim > 0.7:  # Very high confidence
            fuzzy_matches.append((f'{best_match}.mdc', f'{missing_service}.mdc', sim))
            print(f'  {best_match}.mdc → {missing_service}.mdc (confidence: {sim:.2f})')

print(f'\n📋 SUMMARY:')
print(f'  Manual mappings: {len(manual_mappings)}')
print(f'  Fuzzy matches: {len(fuzzy_matches)}')
print(f'  Total fixes: {len(manual_mappings) + len(fuzzy_matches)}')
print(f'  Remaining missing: {len(remaining_missing) - len(fuzzy_matches)}')

# Apply the fixes
print(f'\n🔄 APPLYING FIXES...')
print('=' * 40)

successful_renames = []
failed_renames = []

# Apply manual mappings
for old_name, new_name in manual_mappings:
    old_path = mdc_dir / old_name
    new_path = mdc_dir / new_name
    
    if old_path.exists():
        try:
            shutil.move(str(old_path), str(new_path))
            successful_renames.append((old_name, new_name))
            print(f'✅ {old_name} → {new_name}')
        except Exception as e:
            failed_renames.append((old_name, new_name, str(e)))
            print(f'❌ {old_name} → {new_name}: {e}')
    else:
        failed_renames.append((old_name, new_name, 'File not found'))
        print(f'❌ {old_name} → {new_name}: File not found')

# Apply fuzzy matches
for old_name, new_name, confidence in fuzzy_matches:
    old_path = mdc_dir / old_name
    new_path = mdc_dir / new_name
    
    if old_path.exists():
        try:
            shutil.move(str(old_path), str(new_path))
            successful_renames.append((old_name, new_name))
            print(f'✅ {old_name} → {new_name} (confidence: {confidence:.2f})')
        except Exception as e:
            failed_renames.append((old_name, new_name, str(e)))
            print(f'❌ {old_name} → {new_name}: {e}')
    else:
        failed_renames.append((old_name, new_name, 'File not found'))
        print(f'❌ {old_name} → {new_name}: File not found')

print(f'\n📊 FINAL RESULTS:')
print(f'  ✅ Successful renames: {len(successful_renames)}')
print(f'  ❌ Failed renames: {len(failed_renames)}')

if failed_renames:
    print(f'\n❌ FAILED RENAMES:')
    for old_name, new_name, error in failed_renames:
        print(f'   {old_name} → {new_name}: {error}')

print(f'\n🎯 NEXT STEPS:')
remaining_after_fix = len(remaining_missing) - len(fuzzy_matches)
if remaining_after_fix > 0:
    print(f'  ⚠️  {remaining_after_fix} services still need MDC files created')
else:
    print(f'  🎉 All services now have MDC files!')
