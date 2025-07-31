#!/usr/bin/env python3
"""
ZmartBot Health Monitor
Comprehensive health monitoring for all backend components
"""
import asyncio
import logging
import time
import requests
import subprocess
import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthMonitor:
    """Comprehensive health monitoring system"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.health_status = {}
        self.start_time = time.time()
    
    async def check_server_status(self) -> Dict[str, Any]:
        """Check if the main server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "data": response.json()
                }
            else:
                return {
                    "status": "unhealthy",
                    "status_code": response.status_code,
                    "error": "Server responded with non-200 status"
                }
        except requests.exceptions.ConnectionError:
            return {
                "status": "down",
                "error": "Server not responding"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_port_usage(self) -> Dict[str, Any]:
        """Check if port 8000 is being used"""
        try:
            result = subprocess.run(['lsof', '-ti', ':8000'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                return {
                    "status": "in_use",
                    "pids": pids,
                    "count": len(pids)
                }
            else:
                return {
                    "status": "available",
                    "pids": [],
                    "count": 0
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_processes(self) -> Dict[str, Any]:
        """Check for running Python/uvicorn processes"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            python_processes = []
            uvicorn_processes = []
            
            for line in lines:
                if 'python' in line.lower() and 'zmart' in line.lower():
                    python_processes.append(line.strip())
                if 'uvicorn' in line.lower():
                    uvicorn_processes.append(line.strip())
            
            return {
                "python_processes": python_processes,
                "uvicorn_processes": uvicorn_processes,
                "python_count": len(python_processes),
                "uvicorn_count": len(uvicorn_processes)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_dependencies(self) -> Dict[str, Any]:
        """Check if all required dependencies are available"""
        required_packages = [
            'fastapi',
            'uvicorn',
            'pydantic',
            'pydantic_settings',
            'asyncpg',
            'redis',
            'influxdb_client',
            'httpx',
            'websockets'
        ]
        
        missing_packages = []
        available_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                available_packages.append(package)
            except ImportError:
                missing_packages.append(package)
        
        return {
            "available_packages": available_packages,
            "missing_packages": missing_packages,
            "total_required": len(required_packages),
            "total_available": len(available_packages),
            "status": "complete" if not missing_packages else "incomplete"
        }
    
    async def check_file_structure(self) -> Dict[str, Any]:
        """Check if all required files exist"""
        required_files = [
            'src/main.py',
            'src/config/settings.py',
            'src/utils/database.py',
            'src/utils/monitoring.py',
            'requirements.txt'
        ]
        
        existing_files = []
        missing_files = []
        
        for file_path in required_files:
            if os.path.exists(file_path):
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        return {
            "existing_files": existing_files,
            "missing_files": missing_files,
            "total_required": len(required_files),
            "total_existing": len(existing_files),
            "status": "complete" if not missing_files else "incomplete"
        }
    
    async def check_environment(self) -> Dict[str, Any]:
        """Check environment variables and Python path"""
        env_vars = {
            'ENVIRONMENT': os.environ.get('ENVIRONMENT', 'Not set'),
            'DEBUG': os.environ.get('DEBUG', 'Not set'),
            'HOST': os.environ.get('HOST', 'Not set'),
            'PORT': os.environ.get('PORT', 'Not set'),
            'PYTHONPATH': os.environ.get('PYTHONPATH', 'Not set')
        }
        
        # Check if src is in Python path
        src_in_path = 'src' in sys.path or any('src' in path for path in sys.path)
        
        return {
            "environment_variables": env_vars,
            "python_path": sys.path,
            "src_in_path": src_in_path,
            "status": "configured" if src_in_path else "misconfigured"
        }
    
    async def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run all health checks"""
        logger.info("🔍 Starting comprehensive health check...")
        
        checks = {
            "server_status": await self.check_server_status(),
            "port_usage": await self.check_port_usage(),
            "processes": await self.check_processes(),
            "dependencies": await self.check_dependencies(),
            "file_structure": await self.check_file_structure(),
            "environment": await self.check_environment()
        }
        
        # Calculate overall health
        healthy_checks = sum(1 for check in checks.values() if check.get('status') in ['healthy', 'complete', 'configured'])
        total_checks = len(checks)
        
        overall_status = "healthy" if healthy_checks == total_checks else "degraded"
        
        self.health_status = {
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - self.start_time,
            "overall_status": overall_status,
            "healthy_checks": healthy_checks,
            "total_checks": total_checks,
            "checks": checks
        }
        
        return self.health_status
    
    def print_health_report(self):
        """Print a formatted health report"""
        if not self.health_status:
            print("❌ No health status available. Run comprehensive check first.")
            return
        
        print("\n" + "="*60)
        print("🏥 ZMARTBOT HEALTH REPORT")
        print("="*60)
        
        status = self.health_status['overall_status']
        emoji = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
        
        print(f"{emoji} Overall Status: {status.upper()}")
        print(f"📊 Healthy Checks: {self.health_status['healthy_checks']}/{self.health_status['total_checks']}")
        print(f"⏰ Timestamp: {self.health_status['timestamp']}")
        print(f"⏱️  Uptime: {self.health_status['uptime']:.2f}s")
        
        print("\n📋 DETAILED CHECKS:")
        print("-" * 40)
        
        for check_name, check_result in self.health_status['checks'].items():
            status = check_result.get('status', 'unknown')
            emoji = "✅" if status in ['healthy', 'complete', 'configured'] else "⚠️" if status == 'degraded' else "❌"
            
            print(f"{emoji} {check_name.replace('_', ' ').title()}: {status}")
            
            if 'error' in check_result:
                print(f"   └─ Error: {check_result['error']}")
            elif 'missing_packages' in check_result and check_result['missing_packages']:
                print(f"   └─ Missing: {', '.join(check_result['missing_packages'])}")
            elif 'missing_files' in check_result and check_result['missing_files']:
                print(f"   └─ Missing: {', '.join(check_result['missing_files'])}")
        
        print("\n" + "="*60)
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations based on health status"""
        recommendations = []
        
        if not self.health_status:
            return ["Run comprehensive health check first"]
        
        checks = self.health_status['checks']
        
        # Server status recommendations
        if checks['server_status']['status'] != 'healthy':
            recommendations.append("Start the backend server using: python start_fixed_server.py")
        
        # Port usage recommendations
        if checks['port_usage']['status'] == 'in_use':
            recommendations.append("Clear port 8000: lsof -ti:8000 | xargs kill -9")
        
        # Dependencies recommendations
        if checks['dependencies']['status'] == 'incomplete':
            missing = checks['dependencies']['missing_packages']
            recommendations.append(f"Install missing packages: pip install {' '.join(missing)}")
        
        # File structure recommendations
        if checks['file_structure']['status'] == 'incomplete':
            recommendations.append("Check file structure and ensure all required files exist")
        
        # Environment recommendations
        if checks['environment']['status'] == 'misconfigured':
            recommendations.append("Set PYTHONPATH to include src directory")
        
        if not recommendations:
            recommendations.append("System is healthy - no recommendations needed")
        
        return recommendations

async def main():
    """Main health monitoring function"""
    monitor = HealthMonitor()
    
    print("🔧 ZmartBot Health Monitor")
    print("=" * 50)
    
    # Run comprehensive health check
    health_status = await monitor.run_comprehensive_check()
    
    # Print health report
    monitor.print_health_report()
    
    # Print recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 20)
    recommendations = monitor.get_recommendations()
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    # Return overall status
    return health_status['overall_status']

if __name__ == "__main__":
    try:
        status = asyncio.run(main())
        sys.exit(0 if status == "healthy" else 1)
    except KeyboardInterrupt:
        print("\n🛑 Health check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1) 