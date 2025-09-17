-- Insert missing symbols into cryptoverse_risk_data table
-- Date: 2025-09-16
-- Source: IntoTheCryptoverse (https://app.intothecryptoverse.com)

-- First, insert the 4 new symbols
INSERT INTO cryptoverse_risk_data (symbol, price_usd, price_btc, fiat_risk, btc_risk, btc_reference_price, data_source, last_updated)
VALUES
    -- SUI
    ('SUI', 3.58, 3.58/115844.88, 0.390, NULL, 115844.88, 'IntoTheCryptoverse', '2025-09-15'),
    -- HBAR
    ('HBAR', 0.235, 0.235/115844.88, 0.521, NULL, 115844.88, 'IntoTheCryptoverse', '2025-09-15'),
    -- RENDER
    ('RENDER', 3.82, 3.82/115844.88, 0.363, NULL, 115844.88, 'IntoTheCryptoverse', '2025-09-15'),
    -- TON
    ('TON', 3.17, 3.17/115844.88, 0.234, NULL, 115844.88, 'IntoTheCryptoverse', '2025-09-15')
ON CONFLICT (symbol) DO UPDATE
SET
    price_usd = EXCLUDED.price_usd,
    price_btc = EXCLUDED.price_btc,
    fiat_risk = EXCLUDED.fiat_risk,
    btc_risk = EXCLUDED.btc_risk,
    last_updated = EXCLUDED.last_updated;

-- Update the 3 existing symbols with latest data
UPDATE cryptoverse_risk_data
SET
    price_usd = CASE symbol
        WHEN 'ALGO' THEN 0.242
        WHEN 'VET' THEN 0.0255
        WHEN 'XLM' THEN 0.0926
    END,
    price_btc = CASE symbol
        WHEN 'ALGO' THEN 0.242/115844.88
        WHEN 'VET' THEN 0.0255/115844.88
        WHEN 'XLM' THEN 0.0926/115844.88
    END,
    fiat_risk = CASE symbol
        WHEN 'ALGO' THEN 0.299
        WHEN 'VET' THEN 0.303
        WHEN 'XLM' THEN 0.120
    END,
    last_updated = '2025-09-16'
WHERE symbol IN ('ALGO', 'VET', 'XLM');

-- Verify the results
SELECT
    symbol,
    ROUND(price_usd::numeric, 4) as price_usd,
    ROUND(fiat_risk::numeric, 3) as fiat_risk,
    CASE
        WHEN fiat_risk < 0.3 THEN 'ACCUMULATION'
        WHEN fiat_risk < 0.7 THEN 'TRANSITION'
        ELSE 'DISTRIBUTION'
    END as risk_zone,
    last_updated
FROM cryptoverse_risk_data
ORDER BY symbol;

-- Summary check - should show 25 symbols
SELECT
    COUNT(DISTINCT symbol) as total_symbols,
    COUNT(CASE WHEN fiat_risk < 0.3 THEN 1 END) as accumulation_zone,
    COUNT(CASE WHEN fiat_risk >= 0.3 AND fiat_risk < 0.7 THEN 1 END) as transition_zone,
    COUNT(CASE WHEN fiat_risk >= 0.7 THEN 1 END) as distribution_zone
FROM cryptoverse_risk_data;