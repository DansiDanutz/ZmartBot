-- ============================================
-- SIMPLE CLEANUP SCRIPT FOR SUPABASE
-- Drops all conflicting functions manually
-- ============================================

-- STEP 1: Drop all RiskMetric related functions explicitly
-- ============================================

-- Drop main functions (try all possible signatures)
DROP FUNCTION IF EXISTS daily_risk_update_master() CASCADE;
DROP FUNCTION IF EXISTS update_daily_risk_bands() CASCADE;
DROP FUNCTION IF EXISTS get_risk_at_price(varchar, numeric, varchar) CASCADE;
DROP FUNCTION IF EXISTS get_risk_at_price(varchar, numeric) CASCADE;
DROP FUNCTION IF EXISTS get_price_at_risk(varchar, numeric, varchar) CASCADE;
DROP FUNCTION IF EXISTS get_price_at_risk(varchar, numeric) CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced(varchar, numeric) CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced(varchar) CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced_detailed(varchar, numeric) CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced_detailed(varchar) CASCADE;
DROP FUNCTION IF EXISTS calculate_time_adjustment(numeric, varchar) CASCADE;
DROP FUNCTION IF EXISTS calculate_time_adjustment(numeric) CASCADE;
DROP FUNCTION IF EXISTS get_band_name(numeric) CASCADE;
DROP FUNCTION IF EXISTS get_signal_type(numeric) CASCADE;
DROP FUNCTION IF EXISTS calculate_signal_score(numeric, numeric) CASCADE;
DROP FUNCTION IF EXISTS get_market_phase(numeric) CASCADE;
DROP FUNCTION IF EXISTS update_riskmetric_daily() CASCADE;
DROP FUNCTION IF EXISTS linear_interpolation(numeric, numeric, numeric, numeric, numeric) CASCADE;
DROP FUNCTION IF EXISTS interpolate_risk(varchar, numeric, varchar) CASCADE;
DROP FUNCTION IF EXISTS interpolate_price(varchar, numeric, varchar) CASCADE;

-- Drop any trigger functions
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS trigger_update_timestamp() CASCADE;
DROP FUNCTION IF EXISTS update_modified_column() CASCADE;

-- Drop scoring functions
DROP FUNCTION IF EXISTS calculate_riskmetric_score(numeric, numeric) CASCADE;
DROP FUNCTION IF EXISTS get_risk_band_score(numeric) CASCADE;
DROP FUNCTION IF EXISTS calculate_final_score(numeric, numeric) CASCADE;

-- Drop band functions
DROP FUNCTION IF EXISTS get_time_band(numeric) CASCADE;
DROP FUNCTION IF EXISTS get_band_days(numeric) CASCADE;
DROP FUNCTION IF EXISTS get_band_coefficient(numeric) CASCADE;

-- Drop validation functions
DROP FUNCTION IF EXISTS validate_risk_value(numeric) CASCADE;
DROP FUNCTION IF EXISTS validate_symbol(varchar) CASCADE;
DROP FUNCTION IF EXISTS check_data_availability(varchar) CASCADE;

-- STEP 2: Drop all views that might depend on these functions
-- ============================================

DROP VIEW IF EXISTS riskmetric_current_status CASCADE;
DROP VIEW IF EXISTS riskmetric_signal_summary CASCADE;
DROP VIEW IF EXISTS active_risk_analysis CASCADE;
DROP VIEW IF EXISTS symbol_risk_overview CASCADE;
DROP VIEW IF EXISTS risk_band_distribution CASCADE;
DROP VIEW IF EXISTS daily_risk_summary CASCADE;
DROP VIEW IF EXISTS market_phase_overview CASCADE;

-- Drop materialized views if any
DROP MATERIALIZED VIEW IF EXISTS mv_risk_calculations CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_daily_risk_summary CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_symbol_risk_cache CASCADE;

-- STEP 3: Drop triggers on risk-related tables
-- ============================================

-- Drop triggers on cryptoverse tables
DROP TRIGGER IF EXISTS update_risk_data_trigger ON cryptoverse_risk_data CASCADE;
DROP TRIGGER IF EXISTS update_risk_grid_trigger ON cryptoverse_risk_grid CASCADE;
DROP TRIGGER IF EXISTS update_btc_grid_trigger ON cryptoverse_btc_risk_grid CASCADE;
DROP TRIGGER IF EXISTS update_time_bands_trigger ON cryptoverse_risk_time_bands CASCADE;
DROP TRIGGER IF EXISTS update_time_bands_v2_trigger ON cryptoverse_risk_time_bands_v2 CASCADE;

-- Drop triggers on riskmetric tables
DROP TRIGGER IF EXISTS update_daily_updates_trigger ON riskmetric_daily_updates CASCADE;
DROP TRIGGER IF EXISTS update_scoring_history_trigger ON riskmetric_scoring_history CASCADE;

-- STEP 4: Check what remains
-- ============================================

-- List remaining functions with 'risk' or related keywords
SELECT
    'Remaining Functions' as check_type,
    proname as function_name,
    pronargs as arg_count
FROM pg_proc
JOIN pg_namespace ON pg_proc.pronamespace = pg_namespace.oid
WHERE nspname = 'public'
AND (
    proname LIKE '%risk%' OR
    proname LIKE '%band%' OR
    proname LIKE '%signal%' OR
    proname LIKE '%daily%' OR
    proname LIKE '%interpolat%'
)
ORDER BY proname;

-- Check tables (should still exist)
SELECT
    'Preserved Tables' as check_type,
    COUNT(*) as count,
    string_agg(table_name, ', ') as tables
FROM information_schema.tables
WHERE table_schema = 'public'
AND (
    table_name LIKE 'cryptoverse_%' OR
    table_name LIKE 'riskmetric_%'
);

-- STEP 5: Final Status
-- ============================================

SELECT
    '✅ CLEANUP COMPLETE' as status,
    'Functions and views removed' as action,
    'Tables preserved with data' as data_status,
    'Ready for COMPLETE_RISKMETRIC_SYSTEM.sql' as next_step;

-- ============================================
-- NOTE: If you still get errors, run this query to find
-- the exact function signatures that need dropping:
-- ============================================

/*
SELECT
    proname || '(' ||
    COALESCE(string_agg(
        CASE
            WHEN t.typname = 'varchar' THEN 'character varying'
            ELSE t.typname
        END, ', ' ORDER BY a.idx), '') || ')' as drop_command
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
LEFT JOIN LATERAL unnest(p.proargtypes) WITH ORDINALITY as a(oid, idx) ON true
LEFT JOIN pg_type t ON a.oid = t.oid
WHERE n.nspname = 'public'
AND p.proname IN (
    'daily_risk_update_master',
    'update_daily_risk_bands',
    'get_risk_at_price',
    'get_price_at_risk',
    'riskmetric_agent_enhanced',
    'riskmetric_agent_enhanced_detailed'
)
GROUP BY p.proname, p.oid;
*/