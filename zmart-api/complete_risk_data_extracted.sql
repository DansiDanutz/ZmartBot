-- ========================================================================
-- COMPLETE RISK METRIC GRID DATA FROM INTOTHECRYPTOVERSE
-- ========================================================================
-- Source: IntoTheCryptoverse Dashboard (app.intothecryptoverse.com)
-- Database: PostgreSQL/Supabase
-- Table: risk_metric_grid
-- Total Symbols: 3 (BNB, SHIB, TON)
-- Total Rows: 336 (168 BNB + 84 SHIB + 84 TON)
-- ========================================================================

-- Create table if not exists
CREATE TABLE IF NOT EXISTS public.risk_metric_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price_point INTEGER NOT NULL,
    risk_value DECIMAL(5,3) NOT NULL,
    price_usd DECIMAL(20,8) NOT NULL,
    risk_band VARCHAR(10) NOT NULL,
    risk_type VARCHAR(20) DEFAULT 'KEY_RISK',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, price_point, risk_type)
);

-- Clear existing data for these symbols
DELETE FROM risk_metric_grid WHERE symbol IN ('BNB', 'SHIB', 'TON');

-- ==================== BNB DATA (Current: $929.34 at risk 0.527) ====================

-- BNB Key Risks (43 rows)
INSERT INTO risk_metric_grid (symbol, price_point, risk_value, price_usd, risk_band, risk_type) VALUES
('BNB', 1, 0.000, 320.60, '0.0-0.1', 'KEY_RISK'),
('BNB', 2, 0.025, 336.57, '0.0-0.1', 'KEY_RISK'),
('BNB', 3, 0.050, 353.15, '0.0-0.1', 'KEY_RISK'),
('BNB', 4, 0.075, 370.81, '0.0-0.1', 'KEY_RISK'),
('BNB', 5, 0.100, 389.24, '0.1-0.2', 'KEY_RISK'),
('BNB', 6, 0.125, 408.58, '0.1-0.2', 'KEY_RISK'),
('BNB', 7, 0.150, 428.85, '0.1-0.2', 'KEY_RISK'),
('BNB', 8, 0.175, 450.19, '0.1-0.2', 'KEY_RISK'),
('BNB', 9, 0.200, 472.61, '0.2-0.3', 'KEY_RISK'),
('BNB', 10, 0.225, 496.25, '0.2-0.3', 'KEY_RISK'),
('BNB', 11, 0.250, 521.12, '0.2-0.3', 'KEY_RISK'),
('BNB', 12, 0.275, 547.23, '0.2-0.3', 'KEY_RISK'),
('BNB', 13, 0.300, 574.56, '0.3-0.4', 'KEY_RISK'),
('BNB', 14, 0.325, 603.42, '0.3-0.4', 'KEY_RISK'),
('BNB', 15, 0.350, 633.67, '0.3-0.4', 'KEY_RISK'),
('BNB', 16, 0.375, 665.45, '0.3-0.4', 'KEY_RISK'),
('BNB', 17, 0.400, 698.92, '0.4-0.5', 'KEY_RISK'),
('BNB', 18, 0.425, 734.23, '0.4-0.5', 'KEY_RISK'),
('BNB', 19, 0.450, 771.24, '0.4-0.5', 'KEY_RISK'),
('BNB', 20, 0.475, 810.08, '0.4-0.5', 'KEY_RISK'),
('BNB', 21, 0.500, 853.99, '0.5-0.6', 'KEY_RISK'),
('BNB', 22, 0.525, 923.09, '0.5-0.6', 'KEY_RISK'),
('BNB', 23, 0.527, 929.34, '0.5-0.6', 'KEY_RISK'),  -- CURRENT
('BNB', 24, 0.550, 1012.14, '0.5-0.6', 'KEY_RISK'),
('BNB', 25, 0.575, 1110.40, '0.5-0.6', 'KEY_RISK'),
('BNB', 26, 0.600, 1217.26, '0.6-0.7', 'KEY_RISK'),
('BNB', 27, 0.625, 1335.18, '0.6-0.7', 'KEY_RISK'),
('BNB', 28, 0.650, 1464.15, '0.6-0.7', 'KEY_RISK'),
('BNB', 29, 0.675, 1606.64, '0.6-0.7', 'KEY_RISK'),
('BNB', 30, 0.700, 1761.40, '0.7-0.8', 'KEY_RISK'),
('BNB', 31, 0.725, 1932.14, '0.7-0.8', 'KEY_RISK'),
('BNB', 32, 0.750, 2118.84, '0.7-0.8', 'KEY_RISK'),
('BNB', 33, 0.775, 2325.19, '0.7-0.8', 'KEY_RISK'),
('BNB', 34, 0.800, 2549.97, '0.8-0.9', 'KEY_RISK'),
('BNB', 35, 0.825, 2796.86, '0.8-0.9', 'KEY_RISK'),
('BNB', 36, 0.850, 3069.54, '0.8-0.9', 'KEY_RISK'),
('BNB', 37, 0.875, 3366.79, '0.8-0.9', 'KEY_RISK'),
('BNB', 38, 0.900, 3693.52, '0.9-1.0', 'KEY_RISK'),
('BNB', 39, 0.925, 4052.18, '0.9-1.0', 'KEY_RISK'),
('BNB', 40, 0.950, 4445.24, '0.9-1.0', 'KEY_RISK'),
('BNB', 41, 0.975, 4877.60, '0.9-1.0', 'KEY_RISK'),
('BNB', 42, 1.000, 5351.73, '0.9-1.0', 'KEY_RISK')
ON CONFLICT (symbol, price_point, risk_type) DO UPDATE SET
    risk_value = EXCLUDED.risk_value,
    price_usd = EXCLUDED.price_usd,
    risk_band = EXCLUDED.risk_band;

