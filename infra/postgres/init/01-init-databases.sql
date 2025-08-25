-- Diana PostgreSQL Initialization Script
-- Creates all required databases and users for ZmartBot services

-- Create application databases
CREATE DATABASE zmart_core;
CREATE DATABASE zmart_trading;  
CREATE DATABASE zmart_analytics;
CREATE DATABASE zmart_config;

-- Create service users
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'zmart_api') THEN
        CREATE USER zmart_api WITH PASSWORD 'api_secure_pass_2025';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'zmart_trader') THEN
        CREATE USER zmart_trader WITH PASSWORD 'trader_secure_pass_2025';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'zmart_analytics') THEN
        CREATE USER zmart_analytics WITH PASSWORD 'analytics_secure_pass_2025';
    END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE zmart_core TO zmart;
GRANT ALL PRIVILEGES ON DATABASE zmart_trading TO zmart_trader;
GRANT ALL PRIVILEGES ON DATABASE zmart_analytics TO zmart_analytics;
GRANT ALL PRIVILEGES ON DATABASE zmart_config TO zmart;

-- Connect to zmart_core and create schemas
\c zmart_core;

-- Core trading schemas
CREATE SCHEMA IF NOT EXISTS trading;
CREATE SCHEMA IF NOT EXISTS portfolio;
CREATE SCHEMA IF NOT EXISTS risk;
CREATE SCHEMA IF NOT EXISTS events;
CREATE SCHEMA IF NOT EXISTS config;

-- Create outbox table for event sourcing
CREATE TABLE IF NOT EXISTS events.outbox (
    id SERIAL PRIMARY KEY,
    aggregate_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1,
    correlation_id VARCHAR(255)
);

-- Create event store table
CREATE TABLE IF NOT EXISTS events.event_store (
    id SERIAL PRIMARY KEY,
    stream_id VARCHAR(255) NOT NULL,
    event_number INTEGER NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(stream_id, event_number)
);

-- Trading positions table
CREATE TABLE IF NOT EXISTS trading.positions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('long', 'short')),
    size DECIMAL(18, 8) NOT NULL,
    entry_price DECIMAL(18, 8) NOT NULL,
    current_price DECIMAL(18, 8),
    unrealized_pnl DECIMAL(18, 8),
    realized_pnl DECIMAL(18, 8) DEFAULT 0,
    leverage INTEGER DEFAULT 1,
    exchange VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'open',
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,
    correlation_id VARCHAR(255)
);

-- Portfolio holdings table
CREATE TABLE IF NOT EXISTS portfolio.holdings (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    quantity DECIMAL(18, 8) NOT NULL,
    average_cost DECIMAL(18, 8) NOT NULL,
    current_price DECIMAL(18, 8),
    market_value DECIMAL(18, 8),
    unrealized_gain_loss DECIMAL(18, 8),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol)
);

-- Risk metrics table
CREATE TABLE IF NOT EXISTS risk.metrics (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    rsi DECIMAL(5, 2),
    macd DECIMAL(10, 6),
    ema_cross VARCHAR(10),
    bollinger_position DECIMAL(5, 2),
    volume_profile DECIMAL(10, 2),
    support_level DECIMAL(18, 8),
    resistance_level DECIMAL(18, 8),
    risk_score INTEGER,
    confidence DECIMAL(3, 2),
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Configuration table
CREATE TABLE IF NOT EXISTS config.service_config (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    config_key VARCHAR(255) NOT NULL,
    config_value JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(service_name, config_key)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_positions_symbol ON trading.positions(symbol);
CREATE INDEX IF NOT EXISTS idx_positions_status ON trading.positions(status);
CREATE INDEX IF NOT EXISTS idx_outbox_processed ON events.outbox(processed_at) WHERE processed_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_event_store_stream ON events.event_store(stream_id, event_number);
CREATE INDEX IF NOT EXISTS idx_risk_metrics_symbol_time ON risk.metrics(symbol, calculated_at);

-- Insert initial configuration
INSERT INTO config.service_config (service_name, config_key, config_value) VALUES
('diana-platform', 'version', '"1.0.0"'),
('diana-platform', 'deployment_mode', '"production"'),
('diana-platform', 'circuit_breaker', '{"failure_threshold": 5, "recovery_timeout": 30}'),
('diana-platform', 'rate_limits', '{"default": 1000, "trading": 100, "analytics": 500}')
ON CONFLICT (service_name, config_key) DO NOTHING;

-- Create functions for event processing
CREATE OR REPLACE FUNCTION events.process_outbox_events()
RETURNS TRIGGER AS $$
BEGIN
    -- Notify event processors of new events
    PERFORM pg_notify('outbox_events', NEW.id::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for outbox events
DROP TRIGGER IF EXISTS trigger_outbox_events ON events.outbox;
CREATE TRIGGER trigger_outbox_events
    AFTER INSERT ON events.outbox
    FOR EACH ROW
    EXECUTE FUNCTION events.process_outbox_events();

COMMIT;