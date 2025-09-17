-- Complete Risk Metric Grid for All Symbols
-- Source: IntoTheCryptoverse
-- Last Updated: 2025-09-14

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

-- ==================== BTC DATA ====================
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
-- BTC Fiat Risk Values
('BTC', 0.000, 30000.00),
('BTC', 0.092, 35000.00),
('BTC', 0.159, 40000.00),
('BTC', 0.206, 45000.00),
('BTC', 0.245, 50000.00),
('BTC', 0.279, 55000.00),
('BTC', 0.309, 60000.00),
('BTC', 0.337, 65000.00),
('BTC', 0.363, 70000.00),
('BTC', 0.387, 75000.00),
('BTC', 0.410, 80000.00),
('BTC', 0.432, 85000.00),
('BTC', 0.453, 90000.00),
('BTC', 0.473, 95000.00),
('BTC', 0.492, 100000.00),
('BTC', 0.511, 105000.00),
('BTC', 0.529, 110000.00),
('BTC', 0.547, 115000.00),
('BTC', 0.550, 116024.00),  -- Current
('BTC', 0.563, 120000.00),
('BTC', 0.580, 125000.00),
('BTC', 0.596, 130000.00),
('BTC', 0.612, 135000.00),
('BTC', 0.627, 140000.00),
('BTC', 0.642, 145000.00),
('BTC', 0.657, 150000.00),
('BTC', 0.671, 155000.00),
('BTC', 0.686, 160000.00),
('BTC', 0.699, 165000.00),
('BTC', 0.713, 170000.00),
('BTC', 0.726, 175000.00),
('BTC', 0.740, 180000.00),
('BTC', 0.753, 185000.00),
('BTC', 0.765, 190000.00),
('BTC', 0.778, 195000.00),
('BTC', 0.790, 200000.00),
('BTC', 0.802, 205000.00),
('BTC', 0.814, 210000.00),
('BTC', 0.826, 215000.00),
('BTC', 0.838, 220000.00),
('BTC', 0.850, 225000.00),
('BTC', 0.861, 230000.00),
('BTC', 0.872, 235000.00),
('BTC', 0.884, 240000.00),
('BTC', 0.895, 245000.00),
('BTC', 0.905, 250000.00),
('BTC', 0.916, 255000.00),
('BTC', 0.927, 260000.00),
('BTC', 0.937, 265000.00),
('BTC', 1.000, 300000.00);

-- BTC Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('BTC', 0.025, 31352.00),
('BTC', 0.050, 32704.00),
('BTC', 0.075, 34055.00),
('BTC', 0.100, 35567.00),
('BTC', 0.125, 37452.00),
('BTC', 0.150, 39336.00),
('BTC', 0.175, 41718.00),
('BTC', 0.200, 44371.00),
('BTC', 0.225, 47457.00),
('BTC', 0.250, 50778.00),
('BTC', 0.275, 54471.00),
('BTC', 0.300, 58519.00),
('BTC', 0.325, 62865.00),
('BTC', 0.350, 67523.00),
('BTC', 0.375, 72497.00),
('BTC', 0.400, 77786.00),
('BTC', 0.425, 83385.00),
('BTC', 0.450, 89289.00),
('BTC', 0.475, 95509.00),
('BTC', 0.500, 102054.00),
('BTC', 0.525, 108886.00),
('BTC', 0.575, 123479.00),
('BTC', 0.600, 131227.00),
('BTC', 0.625, 139275.00),
('BTC', 0.650, 147635.00),
('BTC', 0.675, 156284.00),
('BTC', 0.700, 165228.00),
('BTC', 0.725, 174480.00),
('BTC', 0.750, 184029.00),
('BTC', 0.775, 193872.00),
('BTC', 0.800, 204009.00),
('BTC', 0.825, 214439.00),
('BTC', 0.850, 225163.00),
('BTC', 0.875, 236186.00),
('BTC', 0.900, 247499.00),
('BTC', 0.925, 259099.00),
('BTC', 0.950, 272006.00),
('BTC', 0.975, 286003.00),
('BTC', 1.000, 299720.00)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- ==================== ETH DATA ====================
-- ETH Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('ETH', 0.000, 824.00),
('ETH', 0.025, 924.00),
('ETH', 0.050, 1039.00),
('ETH', 0.075, 1168.00),
('ETH', 0.100, 1313.00),
('ETH', 0.125, 1475.00),
('ETH', 0.150, 1657.00),
('ETH', 0.175, 1863.00),
('ETH', 0.200, 2094.00),
('ETH', 0.225, 2354.00),
('ETH', 0.250, 2645.00),
('ETH', 0.275, 2974.00),
('ETH', 0.300, 3342.00),
('ETH', 0.325, 3757.00),
('ETH', 0.350, 4222.00),
('ETH', 0.375, 4746.00),
('ETH', 0.400, 5333.00),
('ETH', 0.425, 5993.00),
('ETH', 0.450, 6736.00),
('ETH', 0.475, 7572.00),
('ETH', 0.500, 8511.00),
('ETH', 0.525, 9567.00),
('ETH', 0.550, 10752.00),
('ETH', 0.575, 12085.00),
('ETH', 0.600, 13583.00),
('ETH', 0.625, 15267.00),
('ETH', 0.650, 17159.00),
('ETH', 0.675, 19286.00),
('ETH', 0.700, 21675.00),
('ETH', 0.725, 24360.00),
('ETH', 0.750, 27375.00),
('ETH', 0.775, 30763.00),
('ETH', 0.800, 34568.00),
('ETH', 0.825, 38844.00),
('ETH', 0.850, 43648.00),
('ETH', 0.875, 49047.00),
('ETH', 0.900, 55116.00),
('ETH', 0.925, 61935.00),
('ETH', 0.950, 69603.00),
('ETH', 0.975, 78223.00),
('ETH', 1.000, 87916.00)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- ETH Fiat Risk Values (detailed)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('ETH', 0.102, 1340.29),
('ETH', 0.203, 2172.21),
('ETH', 0.296, 3319.23),
('ETH', 0.391, 4947.12),
('ETH', 0.459, 6766.22),
('ETH', 0.497, 8341.45),
('ETH', 0.524, 9554.78),
('ETH', 0.567, 11655.29),
('ETH', 0.601, 13675.00),
('ETH', 0.629, 15593.74),
('ETH', 0.653, 17576.20),
('ETH', 0.674, 19213.45),
('ETH', 0.692, 20935.62),
('ETH', 0.709, 22748.14),
('ETH', 0.725, 24656.89),
('ETH', 0.740, 26668.27),
('ETH', 0.754, 28789.12),
('ETH', 0.768, 31026.79),
('ETH', 0.781, 33389.13),
('ETH', 0.793, 35884.48),
('ETH', 0.805, 38521.73),
('ETH', 0.817, 41310.27),
('ETH', 0.828, 44260.02),
('ETH', 0.839, 47381.46),
('ETH', 0.849, 50685.65),
('ETH', 0.859, 54184.20),
('ETH', 0.869, 57889.35),
('ETH', 0.878, 61813.95),
('ETH', 0.887, 65971.51),
('ETH', 0.896, 70376.15),
('ETH', 0.905, 75042.66),
('ETH', 0.913, 79987.46),
('ETH', 0.921, 85227.63)
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
('SOL', 1.000, 933.79)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- ==================== ADA (CARDANO) DATA ====================
-- ADA Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('ADA', 0.000, 0.101),
('ADA', 0.025, 0.113),
('ADA', 0.050, 0.127),
('ADA', 0.075, 0.143),
('ADA', 0.100, 0.161),
('ADA', 0.125, 0.182),
('ADA', 0.150, 0.205),
('ADA', 0.175, 0.230),
('ADA', 0.200, 0.260),
('ADA', 0.225, 0.292),
('ADA', 0.250, 0.329),
('ADA', 0.275, 0.371),
('ADA', 0.300, 0.418),
('ADA', 0.325, 0.472),
('ADA', 0.350, 0.514),
('ADA', 0.375, 0.546),
('ADA', 0.400, 0.579),
('ADA', 0.425, 0.615),
('ADA', 0.450, 0.653),
('ADA', 0.475, 0.693),
('ADA', 0.500, 0.735),
('ADA', 0.525, 0.781),
('ADA', 0.550, 0.829),
('ADA', 0.574, 0.891),  -- Current
('ADA', 0.575, 0.893),
('ADA', 0.600, 1.004),
('ADA', 0.625, 1.130),
('ADA', 0.650, 1.271),
('ADA', 0.675, 1.430),
('ADA', 0.700, 1.608),
('ADA', 0.725, 1.809),
('ADA', 0.750, 2.035),
('ADA', 0.775, 2.290),
('ADA', 0.800, 2.576),
('ADA', 0.825, 2.900),
('ADA', 0.850, 3.263),
('ADA', 0.875, 3.670),
('ADA', 0.900, 4.129),
('ADA', 0.925, 4.648),
('ADA', 0.950, 5.227),
('ADA', 0.975, 5.883),
('ADA', 1.000, 6.622)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- ADA Fiat Risk Values (detailed)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('ADA', 0.203, 0.264),
('ADA', 0.304, 0.427),
('ADA', 0.407, 0.590),
('ADA', 0.510, 0.753),
('ADA', 0.580, 0.916),
('ADA', 0.615, 1.079),
('ADA', 0.645, 1.242),
('ADA', 0.671, 1.405),
('ADA', 0.695, 1.568),
('ADA', 0.716, 1.731),
('ADA', 0.735, 1.894),
('ADA', 0.752, 2.057),
('ADA', 0.768, 2.220),
('ADA', 0.783, 2.383),
('ADA', 0.797, 2.546),
('ADA', 0.811, 2.709),
('ADA', 0.823, 2.872),
('ADA', 0.835, 3.035),
('ADA', 0.846, 3.198),
('ADA', 0.856, 3.361),
('ADA', 0.866, 3.524),
('ADA', 0.876, 3.687),
('ADA', 0.885, 3.850),
('ADA', 0.894, 4.013),
('ADA', 0.902, 4.176),
('ADA', 0.911, 4.339),
('ADA', 0.918, 4.503),
('ADA', 0.926, 4.666),
('ADA', 0.933, 4.829),
('ADA', 0.940, 4.992),
('ADA', 0.947, 5.155),
('ADA', 0.954, 5.318),
('ADA', 0.960, 5.481),
('ADA', 0.966, 5.644),
('ADA', 0.972, 5.807),
('ADA', 0.978, 5.970),
('ADA', 0.984, 6.133),
('ADA', 0.989, 6.296),
('ADA', 0.995, 6.459)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- ==================== DOT (POLKADOT) DATA ====================
-- DOT Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('DOT', 0.000, 1.46),
('DOT', 0.025, 1.64),
('DOT', 0.050, 1.85),
('DOT', 0.075, 2.09),
('DOT', 0.100, 2.36),
('DOT', 0.125, 2.66),
('DOT', 0.150, 3.00),
('DOT', 0.175, 3.38),
('DOT', 0.200, 3.81),
('DOT', 0.225, 4.05),
('DOT', 0.250, 4.30),
('DOT', 0.254, 4.34),  -- Current
('DOT', 0.275, 4.57),
('DOT', 0.300, 4.85),
('DOT', 0.325, 5.15),
('DOT', 0.350, 5.48),
('DOT', 0.375, 5.82),
('DOT', 0.400, 6.18),
('DOT', 0.425, 6.57),
('DOT', 0.450, 6.98),
('DOT', 0.475, 7.41),
('DOT', 0.500, 7.88),
('DOT', 0.525, 8.37),
('DOT', 0.550, 8.90),
('DOT', 0.575, 9.45),
('DOT', 0.600, 10.05),
('DOT', 0.625, 10.68),
('DOT', 0.650, 11.35),
('DOT', 0.675, 12.23),
('DOT', 0.700, 13.85),
('DOT', 0.725, 15.69),
('DOT', 0.750, 17.80),
('DOT', 0.775, 20.21),
('DOT', 0.800, 22.96),
('DOT', 0.825, 26.11),
('DOT', 0.850, 29.70),
('DOT', 0.875, 33.81),
('DOT', 0.900, 38.57),
('DOT', 0.925, 43.85),
('DOT', 0.950, 49.87),
('DOT', 0.975, 56.76),
('DOT', 1.000, 64.74)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- DOT Fiat Risk Values (detailed)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('DOT', 0.153, 3.04),
('DOT', 0.280, 4.62),
('DOT', 0.402, 6.20),
('DOT', 0.495, 7.79),
('DOT', 0.571, 9.37),
('DOT', 0.635, 10.95),
('DOT', 0.680, 12.53),
('DOT', 0.704, 14.11),
('DOT', 0.725, 15.70),
('DOT', 0.744, 17.28),
('DOT', 0.761, 18.86),
('DOT', 0.777, 20.44),
('DOT', 0.792, 22.02),
('DOT', 0.805, 23.61),
('DOT', 0.818, 25.19),
('DOT', 0.830, 26.77),
('DOT', 0.841, 28.35),
('DOT', 0.852, 29.93),
('DOT', 0.861, 31.51),
('DOT', 0.871, 33.10),
('DOT', 0.880, 34.68),
('DOT', 0.888, 36.26),
('DOT', 0.896, 37.84),
('DOT', 0.904, 39.42),
('DOT', 0.912, 41.01),
('DOT', 0.919, 42.59),
('DOT', 0.926, 44.17),
('DOT', 0.933, 45.75),
('DOT', 0.940, 47.33),
('DOT', 0.946, 48.92),
('DOT', 0.952, 50.50),
('DOT', 0.958, 52.08),
('DOT', 0.964, 53.66),
('DOT', 0.970, 55.24),
('DOT', 0.975, 56.83),
('DOT', 0.980, 58.41),
('DOT', 0.985, 59.99),
('DOT', 0.990, 61.57),
('DOT', 0.995, 63.15)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- ==================== AVAX (AVALANCHE) DATA ====================
-- AVAX Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('AVAX', 0.000, 4.10),
('AVAX', 0.025, 4.63),
('AVAX', 0.050, 5.22),
('AVAX', 0.075, 5.88),
('AVAX', 0.100, 6.63),
('AVAX', 0.125, 7.48),
('AVAX', 0.150, 8.43),
('AVAX', 0.175, 9.51),
('AVAX', 0.200, 10.72),
('AVAX', 0.225, 12.08),
('AVAX', 0.250, 13.63),
('AVAX', 0.275, 15.36),
('AVAX', 0.300, 17.32),
('AVAX', 0.325, 19.53),
('AVAX', 0.350, 21.64),
('AVAX', 0.375, 22.99),
('AVAX', 0.400, 24.42),
('AVAX', 0.425, 25.94),
('AVAX', 0.450, 27.54),
('AVAX', 0.475, 29.25),
('AVAX', 0.477, 29.39),  -- Current
('AVAX', 0.500, 31.07),
('AVAX', 0.525, 33.00),
('AVAX', 0.550, 36.63),
('AVAX', 0.575, 41.37),
('AVAX', 0.600, 46.72),
('AVAX', 0.625, 52.73),
('AVAX', 0.650, 59.57),
('AVAX', 0.675, 67.27),
('AVAX', 0.700, 75.99),
('AVAX', 0.725, 85.96),
('AVAX', 0.750, 97.16),
('AVAX', 0.775, 109.84),
('AVAX', 0.800, 124.33),
('AVAX', 0.825, 140.72),
('AVAX', 0.850, 159.41),
('AVAX', 0.875, 180.66),
('AVAX', 0.900, 204.71),
('AVAX', 0.925, 232.37),
('AVAX', 0.950, 264.00),
('AVAX', 0.975, 299.90),
('AVAX', 1.000, 341.40)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- AVAX Fiat Risk Values (detailed)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('AVAX', 0.233, 12.54),
('AVAX', 0.340, 20.97),
('AVAX', 0.477, 29.40),
('AVAX', 0.557, 37.83),
('AVAX', 0.598, 46.27),
('AVAX', 0.633, 54.70),
('AVAX', 0.662, 63.13),
('AVAX', 0.688, 71.56),
('AVAX', 0.710, 80.00),
('AVAX', 0.731, 88.43),
('AVAX', 0.749, 96.86),
('AVAX', 0.766, 105.29),
('AVAX', 0.782, 113.73),
('AVAX', 0.796, 122.16),
('AVAX', 0.810, 130.59),
('AVAX', 0.823, 139.02),
('AVAX', 0.834, 147.46),
('AVAX', 0.846, 155.89),
('AVAX', 0.856, 164.32),
('AVAX', 0.866, 172.75),
('AVAX', 0.876, 181.19),
('AVAX', 0.885, 189.62),
('AVAX', 0.893, 198.05),
('AVAX', 0.902, 206.48),
('AVAX', 0.910, 214.92),
('AVAX', 0.917, 223.35),
('AVAX', 0.924, 231.78),
('AVAX', 0.932, 240.21),
('AVAX', 0.938, 248.65),
('AVAX', 0.945, 257.08),
('AVAX', 0.951, 265.51),
('AVAX', 0.957, 273.94),
('AVAX', 0.963, 282.38),
('AVAX', 0.969, 290.81),
('AVAX', 0.975, 299.24),
('AVAX', 0.980, 307.67),
('AVAX', 0.985, 316.11),
('AVAX', 0.990, 324.54),
('AVAX', 0.995, 332.97)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- =======================
-- CHAINLINK (LINK) DATA
-- =======================
-- Current price: $24.21 at risk 0.641
-- Source: https://app.intothecryptoverse.com/assets/chainlink/risk

