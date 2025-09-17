-- COMPLETE SUPABASE SETUP FOR RISK GRIDS
-- Run this entire script in Supabase SQL Editor
-- Date: 2025-09-16

-- ============================================
-- STEP 1: CREATE TABLES IF THEY DON'T EXIST
-- ============================================

-- 1A. Create FIAT risk grid table
CREATE TABLE IF NOT EXISTS cryptoverse_risk_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price_usd DECIMAL(20, 2) NOT NULL,
    fiat_risk DECIMAL(5, 3) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, fiat_risk)
);

-- 1B. Create BTC risk grid table
CREATE TABLE IF NOT EXISTS cryptoverse_btc_risk_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price_btc DECIMAL(20, 10) NOT NULL,
    btc_risk DECIMAL(5, 3) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, btc_risk)
);

-- 1C. Create current risk data table (if not exists)
CREATE TABLE IF NOT EXISTS cryptoverse_risk_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    price_usd DECIMAL(20, 8),
    price_btc DECIMAL(20, 10),
    fiat_risk DECIMAL(5, 3),
    btc_risk DECIMAL(5, 3),
    btc_reference_price DECIMAL(20, 2),
    data_source VARCHAR(50) DEFAULT 'IntoTheCryptoverse',
    last_updated DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- STEP 2: CREATE INDEXES FOR PERFORMANCE
-- ============================================

-- Indexes for FIAT risk grid
CREATE INDEX IF NOT EXISTS idx_risk_grid_symbol ON cryptoverse_risk_grid(symbol);
CREATE INDEX IF NOT EXISTS idx_risk_grid_risk ON cryptoverse_risk_grid(fiat_risk);
CREATE INDEX IF NOT EXISTS idx_risk_grid_symbol_risk ON cryptoverse_risk_grid(symbol, fiat_risk);

-- Indexes for BTC risk grid
CREATE INDEX IF NOT EXISTS idx_btc_risk_grid_symbol ON cryptoverse_btc_risk_grid(symbol);
CREATE INDEX IF NOT EXISTS idx_btc_risk_grid_risk ON cryptoverse_btc_risk_grid(btc_risk);
CREATE INDEX IF NOT EXISTS idx_btc_risk_grid_symbol_risk ON cryptoverse_btc_risk_grid(symbol, btc_risk);

-- Indexes for current risk data
CREATE INDEX IF NOT EXISTS idx_risk_data_symbol ON cryptoverse_risk_data(symbol);
CREATE INDEX IF NOT EXISTS idx_risk_data_fiat_risk ON cryptoverse_risk_data(fiat_risk);

-- ============================================
-- STEP 3: CREATE USEFUL FUNCTIONS
-- ============================================

-- Function to get price at specific risk level
CREATE OR REPLACE FUNCTION get_price_at_risk(
    p_symbol VARCHAR,
    p_risk DECIMAL,
    p_risk_type VARCHAR DEFAULT 'fiat'
)
RETURNS DECIMAL AS $$
DECLARE
    v_price DECIMAL;
BEGIN
    IF p_risk_type = 'btc' THEN
        SELECT price_btc INTO v_price
        FROM cryptoverse_btc_risk_grid
        WHERE symbol = p_symbol
        AND ABS(btc_risk - p_risk) < 0.001
        LIMIT 1;
    ELSE
        SELECT price_usd INTO v_price
        FROM cryptoverse_risk_grid
        WHERE symbol = p_symbol
        AND ABS(fiat_risk - p_risk) < 0.001
        LIMIT 1;
    END IF;

    RETURN v_price;
END;
$$ LANGUAGE plpgsql;

-- Function to get risk level at specific price
CREATE OR REPLACE FUNCTION get_risk_at_price(
    p_symbol VARCHAR,
    p_price DECIMAL,
    p_risk_type VARCHAR DEFAULT 'fiat'
)
RETURNS DECIMAL AS $$
DECLARE
    v_risk DECIMAL;
BEGIN
    IF p_risk_type = 'btc' THEN
        -- Find closest risk level for given BTC price
        SELECT btc_risk INTO v_risk
        FROM cryptoverse_btc_risk_grid
        WHERE symbol = p_symbol
        ORDER BY ABS(price_btc - p_price)
        LIMIT 1;
    ELSE
        -- Find closest risk level for given USD price
        SELECT fiat_risk INTO v_risk
        FROM cryptoverse_risk_grid
        WHERE symbol = p_symbol
        ORDER BY ABS(price_usd - p_price)
        LIMIT 1;
    END IF;

    RETURN v_risk;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- STEP 4: CREATE VIEWS FOR EASY ACCESS
-- ============================================

-- View for current risk status with zones
CREATE OR REPLACE VIEW v_risk_status AS
SELECT
    symbol,
    price_usd,
    fiat_risk,
    CASE
        WHEN fiat_risk < 0.3 THEN 'ACCUMULATION'
        WHEN fiat_risk < 0.7 THEN 'TRANSITION'
        ELSE 'DISTRIBUTION'
    END as risk_zone,
    CASE
        WHEN fiat_risk < 0.3 THEN 'green'
        WHEN fiat_risk < 0.7 THEN 'yellow'
        ELSE 'red'
    END as zone_color,
    last_updated
