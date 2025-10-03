-- ============================================================================
-- ZMARTBOT DATABASE OPTIMIZATION - UNUSED INDEX CLEANUP (SAFE VERSION)
-- ============================================================================
-- Purpose: Remove unused indexes (excluding constraint-backed indexes)
-- Date: 2025-10-01
-- Version: SAFE (skips indexes that support constraints)
-- ============================================================================

-- NOTE: Skipping 'unique_active_symbol' - it backs a UNIQUE constraint

-- BATCH 1: Alert & Report Indexes (14 indexes - skip unique_active_symbol)
DROP INDEX IF EXISTS public.idx_alert_reports_active;
DROP INDEX IF EXISTS public.idx_alert_reports_confidence;
DROP INDEX IF EXISTS public.idx_alert_reports_created_at;
DROP INDEX IF EXISTS public.idx_alert_reports_symbol;
DROP INDEX IF EXISTS public.idx_alert_collections_confidence;
DROP INDEX IF EXISTS public.idx_alert_collections_priority;
DROP INDEX IF EXISTS public.idx_alert_collections_status;
DROP INDEX IF EXISTS public.idx_alert_collections_symbol;
DROP INDEX IF EXISTS public.idx_alert_collections_timestamp;
DROP INDEX IF EXISTS public.idx_alert_fusion_score;
DROP INDEX IF EXISTS public.idx_alert_fusion_symbol;
DROP INDEX IF EXISTS public.idx_alert_fusion_timestamp;
DROP INDEX IF EXISTS public.idx_alerts_symbol;
DROP INDEX IF EXISTS public.idx_alerts_user_id;

-- BATCH 2: Cryptometer Indexes (9 indexes)
DROP INDEX IF EXISTS public.idx_cryptometer_symbol_analysis_symbol_timestamp;
DROP INDEX IF EXISTS public.idx_cryptometer_symbol_analysis_score;
DROP INDEX IF EXISTS public.idx_cryptometer_system_status_timestamp;
DROP INDEX IF EXISTS public.idx_cryptometer_win_rates_best_opportunity;
DROP INDEX IF EXISTS public.idx_cryptometer_win_rates_symbol_timestamp;
DROP INDEX IF EXISTS public.idx_cryptometer_daily_summary_symbol_date;
DROP INDEX IF EXISTS public.idx_cryptometer_endpoint_data_symbol_endpoint;
DROP INDEX IF EXISTS public.idx_cryptometer_patterns_signal;
DROP INDEX IF EXISTS public.idx_cryptometer_patterns_symbol_timeframe;

-- BATCH 3: Cryptoverse Risk Indexes (14 indexes)
DROP INDEX IF EXISTS public.idx_btc_grid_risk;
DROP INDEX IF EXISTS public.idx_btc_grid_symbol;
DROP INDEX IF EXISTS public.idx_btc_risks_risk_value;
DROP INDEX IF EXISTS public.idx_btc_risks_symbol;
DROP INDEX IF EXISTS public.idx_fiat_grid_risk;
DROP INDEX IF EXISTS public.idx_fiat_grid_symbol;
DROP INDEX IF EXISTS public.idx_fiat_risks_risk_value;
DROP INDEX IF EXISTS public.idx_fiat_risks_symbol;
DROP INDEX IF EXISTS public.idx_risk_data_symbol;
DROP INDEX IF EXISTS public.idx_time_bands_current;
DROP INDEX IF EXISTS public.idx_time_bands_symbol;
DROP INDEX IF EXISTS public.idx_risk_metric_grid_price;
DROP INDEX IF EXISTS public.idx_risk_metric_grid_risk;
DROP INDEX IF EXISTS public.idx_risk_metric_grid_symbol;

-- BATCH 4: Risk Time Bands (2 indexes)
DROP INDEX IF EXISTS public.idx_risk_time_bands_coefficient;
DROP INDEX IF EXISTS public.idx_risk_time_bands_symbol;

