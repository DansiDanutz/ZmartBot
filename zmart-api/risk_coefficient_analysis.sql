-- RISK COEFFICIENT ANALYSIS WITH TIME BANDS
-- ==========================================
-- The coefficients help predict future behavior based on historical time distribution

-- 1. UNDERSTAND THE COEFFICIENT CALCULATION
-- Coefficient = (Band Center × Time Percentage) / 100
-- Example: SOL spent 21.96% in 0.5-0.6 band
-- Coefficient = 0.55 × 21.96 / 100 = 0.121

-- 2. CREATE A COMPLETE RISK ANALYSIS VIEW
CREATE OR REPLACE VIEW v_risk_coefficient_analysis AS
WITH band_analysis AS (
    SELECT
        symbol,
        symbol_name,
        birth_date,
        total_days,
        current_risk_band,

        -- Calculate coefficients for each band
        (0.05 * band_0_10_pct / 100) as coef_0_10,
        (0.15 * band_10_20_pct / 100) as coef_10_20,
        (0.25 * band_20_30_pct / 100) as coef_20_30,
        (0.35 * band_30_40_pct / 100) as coef_30_40,
        (0.45 * band_40_50_pct / 100) as coef_40_50,
        (0.55 * band_50_60_pct / 100) as coef_50_60,
        (0.65 * band_60_70_pct / 100) as coef_60_70,
        (0.75 * band_70_80_pct / 100) as coef_70_80,
        (0.85 * band_80_90_pct / 100) as coef_80_90,
        (0.95 * band_90_100_pct / 100) as coef_90_100,

        -- Time in bands for analysis
        band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
        band_50_60, band_60_70, band_70_80, band_80_90, band_90_100,

        band_0_10_pct, band_10_20_pct, band_20_30_pct, band_30_40_pct, band_40_50_pct,
        band_50_60_pct, band_60_70_pct, band_70_80_pct, band_80_90_pct, band_90_100_pct

    FROM cryptoverse_risk_time_bands
)
SELECT
    symbol,
    symbol_name,
    birth_date,
    total_days,
    current_risk_band,

    -- Weighted Risk Score (sum of all coefficients)
    ROUND(
        coef_0_10 + coef_10_20 + coef_20_30 + coef_30_40 + coef_40_50 +
        coef_50_60 + coef_60_70 + coef_70_80 + coef_80_90 + coef_90_100, 4
    ) as weighted_risk_score,

    -- Most time spent in which band
    CASE
        WHEN GREATEST(band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
                     band_50_60, band_60_70, band_70_80, band_80_90, band_90_100) = band_0_10 THEN '0.0-0.1'
        WHEN GREATEST(band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
                     band_50_60, band_60_70, band_70_80, band_80_90, band_90_100) = band_10_20 THEN '0.1-0.2'
        WHEN GREATEST(band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
                     band_50_60, band_60_70, band_70_80, band_80_90, band_90_100) = band_20_30 THEN '0.2-0.3'
        WHEN GREATEST(band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
                     band_50_60, band_60_70, band_70_80, band_80_90, band_90_100) = band_30_40 THEN '0.3-0.4'
        WHEN GREATEST(band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
                     band_50_60, band_60_70, band_70_80, band_80_90, band_90_100) = band_40_50 THEN '0.4-0.5'
        WHEN GREATEST(band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
                     band_50_60, band_60_70, band_70_80, band_80_90, band_90_100) = band_50_60 THEN '0.5-0.6'
        WHEN GREATEST(band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
                     band_50_60, band_60_70, band_70_80, band_80_90, band_90_100) = band_60_70 THEN '0.6-0.7'
        WHEN GREATEST(band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
                     band_50_60, band_60_70, band_70_80, band_80_90, band_90_100) = band_70_80 THEN '0.7-0.8'
        WHEN GREATEST(band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
                     band_50_60, band_60_70, band_70_80, band_80_90, band_90_100) = band_80_90 THEN '0.8-0.9'
        ELSE '0.9-1.0'
    END as dominant_band,

    -- Days in dominant band
    GREATEST(band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
            band_50_60, band_60_70, band_70_80, band_80_90, band_90_100) as days_in_dominant,

    -- Percentage in dominant band
    GREATEST(band_0_10_pct, band_10_20_pct, band_20_30_pct, band_30_40_pct, band_40_50_pct,
            band_50_60_pct, band_60_70_pct, band_70_80_pct, band_80_90_pct, band_90_100_pct) as pct_in_dominant

FROM band_analysis;

-- 3. ANALYZE SOL SPECIFICALLY
SELECT
    '📊 SOL RISK COEFFICIENT ANALYSIS' as analysis;

SELECT
    'Time Distribution' as metric,
    band_50_60 as "Days in 50-60% band",
    ROUND(band_50_60_pct, 2) as "% Time in 50-60%",
    ROUND(0.55 * band_50_60_pct / 100, 4) as "Coefficient (0.55 × 21.96%)"
FROM cryptoverse_risk_time_bands
WHERE symbol = 'SOL'
UNION ALL
SELECT
    'Current Status' as metric,
    NULL as "Days in 50-60% band",
    0.715 * 100 as "% Time in 50-60%",
    0.715 as "Coefficient (0.55 × 21.96%)"
