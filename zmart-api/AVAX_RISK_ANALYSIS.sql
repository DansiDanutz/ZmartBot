-- ========================================
-- AVAX RISK METRIC ANALYSIS
-- Current Market Price: $30.47
-- Analysis Date: December 17, 2024
-- ========================================

-- 1. GET AVAX RISK AT CURRENT PRICE
SELECT '📊 AVAX CURRENT RISK ANALYSIS' as analysis;
SELECT
    'AVAX' as symbol,
    30.47 as current_price_usd,
    get_risk_at_price('AVAX', 30.47, 'fiat') as current_risk,
    get_current_risk_band(get_risk_at_price('AVAX', 30.47, 'fiat')) as risk_band;

-- 2. GET AVAX TIME DISTRIBUTION & COEFFICIENTS
SELECT '📈 AVAX TIME BANDS & COEFFICIENTS' as analysis;
SELECT
    symbol,
    total_days,
    current_risk,
    current_risk_band,
    -- Show all band days
    band_0_10 || ' days' as band_0_10,
    band_10_20 || ' days' as band_10_20,
    band_20_30 || ' days' as band_20_30,
    band_30_40 || ' days' as band_30_40,
    band_40_50 || ' days' as band_40_50,
    band_50_60 || ' days' as band_50_60,
    band_60_70 || ' days' as band_60_70,
    band_70_80 || ' days' as band_70_80,
    band_80_90 || ' days' as band_80_90,
    band_90_100 || ' days' as band_90_100
FROM cryptoverse_risk_time_bands_v2
WHERE symbol = 'AVAX';

-- 3. GET AVAX COEFFICIENTS
SELECT '🔢 AVAX RARITY COEFFICIENTS' as analysis;
SELECT
    symbol,
    ROUND(coef_0_10, 3) as coef_0_10,
    ROUND(coef_10_20, 3) as coef_10_20,
    ROUND(coef_20_30, 3) as coef_20_30,
    ROUND(coef_30_40, 3) as coef_30_40,
    ROUND(coef_40_50, 3) as coef_40_50,
    ROUND(coef_50_60, 3) as coef_50_60,
    ROUND(coef_60_70, 3) as coef_60_70,
    ROUND(coef_70_80, 3) as coef_70_80,
    ROUND(coef_80_90, 3) as coef_80_90,
    ROUND(coef_90_100, 3) as coef_90_100
FROM cryptoverse_risk_time_bands_v2
WHERE symbol = 'AVAX';

-- 4. CALCULATE AVAX SCORE AT CURRENT PRICE
SELECT '🎯 AVAX SCORING AT $30.47' as analysis;
WITH avax_current AS (
    SELECT
        'AVAX' as symbol,
        get_risk_at_price('AVAX', 30.47, 'fiat') as risk,
        get_current_risk_band(get_risk_at_price('AVAX', 30.47, 'fiat')) as band
)
SELECT
    a.symbol,
    30.47 as price,
    ROUND(a.risk, 3) as risk_value,
    a.band as risk_band,
    calculate_base_score(a.risk) as base_score,
    CASE a.band
        WHEN '0.0-0.1' THEN t.coef_0_10
        WHEN '0.1-0.2' THEN t.coef_10_20
        WHEN '0.2-0.3' THEN t.coef_20_30
        WHEN '0.3-0.4' THEN t.coef_30_40
        WHEN '0.4-0.5' THEN t.coef_40_50
        WHEN '0.5-0.6' THEN t.coef_50_60
        WHEN '0.6-0.7' THEN t.coef_60_70
        WHEN '0.7-0.8' THEN t.coef_70_80
        WHEN '0.8-0.9' THEN t.coef_80_90
        WHEN '0.9-1.0' THEN t.coef_90_100
    END as coefficient,
    calculate_base_score(a.risk) *
    CASE a.band
        WHEN '0.0-0.1' THEN t.coef_0_10
        WHEN '0.1-0.2' THEN t.coef_10_20
        WHEN '0.2-0.3' THEN t.coef_20_30
        WHEN '0.3-0.4' THEN t.coef_30_40
        WHEN '0.4-0.5' THEN t.coef_40_50
        WHEN '0.5-0.6' THEN t.coef_50_60
        WHEN '0.6-0.7' THEN t.coef_60_70
        WHEN '0.7-0.8' THEN t.coef_70_80
        WHEN '0.8-0.9' THEN t.coef_80_90
        WHEN '0.9-1.0' THEN t.coef_90_100
    END as total_score,
    determine_signal_type(a.risk) as signal_type
FROM avax_current a, cryptoverse_risk_time_bands_v2 t
WHERE t.symbol = 'AVAX';

-- 5. GET AVAX TRADING SIGNAL
SELECT '🚨 AVAX TRADING SIGNAL' as analysis;
SELECT * FROM calculate_riskmetric_score(
    'AVAX',
    get_risk_at_price('AVAX', 30.47, 'fiat'),
    (SELECT
        CASE get_current_risk_band(get_risk_at_price('AVAX', 30.47, 'fiat'))
            WHEN '0.0-0.1' THEN coef_0_10
            WHEN '0.1-0.2' THEN coef_10_20
            WHEN '0.2-0.3' THEN coef_20_30
            WHEN '0.3-0.4' THEN coef_30_40
            WHEN '0.4-0.5' THEN coef_40_50
            WHEN '0.5-0.6' THEN coef_50_60
            WHEN '0.6-0.7' THEN coef_60_70
            WHEN '0.7-0.8' THEN coef_70_80
            WHEN '0.8-0.9' THEN coef_80_90
            WHEN '0.9-1.0' THEN coef_90_100
        END
     FROM cryptoverse_risk_time_bands_v2
     WHERE symbol = 'AVAX')
);

