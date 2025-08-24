-- Universal Cryptocurrency Data Collection Database Schema
-- Created: August 8, 2025
-- Purpose: Store historical patterns and squeeze events for ANY cryptocurrency symbol

-- Enable UUID extension for unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table 1: Market Snapshot Data
CREATE TABLE market_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price DECIMAL(18,8) NOT NULL,
    volume_24h BIGINT,
    volume_change_24h DECIMAL(8,2),
    open_interest BIGINT,
    oi_change_24h DECIMAL(8,2),
    market_cap BIGINT,
    circulating_supply BIGINT,
    data_source VARCHAR(50),
    data_quality_score DECIMAL(5,2) DEFAULT 100.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Liquidation Analysis Data
CREATE TABLE liquidation_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    timeframe VARCHAR(10) NOT NULL, -- '1h', '4h', '12h', '24h'
    total_liquidations DECIMAL(15,2),
    long_liquidations DECIMAL(15,2),
    short_liquidations DECIMAL(15,2),
    long_liquidation_pct DECIMAL(5,2),
    short_liquidation_pct DECIMAL(5,2),
    liquidation_dominance VARCHAR(10), -- 'LONG' or 'SHORT'
    dominance_strength DECIMAL(5,2), -- percentage strength
    liquidation_intensity VARCHAR(20), -- 'LOW', 'MEDIUM', 'HIGH', 'EXTREME'
    cascade_potential DECIMAL(5,2), -- 0-100 score
    data_source VARCHAR(50),
    screenshot_path VARCHAR(255),
    image_hash VARCHAR(64), -- For duplicate detection
    extraction_confidence DECIMAL(5,2) DEFAULT 100.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: Technical Indicators
