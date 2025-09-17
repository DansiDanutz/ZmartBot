#!/usr/bin/env python3
"""
🔍 ZmartBot Port Conflict Analyzer & Prevention System
Comprehensive port allocation system to prevent conflicts forever
"""

import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path

class PortManager:
    def __init__(self):
        self.base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
        self.databases = {
            "service_registry": "service_registry.db",
            "passport_registry": "data/passport_registry.db"
        }
        self.port_allocations = {}
        self.conflicts = []
        
    def scan_all_ports(self):
        """Scan all databases for port usage"""
        print("🔍 SCANNING ALL PORT ALLOCATIONS")
        print("=" * 60)
        
        for db_name, db_path in self.databases.items():
            full_path = os.path.join(self.base_path, db_path)
            if os.path.exists(full_path):
                print(f"\n📊 Scanning {db_name}...")
                try:
                    conn = sqlite3.connect(full_path)
                    cursor = conn.cursor()
                    
                    # Get table name
                    table_name = db_name.replace("_registry", "_registry") if "registry" in db_name else db_name
                    
                    cursor.execute(f"SELECT port, service_name FROM {table_name} ORDER BY port")
                    
                    for port, service in cursor.fetchall():
                        if port not in self.port_allocations:
                            self.port_allocations[port] = []
                        
                        self.port_allocations[port].append({
                            'service': service,
                            'database': db_name,
                            'path': db_path
                        })
                    
                    conn.close()
                    print(f"   ✅ Scanned {len(self.port_allocations)} total ports")
                    
                except Exception as e:
                    print(f"   ❌ Error scanning {db_name}: {e}")
    
    def detect_conflicts(self):
        """Detect actual port conflicts between different services"""
        print(f"\n🚨 ANALYZING PORT CONFLICTS")
        print("=" * 60)
        
        conflicts_found = 0
        same_service_duplicates = 0
        
        for port, allocations in self.port_allocations.items():
            if len(allocations) > 1:
                # Check if it's the same service in multiple databases
                service_names = [alloc['service'] for alloc in allocations]
                unique_services = set(service_names)
                
                if len(unique_services) == 1:
                    # Same service in multiple databases - this is OK
                    same_service_duplicates += 1
                    print(f"   ℹ️  Port {port}: {service_names[0]} (appears in {len(allocations)} databases) - OK")
                else:
                    # Different services using same port - CONFLICT!
                    conflicts_found += 1
                    print(f"   🚨 CONFLICT Port {port}:")
                    for alloc in allocations:
                        print(f"      - {alloc['service']} ({alloc['database']})")
                    
                    self.conflicts.append({
                        'port': port,
                        'services': allocations,
                        'type': 'CRITICAL'
                    })
        
        print(f"\n📊 CONFLICT ANALYSIS SUMMARY:")
        print(f"   🚨 Critical Conflicts: {conflicts_found}")
        print(f"   ℹ️  Same Service Duplicates: {same_service_duplicates}")
        print(f"   📊 Total Ports Used: {len(self.port_allocations)}")
        
        return conflicts_found == 0
    
    def get_port_range_usage(self):
        """Analyze port range usage patterns"""
        print(f"\n📈 PORT RANGE ANALYSIS")
        print("=" * 60)
        
        used_ports = sorted(self.port_allocations.keys())
        
        ranges = {
            "8000-8099": [p for p in used_ports if 8000 <= p <= 8099],
            "8100-8199": [p for p in used_ports if 8100 <= p <= 8199], 
            "8200-8299": [p for p in used_ports if 8200 <= p <= 8299],
            "8300-8399": [p for p in used_ports if 8300 <= p <= 8399],
            "8400-8499": [p for p in used_ports if 8400 <= p <= 8499],
            "8500-8599": [p for p in used_ports if 8500 <= p <= 8599],
            "8600-8699": [p for p in used_ports if 8600 <= p <= 8699],
            "8700-8799": [p for p in used_ports if 8700 <= p <= 8799],
            "8800-8899": [p for p in used_ports if 8800 <= p <= 8899],
            "8900-8999": [p for p in used_ports if 8900 <= p <= 8999]
        }
        
        for range_name, ports in ranges.items():
            usage = len(ports)
            capacity = 100
            percentage = (usage/capacity) * 100
            print(f"   {range_name}: {usage:2d}/100 ports ({percentage:4.1f}%) {ports[:5]}{'...' if len(ports) > 5 else ''}")
    
    def find_available_ports(self, count=10, start_range=9000):
        """Find available ports for new services"""
        print(f"\n🔍 FINDING AVAILABLE PORTS")
        print("=" * 60)
        
        used_ports = set(self.port_allocations.keys())
        available = []
        
        port = start_range
        while len(available) < count and port < 10000:
            if port not in used_ports:
                available.append(port)
            port += 1
        
        print(f"   Next {count} available ports starting from {start_range}:")
        for i, port in enumerate(available, 1):
            print(f"   {i:2d}. Port {port}")
        
        return available
    
    def create_port_allocation_database(self):
        """Create centralized port allocation database"""
        print(f"\n💾 CREATING PORT ALLOCATION DATABASE")
        print("=" * 60)
        
        db_path = os.path.join(self.base_path, "data/port_allocation_registry.db")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create port allocation table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS port_allocations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    port INTEGER UNIQUE NOT NULL,
                    service_name TEXT NOT NULL,
                    allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'ALLOCATED',
                    source_database TEXT,
                    notes TEXT
                )
            """)
            
            # Insert all current allocations
            for port, allocations in self.port_allocations.items():
                # Use the first allocation (prefer service_registry if available)
                main_alloc = None
                for alloc in allocations:
                    if alloc['database'] == 'service_registry':
                        main_alloc = alloc
                        break
                
                if not main_alloc:
                    main_alloc = allocations[0]
                
                cursor.execute("""
                    INSERT OR REPLACE INTO port_allocations 
                    (port, service_name, source_database, notes)
                    VALUES (?, ?, ?, ?)
                """, (
                    port,
                    main_alloc['service'],
                    main_alloc['database'],
                    f"Imported from {len(allocations)} database(s)"
                ))
            
            conn.commit()
            conn.close()
            
            print(f"   ✅ Created port allocation database: {db_path}")
            print(f"   ✅ Imported {len(self.port_allocations)} port allocations")
            
        except Exception as e:
            print(f"   ❌ Error creating database: {e}")
    
    def create_port_allocation_script(self):
        """Create automated port allocation script"""
        print(f"\n🔧 CREATING PORT ALLOCATION PREVENTION SYSTEM")
        print("=" * 60)
        
        script_content = """#!/usr/bin/env python3