-- BNB Fiat Risks (42 rows)
INSERT INTO risk_metric_grid (symbol, price_point, risk_value, price_usd, risk_band, risk_type) VALUES
('BNB', 43, 0.000, 320.60, '0.0-0.1', 'FIAT_RISK'),
('BNB', 44, 0.171, 446.38, '0.1-0.2', 'FIAT_RISK'),
('BNB', 45, 0.298, 572.16, '0.2-0.3', 'FIAT_RISK'),
('BNB', 46, 0.399, 697.94, '0.3-0.4', 'FIAT_RISK'),
('BNB', 47, 0.483, 823.72, '0.4-0.5', 'FIAT_RISK'),
('BNB', 48, 0.527, 929.34, '0.5-0.6', 'FIAT_RISK'),  -- CURRENT
('BNB', 49, 0.533, 949.49, '0.5-0.6', 'FIAT_RISK'),
('BNB', 50, 0.566, 1075.27, '0.5-0.6', 'FIAT_RISK'),
('BNB', 51, 0.596, 1201.05, '0.5-0.6', 'FIAT_RISK'),
('BNB', 52, 0.623, 1326.83, '0.6-0.7', 'FIAT_RISK'),
('BNB', 53, 0.648, 1452.61, '0.6-0.7', 'FIAT_RISK'),
('BNB', 54, 0.670, 1578.38, '0.6-0.7', 'FIAT_RISK'),
('BNB', 55, 0.691, 1704.16, '0.6-0.7', 'FIAT_RISK'),
('BNB', 56, 0.710, 1829.94, '0.7-0.8', 'FIAT_RISK'),
('BNB', 57, 0.728, 1955.72, '0.7-0.8', 'FIAT_RISK'),
('BNB', 58, 0.745, 2081.50, '0.7-0.8', 'FIAT_RISK'),
('BNB', 59, 0.761, 2207.27, '0.7-0.8', 'FIAT_RISK'),
('BNB', 60, 0.776, 2333.05, '0.7-0.8', 'FIAT_RISK'),
('BNB', 61, 0.790, 2458.83, '0.7-0.8', 'FIAT_RISK'),
('BNB', 62, 0.804, 2584.61, '0.8-0.9', 'FIAT_RISK'),
('BNB', 63, 0.816, 2710.39, '0.8-0.9', 'FIAT_RISK'),
('BNB', 64, 0.829, 2836.17, '0.8-0.9', 'FIAT_RISK'),
('BNB', 65, 0.840, 2961.94, '0.8-0.9', 'FIAT_RISK'),
('BNB', 66, 0.852, 3087.72, '0.8-0.9', 'FIAT_RISK'),
('BNB', 67, 0.862, 3213.50, '0.8-0.9', 'FIAT_RISK'),
('BNB', 68, 0.873, 3339.28, '0.8-0.9', 'FIAT_RISK'),
('BNB', 69, 0.883, 3465.06, '0.8-0.9', 'FIAT_RISK'),
('BNB', 70, 0.892, 3590.83, '0.8-0.9', 'FIAT_RISK'),
('BNB', 71, 0.902, 3716.61, '0.9-1.0', 'FIAT_RISK'),
('BNB', 72, 0.911, 3842.39, '0.9-1.0', 'FIAT_RISK'),
('BNB', 73, 0.919, 3968.17, '0.9-1.0', 'FIAT_RISK'),
('BNB', 74, 0.928, 4093.95, '0.9-1.0', 'FIAT_RISK'),
('BNB', 75, 0.936, 4219.72, '0.9-1.0', 'FIAT_RISK'),
('BNB', 76, 0.944, 4345.50, '0.9-1.0', 'FIAT_RISK'),
('BNB', 77, 0.952, 4471.28, '0.9-1.0', 'FIAT_RISK'),
('BNB', 78, 0.959, 4597.06, '0.9-1.0', 'FIAT_RISK'),
('BNB', 79, 0.966, 4722.84, '0.9-1.0', 'FIAT_RISK'),
('BNB', 80, 0.973, 4848.61, '0.9-1.0', 'FIAT_RISK'),
('BNB', 81, 0.980, 4974.39, '0.9-1.0', 'FIAT_RISK'),
('BNB', 82, 0.987, 5100.17, '0.9-1.0', 'FIAT_RISK'),
('BNB', 83, 0.994, 5225.95, '0.9-1.0', 'FIAT_RISK'),
('BNB', 84, 1.000, 5351.73, '0.9-1.0', 'FIAT_RISK')
ON CONFLICT (symbol, price_point, risk_type) DO UPDATE SET
    risk_value = EXCLUDED.risk_value,
    price_usd = EXCLUDED.price_usd,
    risk_band = EXCLUDED.risk_band;

