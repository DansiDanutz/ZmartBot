-- Clean up any existing objects (handle both table and view)
DROP TABLE IF EXISTS public.user_profiles CASCADE;
DROP VIEW IF EXISTS public.user_profiles CASCADE;
DROP VIEW IF EXISTS public.user_details CASCADE;
DROP FUNCTION IF EXISTS public.get_user_profile(uuid) CASCADE;

-- Create safe view
CREATE VIEW public.user_profiles AS
SELECT
    p.id,
    p.full_name,
    p.updated_at
FROM public.profiles p
WHERE p.id = auth.uid();

-- Set permissions
GRANT SELECT ON public.user_profiles TO authenticated;
REVOKE ALL ON public.user_profiles FROM anon;

-- Enable RLS on profiles table
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Create secure function
CREATE FUNCTION public.get_user_profile(user_id uuid)
RETURNS TABLE (
    id uuid,
    full_name text
)
LANGUAGE plpgsql
SECURITY INVOKER
AS $$
BEGIN
    IF user_id = auth.uid() OR auth.jwt()->>'role' = 'service_role' THEN
        RETURN QUERY
        SELECT p.id, p.full_name
        FROM public.profiles p
        WHERE p.id = user_id;
    ELSE
        RETURN;
    END IF;
END;
$$;

-- Grant permissions
GRANT EXECUTE ON FUNCTION public.get_user_profile(uuid) TO authenticated;
REVOKE EXECUTE ON FUNCTION public.get_user_profile(uuid) FROM anon;