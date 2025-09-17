#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

# Define the high-confidence fuzzy matches to rename
fuzzy_renames = [
    ('zmart-risk-management.mdc', 'zmart_risk_management.mdc'),
    ('zmart-technical-analysis.mdc', 'zmart_technical_analysis.mdc'),
    ('zmart-alert-system.mdc', 'zmart_alert_system.mdc'),
    ('zmart-machine-learning.mdc', 'zmart_machine_learning.mdc'),
    ('zmart-data-warehouse.mdc', 'zmart_data_warehouse.mdc'),
    ('zmart-analytics.mdc', 'zmart_analytics.mdc'),
    ('kingfisher-api.mdc', 'kingfisher-ai.mdc'),
]

print('🔄 RENAMING FUZZY MATCHED MDC FILES')
print('=' * 50)

mdc_dir = Path('.cursor/rules')
successful_renames = []
failed_renames = []

for old_name, new_name in fuzzy_renames:
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
