-- ============================================
-- COMPLETE CLEANUP SCRIPT FOR RISKMETRIC
-- Run this BEFORE any migrations to clean conflicts
-- ============================================

-- STEP 1: Drop all dependent objects first
-- ============================================

-- Drop any views that depend on functions
DROP VIEW IF EXISTS riskmetric_current_status CASCADE;
DROP VIEW IF EXISTS riskmetric_signal_summary CASCADE;
DROP VIEW IF EXISTS active_risk_analysis CASCADE;
DROP VIEW IF EXISTS symbol_risk_overview CASCADE;

-- Drop any materialized views
DROP MATERIALIZED VIEW IF EXISTS mv_risk_calculations CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_daily_risk_summary CASCADE;

-- STEP 2: Drop all RiskMetric functions
-- ============================================

-- Drop main risk functions
DROP FUNCTION IF EXISTS get_risk_at_price CASCADE;
DROP FUNCTION IF EXISTS get_price_at_risk CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced_detailed CASCADE;

-- Drop utility functions
DROP FUNCTION IF EXISTS calculate_time_adjustment CASCADE;
DROP FUNCTION IF EXISTS get_band_name CASCADE;
DROP FUNCTION IF EXISTS get_signal_type CASCADE;
DROP FUNCTION IF EXISTS calculate_signal_score CASCADE;
DROP FUNCTION IF EXISTS get_market_phase CASCADE;

-- Drop update/maintenance functions
DROP FUNCTION IF EXISTS update_riskmetric_daily CASCADE;
DROP FUNCTION IF EXISTS update_daily_risk_bands CASCADE;
DROP FUNCTION IF EXISTS refresh_risk_calculations CASCADE;
DROP FUNCTION IF EXISTS calculate_risk_metrics CASCADE;

-- Drop any overloaded versions (different parameter counts)
DROP FUNCTION IF EXISTS get_risk_at_price(varchar, numeric) CASCADE;
DROP FUNCTION IF EXISTS get_risk_at_price(varchar, numeric, varchar) CASCADE;
DROP FUNCTION IF EXISTS get_price_at_risk(varchar, numeric) CASCADE;
DROP FUNCTION IF EXISTS get_price_at_risk(varchar, numeric, varchar) CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced(varchar) CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced(varchar, numeric) CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced_detailed(varchar) CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced_detailed(varchar, numeric) CASCADE;

-- Drop interpolation functions
DROP FUNCTION IF EXISTS linear_interpolation CASCADE;
DROP FUNCTION IF EXISTS interpolate_risk CASCADE;
DROP FUNCTION IF EXISTS interpolate_price CASCADE;

-- STEP 3: Drop triggers if they exist
-- ============================================

DROP TRIGGER IF EXISTS update_risk_data_trigger ON cryptoverse_risk_data;
DROP TRIGGER IF EXISTS update_risk_grid_trigger ON cryptoverse_risk_grid;
DROP TRIGGER IF EXISTS update_btc_grid_trigger ON cryptoverse_btc_risk_grid;

-- STEP 4: Check what's left
-- ============================================

-- Check remaining functions
SELECT
    '📋 Remaining Functions' as check_type,
    COUNT(*) as count,
    string_agg(routine_name, ', ') as function_list
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name LIKE '%risk%'
   OR routine_name LIKE '%band%'
   OR routine_name LIKE '%signal%';

-- Check remaining tables (DO NOT DROP - just list)
SELECT
    '📋 Existing RiskMetric Tables' as check_type,
    COUNT(*) as count,
    string_agg(table_name, ', ') as table_list
FROM information_schema.tables
WHERE table_schema = 'public'
AND (table_name LIKE 'cryptoverse_%' OR table_name LIKE 'riskmetric_%');

-- STEP 5: Final Status
-- ============================================

SELECT
    '✅ CLEANUP COMPLETE' as status,
    'All conflicting functions removed. Safe to run COMPLETE_RISKMETRIC_SYSTEM.sql' as message,
    'Tables preserved - data is safe' as note;

-- ============================================
-- IMPORTANT NOTES:
-- 1. This script ONLY drops functions and views
-- 2. Your DATA in tables is PRESERVED
-- 3. After running this, run COMPLETE_RISKMETRIC_SYSTEM.sql
-- 4. The system will recreate all functions with correct signatures
-- ============================================