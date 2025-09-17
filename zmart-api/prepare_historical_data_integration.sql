-- PREPARE HISTORICAL DATA INTEGRATION
-- ====================================
-- Setup for incorporating historical price data into risk calculations

-- 1. CREATE HISTORICAL PRICE TABLE
CREATE TABLE IF NOT EXISTS historical_price_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(20, 8),
    high_price DECIMAL(20, 8),
    low_price DECIMAL(20, 8),
    close_price DECIMAL(20, 8),
    volume DECIMAL(30, 8),
    market_cap DECIMAL(30, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, date)
);

CREATE INDEX IF NOT EXISTS idx_historical_symbol_date ON historical_price_data(symbol, date);
CREATE INDEX IF NOT EXISTS idx_historical_date ON historical_price_data(date);

-- 2. CREATE HISTORICAL RISK CALCULATION TABLE
CREATE TABLE IF NOT EXISTS historical_risk_calculations (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    close_price DECIMAL(20, 8),
    risk_value DECIMAL(5, 3),
    risk_band VARCHAR(10),
    band_coefficient DECIMAL(4, 3),
    adjusted_risk DECIMAL(5, 3),
    days_in_band_at_date INTEGER,
    total_days_at_date INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, date)
);

CREATE INDEX IF NOT EXISTS idx_historical_risk_symbol_date ON historical_risk_calculations(symbol, date);
CREATE INDEX IF NOT EXISTS idx_historical_risk_band ON historical_risk_calculations(risk_band);

-- 3. FUNCTION TO BACKFILL HISTORICAL RISK
CREATE OR REPLACE FUNCTION calculate_historical_risk(
    p_symbol VARCHAR,
    p_date DATE,
    p_price DECIMAL
)
RETURNS TABLE(
    risk_value DECIMAL,
    risk_band VARCHAR,
    coefficient DECIMAL,
    adjusted_risk DECIMAL
) AS $$
DECLARE
    v_risk DECIMAL;
    v_band VARCHAR;
    v_coef DECIMAL;
    v_days_in_band INTEGER;
    v_total_days INTEGER;
    v_min_days INTEGER;
    v_max_days INTEGER;
BEGIN
    -- Calculate risk from historical price
    v_risk := get_risk_at_price(p_symbol, p_price, 'fiat');

    -- Determine band
    v_band := get_current_risk_band(v_risk);

    -- Get historical band distribution up to that date
    -- This would need actual historical data to be accurate
    -- For now, we'll use current coefficients as approximation

    SELECT
        CASE v_band
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
        END INTO v_coef
    FROM cryptoverse_risk_time_bands_v2
    WHERE symbol = p_symbol;

    IF v_coef IS NULL THEN
        v_coef := 1.0;
    END IF;

    RETURN QUERY
    SELECT
        v_risk as risk_value,
        v_band as risk_band,
        v_coef as coefficient,
        v_risk * v_coef as adjusted_risk;
END;
$$ LANGUAGE plpgsql;

-- 4. FUNCTION TO REBUILD HISTORICAL TIME BANDS
CREATE OR REPLACE FUNCTION rebuild_historical_time_bands(
    p_symbol VARCHAR
)
RETURNS TABLE(
    band VARCHAR,
    days_count INTEGER,
    percentage DECIMAL
) AS $$
DECLARE
    total_days INTEGER;
BEGIN
    -- Count total historical days
    SELECT COUNT(DISTINCT date) INTO total_days
    FROM historical_risk_calculations
    WHERE symbol = p_symbol;

    -- Return band distribution
    RETURN QUERY
    SELECT
        risk_band as band,
        COUNT(*)::INTEGER as days_count,
        ROUND(100.0 * COUNT(*) / NULLIF(total_days, 0), 2) as percentage
    FROM historical_risk_calculations
    WHERE symbol = p_symbol
    GROUP BY risk_band
    ORDER BY risk_band;
END;
$$ LANGUAGE plpgsql;