-- LINK Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('LINK', 0.000, 3.14),
('LINK', 0.025, 3.51),
('LINK', 0.050, 3.92),
('LINK', 0.075, 4.38),
('LINK', 0.100, 4.90),
('LINK', 0.125, 5.47),
('LINK', 0.150, 6.12),
('LINK', 0.175, 6.84),
('LINK', 0.200, 7.65),
('LINK', 0.225, 8.55),
('LINK', 0.250, 9.57),
('LINK', 0.275, 10.57),
('LINK', 0.300, 11.18),
('LINK', 0.325, 11.82),
('LINK', 0.350, 12.50),
('LINK', 0.375, 13.21),
('LINK', 0.400, 13.97),
('LINK', 0.425, 14.77),
('LINK', 0.450, 15.62),
('LINK', 0.475, 16.52),
('LINK', 0.500, 17.46),
('LINK', 0.525, 18.47),
('LINK', 0.550, 19.54),
('LINK', 0.575, 20.67),
('LINK', 0.600, 21.86),
('LINK', 0.625, 23.12),
('LINK', 0.641, 24.21),  -- Current price/risk
('LINK', 0.650, 24.79),
('LINK', 0.675, 27.68),
('LINK', 0.700, 30.90),
('LINK', 0.725, 34.49),
('LINK', 0.750, 38.52),
('LINK', 0.775, 43.02),
('LINK', 0.800, 48.01),
('LINK', 0.825, 53.64),
('LINK', 0.850, 59.88),
('LINK', 0.875, 66.89),
('LINK', 0.900, 74.67),
('LINK', 0.925, 83.39),
('LINK', 0.950, 93.11),
('LINK', 0.975, 104.04),
('LINK', 1.000, 116.18)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- LINK Fiat Risk Values (detailed)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('LINK', 0.000, 3.14),
('LINK', 0.144, 5.97),
('LINK', 0.231, 8.79),
('LINK', 0.317, 11.62),
('LINK', 0.415, 14.45),
('LINK', 0.495, 17.27),
('LINK', 0.563, 20.10),
('LINK', 0.621, 22.92),
('LINK', 0.641, 24.21),  -- Current
('LINK', 0.659, 25.75),
('LINK', 0.682, 28.58),
('LINK', 0.704, 31.40),
('LINK', 0.723, 34.23),
('LINK', 0.741, 37.05),
('LINK', 0.758, 39.88),
('LINK', 0.773, 42.71),
('LINK', 0.788, 45.53),
('LINK', 0.802, 48.36),
('LINK', 0.814, 51.18),
('LINK', 0.827, 54.01),
('LINK', 0.838, 56.83),
('LINK', 0.849, 59.66),
('LINK', 0.860, 62.49),
('LINK', 0.870, 65.31),
('LINK', 0.879, 68.14),
('LINK', 0.888, 70.96),
('LINK', 0.897, 73.79),
('LINK', 0.906, 76.62),
('LINK', 0.914, 79.44),
('LINK', 0.922, 82.27),
('LINK', 0.930, 85.09),
('LINK', 0.937, 87.92),
('LINK', 0.944, 90.75),
('LINK', 0.951, 93.57),
('LINK', 0.958, 96.40),
('LINK', 0.964, 99.22),
('LINK', 0.971, 102.05),
('LINK', 0.977, 104.88),
('LINK', 0.983, 107.70),
('LINK', 0.989, 110.53),
('LINK', 0.994, 113.35),
('LINK', 1.000, 116.18)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- =======================
-- DOGECOIN (DOGE) DATA
-- =======================
-- Current price: $0.28 at risk 0.555
-- Source: https://app.intothecryptoverse.com/assets/dogecoin/risk

