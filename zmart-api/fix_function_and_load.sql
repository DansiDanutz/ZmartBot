-- FIX FUNCTION AND LOAD RISK GRIDS
-- This script drops the existing function and recreates it properly

-- STEP 1: Drop the existing function with the old signature
DROP FUNCTION IF EXISTS get_price_at_risk(VARCHAR, DECIMAL, VARCHAR);

-- STEP 2: Create the function with correct parameter names
CREATE OR REPLACE FUNCTION get_price_at_risk(
    p_symbol VARCHAR,
    p_risk DECIMAL,
    p_type VARCHAR DEFAULT 'fiat'
)
RETURNS DECIMAL AS $$
DECLARE
    v_price DECIMAL;
BEGIN
    IF p_type = 'fiat' THEN
        -- Get interpolated price from fiat risk grid
        WITH risk_bounds AS (
            SELECT
                MAX(CASE WHEN fiat_risk <= p_risk THEN fiat_risk END) as lower_risk,
                MIN(CASE WHEN fiat_risk >= p_risk THEN fiat_risk END) as upper_risk
            FROM cryptoverse_risk_grid
            WHERE symbol = p_symbol
        ),
        price_points AS (
            SELECT
                rb.lower_risk,
                rb.upper_risk,
                l.price_usd as lower_price,
                u.price_usd as upper_price
            FROM risk_bounds rb
            LEFT JOIN cryptoverse_risk_grid l ON l.symbol = p_symbol AND l.fiat_risk = rb.lower_risk
            LEFT JOIN cryptoverse_risk_grid u ON u.symbol = p_symbol AND u.fiat_risk = rb.upper_risk
        )
        SELECT
            CASE
                WHEN lower_risk = upper_risk OR lower_risk IS NULL OR upper_risk IS NULL THEN
                    COALESCE(lower_price, upper_price)
                ELSE
                    lower_price + (upper_price - lower_price) *
                    ((p_risk - lower_risk) / (upper_risk - lower_risk))
            END INTO v_price
        FROM price_points;

    ELSIF p_type = 'btc' THEN
        -- Get interpolated price from btc risk grid
        WITH risk_bounds AS (
            SELECT
                MAX(CASE WHEN btc_risk <= p_risk THEN btc_risk END) as lower_risk,
                MIN(CASE WHEN btc_risk >= p_risk THEN btc_risk END) as upper_risk
            FROM cryptoverse_btc_risk_grid
            WHERE symbol = p_symbol
        ),
        price_points AS (
            SELECT
                rb.lower_risk,
                rb.upper_risk,
                l.price_btc as lower_price,
                u.price_btc as upper_price
            FROM risk_bounds rb
            LEFT JOIN cryptoverse_btc_risk_grid l ON l.symbol = p_symbol AND l.btc_risk = rb.lower_risk
            LEFT JOIN cryptoverse_btc_risk_grid u ON u.symbol = p_symbol AND u.btc_risk = rb.upper_risk
        )
        SELECT
            CASE
                WHEN lower_risk = upper_risk OR lower_risk IS NULL OR upper_risk IS NULL THEN
                    COALESCE(lower_price, upper_price)
                ELSE
                    lower_price + (upper_price - lower_price) *
                    ((p_risk - lower_risk) / (upper_risk - lower_risk))
            END INTO v_price
        FROM price_points;
    END IF;

    RETURN v_price;
END;
$$ LANGUAGE plpgsql;

-- STEP 3: Test the function with existing data
SELECT
    'Function Test' as test,
    get_price_at_risk('BTC', 0.05, 'fiat') as btc_at_5_percent,
    get_price_at_risk('BTC', 0.10, 'fiat') as btc_at_10_percent;

-- STEP 4: Check current data status
SELECT
    'Data Status' as info,
    (SELECT COUNT(*) FROM cryptoverse_risk_grid) as fiat_grid_rows,
    (SELECT COUNT(DISTINCT symbol) FROM cryptoverse_risk_grid) as fiat_symbols,
    (SELECT COUNT(*) FROM cryptoverse_btc_risk_grid) as btc_grid_rows,
    (SELECT COUNT(DISTINCT symbol) FROM cryptoverse_btc_risk_grid) as btc_symbols;

-- STEP 5: If you see only 5 rows for BTC test data, you're ready to load full data
SELECT
    '✅ FUNCTION FIXED' as status,
    'Now run insert_full_risk_grids.sql and insert_btc_risk_grids.sql' as next_step;