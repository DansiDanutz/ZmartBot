-- =================================================================
-- ZmartBot Database Visualization SQL Queries
-- Custom queries for building advanced visualizations in Supabase
-- =================================================================

-- 1. DATABASE HEALTH DASHBOARD QUERY
-- Shows database health metrics with categorization
CREATE OR REPLACE VIEW database_health_overview AS
SELECT 
    name,
    category,
    health_score,
    size_bytes / (1024 * 1024) as size_mb,
    table_count,
    row_count,
    CASE 
        WHEN health_score >= 90 THEN 'Excellent'
        WHEN health_score >= 75 THEN 'Good'  
        WHEN health_score >= 50 THEN 'Fair'
        ELSE 'Poor'
    END as health_status,
    CASE
        WHEN size_bytes < 1024*1024 THEN 'Small (<1MB)'
        WHEN size_bytes < 5*1024*1024 THEN 'Medium (1-5MB)'
        WHEN size_bytes < 10*1024*1024 THEN 'Large (5-10MB)'
        ELSE 'Very Large (>10MB)'
    END as size_category,
    last_synced,
    sync_status
FROM database_registry
ORDER BY health_score DESC, size_bytes DESC;

-- 2. SERVICE LIFECYCLE VISUALIZATION
-- Shows the 3-database service lifecycle progression
CREATE OR REPLACE VIEW service_lifecycle_stats AS
SELECT 
    category,
    COUNT(*) as total_databases,
    SUM(row_count) as total_services,
    AVG(health_score) as avg_health,
    SUM(size_bytes) / (1024 * 1024) as total_size_mb,
    CASE 
        WHEN category = 'service_lifecycle' THEN
            CASE 
                WHEN name LIKE '%discovery%' THEN 'Level 1: Discovery'
                WHEN name LIKE '%passport%' THEN 'Level 2: Passport'  
                WHEN name LIKE '%service_registry%' THEN 'Level 3: Certified'
                ELSE 'Unknown Level'
            END
        ELSE category
    END as service_level
FROM database_registry
GROUP BY category, service_level
ORDER BY service_level, avg_health DESC;

-- 3. REAL-TIME SYNC PERFORMANCE METRICS
-- Tracks sync performance over time
CREATE OR REPLACE VIEW sync_performance_timeline AS
SELECT 
    database_name,
    sync_timestamp,
    status,
    tables_synced,
    rows_synced,
    sync_duration_ms,
    DATE_TRUNC('hour', sync_timestamp) as sync_hour,
    COUNT(*) OVER (PARTITION BY database_name ORDER BY sync_timestamp) as sync_sequence
FROM database_sync_log
ORDER BY sync_timestamp DESC;

-- 4. DATABASE CATEGORY ANALYSIS
-- Detailed breakdown by category with trends
CREATE OR REPLACE VIEW category_analysis AS
SELECT 
    category,
    COUNT(*) as database_count,
    AVG(health_score) as avg_health,
    MIN(health_score) as min_health,
    MAX(health_score) as max_health,
    SUM(table_count) as total_tables,
    SUM(row_count) as total_records,
    SUM(size_bytes) / (1024 * 1024) as total_size_mb,
    ROUND(
        SUM(size_bytes) * 100.0 / SUM(SUM(size_bytes)) OVER (), 
        2
    ) as size_percentage
FROM database_registry
GROUP BY category
ORDER BY database_count DESC;

-- 5. HEALTH TREND ANALYSIS
-- Historical health score trends
CREATE OR REPLACE VIEW health_trend_analysis AS
SELECT 
    database_name,
    metric_timestamp,
    metric_value as health_score,
    LAG(metric_value) OVER (
        PARTITION BY database_name 
        ORDER BY metric_timestamp
    ) as previous_health,
    metric_value - LAG(metric_value) OVER (
        PARTITION BY database_name 
        ORDER BY metric_timestamp  
    ) as health_change,
    DATE_TRUNC('day', metric_timestamp) as health_date
FROM database_health_metrics
WHERE metric_name = 'health_score'
ORDER BY database_name, metric_timestamp DESC;

-- 6. TOP PERFORMING DATABASES
-- Best performing databases by multiple criteria
CREATE OR REPLACE VIEW top_performers AS
SELECT 
    name,
    category,
    health_score,
    table_count,
    row_count,
    size_bytes / (1024 * 1024) as size_mb,
    sync_status,
    last_synced,
    RANK() OVER (ORDER BY health_score DESC) as health_rank,
    RANK() OVER (ORDER BY row_count DESC) as data_rank,
    RANK() OVER (ORDER BY table_count DESC) as complexity_rank,
    (
        RANK() OVER (ORDER BY health_score DESC) +
        RANK() OVER (ORDER BY row_count DESC) + 
        RANK() OVER (ORDER BY table_count DESC)
    ) / 3.0 as overall_score
FROM database_registry
WHERE health_score > 0
ORDER BY overall_score ASC;