CREATE TABLE technical_indicators (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price_position_in_range DECIMAL(5,2), -- 0-100%
    range_low DECIMAL(18,8),
    range_high DECIMAL(18,8),
    range_duration_days INTEGER,
    fibonacci_0 DECIMAL(18,8), -- 0% (high)
    fibonacci_23_6 DECIMAL(18,8),
    fibonacci_38_2 DECIMAL(18,8),
    fibonacci_50_0 DECIMAL(18,8),
    fibonacci_61_8 DECIMAL(18,8),
    fibonacci_78_6 DECIMAL(18,8),
    fibonacci_100 DECIMAL(18,8), -- 100% (low)
    rsi_14 DECIMAL(5,2),
    rsi_position VARCHAR(20), -- 'OVERSOLD', 'NEUTRAL', 'OVERBOUGHT'
    volume_sma_20 BIGINT,
    volume_vs_sma DECIMAL(8,2),
    volume_trend VARCHAR(20), -- 'INCREASING', 'DECREASING', 'STABLE'
    support_levels TEXT, -- JSON array of support prices
    resistance_levels TEXT, -- JSON array of resistance prices
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 4: Win Rate Calculations
CREATE TABLE win_rate_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    timeframe VARCHAR(10) NOT NULL, -- '24h', '7d', '1m'
    long_win_rate DECIMAL(5,2),
    short_win_rate DECIMAL(5,2),
    confidence_level DECIMAL(5,2),
    market_bias VARCHAR(20), -- 'BULLISH', 'BEARISH', 'NEUTRAL'
    bias_strength VARCHAR(20), -- 'WEAK', 'MODERATE', 'STRONG', 'EXTREME'
    calculation_method VARCHAR(100),
    data_quality_score DECIMAL(5,2),
    historical_accuracy DECIMAL(5,2), -- Backtest accuracy %
    sample_size INTEGER, -- Number of historical events used
    mean_reversion_factor DECIMAL(5,2), -- Applied for longer timeframes
    external_factors TEXT, -- JSON array of considered factors
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 5: Squeeze Events Detection
CREATE TABLE squeeze_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    event_start TIMESTAMP NOT NULL,
    event_end TIMESTAMP,
    event_type VARCHAR(20) NOT NULL, -- 'LONG_SQUEEZE', 'SHORT_SQUEEZE'
    event_status VARCHAR(20) DEFAULT 'DETECTED', -- 'DETECTED', 'CONFIRMED', 'COMPLETED', 'FAILED'
    trigger_price DECIMAL(18,8),
    peak_price DECIMAL(18,8),
    end_price DECIMAL(18,8),
    price_change_pct DECIMAL(8,2),
    max_price_change_pct DECIMAL(8,2),
    volume_spike_pct DECIMAL(8,2),
    liquidation_volume DECIMAL(15,2),
    duration_minutes INTEGER,
    severity VARCHAR(20), -- 'MINOR', 'MODERATE', 'MAJOR', 'EXTREME'
    prediction_accuracy DECIMAL(5,2), -- How accurate was the prediction
    pre_event_signals TEXT, -- JSON array of warning signals
    post_event_analysis TEXT, -- JSON analysis results
    screenshot_paths TEXT, -- JSON array of screenshot paths
    related_events TEXT, -- JSON array of related squeeze events
    market_impact_score DECIMAL(5,2), -- 0-100 impact score
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 6: Pattern Recognition Library
CREATE TABLE pattern_library (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_name VARCHAR(100) NOT NULL,
    pattern_type VARCHAR(50), -- 'LIQUIDATION', 'VOLUME', 'PRICE', 'COMBINED'
    pattern_category VARCHAR(50), -- 'SQUEEZE', 'REVERSAL', 'CONTINUATION', 'BREAKOUT'
    description TEXT,
    success_rate DECIMAL(5,2),
    avg_price_move DECIMAL(8,2),
    avg_duration_hours INTEGER,
    min_volume_threshold BIGINT,
    required_conditions TEXT, -- JSON array of conditions
    warning_signals TEXT, -- JSON array of early signals
    confirmation_signals TEXT, -- JSON array of confirmation signals
    symbols_applicable TEXT, -- JSON array or 'ALL'
    market_cap_range TEXT, -- JSON object with min/max
    volatility_range TEXT, -- JSON object with min/max
    historical_examples TEXT, -- JSON array of historical occurrences
    last_occurrence TIMESTAMP,
    occurrence_frequency VARCHAR(50), -- 'RARE', 'UNCOMMON', 'COMMON', 'FREQUENT'
    seasonal_bias TEXT, -- JSON object with monthly/quarterly patterns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 7: Risk Assessment Data
CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    liquidation_intensity_score DECIMAL(5,2),
    data_discrepancy_score DECIMAL(5,2),
    volume_volatility_score DECIMAL(5,2),
    market_structure_score DECIMAL(5,2),
    correlation_risk_score DECIMAL(5,2), -- Risk from correlated assets
    liquidity_risk_score DECIMAL(5,2), -- Risk from low liquidity
    total_risk_score DECIMAL(5,2),
    risk_level VARCHAR(20), -- 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'
    max_position_size_pct DECIMAL(5,2),
    recommended_stop_loss DECIMAL(18,8),
    recommended_take_profit DECIMAL(18,8),
    position_hold_time VARCHAR(50), -- 'SCALP', 'INTRADAY', 'SWING', 'POSITION'
    risk_factors TEXT, -- JSON array of specific risk factors
    mitigation_strategies TEXT, -- JSON array of risk mitigation approaches
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 8: Cycle Analysis
CREATE TABLE cycle_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    cycle_type VARCHAR(20), -- 'SHORT', 'MEDIUM', 'LONG', '4YEAR'
    cycle_timeframe_days INTEGER,
    current_cycle_position DECIMAL(5,2), -- 0-100%
    cycle_start_date DATE,
    cycle_start_price DECIMAL(18,8),
    cycle_low DECIMAL(18,8),
    cycle_low_date DATE,
    cycle_high DECIMAL(18,8),
    cycle_high_date DATE,
    projected_peak DECIMAL(18,8),
    projected_peak_date DATE,
    projected_low DECIMAL(18,8),
    projected_low_date DATE,
    confidence_level DECIMAL(5,2),
    cycle_strength VARCHAR(20), -- 'WEAK', 'MODERATE', 'STRONG'
    supporting_factors TEXT, -- JSON array of supporting analysis
    historical_comparisons TEXT, -- JSON array of similar historical cycles
    fibonacci_targets TEXT, -- JSON object with fibonacci-based targets
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 9: Data Sources and Quality
CREATE TABLE data_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_name VARCHAR(50) NOT NULL,
    source_type VARCHAR(30), -- 'API', 'SCREENSHOT', 'MANUAL'
    reliability_score DECIMAL(5,2),
    last_update TIMESTAMP,
    update_frequency VARCHAR(30),
    supported_symbols TEXT, -- JSON array
    data_lag_seconds INTEGER,
    cost_per_request DECIMAL(10,4),
    rate_limit_per_minute INTEGER,
    status VARCHAR(20) DEFAULT 'ACTIVE', -- 'ACTIVE', 'INACTIVE', 'DEPRECATED'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 10: Analysis Sessions
CREATE TABLE analysis_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_name VARCHAR(100),
    symbols_analyzed TEXT, -- JSON array
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_symbols INTEGER,
    successful_analyses INTEGER,
    failed_analyses INTEGER,
    avg_processing_time_seconds DECIMAL(8,2),
    data_sources_used TEXT, -- JSON array
    analysis_type VARCHAR(50), -- 'BATCH', 'REAL_TIME', 'HISTORICAL'
    user_id VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance optimization
CREATE INDEX idx_market_snapshots_symbol_timestamp ON market_snapshots(symbol, timestamp DESC);
CREATE INDEX idx_liquidation_data_symbol_timestamp ON liquidation_data(symbol, timestamp DESC);
CREATE INDEX idx_liquidation_data_timeframe ON liquidation_data(timeframe);
CREATE INDEX idx_technical_indicators_symbol_timestamp ON technical_indicators(symbol, timestamp DESC);
CREATE INDEX idx_win_rate_analysis_symbol_timeframe ON win_rate_analysis(symbol, timeframe, timestamp DESC);
CREATE INDEX idx_squeeze_events_symbol_type ON squeeze_events(symbol, event_type, event_start DESC);
CREATE INDEX idx_squeeze_events_status ON squeeze_events(event_status, event_start DESC);
CREATE INDEX idx_pattern_library_type_category ON pattern_library(pattern_type, pattern_category);
CREATE INDEX idx_risk_assessments_symbol_timestamp ON risk_assessments(symbol, timestamp DESC);
CREATE INDEX idx_cycle_analysis_symbol_type ON cycle_analysis(symbol, cycle_type, timestamp DESC);

-- Create composite indexes for common queries
CREATE INDEX idx_liquidation_dominance_analysis ON liquidation_data(symbol, liquidation_dominance, dominance_strength, timestamp DESC);
CREATE INDEX idx_squeeze_detection ON liquidation_data(symbol, liquidation_intensity, cascade_potential, timestamp DESC);
CREATE INDEX idx_win_rate_confidence ON win_rate_analysis(symbol, timeframe, confidence_level, timestamp DESC);

-- Create triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_market_snapshots_updated_at BEFORE UPDATE ON market_snapshots FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_squeeze_events_updated_at BEFORE UPDATE ON squeeze_events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pattern_library_updated_at BEFORE UPDATE ON pattern_library FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common analysis queries
CREATE VIEW latest_market_data AS
SELECT DISTINCT ON (symbol) 
    symbol, timestamp, price, volume_24h, volume_change_24h, 
    open_interest, oi_change_24h, data_source
FROM market_snapshots 
ORDER BY symbol, timestamp DESC;

CREATE VIEW active_squeeze_alerts AS
SELECT 
    symbol, event_type, event_start, trigger_price, 
    severity, prediction_accuracy, pre_event_signals
FROM squeeze_events 
WHERE event_status IN ('DETECTED', 'CONFIRMED') 
    AND event_start > CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY event_start DESC;

CREATE VIEW symbol_risk_summary AS
SELECT DISTINCT ON (symbol)
    symbol, total_risk_score, risk_level, max_position_size_pct,
    recommended_stop_loss, timestamp
FROM risk_assessments
ORDER BY symbol, timestamp DESC;

-- Insert initial pattern library data
INSERT INTO pattern_library (pattern_name, pattern_type, pattern_category, description, success_rate, avg_price_move, avg_duration_hours, symbols_applicable) VALUES
('Classic Long Squeeze', 'LIQUIDATION', 'SQUEEZE', 'Short liquidation dominance >70% with volume spike >50%', 75.5, 15.2, 6, 'ALL'),
('Classic Short Squeeze', 'LIQUIDATION', 'SQUEEZE', 'Long liquidation dominance >70% with volume spike >50%', 72.3, -12.8, 8, 'ALL'),
('Fibonacci Breakout', 'PRICE', 'BREAKOUT', 'Price breaks above 61.8% fibonacci with volume confirmation', 68.9, 8.7, 24, 'ALL'),
('Volume Spike Reversal', 'VOLUME', 'REVERSAL', 'Extreme volume spike (>100%) at support/resistance', 64.2, 11.3, 12, 'ALL'),
('Liquidation Cascade', 'LIQUIDATION', 'CONTINUATION', 'Progressive liquidation intensity increase over 4+ hours', 78.1, 18.9, 16, 'ALL');

-- Insert initial data sources
INSERT INTO data_sources (source_name, source_type, reliability_score, update_frequency, supported_symbols, data_lag_seconds, rate_limit_per_minute) VALUES
('CoinGlass', 'API', 95.5, 'Real-time', '["ALL"]', 30, 60),
('Binance', 'API', 98.2, 'Real-time', '["ALL"]', 5, 1200),
('OKX', 'API', 94.8, 'Real-time', '["ALL"]', 10, 600),
('Bybit', 'API', 93.7, 'Real-time', '["ALL"]', 15, 300),
('Kingfisher Screenshots', 'SCREENSHOT', 85.0, 'Manual', '["ALL"]', 300, 10);

-- Create materialized view for performance on large datasets
CREATE MATERIALIZED VIEW hourly_liquidation_summary AS
SELECT 
    symbol,
    DATE_TRUNC('hour', timestamp) as hour,
    AVG(total_liquidations) as avg_liquidations,
    AVG(long_liquidation_pct) as avg_long_pct,
    AVG(short_liquidation_pct) as avg_short_pct,
    MAX(dominance_strength) as max_dominance,
    COUNT(*) as data_points
FROM liquidation_data
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY symbol, DATE_TRUNC('hour', timestamp)
ORDER BY symbol, hour DESC;

-- Create refresh function for materialized view
CREATE OR REPLACE FUNCTION refresh_hourly_liquidation_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW hourly_liquidation_summary;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE market_snapshots IS 'Real-time market data snapshots for all cryptocurrency symbols';
COMMENT ON TABLE liquidation_data IS 'Liquidation analysis data extracted from screenshots and APIs';
COMMENT ON TABLE squeeze_events IS 'Detected and confirmed squeeze events with outcome tracking';
COMMENT ON TABLE pattern_library IS 'Library of validated trading patterns with success rates';
COMMENT ON TABLE win_rate_analysis IS 'Calculated win rates for long/short positions across timeframes';
COMMENT ON TABLE risk_assessments IS 'Risk analysis and position sizing recommendations';
COMMENT ON TABLE cycle_analysis IS 'Market cycle analysis and projections';

-- Grant permissions (adjust as needed for your environment)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO crypto_analyst;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO crypto_analyst;

