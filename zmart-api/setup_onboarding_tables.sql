-- =====================================================
-- SETUP TABLES FOR ONBOARDING APP
-- =====================================================
-- Run this in your Supabase SQL Editor to ensure all required tables exist

-- =====================================================
-- 1. CREATE PROFILES TABLE (if not exists)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create RLS policies for profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;

-- Users can view their own profile
CREATE POLICY "Users can view own profile" ON public.profiles
  FOR SELECT
  TO authenticated
  USING ((SELECT auth.uid()) = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON public.profiles
  FOR UPDATE
  TO authenticated
  USING ((SELECT auth.uid()) = id)
  WITH CHECK ((SELECT auth.uid()) = id);

-- Users can insert their own profile
CREATE POLICY "Users can insert own profile" ON public.profiles
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid()) = id);

-- =====================================================
-- 2. CREATE TRIGGER FOR NEW USER PROFILES
-- =====================================================
-- Function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_catalog
AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, created_at, updated_at)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    NOW(),
    NOW()
  )
  ON CONFLICT (id) DO UPDATE
  SET
    email = EXCLUDED.email,
    full_name = COALESCE(EXCLUDED.full_name, profiles.full_name),
    updated_at = NOW();

  RETURN NEW;
END;
$$;

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Create trigger for new users
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- =====================================================
-- 3. CHECK EXISTING DATA
-- =====================================================
-- Check if tables exist
SELECT
  'Tables Status' as check_type,
  EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'profiles') as profiles_exists,
  EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') as users_table_exists,
  EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'invitations') as invitations_exists;

-- Check RLS status
SELECT
  'RLS Status' as check_type,
  tablename,
  rowsecurity as rls_enabled,
  COUNT(*) FILTER (WHERE policyname IS NOT NULL) as policy_count
FROM pg_tables
LEFT JOIN pg_policies ON pg_tables.tablename = pg_policies.tablename
WHERE pg_tables.schemaname = 'public'
  AND pg_tables.tablename IN ('profiles', 'users', 'invitations')
GROUP BY pg_tables.tablename, pg_tables.rowsecurity;

-- =====================================================
-- 4. CONFIGURE SUPABASE AUTH SETTINGS
-- =====================================================
-- Note: These settings must be configured in the Supabase Dashboard:
-- 1. Go to Authentication > Providers
-- 2. Enable Email/Password authentication
-- 3. Configure Google OAuth with your Client ID:
--    - Client ID: 966065216838-fu5fmuckc7n4e9pjbvg4o1m9vo6d9uur.apps.googleusercontent.com
--    - Add authorized redirect URLs:
--      - https://xhskmqsgtdhehzlvtuns.supabase.co/auth/v1/callback
--      - https://vermillion-paprenjak-67497b.netlify.app/auth/callback
-- 4. Configure Email Templates in Authentication > Email Templates
-- 5. Set Site URL to: https://vermillion-paprenjak-67497b.netlify.app
-- 6. Add Redirect URLs:
--    - https://vermillion-paprenjak-67497b.netlify.app/*
--    - http://localhost:5173/*

-- =====================================================
-- 5. VERIFICATION QUERIES
-- =====================================================

-- Check auth.users table
SELECT
  'Auth Users' as table_name,
  COUNT(*) as user_count
FROM auth.users;

-- Check profiles table
SELECT
  'Profiles' as table_name,
  COUNT(*) as profile_count
FROM public.profiles;

-- Verify function has correct search_path
SELECT
  'Function Security' as check_type,
  proname as function_name,
  CASE
    WHEN proconfig IS NOT NULL AND 'search_path=public, pg_catalog' = ANY(proconfig)
    THEN '✅ Secure'
    ELSE '⚠️ Needs search_path'
  END as security_status
FROM pg_proc
WHERE proname = 'handle_new_user'
AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

-- =====================================================
-- SUMMARY
-- =====================================================
-- After running this script:
-- ✅ Profiles table will be created with proper RLS
-- ✅ New users will automatically get a profile
-- ✅ Authentication will work with your onboarding app
--
-- Next steps:
-- 1. Configure OAuth in Supabase Dashboard
-- 2. Set Site URL and Redirect URLs
-- 3. Test registration at https://vermillion-paprenjak-67497b.netlify.app