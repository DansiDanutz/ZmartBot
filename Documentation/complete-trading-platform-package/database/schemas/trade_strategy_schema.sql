-- Trade Strategy Module Database Schema
-- Version: 1.0 Professional Edition
-- Compatibility: PostgreSQL 14+
-- Integration: ZmartBot + KingFisher Unified Platform

-- Create dedicated schema for Trade Strategy module
CREATE SCHEMA IF NOT EXISTS trade_strategy;

-- Set search path for this session
SET search_path TO trade_strategy, public;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =====================================================
-- SIGNAL CENTER TABLES
-- =====================================================

-- Signal Sources - Manages different signal providers
CREATE TABLE signal_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    source_type VARCHAR(50) NOT NULL, -- 'technical', 'fundamental', 'sentiment', 'external'
    description TEXT,
    api_endpoint VARCHAR(500),
    api_key_encrypted TEXT,
    reliability_score DECIMAL(5,4) DEFAULT 0.5000, -- 0.0000 to 1.0000
    is_active BOOLEAN DEFAULT true,
    configuration JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- Create indexes for signal_sources
CREATE INDEX idx_signal_sources_type ON signal_sources(source_type);
CREATE INDEX idx_signal_sources_active ON signal_sources(is_active);
CREATE INDEX idx_signal_sources_reliability ON signal_sources(reliability_score DESC);

-- Raw Signals - Stores incoming signals before processing
CREATE TABLE raw_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES signal_sources(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(50) NOT NULL, -- 'buy', 'sell', 'hold', 'strong_buy', 'strong_sell'
    strength DECIMAL(5,4) NOT NULL, -- 0.0000 to 1.0000
    timeframe VARCHAR(10) NOT NULL, -- '1m', '5m', '15m', '1h', '4h', '1d'
    price DECIMAL(20,8),
    target_price DECIMAL(20,8),
    stop_loss DECIMAL(20,8),
    confidence DECIMAL(5,4) NOT NULL, -- 0.0000 to 1.0000
    metadata JSONB DEFAULT '{}',
    raw_data JSONB,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    is_processed BOOLEAN DEFAULT false,
    processing_status VARCHAR(20) DEFAULT 'pending' -- 'pending', 'processing', 'completed', 'failed'
) PARTITION BY RANGE (received_at);

-- Create partitions for raw_signals (monthly partitions)
CREATE TABLE raw_signals_y2025m01 PARTITION OF raw_signals
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE raw_signals_y2025m02 PARTITION OF raw_signals
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE raw_signals_y2025m03 PARTITION OF raw_signals
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE raw_signals_y2025m04 PARTITION OF raw_signals
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
CREATE TABLE raw_signals_y2025m05 PARTITION OF raw_signals
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');
CREATE TABLE raw_signals_y2025m06 PARTITION OF raw_signals
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');
CREATE TABLE raw_signals_y2025m07 PARTITION OF raw_signals
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
CREATE TABLE raw_signals_y2025m08 PARTITION OF raw_signals
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
CREATE TABLE raw_signals_y2025m09 PARTITION OF raw_signals
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
CREATE TABLE raw_signals_y2025m10 PARTITION OF raw_signals
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
CREATE TABLE raw_signals_y2025m11 PARTITION OF raw_signals
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
CREATE TABLE raw_signals_y2025m12 PARTITION OF raw_signals
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Create indexes for raw_signals
CREATE INDEX idx_raw_signals_symbol ON raw_signals(symbol);
CREATE INDEX idx_raw_signals_source ON raw_signals(source_id);
CREATE INDEX idx_raw_signals_received ON raw_signals(received_at DESC);
CREATE INDEX idx_raw_signals_processed ON raw_signals(is_processed, processing_status);
CREATE INDEX idx_raw_signals_strength ON raw_signals(strength DESC);
CREATE INDEX idx_raw_signals_composite ON raw_signals(symbol, signal_type, received_at DESC);

