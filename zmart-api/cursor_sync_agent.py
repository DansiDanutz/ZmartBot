#!/usr/bin/env python3
"""
Cursor-Claude Synchronization Agent
Ensures Cursor and Claude work with the same service data structure
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from src.config.database_config import get_master_database_connection

class CursorSyncAgent:
    """Synchronizes service classification between Cursor and Claude"""
    
    def __init__(self):
        self.master_db_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/src/data/service_registry.db"
        self.sync_file = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/.cursor/service_sync.json"
        self.claude_md = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/CLAUDE.md"
        
    def sync_cursor_with_database(self):
        """Export database service classification for Cursor to use"""
        print("🔄 Synchronizing Cursor with master database...")
        
        # Get services from master database
        conn = get_master_database_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT service_name, port, certification_level, python_file_path, 
                   passport_id, kind, status, description, created_at, updated_at
            FROM service_registry 
            ORDER BY certification_level DESC, service_name
        ''')
        
        services = cursor.fetchall()
        conn.close()
        
        # Organize by certification level
        level_1 = []
        level_2 = []
        level_3 = []
        
        for service in services:
            service_data = {
                "service_name": service[0],
                "port": service[1],
                "certification_level": service[2],
                "python_file_path": service[3],
                "passport_id": service[4],
                "kind": service[5],
                "status": service[6],
                "description": service[7],
                "created_at": service[8],
                "updated_at": service[9]
            }
            
            if service[2] == 1:
                level_1.append(service_data)
            elif service[2] == 2:
                level_2.append(service_data)
            elif service[2] == 3:
                level_3.append(service_data)
        
        # Create sync data structure
        sync_data = {
            "sync_timestamp": datetime.now().isoformat(),
            "total_services": len(services),
            "level_3_certified": len(level_3),
            "level_2_active": len(level_2),
            "level_1_discovery": len(level_1),
            "services": {
                "level_3": level_3,
                "level_2": level_2,
                "level_1": level_1
            },
            "classification_summary": {
                "🏆 LEVEL 3 (CERTIFIED/REGISTERED) SERVICES": len(level_3),
                "🎫 LEVEL 2 (ACTIVE/PASSPORT) SERVICES": len(level_2), 
                "🔍 LEVEL 1 (DISCOVERY) SERVICES": len(level_1),
                "📊 TOTAL SERVICES": len(services)
            }
        }
        
        # Ensure .cursor directory exists
        os.makedirs(os.path.dirname(self.sync_file), exist_ok=True)
        
        # Write sync file for Cursor to read
        with open(self.sync_file, 'w') as f:
            json.dump(sync_data, f, indent=2)
        
        print(f"✅ Sync file created: {self.sync_file}")
        print(f"📊 Services synchronized:")
        print(f"   Level 3: {len(level_3)} services")
        print(f"   Level 2: {len(level_2)} services") 
        print(f"   Level 1: {len(level_1)} services")
        print(f"   Total: {len(services)} services")
        
        return sync_data
    
    def create_cursor_service_classification(self):
        """Create a service classification that Cursor can read"""
        sync_data = self.sync_cursor_with_database()
        
        # Create classification report for Cursor
        classification_report = f"""
# ZmartBot Service Classification Results (Synchronized)
📊 TOTAL SERVICES: {sync_data['total_services']}

🏆 LEVEL 3 (CERTIFIED/REGISTERED) SERVICES: {sync_data['level_3_certified']}
Criteria: Level 2 + all certification requirements + YAML files
Status: All services certified with passports and YAML manifests

Services:"""
        
        for service in sync_data['services']['level_3']:
            classification_report += f"""
{service['service_name']} (Port: {service['port']}, Passport: {service['passport_id']})"""
        
        classification_report += f"""

🎫 LEVEL 2 (ACTIVE/PASSPORT) SERVICES: {sync_data['level_2_active']}
Criteria: MDC + Python + PORT + PASSPORT
Services:"""
        
        for service in sync_data['services']['level_2']:
            classification_report += f"""
{service['service_name']} (Port: {service['port']}, Passport: {service['passport_id'] or 'N/A'})"""
        
        classification_report += f"""

🔍 LEVEL 1 (DISCOVERY) SERVICES: {sync_data['level_1_discovery']}
Criteria: MDC and/or Python file, NO port, NO passport
Services:"""
        
        for service in sync_data['services']['level_1'][:10]:  # Show first 10
            classification_report += f"""
{service['service_name']} (Status: {service['status']})"""
        
        if len(sync_data['services']['level_1']) > 10:
            classification_report += f"""
... and {len(sync_data['services']['level_1']) - 10} more Level 1 services"""
        
        classification_report += f"""

📊 SYSTEM BREAKDOWN
Service Distribution: {round(sync_data['level_1_discovery']/sync_data['total_services']*100)}% Level 1, {round(sync_data['level_2_active']/sync_data['total_services']*100)}% Level 2, {round(sync_data['level_3_certified']/sync_data['total_services']*100)}% Level 3

🎯 KEY OBSERVATIONS
✅ Level 3 Services: {sync_data['level_3_certified']} services fully certified with YAML manifests
✅ Level 2 Services: {sync_data['level_2_active']} services active with passports
✅ Level 1 Services: {sync_data['level_1_discovery']} services in discovery phase
✅ Data Source: Master database (src/data/service_registry.db)
✅ Last Sync: {sync_data['sync_timestamp']}

This classification is synchronized with the master database and reflects the actual service state.
"""
        
        # Write classification report
        report_file = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/.cursor/service_classification_report.md"
        with open(report_file, 'w') as f:
            f.write(classification_report)
        
        print(f"✅ Classification report created: {report_file}")
        return classification_report
    
    def update_claude_md_with_sync_info(self):
        """Update CLAUDE.md with sync information"""
        if os.path.exists(self.claude_md):
            with open(self.claude_md, 'r') as f:
                content = f.read()
            
            # Add sync status
            sync_info = f"""
## 🔄 Cursor-Claude Synchronization

- **Last Sync**: {datetime.now().isoformat()}
- **Sync Status**: ✅ Active
- **Service Data Source**: Master Database (src/data/service_registry.db)
- **Cursor Sync File**: .cursor/service_sync.json
"""
            
            # Insert sync info after system overview
            if "## 🎯 System Overview" in content:
                content = content.replace(
                    "## 🎯 System Overview", 
                    f"## 🎯 System Overview{sync_info}"
                )
                
                with open(self.claude_md, 'w') as f:
                    f.write(content)
                print("✅ CLAUDE.md updated with sync information")

def main():
    """Main execution"""
    sync_agent = CursorSyncAgent()
    
    print("🚀 Starting Cursor-Claude Synchronization...")
    
    # Sync data structures
    sync_data = sync_agent.sync_cursor_with_database()
    
    # Create classification report for Cursor
    classification = sync_agent.create_cursor_service_classification()
    
    # Update CLAUDE.md
    sync_agent.update_claude_md_with_sync_info()
    
    print("✅ Synchronization complete!")
    print(f"📊 Cursor and Claude now share the same service data:")
    print(f"   - Total Services: {sync_data['total_services']}")
    print(f"   - Level 3: {sync_data['level_3_certified']}")
    print(f"   - Level 2: {sync_data['level_2_active']}")
    print(f"   - Level 1: {sync_data['level_1_discovery']}")

if __name__ == "__main__":
    main()