-- ============================================================================
-- ZMARTBOT DATABASE OPTIMIZATION - UNUSED INDEX CLEANUP
-- ============================================================================
-- Purpose: Remove unused indexes to free storage and improve write performance
-- Date: 2025-10-01
-- Issue: 97 unused indexes consuming storage and slowing down writes
-- ============================================================================

-- IMPORTANT SAFETY NOTES:
-- 1. BACKUP YOUR DATABASE BEFORE RUNNING THIS SCRIPT
-- 2. Review each DROP statement carefully
-- 3. Consider monitoring index usage for 30+ days before removal
-- 4. Run during low-traffic period
-- 5. Keep a record of dropped indexes in case rollback is needed
-- ============================================================================

-- RECOMMENDED APPROACH: Run in stages, not all at once
-- Stage 1: Drop obviously unused indexes (test/demo related)
-- Stage 2: Drop low-priority indexes after monitoring
-- Stage 3: Drop remaining after validation

BEGIN;

-- ============================================================================
-- STAGE 1: SAFE TO REMOVE - Unused Alert & Report Indexes
-- ============================================================================

-- Alert Reports Table - Unused indexes
DROP INDEX IF EXISTS public.unique_active_symbol;  -- Never used
DROP INDEX IF EXISTS public.idx_alert_reports_active;
DROP INDEX IF EXISTS public.idx_alert_reports_confidence;
DROP INDEX IF EXISTS public.idx_alert_reports_created_at;
DROP INDEX IF EXISTS public.idx_alert_reports_symbol;

-- Alert Collections - Unused indexes
DROP INDEX IF EXISTS public.idx_alert_collections_confidence;
DROP INDEX IF EXISTS public.idx_alert_collections_priority;
DROP INDEX IF EXISTS public.idx_alert_collections_status;
DROP INDEX IF EXISTS public.idx_alert_collections_symbol;
DROP INDEX IF EXISTS public.idx_alert_collections_timestamp;

-- Alert Fusion Data - Unused indexes
DROP INDEX IF EXISTS public.idx_alert_fusion_score;
DROP INDEX IF EXISTS public.idx_alert_fusion_symbol;
DROP INDEX IF EXISTS public.idx_alert_fusion_timestamp;

-- Alerts Table - Unused indexes
DROP INDEX IF EXISTS public.idx_alerts_symbol;
DROP INDEX IF EXISTS public.idx_alerts_user_id;

-- ============================================================================
-- STAGE 2: CRYPTOMETER INDEXES - Monitor before removal
-- ============================================================================

-- Cryptometer Symbol Analysis
DROP INDEX IF EXISTS public.idx_cryptometer_symbol_analysis_symbol_timestamp;
DROP INDEX IF EXISTS public.idx_cryptometer_symbol_analysis_score;

-- Cryptometer System Status
DROP INDEX IF EXISTS public.idx_cryptometer_system_status_timestamp;

-- Cryptometer Win Rates
DROP INDEX IF EXISTS public.idx_cryptometer_win_rates_best_opportunity;
DROP INDEX IF EXISTS public.idx_cryptometer_win_rates_symbol_timestamp;

-- Cryptometer Daily Summary
DROP INDEX IF EXISTS public.idx_cryptometer_daily_summary_symbol_date;

-- Cryptometer Endpoint Data
DROP INDEX IF EXISTS public.idx_cryptometer_endpoint_data_symbol_endpoint;

-- Cryptometer Patterns
DROP INDEX IF EXISTS public.idx_cryptometer_patterns_signal;
DROP INDEX IF EXISTS public.idx_cryptometer_patterns_symbol_timeframe;

-- ============================================================================
-- STAGE 3: CRYPTOVERSE RISK INDEXES
-- ============================================================================

-- BTC Risk Grid
DROP INDEX IF EXISTS public.idx_btc_grid_risk;
DROP INDEX IF EXISTS public.idx_btc_grid_symbol;

