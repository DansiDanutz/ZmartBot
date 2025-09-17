-- ============================================
-- SUPABASE PRE-MIGRATION SAFETY CHECK (SIMPLIFIED)
-- Compatible with Supabase SQL Editor
-- ============================================

-- ============================================
-- 1. CHECK WHAT TABLES ALREADY EXIST
-- ============================================

SELECT
    'EXISTING TABLES CHECK' as check_type,
    COUNT(*) as total_tables_found,
    string_agg(table_name, ', ') as existing_tables
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
);

-- ============================================
-- 2. CHECK TABLES BY MODULE
-- ============================================

-- Alert System Tables
SELECT
    'Alert System' as module,
    COUNT(*) as tables_found,
    COUNT(*) FILTER (WHERE table_name IN (
        'alert_collections', 'alert_reports', 'symbol_coverage',
        'manus_extraordinary_reports', 'mdc_documentation',
        'alert_agent_statistics', 'prompt_templates', 'alert_fusion_data'
    )) as expected_tables,
    string_agg(table_name, ', ') as table_list
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'alert_%' OR table_name = 'symbol_coverage'
    OR table_name = 'manus_extraordinary_reports' OR table_name = 'mdc_documentation'
    OR table_name = 'prompt_templates';

-- RiskMetric System Tables
SELECT
    'RiskMetric System' as module,
    COUNT(*) as tables_found,
    string_agg(table_name, ', ') as table_list
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'cryptoverse_%' OR table_name LIKE 'riskmetric_%';

-- Cryptometer Tables
SELECT
    'Cryptometer' as module,
    COUNT(*) as tables_found,
    string_agg(table_name, ', ') as table_list
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'cryptometer_%';

-- Trading Intelligence Tables
SELECT
    'Trading Intelligence' as module,
    COUNT(*) as tables_found,
    string_agg(table_name, ', ') as table_list
FROM information_schema.tables
WHERE table_schema = 'public'
AND (table_name LIKE 'trading_%' OR table_name LIKE 'pattern_%' OR table_name LIKE 'smart_%');

-- ============================================
-- 3. CHECK EXISTING FUNCTIONS
-- ============================================

SELECT
    'FUNCTIONS CHECK' as check_type,
    routine_name,
    routine_type,
    CASE
        WHEN routine_name IN ('get_risk_at_price', 'get_price_at_risk') THEN '⚠️ Critical Interpolation'
        WHEN routine_name LIKE 'riskmetric%' THEN '⚠️ Risk Calculation'
        WHEN routine_name = 'update_updated_at_column' THEN 'Trigger Function'
        ELSE 'Other'
    END as importance
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_type = 'FUNCTION'
ORDER BY importance, routine_name;

-- ============================================
-- 4. CHECK EXISTING VIEWS
-- ============================================

SELECT
    'VIEWS CHECK' as check_type,
    viewname,
    CASE
        WHEN viewname LIKE '%alert%' THEN 'Alert System'
        WHEN viewname LIKE '%coverage%' THEN 'Coverage'
        WHEN viewname LIKE '%manus%' THEN 'Manus'
        WHEN viewname LIKE '%performance%' THEN 'Performance'
        ELSE 'Other'
    END as module
FROM pg_views
WHERE schemaname = 'public'
ORDER BY module, viewname;

-- ============================================
-- 5. CRITICAL DATA CHECK
-- ============================================

-- Check Risk Grid Data (if tables exist)
SELECT
    'Risk Grid Fiat' as table_name,
    COALESCE((SELECT COUNT(*) FROM cryptoverse_risk_grid), 0) as row_count,
    CASE
        WHEN COALESCE((SELECT COUNT(*) FROM cryptoverse_risk_grid), 0) >= 1025 THEN '✅ Complete'
        WHEN COALESCE((SELECT COUNT(*) FROM cryptoverse_risk_grid), 0) > 0 THEN '⚠️ Partial Data'
        ELSE '❌ Empty or Missing'
    END as status
UNION ALL
SELECT
    'Risk Grid BTC' as table_name,
    COALESCE((SELECT COUNT(*) FROM cryptoverse_btc_risk_grid), 0) as row_count,
    CASE
        WHEN COALESCE((SELECT COUNT(*) FROM cryptoverse_btc_risk_grid), 0) >= 410 THEN '✅ Complete'
        WHEN COALESCE((SELECT COUNT(*) FROM cryptoverse_btc_risk_grid), 0) > 0 THEN '⚠️ Partial Data'
        ELSE '❌ Empty or Missing'
    END as status
UNION ALL
SELECT
    'Prompt Templates' as table_name,
    COALESCE((SELECT COUNT(*) FROM prompt_templates), 0) as row_count,
    CASE
        WHEN COALESCE((SELECT COUNT(*) FROM prompt_templates), 0) >= 4 THEN '✅ Has Templates'
        WHEN COALESCE((SELECT COUNT(*) FROM prompt_templates), 0) > 0 THEN '⚠️ Some Templates'
        ELSE '❌ Empty or Missing'
    END as status;

-- ============================================
-- 6. SAFETY RECOMMENDATIONS
-- ============================================

WITH existing_check AS (
    SELECT
        EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'cryptoverse_risk_grid') as has_risk,
        EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'alert_collections') as has_alerts,
        EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'cryptometer_symbol_analysis') as has_crypto,
        EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'trading_analyses') as has_trading
)
SELECT
    'MIGRATION SAFETY' as check_type,
    CASE
        WHEN NOT has_risk AND NOT has_alerts AND NOT has_crypto AND NOT has_trading THEN
            '🟢 SAFE - Database empty, run all migrations in order'
        WHEN has_risk OR has_alerts OR has_crypto OR has_trading THEN
            '🟡 CAUTION - Some tables exist, review before proceeding'
        ELSE '🔍 REVIEW - Check individual modules'
    END as overall_status,
    CASE WHEN NOT has_risk THEN '✅' ELSE '⚠️' END || ' RiskMetric: ' ||
        CASE WHEN NOT has_risk THEN 'Safe to run' ELSE 'Tables exist' END as riskmetric,
    CASE WHEN NOT has_trading THEN '✅' ELSE '⚠️' END || ' Trading: ' ||
        CASE WHEN NOT has_trading THEN 'Safe to run' ELSE 'Tables exist' END as trading,
    CASE WHEN NOT has_alerts THEN '✅' ELSE '⚠️' END || ' Alerts: ' ||
        CASE WHEN NOT has_alerts THEN 'Safe to run' ELSE 'Tables exist' END as alerts,
    CASE WHEN NOT has_crypto THEN '✅' ELSE '⚠️' END || ' Cryptometer: ' ||
        CASE WHEN NOT has_crypto THEN 'Safe to run' ELSE 'Tables exist' END as cryptometer
FROM existing_check;

-- ============================================
-- 7. ROW LEVEL SECURITY CHECK
-- ============================================

SELECT
    'RLS CHECK' as check_type,
    tablename,
    CASE WHEN rowsecurity THEN '✅ Enabled' ELSE '❌ Disabled' END as rls_status
FROM pg_tables
WHERE schemaname = 'public'
AND (
    tablename LIKE 'alert_%' OR
    tablename LIKE 'cryptoverse_%' OR
    tablename LIKE 'cryptometer_%' OR
    tablename LIKE 'trading_%'
)
ORDER BY tablename;

-- ============================================
-- FINAL SUMMARY
-- ============================================

SELECT
    '📋 SUMMARY' as report,
    'Check complete! Review results above.' as message,
    'Migration Order: 1) RiskMetric, 2) Trading, 3) Alerts, 4) Cryptometer, 5) Risk Data' as required_order;