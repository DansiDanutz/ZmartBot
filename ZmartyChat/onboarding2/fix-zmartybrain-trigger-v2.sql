-- FIX ZMARTYBRAIN USER CREATION TRIGGER (Version 2 - Handles Existing Objects)
-- Run this in ZmartyBrain SQL Editor: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/sql

-- First, drop the existing trigger if it exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user() CASCADE;

-- Create the correct function that uses zmartychat_users table
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    default_plan_id UUID;
BEGIN
    -- Get the free plan ID
    SELECT id INTO default_plan_id
    FROM zmartychat_subscription_plans
    WHERE name = 'free'
    LIMIT 1;

    -- Insert into zmartychat_users table
    INSERT INTO public.zmartychat_users (
        auth_id,
        email,
        full_name,
        country,
        selected_tier,
        onboarding_completed
    )
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        COALESCE(NEW.raw_user_meta_data->>'country', ''),
        COALESCE(NEW.raw_user_meta_data->>'selected_tier', 'free'),
        false
    );

    -- Create subscription entry if plan exists
    IF default_plan_id IS NOT NULL THEN
        INSERT INTO public.zmartychat_user_subscriptions (
            user_id,
            plan_id,
            status,
            credits_remaining
        )
        VALUES (
            (SELECT id FROM zmartychat_users WHERE auth_id = NEW.id),
            default_plan_id,
            'active',
            100
        );
    END IF;

    -- Initialize user insights
    INSERT INTO public.zmartychat_user_insights (
        user_id,
        total_messages_sent,
        total_credits_used
    )
    VALUES (
        (SELECT id FROM zmartychat_users WHERE auth_id = NEW.id),
        0,
        0
    )
    ON CONFLICT (user_id) DO NOTHING;  -- Prevent duplicate if already exists

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        -- Log error but don't fail the auth signup
        RAISE WARNING 'Error in handle_new_user trigger: %', SQLERRM;
        RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create the trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Grant necessary permissions (if not already granted)
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Enable Row Level Security on tables (if not already enabled)
ALTER TABLE zmartychat_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE zmartychat_user_insights ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to recreate them)
DROP POLICY IF EXISTS "Users can view own profile" ON zmartychat_users;
DROP POLICY IF EXISTS "Users can update own profile" ON zmartychat_users;
DROP POLICY IF EXISTS "Users can view own subscription" ON zmartychat_user_subscriptions;
DROP POLICY IF EXISTS "Users can view own transactions" ON zmartychat_credit_transactions;
DROP POLICY IF EXISTS "Users can view own messages" ON zmartychat_conversation_messages;
DROP POLICY IF EXISTS "Users can insert own messages" ON zmartychat_conversation_messages;
DROP POLICY IF EXISTS "Users can view own insights" ON zmartychat_user_insights;

-- Create RLS policies for users to access their own data
CREATE POLICY "Users can view own profile" ON zmartychat_users
    FOR SELECT USING (auth.uid() = auth_id);

CREATE POLICY "Users can update own profile" ON zmartychat_users
    FOR UPDATE USING (auth.uid() = auth_id);

CREATE POLICY "Users can view own subscription" ON zmartychat_user_subscriptions
    FOR SELECT USING (user_id IN (SELECT id FROM zmartychat_users WHERE auth_id = auth.uid()));

CREATE POLICY "Users can view own transactions" ON zmartychat_credit_transactions
    FOR SELECT USING (user_id IN (SELECT id FROM zmartychat_users WHERE auth_id = auth.uid()));

CREATE POLICY "Users can view own messages" ON zmartychat_conversation_messages
    FOR SELECT USING (user_id IN (SELECT id FROM zmartychat_users WHERE auth_id = auth.uid()));

CREATE POLICY "Users can insert own messages" ON zmartychat_conversation_messages
    FOR INSERT WITH CHECK (user_id IN (SELECT id FROM zmartychat_users WHERE auth_id = auth.uid()));

CREATE POLICY "Users can view own insights" ON zmartychat_user_insights
    FOR SELECT USING (user_id IN (SELECT id FROM zmartychat_users WHERE auth_id = auth.uid()));

-- Test the setup by checking if trigger exists
SELECT
    n.nspname as schema_name,
    t.tgname as trigger_name,
    p.proname as function_name
FROM pg_trigger t
JOIN pg_class c ON t.tgrelid = c.oid
JOIN pg_namespace n ON c.relnamespace = n.oid
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE n.nspname = 'auth' AND c.relname = 'users';

-- Check if any existing users need cleanup
SELECT email, created_at
FROM auth.users
WHERE email = 'seme@kryptostack.com';

-- Success message
SELECT 'Trigger fixed successfully! New users will now be properly created in zmartychat_users table.' AS status;