-- Processed Signals - Stores validated and scored signals
CREATE TABLE processed_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    raw_signal_id UUID NOT NULL REFERENCES raw_signals(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES signal_sources(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,
    original_strength DECIMAL(5,4) NOT NULL,
    adjusted_strength DECIMAL(5,4) NOT NULL, -- Strength after processing
    confidence DECIMAL(5,4) NOT NULL,
    quality_score DECIMAL(5,4) NOT NULL, -- Overall signal quality
    risk_score DECIMAL(5,4) NOT NULL, -- Risk assessment
    timeframe VARCHAR(10) NOT NULL,
    price DECIMAL(20,8),
    target_price DECIMAL(20,8),
    stop_loss DECIMAL(20,8),
    expected_return DECIMAL(8,4), -- Expected return percentage
    max_drawdown DECIMAL(8,4), -- Maximum expected drawdown
    correlation_score DECIMAL(5,4), -- Correlation with other signals
    market_condition VARCHAR(50), -- 'bullish', 'bearish', 'sideways', 'volatile'
    validation_flags JSONB DEFAULT '{}',
    processing_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
) PARTITION BY RANGE (created_at);

-- Create partitions for processed_signals (monthly partitions)
CREATE TABLE processed_signals_y2025m01 PARTITION OF processed_signals
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE processed_signals_y2025m02 PARTITION OF processed_signals
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE processed_signals_y2025m03 PARTITION OF processed_signals
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE processed_signals_y2025m04 PARTITION OF processed_signals
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
CREATE TABLE processed_signals_y2025m05 PARTITION OF processed_signals
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');
CREATE TABLE processed_signals_y2025m06 PARTITION OF processed_signals
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');
CREATE TABLE processed_signals_y2025m07 PARTITION OF processed_signals
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
CREATE TABLE processed_signals_y2025m08 PARTITION OF processed_signals
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
CREATE TABLE processed_signals_y2025m09 PARTITION OF processed_signals
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
CREATE TABLE processed_signals_y2025m10 PARTITION OF processed_signals
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
CREATE TABLE processed_signals_y2025m11 PARTITION OF processed_signals
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
CREATE TABLE processed_signals_y2025m12 PARTITION OF processed_signals
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Create indexes for processed_signals
CREATE INDEX idx_processed_signals_symbol ON processed_signals(symbol);
CREATE INDEX idx_processed_signals_quality ON processed_signals(quality_score DESC);
CREATE INDEX idx_processed_signals_active ON processed_signals(is_active, expires_at);
CREATE INDEX idx_processed_signals_composite ON processed_signals(symbol, signal_type, quality_score DESC);
CREATE INDEX idx_processed_signals_risk ON processed_signals(risk_score);

-- Signal Aggregations - Stores combined signals for trading decisions
CREATE TABLE signal_aggregations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    aggregation_type VARCHAR(50) NOT NULL, -- 'consensus', 'weighted_average', 'ml_ensemble'
    signal_count INTEGER NOT NULL,
    buy_signals INTEGER DEFAULT 0,
    sell_signals INTEGER DEFAULT 0,
    hold_signals INTEGER DEFAULT 0,
    consensus_signal VARCHAR(50) NOT NULL, -- Final aggregated signal
    consensus_strength DECIMAL(5,4) NOT NULL,
    consensus_confidence DECIMAL(5,4) NOT NULL,
    risk_reward_ratio DECIMAL(8,4),
    expected_return DECIMAL(8,4),
    max_risk DECIMAL(8,4),
    signal_ids UUID[] NOT NULL, -- Array of contributing signal IDs
    weights DECIMAL(5,4)[] NOT NULL, -- Corresponding weights for each signal
    aggregation_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    used_for_trading BOOLEAN DEFAULT false,
    trading_decision_id UUID -- Reference to trading decision if used
);

-- Create indexes for signal_aggregations
CREATE INDEX idx_signal_aggregations_symbol ON signal_aggregations(symbol);
CREATE INDEX idx_signal_aggregations_active ON signal_aggregations(is_active, expires_at);
CREATE INDEX idx_signal_aggregations_strength ON signal_aggregations(consensus_strength DESC);
CREATE INDEX idx_signal_aggregations_unused ON signal_aggregations(used_for_trading, is_active);

-- =====================================================
-- VAULT MANAGEMENT TABLES
-- =====================================================

-- Vaults - Trading account management
CREATE TABLE vaults (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    vault_type VARCHAR(50) NOT NULL DEFAULT 'standard', -- 'standard', 'master', 'slave', 'test'
    parent_vault_id UUID REFERENCES vaults(id) ON DELETE SET NULL,
    exchange VARCHAR(50) NOT NULL, -- 'binance', 'kucoin', 'bybit', etc.
    api_key_encrypted TEXT NOT NULL,
    api_secret_encrypted TEXT NOT NULL,
    api_passphrase_encrypted TEXT,
    testnet BOOLEAN DEFAULT false,
    initial_balance DECIMAL(20,8) NOT NULL,
    current_balance DECIMAL(20,8) NOT NULL,
    available_balance DECIMAL(20,8) NOT NULL,
    reserved_balance DECIMAL(20,8) DEFAULT 0,
    total_pnl DECIMAL(20,8) DEFAULT 0,
    unrealized_pnl DECIMAL(20,8) DEFAULT 0,
    max_positions INTEGER DEFAULT 2, -- Maximum concurrent positions
    current_positions INTEGER DEFAULT 0,
    max_position_size DECIMAL(5,4) DEFAULT 0.15, -- Maximum position size as % of balance
    max_daily_loss DECIMAL(8,4) DEFAULT 0.05, -- Maximum daily loss as % of balance
    max_drawdown DECIMAL(8,4) DEFAULT 0.20, -- Maximum drawdown as % of balance
    risk_level VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'aggressive'
    is_active BOOLEAN DEFAULT true,
    auto_trading BOOLEAN DEFAULT false,
    configuration JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    updated_by UUID
);

-- Create indexes for vaults
CREATE INDEX idx_vaults_active ON vaults(is_active);
CREATE INDEX idx_vaults_exchange ON vaults(exchange);
CREATE INDEX idx_vaults_parent ON vaults(parent_vault_id);
CREATE INDEX idx_vaults_auto_trading ON vaults(auto_trading, is_active);

