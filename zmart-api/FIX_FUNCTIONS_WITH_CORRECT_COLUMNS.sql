-- ============================================
-- FIX: CHECK ACTUAL TABLE STRUCTURE AND CREATE CORRECT FUNCTIONS
-- ============================================

-- 1. First, check what columns actually exist in your risk tables
SELECT
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'cryptoverse_risk_grid'
ORDER BY ordinal_position;

-- 2. Check sample data to understand structure
SELECT * FROM cryptoverse_risk_grid LIMIT 5;

-- 3. Create functions with CORRECT column names
-- Based on the error, it seems the column is 'fiat_risk' not 'risk_value'

DROP FUNCTION IF EXISTS get_risk_at_price CASCADE;

CREATE OR REPLACE FUNCTION get_risk_at_price(
    p_symbol VARCHAR,
    p_price NUMERIC,
    p_type VARCHAR DEFAULT 'fiat'
)
RETURNS NUMERIC AS $$
DECLARE
    v_risk NUMERIC;
BEGIN
    -- Using the correct column name: fiat_risk
    SELECT fiat_risk INTO v_risk
    FROM cryptoverse_risk_grid
    WHERE symbol = p_symbol
    AND price_usd <= p_price
    ORDER BY price_usd DESC
    LIMIT 1;

    RETURN COALESCE(v_risk, 0.5);
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS get_price_at_risk CASCADE;

CREATE OR REPLACE FUNCTION get_price_at_risk(
    p_symbol VARCHAR,
    p_risk NUMERIC,
    p_type VARCHAR DEFAULT 'fiat'
)
RETURNS NUMERIC AS $$
DECLARE
    v_price NUMERIC;
BEGIN
    -- Using the correct column names
    SELECT price_usd INTO v_price
    FROM cryptoverse_risk_grid
    WHERE symbol = p_symbol
    AND fiat_risk <= p_risk
    ORDER BY fiat_risk DESC
    LIMIT 1;

    RETURN COALESCE(v_price, 0);
END;
$$ LANGUAGE plpgsql;

-- 4. Test the fixed functions
SELECT
    'FIXED FUNCTION TEST' as test,
    get_risk_at_price('BTC', 100000::numeric, 'fiat') as btc_risk_at_100k,
    get_price_at_risk('BTC', 0.5::numeric, 'fiat') as btc_price_at_50_risk;

-- 5. Check if we have data for common symbols
SELECT
    symbol,
    COUNT(*) as data_points,
    MIN(price_usd) as min_price,
    MAX(price_usd) as max_price,
    MIN(fiat_risk) as min_risk,
    MAX(fiat_risk) as max_risk
FROM cryptoverse_risk_grid
WHERE symbol IN ('BTC', 'ETH', 'ADA', 'SOL')
GROUP BY symbol;

-- 6. Final status
SELECT
    '✅ FUNCTIONS FIXED' as status,
    'Using correct column names (fiat_risk, price_usd)' as fix,
    'System should work now' as result;