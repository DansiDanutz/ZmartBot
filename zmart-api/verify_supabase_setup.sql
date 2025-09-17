-- VERIFICATION SCRIPT FOR SUPABASE RISK GRID SETUP
-- Run this to check if everything was created successfully
-- Date: 2025-09-16

-- ============================================
-- 1. CHECK TABLES EXIST
-- ============================================
SELECT
    '📋 TABLE CHECK' as check_type,
    table_name,
    CASE
        WHEN table_name = 'cryptoverse_risk_grid' THEN '✅ FIAT Risk Grid Table'
        WHEN table_name = 'cryptoverse_btc_risk_grid' THEN '✅ BTC Risk Grid Table'
        WHEN table_name = 'cryptoverse_risk_data' THEN '✅ Current Risk Data Table'
        ELSE '❓ Unknown Table'
    END as description
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('cryptoverse_risk_grid', 'cryptoverse_btc_risk_grid', 'cryptoverse_risk_data')
ORDER BY table_name;

-- ============================================
-- 2. CHECK COLUMNS IN EACH TABLE
-- ============================================
SELECT
    '📊 FIAT RISK GRID COLUMNS' as check_type,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'cryptoverse_risk_grid'
AND table_schema = 'public'
ORDER BY ordinal_position;

SELECT
    '📊 BTC RISK GRID COLUMNS' as check_type,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'cryptoverse_btc_risk_grid'
AND table_schema = 'public'
ORDER BY ordinal_position;

-- ============================================
-- 3. CHECK INDEXES EXIST
-- ============================================
SELECT
    '🔍 INDEXES' as check_type,
    indexname,
    tablename,
    CASE
        WHEN indexname LIKE '%symbol%' THEN '✅ Symbol Index'
        WHEN indexname LIKE '%risk%' THEN '✅ Risk Index'
        WHEN indexname LIKE '%pkey%' THEN '✅ Primary Key'
        ELSE '✅ Other Index'
    END as index_type
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN ('cryptoverse_risk_grid', 'cryptoverse_btc_risk_grid', 'cryptoverse_risk_data')
ORDER BY tablename, indexname;

-- ============================================
-- 4. CHECK FUNCTIONS EXIST
-- ============================================
SELECT
    '⚙️ FUNCTIONS' as check_type,
    routine_name as function_name,
    CASE
        WHEN routine_name = 'get_price_at_risk' THEN '✅ Get price at specific risk level'
        WHEN routine_name = 'get_risk_at_price' THEN '✅ Get risk at specific price'
        WHEN routine_name = 'get_risk_profile' THEN '✅ Get complete risk profile'
        ELSE '✅ Function exists'
    END as description
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN ('get_price_at_risk', 'get_risk_at_price', 'get_risk_profile')
ORDER BY routine_name;

-- ============================================
-- 5. CHECK VIEWS EXIST
-- ============================================
SELECT
    '👁️ VIEWS' as check_type,
    table_name as view_name,
    CASE
        WHEN table_name = 'v_risk_status' THEN '✅ Current risk with zones'
        WHEN table_name = 'v_dual_risk_symbols' THEN '✅ Symbols with both risk types'
        WHEN table_name = 'v_risk_grid_summary' THEN '✅ Summary of all risk data'
        ELSE '✅ View exists'
    END as description
FROM information_schema.views
WHERE table_schema = 'public'
AND table_name IN ('v_risk_status', 'v_dual_risk_symbols', 'v_risk_grid_summary')
ORDER BY table_name;

-- ============================================
-- 6. CHECK ROW LEVEL SECURITY
-- ============================================
SELECT
    '🔒 SECURITY' as check_type,
    tablename,
    CASE
        WHEN rowsecurity = true THEN '✅ RLS Enabled'
        ELSE '⚠️ RLS Disabled'
    END as rls_status
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('cryptoverse_risk_grid', 'cryptoverse_btc_risk_grid', 'cryptoverse_risk_data')
ORDER BY tablename;

-- ============================================
-- 7. CHECK DATA STATUS
-- ============================================
SELECT
    '📈 DATA STATUS' as check_type,
    'cryptoverse_risk_grid' as table_name,
    COUNT(DISTINCT symbol) as symbols,
    COUNT(*) as total_rows,
    CASE
        WHEN COUNT(*) = 0 THEN '⚠️ Empty - Need to load data'
        WHEN COUNT(*) = 1025 THEN '✅ Complete (25 symbols × 41 points)'
        ELSE '⚠️ Partial data loaded'
    END as status
FROM cryptoverse_risk_grid
UNION ALL
SELECT
    '📈 DATA STATUS' as check_type,
    'cryptoverse_btc_risk_grid' as table_name,
    COUNT(DISTINCT symbol) as symbols,
    COUNT(*) as total_rows,
    CASE
        WHEN COUNT(*) = 0 THEN '⚠️ Empty - Need to load data'
        WHEN COUNT(*) = 410 THEN '✅ Complete (10 symbols × 41 points)'
        ELSE '⚠️ Partial data loaded'
    END as status
FROM cryptoverse_btc_risk_grid
UNION ALL
SELECT
    '📈 DATA STATUS' as check_type,
    'cryptoverse_risk_data' as table_name,
    COUNT(DISTINCT symbol) as symbols,
    COUNT(*) as total_rows,
    CASE
        WHEN COUNT(*) = 0 THEN '⚠️ Empty - Need to load current risk data'
        WHEN COUNT(*) >= 25 THEN '✅ All symbols have current risk'
        ELSE '⚠️ Some symbols missing current risk'
    END as status
FROM cryptoverse_risk_data;

-- ============================================
-- 8. FINAL SUMMARY
-- ============================================
SELECT
    '✅ SETUP VERIFICATION COMPLETE' as message,
    'Check results above. All items should show ✅' as instruction
UNION ALL
SELECT
    '📝 NEXT STEPS' as message,
    'If tables are empty, run: insert_full_risk_grids.sql and insert_btc_risk_grids.sql' as instruction;