-- Create Risk Metric Grid Table
-- This is the MAIN TABLE that maps prices to risk values
-- 41 price points per symbol with corresponding risk metrics

CREATE TABLE IF NOT EXISTS risk_metric_grid (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price_point INTEGER NOT NULL,  -- 1 to 41
    price_usd DECIMAL(20,8) NOT NULL,
    fiat_risk DECIMAL(5,4) NOT NULL,  -- 0.0000 to 1.0000
    btc_risk DECIMAL(5,4),  -- Optional, for symbols with BTC pairs
    risk_band VARCHAR(10) NOT NULL,  -- e.g., "0.0-0.1"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, price_point)
);

-- Create indexes for fast lookups
CREATE INDEX idx_risk_metric_grid_symbol ON risk_metric_grid(symbol);
CREATE INDEX idx_risk_metric_grid_price ON risk_metric_grid(symbol, price_usd);
CREATE INDEX idx_risk_metric_grid_risk ON risk_metric_grid(symbol, fiat_risk);

-- Example: For SOL, we need 41 price points
-- Price range from low to high with corresponding risk values
-- Risk 0.0 = bottom price, Risk 1.0 = top price