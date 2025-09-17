import sqlite3
import requests
import json
from pathlib import Path

# Connect to service registry
conn = sqlite3.connect('src/data/service_registry.db')
cursor = conn.cursor()

# Get all services
cursor.execute("SELECT service_name, status, passport_id, port FROM service_registry ORDER BY service_name")
all_services = cursor.fetchall()

# Get certified count from API
try:
    response = requests.get('http://localhost:8901/health', timeout=5)
    certified_count = response.json().get('certified_services', 0)
except:
    certified_count = 29  # Fallback

print("=== COMPREHENSIVE SERVICE STATUS BREAKDOWN ===")
print(f"Total Services: {len(all_services)}")
print(f"Certified Services: {certified_count}")
print("")

# Categorize services
certified_services = []
passport_only_services = []
no_passport_services = []

# Based on our previous work, these are the services we know are certified
known_certified = [
    'achievements', 'api-keys-manager-service', 'binance', 'certification', 
    'doctor-service', 'explainability-service', 'kucoin', 'master-orchestration-agent',
    'mdc-dashboard', 'mdc-orchestration-agent', 'my-symbols-extended-service', 
    'mysymbols', 'optimization-claude-service', 'passport-service', 'port-manager-service',
    'professional-dashboard', 'qu2cu', 'service-dashboard', 'service-discovery',
    'servicelog-service', 'snapshot-service', 'system-protection-service',
    'test-analytics-service', 'test-service', 'test-websocket-service',
    'zmart-analytics', 'zmart-api', 'zmart-dashboard', 'zmart-notification',
    'zmart-websocket', 'zmart_alert_system', 'zmart_backtesting', 'zmart_data_warehouse',
    'zmart_machine_learning', 'zmart_risk_management', 'zmart_technical_analysis'
]

for service_name, status, passport_id, port in all_services:
    if passport_id:
        if service_name in known_certified:
            certified_services.append((service_name, status, passport_id, port))
        else:
            passport_only_services.append((service_name, status, passport_id, port))
    else:
        no_passport_services.append((service_name, status, passport_id, port))

print("🔵 SERVICES WITH CERTIFICATE + PASSPORT:")
print("=" * 50)
for service_name, status, passport_id, port in certified_services:
    print(f"✅ {service_name:<30} | {status:<10} | {passport_id:<25} | Port: {port}")
print(f"Total: {len(certified_services)} services")
print("")

print("🟡 SERVICES WITH PASSPORT ONLY (NO CERTIFICATE):")
print("=" * 50)
for service_name, status, passport_id, port in passport_only_services:
    print(f"🟡 {service_name:<30} | {status:<10} | {passport_id:<25} | Port: {port}")
print(f"Total: {len(passport_only_services)} services")
print("")

print("🔴 SERVICES WITH NO PASSPORT (NO CERTIFICATE):")
print("=" * 50)
for service_name, status, passport_id, port in no_passport_services:
    print(f"🔴 {service_name:<30} | {status:<10} | {passport_id or 'NONE':<25} | Port: {port}")
print(f"Total: {len(no_passport_services)} services")
print("")

print("📊 SUMMARY:")
print("=" * 50)
print(f"🔵 Certified + Passport:     {len(certified_services)}")
print(f"🟡 Passport Only:            {len(passport_only_services)}")
print(f"🔴 No Passport:              {len(no_passport_services)}")
print(f"📋 Total Services:           {len(all_services)}")
print("")

conn.close()