FROM cryptoverse_risk_data
ORDER BY symbol;

-- View for symbols with both FIAT and BTC risk
CREATE OR REPLACE VIEW v_dual_risk_symbols AS
SELECT DISTINCT
    f.symbol,
    r.price_usd as current_price,
    r.fiat_risk as current_fiat_risk,
    r.btc_risk as current_btc_risk,
    COUNT(DISTINCT f.fiat_risk) as fiat_levels,
    COUNT(DISTINCT b.btc_risk) as btc_levels
FROM cryptoverse_risk_grid f
LEFT JOIN cryptoverse_btc_risk_grid b ON f.symbol = b.symbol
LEFT JOIN cryptoverse_risk_data r ON f.symbol = r.symbol
WHERE b.symbol IS NOT NULL
GROUP BY f.symbol, r.price_usd, r.fiat_risk, r.btc_risk;

-- View for risk grid summary
CREATE OR REPLACE VIEW v_risk_grid_summary AS
SELECT
    symbol,
    'FIAT' as risk_type,
    COUNT(*) as data_points,
    MIN(fiat_risk) as min_risk,
    MAX(fiat_risk) as max_risk,
    MIN(price_usd) as min_price,
    MAX(price_usd) as max_price
FROM cryptoverse_risk_grid
GROUP BY symbol
UNION ALL
SELECT
    symbol,
    'BTC' as risk_type,
    COUNT(*) as data_points,
    MIN(btc_risk) as min_risk,
    MAX(btc_risk) as max_risk,
    MIN(price_btc) as min_price,
    MAX(price_btc) as max_price
FROM cryptoverse_btc_risk_grid
GROUP BY symbol
ORDER BY symbol, risk_type;

-- ============================================
-- STEP 5: CREATE API-READY FUNCTIONS
-- ============================================

-- Function to get complete risk profile for a symbol
CREATE OR REPLACE FUNCTION get_risk_profile(p_symbol VARCHAR)
RETURNS TABLE (
    symbol VARCHAR,
    current_price_usd DECIMAL,
    current_fiat_risk DECIMAL,
    current_btc_risk DECIMAL,
    risk_zone VARCHAR,
    has_btc_risk BOOLEAN,
    price_at_risk_25 DECIMAL,
    price_at_risk_50 DECIMAL,
    price_at_risk_75 DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        rd.symbol,
        rd.price_usd,
        rd.fiat_risk,
        rd.btc_risk,
        CASE
            WHEN rd.fiat_risk < 0.3 THEN 'ACCUMULATION'
            WHEN rd.fiat_risk < 0.7 THEN 'TRANSITION'
            ELSE 'DISTRIBUTION'
        END::VARCHAR,
        EXISTS(SELECT 1 FROM cryptoverse_btc_risk_grid WHERE cryptoverse_btc_risk_grid.symbol = p_symbol),
        get_price_at_risk(p_symbol, 0.25, 'fiat'),
        get_price_at_risk(p_symbol, 0.50, 'fiat'),
        get_price_at_risk(p_symbol, 0.75, 'fiat')
    FROM cryptoverse_risk_data rd
    WHERE rd.symbol = p_symbol;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- STEP 6: ENABLE ROW LEVEL SECURITY (OPTIONAL)
-- ============================================

-- If you want to control access to the data
ALTER TABLE cryptoverse_risk_grid ENABLE ROW LEVEL SECURITY;
ALTER TABLE cryptoverse_btc_risk_grid ENABLE ROW LEVEL SECURITY;
ALTER TABLE cryptoverse_risk_data ENABLE ROW LEVEL SECURITY;

-- Create policy for read access (adjust as needed)
CREATE POLICY "Allow public read access" ON cryptoverse_risk_grid
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access" ON cryptoverse_btc_risk_grid
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access" ON cryptoverse_risk_data
    FOR SELECT USING (true);

-- ============================================
-- STEP 7: VERIFY SETUP
-- ============================================

-- Check all tables exist
SELECT
    table_name,
    CASE
        WHEN table_name IN ('cryptoverse_risk_grid', 'cryptoverse_btc_risk_grid', 'cryptoverse_risk_data')
        THEN '✅ Ready'
        ELSE '❌ Missing'
    END as status
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'cryptoverse%'
ORDER BY table_name;

-- ============================================
-- FINAL MESSAGE
-- ============================================
SELECT
    '✅ Setup Complete! Now run the following files in order:' as message
UNION ALL
SELECT
    '1. insert_full_risk_grids.sql - Load FIAT risk data'
UNION ALL
SELECT
    '2. insert_btc_risk_grids.sql - Load BTC risk data'
UNION ALL
SELECT
    '3. Test with: SELECT * FROM v_risk_status;';