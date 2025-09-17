-- Universal Risk Metric Grid Table
-- ONE table for ALL symbols - like the Google Sheet
-- Source: IntoTheCryptoverse
-- Last Updated: 2025-09-08

DROP TABLE IF EXISTS public.risk_metric_grid CASCADE;

CREATE TABLE public.risk_metric_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    risk_value DECIMAL(5,3) NOT NULL,
    price_usd DECIMAL(20,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, risk_value)
);

-- Create indexes for fast lookups
CREATE INDEX idx_rmg_symbol ON risk_metric_grid(symbol);
CREATE INDEX idx_rmg_symbol_risk ON risk_metric_grid(symbol, risk_value);
CREATE INDEX idx_rmg_symbol_price ON risk_metric_grid(symbol, price_usd);

-- SOL Data from IntoTheCryptoverse
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
-- SOL Fiat Risk Values
('SOL', 0.000, 20.61),
('SOL', 0.158, 43.44),
('SOL', 0.247, 66.27),
('SOL', 0.329, 89.10),
('SOL', 0.425, 111.93),
('SOL', 0.503, 134.76),
('SOL', 0.568, 157.59),
('SOL', 0.624, 180.42),
('SOL', 0.673, 203.25),
('SOL', 0.697, 226.08),
('SOL', 0.713, 243.85),
('SOL', 0.718, 248.91),
('SOL', 0.737, 271.74),
('SOL', 0.754, 294.57),
('SOL', 0.770, 317.40),
('SOL', 0.785, 340.23),
('SOL', 0.799, 363.05),
('SOL', 0.812, 385.88),
('SOL', 0.824, 408.71),
('SOL', 0.835, 431.54),
('SOL', 0.846, 454.37),
('SOL', 0.857, 477.20),
('SOL', 0.867, 500.03),
('SOL', 0.876, 522.86),
('SOL', 0.886, 545.69),
('SOL', 0.894, 568.52),
('SOL', 0.903, 591.35),
('SOL', 0.911, 614.18),
('SOL', 0.919, 637.01),
('SOL', 0.926, 659.84),
('SOL', 0.933, 682.67),
('SOL', 0.940, 705.50),
('SOL', 0.947, 728.32),
('SOL', 0.954, 751.15),
('SOL', 0.960, 773.98),
('SOL', 0.966, 796.81),
('SOL', 0.972, 819.64),
('SOL', 0.978, 842.47),
('SOL', 0.984, 865.30),
('SOL', 0.989, 888.13),
('SOL', 0.995, 910.96),
('SOL', 1.000, 933.79);

-- BTC Data (example - you'll need to get from browserMCP)
-- INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
-- ('BTC', 0.000, 30000),
-- ('BTC', 0.100, 50000),
-- ... etc

-- ETH Data (example - you'll need to get from browserMCP)
-- INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
-- ('ETH', 0.000, 1500),
-- ('ETH', 0.100, 2500),
-- ... etc

-- Function to get risk for any price with interpolation
CREATE OR REPLACE FUNCTION get_risk_for_price(
    p_symbol VARCHAR,
    p_price DECIMAL
) RETURNS TABLE (
    symbol VARCHAR,
    target_price DECIMAL,
    calculated_risk DECIMAL,
    lower_price DECIMAL,
    lower_risk DECIMAL,
    upper_price DECIMAL,
    upper_risk DECIMAL
) AS $$
DECLARE
    v_lower RECORD;
    v_upper RECORD;
    v_risk DECIMAL;
BEGIN
    -- Get lower bound
    SELECT risk_value, price_usd
    INTO v_lower
    FROM risk_metric_grid
    WHERE risk_metric_grid.symbol = p_symbol
      AND price_usd <= p_price
    ORDER BY price_usd DESC
    LIMIT 1;

    -- Get upper bound
    SELECT risk_value, price_usd
    INTO v_upper
    FROM risk_metric_grid
    WHERE risk_metric_grid.symbol = p_symbol
      AND price_usd >= p_price
    ORDER BY price_usd ASC
    LIMIT 1;

    -- Calculate interpolated risk
    IF v_lower.price_usd IS NOT NULL AND v_upper.price_usd IS NOT NULL THEN
        IF v_lower.price_usd = v_upper.price_usd THEN
            -- Exact match
            v_risk := v_lower.risk_value;
        ELSE
            -- Linear interpolation
            v_risk := v_lower.risk_value +
                     (v_upper.risk_value - v_lower.risk_value) *
                     ((p_price - v_lower.price_usd) / (v_upper.price_usd - v_lower.price_usd));
        END IF;

        RETURN QUERY SELECT
            p_symbol,
            p_price,
            v_risk,
            v_lower.price_usd,
            v_lower.risk_value,
            v_upper.price_usd,
            v_upper.risk_value;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to get price for any risk value with interpolation
CREATE OR REPLACE FUNCTION get_price_for_risk(
    p_symbol VARCHAR,
    p_risk DECIMAL
) RETURNS TABLE (
    symbol VARCHAR,
    target_risk DECIMAL,
    calculated_price DECIMAL,
    lower_risk DECIMAL,
    lower_price DECIMAL,
    upper_risk DECIMAL,
    upper_price DECIMAL
) AS $$
DECLARE
    v_lower RECORD;
    v_upper RECORD;
    v_price DECIMAL;
BEGIN
    -- Get lower bound
    SELECT risk_value, price_usd
    INTO v_lower
    FROM risk_metric_grid
    WHERE risk_metric_grid.symbol = p_symbol
      AND risk_value <= p_risk
    ORDER BY risk_value DESC
    LIMIT 1;

    -- Get upper bound
    SELECT risk_value, price_usd
    INTO v_upper
    FROM risk_metric_grid
    WHERE risk_metric_grid.symbol = p_symbol
      AND risk_value >= p_risk
    ORDER BY risk_value ASC
    LIMIT 1;

    -- Calculate interpolated price
    IF v_lower.risk_value IS NOT NULL AND v_upper.risk_value IS NOT NULL THEN
        IF v_lower.risk_value = v_upper.risk_value THEN
            -- Exact match
            v_price := v_lower.price_usd;
        ELSE
            -- Linear interpolation
            v_price := v_lower.price_usd +
                      (v_upper.price_usd - v_lower.price_usd) *
                      ((p_risk - v_lower.risk_value) / (v_upper.risk_value - v_lower.risk_value));
        END IF;

        RETURN QUERY SELECT
            p_symbol,
            p_risk,
            v_price,
            v_lower.risk_value,
            v_lower.price_usd,
            v_upper.risk_value,
            v_upper.price_usd;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Test queries
SELECT '=== SOL at $300 ===' as test;
SELECT * FROM get_risk_for_price('SOL', 300);

SELECT '=== SOL at current price $243.85 ===' as test;
SELECT * FROM get_risk_for_price('SOL', 243.85);

SELECT '=== What price for SOL at 0.500 risk? ===' as test;
SELECT * FROM get_price_for_risk('SOL', 0.500);

SELECT '=== What price for SOL at 0.750 risk? ===' as test;
SELECT * FROM get_price_for_risk('SOL', 0.750);

-- View all SOL data
SELECT '=== Complete SOL Risk Grid ===' as test;
SELECT
    symbol,
    risk_value,
    price_usd,
    CASE
        WHEN price_usd = 243.85 THEN '← Current'
        WHEN price_usd BETWEEN 290 AND 310 THEN '← $300 range'
        ELSE ''
    END as note
FROM risk_metric_grid
WHERE symbol = 'SOL'
ORDER BY risk_value;