\"\"\"
🛡️ ZmartBot Port Allocation Prevention System
Ensures no duplicate port assignments ever happen
\"\"\"

import sqlite3
import os

class PortGuard:
    def __init__(self):
        self.base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
        self.allocation_db = os.path.join(self.base_path, "data/port_allocation_registry.db")
    
    def is_port_available(self, port):
        \"\"\"Check if a port is available for allocation\"\"\"
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
        \"\"\"Allocate a port for a service\"\"\"
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
            cursor.execute(\"\"\"
                INSERT INTO port_allocations (port, service_name, status, notes)
                VALUES (?, ?, 'ALLOCATED', 'Auto-allocated by PortGuard')
            \"\"\", (port, service_name))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Port {port} allocated to {service_name}")
            return port
            
        except Exception as e:
            print(f"❌ Error allocating port: {e}")
            return None
    
    def deallocate_port(self, port):
        \"\"\"Deallocate a port\"\"\"
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
"""
        
        script_path = os.path.join(self.base_path, "port_guard.py")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        print(f"   ✅ Created port allocation prevention script: {script_path}")
    
    def generate_report(self):
        """Generate comprehensive port allocation report"""
        print(f"\n📋 COMPREHENSIVE PORT ALLOCATION REPORT")
        print("=" * 70)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Ports Analyzed: {len(self.port_allocations)}")
        print(f"Conflicts Found: {len(self.conflicts)}")
        
        if self.conflicts:
            print(f"\n🚨 CRITICAL CONFLICTS REQUIRING IMMEDIATE ATTENTION:")
            for conflict in self.conflicts:
                print(f"   Port {conflict['port']}:")
                for service in conflict['services']:
                    print(f"     - {service['service']} ({service['database']})")
        else:
            print(f"\n✅ NO PORT CONFLICTS DETECTED - SYSTEM IS HEALTHY")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        print(f"   1. Use port_guard.py for all future port allocations")
        print(f"   2. Always check port availability before assigning")
        print(f"   3. Use port ranges 9000-9999 for new services")
        print(f"   4. Monitor port_allocation_registry.db regularly")

def main():
    manager = PortManager()
    manager.scan_all_ports()
    no_conflicts = manager.detect_conflicts()
    manager.get_port_range_usage()
    manager.find_available_ports()
    manager.create_port_allocation_database()
    manager.create_port_allocation_script()
    manager.generate_report()
    
    return no_conflicts

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)