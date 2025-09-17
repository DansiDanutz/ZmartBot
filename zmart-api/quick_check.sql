-- QUICK CHECK - RUN THIS TO SEE YOUR CURRENT STATUS
-- ============================================

-- 1. WHAT TABLES EXIST?
SELECT
    'TABLES' as category,
    COUNT(*) as count,
    string_agg(table_name, ', ') as items
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'cryptoverse%';

-- 2. HOW MUCH DATA IS LOADED?
SELECT
    'DATA CHECK' as info,
    (SELECT COUNT(*) FROM cryptoverse_risk_grid) as fiat_grid_rows,
    (SELECT COUNT(DISTINCT symbol) FROM cryptoverse_risk_grid) as fiat_symbols,
    (SELECT COUNT(*) FROM cryptoverse_btc_risk_grid) as btc_grid_rows,
    (SELECT COUNT(DISTINCT symbol) FROM cryptoverse_btc_risk_grid) as btc_symbols,
    (SELECT COUNT(*) FROM cryptoverse_risk_data) as current_risk_rows;

-- 3. SAMPLE DATA FROM FIAT RISK GRID
SELECT
    'FIAT RISK SAMPLE (BTC)' as info,
    symbol,
    fiat_risk,
    price_usd
FROM cryptoverse_risk_grid
WHERE symbol = 'BTC'
AND fiat_risk IN (0.000, 0.250, 0.500, 0.750, 1.000)
ORDER BY fiat_risk;

-- 4. SAMPLE DATA FROM BTC RISK GRID
SELECT
    'BTC RISK SAMPLE (ETH)' as info,
    symbol,
    btc_risk,
    price_btc
FROM cryptoverse_btc_risk_grid
WHERE symbol = 'ETH'
AND btc_risk IN (0.000, 0.250, 0.500, 0.750, 1.000)
ORDER BY btc_risk;

-- 5. CURRENT RISK STATUS
SELECT
    'CURRENT RISK' as info,
    symbol,
    price_usd,
    fiat_risk,
    CASE
        WHEN fiat_risk < 0.3 THEN '🟢 ACCUMULATION'
        WHEN fiat_risk < 0.7 THEN '🟡 TRANSITION'
        ELSE '🔴 DISTRIBUTION'
    END as zone
FROM cryptoverse_risk_data
WHERE symbol IN ('BTC', 'ETH', 'SOL')
ORDER BY symbol;

-- 6. TEST A FUNCTION
SELECT
    'FUNCTION TEST' as info,
    get_price_at_risk('BTC', 0.5, 'fiat') as btc_price_at_50_risk,
    get_price_at_risk('ETH', 0.5, 'fiat') as eth_price_at_50_risk;