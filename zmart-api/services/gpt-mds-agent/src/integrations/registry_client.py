"""
Registry Client - ZmartBot Service Integration
=============================================
Handles connections to ZmartBot service registry and port management
"""

import aiohttp
import asyncio
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog
from aiohttp import ClientTimeout

logger = structlog.get_logger()

@dataclass
class ServiceInfo:
    """Service information from registry"""
    service_name: str
    service_type: str
    port: int
    status: str
    passport_id: Optional[str] = None
    description: Optional[str] = None
    registered_at: Optional[str] = None
    last_seen: Optional[str] = None
    health_url: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PortAssignment:
    """Port assignment information"""
    service_name: str
    port: int
    service_type: str
    status: str
    assigned_at: Optional[str] = None
    pid: Optional[int] = None

class RegistryClient:
    """
    Client for ZmartBot service registry integration
    """
    
    def __init__(self, 
                 registry_url: str = "http://localhost:8610",
                 port_db_path: str = "port_registry.db",
                 service_db_path: str = "src/data/service_registry.db"):
        self.registry_url = registry_url.rstrip('/')
        self.port_db_path = Path(port_db_path)
        self.service_db_path = Path(service_db_path)
        self.session = None
        self.connection_stats = {
            "successful_requests": 0,
            "failed_requests": 0,
            "total_requests": 0,
            "last_connection": None
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Initialize HTTP session"""
        if self.session is None:
            timeout = ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.info("Registry client connected", url=self.registry_url)
    
    async def disconnect(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Registry client disconnected")
    
    async def health_check(self) -> bool:
        """Check if registry is accessible"""
        try:
            await self.connect()
            async with self.session.get(f"{self.registry_url}/health") as response:
                if response.status == 200:
                    self.connection_stats["successful_requests"] += 1
                    self.connection_stats["last_connection"] = datetime.now().isoformat()
                    return True
                else:
                    self.connection_stats["failed_requests"] += 1
                    return False
        except Exception as e:
            self.connection_stats["failed_requests"] += 1
            logger.error("Registry health check failed", error=str(e))
            return False
        finally:
            self.connection_stats["total_requests"] += 1
    
    async def get_all_services(self) -> List[ServiceInfo]:
        """Get all registered services from registry"""
        try:
            await self.connect()
            async with self.session.get(f"{self.registry_url}/services") as response:
                if response.status == 200:
                    data = await response.json()
                    services = []
                    
                    for service_data in data.get("services", []):
                        service = ServiceInfo(
                            service_name=service_data.get("service_name", ""),
                            service_type=service_data.get("service_type", "unknown"),
                            port=service_data.get("port", 0),
                            status=service_data.get("status", "unknown"),
                            passport_id=service_data.get("passport_id"),
                            description=service_data.get("description"),
                            registered_at=service_data.get("registered_at"),
                            last_seen=service_data.get("last_seen"),
                            health_url=service_data.get("health_url"),
                            dependencies=service_data.get("dependencies", []),
                            tags=service_data.get("tags", []),
                            metadata=service_data.get("metadata", {})
                        )
                        services.append(service)
                    
                    self.connection_stats["successful_requests"] += 1
                    logger.info("Retrieved services from registry", count=len(services))
                    return services
                else:
                    self.connection_stats["failed_requests"] += 1
                    logger.error("Failed to get services", status=response.status)
                    return []
                    
        except Exception as e:
            self.connection_stats["failed_requests"] += 1
            logger.error("Error getting services", error=str(e))
            return []
        finally:
            self.connection_stats["total_requests"] += 1
    
    async def get_service_by_name(self, service_name: str) -> Optional[ServiceInfo]:
        """Get specific service by name"""
        try:
            await self.connect()
            async with self.session.get(f"{self.registry_url}/services/{service_name}") as response:
                if response.status == 200:
                    service_data = await response.json()
                    service = ServiceInfo(
                        service_name=service_data.get("service_name", ""),
                        service_type=service_data.get("service_type", "unknown"),
                        port=service_data.get("port", 0),
                        status=service_data.get("status", "unknown"),
                        passport_id=service_data.get("passport_id"),
                        description=service_data.get("description"),
                        registered_at=service_data.get("registered_at"),
                        last_seen=service_data.get("last_seen"),
                        health_url=service_data.get("health_url"),
                        dependencies=service_data.get("dependencies", []),
                        tags=service_data.get("tags", []),
                        metadata=service_data.get("metadata", {})
                    )
                    
                    self.connection_stats["successful_requests"] += 1
                    logger.info("Retrieved service", name=service_name)
                    return service
                else:
                    self.connection_stats["failed_requests"] += 1
                    logger.warning("Service not found", name=service_name, status=response.status)
                    return None
                    
        except Exception as e:
            self.connection_stats["failed_requests"] += 1
            logger.error("Error getting service", name=service_name, error=str(e))
            return None
        finally:
            self.connection_stats["total_requests"] += 1
    
    async def register_service(self, service_info: ServiceInfo) -> bool:
        """Register a new service"""
        try:
            await self.connect()
            payload = {
                "service_name": service_info.service_name,
                "service_type": service_info.service_type,
                "port": service_info.port,
                "status": service_info.status,
                "passport_id": service_info.passport_id,
                "description": service_info.description,
                "health_url": service_info.health_url,
                "dependencies": service_info.dependencies,
                "tags": service_info.tags,
                "metadata": service_info.metadata
            }
            
            async with self.session.post(f"{self.registry_url}/services", json=payload) as response:
                if response.status in [200, 201]:
                    self.connection_stats["successful_requests"] += 1
                    logger.info("Service registered", name=service_info.service_name)
                    return True
                else:
                    self.connection_stats["failed_requests"] += 1
                    error_data = await response.text()
                    logger.error("Failed to register service", 
                               name=service_info.service_name,
                               status=response.status,
                               error=error_data)
                    return False
                    
        except Exception as e:
            self.connection_stats["failed_requests"] += 1
            logger.error("Error registering service", 
                        name=service_info.service_name,
                        error=str(e))
            return False
        finally:
            self.connection_stats["total_requests"] += 1
    
    async def update_service_status(self, service_name: str, status: str) -> bool:
        """Update service status"""
        try:
            await self.connect()
            payload = {"status": status}
            
            async with self.session.patch(f"{self.registry_url}/services/{service_name}", 
                                        json=payload) as response:
                if response.status == 200:
                    self.connection_stats["successful_requests"] += 1
                    logger.info("Service status updated", name=service_name, status=status)
                    return True
                else:
                    self.connection_stats["failed_requests"] += 1
                    logger.error("Failed to update service status", 
                               name=service_name,
                               status=response.status)
                    return False
                    
        except Exception as e:
            self.connection_stats["failed_requests"] += 1
            logger.error("Error updating service status", 
                        name=service_name,
                        error=str(e))
            return False
        finally:
            self.connection_stats["total_requests"] += 1

class PortManagerClient:
    """
    Client for ZmartBot port management integration
    """
    
    def __init__(self, port_db_path: str = "port_registry.db"):
        self.port_db_path = Path(port_db_path)
        
    def get_all_port_assignments(self) -> List[PortAssignment]:
        """Get all port assignments from database"""
        try:
            if not self.port_db_path.exists():
                logger.warning("Port registry database not found", path=str(self.port_db_path))
                return []
            
            conn = sqlite3.connect(self.port_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, port, service_type, status, assigned_at, pid
                FROM port_assignments
                ORDER BY service_name
            """)
            
            assignments = []
            for row in cursor.fetchall():
                assignment = PortAssignment(
                    service_name=row[0],
                    port=row[1],
                    service_type=row[2],
                    status=row[3],
                    assigned_at=row[4],
                    pid=row[5]
                )
                assignments.append(assignment)
            
            conn.close()
            logger.info("Retrieved port assignments", count=len(assignments))
            return assignments
            
        except Exception as e:
            logger.error("Error getting port assignments", error=str(e))
            return []
    
    def get_service_port(self, service_name: str) -> Optional[int]:
        """Get port for specific service"""
        try:
            if not self.port_db_path.exists():
                return None
            
            conn = sqlite3.connect(self.port_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT port FROM port_assignments 
                WHERE service_name = ? AND status = 'active'
            """, (service_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                logger.info("Found port for service", name=service_name, port=result[0])
                return result[0]
            else:
                logger.warning("No port found for service", name=service_name)
                return None
                
        except Exception as e:
            logger.error("Error getting service port", name=service_name, error=str(e))
            return None
    
    def assign_port(self, service_name: str, preferred_port: Optional[int] = None) -> Optional[int]:
        """Assign a port to a service"""
        try:
            if not self.port_db_path.exists():
                logger.error("Port registry database not found")
                return None
            
            conn = sqlite3.connect(self.port_db_path)
            cursor = conn.cursor()
            
            # Check if service already has a port
            cursor.execute("""
                SELECT port FROM port_assignments 
                WHERE service_name = ?
            """, (service_name,))
            
            existing = cursor.fetchone()
            if existing:
                logger.info("Service already has port", name=service_name, port=existing[0])
                conn.close()
                return existing[0]
            
            # Find available port
            if preferred_port:
                # Check if preferred port is available
                cursor.execute("""
                    SELECT service_name FROM port_assignments 
                    WHERE port = ? AND status = 'active'
                """, (preferred_port,))
                
                if not cursor.fetchone():
                    assigned_port = preferred_port
                else:
                    assigned_port = self._find_next_available_port(cursor, preferred_port)
            else:
                assigned_port = self._find_next_available_port(cursor)
            
            # Assign the port
            cursor.execute("""
                INSERT INTO port_assignments 
                (service_name, port, service_type, status, assigned_at)
                VALUES (?, ?, 'backend', 'active', ?)
            """, (service_name, assigned_port, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            logger.info("Port assigned", name=service_name, port=assigned_port)
            return assigned_port
            
        except Exception as e:
            logger.error("Error assigning port", name=service_name, error=str(e))
            return None
    
    def _find_next_available_port(self, cursor, start_port: int = 8000) -> int:
        """Find next available port starting from start_port"""
        port = start_port
        max_attempts = 1000  # Prevent infinite loop
        
        for _ in range(max_attempts):
            cursor.execute("""
                SELECT service_name FROM port_assignments 
                WHERE port = ? AND status = 'active'
            """, (port,))
            
            if not cursor.fetchone():
                return port
            
            port += 1
        
        raise RuntimeError(f"Could not find available port after {max_attempts} attempts")
    
    def release_port(self, service_name: str) -> bool:
        """Release port assignment for service"""
        try:
            if not self.port_db_path.exists():
                return False
            
            conn = sqlite3.connect(self.port_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE port_assignments 
                SET status = 'inactive' 
                WHERE service_name = ?
            """, (service_name,))
            
            affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if affected > 0:
                logger.info("Port released", name=service_name)
                return True
            else:
                logger.warning("No port assignment found to release", name=service_name)
                return False
                
        except Exception as e:
            logger.error("Error releasing port", name=service_name, error=str(e))
            return False

