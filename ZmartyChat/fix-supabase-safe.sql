-- ============================================
-- SAFE FIX SUPABASE ISSUES - Idempotent Script
-- ============================================
-- This script safely fixes issues without errors
-- It checks for existing objects before creating
-- ============================================

-- 1. DROP EXISTING POLICIES (to recreate them properly)
-- ============================================
DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can view own settings" ON public.user_settings;
DROP POLICY IF EXISTS "Users can update own settings" ON public.user_settings;
DROP POLICY IF EXISTS "Users can insert own settings" ON public.user_settings;
DROP POLICY IF EXISTS "Users can view own subscriptions" ON public.user_subscriptions;
DROP POLICY IF EXISTS "Users can view own signals" ON public.trading_signals;
DROP POLICY IF EXISTS "Users can insert own signals" ON public.trading_signals;
DROP POLICY IF EXISTS "Users can view own messages" ON public.chat_messages;
DROP POLICY IF EXISTS "Users can insert own messages" ON public.chat_messages;
DROP POLICY IF EXISTS "Users can manage own API keys" ON public.api_keys;

-- 2. CREATE OR REPLACE TABLES (safe approach)
-- ============================================

-- User Profiles Table (might exist)
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    country TEXT,
    phone_code TEXT,
    phone_number TEXT,
    tier TEXT DEFAULT 'free',
    credits INTEGER DEFAULT 100,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add missing columns if table exists
DO $$
BEGIN
    -- Add phone_code if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                  WHERE table_name='user_profiles' AND column_name='phone_code') THEN
        ALTER TABLE public.user_profiles ADD COLUMN phone_code TEXT;
    END IF;

    -- Add phone_number if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                  WHERE table_name='user_profiles' AND column_name='phone_number') THEN
        ALTER TABLE public.user_profiles ADD COLUMN phone_number TEXT;
    END IF;

    -- Add tier if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                  WHERE table_name='user_profiles' AND column_name='tier') THEN
        ALTER TABLE public.user_profiles ADD COLUMN tier TEXT DEFAULT 'free';
    END IF;

    -- Add credits if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                  WHERE table_name='user_profiles' AND column_name='credits') THEN
        ALTER TABLE public.user_profiles ADD COLUMN credits INTEGER DEFAULT 100;
    END IF;
END $$;

-- User Settings Table
CREATE TABLE IF NOT EXISTS public.user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    theme TEXT DEFAULT 'light',
    language TEXT DEFAULT 'en',
    notifications_enabled BOOLEAN DEFAULT true,
    email_notifications BOOLEAN DEFAULT true,
    trading_notifications BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Subscription Plans Table
CREATE TABLE IF NOT EXISTS public.subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    price DECIMAL(10,2) NOT NULL,
    credits_per_month INTEGER NOT NULL,
    features JSONB,
    stripe_price_id TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Subscriptions Table
CREATE TABLE IF NOT EXISTS public.user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES public.subscription_plans(id),
    stripe_subscription_id TEXT,
    status TEXT DEFAULT 'active',
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trading Signals Table
CREATE TABLE IF NOT EXISTS public.trading_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    exchange TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    confidence DECIMAL(5,2),
    price DECIMAL(20,8),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Sessions Table
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat Messages Table
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- API Keys Table
CREATE TABLE IF NOT EXISTS public.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    key_hash TEXT NOT NULL,
    last_used TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. INSERT DEFAULT SUBSCRIPTION PLANS (if not exist)
-- ============================================
INSERT INTO public.subscription_plans (name, price, credits_per_month, features)
VALUES
    ('Free', 0, 100, '{"ai_models": 1, "exchanges": 3, "signals_per_day": 10}'),
    ('Gold', 29.99, 1000, '{"ai_models": 3, "exchanges": 10, "signals_per_day": 100}'),
    ('Premium', 99.99, 99999, '{"ai_models": -1, "exchanges": -1, "signals_per_day": -1}')
ON CONFLICT (name) DO UPDATE SET
    price = EXCLUDED.price,
    credits_per_month = EXCLUDED.credits_per_month,
    features = EXCLUDED.features;

-- 4. ENABLE ROW LEVEL SECURITY
-- ============================================
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trading_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_plans ENABLE ROW LEVEL SECURITY;

-- 5. CREATE NEW RLS POLICIES
-- ============================================

-- User Profiles Policies
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- User Settings Policies
CREATE POLICY "Users can view own settings" ON public.user_settings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own settings" ON public.user_settings
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own settings" ON public.user_settings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- User Subscriptions Policies
CREATE POLICY "Users can view own subscriptions" ON public.user_subscriptions
    FOR SELECT USING (auth.uid() = user_id);

-- Trading Signals Policies
CREATE POLICY "Users can view own signals" ON public.trading_signals
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own signals" ON public.trading_signals
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Chat Messages Policies
CREATE POLICY "Users can view own messages" ON public.chat_messages
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own messages" ON public.chat_messages
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- API Keys Policies
CREATE POLICY "Users can manage own API keys" ON public.api_keys
    FOR ALL USING (auth.uid() = user_id);