-- BNB BTC Risks (42 rows)
INSERT INTO risk_metric_grid (symbol, price_point, risk_value, price_usd, risk_band, risk_type) VALUES
('BNB', 85, 0.000, 0.005484, '0.0-0.1', 'BTC_RISK'),
('BNB', 86, 0.025, 0.005776, '0.0-0.1', 'BTC_RISK'),
('BNB', 87, 0.050, 0.006043, '0.0-0.1', 'BTC_RISK'),
('BNB', 88, 0.075, 0.006202, '0.0-0.1', 'BTC_RISK'),
('BNB', 89, 0.100, 0.006366, '0.1-0.2', 'BTC_RISK'),
('BNB', 90, 0.125, 0.006533, '0.1-0.2', 'BTC_RISK'),
('BNB', 91, 0.150, 0.006705, '0.1-0.2', 'BTC_RISK'),
('BNB', 92, 0.175, 0.006881, '0.1-0.2', 'BTC_RISK'),
('BNB', 93, 0.200, 0.007061, '0.2-0.3', 'BTC_RISK'),
('BNB', 94, 0.225, 0.007247, '0.2-0.3', 'BTC_RISK'),
('BNB', 95, 0.250, 0.007438, '0.2-0.3', 'BTC_RISK'),
('BNB', 96, 0.275, 0.007633, '0.2-0.3', 'BTC_RISK'),
('BNB', 97, 0.300, 0.007834, '0.3-0.4', 'BTC_RISK'),
('BNB', 98, 0.325, 0.008040, '0.3-0.4', 'BTC_RISK'),
('BNB', 99, 0.329, 0.008073, '0.3-0.4', 'BTC_RISK'),  -- CURRENT
('BNB', 100, 0.350, 0.008251, '0.3-0.4', 'BTC_RISK'),
('BNB', 101, 0.375, 0.008468, '0.3-0.4', 'BTC_RISK'),
('BNB', 102, 0.400, 0.008691, '0.4-0.5', 'BTC_RISK'),
('BNB', 103, 0.425, 0.008920, '0.4-0.5', 'BTC_RISK'),
('BNB', 104, 0.450, 0.009154, '0.4-0.5', 'BTC_RISK'),
('BNB', 105, 0.475, 0.009395, '0.4-0.5', 'BTC_RISK'),
('BNB', 106, 0.500, 0.009802, '0.5-0.6', 'BTC_RISK'),
('BNB', 107, 0.525, 0.010325, '0.5-0.6', 'BTC_RISK'),
('BNB', 108, 0.550, 0.010873, '0.5-0.6', 'BTC_RISK'),
('BNB', 109, 0.575, 0.011453, '0.5-0.6', 'BTC_RISK'),
('BNB', 110, 0.600, 0.012066, '0.6-0.7', 'BTC_RISK'),
('BNB', 111, 0.625, 0.012705, '0.6-0.7', 'BTC_RISK'),
('BNB', 112, 0.650, 0.013383, '0.6-0.7', 'BTC_RISK'),
('BNB', 113, 0.675, 0.014099, '0.6-0.7', 'BTC_RISK'),
('BNB', 114, 0.700, 0.014847, '0.7-0.8', 'BTC_RISK'),
('BNB', 115, 0.725, 0.015639, '0.7-0.8', 'BTC_RISK'),
('BNB', 116, 0.750, 0.016474, '0.7-0.8', 'BTC_RISK'),
('BNB', 117, 0.775, 0.017352, '0.7-0.8', 'BTC_RISK'),
('BNB', 118, 0.800, 0.018279, '0.8-0.9', 'BTC_RISK'),
('BNB', 119, 0.825, 0.019250, '0.8-0.9', 'BTC_RISK'),
('BNB', 120, 0.850, 0.020274, '0.8-0.9', 'BTC_RISK'),
('BNB', 121, 0.875, 0.021359, '0.8-0.9', 'BTC_RISK'),
('BNB', 122, 0.900, 0.022497, '0.9-1.0', 'BTC_RISK'),
('BNB', 123, 0.925, 0.023696, '0.9-1.0', 'BTC_RISK'),
('BNB', 124, 0.950, 0.024959, '0.9-1.0', 'BTC_RISK'),
('BNB', 125, 0.975, 0.026293, '0.9-1.0', 'BTC_RISK'),
('BNB', 126, 1.000, 0.027691, '0.9-1.0', 'BTC_RISK')
ON CONFLICT (symbol, price_point, risk_type) DO UPDATE SET
    risk_value = EXCLUDED.risk_value,
    price_usd = EXCLUDED.price_usd,
    risk_band = EXCLUDED.risk_band;

