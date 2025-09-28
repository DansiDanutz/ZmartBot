-- CRITICAL SECURITY FIX FOR ZMARTYBRAIN
-- This fixes exposed auth.users data and removes dangerous SECURITY DEFINER

-- Step 1: Drop the dangerous view that exposes auth.users
DROP VIEW IF EXISTS public.user_details CASCADE;

-- Step 2: Create a safer view that only exposes necessary profile data
-- This view uses SECURITY INVOKER (default) and only shows public profile data
CREATE OR REPLACE VIEW public.user_profiles AS
SELECT
    p.id,
    p.full_name,
    p.username,
    p.updated_at
FROM public.profiles p
WHERE p.id = auth.uid();  -- Only show current user's profile

-- Step 3: Set proper permissions on the new view
GRANT SELECT ON public.user_profiles TO authenticated;
REVOKE ALL ON public.user_profiles FROM anon;  -- Anon users shouldn't see profiles

-- Step 4: Ensure profiles table has proper RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Step 5: Verify no other views expose auth.users
-- This query will show any remaining problematic views
SELECT
    schemaname,
    viewname,
    definition
FROM pg_views
WHERE schemaname IN ('public', 'api')
    AND definition ILIKE '%auth.users%';

-- Step 6: Check for any SECURITY DEFINER views
SELECT
    n.nspname AS schema,
    c.relname AS view_name,
    CASE
        WHEN c.relkind = 'v' THEN 'VIEW'
        WHEN c.relkind = 'm' THEN 'MATERIALIZED VIEW'
    END AS type
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind IN ('v', 'm')
    AND n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND pg_get_userbyid(c.relowner) = current_user
    AND EXISTS (
        SELECT 1
        FROM pg_depend d
        JOIN pg_rewrite r ON r.oid = d.objid
        WHERE r.ev_class = c.oid
            AND r.ev_type = '1'
            AND r.is_instead
    );

-- Step 7: Create a secure function to get user details if needed
CREATE OR REPLACE FUNCTION public.get_user_profile(user_id uuid)
RETURNS TABLE (
    id uuid,
    full_name text,
    username text
)
LANGUAGE plpgsql
SECURITY INVOKER  -- Uses permissions of the calling user
AS $$
BEGIN
    -- Only return data if requesting own profile or is admin
    IF user_id = auth.uid() OR auth.jwt()->>'role' = 'service_role' THEN
        RETURN QUERY
        SELECT p.id, p.full_name, p.username
        FROM public.profiles p
        WHERE p.id = user_id;
    ELSE
        -- Return empty result for unauthorized access
        RETURN;
    END IF;
END;
$$;

-- Grant execute permission only to authenticated users
GRANT EXECUTE ON FUNCTION public.get_user_profile(uuid) TO authenticated;
REVOKE EXECUTE ON FUNCTION public.get_user_profile(uuid) FROM anon;