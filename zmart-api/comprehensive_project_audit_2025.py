#!/usr/bin/env python3
"""
🚀 ZmartBot Comprehensive Project Audit 2025
Complete functionality audit, bug detection, and attention items identification
"""

import os
import sqlite3
import glob
import subprocess
import json
import ast
from pathlib import Path
import re

class ZmartBotProjectAuditor:
    def __init__(self):
        self.base_path = "/Users/dansidanutz/Desktop/ZmartBot"
        self.issues = {
            'critical_bugs': [],
            'warnings': [],
            'attention_needed': [],
            'optimization_opportunities': [],
            'security_concerns': []
        }
        self.functionality_status = {}
        
    def audit_database_integrity(self):
        """Audit all database files for integrity and consistency"""
        print("🗄️ AUDITING DATABASE INTEGRITY")
        print("-" * 50)
        
        db_files = []
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if not d.startswith('backups')]
            for file in files:
                if file.endswith('.db'):
                    db_files.append(os.path.join(root, file))
        
        db_issues = []
        critical_dbs = ['service_registry.db', 'passport_registry.db']
        
        for db_file in db_files:
            db_name = os.path.basename(db_file)
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Check database integrity
                cursor.execute("PRAGMA integrity_check;")
                integrity = cursor.fetchone()[0]
                
                if integrity != "ok":
                    db_issues.append(f"❌ {db_name}: Integrity check failed - {integrity}")
                
                # Check for empty critical databases
                if db_name in critical_dbs:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    if not tables:
                        db_issues.append(f"⚠️ {db_name}: No tables found - database may be corrupted")
                    else:
                        for table in tables:
                            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                            count = cursor.fetchone()[0]
                            if count == 0 and db_name == 'service_registry.db' and table[0] == 'service_registry':
                                db_issues.append(f"🚨 {db_name}: service_registry table is empty!")
                
                conn.close()
                
            except Exception as e:
                db_issues.append(f"❌ {db_name}: Database error - {str(e)}")
        
        if db_issues:
            self.issues['critical_bugs'].extend(db_issues)
            print(f"Found {len(db_issues)} database issues:")
            for issue in db_issues:
                print(f"  {issue}")
        else:
            print("✅ All databases passed integrity checks")
            
        return len(db_issues)
    
    def audit_python_syntax_errors(self):
        """Check all Python files for syntax errors"""
        print("\n🐍 AUDITING PYTHON SYNTAX")
        print("-" * 50)
        
        python_files = []
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if not d.startswith('backups') and not d.startswith('.')]
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    python_files.append(os.path.join(root, file))
        
        syntax_errors = []
        critical_files = ['server.py', 'main.py', 'service.py', 'agent.py']
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check syntax
                ast.parse(content)
                
            except SyntaxError as e:
                filename = os.path.basename(py_file)
                severity = "🚨" if any(cf in filename for cf in critical_files) else "⚠️"
                syntax_errors.append(f"{severity} {py_file}: Syntax error at line {e.lineno} - {e.msg}")
                
            except Exception as e:
                syntax_errors.append(f"❌ {py_file}: File error - {str(e)}")
        
        if syntax_errors:
            self.issues['critical_bugs'].extend(syntax_errors)
            print(f"Found {len(syntax_errors)} Python syntax issues:")
            for error in syntax_errors[:10]:  # Show first 10
                print(f"  {error}")
            if len(syntax_errors) > 10:
                print(f"  ... and {len(syntax_errors) - 10} more issues")
        else:
            print("✅ All Python files have valid syntax")
            
        return len(syntax_errors)
    
    def audit_service_configurations(self):
        """Audit service configuration consistency"""
        print("\n⚙️ AUDITING SERVICE CONFIGURATIONS")
        print("-" * 50)
        
        config_issues = []
        
        # Check for port conflicts
        used_ports = {}
        
        # Get ports from service registry
        try:
            conn = sqlite3.connect(os.path.join(self.base_path, "zmart-api/service_registry.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT service_name, port FROM service_registry")
            for service, port in cursor.fetchall():
                if port in used_ports:
                    config_issues.append(f"🚨 Port conflict: {port} used by both {used_ports[port]} and {service}")
                else:
                    used_ports[port] = service
            conn.close()
        except Exception as e:
            config_issues.append(f"❌ Cannot read service registry: {e}")
        
        # Get ports from passport registry
        try:
            conn = sqlite3.connect(os.path.join(self.base_path, "zmart-api/data/passport_registry.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT service_name, port FROM passport_registry")
            for service, port in cursor.fetchall():
                if port in used_ports and used_ports[port] != service:
                    config_issues.append(f"🚨 Port conflict: {port} used by {used_ports[port]} (registry) and {service} (passport)")
            conn.close()
        except Exception as e:
            config_issues.append(f"⚠️ Cannot read passport registry: {e}")
        
        # Check for missing environment configurations
        env_files = []
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if not d.startswith('backups')]
            for file in files:
                if file in ['.env', '.env.example', 'config.py', 'settings.py']:
                    env_files.append(os.path.join(root, file))
        
        if not env_files:
            config_issues.append("⚠️ No environment configuration files found")
        
        if config_issues:
            self.issues['warnings'].extend(config_issues)
            print(f"Found {len(config_issues)} configuration issues:")
            for issue in config_issues:
                print(f"  {issue}")
        else:
            print("✅ Service configurations look good")
            
        return len(config_issues)
    
    def audit_missing_dependencies(self):
        """Check for missing dependencies and imports"""
        print("\n📦 AUDITING DEPENDENCIES")
        print("-" * 50)
        
        dependency_issues = []
        
        # Find requirements files
        req_files = []
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if not d.startswith('backups')]
            for file in files:
                if file in ['requirements.txt', 'Pipfile', 'pyproject.toml', 'package.json']:
                    req_files.append(os.path.join(root, file))
        
        print(f"Found {len(req_files)} dependency files:")
        for req_file in req_files:
            print(f"  📄 {req_file}")
        
        # Check for common import issues in Python files
        common_imports = ['fastapi', 'uvicorn', 'sqlite3', 'requests', 'pandas', 'numpy']
        missing_imports = []
        
        # Sample a few key Python files
        key_files = []
        for root, dirs, files in os.walk(os.path.join(self.base_path, "zmart-api")):
            dirs[:] = [d for d in dirs if not d.startswith('backups')]
            for file in files:
                if file.endswith('_server.py') or file.endswith('_service.py'):
                    key_files.append(os.path.join(root, file))
        
        for py_file in key_files[:5]:  # Check first 5 key files
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                for imp in common_imports:
                    if f"import {imp}" in content or f"from {imp}" in content:
                        # Try to import to check if available
                        try:
                            subprocess.run(['python3', '-c', f'import {imp}'], 
                                         check=True, capture_output=True, timeout=5)
                        except subprocess.CalledProcessError:
                            missing_imports.append(f"⚠️ {imp} imported in {os.path.basename(py_file)} but not available")
                        except subprocess.TimeoutExpired:
                            pass
            except Exception:
                pass
        
        if missing_imports:
            self.issues['warnings'].extend(missing_imports)
            
        if not req_files:
            dependency_issues.append("🚨 No dependency files found - this could cause deployment issues")
        
        if dependency_issues:
            self.issues['attention_needed'].extend(dependency_issues)
        
        print(f"Dependencies audit: {len(missing_imports)} missing imports, {len(dependency_issues)} general issues")
        return len(missing_imports) + len(dependency_issues)
    
    def audit_security_issues(self):
        """Check for potential security vulnerabilities"""
        print("\n🔒 AUDITING SECURITY")
        print("-" * 50)
        
        security_issues = []
        
        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\']([^"\']+)["\']',
            r'api_key\s*=\s*["\']([^"\']+)["\']',
            r'secret\s*=\s*["\']([^"\']+)["\']',
            r'token\s*=\s*["\']([^"\']+)["\']'
        ]
        
        python_files = glob.glob(os.path.join(self.base_path, "**/*.py"), recursive=True)
        
        for py_file in python_files[:20]:  # Check first 20 files
            if 'backups' in py_file:
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if len(match) > 5 and match not in ['your_password', 'your_api_key', 'secret_key']:
                            security_issues.append(f"🚨 Potential hardcoded secret in {os.path.basename(py_file)}")
            except Exception:
                pass
        
        # Check for insecure database connections
        db_files = glob.glob(os.path.join(self.base_path, "**/*.db"), recursive=True)
        world_readable = []
        
        for db_file in db_files:
            if 'backups' in db_file:
                continue
            try:
                stat_info = os.stat(db_file)
                # Check if file is world-readable
                if stat_info.st_mode & 0o044:
                    world_readable.append(f"⚠️ Database {os.path.basename(db_file)} is world-readable")
            except Exception:
                pass
        
        security_issues.extend(world_readable)
        
        if security_issues:
            self.issues['security_concerns'].extend(security_issues)
            print(f"Found {len(security_issues)} security concerns:")
            for issue in security_issues:
                print(f"  {issue}")
        else:
            print("✅ No obvious security issues found")
            
        return len(security_issues)
    
    def audit_functionality_completeness(self):
        """Check if core functionalities are complete and working"""
        print("\n🎯 AUDITING FUNCTIONALITY COMPLETENESS")
        print("-" * 50)
        
        functionality_status = {}
        
        # Core trading functionality
        trading_files = ['trading_orchestration_agent.py', 'binance_service.py', 'kucoin_service.py']
        for tf in trading_files:
            file_path = os.path.join(self.base_path, "zmart-api", tf)
            functionality_status[f"Trading: {tf}"] = "✅ Present" if os.path.exists(file_path) else "❌ Missing"
        
        # API functionality
        api_files = ['main.py', 'api_keys_manager_server.py']
        for af in api_files:
            file_path = os.path.join(self.base_path, "zmart-api", af)
            functionality_status[f"API: {af}"] = "✅ Present" if os.path.exists(file_path) else "❌ Missing"
        
        # Alert systems
        alert_files = ['messi_alerts_server.py', 'pele_alerts_server.py', 'maradona_alerts_server.py', 
                      'live_alerts_server.py', 'whale_alerts_server.py']
        for alert_file in alert_files:
            file_path = os.path.join(self.base_path, "zmart-api", alert_file)
            functionality_status[f"Alerts: {alert_file}"] = "✅ Present" if os.path.exists(file_path) else "❌ Missing"
        
        # Database functionality
        critical_dbs = ['service_registry.db', 'passport_registry.db']
        for db in critical_dbs:
            db_path = os.path.join(self.base_path, "zmart-api", db) if db == 'service_registry.db' else os.path.join(self.base_path, "zmart-api/data", db)
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
                    table_count = cursor.fetchone()[0]
                    functionality_status[f"Database: {db}"] = f"✅ Present ({table_count} tables)"
                    conn.close()
                except Exception as e:
                    functionality_status[f"Database: {db}"] = f"⚠️ Present but error: {str(e)}"
            else:
                functionality_status[f"Database: {db}"] = "❌ Missing"
        
        # Print functionality status
        missing_critical = []
        for func, status in functionality_status.items():
            print(f"  {status} {func}")
            if "❌ Missing" in status and any(critical in func for critical in ['trading_orchestration', 'service_registry', 'passport_registry']):
                missing_critical.append(f"🚨 Critical functionality missing: {func}")
        
        if missing_critical:
            self.issues['critical_bugs'].extend(missing_critical)
        
        self.functionality_status = functionality_status
        return len(missing_critical)
    
    def generate_attention_items(self):
        """Generate list of items that need immediate attention"""
        print("\n🚨 GENERATING ATTENTION ITEMS")
        print("-" * 50)
        
        attention_items = []
        
        # Check service registry health
        try:
            conn = sqlite3.connect(os.path.join(self.base_path, "zmart-api/service_registry.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM service_registry WHERE status = 'CERTIFIED'")
            certified_count = cursor.fetchone()[0]
            
            if certified_count < 5:
                attention_items.append("⚠️ Low certification rate: Only {certified_count} services are Level 3 certified")
            
            conn.close()
        except Exception:
            attention_items.append("🚨 Cannot access service registry - critical system component")
        
        # Check for outdated documentation
        claude_md_path = os.path.join(self.base_path, "zmart-api/CLAUDE.md")
        if os.path.exists(claude_md_path):
            try:
                stat_info = os.stat(claude_md_path)
                import time
                days_old = (time.time() - stat_info.st_mtime) / (24 * 3600)
                if days_old > 7:
                    attention_items.append(f"📄 CLAUDE.md is {int(days_old)} days old - may need updates")
            except Exception:
                pass
        
        # Check for running services
        common_ports = [8000, 8006, 8012, 8014, 8015, 8093, 8098, 8105, 8113]
        running_count = 0
        for port in common_ports:
            try:
                result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                      capture_output=True, text=True, timeout=2)
                if result.stdout.strip():
                    running_count += 1
            except:
                pass
        
        if running_count == 0:
            attention_items.append("🚨 No services are currently running - system appears offline")
        elif running_count < 3:
            attention_items.append(f"⚠️ Only {running_count} services running - system may be partially offline")
        
        self.issues['attention_needed'].extend(attention_items)
        
        for item in attention_items:
            print(f"  {item}")
        
        return len(attention_items)
    
    def generate_comprehensive_report(self):
        """Generate the final comprehensive audit report"""
        print(f"\n{'='*70}")
        print("🚀 ZMARTBOT COMPREHENSIVE PROJECT AUDIT REPORT 2025")
        print(f"{'='*70}")
        
        # Run all audits
        db_issues = self.audit_database_integrity()
        syntax_issues = self.audit_python_syntax_errors()
        config_issues = self.audit_service_configurations()
        dependency_issues = self.audit_missing_dependencies()
        security_issues = self.audit_security_issues()
        functionality_issues = self.audit_functionality_completeness()
        attention_items_count = self.generate_attention_items()
        
        # Calculate health scores
        total_issues = db_issues + syntax_issues + config_issues + dependency_issues + security_issues + functionality_issues
        
        # Generate overall health score
        max_possible_issues = 100  # Arbitrary baseline
        health_score = max(0, 100 - (total_issues * 5))  # Each issue reduces score by 5
        
        print(f"\n{'='*70}")
        print("🎯 AUDIT SUMMARY")
        print(f"{'='*70}")
        
        print(f"📊 ISSUE BREAKDOWN:")
        print(f"  🚨 Critical Bugs: {len(self.issues['critical_bugs'])}")
        print(f"  ⚠️ Warnings: {len(self.issues['warnings'])}")
        print(f"  👀 Attention Needed: {len(self.issues['attention_needed'])}")
        print(f"  🔒 Security Concerns: {len(self.issues['security_concerns'])}")
        print(f"  🎯 Total Issues: {total_issues}")
        
        print(f"\n🏥 SYSTEM HEALTH:")
        print(f"  📈 Health Score: {health_score:.1f}/100")
        
        health_status = "🟢 EXCELLENT" if health_score >= 90 else \
                       "🟡 GOOD" if health_score >= 70 else \
                       "🟠 NEEDS ATTENTION" if health_score >= 50 else "🔴 CRITICAL"
        
        print(f"  🎯 Status: {health_status}")
        
        print(f"\n🔧 FUNCTIONALITY STATUS:")
        working_funcs = sum(1 for status in self.functionality_status.values() if "✅" in status)
        total_funcs = len(self.functionality_status)
        print(f"  📊 Working Components: {working_funcs}/{total_funcs} ({working_funcs/total_funcs*100:.1f}%)")
        
        print(f"\n🚨 IMMEDIATE ATTENTION REQUIRED:")
        critical_items = [item for item in self.issues['critical_bugs'] + self.issues['attention_needed'] if "🚨" in item]
        if critical_items:
            for item in critical_items[:5]:  # Show top 5
                print(f"  {item}")
            if len(critical_items) > 5:
                print(f"  ... and {len(critical_items) - 5} more critical items")
        else:
            print("  ✅ No critical issues requiring immediate attention")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        if health_score < 70:
            print("  1. 🚨 Address critical bugs immediately")
            print("  2. 🔧 Fix configuration issues")
            print("  3. 🔒 Review security concerns")
        elif health_score < 90:
            print("  1. 📈 Focus on optimization opportunities")
            print("  2. 📚 Update documentation")
            print("  3. 🧹 Clean up warnings")
        else:
            print("  1. 🎉 System is in excellent condition!")
            print("  2. 📊 Monitor ongoing performance")
            print("  3. 🔄 Regular maintenance recommended")
        
        return {
            'health_score': health_score,
            'total_issues': total_issues,
            'critical_issues': len([item for item in self.issues['critical_bugs'] + self.issues['attention_needed'] if "🚨" in item]),
            'functionality_rate': working_funcs/total_funcs*100 if total_funcs > 0 else 0,
            'issues': self.issues,
            'functionality_status': self.functionality_status
        }

def main():
    auditor = ZmartBotProjectAuditor()
    report = auditor.generate_comprehensive_report()
    return report

if __name__ == "__main__":
    results = main()