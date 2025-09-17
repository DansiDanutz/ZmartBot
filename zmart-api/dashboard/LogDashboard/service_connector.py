#!/usr/bin/env python3
"""
🔌 ZmartBot Passport Service Connector
Real-time connector to all 29 passport services
NO MOCK DATA - ONLY REAL DATA
"""

import asyncio
import json
import logging
import sqlite3
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PassportService:
    """Represents a passport service with its connection details"""
    service_name: str
    port: int
    passport_id: str
    health_status: str
    connection_status: str
    last_seen: Optional[datetime] = None
    response_time: Optional[float] = None
    error_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'service_name': self.service_name,
            'port': self.port,
            'passport_id': self.passport_id,
            'health_status': self.health_status,
            'connection_status': self.connection_status,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'response_time': self.response_time,
            'error_count': self.error_count
        }

class ServiceConnector:
    """Real-time connector to all passport services"""
    
    def __init__(self, db_path: str = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/src/data/service_registry.db"):
        self.db_path = db_path
        self.services: Dict[str, PassportService] = {}
        self.running = False
        self.update_thread = None
        self.health_check_thread = None
        
        # Thread-safe queues for real-time updates
        self.service_updates = queue.Queue()
        self.log_updates = queue.Queue()
        self.metric_updates = queue.Queue()
        
        # Connection settings
        self.check_interval = 30  # seconds
        self.timeout = 5  # seconds
        self.max_workers = 10
        
        logger.info("🔌 ServiceConnector initialized")
        
    def start(self):
        """Start real-time monitoring of all passport services"""
        logger.info("🚀 Starting real-time service monitoring...")
        
        self.running = True
        
        # Load initial service data
        self.load_passport_services()
        
        # Start background monitoring threads
        self.health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.update_thread = threading.Thread(target=self._metric_collection_loop, daemon=True)
        
        self.health_check_thread.start()
        self.update_thread.start()
        
        logger.info(f"✅ Monitoring {len(self.services)} passport services")
        
    def stop(self):
        """Stop monitoring"""
        logger.info("🛑 Stopping service monitoring...")
        self.running = False
        
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5)
        if self.update_thread:
            self.update_thread.join(timeout=5)
            
        logger.info("✅ Service monitoring stopped")
        
    def load_passport_services(self):
        """Load all passport services from the registry database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, port, passport_id, health_status, connection_status, last_state_change
                FROM service_registry 
                WHERE passport_id IS NOT NULL 
                ORDER BY service_name
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            self.services.clear()
            
            for row in rows:
                service_name, port, passport_id, health_status, connection_status, last_change = row
                
                service = PassportService(
                    service_name=service_name,
                    port=port,
                    passport_id=passport_id,
                    health_status=health_status,
                    connection_status=connection_status,
                    last_seen=datetime.fromisoformat(last_change) if last_change else None
                )
                
                self.services[service_name] = service
                
            logger.info(f"📊 Loaded {len(self.services)} passport services")
            
        except Exception as e:
            logger.error(f"❌ Failed to load passport services: {e}")
            
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all passport services with real-time data"""
        return [service.to_dict() for service in self.services.values()]
        
    def get_service_by_name(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get specific service data"""
        service = self.services.get(service_name)
        return service.to_dict() if service else None
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get real system metrics from passport services"""
        total_services = len(self.services)
        healthy_services = sum(1 for s in self.services.values() if s.health_status == 'healthy')
        connected_services = sum(1 for s in self.services.values() if s.connection_status == 'connected')
        
        # Calculate response time statistics
        response_times = [s.response_time for s in self.services.values() if s.response_time is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Error statistics
        total_errors = sum(s.error_count for s in self.services.values())
        services_with_errors = sum(1 for s in self.services.values() if s.error_count > 0)
        
        # Calculate health percentage
        health_percentage = (healthy_services / total_services * 100) if total_services > 0 else 0
        
        return {
            'total_services': total_services,
            'healthy_services': healthy_services,
            'connected_services': connected_services,
            'health_percentage': round(health_percentage, 1),
            'avg_response_time': round(avg_response_time, 2),
            'total_errors': total_errors,
            'services_with_errors': services_with_errors,
            'last_updated': datetime.now().isoformat()
        }
        
    def get_service_categories(self) -> Dict[str, List[Dict]]:
        """Categorize services by type"""
        categories = {
            'core': [],
            'exchange': [],
            'analytics': [],
            'infrastructure': [],
            'communication': [],
            'data': [],
            'orchestration': []
        }
        
        # Service categorization based on name patterns
        for service in self.services.values():
            service_dict = service.to_dict()
            name = service.service_name.lower()
            
            if 'api' in name or name in ['mysymbols']:
                categories['core'].append(service_dict)
            elif name in ['binance', 'kucoin']:
                categories['exchange'].append(service_dict)
            elif 'analytics' in name or 'backtesting' in name or 'technical' in name or 'machine_learning' in name:
                categories['analytics'].append(service_dict)
            elif 'orchestration' in name or 'doctor' in name or 'passport' in name or 'protection' in name:
                categories['infrastructure'].append(service_dict)
            elif 'websocket' in name or 'notification' in name or 'alert' in name:
                categories['communication'].append(service_dict)
            elif 'data' in name or 'warehouse' in name:
                categories['data'].append(service_dict)
            elif 'agent' in name:
                categories['orchestration'].append(service_dict)
            else:
                categories['infrastructure'].append(service_dict)  # Default category
                
        return categories
        
    def _health_check_loop(self):
        """Background loop for health checking all services"""
        while self.running:
            try:
                self._perform_health_checks()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Health check loop error: {e}")
                time.sleep(5)
                
    def _perform_health_checks(self):
        """Perform parallel health checks on all services"""
        logger.info("🔍 Performing health checks on all passport services...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit health check tasks
            future_to_service = {
                executor.submit(self._check_service_health, service): service 
                for service in self.services.values()
            }
            
            # Process completed health checks
            for future in as_completed(future_to_service):
                service = future_to_service[future]
                try:
                    health_data = future.result()
                    self._update_service_health(service.service_name, health_data)
                except Exception as e:
                    logger.warning(f"⚠️ Health check failed for {service.service_name}: {e}")
                    self._update_service_health(service.service_name, {
                        'healthy': False,
                        'error': str(e),
                        'response_time': None
                    })
                    
        logger.info("✅ Health checks completed")
        
    def _check_service_health(self, service: PassportService) -> Dict[str, Any]:
        """Check health of a single service"""
        start_time = time.time()
        
        try:
            # Try multiple health endpoints
            health_urls = [
                f"http://localhost:{service.port}/health",
                f"http://127.0.0.1:{service.port}/health",
                f"http://localhost:{service.port}/api/health",
                f"http://localhost:{service.port}/status"
            ]
            
            last_exception = None
            
            for url in health_urls:
                try:
                    response = requests.get(url, timeout=self.timeout)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            return {
                                'healthy': True,
                                'response_time': response_time,
                                'data': data,
                                'url': url
                            }
                        except json.JSONDecodeError:
                            # Health endpoint returned non-JSON but with 200 status
                            return {
                                'healthy': True,
                                'response_time': response_time,
                                'data': {'status': 'ok', 'text': response.text[:100]},
                                'url': url
                            }
                    else:
                        last_exception = f"HTTP {response.status_code}"
                        
                except requests.RequestException as e:
                    last_exception = str(e)
                    continue
                    
            # If no health endpoint worked, try a simple connection test
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                result = sock.connect_ex(('localhost', service.port))
                sock.close()
                
                response_time = time.time() - start_time
                
                if result == 0:
                    return {
                        'healthy': True,
                        'response_time': response_time,
                        'data': {'status': 'port_open', 'method': 'socket'},
                        'url': f"socket://localhost:{service.port}"
                    }
                else:
                    return {
                        'healthy': False,
                        'response_time': response_time,
                        'error': f"Port {service.port} not accessible",
                        'last_exception': last_exception
                    }
                    
            except Exception as e:
                return {
                    'healthy': False,
                    'response_time': time.time() - start_time,
                    'error': f"Connection failed: {str(e)}",
                    'last_exception': last_exception
                }
                
        except Exception as e:
            return {
                'healthy': False,
                'response_time': time.time() - start_time,
                'error': f"Health check failed: {str(e)}"
            }
            
    def _update_service_health(self, service_name: str, health_data: Dict[str, Any]):
        """Update service health status"""
        if service_name not in self.services:
            return
            
        service = self.services[service_name]
        old_health = service.health_status
        old_connection = service.connection_status
        
        # Update health status
        service.health_status = 'healthy' if health_data.get('healthy', False) else 'unhealthy'
        service.connection_status = 'connected' if health_data.get('healthy', False) else 'disconnected'
        service.response_time = health_data.get('response_time')
        service.last_seen = datetime.now()
        
        # Update error count
        if not health_data.get('healthy', False):
            service.error_count += 1
        else:
            service.error_count = max(0, service.error_count - 1)  # Gradually reduce error count
            
        # Log status changes
        if old_health != service.health_status or old_connection != service.connection_status:
            logger.info(f"🔄 {service_name}: {old_health}/{old_connection} → {service.health_status}/{service.connection_status}")
            
            # Queue update for dashboard
            self.service_updates.put({
                'type': 'service_status_change',
                'service_name': service_name,
                'old_status': {'health': old_health, 'connection': old_connection},
                'new_status': {'health': service.health_status, 'connection': service.connection_status},
                'timestamp': datetime.now().isoformat(),
                'response_time': service.response_time
            })
            
        # Update database
        self._update_service_in_db(service)
        
    def _update_service_in_db(self, service: PassportService):
        """Update service status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE service_registry 
                SET health_status = ?, connection_status = ?, last_state_change = ?
                WHERE service_name = ?
            """, (
                service.health_status,
                service.connection_status,
                service.last_seen.isoformat() if service.last_seen else datetime.now().isoformat(),
                service.service_name
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to update {service.service_name} in database: {e}")
            
    def _metric_collection_loop(self):
        """Background loop for collecting detailed metrics"""
        while self.running:
            try:
                self._collect_detailed_metrics()
                time.sleep(60)  # Collect detailed metrics every minute
            except Exception as e:
                logger.error(f"❌ Metric collection error: {e}")
                time.sleep(10)
                
    def _collect_detailed_metrics(self):
        """Collect detailed metrics from services that support it"""
        logger.debug("📊 Collecting detailed metrics...")
        
        metrics = self.get_system_metrics()
        
        # Queue metrics update for dashboard
        self.metric_updates.put({
            'type': 'metrics_update',
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })
        
    def get_real_time_updates(self) -> List[Dict[str, Any]]:
        """Get all pending real-time updates"""
        updates = []
        
        # Get service updates
        while not self.service_updates.empty():
            try:
                updates.append(self.service_updates.get_nowait())
            except queue.Empty:
                break
                
        # Get metric updates
        while not self.metric_updates.empty():
            try:
                updates.append(self.metric_updates.get_nowait())
            except queue.Empty:
                break
                
        return updates
        
    def get_service_logs(self, service_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent logs from a specific service (if available)"""
        # This would connect to actual log sources
        # For now, return empty as we need to implement log collection
        return []
        
    def get_critical_issues(self) -> List[Dict[str, Any]]:
        """Get critical issues from real services"""
        issues = []
        
        for service in self.services.values():
            if service.health_status == 'unhealthy':
                issues.append({
                    'service_name': service.service_name,
                    'issue_type': 'health_check_failed',
                    'severity': 'HIGH',
                    'description': f"Service {service.service_name} is unhealthy",
                    'last_seen': service.last_seen.isoformat() if service.last_seen else None,
                    'error_count': service.error_count
                })
                
            if service.connection_status == 'disconnected':
                issues.append({
                    'service_name': service.service_name,
                    'issue_type': 'connection_failed',
                    'severity': 'CRITICAL',
                    'description': f"Cannot connect to {service.service_name}",
                    'last_seen': service.last_seen.isoformat() if service.last_seen else None,
                    'error_count': service.error_count
                })
                
        return sorted(issues, key=lambda x: x['error_count'], reverse=True)

# Global instance
_connector_instance = None

def get_connector() -> ServiceConnector:
    """Get global ServiceConnector instance"""
    global _connector_instance
    if _connector_instance is None:
        _connector_instance = ServiceConnector()
        _connector_instance.start()
    return _connector_instance

def stop_connector():
    """Stop global ServiceConnector instance"""
    global _connector_instance
    if _connector_instance is not None:
        _connector_instance.stop()
        _connector_instance = None

if __name__ == '__main__':
    # Test the connector
    connector = ServiceConnector()
    connector.start()
    
    try:
        # Run for 2 minutes to see real data
        time.sleep(120)
        
        # Print results
        print("\n📊 REAL SYSTEM METRICS:")
        metrics = connector.get_system_metrics()
        for key, value in metrics.items():
            print(f"  {key}: {value}")
            
        print("\n🏢 SERVICE CATEGORIES:")
        categories = connector.get_service_categories()
        for category, services in categories.items():
            print(f"  {category}: {len(services)} services")
            
        print("\n🚨 CRITICAL ISSUES:")
        issues = connector.get_critical_issues()
        for issue in issues[:5]:  # Show top 5
            print(f"  {issue['service_name']}: {issue['description']}")
            
    except KeyboardInterrupt:
        pass
    finally:
        connector.stop()