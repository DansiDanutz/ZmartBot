-- Fix Supabase Security Issues
-- Generated: 2025-09-27
-- Issues: Function search_path vulnerability & Leaked password protection

-- ============================================
-- ISSUE 1: Fix function search_path vulnerability
-- ============================================

-- Drop and recreate the function with proper security settings
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    -- Update the updated_at column with current UTC timestamp
    NEW.updated_at := timezone('UTC', now());
    RETURN NEW;
END;
$$;

-- Optional: Restrict execution permissions if needed
-- Uncomment these lines if you want to restrict who can execute this trigger
-- REVOKE EXECUTE ON FUNCTION public.update_updated_at_column() FROM PUBLIC;
-- GRANT EXECUTE ON FUNCTION public.update_updated_at_column() TO postgres;

-- ============================================
-- ISSUE 2: Enable Leaked Password Protection
-- ============================================

-- Note: This setting needs to be enabled in the Supabase Dashboard
-- Go to: Authentication > Providers > Email > Password Security
-- Enable: "Check passwords against HaveIBeenPwned"

-- Alternative: You can enable it via SQL if you have access to auth settings
-- This requires superuser privileges and may not work in all Supabase environments

-- If you have the necessary permissions, uncomment and run:
/*
UPDATE auth.config
SET config = jsonb_set(
    COALESCE(config, '{}'::jsonb),
    '{password_min_length}',
    '8'::jsonb
)
WHERE id = 'password_policy';

-- Enable leaked password protection
UPDATE auth.config
SET config = jsonb_set(
    COALESCE(config, '{}'::jsonb),
    '{hibp_enabled}',
    'true'::jsonb
)
WHERE id = 'password_policy';
*/

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Check if the function has been fixed
SELECT
    n.nspname as schema,
    p.proname as function_name,
    pg_get_functiondef(p.oid) as function_definition
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'
    AND p.proname = 'update_updated_at_column';

-- List all triggers using this function
SELECT
    trigger_schema,
    trigger_name,
    event_object_schema,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE action_statement LIKE '%update_updated_at_column%';

-- ============================================
-- NOTES
-- ============================================
/*
1. The function now uses SECURITY DEFINER with an empty search_path
   This prevents search_path hijacking attacks

2. All object references are now secure
   - NEW/OLD pseudo-tables don't need schema qualification
   - timezone() and now() are built-in functions

3. For leaked password protection:
   - Best enabled via Supabase Dashboard
   - Go to: Project Settings > Authentication > Password Security
   - Toggle on "Leaked password protection"

4. This will check passwords against HaveIBeenPwned.org database
   - Prevents use of compromised passwords
   - Enhances overall security posture
*/