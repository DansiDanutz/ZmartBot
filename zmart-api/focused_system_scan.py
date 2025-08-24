#!/usr/bin/env python3
"""
Focused System Scanner for ZmartBot - Identifies Key Services and Scripts for MDC Documentation
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class FocusedSystemScanner:
    """Focused system scanner for ZmartBot key services and scripts"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.scan_results = {
            "critical_orchestration": [],
            "core_services": [],
            "api_services": [],
            "database_services": [],
            "monitoring_services": [],
            "security_components": [],
            "frontend_components": [],
            "utility_scripts": []
        }
        
        # Directories to exclude
        self.exclude_dirs = {
            '.git', 'node_modules', 'venv', '__pycache__', '.vscode', 
            'grok_x_env', 'site-packages', 'backups', 'legacy_backend_backup',
            'zmart-api_old_20250822_230656', 'Documentation/complete-trading-platform-package'
        }
        
    def should_scan_file(self, file_path: Path) -> bool:
        """Check if file should be scanned"""
        # Skip excluded directories
        for exclude_dir in self.exclude_dirs:
            if exclude_dir in str(file_path):
                return False
        
        # Only scan specific file types
        if file_path.suffix not in ['.py', '.sh', '.js', '.jsx', '.ts', '.tsx', '.md', '.toml', '.yml', '.yaml']:
            return False
            
        # Skip certain file patterns
        skip_patterns = [
            'test_', 'backup', 'old_', 'legacy_', 'temp_', 'tmp_',
            'node_modules', 'venv', '__pycache__', '.git'
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path):
                return False
                
        return True
    
    def scan_critical_orchestration(self):
        """Scan for critical orchestration components"""
        critical_files = [
            "START_ZMARTBOT.sh",
            "STOP_ZMARTBOT.sh",
            "start_zmartbot_official.sh",
            "stop_zmartbot_official.sh",
            "zmartbot_master_control.py",
            "health_check_and_orchestration.py",
            "orchestration_agent.py",
            "master_orchestration_agent.py"
        ]
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if not self.should_scan_file(file_path):
                    continue
                    
                if any(critical_file.lower() in file.lower() for critical_file in critical_files):
                    relative_path = file_path.relative_to(self.project_root)
                    
                    self.scan_results["critical_orchestration"].append({
                        "file": str(relative_path),
                        "full_path": str(file_path),
                        "priority": "critical",
                        "type": "orchestration_script",
                        "size": file_path.stat().st_size,
                        "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
    
    def scan_core_services(self):
        """Scan for core system services"""
        core_patterns = [
            r"class.*Service.*:",
            r"def main\(\):",
            r"FastAPI",
            r"Flask",
            r"@app\.route",
            r"@router\."
        ]
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if not self.should_scan_file(file_path):
                    continue
                    
                if file.endswith('.py'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in core_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                relative_path = file_path.relative_to(self.project_root)
                                
                                self.scan_results["core_services"].append({
                                    "file": str(relative_path),
                                    "full_path": str(file_path),
                                    "priority": "high",
                                    "type": "core_service",
                                    "size": len(content),
                                    "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                                })
                                break
                    except Exception as e:
                        continue  # Skip files with encoding issues
    
    def scan_api_services(self):
        """Scan for API services"""
        api_patterns = [
            r"api/v1",
            r"endpoint",
            r"route",
            r"service.*api",
            r"cryptometer",
            r"kucoin",
            r"binance",
            r"my_symbols"
        ]
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if not self.should_scan_file(file_path):
                    continue
                    
                if file.endswith('.py'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in api_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                relative_path = file_path.relative_to(self.project_root)
                                
                                self.scan_results["api_services"].append({
                                    "file": str(relative_path),
                                    "full_path": str(file_path),
                                    "priority": "high",
                                    "type": "api_service",
                                    "size": len(content),
                                    "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                                })
                                break
                    except Exception as e:
                        continue
    
    def scan_database_services(self):
        """Scan for database services"""
        db_patterns = [
            r"\.db$",
            r"sqlite",
            r"database",
            r"my_symbols",
            r"cryptometer",
            r"riskmetric",
            r"learning_data"
        ]
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if not self.should_scan_file(file_path):
                    continue
                    
                if any(re.search(pattern, str(file_path), re.IGNORECASE) for pattern in db_patterns):
                    relative_path = file_path.relative_to(self.project_root)
                    
                    self.scan_results["database_services"].append({
                        "file": str(relative_path),
                        "full_path": str(file_path),
                        "priority": "high",
                        "type": "database_service",
                        "size": file_path.stat().st_size,
                        "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
    
    def scan_monitoring_services(self):
        """Scan for monitoring services"""
        monitoring_patterns = [
            r"monitor",
            r"health",
            r"watchdog",
            r"performance",
            r"metrics",
            r"logging",
            r"alert"
        ]
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if not self.should_scan_file(file_path):
                    continue
                    
                if file.endswith('.py') or file.endswith('.sh'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in monitoring_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                relative_path = file_path.relative_to(self.project_root)
                                
                                self.scan_results["monitoring_services"].append({
                                    "file": str(relative_path),
                                    "full_path": str(file_path),
                                    "priority": "high",
                                    "type": "monitoring_service",
                                    "size": len(content),
                                    "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                                })
                                break
                    except Exception as e:
                        continue
    
    def scan_security_components(self):
        """Scan for security components"""
        security_patterns = [
            r"security",
            r"gitleaks",
            r"detect-secrets",
            r"encrypt",
            r"protect",
            r"auth",
            r"api_key"
        ]
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if not self.should_scan_file(file_path):
                    continue
                    
                if file.endswith('.py') or file.endswith('.sh') or file.endswith('.toml'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in security_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                relative_path = file_path.relative_to(self.project_root)
                                
                                self.scan_results["security_components"].append({
                                    "file": str(relative_path),
                                    "full_path": str(file_path),
                                    "priority": "high",
                                    "type": "security_component",
                                    "size": len(content),
                                    "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                                })
                                break
                    except Exception as e:
                        continue
    
    def generate_mdc_priorities(self):
        """Generate MDC documentation priorities"""
        mdc_priorities = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        # Process all scan results
        for category, items in self.scan_results.items():
            for item in items:
                priority = item.get("priority", "medium")
                mdc_priorities[priority].append({
                    "category": category,
                    "file": item["file"],
                    "type": item.get("type", "service"),
                    "size": item["size"]
                })
        
        return mdc_priorities
    
    def generate_report(self):
        """Generate comprehensive scan report"""
        report = {
            "scan_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "summary": {
                "total_files_scanned": sum(len(items) for items in self.scan_results.values()),
                "critical_components": len(self.scan_results["critical_orchestration"]),
                "high_priority_components": len(self.scan_results["core_services"]) + len(self.scan_results["api_services"]) + len(self.scan_results["database_services"]),
                "monitoring_components": len(self.scan_results["monitoring_services"]),
                "security_components": len(self.scan_results["security_components"])
            },
            "mdc_priorities": self.generate_mdc_priorities(),
            "detailed_results": self.scan_results
        }
        
        return report

def main():
    """Main entry point for focused system scanner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Focused System Scanner for ZmartBot MDC Documentation")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output", default="focused_scan_report.json", help="Output file for scan report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("🔍 Running focused scan of ZmartBot system for MDC documentation requirements...")
    
    scanner = FocusedSystemScanner(args.project_root)
    
    # Run focused scans
    print("🚀 Scanning critical orchestration components...")
    scanner.scan_critical_orchestration()
    
    print("🔧 Scanning core services...")
    scanner.scan_core_services()
    
    print("🔌 Scanning API services...")
    scanner.scan_api_services()
    
    print("🗄️ Scanning database services...")
    scanner.scan_database_services()
    
    print("📈 Scanning monitoring services...")
    scanner.scan_monitoring_services()
    
    print("🔒 Scanning security components...")
    scanner.scan_security_components()
    
    # Generate report
    print("📋 Generating focused scan report...")
    report = scanner.generate_report()
    
    # Save report
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Focused scan complete! Report saved to: {args.output}")
    
    # Print summary
    print("\n📊 FOCUSED SCAN SUMMARY:")
    print(f"Total components found: {report['summary']['total_files_scanned']}")
    print(f"Critical orchestration components: {report['summary']['critical_components']}")
    print(f"High priority components: {report['summary']['high_priority_components']}")
    print(f"Monitoring components: {report['summary']['monitoring_components']}")
    print(f"Security components: {report['summary']['security_components']}")
    
    print("\n🎯 MDC DOCUMENTATION PRIORITIES:")
    for priority, items in report['mdc_priorities'].items():
        print(f"{priority.upper()}: {len(items)} components")
        if args.verbose and items:
            for item in items[:10]:  # Show first 10 items
                print(f"  - {item['file']} ({item['category']})")
            if len(items) > 10:
                print(f"  ... and {len(items) - 10} more")

if __name__ == "__main__":
    main()