-- DOGE Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('DOGE', 0.000, 0.06),
('DOGE', 0.025, 0.07),
('DOGE', 0.050, 0.07),
('DOGE', 0.075, 0.08),
('DOGE', 0.100, 0.08),
('DOGE', 0.125, 0.09),
('DOGE', 0.150, 0.09),
('DOGE', 0.175, 0.10),
('DOGE', 0.200, 0.11),
('DOGE', 0.225, 0.11),
('DOGE', 0.250, 0.12),
('DOGE', 0.275, 0.13),
('DOGE', 0.300, 0.14),
('DOGE', 0.325, 0.15),
('DOGE', 0.350, 0.16),
('DOGE', 0.375, 0.17),
('DOGE', 0.400, 0.18),
('DOGE', 0.425, 0.19),
('DOGE', 0.450, 0.20),
('DOGE', 0.475, 0.22),
('DOGE', 0.500, 0.23),
('DOGE', 0.525, 0.24),
('DOGE', 0.550, 0.27),
('DOGE', 0.555, 0.28),  -- Current price/risk
('DOGE', 0.575, 0.31),
('DOGE', 0.600, 0.35),
('DOGE', 0.625, 0.40),
('DOGE', 0.650, 0.45),
('DOGE', 0.675, 0.51),
('DOGE', 0.700, 0.58),
('DOGE', 0.725, 0.65),
('DOGE', 0.750, 0.74),
('DOGE', 0.775, 0.84),
('DOGE', 0.800, 0.95),
('DOGE', 0.825, 1.08),
('DOGE', 0.850, 1.22),
('DOGE', 0.875, 1.39),
('DOGE', 0.900, 1.57),
('DOGE', 0.925, 1.79),
('DOGE', 0.950, 2.03),
('DOGE', 0.975, 2.30),
('DOGE', 1.000, 2.61)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- DOGE Fiat Risk Values (detailed)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('DOGE', 0.000, 0.06),
('DOGE', 0.270, 0.13),
('DOGE', 0.429, 0.19),
('DOGE', 0.537, 0.26),
('DOGE', 0.555, 0.28),  -- Current
('DOGE', 0.581, 0.32),
('DOGE', 0.618, 0.38),
('DOGE', 0.648, 0.45),
('DOGE', 0.675, 0.51),
('DOGE', 0.699, 0.57),
('DOGE', 0.720, 0.64),
('DOGE', 0.738, 0.70),
('DOGE', 0.756, 0.76),
('DOGE', 0.772, 0.83),
('DOGE', 0.787, 0.89),
('DOGE', 0.800, 0.95),
('DOGE', 0.813, 1.02),
('DOGE', 0.825, 1.08),
('DOGE', 0.837, 1.14),
('DOGE', 0.847, 1.21),
('DOGE', 0.858, 1.27),
('DOGE', 0.867, 1.34),
('DOGE', 0.876, 1.40),
('DOGE', 0.885, 1.46),
('DOGE', 0.894, 1.53),
('DOGE', 0.902, 1.59),
('DOGE', 0.910, 1.65),
('DOGE', 0.917, 1.72),
('DOGE', 0.924, 1.78),
('DOGE', 0.931, 1.84),
('DOGE', 0.938, 1.91),
('DOGE', 0.945, 1.97),
('DOGE', 0.951, 2.03),
('DOGE', 0.957, 2.10),
('DOGE', 0.963, 2.16),
('DOGE', 0.969, 2.22),
('DOGE', 0.974, 2.29),
('DOGE', 0.980, 2.35),
('DOGE', 0.985, 2.42),
('DOGE', 0.990, 2.48),
('DOGE', 0.995, 2.54),
('DOGE', 1.000, 2.61)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- =======================
-- TRON (TRX) DATA
-- =======================
-- Current price: $0.349 at risk 0.664
-- Source: https://app.intothecryptoverse.com/assets/tron/risk

-- TRX Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('TRX', 0.000, 0.11),
('TRX', 0.025, 0.12),
('TRX', 0.050, 0.12),
('TRX', 0.075, 0.13),
('TRX', 0.100, 0.13),
('TRX', 0.125, 0.14),
('TRX', 0.150, 0.14),
('TRX', 0.175, 0.15),
('TRX', 0.200, 0.16),
('TRX', 0.225, 0.16),
('TRX', 0.250, 0.17),
('TRX', 0.275, 0.18),
('TRX', 0.300, 0.19),
('TRX', 0.325, 0.19),
('TRX', 0.350, 0.20),
('TRX', 0.375, 0.21),
('TRX', 0.400, 0.22),
('TRX', 0.425, 0.23),
('TRX', 0.450, 0.24),
('TRX', 0.475, 0.25),
('TRX', 0.500, 0.26),
('TRX', 0.525, 0.27),
('TRX', 0.550, 0.28),
('TRX', 0.575, 0.30),
('TRX', 0.600, 0.31),
('TRX', 0.625, 0.32),
('TRX', 0.650, 0.34),
('TRX', 0.664, 0.35),  -- Current price/risk
('TRX', 0.675, 0.36),
('TRX', 0.700, 0.39),
('TRX', 0.725, 0.42),
('TRX', 0.750, 0.45),
('TRX', 0.775, 0.49),
('TRX', 0.800, 0.53),
('TRX', 0.825, 0.57),
('TRX', 0.850, 0.62),
('TRX', 0.875, 0.67),
('TRX', 0.900, 0.73),
('TRX', 0.925, 0.79),
('TRX', 0.950, 0.85),
('TRX', 0.975, 0.92),
('TRX', 1.000, 1.00)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- TRX Fiat Risk Values (detailed)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('TRX', 0.000, 0.11),
('TRX', 0.107, 0.13),
('TRX', 0.197, 0.16),
('TRX', 0.275, 0.18),
('TRX', 0.344, 0.20),
('TRX', 0.406, 0.22),
('TRX', 0.462, 0.24),
('TRX', 0.513, 0.27),
('TRX', 0.559, 0.29),
('TRX', 0.603, 0.31),
('TRX', 0.643, 0.33),
('TRX', 0.664, 0.35),  -- Current
('TRX', 0.673, 0.36),
('TRX', 0.693, 0.38),
('TRX', 0.711, 0.40),
('TRX', 0.728, 0.42),
('TRX', 0.744, 0.44),
('TRX', 0.759, 0.47),
('TRX', 0.774, 0.49),
('TRX', 0.788, 0.51),
('TRX', 0.801, 0.53),
('TRX', 0.814, 0.56),
('TRX', 0.827, 0.58),
('TRX', 0.839, 0.60),
('TRX', 0.850, 0.62),
('TRX', 0.861, 0.64),
('TRX', 0.872, 0.67),
('TRX', 0.882, 0.69),
('TRX', 0.892, 0.71),
('TRX', 0.902, 0.73),
('TRX', 0.911, 0.75),
('TRX', 0.921, 0.78),
('TRX', 0.930, 0.80),
('TRX', 0.938, 0.82),
('TRX', 0.947, 0.84),
('TRX', 0.955, 0.87),
('TRX', 0.963, 0.89),
('TRX', 0.971, 0.91),
('TRX', 0.978, 0.93),
('TRX', 0.986, 0.95),
('TRX', 0.993, 0.98),
('TRX', 1.000, 1.00)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- =======================
-- BNB DATA
-- =======================
-- Current price: $932.96 at risk 0.528
-- Source: https://app.intothecryptoverse.com/assets/binancecoin/risk

-- BNB Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('BNB', 0.000, 320.60),
('BNB', 0.025, 336.57),
('BNB', 0.050, 353.15),
('BNB', 0.075, 370.81),
('BNB', 0.100, 389.24),
('BNB', 0.125, 408.58),
('BNB', 0.150, 428.85),
('BNB', 0.175, 450.19),
('BNB', 0.200, 472.61),
('BNB', 0.225, 496.25),
('BNB', 0.250, 521.12),
('BNB', 0.275, 547.23),
('BNB', 0.300, 574.56),
('BNB', 0.325, 603.42),
('BNB', 0.350, 633.67),
('BNB', 0.375, 665.45),
('BNB', 0.400, 698.92),
('BNB', 0.425, 734.23),
('BNB', 0.450, 771.24),
('BNB', 0.475, 810.08),
('BNB', 0.500, 853.99),
('BNB', 0.525, 923.09),
('BNB', 0.528, 932.96),  -- Current price/risk
('BNB', 0.550, 1012.14),
('BNB', 0.575, 1110.40),
('BNB', 0.600, 1217.26),
('BNB', 0.625, 1335.18),
('BNB', 0.650, 1464.15),
('BNB', 0.675, 1606.64),
('BNB', 0.700, 1761.40),
('BNB', 0.725, 1932.14),
('BNB', 0.750, 2118.84),
('BNB', 0.775, 2325.19),
('BNB', 0.800, 2549.97),
('BNB', 0.825, 2796.86),
('BNB', 0.850, 3069.54),
('BNB', 0.875, 3366.79),
('BNB', 0.900, 3693.52),
('BNB', 0.925, 4052.18),
('BNB', 0.950, 4445.24),
('BNB', 0.975, 4877.60),
('BNB', 1.000, 5351.73)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- BNB Fiat Risk Values (detailed)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('BNB', 0.000, 320.60),
('BNB', 0.171, 446.38),
('BNB', 0.298, 572.16),
('BNB', 0.399, 697.94),
('BNB', 0.483, 823.72),
('BNB', 0.528, 932.96),  -- Current
('BNB', 0.533, 949.49),
('BNB', 0.566, 1075.27),
('BNB', 0.596, 1201.05),
('BNB', 0.623, 1326.83),
('BNB', 0.648, 1452.61),
('BNB', 0.670, 1578.38),
('BNB', 0.691, 1704.16),
('BNB', 0.710, 1829.94),
('BNB', 0.728, 1955.72),
('BNB', 0.745, 2081.50),
('BNB', 0.761, 2207.27),
('BNB', 0.776, 2333.05),
('BNB', 0.790, 2458.83),
('BNB', 0.804, 2584.61),
('BNB', 0.816, 2710.39),
('BNB', 0.829, 2836.17),
('BNB', 0.840, 2961.94),
('BNB', 0.852, 3087.72),
('BNB', 0.862, 3213.50),
('BNB', 0.873, 3339.28),
('BNB', 0.883, 3465.06),
('BNB', 0.892, 3590.83),
('BNB', 0.902, 3716.61),
('BNB', 0.911, 3842.39),
('BNB', 0.919, 3968.17),
('BNB', 0.928, 4093.95),
('BNB', 0.936, 4219.72),
('BNB', 0.944, 4345.50),
('BNB', 0.952, 4471.28),
('BNB', 0.959, 4597.06),
('BNB', 0.966, 4722.84),
('BNB', 0.973, 4848.61),
('BNB', 0.980, 4974.39),
('BNB', 0.987, 5100.17),
('BNB', 0.994, 5225.95),
('BNB', 1.000, 5351.73)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- =======================
-- SHIBA INU (SHIB) DATA
-- =======================
-- Current price: $0.0000137 at risk 0.227
-- Source: https://app.intothecryptoverse.com/assets/shiba-inu/risk

