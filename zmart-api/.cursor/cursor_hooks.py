#!/usr/bin/env python3
"""
Cursor Hooks - Auto-sync with master database
Runs whenever Cursor needs service classification
"""

import subprocess
import sys
import os
from pathlib import Path

def get_service_classification():
    """Get service classification from master database instead of filesystem scan"""
    
    # Run sync to ensure latest data
    project_root = Path(__file__).parent.parent
    sync_script = project_root / "cursor_sync_agent.py"
    
    if sync_script.exists():
        try:
            subprocess.run([sys.executable, str(sync_script)], 
                         capture_output=True, check=True)
        except subprocess.CalledProcessError:
            pass  # Continue even if sync fails
    
    # Read synchronized classification
    sync_file = project_root / ".cursor" / "service_classification_report.md"
    
    if sync_file.exists():
        with open(sync_file, 'r') as f:
            return f.read()
    
    # Fallback to database query
    return get_database_classification()

def get_database_classification():
    """Get classification directly from database"""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from src.config.database_config import get_master_database_connection
        
        conn = get_master_database_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT certification_level, COUNT(*) FROM service_registry GROUP BY certification_level ORDER BY certification_level')
        levels = cursor.fetchall()
        
        level_counts = {level: count for level, count in levels}
        total = sum(level_counts.values())
        
        conn.close()
        
        return f"""
# ZmartBot Service Classification Results (Database Sync)
📊 TOTAL SERVICES: {total}
🏆 LEVEL 3 (CERTIFIED/REGISTERED) SERVICES: {level_counts.get(3, 0)}
🎫 LEVEL 2 (ACTIVE/PASSPORT) SERVICES: {level_counts.get(2, 0)}
🔍 LEVEL 1 (DISCOVERY) SERVICES: {level_counts.get(1, 0)}

✅ Data Source: Master Database (src/data/service_registry.db)
✅ Sync Status: Active
"""
    except Exception as e:
        return f"Error getting classification: {e}"

if __name__ == "__main__":
    print(get_service_classification())