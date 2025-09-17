#!/usr/bin/env python3

import sqlite3
import os
from pathlib import Path

print('🔧 FIXING PYTHON FILE PATHS FOR LEVEL 2 SERVICES')
print('=' * 60)

# Define the mapping of service names to actual Python files
python_file_mappings = {
    'OrchestrationStart': 'master_orchestration_agent.py',
    'RegistryConsolidator': 'master_database_registry_system.py',
    'TradingStrategy': 'trading_orchestration_agent.py',
    'YAMLGovernanceService': '.yaml-governance/yaml_governance_service.py',
    'YAMLMonitoringDaemon': '.yaml-governance/yaml_governance_service.py',  # Same file
    'background-mdc-agent': 'gpt_mds_agent.py',
    'binance-worker': 'binance_worker_service.py',
    'cryptometer-service': 'cryptometer_data_types.py',
    'discovery-database-service': 'database/discovery_database_server.py',
    'explainability-service': 'explainability_service.py',
    'gpt-mds-agent': 'gpt_mds_agent.py',
    'historical-data-service': 'historical_data_service.py',
    'kingfisher-module': 'kingfisher_ai_server.py',
    'pattern-recognition-service': 'pattern_recognition_service.py',
    'professional-dashboard': 'professional_dashboard_server.py',
    'registration-service': 'registration_service.py',
    'scoring-service': 'scoring_service.py',
    'sentiment-analysis-service': 'sentiment_analysis_service.py',
    'test-analytics-service': 'test_analytics_service.py',
    'test-websocket-service': 'test_websocket_service.py',
    'trading-orchestration-agent': 'trading_orchestration_agent.py',
}

# Connect to database
db_path = 'src/data/service_registry.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f'📊 Updating Python file paths for Level 2 services...')
print()

successful_updates = []
failed_updates = []

for service_name, python_file in python_file_mappings.items():
    # Check if the Python file actually exists
    full_path = os.path.join(os.getcwd(), python_file)
    if os.path.exists(full_path):
        try:
            # Update the database
            cursor.execute("""
                UPDATE service_registry 
                SET python_file_path = ? 
                WHERE service_name = ? AND certification_level = 2
            """, (python_file, service_name))
            
            if cursor.rowcount > 0:
                successful_updates.append((service_name, python_file))
                print(f'✅ {service_name:<25} → {python_file}')
            else:
                failed_updates.append((service_name, "Service not found in database"))
                print(f'❌ {service_name:<25} → Service not found in database')
        except Exception as e:
            failed_updates.append((service_name, str(e)))
            print(f'❌ {service_name:<25} → Error: {e}')
    else:
        failed_updates.append((service_name, f"File not found: {python_file}"))
        print(f'❌ {service_name:<25} → File not found: {python_file}')

# Commit changes
conn.commit()
conn.close()

print()
print('📊 UPDATE SUMMARY:')
print(f'✅ Successful updates: {len(successful_updates)}')
print(f'❌ Failed updates: {len(failed_updates)}')

if failed_updates:
    print('\n❌ FAILED UPDATES:')
    for service_name, error in failed_updates:
        print(f'  - {service_name}: {error}')

print('\n🎉 Python file path update completed!')
