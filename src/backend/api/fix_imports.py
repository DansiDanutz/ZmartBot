#!/usr/bin/env python3
"""
Fix import issues in ZmartBot backend
"""

import os
import re
import glob

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix config imports
        content = re.sub(r'from config\.', 'from src.config.', content)
        content = re.sub(r'from utils\.', 'from src.utils.', content)
        content = re.sub(r'from agents\.', 'from src.agents.', content)
        content = re.sub(r'from services\.', 'from src.services.', content)
        content = re.sub(r'from routes\.', 'from src.routes.', content)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed imports in {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix imports in all Python files"""
    print("🔧 Fixing import issues in ZmartBot backend...")
    
    # Get all Python files in src directory
    src_dir = "src"
    python_files = glob.glob(f"{src_dir}/**/*.py", recursive=True)
    
    fixed_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"✅ Fixed imports in {fixed_count} files")
    print("🎉 Import fixes complete!")

if __name__ == "__main__":
    main() 