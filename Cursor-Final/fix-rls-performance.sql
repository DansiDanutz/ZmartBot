-- Fix RLS Performance Issues for ZmartyBrain
-- This optimizes auth function calls by using subqueries to prevent re-evaluation for each row

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can view own credits" ON public.user_credits;

-- Recreate optimized policies for profiles table
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT
    USING (id = (SELECT auth.uid()));

CREATE POLICY "Users can insert own profile" ON public.profiles
    FOR INSERT
    WITH CHECK (id = (SELECT auth.uid()));

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE
    USING (id = (SELECT auth.uid()))
    WITH CHECK (id = (SELECT auth.uid()));

-- Recreate optimized policy for user_credits table
CREATE POLICY "Users can view own credits" ON public.user_credits
    FOR SELECT
    USING (user_id = (SELECT auth.uid()));

-- Optional: Add policies for user_credits if they need insert/update
CREATE POLICY "Users can insert own credits" ON public.user_credits
    FOR INSERT
    WITH CHECK (user_id = (SELECT auth.uid()));

CREATE POLICY "Users can update own credits" ON public.user_credits
    FOR UPDATE
    USING (user_id = (SELECT auth.uid()))
    WITH CHECK (user_id = (SELECT auth.uid()));

-- Verify the changes
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
    AND tablename IN ('profiles', 'user_credits')
ORDER BY tablename, policyname;