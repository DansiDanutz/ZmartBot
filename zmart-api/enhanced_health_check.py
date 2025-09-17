#!/usr/bin/env python3
"""
Enhanced Health Check for All Services (Passport + Non-Passport)
Simple status tracking with timestamps
"""

import sqlite3
import requests
import asyncio
import aiohttp
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedHealthChecker:
    def __init__(self):
        self.db_path = "src/data/service_registry.db"
    
    def get_all_services(self):
        """Get all services from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT service_name, port, passport_id, health_status, connection_status, last_state_change 
            FROM service_registry 
            ORDER BY passport_id DESC, service_name
        """)
        services = cursor.fetchall()
        conn.close()
        return services
    
    async def check_service_health(self, session, service_name, port):
        """Check if service is healthy via HTTP request"""
        try:
            url = f"http://127.0.0.1:{port}/health"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as response:
                if response.status == 200:
                    return "healthy", "connected"
                else:
                    return "unhealthy", "connected"
        except asyncio.TimeoutError:
            return "unhealthy", "timeout"
        except Exception:
            return "offline", "disconnected"
    
    def update_service_status(self, service_name, health_status, connection_status, state_changed=False):
        """Update service status in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if state_changed:
            # Update with new timestamp
            cursor.execute("""
                UPDATE service_registry 
                SET health_status = ?, connection_status = ?, last_state_change = datetime('now')
                WHERE service_name = ?
            """, (health_status, connection_status, service_name))
        else:
            # Update without changing timestamp
            cursor.execute("""
                UPDATE service_registry 
                SET health_status = ?, connection_status = ?
                WHERE service_name = ?
            """, (health_status, connection_status, service_name))
        
        conn.commit()
        conn.close()
    
    async def run_health_check(self):
        """Run health check on all services"""
        services = self.get_all_services()
        total_services = len(services)
        
        print(f"🔍 Checking health status for {total_services} services...")
        
        passport_healthy = 0
        passport_total = 0
        non_passport_healthy = 0
        non_passport_total = 0
        
        async with aiohttp.ClientSession() as session:
            for service_name, port, passport_id, old_health, old_connection, last_change in services:
                print(f"⏳ Checking {service_name} on port {port}...")
                
                # Check service health
                new_health, new_connection = await self.check_service_health(session, service_name, port)
                
                # Check if state changed
                state_changed = (new_health != old_health) or (new_connection != old_connection)
                
                # Update database
                self.update_service_status(service_name, new_health, new_connection, state_changed)
                
                # Display result with status light
                if new_health == "healthy" and new_connection == "connected":
                    status_light = "🟢"
                    timestamp_info = f"GREEN since {last_change if not state_changed else 'just now'}"
                elif new_connection == "connected":
                    status_light = "🟡" 
                    timestamp_info = f"YELLOW since {last_change if not state_changed else 'just now'}"
                else:
                    status_light = "🔴"
                    timestamp_info = f"RED since {last_change if not state_changed else 'just now'}"
                
                # Count statistics
                if passport_id:
                    passport_total += 1
                    if new_health == "healthy":
                        passport_healthy += 1
                else:
                    non_passport_total += 1
                    if new_health == "healthy":
                        non_passport_healthy += 1
                
                service_type = "PASSPORT" if passport_id else "NON-PASSPORT"
                print(f"   {status_light} {service_name} ({service_type}): {new_health} / {new_connection}")
                print(f"      └── {timestamp_info}")
        
        # Display summary
        print(f"\n🎯 Health Check Complete:")
        print(f"   📋 PASSPORT SERVICES: {passport_healthy}/{passport_total} healthy ({passport_healthy/passport_total*100:.1f}%)")
        print(f"   📋 NON-PASSPORT SERVICES: {non_passport_healthy}/{non_passport_total} healthy ({non_passport_healthy/non_passport_total*100:.1f}%)")
        print(f"   📊 TOTAL SERVICES: {passport_healthy + non_passport_healthy}/{total_services} healthy ({(passport_healthy + non_passport_healthy)/total_services*100:.1f}%)")
        print(f"\n✅ Status tracking updated with timestamps!")

if __name__ == "__main__":
    checker = EnhancedHealthChecker()
    asyncio.run(checker.run_health_check())