#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

# Define the remaining renaming mappings
remaining_renames = [
    ('MySymbolsDatabase.mdc', 'mysymbols.mdc'),
    ('MDC-Dashboard.mdc', 'mdc-dashboard.mdc'),
    ('binance.mdc', 'binance-worker.mdc'),
    ('database-service.mdc', 'discovery-database-service.mdc'),
]

print('🔄 FIXING REMAINING MDC FILE RENAMES')
print('=' * 50)

mdc_dir = Path('.cursor/rules')
successful_renames = []
failed_renames = []

# Handle special cases
for old_name, new_name in remaining_renames:
    old_path = mdc_dir / old_name
    new_path = mdc_dir / new_name
    
    if old_path.exists():
        try:
            # For binance.mdc, we need to copy it since it's already used for 'binance' service
            if old_name == 'binance.mdc':
                shutil.copy2(old_path, new_path)
                print(f'✅ Copied: {old_name} → {new_name}')
            else:
                # Check if target already exists
                if new_path.exists():
                    print(f'⚠️  Target already exists: {new_name}')
                    continue
                    
                old_path.rename(new_path)
                print(f'✅ Renamed: {old_name} → {new_name}')
            
            successful_renames.append((old_name, new_name))
        except Exception as e:
            print(f'❌ Failed to rename {old_name} → {new_name}: {e}')
            failed_renames.append((old_name, new_name, str(e)))
    else:
        print(f'⚠️  Source file not found: {old_name}')

print()
print('📊 RENAME SUMMARY:')
print('=' * 30)
print(f'✅ Successful renames: {len(successful_renames)}')
print(f'❌ Failed renames: {len(failed_renames)}')

if successful_renames:
    print('\n✅ SUCCESSFULLY RENAMED:')
    for old_name, new_name in successful_renames:
        print(f'   {old_name} → {new_name}')

if failed_renames:
    print('\n❌ FAILED RENAMES:')
    for old_name, new_name, error in failed_renames:
        print(f'   {old_name} → {new_name}: {error}')

print('\n🎯 Next steps:')
print('   - Run the identification script again to verify all renames')
print('   - Create MDC files for the 24 services that are completely missing')
