#!/usr/bin/env python3
"""
ZmartBot Supabase Orchestration Integration
Connects all orchestration components to Supabase database for centralized management
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import aiohttp
import asyncpg
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SupabaseOrchestration')

@dataclass
class ServiceHealth:
    service_id: int
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    response_time_ms: int
    error_count: int
    request_count: int
    timestamp: datetime

@dataclass
class ServiceConfig:
    service_id: int
    config_key: str
    config_value: str
    config_type: str = 'string'
    is_encrypted: bool = False

class SupabaseOrchestrationManager:
    def __init__(self):
        self.supabase_url = "https://asjtxrmftmutcsnqgidy.supabase.co"
        self.anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM"
        self.headers = {
            'apikey': self.anon_key,
            'Authorization': f'Bearer {self.anon_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def register_service(self, service_name: str, service_type: str, port: Optional[int] = None, 
                             passport_id: Optional[str] = None) -> Dict:
        """Register a service in the service registry"""
        data = {
            'service_name': service_name,
            'service_type': service_type,
            'port': port,
            'status': 'ACTIVE',
            'passport_id': passport_id,
            'registered_at': datetime.now(timezone.utc).isoformat(),
            'last_health_check': datetime.now(timezone.utc).isoformat(),
            'health_score': 100
        }
        
        async with self.session.post(f'{self.supabase_url}/rest/v1/service_registry', json=data) as response:
            if response.status == 201:
                result = await response.json()
                logger.info(f"Service {service_name} registered successfully with ID: {result[0]['id']}")
                return result[0]
            else:
                error_text = await response.text()
                logger.error(f"Failed to register service {service_name}: {error_text}")
                raise Exception(f"Service registration failed: {error_text}")

    async def update_service_health(self, service_id: int, health_data: ServiceHealth) -> bool:
        """Update service health metrics"""
        try:
            # Update health score in service registry
            registry_data = {
                'health_score': min(100, max(0, 100 - health_data.error_count)),
                'last_health_check': health_data.timestamp.isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            async with self.session.patch(
                f'{self.supabase_url}/rest/v1/service_registry?id=eq.{service_id}',
                json=registry_data
            ) as response:
                if response.status != 200:
                    logger.error(f"Failed to update service registry for service {service_id}")
                    return False

            # Store detailed health metrics (if health table exists)
            health_metrics_data = {
                'service_id': service_id,
                'cpu_usage': health_data.cpu_usage,
                'memory_usage': health_data.memory_usage,
                'disk_usage': health_data.disk_usage,
                'response_time_ms': health_data.response_time_ms,
                'error_count': health_data.error_count,
                'request_count': health_data.request_count,
                'timestamp': health_data.timestamp.isoformat()
            }
            
            # Try to insert health metrics (table may not exist yet)
            try:
                async with self.session.post(
                    f'{self.supabase_url}/rest/v1/service_health_metrics',
                    json=health_metrics_data
                ) as response:
                    if response.status == 201:
                        logger.debug(f"Health metrics stored for service {service_id}")
            except Exception as e:
                logger.debug(f"Health metrics table not available yet: {e}")

            return True
        except Exception as e:
            logger.error(f"Failed to update health for service {service_id}: {e}")
            return False

    async def get_service_by_name(self, service_name: str) -> Optional[Dict]:
        """Get service by name from registry"""
        try:
            async with self.session.get(
                f'{self.supabase_url}/rest/v1/service_registry?service_name=eq.{service_name}'
            ) as response:
                if response.status == 200:
                    services = await response.json()
                    return services[0] if services else None
        except Exception as e:
            logger.error(f"Failed to get service {service_name}: {e}")
        return None

    async def get_all_services(self) -> List[Dict]:
        """Get all services from registry"""
        try:
            async with self.session.get(f'{self.supabase_url}/rest/v1/service_registry') as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            logger.error(f"Failed to get services: {e}")
        return []

    async def add_service_dependency(self, service_id: int, depends_on_service_id: int, 
                                   dependency_type: str = 'required') -> bool:
        """Add service dependency relationship"""
        data = {
            'service_id': service_id,
            'depends_on_service_id': depends_on_service_id,
            'dependency_type': dependency_type,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            async with self.session.post(
                f'{self.supabase_url}/rest/v1/service_dependencies',
                json=data
            ) as response:
                if response.status == 201:
                    logger.info(f"Dependency added: service {service_id} depends on {depends_on_service_id}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to add dependency: {error_text}")
        except Exception as e:
            logger.debug(f"Dependencies table not available yet: {e}")
        return False

    async def set_service_config(self, service_id: int, config_key: str, config_value: str,
                               config_type: str = 'string', is_encrypted: bool = False) -> bool:
        """Set service configuration"""
        data = {
            'service_id': service_id,
            'config_key': config_key,
            'config_value': config_value,
            'config_type': config_type,
            'is_encrypted': is_encrypted,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Try to upsert (update if exists, insert if not)
            async with self.session.post(
                f'{self.supabase_url}/rest/v1/service_configurations',
                json=data
            ) as response:
                if response.status == 201:
                    logger.debug(f"Config set for service {service_id}: {config_key}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to set config: {error_text}")
        except Exception as e:
            logger.debug(f"Configurations table not available yet: {e}")
        return False

    async def log_service_communication(self, from_service_id: int, to_service_id: int,
                                      communication_type: str, endpoint: str, method: str,
                                      status_code: int, response_time_ms: int) -> bool:
        """Log service-to-service communication"""
        data = {
            'from_service_id': from_service_id,
            'to_service_id': to_service_id,
            'communication_type': communication_type,
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response_time_ms': response_time_ms,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            async with self.session.post(
                f'{self.supabase_url}/rest/v1/service_communications',
                json=data
            ) as response:
                if response.status == 201:
                    logger.debug(f"Communication logged: {from_service_id} -> {to_service_id}")
                    return True
        except Exception as e:
            logger.debug(f"Communications table not available yet: {e}")
        return False

    async def update_service_status(self, service_id: int, status: str) -> bool:
        """Update service status"""
        data = {
            'status': status,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            async with self.session.patch(
                f'{self.supabase_url}/rest/v1/service_registry?id=eq.{service_id}',
                json=data
            ) as response:
                if response.status == 200:
                    logger.info(f"Service {service_id} status updated to {status}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to update service status: {error_text}")
        except Exception as e:
            logger.error(f"Failed to update service status: {e}")
        return False

class ZmartBotOrchestrationBridge:
    """Bridge between existing ZmartBot orchestration and Supabase"""
    
    def __init__(self):
        self.supabase_manager = SupabaseOrchestrationManager()
        self.service_mappings = {}  # Maps local service names to Supabase IDs
        
    async def initialize(self):
        """Initialize and sync existing services with Supabase"""
        async with self.supabase_manager:
            # Register known ZmartBot services
            zmartbot_services = [
                ('zmart-foundation', 'backend', 8000),
                ('zmart-api', 'backend', 8001),
                ('zmart-dashboard', 'frontend', 3000),
                ('zmart-websocket', 'backend', 8002),
                ('master-orchestration-agent', 'AGT', None),
                ('system-protection-service', 'PROTECTION', 8999),
                ('optimization-claude-service', 'SRV', 8998),
                ('snapshot-service', 'backend', None),
                ('passport-service', 'backend', None),
                ('api-keys-manager-service', 'backend', None),
                ('health-check-service', 'backend', None),
                ('service-discovery', 'backend', None),
                ('port-manager', 'backend', None),
                ('process-reaper', 'backend', None),
                ('cryptometer-service', 'SRV', None),
                ('binance-service', 'ENG', None),
                ('kucoin-service', 'ENG', None),
                ('whale-alerts', 'SRV', None),
                ('live-alerts', 'SRV', None),
                ('messi-alerts', 'SRV', None),
                ('21indicators', 'SRV', None),
                ('my-symbols-service', 'SRV', None),
                ('indicators-card', 'SRV', None),
                ('backtesting-server', 'SRV', None),
                ('security-scan-service', 'PROTECTION', None)
            ]
            
            for service_name, service_type, port in zmartbot_services:
                try:
                    # Check if service already exists
                    existing = await self.supabase_manager.get_service_by_name(service_name)
                    if existing:
                        self.service_mappings[service_name] = existing['id']
                        logger.info(f"Service {service_name} already registered with ID {existing['id']}")
                    else:
                        # Register new service
                        result = await self.supabase_manager.register_service(
                            service_name, service_type, port
                        )
                        self.service_mappings[service_name] = result['id']
                        logger.info(f"Registered new service {service_name} with ID {result['id']}")
                except Exception as e:
                    logger.error(f"Failed to process service {service_name}: {e}")

    async def sync_service_health(self, service_name: str, cpu_usage: float, memory_usage: float,
                                response_time_ms: int = 0, error_count: int = 0, request_count: int = 0):
        """Sync service health data to Supabase"""
        if service_name not in self.service_mappings:
            logger.warning(f"Service {service_name} not found in mappings")
            return
            
        service_id = self.service_mappings[service_name]
        health_data = ServiceHealth(
            service_id=service_id,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=0.0,  # Can be enhanced later
            response_time_ms=response_time_ms,
            error_count=error_count,
            request_count=request_count,
            timestamp=datetime.now(timezone.utc)
        )
        
        async with self.supabase_manager:
            await self.supabase_manager.update_service_health(service_id, health_data)

    async def get_service_status_dashboard(self) -> Dict:
        """Get comprehensive service status for dashboard"""
        async with self.supabase_manager:
            services = await self.supabase_manager.get_all_services()
            
            dashboard_data = {
                'total_services': len(services),
                'active_services': len([s for s in services if s['status'] == 'ACTIVE']),
                'services_by_type': {},
                'avg_health_score': 0,
                'services': services
            }
            
            # Group by type
            for service in services:
                service_type = service['service_type']
                if service_type not in dashboard_data['services_by_type']:
                    dashboard_data['services_by_type'][service_type] = 0
                dashboard_data['services_by_type'][service_type] += 1
            
            # Calculate average health
            if services:
                total_health = sum(s.get('health_score', 0) for s in services)
                dashboard_data['avg_health_score'] = total_health / len(services)
            
            return dashboard_data

async def main():
    """Test the Supabase integration"""
    bridge = ZmartBotOrchestrationBridge()
    
    try:
        await bridge.initialize()
        logger.info("Supabase orchestration bridge initialized successfully")
        
        # Test health sync
        await bridge.sync_service_health('zmart-foundation', 25.5, 45.2, 150, 0, 1000)
        
        # Get dashboard data
        dashboard = await bridge.get_service_status_dashboard()
        logger.info(f"Dashboard data: {json.dumps(dashboard, indent=2, default=str)}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main())