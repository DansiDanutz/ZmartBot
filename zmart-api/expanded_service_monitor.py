#!/usr/bin/env python3
"""
Expanded Service Monitor
Comprehensive monitoring for all ZmartBot services and components
"""

import json
import logging
import requests
import psutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

@dataclass
class ServiceHealth:
    """Service health status"""
    name: str
    port: int
    status: str
    response_time: float
    last_check: str
    error_count: int
    uptime: Optional[str] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None

class ExpandedServiceMonitor:
    """Monitor all ZmartBot services comprehensively"""
    
    def __init__(self, config_file="expanded_monitoring_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.logger = self.setup_logger()
        self.console = Console()
        
        # Service definitions
        self.services = {
            "zmart-api": {"port": 8000, "health_endpoint": "/health"},
            "zmart-dashboard": {"port": 3400, "health_endpoint": "/health"},
            "service-dashboard": {"port": 3000, "health_endpoint": "/health"},
            "kucoin": {"port": 8302, "health_endpoint": "/health"},
            "binance": {"port": 8303, "health_endpoint": "/health"},
            "test-service": {"port": 8301, "health_endpoint": "/health"},
            "api-keys-manager": {"port": 8006, "health_endpoint": "/health"},
            "port-manager": {"port": 8050, "health_endpoint": "/health"},
            "master-orchestration": {"port": 8002, "health_endpoint": "/health"},
            "service-discovery": {"port": 8550, "health_endpoint": "/health"},
            "mdc-dashboard": {"port": 8090, "health_endpoint": "/health"},
            "certification": {"port": 8901, "health_endpoint": "/health"},
            "system-protection": {"port": 8999, "health_endpoint": "/health"},
            "optimization-claude": {"port": 8080, "health_endpoint": "/health"},
            "snapshot-service": {"port": 8085, "health_endpoint": "/health"},
            "passport-service": {"port": 8620, "health_endpoint": "/health"},
            "doctor-service": {"port": 8700, "health_endpoint": "/health"},
            "servicelog-service": {"port": 8750, "health_endpoint": "/health"},
            "mdc-orchestration": {"port": 8615, "health_endpoint": "/health"},
            "zmart-analytics": {"port": 8007, "health_endpoint": "/health"},
            "zmart-backtesting": {"port": 8013, "health_endpoint": "/health"},
            "zmart-data-warehouse": {"port": 8015, "health_endpoint": "/health"},
            "zmart-machine-learning": {"port": 8014, "health_endpoint": "/health"},
            "zmart-risk-management": {"port": 8010, "health_endpoint": "/health"},
            "zmart-notification": {"port": 8008, "health_endpoint": "/health"},
            "zmart-websocket": {"port": 8009, "health_endpoint": "/health"},
            "zmart-alert-system": {"port": 8012, "health_endpoint": "/health"},
            "zmart-technical-analysis": {"port": 8011, "health_endpoint": "/health"},
            "my-symbols-extended": {"port": 8005, "health_endpoint": "/health"},
            "mysymbols": {"port": 8201, "health_endpoint": "/health"}
        }
    
    def setup_logger(self):
        """Setup monitoring logging"""
        logger = logging.getLogger('expanded_service_monitor')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('expanded_service_monitor.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def load_config(self):
        """Load monitoring configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        # Default configuration
        default_config = {
            "check_interval": 30,
            "timeout": 5,
            "retry_count": 3,
            "alert_threshold": 3,
            "monitoring_enabled": True,
            "services_to_monitor": [
                {"name": "KuCoinService", "url": "http://localhost:8302/health", "type": "http"},
                {"name": "CryptometerService", "url": "http://localhost:8303/health", "type": "http"},
                {"name": "MasterOrchestrationAgent", "url": "http://localhost:8000/health", "type": "http"},
                {"name": "APIKeysManagerService", "url": "http://localhost:8006/health", "type": "http"},
                {"name": "MDCFileCreator", "url": "http://localhost:8007/health", "type": "http"}
            ],
            "performance_tracking": True,
            "resource_monitoring": True
        }
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config):
        """Save monitoring configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def check_service_health(self, service_name: str, service_config: Dict) -> ServiceHealth:
        """Check health of a specific service"""
        port = service_config["port"]
        health_endpoint = service_config.get("health_endpoint", "/health")
        
        start_time = time.time()
        status = "UNKNOWN"
        error_count = 0
        
        try:
            # Check if port is listening
            if not self.is_port_listening(port):
                status = "DOWN"
                error_count = 1
            else:
                # Try health endpoint
                try:
                    response = requests.get(
                        f"http://localhost:{port}{health_endpoint}",
                        timeout=self.config["timeout"]
                    )
                    
                    if response.status_code == 200:
                        status = "HEALTHY"
                        response_time = (time.time() - start_time) * 1000
                    else:
                        status = "UNHEALTHY"
                        error_count = 1
                        response_time = (time.time() - start_time) * 1000
                        
                except requests.exceptions.RequestException:
                    status = "UNREACHABLE"
                    error_count = 1
                    response_time = (time.time() - start_time) * 1000
            
            # Get process information
            process_info = self.get_process_info(port)
            
            return ServiceHealth(
                name=service_name,
                port=port,
                status=status,
                response_time=response_time if 'response_time' in locals() else 0,
                last_check=datetime.now().isoformat(),
                error_count=error_count,
                uptime=process_info.get("uptime"),
                memory_usage=process_info.get("memory_usage"),
                cpu_usage=process_info.get("cpu_usage")
            )
            
        except Exception as e:
            self.logger.error(f"Error checking {service_name}: {e}")
            return ServiceHealth(
                name=service_name,
                port=port,
                status="ERROR",
                response_time=0,
                last_check=datetime.now().isoformat(),
                error_count=1
            )
    
    def is_port_listening(self, port: int) -> bool:
        """Check if a port is listening"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
            return False
        except Exception:
            return False
    
    def get_process_info(self, port: int) -> Dict:
        """Get process information for a service"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    try:
                        process = psutil.Process(conn.pid)
                        return {
                            "uptime": str(datetime.now() - datetime.fromtimestamp(process.create_time())),
                            "memory_usage": process.memory_percent(),
                            "cpu_usage": process.cpu_percent()
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            return {}
        except Exception:
            return {}
    
    def check_all_services(self) -> Dict[str, ServiceHealth]:
        """Check health of all services"""
        self.logger.info("Starting comprehensive service health check")
        
        health_status = {}
        services_to_check = self.config.get("services_to_monitor", list(self.services.keys()))
        
        for service_name in services_to_check:
            if service_name in self.services:
                service_config = self.services[service_name]
                health_status[service_name] = self.check_service_health(service_name, service_config)
        
        return health_status
    
    def generate_health_report(self, health_status: Dict[str, ServiceHealth]) -> Dict:
        """Generate comprehensive health report"""
        total_services = len(health_status)
        healthy_services = sum(1 for health in health_status.values() if health.status == "HEALTHY")
        unhealthy_services = sum(1 for health in health_status.values() if health.status in ["UNHEALTHY", "DOWN", "UNREACHABLE", "ERROR"])
        warning_services = sum(1 for health in health_status.values() if health.status == "WARNING")
        
        # Calculate average response time
        response_times = [health.response_time for health in health_status.values() if health.response_time > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Calculate total error count
        total_errors = sum(health.error_count for health in health_status.values())
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_services": total_services,
                "healthy_services": healthy_services,
                "unhealthy_services": unhealthy_services,
                "warning_services": warning_services,
                "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
                "average_response_time": avg_response_time,
                "total_errors": total_errors
            },
            "services": {
                name: {
                    "name": health.name,
                    "port": health.port,
                    "status": health.status,
                    "response_time": health.response_time,
                    "last_check": health.last_check,
                    "error_count": health.error_count,
                    "uptime": health.uptime,
                    "memory_usage": health.memory_usage,
                    "cpu_usage": health.cpu_usage
                }
                for name, health in health_status.items()
            }
        }
    
    def send_health_alerts(self, health_status: Dict[str, ServiceHealth]):
        """Send alerts for unhealthy services"""
        try:
            from mdc_alert_handler import alert_handler
            
            for service_name, health in health_status.items():
                if health.status in ["UNHEALTHY", "DOWN", "UNREACHABLE", "ERROR"]:
                    alert_handler.send_alert(
                        "SERVICE_HEALTH",
                        f"Service {service_name} (port {health.port}) is {health.status}",
                        "CRITICAL"
                    )
                elif health.error_count > self.config.get("alert_threshold", 3):
                    alert_handler.send_alert(
                        "SERVICE_ERRORS",
                        f"Service {service_name} has {health.error_count} errors",
                        "WARNING"
                    )
        except Exception as e:
            self.logger.error(f"Failed to send health alerts: {e}")
    
    def create_health_dashboard(self, health_status: Dict[str, ServiceHealth]):
        """Create visual health dashboard"""
        # Summary panel
        total_services = len(health_status)
        healthy_services = sum(1 for health in health_status.values() if health.status == "HEALTHY")
        health_percentage = (healthy_services / total_services * 100) if total_services > 0 else 0
        
        summary_text = f"Services: {healthy_services}/{total_services} healthy ({health_percentage:.1f}%)"
        summary_panel = Panel(
            summary_text,
            title="[bold blue]Service Health Summary[/bold blue]",
            border_style="green" if health_percentage > 80 else "yellow" if health_percentage > 60 else "red"
        )
        
        # Services table
        table = Table(title="Service Health Status")
        table.add_column("Service", style="cyan")
        table.add_column("Port", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Response Time", style="yellow")
        table.add_column("Errors", style="red")
        table.add_column("Uptime", style="blue")
        
        for health in health_status.values():
            status_style = {
                "HEALTHY": "green",
                "UNHEALTHY": "yellow",
                "DOWN": "red",
                "UNREACHABLE": "red",
                "ERROR": "red"
            }.get(health.status, "white")
            
            table.add_row(
                health.name,
                str(health.port),
                f"[{status_style}]{health.status}[/{status_style}]",
                f"{health.response_time:.1f}ms" if health.response_time > 0 else "N/A",
                str(health.error_count),
                health.uptime or "N/A"
            )
        
        return summary_panel, table
    
    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        self.logger.info("Starting monitoring cycle")
        
        # Check all services
        health_status = self.check_all_services()
        
        # Generate report
        report = self.generate_health_report(health_status)
        
        # Send alerts if needed
        self.send_health_alerts(health_status)
        
        # Save report
        report_file = Path("service_health_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Display dashboard
        summary_panel, table = self.create_health_dashboard(health_status)
        self.console.print(summary_panel)
        self.console.print(table)
        
        self.logger.info(f"Monitoring cycle complete: {report['summary']['health_percentage']:.1f}% healthy")
        
        return report

# Global service monitor instance
service_monitor = ExpandedServiceMonitor()

if __name__ == "__main__":
    # Run monitoring cycle
    monitor = ExpandedServiceMonitor()
    report = monitor.run_monitoring_cycle()
    
    print(f"\n📊 Monitoring Results:")
    print(f"   Total Services: {report['summary']['total_services']}")
    print(f"   Healthy: {report['summary']['healthy_services']}")
    print(f"   Unhealthy: {report['summary']['unhealthy_services']}")
    print(f"   Health Percentage: {report['summary']['health_percentage']:.1f}%")
    print(f"   Average Response Time: {report['summary']['average_response_time']:.1f}ms")
