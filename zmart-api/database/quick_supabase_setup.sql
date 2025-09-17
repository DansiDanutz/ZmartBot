-- 🚀 ZmartBot Supabase Tables Setup
-- Execute this entire file in your Supabase SQL Editor

-- 1. Service Registry Table
CREATE TABLE IF NOT EXISTS service_registry (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL UNIQUE,
    service_type VARCHAR(100) DEFAULT 'unknown',
    port INTEGER,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    passport_id VARCHAR(100),
    certificate_id VARCHAR(100),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_health_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    health_score INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Database Registry Table
CREATE TABLE IF NOT EXISTS database_registry (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    path TEXT NOT NULL,
    size_bytes BIGINT DEFAULT 0,
    table_count INTEGER DEFAULT 0,
    row_count INTEGER DEFAULT 0,
    health_score INTEGER DEFAULT 0,
    category VARCHAR(100) DEFAULT 'unknown',
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sync_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Service Lifecycle Table
CREATE TABLE IF NOT EXISTS service_lifecycle (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Service Health Metrics Table
CREATE TABLE IF NOT EXISTS service_health_metrics (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    health_score INTEGER NOT NULL,
    response_time_ms INTEGER,
    uptime_percentage DECIMAL(5,2),
    error_count INTEGER DEFAULT 0,
    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Service Connections Table
CREATE TABLE IF NOT EXISTS service_connections (
    id SERIAL PRIMARY KEY,
    source_service VARCHAR(255) NOT NULL,
    target_service VARCHAR(255) NOT NULL,
    connection_type VARCHAR(50) DEFAULT 'api',
    status VARCHAR(50) DEFAULT 'active',
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Add some sample data to test
INSERT INTO service_registry (service_name, service_type, port, status, passport_id, health_score) 
VALUES 
    ('database-service', 'backend', 8900, 'ACTIVE', 'ZMBT-DB-20250829-47C2DE', 100),
    ('registration-service', 'backend', 8902, 'ACTIVE', 'ZMBT-REG-20250829-8F9A1B', 100)
ON CONFLICT (service_name) DO NOTHING;

-- 7. Verify tables were created
SELECT 
    table_name,
    column_count
FROM (
    SELECT 
        t.table_name,
        COUNT(c.column_name) as column_count
    FROM information_schema.tables t
    LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
    WHERE t.table_schema = 'public' 
    AND t.table_name IN ('service_registry', 'database_registry', 'service_lifecycle', 'service_health_metrics', 'service_connections')
    GROUP BY t.table_name
) as table_info
ORDER BY table_name;
