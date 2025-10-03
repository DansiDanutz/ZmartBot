-- =====================================================
-- FIX SUPABASE RLS POLICIES - MINIMAL APPROACH V3
-- =====================================================
-- This approach uses the simplest possible structure to avoid any optimization issues

-- =====================================================
-- STEP 1: CLEAN SLATE
-- =====================================================
-- Drop ALL existing policies on invitations table
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

-- =====================================================
-- STEP 2: SINGLE CONSOLIDATED POLICY PER ROLE
-- =====================================================
-- Enable RLS
ALTER TABLE public.invitations ENABLE ROW LEVEL SECURITY;

-- Single policy for authenticated users (combining all operations)
CREATE POLICY "authenticated_access" ON public.invitations
    FOR ALL
    TO authenticated
    USING (
        inviter_id IN (SELECT auth.uid())
        OR
        invitee_id IN (SELECT auth.uid())
    )
    WITH CHECK (
        inviter_id IN (SELECT auth.uid())
    );

-- Single policy for service role (full access)
CREATE POLICY "service_role_access" ON public.invitations
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- =====================================================
-- STEP 3: VERIFY
-- =====================================================
SELECT
    'Total policies: ' || COUNT(*)::text as summary,
    string_agg(policyname || ' (for: ' || roles::text || ')', ', ') as policies
FROM pg_policies
WHERE tablename = 'invitations'
AND schemaname = 'public';

-- =====================================================
-- ALTERNATIVE: USE SECURITY DEFINER FUNCTIONS
-- =====================================================
-- If the above still doesn't work, try this approach with functions:

/*
-- Drop the simple policies
DROP POLICY IF EXISTS "authenticated_access" ON public.invitations;
DROP POLICY IF EXISTS "service_role_access" ON public.invitations;

-- Create security definer functions for CRUD operations
CREATE OR REPLACE FUNCTION public.can_view_invitation(invitation_row public.invitations)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN (
        invitation_row.inviter_id = auth.uid()
        OR invitation_row.invitee_id = auth.uid()
        OR (auth.jwt() ->> 'role') = 'service_role'
    );
END;
$$;

CREATE OR REPLACE FUNCTION public.can_create_invitation(invitation_row public.invitations)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN (
        invitation_row.inviter_id = auth.uid()
        OR (auth.jwt() ->> 'role') = 'service_role'
    );
END;
$$;

-- Apply policies using the functions
CREATE POLICY "view_invitations" ON public.invitations
    FOR SELECT
    USING (public.can_view_invitation(invitations));

CREATE POLICY "create_invitations" ON public.invitations
    FOR INSERT
    WITH CHECK (public.can_create_invitation(invitations));

CREATE POLICY "update_invitations" ON public.invitations
    FOR UPDATE
    USING (public.can_view_invitation(invitations))
    WITH CHECK (public.can_view_invitation(invitations));

CREATE POLICY "delete_invitations" ON public.invitations
    FOR DELETE
    USING (public.can_create_invitation(invitations));

-- Grant execute on functions
GRANT EXECUTE ON FUNCTION public.can_view_invitation TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.can_create_invitation TO authenticated, service_role;
*/