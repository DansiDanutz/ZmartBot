-- =====================================================
-- ZMARTYBRAIN DATABASE SETUP
-- Run this in: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/sql
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if needed (BE CAREFUL!)
-- DROP TABLE IF EXISTS public.user_profiles CASCADE;
-- DROP TABLE IF EXISTS public.user_subscriptions CASCADE;
-- DROP TABLE IF EXISTS public.user_activity CASCADE;

-- Create user profiles table
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'enterprise')),
    name TEXT,
    country TEXT,
    profile_completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Create user subscriptions table
CREATE TABLE IF NOT EXISTS public.user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    tier TEXT NOT NULL CHECK (tier IN ('free', 'pro', 'enterprise')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user activity table
CREATE TABLE IF NOT EXISTS public.user_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON public.user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON public.user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON public.user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_created_at ON public.user_activity(created_at DESC);

-- Enable Row Level Security
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_activity ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for user_profiles
CREATE POLICY "Users can view own profile"
    ON public.user_profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
    ON public.user_profiles FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile"
    ON public.user_profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create RLS policies for user_subscriptions
CREATE POLICY "Users can view own subscriptions"
    ON public.user_subscriptions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage subscriptions"
    ON public.user_subscriptions FOR ALL
    USING (auth.role() = 'service_role');

-- Create RLS policies for user_activity
CREATE POLICY "Users can view own activity"
    ON public.user_activity FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own activity"
    ON public.user_activity FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to auto-update updated_at
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to auto-create user profile after signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (user_id, tier, name, country)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'tier', 'free'),
        COALESCE(NEW.raw_user_meta_data->>'name', ''),
        COALESCE(NEW.raw_user_meta_data->>'country', '')
    );

    INSERT INTO public.user_subscriptions (user_id, tier)
    VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data->>'tier', 'free'));

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to auto-create profile on user signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Grant permissions
GRANT ALL ON public.user_profiles TO authenticated;
GRANT ALL ON public.user_subscriptions TO authenticated;
GRANT ALL ON public.user_activity TO authenticated;

-- Success message
SELECT 'ZmartyBrain tables created successfully!' AS status;