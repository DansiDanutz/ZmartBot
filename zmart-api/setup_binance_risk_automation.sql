-- AUTOMATED BINANCE RISK UPDATES IN SUPABASE
-- ============================================
-- Uses pg_cron to fetch Binance prices and update risk values

-- STEP 1: Create function to fetch Binance price (using HTTP extension)
-- First enable the HTTP extension
CREATE EXTENSION IF NOT EXISTS http;

-- STEP 2: Function to get Binance price for a symbol
CREATE OR REPLACE FUNCTION get_binance_price(p_symbol VARCHAR)
RETURNS DECIMAL AS $$
DECLARE
    binance_symbol VARCHAR;
    response_json JSONB;
    price DECIMAL;
BEGIN
    -- Map our symbols to Binance format
    binance_symbol := CASE p_symbol
        WHEN 'BTC' THEN 'BTCUSDT'
        WHEN 'ETH' THEN 'ETHUSDT'
        WHEN 'SOL' THEN 'SOLUSDT'
        WHEN 'BNB' THEN 'BNBUSDT'
        WHEN 'XRP' THEN 'XRPUSDT'
        WHEN 'ADA' THEN 'ADAUSDT'
        WHEN 'AVAX' THEN 'AVAXUSDT'
        WHEN 'DOGE' THEN 'DOGEUSDT'
        WHEN 'DOT' THEN 'DOTUSDT'
        WHEN 'LINK' THEN 'LINKUSDT'
        WHEN 'LTC' THEN 'LTCUSDT'
        WHEN 'ATOM' THEN 'ATOMUSDT'
        WHEN 'XTZ' THEN 'XTZUSDT'
        WHEN 'AAVE' THEN 'AAVEUSDT'
        WHEN 'MKR' THEN 'MKRUSDT'
        WHEN 'XMR' THEN 'XMRUSDT'
        WHEN 'XLM' THEN 'XLMUSDT'
        WHEN 'SUI' THEN 'SUIUSDT'
        WHEN 'HBAR' THEN 'HBARUSDT'
        WHEN 'RENDER' THEN 'RENDERUSDT'
        WHEN 'TRX' THEN 'TRXUSDT'
        WHEN 'VET' THEN 'VETUSDT'
        WHEN 'ALGO' THEN 'ALGOUSDT'
        WHEN 'SHIB' THEN 'SHIBUSDT'
        WHEN 'TON' THEN 'TONUSDT'
        ELSE NULL
    END;

    IF binance_symbol IS NULL THEN
        RETURN NULL;
    END IF;

    -- Make HTTP request to Binance API
    SELECT content::jsonb INTO response_json
    FROM http_get('https://api.binance.com/api/v3/ticker/price?symbol=' || binance_symbol);

    -- Extract price
    price := (response_json->>'price')::DECIMAL;

    RETURN price;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- STEP 3: Function to update all risk values from Binance
CREATE OR REPLACE FUNCTION update_risk_from_binance()
RETURNS TABLE(
    symbol VARCHAR,
    price DECIMAL,
    risk_value DECIMAL,
    risk_band VARCHAR,
    signal TEXT
) AS $$
DECLARE
    r RECORD;
    current_price DECIMAL;
    current_risk DECIMAL;
    current_band VARCHAR;
    coefficient DECIMAL;
BEGIN
    -- Process each symbol
    FOR r IN SELECT DISTINCT crd.symbol
             FROM cryptoverse_risk_data crd
    LOOP
        -- Get current Binance price
        current_price := get_binance_price(r.symbol);

        IF current_price IS NOT NULL THEN
            -- Calculate risk from price
            current_risk := get_risk_at_price(r.symbol, current_price, 'fiat');

            -- Get risk band
            current_band := get_current_risk_band(current_risk);

            -- Update risk data
            UPDATE cryptoverse_risk_data
            SET
                price_usd = current_price,
                fiat_risk = current_risk,
                last_updated = NOW()
            WHERE cryptoverse_risk_data.symbol = r.symbol;

            -- Update time bands
            UPDATE cryptoverse_risk_time_bands_v2
            SET
                current_risk = current_risk,
                current_risk_band = current_band,
                last_risk_update = NOW()
            WHERE cryptoverse_risk_time_bands_v2.symbol = r.symbol;

            -- Get coefficient
            SELECT
                CASE current_band
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
                END INTO coefficient
            FROM cryptoverse_risk_time_bands_v2
            WHERE cryptoverse_risk_time_bands_v2.symbol = r.symbol;

            -- Return result
            RETURN QUERY
            SELECT
                r.symbol,
                current_price,
                current_risk,
                current_band,
                CASE
                    WHEN current_risk < 0.3 AND coefficient >= 1.5 THEN '🔥 STRONG BUY'
                    WHEN current_risk > 0.7 AND coefficient >= 1.3 THEN '📉 SELL'
                    WHEN current_risk < 0.3 THEN '💰 BUY'
                    WHEN current_risk > 0.7 THEN '💸 TAKE PROFIT'
                    ELSE '⏸️ HOLD'
                END AS signal;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- STEP 4: Schedule hourly updates (more frequent than daily)
SELECT cron.schedule(
    'hourly-binance-risk-update',
    '0 * * * *',  -- Every hour
    $$SELECT update_risk_from_binance();$$
);

-- STEP 5: View for current risk status
CREATE OR REPLACE VIEW v_current_risk_status AS
SELECT
    crd.symbol,
    crd.price_usd as current_price,
    crd.fiat_risk as current_risk,
    get_current_risk_band(crd.fiat_risk) as risk_band,
    rtb.coef_0_10, rtb.coef_10_20, rtb.coef_20_30, rtb.coef_30_40, rtb.coef_40_50,
    rtb.coef_50_60, rtb.coef_60_70, rtb.coef_70_80, rtb.coef_80_90, rtb.coef_90_100,
    CASE get_current_risk_band(crd.fiat_risk)
        WHEN '0.0-0.1' THEN rtb.coef_0_10
        WHEN '0.1-0.2' THEN rtb.coef_10_20
        WHEN '0.2-0.3' THEN rtb.coef_20_30
        WHEN '0.3-0.4' THEN rtb.coef_30_40
        WHEN '0.4-0.5' THEN rtb.coef_40_50
        WHEN '0.5-0.6' THEN rtb.coef_50_60
        WHEN '0.6-0.7' THEN rtb.coef_60_70
        WHEN '0.7-0.8' THEN rtb.coef_70_80
        WHEN '0.8-0.9' THEN rtb.coef_80_90
        WHEN '0.9-1.0' THEN rtb.coef_90_100
    END as current_coefficient,
    crd.last_updated
FROM cryptoverse_risk_data crd
LEFT JOIN cryptoverse_risk_time_bands_v2 rtb ON crd.symbol = rtb.symbol
ORDER BY crd.symbol;

-- TEST: Update risk values now
SELECT * FROM update_risk_from_binance() LIMIT 5;

-- VIEW: Current status
SELECT
    symbol,
    current_price,
    current_risk,
    risk_band,
    current_coefficient,
    CASE
        WHEN current_risk < 0.3 AND current_coefficient >= 1.5 THEN '🔥 STRONG BUY'
        WHEN current_risk > 0.7 AND current_coefficient >= 1.3 THEN '📉 SELL'
        WHEN current_risk < 0.3 THEN '💰 BUY'
        WHEN current_risk > 0.7 THEN '💸 PROFIT'
        ELSE '⏸️ HOLD'
    END as signal
FROM v_current_risk_status
WHERE symbol IN ('BTC', 'ETH', 'SOL', 'ADA', 'DOT')
ORDER BY current_risk DESC;