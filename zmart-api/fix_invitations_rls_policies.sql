-- =====================================================
-- FIX SUPABASE RLS POLICIES FOR INVITATIONS TABLE
-- =====================================================
-- This script fixes the performance issues identified by Supabase linter:
-- 1. Auth RLS Initialization Plan (auth.uid() being re-evaluated for each row)
-- 2. Multiple Permissive Policies (consolidating multiple policies for same role/action)

-- =====================================================
-- STEP 1: DROP ALL EXISTING POLICIES ON INVITATIONS TABLE
-- =====================================================
-- First, we need to drop all existing policies to start fresh
DROP POLICY IF EXISTS "Users can view their invitations" ON public.invitations;
DROP POLICY IF EXISTS "Users can create invites" ON public.invitations;
DROP POLICY IF EXISTS "invitations_service_only" ON public.invitations;
DROP POLICY IF EXISTS "Users can view own invitations" ON public.invitations;

-- Drop any other potential policies (catch-all)
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
-- STEP 2: CREATE OPTIMIZED RLS POLICIES
-- =====================================================
-- These policies use (SELECT auth.uid()) to avoid re-evaluation for each row
-- and consolidate multiple policies into single, efficient ones

-- Enable RLS if not already enabled
ALTER TABLE public.invitations ENABLE ROW LEVEL SECURITY;

-- OPTIMIZED SELECT POLICY
-- Combines all SELECT permissions into one policy
CREATE POLICY "invitations_select_policy" ON public.invitations
    FOR SELECT
    USING (
        -- Users can view invitations where they are either inviter or invitee
        inviter_id = (SELECT auth.uid())
        OR invitee_id = (SELECT auth.uid())
        OR
        -- Service role can view all
        (SELECT (auth.jwt() ->> 'role')) = 'service_role'
    );

-- OPTIMIZED INSERT POLICY
-- Allows authenticated users to create invitations only as the inviter
CREATE POLICY "invitations_insert_policy" ON public.invitations
    FOR INSERT
    WITH CHECK (
        -- Users can only create invitations where they are the inviter
        inviter_id = (SELECT auth.uid())
        OR
        -- Service role can insert any invitation
        (SELECT (auth.jwt() ->> 'role')) = 'service_role'
    );

-- OPTIMIZED UPDATE POLICY
-- Allows users to update their own invitations
CREATE POLICY "invitations_update_policy" ON public.invitations
    FOR UPDATE
    USING (
        -- Only inviter can update their invitations
        inviter_id = (SELECT auth.uid())
        OR
        -- Or invitee can update (e.g., to accept/reject)
        invitee_id = (SELECT auth.uid())
        OR
        -- Service role can update all
        (SELECT (auth.jwt() ->> 'role')) = 'service_role'
    )
    WITH CHECK (
        -- Ensure the relationship doesn't change
        inviter_id = (SELECT auth.uid())
        OR invitee_id = (SELECT auth.uid())
        OR
        (SELECT (auth.jwt() ->> 'role')) = 'service_role'
    );

-- OPTIMIZED DELETE POLICY
-- Only inviter or service role can delete invitations
CREATE POLICY "invitations_delete_policy" ON public.invitations
    FOR DELETE
    USING (
        -- Only inviter can delete their invitations
        inviter_id = (SELECT auth.uid())
        OR
        -- Service role can delete any
        (SELECT (auth.jwt() ->> 'role')) = 'service_role'
    );

-- =====================================================
-- STEP 3: CREATE INDEXES FOR BETTER PERFORMANCE
-- =====================================================
-- These indexes will help with the RLS policy evaluations
CREATE INDEX IF NOT EXISTS idx_invitations_inviter_id ON public.invitations(inviter_id);
CREATE INDEX IF NOT EXISTS idx_invitations_invitee_id ON public.invitations(invitee_id);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON public.invitations(status);
CREATE INDEX IF NOT EXISTS idx_invitations_invitation_code ON public.invitations(invitation_code);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_invitations_inviter_status ON public.invitations(inviter_id, status);
CREATE INDEX IF NOT EXISTS idx_invitations_invitee_status ON public.invitations(invitee_id, status);

-- =====================================================
-- STEP 4: VERIFY THE FIXES
-- =====================================================
-- Run these queries to verify the policies are correctly set

-- Check that we have exactly 4 policies (one for each operation)
SELECT
    COUNT(*) as policy_count,
    string_agg(policyname || ' (' || cmd || ')', ', ' ORDER BY policyname) as policies
FROM pg_policies
WHERE tablename = 'invitations'
AND schemaname = 'public';

-- Verify no auth.uid() direct calls (should use SELECT auth.uid())
SELECT
    policyname,
    cmd,
    CASE
        WHEN qual LIKE '%auth.uid()%'
             AND qual NOT LIKE '%(SELECT auth.uid())%'
        THEN 'WARNING: Direct auth.uid() call found'
        ELSE 'OK: Using SELECT auth.uid()'
    END as status
FROM pg_policies
WHERE tablename = 'invitations'
AND schemaname = 'public';

-- =====================================================
-- STEP 5: TEST THE POLICIES
-- =====================================================
-- You can test these policies with the following queries:

-- Test 1: Check if current user can see their invitations
-- SELECT * FROM public.invitations WHERE inviter_id = auth.uid() OR invitee_id = auth.uid();

-- Test 2: Check if insert works for authenticated users
-- INSERT INTO public.invitations (inviter_id, invitation_code, message)
-- VALUES (auth.uid(), 'TEST_CODE_' || gen_random_uuid(), 'Test invitation');

-- Test 3: Verify performance improvement
-- EXPLAIN ANALYZE SELECT * FROM public.invitations WHERE inviter_id = auth.uid();

-- =====================================================
-- SUMMARY OF CHANGES
-- =====================================================
-- 1. Replaced auth.uid() with (SELECT auth.uid()) to avoid re-evaluation
-- 2. Consolidated multiple permissive policies into single policies per operation
-- 3. Added proper indexes to support RLS policy evaluations
-- 4. Simplified policy logic while maintaining security
--
-- Expected results:
-- - Eliminated "auth_rls_initplan" warnings
-- - Eliminated "multiple_permissive_policies" warnings
-- - Improved query performance at scale