class ZmartBotIntegration:
    """
    Main integration class for ZmartBot ecosystem
    """
    
    def __init__(self, 
                 registry_url: str = "http://localhost:8610",
                 port_db_path: str = "port_registry.db",
                 service_db_path: str = "src/data/service_registry.db"):
        self.registry_client = RegistryClient(registry_url, port_db_path, service_db_path)
        self.port_client = PortManagerClient(port_db_path)
        self.integration_stats = {
            "services_discovered": 0,
            "ports_assigned": 0,
            "registrations_successful": 0,
            "registrations_failed": 0
        }
    
    async def discover_services(self) -> List[ServiceInfo]:
        """Discover all services in ZmartBot ecosystem"""
        services = await self.registry_client.get_all_services()
        self.integration_stats["services_discovered"] = len(services)
        return services
    
    async def get_service_details(self, service_name: str) -> Optional[ServiceInfo]:
        """Get detailed information about a specific service"""
        return await self.registry_client.get_service_by_name(service_name)
    
    def get_port_assignments(self) -> List[PortAssignment]:
        """Get all port assignments"""
        return self.port_client.get_all_port_assignments()
    
    def get_service_port(self, service_name: str) -> Optional[int]:
        """Get port for a specific service"""
        return self.port_client.get_service_port(service_name)
    
    async def register_new_service(self, 
                                  service_name: str,
                                  service_type: str = "backend",
                                  description: str = "",
                                  health_url: Optional[str] = None,
                                  dependencies: List[str] = None,
                                  tags: List[str] = None) -> Tuple[bool, Optional[int]]:
        """
        Register a new service with port assignment
        
        Returns:
            Tuple of (success, assigned_port)
        """
        try:
            # Assign port
            assigned_port = self.port_client.assign_port(service_name)
            if not assigned_port:
                logger.error("Failed to assign port", name=service_name)
                return False, None
            
            # Create service info
            service_info = ServiceInfo(
                service_name=service_name,
                service_type=service_type,
                port=assigned_port,
                status="ACTIVE",
                description=description,
                health_url=health_url or f"http://localhost:{assigned_port}/health",
                dependencies=dependencies or [],
                tags=tags or []
            )
            
            # Register with registry
            success = await self.registry_client.register_service(service_info)
            
            if success:
                self.integration_stats["registrations_successful"] += 1
                self.integration_stats["ports_assigned"] += 1
                logger.info("Service registered successfully", 
                           name=service_name,
                           port=assigned_port)
                return True, assigned_port
            else:
                self.integration_stats["registrations_failed"] += 1
                # Release port if registration failed
                self.port_client.release_port(service_name)
                logger.error("Service registration failed", name=service_name)
                return False, None
                
        except Exception as e:
            self.integration_stats["registrations_failed"] += 1
            logger.error("Error registering service", name=service_name, error=str(e))
            return False, None
    
    async def update_service_status(self, service_name: str, status: str) -> bool:
        """Update service status"""
        return await self.registry_client.update_service_status(service_name, status)
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        return {
            **self.integration_stats,
            **self.registry_client.connection_stats
        }
    
    async def health_check(self) -> bool:
        """Check overall integration health"""
        return await self.registry_client.health_check()
