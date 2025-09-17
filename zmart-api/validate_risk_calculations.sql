-- VALIDATE RISK CALCULATIONS
-- ===========================
-- Comprehensive validation to ensure all calculations are correct

-- 1. VALIDATE RISK GRID INTERPOLATION
-- Test with known values from SOL
SELECT '🔍 RISK GRID INTERPOLATION TEST' as validation;
WITH test_cases AS (
    SELECT
        'SOL' as symbol,
        245.03 as test_price,
        0.715 as expected_risk
    UNION ALL
    SELECT 'SOL', 20.61, 0.000  -- Bottom
    UNION ALL
    SELECT 'SOL', 299.72, 1.000  -- Top
)
SELECT
    t.symbol,
    t.test_price,
    t.expected_risk,
    get_risk_at_price(t.symbol, t.test_price, 'fiat') as calculated_risk,
    ABS(t.expected_risk - get_risk_at_price(t.symbol, t.test_price, 'fiat')) as difference,
    CASE
        WHEN ABS(t.expected_risk - get_risk_at_price(t.symbol, t.test_price, 'fiat')) < 0.01
        THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM test_cases t;

-- 2. VALIDATE COEFFICIENT CALCULATION
-- Most common should be 1.00, rarest should be 1.60
SELECT '🔍 COEFFICIENT CALCULATION TEST' as validation;
WITH band_stats AS (
    SELECT
        symbol,
        -- Find max and min days
        GREATEST(band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
                band_50_60, band_60_70, band_70_80, band_80_90, band_90_100) as max_days,
        LEAST(
            CASE WHEN band_0_10 > 0 THEN band_0_10 ELSE 999999 END,
            CASE WHEN band_10_20 > 0 THEN band_10_20 ELSE 999999 END,
            CASE WHEN band_20_30 > 0 THEN band_20_30 ELSE 999999 END,
            CASE WHEN band_30_40 > 0 THEN band_30_40 ELSE 999999 END,
            CASE WHEN band_40_50 > 0 THEN band_40_50 ELSE 999999 END,
            CASE WHEN band_50_60 > 0 THEN band_50_60 ELSE 999999 END,
            CASE WHEN band_60_70 > 0 THEN band_60_70 ELSE 999999 END,
            CASE WHEN band_70_80 > 0 THEN band_70_80 ELSE 999999 END,
            CASE WHEN band_80_90 > 0 THEN band_80_90 ELSE 999999 END,
            CASE WHEN band_90_100 > 0 THEN band_90_100 ELSE 999999 END
        ) as min_days,
        -- Get actual coefficients
        coef_0_10, coef_10_20, coef_20_30, coef_30_40, coef_40_50,
        coef_50_60, coef_60_70, coef_70_80, coef_80_90, coef_90_100,
        -- Get actual days
        band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
        band_50_60, band_60_70, band_70_80, band_80_90, band_90_100
    FROM cryptoverse_risk_time_bands_v2
    WHERE symbol = 'SOL'
)
SELECT
    symbol,
    '0.5-0.6 (441 days - most common)' as band_test,
    band_50_60 as days,
    coef_50_60 as coefficient,
    CASE WHEN ABS(coef_50_60 - 1.000) < 0.01 THEN '✅ PASS' ELSE '❌ FAIL' END as status
FROM band_stats
UNION ALL
SELECT
    symbol,
    '0.9-1.0 (40 days - rarest)' as band_test,
    band_90_100 as days,
    coef_90_100 as coefficient,
    CASE WHEN ABS(coef_90_100 - 1.600) < 0.01 THEN '✅ PASS' ELSE '❌ FAIL' END as status
FROM band_stats
UNION ALL
SELECT
    symbol,
    '0.7-0.8 (140 days - intermediate)' as band_test,
    band_70_80 as days,
    coef_70_80 as coefficient,
    CASE
        WHEN ABS(coef_70_80 - (1.600 - ((band_70_80 - min_days)::DECIMAL * 0.600 / (max_days - min_days)))) < 0.01
        THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM band_stats;

