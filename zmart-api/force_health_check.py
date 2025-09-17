#!/usr/bin/env python3
"""
Force Health Check Update
Manually checks all services and updates their health status in the database
"""

import sqlite3
import requests
import psutil
import time
from pathlib import Path

def check_service_health(service_name, port):
    """Check individual service health"""
    try:
        # Try health endpoint first
        response = requests.get(f"http://localhost:{port}/health", timeout=3)
        if response.status_code == 200:
            return {"health_status": "healthy", "connection_status": "connected"}
        else:
            return {"health_status": "unhealthy", "connection_status": "connected"}
    except requests.exceptions.RequestException:
        # Check if port is in use by scanning processes
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                connections = proc.info['connections']
                if connections:
                    for conn in connections:
                        if conn.laddr.port == port and conn.status == 'LISTEN':
                            return {"health_status": "no_health_endpoint", "connection_status": "connected"}
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
        
        return {"health_status": "offline", "connection_status": "disconnected"}

def update_all_health_status():
    """Update health status for all services in the registry"""
    
    db_path = Path(__file__).parent / "src" / "data" / "service_registry.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all services
        cursor.execute("SELECT service_name, port FROM service_registry")
        services = cursor.fetchall()
        
        print(f"🔍 Checking health status for {len(services)} services...")
        
        healthy_count = 0
        connected_count = 0
        
        for service_name, port in services:
            print(f"⏳ Checking {service_name} on port {port}...")
            
            health_result = check_service_health(service_name, port)
            
            # Update database
            cursor.execute("""
                UPDATE service_registry 
                SET health_status = ?, connection_status = ?
                WHERE service_name = ?
            """, (health_result["health_status"], health_result["connection_status"], service_name))
            
            status_icon = "✅" if health_result["health_status"] == "healthy" else "⚠️" if health_result["connection_status"] == "connected" else "❌"
            print(f"   {status_icon} {service_name}: {health_result['health_status']} / {health_result['connection_status']}")
            
            if health_result["health_status"] == "healthy":
                healthy_count += 1
            if health_result["connection_status"] == "connected":
                connected_count += 1
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"\n🎯 Health Check Complete:")
        print(f"   - Total services: {len(services)}")
        print(f"   - Healthy services: {healthy_count}")
        print(f"   - Connected services: {connected_count}")
        print(f"   - Offline services: {len(services) - connected_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating health status: {e}")
        return False

if __name__ == "__main__":
    success = update_all_health_status()
    if success:
        print("\n✅ Health status updated successfully!")
        print("🔄 Refresh the Service Dashboard to see updated status.")
    else:
        print("\n❌ Failed to update health status.")