-- SHIB Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('SHIB', 0.000, 0.0000045),
('SHIB', 0.025, 0.0000052),
('SHIB', 0.050, 0.0000059),
('SHIB', 0.075, 0.0000067),
('SHIB', 0.100, 0.0000077),
('SHIB', 0.125, 0.0000088),
('SHIB', 0.150, 0.0000100),
('SHIB', 0.175, 0.0000115),
('SHIB', 0.200, 0.0000127),
('SHIB', 0.225, 0.0000136),
('SHIB', 0.227, 0.0000137),  -- Current price/risk
('SHIB', 0.250, 0.0000146),
('SHIB', 0.275, 0.0000157),
('SHIB', 0.300, 0.0000168),
('SHIB', 0.325, 0.0000180),
('SHIB', 0.350, 0.0000204),
('SHIB', 0.375, 0.0000234),
('SHIB', 0.400, 0.0000268),
('SHIB', 0.425, 0.0000307),
('SHIB', 0.450, 0.0000352),
('SHIB', 0.475, 0.0000403),
('SHIB', 0.500, 0.0000462),
('SHIB', 0.525, 0.0000531),
('SHIB', 0.550, 0.0000610),
('SHIB', 0.575, 0.0000702),
('SHIB', 0.600, 0.0000805),
('SHIB', 0.625, 0.0000921),
('SHIB', 0.650, 0.0001052),
('SHIB', 0.675, 0.0001204),
('SHIB', 0.700, 0.0001375),
('SHIB', 0.725, 0.0001571),
('SHIB', 0.750, 0.0001796),
('SHIB', 0.775, 0.0002053),
('SHIB', 0.800, 0.0002348),
('SHIB', 0.825, 0.0002684),
('SHIB', 0.850, 0.0003070),
('SHIB', 0.875, 0.0003513),
('SHIB', 0.900, 0.0004020),
('SHIB', 0.925, 0.0004605),
('SHIB', 0.950, 0.0005269),
('SHIB', 0.975, 0.0006042),
('SHIB', 1.000, 0.0006921)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- SHIB Fiat Risk Values (detailed)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('SHIB', 0.000, 0.0000045),
('SHIB', 0.227, 0.0000137),  -- Current
('SHIB', 0.361, 0.0000217),
('SHIB', 0.469, 0.0000389),
('SHIB', 0.535, 0.0000561),
('SHIB', 0.583, 0.0000733),
('SHIB', 0.622, 0.0000905),
('SHIB', 0.654, 0.0001077),
('SHIB', 0.682, 0.0001249),
('SHIB', 0.706, 0.0001420),
('SHIB', 0.727, 0.0001592),
('SHIB', 0.747, 0.0001764),
('SHIB', 0.764, 0.0001936),
('SHIB', 0.780, 0.0002108),
('SHIB', 0.795, 0.0002280),
('SHIB', 0.808, 0.0002452),
('SHIB', 0.821, 0.0002624),
('SHIB', 0.832, 0.0002796),
('SHIB', 0.844, 0.0002968),
('SHIB', 0.854, 0.0003139),
('SHIB', 0.864, 0.0003311),
('SHIB', 0.873, 0.0003483),
('SHIB', 0.882, 0.0003655),
('SHIB', 0.891, 0.0003827),
('SHIB', 0.899, 0.0003999),
('SHIB', 0.907, 0.0004171),
('SHIB', 0.914, 0.0004343),
('SHIB', 0.921, 0.0004515),
('SHIB', 0.928, 0.0004687),
('SHIB', 0.935, 0.0004858),
('SHIB', 0.941, 0.0005030),
('SHIB', 0.948, 0.0005202),
('SHIB', 0.954, 0.0005374),
('SHIB', 0.959, 0.0005546),
('SHIB', 0.965, 0.0005718),
('SHIB', 0.970, 0.0005890),
('SHIB', 0.976, 0.0006062),
('SHIB', 0.981, 0.0006234),
('SHIB', 0.986, 0.0006406),
('SHIB', 0.991, 0.0006577),
('SHIB', 0.995, 0.0006749),
('SHIB', 1.000, 0.0006921)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd;

-- ==================== FUNCTIONS ====================
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

-- TON (The Open Network) Key Risk values (42 values from IntoTheCryptoverse)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('TON', 0.000, 1.45),
('TON', 0.025, 1.59),
('TON', 0.050, 1.74),
('TON', 0.075, 1.90),
('TON', 0.100, 2.08),
('TON', 0.125, 2.28),
('TON', 0.150, 2.49),
('TON', 0.175, 2.73),
('TON', 0.200, 2.99),
('TON', 0.225, 3.13),
('TON', 0.236, 3.19),  -- Current price/risk
('TON', 0.250, 3.27),
('TON', 0.275, 3.42),
('TON', 0.300, 3.58),
('TON', 0.325, 3.75),
('TON', 0.350, 3.92),
('TON', 0.375, 4.10),
('TON', 0.400, 4.29),
('TON', 0.425, 4.49),
('TON', 0.450, 4.70),
('TON', 0.475, 4.96),
('TON', 0.500, 5.43),
('TON', 0.525, 5.94),
('TON', 0.550, 6.51),
('TON', 0.575, 7.12),
('TON', 0.600, 7.80),
('TON', 0.625, 8.53),
('TON', 0.650, 9.34),
('TON', 0.675, 10.23),
('TON', 0.700, 11.20),
('TON', 0.725, 12.25),
('TON', 0.750, 13.42),
('TON', 0.775, 14.69),
('TON', 0.800, 16.08),
('TON', 0.825, 17.61),
('TON', 0.850, 19.28),
('TON', 0.875, 21.12),
('TON', 0.900, 23.12),
('TON', 0.925, 25.33),
('TON', 0.950, 27.73),
('TON', 0.975, 30.37),
('TON', 1.000, 33.26)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- TON Fiat Risk values (42 detailed price/risk pairs from IntoTheCryptoverse)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('TON', 0.000, 1.45),
('TON', 0.121, 2.24),
('TON', 0.209, 3.04),
('TON', 0.236, 3.19),  -- Current risk/price
('TON', 0.338, 3.84),
('TON', 0.442, 4.63),
('TON', 0.500, 5.43),
('TON', 0.538, 6.22),
('TON', 0.571, 7.02),
('TON', 0.601, 7.81),
('TON', 0.627, 8.61),
('TON', 0.652, 9.40),
('TON', 0.674, 10.20),
('TON', 0.695, 10.99),
('TON', 0.714, 11.79),
('TON', 0.732, 12.58),
('TON', 0.749, 13.38),
('TON', 0.765, 14.18),
('TON', 0.780, 14.97),
('TON', 0.794, 15.77),
('TON', 0.808, 16.56),
('TON', 0.821, 17.36),
('TON', 0.833, 18.15),
('TON', 0.845, 18.95),
('TON', 0.856, 19.74),
('TON', 0.867, 20.54),
('TON', 0.878, 21.33),
('TON', 0.888, 22.13),
('TON', 0.898, 22.92),
('TON', 0.907, 23.72),
('TON', 0.916, 24.51),
('TON', 0.925, 25.31),
('TON', 0.933, 26.11),
('TON', 0.942, 26.90),
('TON', 0.950, 27.70),
('TON', 0.957, 28.49),
('TON', 0.965, 29.29),
('TON', 0.972, 30.08),
('TON', 0.980, 30.88),
('TON', 0.987, 31.67),
('TON', 0.993, 32.47),
('TON', 1.000, 33.26)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- MATIC (Matic Network) Key Risk values (42 values from IntoTheCryptoverse)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('MATIC', 0.000, 0.19),
('MATIC', 0.025, 0.22),
('MATIC', 0.050, 0.23),
('MATIC', 0.075, 0.25),
('MATIC', 0.100, 0.26),
('MATIC', 0.125, 0.28),
('MATIC', 0.150, 0.30),
('MATIC', 0.175, 0.32),
('MATIC', 0.200, 0.34),
('MATIC', 0.225, 0.36),
('MATIC', 0.250, 0.38),
('MATIC', 0.275, 0.41),
('MATIC', 0.300, 0.43),
('MATIC', 0.325, 0.46),
('MATIC', 0.350, 0.49),
('MATIC', 0.375, 0.52),
('MATIC', 0.400, 0.55),
('MATIC', 0.425, 0.59),
('MATIC', 0.450, 0.63),
('MATIC', 0.475, 0.67),
('MATIC', 0.500, 0.71),
('MATIC', 0.525, 0.76),
('MATIC', 0.550, 0.81),
('MATIC', 0.575, 0.86),
('MATIC', 0.600, 0.98),
('MATIC', 0.625, 1.11),
('MATIC', 0.650, 1.26),
('MATIC', 0.675, 1.43),
('MATIC', 0.700, 1.63),
('MATIC', 0.725, 1.85),
('MATIC', 0.750, 2.11),
('MATIC', 0.775, 2.40),
('MATIC', 0.800, 2.74),
('MATIC', 0.825, 3.13),
('MATIC', 0.850, 3.58),
('MATIC', 0.875, 4.10),
('MATIC', 0.900, 4.70),
('MATIC', 0.925, 5.41),
('MATIC', 0.950, 6.22),
('MATIC', 0.975, 7.19),
('MATIC', 1.000, 8.32)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- MATIC Fiat Risk values (42 detailed price/risk pairs from IntoTheCryptoverse)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('MATIC', 0.000, 0.19),
('MATIC', 0.050, 0.23),  -- Current risk/price
('MATIC', 0.263, 0.39),
('MATIC', 0.430, 0.60),
('MATIC', 0.547, 0.80),
('MATIC', 0.605, 1.00),
('MATIC', 0.642, 1.21),
('MATIC', 0.672, 1.41),
('MATIC', 0.698, 1.61),
('MATIC', 0.721, 1.82),
('MATIC', 0.742, 2.02),
('MATIC', 0.760, 2.22),
('MATIC', 0.777, 2.43),
('MATIC', 0.792, 2.63),
('MATIC', 0.806, 2.83),
('MATIC', 0.819, 3.04),
('MATIC', 0.831, 3.24),
('MATIC', 0.843, 3.44),
('MATIC', 0.853, 3.65),
('MATIC', 0.863, 3.85),
('MATIC', 0.873, 4.05),
('MATIC', 0.882, 4.26),
('MATIC', 0.890, 4.46),
('MATIC', 0.898, 4.66),
('MATIC', 0.906, 4.87),
('MATIC', 0.914, 5.07),
('MATIC', 0.921, 5.27),
('MATIC', 0.927, 5.48),
('MATIC', 0.934, 5.68),
('MATIC', 0.940, 5.88),
('MATIC', 0.946, 6.09),
('MATIC', 0.952, 6.29),
('MATIC', 0.957, 6.49),
('MATIC', 0.963, 6.69),
('MATIC', 0.968, 6.90),
('MATIC', 0.973, 7.10),
('MATIC', 0.978, 7.30),
('MATIC', 0.983, 7.51),
('MATIC', 0.987, 7.71),
('MATIC', 0.992, 7.91),
('MATIC', 0.996, 8.12),
('MATIC', 1.000, 8.32)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- POL (Polygon Ex-Matic) Key Risk values (42 values from IntoTheCryptoverse)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('POL', 0.000, 0.11),
('POL', 0.025, 0.13),
('POL', 0.050, 0.15),
('POL', 0.075, 0.17),
('POL', 0.100, 0.19),
('POL', 0.125, 0.21),
('POL', 0.150, 0.23),
('POL', 0.175, 0.25),
('POL', 0.200, 0.26),
('POL', 0.217, 0.27),  -- Current price/risk
('POL', 0.225, 0.28),
('POL', 0.250, 0.30),
('POL', 0.275, 0.32),
('POL', 0.300, 0.34),
('POL', 0.325, 0.36),
('POL', 0.350, 0.38),
('POL', 0.375, 0.40),
('POL', 0.400, 0.43),
('POL', 0.425, 0.46),
('POL', 0.450, 0.49),
('POL', 0.475, 0.52),
('POL', 0.500, 0.59),
('POL', 0.525, 0.67),
('POL', 0.550, 0.76),
('POL', 0.575, 0.86),
('POL', 0.600, 0.98),
('POL', 0.625, 1.11),
('POL', 0.650, 1.26),
('POL', 0.675, 1.43),
('POL', 0.700, 1.63),
('POL', 0.725, 1.85),
('POL', 0.750, 2.11),
('POL', 0.775, 2.40),
('POL', 0.800, 2.74),
('POL', 0.825, 3.13),
('POL', 0.850, 3.58),
('POL', 0.875, 4.10),
('POL', 0.900, 4.70),
('POL', 0.925, 5.40),
('POL', 0.950, 6.22),
('POL', 0.975, 7.18),
('POL', 1.000, 8.32)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- POL Fiat Risk values (42 detailed price/risk pairs from IntoTheCryptoverse)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('POL', 0.000, 0.11),
('POL', 0.217, 0.27),  -- Current risk/price
('POL', 0.282, 0.32),
('POL', 0.477, 0.53),
('POL', 0.543, 0.73),
('POL', 0.592, 0.94),
('POL', 0.631, 1.14),
('POL', 0.663, 1.35),
('POL', 0.691, 1.55),
('POL', 0.715, 1.76),
('POL', 0.736, 1.96),
('POL', 0.755, 2.17),
('POL', 0.772, 2.37),
('POL', 0.788, 2.58),
('POL', 0.803, 2.78),
('POL', 0.816, 2.99),
('POL', 0.829, 3.19),
('POL', 0.840, 3.40),
('POL', 0.851, 3.60),
('POL', 0.861, 3.81),
('POL', 0.871, 4.01),
('POL', 0.880, 4.22),
('POL', 0.889, 4.42),
('POL', 0.897, 4.63),
('POL', 0.905, 4.83),
('POL', 0.912, 5.04),
('POL', 0.920, 5.24),
('POL', 0.926, 5.45),
('POL', 0.933, 5.65),
('POL', 0.939, 5.86),
('POL', 0.945, 6.06),
('POL', 0.951, 6.27),
('POL', 0.957, 6.47),
('POL', 0.962, 6.68),
('POL', 0.968, 6.88),
('POL', 0.973, 7.09),
('POL', 0.978, 7.29),
('POL', 0.982, 7.50),
('POL', 0.987, 7.71),
('POL', 0.991, 7.91),
('POL', 0.996, 8.12),
('POL', 1.000, 8.32)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- VET (VeChain) Key Risk values (42 values from IntoTheCryptoverse)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('VET', 0.000, 0.011),
('VET', 0.025, 0.013),
('VET', 0.050, 0.014),
('VET', 0.075, 0.016),
('VET', 0.100, 0.018),
('VET', 0.125, 0.020),
('VET', 0.150, 0.022),
('VET', 0.175, 0.024),
('VET', 0.185, 0.025),  -- Current price/risk
('VET', 0.200, 0.026),
('VET', 0.225, 0.027),
('VET', 0.250, 0.029),
('VET', 0.275, 0.030),
('VET', 0.300, 0.032),
('VET', 0.325, 0.034),
('VET', 0.350, 0.036),
('VET', 0.375, 0.038),
('VET', 0.400, 0.040),
('VET', 0.425, 0.043),
('VET', 0.450, 0.045),
('VET', 0.475, 0.049),
('VET', 0.500, 0.055),
('VET', 0.525, 0.062),
('VET', 0.550, 0.070),
('VET', 0.575, 0.078),
('VET', 0.600, 0.088),
('VET', 0.625, 0.099),
('VET', 0.650, 0.111),
('VET', 0.675, 0.125),
('VET', 0.700, 0.140),
('VET', 0.725, 0.158),
('VET', 0.750, 0.178),
('VET', 0.775, 0.201),
('VET', 0.800, 0.226),
('VET', 0.825, 0.254),
('VET', 0.850, 0.286),
('VET', 0.875, 0.322),
('VET', 0.900, 0.364),
('VET', 0.925, 0.411),
('VET', 0.950, 0.465),
('VET', 0.975, 0.525),
('VET', 1.000, 0.588)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- VET Fiat Risk values (42 detailed price/risk pairs from IntoTheCryptoverse)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('VET', 0.000, 0.011),
('VET', 0.185, 0.025),  -- Current risk/price
('VET', 0.202, 0.026),
('VET', 0.399, 0.040),
('VET', 0.497, 0.055),
('VET', 0.548, 0.069),
('VET', 0.589, 0.083),
('VET', 0.623, 0.098),
('VET', 0.653, 0.112),
('VET', 0.679, 0.127),
('VET', 0.701, 0.141),
('VET', 0.722, 0.155),
('VET', 0.740, 0.170),
('VET', 0.757, 0.184),
('VET', 0.773, 0.199),
('VET', 0.788, 0.213),
('VET', 0.802, 0.228),
('VET', 0.815, 0.242),
('VET', 0.827, 0.256),
('VET', 0.838, 0.271),
('VET', 0.849, 0.285),
('VET', 0.860, 0.300),
('VET', 0.869, 0.314),
('VET', 0.879, 0.329),
('VET', 0.888, 0.343),
('VET', 0.896, 0.357),
('VET', 0.904, 0.372),
('VET', 0.912, 0.386),
('VET', 0.920, 0.401),
('VET', 0.927, 0.415),
('VET', 0.934, 0.429),
('VET', 0.941, 0.444),
('VET', 0.947, 0.458),
('VET', 0.953, 0.473),
('VET', 0.960, 0.487),
('VET', 0.965, 0.502),
('VET', 0.971, 0.516),
('VET', 0.977, 0.530),
('VET', 0.983, 0.545),
('VET', 0.989, 0.559),
('VET', 0.995, 0.574),
('VET', 1.000, 0.588)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- ALGO (Algorand) Key Risk values (42 values from IntoTheCryptoverse)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('ALGO', 0.000, 0.087),
('ALGO', 0.025, 0.096),
('ALGO', 0.050, 0.107),
('ALGO', 0.075, 0.119),
('ALGO', 0.100, 0.132),
('ALGO', 0.125, 0.147),
('ALGO', 0.150, 0.164),
('ALGO', 0.175, 0.182),
('ALGO', 0.200, 0.196),
('ALGO', 0.225, 0.207),
('ALGO', 0.250, 0.218),
('ALGO', 0.275, 0.230),
('ALGO', 0.295, 0.240),  -- Current price/risk
('ALGO', 0.300, 0.243),
('ALGO', 0.325, 0.256),
('ALGO', 0.350, 0.270),
('ALGO', 0.375, 0.284),
('ALGO', 0.400, 0.300),
('ALGO', 0.425, 0.316),
('ALGO', 0.450, 0.333),
('ALGO', 0.475, 0.351),
('ALGO', 0.500, 0.371),
('ALGO', 0.525, 0.391),
('ALGO', 0.550, 0.412),
('ALGO', 0.575, 0.434),
('ALGO', 0.600, 0.458),
('ALGO', 0.625, 0.483),
('ALGO', 0.650, 0.525),
('ALGO', 0.675, 0.585),
('ALGO', 0.700, 0.650),
('ALGO', 0.725, 0.723),
('ALGO', 0.750, 0.804),
('ALGO', 0.775, 0.894),
('ALGO', 0.800, 0.995),
('ALGO', 0.825, 1.107),
('ALGO', 0.850, 1.231),
('ALGO', 0.875, 1.370),
('ALGO', 0.900, 1.525),
('ALGO', 0.925, 1.697),
('ALGO', 0.950, 1.889),
('ALGO', 0.975, 2.103),
('ALGO', 1.000, 2.340)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- ALGO Fiat Risk values (42 detailed price/risk pairs from IntoTheCryptoverse)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('ALGO', 0.000, 0.087),
('ALGO', 0.118, 0.143),
('ALGO', 0.208, 0.199),
('ALGO', 0.295, 0.240),  -- Current risk/price
('ALGO', 0.325, 0.256),
('ALGO', 0.419, 0.312),
('ALGO', 0.497, 0.368),
('ALGO', 0.564, 0.425),
('ALGO', 0.623, 0.481),
('ALGO', 0.655, 0.537),
('ALGO', 0.679, 0.594),
('ALGO', 0.700, 0.650),
('ALGO', 0.720, 0.706),
('ALGO', 0.738, 0.763),
('ALGO', 0.754, 0.819),
('ALGO', 0.770, 0.875),
('ALGO', 0.785, 0.932),
('ALGO', 0.798, 0.988),
('ALGO', 0.811, 1.045),
('ALGO', 0.824, 1.101),
('ALGO', 0.835, 1.157),
('ALGO', 0.847, 1.214),
('ALGO', 0.857, 1.270),
('ALGO', 0.867, 1.326),
('ALGO', 0.877, 1.383),
('ALGO', 0.886, 1.439),
('ALGO', 0.895, 1.495),
('ALGO', 0.904, 1.552),
('ALGO', 0.912, 1.608),
('ALGO', 0.920, 1.664),
('ALGO', 0.928, 1.721),
('ALGO', 0.936, 1.777),
('ALGO', 0.943, 1.833),
('ALGO', 0.950, 1.890),
('ALGO', 0.957, 1.946),
('ALGO', 0.964, 2.002),
('ALGO', 0.970, 2.059),
('ALGO', 0.976, 2.115),
('ALGO', 0.983, 2.171),
('ALGO', 0.989, 2.228),
('ALGO', 0.994, 2.284),
('ALGO', 1.000, 2.340)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- ================================
-- MKR (Maker) Risk Data - Current Price: $1,793.84 (Risk: 0.470)
-- Source: IntoTheCryptoverse - Extracted: 2025-09-15
-- ================================

