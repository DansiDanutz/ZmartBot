-- Fix SECURITY DEFINER view warning for user_profiles
-- This converts the view from SECURITY DEFINER to SECURITY INVOKER
-- which enforces RLS policies based on the querying user rather than view creator

-- ALTER the existing user_profiles view to use SECURITY INVOKER
ALTER VIEW public.user_profiles SET (security_invoker = true);

-- Verify the change
SELECT schemaname, viewname, viewowner, definition
FROM pg_views
WHERE viewname = 'user_profiles' AND schemaname = 'public';

-- Optional: Show current security setting
SELECT
    schemaname,
    viewname,
    case
        when viewoptions && ARRAY['security_invoker=true'] then 'SECURITY INVOKER'
        else 'SECURITY DEFINER'
    end as security_mode
FROM pg_views
WHERE viewname = 'user_profiles' AND schemaname = 'public';