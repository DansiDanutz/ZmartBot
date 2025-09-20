-- ============================================
-- RESTORE USER REFERENCE TABLES IN SMART TRADING
-- These tables link users to their trading data
-- Run this in Smart Trading (asjtxrmftmutcsnqgidy)
-- ============================================

-- 1. User Trades (trading history per user)
CREATE TABLE IF NOT EXISTS user_trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- References user in ZmartyBrain
    symbol TEXT NOT NULL,
    trade_type TEXT NOT NULL, -- 'buy', 'sell'
    quantity DECIMAL(20,8),
    price DECIMAL(20,8),
    total_value DECIMAL(20,2),
    exchange TEXT,
    status TEXT DEFAULT 'pending', -- 'pending', 'completed', 'failed'
    executed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. User Portfolios (what each user owns)
CREATE TABLE IF NOT EXISTS user_portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    portfolio_name TEXT NOT NULL,
    holdings JSONB DEFAULT '{}', -- {"BTC": 0.5, "ETH": 2.3}
    total_value DECIMAL(20,2) DEFAULT 0,
    performance JSONB DEFAULT '{}',
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. User Strategies (trading strategies per user)
CREATE TABLE IF NOT EXISTS user_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    strategy_name TEXT NOT NULL,
    strategy_type TEXT, -- 'scalping', 'swing', 'hodl'
    parameters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    performance_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. User Trading Profiles (risk settings)
CREATE TABLE IF NOT EXISTS user_trading_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    risk_tolerance TEXT DEFAULT 'medium', -- 'low', 'medium', 'high'
    preferred_exchanges JSONB DEFAULT '[]',
    trading_experience TEXT,
    investment_goals JSONB DEFAULT '{}',
    max_position_size DECIMAL(10,2),
    stop_loss_percentage DECIMAL(5,2),
    take_profit_percentage DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. User Indicators (which indicators each user wants)
CREATE TABLE IF NOT EXISTS user_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    indicator_name TEXT NOT NULL, -- 'RSI', 'MACD', 'Bollinger'
    settings JSONB DEFAULT '{}', -- {"period": 14, "threshold": 70}
    is_active BOOLEAN DEFAULT true,
    alert_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, indicator_name)
);

-- 6. User Symbols (which symbols/slots each user is tracking)
CREATE TABLE IF NOT EXISTS user_symbols (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    symbol TEXT NOT NULL, -- 'BTC/USDT', 'ETH/USDT'
    slot_number INTEGER, -- 1-10 for their slots
    is_active BOOLEAN DEFAULT true,
    alert_settings JSONB DEFAULT '{}',
    price_alerts JSONB DEFAULT '[]', -- [{"type": "above", "value": 50000}]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, symbol),
    UNIQUE(user_id, slot_number)
);

-- 7. User API Keys (for exchange connections)
CREATE TABLE IF NOT EXISTS user_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    exchange TEXT NOT NULL, -- 'binance', 'coinbase'
    key_name TEXT NOT NULL,
    api_key_encrypted TEXT NOT NULL, -- Encrypted!
    api_secret_encrypted TEXT, -- Encrypted!
    permissions JSONB DEFAULT '{}', -- {"trade": true, "read": true}
    is_active BOOLEAN DEFAULT true,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_trades_user_id ON user_trades(user_id);
CREATE INDEX IF NOT EXISTS idx_user_trades_symbol ON user_trades(symbol);
CREATE INDEX IF NOT EXISTS idx_user_portfolios_user_id ON user_portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_user_strategies_user_id ON user_strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_user_indicators_user_id ON user_indicators(user_id);
CREATE INDEX IF NOT EXISTS idx_user_symbols_user_id ON user_symbols(user_id);
CREATE INDEX IF NOT EXISTS idx_user_symbols_slot ON user_symbols(user_id, slot_number);

-- Enable Row Level Security (users only see their own data)
ALTER TABLE user_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_trading_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_indicators ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_symbols ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_api_keys ENABLE ROW LEVEL SECURITY;

SELECT 'User reference tables created in Smart Trading!' as status;

-- Show the tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name LIKE 'user_%'
ORDER BY table_name;