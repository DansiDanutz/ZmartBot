# 🚀 Supabase Tables Setup Guide

## Quick Setup Instructions

### Step 1: Access Supabase Dashboard
1. Go to: https://supabase.com/dashboard
2. Sign in to your account
3. Select project: `asjtxrmftmutcsnqgidy`

### Step 2: Open SQL Editor
1. Click on "SQL Editor" in the left sidebar
2. Click "New query"

### Step 3: Execute SQL Commands
Copy and paste each SQL command below, then click "Run":

## SQL Commands to Execute

### 1. Service Registry Table
```sql
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
```

### 2. Database Registry Table
```sql
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
```

### 3. Service Lifecycle Table
```sql
CREATE TABLE IF NOT EXISTS service_lifecycle (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Service Health Metrics Table
```sql
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
```

### 5. Service Connections Table
```sql
CREATE TABLE IF NOT EXISTS service_connections (
    id SERIAL PRIMARY KEY,
    source_service VARCHAR(255) NOT NULL,
    target_service VARCHAR(255) NOT NULL,
    connection_type VARCHAR(50) DEFAULT 'api',
    status VARCHAR(50) DEFAULT 'active',
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Step 4: Test the Setup
After creating all tables, run this test command:

```bash
curl -X POST "http://127.0.0.1:8900/api/services/sync-to-supabase"
```

## Expected Result
You should see a success message indicating that the service registry data has been synced to Supabase.

## Troubleshooting
- If you get permission errors, make sure you're using the correct Supabase project
- If tables already exist, the commands will be skipped safely
- If sync fails, check that the database service is running with the SUPABASE_KEY environment variable

## Next Steps
Once tables are created and sync is working:
1. Your service registry data will be automatically synced to Supabase
2. You can view the data in the Supabase dashboard under "Table Editor"
3. The database service will maintain real-time sync with Supabase
