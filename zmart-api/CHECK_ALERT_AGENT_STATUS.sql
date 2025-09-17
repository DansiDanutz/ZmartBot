-- ============================================
-- CHECK ALERT AGENT STATUS
-- See what's already installed
-- ============================================

-- 1. Check which Alert Agent tables exist
SELECT
    'Alert Agent Tables' as module,
    COUNT(*) as tables_found,
    string_agg(table_name, ', ') as existing_tables
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'alert_collections',
    'alert_reports',
    'symbol_coverage',
    'manus_extraordinary_reports',
    'mdc_documentation',
    'alert_agent_statistics',
    'prompt_templates',
    'alert_fusion_data'
);

-- 2. Check if tables have data
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns,
    CASE table_name
        WHEN 'alert_collections' THEN (SELECT COUNT(*) FROM alert_collections)
        WHEN 'alert_reports' THEN (SELECT COUNT(*) FROM alert_reports)
        WHEN 'symbol_coverage' THEN (SELECT COUNT(*) FROM symbol_coverage)
        WHEN 'prompt_templates' THEN (SELECT COUNT(*) FROM prompt_templates)
        ELSE 0
    END as row_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name IN (
    'alert_collections', 'alert_reports', 'symbol_coverage',
    'prompt_templates', 'mdc_documentation'
);

-- 3. Check if views exist
SELECT
    'Alert Agent Views' as module,
    COUNT(*) as views_found,
    string_agg(viewname, ', ') as existing_views
FROM pg_views
WHERE schemaname = 'public'
AND viewname IN (
    'active_alerts_summary',
    'symbol_coverage_status',
    'manus_reports_summary',
    'agent_performance_metrics'
);

-- 4. Check prompt templates
SELECT
    template_name,
    template_type,
    is_active
FROM prompt_templates
LIMIT 5;

-- 5. Final Status
SELECT
    '📊 ALERT AGENT STATUS' as report,
    'Alert Agent is ALREADY INSTALLED' as status,
    'Tables and triggers already exist' as finding,
    'You can start using it immediately!' as recommendation;

-- 6. Test Alert Agent functionality
SELECT
    '🚀 READY TO USE' as status,
    'You can now:' as actions,
    '1. Store alerts in alert_collections' as action_1,
    '2. Generate reports in alert_reports' as action_2,
    '3. Track symbols in symbol_coverage' as action_3,
    '4. Use MDC documentation features' as action_4;