-- Vault Balance History - Track balance changes over time
CREATE TABLE vault_balance_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vault_id UUID NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
    balance_before DECIMAL(20,8) NOT NULL,
    balance_after DECIMAL(20,8) NOT NULL,
    change_amount DECIMAL(20,8) NOT NULL,
    change_type VARCHAR(50) NOT NULL, -- 'deposit', 'withdrawal', 'trade_pnl', 'fee', 'adjustment'
    description TEXT,
    reference_id UUID, -- Reference to trade, deposit, etc.
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Create partitions for vault_balance_history (monthly partitions)
CREATE TABLE vault_balance_history_y2025m01 PARTITION OF vault_balance_history
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE vault_balance_history_y2025m02 PARTITION OF vault_balance_history
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE vault_balance_history_y2025m03 PARTITION OF vault_balance_history
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE vault_balance_history_y2025m04 PARTITION OF vault_balance_history
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
CREATE TABLE vault_balance_history_y2025m05 PARTITION OF vault_balance_history
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');
CREATE TABLE vault_balance_history_y2025m06 PARTITION OF vault_balance_history
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');
CREATE TABLE vault_balance_history_y2025m07 PARTITION OF vault_balance_history
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
CREATE TABLE vault_balance_history_y2025m08 PARTITION OF vault_balance_history
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
CREATE TABLE vault_balance_history_y2025m09 PARTITION OF vault_balance_history
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
CREATE TABLE vault_balance_history_y2025m10 PARTITION OF vault_balance_history
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
CREATE TABLE vault_balance_history_y2025m11 PARTITION OF vault_balance_history
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
CREATE TABLE vault_balance_history_y2025m12 PARTITION OF vault_balance_history
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Create indexes for vault_balance_history
CREATE INDEX idx_vault_balance_history_vault ON vault_balance_history(vault_id);
CREATE INDEX idx_vault_balance_history_created ON vault_balance_history(created_at DESC);
CREATE INDEX idx_vault_balance_history_type ON vault_balance_history(change_type);

-- =====================================================
-- TRADING AGENT TABLES
-- =====================================================

-- Trading Decisions - Records of trading agent decisions
CREATE TABLE trading_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vault_id UUID NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
    aggregation_id UUID NOT NULL REFERENCES signal_aggregations(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    decision_type VARCHAR(50) NOT NULL, -- 'open_position', 'scale_position', 'close_position', 'hold'
    decision VARCHAR(50) NOT NULL, -- 'buy', 'sell', 'hold', 'scale_up', 'scale_down'
    confidence DECIMAL(5,4) NOT NULL,
    risk_score DECIMAL(5,4) NOT NULL,
    expected_return DECIMAL(8,4),
    max_risk DECIMAL(8,4),
    position_size DECIMAL(8,4), -- As percentage of vault balance
    leverage DECIMAL(4,2),
    entry_price DECIMAL(20,8),
    target_price DECIMAL(20,8),
    stop_loss DECIMAL(20,8),
    reasoning TEXT,
    market_conditions JSONB DEFAULT '{}',
    risk_assessment JSONB DEFAULT '{}',
    decision_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP WITH TIME ZONE,
    execution_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'executing', 'executed', 'failed', 'cancelled'
    execution_result JSONB DEFAULT '{}',
    position_id UUID -- Reference to created/modified position
);

-- Create indexes for trading_decisions
CREATE INDEX idx_trading_decisions_vault ON trading_decisions(vault_id);
CREATE INDEX idx_trading_decisions_symbol ON trading_decisions(symbol);
CREATE INDEX idx_trading_decisions_status ON trading_decisions(execution_status);
CREATE INDEX idx_trading_decisions_created ON trading_decisions(created_at DESC);
CREATE INDEX idx_trading_decisions_confidence ON trading_decisions(confidence DESC);

-- =====================================================
-- POSITION MANAGEMENT TABLES
-- =====================================================

-- Positions - Track all trading positions
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vault_id UUID NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL, -- 'long', 'short'
    status VARCHAR(20) NOT NULL DEFAULT 'open', -- 'open', 'closed', 'liquidated'
    initial_entry_price DECIMAL(20,8) NOT NULL,
    current_price DECIMAL(20,8) NOT NULL,
    average_entry_price DECIMAL(20,8) NOT NULL,
    total_size DECIMAL(20,8) NOT NULL, -- Total position size in base currency
    total_value DECIMAL(20,8) NOT NULL, -- Total position value in quote currency
    initial_margin DECIMAL(20,8) NOT NULL,
    maintenance_margin DECIMAL(20,8) NOT NULL,
    unrealized_pnl DECIMAL(20,8) DEFAULT 0,
    realized_pnl DECIMAL(20,8) DEFAULT 0,
    total_fees DECIMAL(20,8) DEFAULT 0,
    liquidation_price DECIMAL(20,8),
    bankruptcy_price DECIMAL(20,8),
    scale_count INTEGER DEFAULT 1, -- Number of scaling events
    max_scale_count INTEGER DEFAULT 4, -- Maximum allowed scaling
    risk_level VARCHAR(20) DEFAULT 'medium',
    stop_loss_price DECIMAL(20,8),
    take_profit_price DECIMAL(20,8),
    trailing_stop_distance DECIMAL(8,4), -- As percentage
    trailing_stop_price DECIMAL(20,8),
    auto_close_enabled BOOLEAN DEFAULT true,
    position_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP WITH TIME ZONE,
    created_by_decision_id UUID REFERENCES trading_decisions(id)
);