-- BNB ETH Risks (41 rows)
INSERT INTO risk_metric_grid (symbol, price_point, risk_value, price_usd, risk_band, risk_type) VALUES
('BNB', 127, 0.000, 0.117218, '0.0-0.1', 'ETH_RISK'),
('BNB', 128, 0.025, 0.124030, '0.0-0.1', 'ETH_RISK'),
('BNB', 129, 0.050, 0.128571, '0.0-0.1', 'ETH_RISK'),
('BNB', 130, 0.075, 0.132229, '0.0-0.1', 'ETH_RISK'),
('BNB', 131, 0.100, 0.136014, '0.1-0.2', 'ETH_RISK'),
('BNB', 132, 0.125, 0.139899, '0.1-0.2', 'ETH_RISK'),
('BNB', 133, 0.150, 0.143911, '0.1-0.2', 'ETH_RISK'),
('BNB', 134, 0.175, 0.148024, '0.1-0.2', 'ETH_RISK'),
('BNB', 135, 0.200, 0.152237, '0.2-0.3', 'ETH_RISK'),
('BNB', 136, 0.225, 0.156602, '0.2-0.3', 'ETH_RISK'),
('BNB', 137, 0.250, 0.161068, '0.2-0.3', 'ETH_RISK'),
('BNB', 138, 0.275, 0.165685, '0.2-0.3', 'ETH_RISK'),
('BNB', 139, 0.300, 0.170403, '0.3-0.4', 'ETH_RISK'),
('BNB', 140, 0.325, 0.175297, '0.3-0.4', 'ETH_RISK'),
('BNB', 141, 0.350, 0.180293, '0.3-0.4', 'ETH_RISK'),
('BNB', 142, 0.375, 0.185465, '0.3-0.4', 'ETH_RISK'),
('BNB', 143, 0.400, 0.190789, '0.4-0.5', 'ETH_RISK'),
('BNB', 144, 0.425, 0.196238, '0.4-0.5', 'ETH_RISK'),
('BNB', 145, 0.449, 0.201552, '0.4-0.5', 'ETH_RISK'),  -- CURRENT
('BNB', 146, 0.450, 0.201839, '0.4-0.5', 'ETH_RISK'),
('BNB', 147, 0.475, 0.207592, '0.4-0.5', 'ETH_RISK'),
('BNB', 148, 0.500, 0.213546, '0.5-0.6', 'ETH_RISK'),
('BNB', 149, 0.525, 0.219652, '0.5-0.6', 'ETH_RISK'),
('BNB', 150, 0.550, 0.225959, '0.5-0.6', 'ETH_RISK'),
('BNB', 151, 0.575, 0.232418, '0.5-0.6', 'ETH_RISK'),
('BNB', 152, 0.600, 0.239079, '0.6-0.7', 'ETH_RISK'),
('BNB', 153, 0.625, 0.245891, '0.6-0.7', 'ETH_RISK'),
('BNB', 154, 0.650, 0.252956, '0.6-0.7', 'ETH_RISK'),
('BNB', 155, 0.675, 0.260171, '0.6-0.7', 'ETH_RISK'),
('BNB', 156, 0.700, 0.269809, '0.7-0.8', 'ETH_RISK'),
('BNB', 157, 0.725, 0.285553, '0.7-0.8', 'ETH_RISK'),
('BNB', 158, 0.750, 0.302003, '0.7-0.8', 'ETH_RISK'),
('BNB', 159, 0.775, 0.319462, '0.7-0.8', 'ETH_RISK'),
('BNB', 160, 0.800, 0.338032, '0.8-0.9', 'ETH_RISK'),
('BNB', 161, 0.825, 0.357610, '0.8-0.9', 'ETH_RISK'),
('BNB', 162, 0.850, 0.378400, '0.8-0.9', 'ETH_RISK'),
('BNB', 163, 0.875, 0.400299, '0.8-0.9', 'ETH_RISK'),
('BNB', 164, 0.900, 0.423410, '0.9-1.0', 'ETH_RISK'),
('BNB', 165, 0.925, 0.448035, '0.9-1.0', 'ETH_RISK'),
('BNB', 166, 0.950, 0.474072, '0.9-1.0', 'ETH_RISK'),
('BNB', 167, 0.975, 0.501523, '0.9-1.0', 'ETH_RISK'),
('BNB', 168, 1.000, 0.530588, '0.9-1.0', 'ETH_RISK')
ON CONFLICT (symbol, price_point, risk_type) DO UPDATE SET
    risk_value = EXCLUDED.risk_value,
    price_usd = EXCLUDED.price_usd,
    risk_band = EXCLUDED.risk_band;

