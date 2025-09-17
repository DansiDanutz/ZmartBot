#!/usr/bin/env python3
"""
🏛️ MASTER DATABASE REGISTRY SYSTEM
Advanced database catalog and duplicate prevention system for ZmartBot ecosystem
CRITICAL: Prevents database duplication and enforces single source of truth
"""

import sqlite3
import os
import hashlib
import json
from datetime import datetime
from pathlib import Path
import difflib

class MasterDatabaseRegistry:
    def __init__(self):
        self.project_root = Path('/Users/dansidanutz/Desktop/ZmartBot')
        self.registry_path = self.project_root / 'zmart-api/src/data/master_database_registry.db'
        self.duplicate_log = []
        self.forbidden_patterns = []
        
        # Initialize registry database
        self.init_registry_database()
        print("🏛️ Master Database Registry System Initialized")
    
    def init_registry_database(self):
        """Initialize the master database registry with comprehensive schema"""
        conn = sqlite3.connect(str(self.registry_path))
        cursor = conn.cursor()
        
        # Main database registry table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS database_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                database_name TEXT NOT NULL,
                full_path TEXT UNIQUE NOT NULL,
                relative_path TEXT NOT NULL,
                database_type TEXT NOT NULL,
                purpose TEXT,
                size_bytes INTEGER,
                schema_hash TEXT,
                structure_signature TEXT,
                created_date TIMESTAMP,
                last_modified TIMESTAMP,
                last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                table_count INTEGER DEFAULT 0,
                record_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                is_duplicate BOOLEAN DEFAULT FALSE,
                duplicate_of INTEGER REFERENCES database_registry(id),
                access_pattern TEXT DEFAULT 'UNKNOWN',
                owner_service TEXT,
                criticality_level TEXT DEFAULT 'MEDIUM',
                backup_required BOOLEAN DEFAULT TRUE,
                notes TEXT
            )
        ''')
        
        # Database structure comparison table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS database_structures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                database_id INTEGER REFERENCES database_registry(id),
                table_name TEXT NOT NULL,
                schema_definition TEXT NOT NULL,
                column_count INTEGER,
                index_info TEXT,
                constraints_info TEXT
            )
        ''')
        
        # Duplicate detection log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplicate_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                database1_id INTEGER REFERENCES database_registry(id),
                database2_id INTEGER REFERENCES database_registry(id),
                similarity_score REAL,
                duplicate_type TEXT,
                action_taken TEXT,
                details TEXT
            )
        ''')
        
        # Prevention rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prevention_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT UNIQUE NOT NULL,
                pattern_match TEXT NOT NULL,
                action TEXT NOT NULL,
                severity TEXT DEFAULT 'HIGH',
                enabled BOOLEAN DEFAULT TRUE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Database access log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS database_access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                database_id INTEGER REFERENCES database_registry(id),
                access_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_type TEXT,
                service_name TEXT,
                operation_type TEXT,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Master Database Registry schema initialized")
    
    def get_database_schema_hash(self, db_path):
        """Generate hash of database schema for comparison"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get all table schemas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            schema_data = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                schema = cursor.fetchone()
                if schema:
                    schema_data[table_name] = schema[0]
            
            conn.close()
            
            # Generate hash of combined schemas
            schema_string = json.dumps(schema_data, sort_keys=True)
            return hashlib.md5(schema_string.encode()).hexdigest()
        
        except Exception as e:
            print(f"❌ Error analyzing schema for {db_path}: {e}")
            return None
    
    def get_database_structure_signature(self, db_path):
        """Create detailed structure signature for similarity comparison"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            structure = {
                'tables': {},
                'indexes': {},
                'triggers': {}
            }
            
            # Get table structures
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                structure['tables'][table_name] = {
                    'columns': [(col[1], col[2], col[3], col[5]) for col in columns],
                    'column_count': len(columns)
                }
            
            # Get indexes
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index'")
            indexes = cursor.fetchall()
            for idx in indexes:
                if idx[1]:  # Skip auto-generated indexes
                    structure['indexes'][idx[0]] = idx[1]
            
            conn.close()
            
            return json.dumps(structure, sort_keys=True)
        
        except Exception as e:
            print(f"❌ Error creating structure signature for {db_path}: {e}")
            return "{}"
    
    def calculate_similarity(self, sig1, sig2):
        """Calculate similarity between two database structures"""
        try:
            struct1 = json.loads(sig1)
            struct2 = json.loads(sig2)
            
            # Compare table names
            tables1 = set(struct1.get('tables', {}).keys())
            tables2 = set(struct2.get('tables', {}).keys())
            
            if not tables1 or not tables2:
                return 0.0
            
            common_tables = tables1.intersection(tables2)
            total_tables = tables1.union(tables2)
            
            table_similarity = len(common_tables) / len(total_tables) if total_tables else 0
            
            # Compare column structures for common tables
            column_similarity = 0
            if common_tables:
                column_matches = 0
                total_comparisons = 0
                
                for table in common_tables:
                    cols1 = struct1['tables'][table]['columns']
                    cols2 = struct2['tables'][table]['columns']
                    
                    # Compare column names and types
                    col_names1 = {col[0]: col[1] for col in cols1}
                    col_names2 = {col[0]: col[1] for col in cols2}
                    
                    common_cols = set(col_names1.keys()).intersection(set(col_names2.keys()))
                    total_cols = set(col_names1.keys()).union(set(col_names2.keys()))
                    
                    if total_cols:
                        column_matches += len(common_cols)
                        total_comparisons += len(total_cols)
                
                column_similarity = column_matches / total_comparisons if total_comparisons else 0
            
            # Weighted average
            return (table_similarity * 0.6) + (column_similarity * 0.4)
        
        except Exception as e:
            print(f"❌ Error calculating similarity: {e}")
            return 0.0
    
    def scan_all_databases(self):
        """Comprehensive scan of all databases in ZmartBot system"""
        print("🔍 Starting comprehensive database scan...")
        
        conn = sqlite3.connect(str(self.registry_path))
        cursor = conn.cursor()
        
        # Find all .db files
        db_files = []
        for root, dirs, files in os.walk(str(self.project_root)):
            for file in files:
                if file.endswith('.db'):
                    full_path = os.path.join(root, file)
                    db_files.append(Path(full_path))
        
        print(f"📊 Found {len(db_files)} database files")
        
        # Process each database
        for db_path in db_files:
            try:
                # Get file stats
                stat = db_path.stat()
                size_bytes = stat.st_size
                created_date = datetime.fromtimestamp(stat.st_ctime)
                modified_date = datetime.fromtimestamp(stat.st_mtime)
                
                # Calculate relative path
                relative_path = db_path.relative_to(self.project_root)
                
                # Get database metadata
                schema_hash = self.get_database_schema_hash(db_path)
                structure_sig = self.get_database_structure_signature(db_path)
                
                # Count tables and records
                table_count, record_count = self.count_database_content(db_path)
                
                # Determine database type and purpose
                db_type, purpose = self.classify_database(db_path)
                
                # Check if already exists
                cursor.execute("SELECT id FROM database_registry WHERE full_path = ?", (str(db_path),))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing entry
                    cursor.execute('''
                        UPDATE database_registry 
                        SET size_bytes = ?, last_modified = ?, last_scanned = ?, 
                            table_count = ?, record_count = ?, schema_hash = ?, 
                            structure_signature = ?
                        WHERE id = ?
                    ''', (size_bytes, modified_date, datetime.now(), table_count, 
                          record_count, schema_hash, structure_sig, existing[0]))
                else:
                    # Insert new entry
                    cursor.execute('''
                        INSERT INTO database_registry 
                        (database_name, full_path, relative_path, database_type, purpose,
                         size_bytes, schema_hash, structure_signature, created_date, 
                         last_modified, table_count, record_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (db_path.name, str(db_path), str(relative_path), db_type, purpose,
                          size_bytes, schema_hash, structure_sig, created_date, 
                          modified_date, table_count, record_count))
                
                print(f"✅ Cataloged: {db_path.name} ({size_bytes} bytes, {table_count} tables)")
            
            except Exception as e:
                print(f"❌ Error processing {db_path}: {e}")
        
        conn.commit()
        conn.close()
        
        print("✅ Database scan completed")
        return len(db_files)
    
    def count_database_content(self, db_path):
        """Count tables and records in database"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Count tables
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # Count total records across all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            total_records = 0
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    total_records += count
                except:
                    pass  # Skip if table has issues
            
            conn.close()
            return table_count, total_records
        
        except Exception as e:
            return 0, 0
    
    def classify_database(self, db_path):
        """Classify database type and purpose based on name and location"""
        path_str = str(db_path).lower()
        name = db_path.name.lower()
        
        # Classification logic
        if 'registry' in name:
            return 'REGISTRY', 'Service and system registry management'
        elif 'learning' in name or 'ml' in name:
            return 'MACHINE_LEARNING', 'Machine learning data and models'
        elif 'analytics' in name or 'analysis' in name:
            return 'ANALYTICS', 'Data analysis and reporting'
        elif 'risk' in name:
            return 'RISK_MANAGEMENT', 'Risk assessment and management'
        elif 'auth' in name or 'passport' in name:
            return 'AUTHENTICATION', 'User and service authentication'
        elif 'crypto' in name:
            return 'CRYPTOCURRENCY', 'Cryptocurrency data and operations'
        elif 'achievement' in name:
            return 'GAMIFICATION', 'Achievement and progress tracking'
        elif 'governance' in name:
            return 'GOVERNANCE', 'System governance and compliance'
        elif 'test' in name:
            return 'TESTING', 'Testing and development data'
        elif 'archive' in path_str or 'backup' in path_str:
            return 'ARCHIVE', 'Archived or backup data'
        else:
            return 'OPERATIONAL', 'General operational data'
    
    def detect_duplicates(self):
        """Advanced duplicate detection with structure comparison"""
        print("🔍 Starting duplicate detection analysis...")
        
        conn = sqlite3.connect(str(self.registry_path))
        cursor = conn.cursor()
        
        # Get all databases for comparison
        cursor.execute('''
            SELECT id, database_name, full_path, schema_hash, structure_signature 
            FROM database_registry 
            WHERE is_active = TRUE
        ''')
        databases = cursor.fetchall()
        
        duplicates_found = 0
        
        # Compare each database with every other database
        for i, db1 in enumerate(databases):
            for j, db2 in enumerate(databases[i+1:], i+1):
                similarity = 0
                duplicate_type = None
                
                # Check for exact schema match
                if db1[3] and db2[3] and db1[3] == db2[3]:
                    similarity = 1.0
                    duplicate_type = 'EXACT_SCHEMA'
                else:
                    # Calculate structural similarity
                    similarity = self.calculate_similarity(db1[4], db2[4])
                    if similarity > 0.9:
                        duplicate_type = 'HIGH_SIMILARITY'
                    elif similarity > 0.7:
                        duplicate_type = 'MODERATE_SIMILARITY'
                
                # Log potential duplicates
                if similarity > 0.7:  # 70% similarity threshold
                    cursor.execute('''
                        INSERT INTO duplicate_detections 
                        (database1_id, database2_id, similarity_score, duplicate_type, details)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (db1[0], db2[0], similarity, duplicate_type, 
                          f"Similarity: {similarity:.2%} between {db1[1]} and {db2[1]}"))
                    
                    duplicates_found += 1
                    print(f"🚨 DUPLICATE DETECTED: {db1[1]} ↔ {db2[1]} (Similarity: {similarity:.2%})")
                    
                    # Mark as duplicate if very similar
                    if similarity > 0.9:
                        cursor.execute('''
                            UPDATE database_registry 
                            SET is_duplicate = TRUE, duplicate_of = ?
                            WHERE id = ? AND created_date > (SELECT created_date FROM database_registry WHERE id = ?)
                        ''', (db1[0], db2[0], db1[0]))
        
        conn.commit()
        conn.close()
        
        print(f"🎯 Duplicate detection completed: {duplicates_found} potential duplicates found")
        return duplicates_found
    
    def setup_prevention_rules(self):
        """Setup database creation prevention rules"""
        print("🛡️ Setting up duplicate prevention rules...")
        
        conn = sqlite3.connect(str(self.registry_path))
        cursor = conn.cursor()
        
        # Define prevention rules
        prevention_rules = [
            ('NO_REGISTRY_DUPLICATES', '%registry%.db', 'BLOCK', 'CRITICAL'),
            ('NO_SERVICE_DUPLICATES', '%service%.db', 'WARN', 'HIGH'),
            ('NO_SIMILAR_NAMES', '%similar_pattern%', 'REVIEW', 'MEDIUM'),
            ('SINGLE_AUTH_DB', '%auth%', 'BLOCK', 'HIGH'),
            ('SINGLE_PASSPORT_DB', '%passport%', 'BLOCK', 'HIGH'),
            ('NO_TEMP_PERMANENT', 'temp_%', 'WARN', 'MEDIUM')
        ]
        
        for rule in prevention_rules:
            cursor.execute('''
                INSERT OR REPLACE INTO prevention_rules 
                (rule_name, pattern_match, action, severity)
                VALUES (?, ?, ?, ?)
            ''', rule)
        
        conn.commit()
        conn.close()
        
        print("✅ Prevention rules configured")
    
    def generate_registry_report(self):
        """Generate comprehensive database registry report"""
        conn = sqlite3.connect(str(self.registry_path))
        cursor = conn.cursor()
        
        # Get summary statistics
        cursor.execute("SELECT COUNT(*) FROM database_registry")
        total_databases = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM database_registry WHERE is_duplicate = TRUE")
        duplicate_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT database_type, COUNT(*) FROM database_registry GROUP BY database_type")
        type_breakdown = cursor.fetchall()
        
        cursor.execute("SELECT SUM(size_bytes) FROM database_registry")
        total_size = cursor.fetchone()[0] or 0
        
        # Get recent duplicates
        cursor.execute('''
            SELECT d.similarity_score, d.duplicate_type, d.detection_date,
                   db1.database_name, db2.database_name
            FROM duplicate_detections d
            JOIN database_registry db1 ON d.database1_id = db1.id
            JOIN database_registry db2 ON d.database2_id = db2.id
            ORDER BY d.detection_date DESC
            LIMIT 10
        ''')
        recent_duplicates = cursor.fetchall()
        
        conn.close()
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_databases': total_databases,
                'duplicate_databases': duplicate_count,
                'unique_databases': total_databases - duplicate_count,
                'total_size_mb': round(total_size / (1024*1024), 2)
            },
            'type_breakdown': dict(type_breakdown),
            'recent_duplicates': [
                {
                    'similarity': dup[0],
                    'type': dup[1],
                    'date': dup[2],
                    'database1': dup[3],
                    'database2': dup[4]
                }
                for dup in recent_duplicates
            ]
        }
        
        # Save report
        report_path = self.project_root / 'zmart-api/database_consolidation/master_database_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 MASTER DATABASE REGISTRY REPORT")
        print(f"Total Databases: {total_databases}")
        print(f"Duplicates Found: {duplicate_count}")
        print(f"Total Size: {report['summary']['total_size_mb']} MB")
        print(f"Report saved: {report_path}")
        
        return report
    
    def run_complete_analysis(self):
        """Run complete database registry analysis"""
        print("🚀 Starting Master Database Registry Analysis...")
        
        # Step 1: Scan all databases
        total_dbs = self.scan_all_databases()
        
        # Step 2: Detect duplicates
        duplicates = self.detect_duplicates()
        
        # Step 3: Setup prevention rules
        self.setup_prevention_rules()
        
        # Step 4: Generate comprehensive report
        report = self.generate_registry_report()
        
        print(f"\n🎉 MASTER DATABASE REGISTRY ANALYSIS COMPLETE!")
        print(f"✅ Cataloged {total_dbs} databases")
        print(f"🚨 Found {duplicates} potential duplicates")
        print(f"🛡️ Prevention system active")
        print(f"📊 Full report available")
        
        return report

if __name__ == "__main__":
    registry = MasterDatabaseRegistry()
    registry.run_complete_analysis()