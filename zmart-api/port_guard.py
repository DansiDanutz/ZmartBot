#!/usr/bin/env python3
"""
🛡️ ZmartBot Port Allocation Prevention System
Ensures no duplicate port assignments ever happen
"""

import sqlite3
import os

class PortGuard:
    def __init__(self):
        self.base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
        self.allocation_db = os.path.join(self.base_path, "data/port_allocation_registry.db")
    
    def is_port_available(self, port):
        """Check if a port is available for allocation"""
        try:
            conn = sqlite3.connect(self.allocation_db)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM port_allocations WHERE port = ? AND status = 'ALLOCATED'", (port,))
            count = cursor.fetchone()[0]
            conn.close()
            return count == 0
        except Exception as e:
            print(f"Error checking port availability: {e}")
            return False
    
    def allocate_port(self, service_name, preferred_port=None):
        """Allocate a port for a service"""
        try:
            conn = sqlite3.connect(self.allocation_db)
            cursor = conn.cursor()
            
            if preferred_port and self.is_port_available(preferred_port):
                port = preferred_port
            else:
                # Find next available port starting from 9000
                cursor.execute("SELECT MAX(port) FROM port_allocations")
                max_port = cursor.fetchone()[0] or 8999
                port = max(max_port + 1, 9000)
                
                while not self.is_port_available(port):
                    port += 1
            
            # Allocate the port
            cursor.execute("""
                INSERT INTO port_allocations (port, service_name, status, notes)
                VALUES (?, ?, 'ALLOCATED', 'Auto-allocated by PortGuard')
            """, (port, service_name))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Port {port} allocated to {service_name}")
            return port
            
        except Exception as e:
            print(f"❌ Error allocating port: {e}")
            return None
    
    def deallocate_port(self, port):
        """Deallocate a port"""
        try:
            conn = sqlite3.connect(self.allocation_db)
            cursor = conn.cursor()
            cursor.execute("UPDATE port_allocations SET status = 'AVAILABLE' WHERE port = ?", (port,))
            conn.commit()
            conn.close()
            print(f"✅ Port {port} deallocated")
        except Exception as e:
            print(f"❌ Error deallocating port: {e}")

# Usage example:
# guard = PortGuard()
# new_port = guard.allocate_port("new-service")
# print(f"Your service should use port: {new_port}")
