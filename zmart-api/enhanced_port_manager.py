#!/usr/bin/env python3
"""
Enhanced Port Manager with Service Registry
Tracks all services and their actual ports to prevent conflicts
"""

import json
import socket
import psutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServicePort:
    """Service port registration"""
    service_name: str
    port: int
    status: str  # running, stopped, allocated
    pid: Optional[int] = None
    started_at: Optional[str] = None
    health_endpoint: Optional[str] = None
    description: Optional[str] = None

class EnhancedPortManager:
    """Enhanced Port Manager with real-time tracking"""

    # Known service port mappings (discovered from running services)
    KNOWN_SERVICES = {
        # Core Services
        "main_api": {"port": 8000, "name": "Main API Server", "health": "/health"},
        "kingfisher_ai": {"port": 8098, "name": "KingFisher AI", "health": "/health"},

        # Services discovered from background processes
        "webhook_manus": {"port": 8555, "name": "Manus Webhook", "health": "/health"},
        "simple_webhook": {"port": 8555, "name": "Simple Webhook", "health": "/health"},
        "simple_riskmetric": {"port": 8556, "name": "Simple RiskMetric", "health": "/health"},
        "enhanced_riskmetric": {"port": 8557, "name": "Enhanced RiskMetric", "health": "/health"},
        "strategy_riskmetric": {"port": 8558, "name": "Strategy RiskMetric", "health": "/health"},
        "mdc_agent": {"port": 8559, "name": "MDC Background Agent", "health": None},

        # Additional discovered ports
        "influxdb": {"port": 8086, "name": "InfluxDB", "health": "/ping"},
        "prometheus": {"port": 9090, "name": "Prometheus", "health": "/-/healthy"},
        "grafana": {"port": 3000, "name": "Grafana", "health": "/api/health"},

        # Database services
        "postgresql": {"port": 5432, "name": "PostgreSQL", "health": None},
        "redis": {"port": 6379, "name": "Redis", "health": None},
        "rabbitmq": {"port": 5672, "name": "RabbitMQ", "health": None},
        "rabbitmq_mgmt": {"port": 15672, "name": "RabbitMQ Management", "health": "/api/health/checks/alarms"},

        # Development/Test ports
        "test_api": {"port": 8888, "name": "Test API", "health": "/health"},
        "dev_server": {"port": 5173, "name": "Vite Dev Server", "health": None},

        # Monitoring dashboards
        "service_dashboard": {"port": 8080, "name": "Service Dashboard", "health": "/health"},
        "port_manager_ui": {"port": 8085, "name": "Port Manager UI", "health": "/health"},
    }

    # Reserved port ranges
    PORT_RANGES = {
        "system": (1, 1023),          # System ports (require root)
        "registered": (1024, 49151),   # User ports
        "dynamic": (49152, 65535),     # Dynamic/private ports
        "zmartbot_api": (8000, 8099), # ZmartBot API services
        "zmartbot_ui": (8100, 8199),  # ZmartBot UI services
        "zmartbot_test": (8800, 8899),# ZmartBot test services
        "zmartbot_internal": (8500, 8599), # Internal services
    }

    def __init__(self, registry_file: str = "port_registry.json"):
        self.registry_file = Path(registry_file)
        self.registry: Dict[int, ServicePort] = {}
        self.load_registry()

    def load_registry(self):
        """Load port registry from file"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    for port_str, service_data in data.items():
                        self.registry[int(port_str)] = ServicePort(**service_data)
                logger.info(f"Loaded {len(self.registry)} port registrations")
            except Exception as e:
                logger.error(f"Error loading registry: {e}")

    def save_registry(self):
        """Save port registry to file"""
        try:
            data = {str(port): asdict(service) for port, service in self.registry.items()}
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Port registry saved")
        except Exception as e:
            logger.error(f"Error saving registry: {e}")

    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is currently in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return False
            except:
                return True

    def get_process_using_port(self, port: int) -> Optional[Tuple[int, str]]:
        """Get process using a specific port"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                try:
                    process = psutil.Process(conn.pid)
                    return conn.pid, process.name()
                except:
                    return conn.pid, "Unknown"
        return None

    def register_service(self, service_name: str, port: int,
                        health_endpoint: Optional[str] = None,
                        description: Optional[str] = None) -> bool:
        """Register a service with its port"""
        # Check if port is already registered
        if port in self.registry:
            existing = self.registry[port]
            if existing.service_name != service_name:
                logger.error(f"Port {port} already registered to {existing.service_name}")
                return False

        # Check if port is actually in use
        if self.is_port_in_use(port):
            process_info = self.get_process_using_port(port)
            pid = process_info[0] if process_info else None
            status = "running"
        else:
            pid = None
            status = "allocated"

        # Register the service
        self.registry[port] = ServicePort(
            service_name=service_name,
            port=port,
            status=status,
            pid=pid,
            started_at=datetime.now().isoformat() if status == "running" else None,
            health_endpoint=health_endpoint,
            description=description
        )

        self.save_registry()
        logger.info(f"Registered {service_name} on port {port} (status: {status})")
        return True

    def unregister_service(self, port: int):
        """Unregister a service port"""
        if port in self.registry:
            service = self.registry[port]
            del self.registry[port]
            self.save_registry()
            logger.info(f"Unregistered {service.service_name} from port {port}")

    def find_free_port(self, range_name: str = "zmartbot_api") -> Optional[int]:
        """Find a free port in the specified range"""
        if range_name not in self.PORT_RANGES:
            logger.error(f"Unknown port range: {range_name}")
            return None

        start, end = self.PORT_RANGES[range_name]
        for port in range(start, end + 1):
            if port not in self.registry and not self.is_port_in_use(port):
                return port
        return None

    def scan_running_services(self) -> Dict[int, str]:
        """Scan for all services running on known ports"""
        running_services = {}

        # Check known service ports
        for service_key, service_info in self.KNOWN_SERVICES.items():
            port = service_info["port"]
            if self.is_port_in_use(port):
                process_info = self.get_process_using_port(port)
                if process_info:
                    running_services[port] = f"{service_info['name']} (PID: {process_info[0]})"
                else:
                    running_services[port] = service_info['name']

        # Scan ZmartBot port ranges
        for range_name in ["zmartbot_api", "zmartbot_internal", "zmartbot_ui"]:
            start, end = self.PORT_RANGES[range_name]
            for port in range(start, min(end + 1, start + 100)):  # Limit scan
                if port not in running_services and self.is_port_in_use(port):
                    process_info = self.get_process_using_port(port)
                    if process_info:
                        running_services[port] = f"Unknown Service (PID: {process_info[0]})"

        return running_services

    def generate_report(self) -> str:
        """Generate a comprehensive port usage report"""
        report = []
        report.append("=" * 60)
        report.append("PORT MANAGER REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        # Scan for running services
        running = self.scan_running_services()

        report.append("RUNNING SERVICES:")
        for port in sorted(running.keys()):
            report.append(f"  Port {port:5}: {running[port]}")
        report.append("")

        report.append("REGISTERED SERVICES:")
        for port in sorted(self.registry.keys()):
            service = self.registry[port]
            status_icon = "✅" if service.status == "running" else "⚠️"
            report.append(f"  {status_icon} Port {port:5}: {service.service_name} ({service.status})")
        report.append("")

        # Port range usage
        report.append("PORT RANGE USAGE:")
        for range_name, (start, end) in self.PORT_RANGES.items():
            used_in_range = sum(1 for p in running.keys() if start <= p <= end)
            report.append(f"  {range_name:20}: {used_in_range} ports in use ({start}-{end})")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

async def main():
    """Main function to run port manager"""
    manager = EnhancedPortManager()

    # Register all known services
    for service_key, service_info in manager.KNOWN_SERVICES.items():
        manager.register_service(
            service_name=service_info["name"],
            port=service_info["port"],
            health_endpoint=service_info.get("health"),
            description=f"ZmartBot {service_info['name']}"
        )

    # Generate and print report
    report = manager.generate_report()
    print(report)

    # Save report to file
    with open("port_manager_report.txt", "w") as f:
        f.write(report)
    print("\n📄 Report saved to: port_manager_report.txt")

    # Save updated registry
    manager.save_registry()
    print("📁 Registry saved to: port_registry.json")

if __name__ == "__main__":
    asyncio.run(main())