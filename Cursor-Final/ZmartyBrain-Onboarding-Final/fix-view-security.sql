-- Fix SECURITY DEFINER view error

-- Drop the problematic view
DROP VIEW IF EXISTS public.user_profiles CASCADE;

-- Recreate view with SECURITY INVOKER (the default, safe option)
CREATE VIEW public.user_profiles AS
SELECT
    p.id,
    p.full_name,
    p.updated_at
FROM public.profiles p
WHERE p.id = auth.uid();

-- Set proper permissions
GRANT SELECT ON public.user_profiles TO authenticated;
REVOKE ALL ON public.user_profiles FROM anon;