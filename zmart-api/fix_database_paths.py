#!/usr/bin/env python3
"""
🔧 MASS DATABASE PATH FIXER
Fix all services to use the single source of truth database path
"""

import os
import re
from pathlib import Path

def fix_database_paths():
    """Fix all Python files to use correct database path"""
    
    project_root = Path("/Users/dansidanutz/Desktop/ZmartBot/zmart-api")
    
    # Files to fix (from our analysis)
    wrong_patterns = [
        r'sqlite3\.connect\("service_registry\.db"\)',
        r'sqlite3\.connect\("/Users/dansidanutz/Desktop/ZmartBot/zmart-api/service_registry\.db"\)',
        r'sqlite3\.connect\("passport_registry\.db"\)',
        r'"service_registry\.db"',
        r"'service_registry\.db'",
    ]
    
    # Correct replacement
    correct_import = "from src.config.database_config import get_master_database_connection"
    correct_connect = "get_master_database_connection()"
    
    fixed_files = []
    
    # Find all Python files
    for py_file in project_root.rglob("*.py"):
        if "src/config/database_config.py" in str(py_file):
            continue  # Skip our config file
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            needs_import = False
            
            # Fix sqlite3.connect patterns
            if 'get_master_database_connection()' in content:
                content = content.replace('get_master_database_connection()', correct_connect)
                needs_import = True
            
            if 'get_master_database_connection()' in content:
                content = content.replace('get_master_database_connection()', correct_connect)
                needs_import = True
            
            # Add import if needed and not already present
            if needs_import and correct_import not in content:
                # Add import after other imports
                lines = content.split('\n')
                import_line_idx = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_line_idx = i
                lines.insert(import_line_idx + 1, correct_import)
                content = '\n'.join(lines)
            
            # Write back if changed
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(str(py_file))
                
        except Exception as e:
            print(f"❌ Error fixing {py_file}: {e}")
    
    return fixed_files

if __name__ == "__main__":
    print("🔧 Starting mass database path fix...")
    fixed = fix_database_paths()
    print(f"✅ Fixed {len(fixed)} files:")
    for f in fixed[:10]:  # Show first 10
        print(f"   ✅ {f}")
    if len(fixed) > 10:
        print(f"   ... and {len(fixed) - 10} more files")