-- MKR Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('MKR', 0.000, 526.00),
('MKR', 0.025, 571.00),
('MKR', 0.050, 620.00),
('MKR', 0.075, 673.00),
('MKR', 0.100, 731.00),
('MKR', 0.125, 794.00),
('MKR', 0.150, 861.00),
('MKR', 0.175, 935.00),
('MKR', 0.200, 1015.00),
('MKR', 0.225, 1103.00),
('MKR', 0.250, 1197.00),
('MKR', 0.275, 1300.00),
('MKR', 0.300, 1357.00),
('MKR', 0.325, 1414.00),
('MKR', 0.350, 1473.00),
('MKR', 0.375, 1535.00),
('MKR', 0.400, 1599.00),
('MKR', 0.425, 1666.00),
('MKR', 0.450, 1736.00),
('MKR', 0.470, 1794.00),  -- Current price/risk
('MKR', 0.475, 1809.00),
('MKR', 0.500, 1885.00),
('MKR', 0.525, 1990.00),
('MKR', 0.550, 2159.00),
('MKR', 0.575, 2344.00),
('MKR', 0.600, 2545.00),
('MKR', 0.625, 2764.00),
('MKR', 0.650, 3000.00),
('MKR', 0.675, 3256.00),
('MKR', 0.700, 3536.00),
('MKR', 0.725, 3838.00),
('MKR', 0.750, 4166.00),
('MKR', 0.775, 4525.00),
('MKR', 0.800, 4912.00),
('MKR', 0.825, 5335.00),
('MKR', 0.850, 5790.00),
('MKR', 0.875, 6288.00),
('MKR', 0.900, 6826.00),
('MKR', 0.925, 7413.00),
('MKR', 0.950, 8047.00),
('MKR', 0.975, 8738.00),
('MKR', 1.000, 9487.00)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- MKR Fiat Risk Values (detailed price/risk pairs for precise interpolation)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('MKR', 0.108, 750.00),
('MKR', 0.187, 974.00),
('MKR', 0.329, 1422.00),
('MKR', 0.418, 1646.00),
('MKR', 0.495, 1870.00),
('MKR', 0.541, 2094.00),
('MKR', 0.572, 2318.00),
('MKR', 0.649, 2990.00),
('MKR', 0.671, 3214.00),
('MKR', 0.691, 3438.00),
('MKR', 0.711, 3662.00),
('MKR', 0.729, 3886.00),
('MKR', 0.746, 4110.00),
('MKR', 0.762, 4334.00),
('MKR', 0.777, 4558.00),
('MKR', 0.792, 4782.00),
('MKR', 0.806, 5006.00),
('MKR', 0.819, 5230.00),
('MKR', 0.832, 5454.00),
('MKR', 0.844, 5678.00),
('MKR', 0.856, 5902.00),
('MKR', 0.867, 6126.00),
('MKR', 0.878, 6350.00),
('MKR', 0.889, 6574.00),
('MKR', 0.899, 6798.00),
('MKR', 0.909, 7022.00),
('MKR', 0.918, 7246.00),
('MKR', 0.927, 7470.00),
('MKR', 0.936, 7694.00),
('MKR', 0.945, 7918.00),
('MKR', 0.954, 8142.00),
('MKR', 0.962, 8366.00),
('MKR', 0.970, 8591.00),
('MKR', 0.978, 8815.00),
('MKR', 0.985, 9039.00),
('MKR', 0.993, 9263.00)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- ================================
-- XRP (Ripple) Risk Data - Current Price: $3.05 (Risk: 0.762)
-- Source: IntoTheCryptoverse - Extracted: 2025-09-15
-- ================================

