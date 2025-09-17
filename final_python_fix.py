#!/usr/bin/env python3

import sqlite3
import os
from pathlib import Path

print('🔧 FINAL PYTHON FILE PATH UPDATE FOR REMAINING LEVEL 2 SERVICES')
print('=' * 60)

# Connect to the database
conn = sqlite3.connect('src/data/service_registry.db')
cursor = conn.cursor()

# Define the final mapping for the remaining 4 services
final_python_mappings = {
    'historical-data-service': 'historical_data_service.py',
    'pattern-recognition-service': 'pattern_recognition_service.py', 
    'scoring-service': 'scoring_service.py',
    'sentiment-analysis-service': 'sentiment_analysis_service.py'
}

print(f'📝 Updating Python file paths for {len(final_python_mappings)} services...')

updated_count = 0
for service_name, python_file in final_python_mappings.items():
    try:
        # Update the python_file field for this service
        cursor.execute('''
            UPDATE service_registry 
            SET python_file = ? 
            WHERE service_name = ?
        ''', (python_file, service_name))
        
        if cursor.rowcount > 0:
            print(f'✅ Updated {service_name} -> {python_file}')
            updated_count += 1
        else:
            print(f'⚠️ No record found for {service_name}')
            
    except Exception as e:
        print(f'❌ Error updating {service_name}: {e}')

# Commit changes
conn.commit()
conn.close()

print(f'\n🎉 Final Python file update completed!')
print(f'📊 Successfully updated {updated_count} out of {len(final_python_mappings)} services')