-- Subscription Plans - Public read access
CREATE POLICY "Anyone can view plans" ON public.subscription_plans
    FOR SELECT USING (true);

-- 6. CREATE OR REPLACE FUNCTIONS
-- ============================================

-- Drop existing function/trigger first
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

-- Create improved handle_new_user function
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    free_plan_id UUID;
BEGIN
    -- Get the Free plan ID
    SELECT id INTO free_plan_id FROM public.subscription_plans WHERE name = 'Free' LIMIT 1;

    -- Create user profile (with better error handling)
    INSERT INTO public.user_profiles (id, email, full_name, country, tier, credits)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        COALESCE(NEW.raw_user_meta_data->>'country', 'US'),
        'free',
        100
    )
    ON CONFLICT (id) DO UPDATE SET
        email = EXCLUDED.email,
        full_name = COALESCE(EXCLUDED.full_name, user_profiles.full_name),
        country = COALESCE(EXCLUDED.country, user_profiles.country);

    -- Create user settings
    INSERT INTO public.user_settings (user_id)
    VALUES (NEW.id)
    ON CONFLICT (user_id) DO NOTHING;

    -- Create free subscription
    IF free_plan_id IS NOT NULL THEN
        INSERT INTO public.user_subscriptions (user_id, plan_id, status)
        VALUES (NEW.id, free_plan_id, 'active')
        ON CONFLICT DO NOTHING;
    END IF;

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        RAISE LOG 'Error in handle_new_user for user %: %', NEW.id, SQLERRM;
        RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new users
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Update timestamp function
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 7. CREATE UPDATE TRIGGERS
-- ============================================
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON public.user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS update_user_settings_updated_at ON public.user_settings;
CREATE TRIGGER update_user_settings_updated_at
    BEFORE UPDATE ON public.user_settings
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS update_user_subscriptions_updated_at ON public.user_subscriptions;
CREATE TRIGGER update_user_subscriptions_updated_at
    BEFORE UPDATE ON public.user_subscriptions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- 8. CREATE INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON public.user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_trading_signals_user_created ON public.trading_signals(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_created ON public.chat_messages(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON public.user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user ON public.user_subscriptions(user_id);

-- 9. GRANT PERMISSIONS
-- ============================================
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;

-- 10. FIX EXISTING USERS (if any)
-- ============================================
DO $$
DECLARE
    user_record RECORD;
    free_plan_id UUID;
BEGIN
    -- Get Free plan ID
    SELECT id INTO free_plan_id FROM public.subscription_plans WHERE name = 'Free' LIMIT 1;

    -- Loop through auth users and ensure they have profiles
    FOR user_record IN SELECT * FROM auth.users LOOP
        -- Ensure user profile exists
        INSERT INTO public.user_profiles (id, email, tier, credits)
        VALUES (user_record.id, user_record.email, 'free', 100)
        ON CONFLICT (id) DO NOTHING;

        -- Ensure user settings exist
        INSERT INTO public.user_settings (user_id)
        VALUES (user_record.id)
        ON CONFLICT (user_id) DO NOTHING;

        -- Ensure user has a subscription
        IF free_plan_id IS NOT NULL THEN
            INSERT INTO public.user_subscriptions (user_id, plan_id, status)
            SELECT user_record.id, free_plan_id, 'active'
            WHERE NOT EXISTS (
                SELECT 1 FROM public.user_subscriptions
                WHERE user_id = user_record.id
            );
        END IF;
    END LOOP;
END $$;

-- 11. VERIFICATION
-- ============================================
DO $$
DECLARE
    table_count INTEGER;
    policy_count INTEGER;
    plan_count INTEGER;
BEGIN
    -- Count tables
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('user_profiles', 'user_settings', 'subscription_plans', 'user_subscriptions', 'trading_signals', 'chat_messages');

    -- Count policies
    SELECT COUNT(*) INTO policy_count
    FROM pg_policies
    WHERE schemaname = 'public';

    -- Count plans
    SELECT COUNT(*) INTO plan_count
    FROM public.subscription_plans;

    RAISE NOTICE '✅ Setup Complete:';
    RAISE NOTICE '   Tables created: %', table_count;
    RAISE NOTICE '   RLS policies: %', policy_count;
    RAISE NOTICE '   Subscription plans: %', plan_count;
END $$;

-- 12. TEST QUERIES
-- ============================================
-- Run these to verify:
SELECT 'Tables' as check_type, COUNT(*) as count FROM information_schema.tables WHERE table_schema = 'public';
SELECT 'Plans' as check_type, COUNT(*) as count FROM public.subscription_plans;
SELECT 'Users' as check_type, COUNT(*) as count FROM auth.users;
SELECT 'Profiles' as check_type, COUNT(*) as count FROM public.user_profiles;

-- ============================================
-- END OF SAFE SCRIPT
-- ============================================