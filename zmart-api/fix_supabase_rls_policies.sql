-- =====================================================
-- SUPABASE RLS POLICY FIX FOR MDC OPERATIONS
-- =====================================================
-- This script fixes Row Level Security policies to allow
-- proper MDC file storage and retrieval operations

-- =====================================================
-- 1. ENABLE RLS ON TABLES (if not already enabled)
-- =====================================================
ALTER TABLE mdc_documentation ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_templates ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- 2. DROP EXISTING RESTRICTIVE POLICIES
-- =====================================================
-- Drop any existing policies that might be blocking operations
DROP POLICY IF EXISTS "mdc_documentation_insert_policy" ON mdc_documentation;
DROP POLICY IF EXISTS "mdc_documentation_select_policy" ON mdc_documentation;
DROP POLICY IF EXISTS "mdc_documentation_update_policy" ON mdc_documentation;
DROP POLICY IF EXISTS "mdc_documentation_delete_policy" ON mdc_documentation;

DROP POLICY IF EXISTS "alert_reports_insert_policy" ON alert_reports;
DROP POLICY IF EXISTS "alert_reports_select_policy" ON alert_reports;
DROP POLICY IF EXISTS "alert_reports_update_policy" ON alert_reports;
DROP POLICY IF EXISTS "alert_reports_delete_policy" ON alert_reports;

DROP POLICY IF EXISTS "prompt_templates_insert_policy" ON prompt_templates;
DROP POLICY IF EXISTS "prompt_templates_select_policy" ON prompt_templates;
DROP POLICY IF EXISTS "prompt_templates_update_policy" ON prompt_templates;
DROP POLICY IF EXISTS "prompt_templates_delete_policy" ON prompt_templates;

-- =====================================================
-- 3. CREATE PERMISSIVE POLICIES FOR MDC DOCUMENTATION
-- =====================================================

-- Allow INSERT for authenticated users and service role
CREATE POLICY "mdc_documentation_insert_policy" ON mdc_documentation
    FOR INSERT 
    WITH CHECK (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated' OR
        auth.role() = 'anon' OR
        (auth.jwt() ->> 'role' = 'service_role') OR
        (auth.jwt() ->> 'role' = 'authenticated')
    );

-- Allow SELECT for all users (read access)
CREATE POLICY "mdc_documentation_select_policy" ON mdc_documentation
    FOR SELECT 
    USING (true);

-- Allow UPDATE for authenticated users and service role
CREATE POLICY "mdc_documentation_update_policy" ON mdc_documentation
    FOR UPDATE 
    USING (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated' OR
        (auth.jwt() ->> 'role' = 'service_role') OR
        (auth.jwt() ->> 'role' = 'authenticated')
    )
    WITH CHECK (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated' OR
        (auth.jwt() ->> 'role' = 'service_role') OR
        (auth.jwt() ->> 'role' = 'authenticated')
    );

-- Allow DELETE for service role only (for cleanup)
CREATE POLICY "mdc_documentation_delete_policy" ON mdc_documentation
    FOR DELETE 
    USING (
        auth.role() = 'service_role' OR
        (auth.jwt() ->> 'role' = 'service_role')
    );

-- =====================================================
-- 4. CREATE PERMISSIVE POLICIES FOR ALERT REPORTS
-- =====================================================

-- Allow INSERT for authenticated users and service role
CREATE POLICY "alert_reports_insert_policy" ON alert_reports
    FOR INSERT 
    WITH CHECK (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated' OR
        auth.role() = 'anon' OR
        (auth.jwt() ->> 'role' = 'service_role') OR
        (auth.jwt() ->> 'role' = 'authenticated')
    );

-- Allow SELECT for all users (read access)
CREATE POLICY "alert_reports_select_policy" ON alert_reports
    FOR SELECT 
    USING (true);

-- Allow UPDATE for authenticated users and service role
CREATE POLICY "alert_reports_update_policy" ON alert_reports
    FOR UPDATE 
    USING (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated' OR
        (auth.jwt() ->> 'role' = 'service_role') OR
        (auth.jwt() ->> 'role' = 'authenticated')
    )
    WITH CHECK (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated' OR
        (auth.jwt() ->> 'role' = 'service_role') OR
        (auth.jwt() ->> 'role' = 'authenticated')
    );