-- Create indexes for positions
CREATE INDEX idx_positions_vault ON positions(vault_id);
CREATE INDEX idx_positions_symbol ON positions(symbol);
CREATE INDEX idx_positions_status ON positions(status);
CREATE INDEX idx_positions_open ON positions(status) WHERE status = 'open';
CREATE INDEX idx_positions_pnl ON positions(unrealized_pnl DESC);
CREATE INDEX idx_positions_created ON positions(created_at DESC);

-- Position Scales - Track individual scaling events
CREATE TABLE position_scales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    position_id UUID NOT NULL REFERENCES positions(id) ON DELETE CASCADE,
    scale_number INTEGER NOT NULL, -- 1, 2, 3, 4 (as per requirements)
    entry_price DECIMAL(20,8) NOT NULL,
    size DECIMAL(20,8) NOT NULL, -- Size of this scale
    value DECIMAL(20,8) NOT NULL, -- Value of this scale
    leverage DECIMAL(4,2) NOT NULL,
    margin_used DECIMAL(20,8) NOT NULL,
    bankroll_percentage DECIMAL(5,4) NOT NULL, -- Percentage of vault balance used
    trigger_reason VARCHAR(100), -- 'initial_entry', 'better_signal', 'liquidation_cluster'
    trigger_signal_id UUID,
    liquidation_price DECIMAL(20,8),
    unrealized_pnl DECIMAL(20,8) DEFAULT 0,
    fees_paid DECIMAL(20,8) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    scale_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP WITH TIME ZONE,
    created_by_decision_id UUID REFERENCES trading_decisions(id)
);

-- Create indexes for position_scales
CREATE INDEX idx_position_scales_position ON position_scales(position_id);
CREATE INDEX idx_position_scales_number ON position_scales(scale_number);
CREATE INDEX idx_position_scales_active ON position_scales(is_active);
CREATE INDEX idx_position_scales_created ON position_scales(created_at DESC);

-- Position Closures - Track position closure events
CREATE TABLE position_closures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    position_id UUID NOT NULL REFERENCES positions(id) ON DELETE CASCADE,
    closure_type VARCHAR(50) NOT NULL, -- 'partial', 'full', 'liquidation', 'stop_loss', 'take_profit'
    closure_reason VARCHAR(100), -- 'trailing_stop', 'profit_target', 'risk_management', etc.
    size_closed DECIMAL(20,8) NOT NULL,
    closure_price DECIMAL(20,8) NOT NULL,
    realized_pnl DECIMAL(20,8) NOT NULL,
    fees_paid DECIMAL(20,8) NOT NULL,
    remaining_size DECIMAL(20,8) NOT NULL,
    closure_percentage DECIMAL(5,4) NOT NULL, -- Percentage of position closed
    profit_percentage DECIMAL(8,4), -- Profit as percentage of initial investment
    closure_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by_decision_id UUID REFERENCES trading_decisions(id)
);

-- Create indexes for position_closures
CREATE INDEX idx_position_closures_position ON position_closures(position_id);
CREATE INDEX idx_position_closures_type ON position_closures(closure_type);
CREATE INDEX idx_position_closures_created ON position_closures(created_at DESC);
CREATE INDEX idx_position_closures_pnl ON position_closures(realized_pnl DESC);

-- =====================================================
-- RISK MANAGEMENT TABLES
-- =====================================================

-- Risk Assessments - Detailed risk analysis for positions
CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    position_id UUID REFERENCES positions(id) ON DELETE CASCADE,
    vault_id UUID NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) NOT NULL, -- 'pre_trade', 'ongoing', 'pre_scale', 'emergency'
    symbol VARCHAR(20) NOT NULL,
    current_price DECIMAL(20,8) NOT NULL,
    volatility DECIMAL(8,4), -- Annualized volatility
    var_1d DECIMAL(20,8), -- 1-day Value at Risk
    var_7d DECIMAL(20,8), -- 7-day Value at Risk
    max_drawdown_risk DECIMAL(8,4),
    liquidation_risk DECIMAL(5,4), -- Probability of liquidation
    correlation_risk DECIMAL(5,4), -- Risk from correlated positions
    concentration_risk DECIMAL(5,4), -- Risk from position concentration
    market_risk DECIMAL(5,4), -- Overall market risk
    liquidity_risk DECIMAL(5,4), -- Risk from low liquidity
    overall_risk_score DECIMAL(5,4) NOT NULL,
    risk_level VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'extreme'
    recommended_action VARCHAR(50), -- 'proceed', 'reduce_size', 'close_position', 'add_margin'
    risk_factors JSONB DEFAULT '{}',
    mitigation_strategies JSONB DEFAULT '{}',
    assessment_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP WITH TIME ZONE
);

-- Create indexes for risk_assessments
CREATE INDEX idx_risk_assessments_position ON risk_assessments(position_id);
CREATE INDEX idx_risk_assessments_vault ON risk_assessments(vault_id);
CREATE INDEX idx_risk_assessments_risk_score ON risk_assessments(overall_risk_score DESC);
CREATE INDEX idx_risk_assessments_created ON risk_assessments(created_at DESC);

