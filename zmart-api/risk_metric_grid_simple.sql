-- Risk Metric Grid Table - Simple Format like Google Sheets
-- Risk values on left, prices on right - easy to search!

DROP TABLE IF EXISTS public.risk_metric_grid CASCADE;

CREATE TABLE public.risk_metric_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    risk_value DECIMAL(5,3) NOT NULL,  -- 0.000 to 1.000
    price_usd DECIMAL(20,2) NOT NULL,   -- Price in USD
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, risk_value)
);

-- Index for fast lookups
CREATE INDEX idx_rmg_symbol_risk ON risk_metric_grid(symbol, risk_value);
CREATE INDEX idx_rmg_symbol_price ON risk_metric_grid(symbol, price_usd);

-- Insert SOL data (42 rows from your data)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('SOL', 0.000, 20.61),
('SOL', 0.024, 22.89),
('SOL', 0.048, 25.42),
('SOL', 0.071, 28.24),
('SOL', 0.095, 31.36),
('SOL', 0.119, 34.83),
('SOL', 0.143, 38.69),
('SOL', 0.167, 42.97),
('SOL', 0.190, 47.72),
('SOL', 0.214, 53.00),
('SOL', 0.238, 58.86),
('SOL', 0.262, 65.38),
('SOL', 0.286, 72.62),
('SOL', 0.310, 80.67),
('SOL', 0.333, 89.60),
('SOL', 0.357, 99.52),
('SOL', 0.381, 110.54),
('SOL', 0.405, 122.78),
('SOL', 0.429, 136.37),
('SOL', 0.452, 151.46),
('SOL', 0.476, 168.23),
('SOL', 0.500, 186.85),
('SOL', 0.524, 207.53),
('SOL', 0.548, 230.52),
('SOL', 0.571, 256.08),
('SOL', 0.595, 284.49),
('SOL', 0.619, 316.07),
('SOL', 0.643, 351.16),
('SOL', 0.667, 390.15),
('SOL', 0.690, 433.45),
('SOL', 0.713, 244.11),  -- From your data: $244.11 = 0.713 risk
('SOL', 0.714, 481.45),
('SOL', 0.738, 534.37),
('SOL', 0.762, 593.61),
('SOL', 0.786, 659.41),
('SOL', 0.810, 732.49),
('SOL', 0.833, 813.71),
('SOL', 0.857, 903.95),
('SOL', 0.881, 1004.25),
('SOL', 0.905, 1115.70),
('SOL', 0.929, 1239.52),
('SOL', 0.952, 1377.02),
('SOL', 1.000, 1529.76)  -- Corrected value
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- Simple query examples:
SELECT '=== Risk Metric Grid for SOL ===' as info;
SELECT
    risk_value,
    price_usd,
    CASE
        WHEN price_usd BETWEEN 230 AND 250 THEN '← Current Price Range'
        WHEN price_usd = 300 THEN '← Target'
        ELSE ''
    END as note
FROM risk_metric_grid
WHERE symbol = 'SOL'
ORDER BY risk_value;

-- Find risk for price $300 (look for closest)
SELECT '=== Finding risk for $300 ===' as info;
SELECT
    risk_value,
    price_usd,
    ABS(price_usd - 300) as price_diff
FROM risk_metric_grid
WHERE symbol = 'SOL'
ORDER BY ABS(price_usd - 300)
LIMIT 2;

-- Find risk for current price $238.88
SELECT '=== Finding risk for current price $238.88 ===' as info;
SELECT
    risk_value,
    price_usd,
    ABS(price_usd - 238.88) as price_diff
FROM risk_metric_grid
WHERE symbol = 'SOL'
ORDER BY ABS(price_usd - 238.88)
LIMIT 2;