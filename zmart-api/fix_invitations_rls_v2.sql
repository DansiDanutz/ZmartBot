-- =====================================================
-- FIX SUPABASE RLS POLICIES FOR INVITATIONS TABLE V2
-- =====================================================
-- Alternative approach using different optimization techniques

-- =====================================================
-- STEP 1: DROP ALL EXISTING POLICIES
-- =====================================================
DROP POLICY IF EXISTS "invitations_select_policy" ON public.invitations;
DROP POLICY IF EXISTS "invitations_insert_policy" ON public.invitations;
DROP POLICY IF EXISTS "invitations_update_policy" ON public.invitations;
DROP POLICY IF EXISTS "invitations_delete_policy" ON public.invitations;
DROP POLICY IF EXISTS "Users can view their invitations" ON public.invitations;
DROP POLICY IF EXISTS "Users can create invites" ON public.invitations;
DROP POLICY IF EXISTS "invitations_service_only" ON public.invitations;
DROP POLICY IF EXISTS "Users can view own invitations" ON public.invitations;

-- =====================================================
-- STEP 2: CREATE HELPER FUNCTION FOR AUTH CHECKS
-- =====================================================
-- Create a stable function that caches the auth.uid() result
CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS uuid
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT auth.uid()
$$;

-- Create a stable function for checking service role
CREATE OR REPLACE FUNCTION is_service_role()
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT coalesce((auth.jwt() ->> 'role')::text = 'service_role', false)
$$;

-- =====================================================
-- STEP 3: CREATE OPTIMIZED POLICIES USING FUNCTIONS
-- =====================================================

-- Enable RLS
ALTER TABLE public.invitations ENABLE ROW LEVEL SECURITY;

-- SELECT POLICY - Users can view their own invitations
CREATE POLICY "invitations_select_authenticated" ON public.invitations
    FOR SELECT
    TO authenticated
    USING (
        inviter_id = get_current_user_id()
        OR
        invitee_id = get_current_user_id()
    );

-- SELECT POLICY - Service role can view all
CREATE POLICY "invitations_select_service" ON public.invitations
    FOR SELECT
    TO service_role
    USING (true);

-- INSERT POLICY - Authenticated users can create invitations
CREATE POLICY "invitations_insert_authenticated" ON public.invitations
    FOR INSERT
    TO authenticated
    WITH CHECK (
        inviter_id = get_current_user_id()
    );

-- INSERT POLICY - Service role can insert any
CREATE POLICY "invitations_insert_service" ON public.invitations
    FOR INSERT
    TO service_role
    WITH CHECK (true);

-- UPDATE POLICY - Users can update their own invitations
CREATE POLICY "invitations_update_authenticated" ON public.invitations
    FOR UPDATE
    TO authenticated
    USING (
        inviter_id = get_current_user_id()
        OR
        invitee_id = get_current_user_id()
    )
    WITH CHECK (
        inviter_id = get_current_user_id()
        OR
        invitee_id = get_current_user_id()
    );

-- UPDATE POLICY - Service role can update all
CREATE POLICY "invitations_update_service" ON public.invitations
    FOR UPDATE
    TO service_role
    USING (true)
    WITH CHECK (true);

-- DELETE POLICY - Users can delete their own invitations
CREATE POLICY "invitations_delete_authenticated" ON public.invitations
    FOR DELETE
    TO authenticated
    USING (
        inviter_id = get_current_user_id()
    );

-- DELETE POLICY - Service role can delete any
CREATE POLICY "invitations_delete_service" ON public.invitations
    FOR DELETE
    TO service_role
    USING (true);

-- =====================================================
-- STEP 4: CREATE INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_invitations_inviter_id ON public.invitations(inviter_id);
CREATE INDEX IF NOT EXISTS idx_invitations_invitee_id ON public.invitations(invitee_id);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON public.invitations(status);
CREATE INDEX IF NOT EXISTS idx_invitations_invitation_code ON public.invitations(invitation_code);
CREATE INDEX IF NOT EXISTS idx_invitations_inviter_status ON public.invitations(inviter_id, status);
CREATE INDEX IF NOT EXISTS idx_invitations_invitee_status ON public.invitations(invitee_id, status);

-- =====================================================
-- STEP 5: ANALYZE TABLE FOR OPTIMIZER
-- =====================================================
ANALYZE public.invitations;

-- =====================================================
-- STEP 6: VERIFY THE FIXES
-- =====================================================
SELECT
    COUNT(*) as policy_count,
    string_agg(policyname || ' (' || cmd || ', ' || roles::text || ')', E'\n' ORDER BY policyname) as policies
FROM pg_policies
WHERE tablename = 'invitations'
AND schemaname = 'public';

-- Check for any remaining auth function issues
SELECT
    policyname,
    cmd,
    roles,
    CASE
        WHEN qual LIKE '%auth.uid()%' AND qual NOT LIKE '%get_current_user_id%'
        THEN 'WARNING: Direct auth.uid() found'
        WHEN qual LIKE '%auth.jwt()%' AND qual NOT LIKE '%is_service_role%'
        THEN 'WARNING: Direct auth.jwt() found'
        ELSE 'OK'
    END as status
FROM pg_policies
WHERE tablename = 'invitations'
AND schemaname = 'public';

-- =====================================================
-- ALTERNATIVE APPROACH IF ABOVE DOESN'T WORK
-- =====================================================
-- If the above approach still shows warnings, uncomment and run this section:

/*
-- Drop all policies again
DO $$
DECLARE
    policy_record RECORD;
BEGIN
    FOR policy_record IN
        SELECT policyname
        FROM pg_policies
        WHERE tablename = 'invitations'
        AND schemaname = 'public'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.invitations', policy_record.policyname);
    END LOOP;
END $$;

-- Create a single combined policy for authenticated users
CREATE POLICY "invitations_authenticated_all" ON public.invitations
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1
            WHERE inviter_id = auth.uid()
               OR invitee_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1
            WHERE inviter_id = auth.uid()
        )
    );

-- Service role bypass
CREATE POLICY "invitations_service_bypass" ON public.invitations
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
*/

-- =====================================================
-- CLEANUP TEMPORARY OBJECTS (OPTIONAL)
-- =====================================================
-- If you want to remove the helper functions later:
-- DROP FUNCTION IF EXISTS get_current_user_id();
-- DROP FUNCTION IF EXISTS is_service_role();