-- Trading Coefficients for SOL
-- Based on inverse rarity: Most common = 1.00, Rarest = 1.60

-- Create table if not exists
CREATE TABLE IF NOT EXISTS trading_coefficients (
    symbol VARCHAR(10) NOT NULL,
    risk_band VARCHAR(10) NOT NULL,
    days_in_band INTEGER,
    percentage DECIMAL(5,2),
    coefficient DECIMAL(4,3),
    rarity_rank INTEGER,
    PRIMARY KEY (symbol, risk_band)
);

-- Insert coefficients for SOL

INSERT INTO trading_coefficients (symbol, risk_band, days_in_band, percentage, coefficient, rarity_rank)
VALUES ('SOL', '0.0-0.1', 60, 2.99, 1.57, 2)
ON CONFLICT (symbol, risk_band) DO UPDATE SET
    days_in_band = EXCLUDED.days_in_band,
    percentage = EXCLUDED.percentage,
    coefficient = EXCLUDED.coefficient,
    rarity_rank = EXCLUDED.rarity_rank;

INSERT INTO trading_coefficients (symbol, risk_band, days_in_band, percentage, coefficient, rarity_rank)
VALUES ('SOL', '0.1-0.2', 200, 9.96, 1.361, 5)
ON CONFLICT (symbol, risk_band) DO UPDATE SET
    days_in_band = EXCLUDED.days_in_band,
    percentage = EXCLUDED.percentage,
    coefficient = EXCLUDED.coefficient,
    rarity_rank = EXCLUDED.rarity_rank;

INSERT INTO trading_coefficients (symbol, risk_band, days_in_band, percentage, coefficient, rarity_rank)
VALUES ('SOL', '0.2-0.3', 261, 13.0, 1.269, 6)
ON CONFLICT (symbol, risk_band) DO UPDATE SET
    days_in_band = EXCLUDED.days_in_band,
    percentage = EXCLUDED.percentage,
    coefficient = EXCLUDED.coefficient,
    rarity_rank = EXCLUDED.rarity_rank;

INSERT INTO trading_coefficients (symbol, risk_band, days_in_band, percentage, coefficient, rarity_rank)
VALUES ('SOL', '0.3-0.4', 321, 15.99, 1.18, 8)
ON CONFLICT (symbol, risk_band) DO UPDATE SET
    days_in_band = EXCLUDED.days_in_band,
    percentage = EXCLUDED.percentage,
    coefficient = EXCLUDED.coefficient,
    rarity_rank = EXCLUDED.rarity_rank;

INSERT INTO trading_coefficients (symbol, risk_band, days_in_band, percentage, coefficient, rarity_rank)
VALUES ('SOL', '0.4-0.5', 401, 19.97, 1.06, 9)
ON CONFLICT (symbol, risk_band) DO UPDATE SET
    days_in_band = EXCLUDED.days_in_band,
    percentage = EXCLUDED.percentage,
    coefficient = EXCLUDED.coefficient,
    rarity_rank = EXCLUDED.rarity_rank;

INSERT INTO trading_coefficients (symbol, risk_band, days_in_band, percentage, coefficient, rarity_rank)
VALUES ('SOL', '0.5-0.6', 441, 21.96, 1.0, 10)
ON CONFLICT (symbol, risk_band) DO UPDATE SET
    days_in_band = EXCLUDED.days_in_band,
    percentage = EXCLUDED.percentage,
    coefficient = EXCLUDED.coefficient,
    rarity_rank = EXCLUDED.rarity_rank;

INSERT INTO trading_coefficients (symbol, risk_band, days_in_band, percentage, coefficient, rarity_rank)
VALUES ('SOL', '0.6-0.7', 261, 13.0, 1.269, 6)
ON CONFLICT (symbol, risk_band) DO UPDATE SET
    days_in_band = EXCLUDED.days_in_band,
    percentage = EXCLUDED.percentage,
    coefficient = EXCLUDED.coefficient,
    rarity_rank = EXCLUDED.rarity_rank;

INSERT INTO trading_coefficients (symbol, risk_band, days_in_band, percentage, coefficient, rarity_rank)
VALUES ('SOL', '0.7-0.8', 140, 6.97, 1.45, 4)
ON CONFLICT (symbol, risk_band) DO UPDATE SET
    days_in_band = EXCLUDED.days_in_band,
    percentage = EXCLUDED.percentage,
    coefficient = EXCLUDED.coefficient,
    rarity_rank = EXCLUDED.rarity_rank;

INSERT INTO trading_coefficients (symbol, risk_band, days_in_band, percentage, coefficient, rarity_rank)
VALUES ('SOL', '0.8-0.9', 80, 3.98, 1.54, 3)
ON CONFLICT (symbol, risk_band) DO UPDATE SET
    days_in_band = EXCLUDED.days_in_band,
    percentage = EXCLUDED.percentage,
    coefficient = EXCLUDED.coefficient,
    rarity_rank = EXCLUDED.rarity_rank;

INSERT INTO trading_coefficients (symbol, risk_band, days_in_band, percentage, coefficient, rarity_rank)
VALUES ('SOL', '0.9-1.0', 40, 1.99, 1.6, 1)
ON CONFLICT (symbol, risk_band) DO UPDATE SET
    days_in_band = EXCLUDED.days_in_band,
    percentage = EXCLUDED.percentage,
    coefficient = EXCLUDED.coefficient,
    rarity_rank = EXCLUDED.rarity_rank;

-- Function to get trading signal
CREATE OR REPLACE FUNCTION get_trading_signal(p_symbol VARCHAR, p_current_risk DECIMAL)
RETURNS TABLE(
    symbol VARCHAR,
    current_risk DECIMAL,
    risk_band VARCHAR,
    coefficient DECIMAL,
    adjusted_risk DECIMAL,
    trading_signal TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p_symbol as symbol,
        p_current_risk as current_risk,
        tc.risk_band,
        tc.coefficient,
        p_current_risk * tc.coefficient as adjusted_risk,
        CASE
            WHEN tc.coefficient >= 1.5 AND p_current_risk < 0.2 THEN '🔥 STRONG BUY'
            WHEN tc.coefficient >= 1.5 AND p_current_risk > 0.8 THEN '⚠️ STRONG SELL'
            WHEN tc.coefficient >= 1.3 AND p_current_risk < 0.3 THEN '✅ BUY'
            WHEN tc.coefficient >= 1.3 AND p_current_risk > 0.7 THEN '📉 SELL'
            WHEN p_current_risk < 0.3 THEN '💰 ACCUMULATE'
            WHEN p_current_risk > 0.7 THEN '💸 TAKE PROFIT'
            ELSE '⏸️ HOLD'
        END as trading_signal
    FROM trading_coefficients tc
    WHERE tc.symbol = p_symbol
    AND p_current_risk >= CAST(SPLIT_PART(tc.risk_band, '-', 1) AS DECIMAL)
    AND p_current_risk < CAST(SPLIT_PART(tc.risk_band, '-', 2) AS DECIMAL);
END;
$$ LANGUAGE plpgsql;

-- Test with current SOL risk
SELECT * FROM get_trading_signal('SOL', 0.715);