-- Liquidation Clusters - Track liquidation price clusters
CREATE TABLE liquidation_clusters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    price_level DECIMAL(20,8) NOT NULL,
    cluster_strength DECIMAL(10,2) NOT NULL, -- Total value at risk at this price level
    position_count INTEGER NOT NULL, -- Number of positions that would be liquidated
    side VARCHAR(10) NOT NULL, -- 'long', 'short'
    timeframe VARCHAR(10) NOT NULL, -- Time horizon for this cluster
    confidence DECIMAL(5,4) NOT NULL, -- Confidence in cluster accuracy
    market_impact DECIMAL(5,4), -- Expected market impact if triggered
    opportunity_score DECIMAL(5,4), -- Trading opportunity score
    cluster_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT true
);

-- Create indexes for liquidation_clusters
CREATE INDEX idx_liquidation_clusters_symbol ON liquidation_clusters(symbol);
CREATE INDEX idx_liquidation_clusters_price ON liquidation_clusters(symbol, price_level);
CREATE INDEX idx_liquidation_clusters_strength ON liquidation_clusters(cluster_strength DESC);
CREATE INDEX idx_liquidation_clusters_active ON liquidation_clusters(is_active, expires_at);

-- =====================================================
-- PERFORMANCE TRACKING TABLES
-- =====================================================

-- Performance Metrics - Track performance across different dimensions
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vault_id UUID REFERENCES vaults(id) ON DELETE CASCADE,
    position_id UUID REFERENCES positions(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL, -- 'vault_daily', 'vault_monthly', 'position', 'strategy'
    symbol VARCHAR(20),
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,4) DEFAULT 0,
    total_pnl DECIMAL(20,8) DEFAULT 0,
    gross_profit DECIMAL(20,8) DEFAULT 0,
    gross_loss DECIMAL(20,8) DEFAULT 0,
    profit_factor DECIMAL(8,4) DEFAULT 0,
    average_win DECIMAL(20,8) DEFAULT 0,
    average_loss DECIMAL(20,8) DEFAULT 0,
    largest_win DECIMAL(20,8) DEFAULT 0,
    largest_loss DECIMAL(20,8) DEFAULT 0,
    max_consecutive_wins INTEGER DEFAULT 0,
    max_consecutive_losses INTEGER DEFAULT 0,
    max_drawdown DECIMAL(8,4) DEFAULT 0,
    max_drawdown_duration INTEGER, -- In hours
    sharpe_ratio DECIMAL(8,4),
    sortino_ratio DECIMAL(8,4),
    calmar_ratio DECIMAL(8,4),
    total_fees DECIMAL(20,8) DEFAULT 0,
    roi DECIMAL(8,4) DEFAULT 0, -- Return on Investment
    annualized_return DECIMAL(8,4),
    volatility DECIMAL(8,4),
    metrics_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (period_start);

-- Create partitions for performance_metrics (quarterly partitions)
CREATE TABLE performance_metrics_y2025q1 PARTITION OF performance_metrics
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE performance_metrics_y2025q2 PARTITION OF performance_metrics
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE performance_metrics_y2025q3 PARTITION OF performance_metrics
    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
CREATE TABLE performance_metrics_y2025q4 PARTITION OF performance_metrics
    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');

-- Create indexes for performance_metrics
CREATE INDEX idx_performance_metrics_vault ON performance_metrics(vault_id);
CREATE INDEX idx_performance_metrics_type ON performance_metrics(metric_type);
CREATE INDEX idx_performance_metrics_period ON performance_metrics(period_start DESC);
CREATE INDEX idx_performance_metrics_roi ON performance_metrics(roi DESC);

-- =====================================================
-- SYSTEM CONFIGURATION TABLES
-- =====================================================

