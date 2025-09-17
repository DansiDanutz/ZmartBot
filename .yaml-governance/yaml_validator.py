#!/usr/bin/env python3
"""
YAML Governance System - Prevention of Duplication and Chaos
Created: 2025-08-31
Purpose: Validate, enforce, and prevent YAML configuration issues
Level: 2 (Production Ready)
Port: N/A (Library Component)
Passport: YAML-VALIDATOR-LIB-L2
Owner: zmartbot-system
Status: LIBRARY
"""

import os
import sys
import glob
import yaml
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ServiceYAML:
    path: str
    service_name: str
    content_hash: str
    port: Optional[int]
    service_type: str
    content: dict

class YAMLGovernanceValidator:
    """Comprehensive YAML validation and governance system"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.registry_file = self.root_dir / ".yaml-governance" / "yaml_registry.json"
        self.rules_file = self.root_dir / ".yaml-governance" / "governance_rules.yaml"
        self.allowed_locations = {
            "zmart-api/[service_name]/service.yaml",
            "zmart-api/alerts/[alert_name]/service.yaml", 
            "zmart-api/security/[security_service]/service.yaml",
            "zmart-api/infrastructure/[infra_service]/service.yaml"
        }
        
    def load_governance_rules(self) -> dict:
        """Load governance rules configuration"""
        default_rules = {
            "allowed_directories": [
                "zmart-api/*/service.yaml",
                "zmart-api/alerts/*/service.yaml",
                "zmart-api/security/*/service.yaml", 
                "zmart-api/infrastructure/*/service.yaml"
            ],
            "forbidden_directories": [
                "services/*/service.yaml",  # Legacy location
                "*/zmart_*/service.yaml",   # Incorrect naming
                "*/zmart-*/zmart-*/service.yaml"  # Nested duplication
            ],
            "required_fields": [
                "service_name", "service_type", "port", "passport_id", 
                "version", "owner", "description"
            ],
            "naming_conventions": {
                "service_name_pattern": "^[a-z0-9-]+$",
                "directory_pattern": "^[a-z0-9_]+$",
                "no_mixed_separators": True
            },
            "port_ranges": {
                "alert_services": [8014, 8025],
                "backend_services": [8100, 8200],
                "infrastructure": [8890, 8910],
                "security": [8880, 8900]
            }
        }
        
        if self.rules_file.exists():
            with open(self.rules_file, 'r') as f:
                return yaml.safe_load(f)
        return default_rules
    
    def scan_yaml_files(self) -> List[ServiceYAML]:
        """Scan all service.yaml files in the project"""
        yaml_files = []
        
        for yaml_path in glob.glob("**/service.yaml", recursive=True):
            if "node_modules" in yaml_path or ".git" in yaml_path:
                continue
                
            try:
                with open(yaml_path, 'r') as f:
                    content = yaml.safe_load(f)
                
                if not content:
                    continue
                    
                content_hash = hashlib.md5(yaml.dump(content, sort_keys=True).encode()).hexdigest()
                
                service_yaml = ServiceYAML(
                    path=yaml_path,
                    service_name=content.get('service_name', 'unknown'),
                    content_hash=content_hash,
                    port=content.get('port'),
                    service_type=content.get('service_type', 'unknown'),
                    content=content
                )
                
                yaml_files.append(service_yaml)
                
            except Exception as e:
                print(f"❌ Error reading {yaml_path}: {e}")
                
        return yaml_files
    
    def detect_duplicates(self, yaml_files: List[ServiceYAML]) -> Dict[str, List[ServiceYAML]]:
        """Detect duplicate services by name and content"""
        duplicates = {}
        
        # Group by service name
        by_name = {}
        for yaml_file in yaml_files:
            name = yaml_file.service_name
            if name not in by_name:
                by_name[name] = []
            by_name[name].append(yaml_file)
        
        # Find duplicates
        for name, files in by_name.items():
            if len(files) > 1:
                duplicates[name] = files
                
        return duplicates
    
    def detect_port_conflicts(self, yaml_files: List[ServiceYAML]) -> Dict[int, List[ServiceYAML]]:
        """Detect port conflicts"""
        by_port = {}
        for yaml_file in yaml_files:
            if yaml_file.port:
                if yaml_file.port not in by_port:
                    by_port[yaml_file.port] = []
                by_port[yaml_file.port].append(yaml_file)
        
        return {port: files for port, files in by_port.items() if len(files) > 1}
    
    def validate_location(self, yaml_path: str, rules: dict) -> Tuple[bool, str]:
        """Validate if YAML file is in allowed location"""
        path = Path(yaml_path)
        
        # Check forbidden locations
        for forbidden in rules.get("forbidden_directories", []):
            if path.match(forbidden):
                return False, f"YAML file in forbidden location: {forbidden}"
        
        # Check allowed locations
        allowed = rules.get("allowed_directories", [])
        for pattern in allowed:
            if path.match(pattern):
                return True, "Valid location"
        
        return False, f"YAML file not in any allowed location. Allowed: {allowed}"
    
    def validate_content(self, yaml_file: ServiceYAML, rules: dict) -> List[str]:
        """Validate YAML content against governance rules"""
        errors = []
        content = yaml_file.content
        
        # Check required fields
        required = rules.get("required_fields", [])
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        
        # Validate naming conventions
        naming = rules.get("naming_conventions", {})
        if "service_name_pattern" in naming:
            import re
            pattern = naming["service_name_pattern"]
            if not re.match(pattern, yaml_file.service_name):
                errors.append(f"Service name '{yaml_file.service_name}' doesn't match pattern {pattern}")
        
        # Validate port ranges
        port_ranges = rules.get("port_ranges", {})
        if yaml_file.port and yaml_file.service_type in port_ranges:
            port_range = port_ranges[yaml_file.service_type]
            if not (port_range[0] <= yaml_file.port <= port_range[1]):
                errors.append(f"Port {yaml_file.port} not in allowed range {port_range} for {yaml_file.service_type}")
        
        return errors
    
    def run_validation(self) -> dict:
        """Run comprehensive YAML validation"""
        print("🔍 Running YAML Governance Validation...")
        
        rules = self.load_governance_rules()
        yaml_files = self.scan_yaml_files()
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_yaml_files": len(yaml_files),
            "duplicates": {},
            "port_conflicts": {},
            "location_violations": [],
            "content_violations": [],
            "status": "PASSED"
        }
        
        # Detect duplicates
        duplicates = self.detect_duplicates(yaml_files)
        if duplicates:
            results["duplicates"] = {name: [f.path for f in files] for name, files in duplicates.items()}
            results["status"] = "FAILED"
        
        # Detect port conflicts  
        port_conflicts = self.detect_port_conflicts(yaml_files)
        if port_conflicts:
            results["port_conflicts"] = {port: [f.path for f in files] for port, files in port_conflicts.items()}
            results["status"] = "FAILED"
        
        # Validate locations and content
        for yaml_file in yaml_files:
            # Location validation
            location_valid, location_msg = self.validate_location(yaml_file.path, rules)
            if not location_valid:
                results["location_violations"].append({
                    "path": yaml_file.path,
                    "error": location_msg
                })
                results["status"] = "FAILED"
            
            # Content validation
            content_errors = self.validate_content(yaml_file, rules)
            if content_errors:
                results["content_violations"].append({
                    "path": yaml_file.path,
                    "errors": content_errors
                })
                results["status"] = "FAILED"
        
        return results
    
    def create_registry_update(self, yaml_files: List[ServiceYAML]):
        """Update the central YAML registry"""
        registry = {
            "last_updated": datetime.now().isoformat(),
            "total_services": len(yaml_files),
            "services": {}
        }
        
        for yaml_file in yaml_files:
            registry["services"][yaml_file.service_name] = {
                "path": yaml_file.path,
                "content_hash": yaml_file.content_hash,
                "port": yaml_file.port,
                "service_type": yaml_file.service_type
            }
        
        # Create directory if it doesn't exist
        self.registry_file.parent.mkdir(exist_ok=True)
        
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def suggest_fixes(self, results: dict) -> List[str]:
        """Suggest fixes for validation issues"""
        suggestions = []
        
        if results["duplicates"]:
            suggestions.append("🔧 DUPLICATE FIXES:")
            for service, paths in results["duplicates"].items():
                suggestions.append(f"  Service '{service}' has duplicates:")
                for path in paths:
                    suggestions.append(f"    - {path}")
                suggestions.append(f"  → Keep the most complete version and remove others")
        
        if results["port_conflicts"]:
            suggestions.append("🔧 PORT CONFLICT FIXES:")
            for port, paths in results["port_conflicts"].items():
                suggestions.append(f"  Port {port} is used by multiple services:")
                for path in paths:
                    suggestions.append(f"    - {path}")
        
        if results["location_violations"]:
            suggestions.append("🔧 LOCATION FIXES:")
            for violation in results["location_violations"]:
                suggestions.append(f"  Move {violation['path']} to allowed location")
                suggestions.append(f"    Error: {violation['error']}")
        
        return suggestions

def main():
    """Main validation function"""
    validator = YAMLGovernanceValidator()
    results = validator.run_validation()
    
    print(f"\n📊 YAML Governance Report - {results['status']}")
    print(f"Total YAML files scanned: {results['total_yaml_files']}")
    
    if results["status"] == "FAILED":
        print(f"\n❌ VALIDATION FAILED")
        
        if results["duplicates"]:
            print(f"🔄 Duplicates found: {len(results['duplicates'])}")
            for service, paths in results["duplicates"].items():
                print(f"  - {service}: {len(paths)} files")
        
        if results["port_conflicts"]:
            print(f"⚠️  Port conflicts: {len(results['port_conflicts'])}")
        
        if results["location_violations"]:
            print(f"📁 Location violations: {len(results['location_violations'])}")
            
        if results["content_violations"]:
            print(f"📝 Content violations: {len(results['content_violations'])}")
        
        # Show suggestions
        suggestions = validator.suggest_fixes(results)
        if suggestions:
            print(f"\n💡 SUGGESTED FIXES:")
            for suggestion in suggestions:
                print(suggestion)
        
        sys.exit(1)
    else:
        print(f"✅ ALL VALIDATIONS PASSED")
        
        # Update registry
        yaml_files = validator.scan_yaml_files()
        validator.create_registry_update(yaml_files)
        print(f"📄 Registry updated with {len(yaml_files)} services")
    
    sys.exit(0)

if __name__ == "__main__":
    main()