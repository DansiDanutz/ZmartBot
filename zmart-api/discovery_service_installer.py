#!/usr/bin/env python3
"""
Discovery Database Service - Professional Installation & Deployment Script
Complete setup and configuration for the Discovery Database Service

Features:
- Dependency installation and validation
- Database initialization and schema setup
- Service configuration and validation
- Health checks and system verification
- Integration with ZmartBot ecosystem
"""

import os
import sys
import sqlite3
import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class DiscoveryServiceInstaller:
    """Professional installer for Discovery Database Service"""
    
    def __init__(self):
        self.base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
        self.service_name = "discovery-database-service"
        self.service_port = 8780
        self.required_files = [
            "discovery_database_server.py",
            "discovery_trigger_professional.py", 
            "discovery_file_watcher_professional.py",
            "discovery_usage_guide.md"
        ]
        self.logs_dir = os.path.join(self.base_path, "logs")
        self.requirements = [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0", 
            "pydantic>=2.0.0",
            "watchdog>=3.0.0",
            "psutil>=5.9.0"
        ]
        
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"🚀 {title}")
        print(f"{'='*60}")
    
    def print_step(self, step: str, status: str = ""):
        """Print installation step"""
        if status == "SUCCESS":
            print(f"✅ {step}")
        elif status == "FAILED":
            print(f"❌ {step}")
        elif status == "WARNING":
            print(f"⚠️  {step}")
        else:
            print(f"🔧 {step}")
    
    def check_python_version(self) -> bool:
        """Check Python version compatibility"""
        self.print_step("Checking Python version...")
        
        version_info = sys.version_info
        if version_info.major != 3 or version_info.minor < 8:
            self.print_step(f"Python {version_info.major}.{version_info.minor} not supported. Requires Python 3.8+", "FAILED")
            return False
        
        self.print_step(f"Python {version_info.major}.{version_info.minor}.{version_info.micro} - Compatible", "SUCCESS")
        return True
    
    def install_dependencies(self) -> bool:
        """Install required Python packages"""
        self.print_step("Installing Python dependencies...")
        
        try:
            # Check if requirements are already installed
            missing_packages = []
            for requirement in self.requirements:
                package_name = requirement.split(">=")[0]
                try:
                    __import__(package_name.replace("-", "_"))
                except ImportError:
                    missing_packages.append(requirement)
            
            if not missing_packages:
                self.print_step("All dependencies already installed", "SUCCESS")
                return True
            
            # Install missing packages
            for package in missing_packages:
                self.print_step(f"Installing {package}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.print_step(f"Failed to install {package}: {result.stderr}", "FAILED")
                    return False
            
            self.print_step("All dependencies installed successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_step(f"Dependency installation failed: {e}", "FAILED")
            return False
    
    def verify_files(self) -> bool:
        """Verify all required files exist"""
        self.print_step("Verifying service files...")
        
        missing_files = []
        for file_name in self.required_files:
            file_path = os.path.join(self.base_path, file_name)
            if not os.path.exists(file_path):
                missing_files.append(file_name)
        
        if missing_files:
            self.print_step(f"Missing files: {', '.join(missing_files)}", "FAILED")
            return False
        
        self.print_step("All service files present", "SUCCESS")
        return True
    
    def setup_directories(self) -> bool:
        """Setup required directories"""
        self.print_step("Setting up directories...")
        
        try:
            os.makedirs(self.logs_dir, exist_ok=True)
            os.makedirs("/Users/dansidanutz/Desktop/ZmartBot/zmart-api/data", exist_ok=True)
            
            # Set proper permissions
            os.chmod(self.logs_dir, 0o755)
            
            self.print_step("Directories created successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_step(f"Directory setup failed: {e}", "FAILED")
            return False
    
    def initialize_database(self) -> bool:
        """Initialize the discovery database"""
        self.print_step("Initializing discovery database...")
        
        try:
            db_path = os.path.join(self.base_path, "discovery_registry.db")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create discovery services table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS discovery_services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT UNIQUE NOT NULL,
                    discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'DISCOVERED',
                    has_mdc_file BOOLEAN DEFAULT 0,
                    has_python_file BOOLEAN DEFAULT 1,
                    python_file_path TEXT,
                    mdc_file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_service_name ON discovery_services(service_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_python_path ON discovery_services(python_file_path)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON discovery_services(status)')
            
            # Insert metadata
            cursor.execute('''
                INSERT OR REPLACE INTO discovery_services 
                (service_name, discovered_date, status, has_mdc_file, has_python_file, python_file_path, mdc_file_path) 
                VALUES (?, ?, 'METADATA', 1, 0, ?, ?)
            ''', (
                "_database_metadata", 
                datetime.now(),
                "Database initialized by installer",
                "Installation metadata entry"
            ))
            
            conn.commit()
            conn.close()
            
            self.print_step("Discovery database initialized successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_step(f"Database initialization failed: {e}", "FAILED")
            return False
    
    def test_service_startup(self) -> bool:
        """Test service startup and basic functionality"""
        self.print_step("Testing service startup...")
        
        try:
            # Test database connection
            db_path = os.path.join(self.base_path, "discovery_registry.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM discovery_services")
            count = cursor.fetchone()[0]
            conn.close()
            
            self.print_step(f"Database connectivity test passed ({count} entries)", "SUCCESS")
            
            # Test Python imports
            sys.path.insert(0, self.base_path)
            try:
                import discovery_database_server
                self.print_step("Service imports test passed", "SUCCESS")
            except ImportError as e:
                self.print_step(f"Service import test failed: {e}", "FAILED")
                return False
            
            return True
            
        except Exception as e:
            self.print_step(f"Service startup test failed: {e}", "FAILED")
            return False
    
    def create_service_scripts(self) -> bool:
        """Create service management scripts"""
        self.print_step("Creating service management scripts...")
        
        try:
            # Create start script
            start_script = os.path.join(self.base_path, "start_discovery_service.sh")
            with open(start_script, 'w') as f:
                f.write(f"""#!/bin/bash
# Discovery Database Service - Start Script
# Generated by installer on {datetime.now().isoformat()}

export DISCOVERY_DB_PATH="{self.base_path}/discovery_registry.db"
export MDC_RULES_PATH="/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules"
export ZMARTBOT_PATH="/Users/dansidanutz/Desktop/ZmartBot"
export SERVICE_PORT="{self.service_port}"

cd "{self.base_path}"

echo "🚀 Starting Discovery Database Service on port {self.service_port}..."
python3 discovery_database_server.py
""")
            
            # Create stop script
            stop_script = os.path.join(self.base_path, "stop_discovery_service.sh")
            with open(stop_script, 'w') as f:
                f.write(f"""#!/bin/bash
# Discovery Database Service - Stop Script
# Generated by installer on {datetime.now().isoformat()}

echo "🛑 Stopping Discovery Database Service..."
pkill -f "discovery_database_server.py"
echo "✅ Discovery Database Service stopped"
""")
            
            # Create health check script
            health_script = os.path.join(self.base_path, "check_discovery_health.sh")
            with open(health_script, 'w') as f:
                f.write(f"""#!/bin/bash
# Discovery Database Service - Health Check Script
# Generated by installer on {datetime.now().isoformat()}

echo "🏥 Checking Discovery Database Service health..."
curl -s http://localhost:{self.service_port}/health | python3 -m json.tool
echo ""
echo "📊 Checking service status..."
curl -s http://localhost:{self.service_port}/status | python3 -m json.tool
""")
            
            # Make scripts executable
            os.chmod(start_script, 0o755)
            os.chmod(stop_script, 0o755)
            os.chmod(health_script, 0o755)
            
            self.print_step("Service management scripts created", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_step(f"Script creation failed: {e}", "FAILED")
            return False
    
    def run_initial_discovery(self) -> bool:
        """Run initial discovery scan"""
        self.print_step("Running initial discovery scan...")
        
        try:
            # Run discovery trigger on main service files
            trigger_script = os.path.join(self.base_path, "discovery_trigger_professional.py")
            
            test_files = [
                os.path.join(self.base_path, "discovery_database_server.py"),
                "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules/discovery-database-service.mdc"
            ]
            
            discovered_count = 0
            for test_file in test_files:
                if os.path.exists(test_file):
                    result = subprocess.run([
                        sys.executable, trigger_script, test_file
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        discovered_count += 1
            
            self.print_step(f"Initial discovery completed - {discovered_count} services processed", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_step(f"Initial discovery failed: {e}", "WARNING")
            return True  # Non-critical failure
    
    def generate_installation_report(self) -> Dict[str, Any]:
        """Generate comprehensive installation report"""
        try:
            # Get database stats
            db_path = os.path.join(self.base_path, "discovery_registry.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM discovery_services")
            db_count = cursor.fetchone()[0]
            conn.close()
            
            report = {
                "installation_date": datetime.now().isoformat(),
                "service_name": self.service_name,
                "service_port": self.service_port,
                "base_path": self.base_path,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "database_path": db_path,
                "database_entries": db_count,
                "installed_files": self.required_files,
                "management_scripts": [
                    "start_discovery_service.sh",
                    "stop_discovery_service.sh", 
                    "check_discovery_health.sh"
                ],
                "service_urls": {
                    "health": f"http://localhost:{self.service_port}/health",
                    "status": f"http://localhost:{self.service_port}/status",
                    "services": f"http://localhost:{self.service_port}/services",
                    "metrics": f"http://localhost:{self.service_port}/metrics"
                },
                "next_steps": [
                    "Run: ./start_discovery_service.sh",
                    "Check health: ./check_discovery_health.sh",
                    "Request port assignment from Port Manager",
                    "Request passport from Passport Service",
                    "Complete certification workflow"
                ]
            }
            
            # Write report to file
            report_path = os.path.join(self.base_path, "discovery_installation_report.json")
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            return report
            
        except Exception as e:
            return {"error": f"Report generation failed: {e}"}
    
    def install(self) -> bool:
        """Run complete installation process"""
        self.print_header("Discovery Database Service Installation")
        
        print(f"🎯 Service: {self.service_name}")
        print(f"📁 Location: {self.base_path}")
        print(f"🌐 Port: {self.service_port}")
        print(f"📋 Files: {len(self.required_files)} service files")
        print("")
        
        # Installation steps
        steps = [
            ("Check Python version", self.check_python_version),
            ("Install dependencies", self.install_dependencies),
            ("Verify service files", self.verify_files),
            ("Setup directories", self.setup_directories),
            ("Initialize database", self.initialize_database),
            ("Test service startup", self.test_service_startup),
            ("Create management scripts", self.create_service_scripts),
            ("Run initial discovery", self.run_initial_discovery),
        ]
        
        failed_steps = []
        for step_name, step_func in steps:
            try:
                if not step_func():
                    failed_steps.append(step_name)
            except Exception as e:
                self.print_step(f"{step_name} - Exception: {e}", "FAILED")
                failed_steps.append(step_name)
        
        # Generate installation report
        print("\n🔧 Generating installation report...")
        report = self.generate_installation_report()
        
        # Final status
        if failed_steps:
            self.print_header("Installation FAILED")
            print(f"❌ Failed steps: {', '.join(failed_steps)}")
            print("🔧 Please fix the issues and run the installer again.")
            return False
        else:
            self.print_header("Installation SUCCESSFUL")
            print("✅ Discovery Database Service installed successfully!")
            print("")
            print("📋 NEXT STEPS:")
            for step in report.get("next_steps", []):
                print(f"   • {step}")
            print("")
            print(f"📊 Installation report: {self.base_path}/discovery_installation_report.json")
            print(f"🚀 Start service: {self.base_path}/start_discovery_service.sh")
            print(f"🏥 Health check: {self.base_path}/check_discovery_health.sh")
            return True

def main():
    """Main installation function"""
    print("🚀 Discovery Database Service - Professional Installer")
    print("⚡ Complete setup and configuration for certification-ready service")
    print("")
    
    try:
        installer = DiscoveryServiceInstaller()
        success = installer.install()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️ Installation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Installation failed with critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()