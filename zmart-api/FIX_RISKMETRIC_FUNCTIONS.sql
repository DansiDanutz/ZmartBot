-- ============================================
-- FIX FOR RISKMETRIC FUNCTION CONFLICTS
-- Run this BEFORE COMPLETE_RISKMETRIC_SYSTEM.sql
-- ============================================

-- Drop existing functions if they exist with different signatures
DROP FUNCTION IF EXISTS get_risk_at_price(character varying, numeric, character varying) CASCADE;
DROP FUNCTION IF EXISTS get_price_at_risk(character varying, numeric, character varying) CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced(character varying, numeric) CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced_detailed(character varying, numeric) CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced_detailed(character varying) CASCADE;
DROP FUNCTION IF EXISTS calculate_time_adjustment(numeric, character varying) CASCADE;
DROP FUNCTION IF EXISTS get_band_name(numeric) CASCADE;
DROP FUNCTION IF EXISTS get_signal_type(numeric) CASCADE;
DROP FUNCTION IF EXISTS calculate_signal_score(numeric, numeric) CASCADE;
DROP FUNCTION IF EXISTS get_market_phase(numeric) CASCADE;
DROP FUNCTION IF EXISTS update_riskmetric_daily() CASCADE;

-- Drop any dependent views that might exist
DROP VIEW IF EXISTS riskmetric_current_status CASCADE;
DROP VIEW IF EXISTS riskmetric_signal_summary CASCADE;

-- Now you can safely run COMPLETE_RISKMETRIC_SYSTEM.sql

-- ============================================
-- VERIFICATION
-- ============================================

-- Check that functions were dropped
SELECT
    'Functions after cleanup' as check_type,
    COUNT(*) as remaining_functions,
    string_agg(routine_name, ', ') as function_list
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN (
    'get_risk_at_price',
    'get_price_at_risk',
    'riskmetric_agent_enhanced',
    'riskmetric_agent_enhanced_detailed',
    'calculate_time_adjustment'
);

-- Message
SELECT
    '✅ READY' as status,
    'Old functions cleaned up. You can now run COMPLETE_RISKMETRIC_SYSTEM.sql' as message;