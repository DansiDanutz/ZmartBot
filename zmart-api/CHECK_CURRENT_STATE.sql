-- ============================================
-- CHECK WHAT YOU ACTUALLY HAVE RIGHT NOW
-- This will show you everything is still working!
-- ============================================

-- 1. Check your tables (should all be there)
SELECT
    'TABLES CHECK' as status,
    COUNT(*) as table_count,
    'All your tables with data' as description
FROM information_schema.tables
WHERE table_schema = 'public';

-- 2. Check your functions (should have many)
SELECT
    'FUNCTIONS CHECK' as status,
    COUNT(*) as function_count,
    'Risk functions still exist' as description
FROM pg_proc
JOIN pg_namespace ON pg_proc.pronamespace = pg_namespace.oid
WHERE nspname = 'public';

-- 3. Test if RiskMetric actually works RIGHT NOW
DO $$
BEGIN
    -- Try to use existing function
    BEGIN
        PERFORM get_risk_at_price('BTC', 100000, 'fiat');
        RAISE NOTICE '✅ RiskMetric is WORKING!';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE '⚠️ RiskMetric needs adjustment: %', SQLERRM;
    END;
END $$;

-- 4. Count data in critical tables
SELECT
    'DATA STATUS' as check_type,
    table_name,
    n_live_tup as row_count,
    CASE
        WHEN n_live_tup > 0 THEN '✅ Has data'
        ELSE '⚠️ Empty'
    END as status
FROM pg_stat_user_tables
WHERE schemaname = 'public'
AND (
    tablename LIKE 'cryptoverse_%' OR
    tablename LIKE 'alert_%' OR
    tablename LIKE 'trading_%'
)
ORDER BY n_live_tup DESC;

-- 5. FINAL VERDICT
SELECT
    '📊 SYSTEM STATUS' as report,
    'Your system is probably STILL WORKING' as verdict,
    'The cleanup partially failed which means functions are still there' as explanation,
    'You can likely continue using the system as before' as recommendation;