#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

# Define the renaming mappings based on the analysis
rename_mappings = [
    ('MySymbolsDatabase.mdc', 'mysymbols.mdc'),
    ('KuCoinService.mdc', 'kucoin.mdc'),
    ('binance-worker-service.mdc', 'binance.mdc'),
    ('test.mdc', 'zmart_backtesting.mdc'),
    ('PassportService.mdc', 'passport-service.mdc'),
    ('DoctorService.mdc', 'doctor-service.mdc'),
    ('SystemProtectionService.mdc', 'system-protection-service.mdc'),
    ('MDC-Dashboard.mdc', 'mdc-dashboard.mdc'),
    ('ProfessionalDashboard.mdc', 'professional-dashboard.mdc'),
    ('binance-worker-service.mdc', 'binance-worker.mdc'),
    ('CryptometerService.mdc', 'cryptometer-service.mdc'),
    ('ServiceLog.mdc', 'servicelog-service.mdc'),
    ('ServiceDiscovery.mdc', 'service-discovery.mdc'),
    ('MasterOrchestrationAgent.mdc', 'master-orchestration-agent.mdc'),
    ('CertificationService.mdc', 'certification.mdc'),
    ('GptMDSagentService.mdc', 'gpt-mds-agent.mdc'),
    ('Maradona.mdc', 'maradona-alerts.mdc'),
    ('WhaleAlerts.mdc', 'whale-alerts.mdc'),
    ('MessiAlerts.mdc', 'messi-alerts.mdc'),
    ('Pele.mdc', 'pele-alerts.mdc'),
    ('LiveAlerts.mdc', 'live-alerts.mdc'),
    ('discovery-database-service.mdc', 'database-service.mdc'),
]

print('🔄 RENAMING MDC FILES TO MATCH SERVICE NAMES')
print('=' * 50)

mdc_dir = Path('.cursor/rules')
successful_renames = []
failed_renames = []

# Handle the special case of binance-worker-service.mdc which needs to be duplicated
# since it matches both 'binance' and 'binance-worker' services
binance_original = mdc_dir / 'binance-worker-service.mdc'
if binance_original.exists():
    # First rename to binance.mdc
    binance_new = mdc_dir / 'binance.mdc'
    try:
        shutil.copy2(binance_original, binance_new)
        print(f'✅ Copied: binance-worker-service.mdc → binance.mdc')
        successful_renames.append(('binance-worker-service.mdc', 'binance.mdc'))
    except Exception as e:
        print(f'❌ Failed to copy binance-worker-service.mdc → binance.mdc: {e}')
        failed_renames.append(('binance-worker-service.mdc', 'binance.mdc', str(e)))

# Process all other renames
for old_name, new_name in rename_mappings:
    # Skip the binance case as we handled it above
    if old_name == 'binance-worker-service.mdc':
        continue
        
    old_path = mdc_dir / old_name
    new_path = mdc_dir / new_name
    
    if old_path.exists():
        try:
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