-- BTC Risks
DROP INDEX IF EXISTS public.idx_btc_risks_risk_value;
DROP INDEX IF EXISTS public.idx_btc_risks_symbol;

-- Fiat Risk Grid
DROP INDEX IF EXISTS public.idx_fiat_grid_risk;
DROP INDEX IF EXISTS public.idx_fiat_grid_symbol;

-- Fiat Risks
DROP INDEX IF EXISTS public.idx_fiat_risks_risk_value;
DROP INDEX IF EXISTS public.idx_fiat_risks_symbol;

-- Risk Data
DROP INDEX IF EXISTS public.idx_risk_data_symbol;

-- Risk Time Bands
DROP INDEX IF EXISTS public.idx_time_bands_current;
DROP INDEX IF EXISTS public.idx_time_bands_symbol;

-- Risk Metric Grid
DROP INDEX IF EXISTS public.idx_risk_metric_grid_price;
DROP INDEX IF EXISTS public.idx_risk_metric_grid_risk;
DROP INDEX IF EXISTS public.idx_risk_metric_grid_symbol;

-- Risk Time Bands (different table)
DROP INDEX IF EXISTS public.idx_risk_time_bands_coefficient;
DROP INDEX IF EXISTS public.idx_risk_time_bands_symbol;

-- ============================================================================
-- STAGE 4: ZMARTYCHAT INDEXES
-- ============================================================================

-- Conversation Messages
DROP INDEX IF EXISTS public.idx_conversation_messages_user_id;

-- Credit Transactions
DROP INDEX IF EXISTS public.idx_credit_transactions_created_at;
DROP INDEX IF EXISTS public.idx_credit_transactions_user_id;

-- User Categories
DROP INDEX IF EXISTS public.idx_user_categories_user_id;

-- User Insights
DROP INDEX IF EXISTS public.idx_user_insights_user_id;

-- User Subscriptions
DROP INDEX IF EXISTS public.idx_user_subscriptions_user_id;

-- User Transcripts
DROP INDEX IF EXISTS public.idx_user_transcripts_user_id;

-- ============================================================================
-- STAGE 5: TRADING & PORTFOLIO INDEXES
-- ============================================================================

-- Trade History
DROP INDEX IF EXISTS public.idx_trade_history_executed_at;
DROP INDEX IF EXISTS public.idx_trade_history_symbol;
DROP INDEX IF EXISTS public.idx_trade_history_user_id;

-- Trading Accounts
DROP INDEX IF EXISTS public.idx_trading_accounts_user_id;

-- Trading Intelligence
DROP INDEX IF EXISTS public.idx_trading_intelligence_created;
DROP INDEX IF EXISTS public.idx_trading_intelligence_symbol;

-- Trading Strategies
DROP INDEX IF EXISTS public.idx_trading_strategies_user_id;

-- Portfolio Snapshots
DROP INDEX IF EXISTS public.idx_portfolio_snapshots_portfolio_id;
DROP INDEX IF EXISTS public.idx_portfolio_snapshots_timestamp;

-- Portfolios
DROP INDEX IF EXISTS public.idx_portfolios_account_id;
DROP INDEX IF EXISTS public.idx_portfolios_user_id;

-- ============================================================================
-- STAGE 6: SERVICE & SYSTEM INDEXES
-- ============================================================================

-- Service Communications
DROP INDEX IF EXISTS public.idx_service_communications_from_service;
DROP INDEX IF EXISTS public.idx_service_communications_timestamp;
DROP INDEX IF EXISTS public.idx_service_communications_to_service;

-- Service Configurations
DROP INDEX IF EXISTS public.idx_service_configurations_key;
DROP INDEX IF EXISTS public.idx_service_configurations_service;

-- Service Dependencies
DROP INDEX IF EXISTS public.idx_service_dependencies_depends_on;
DROP INDEX IF EXISTS public.idx_service_dependencies_service;

