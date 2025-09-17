# 🚀 Complete Supabase Setup Instructions for ZmartBot

## Overview
Comprehensive setup guide for ALL ZmartBot modules requiring Supabase database integration. This includes Alert Agent, RiskMetric System, Cryptometer, Trading Intelligence, and more.

## 🗂️ Module Overview

### Core Modules Requiring Supabase Setup:

1. **Alert Collection Agent** - Alert management and MDC documentation
2. **RiskMetric System** - Advanced risk analysis with Cowen methodology
3. **Cryptometer Integration** - Multi-timeframe analysis and win rates
4. **Trading Intelligence** - Pattern recognition and ML analysis
5. **Symbol Coverage** - Complete symbol monitoring system

## 📋 Required Migration Files

Execute these SQL files in order in your Supabase SQL Editor:

### Priority 1: Core System Tables
1. **RiskMetric System** (`COMPLETE_RISKMETRIC_SYSTEM.sql`)
   - Cryptoverse risk grids (1,435 data points)
   - Time bands and scoring functions
   - Interpolation and calculation functions

2. **Trading Intelligence** (`database/trading_intelligence_tables.sql`)
   - Trading analyses core tables
   - Pattern library for ML
   - Smart alerts system
   - Performance tracking

### Priority 2: Agent Systems
3. **Alert Collection Agent** (`database/migrations/alert_agent_supabase_schema.sql`)
   - 8 core tables for alert management
   - 21 indexes for optimal performance
   - 4 database views for monitoring
   - Row-level security policies

4. **Cryptometer Tables** (`database/migrations/cryptometer_tables_migration.sql`)
   - Multi-timeframe analysis storage
   - Win rate predictions
   - AI recommendations tracking
   - Real-time indicators

### Priority 3: Risk Data Import
5. **Symbol Risk Data** (Execute all in any order):
   - `btc_risk_data.sql`, `eth_risk_data.sql`, `ada_risk_data.sql`
   - `sol_risk_data.sql`, `avax_risk_data.sql`, `xrp_risk_data.sql`
   - `atom_risk_data.sql`, `algo_risk_data.sql`, `hbar_risk_data.sql`
   - And all other `*_risk_data.sql` files

## 📝 Step-by-Step Setup Guide

### Step 1: Verify Environment Variables ✅

Ensure these are set in your `.env` file:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

**Current Status:** ✅ Already configured with valid keys (expires 2065)

### Step 2: Execute Core Migrations in Order

1. **Login to Supabase Dashboard**
   - Go to your project at https://app.supabase.com
   - Navigate to "SQL Editor" in the left sidebar

2. **Run RiskMetric System First** (CRITICAL)
   ```sql
   -- Execute: COMPLETE_RISKMETRIC_SYSTEM.sql
   -- This creates all core risk analysis infrastructure
   ```

3. **Run Trading Intelligence Tables**
   ```sql
   -- Execute: database/trading_intelligence_tables.sql
   -- Creates pattern recognition and ML tables
   ```

4. **Run Alert Collection Schema**
   ```sql
   -- Execute: database/migrations/alert_agent_supabase_schema.sql
   -- Creates alert management system
   ```

5. **Run Cryptometer Migration**
   ```sql
   -- Execute: database/migrations/cryptometer_tables_migration.sql
   -- Creates multi-timeframe analysis tables
   ```

6. **Import Risk Data** (All symbol-specific data)
   ```sql
   -- Execute all *_risk_data.sql files
   -- This populates the risk grids with actual data
   ```

### Step 3: Comprehensive Table Verification

Run this master verification query:

```sql
-- Check ALL ZmartBot tables
SELECT
    table_name,
    CASE
        WHEN table_name LIKE 'alert_%' THEN 'Alert System'
        WHEN table_name LIKE 'cryptometer_%' THEN 'Cryptometer'
        WHEN table_name LIKE 'cryptoverse_%' THEN 'RiskMetric'
        WHEN table_name LIKE 'trading_%' THEN 'Trading Intelligence'
        WHEN table_name LIKE 'pattern_%' THEN 'Pattern Recognition'
        WHEN table_name LIKE 'smart_%' THEN 'Smart Alerts'
        WHEN table_name LIKE 'manus_%' THEN 'Manus Integration'
        WHEN table_name LIKE 'mdc_%' THEN 'MDC Documentation'
        WHEN table_name LIKE 'symbol_%' THEN 'Symbol Coverage'
        WHEN table_name LIKE 'prompt_%' THEN 'Prompt Templates'
        ELSE 'Other'
    END as module
FROM information_schema.tables
WHERE table_schema = 'public'
AND (
    table_name LIKE 'alert_%' OR
    table_name LIKE 'cryptometer_%' OR
    table_name LIKE 'cryptoverse_%' OR
    table_name LIKE 'trading_%' OR
    table_name LIKE 'pattern_%' OR
    table_name LIKE 'smart_%' OR
    table_name LIKE 'manus_%' OR
    table_name LIKE 'mdc_%' OR
    table_name LIKE 'symbol_%' OR
    table_name LIKE 'prompt_%'
)
ORDER BY module, table_name;
```

