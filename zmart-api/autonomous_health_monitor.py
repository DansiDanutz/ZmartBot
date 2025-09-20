#!/usr/bin/env python3
"""
Autonomous Health Monitor for ZmartBot System
Continuously monitors system health and automatically fixes issues
"""

import os
import sys
import time
import json
import logging
import subprocess
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AutonomousHealthMonitor:
    """Monitors and maintains system health autonomously"""
    
    def __init__(self, config_path: str = "autonomous_health_config.json"):
        self.config_path = Path(config_path)
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.config = self.load_config()
        
        # Health check results
        self.health_status = {
            "last_check": None,
            "overall_status": "unknown",
            "components": {},
            "auto_fixes_applied": []
        }
        
    def setup_logging(self):
        """Setup logging for health monitor"""
        log_file = self.logs_dir / "autonomous_health_monitor.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self) -> Dict:
        """Load health monitor configuration"""
        default_config = {
            "health_check_interval": 300,  # 5 minutes
            "auto_fix_enabled": True,
            "max_memory_usage_percent": 90,
            "max_cpu_usage_percent": 80,
            "min_disk_space_gb": 5,
            "required_services": [
                "background_optimization_agent.py",
                "comprehensive_optimization_integration.py",
                "run_dev.py"
            ],
            "log_rotation_threshold_mb": 10,
            "auto_restart_failed_services": True,
            "notification_webhook": None
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                
        # Create default config file
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        return default_config
        
    def check_system_resources(self) -> Dict:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_free_gb = disk.free / (1024**3)
            
            # Network connections
            network_connections = len(psutil.net_connections())
            
            status = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_free_gb": disk_free_gb,
                "network_connections": network_connections,
                "status": "healthy"
            }
            
            # Check thresholds
            if cpu_percent > self.config["max_cpu_usage_percent"]:
                status["status"] = "warning"
                status["issues"] = status.get("issues", [])
                status["issues"].append(f"High CPU usage: {cpu_percent}%")
                
            if memory_percent > self.config["max_memory_usage_percent"]:
                status["status"] = "warning"
                status["issues"] = status.get("issues", [])
                status["issues"].append(f"High memory usage: {memory_percent}%")
                
            if disk_free_gb < self.config["min_disk_space_gb"]:
                status["status"] = "critical"
                status["issues"] = status.get("issues", [])
                status["issues"].append(f"Low disk space: {disk_free_gb:.1f}GB")
                
            return status
            
        except Exception as e:
            self.logger.error(f"Error checking system resources: {e}")
            return {"status": "error", "error": str(e)}
            
    def check_required_services(self) -> Dict:
        """Check if required services are running"""
        try:
            services_status = {}
            all_healthy = True
            
            for service in self.config["required_services"]:
                # Check if service is running
                result = subprocess.run(
                    ["pgrep", "-f", service],
                    capture_output=True,
                    text=True
                )
                
                is_running = result.returncode == 0
                services_status[service] = {
                    "running": is_running,
                    "status": "healthy" if is_running else "stopped"
                }
                
                if not is_running:
                    all_healthy = False
                    
            return {
                "services": services_status,
                "status": "healthy" if all_healthy else "warning",
                "all_running": all_healthy
            }
            
        except Exception as e:
            self.logger.error(f"Error checking services: {e}")
            return {"status": "error", "error": str(e)}
            
    def check_log_files(self) -> Dict:
        """Check log file sizes and rotation needs"""
        try:
            log_status = {}
            needs_rotation = False
            
            for log_file in self.logs_dir.glob("*.log"):
                size_mb = log_file.stat().st_size / (1024 * 1024)
                
                log_status[log_file.name] = {
                    "size_mb": round(size_mb, 2),
                    "needs_rotation": size_mb > self.config["log_rotation_threshold_mb"],
                    "status": "healthy" if size_mb <= self.config["log_rotation_threshold_mb"] else "warning"
                }
                
                if size_mb > self.config["log_rotation_threshold_mb"]:
                    needs_rotation = True
                    
            return {
                "logs": log_status,
                "status": "warning" if needs_rotation else "healthy",
                "needs_rotation": needs_rotation
            }
            
        except Exception as e:
            self.logger.error(f"Error checking log files: {e}")
            return {"status": "error", "error": str(e)}
            
    def auto_fix_issues(self, health_results: Dict) -> List[str]:
        """Automatically fix detected issues"""
        fixes_applied = []
        
        if not self.config["auto_fix_enabled"]:
            return fixes_applied
            
        try:
            # Fix log rotation issues
            if health_results.get("logs", {}).get("needs_rotation"):
                self.logger.info("Auto-fixing: Rotating large log files...")
                result = subprocess.run(
                    ["python3", "log_rotation_manager.py", "--rotate"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    fixes_applied.append("Log rotation completed")
                    self.logger.info("✅ Log rotation completed successfully")
                else:
                    self.logger.error(f"❌ Log rotation failed: {result.stderr}")
                    
            # Fix stopped services
            if not health_results.get("services", {}).get("all_running"):
                if self.config["auto_restart_failed_services"]:
                    self.logger.info("Auto-fixing: Restarting failed services...")
                    
                    # Restart background optimization agent
                    if not health_results.get("services", {}).get("services", {}).get("background_optimization_agent.py", {}).get("running"):
                        result = subprocess.run(
                            ["./start_background_optimization_agent.sh"],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            fixes_applied.append("Background optimization agent restarted")
                            self.logger.info("✅ Background optimization agent restarted")
                        else:
                            self.logger.error(f"❌ Failed to restart background agent: {result.stderr}")
                            
            # Fix high memory usage
            if health_results.get("system_resources", {}).get("memory_percent", 0) > self.config["max_memory_usage_percent"]:
                self.logger.info("Auto-fixing: High memory usage detected, restarting optimization system...")
                result = subprocess.run(
                    ["./stop_background_optimization_agent.sh"],
                    capture_output=True,
                    text=True
                )
                time.sleep(5)
                result = subprocess.run(
                    ["./start_background_optimization_agent.sh"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    fixes_applied.append("System restarted due to high memory usage")
                    self.logger.info("✅ System restarted due to high memory usage")
                    
        except Exception as e:
            self.logger.error(f"Error applying auto-fixes: {e}")
            
        return fixes_applied
        
    def run_health_check(self) -> Dict:
        """Run complete health check"""
        self.logger.info("🔍 Running autonomous health check...")
        
        # Check system resources
        system_resources = self.check_system_resources()
        
        # Check required services
        services = self.check_required_services()
        
        # Check log files
        logs = self.check_log_files()
        
        # Determine overall status
        statuses = [system_resources.get("status"), services.get("status"), logs.get("status")]
        if "critical" in statuses:
            overall_status = "critical"
        elif "error" in statuses:
            overall_status = "error"
        elif "warning" in statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"
            
        health_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "system_resources": system_resources,
            "services": services,
            "logs": logs
        }
        
        # Apply auto-fixes if enabled
        if self.config["auto_fix_enabled"]:
            fixes_applied = self.auto_fix_issues(health_results)
            health_results["auto_fixes_applied"] = fixes_applied
            
        # Log results
        self.logger.info(f"📊 Health check completed - Status: {overall_status.upper()}")
        if health_results.get("auto_fixes_applied"):
            self.logger.info(f"🔧 Auto-fixes applied: {', '.join(health_results['auto_fixes_applied'])}")
            
        return health_results
        
    def run_continuous_monitoring(self):
        """Run continuous health monitoring"""
        self.logger.info("🚀 Starting autonomous health monitoring...")
        
        try:
            while True:
                # Run health check
                health_results = self.run_health_check()
                
                # Save health status
                self.health_status = health_results
                
                # Wait for next check
                time.sleep(self.config["health_check_interval"])
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Health monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Error in health monitoring: {e}")
            
    def get_status_report(self) -> str:
        """Get current status report"""
        if not self.health_status.get("timestamp"):
            return "No health check data available"
            
        report = f"""
🏥 ZmartBot Autonomous Health Monitor Status
==========================================
Last Check: {self.health_status.get('timestamp', 'Never')}
Overall Status: {self.health_status.get('overall_status', 'Unknown').upper()}

📊 System Resources:
   CPU: {self.health_status.get('system_resources', {}).get('cpu_percent', 'N/A')}%
   Memory: {self.health_status.get('system_resources', {}).get('memory_percent', 'N/A')}%
   Disk Free: {self.health_status.get('system_resources', {}).get('disk_free_gb', 'N/A')}GB

🔧 Services:
"""
        
        services = self.health_status.get('services', {}).get('services', {})
        for service, status in services.items():
            status_icon = "✅" if status.get('running') else "❌"
            report += f"   {status_icon} {service}: {status.get('status', 'Unknown')}\n"
            
        if self.health_status.get('auto_fixes_applied'):
            report += f"\n🔧 Auto-fixes Applied: {', '.join(self.health_status['auto_fixes_applied'])}\n"
            
        return report

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomous Health Monitor for ZmartBot")
    parser.add_argument("--check", action="store_true", help="Run single health check")
    parser.add_argument("--monitor", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--status", action="store_true", help="Show current status")
    
    args = parser.parse_args()
    
    monitor = AutonomousHealthMonitor()
    
    if args.check:
        results = monitor.run_health_check()
        print(json.dumps(results, indent=2))
    elif args.status:
        print(monitor.get_status_report())
    elif args.monitor:
        monitor.run_continuous_monitoring()
    else:
        # Default: run single check and show status
        monitor.run_health_check()
        print(monitor.get_status_report())

if __name__ == "__main__":
    main()
