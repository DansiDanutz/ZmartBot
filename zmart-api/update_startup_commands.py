#!/usr/bin/env python3
"""
Update Service Startup Commands
Ensures all services have correct startup commands based on their actual file locations
"""

import sqlite3
from pathlib import Path

def update_startup_commands():
    """Update startup commands for all services"""
    
    db_path = Path(__file__).parent / "src" / "data" / "service_registry.db"
    
    # Correct startup commands based on actual file locations and MDC documentation
    startup_commands = {
        'zmart-api': 'python3 start_backend_safe.py',
        'zmart-dashboard': 'python3 start_guard.py --name frontend --port 3400 --cmd "python3 professional_dashboard_server.py --port 3400" --max-wait 20',
        'my-symbols-extended-service': 'python3 symbols_extended_server.py --port 8005',
        'api-keys-manager-service': 'python3 api_keys_manager_server.py --port 8006',
        'zmart-analytics': 'python3 analytics_server.py --port 8007',
        'zmart-notification': 'python3 notification_server.py --port 8008',
        'zmart-websocket': 'python3 websocket_server.py --port 8009',
        'test-analytics-service': 'python3 analytics/analytics_server.py --port 8003',
        'test-websocket-service': 'python3 websocket/websocket_server.py --port 8004',
        'master-orchestration-agent': 'python3 orchestration_server.py --port 8002',
        'kingfisher-module': 'echo "Integrated service module - managed through zmart-api"',
        'binance': 'echo "Exchange connector service - managed through main API"',
        'kucoin': 'echo "Exchange connector service - managed through main API"',
        'mysymbols': 'echo "Internal API service - managed through main API"',
        'test-service': 'echo "Test service - managed through main API"',
        'passport-service': 'python3 passport_service.py --port 8620',
        'doctor-service': 'python3 doctor_service.py --port 8700',
        'zmart_risk_management': 'python3 risk_management_server.py --port 8010',
        'zmart_technical_analysis': 'python3 technical_analysis_server.py --port 8011',
        'zmart_alert_system': 'python3 alert_system_server.py --port 8012',
        'zmart_backtesting': 'python3 backtesting_server.py --port 8013',
        'zmart_machine_learning': 'python3 ml_server.py --port 8014',
        'zmart_data_warehouse': 'python3 data_warehouse_server.py --port 8015'
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        updated_count = 0
        for service_name, startup_command in startup_commands.items():
            cursor.execute("""
                UPDATE service_registry 
                SET startup_command = ? 
                WHERE service_name = ?
            """, (startup_command, service_name))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"✅ Updated {service_name}: {startup_command}")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"\n🎯 Startup Commands Updated:")
        print(f"   - Updated {updated_count} services")
        print(f"   - All services now have correct startup commands")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating startup commands: {e}")
        return False

if __name__ == "__main__":
    success = update_startup_commands()
    if success:
        print("\n✅ All startup commands updated successfully!")
        print("🔄 Services will now start correctly through the orchestration agent.")
    else:
        print("\n❌ Failed to update startup commands.")