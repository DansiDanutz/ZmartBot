-- ============================================
-- SUPABASE PRE-MIGRATION SAFETY CHECK
-- Run this BEFORE applying any migrations
-- ============================================

-- This script will help you verify what already exists in your database
-- and identify any potential conflicts before running migrations

-- ============================================
-- SECTION 1: CHECK EXISTING TABLES
-- ============================================

\echo '=========================================='
\echo '1. CHECKING EXISTING TABLES'
\echo '=========================================='

-- Check for Alert System tables
SELECT
    'Alert System' as module,
    COUNT(*) as existing_tables,
    string_agg(table_name, ', ') as table_names
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'alert_collections',
    'alert_reports',
    'symbol_coverage',
    'manus_extraordinary_reports',
    'mdc_documentation',
    'alert_agent_statistics',
    'prompt_templates',
    'alert_fusion_data'
);

-- Check for RiskMetric System tables
SELECT
    'RiskMetric System' as module,
    COUNT(*) as existing_tables,
    string_agg(table_name, ', ') as table_names
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'cryptoverse_risk_grid',
    'cryptoverse_btc_risk_grid',
    'cryptoverse_risk_data',
    'cryptoverse_risk_time_bands',
    'cryptoverse_risk_time_bands_v2',
    'riskmetric_daily_updates',
    'riskmetric_scoring_history'
);

-- Check for Cryptometer tables
SELECT
    'Cryptometer' as module,
    COUNT(*) as existing_tables,
    string_agg(table_name, ', ') as table_names
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'cryptometer_symbol_analysis',
    'cryptometer_win_rates',
    'cryptometer_technical_indicators',
    'cryptometer_market_data',
    'cryptometer_ai_predictions',
    'cryptometer_performance_tracking'
);

-- Check for Trading Intelligence tables
SELECT
    'Trading Intelligence' as module,
    COUNT(*) as existing_tables,
    string_agg(table_name, ', ') as table_names
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'trading_analyses',
    'pattern_library',
    'smart_alerts',
    'trading_signals',
    'market_regimes',
    'performance_metrics'
);

-- ============================================
-- SECTION 2: CHECK EXISTING FUNCTIONS
-- ============================================

\echo ''
\echo '=========================================='
\echo '2. CHECKING EXISTING FUNCTIONS'
\echo '=========================================='

SELECT
    routine_name,
    routine_type,
    CASE
        WHEN routine_name IN ('get_risk_at_price', 'get_price_at_risk') THEN 'Critical - Interpolation'
        WHEN routine_name LIKE 'riskmetric%' THEN 'Critical - Risk Calculation'
        WHEN routine_name = 'update_updated_at_column' THEN 'Trigger Function'
        ELSE 'Other'
    END as importance
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_type IN ('FUNCTION', 'PROCEDURE')
ORDER BY importance, routine_name;

-- ============================================
-- SECTION 3: CHECK EXISTING VIEWS
-- ============================================

\echo ''
\echo '=========================================='
\echo '3. CHECKING EXISTING VIEWS'
\echo '=========================================='

SELECT
    viewname,
    CASE
        WHEN viewname LIKE 'active_alerts%' THEN 'Alert System'
        WHEN viewname LIKE 'symbol_coverage%' THEN 'Symbol Coverage'
        WHEN viewname LIKE 'manus%' THEN 'Manus Reports'
        WHEN viewname LIKE 'agent_performance%' THEN 'Performance'
        ELSE 'Other'
    END as module
FROM pg_views
WHERE schemaname = 'public'
AND viewname IN (
    'active_alerts_summary',
    'symbol_coverage_status',
    'manus_reports_summary',
    'agent_performance_metrics'
)
ORDER BY module;

-- ============================================
-- SECTION 4: CHECK DATA IN CRITICAL TABLES
-- ============================================

\echo ''
\echo '=========================================='
\echo '4. CHECKING DATA IN CRITICAL TABLES'
\echo '=========================================='

-- Check if risk grids have data
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_name = 'cryptoverse_risk_grid') THEN
        RAISE NOTICE 'Risk Grid (Fiat): % rows',
            (SELECT COUNT(*) FROM cryptoverse_risk_grid);
    ELSE
        RAISE NOTICE 'Risk Grid (Fiat): Table does not exist';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_name = 'cryptoverse_btc_risk_grid') THEN
        RAISE NOTICE 'Risk Grid (BTC): % rows',
            (SELECT COUNT(*) FROM cryptoverse_btc_risk_grid);
    ELSE
        RAISE NOTICE 'Risk Grid (BTC): Table does not exist';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_name = 'prompt_templates') THEN
        RAISE NOTICE 'Prompt Templates: % rows',
            (SELECT COUNT(*) FROM prompt_templates);
    ELSE
        RAISE NOTICE 'Prompt Templates: Table does not exist';
    END IF;
END $$;

-- ============================================
-- SECTION 5: CHECK FOR POTENTIAL CONFLICTS
-- ============================================

\echo ''
\echo '=========================================='
\echo '5. CHECKING FOR POTENTIAL CONFLICTS'
\echo '=========================================='

