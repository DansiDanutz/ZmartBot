-- FINAL VERIFICATION - Run this after loading all data
-- =====================================================

-- 1. CHECK DATA COUNTS
SELECT
    '📊 DATA LOADED' as check_type,
    'FIAT Risk Grid' as data_type,
    COUNT(*) as total_rows,
    COUNT(DISTINCT symbol) as symbols,
    CASE
        WHEN COUNT(*) = 1025 THEN '✅ Complete (25 symbols × 41 points)'
        ELSE '⚠️ Incomplete - Expected 1025 rows'
    END as status
FROM cryptoverse_risk_grid
UNION ALL
SELECT
    '📊 DATA LOADED' as check_type,
    'BTC Risk Grid' as data_type,
    COUNT(*) as total_rows,
    COUNT(DISTINCT symbol) as symbols,
    CASE
        WHEN COUNT(*) = 410 THEN '✅ Complete (10 symbols × 41 points)'
        ELSE '⚠️ Incomplete - Expected 410 rows'
    END as status
FROM cryptoverse_btc_risk_grid;

-- 2. LIST ALL SYMBOLS WITH FIAT RISK
SELECT
    '💰 FIAT RISK SYMBOLS' as category,
    string_agg(DISTINCT symbol, ', ' ORDER BY symbol) as symbols
FROM cryptoverse_risk_grid;

-- 3. LIST ALL SYMBOLS WITH BTC RISK
SELECT
    '₿ BTC RISK SYMBOLS' as category,
    string_agg(DISTINCT symbol, ', ' ORDER BY symbol) as symbols
FROM cryptoverse_btc_risk_grid;

-- 4. TEST FUNCTIONS WITH REAL DATA
SELECT
    '🧪 FUNCTION TESTS' as test_type,
    'BTC at 50% FIAT risk' as test_name,
    get_price_at_risk('BTC', 0.5, 'fiat') as result
UNION ALL
SELECT
    '🧪 FUNCTION TESTS' as test_type,
    'ETH at 50% FIAT risk' as test_name,
    get_price_at_risk('ETH', 0.5, 'fiat') as result
UNION ALL
SELECT
    '🧪 FUNCTION TESTS' as test_type,
    'ETH at 50% BTC risk' as test_name,
    get_price_at_risk('ETH', 0.5, 'btc') as result
UNION ALL
SELECT
    '🧪 FUNCTION TESTS' as test_type,
    'SOL at 75% FIAT risk' as test_name,
    get_price_at_risk('SOL', 0.75, 'fiat') as result;

-- 5. SAMPLE RISK ZONES FOR KEY SYMBOLS
SELECT
    symbol,
    get_price_at_risk(symbol, 0.0, 'fiat') as "0% Risk (Bottom)",
    get_price_at_risk(symbol, 0.3, 'fiat') as "30% Risk (Accumulation End)",
    get_price_at_risk(symbol, 0.5, 'fiat') as "50% Risk (Mid)",
    get_price_at_risk(symbol, 0.7, 'fiat') as "70% Risk (Distribution Start)",
    get_price_at_risk(symbol, 1.0, 'fiat') as "100% Risk (Top)"
FROM (SELECT DISTINCT symbol FROM cryptoverse_risk_grid) s
WHERE symbol IN ('BTC', 'ETH', 'SOL', 'ADA', 'DOT')
ORDER BY symbol;

-- 6. VERIFY BTC RISK VALUES
SELECT
    symbol,
    get_price_at_risk(symbol, 0.0, 'btc') as "0% BTC Risk",
    get_price_at_risk(symbol, 0.5, 'btc') as "50% BTC Risk",
    get_price_at_risk(symbol, 1.0, 'btc') as "100% BTC Risk"
FROM (SELECT DISTINCT symbol FROM cryptoverse_btc_risk_grid) s
WHERE symbol IN ('ETH', 'ADA', 'SOL')
ORDER BY symbol;

-- 7. FINAL STATUS
SELECT
    '🎉 SYSTEM STATUS' as status,
    CASE
        WHEN (SELECT COUNT(*) FROM cryptoverse_risk_grid) = 1025
         AND (SELECT COUNT(*) FROM cryptoverse_btc_risk_grid) = 410
        THEN '✅ ALL DATA LOADED SUCCESSFULLY! System ready for production.'
        ELSE '⚠️ Some data missing. Check counts above.'
    END as message;