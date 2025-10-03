-- =====================================================
-- DEBUG AND FIX INVITATIONS RLS POLICIES
-- =====================================================

-- STEP 1: CHECK CURRENT POLICIES
-- =====================================================
SELECT
    policyname,
    cmd,
    roles::text as roles,
    qual as using_clause,
    with_check as check_clause
FROM pg_policies
WHERE tablename = 'invitations'
AND schemaname = 'public'
ORDER BY policyname;

-- STEP 2: VIEW ACTUAL POLICY DEFINITIONS
-- =====================================================
SELECT
    polname as policy_name,
    CASE polcmd
        WHEN 'r' THEN 'SELECT'
        WHEN 'a' THEN 'INSERT'
        WHEN 'w' THEN 'UPDATE'
        WHEN 'd' THEN 'DELETE'
        WHEN '*' THEN 'ALL'
    END as operation,
    pg_get_expr(polqual::pg_node_tree, polrelid) as using_expression,
    pg_get_expr(polwithcheck::pg_node_tree, polrelid) as with_check_expression
FROM pg_policy
WHERE polrelid = 'public.invitations'::regclass
ORDER BY polname;

-- STEP 3: NUCLEAR OPTION - DROP ALL AND RECREATE
-- =====================================================
-- First, disable RLS temporarily
ALTER TABLE public.invitations DISABLE ROW LEVEL SECURITY;

-- Drop ALL policies (comprehensive)
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

-- Re-enable RLS
ALTER TABLE public.invitations ENABLE ROW LEVEL SECURITY;

-- STEP 4: CREATE NEW OPTIMIZED POLICIES WITH DIFFERENT APPROACH
-- =====================================================

-- Method 1: Using subselects with EXISTS (often works better)
CREATE POLICY "inv_select" ON public.invitations
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1
            WHERE inviter_id = auth.uid()
               OR invitee_id = auth.uid()
        )
    );

CREATE POLICY "inv_insert" ON public.invitations
    FOR INSERT
    TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1
            WHERE inviter_id = auth.uid()
        )
    );

CREATE POLICY "inv_update" ON public.invitations
    FOR UPDATE
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
               OR invitee_id = auth.uid()
        )
    );

CREATE POLICY "inv_delete" ON public.invitations
    FOR DELETE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1
            WHERE inviter_id = auth.uid()
        )
    );

-- Service role gets full access (separate policy)
CREATE POLICY "inv_service" ON public.invitations
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- STEP 5: VERIFY THE FIX
-- =====================================================
SELECT
    COUNT(*) as total_policies,
    string_agg(policyname || ' (' || cmd || ')', ', ' ORDER BY policyname) as policy_list
FROM pg_policies
WHERE tablename = 'invitations'
AND schemaname = 'public';

-- Check if auth functions are properly handled
SELECT
    policyname,
    CASE
        WHEN qual LIKE '%auth.uid()%'
             AND qual NOT LIKE '%EXISTS%'
             AND qual NOT LIKE '%(SELECT%'
        THEN '❌ PROBLEM: Direct auth.uid() call'
        ELSE '✅ OK'
    END as status
FROM pg_policies
WHERE tablename = 'invitations'
AND schemaname = 'public'
ORDER BY policyname;

-- STEP 6: ALTERNATIVE IF STILL HAVING ISSUES
-- =====================================================
-- If the above still doesn't work, try this ultra-simple approach:

/*
-- Drop all policies again
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

-- Single combined policy with role check
CREATE POLICY "invitations_combined" ON public.invitations
    FOR ALL
    USING (
        CASE
            WHEN current_setting('request.jwt.claim.role', true) = 'service_role' THEN true
            WHEN inviter_id = uuid(current_setting('request.jwt.claim.sub', true)) THEN true
            WHEN invitee_id = uuid(current_setting('request.jwt.claim.sub', true)) THEN true
            ELSE false
        END
    )
    WITH CHECK (
        CASE
            WHEN current_setting('request.jwt.claim.role', true) = 'service_role' THEN true
            WHEN inviter_id = uuid(current_setting('request.jwt.claim.sub', true)) THEN true
            ELSE false
        END
    );
*/

-- STEP 7: FINAL VERIFICATION
-- =====================================================
-- Run this to see the final state
SELECT
    'Policies after fix:' as status,
    COUNT(*) as count
FROM pg_policies
WHERE tablename = 'invitations'
AND schemaname = 'public';