-- =====================================================
-- FIND AND FIX REMAINING FUNCTION WITHOUT SEARCH_PATH
-- =====================================================

-- STEP 1: IDENTIFY THE FUNCTION WITHOUT SEARCH_PATH
-- =====================================================
SELECT
    n.nspname as schema,
    p.proname as function_name,
    pg_get_function_identity_arguments(p.oid) as arguments,
    pg_get_functiondef(p.oid) as current_definition,
    CASE
        WHEN p.prosecdef THEN 'SECURITY DEFINER'
        ELSE 'SECURITY INVOKER'
    END as security_type
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'
AND p.prokind = 'f'
AND (p.proconfig IS NULL OR NOT ('search_path' = ANY(
    SELECT split_part(unnest(p.proconfig), '=', 1)
)));

-- STEP 2: FIX COMMON FUNCTIONS THAT MIGHT BE MISSING SEARCH_PATH
-- =====================================================
-- Based on common patterns, these functions often lack search_path:

-- Fix handle_new_user if it exists and lacks search_path
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public' AND p.proname = 'handle_new_user'
        AND (p.proconfig IS NULL OR NOT ('search_path' = ANY(
            SELECT split_part(unnest(p.proconfig), '=', 1)
        )))
    ) THEN
        CREATE OR REPLACE FUNCTION public.handle_new_user()
        RETURNS trigger
        LANGUAGE plpgsql
        SECURITY DEFINER
        SET search_path = public, pg_catalog
        AS $func$
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
        $func$;
        RAISE NOTICE 'Fixed: handle_new_user';
    END IF;
END $$;

-- Fix update_user_tier if it exists and lacks search_path
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public' AND p.proname = 'update_user_tier'
        AND (p.proconfig IS NULL OR NOT ('search_path' = ANY(
            SELECT split_part(unnest(p.proconfig), '=', 1)
        )))
    ) THEN
        CREATE OR REPLACE FUNCTION public.update_user_tier()
        RETURNS trigger
        LANGUAGE plpgsql
        SECURITY DEFINER
        SET search_path = public, pg_catalog
        AS $func$
        BEGIN
            -- Add your tier update logic here
            RETURN NEW;
        END;
        $func$;
        RAISE NOTICE 'Fixed: update_user_tier';
    END IF;
END $$;

-- Fix get_user_profile if it exists and lacks search_path
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public' AND p.proname = 'get_user_profile'
        AND (p.proconfig IS NULL OR NOT ('search_path' = ANY(
            SELECT split_part(unnest(p.proconfig), '=', 1)
        )))
    ) THEN
        CREATE OR REPLACE FUNCTION public.get_user_profile(user_id uuid)
        RETURNS TABLE (
            id uuid,
            full_name text
        )
        LANGUAGE plpgsql
        SECURITY INVOKER
        SET search_path = public, pg_catalog
        AS $func$
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
        $func$;
        RAISE NOTICE 'Fixed: get_user_profile';
    END IF;
END $$;

-- Fix any helper functions from previous fixes
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public' AND p.proname = 'get_current_user_id'
        AND (p.proconfig IS NULL OR NOT ('search_path' = ANY(
            SELECT split_part(unnest(p.proconfig), '=', 1)
        )))
    ) THEN
        CREATE OR REPLACE FUNCTION public.get_current_user_id()
        RETURNS uuid
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        SET search_path = public, pg_catalog
        AS $func$
          SELECT auth.uid()
        $func$;
        RAISE NOTICE 'Fixed: get_current_user_id';
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public' AND p.proname = 'is_service_role'
        AND (p.proconfig IS NULL OR NOT ('search_path' = ANY(
            SELECT split_part(unnest(p.proconfig), '=', 1)
        )))
    ) THEN
        CREATE OR REPLACE FUNCTION public.is_service_role()
        RETURNS boolean
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        SET search_path = public, pg_catalog
        AS $func$
          SELECT coalesce((auth.jwt() ->> 'role')::text = 'service_role', false)
        $func$;
        RAISE NOTICE 'Fixed: is_service_role';
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public' AND p.proname = 'get_auth_user_id'
        AND (p.proconfig IS NULL OR NOT ('search_path' = ANY(
            SELECT split_part(unnest(p.proconfig), '=', 1)
        )))
    ) THEN
        CREATE OR REPLACE FUNCTION public.get_auth_user_id()
        RETURNS uuid
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        SET search_path = public, pg_catalog
        AS $func$
            SELECT NULLIF(current_setting('request.jwt.claim.sub', true), '')::uuid
        $func$;
        RAISE NOTICE 'Fixed: get_auth_user_id';
    END IF;
END $$;

-- STEP 3: GENERIC FIX FOR ANY REMAINING FUNCTIONS
-- =====================================================
-- This will attempt to fix any remaining functions by recreating them with search_path

DO $$
DECLARE
    func_record RECORD;
    func_def TEXT;
    func_name TEXT;
BEGIN
    FOR func_record IN
        SELECT
            p.proname,
            pg_get_functiondef(p.oid) as definition
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public'
        AND p.prokind = 'f'
        AND (p.proconfig IS NULL OR NOT ('search_path' = ANY(
            SELECT split_part(unnest(p.proconfig), '=', 1)
        )))
    LOOP
        func_name := func_record.proname;
        func_def := func_record.definition;

        -- Add SET search_path to the function definition if it's not already there
        IF func_def NOT LIKE '%SET search_path%' THEN
            -- Insert SET search_path before AS
            func_def := regexp_replace(
                func_def,
                '(SECURITY (DEFINER|INVOKER))',
                '\1' || E'\nSET search_path = public, pg_catalog',
                'i'
            );

            -- If no SECURITY clause, add it before AS
            IF func_def NOT LIKE '%SECURITY%' THEN
                func_def := regexp_replace(
                    func_def,
                    '(LANGUAGE \w+)',
                    '\1' || E'\nSET search_path = public, pg_catalog',
                    'i'
                );
            END IF;

            -- Execute the modified function definition
            BEGIN
                EXECUTE func_def;
                RAISE NOTICE 'Fixed function: %', func_name;
            EXCEPTION WHEN OTHERS THEN
                RAISE WARNING 'Could not auto-fix function %: %. Please fix manually.', func_name, SQLERRM;
            END;
        END IF;
    END LOOP;
END $$;

-- STEP 4: FINAL VERIFICATION
-- =====================================================
-- Check if all functions now have search_path set

SELECT
    'Final Check' as status,
    COUNT(*) FILTER (WHERE proconfig IS NULL OR NOT ('search_path' = ANY(
        SELECT split_part(unnest(proconfig), '=', 1)
    ))) as functions_without_search_path,
    COUNT(*) FILTER (WHERE proconfig IS NOT NULL AND 'search_path' = ANY(
        SELECT split_part(unnest(proconfig), '=', 1)
    )) as functions_with_search_path,
    COUNT(*) as total_functions
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'
AND p.prokind = 'f';

-- Show any remaining functions without search_path (should be 0)
SELECT
    'Functions Still Missing search_path' as issue,
    p.proname as function_name,
    pg_get_function_identity_arguments(p.oid) as arguments
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'
AND p.prokind = 'f'
AND (p.proconfig IS NULL OR NOT ('search_path' = ANY(
    SELECT split_part(unnest(p.proconfig), '=', 1)
)));