-- 6. COMPARE WITH OTHER TOP SYMBOLS
SELECT '📊 AVAX VS TOP SYMBOLS' as comparison;
SELECT
    symbol,
    ROUND(current_risk, 3) as risk,
    current_risk_band as band,
    base_score,
    ROUND(coefficient, 3) as coef,
    ROUND(total_score, 1) as score,
    signal_type,
    signal_strength,
    action
FROM v_riskmetric_scores
WHERE symbol IN ('AVAX', 'BTC', 'ETH', 'SOL')
ORDER BY total_score DESC;

-- 7. AVAX HISTORICAL BANDS
SELECT '📅 AVAX BAND HISTORY (Most to Least Time)' as history;
WITH band_data AS (
    SELECT * FROM cryptoverse_risk_time_bands_v2 WHERE symbol = 'AVAX'
)
SELECT
    'Band 0.0-0.1' as band, band_0_10 as days, coef_0_10 as coefficient FROM band_data
UNION ALL
SELECT 'Band 0.1-0.2', band_10_20, coef_10_20 FROM band_data
UNION ALL
SELECT 'Band 0.2-0.3', band_20_30, coef_20_30 FROM band_data
UNION ALL
SELECT 'Band 0.3-0.4', band_30_40, coef_30_40 FROM band_data
UNION ALL
SELECT 'Band 0.4-0.5', band_40_50, coef_40_50 FROM band_data
UNION ALL
SELECT 'Band 0.5-0.6', band_50_60, coef_50_60 FROM band_data
UNION ALL
SELECT 'Band 0.6-0.7', band_60_70, coef_60_70 FROM band_data
UNION ALL
SELECT 'Band 0.7-0.8', band_70_80, coef_70_80 FROM band_data
UNION ALL
SELECT 'Band 0.8-0.9', band_80_90, coef_80_90 FROM band_data
UNION ALL
SELECT 'Band 0.9-1.0', band_90_100, coef_90_100 FROM band_data
ORDER BY days DESC;

-- 8. PRICE TARGETS FOR AVAX
SELECT '🎯 AVAX KEY PRICE LEVELS' as targets;
SELECT
    'AVAX' as symbol,
    get_price_at_risk('AVAX', 0.10, 'fiat') as extreme_oversold_10,
    get_price_at_risk('AVAX', 0.15, 'fiat') as extreme_oversold_15,
    get_price_at_risk('AVAX', 0.25, 'fiat') as strong_oversold_25,
    get_price_at_risk('AVAX', 0.35, 'fiat') as moderate_oversold_35,
    get_price_at_risk('AVAX', 0.50, 'fiat') as neutral_50,
    get_price_at_risk('AVAX', 0.65, 'fiat') as moderate_overbought_65,
    get_price_at_risk('AVAX', 0.75, 'fiat') as strong_overbought_75,
    get_price_at_risk('AVAX', 0.85, 'fiat') as extreme_overbought_85,
    get_price_at_risk('AVAX', 0.90, 'fiat') as extreme_overbought_90;

-- 9. UPDATE AVAX WITH CURRENT PRICE
UPDATE cryptoverse_risk_data
SET
    price_usd = 30.47,
    fiat_risk = get_risk_at_price('AVAX', 30.47, 'fiat'),
    last_updated = NOW()
WHERE symbol = 'AVAX';

UPDATE cryptoverse_risk_time_bands_v2
SET
    current_risk = get_risk_at_price('AVAX', 30.47, 'fiat'),
    current_risk_band = get_current_risk_band(get_risk_at_price('AVAX', 30.47, 'fiat'))
WHERE symbol = 'AVAX';

-- Trigger score update
SELECT update_all_riskmetric_scores();

-- 10. FINAL AVAX ASSESSMENT
SELECT '✅ AVAX FINAL ASSESSMENT AT $30.47' as assessment;
SELECT
    symbol,
    current_price,
    ROUND(current_risk, 3) as risk,
    CASE
        WHEN current_risk <= 0.15 THEN '🔥 EXTREME OVERSOLD (0-15%)'
        WHEN current_risk <= 0.25 THEN '🔥 STRONG OVERSOLD (15-25%)'
        WHEN current_risk <= 0.35 THEN '✅ MODERATE OVERSOLD (25-35%)'
        WHEN current_risk >= 0.85 THEN '⚠️ EXTREME OVERBOUGHT (85-100%)'
        WHEN current_risk >= 0.75 THEN '⚠️ STRONG OVERBOUGHT (75-85%)'
        WHEN current_risk >= 0.65 THEN '📉 MODERATE OVERBOUGHT (65-75%)'
        ELSE '⏸️ NEUTRAL (35-65%)'
    END as zone,
    base_score,
    ROUND(coefficient, 3) as coef,
    ROUND(total_score, 1) as score,
    signal_type,
    signal_strength,
    action
FROM v_riskmetric_scores
WHERE symbol = 'AVAX';