# On-Call Runbook

## Overview

This runbook provides **step-by-step troubleshooting guides** for common production issues with the Zmarty platform.

---

## 🚨 Issue: Users Report "No Updates" or Stale Signals

### Symptoms
- Users see old signals (> 10 minutes old)
- New symbols not getting signals
- Win rates not updating

### Diagnosis Steps

#### Step 1: Check Health Endpoint

```bash
curl https://orchestrator-api.onrender.com/healthz
```

**Expected**: `status: "healthy"`

**If unhealthy**: Check which service is down in response

---

#### Step 2: Check Queue Depths

```sql
-- Run in Supabase B SQL Editor
SELECT
  'ingest_indicators' AS queue,
  pgmq.queue_depth('ingest_indicators') AS depth
UNION ALL
SELECT 'compute_signals', pgmq.queue_depth('compute_signals')
UNION ALL
SELECT 'compute_winrate', pgmq.queue_depth('compute_winrate');
```

**Expected**: Depth < 100 for each queue

**If depth > 100**: Queue backlog, scale worker up (see resolution below)

---

#### Step 3: Check Latest Signal Timestamp

```sql
-- Run in Supabase B SQL Editor
SELECT
  symbol,
  timeframe,
  MAX(created_at) AS latest_signal,
  NOW() - MAX(created_at) AS age
FROM public.signals
GROUP BY symbol, timeframe
ORDER BY latest_signal DESC;
```

**Expected**: Latest signal within last 5-10 minutes

**If older**: Check cron jobs and worker status

---

#### Step 4: Check Cron Job Status

```sql
-- Run in Supabase B SQL Editor
SELECT
  jobname,
  schedule,
  active,
  last_run,
  next_run
FROM cron.job;
```

**Expected**:

- `ingest_active_watchers` - active, next_run within 5 minutes
- `recompute_winrate` - active, next_run within 1 hour

**If inactive**: Re-enable cron jobs (see resolution)

---

### Resolution

#### If Queue Backlog High (depth > 100)

1. **Scale Worker Up** in Render:

```text
   Render Dashboard → orchestrator-worker → Settings → Instance Type
   Select larger instance (e.g., Starter → Standard)
   ```

2. **Add More Workers** (if supported):

```text
   Render Dashboard → orchestrator-worker → Settings → Scaling
   Increase number of instances
   ```

3. **Check API Rate Limits**:
   - Cryptometer: 60 req/min
   - KingFisher: 30 req/min
   - If hitting limits, add backoff or upgrade API plan

---

#### If Cron Jobs Inactive

```sql
-- Re-enable cron job
SELECT cron.unschedule('ingest_active_watchers');

SELECT cron.schedule(
  'ingest_active_watchers',
  '*/5 * * * *',
  $$SELECT pgmq.send('ingest_indicators', jsonb_build_object('symbol', symbol, 'timeframe', timeframe))
    FROM (SELECT DISTINCT symbol, timeframe FROM public.watchers WHERE active = true) AS active_watchers$$
);
```

---

#### If Worker Not Processing

1. **Check Worker Logs** in Render:

```text
   Render Dashboard → orchestrator-worker → Logs
   Look for errors or exceptions
   ```

2. **Restart Worker**:

```text
   Render Dashboard → orchestrator-worker → Manual Deploy → Clear build cache & deploy
   ```

3. **Verify Environment Variables**:

```bash
   Check SUPABASE_B_URL, SUPABASE_B_SERVICE_KEY are set correctly
   ```

---

## 🚨 Issue: Chat Endpoint Returns 500 Error

### Symptoms
- `/chat` endpoint returning 500 Internal Server Error
- Frontend shows error message
- Logs show exceptions

### Diagnosis Steps

#### Step 1: Check API Logs

```text
Render Dashboard → orchestrator-api → Logs
Filter by: last 10 minutes, level: error
```

#### Step 2: Test Health Endpoint

```bash
curl https://orchestrator-api.onrender.com/healthz
```

#### Step 3: Check Provider Status

```bash

# Test Grok

curl https://api.x.ai/v1/models -H "Authorization: Bearer $XAI_API_KEY"

# Test GPT

curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"

# Test Claude

curl https://api.anthropic.com/v1/messages -H "x-api-key: $ANTHROPIC_API_KEY"
```

### Resolution

#### If Provider Down
- **Temporary**: Use different provider in prompt (e.g., "use GPT")
- **Permanent**: Check API key validity, billing status, rate limits

#### If Database Connection Error

1. Check Supabase status: https://status.supabase.com
2. Verify service role keys in Render env vars
3. Check connection pool exhaustion (increase pool size)

#### If Out of Memory

1. Scale API service to larger instance
2. Check for memory leaks in logs
3. Restart service

---

## 🚨 Issue: Users Not Getting Credits Charged

### Symptoms
- Chat works but credits balance doesn't decrease
- Credits ledger not showing new rows

### Diagnosis Steps

#### Step 1: Check Credits Ledger

```sql
-- Run in Supabase A SQL Editor
SELECT * FROM public.credits_ledger
WHERE user_id = '<user-uuid>'
ORDER BY created_at DESC
LIMIT 10;
```

**Expected**: New row for each chat request

---

#### Step 2: Check Function Permissions

```sql
-- Run in Supabase A SQL Editor
SELECT * FROM pg_proc WHERE proname = 'charge_user_credits';
```

