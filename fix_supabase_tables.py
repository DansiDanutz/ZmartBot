#!/usr/bin/env python3
"""
Fix Missing Supabase Tables for ZmartBot Orchestration
This script creates the missing tables that were identified in the integration tests
"""

import asyncio
import logging
from supabase_orchestration_integration import SupabaseOrchestrationManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SupabaseTableFix')

async def create_missing_tables():
    """Create the missing tables for complete orchestration"""
    
    tables_sql = [
        # Service Dependencies Table
        """
        CREATE TABLE IF NOT EXISTS service_dependencies (
            id SERIAL PRIMARY KEY,
            service_id INTEGER REFERENCES service_registry(id) ON DELETE CASCADE,
            depends_on_service_id INTEGER REFERENCES service_registry(id) ON DELETE CASCADE,
            dependency_type VARCHAR(50) DEFAULT 'required',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(service_id, depends_on_service_id)
        );
        """,
        
        # Service Configurations Table
        """
        CREATE TABLE IF NOT EXISTS service_configurations (
            id SERIAL PRIMARY KEY,
            service_id INTEGER REFERENCES service_registry(id) ON DELETE CASCADE,
            config_key VARCHAR(255) NOT NULL,
            config_value TEXT,
            config_type VARCHAR(50) DEFAULT 'string',
            is_encrypted BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(service_id, config_key)
        );
        """,
        
        # Service Health Metrics Table
        """
        CREATE TABLE IF NOT EXISTS service_health_metrics (
            id SERIAL PRIMARY KEY,
            service_id INTEGER REFERENCES service_registry(id) ON DELETE CASCADE,
            cpu_usage DECIMAL(5,2),
            memory_usage DECIMAL(5,2),
            disk_usage DECIMAL(5,2),
            response_time_ms INTEGER,
            error_count INTEGER DEFAULT 0,
            request_count INTEGER DEFAULT 0,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Service Communications Table
        """
        CREATE TABLE IF NOT EXISTS service_communications (
            id SERIAL PRIMARY KEY,
            from_service_id INTEGER REFERENCES service_registry(id) ON DELETE CASCADE,
            to_service_id INTEGER REFERENCES service_registry(id) ON DELETE CASCADE,
            communication_type VARCHAR(50) NOT NULL,
            endpoint VARCHAR(255),
            method VARCHAR(10),
            status_code INTEGER,
            response_time_ms INTEGER,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Service Logs Table
        """
        CREATE TABLE IF NOT EXISTS service_logs (
            id SERIAL PRIMARY KEY,
            service_id INTEGER REFERENCES service_registry(id) ON DELETE CASCADE,
            log_level VARCHAR(10) NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata JSONB
        );
        """,
        
        # Orchestration States Table
        """
        CREATE TABLE IF NOT EXISTS orchestration_states (
            id SERIAL PRIMARY KEY,
            state_name VARCHAR(100) NOT NULL UNIQUE,
            state_data JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
    ]
    
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_service_health_timestamp ON service_health_metrics(timestamp);",
        "CREATE INDEX IF NOT EXISTS idx_service_health_service_id ON service_health_metrics(service_id);",
        "CREATE INDEX IF NOT EXISTS idx_service_logs_timestamp ON service_logs(timestamp);",
        "CREATE INDEX IF NOT EXISTS idx_service_logs_service_id ON service_logs(service_id);",
        "CREATE INDEX IF NOT EXISTS idx_service_communications_timestamp ON service_communications(timestamp);",
        "CREATE INDEX IF NOT EXISTS idx_service_dependencies_service ON service_dependencies(service_id);",
        "CREATE INDEX IF NOT EXISTS idx_service_configurations_service ON service_configurations(service_id);"
    ]
    
    async with SupabaseOrchestrationManager() as manager:
        # Create tables using direct API calls
        for i, table_sql in enumerate(tables_sql, 1):
            try:
                # Use Supabase RPC or direct API calls
                # For now, we'll use the REST API with stored procedures
                logger.info(f"🔄 Creating table {i}/{len(tables_sql)}...")
                
                # Try to create via direct HTTP call to Supabase
                response = await manager.session.post(
                    f'{manager.supabase_url}/rest/v1/rpc/create_table_if_not_exists',
                    json={'sql': table_sql.strip()}
                )
                
                if response.status in [200, 201]:
                    logger.info(f"✅ Table {i} created successfully")
                else:
                    logger.warning(f"⚠️ Table {i} creation returned status {response.status}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to create table {i}: {e}")
        
        # Create indexes
        for i, index_sql in enumerate(indexes_sql, 1):
            try:
                logger.info(f"🔄 Creating index {i}/{len(indexes_sql)}...")
                
                response = await manager.session.post(
                    f'{manager.supabase_url}/rest/v1/rpc/create_index_if_not_exists',
                    json={'sql': index_sql.strip()}
                )
                
                if response.status in [200, 201]:
                    logger.info(f"✅ Index {i} created successfully")
                else:
                    logger.warning(f"⚠️ Index {i} creation returned status {response.status}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to create index {i}: {e}")

async def verify_tables():
    """Verify that all tables exist"""
    
    expected_tables = [
        'service_registry',
        'service_dependencies', 
        'service_configurations',
        'service_health_metrics',
        'service_communications',
        'service_logs',
        'orchestration_states'
    ]
    
    # Simple verification by trying to query each table
    async with SupabaseOrchestrationManager() as manager:
        existing_tables = []
        
        for table_name in expected_tables:
            try:
                response = await manager.session.get(
                    f'{manager.supabase_url}/rest/v1/{table_name}?limit=1'
                )
                
                if response.status == 200:
                    existing_tables.append(table_name)
                    logger.info(f"✅ Table {table_name} exists and accessible")
                else:
                    logger.warning(f"❌ Table {table_name} not accessible (status: {response.status})")
                    
            except Exception as e:
                logger.warning(f"❌ Table {table_name} check failed: {e}")
        
        print(f"\n📊 Table Status Summary:")
        print(f"   • Expected: {len(expected_tables)}")
        print(f"   • Found: {len(existing_tables)}")
        print(f"   • Success Rate: {(len(existing_tables)/len(expected_tables))*100:.1f}%")
        
        if len(existing_tables) == len(expected_tables):
            print(f"🎉 All tables are ready for orchestration!")
            return True
        else:
            missing = set(expected_tables) - set(existing_tables)
            print(f"⚠️ Missing tables: {', '.join(missing)}")
            return False

async def main():
    """Main execution"""
    print("🔧 ZmartBot Supabase Tables Fix")
    print("=" * 50)
    
    # First, verify current state
    logger.info("📋 Checking current table status...")
    initial_status = await verify_tables()
    
    if not initial_status:
        logger.info("🛠️ Creating missing tables...")
        await create_missing_tables()
        
        # Verify again
        logger.info("✅ Verifying table creation...")
        final_status = await verify_tables()
        
        if final_status:
            print("\n🎉 Bug fix complete! All orchestration tables are ready.")
        else:
            print("\n⚠️ Some tables still missing. Manual intervention may be required.")
    else:
        print("\n✅ All tables already exist. No fix needed.")

if __name__ == "__main__":
    asyncio.run(main())