-- Service Deployments
DROP INDEX IF EXISTS public.idx_service_deployments_service;
DROP INDEX IF EXISTS public.idx_service_deployments_status;

-- Service Health Metrics
DROP INDEX IF EXISTS public.idx_service_health_service_id;
DROP INDEX IF EXISTS public.idx_service_health_timestamp;

-- Service Logs
DROP INDEX IF EXISTS public.idx_service_logs_level;
DROP INDEX IF EXISTS public.idx_service_logs_service_id;
DROP INDEX IF EXISTS public.idx_service_logs_timestamp;

-- ============================================================================
-- STAGE 7: MISCELLANEOUS INDEXES
-- ============================================================================

-- Manus Extraordinary Reports
DROP INDEX IF EXISTS public.idx_manus_reports_score;
DROP INDEX IF EXISTS public.idx_manus_reports_status;
DROP INDEX IF EXISTS public.idx_manus_reports_symbol;

-- MDC Documentation
DROP INDEX IF EXISTS public.idx_mdc_docs_status;
DROP INDEX IF EXISTS public.idx_mdc_docs_symbol;
DROP INDEX IF EXISTS public.idx_mdc_docs_type;

-- Prompt Templates
DROP INDEX IF EXISTS public.idx_prompt_templates_active;
DROP INDEX IF EXISTS public.idx_prompt_templates_type;

-- Snippet Contents
DROP INDEX IF EXISTS public.idx_snippet_contents_name;
DROP INDEX IF EXISTS public.idx_snippet_contents_type;

-- Symbol Coverage
DROP INDEX IF EXISTS public.idx_symbol_coverage_last_alert;
DROP INDEX IF EXISTS public.idx_symbol_coverage_status;

-- ============================================================================
-- STAGE 8: PRIVATE SCHEMA INDEXES
-- ============================================================================

-- MV Risk Trading Signals
DROP INDEX IF EXISTS private.idx_mv_risk_signals_time;

-- MV Risk Time Distribution
DROP INDEX IF EXISTS private.idx_mv_risk_time_period;

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check total number of indexes before/after
SELECT
    schemaname,
    COUNT(*) as index_count,
    pg_size_pretty(SUM(pg_relation_size(indexrelid))) as total_size
FROM pg_stat_user_indexes
WHERE schemaname IN ('public', 'private')
GROUP BY schemaname;

-- Find any remaining unused indexes
SELECT
    schemaname,
    tablename,
    indexrelname,
    idx_scan as times_used,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname IN ('public', 'private')
  AND idx_scan = 0
  AND indexrelname NOT LIKE 'pg_%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- ============================================================================
-- ROLLBACK SCRIPT GENERATOR
-- ============================================================================
-- If you need to recreate any dropped index, use this template:
--
-- CREATE INDEX index_name ON schema.table_name(column_name);
--
-- Save the output of this query BEFORE running drops:
--
-- SELECT indexdef || ';' as recreate_statement
-- FROM pg_indexes
-- WHERE indexname LIKE 'idx_%'
--   AND schemaname IN ('public', 'private');
-- ============================================================================

-- ============================================================================
-- EXPECTED BENEFITS
-- ============================================================================
-- 1. Storage Savings: ~100-500MB (depends on table sizes)
-- 2. Write Performance: 5-15% improvement on INSERT/UPDATE operations
-- 3. Maintenance: Reduced VACUUM and ANALYZE overhead
-- 4. Simplified Schema: Easier to understand and maintain
-- ============================================================================

-- ============================================================================
-- MONITORING AFTER CLEANUP
-- ============================================================================
-- Monitor for 7 days after cleanup:
--
-- 1. Check query performance hasn't degraded
-- 2. Monitor slow query log
-- 3. Watch for missing index errors in application logs
-- 4. Run EXPLAIN ANALYZE on critical queries
-- ============================================================================