**Expected Tables by Module:**

| Module | Tables Count | Key Tables |
|--------|-------------|------------|
| Alert System | 8 | alert_collections, alert_reports, alert_fusion_data |
| RiskMetric | 5+ | cryptoverse_risk_grid, cryptoverse_btc_risk_grid, cryptoverse_risk_data |
| Cryptometer | 6+ | cryptometer_symbol_analysis, cryptometer_win_rates |
| Trading Intelligence | 8+ | trading_analyses, pattern_library, smart_alerts |
| MDC Documentation | 1 | mdc_documentation |
| Manus Integration | 1 | manus_extraordinary_reports |
| Symbol Coverage | 1 | symbol_coverage |
| Prompt Templates | 1 | prompt_templates |

### 5. Verify Views Created

```sql
-- Check views
SELECT viewname
FROM pg_views
WHERE schemaname = 'public'
AND viewname IN (
    'active_alerts_summary',
    'symbol_coverage_status',
    'manus_reports_summary',
    'agent_performance_metrics'
);
```

**Expected Result:** Should return 4 rows

### 6. Verify RLS Policies

```sql
-- Check Row Level Security is enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename LIKE 'alert%'
OR tablename LIKE 'manus%'
OR tablename LIKE 'mdc%'
OR tablename LIKE 'symbol%'
OR tablename LIKE 'prompt%';
```

**Expected Result:** All tables should show `rowsecurity = true`

### 7. Test Initial Data

```sql
-- Check prompt templates were inserted
SELECT template_name, template_type
FROM prompt_templates
WHERE is_active = true;
```

**Expected Result:** Should return 4 prompt templates:
- `mdc_alert_report`
- `manus_extraordinary_analysis`
- `technical_analysis_comprehensive`
- `risk_assessment_professional`

### 8. Optional: Insert Professional Prompt Templates

If you want to add the new professional templates from `professional_prompt_templates.py`:

```sql
-- Add ChatGPT professional template
INSERT INTO prompt_templates (
    template_name,
    template_type,
    template_content,
    variables,
    example_usage,
    version
) VALUES (
    'chatgpt_alert_analysis_professional',
    'manus_analysis',
    'Professional ChatGPT prompt content here...',
    '{"symbol": "string", "alert_data": "object", "technical_data": "object"}',
    'Use for ChatGPT professional alert analysis with GPT-4',
    '2.0.0'
);

-- Add Manus task execution template
INSERT INTO prompt_templates (
    template_name,
    template_type,
    template_content,
    variables,
    example_usage,
    version
) VALUES (
    'manus_task_execution_professional',
    'manus_analysis',
    'Manus task execution prompt content here...',
    '{"task_id": "string", "task_type": "string", "parameters": "object"}',
    'Use for Manus webhook task execution',
    '2.0.0'
);
```

### 9. Test Connection from Application

Run this test to verify connection:

```python
python3 -c "
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')

if url and key:
    client = create_client(url, key)
    result = client.table('prompt_templates').select('template_name').limit(1).execute()
    if result.data:
        print('✅ Supabase connection successful!')
        print(f'Found template: {result.data[0][\"template_name\"]}')
    else:
        print('⚠️ Connection works but no data found')
else:
    print('❌ Missing environment variables')
"
```

### 10. Production Checklist

Before running in production:

- [ ] All 8 tables created
- [ ] All 21 indexes created
- [ ] All 4 views created
- [ ] RLS policies active on all tables
- [ ] Prompt templates inserted
- [ ] Environment variables set correctly
- [ ] Connection test passes
- [ ] Webhook endpoints tested (`/api/webhooks/manus/alerts/*`)
- [ ] Alert Collection Agent can write to database
- [ ] Master Agent can read alerts

## 🔍 Monitoring & Maintenance

### Check Alert Collection Status