-- System Configuration - Global system settings
CREATE TABLE system_configuration (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    config_type VARCHAR(20) NOT NULL, -- 'string', 'integer', 'decimal', 'boolean', 'json'
    category VARCHAR(50) NOT NULL, -- 'trading', 'risk', 'system', 'api'
    description TEXT,
    is_encrypted BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- Create indexes for system_configuration
CREATE INDEX idx_system_configuration_category ON system_configuration(category);
CREATE INDEX idx_system_configuration_active ON system_configuration(is_active);

-- Audit Log - Track all significant system events
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL, -- 'trade', 'config_change', 'risk_event', 'system_event'
    event_category VARCHAR(50) NOT NULL,
    event_description TEXT NOT NULL,
    user_id UUID,
    vault_id UUID REFERENCES vaults(id) ON DELETE SET NULL,
    position_id UUID REFERENCES positions(id) ON DELETE SET NULL,
    entity_type VARCHAR(50), -- Type of entity affected
    entity_id UUID, -- ID of entity affected
    old_values JSONB,
    new_values JSONB,
    metadata JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    severity VARCHAR(20) DEFAULT 'info', -- 'debug', 'info', 'warning', 'error', 'critical'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Create partitions for audit_log (monthly partitions)
CREATE TABLE audit_log_y2025m01 PARTITION OF audit_log
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE audit_log_y2025m02 PARTITION OF audit_log
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE audit_log_y2025m03 PARTITION OF audit_log
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE audit_log_y2025m04 PARTITION OF audit_log
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
CREATE TABLE audit_log_y2025m05 PARTITION OF audit_log
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');
CREATE TABLE audit_log_y2025m06 PARTITION OF audit_log
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');
CREATE TABLE audit_log_y2025m07 PARTITION OF audit_log
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
CREATE TABLE audit_log_y2025m08 PARTITION OF audit_log
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
CREATE TABLE audit_log_y2025m09 PARTITION OF audit_log
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
CREATE TABLE audit_log_y2025m10 PARTITION OF audit_log
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
CREATE TABLE audit_log_y2025m11 PARTITION OF audit_log
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
CREATE TABLE audit_log_y2025m12 PARTITION OF audit_log
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Create indexes for audit_log
CREATE INDEX idx_audit_log_event_type ON audit_log(event_type);
CREATE INDEX idx_audit_log_severity ON audit_log(severity);
CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_vault ON audit_log(vault_id);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Active Positions Summary
CREATE VIEW active_positions_summary AS
SELECT 
    p.id,
    p.vault_id,
    v.name as vault_name,
    p.symbol,
    p.side,
    p.total_size,
    p.total_value,
    p.average_entry_price,
    p.current_price,
    p.unrealized_pnl,
    p.liquidation_price,
    p.scale_count,
    p.risk_level,
    p.created_at,
    CASE 
        WHEN p.unrealized_pnl > 0 THEN 'profit'
        WHEN p.unrealized_pnl < 0 THEN 'loss'
        ELSE 'breakeven'
    END as pnl_status,
    (p.unrealized_pnl / p.initial_margin * 100) as roi_percentage
FROM positions p
JOIN vaults v ON p.vault_id = v.id
WHERE p.status = 'open';

-- Vault Performance Summary
CREATE VIEW vault_performance_summary AS
SELECT 
    v.id,
    v.name,
    v.current_balance,
    v.total_pnl,
    v.unrealized_pnl,
    v.current_positions,
    v.max_positions,
    COALESCE(pm.win_rate, 0) as win_rate,
    COALESCE(pm.profit_factor, 0) as profit_factor,
    COALESCE(pm.sharpe_ratio, 0) as sharpe_ratio,
    COALESCE(pm.max_drawdown, 0) as max_drawdown,
    v.updated_at
FROM vaults v
LEFT JOIN LATERAL (
    SELECT 
        win_rate,
        profit_factor,
        sharpe_ratio,
        max_drawdown
    FROM performance_metrics pm
    WHERE pm.vault_id = v.id 
    AND pm.metric_type = 'vault_monthly'
    ORDER BY pm.period_end DESC
    LIMIT 1
) pm ON true
WHERE v.is_active = true;

-- Signal Quality Summary
CREATE VIEW signal_quality_summary AS
SELECT 
    ss.id,
    ss.name,
    ss.source_type,
    ss.reliability_score,
    COUNT(ps.id) as total_signals_24h,
    AVG(ps.quality_score) as avg_quality_score,
    AVG(ps.confidence) as avg_confidence,
    COUNT(CASE WHEN ps.quality_score >= 0.7 THEN 1 END) as high_quality_signals,
    ss.updated_at
FROM signal_sources ss
LEFT JOIN processed_signals ps ON ss.id = ps.source_id
    AND ps.created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
WHERE ss.is_active = true
GROUP BY ss.id, ss.name, ss.source_type, ss.reliability_score, ss.updated_at;

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers to relevant tables
CREATE TRIGGER update_vaults_updated_at BEFORE UPDATE ON vaults
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_configuration_updated_at BEFORE UPDATE ON system_configuration
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically create monthly partitions
CREATE OR REPLACE FUNCTION create_monthly_partition(table_name TEXT, start_date DATE)
RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    end_date DATE;
BEGIN
    end_date := start_date + INTERVAL '1 month';
    partition_name := table_name || '_y' || EXTRACT(YEAR FROM start_date) || 'm' || LPAD(EXTRACT(MONTH FROM start_date)::TEXT, 2, '0');
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
                   partition_name, table_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INITIAL DATA SEEDING
-- =====================================================

-- Insert default system configuration
INSERT INTO system_configuration (config_key, config_value, config_type, category, description) VALUES
('max_concurrent_positions_per_vault', '2', 'integer', 'trading', 'Maximum concurrent positions allowed per vault'),
('default_leverage_stage_1', '20', 'decimal', 'trading', 'Default leverage for first position entry'),
('default_leverage_stage_2', '10', 'decimal', 'trading', 'Default leverage for second position scaling'),
('default_leverage_stage_3', '5', 'decimal', 'trading', 'Default leverage for third position scaling'),
('default_leverage_stage_4', '2', 'decimal', 'trading', 'Default leverage for fourth position scaling'),
('bankroll_percentage_stage_1', '0.01', 'decimal', 'trading', 'Bankroll percentage for first position entry (1%)'),
('bankroll_percentage_stage_2', '0.02', 'decimal', 'trading', 'Bankroll percentage for second position scaling (2%)'),
('bankroll_percentage_stage_3', '0.04', 'decimal', 'trading', 'Bankroll percentage for third position scaling (4%)'),
('bankroll_percentage_stage_4', '0.08', 'decimal', 'trading', 'Bankroll percentage for fourth position scaling (8%)'),
('minimum_profit_threshold', '0.75', 'decimal', 'trading', 'Minimum profit threshold before closing positions (75%)'),
('trailing_stop_initial', '0.30', 'decimal', 'trading', 'Initial trailing stop percentage for profit taking'),
('trailing_stop_secondary', '0.25', 'decimal', 'trading', 'Secondary trailing stop percentage'),
('trailing_stop_final', '0.03', 'decimal', 'trading', 'Final trailing stop percentage (3%)'),
('signal_expiry_minutes', '60', 'integer', 'trading', 'Default signal expiry time in minutes'),
('risk_assessment_interval_minutes', '15', 'integer', 'risk', 'Interval for automated risk assessments'),
('max_daily_loss_percentage', '0.05', 'decimal', 'risk', 'Maximum daily loss as percentage of vault balance'),
('max_drawdown_percentage', '0.20', 'decimal', 'risk', 'Maximum drawdown as percentage of vault balance'),
('liquidation_cluster_threshold', '1000000', 'decimal', 'risk', 'Minimum cluster value to be considered significant'),
('api_rate_limit_per_minute', '1000', 'integer', 'api', 'API rate limit per minute per client'),
('websocket_heartbeat_interval', '30', 'integer', 'system', 'WebSocket heartbeat interval in seconds'),
('database_connection_pool_size', '20', 'integer', 'system', 'Database connection pool size'),
('redis_cache_ttl_seconds', '300', 'integer', 'system', 'Default Redis cache TTL in seconds'),
('log_retention_days', '90', 'integer', 'system', 'Log retention period in days'),
('backup_retention_days', '30', 'integer', 'system', 'Backup retention period in days');

-- Create default signal sources
INSERT INTO signal_sources (name, source_type, description, reliability_score) VALUES
('Technical Analysis Engine', 'technical', 'Internal technical analysis signal generator', 0.7500),
('Market Sentiment Analyzer', 'sentiment', 'Social media and news sentiment analysis', 0.6500),
('Fundamental Analysis Engine', 'fundamental', 'Economic and fundamental data analysis', 0.8000),
('External Signal Provider A', 'external', 'Third-party signal provider integration', 0.6000),
('Machine Learning Predictor', 'technical', 'ML-based price prediction system', 0.7000);

-- =====================================================
-- PERMISSIONS AND SECURITY
-- =====================================================

-- Create roles for different access levels
CREATE ROLE trade_strategy_admin;
CREATE ROLE trade_strategy_trader;
CREATE ROLE trade_strategy_viewer;

-- Grant permissions to admin role (full access)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA trade_strategy TO trade_strategy_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA trade_strategy TO trade_strategy_admin;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA trade_strategy TO trade_strategy_admin;

-- Grant permissions to trader role (limited write access)
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA trade_strategy TO trade_strategy_trader;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA trade_strategy TO trade_strategy_trader;
-- Restrict DELETE access for critical tables
REVOKE DELETE ON vaults FROM trade_strategy_trader;
REVOKE DELETE ON positions FROM trade_strategy_trader;
REVOKE DELETE ON system_configuration FROM trade_strategy_trader;

-- Grant permissions to viewer role (read-only access)
GRANT SELECT ON ALL TABLES IN SCHEMA trade_strategy TO trade_strategy_viewer;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA trade_strategy TO trade_strategy_viewer;

-- Create specific users for the application
CREATE USER trade_strategy_app WITH PASSWORD 'secure_app_password_2025';
CREATE USER trade_strategy_readonly WITH PASSWORD 'secure_readonly_password_2025';

-- Assign roles to users
GRANT trade_strategy_trader TO trade_strategy_app;
GRANT trade_strategy_viewer TO trade_strategy_readonly;

-- Enable Row Level Security (RLS) for sensitive tables
ALTER TABLE vaults ENABLE ROW LEVEL SECURITY;
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_decisions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (example for multi-tenant support)
CREATE POLICY vault_access_policy ON vaults
    FOR ALL TO trade_strategy_trader
    USING (created_by = current_setting('app.current_user_id')::UUID OR 
           id IN (SELECT vault_id FROM vault_permissions WHERE user_id = current_setting('app.current_user_id')::UUID));

-- =====================================================
-- PERFORMANCE OPTIMIZATION
-- =====================================================

-- Create materialized views for expensive queries
CREATE MATERIALIZED VIEW mv_daily_vault_performance AS
SELECT 
    v.id as vault_id,
    v.name as vault_name,
    DATE(CURRENT_TIMESTAMP) as performance_date,
    v.current_balance,
    v.total_pnl,
    v.unrealized_pnl,
    COUNT(p.id) as active_positions,
    SUM(CASE WHEN p.unrealized_pnl > 0 THEN 1 ELSE 0 END) as profitable_positions,
    SUM(CASE WHEN p.unrealized_pnl < 0 THEN 1 ELSE 0 END) as losing_positions,
    AVG(p.unrealized_pnl) as avg_position_pnl,
    MAX(p.unrealized_pnl) as best_position_pnl,
    MIN(p.unrealized_pnl) as worst_position_pnl
FROM vaults v
LEFT JOIN positions p ON v.id = p.vault_id AND p.status = 'open'
WHERE v.is_active = true
GROUP BY v.id, v.name, v.current_balance, v.total_pnl, v.unrealized_pnl;

-- Create indexes on materialized view
CREATE INDEX idx_mv_daily_vault_performance_vault ON mv_daily_vault_performance(vault_id);
CREATE INDEX idx_mv_daily_vault_performance_date ON mv_daily_vault_performance(performance_date);

-- Create refresh function for materialized views
CREATE OR REPLACE FUNCTION refresh_performance_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_vault_performance;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- MONITORING AND HEALTH CHECKS
-- =====================================================

-- Create health check function
CREATE OR REPLACE FUNCTION health_check()
RETURNS TABLE(
    component VARCHAR(50),
    status VARCHAR(20),
    message TEXT,
    last_updated TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    -- Check database connectivity
    RETURN QUERY SELECT 'database'::VARCHAR(50), 'healthy'::VARCHAR(20), 'Database connection active'::TEXT, CURRENT_TIMESTAMP;
    
    -- Check recent signal activity
    RETURN QUERY 
    SELECT 
        'signal_processing'::VARCHAR(50),
        CASE WHEN COUNT(*) > 0 THEN 'healthy'::VARCHAR(20) ELSE 'warning'::VARCHAR(20) END,
        CASE WHEN COUNT(*) > 0 THEN 'Signals processed in last hour'::TEXT ELSE 'No signals processed in last hour'::TEXT END,
        MAX(created_at)
    FROM processed_signals 
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour';
    
    -- Check active vaults
    RETURN QUERY
    SELECT 
        'vault_management'::VARCHAR(50),
        CASE WHEN COUNT(*) > 0 THEN 'healthy'::VARCHAR(20) ELSE 'error'::VARCHAR(20) END,
        CONCAT(COUNT(*), ' active vaults')::TEXT,
        MAX(updated_at)
    FROM vaults 
    WHERE is_active = true;
    
    -- Check position monitoring
    RETURN QUERY
    SELECT 
        'position_monitoring'::VARCHAR(50),
        'healthy'::VARCHAR(20),
        CONCAT(COUNT(*), ' open positions')::TEXT,
        COALESCE(MAX(updated_at), CURRENT_TIMESTAMP)
    FROM positions 
    WHERE status = 'open';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- CLEANUP AND MAINTENANCE
-- =====================================================

-- Create cleanup function for old data
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS VOID AS $$
BEGIN
    -- Clean up old raw signals (keep 30 days)
    DELETE FROM raw_signals 
    WHERE received_at < CURRENT_TIMESTAMP - INTERVAL '30 days'
    AND is_processed = true;
    
    -- Clean up old processed signals (keep 90 days)
    DELETE FROM processed_signals 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '90 days'
    AND is_active = false;
    
    -- Clean up old audit logs (keep 180 days)
    DELETE FROM audit_log 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '180 days'
    AND severity IN ('debug', 'info');
    
    -- Clean up expired signal aggregations
    DELETE FROM signal_aggregations 
    WHERE expires_at < CURRENT_TIMESTAMP
    AND used_for_trading = false;
    
    -- Clean up old risk assessments (keep 60 days)
    DELETE FROM risk_assessments 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '60 days';
    
    -- Clean up expired liquidation clusters
    DELETE FROM liquidation_clusters 
    WHERE expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FINAL SETUP
-- =====================================================

-- Reset search path
SET search_path TO public;

-- Add comments for documentation
COMMENT ON SCHEMA trade_strategy IS 'Trade Strategy Module - Advanced trading system with signal processing, vault management, and position scaling';
COMMENT ON TABLE trade_strategy.vaults IS 'Trading account management with multi-vault support and risk controls';
COMMENT ON TABLE trade_strategy.positions IS 'Position tracking with advanced scaling and risk management';
COMMENT ON TABLE trade_strategy.signal_sources IS 'Signal provider management and reliability tracking';
COMMENT ON TABLE trade_strategy.processed_signals IS 'Validated and scored trading signals ready for decision making';
COMMENT ON TABLE trade_strategy.trading_decisions IS 'Trading agent decisions with full reasoning and execution tracking';

-- Create completion marker
CREATE TABLE IF NOT EXISTS trade_strategy.schema_version (
    version VARCHAR(20) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO trade_strategy.schema_version (version, description) VALUES 
('1.0.0', 'Initial Trade Strategy Module schema with full feature set');

-- Final success message
DO $$
BEGIN
    RAISE NOTICE 'Trade Strategy Module database schema created successfully!';
    RAISE NOTICE 'Schema version: 1.0.0';
    RAISE NOTICE 'Total tables created: %', (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'trade_strategy');
    RAISE NOTICE 'Total indexes created: %', (SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'trade_strategy');
    RAISE NOTICE 'Ready for Trade Strategy Module deployment!';
END $$;

