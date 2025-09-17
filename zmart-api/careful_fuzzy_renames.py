#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

# Define the safe fuzzy matches (only rename if not already used by other services)
safe_fuzzy_renames = [
    ('RegistrationCertificate.mdc', 'registration-service.mdc'),
    ('mdc-orchestration-agent.mdc', 'trading-orchestration-agent.mdc'),
]

print('🔄 CAREFUL FUZZY RENAMING (SAFE MATCHES ONLY)')
print('=' * 50)

mdc_dir = Path('.cursor/rules')
successful_renames = []
failed_renames = []

for old_name, new_name in safe_fuzzy_renames:
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

print(f'\n📊 RESULTS:')
print(f'✅ Successful renames: {len(successful_renames)}')
print(f'❌ Failed renames: {len(failed_renames)}')

if failed_renames:
    print('\n❌ FAILED RENAMES:')
    for old_name, new_name, error in failed_renames:
        print(f'   {old_name} → {new_name}: {error}')

print('\n💡 NOTE: Some MDC files were not renamed to avoid conflicts with existing services.')