-- Allow DELETE for service role only (for cleanup)
CREATE POLICY "alert_reports_delete_policy" ON alert_reports
    FOR DELETE 
    USING (
        auth.role() = 'service_role' OR
        (auth.jwt() ->> 'role' = 'service_role')
    );

-- =====================================================
-- 5. CREATE PERMISSIVE POLICIES FOR PROMPT TEMPLATES
-- =====================================================

-- Allow INSERT for authenticated users and service role
CREATE POLICY "prompt_templates_insert_policy" ON prompt_templates
    FOR INSERT 
    WITH CHECK (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated' OR
        auth.role() = 'anon' OR
        (auth.jwt() ->> 'role' = 'service_role') OR
        (auth.jwt() ->> 'role' = 'authenticated')
    );

-- Allow SELECT for all users (read access)
CREATE POLICY "prompt_templates_select_policy" ON prompt_templates
    FOR SELECT 
    USING (true);

-- Allow UPDATE for authenticated users and service role
CREATE POLICY "prompt_templates_update_policy" ON prompt_templates
    FOR UPDATE 
    USING (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated' OR
        (auth.jwt() ->> 'role' = 'service_role') OR
        (auth.jwt() ->> 'role' = 'authenticated')
    )
    WITH CHECK (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated' OR
        (auth.jwt() ->> 'role' = 'service_role') OR
        (auth.jwt() ->> 'role' = 'authenticated')
    );

-- Allow DELETE for service role only (for cleanup)
CREATE POLICY "prompt_templates_delete_policy" ON prompt_templates
    FOR DELETE 
    USING (
        auth.role() = 'service_role' OR
        (auth.jwt() ->> 'role' = 'service_role')
    );

-- =====================================================
-- 6. CREATE HELPER FUNCTIONS FOR MDC OPERATIONS
-- =====================================================

-- Function to safely insert MDC documentation
CREATE OR REPLACE FUNCTION insert_mdc_documentation(
    p_symbol TEXT,
    p_document_type TEXT,
    p_mdc_content TEXT,
    p_md_content TEXT DEFAULT NULL,
    p_version TEXT DEFAULT '1.0.0',
    p_owner TEXT DEFAULT 'zmartbot',
    p_status TEXT DEFAULT 'active',
    p_metadata JSONB DEFAULT NULL,
    p_tags TEXT[] DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    new_id UUID;
BEGIN
    INSERT INTO mdc_documentation (
        symbol, document_type, mdc_content, md_content, 
        version, owner, status, metadata, tags
    ) VALUES (
        p_symbol, p_document_type, p_mdc_content, p_md_content,
        p_version, p_owner, p_status, p_metadata, p_tags
    ) RETURNING id INTO new_id;
    
    RETURN new_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to safely insert alert report with MDC content
CREATE OR REPLACE FUNCTION insert_alert_report_with_mdc(
    p_symbol TEXT,
    p_alert_summary TEXT,
    p_technical_analysis TEXT DEFAULT NULL,
    p_risk_assessment TEXT DEFAULT NULL,
    p_market_context TEXT DEFAULT NULL,
    p_action_plan TEXT DEFAULT NULL,
    p_confidence_rating TEXT DEFAULT 'Medium',
    p_mdc_content TEXT DEFAULT NULL,
    p_md_content TEXT DEFAULT NULL,
    p_data_sources JSONB DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    new_id UUID;
BEGIN
    INSERT INTO alert_reports (
        symbol, alert_summary, technical_analysis, risk_assessment,
        market_context, action_plan, confidence_rating, mdc_content,
        md_content, data_sources
    ) VALUES (
        p_symbol, p_alert_summary, p_technical_analysis, p_risk_assessment,
        p_market_context, p_action_plan, p_confidence_rating, p_mdc_content,
        p_md_content, p_data_sources
    ) RETURNING id INTO new_id;
    
    RETURN new_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 7. GRANT NECESSARY PERMISSIONS
-- =====================================================

-- Grant execute permissions on helper functions
GRANT EXECUTE ON FUNCTION insert_mdc_documentation TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION insert_alert_report_with_mdc TO authenticated, anon, service_role;

-- =====================================================
-- 8. VERIFICATION QUERIES
-- =====================================================

-- Test the policies by checking if we can see the tables
SELECT 'RLS Policies Applied Successfully' as status;

-- Show current policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename IN ('mdc_documentation', 'alert_reports', 'prompt_templates')
ORDER BY tablename, policyname;
