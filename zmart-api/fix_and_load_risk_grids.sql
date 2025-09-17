-- FIX AND LOAD RISK GRIDS
-- This script fixes the constraint issue and loads all data
-- Run this in Supabase SQL Editor

-- STEP 1: Drop and recreate tables with proper constraints
DROP TABLE IF EXISTS cryptoverse_risk_grid CASCADE;
DROP TABLE IF EXISTS cryptoverse_btc_risk_grid CASCADE;
DROP TABLE IF EXISTS cryptoverse_risk_data CASCADE;

-- STEP 2: Create tables with UNIQUE constraints properly defined
CREATE TABLE cryptoverse_risk_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price_usd DECIMAL(20, 2) NOT NULL,
    fiat_risk DECIMAL(5, 3) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_symbol_fiat_risk UNIQUE(symbol, fiat_risk)
);

CREATE TABLE cryptoverse_btc_risk_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price_btc DECIMAL(20, 8) NOT NULL,
    btc_risk DECIMAL(5, 3) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_symbol_btc_risk UNIQUE(symbol, btc_risk)
);

CREATE TABLE cryptoverse_risk_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    price_usd DECIMAL(20, 2),
    price_btc DECIMAL(20, 8),
    fiat_risk DECIMAL(5, 3),
    btc_risk DECIMAL(5, 3),
    eth_risk DECIMAL(5, 3),
    last_updated TIMESTAMP DEFAULT NOW()
);

-- STEP 3: Create indexes for performance
CREATE INDEX idx_fiat_grid_symbol ON cryptoverse_risk_grid(symbol);
CREATE INDEX idx_fiat_grid_risk ON cryptoverse_risk_grid(fiat_risk);
CREATE INDEX idx_btc_grid_symbol ON cryptoverse_btc_risk_grid(symbol);
CREATE INDEX idx_btc_grid_risk ON cryptoverse_btc_risk_grid(btc_risk);
CREATE INDEX idx_risk_data_symbol ON cryptoverse_risk_data(symbol);

-- STEP 4: Test insert with sample data first
INSERT INTO cryptoverse_risk_grid (symbol, price_usd, fiat_risk) VALUES
    ('BTC', 30000.00, 0.000),
    ('BTC', 31352.00, 0.025),
    ('BTC', 32704.00, 0.050),
    ('BTC', 34055.00, 0.075),
    ('BTC', 35567.00, 0.100)
ON CONFLICT (symbol, fiat_risk) DO UPDATE
SET price_usd = EXCLUDED.price_usd,
    updated_at = NOW();

-- STEP 5: Verify the test insert worked
SELECT COUNT(*) as test_rows_inserted FROM cryptoverse_risk_grid WHERE symbol = 'BTC';

-- STEP 6: Create the functions
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

-- STEP 7: Test the function
SELECT
    'Function Test' as test,
    get_price_at_risk('BTC', 0.05, 'fiat') as btc_at_5_percent;

-- STEP 8: If everything above works, you're ready!
SELECT
    '✅ SETUP COMPLETE' as status,
    'Now run insert_full_risk_grids.sql to load all data' as next_step;