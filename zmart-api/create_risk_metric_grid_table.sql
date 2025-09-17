-- Create Risk Metric Grid Table in Supabase
-- This is the MAIN TABLE mapping prices to risk values
-- 41 price points per symbol (0.000 to 1.000 in 0.025 increments)

CREATE TABLE IF NOT EXISTS risk_metric_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price_point INTEGER NOT NULL CHECK (price_point >= 1 AND price_point <= 41),
    risk_value DECIMAL(5,4) NOT NULL CHECK (risk_value >= 0 AND risk_value <= 1),
    price_usd DECIMAL(20,8) NOT NULL,
    price_btc DECIMAL(20,8),  -- Optional BTC price
    risk_band VARCHAR(10) NOT NULL,  -- e.g., "0.0-0.1"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, price_point),
    UNIQUE(symbol, risk_value)
);

-- Create indexes for fast lookups
CREATE INDEX idx_risk_metric_grid_symbol ON risk_metric_grid(symbol);
CREATE INDEX idx_risk_metric_grid_price ON risk_metric_grid(symbol, price_usd);
CREATE INDEX idx_risk_metric_grid_risk ON risk_metric_grid(symbol, risk_value);

-- Insert SOL data (41 points)
-- Based on our analysis where $300 = risk ~0.575
INSERT INTO risk_metric_grid (symbol, price_point, risk_value, price_usd, risk_band) VALUES
-- Risk 0.000 to 0.100 (points 1-5)
('SOL', 1, 0.000, 10.00, '0.0-0.1'),
('SOL', 2, 0.025, 15.00, '0.0-0.1'),
('SOL', 3, 0.050, 20.00, '0.0-0.1'),
('SOL', 4, 0.075, 25.00, '0.0-0.1'),
('SOL', 5, 0.100, 30.00, '0.1-0.2'),
-- Risk 0.125 to 0.225 (points 6-10)
('SOL', 6, 0.125, 35.00, '0.1-0.2'),
('SOL', 7, 0.150, 40.00, '0.1-0.2'),
('SOL', 8, 0.175, 50.00, '0.1-0.2'),
('SOL', 9, 0.200, 60.00, '0.2-0.3'),
('SOL', 10, 0.225, 70.00, '0.2-0.3'),
-- Risk 0.250 to 0.350 (points 11-15)
('SOL', 11, 0.250, 80.00, '0.2-0.3'),
('SOL', 12, 0.275, 90.00, '0.2-0.3'),
('SOL', 13, 0.300, 100.00, '0.3-0.4'),
('SOL', 14, 0.325, 115.00, '0.3-0.4'),
('SOL', 15, 0.350, 130.00, '0.3-0.4'),
-- Risk 0.375 to 0.475 (points 16-20)
('SOL', 16, 0.375, 145.00, '0.3-0.4'),
('SOL', 17, 0.400, 160.00, '0.4-0.5'),
('SOL', 18, 0.425, 180.00, '0.4-0.5'),
('SOL', 19, 0.450, 200.00, '0.4-0.5'),
('SOL', 20, 0.475, 220.00, '0.4-0.5'),
-- Risk 0.500 to 0.600 (points 21-25) - Current range
('SOL', 21, 0.500, 235.00, '0.5-0.6'),  -- Current price ~$238
('SOL', 22, 0.525, 260.00, '0.5-0.6'),
('SOL', 23, 0.550, 280.00, '0.5-0.6'),
('SOL', 24, 0.575, 300.00, '0.5-0.6'),  -- $300 target
('SOL', 25, 0.600, 330.00, '0.6-0.7'),
-- Risk 0.625 to 0.725 (points 26-30)
('SOL', 26, 0.625, 360.00, '0.6-0.7'),
('SOL', 27, 0.650, 400.00, '0.6-0.7'),
('SOL', 28, 0.675, 440.00, '0.6-0.7'),
('SOL', 29, 0.700, 490.00, '0.7-0.8'),
('SOL', 30, 0.725, 540.00, '0.7-0.8'),
-- Risk 0.750 to 0.850 (points 31-35)
('SOL', 31, 0.750, 600.00, '0.7-0.8'),
('SOL', 32, 0.775, 670.00, '0.7-0.8'),
('SOL', 33, 0.800, 750.00, '0.8-0.9'),
('SOL', 34, 0.825, 850.00, '0.8-0.9'),
('SOL', 35, 0.850, 950.00, '0.8-0.9'),
-- Risk 0.875 to 1.000 (points 36-41)
('SOL', 36, 0.875, 1100.00, '0.8-0.9'),
('SOL', 37, 0.900, 1300.00, '0.9-1.0'),
('SOL', 38, 0.925, 1500.00, '0.9-1.0'),
('SOL', 39, 0.950, 1800.00, '0.9-1.0'),
('SOL', 40, 0.975, 2200.00, '0.9-1.0'),
('SOL', 41, 1.000, 3000.00, '0.9-1.0')
ON CONFLICT (symbol, price_point) DO NOTHING;

-- Verify the data
SELECT
    price_point,
    risk_value,
    price_usd,
    risk_band,
    CASE
        WHEN price_usd = 300 THEN '← $300 TARGET'
        WHEN price_usd BETWEEN 230 AND 240 THEN '← CURRENT'
        ELSE ''
    END as note
FROM risk_metric_grid
WHERE symbol = 'SOL'
ORDER BY price_point;