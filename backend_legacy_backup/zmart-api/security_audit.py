#!/usr/bin/env python3
"""
Security Audit Script
Checks for exposed API keys and security vulnerabilities
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple
import stat

class SecurityAuditor:
    """Performs security audit on the codebase"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.successes = []
        
        # Patterns that indicate potential API keys
        self.api_key_patterns = [
            (r'sk-[a-zA-Z0-9]{48,}', 'OpenAI API Key'),
            (r'sk-ant-[a-zA-Z0-9\-]{50,}', 'Anthropic API Key'),
            (r'xai-[a-zA-Z0-9]{40,}', 'Grok API Key'),
            (r'[a-fA-F0-9]{64}', 'Potential Secret Key'),
            (r'[a-zA-Z0-9]{32,}:[a-zA-Z0-9]{32,}', 'Bot Token Pattern'),
            (r'Bearer\s+[a-zA-Z0-9\-_%]{50,}', 'Bearer Token'),
        ]
        
        # Files to skip
        self.skip_patterns = [
            '*.pyc', '__pycache__', '.git', 'venv', 'env',
            'node_modules', '*.log', '*.sqlite', '*.db'
        ]
    
    def check_env_file_permissions(self):
        """Check .env file permissions"""
        env_file = self.project_root / '.env'
        
        if not env_file.exists():
            self.warnings.append("⚠️ No .env file found")
            return
        
        mode = env_file.stat().st_mode
        
        # Check if file is readable/writable by others
        if mode & stat.S_IROTH:
            self.issues.append("🚨 .env file is readable by others!")
        if mode & stat.S_IWOTH:
            self.issues.append("🚨 .env file is writable by others!")
        
        # Check if file is readable/writable by group
        if mode & stat.S_IRGRP:
            self.warnings.append("⚠️ .env file is readable by group")
        if mode & stat.S_IWGRP:
            self.warnings.append("⚠️ .env file is writable by group")
        
        # Ideal permissions: 600 (owner read/write only)
        if oct(mode)[-3:] == '600':
            self.successes.append("✅ .env file has secure permissions (600)")
    
    def check_gitignore(self):
        """Verify .gitignore includes sensitive files"""
        gitignore = self.project_root.parent.parent / '.gitignore'
        
        if not gitignore.exists():
            self.issues.append("🚨 No .gitignore file found!")
            return
        
        with open(gitignore, 'r') as f:
            content = f.read()
        
        critical_patterns = [
            '.env', '*.env', 'api_keys.json', 'credentials.json',
            'secrets.json', '*.key', '*.pem'
        ]
        
        for pattern in critical_patterns:
            if pattern in content:
                self.successes.append(f"✅ {pattern} is in .gitignore")
            else:
                self.warnings.append(f"⚠️ {pattern} is not in .gitignore")
    
    def scan_for_hardcoded_keys(self):
        """Scan Python files for hardcoded API keys"""
        py_files = list(self.project_root.rglob('*.py'))
        
        for py_file in py_files:
            # Skip test files and this script
            if 'test' in py_file.name or py_file.name == 'security_audit.py':
                continue
            
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    # Skip comments and imports
                    if line.strip().startswith('#') or 'import' in line:
                        continue
                    
                    for pattern, key_type in self.api_key_patterns:
                        if re.search(pattern, line):
                            # Check if it's using environment variable
                            if 'os.getenv' in line or 'os.environ' in line:
                                continue
                            # Check if it's a placeholder
                            if 'your_' in line.lower() or 'example' in line.lower():
                                continue
                            
                            self.issues.append(
                                f"🚨 Potential {key_type} in {py_file.name}:{line_num}"
                            )
            except Exception as e:
                self.warnings.append(f"⚠️ Could not scan {py_file.name}: {e}")
    
    def check_api_key_usage(self):
        """Check if services are using secure configuration"""
        services_dir = self.project_root / 'src' / 'services'
        
        if not services_dir.exists():
            return
        
        secure_imports = [
            'from src.config.secure_config import',
            'from src.config.api_keys_manager import',
            'os.getenv',
            'os.environ'
        ]
        
        for py_file in services_dir.rglob('*.py'):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                uses_secure_config = any(imp in content for imp in secure_imports)
                
                if 'api_key' in content.lower() or 'secret' in content.lower():
                    if uses_secure_config:
                        self.successes.append(f"✅ {py_file.name} uses secure configuration")
                    else:
                        # Check if it has hardcoded keys
                        if re.search(r'api_key\s*=\s*["\'][^"\']+["\']', content):
                            self.warnings.append(f"⚠️ {py_file.name} may have hardcoded API keys")
            
            except Exception as e:
                pass
    
    def generate_report(self):
        """Generate security audit report"""
        print("\n" + "="*60)
        print("🔒 SECURITY AUDIT REPORT")
        print("="*60)
        
        if self.issues:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"  {issue}")
        
        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.successes:
            print("\n✅ PASSED CHECKS:")
            for success in self.successes[:10]:  # Show first 10 successes
                print(f"  {success}")
            if len(self.successes) > 10:
                print(f"  ... and {len(self.successes) - 10} more")
        
        # Summary
        print("\n" + "-"*60)
        print("📊 SUMMARY:")
        print(f"  Critical Issues: {len(self.issues)}")
        print(f"  Warnings: {len(self.warnings)}")
        print(f"  Passed Checks: {len(self.successes)}")
        
        # Recommendations
        print("\n📝 RECOMMENDATIONS:")
        if not self.issues and not self.warnings:
            print("  ✅ Your API key security looks good!")
        else:
            print("  1. Fix all critical issues immediately")
            print("  2. Review and address warnings")
            print("  3. Regenerate any exposed API keys")
            print("  4. Use environment variables for all sensitive data")
            print("  5. Never commit .env files to version control")
        
        print("\n" + "="*60)
        
        # Return exit code
        return 0 if not self.issues else 1

def main():
    """Run security audit"""
    auditor = SecurityAuditor()
    
    print("🔍 Starting security audit...")
    
    # Run all checks
    auditor.check_env_file_permissions()
    auditor.check_gitignore()
    auditor.scan_for_hardcoded_keys()
    auditor.check_api_key_usage()
    
    # Generate report
    exit_code = auditor.generate_report()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()