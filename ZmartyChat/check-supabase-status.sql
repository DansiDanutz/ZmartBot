-- ============================================
-- QUICK DIAGNOSTIC - Check Current State
-- ============================================
-- Run this to see what exists already

-- Check which tables exist
SELECT
    table_name,
    CASE
        WHEN table_name IN ('user_profiles', 'user_settings', 'subscription_plans',
                           'user_subscriptions', 'trading_signals', 'chat_messages',
                           'user_sessions', 'api_keys')
        THEN '✅ Required'
        ELSE '⚠️ Extra'
    END as status
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Check if user_profiles table has the right columns
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'user_profiles'
AND table_schema = 'public'
ORDER BY ordinal_position;

-- Check subscription plans
SELECT name, price, credits_per_month
FROM public.subscription_plans
ORDER BY price;

-- Check how many users exist
SELECT COUNT(*) as total_users FROM auth.users;

-- Check how many user profiles exist
SELECT COUNT(*) as total_profiles FROM public.user_profiles;

-- Check RLS policies
SELECT tablename, policyname, permissive, roles, cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Check if triggers exist
SELECT trigger_name, event_manipulation, event_object_table
FROM information_schema.triggers
WHERE trigger_schema = 'public'
OR event_object_schema = 'auth';

-- Check for any locks or long-running queries
SELECT
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query,
    state
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
AND state != 'idle';