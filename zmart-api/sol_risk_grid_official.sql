-- SOL Risk Metric Grid - Official Data from IntoTheCryptoverse
-- Source: https://app.intothecryptoverse.com/assets/solana/risk
-- Last Updated: 2025-09-08

DROP TABLE IF EXISTS public.risk_metric_grid CASCADE;

CREATE TABLE public.risk_metric_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    risk_value DECIMAL(5,3) NOT NULL,
    price_usd DECIMAL(20,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, risk_value)
);

-- Create indexes for fast lookups
CREATE INDEX idx_rmg_symbol_risk ON risk_metric_grid(symbol, risk_value);
CREATE INDEX idx_rmg_symbol_price ON risk_metric_grid(symbol, price_usd);

-- Insert SOL Key Risk values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('SOL', 0.000, 20.61),
('SOL', 0.025, 23.18),
('SOL', 0.050, 26.08),
('SOL', 0.075, 29.34),
('SOL', 0.100, 33.02),
('SOL', 0.125, 37.14),
('SOL', 0.150, 41.79),
('SOL', 0.175, 47.03),
('SOL', 0.200, 52.94),
('SOL', 0.225, 59.63),
('SOL', 0.250, 67.15),
('SOL', 0.275, 75.68),
('SOL', 0.300, 83.21),
('SOL', 0.325, 88.28),
('SOL', 0.350, 93.68),
('SOL', 0.375, 99.37),
('SOL', 0.400, 105.44),
('SOL', 0.425, 111.91),
('SOL', 0.450, 118.76),
('SOL', 0.475, 126.01),
('SOL', 0.500, 133.81),
('SOL', 0.525, 142.06),
('SOL', 0.550, 150.87),
('SOL', 0.575, 160.23),
('SOL', 0.600, 170.21),
('SOL', 0.625, 180.80),
('SOL', 0.650, 192.11),
('SOL', 0.675, 204.54),
('SOL', 0.700, 228.84),
('SOL', 0.713, 243.85),  -- Current price/risk
('SOL', 0.725, 257.38),
('SOL', 0.750, 289.26),
('SOL', 0.775, 325.15),
('SOL', 0.800, 365.51),
('SOL', 0.825, 410.76),
('SOL', 0.850, 462.04),
('SOL', 0.875, 519.56),
('SOL', 0.900, 584.21),
('SOL', 0.925, 656.45),
('SOL', 0.950, 738.49),
('SOL', 0.975, 830.34),
('SOL', 1.000, 933.79)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- Additional Fiat Risk points for more granular data
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('SOL', 0.158, 43.44),
('SOL', 0.247, 66.27),
('SOL', 0.329, 89.10),
('SOL', 0.503, 134.76),
('SOL', 0.568, 157.59),
('SOL', 0.624, 180.42),
('SOL', 0.673, 203.25),
('SOL', 0.697, 226.08),
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
('SOL', 0.995, 910.96)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- Create BTC Risk table for SOL/BTC pair
CREATE TABLE IF NOT EXISTS public.btc_risk_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    risk_value DECIMAL(5,3) NOT NULL,
    price_btc DECIMAL(20,8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, risk_value)
);

-- Insert SOL BTC Risk values
INSERT INTO btc_risk_grid (symbol, risk_value, price_btc) VALUES
('SOL', 0.000, 0.000532),
('SOL', 0.025, 0.000583),
('SOL', 0.050, 0.000638),
('SOL', 0.075, 0.000699),
('SOL', 0.100, 0.000765),
('SOL', 0.125, 0.000838),
('SOL', 0.150, 0.000917),
('SOL', 0.175, 0.001004),
('SOL', 0.200, 0.001099),
('SOL', 0.225, 0.001203),
('SOL', 0.250, 0.001318),
('SOL', 0.275, 0.001443),
('SOL', 0.300, 0.001527),
('SOL', 0.325, 0.001598),
('SOL', 0.350, 0.001672),
('SOL', 0.375, 0.001750),
('SOL', 0.400, 0.001831),
('SOL', 0.425, 0.001916),
('SOL', 0.450, 0.002005),
('SOL', 0.472, 0.002103),  -- Current BTC risk
('SOL', 0.475, 0.002116),
('SOL', 0.500, 0.002317),
('SOL', 0.525, 0.002536),
('SOL', 0.550, 0.002777),
('SOL', 0.575, 0.003040),
('SOL', 0.600, 0.003328),
('SOL', 0.625, 0.003646),
('SOL', 0.650, 0.003991),
('SOL', 0.675, 0.004370),
('SOL', 0.700, 0.004785),
('SOL', 0.725, 0.005240),
('SOL', 0.750, 0.005739),
('SOL', 0.775, 0.006285),
('SOL', 0.800, 0.006881),
('SOL', 0.825, 0.007537),
('SOL', 0.850, 0.008254),
('SOL', 0.875, 0.009037),
('SOL', 0.900, 0.009901),
('SOL', 0.925, 0.010846),
('SOL', 0.950, 0.011877),
('SOL', 0.975, 0.013009),
('SOL', 1.000, 0.014248)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_btc = EXCLUDED.price_btc;

-- Query examples
SELECT '=== Current SOL Risk ===' as info;
SELECT * FROM risk_metric_grid
WHERE symbol = 'SOL' AND risk_value = 0.713;

SELECT '=== Find risk for $300 ===' as info;
SELECT * FROM risk_metric_grid
WHERE symbol = 'SOL'
ORDER BY ABS(price_usd - 300)
LIMIT 2;

SELECT '=== Find risk for current price $243.85 ===' as info;
SELECT * FROM risk_metric_grid
WHERE symbol = 'SOL'
ORDER BY ABS(price_usd - 243.85)
LIMIT 1;