-- XRP Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('XRP', 0.000, 0.752),
('XRP', 0.025, 0.787),
('XRP', 0.050, 0.824),
('XRP', 0.075, 0.862),
('XRP', 0.100, 0.903),
('XRP', 0.125, 0.945),
('XRP', 0.150, 0.989),
('XRP', 0.175, 1.035),
('XRP', 0.200, 1.084),
('XRP', 0.225, 1.135),
('XRP', 0.250, 1.188),
('XRP', 0.275, 1.244),
('XRP', 0.300, 1.302),
('XRP', 0.325, 1.363),
('XRP', 0.350, 1.427),
('XRP', 0.375, 1.494),
('XRP', 0.400, 1.563),
('XRP', 0.425, 1.637),
('XRP', 0.450, 1.714),
('XRP', 0.475, 1.794),
('XRP', 0.500, 1.878),
('XRP', 0.525, 1.967),
('XRP', 0.550, 2.059),
('XRP', 0.575, 2.156),
('XRP', 0.600, 2.257),
('XRP', 0.625, 2.363),
('XRP', 0.650, 2.474),
('XRP', 0.675, 2.590),
('XRP', 0.700, 2.712),
('XRP', 0.725, 2.839),
('XRP', 0.750, 2.973),
('XRP', 0.762, 3.050),  -- Current price/risk
('XRP', 0.775, 3.148),
('XRP', 0.800, 3.423),
('XRP', 0.825, 3.722),
('XRP', 0.850, 4.046),
('XRP', 0.875, 4.400),
('XRP', 0.900, 4.782),
('XRP', 0.925, 5.202),
('XRP', 0.950, 5.654),
('XRP', 0.975, 6.149),
('XRP', 1.000, 6.685)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- XRP Fiat Risk Values (detailed price/risk pairs for precise interpolation)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('XRP', 0.098, 0.900),
('XRP', 0.182, 1.049),
('XRP', 0.254, 1.197),
('XRP', 0.318, 1.345),
('XRP', 0.427, 1.642),
('XRP', 0.474, 1.790),
('XRP', 0.517, 1.939),
('XRP', 0.557, 2.087),
('XRP', 0.595, 2.235),
('XRP', 0.630, 2.384),
('XRP', 0.663, 2.532),
('XRP', 0.694, 2.680),
('XRP', 0.723, 2.829),
('XRP', 0.751, 2.977),
('XRP', 0.773, 3.125),
('XRP', 0.787, 3.274),
('XRP', 0.813, 3.570),
('XRP', 0.836, 3.867),
('XRP', 0.848, 4.015),
('XRP', 0.859, 4.164),
('XRP', 0.869, 4.312),
('XRP', 0.879, 4.460),
('XRP', 0.889, 4.609),
('XRP', 0.898, 4.757),
('XRP', 0.908, 4.905),
('XRP', 0.916, 5.054),
('XRP', 0.933, 5.350),
('XRP', 0.942, 5.499),
('XRP', 0.957, 5.795),
('XRP', 0.965, 5.944),
('XRP', 0.972, 6.092),
('XRP', 0.979, 6.240),
('XRP', 0.986, 6.389),
('XRP', 0.993, 6.537)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- ================================
-- ATOM (Cosmos) Risk Data - Current Price: $4.67 (Risk: 0.224)
-- Source: IntoTheCryptoverse - Extracted: 2025-09-15
-- ================================

-- ATOM Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('ATOM', 0.000, 1.72),
('ATOM', 0.025, 1.94),
('ATOM', 0.050, 2.18),
('ATOM', 0.075, 2.45),
('ATOM', 0.100, 2.76),
('ATOM', 0.125, 3.10),
('ATOM', 0.150, 3.48),
('ATOM', 0.175, 3.92),
('ATOM', 0.200, 4.41),
('ATOM', 0.224, 4.67),  -- Current price/risk
('ATOM', 0.225, 4.68),
('ATOM', 0.250, 4.96),
('ATOM', 0.275, 5.26),
('ATOM', 0.300, 5.58),
('ATOM', 0.325, 5.93),
('ATOM', 0.350, 6.29),
('ATOM', 0.375, 6.67),
('ATOM', 0.400, 7.08),
('ATOM', 0.425, 7.51),
('ATOM', 0.450, 7.97),
('ATOM', 0.475, 8.45),
('ATOM', 0.500, 8.97),
('ATOM', 0.525, 9.52),
('ATOM', 0.550, 10.10),
('ATOM', 0.575, 10.72),
('ATOM', 0.600, 11.38),
('ATOM', 0.625, 12.07),
('ATOM', 0.650, 12.90),
('ATOM', 0.675, 14.54),
('ATOM', 0.700, 16.39),
('ATOM', 0.725, 18.48),
('ATOM', 0.750, 20.84),
('ATOM', 0.775, 23.53),
('ATOM', 0.800, 26.55),
('ATOM', 0.825, 29.98),
('ATOM', 0.850, 33.85),
('ATOM', 0.875, 38.27),
('ATOM', 0.900, 43.26),
('ATOM', 0.925, 48.97),
('ATOM', 0.950, 55.45),
('ATOM', 0.975, 62.86),
('ATOM', 1.000, 71.28)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- ATOM Fiat Risk Values (detailed price/risk pairs for precise interpolation)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('ATOM', 0.149, 3.46),
('ATOM', 0.270, 5.20),
('ATOM', 0.392, 6.94),
('ATOM', 0.486, 8.68),
('ATOM', 0.563, 10.42),
('ATOM', 0.628, 12.16),
('ATOM', 0.665, 13.89),
('ATOM', 0.690, 15.63),
('ATOM', 0.712, 17.37),
('ATOM', 0.732, 19.11),
('ATOM', 0.767, 22.59),
('ATOM', 0.782, 24.33),
('ATOM', 0.796, 26.07),
('ATOM', 0.810, 27.81),
('ATOM', 0.822, 29.55),
('ATOM', 0.834, 31.29),
('ATOM', 0.845, 33.02),
('ATOM', 0.855, 34.76),
('ATOM', 0.865, 36.50),
('ATOM', 0.884, 39.98),
('ATOM', 0.893, 41.72),
('ATOM', 0.901, 43.46),
('ATOM', 0.909, 45.20),
('ATOM', 0.916, 46.94),
('ATOM', 0.924, 48.68),
('ATOM', 0.931, 50.41),
('ATOM', 0.938, 52.15),
('ATOM', 0.944, 53.89),
('ATOM', 0.951, 55.63),
('ATOM', 0.957, 57.37),
('ATOM', 0.963, 59.11),
('ATOM', 0.969, 60.85),
('ATOM', 0.974, 62.59),
('ATOM', 0.980, 64.33),
('ATOM', 0.985, 66.07),
('ATOM', 0.990, 67.80),
('ATOM', 0.995, 69.54)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- ================================
-- XTZ (Tezos) Risk Data - Current Price: $0.775 (Risk: 0.174)
-- Source: IntoTheCryptoverse - Extracted: 2025-09-15
-- ================================

-- XTZ Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('XTZ', 0.000, 0.48),
('XTZ', 0.025, 0.52),
('XTZ', 0.050, 0.57),
('XTZ', 0.075, 0.63),
('XTZ', 0.100, 0.67),
('XTZ', 0.125, 0.71),
('XTZ', 0.150, 0.74),
('XTZ', 0.174, 0.78),  -- Current price/risk
('XTZ', 0.175, 0.78),
('XTZ', 0.200, 0.81),
('XTZ', 0.225, 0.85),
('XTZ', 0.250, 0.90),
('XTZ', 0.275, 0.94),
('XTZ', 0.300, 0.98),
('XTZ', 0.325, 1.03),
('XTZ', 0.350, 1.08),
('XTZ', 0.375, 1.14),
('XTZ', 0.400, 1.19),
('XTZ', 0.425, 1.25),
('XTZ', 0.450, 1.31),
('XTZ', 0.475, 1.37),
('XTZ', 0.500, 1.44),
('XTZ', 0.525, 1.51),
('XTZ', 0.550, 1.58),
('XTZ', 0.575, 1.66),
('XTZ', 0.600, 1.74),
('XTZ', 0.625, 1.83),
('XTZ', 0.650, 1.91),
('XTZ', 0.675, 2.01),
('XTZ', 0.700, 2.18),
('XTZ', 0.725, 2.40),
('XTZ', 0.750, 2.65),
('XTZ', 0.775, 2.91),
('XTZ', 0.800, 3.21),
('XTZ', 0.825, 3.54),
('XTZ', 0.850, 3.90),
('XTZ', 0.875, 4.31),
('XTZ', 0.900, 4.75),
('XTZ', 0.925, 5.24),
('XTZ', 0.950, 5.79),
('XTZ', 0.975, 6.40),
('XTZ', 1.000, 7.08)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- XTZ Fiat Risk Values (detailed price/risk pairs for precise interpolation)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('XTZ', 0.079, 0.64),
('XTZ', 0.194, 0.81),
('XTZ', 0.292, 0.97),
('XTZ', 0.447, 1.30),
('XTZ', 0.509, 1.47),
('XTZ', 0.566, 1.63),
('XTZ', 0.616, 1.80),
('XTZ', 0.662, 1.96),
('XTZ', 0.693, 2.13),
('XTZ', 0.713, 2.29),
('XTZ', 0.731, 2.46),
('XTZ', 0.747, 2.62),
('XTZ', 0.763, 2.79),
('XTZ', 0.778, 2.95),
('XTZ', 0.792, 3.12),
('XTZ', 0.805, 3.28),
('XTZ', 0.818, 3.45),
('XTZ', 0.830, 3.61),
('XTZ', 0.841, 3.78),
('XTZ', 0.852, 3.94),
('XTZ', 0.863, 4.11),
('XTZ', 0.873, 4.27),
('XTZ', 0.882, 4.44),
('XTZ', 0.892, 4.60),
('XTZ', 0.901, 4.77),
('XTZ', 0.909, 4.93),
('XTZ', 0.918, 5.10),
('XTZ', 0.926, 5.26),
('XTZ', 0.934, 5.43),
('XTZ', 0.941, 5.59),
('XTZ', 0.948, 5.76),
('XTZ', 0.955, 5.92),
('XTZ', 0.962, 6.09),
('XTZ', 0.969, 6.25),
('XTZ', 0.976, 6.42),
('XTZ', 0.982, 6.58),
('XTZ', 0.988, 6.75),
('XTZ', 0.994, 6.91)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- ================================
-- AAVE Risk Data - Current Price: $308.65 (Risk: 0.595)
-- Source: IntoTheCryptoverse - Extracted: 2025-09-15
-- ================================