```sql
-- View recent alerts
SELECT * FROM active_alerts_summary;

-- Check symbol coverage
SELECT * FROM symbol_coverage_status;

-- View agent performance
SELECT * FROM agent_performance_metrics
WHERE hour > NOW() - INTERVAL '24 hours';
```

### Monitor Manus Reports

```sql
-- Check extraordinary reports
SELECT * FROM manus_reports_summary;

-- View recent Manus analyses
SELECT symbol, extraordinary_score, created_at
FROM manus_extraordinary_reports
WHERE status = 'completed'
ORDER BY created_at DESC
LIMIT 10;
```

### Database Maintenance

```sql
-- Clean old alerts (keep last 30 days)
DELETE FROM alert_collections
WHERE created_at < NOW() - INTERVAL '30 days'
AND status = 'archived';

-- Update statistics
ANALYZE alert_collections;
ANALYZE alert_reports;
```

## 🚨 Troubleshooting

### Common Issues

1. **"Invalid API Key" Error**
   - Check SUPABASE_ANON_KEY is correct
   - Verify key hasn't expired
   - Ensure using anon key, not service role key

2. **"Table not found" Error**
   - Run migration script again
   - Check you're in correct project
   - Verify schema is 'public'

3. **"Permission denied" Error**
   - Check RLS policies are correct
   - Verify using correct authentication
   - For testing, temporarily disable RLS:
   ```sql
   ALTER TABLE alert_collections DISABLE ROW LEVEL SECURITY;
   ```

4. **Connection Timeout**
   - Check SUPABASE_URL is correct
   - Verify network connectivity
   - Check Supabase project is active

## ✅ Success Indicators

Your Alert Agent is properly configured when:

1. All database objects created successfully
2. Connection test passes
3. Alert Collection Agent can store alerts
4. MDC documentation generates correctly
5. Manus reports trigger for high-confidence alerts
6. Master Agent can retrieve alerts on demand
7. Performance metrics are being recorded

## 📞 Support

If you encounter issues:
1. Check Supabase logs in dashboard
2. Review application logs for detailed errors
3. Verify all environment variables
4. Test with simple queries first
5. Check Supabase status page for outages

---

## 🧪 Module-Specific Testing

### Test RiskMetric System
```sql
-- Test risk calculation for ADA at current price
SELECT riskmetric_agent_enhanced('ADA', 0.8824);

-- Test detailed output
SELECT * FROM riskmetric_agent_enhanced_detailed('ADA', 0.8824);

-- Test multiple symbols
SELECT
    symbol,
    get_risk_at_price(symbol, 100000, 'fiat') as btc_risk,
    get_price_at_risk(symbol, 0.5, 'fiat') as price_at_50_risk
FROM (VALUES ('BTC'), ('ETH'), ('ADA')) AS t(symbol);
```

### Test Cryptometer Integration
```sql
-- Check latest Cryptometer analyses
SELECT symbol, short_term_score, medium_term_score, long_term_score, ai_recommendation
FROM cryptometer_symbol_analysis
ORDER BY created_at DESC
LIMIT 5;

-- Check win rate predictions
SELECT symbol, short_term_24h_win_rate, medium_term_7d_win_rate, long_term_30d_win_rate
FROM cryptometer_win_rates
ORDER BY timestamp DESC
LIMIT 5;
```

### Test Alert System
```sql
-- Check active alerts
SELECT * FROM active_alerts_summary;

-- Check symbol coverage
SELECT * FROM symbol_coverage_status;

-- Check Manus reports
SELECT symbol, extraordinary_score, created_at
FROM manus_extraordinary_reports
WHERE status = 'completed'
ORDER BY created_at DESC
LIMIT 5;
```

### Test Trading Intelligence
```sql
-- Check recent analyses
SELECT symbol, analysis_type, confidence_score, risk_level, recommendation
FROM trading_analyses
ORDER BY created_at DESC
LIMIT 5;

-- Check pattern detections
SELECT pattern_name, pattern_type, success_rate, last_detected
FROM pattern_library
WHERE usage_count > 0
ORDER BY last_detected DESC
LIMIT 5;
```

## ⚡ Critical Functions to Verify

Run this to check all critical functions exist:

```sql
SELECT
    routine_name,
    routine_type,
    CASE
        WHEN routine_name LIKE '%risk%' THEN 'RiskMetric'
        WHEN routine_name LIKE '%interpolation%' THEN 'Interpolation'
        WHEN routine_name LIKE '%update%' THEN 'Triggers'
        ELSE 'Other'
    END as category
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_type IN ('FUNCTION', 'PROCEDURE')
ORDER BY category, routine_name;
```