FROM cryptoverse_risk_time_bands
WHERE symbol = 'SOL';

-- 4. SHOW COEFFICIENT CALCULATION FOR ALL SOL BANDS
SELECT
    'Band' as band,
    'Days' as days,
    '% Time' as pct_time,
    'Center' as center,
    'Coefficient' as coefficient
UNION ALL
SELECT
    '0.0-0.1' as band,
    band_0_10::text as days,
    ROUND(band_0_10_pct, 2)::text as pct_time,
    '0.05' as center,
    ROUND(0.05 * band_0_10_pct / 100, 4)::text as coefficient
FROM cryptoverse_risk_time_bands WHERE symbol = 'SOL'
UNION ALL
SELECT
    '0.1-0.2' as band,
    band_10_20::text as days,
    ROUND(band_10_20_pct, 2)::text as pct_time,
    '0.15' as center,
    ROUND(0.15 * band_10_20_pct / 100, 4)::text as coefficient
FROM cryptoverse_risk_time_bands WHERE symbol = 'SOL'
UNION ALL
SELECT
    '0.2-0.3' as band,
    band_20_30::text as days,
    ROUND(band_20_30_pct, 2)::text as pct_time,
    '0.25' as center,
    ROUND(0.25 * band_20_30_pct / 100, 4)::text as coefficient
FROM cryptoverse_risk_time_bands WHERE symbol = 'SOL'
UNION ALL
SELECT
    '0.3-0.4' as band,
    band_30_40::text as days,
    ROUND(band_30_40_pct, 2)::text as pct_time,
    '0.35' as center,
    ROUND(0.35 * band_30_40_pct / 100, 4)::text as coefficient
FROM cryptoverse_risk_time_bands WHERE symbol = 'SOL'
UNION ALL
SELECT
    '0.4-0.5' as band,
    band_40_50::text as days,
    ROUND(band_40_50_pct, 2)::text as pct_time,
    '0.45' as center,
    ROUND(0.45 * band_40_50_pct / 100, 4)::text as coefficient
FROM cryptoverse_risk_time_bands WHERE symbol = 'SOL'
UNION ALL
SELECT
    '0.5-0.6 ⭐' as band,
    band_50_60::text as days,
    ROUND(band_50_60_pct, 2)::text as pct_time,
    '0.55' as center,
    ROUND(0.55 * band_50_60_pct / 100, 4)::text as coefficient
FROM cryptoverse_risk_time_bands WHERE symbol = 'SOL'
UNION ALL
SELECT
    '0.6-0.7' as band,
    band_60_70::text as days,
    ROUND(band_60_70_pct, 2)::text as pct_time,
    '0.65' as center,
    ROUND(0.65 * band_60_70_pct / 100, 4)::text as coefficient
FROM cryptoverse_risk_time_bands WHERE symbol = 'SOL'
UNION ALL
SELECT
    '0.7-0.8 📍' as band,
    band_70_80::text as days,
    ROUND(band_70_80_pct, 2)::text as pct_time,
    '0.75' as center,
    ROUND(0.75 * band_70_80_pct / 100, 4)::text as coefficient
FROM cryptoverse_risk_time_bands WHERE symbol = 'SOL'
UNION ALL
SELECT
    '0.8-0.9' as band,
    band_80_90::text as days,
    ROUND(band_80_90_pct, 2)::text as pct_time,
    '0.85' as center,
    ROUND(0.85 * band_80_90_pct / 100, 4)::text as coefficient
FROM cryptoverse_risk_time_bands WHERE symbol = 'SOL'
UNION ALL
SELECT
    '0.9-1.0' as band,
    band_90_100::text as days,
    ROUND(band_90_100_pct, 2)::text as pct_time,
    '0.95' as center,
    ROUND(0.95 * band_90_100_pct / 100, 4)::text as coefficient
FROM cryptoverse_risk_time_bands WHERE symbol = 'SOL';

-- 5. PREDICTIVE POWER
SELECT
    '🔮 WHAT THE COEFFICIENTS TELL US' as insight,
    'SOL spends most time (21.96%) in 0.5-0.6 band' as observation
UNION ALL
SELECT
    '⚠️ CURRENT RISK' as insight,
    'SOL is now at 71.5% risk (0.7-0.8 band)' as observation
UNION ALL
SELECT
    '📈 HISTORICAL PATTERN' as insight,
    'SOL only spent 6.97% of time in 70-80% band' as observation
UNION ALL
SELECT
    '💡 IMPLICATION' as insight,
    'High probability SOL will revert to lower risk levels' as observation;

-- 6. WEIGHTED RISK SCORE RANKING
SELECT
    symbol,
    ROUND(weighted_risk_score, 4) as weighted_score,
    dominant_band,
    days_in_dominant as "Days in Dominant",
    ROUND(pct_in_dominant, 1) as "% in Dominant",
    current_risk_band as "Current Band"
FROM v_risk_coefficient_analysis
ORDER BY weighted_risk_score DESC
LIMIT 10;