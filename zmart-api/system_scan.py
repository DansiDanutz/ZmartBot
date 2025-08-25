#!/usr/bin/env python3
"""
System Scanner for ZmartBot - Identifies Key Services and Scripts for MDC Documentation
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class SystemScanner:
    """Comprehensive system scanner for ZmartBot services and scripts"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.scan_results = {
            "critical_services": [],
            "core_scripts": [],
            "orchestration_components": [],
            "monitoring_services": [],
            "data_services": [],
            "api_services": [],
            "security_components": [],
            "database_services": [],
            "frontend_components": [],
            "utility_scripts": []
        }
        
    def scan_critical_services(self):
        """Scan for critical system services"""
        critical_patterns = [
            # Core API Services
            {"pattern": r"class.*Service.*:", "category": "api_services", "priority": "critical"},
            {"pattern": r"def main\(\):", "category": "core_scripts", "priority": "critical"},
            {"pattern": r"\.sh$", "category": "orchestration_components", "priority": "critical"},
            {"pattern": r"orchestration", "category": "orchestration_components", "priority": "critical"},
            {"pattern": r"monitoring", "category": "monitoring_services", "priority": "high"},
            {"pattern": r"database", "category": "database_services", "priority": "high"},
            {"pattern": r"security", "category": "security_components", "priority": "high"},
            {"pattern": r"dashboard", "category": "frontend_components", "priority": "medium"},
            {"pattern": r"test_.*\.py", "category": "utility_scripts", "priority": "low"}
        ]
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            if any(skip in root for skip in ['.git', 'node_modules', 'venv', '__pycache__', '.vscode']):
                continue
                
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.project_root)
                
                # Analyze file content
                if file.endswith('.py') or file.endswith('.sh'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern_info in critical_patterns:
                            if re.search(pattern_info["pattern"], content, re.IGNORECASE):
                                self.scan_results[pattern_info["category"]].append({
                                    "file": str(relative_path),
                                    "full_path": str(file_path),
                                    "priority": pattern_info["priority"],
                                    "size": len(content),
                                    "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                                })
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    
    def scan_startup_scripts(self):
        """Scan for startup and orchestration scripts"""
        startup_patterns = [
            "START_ZMARTBOT.sh",
            "STOP_ZMARTBOT.sh", 
            "start_zmartbot",
            "stop_zmartbot",
            "orchestration",
            "master_control",
            "health_check"
        ]
        
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if any(pattern.lower() in file.lower() for pattern in startup_patterns):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.project_root)
                    
                    self.scan_results["orchestration_components"].append({
                        "file": str(relative_path),
                        "full_path": str(file_path),
                        "priority": "critical",
                        "type": "startup_script",
                        "size": file_path.stat().st_size,
                        "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
    
    def scan_api_services(self):
        """Scan for API services and endpoints"""
        api_patterns = [
            r"class.*Service.*:",
            r"@app\.route",
            r"@router\.",
            r"FastAPI",
            r"Flask",
            r"api/v1",
            r"endpoint"
        ]
        
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.project_root)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in api_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
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
                        print(f"Error reading {file_path}: {e}")
    
    def scan_database_services(self):
        """Scan for database-related services"""
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
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.project_root)
                
                if any(re.search(pattern, str(file_path), re.IGNORECASE) for pattern in db_patterns):
                    self.scan_results["database_services"].append({
                        "file": str(relative_path),
                        "full_path": str(file_path),
                        "priority": "high",
                        "type": "database_service",
                        "size": file_path.stat().st_size,
                        "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
    
    def scan_monitoring_services(self):
        """Scan for monitoring and health check services"""
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
            for file in files:
                if file.endswith('.py') or file.endswith('.sh'):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.project_root)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in monitoring_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
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
                        print(f"Error reading {file_path}: {e}")
    
    def scan_security_components(self):
        """Scan for security-related components"""
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
            for file in files:
                if file.endswith('.py') or file.endswith('.sh') or file.endswith('.toml'):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.project_root)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in security_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
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
                        print(f"Error reading {file_path}: {e}")
    
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
                "critical_components": len(self.scan_results["critical_services"]) + len(self.scan_results["orchestration_components"]),
                "high_priority_components": len(self.scan_results["api_services"]) + len(self.scan_results["database_services"]) + len(self.scan_results["monitoring_services"]),
                "security_components": len(self.scan_results["security_components"]),
                "frontend_components": len(self.scan_results["frontend_components"])
            },
            "mdc_priorities": self.generate_mdc_priorities(),
            "detailed_results": self.scan_results
        }
        
        return report

def main():
    """Main entry point for system scanner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="System Scanner for ZmartBot MDC Documentation")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output", default="system_scan_report.json", help="Output file for scan report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("🔍 Scanning ZmartBot system for MDC documentation requirements...")
    
    scanner = SystemScanner(args.project_root)
    
    # Run all scans
    print("📊 Scanning critical services...")
    scanner.scan_critical_services()
    
    print("🚀 Scanning startup scripts...")
    scanner.scan_startup_scripts()
    
    print("🔌 Scanning API services...")
    scanner.scan_api_services()
    
    print("🗄️ Scanning database services...")
    scanner.scan_database_services()
    
    print("📈 Scanning monitoring services...")
    scanner.scan_monitoring_services()
    
    print("🔒 Scanning security components...")
    scanner.scan_security_components()
    
    # Generate report
    print("📋 Generating comprehensive report...")
    report = scanner.generate_report()
    
    # Save report
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Scan complete! Report saved to: {args.output}")
    
    # Print summary
    print("\n📊 SCAN SUMMARY:")
    print(f"Total components found: {report['summary']['total_files_scanned']}")
    print(f"Critical components: {report['summary']['critical_components']}")
    print(f"High priority components: {report['summary']['high_priority_components']}")
    print(f"Security components: {report['summary']['security_components']}")
    
    print("\n🎯 MDC DOCUMENTATION PRIORITIES:")
    for priority, items in report['mdc_priorities'].items():
        print(f"{priority.upper()}: {len(items)} components")
        if args.verbose and items:
            for item in items[:5]:  # Show first 5 items
                print(f"  - {item['file']} ({item['category']})")
            if len(items) > 5:
                print(f"  ... and {len(items) - 5} more")

if __name__ == "__main__":
    main()
