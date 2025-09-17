#!/usr/bin/env python3
"""
🔗 Database Service Adapter
Adapts the existing database service to work with our consolidated single source of truth
WITHOUT changing the original design - just provides compatibility layer
"""

import sqlite3
import os
import hashlib
from pathlib import Path
from datetime import datetime

class DatabaseServiceAdapter:
    """Adapter to make database service work with our consolidated infrastructure"""
    
    def __init__(self):
        self.master_registry_path = Path("/Users/dansidanutz/Desktop/ZmartBot/zmart-api/database/master_database_registry.db")
        self.service_registry_path = Path("/Users/dansidanutz/Desktop/ZmartBot/zmart-api/src/data/service_registry.db")
        
    def initialize_master_registry(self):
        """Initialize the master_database_registry.db with data from our consolidated system"""
        
        # Create master registry database with expected schema
        conn = sqlite3.connect(self.master_registry_path)
        cursor = conn.cursor()
        
        # Create the expected database_registry table with all required columns matching DatabaseInfo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS database_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                path TEXT NOT NULL,
                size_bytes INTEGER DEFAULT 0,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                table_count INTEGER DEFAULT 0,
                record_count INTEGER DEFAULT 0,
                health_score REAL DEFAULT 100.0,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                schema_hash TEXT DEFAULT '',
                category TEXT DEFAULT 'service',
                description TEXT DEFAULT '',
                integration_level INTEGER DEFAULT 3,
                backup_status TEXT DEFAULT 'none',
                is_active BOOLEAN DEFAULT 1,
                type TEXT DEFAULT 'SQLite',
                tags TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Populate with our current service data
        if self.service_registry_path.exists():
            service_conn = sqlite3.connect(self.service_registry_path)
            service_cursor = service_conn.cursor()
            
            # Get all services with their data
            service_cursor.execute('''
                SELECT service_name, python_file_path, port, certification_level 
                FROM service_registry 
                WHERE service_name IS NOT NULL
            ''')
            
            services = service_cursor.fetchall()
            
            for service_name, file_path, port, level in services:
                # Insert service as database entry with all required columns
                cursor.execute('''
                    INSERT OR REPLACE INTO database_registry 
                    (name, path, status, category, table_count, record_count, health_score, 
                     last_checked, schema_hash, integration_level, backup_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    service_name,
                    file_path or f"Service on port {port}",
                    f"Level {level}" if level else "active",
                    "service",
                    1,  # Each service counts as 1 table
                    1,  # Each service counts as 1 record
                    100.0,  # Default health score
                    datetime.now(),  # Last checked
                    "service_schema",  # Default schema hash
                    int(level) if level else 1,  # Integration level
                    "active"  # Backup status
                ))
            
            service_conn.close()
            
            print(f"✅ Initialized master registry with {len(services)} service entries")
        
        # Add actual database files
        project_root = Path("/Users/dansidanutz/Desktop/ZmartBot/zmart-api")
        
        for db_file in project_root.rglob("*.db"):
            if db_file.name == "master_database_registry.db":
                continue
                
            try:
                stat = db_file.stat()
                # Generate schema hash based on file properties
                schema_hash = hashlib.md5(f"{db_file.name}_{stat.st_size}_{stat.st_mtime}".encode()).hexdigest()[:16]
                
                # Categorize database based on name patterns
                category = self.categorize_database(db_file.name)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO database_registry 
                    (name, path, size_bytes, last_modified, status, category, health_score, 
                     last_checked, schema_hash, integration_level, backup_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    db_file.name,
                    str(db_file),
                    stat.st_size,
                    datetime.fromtimestamp(stat.st_mtime),
                    "active" if stat.st_size > 0 else "empty",
                    category,  # Use categorized category
                    90.0 if stat.st_size > 0 else 50.0,  # Health score based on size
                    datetime.now(),  # Last checked
                    schema_hash,  # Schema hash
                    2,  # Default integration level for databases
                    "monitored"  # Backup status
                ))
            except Exception as e:
                print(f"⚠️  Could not process {db_file}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Master database registry initialized at {self.master_registry_path}")
        
    def get_registry_stats(self):
        """Get statistics about the registry"""
        if not self.master_registry_path.exists():
            return {"error": "Master registry not initialized"}
            
        conn = sqlite3.connect(self.master_registry_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM database_registry")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM database_registry WHERE category = 'service'")
        service_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM database_registry WHERE category = 'database'")
        db_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_entries": total_count,
            "services": service_count,
            "databases": db_count,
            "registry_path": str(self.master_registry_path)
        }
    
    def categorize_database(self, db_name: str) -> str:
        """Categorize database based on name with comprehensive visual categories"""
        name_lower = db_name.lower()
        
        # 🏗️ Core System Infrastructure (Critical)
        if any(term in name_lower for term in ['service_registry', 'master_database_registry']):
            return "🏗️ System Core"
        elif any(term in name_lower for term in ['passport_registry', 'cert', 'discovery_registry']):
            return "🔐 Service Management"
        
        # 📊 Trading & Market Data
        elif any(term in name_lower for term in ['symbol', 'market', 'trading', 'binance', 'kucoin']):
            return "📊 Trading Data"
        elif any(term in name_lower for term in ['risk', 'cowen', 'riskmetric']):
            return "⚠️ Risk Management"
        elif any(term in name_lower for term in ['prediction', 'ultimate']):
            return "🎯 Predictions"
        
        # 🤖 AI & Machine Learning
        elif any(term in name_lower for term in ['learning', 'pattern', 'grok', 'enhanced']):
            return "🤖 AI Systems"
        elif any(term in name_lower for term in ['cryptometer', 'cryptoverse']):
            return "🔍 Data Mining"
        
        # 🛡️ Security & Authentication  
        elif any(term in name_lower for term in ['auth', 'security', 'api_key', 'session']):
            return "🛡️ Security"
        
        # 📈 Analytics & Reporting
        elif any(term in name_lower for term in ['analytic', 'history', 'indicator', 'achievements']):
            return "📈 Analytics"
        elif any(term in name_lower for term in ['log', 'servicelog', 'update_log']):
            return "📝 Logging"
        
        # 🔧 System Maintenance
        elif any(term in name_lower for term in ['backup', 'test_', 'temp_', 'tmp_']):
            return "🔧 Maintenance"
        elif any(term in name_lower for term in ['governance', 'failover', 'lifecycle']):
            return "⚙️ Operations"
        
        # 💾 Data Storage
        elif any(term in name_lower for term in ['data', 'storage', 'warehouse']):
            return "💾 Data Storage"
        
        # 🔄 Integration & Services
        elif any(term in name_lower for term in ['discovery', 'workflow', 'recommendation']):
            return "🔄 Integration"
        elif any(term in name_lower for term in ['winner', 'impact']):
            return "🏆 Optimization"
        
        # 🔌 Infrastructure
        elif any(term in name_lower for term in ['port', 'registry']):
            return "🔌 Infrastructure"
        
        # ❓ Unategorized
        else:
            return "❓ Other"

if __name__ == "__main__":
    adapter = DatabaseServiceAdapter()
    
    print("🔗 Initializing Database Service Adapter...")
    adapter.initialize_master_registry()
    
    stats = adapter.get_registry_stats()
    print(f"📊 Registry Statistics: {stats}")
    
    print("✅ Database service is now compatible with consolidated architecture!")