**Expected**: Function exists with SECURITY DEFINER

---

### Resolution

#### If Function Missing

Re-apply `20-SCHEMA-SUPABASE-A.sql` schema

#### If Permission Error

```sql
-- Grant execute permission to service role
GRANT EXECUTE ON FUNCTION public.charge_user_credits TO service_role;
```

#### If Logic Error

Check orchestrator-api logs for credit charging errors

---

## 🚨 Issue: Webhook Not Syncing (A → B)

### Symptoms
- Add symbol in frontend (Supabase A)
- Symbol doesn't appear in Supabase B `watchers` table

### Diagnosis Steps

#### Step 1: Check Webhook Status in Supabase A

```text
Supabase A Dashboard → Database → Webhooks
Check: user_symbols_sync webhook is enabled
```

#### Step 2: Check Edge Function Logs in Supabase B

```text
Supabase B Dashboard → Edge Functions → watchers-upsert → Logs
Look for recent invocations and errors
```

#### Step 3: Test Webhook Manually

```bash

# Generate HMAC signature

PAYLOAD='{"type":"INSERT","record":{"user_id":"test","symbol":"BTC/USDT","timeframe":"1h"}}'
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" | cut -d' ' -f2)

# Send request

curl -X POST \
  https://<supabase-b-url>/functions/v1/watchers-upsert \
  -H "Content-Type: application/json" \
  -H "x-hmac-sha256: $SIGNATURE" \
  -d "$PAYLOAD"
```

**Expected**: `{"success":true}`

---

### Resolution

#### If HMAC Signature Invalid
- Verify `WEBHOOK_SECRET` matches in both:
  - Supabase A webhook configuration
  - Supabase B edge function environment

#### If Edge Function Error

1. Check edge function logs for specific error
2. Redeploy edge function:

   ```bash
   supabase functions deploy watchers-upsert --project-ref <ref>
   ```

3. Verify env vars set in Supabase B

#### If Webhook Disabled

Re-enable webhook in Supabase A dashboard

---

## 🚨 Issue: High Latency / Slow Responses

### Symptoms
- Chat responses take > 10 seconds
- Users complaining about slowness

### Diagnosis Steps

#### Step 1: Check Provider Latency

```bash
curl -w "@curl-format.txt" -o /dev/null -s https://api.x.ai/v1/models
```

Create `curl-format.txt`:

```typescript
time_total: %{time_total}s\n
```

#### Step 2: Check Database Query Performance

```sql
-- Run in Supabase B
SELECT
  query,
  calls,
  mean_exec_time,
  max_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- Queries > 100ms
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Resolution

#### If Provider Slow
- Switch to faster provider (Grok is usually fastest)
- Check provider status page
- Reduce max_tokens to speed up generation

#### If Database Slow
- Add missing indexes (check `EXPLAIN ANALYZE`)
- Prune old data (run cleanup function)
- Upgrade Supabase plan for more resources

#### If Worker Backlog
- Scale worker up
- Increase worker concurrency
- Optimize queue processing logic

---

## 📊 Monitoring Dashboard

### Key Metrics to Monitor

1. **Request Latency**:
   - `/chat` p95 < 3 seconds
   - `/healthz` p95 < 100ms

2. **Error Rate**:
   - < 1% overall
   - < 0.1% for 500 errors

3. **Queue Depth**:
   - `ingest_indicators` < 50
   - `compute_signals` < 30
   - `compute_winrate` < 10

4. **Credits Usage**:
   - Daily credits charged
   - Provider distribution (should be 80% Grok)

5. **Win Rate Accuracy**:
   - Compare predicted vs actual for recent signals
   - Should be > 55% for platform credibility

---

## 🔔 Alert Thresholds

### Critical Alerts (Page On-Call)
- `/healthz` returns unhealthy
- Error rate > 5%
- Queue depth > 500
- No signals generated in last 30 minutes

### Warning Alerts (Slack/Email)
- Error rate > 1%
- Queue depth > 100
- Provider latency > 5 seconds
- Credits burn rate spike > 200%

---

## 📞 Escalation Path

1. **Level 1**: On-call engineer (follow this runbook)
2. **Level 2**: Backend lead (if issue persists > 30 min)
3. **Level 3**: CTO (if user impact > 100 users)

### Contact Info
- **Slack**: `#zmarty-oncall`
- **PagerDuty**: `zmarty-production`
- **Email**: `oncall@zmartbot.com`

---

## 🛠️ Useful Commands

### Restart Services

```bash

# Restart API

render services restart orchestrator-api

# Restart Worker

render services restart orchestrator-worker
```

### Clear Queue Backlog

```sql
-- If queue is stuck, archive and recreate
SELECT pgmq.archive('ingest_indicators', NOW() - INTERVAL '1 hour');
SELECT pgmq.create('ingest_indicators');
```

### Force Win Rate Recompute

```sql
-- Enqueue all active symbols
SELECT pgmq.send(
  'compute_winrate',
  jsonb_build_object('symbol', symbol, 'timeframe', timeframe, 'lookback_days', 30)
)
FROM (SELECT DISTINCT symbol, timeframe FROM public.watchers WHERE active = true) AS symbols;
```

### Check Recent Errors

```sql
-- Supabase B: Check edge function errors
SELECT * FROM logs.edge_functions
WHERE level = 'error'
  AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-09-30
**Status**: Runbook Complete