-- 5. FUNCTION TO VALIDATE CALCULATIONS
CREATE OR REPLACE FUNCTION validate_risk_calculations()
RETURNS TABLE(
    test_name TEXT,
    status TEXT,
    details TEXT
) AS $$
BEGIN
    -- Test 1: Risk Grid Integrity
    RETURN QUERY
    SELECT
        'Risk Grid Integrity'::TEXT,
        CASE
            WHEN COUNT(*) = 1025 THEN 'PASS'::TEXT
            ELSE 'FAIL'::TEXT
        END,
        'Expected 1025 points, found ' || COUNT(*) || ' points'::TEXT
    FROM cryptoverse_risk_grid;

    -- Test 2: Coefficient Range
    RETURN QUERY
    SELECT
        'Coefficient Range'::TEXT,
        CASE
            WHEN MIN(LEAST(coef_0_10, coef_10_20, coef_20_30, coef_30_40, coef_40_50,
                          coef_50_60, coef_60_70, coef_70_80, coef_80_90, coef_90_100)) >= 0.999
             AND MAX(GREATEST(coef_0_10, coef_10_20, coef_20_30, coef_30_40, coef_40_50,
                             coef_50_60, coef_60_70, coef_70_80, coef_80_90, coef_90_100)) <= 1.601
            THEN 'PASS'::TEXT
            ELSE 'FAIL'::TEXT
        END,
        'Coefficients should be between 1.00 and 1.60'::TEXT
    FROM cryptoverse_risk_time_bands_v2;

    -- Test 3: Time Band Totals
    RETURN QUERY
    WITH band_sums AS (
        SELECT
            symbol,
            total_days,
            (band_0_10 + band_10_20 + band_20_30 + band_30_40 + band_40_50 +
             band_50_60 + band_60_70 + band_70_80 + band_80_90 + band_90_100) as sum_bands
        FROM cryptoverse_risk_time_bands_v2
    )
    SELECT
        'Time Band Totals'::TEXT,
        CASE
            WHEN MAX(ABS(total_days - sum_bands)) <= 10 THEN 'PASS'::TEXT
            ELSE 'FAIL'::TEXT
        END,
        'Max difference: ' || MAX(ABS(total_days - sum_bands)) || ' days'::TEXT
    FROM band_sums;

    -- Test 4: SOL Specific Values
    RETURN QUERY
    SELECT
        'SOL Risk at $245'::TEXT,
        CASE
            WHEN ABS(get_risk_at_price('SOL', 245.03, 'fiat') - 0.715) < 0.05
            THEN 'PASS'::TEXT
            ELSE 'FAIL'::TEXT
        END,
        'Expected ~0.715, got ' || ROUND(get_risk_at_price('SOL', 245.03, 'fiat'), 3)::TEXT;

    -- Test 5: Coefficient Formula
    RETURN QUERY
    WITH sol_coef AS (
        SELECT
            band_70_80 as days,
            coef_70_80 as coefficient
        FROM cryptoverse_risk_time_bands_v2
        WHERE symbol = 'SOL'
    )
    SELECT
        'SOL Coefficient Formula'::TEXT,
        CASE
            WHEN ABS(coefficient - (1.600 - ((days - 40) * 0.600 / (441 - 40)))) < 0.01
            THEN 'PASS'::TEXT
            ELSE 'FAIL'::TEXT
        END,
        'Band 70-80: ' || days || ' days = ' || coefficient || ' coefficient'::TEXT
    FROM sol_coef;
END;
$$ LANGUAGE plpgsql;

-- 6. RUN VALIDATION
SELECT * FROM validate_risk_calculations();

-- 7. SAMPLE HISTORICAL DATA STRUCTURE
-- This shows what historical data we need
SELECT '📁 HISTORICAL DATA REQUIREMENTS' as info;
SELECT
    'Date' as column_name,
    'DATE' as data_type,
    'Daily date' as description
UNION ALL
SELECT 'Symbol', 'VARCHAR(10)', 'BTC, ETH, SOL, etc.'
UNION ALL
SELECT 'Close Price', 'DECIMAL(20,8)', 'Daily closing price'
UNION ALL
SELECT 'Volume', 'DECIMAL(30,8)', 'Daily trading volume'
UNION ALL
SELECT 'Market Cap', 'DECIMAL(30,2)', 'Market capitalization';

-- 8. CHECK CURRENT CALCULATION ACCURACY
SELECT '✅ CALCULATION VERIFICATION' as status;
SELECT
    'SOL' as symbol,
    245.03 as test_price,
    get_risk_at_price('SOL', 245.03, 'fiat') as calculated_risk,
    0.715 as expected_risk,
    ABS(get_risk_at_price('SOL', 245.03, 'fiat') - 0.715) as difference,
    CASE
        WHEN ABS(get_risk_at_price('SOL', 245.03, 'fiat') - 0.715) < 0.05
        THEN '✅ ACCURATE'
        ELSE '⚠️ CHECK NEEDED'
    END as status;