-- ==================== SHIB DATA (Current: $0.0000137 at risk 0.227) ====================

-- SHIB Key Risks (42 rows)
INSERT INTO risk_metric_grid (symbol, price_point, risk_value, price_usd, risk_band, risk_type) VALUES
('SHIB', 1, 0.000, 0.0000045, '0.0-0.1', 'KEY_RISK'),
('SHIB', 2, 0.025, 0.0000052, '0.0-0.1', 'KEY_RISK'),
('SHIB', 3, 0.050, 0.0000059, '0.0-0.1', 'KEY_RISK'),
('SHIB', 4, 0.075, 0.0000067, '0.0-0.1', 'KEY_RISK'),
('SHIB', 5, 0.100, 0.0000077, '0.1-0.2', 'KEY_RISK'),
('SHIB', 6, 0.125, 0.0000088, '0.1-0.2', 'KEY_RISK'),
('SHIB', 7, 0.150, 0.0000100, '0.1-0.2', 'KEY_RISK'),
('SHIB', 8, 0.175, 0.0000115, '0.1-0.2', 'KEY_RISK'),
('SHIB', 9, 0.200, 0.0000127, '0.2-0.3', 'KEY_RISK'),
('SHIB', 10, 0.225, 0.0000136, '0.2-0.3', 'KEY_RISK'),
('SHIB', 11, 0.227, 0.0000137, '0.2-0.3', 'KEY_RISK'),  -- CURRENT
('SHIB', 12, 0.250, 0.0000146, '0.2-0.3', 'KEY_RISK'),
('SHIB', 13, 0.275, 0.0000157, '0.2-0.3', 'KEY_RISK'),
('SHIB', 14, 0.300, 0.0000168, '0.3-0.4', 'KEY_RISK'),
('SHIB', 15, 0.325, 0.0000180, '0.3-0.4', 'KEY_RISK'),
('SHIB', 16, 0.350, 0.0000204, '0.3-0.4', 'KEY_RISK'),
('SHIB', 17, 0.375, 0.0000234, '0.3-0.4', 'KEY_RISK'),
('SHIB', 18, 0.400, 0.0000268, '0.4-0.5', 'KEY_RISK'),
('SHIB', 19, 0.425, 0.0000307, '0.4-0.5', 'KEY_RISK'),
('SHIB', 20, 0.450, 0.0000352, '0.4-0.5', 'KEY_RISK'),
('SHIB', 21, 0.475, 0.0000403, '0.4-0.5', 'KEY_RISK'),
('SHIB', 22, 0.500, 0.0000462, '0.5-0.6', 'KEY_RISK'),
('SHIB', 23, 0.525, 0.0000531, '0.5-0.6', 'KEY_RISK'),
('SHIB', 24, 0.550, 0.0000610, '0.5-0.6', 'KEY_RISK'),
('SHIB', 25, 0.575, 0.0000702, '0.5-0.6', 'KEY_RISK'),
('SHIB', 26, 0.600, 0.0000805, '0.6-0.7', 'KEY_RISK'),
('SHIB', 27, 0.625, 0.0000921, '0.6-0.7', 'KEY_RISK'),
('SHIB', 28, 0.650, 0.0001052, '0.6-0.7', 'KEY_RISK'),
('SHIB', 29, 0.675, 0.0001204, '0.6-0.7', 'KEY_RISK'),
('SHIB', 30, 0.700, 0.0001375, '0.7-0.8', 'KEY_RISK'),
('SHIB', 31, 0.725, 0.0001571, '0.7-0.8', 'KEY_RISK'),
('SHIB', 32, 0.750, 0.0001796, '0.7-0.8', 'KEY_RISK'),
('SHIB', 33, 0.775, 0.0002053, '0.7-0.8', 'KEY_RISK'),
('SHIB', 34, 0.800, 0.0002348, '0.8-0.9', 'KEY_RISK'),
('SHIB', 35, 0.825, 0.0002684, '0.8-0.9', 'KEY_RISK'),
('SHIB', 36, 0.850, 0.0003070, '0.8-0.9', 'KEY_RISK'),
('SHIB', 37, 0.875, 0.0003513, '0.8-0.9', 'KEY_RISK'),
('SHIB', 38, 0.900, 0.0004020, '0.9-1.0', 'KEY_RISK'),
('SHIB', 39, 0.925, 0.0004605, '0.9-1.0', 'KEY_RISK'),
('SHIB', 40, 0.950, 0.0005269, '0.9-1.0', 'KEY_RISK'),
('SHIB', 41, 0.975, 0.0006042, '0.9-1.0', 'KEY_RISK'),
('SHIB', 42, 1.000, 0.0006921, '0.9-1.0', 'KEY_RISK')
ON CONFLICT (symbol, price_point, risk_type) DO UPDATE SET
    risk_value = EXCLUDED.risk_value,
    price_usd = EXCLUDED.price_usd,
    risk_band = EXCLUDED.risk_band;

