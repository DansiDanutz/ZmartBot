-- TEST AND LOAD SCRIPT
-- Run this step by step to diagnose and fix the issue

-- STEP 1: Check if tables exist (should return 3 rows)
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('cryptoverse_risk_grid', 'cryptoverse_btc_risk_grid', 'cryptoverse_risk_data');

-- STEP 2: Check if tables are empty
SELECT
    'cryptoverse_risk_grid' as table_name,
    COUNT(*) as row_count
FROM cryptoverse_risk_grid
UNION ALL
SELECT
    'cryptoverse_btc_risk_grid' as table_name,
    COUNT(*) as row_count
FROM cryptoverse_btc_risk_grid
UNION ALL
SELECT
    'cryptoverse_risk_data' as table_name,
    COUNT(*) as row_count
FROM cryptoverse_risk_data;

-- STEP 3: If tables are empty, test insert with sample data
-- Test FIAT risk grid with just BTC data
INSERT INTO cryptoverse_risk_grid (symbol, price_usd, fiat_risk) VALUES
    ('BTC', 30000.00, 0.000),
    ('BTC', 31352.00, 0.025),
    ('BTC', 32704.00, 0.050),
    ('BTC', 34055.00, 0.075),
    ('BTC', 35567.00, 0.100),
    ('BTC', 102054.00, 0.500),
    ('BTC', 184029.00, 0.750),
    ('BTC', 299720.00, 1.000)
ON CONFLICT (symbol, fiat_risk) DO UPDATE
SET price_usd = EXCLUDED.price_usd;

-- STEP 4: Test if function works now
SELECT
    get_price_at_risk('BTC', 0.5, 'fiat') as btc_at_50_percent,
    get_price_at_risk('BTC', 0.0, 'fiat') as btc_at_0_percent,
    get_price_at_risk('BTC', 1.0, 'fiat') as btc_at_100_percent;

-- STEP 5: Check what we have
SELECT * FROM cryptoverse_risk_grid WHERE symbol = 'BTC' ORDER BY fiat_risk;

-- If everything works above, then you're ready to load the full data!
-- Next: Run insert_full_risk_grids.sql and insert_btc_risk_grids.sql