-- 7. SYNC STATUS DASHBOARD
-- Real-time sync monitoring
CREATE OR REPLACE VIEW sync_status_dashboard AS
SELECT 
    dr.name,
    dr.category,
    dr.sync_status,
    dr.last_synced,
    COALESCE(dsl.sync_timestamp, dr.last_synced) as last_sync_attempt,
    COALESCE(dsl.status, 'no_recent_sync') as last_sync_status,
    COALESCE(dsl.tables_synced, 0) as last_tables_synced,
    COALESCE(dsl.rows_synced, 0) as last_rows_synced,
    COALESCE(dsl.sync_duration_ms, 0) as last_sync_duration,
    CASE 
        WHEN dr.last_synced > NOW() - INTERVAL '1 hour' THEN 'Recent'
        WHEN dr.last_synced > NOW() - INTERVAL '1 day' THEN 'Today' 
        WHEN dr.last_synced > NOW() - INTERVAL '1 week' THEN 'This Week'
        ELSE 'Outdated'
    END as sync_freshness
FROM database_registry dr
LEFT JOIN LATERAL (
    SELECT * FROM database_sync_log dsl2 
    WHERE dsl2.database_name = dr.name 
    ORDER BY dsl2.sync_timestamp DESC 
    LIMIT 1
) dsl ON true
ORDER BY dr.last_synced DESC;

-- 8. DATA VOLUME ANALYSIS
-- Understanding data distribution and growth
CREATE OR REPLACE VIEW data_volume_analysis AS  
SELECT 
    category,
    name,
    table_count,
    row_count,
    size_bytes / (1024 * 1024) as size_mb,
    CASE 
        WHEN table_count > 0 THEN row_count::float / table_count 
        ELSE 0 
    END as avg_rows_per_table,
    CASE 
        WHEN row_count > 0 THEN (size_bytes::float / row_count) 
        ELSE 0 
    END as bytes_per_row,
    created_at,
    updated_at,
    EXTRACT(DAYS FROM (updated_at - created_at)) as database_age_days
FROM database_registry
ORDER BY size_mb DESC;

-- =================================================================
-- VISUALIZATION-READY AGGREGATED QUERIES
-- These return data perfect for charts and graphs
-- =================================================================

-- CHART DATA: Health Score Distribution
CREATE OR REPLACE VIEW chart_health_distribution AS
SELECT 
    CASE 
        WHEN health_score >= 90 THEN 'Excellent (90-100%)'
        WHEN health_score >= 75 THEN 'Good (75-89%)'
        WHEN health_score >= 50 THEN 'Fair (50-74%)'
        ELSE 'Poor (<50%)'
    END as health_range,
    COUNT(*) as database_count,
    AVG(health_score) as avg_score
FROM database_registry
GROUP BY health_range
ORDER BY avg_score DESC;

-- CHART DATA: Category Distribution  
CREATE OR REPLACE VIEW chart_category_distribution AS
SELECT 
    category,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage
FROM database_registry
GROUP BY category
ORDER BY count DESC;

-- CHART DATA: Size Distribution
CREATE OR REPLACE VIEW chart_size_distribution AS
SELECT 
    CASE
        WHEN size_bytes < 1024*1024 THEN 'Small (<1MB)'
        WHEN size_bytes < 5*1024*1024 THEN 'Medium (1-5MB)'
        WHEN size_bytes < 10*1024*1024 THEN 'Large (5-10MB)'
        ELSE 'Very Large (>10MB)'
    END as size_range,
    COUNT(*) as database_count,
    SUM(size_bytes) / (1024 * 1024) as total_size_mb
FROM database_registry
GROUP BY size_range
ORDER BY total_size_mb DESC;

-- CHART DATA: Sync Activity Timeline (Last 7 Days)
CREATE OR REPLACE VIEW chart_sync_timeline AS
SELECT 
    DATE_TRUNC('day', sync_timestamp) as sync_date,
    COUNT(*) as sync_count,
    COUNT(DISTINCT database_name) as databases_synced,
    AVG(sync_duration_ms) as avg_duration,
    SUM(rows_synced) as total_rows_synced
FROM database_sync_log
WHERE sync_timestamp > NOW() - INTERVAL '7 days'
GROUP BY sync_date
ORDER BY sync_date DESC;

-- =================================================================
-- COMMENTS FOR DOCUMENTATION
-- =================================================================
COMMENT ON VIEW database_health_overview IS 'Complete database health dashboard with categorized metrics';
COMMENT ON VIEW service_lifecycle_stats IS 'ZmartBot 3-database service lifecycle progression tracking';
COMMENT ON VIEW sync_performance_timeline IS 'Historical sync performance metrics for trend analysis';
COMMENT ON VIEW category_analysis IS 'Detailed breakdown of databases by category with percentage analysis';
COMMENT ON VIEW health_trend_analysis IS 'Historical health score changes and trends over time';
COMMENT ON VIEW top_performers IS 'Ranking of best performing databases by multiple criteria';
COMMENT ON VIEW sync_status_dashboard IS 'Real-time sync status monitoring with freshness indicators';
COMMENT ON VIEW data_volume_analysis IS 'Data distribution and growth analysis with efficiency metrics';
COMMENT ON VIEW chart_health_distribution IS 'Chart-ready data for health score distribution visualization';
COMMENT ON VIEW chart_category_distribution IS 'Chart-ready data for category distribution pie charts';
COMMENT ON VIEW chart_size_distribution IS 'Chart-ready data for size distribution visualization';
COMMENT ON VIEW chart_sync_timeline IS 'Chart-ready data for sync activity timeline charts';