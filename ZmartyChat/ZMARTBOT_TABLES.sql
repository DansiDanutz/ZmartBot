-- =====================================================
-- ZMARTBOT DATABASE SETUP
-- Run this in: https://supabase.com/dashboard/project/asjtxrmftmutcsnqgidy/sql
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if needed (BE CAREFUL!)
-- DROP TABLE IF EXISTS public.user_trading_profiles CASCADE;
-- DROP TABLE IF EXISTS public.user_portfolios CASCADE;
-- DROP TABLE IF EXISTS public.user_strategies CASCADE;
-- DROP TABLE IF EXISTS public.user_trades CASCADE;
-- DROP TABLE IF EXISTS public.user_api_keys CASCADE;

-- Create user trading profiles (links to ZmartyBrain users)
CREATE TABLE IF NOT EXISTS public.user_trading_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- From ZmartyBrain auth.users
    email TEXT NOT NULL,
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'enterprise')),
    trading_enabled BOOLEAN DEFAULT false,
    api_access BOOLEAN DEFAULT false,
    total_portfolio_value DECIMAL(20,8) DEFAULT 0,
    total_pnl DECIMAL(20,8) DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Create user portfolios
CREATE TABLE IF NOT EXISTS public.user_portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    symbol TEXT NOT NULL,
    amount DECIMAL(20,8) NOT NULL DEFAULT 0,
    avg_buy_price DECIMAL(20,8),
    current_price DECIMAL(20,8),
    current_value DECIMAL(20,8),
    pnl DECIMAL(20,8),
    pnl_percentage DECIMAL(10,2),
    allocation_percentage DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, symbol)
);

-- Create trading strategies per user
CREATE TABLE IF NOT EXISTS public.user_strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    strategy_name TEXT NOT NULL,
    strategy_type TEXT CHECK (strategy_type IN ('manual', 'automated', 'ai', 'custom')),
    strategy_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT false,
    performance_metrics JSONB DEFAULT '{"total_trades": 0, "win_rate": 0, "total_pnl": 0}',
    risk_level TEXT DEFAULT 'medium' CHECK (risk_level IN ('low', 'medium', 'high', 'extreme')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user trades history
CREATE TABLE IF NOT EXISTS public.user_trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    strategy_id UUID REFERENCES public.user_strategies(id) ON DELETE SET NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL CHECK (side IN ('buy', 'sell')),
    amount DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    total DECIMAL(20,8) NOT NULL,
    fee DECIMAL(20,8) DEFAULT 0,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'executed', 'cancelled', 'failed')),
    exchange TEXT,
    order_id TEXT,
    executed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user API keys (encrypted)
CREATE TABLE IF NOT EXISTS public.user_api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    exchange TEXT NOT NULL,
    api_key_encrypted TEXT, -- Will be encrypted
    api_secret_encrypted TEXT, -- Will be encrypted
    is_active BOOLEAN DEFAULT true,
    is_testnet BOOLEAN DEFAULT false,
    permissions JSONB DEFAULT '{"spot": true, "futures": false, "withdraw": false}',
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, exchange)
);

-- Create user alerts
CREATE TABLE IF NOT EXISTS public.user_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    alert_type TEXT NOT NULL CHECK (alert_type IN ('price', 'volume', 'risk', 'opportunity', 'news')),
    symbol TEXT,
    condition JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    triggered_count INTEGER DEFAULT 0,
    last_triggered TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_trading_profiles_user_id ON public.user_trading_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_portfolios_user_id ON public.user_portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_user_strategies_user_id ON public.user_strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_user_trades_user_id ON public.user_trades(user_id);
CREATE INDEX IF NOT EXISTS idx_user_trades_created_at ON public.user_trades(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_api_keys_user_id ON public.user_api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_user_alerts_user_id ON public.user_alerts(user_id);

-- Enable Row Level Security
ALTER TABLE public.user_trading_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_alerts ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (temporarily allow all for development)
-- TODO: Tighten these policies for production

CREATE POLICY "Allow all for user_trading_profiles"
    ON public.user_trading_profiles FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow all for user_portfolios"
    ON public.user_portfolios FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow all for user_strategies"
    ON public.user_strategies FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow all for user_trades"
    ON public.user_trades FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow all for user_api_keys"
    ON public.user_api_keys FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow all for user_alerts"
    ON public.user_alerts FOR ALL
    USING (true)
    WITH CHECK (true);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to auto-update updated_at
CREATE TRIGGER update_user_trading_profiles_updated_at
    BEFORE UPDATE ON public.user_trading_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_portfolios_updated_at
    BEFORE UPDATE ON public.user_portfolios
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_strategies_updated_at
    BEFORE UPDATE ON public.user_strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_api_keys_updated_at
    BEFORE UPDATE ON public.user_api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL ON public.user_trading_profiles TO anon;
GRANT ALL ON public.user_portfolios TO anon;
GRANT ALL ON public.user_strategies TO anon;
GRANT ALL ON public.user_trades TO anon;
GRANT ALL ON public.user_api_keys TO anon;
GRANT ALL ON public.user_alerts TO anon;

-- Success message
SELECT 'ZmartBot tables created successfully!' AS status;