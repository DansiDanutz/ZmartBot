-- Comprehensive Security Fix for ZmartBot Supabase Database
-- Addresses SECURITY DEFINER view warnings and implements security best practices

-- 1. Fix user_profiles view security mode
-- Convert from SECURITY DEFINER to SECURITY INVOKER for proper RLS enforcement
ALTER VIEW IF EXISTS public.user_profiles SET (security_invoker = true);

-- 2. Audit all views for security issues
-- Check for any other SECURITY DEFINER views that should be SECURITY INVOKER
DO $$
DECLARE
    view_record RECORD;
BEGIN
    FOR view_record IN
        SELECT schemaname, viewname
        FROM pg_views
        WHERE schemaname = 'public'
        AND NOT (viewoptions && ARRAY['security_invoker=true'])
    LOOP
        -- Log the views that need attention
        RAISE NOTICE 'View %.% is using SECURITY DEFINER mode', view_record.schemaname, view_record.viewname;

        -- Automatically fix common views (uncomment if needed)
        -- EXECUTE format('ALTER VIEW %I.%I SET (security_invoker = true)',
        --               view_record.schemaname, view_record.viewname);
    END LOOP;
END $$;

-- 3. Ensure RLS is enabled on relevant tables
-- Enable RLS on user-related tables if not already enabled
ALTER TABLE IF EXISTS public.user_profiles ENABLE ROW LEVEL SECURITY;

-- 4. Create or update RLS policies for user_profiles
-- Policy to allow users to see only their own profile
DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = user_id);

-- Policy to allow users to update only their own profile
DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

-- Policy to allow users to insert their own profile
DROP POLICY IF EXISTS "Users can insert own profile" ON public.user_profiles;
CREATE POLICY "Users can insert own profile" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 5. Verify security configuration
-- Show all views and their security modes
SELECT
    schemaname,
    viewname,
    viewowner,
    CASE
        WHEN viewoptions && ARRAY['security_invoker=true'] THEN 'SECURITY INVOKER ✅'
        ELSE 'SECURITY DEFINER ⚠️'
    END as security_mode
FROM pg_views
WHERE schemaname = 'public'
ORDER BY viewname;

-- Show RLS status for all tables
SELECT
    schemaname,
    tablename,
    rowsecurity as rls_enabled,
    CASE
        WHEN rowsecurity THEN 'RLS Enabled ✅'
        ELSE 'RLS Disabled ⚠️'
    END as rls_status
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Show policies for user_profiles table
SELECT
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public' AND tablename = 'user_profiles'
ORDER BY policyname;