-- Check for tables that might conflict
WITH potential_conflicts AS (
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND (
        table_name LIKE 'alert_%' OR
        table_name LIKE 'cryptoverse_%' OR
        table_name LIKE 'cryptometer_%' OR
        table_name LIKE 'trading_%' OR
        table_name LIKE 'pattern_%' OR
        table_name LIKE 'smart_%' OR
        table_name LIKE 'manus_%' OR
        table_name LIKE 'mdc_%' OR
        table_name LIKE 'symbol_%' OR
        table_name LIKE 'prompt_%'
    )
)
SELECT
    CASE
        WHEN COUNT(*) = 0 THEN '✅ No potential conflicts found'
        ELSE '⚠️ Found ' || COUNT(*) || ' tables that might conflict'
    END as status,
    COUNT(*) as table_count,
    CASE
        WHEN COUNT(*) > 0 THEN string_agg(table_name, ', ' ORDER BY table_name)
        ELSE 'None'
    END as existing_tables
FROM potential_conflicts;

-- ============================================
-- SECTION 6: CHECK ROW LEVEL SECURITY
-- ============================================

\echo ''
\echo '=========================================='
\echo '6. CHECKING ROW LEVEL SECURITY STATUS'
\echo '=========================================='

SELECT
    tablename,
    rowsecurity,
    CASE
        WHEN rowsecurity THEN '✅ Enabled'
        ELSE '❌ Disabled'
    END as rls_status
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN (
    'alert_collections',
    'alert_reports',
    'symbol_coverage',
    'cryptoverse_risk_grid',
    'cryptometer_symbol_analysis',
    'trading_analyses'
)
ORDER BY tablename;

-- ============================================
-- SECTION 7: SAFETY RECOMMENDATIONS
-- ============================================

\echo ''
\echo '=========================================='
\echo '7. SAFETY RECOMMENDATIONS'
\echo '=========================================='

SELECT
    CASE
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'cryptoverse_risk_grid'
        ) THEN '⚠️ RiskMetric tables exist - Review before running COMPLETE_RISKMETRIC_SYSTEM.sql'
        ELSE '✅ Safe to run COMPLETE_RISKMETRIC_SYSTEM.sql'
    END as riskmetric_status
UNION ALL
SELECT
    CASE
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'alert_collections'
        ) THEN '⚠️ Alert tables exist - Review before running alert_agent_supabase_schema.sql'
        ELSE '✅ Safe to run alert_agent_supabase_schema.sql'
    END
UNION ALL
SELECT
    CASE
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'cryptometer_symbol_analysis'
        ) THEN '⚠️ Cryptometer tables exist - Review before running cryptometer_tables_migration.sql'
        ELSE '✅ Safe to run cryptometer_tables_migration.sql'
    END
UNION ALL
SELECT
    CASE
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'trading_analyses'
        ) THEN '⚠️ Trading tables exist - Review before running trading_intelligence_tables.sql'
        ELSE '✅ Safe to run trading_intelligence_tables.sql'
    END;

-- ============================================
-- SECTION 8: BACKUP REMINDER
-- ============================================

\echo ''
\echo '=========================================='
\echo '8. BACKUP REMINDER'
\echo '=========================================='
\echo ''
\echo 'Before proceeding with migrations:'
\echo '1. Go to Supabase Dashboard > Settings > Database > Backups'
\echo '2. Create a manual backup if needed'
\echo '3. Note your current backup restore point'
\echo ''
\echo 'Migration Order (MUST follow):'
\echo '1. COMPLETE_RISKMETRIC_SYSTEM.sql'
\echo '2. database/trading_intelligence_tables.sql'
\echo '3. database/migrations/alert_agent_supabase_schema.sql'
\echo '4. database/migrations/cryptometer_tables_migration.sql'
\echo '5. All *_risk_data.sql files'
\echo ''
\echo '=========================================='

-- ============================================
-- SECTION 9: QUICK DECISION MATRIX
-- ============================================

WITH decision_matrix AS (
    SELECT
        -- Check if any critical tables exist
        EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN (
                'cryptoverse_risk_grid',
                'alert_collections',
                'cryptometer_symbol_analysis',
                'trading_analyses'
            )
        ) as has_existing_tables,

        -- Check if critical functions exist
        EXISTS (
            SELECT 1 FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND routine_name IN ('get_risk_at_price', 'riskmetric_agent_enhanced')
        ) as has_critical_functions
)
SELECT
    CASE
        WHEN NOT has_existing_tables AND NOT has_critical_functions THEN
            '🟢 SAFE TO PROCEED - Database appears empty, run all migrations'
        WHEN has_existing_tables AND has_critical_functions THEN
            '🟡 CAUTION - System partially installed, review existing tables before proceeding'
        WHEN has_existing_tables AND NOT has_critical_functions THEN
            '🟡 PARTIAL INSTALLATION - Tables exist but functions missing, safe to add functions'
        ELSE
            '🔍 REVIEW NEEDED - Unusual state, manual review recommended'
    END as recommendation,
    CASE
        WHEN has_existing_tables THEN 'Yes' ELSE 'No'
    END as "Tables Exist?",
    CASE
        WHEN has_critical_functions THEN 'Yes' ELSE 'No'
    END as "Functions Exist?"
FROM decision_matrix;

-- ============================================
-- END OF PRE-MIGRATION CHECK
-- ============================================