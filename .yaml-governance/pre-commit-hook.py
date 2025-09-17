#!/usr/bin/env python3
"""
Pre-commit Hook for YAML Governance
Created: 2025-08-31
Purpose: Prevent YAML duplication and chaos before commits
Level: 2 (Production Ready)
Port: N/A (Git Hook)
Passport: YAML-PRECOMMIT-HOOK-L2
Owner: zmartbot-system
Status: HOOK
"""

import sys
import subprocess
import os
from pathlib import Path

def run_yaml_validation():
    """Run YAML validation before commit"""
    validator_path = Path(__file__).parent / "yaml_validator.py"
    
    try:
        result = subprocess.run([sys.executable, str(validator_path)], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ PRE-COMMIT HOOK FAILED - YAML GOVERNANCE VIOLATIONS")
            print(result.stdout)
            print(result.stderr)
            
            print("\n🛡️  COMMIT BLOCKED - Fix the following issues:")
            print("1. Remove duplicate YAML files")
            print("2. Resolve port conflicts") 
            print("3. Move YAML files to allowed locations")
            print("4. Fix content validation errors")
            
            print(f"\n💡 Run this command to see detailed issues:")
            print(f"   python3 {validator_path}")
            
            return False
        else:
            print("✅ YAML Governance validation passed")
            return True
            
    except Exception as e:
        print(f"❌ Error running YAML validation: {e}")
        return False

def check_yaml_changes():
    """Check if any YAML files are being committed"""
    try:
        # Get staged files
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True)
        
        staged_files = result.stdout.strip().split('\n')
        yaml_files = [f for f in staged_files if f.endswith('.yaml') or f.endswith('.yml')]
        
        return len(yaml_files) > 0, yaml_files
        
    except Exception as e:
        print(f"Warning: Could not check staged files: {e}")
        return True, []  # Assume YAML changes if we can't check

def main():
    """Main pre-commit hook function"""
    print("🔍 Running YAML Governance Pre-commit Hook...")
    
    # Check if any YAML files are being committed
    has_yaml_changes, yaml_files = check_yaml_changes()
    
    if not has_yaml_changes:
        print("✅ No YAML files changed, skipping validation")
        sys.exit(0)
    
    print(f"📄 Found {len(yaml_files)} YAML files in commit:")
    for yaml_file in yaml_files:
        print(f"   - {yaml_file}")
    
    # Run validation
    if run_yaml_validation():
        print("🎉 All YAML governance checks passed - commit allowed")
        sys.exit(0)
    else:
        print("🚫 YAML governance checks failed - commit blocked")
        sys.exit(1)

if __name__ == "__main__":
    main()