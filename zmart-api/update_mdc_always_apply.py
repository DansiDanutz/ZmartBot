#!/usr/bin/env python3
"""
Update All MDC Files to alwaysApply: true
Updates all MDC files in .cursor/rules to ensure they are always applied
"""

import os
import re
from pathlib import Path

def update_mdc_file(file_path):
    """Update a single MDC file to set alwaysApply to true"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match the description/globs/alwaysApply section
        pattern = r'(description:\s*\n\s*globs:\s*\n\s*alwaysApply:\s*)false'
        replacement = r'\1true'
        
        # Check if the pattern exists
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
            
            # Write the updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        else:
            # If the pattern doesn't exist, add it at the end
            if 'alwaysApply:' not in content:
                new_content = content.rstrip() + '\n\ndescription:\nglobs:\nalwaysApply: true\n---\n'
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return True
            else:
                # Pattern exists but might be different, try to find and replace
                pattern2 = r'(alwaysApply:\s*)false'
                if re.search(pattern2, content):
                    new_content = re.sub(pattern2, r'\1true', content)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    return True
        
        return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Main function to update all MDC files"""
    project_root = Path(__file__).parent.parent
    mdc_dir = project_root / ".cursor" / "rules"
    
    if not mdc_dir.exists():
        print(f"MDC directory not found: {mdc_dir}")
        return 1
    
    # Find all MDC files
    mdc_files = list(mdc_dir.glob("*.mdc"))
    
    if not mdc_files:
        print("No MDC files found")
        return 1
    
    print(f"Found {len(mdc_files)} MDC files to update")
    
    updated_count = 0
    failed_count = 0
    
    for mdc_file in mdc_files:
        print(f"Processing: {mdc_file.name}")
        
        if update_mdc_file(mdc_file):
            print(f"✅ Updated: {mdc_file.name}")
            updated_count += 1
        else:
            print(f"❌ Failed: {mdc_file.name}")
            failed_count += 1
    
    print(f"\n📊 Summary:")
    print(f"✅ Successfully updated: {updated_count} files")
    print(f"❌ Failed to update: {failed_count} files")
    print(f"📁 Total files processed: {len(mdc_files)}")
    
    if failed_count == 0:
        print("🎯 All MDC files now have alwaysApply: true!")
        return 0
    else:
        print("⚠️ Some files failed to update")
        return 1

if __name__ == "__main__":
    exit(main())