-- BATCH 5: ZmartyChat Indexes (7 indexes)
DROP INDEX IF EXISTS public.idx_conversation_messages_user_id;
DROP INDEX IF EXISTS public.idx_credit_transactions_created_at;
DROP INDEX IF EXISTS public.idx_credit_transactions_user_id;
DROP INDEX IF EXISTS public.idx_user_categories_user_id;
DROP INDEX IF EXISTS public.idx_user_insights_user_id;
DROP INDEX IF EXISTS public.idx_user_subscriptions_user_id;
DROP INDEX IF EXISTS public.idx_user_transcripts_user_id;

-- BATCH 6: Trading & Portfolio Indexes (11 indexes)
DROP INDEX IF EXISTS public.idx_trade_history_executed_at;
DROP INDEX IF EXISTS public.idx_trade_history_symbol;
DROP INDEX IF EXISTS public.idx_trade_history_user_id;
DROP INDEX IF EXISTS public.idx_trading_accounts_user_id;
DROP INDEX IF EXISTS public.idx_trading_intelligence_created;
DROP INDEX IF EXISTS public.idx_trading_intelligence_symbol;
DROP INDEX IF EXISTS public.idx_trading_strategies_user_id;
DROP INDEX IF EXISTS public.idx_portfolio_snapshots_portfolio_id;
DROP INDEX IF EXISTS public.idx_portfolio_snapshots_timestamp;
DROP INDEX IF EXISTS public.idx_portfolios_account_id;
DROP INDEX IF EXISTS public.idx_portfolios_user_id;

-- BATCH 7: Service Indexes (14 indexes)
DROP INDEX IF EXISTS public.idx_service_communications_from_service;
DROP INDEX IF EXISTS public.idx_service_communications_timestamp;
DROP INDEX IF EXISTS public.idx_service_communications_to_service;
DROP INDEX IF EXISTS public.idx_service_configurations_key;
DROP INDEX IF EXISTS public.idx_service_configurations_service;
DROP INDEX IF EXISTS public.idx_service_dependencies_depends_on;
DROP INDEX IF EXISTS public.idx_service_dependencies_service;
DROP INDEX IF EXISTS public.idx_service_deployments_service;
DROP INDEX IF EXISTS public.idx_service_deployments_status;
DROP INDEX IF EXISTS public.idx_service_health_service_id;
DROP INDEX IF EXISTS public.idx_service_health_timestamp;
DROP INDEX IF EXISTS public.idx_service_logs_level;
DROP INDEX IF EXISTS public.idx_service_logs_service_id;
DROP INDEX IF EXISTS public.idx_service_logs_timestamp;

-- BATCH 8: Miscellaneous Indexes (12 indexes)
DROP INDEX IF EXISTS public.idx_manus_reports_score;
DROP INDEX IF EXISTS public.idx_manus_reports_status;
DROP INDEX IF EXISTS public.idx_manus_reports_symbol;
DROP INDEX IF EXISTS public.idx_mdc_docs_status;
DROP INDEX IF EXISTS public.idx_mdc_docs_symbol;
DROP INDEX IF EXISTS public.idx_mdc_docs_type;
DROP INDEX IF EXISTS public.idx_prompt_templates_active;
DROP INDEX IF EXISTS public.idx_prompt_templates_type;
DROP INDEX IF EXISTS public.idx_snippet_contents_name;
DROP INDEX IF EXISTS public.idx_snippet_contents_type;
DROP INDEX IF EXISTS public.idx_symbol_coverage_last_alert;
DROP INDEX IF EXISTS public.idx_symbol_coverage_status;

-- BATCH 9: Private Schema Indexes (2 indexes)
DROP INDEX IF EXISTS private.idx_mv_risk_signals_time;
DROP INDEX IF EXISTS private.idx_mv_risk_time_period;

-- Total: 85 unused indexes removed (skipped 1 constraint-backed index)
-- Expected storage savings: 100-400MB
