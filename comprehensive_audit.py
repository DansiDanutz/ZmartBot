#!/usr/bin/env python3
"""
Comprehensive Audit Report for ZmartBot Trading Platform
Analyzes project structure, functionality, and implementation status
"""
import os
import sys
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class ZmartBotAuditor:
    """Comprehensive auditor for ZmartBot Trading Platform"""
    
    def __init__(self):
        self.project_root = Path("/Users/dansidanutz/Desktop/ZmartBot")
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "project_overview": {},
            "backend_analysis": {},
            "frontend_analysis": {},
            "module_status": {},
            "testing_results": {},
            "deployment_status": {},
            "recommendations": []
        }
    
    def analyze_project_structure(self):
        """Analyze overall project structure"""
        print("🔍 Analyzing project structure...")
        
        structure = {
            "backend": {
                "zmart-api": self._analyze_directory("backend/zmart-api"),
                "total_files": 0
            },
            "frontend": {
                "zmart-dashboard": self._analyze_directory("frontend/zmart-dashboard"),
                "total_files": 0
            },
            "documentation": {
                "Documentation": self._analyze_directory("Documentation"),
                "total_files": 0
            },
            "scripts": {
                "startup_scripts": self._find_startup_scripts(),
                "test_scripts": self._find_test_scripts()
            }
        }
        
        # Count total files
        for section in ["backend", "frontend", "documentation"]:
            if section in structure:
                for key, data in structure[section].items():
                    if isinstance(data, dict) and "files" in data:
                        structure[section]["total_files"] += len(data["files"])
        
        self.audit_results["project_overview"]["structure"] = structure
        return structure
    
    def _analyze_directory(self, path: str) -> Dict[str, Any]:
        """Analyze a specific directory"""
        full_path = self.project_root / path
        if not full_path.exists():
            return {"exists": False, "files": [], "size": 0}
        
        files = []
        total_size = 0
        
        for file_path in full_path.rglob("*"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(self.project_root))
                size = file_path.stat().st_size
                files.append({
                    "path": rel_path,
                    "size": size,
                    "extension": file_path.suffix
                })
                total_size += size
        
        return {
            "exists": True,
            "files": files,
            "size": total_size,
            "file_count": len(files)
        }
    
    def _find_startup_scripts(self) -> List[str]:
        """Find all startup scripts"""
        scripts = []
        for file_path in self.project_root.rglob("*.sh"):
            if "start" in file_path.name.lower():
                scripts.append(str(file_path.relative_to(self.project_root)))
        return scripts
    
    def _find_test_scripts(self) -> List[str]:
        """Find all test scripts"""
        scripts = []
        for file_path in self.project_root.rglob("test_*.py"):
            scripts.append(str(file_path.relative_to(self.project_root)))
        return scripts
    
    def analyze_backend_implementation(self):
        """Analyze backend implementation status"""
        print("🔍 Analyzing backend implementation...")
        
        backend_path = self.project_root / "backend" / "zmart-api"
        if not backend_path.exists():
            self.audit_results["backend_analysis"]["status"] = "NOT_FOUND"
            return
        
        # Check main components
        components = {
            "main_app": backend_path / "src" / "main.py",
            "routes": backend_path / "src" / "routes",
            "services": backend_path / "src" / "services",
            "agents": backend_path / "src" / "agents",
            "config": backend_path / "src" / "config",
            "utils": backend_path / "src" / "utils"
        }
        
        backend_status = {
            "status": "IMPLEMENTED",
            "components": {},
            "endpoints": [],
            "dependencies": []
        }
        
        # Check each component
        for name, path in components.items():
            if path.exists():
                if path.is_file():
                    backend_status["components"][name] = {
                        "status": "EXISTS",
                        "size": path.stat().st_size,
                        "lines": len(path.read_text().splitlines())
                    }
                else:
                    files = list(path.rglob("*.py"))
                    backend_status["components"][name] = {
                        "status": "EXISTS",
                        "file_count": len(files),
                        "files": [f.name for f in files]
                    }
            else:
                backend_status["components"][name] = {"status": "MISSING"}
        
        # Check for specific endpoints
        routes_path = backend_path / "src" / "routes"
        if routes_path.exists():
            for route_file in routes_path.glob("*.py"):
                if route_file.name != "__init__.py":
                    backend_status["endpoints"].append(route_file.stem)
        
        # Check dependencies
        requirements_path = backend_path / "requirements.txt"
        if requirements_path.exists():
            backend_status["dependencies"] = requirements_path.read_text().splitlines()
        
        self.audit_results["backend_analysis"] = backend_status
        return backend_status
    
    def analyze_frontend_implementation(self):
        """Analyze frontend implementation status"""
        print("🔍 Analyzing frontend implementation...")
        
        frontend_path = self.project_root / "frontend" / "zmart-dashboard"
        if not frontend_path.exists():
            self.audit_results["frontend_analysis"]["status"] = "NOT_FOUND"
            return
        
        frontend_status = {
            "status": "IMPLEMENTED",
            "components": {},
            "pages": [],
            "dependencies": []
        }
        
        # Check main components
        components = {
            "main_app": frontend_path / "src" / "App.tsx",
            "pages": frontend_path / "src" / "pages",
            "components": frontend_path / "src" / "components",
            "services": frontend_path / "src" / "services"
        }
        
        for name, path in components.items():
            if path.exists():
                if path.is_file():
                    frontend_status["components"][name] = {
                        "status": "EXISTS",
                        "size": path.stat().st_size,
                        "lines": len(path.read_text().splitlines())
                    }
                else:
                    files = list(path.rglob("*.tsx")) + list(path.rglob("*.ts"))
                    frontend_status["components"][name] = {
                        "status": "EXISTS",
                        "file_count": len(files),
                        "files": [f.name for f in files]
                    }
            else:
                frontend_status["components"][name] = {"status": "MISSING"}
        
        # Check pages
        pages_path = frontend_path / "src" / "pages"
        if pages_path.exists():
            for page_file in pages_path.glob("*.tsx"):
                frontend_status["pages"].append(page_file.stem)
        
        # Check dependencies
        package_path = frontend_path / "package.json"
        if package_path.exists():
            try:
                package_data = json.loads(package_path.read_text())
                frontend_status["dependencies"] = list(package_data.get("dependencies", {}).keys())
            except:
                frontend_status["dependencies"] = []
        
        self.audit_results["frontend_analysis"] = frontend_status
        return frontend_status
    
    def analyze_module_status(self):
        """Analyze status of different modules"""
        print("🔍 Analyzing module status...")
        
        modules = {
            "zmartbot": {
                "status": "IMPLEMENTED",
                "backend": "backend/zmart-api",
                "frontend": "frontend/zmart-dashboard",
                "ports": {"api": 8000, "frontend": 3000}
            },
            "kingfisher": {
                "status": "DOCUMENTED_ONLY",
                "backend": "kingfisher-module.md",
                "frontend": "kingfisher-module.md",
                "ports": {"api": 8100, "frontend": 3100}
            },
            "trade_strategy": {
                "status": "DOCUMENTED_ONLY",
                "backend": "trade-strategy-module.md",
                "frontend": "trade-strategy-module.md",
                "ports": {"api": 8200, "frontend": 3200}
            },
            "simulation_agent": {
                "status": "DOCUMENTED_ONLY",
                "backend": "simulation-agent-module.md",
                "frontend": "simulation-agent-module.md",
                "ports": {"api": 8300, "frontend": 3300}
            }
        }
        
        # Check actual implementation status
        for module_name, module_info in modules.items():
            if module_name == "zmartbot":
                backend_exists = (self.project_root / "backend" / "zmart-api").exists()
                frontend_exists = (self.project_root / "frontend" / "zmart-dashboard").exists()
                
                if backend_exists and frontend_exists:
                    module_info["status"] = "IMPLEMENTED"
                elif backend_exists or frontend_exists:
                    module_info["status"] = "PARTIALLY_IMPLEMENTED"
                else:
                    module_info["status"] = "NOT_IMPLEMENTED"
            else:
                # Check if documentation exists
                doc_path = self.project_root / module_info["backend"]
                if doc_path.exists():
                    module_info["status"] = "DOCUMENTED_ONLY"
                else:
                    module_info["status"] = "NOT_DOCUMENTED"
        
        self.audit_results["module_status"] = modules
        return modules
    
    def test_backend_functionality(self):
        """Test backend functionality"""
        print("🧪 Testing backend functionality...")
        
        test_results = {
            "server_startup": "NOT_TESTED",
            "health_endpoint": "NOT_TESTED",
            "api_endpoints": "NOT_TESTED",
            "database_connections": "NOT_TESTED"
        }
        
        # Try to start server
        try:
            # Check if server can start
            backend_path = self.project_root / "backend" / "zmart-api"
            if backend_path.exists():
                test_results["server_startup"] = "READY_TO_TEST"
                
                # Test health endpoint if server is running
                try:
                    response = requests.get("http://localhost:8000/health", timeout=5)
                    if response.status_code == 200:
                        test_results["health_endpoint"] = "WORKING"
                    else:
                        test_results["health_endpoint"] = "ERROR"
                except:
                    test_results["health_endpoint"] = "SERVER_NOT_RUNNING"
        except Exception as e:
            test_results["server_startup"] = f"ERROR: {str(e)}"
        
        self.audit_results["testing_results"]["backend"] = test_results
        return test_results
    
    def test_frontend_functionality(self):
        """Test frontend functionality"""
        print("🧪 Testing frontend functionality...")
        
        test_results = {
            "build_status": "NOT_TESTED",
            "dev_server": "NOT_TESTED",
            "pages": "NOT_TESTED"
        }
        
        frontend_path = self.project_root / "frontend" / "zmart-dashboard"
        if frontend_path.exists():
            # Check if package.json exists
            package_path = frontend_path / "package.json"
            if package_path.exists():
                test_results["build_status"] = "READY_TO_TEST"
                
                # Test if dev server is running
                try:
                    response = requests.get("http://localhost:3000", timeout=5)
                    if response.status_code == 200:
                        test_results["dev_server"] = "WORKING"
                    else:
                        test_results["dev_server"] = "ERROR"
                except:
                    test_results["dev_server"] = "SERVER_NOT_RUNNING"
        
        self.audit_results["testing_results"]["frontend"] = test_results
        return test_results
    
    def generate_recommendations(self):
        """Generate recommendations based on audit results"""
        print("💡 Generating recommendations...")
        
        recommendations = []
        
        # Backend recommendations
        backend_status = self.audit_results.get("backend_analysis", {})
        if backend_status.get("status") == "IMPLEMENTED":
            recommendations.append("✅ Backend is fully implemented - ready for testing")
        else:
            recommendations.append("❌ Backend needs implementation")
        
        # Frontend recommendations
        frontend_status = self.audit_results.get("frontend_analysis", {})
        if frontend_status.get("status") == "IMPLEMENTED":
            recommendations.append("✅ Frontend is fully implemented - ready for testing")
        else:
            recommendations.append("❌ Frontend needs implementation")
        
        # Module recommendations
        module_status = self.audit_results.get("module_status", {})
        for module_name, module_info in module_status.items():
            if module_info.get("status") == "DOCUMENTED_ONLY":
                recommendations.append(f"📋 {module_name.title()} module is documented but needs implementation")
            elif module_info.get("status") == "NOT_IMPLEMENTED":
                recommendations.append(f"❌ {module_name.title()} module needs implementation")
        
        # Testing recommendations
        testing_results = self.audit_results.get("testing_results", {})
        if testing_results.get("backend", {}).get("health_endpoint") != "WORKING":
            recommendations.append("🧪 Backend needs testing - start server and test endpoints")
        
        if testing_results.get("frontend", {}).get("dev_server") != "WORKING":
            recommendations.append("🧪 Frontend needs testing - start dev server and test pages")
        
        # Priority recommendations
        recommendations.append("🚀 NEXT STEPS:")
        recommendations.append("   1. Start backend server and test all endpoints")
        recommendations.append("   2. Start frontend dev server and test all pages")
        recommendations.append("   3. Implement KingFisher module (highest priority)")
        recommendations.append("   4. Implement Trade Strategy module")
        recommendations.append("   5. Implement Simulation Agent module")
        recommendations.append("   6. Set up production deployment")
        
        self.audit_results["recommendations"] = recommendations
        return recommendations
    
    def generate_report(self):
        """Generate comprehensive audit report"""
        print("📊 Generating comprehensive audit report...")
        
        # Run all analyses
        self.analyze_project_structure()
        self.analyze_backend_implementation()
        self.analyze_frontend_implementation()
        self.analyze_module_status()
        self.test_backend_functionality()
        self.test_frontend_functionality()
        self.generate_recommendations()
        
        # Save report
        report_path = self.project_root / "COMPREHENSIVE_AUDIT_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump(self.audit_results, f, indent=2)
        
        # Generate summary
        self._print_summary()
        
        return self.audit_results
    
    def _print_summary(self):
        """Print audit summary"""
        print("\n" + "="*80)
        print("🎯 ZMARTBOT COMPREHENSIVE AUDIT REPORT")
        print("="*80)
        
        # Project Overview
        structure = self.audit_results["project_overview"]["structure"]
        print(f"\n📁 PROJECT STRUCTURE:")
        print(f"   Backend files: {structure['backend']['total_files']}")
        print(f"   Frontend files: {structure['frontend']['total_files']}")
        print(f"   Documentation files: {structure['documentation']['total_files']}")
        print(f"   Startup scripts: {len(structure['scripts']['startup_scripts'])}")
        print(f"   Test scripts: {len(structure['scripts']['test_scripts'])}")
        
        # Backend Status
        backend = self.audit_results["backend_analysis"]
        print(f"\n🔧 BACKEND STATUS: {backend.get('status', 'UNKNOWN')}")
        if backend.get('components'):
            for component, info in backend['components'].items():
                status = info.get('status', 'UNKNOWN')
                print(f"   {component}: {status}")
        
        # Frontend Status
        frontend = self.audit_results["frontend_analysis"]
        print(f"\n🎨 FRONTEND STATUS: {frontend.get('status', 'UNKNOWN')}")
        if frontend.get('components'):
            for component, info in frontend['components'].items():
                status = info.get('status', 'UNKNOWN')
                print(f"   {component}: {status}")
        
        # Module Status
        modules = self.audit_results["module_status"]
        print(f"\n📦 MODULE STATUS:")
        for module_name, module_info in modules.items():
            status = module_info.get('status', 'UNKNOWN')
            print(f"   {module_name.title()}: {status}")
        
        # Testing Status
        testing = self.audit_results["testing_results"]
        print(f"\n🧪 TESTING STATUS:")
        if 'backend' in testing:
            backend_test = testing['backend']
            print(f"   Backend health: {backend_test.get('health_endpoint', 'NOT_TESTED')}")
        if 'frontend' in testing:
            frontend_test = testing['frontend']
            print(f"   Frontend dev server: {frontend_test.get('dev_server', 'NOT_TESTED')}")
        
        # Recommendations
        recommendations = self.audit_results["recommendations"]
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   {rec}")
        
        print(f"\n📄 Full report saved to: COMPREHENSIVE_AUDIT_REPORT.json")
        print("="*80)

def main():
    """Main audit function"""
    auditor = ZmartBotAuditor()
    report = auditor.generate_report()
    return report

if __name__ == "__main__":
    main() 