-- 3. VALIDATE TIME BAND TOTALS
-- Total days should equal sum of all bands
SELECT '🔍 TIME BAND TOTALS TEST' as validation;
SELECT
    symbol,
    total_days,
    (band_0_10 + band_10_20 + band_20_30 + band_30_40 + band_40_50 +
     band_50_60 + band_60_70 + band_70_80 + band_80_90 + band_90_100) as sum_of_bands,
    CASE
        WHEN ABS(total_days - (band_0_10 + band_10_20 + band_20_30 + band_30_40 + band_40_50 +
                               band_50_60 + band_60_70 + band_70_80 + band_80_90 + band_90_100)) <= 10
        THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM cryptoverse_risk_time_bands_v2
WHERE symbol IN ('BTC', 'ETH', 'SOL')
ORDER BY symbol;

-- 4. VALIDATE RISK BAND ASSIGNMENT
-- Current risk should match the band it's in
SELECT '🔍 RISK BAND ASSIGNMENT TEST' as validation;
SELECT
    symbol,
    current_risk,
    current_risk_band,
    get_current_risk_band(current_risk) as calculated_band,
    CASE
        WHEN current_risk_band = get_current_risk_band(current_risk)
        THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM cryptoverse_risk_time_bands_v2
WHERE current_risk IS NOT NULL
LIMIT 10;

-- 5. VALIDATE PRICE-TO-RISK-TO-PRICE ROUND TRIP
-- If we go from price → risk → price, we should get close to original
SELECT '🔍 ROUND TRIP CALCULATION TEST' as validation;
WITH round_trip AS (
    SELECT
        'SOL' as symbol,
        245.03 as original_price,
        get_risk_at_price('SOL', 245.03, 'fiat') as calculated_risk
)
SELECT
    symbol,
    original_price,
    calculated_risk,
    get_price_at_risk(symbol, calculated_risk, 'fiat') as back_to_price,
    ABS(original_price - get_price_at_risk(symbol, calculated_risk, 'fiat')) as difference,
    CASE
        WHEN ABS(original_price - get_price_at_risk(symbol, calculated_risk, 'fiat')) < 5
        THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM round_trip;

-- 6. COEFFICIENT FORMULA VERIFICATION
-- Manual calculation check for SOL
SELECT '📐 COEFFICIENT FORMULA CHECK' as validation;
WITH sol_data AS (
    SELECT
        symbol,
        band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
        band_50_60, band_60_70, band_70_80, band_80_90, band_90_100,
        coef_0_10, coef_10_20, coef_20_30, coef_30_40, coef_40_50,
        coef_50_60, coef_60_70, coef_70_80, coef_80_90, coef_90_100
    FROM cryptoverse_risk_time_bands_v2
    WHERE symbol = 'SOL'
)
SELECT
    'Formula: 1.60 - ((days - 40) * 0.60 / (441 - 40))' as formula,
    'Band 0.7-0.8' as band,
    140 as days,
    ROUND(1.600 - ((140 - 40) * 0.600 / (441 - 40)), 3) as manual_calc,
    coef_70_80 as stored_coef,
    CASE
        WHEN ABS(coef_70_80 - (1.600 - ((140 - 40) * 0.600 / (441 - 40)))) < 0.01
        THEN '✅ MATCH'
        ELSE '❌ MISMATCH'
    END as verification
FROM sol_data;

-- 7. FINAL SUMMARY
SELECT '📊 VALIDATION SUMMARY' as summary;
WITH all_tests AS (
    SELECT COUNT(*) as total_symbols
    FROM cryptoverse_risk_time_bands_v2
),
risk_grid_test AS (
    SELECT COUNT(*) as grid_points
    FROM cryptoverse_risk_grid
),
btc_grid_test AS (
    SELECT COUNT(*) as btc_points
    FROM cryptoverse_btc_risk_grid
)
SELECT
    'System Health' as metric,
    CASE
        WHEN (SELECT grid_points FROM risk_grid_test) = 1025
         AND (SELECT btc_points FROM btc_grid_test) = 410
         AND (SELECT total_symbols FROM all_tests) = 25
        THEN '✅ ALL SYSTEMS OPERATIONAL'
        ELSE '⚠️ CHECK FAILED'
    END as status,
    (SELECT grid_points FROM risk_grid_test) || ' FIAT points' as fiat_grid,
    (SELECT btc_points FROM btc_grid_test) || ' BTC points' as btc_grid,
    (SELECT total_symbols FROM all_tests) || ' symbols tracked' as symbols;