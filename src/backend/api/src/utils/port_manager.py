#!/usr/bin/env python3
"""
Port Manager for ZmartBot Platform
Centralized port management to prevent conflicts and ensure proper service isolation
"""
import socket
import subprocess
import logging
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """Service types in the ZmartBot ecosystem"""
    API_SERVER = "api_server"
    FRONTEND = "frontend"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    TIME_SERIES_DB = "time_series_db"
    MONITORING = "monitoring"
    VISUALIZATION = "visualization"
    PROXY = "proxy"

@dataclass
class PortConfig:
    """Port configuration for a service"""
    service_name: str
    service_type: ServiceType
    default_port: int
    description: str
    protocol: str = "tcp"
    allow_dynamic: bool = True
    env_var: Optional[str] = None

class PortManager:
    """Manages port allocations for all ZmartBot services"""
    
    # Default port configurations for all services
    PORT_CONFIGS = {
        # Core Services
        "zmart_api": PortConfig(
            service_name="ZmartBot API",
            service_type=ServiceType.API_SERVER,
            default_port=8000,
            description="Main FastAPI backend server",
            env_var="PORT"
        ),
        "frontend": PortConfig(
            service_name="Frontend Dashboard",
            service_type=ServiceType.FRONTEND,
            default_port=5173,
            description="Vite React frontend",
            env_var="VITE_PORT"
        ),
        
        # Databases
        "postgresql": PortConfig(
            service_name="PostgreSQL",
            service_type=ServiceType.DATABASE,
            default_port=5432,
            description="Primary relational database",
            env_var="DB_PORT"
        ),
        "redis": PortConfig(
            service_name="Redis",
            service_type=ServiceType.CACHE,
            default_port=6379,
            description="Cache and session storage",
            env_var="REDIS_PORT"
        ),
        "influxdb": PortConfig(
            service_name="InfluxDB",
            service_type=ServiceType.TIME_SERIES_DB,
            default_port=8086,
            description="Time-series metrics database",
            env_var="INFLUX_PORT"
        ),
        
        # Message Queue
        "rabbitmq": PortConfig(
            service_name="RabbitMQ",
            service_type=ServiceType.MESSAGE_QUEUE,
            default_port=5672,
            description="Message broker",
            env_var="RABBITMQ_PORT"
        ),
        "rabbitmq_management": PortConfig(
            service_name="RabbitMQ Management",
            service_type=ServiceType.MESSAGE_QUEUE,
            default_port=15672,
            description="RabbitMQ management UI",
            env_var="RABBITMQ_MANAGEMENT_PORT"
        ),
        
        # Monitoring & Visualization
        "prometheus": PortConfig(
            service_name="Prometheus",
            service_type=ServiceType.MONITORING,
            default_port=9090,
            description="Metrics collection",
            env_var="PROMETHEUS_PORT"
        ),
        "grafana": PortConfig(
            service_name="Grafana",
            service_type=ServiceType.VISUALIZATION,
            default_port=3000,
            description="Metrics visualization dashboards",
            env_var="GRAFANA_PORT"
        ),
        
        # Proxy & Additional Services
        "nginx_http": PortConfig(
            service_name="Nginx HTTP",
            service_type=ServiceType.PROXY,
            default_port=80,
            description="HTTP reverse proxy",
            allow_dynamic=False
        ),
        "nginx_https": PortConfig(
            service_name="Nginx HTTPS",
            service_type=ServiceType.PROXY,
            default_port=443,
            description="HTTPS reverse proxy",
            allow_dynamic=False
        ),
        
        # Additional API Services (if KingFisher runs separately)
        "kingfisher_api": PortConfig(
            service_name="KingFisher API",
            service_type=ServiceType.API_SERVER,
            default_port=8001,
            description="KingFisher image analysis API",
            env_var="KINGFISHER_PORT"
        ),
        
        # Development/Testing Ports
        "test_api": PortConfig(
            service_name="Test API",
            service_type=ServiceType.API_SERVER,
            default_port=8888,
            description="Test server for development",
            env_var="TEST_PORT"
        ),
    }
    
    def __init__(self):
        self.allocated_ports: Dict[str, int] = {}
        self.load_from_environment()
    
    def load_from_environment(self):
        """Load port configurations from environment variables"""
        for key, config in self.PORT_CONFIGS.items():
            if config.env_var and config.env_var in os.environ:
                try:
                    port = int(os.environ[config.env_var])
                    self.allocated_ports[key] = port
                    logger.info(f"Loaded {config.service_name} port from env: {port}")
                except ValueError:
                    logger.warning(f"Invalid port value for {config.env_var}: {os.environ[config.env_var]}")
    
    def is_port_available(self, port: int, host: str = "0.0.0.0") -> bool:
        """Check if a port is available for binding"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((host, port))
                return True
        except socket.error:
            return False
    
    def get_process_using_port(self, port: int) -> Optional[str]:
        """Get process information using a specific port"""
        try:
            result = subprocess.run(
                ['lsof', '-i', f':{port}'],
                capture_output=True,
                text=True
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return lines[1]  # Return first process (skip header)
            return None
        except Exception as e:
            logger.error(f"Error checking port {port}: {e}")
            return None
    
    def find_available_port(self, start: int = 8000, end: int = 9000) -> Optional[int]:
        """Find an available port in the specified range"""
        for port in range(start, end):
            if self.is_port_available(port):
                return port
        return None
    
    def allocate_port(self, service_key: str, preferred_port: Optional[int] = None) -> Tuple[int, bool]:
        """
        Allocate a port for a service
        Returns: (port, is_conflict)
        """
        if service_key not in self.PORT_CONFIGS:
            raise ValueError(f"Unknown service: {service_key}")
        
        config = self.PORT_CONFIGS[service_key]
        
        # Check if already allocated
        if service_key in self.allocated_ports:
            return self.allocated_ports[service_key], False
        
        # Use preferred port if provided
        if preferred_port:
            if self.is_port_available(preferred_port):
                self.allocated_ports[service_key] = preferred_port
                return preferred_port, False
            else:
                if config.allow_dynamic:
                    # Find alternative port
                    new_port = self.find_available_port(preferred_port + 1, preferred_port + 100)
                    if new_port:
                        self.allocated_ports[service_key] = new_port
                        logger.warning(f"Port {preferred_port} in use, allocated {new_port} for {config.service_name}")
                        return new_port, True
                return preferred_port, True
        
        # Use default port
        default_port = config.default_port
        if self.is_port_available(default_port):
            self.allocated_ports[service_key] = default_port
            return default_port, False
        else:
            if config.allow_dynamic:
                # Find alternative port
                new_port = self.find_available_port(default_port + 1, default_port + 100)
                if new_port:
                    self.allocated_ports[service_key] = new_port
                    logger.warning(f"Default port {default_port} in use, allocated {new_port} for {config.service_name}")
                    return new_port, True
            return default_port, True
    
    def check_all_ports(self) -> Dict[str, Dict]:
        """Check status of all configured ports"""
        status = {}
        for key, config in self.PORT_CONFIGS.items():
            port = self.allocated_ports.get(key, config.default_port)
            available = self.is_port_available(port)
            process = None if available else self.get_process_using_port(port)
            
            status[key] = {
                "service": config.service_name,
                "port": port,
                "available": available,
                "process": process,
                "type": config.service_type.value,
                "description": config.description
            }
        return status
    
    def kill_process_on_port(self, port: int) -> bool:
        """Kill process using a specific port (requires appropriate permissions)"""
        try:
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True
            )
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(['kill', '-9', pid])
                logger.info(f"Killed processes on port {port}: {pids}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error killing process on port {port}: {e}")
            return False
    
    def get_port_summary(self) -> str:
        """Get a formatted summary of port allocations"""
        lines = ["=" * 80]
        lines.append("ZMARTBOT PORT ALLOCATION SUMMARY")
        lines.append("=" * 80)
        
        status = self.check_all_ports()
        
        # Group by service type
        by_type = {}
        for key, info in status.items():
            service_type = info['type']
            if service_type not in by_type:
                by_type[service_type] = []
            by_type[service_type].append((key, info))
        
        for service_type, services in by_type.items():
            lines.append(f"\n{service_type.upper().replace('_', ' ')}:")
            lines.append("-" * 40)
            
            for key, info in services:
                status_emoji = "✅" if info['available'] else "❌"
                line = f"{status_emoji} {info['service']:25} Port {info['port']:5}"
                if not info['available'] and info['process']:
                    line += f" (IN USE)"
                lines.append(line)
        
        lines.append("\n" + "=" * 80)
        
        # Add conflict summary
        conflicts = [info for info in status.values() if not info['available']]
        if conflicts:
            lines.append(f"⚠️  PORT CONFLICTS DETECTED: {len(conflicts)}")
            lines.append("Run 'python -m src.utils.port_manager --fix' to resolve")
        else:
            lines.append("✅ No port conflicts detected")
        
        lines.append("=" * 80)
        return "\n".join(lines)
    
    def write_env_file(self, filepath: str = ".env.ports"):
        """Write port allocations to environment file"""
        lines = [
            "# ZmartBot Port Configuration",
            "# Auto-generated by PortManager",
            ""
        ]
        
        for key, config in self.PORT_CONFIGS.items():
            if config.env_var:
                port = self.allocated_ports.get(key, config.default_port)
                lines.append(f"# {config.service_name} - {config.description}")
                lines.append(f"{config.env_var}={port}")
                lines.append("")
        
        with open(filepath, 'w') as f:
            f.write("\n".join(lines))
        
        logger.info(f"Port configuration written to {filepath}")

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ZmartBot Port Manager")
    parser.add_argument("--check", action="store_true", help="Check all port statuses")
    parser.add_argument("--fix", action="store_true", help="Fix port conflicts")
    parser.add_argument("--export", help="Export port config to file")
    parser.add_argument("--kill", type=int, help="Kill process on specific port")
    
    args = parser.parse_args()
    
    manager = PortManager()
    
    if args.check:
        print(manager.get_port_summary())
    
    elif args.fix:
        status = manager.check_all_ports()
        conflicts = [(k, v) for k, v in status.items() if not v['available']]
        
        if not conflicts:
            print("✅ No port conflicts to fix")
        else:
            print(f"Found {len(conflicts)} port conflicts")
            for key, info in conflicts:
                print(f"Fixing {info['service']} on port {info['port']}...")
                manager.kill_process_on_port(info['port'])
            print("✅ Port conflicts resolved")
    
    elif args.export:
        manager.write_env_file(args.export)
        print(f"✅ Port configuration exported to {args.export}")
    
    elif args.kill:
        if manager.kill_process_on_port(args.kill):
            print(f"✅ Killed process on port {args.kill}")
        else:
            print(f"❌ No process found on port {args.kill}")
    
    else:
        print(manager.get_port_summary())