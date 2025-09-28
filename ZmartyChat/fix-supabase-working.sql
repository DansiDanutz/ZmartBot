-- ============================================
-- WORKING FIX - Handles auth.users properly
-- ============================================

-- 1. Create user_profiles table (without email constraint first)
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
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

-- 2. Add unique constraint on email if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'user_profiles_email_key'
    ) THEN
        ALTER TABLE public.user_profiles
        ADD CONSTRAINT user_profiles_email_key UNIQUE (email);
    END IF;
END $$;

-- 3. Enable RLS
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- 4. Drop and recreate policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;

CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- 5. Create subscription plans table
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

-- 6. Insert plans
INSERT INTO public.subscription_plans (name, price, credits_per_month, features)
VALUES
    ('Free', 0, 100, '{"ai_models": 1, "exchanges": 3, "signals_per_day": 10}'),
    ('Gold', 29.99, 1000, '{"ai_models": 3, "exchanges": 10, "signals_per_day": 100}'),
    ('Premium', 99.99, 99999, '{"ai_models": "unlimited", "exchanges": "unlimited", "signals_per_day": "unlimited"}')
ON CONFLICT (name) DO NOTHING;

-- 7. Create user settings table
CREATE TABLE IF NOT EXISTS public.user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    theme TEXT DEFAULT 'light',
    language TEXT DEFAULT 'en',
    notifications_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- 8. Enable RLS on other tables
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_plans ENABLE ROW LEVEL SECURITY;

-- 9. Create policies for settings
DROP POLICY IF EXISTS "Users can manage own settings" ON public.user_settings;
CREATE POLICY "Users can manage own settings" ON public.user_settings
    FOR ALL USING (auth.uid() = user_id);

-- 10. Create policy for plans (public read)
DROP POLICY IF EXISTS "Anyone can view plans" ON public.subscription_plans;
CREATE POLICY "Anyone can view plans" ON public.subscription_plans
    FOR SELECT USING (true);

-- 11. Create the trigger function (fixed version)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert into user_profiles using NEW.email from auth.users
    INSERT INTO public.user_profiles (id, email, full_name, country, tier, credits)
    VALUES (
        NEW.id,
        NEW.email::text,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        COALESCE(NEW.raw_user_meta_data->>'country', 'US'),
        'free',
        100
    )
    ON CONFLICT (id) DO UPDATE SET
        email = EXCLUDED.email,
        full_name = COALESCE(EXCLUDED.full_name, user_profiles.full_name),
        country = COALESCE(EXCLUDED.country, user_profiles.country);

    -- Insert settings
    INSERT INTO public.user_settings (user_id)
    VALUES (NEW.id)
    ON CONFLICT (user_id) DO NOTHING;

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        -- Log but don't fail
        RAISE WARNING 'Error in handle_new_user: %', SQLERRM;
        RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 12. Create trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- 13. Fix any existing users (without using email column directly)
DO $$
DECLARE
    user_record RECORD;
BEGIN
    FOR user_record IN
        SELECT id, email, raw_user_meta_data
        FROM auth.users
    LOOP
        -- Ensure profile exists
        INSERT INTO public.user_profiles (id, email, full_name, country, tier, credits)
        VALUES (
            user_record.id,
            user_record.email,
            COALESCE(user_record.raw_user_meta_data->>'full_name', ''),
            COALESCE(user_record.raw_user_meta_data->>'country', 'US'),
            'free',
            100
        )
        ON CONFLICT (id) DO UPDATE SET
            email = COALESCE(user_profiles.email, EXCLUDED.email);

        -- Ensure settings exist
        INSERT INTO public.user_settings (user_id)
        VALUES (user_record.id)
        ON CONFLICT (user_id) DO NOTHING;
    END LOOP;
END $$;

-- 14. Grant permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- 15. Final check
SELECT
    'Setup Status' as check,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_profiles') as profiles_table,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_settings') as settings_table,
    (SELECT COUNT(*) FROM public.subscription_plans) as plans_count,
    (SELECT COUNT(*) FROM auth.users) as total_users,
    (SELECT COUNT(*) FROM public.user_profiles) as total_profiles;