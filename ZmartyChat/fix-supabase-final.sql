-- ============================================
-- SUPABASE FIX - COMPLETE SETUP
-- ============================================

-- Create all tables
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

CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    key_hash TEXT NOT NULL,
    last_used TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add missing columns to existing tables
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_name='user_profiles' AND table_schema='public') THEN

        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name='user_profiles' AND column_name='phone_code') THEN
            ALTER TABLE public.user_profiles ADD COLUMN phone_code TEXT;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name='user_profiles' AND column_name='phone_number') THEN
            ALTER TABLE public.user_profiles ADD COLUMN phone_number TEXT;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name='user_profiles' AND column_name='tier') THEN
            ALTER TABLE public.user_profiles ADD COLUMN tier TEXT DEFAULT 'free';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name='user_profiles' AND column_name='credits') THEN
            ALTER TABLE public.user_profiles ADD COLUMN credits INTEGER DEFAULT 100;
        END IF;
    END IF;
END $$;

-- Insert subscription plans
INSERT INTO public.subscription_plans (name, price, credits_per_month, features)
VALUES
    ('Free', 0, 100, '{"ai_models": 1, "exchanges": 3, "signals_per_day": 10}'),
    ('Gold', 29.99, 1000, '{"ai_models": 3, "exchanges": 10, "signals_per_day": 100}'),
    ('Premium', 99.99, 99999, '{"ai_models": "unlimited", "exchanges": "unlimited", "signals_per_day": "unlimited"}')
ON CONFLICT (name) DO UPDATE SET
    price = EXCLUDED.price,
    credits_per_month = EXCLUDED.credits_per_month,
    features = EXCLUDED.features;

-- Enable RLS on all tables
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trading_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_plans ENABLE ROW LEVEL SECURITY;

-- Drop existing policies safely
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='user_profiles' AND table_schema='public') THEN
        DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
        DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='user_settings' AND table_schema='public') THEN
        DROP POLICY IF EXISTS "Users can view own settings" ON public.user_settings;
        DROP POLICY IF EXISTS "Users can update own settings" ON public.user_settings;
        DROP POLICY IF EXISTS "Users can insert own settings" ON public.user_settings;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='user_subscriptions' AND table_schema='public') THEN
        DROP POLICY IF EXISTS "Users can view own subscriptions" ON public.user_subscriptions;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='trading_signals' AND table_schema='public') THEN
        DROP POLICY IF EXISTS "Users can view own signals" ON public.trading_signals;
        DROP POLICY IF EXISTS "Users can insert own signals" ON public.trading_signals;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='chat_messages' AND table_schema='public') THEN
        DROP POLICY IF EXISTS "Users can view own messages" ON public.chat_messages;
        DROP POLICY IF EXISTS "Users can insert own messages" ON public.chat_messages;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='api_keys' AND table_schema='public') THEN
        DROP POLICY IF EXISTS "Users can manage own API keys" ON public.api_keys;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='subscription_plans' AND table_schema='public') THEN
        DROP POLICY IF EXISTS "Anyone can view plans" ON public.subscription_plans;
    END IF;
END $$;

-- Create RLS policies
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own settings" ON public.user_settings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own settings" ON public.user_settings
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own settings" ON public.user_settings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own subscriptions" ON public.user_subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own signals" ON public.trading_signals
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own signals" ON public.trading_signals
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own messages" ON public.chat_messages
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own messages" ON public.chat_messages
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can manage own API keys" ON public.api_keys
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Anyone can view plans" ON public.subscription_plans
    FOR SELECT USING (true);

-- Create or replace functions
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    free_plan_id UUID;
BEGIN
    SELECT id INTO free_plan_id FROM public.subscription_plans WHERE name = 'Free' LIMIT 1;

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

    INSERT INTO public.user_settings (user_id)
    VALUES (NEW.id)
    ON CONFLICT (user_id) DO NOTHING;

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

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create update triggers
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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON public.user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_trading_signals_user_created ON public.trading_signals(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_created ON public.chat_messages(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON public.user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user ON public.user_subscriptions(user_id);

-- Grant permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;

-- Fix existing users
DO $$
DECLARE
    user_record RECORD;
    free_plan_id UUID;
BEGIN
    SELECT id INTO free_plan_id FROM public.subscription_plans WHERE name = 'Free' LIMIT 1;

    FOR user_record IN SELECT * FROM auth.users LOOP
        INSERT INTO public.user_profiles (id, email, tier, credits)
        VALUES (user_record.id, user_record.email, 'free', 100)
        ON CONFLICT (id) DO NOTHING;

        INSERT INTO public.user_settings (user_id)
        VALUES (user_record.id)
        ON CONFLICT (user_id) DO NOTHING;

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

-- Final verification
SELECT 'Tables Created' as check_type, COUNT(*) as count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('user_profiles', 'user_settings', 'subscription_plans',
                   'user_subscriptions', 'trading_signals', 'chat_messages',
                   'user_sessions', 'api_keys');

SELECT 'Subscription Plans' as check_type, COUNT(*) as count
FROM public.subscription_plans;

SELECT 'RLS Policies' as check_type, COUNT(*) as count
FROM pg_policies
WHERE schemaname = 'public';

SELECT 'Existing Users' as check_type, COUNT(*) as count
FROM auth.users;

SELECT 'User Profiles' as check_type, COUNT(*) as count
FROM public.user_profiles;

SELECT name, price, credits_per_month FROM public.subscription_plans ORDER BY price;