-- SHIB Fiat Risks (42 rows)
INSERT INTO risk_metric_grid (symbol, price_point, risk_value, price_usd, risk_band, risk_type) VALUES
('SHIB', 43, 0.000, 0.0000045, '0.0-0.1', 'FIAT_RISK'),
('SHIB', 44, 0.227, 0.0000137, '0.2-0.3', 'FIAT_RISK'),  -- CURRENT
('SHIB', 45, 0.361, 0.0000217, '0.3-0.4', 'FIAT_RISK'),
('SHIB', 46, 0.469, 0.0000389, '0.4-0.5', 'FIAT_RISK'),
('SHIB', 47, 0.535, 0.0000561, '0.5-0.6', 'FIAT_RISK'),
('SHIB', 48, 0.583, 0.0000733, '0.5-0.6', 'FIAT_RISK'),
('SHIB', 49, 0.622, 0.0000905, '0.6-0.7', 'FIAT_RISK'),
('SHIB', 50, 0.654, 0.0001077, '0.6-0.7', 'FIAT_RISK'),
('SHIB', 51, 0.682, 0.0001249, '0.6-0.7', 'FIAT_RISK'),
('SHIB', 52, 0.706, 0.0001420, '0.7-0.8', 'FIAT_RISK'),
('SHIB', 53, 0.727, 0.0001592, '0.7-0.8', 'FIAT_RISK'),
('SHIB', 54, 0.747, 0.0001764, '0.7-0.8', 'FIAT_RISK'),
('SHIB', 55, 0.764, 0.0001936, '0.7-0.8', 'FIAT_RISK'),
('SHIB', 56, 0.780, 0.0002108, '0.7-0.8', 'FIAT_RISK'),
('SHIB', 57, 0.795, 0.0002280, '0.7-0.8', 'FIAT_RISK'),
('SHIB', 58, 0.808, 0.0002452, '0.8-0.9', 'FIAT_RISK'),
('SHIB', 59, 0.821, 0.0002624, '0.8-0.9', 'FIAT_RISK'),
('SHIB', 60, 0.832, 0.0002796, '0.8-0.9', 'FIAT_RISK'),
('SHIB', 61, 0.844, 0.0002968, '0.8-0.9', 'FIAT_RISK'),
('SHIB', 62, 0.854, 0.0003139, '0.8-0.9', 'FIAT_RISK'),
('SHIB', 63, 0.864, 0.0003311, '0.8-0.9', 'FIAT_RISK'),
('SHIB', 64, 0.873, 0.0003483, '0.8-0.9', 'FIAT_RISK'),
('SHIB', 65, 0.882, 0.0003655, '0.8-0.9', 'FIAT_RISK'),
('SHIB', 66, 0.891, 0.0003827, '0.8-0.9', 'FIAT_RISK'),
('SHIB', 67, 0.899, 0.0003999, '0.8-0.9', 'FIAT_RISK'),
('SHIB', 68, 0.907, 0.0004171, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 69, 0.914, 0.0004343, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 70, 0.921, 0.0004515, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 71, 0.928, 0.0004687, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 72, 0.935, 0.0004858, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 73, 0.941, 0.0005030, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 74, 0.948, 0.0005202, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 75, 0.954, 0.0005374, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 76, 0.959, 0.0005546, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 77, 0.965, 0.0005718, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 78, 0.970, 0.0005890, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 79, 0.976, 0.0006062, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 80, 0.981, 0.0006234, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 81, 0.986, 0.0006406, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 82, 0.991, 0.0006577, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 83, 0.995, 0.0006749, '0.9-1.0', 'FIAT_RISK'),
('SHIB', 84, 1.000, 0.0006921, '0.9-1.0', 'FIAT_RISK')
ON CONFLICT (symbol, price_point, risk_type) DO UPDATE SET
    risk_value = EXCLUDED.risk_value,
    price_usd = EXCLUDED.price_usd,
    risk_band = EXCLUDED.risk_band;

-- ==================== TON DATA (Current: $3.20 at risk 0.238) ====================

