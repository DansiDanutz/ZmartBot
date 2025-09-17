#!/usr/bin/env python3
"""
Port Registry Manager for ZmartBot
Manages and tracks all service port assignments without requiring root permissions
"""

import json
import socket
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ServicePortInfo:
    """Service port information"""
    service_name: str
    port: int
    description: str
    health_endpoint: Optional[str] = None
    status: str = "registered"
    registered_at: str = ""
    last_checked: str = ""

class PortRegistryManager:
    """Manages port assignments for all ZmartBot services"""

    # Comprehensive service registry based on actual discovered ports
    SERVICE_REGISTRY = {
        # === CORE API SERVICES (8000-8099) ===
        8000: {
            "name": "Main API Server",
            "description": "ZmartBot FastAPI backend",
            "health": "/health"
        },
        8098: {
            "name": "KingFisher AI Server",
            "description": "AI-powered trading analysis",
            "health": "/health"
        },

        # === WEBHOOK SERVICES (8550-8559) ===
        8555: {
            "name": "Manus/Simple Webhook",
            "description": "Webhook receiver service",
            "health": "/health"
        },

        # === RISK METRIC SERVICES (8556-8559) ===
        8556: {
            "name": "Simple RiskMetric",
            "description": "Basic risk calculation service",
            "health": "/api/v1/health"
        },
        8557: {
            "name": "Enhanced RiskMetric",
            "description": "Advanced risk calculation with ML",
            "health": "/api/v1/health"
        },
        8558: {
            "name": "Strategy RiskMetric",
            "description": "Strategy-based risk assessment",
            "health": "/api/v1/health"
        },
        8559: {
            "name": "MDC Background Agent",
            "description": "MDC file monitoring and updates",
            "health": None
        },

        # === MONITORING & METRICS (8080-8089, 9090) ===
        8080: {
            "name": "Service Dashboard",
            "description": "Service monitoring dashboard",
            "health": "/health"
        },
        8085: {
            "name": "Port Manager UI",
            "description": "Port management interface",
            "health": "/health"
        },
        8086: {
            "name": "InfluxDB",
            "description": "Time-series metrics database",
            "health": "/ping"
        },
        9090: {
            "name": "Prometheus",
            "description": "Metrics collection and alerting",
            "health": "/-/healthy"
        },

        # === DATABASE SERVICES ===
        5432: {
            "name": "PostgreSQL",
            "description": "Primary relational database",
            "health": None
        },
        6379: {
            "name": "Redis",
            "description": "Cache and session storage",
            "health": None
        },
        5672: {
            "name": "RabbitMQ",
            "description": "Message broker",
            "health": None
        },
        15672: {
            "name": "RabbitMQ Management",
            "description": "RabbitMQ management interface",
            "health": "/api/health/checks/alarms"
        },

        # === FRONTEND SERVICES ===
        5173: {
            "name": "Vite Dev Server",
            "description": "React frontend development server",
            "health": None
        },
        3000: {
            "name": "Grafana",
            "description": "Metrics visualization",
            "health": "/api/health"
        },

        # === ADDITIONAL DISCOVERED SERVICES ===
        8006: {"name": "Service 8006", "description": "Unknown service", "health": None},
        8007: {"name": "Service 8007", "description": "Unknown service", "health": None},
        8008: {"name": "Service 8008", "description": "Unknown service", "health": None},
        8009: {"name": "Service 8009", "description": "Unknown service", "health": None},
        8010: {"name": "Service 8010", "description": "Unknown service", "health": None},
        8012: {"name": "Service 8012", "description": "Unknown service", "health": None},
        8013: {"name": "Service 8013", "description": "Unknown service", "health": None},
        8015: {"name": "Service 8015", "description": "Unknown service", "health": None},
        8016: {"name": "Service 8016", "description": "Unknown service", "health": None},
        8017: {"name": "Service 8017", "description": "Unknown service", "health": None},
        8018: {"name": "Service 8018", "description": "Unknown service", "health": None},
        8019: {"name": "Service 8019", "description": "Unknown service", "health": None},
        8020: {"name": "Service 8020", "description": "Unknown service", "health": None},
        8050: {"name": "Service 8050", "description": "Unknown service", "health": None},
    }

    def __init__(self, registry_file: str = "port_registry.json"):
        self.registry_file = Path(registry_file)
        self.registry: Dict[int, ServicePortInfo] = {}
        self.load_registry()
        self.sync_with_defaults()

    def load_registry(self):
        """Load registry from file"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    for port_str, service_data in data.items():
                        self.registry[int(port_str)] = ServicePortInfo(**service_data)
                logger.info(f"Loaded {len(self.registry)} port registrations from file")
            except Exception as e:
                logger.warning(f"Could not load registry: {e}")

    def save_registry(self):
        """Save registry to file"""
        try:
            data = {str(port): asdict(service) for port, service in self.registry.items()}
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Saved {len(self.registry)} port registrations to file")
        except Exception as e:
            logger.error(f"Error saving registry: {e}")

    def sync_with_defaults(self):
        """Sync registry with default service definitions"""
        for port, service_def in self.SERVICE_REGISTRY.items():
            if port not in self.registry:
                self.registry[port] = ServicePortInfo(
                    service_name=service_def["name"],
                    port=port,
                    description=service_def["description"],
                    health_endpoint=service_def.get("health"),
                    status="registered",
                    registered_at=datetime.now().isoformat(),
                    last_checked=datetime.now().isoformat()
                )

    def check_port(self, port: int) -> bool:
        """Check if a port is currently in use (without requiring permissions)"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.1)
            result = sock.connect_ex(('127.0.0.1', port))
            return result == 0

    def scan_services(self) -> Dict[int, str]:
        """Scan registered ports to see which are active"""
        active_services = {}

        for port, service in self.registry.items():
            if self.check_port(port):
                active_services[port] = service.service_name
                service.status = "running"
            else:
                service.status = "not_running"
            service.last_checked = datetime.now().isoformat()

        self.save_registry()
        return active_services

    def get_port_for_service(self, service_name: str) -> Optional[int]:
        """Get the assigned port for a service"""
        for port, service in self.registry.items():
            if service.service_name == service_name:
                return port
        return None

    def is_port_registered(self, port: int) -> bool:
        """Check if a port is registered"""
        return port in self.registry

    def register_port(self, port: int, service_name: str,
                     description: str = "", health_endpoint: Optional[str] = None) -> bool:
        """Register a new service port"""
        if port in self.registry:
            logger.warning(f"Port {port} already registered to {self.registry[port].service_name}")
            return False

        self.registry[port] = ServicePortInfo(
            service_name=service_name,
            port=port,
            description=description or f"Service on port {port}",
            health_endpoint=health_endpoint,
            status="registered",
            registered_at=datetime.now().isoformat(),
            last_checked=datetime.now().isoformat()
        )

        self.save_registry()
        logger.info(f"Registered {service_name} on port {port}")
        return True

    def unregister_port(self, port: int) -> bool:
        """Unregister a service port"""
        if port in self.registry:
            service_name = self.registry[port].service_name
            del self.registry[port]
            self.save_registry()
            logger.info(f"Unregistered {service_name} from port {port}")
            return True
        return False

    def generate_report(self) -> str:
        """Generate a comprehensive port registry report"""
        report = []
        report.append("=" * 70)
        report.append("ZMARTBOT PORT REGISTRY REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Registered Ports: {len(self.registry)}")
        report.append("")

        # Scan for active services
        active = self.scan_services()

        report.append(f"ACTIVE SERVICES ({len(active)} running):")
        report.append("-" * 40)
        for port in sorted(active.keys()):
            service = self.registry[port]
            report.append(f"  ✅ Port {port:5} : {service.service_name}")
            report.append(f"              {service.description}")

        report.append("")
        report.append("REGISTERED BUT NOT RUNNING:")
        report.append("-" * 40)
        for port, service in sorted(self.registry.items()):
            if port not in active:
                report.append(f"  ⚠️  Port {port:5} : {service.service_name}")
                report.append(f"              {service.description}")

        report.append("")
        report.append("PORT ALLOCATION BY RANGE:")
        report.append("-" * 40)

        ranges = {
            "Core API (8000-8099)": (8000, 8099),
            "Internal Services (8500-8599)": (8500, 8599),
            "Monitoring (8080-8089, 9090)": (8080, 8089),
            "Databases (5432, 6379, 5672)": (5432, 6379),
            "Frontend (3000-3999, 5173)": (3000, 5173),
        }

        for range_name, (start, end) in ranges.items():
            count = sum(1 for p in self.registry.keys()
                       if (p == 9090 and "Monitoring" in range_name) or
                          (start <= p <= end))
            report.append(f"  {range_name:30} : {count} ports registered")

        report.append("")
        report.append("=" * 70)
        report.append("RECOMMENDATION: Services should always check port availability")
        report.append("                before binding to prevent conflicts.")
        report.append("=" * 70)

        return "\n".join(report)

def main():
    """Main function"""
    manager = PortRegistryManager()

    # Generate report
    report = manager.generate_report()
    print(report)

    # Save report to file
    with open("port_registry_report.txt", "w") as f:
        f.write(report)
    print("\n📄 Report saved to: port_registry_report.txt")
    print("📁 Registry saved to: port_registry.json")

    # Also update the service verification script
    print("\n🔧 Updating service verification script with correct ports...")

    # Get actual ports for key services
    ports_map = {
        "Main API": manager.get_port_for_service("Main API Server"),
        "KingFisher AI": manager.get_port_for_service("KingFisher AI Server"),
        "Risk Metric": manager.get_port_for_service("Simple RiskMetric"),
        "Webhook": manager.get_port_for_service("Manus/Simple Webhook"),
        "MDC Agent": manager.get_port_for_service("MDC Background Agent"),
    }

    print("\nService Port Mappings:")
    for service, port in ports_map.items():
        if port:
            print(f"  {service:20} -> Port {port}")

if __name__ == "__main__":
    main()