**Expected Functions:**
- `get_risk_at_price` - Price to risk interpolation
- `get_price_at_risk` - Risk to price interpolation
- `riskmetric_agent_enhanced` - Main risk calculation
- `riskmetric_agent_enhanced_detailed` - Detailed risk output
- `update_updated_at_column` - Timestamp trigger function
- `calculate_time_adjustment` - Time-based risk adjustment

## 🚀 Quick Start Commands

### For Development Testing
```python
# Test Supabase connection with all modules
python3 -c "
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')

if url and key:
    client = create_client(url, key)

    # Test each module
    tests = {
        'Alert System': 'alert_collections',
        'RiskMetric': 'cryptoverse_risk_grid',
        'Cryptometer': 'cryptometer_symbol_analysis',
        'Trading Intelligence': 'trading_analyses',
        'Prompt Templates': 'prompt_templates'
    }

    for module, table in tests.items():
        try:
            result = client.table(table).select('*').limit(1).execute()
            print(f'✅ {module}: Connected')
        except:
            print(f'❌ {module}: Table missing or error')
else:
    print('❌ Missing environment variables')
"
```

## 📊 Database Health Check

Run this comprehensive health check:

```sql
-- Complete system health check
WITH table_counts AS (
    SELECT 'Alert Collections' as module, COUNT(*) as count FROM alert_collections
    UNION ALL
    SELECT 'Alert Reports', COUNT(*) FROM alert_reports
    UNION ALL
    SELECT 'Symbol Coverage', COUNT(*) FROM symbol_coverage
    UNION ALL
    SELECT 'Risk Grid (Fiat)', COUNT(*) FROM cryptoverse_risk_grid
    UNION ALL
    SELECT 'Risk Grid (BTC)', COUNT(*) FROM cryptoverse_btc_risk_grid
    UNION ALL
    SELECT 'Cryptometer Analyses', COUNT(*) FROM cryptometer_symbol_analysis
    UNION ALL
    SELECT 'Trading Analyses', COUNT(*) FROM trading_analyses
    UNION ALL
    SELECT 'Pattern Library', COUNT(*) FROM pattern_library
    UNION ALL
    SELECT 'Prompt Templates', COUNT(*) FROM prompt_templates
)
SELECT
    module,
    count,
    CASE
        WHEN module = 'Risk Grid (Fiat)' AND count >= 1025 THEN '✅ OK'
        WHEN module = 'Risk Grid (BTC)' AND count >= 410 THEN '✅ OK'
        WHEN module = 'Prompt Templates' AND count >= 4 THEN '✅ OK'
        WHEN count > 0 THEN '⚠️ Has Data'
        ELSE '❌ Empty'
    END as status
FROM table_counts
ORDER BY
    CASE
        WHEN module LIKE 'Risk%' THEN 1
        WHEN module LIKE 'Alert%' THEN 2
        WHEN module LIKE 'Crypto%' THEN 3
        ELSE 4
    END;
```

## 🔴 CRITICAL: Order of Operations

**MUST follow this order to avoid dependency errors:**

1. **RiskMetric System** (creates base functions)
2. **Trading Intelligence** (creates core tables)
3. **Alert Agent** (depends on base structure)
4. **Cryptometer** (depends on trading tables)
5. **Risk Data Import** (populates grids)
6. **Test Functions** (verify everything works)

## 🛠️ Maintenance Scripts

### Daily Maintenance
```sql
-- Update statistics for query optimization
ANALYZE alert_collections;
ANALYZE cryptoverse_risk_grid;
ANALYZE cryptometer_symbol_analysis;
ANALYZE trading_analyses;

-- Clean old data (keep 90 days)
DELETE FROM alert_collections
WHERE created_at < NOW() - INTERVAL '90 days'
AND status = 'archived';

DELETE FROM cryptometer_symbol_analysis
WHERE created_at < NOW() - INTERVAL '90 days';
```

### Performance Monitoring
```sql
-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check slow queries
SELECT
    query,
    calls,
    total_time,
    mean,
    stddev_time,
    rows
FROM pg_stat_statements
WHERE mean > 1000  -- queries taking more than 1 second
ORDER BY mean DESC
LIMIT 10;
```

---

*Last Updated: 2025-09-17*
*ZmartBot Complete System v3.0 - Production Ready*