-- AAVE Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('AAVE', 0.000, 65.41),
('AAVE', 0.025, 72.37),
('AAVE', 0.050, 80.12),
('AAVE', 0.075, 88.64),
('AAVE', 0.100, 98.17),
('AAVE', 0.125, 108.68),
('AAVE', 0.150, 120.38),
('AAVE', 0.175, 131.11),
('AAVE', 0.200, 137.93),
('AAVE', 0.225, 145.12),
('AAVE', 0.250, 152.65),
('AAVE', 0.275, 160.63),
('AAVE', 0.300, 168.97),
('AAVE', 0.325, 177.79),
('AAVE', 0.350, 187.06),
('AAVE', 0.375, 196.85),
('AAVE', 0.400, 207.18),
('AAVE', 0.425, 218.00),
('AAVE', 0.450, 229.44),
('AAVE', 0.475, 241.41),
('AAVE', 0.500, 254.09),
('AAVE', 0.525, 267.47),
('AAVE', 0.550, 281.57),
('AAVE', 0.575, 296.38),
('AAVE', 0.595, 308.65),  -- Current price/risk
('AAVE', 0.600, 312.07),
('AAVE', 0.625, 336.01),
('AAVE', 0.650, 371.48),
('AAVE', 0.675, 410.49),
('AAVE', 0.700, 453.76),
('AAVE', 0.725, 501.64),
('AAVE', 0.750, 554.84),
('AAVE', 0.775, 613.36),
('AAVE', 0.800, 678.26),
('AAVE', 0.825, 749.90),
('AAVE', 0.850, 829.35),
('AAVE', 0.875, 917.30),
('AAVE', 0.900, 1014.48),
('AAVE', 0.925, 1121.59),
('AAVE', 0.950, 1240.76),
('AAVE', 0.975, 1371.98),
('AAVE', 1.000, 1518.10)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- AAVE Fiat Risk Values (detailed price/risk pairs for precise interpolation)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('AAVE', 0.109, 101.72),
('AAVE', 0.315, 174.36),
('AAVE', 0.408, 210.68),
('AAVE', 0.486, 246.99),
('AAVE', 0.553, 283.31),
('AAVE', 0.612, 319.63),
('AAVE', 0.639, 355.95),
('AAVE', 0.664, 392.26),
('AAVE', 0.686, 428.58),
('AAVE', 0.706, 464.90),
('AAVE', 0.742, 537.53),
('AAVE', 0.758, 573.85),
('AAVE', 0.774, 610.17),
('AAVE', 0.788, 646.48),
('AAVE', 0.802, 682.80),
('AAVE', 0.815, 719.12),
('AAVE', 0.827, 755.44),
('AAVE', 0.838, 791.75),
('AAVE', 0.860, 864.39),
('AAVE', 0.871, 900.71),
('AAVE', 0.880, 937.02),
('AAVE', 0.890, 973.34),
('AAVE', 0.899, 1009.66),
('AAVE', 0.908, 1045.98),
('AAVE', 0.916, 1082.29),
('AAVE', 0.924, 1118.61),
('AAVE', 0.932, 1154.93),
('AAVE', 0.940, 1191.24),
('AAVE', 0.947, 1227.56),
('AAVE', 0.955, 1263.88),
('AAVE', 0.962, 1300.20),
('AAVE', 0.968, 1336.51),
('AAVE', 0.982, 1409.15),
('AAVE', 0.988, 1445.47),
('AAVE', 0.994, 1481.78)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- =======================
-- LTC DATA
-- =======================
-- Current price: $115.61 at risk 0.514
-- Source: https://app.intothecryptoverse.com/assets/litecoin/risk

-- LTC Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('LTC', 0.000, 20.09),
('LTC', 0.025, 22.48),
('LTC', 0.050, 25.18),
('LTC', 0.075, 28.18),
('LTC', 0.100, 31.55),
('LTC', 0.125, 35.31),
('LTC', 0.150, 39.55),
('LTC', 0.175, 44.27),
('LTC', 0.200, 49.63),
('LTC', 0.225, 55.58),
('LTC', 0.250, 62.26),
('LTC', 0.275, 67.07),
('LTC', 0.300, 70.98),
('LTC', 0.325, 75.10),
('LTC', 0.350, 79.46),
('LTC', 0.375, 84.09),
('LTC', 0.400, 89.00),
('LTC', 0.425, 94.20),
('LTC', 0.450, 99.67),
('LTC', 0.475, 105.51),
('LTC', 0.500, 111.64),
('LTC', 0.514, 115.61),
('LTC', 0.525, 119.22),
('LTC', 0.550, 133.30),
('LTC', 0.575, 149.18),
('LTC', 0.600, 166.86),
('LTC', 0.625, 186.59),
('LTC', 0.650, 208.73),
('LTC', 0.675, 233.51),
('LTC', 0.700, 261.42),
('LTC', 0.725, 292.46),
('LTC', 0.750, 327.11),
('LTC', 0.775, 366.09),
('LTC', 0.800, 409.39),
('LTC', 0.825, 458.00),
('LTC', 0.850, 512.37),
('LTC', 0.875, 573.49),
('LTC', 0.900, 641.34),
('LTC', 0.925, 717.85),
('LTC', 0.950, 803.03),
('LTC', 0.975, 898.79),
('LTC', 1.000, 1005.62)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- LTC Fiat Risk Values (detailed price/risk pairs)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('LTC', 0.000, 20.09),
('LTC', 0.177, 44.73),
('LTC', 0.290, 69.37),
('LTC', 0.424, 94.01),
('LTC', 0.514, 115.61),
('LTC', 0.524, 118.65),
('LTC', 0.566, 143.28),
('LTC', 0.601, 167.92),
('LTC', 0.632, 192.56),
('LTC', 0.659, 217.20),
('LTC', 0.683, 241.84),
('LTC', 0.704, 266.47),
('LTC', 0.724, 291.11),
('LTC', 0.742, 315.75),
('LTC', 0.759, 340.39),
('LTC', 0.774, 365.03),
('LTC', 0.789, 389.66),
('LTC', 0.803, 414.30),
('LTC', 0.816, 438.94),
('LTC', 0.828, 463.58),
('LTC', 0.839, 488.22),
('LTC', 0.850, 512.86),
('LTC', 0.861, 537.49),
('LTC', 0.871, 562.13),
('LTC', 0.880, 586.77),
('LTC', 0.889, 611.41),
('LTC', 0.898, 636.05),
('LTC', 0.907, 660.68),
('LTC', 0.915, 685.32),
('LTC', 0.923, 709.96),
('LTC', 0.930, 734.60),
('LTC', 0.937, 759.24),
('LTC', 0.945, 783.87),
('LTC', 0.951, 808.51),
('LTC', 0.958, 833.15),
('LTC', 0.965, 857.79),
('LTC', 0.971, 882.43),
('LTC', 0.977, 907.06),
('LTC', 0.983, 931.70),
('LTC', 0.989, 956.34),
('LTC', 0.994, 980.98),
('LTC', 1.000, 1005.62)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- =======================
-- XMR DATA
-- =======================
-- Current price: $307.59 at risk 0.563
-- Source: https://app.intothecryptoverse.com/assets/monero/risk

-- XMR Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('XMR', 0.000, 74.11),
('XMR', 0.025, 82.45),
('XMR', 0.050, 91.70),
('XMR', 0.075, 101.98),
('XMR', 0.100, 113.45),
('XMR', 0.125, 120.88),
('XMR', 0.150, 127.44),
('XMR', 0.175, 134.41),
('XMR', 0.200, 141.78),
('XMR', 0.225, 149.54),
('XMR', 0.250, 157.71),
('XMR', 0.275, 166.33),
('XMR', 0.300, 175.41),
('XMR', 0.325, 185.00),
('XMR', 0.350, 195.11),
('XMR', 0.375, 205.79),
('XMR', 0.400, 217.03),
('XMR', 0.425, 228.91),
('XMR', 0.450, 241.42),
('XMR', 0.475, 254.66),
('XMR', 0.500, 268.60),
('XMR', 0.525, 283.33),
('XMR', 0.550, 298.86),
('XMR', 0.563, 307.59),
('XMR', 0.575, 318.73),
('XMR', 0.600, 354.59),
('XMR', 0.625, 394.33),
('XMR', 0.650, 438.41),
('XMR', 0.675, 487.52),
('XMR', 0.700, 542.34),
('XMR', 0.725, 603.09),
('XMR', 0.750, 670.70),
('XMR', 0.775, 746.07),
('XMR', 0.800, 829.67),
('XMR', 0.825, 922.86),
('XMR', 0.850, 1026.10),
('XMR', 0.875, 1142.12),
('XMR', 0.900, 1270.03),
('XMR', 0.925, 1412.55),
('XMR', 0.950, 1571.52),
('XMR', 0.975, 1747.85),
('XMR', 1.000, 1945.19)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- XMR Fiat Risk Values (detailed price/risk pairs)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('XMR', 0.000, 74.11),
('XMR', 0.125, 120.89),
('XMR', 0.279, 167.67),
('XMR', 0.394, 214.44),
('XMR', 0.487, 261.22),
('XMR', 0.563, 307.59),
('XMR', 0.564, 308.00),
('XMR', 0.600, 354.77),
('XMR', 0.629, 401.55),
('XMR', 0.655, 448.33),
('XMR', 0.679, 495.10),
('XMR', 0.700, 541.88),
('XMR', 0.719, 588.66),
('XMR', 0.737, 635.44),
('XMR', 0.754, 682.21),
('XMR', 0.770, 728.99),
('XMR', 0.784, 775.77),
('XMR', 0.798, 822.54),
('XMR', 0.811, 869.32),
('XMR', 0.823, 916.10),
('XMR', 0.835, 962.87),
('XMR', 0.846, 1009.65),
('XMR', 0.857, 1056.43),
('XMR', 0.867, 1103.20),
('XMR', 0.877, 1149.98),
('XMR', 0.886, 1196.76),
('XMR', 0.895, 1243.54),
('XMR', 0.904, 1290.31),
('XMR', 0.912, 1337.09),
('XMR', 0.920, 1383.87),
('XMR', 0.928, 1430.64),
('XMR', 0.935, 1477.42),
('XMR', 0.943, 1524.20),
('XMR', 0.950, 1570.97),
('XMR', 0.957, 1617.75),
('XMR', 0.963, 1664.53),
('XMR', 0.970, 1711.31),
('XMR', 0.976, 1758.08),
('XMR', 0.982, 1804.86),
('XMR', 0.988, 1851.64),
('XMR', 0.994, 1898.41),
('XMR', 1.000, 1945.19)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- =======================
-- XLM DATA
-- =======================
-- Current price: $0.392 at risk 0.608
-- Source: https://app.intothecryptoverse.com/assets/stellar/risk

