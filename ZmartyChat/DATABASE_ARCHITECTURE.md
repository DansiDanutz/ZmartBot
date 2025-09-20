# 📊 DATABASE ARCHITECTURE - TWO PROJECTS

## 🧠 PROJECT 1: ZmartyBrain (xhskmqsgtdhehzlvtuns)
**Purpose**: User Management & Authentication
**URL**: https://xhskmqsgtdhehzlvtuns.supabase.co

### Tables Needed:
```sql
-- Users are managed by Supabase Auth (auth.users table)

-- Additional user profile data
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'enterprise')),
    name TEXT,
    country TEXT,
    profile_completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User subscription/tier history
CREATE TABLE IF NOT EXISTS public.user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    tier TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    status TEXT DEFAULT 'active'
);

-- User activity tracking
CREATE TABLE IF NOT EXISTS public.user_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🤖 PROJECT 2: ZmartBot (asjtxrmftmutcsnqgidy)
**Purpose**: Crypto Trading & Market Data
**URL**: https://asjtxrmftmutcsnqgidy.supabase.co

### Existing Tables (Already Created):
- cryptometer_* (market analysis tables)
- cryptoverse_* (risk analysis tables)
- risk_metric_grid
- orchestration_states
- service_communications
- alert_collections
- Zmart Vaults

### Additional Tables Needed for User Trading:
```sql
-- Link to users from ZmartyBrain
CREATE TABLE IF NOT EXISTS public.user_trading_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- From ZmartyBrain auth.users
    email TEXT NOT NULL,
    tier TEXT DEFAULT 'free',
    trading_enabled BOOLEAN DEFAULT false,
    api_access BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User portfolios
CREATE TABLE IF NOT EXISTS public.user_portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    symbol TEXT NOT NULL,
    amount DECIMAL(20,8),
    avg_buy_price DECIMAL(20,8),
    current_value DECIMAL(20,8),
    pnl DECIMAL(20,8),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Trading strategies per user
CREATE TABLE IF NOT EXISTS public.user_strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    strategy_name TEXT NOT NULL,
    strategy_config JSONB,
    is_active BOOLEAN DEFAULT false,
    performance_metrics JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User trades history
CREATE TABLE IF NOT EXISTS public.user_trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT CHECK (side IN ('buy', 'sell')),
    amount DECIMAL(20,8),
    price DECIMAL(20,8),
    total DECIMAL(20,8),
    status TEXT DEFAULT 'pending',
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User API keys (encrypted)
CREATE TABLE IF NOT EXISTS public.user_api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    exchange TEXT NOT NULL,
    api_key_encrypted TEXT,
    api_secret_encrypted TEXT,
    is_active BOOLEAN DEFAULT true,
    permissions JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔗 CONNECTING THE PROJECTS

### Flow:
1. User registers in **ZmartyBrain** → Creates auth.users entry
2. After registration → Create profile in **ZmartBot** user_trading_profiles
3. User logs in via **ZmartyBrain** → Access trading in **ZmartBot**

### Data Sync:
- User ID is the common key between projects
- Email and tier are synced to ZmartBot for quick access
- Trading features check tier from ZmartyBrain

## 🔧 IMPLEMENTATION STEPS:

### 1. ZmartyBrain Setup:
```sql
-- Run these in ZmartyBrain SQL Editor
-- https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create user profiles table
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'enterprise')),
    name TEXT,
    country TEXT,
    profile_completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create RLS policies
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

### 2. ZmartBot Setup:
```sql
-- Run these in ZmartBot SQL Editor
-- https://supabase.com/dashboard/project/asjtxrmftmutcsnqgidy/sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create user trading profiles
CREATE TABLE IF NOT EXISTS public.user_trading_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    email TEXT NOT NULL,
    tier TEXT DEFAULT 'free',
    trading_enabled BOOLEAN DEFAULT false,
    api_access BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create portfolios table
CREATE TABLE IF NOT EXISTS public.user_portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    symbol TEXT NOT NULL,
    amount DECIMAL(20,8),
    avg_buy_price DECIMAL(20,8),
    current_value DECIMAL(20,8),
    pnl DECIMAL(20,8),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.user_trading_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_portfolios ENABLE ROW LEVEL SECURITY;

-- Create policies (public read for now, will tighten later)
CREATE POLICY "Public read" ON public.user_trading_profiles
    FOR SELECT USING (true);

CREATE POLICY "Public insert" ON public.user_trading_profiles
    FOR INSERT WITH CHECK (true);
```

## 📋 CHECKLIST:

- [ ] Create tables in ZmartyBrain
- [ ] Create tables in ZmartBot
- [ ] Test user registration flow
- [ ] Test data sync between projects
- [ ] Configure email templates
- [ ] Deploy to production