-- TON Key Risks (42 rows)
INSERT INTO risk_metric_grid (symbol, price_point, risk_value, price_usd, risk_band, risk_type) VALUES
('TON', 1, 0.000, 1.45, '0.0-0.1', 'KEY_RISK'),
('TON', 2, 0.025, 1.59, '0.0-0.1', 'KEY_RISK'),
('TON', 3, 0.050, 1.74, '0.0-0.1', 'KEY_RISK'),
('TON', 4, 0.075, 1.90, '0.0-0.1', 'KEY_RISK'),
('TON', 5, 0.100, 2.08, '0.1-0.2', 'KEY_RISK'),
('TON', 6, 0.125, 2.28, '0.1-0.2', 'KEY_RISK'),
('TON', 7, 0.150, 2.49, '0.1-0.2', 'KEY_RISK'),
('TON', 8, 0.175, 2.73, '0.1-0.2', 'KEY_RISK'),
('TON', 9, 0.200, 2.99, '0.2-0.3', 'KEY_RISK'),
('TON', 10, 0.225, 3.13, '0.2-0.3', 'KEY_RISK'),
('TON', 11, 0.238, 3.20, '0.2-0.3', 'KEY_RISK'),  -- CURRENT
('TON', 12, 0.250, 3.27, '0.2-0.3', 'KEY_RISK'),
('TON', 13, 0.275, 3.42, '0.2-0.3', 'KEY_RISK'),
('TON', 14, 0.300, 3.58, '0.3-0.4', 'KEY_RISK'),
('TON', 15, 0.325, 3.75, '0.3-0.4', 'KEY_RISK'),
('TON', 16, 0.350, 3.92, '0.3-0.4', 'KEY_RISK'),
('TON', 17, 0.375, 4.10, '0.3-0.4', 'KEY_RISK'),
('TON', 18, 0.400, 4.29, '0.4-0.5', 'KEY_RISK'),
('TON', 19, 0.425, 4.49, '0.4-0.5', 'KEY_RISK'),
('TON', 20, 0.450, 4.70, '0.4-0.5', 'KEY_RISK'),
('TON', 21, 0.475, 4.96, '0.4-0.5', 'KEY_RISK'),
('TON', 22, 0.500, 5.43, '0.5-0.6', 'KEY_RISK'),
('TON', 23, 0.525, 5.94, '0.5-0.6', 'KEY_RISK'),
('TON', 24, 0.550, 6.51, '0.5-0.6', 'KEY_RISK'),
('TON', 25, 0.575, 7.12, '0.5-0.6', 'KEY_RISK'),
('TON', 26, 0.600, 7.80, '0.6-0.7', 'KEY_RISK'),
('TON', 27, 0.625, 8.53, '0.6-0.7', 'KEY_RISK'),
('TON', 28, 0.650, 9.34, '0.6-0.7', 'KEY_RISK'),
('TON', 29, 0.675, 10.23, '0.6-0.7', 'KEY_RISK'),
('TON', 30, 0.700, 11.20, '0.7-0.8', 'KEY_RISK'),
('TON', 31, 0.725, 12.25, '0.7-0.8', 'KEY_RISK'),
('TON', 32, 0.750, 13.42, '0.7-0.8', 'KEY_RISK'),
('TON', 33, 0.775, 14.69, '0.7-0.8', 'KEY_RISK'),
('TON', 34, 0.800, 16.08, '0.8-0.9', 'KEY_RISK'),
('TON', 35, 0.825, 17.61, '0.8-0.9', 'KEY_RISK'),
('TON', 36, 0.850, 19.28, '0.8-0.9', 'KEY_RISK'),
('TON', 37, 0.875, 21.12, '0.8-0.9', 'KEY_RISK'),
('TON', 38, 0.900, 23.12, '0.9-1.0', 'KEY_RISK'),
('TON', 39, 0.925, 25.33, '0.9-1.0', 'KEY_RISK'),
('TON', 40, 0.950, 27.73, '0.9-1.0', 'KEY_RISK'),
('TON', 41, 0.975, 30.37, '0.9-1.0', 'KEY_RISK'),
('TON', 42, 1.000, 33.26, '0.9-1.0', 'KEY_RISK')
ON CONFLICT (symbol, price_point, risk_type) DO UPDATE SET
    risk_value = EXCLUDED.risk_value,
    price_usd = EXCLUDED.price_usd,
    risk_band = EXCLUDED.risk_band;