-- XLM Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('XLM', 0.000, 0.074),
('XLM', 0.025, 0.083),
('XLM', 0.050, 0.092),
('XLM', 0.075, 0.103),
('XLM', 0.100, 0.116),
('XLM', 0.125, 0.130),
('XLM', 0.150, 0.139),
('XLM', 0.175, 0.147),
('XLM', 0.200, 0.156),
('XLM', 0.225, 0.165),
('XLM', 0.250, 0.174),
('XLM', 0.275, 0.185),
('XLM', 0.300, 0.195),
('XLM', 0.325, 0.207),
('XLM', 0.350, 0.219),
('XLM', 0.375, 0.231),
('XLM', 0.400, 0.245),
('XLM', 0.425, 0.259),
('XLM', 0.450, 0.274),
('XLM', 0.475, 0.290),
('XLM', 0.500, 0.307),
('XLM', 0.525, 0.325),
('XLM', 0.550, 0.344),
('XLM', 0.575, 0.364),
('XLM', 0.600, 0.385),
('XLM', 0.608, 0.392),
('XLM', 0.625, 0.407),
('XLM', 0.650, 0.448),
('XLM', 0.675, 0.501),
('XLM', 0.700, 0.561),
('XLM', 0.725, 0.628),
('XLM', 0.750, 0.703),
('XLM', 0.775, 0.786),
('XLM', 0.800, 0.880),
('XLM', 0.825, 0.985),
('XLM', 0.850, 1.102),
('XLM', 0.875, 1.233),
('XLM', 0.900, 1.381),
('XLM', 0.925, 1.546),
('XLM', 0.950, 1.730),
('XLM', 0.975, 1.937),
('XLM', 1.000, 2.168)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- XLM Fiat Risk Values (detailed price/risk pairs)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('XLM', 0.000, 0.074),
('XLM', 0.119, 0.126),
('XLM', 0.260, 0.178),
('XLM', 0.374, 0.231),
('XLM', 0.464, 0.283),
('XLM', 0.539, 0.335),
('XLM', 0.603, 0.388),
('XLM', 0.608, 0.392),
('XLM', 0.646, 0.440),
('XLM', 0.671, 0.493),
('XLM', 0.694, 0.545),
('XLM', 0.714, 0.597),
('XLM', 0.733, 0.650),
('XLM', 0.750, 0.702),
('XLM', 0.766, 0.754),
('XLM', 0.781, 0.807),
('XLM', 0.795, 0.859),
('XLM', 0.808, 0.911),
('XLM', 0.820, 0.964),
('XLM', 0.832, 1.016),
('XLM', 0.843, 1.069),
('XLM', 0.854, 1.121),
('XLM', 0.864, 1.173),
('XLM', 0.874, 1.226),
('XLM', 0.883, 1.278),
('XLM', 0.892, 1.330),
('XLM', 0.900, 1.383),
('XLM', 0.909, 1.435),
('XLM', 0.916, 1.487),
('XLM', 0.924, 1.540),
('XLM', 0.932, 1.592),
('XLM', 0.939, 1.644),
('XLM', 0.946, 1.697),
('XLM', 0.952, 1.749),
('XLM', 0.959, 1.802),
('XLM', 0.965, 1.854),
('XLM', 0.971, 1.906),
('XLM', 0.977, 1.959),
('XLM', 0.983, 2.011),
('XLM', 0.989, 2.063),
('XLM', 0.995, 2.116),
('XLM', 1.000, 2.168)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- =======================
-- SUI DATA
-- =======================
-- Current price: $3.73 at risk 0.410
-- Source: https://app.intothecryptoverse.com/assets/sui/risk

-- SUI Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('SUI', 0.000, 1.20),
('SUI', 0.025, 1.34),
('SUI', 0.050, 1.50),
('SUI', 0.075, 1.67),
('SUI', 0.100, 1.87),
('SUI', 0.125, 1.97),
('SUI', 0.150, 2.08),
('SUI', 0.175, 2.20),
('SUI', 0.200, 2.33),
('SUI', 0.225, 2.46),
('SUI', 0.250, 2.60),
('SUI', 0.275, 2.75),
('SUI', 0.300, 2.90),
('SUI', 0.325, 3.07),
('SUI', 0.350, 3.24),
('SUI', 0.375, 3.42),
('SUI', 0.400, 3.62),
('SUI', 0.410, 3.73),
('SUI', 0.425, 3.99),
('SUI', 0.450, 4.46),
('SUI', 0.475, 4.98),
('SUI', 0.500, 5.55),
('SUI', 0.525, 6.20),
('SUI', 0.550, 6.92),
('SUI', 0.575, 7.73),
('SUI', 0.600, 8.63),
('SUI', 0.625, 9.64),
('SUI', 0.650, 10.76),
('SUI', 0.675, 12.02),
('SUI', 0.700, 13.42),
('SUI', 0.725, 14.99),
('SUI', 0.750, 16.75),
('SUI', 0.775, 18.70),
('SUI', 0.800, 20.90),
('SUI', 0.825, 23.37),
('SUI', 0.850, 26.12),
('SUI', 0.875, 29.20),
('SUI', 0.900, 32.64),
('SUI', 0.925, 36.52),
('SUI', 0.950, 40.84),
('SUI', 0.975, 45.73),
('SUI', 1.000, 51.19)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- SUI Fiat Risk Values (detailed price/risk pairs)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('SUI', 0.000, 1.20),
('SUI', 0.224, 2.45),
('SUI', 0.408, 3.70),
('SUI', 0.410, 3.73),
('SUI', 0.474, 4.95),
('SUI', 0.525, 6.20),
('SUI', 0.567, 7.45),
('SUI', 0.602, 8.70),
('SUI', 0.632, 9.95),
('SUI', 0.659, 11.20),
('SUI', 0.683, 12.45),
('SUI', 0.705, 13.70),
('SUI', 0.724, 14.95),
('SUI', 0.743, 16.20),
('SUI', 0.759, 17.45),
('SUI', 0.775, 18.70),
('SUI', 0.789, 19.95),
('SUI', 0.803, 21.20),
('SUI', 0.816, 22.45),
('SUI', 0.828, 23.70),
('SUI', 0.840, 24.95),
('SUI', 0.851, 26.20),
('SUI', 0.861, 27.45),
('SUI', 0.871, 28.70),
('SUI', 0.881, 29.95),
('SUI', 0.890, 31.20),
('SUI', 0.899, 32.45),
('SUI', 0.907, 33.70),
('SUI', 0.915, 34.95),
('SUI', 0.923, 36.20),
('SUI', 0.931, 37.45),
('SUI', 0.938, 38.70),
('SUI', 0.945, 39.95),
('SUI', 0.952, 41.20),
('SUI', 0.958, 42.44),
('SUI', 0.965, 43.69),
('SUI', 0.971, 44.94),
('SUI', 0.977, 46.19),
('SUI', 0.983, 47.44),
('SUI', 0.989, 48.69),
('SUI', 0.995, 49.94),
('SUI', 1.000, 51.19)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- =======================
-- HBAR DATA
-- =======================
-- Current price: $0.243 at risk 0.536
-- Source: https://app.intothecryptoverse.com/assets/hedera-hashgraph/risk

-- HBAR Key Risk Values (0.025 increments)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('HBAR', 0.000, 0.0605),
('HBAR', 0.025, 0.0671),
('HBAR', 0.050, 0.0744),
('HBAR', 0.075, 0.0826),
('HBAR', 0.100, 0.0915),
('HBAR', 0.125, 0.1016),
('HBAR', 0.150, 0.1087),
('HBAR', 0.175, 0.1145),
('HBAR', 0.200, 0.1206),
('HBAR', 0.225, 0.1270),
('HBAR', 0.250, 0.1337),
('HBAR', 0.275, 0.1409),
('HBAR', 0.300, 0.1484),
('HBAR', 0.325, 0.1563),
('HBAR', 0.350, 0.1646),
('HBAR', 0.375, 0.1734),
('HBAR', 0.400, 0.1826),
('HBAR', 0.425, 0.1923),
('HBAR', 0.450, 0.2026),
('HBAR', 0.475, 0.2134),
('HBAR', 0.500, 0.2248),
('HBAR', 0.525, 0.2368),
('HBAR', 0.536, 0.2430),
('HBAR', 0.550, 0.2515),
('HBAR', 0.575, 0.2788),
('HBAR', 0.600, 0.3094),
('HBAR', 0.625, 0.3430),
('HBAR', 0.650, 0.3803),
('HBAR', 0.675, 0.4218),
('HBAR', 0.700, 0.4677),
('HBAR', 0.725, 0.5185),
('HBAR', 0.750, 0.5751),
('HBAR', 0.775, 0.6382),
('HBAR', 0.800, 0.7078),
('HBAR', 0.825, 0.7854),
('HBAR', 0.850, 0.8711),
('HBAR', 0.875, 0.9667),
('HBAR', 0.900, 1.0722),
('HBAR', 0.925, 1.1900),
('HBAR', 0.950, 1.3207),
('HBAR', 0.975, 1.4652),
('HBAR', 1.000, 1.6266)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- HBAR Fiat Risk Values (detailed price/risk pairs)
INSERT INTO risk_metric_grid (symbol, risk_value, price_usd) VALUES
('HBAR', 0.000, 0.0605),
('HBAR', 0.120, 0.0996),
('HBAR', 0.268, 0.1388),
('HBAR', 0.388, 0.1779),
('HBAR', 0.483, 0.2171),
('HBAR', 0.536, 0.2430),
('HBAR', 0.554, 0.2562),
('HBAR', 0.589, 0.2954),
('HBAR', 0.619, 0.3345),
('HBAR', 0.646, 0.3737),
('HBAR', 0.670, 0.4129),
('HBAR', 0.692, 0.4520),
('HBAR', 0.712, 0.4912),
('HBAR', 0.730, 0.5303),
('HBAR', 0.748, 0.5695),
('HBAR', 0.764, 0.6086),
('HBAR', 0.779, 0.6478),
('HBAR', 0.793, 0.6869),
('HBAR', 0.806, 0.7261),
('HBAR', 0.819, 0.7652),
('HBAR', 0.831, 0.8044),
('HBAR', 0.842, 0.8435),
('HBAR', 0.853, 0.8827),
('HBAR', 0.864, 0.9218),
('HBAR', 0.874, 0.9610),
('HBAR', 0.883, 1.0002),
('HBAR', 0.893, 1.0393),
('HBAR', 0.901, 1.0785),
('HBAR', 0.910, 1.1176),
('HBAR', 0.918, 1.1568),
('HBAR', 0.926, 1.1959),
('HBAR', 0.934, 1.2351),
('HBAR', 0.941, 1.2742),
('HBAR', 0.949, 1.3134),
('HBAR', 0.956, 1.3525),
('HBAR', 0.963, 1.3917),
('HBAR', 0.969, 1.4308),
('HBAR', 0.976, 1.4700),
('HBAR', 0.982, 1.5091),
('HBAR', 0.988, 1.5483),
('HBAR', 0.994, 1.5874),
('HBAR', 1.000, 1.6266)
ON CONFLICT (symbol, risk_value) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    updated_at = CURRENT_TIMESTAMP;

-- ==================== TEST QUERIES ====================
SELECT '=== BTC at $150,000 ===' as test;
SELECT * FROM get_risk_for_price('BTC', 150000);

SELECT '=== SOL at $300 ===' as test;
SELECT * FROM get_risk_for_price('SOL', 300);

SELECT '=== Get BTC price at 0.500 risk ===' as test;
SELECT * FROM get_price_for_risk('BTC', 0.500);

SELECT '=== Get SOL price at 0.750 risk ===' as test;
SELECT * FROM get_price_for_risk('SOL', 0.750);

-- View summary
SELECT '=== Symbol Summary ===' as test;
SELECT
    symbol,
    COUNT(*) as data_points,
    MIN(price_usd) as min_price,
    MAX(price_usd) as max_price,
    MIN(risk_value) as min_risk,
    MAX(risk_value) as max_risk
FROM risk_metric_grid
GROUP BY symbol
ORDER BY symbol;