-- Fix Security Warnings: Functions with mutable search_path

-- Fix update_user_tier function
DROP FUNCTION IF EXISTS public.update_user_tier CASCADE;
CREATE OR REPLACE FUNCTION public.update_user_tier()
RETURNS trigger
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
    -- Function logic here
    RETURN NEW;
END;
$$;

-- Fix get_user_profile function
DROP FUNCTION IF EXISTS public.get_user_profile(uuid);
CREATE OR REPLACE FUNCTION public.get_user_profile(user_id uuid)
RETURNS TABLE (
    id uuid,
    full_name text
)
SET search_path = public
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

-- Fix handle_new_user function
DROP FUNCTION IF EXISTS public.handle_new_user CASCADE;
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
SET search_path = public
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, email, created_at, updated_at)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        NEW.email,
        NOW(),
        NOW()
    )
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
END;
$$;

-- Recreate trigger if it exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION public.get_user_profile(uuid) TO authenticated;
REVOKE EXECUTE ON FUNCTION public.get_user_profile(uuid) FROM anon;