-- TON Fiat Risks (42 rows)
INSERT INTO risk_metric_grid (symbol, price_point, risk_value, price_usd, risk_band, risk_type) VALUES
('TON', 43, 0.000, 1.45, '0.0-0.1', 'FIAT_RISK'),
('TON', 44, 0.121, 2.24, '0.1-0.2', 'FIAT_RISK'),
('TON', 45, 0.209, 3.04, '0.2-0.3', 'FIAT_RISK'),
('TON', 46, 0.238, 3.20, '0.2-0.3', 'FIAT_RISK'),  -- CURRENT
('TON', 47, 0.338, 3.84, '0.3-0.4', 'FIAT_RISK'),
('TON', 48, 0.442, 4.63, '0.4-0.5', 'FIAT_RISK'),
('TON', 49, 0.500, 5.43, '0.5-0.6', 'FIAT_RISK'),
('TON', 50, 0.538, 6.22, '0.5-0.6', 'FIAT_RISK'),
('TON', 51, 0.571, 7.02, '0.5-0.6', 'FIAT_RISK'),
('TON', 52, 0.601, 7.81, '0.6-0.7', 'FIAT_RISK'),
('TON', 53, 0.627, 8.61, '0.6-0.7', 'FIAT_RISK'),
('TON', 54, 0.652, 9.40, '0.6-0.7', 'FIAT_RISK'),
('TON', 55, 0.674, 10.20, '0.6-0.7', 'FIAT_RISK'),
('TON', 56, 0.695, 10.99, '0.6-0.7', 'FIAT_RISK'),
('TON', 57, 0.714, 11.79, '0.7-0.8', 'FIAT_RISK'),
('TON', 58, 0.732, 12.58, '0.7-0.8', 'FIAT_RISK'),
('TON', 59, 0.749, 13.38, '0.7-0.8', 'FIAT_RISK'),
('TON', 60, 0.765, 14.18, '0.7-0.8', 'FIAT_RISK'),
('TON', 61, 0.780, 14.97, '0.7-0.8', 'FIAT_RISK'),
('TON', 62, 0.794, 15.77, '0.7-0.8', 'FIAT_RISK'),
('TON', 63, 0.808, 16.56, '0.8-0.9', 'FIAT_RISK'),
('TON', 64, 0.821, 17.36, '0.8-0.9', 'FIAT_RISK'),
('TON', 65, 0.833, 18.15, '0.8-0.9', 'FIAT_RISK'),
('TON', 66, 0.845, 18.95, '0.8-0.9', 'FIAT_RISK'),
('TON', 67, 0.856, 19.74, '0.8-0.9', 'FIAT_RISK'),
('TON', 68, 0.867, 20.54, '0.8-0.9', 'FIAT_RISK'),
('TON', 69, 0.878, 21.33, '0.8-0.9', 'FIAT_RISK'),
('TON', 70, 0.888, 22.13, '0.8-0.9', 'FIAT_RISK'),
('TON', 71, 0.898, 22.92, '0.8-0.9', 'FIAT_RISK'),
('TON', 72, 0.907, 23.72, '0.9-1.0', 'FIAT_RISK'),
('TON', 73, 0.916, 24.51, '0.9-1.0', 'FIAT_RISK'),
('TON', 74, 0.925, 25.31, '0.9-1.0', 'FIAT_RISK'),
('TON', 75, 0.933, 26.11, '0.9-1.0', 'FIAT_RISK'),
('TON', 76, 0.942, 26.90, '0.9-1.0', 'FIAT_RISK'),
('TON', 77, 0.950, 27.70, '0.9-1.0', 'FIAT_RISK'),
('TON', 78, 0.957, 28.49, '0.9-1.0', 'FIAT_RISK'),
('TON', 79, 0.965, 29.29, '0.9-1.0', 'FIAT_RISK'),
('TON', 80, 0.972, 30.08, '0.9-1.0', 'FIAT_RISK'),
('TON', 81, 0.980, 30.88, '0.9-1.0', 'FIAT_RISK'),
('TON', 82, 0.987, 31.67, '0.9-1.0', 'FIAT_RISK'),
('TON', 83, 0.993, 32.47, '0.9-1.0', 'FIAT_RISK'),
('TON', 84, 1.000, 33.26, '0.9-1.0', 'FIAT_RISK')
ON CONFLICT (symbol, price_point, risk_type) DO UPDATE SET
    risk_value = EXCLUDED.risk_value,
    price_usd = EXCLUDED.price_usd,
    risk_band = EXCLUDED.risk_band;

-- ========================================================================
-- SUMMARY STATISTICS
-- ========================================================================
-- BNB: 168 rows (43 Key + 42 Fiat + 42 BTC + 41 ETH)
-- SHIB: 84 rows (42 Key + 42 Fiat)
-- TON: 84 rows (42 Key + 42 Fiat)
-- Total: 336 rows

-- Verify data integrity
SELECT
    symbol,
    risk_type,
    COUNT(*) as row_count,
    MIN(risk_value) as min_risk,
    MAX(risk_value) as max_risk,
    MIN(price_usd) as min_price,
    MAX(price_usd) as max_price
FROM risk_metric_grid
WHERE symbol IN ('BNB', 'SHIB', 'TON')
GROUP BY symbol, risk_type
ORDER BY symbol, risk_type;

-- Current risk levels
SELECT
    symbol,
    risk_type,
    risk_value,
    price_usd,
    risk_band,
    'CURRENT' as status
FROM risk_metric_grid
WHERE
    (symbol = 'BNB' AND
     ((risk_type = 'KEY_RISK' AND price_point = 23) OR
      (risk_type = 'FIAT_RISK' AND price_point = 48) OR
      (risk_type = 'BTC_RISK' AND price_point = 99) OR
      (risk_type = 'ETH_RISK' AND price_point = 145)))
    OR
    (symbol = 'SHIB' AND
     ((risk_type = 'KEY_RISK' AND price_point = 11) OR
      (risk_type = 'FIAT_RISK' AND price_point = 44)))
    OR
    (symbol = 'TON' AND
     ((risk_type = 'KEY_RISK' AND price_point = 11) OR
      (risk_type = 'FIAT_RISK' AND price_point = 46)))
ORDER BY symbol, risk_type;