-- =====================================================
-- FINAL FIX FOR INVITATIONS RLS POLICIES
-- =====================================================
-- This solution properly wraps auth.uid() with SELECT even inside EXISTS

-- STEP 1: DROP ALL EXISTING POLICIES
-- =====================================================
DO $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN
        SELECT polname
        FROM pg_policy
        WHERE polrelid = 'public.invitations'::regclass
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.invitations', rec.polname);
        RAISE NOTICE 'Dropped policy: %', rec.polname;
    END LOOP;
END $$;

-- STEP 2: CREATE PROPERLY OPTIMIZED POLICIES
-- =====================================================
-- The key is that auth.uid() must be wrapped with SELECT even inside EXISTS clauses

-- SELECT POLICY for authenticated users
CREATE POLICY "inv_select" ON public.invitations
    FOR SELECT
    TO authenticated
    USING (
        inviter_id = (SELECT auth.uid())
        OR
        invitee_id = (SELECT auth.uid())
    );

-- INSERT POLICY for authenticated users
CREATE POLICY "inv_insert" ON public.invitations
    FOR INSERT
    TO authenticated
    WITH CHECK (
        inviter_id = (SELECT auth.uid())
    );

-- UPDATE POLICY for authenticated users
CREATE POLICY "inv_update" ON public.invitations
    FOR UPDATE
    TO authenticated
    USING (
        inviter_id = (SELECT auth.uid())
        OR
        invitee_id = (SELECT auth.uid())
    )
    WITH CHECK (
        inviter_id = (SELECT auth.uid())
        OR
        invitee_id = (SELECT auth.uid())
    );

-- DELETE POLICY for authenticated users
CREATE POLICY "inv_delete" ON public.invitations
    FOR DELETE
    TO authenticated
    USING (
        inviter_id = (SELECT auth.uid())
    );

-- Service role bypass policy
CREATE POLICY "inv_service" ON public.invitations
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- STEP 3: VERIFY THE POLICIES
-- =====================================================
SELECT
    policyname,
    cmd,
    roles::text,
    qual as using_clause
FROM pg_policies
WHERE tablename = 'invitations'
AND schemaname = 'public'
ORDER BY policyname;

-- STEP 4: IF THE ABOVE STILL DOESN'T WORK - ALTERNATIVE SOLUTION
-- =====================================================
-- This uses a completely different approach without auth functions

/*
-- Drop all policies first
DO $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN
        SELECT polname
        FROM pg_policy
        WHERE polrelid = 'public.invitations'::regclass
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.invitations', rec.polname);
    END LOOP;
END $$;

-- Create a SECURITY DEFINER function to get current user ID
CREATE OR REPLACE FUNCTION public.get_auth_user_id()
RETURNS uuid
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT NULLIF(current_setting('request.jwt.claim.sub', true), '')::uuid
$$;

-- Create policies using the function
CREATE POLICY "inv_all_authenticated" ON public.invitations
    FOR ALL
    TO authenticated
    USING (
        inviter_id = get_auth_user_id()
        OR
        invitee_id = get_auth_user_id()
    )
    WITH CHECK (
        inviter_id = get_auth_user_id()
    );

-- Service role bypass
CREATE POLICY "inv_all_service" ON public.invitations
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Grant execute permission
GRANT EXECUTE ON FUNCTION public.get_auth_user_id() TO authenticated, service_role;
*/

-- STEP 5: NUCLEAR OPTION - USE CURRENT_SETTING DIRECTLY
-- =====================================================
-- If nothing else works, this bypasses auth functions completely

/*
-- Drop all policies
DO $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN
        SELECT polname
        FROM pg_policy
        WHERE polrelid = 'public.invitations'::regclass
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.invitations', rec.polname);
    END LOOP;
END $$;

-- Single policy using current_setting
CREATE POLICY "invitations_access" ON public.invitations
    FOR ALL
    USING (
        CASE
            WHEN current_setting('request.jwt.claim.role', true) = 'service_role' THEN true
            ELSE (
                inviter_id = NULLIF(current_setting('request.jwt.claim.sub', true), '')::uuid
                OR
                invitee_id = NULLIF(current_setting('request.jwt.claim.sub', true), '')::uuid
            )
        END
    )
    WITH CHECK (
        CASE
            WHEN current_setting('request.jwt.claim.role', true) = 'service_role' THEN true
            ELSE inviter_id = NULLIF(current_setting('request.jwt.claim.sub', true), '')::uuid
        END
    );
*/