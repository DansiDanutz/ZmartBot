#!/usr/bin/env python3
"""
Comprehensive Backend Audit Script
Identifies and reports all issues in the ZmartBot backend
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path

class BackendAuditor:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
        self.project_root = Path("/Users/dansidanutz/Desktop/ZmartBot")
        self.backend_path = self.project_root / "backend" / "zmart-api"
        
    def log_issue(self, category, message, severity="ERROR"):
        self.issues.append({
            "category": category,
            "message": message,
            "severity": severity
        })
        
    def log_warning(self, category, message):
        self.warnings.append({
            "category": category,
            "message": message
        })
        
    def log_success(self, category, message):
        self.successes.append({
            "category": category,
            "message": message
        })
    
    def check_directory_structure(self):
        """Check if all required directories and files exist"""
        print("🔍 Checking directory structure...")
        
        required_paths = [
            self.backend_path,
            self.backend_path / "src",
            self.backend_path / "src" / "main.py",
            self.backend_path / "src" / "config",
            self.backend_path / "src" / "routes",
            self.backend_path / "src" / "services",
            self.backend_path / "src" / "utils",
            self.backend_path / "src" / "agents",
            self.backend_path / "requirements.txt",
            self.backend_path / "venv"
        ]
        
        for path in required_paths:
            if path.exists():
                self.log_success("Directory Structure", f"✅ {path} exists")
            else:
                self.log_issue("Directory Structure", f"❌ Missing: {path}")
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        try:
            # Check if we're in the right directory
            os.chdir(self.backend_path)
            
            # Check if virtual environment exists and is activated
            if not os.path.exists("venv"):
                self.log_issue("Dependencies", "Virtual environment not found")
                return
                
            # Test imports
            import_test = """
import sys
sys.path.insert(0, '.')
try:
    import fastapi
    import uvicorn
    import pydantic
    import sqlalchemy
    import redis
    import influxdb_client
    import prometheus_client
    print("SUCCESS")
except ImportError as e:
    print(f"IMPORT_ERROR: {e}")
"""
            
            result = subprocess.run([
                "venv/bin/python", "-c", import_test
            ], capture_output=True, text=True, cwd=self.backend_path)
            
            if "SUCCESS" in result.stdout:
                self.log_success("Dependencies", "All required packages are installed")
            else:
                self.log_issue("Dependencies", f"Import errors: {result.stderr}")
                
        except Exception as e:
            self.log_issue("Dependencies", f"Error checking dependencies: {e}")
    
    def check_database_connections(self):
        """Check database connection status"""
        print("🔍 Checking database connections...")
        
        # Check if databases are running
        try:
            # Check PostgreSQL
            result = subprocess.run(["pg_isready", "-h", "localhost"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_success("Database", "PostgreSQL is running")
            else:
                self.log_warning("Database", "PostgreSQL not responding")
                
            # Check Redis
            result = subprocess.run(["redis-cli", "ping"], 
                                  capture_output=True, text=True)
            if "PONG" in result.stdout:
                self.log_success("Database", "Redis is running")
            else:
                self.log_warning("Database", "Redis not responding")
                
            # Check InfluxDB
            result = subprocess.run(["curl", "-s", "http://localhost:8086/health"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_success("Database", "InfluxDB is running")
            else:
                self.log_warning("Database", "InfluxDB not responding")
                
        except Exception as e:
            self.log_issue("Database", f"Error checking databases: {e}")
    
    def check_server_status(self):
        """Check if the server can start and respond"""
        print("🔍 Checking server status...")
        
        try:
            # Test if server can import
            import_test = """
import sys
sys.path.insert(0, '.')
try:
    from src.main import app
    print("SUCCESS")
except Exception as e:
    print(f"IMPORT_ERROR: {e}")
"""
            
            result = subprocess.run([
                "venv/bin/python", "-c", import_test
            ], capture_output=True, text=True, cwd=self.backend_path)
            
            if "SUCCESS" in result.stdout:
                self.log_success("Server", "FastAPI app imports successfully")
            else:
                self.log_issue("Server", f"App import failed: {result.stderr}")
                
        except Exception as e:
            self.log_issue("Server", f"Error checking server: {e}")
    
    def check_configuration(self):
        """Check configuration files and settings"""
        print("🔍 Checking configuration...")
        
        config_file = self.backend_path / "src" / "config" / "settings.py"
        if config_file.exists():
            self.log_success("Configuration", "Settings file exists")
            
            # Check for common configuration issues
            with open(config_file, 'r') as f:
                content = f.read()
                
            if "DATABASE_URL" in content:
                self.log_success("Configuration", "Database URL configured")
            else:
                self.log_warning("Configuration", "Database URL not found")
                
            if "REDIS_URL" in content:
                self.log_success("Configuration", "Redis URL configured")
            else:
                self.log_warning("Configuration", "Redis URL not found")
        else:
            self.log_issue("Configuration", "Settings file missing")
    
    def check_api_endpoints(self):
        """Check if API endpoints are accessible"""
        print("🔍 Checking API endpoints...")
        
        try:
            # Try to start server in background
            server_process = subprocess.Popen([
                "venv/bin/python", "-m", "uvicorn", "src.main:app", 
                "--host", "0.0.0.0", "--port", "8000"
            ], cwd=self.backend_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a moment for server to start
            import time
            time.sleep(3)
            
            # Test health endpoint
            try:
                response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
                if response.status_code == 200:
                    self.log_success("API", "Health endpoint responding")
                else:
                    self.log_warning("API", f"Health endpoint returned {response.status_code}")
            except:
                self.log_issue("API", "Health endpoint not accessible")
            
            # Kill the server
            server_process.terminate()
            server_process.wait()
            
        except Exception as e:
            self.log_issue("API", f"Error testing API: {e}")
    
    def check_logs_for_errors(self):
        """Check for common error patterns"""
        print("🔍 Checking for error patterns...")
        
        # Common error patterns to look for
        error_patterns = [
            "ModuleNotFoundError",
            "ImportError", 
            "ConnectionError",
            "AuthenticationError",
            "PermissionError"
        ]
        
        # Check if there are any obvious error files
        log_files = list(self.project_root.glob("*.log"))
        if log_files:
            self.log_warning("Logs", f"Found log files: {[f.name for f in log_files]}")
    
    def run_full_audit(self):
        """Run the complete audit"""
        print("🚀 Starting Comprehensive Backend Audit...")
        print("=" * 50)
        
        self.check_directory_structure()
        self.check_dependencies()
        self.check_database_connections()
        self.check_server_status()
        self.check_configuration()
        self.check_api_endpoints()
        self.check_logs_for_errors()
        
        # Print results
        print("\n" + "=" * 50)
        print("📊 AUDIT RESULTS")
        print("=" * 50)
        
        if self.successes:
            print("\n✅ SUCCESSES:")
            for success in self.successes:
                print(f"  • {success['message']}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning['message']}")
        
        if self.issues:
            print("\n❌ ISSUES:")
            for issue in self.issues:
                print(f"  • [{issue['severity']}] {issue['message']}")
        
        print(f"\n📈 SUMMARY:")
        print(f"  • Successes: {len(self.successes)}")
        print(f"  • Warnings: {len(self.warnings)}")
        print(f"  • Issues: {len(self.issues)}")
        
        return len(self.issues) == 0

if __name__ == "__main__":
    auditor = BackendAuditor()
    success = auditor.run_full_audit()
    
    if success:
        print("\n🎉 Backend audit completed successfully!")
    else:
        print("\n🔧 Backend has issues that need to be fixed.")
        sys.exit(1) 