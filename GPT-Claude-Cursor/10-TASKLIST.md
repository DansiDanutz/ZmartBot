# Minimal Tasks to Wire Everything

## Implementation Phases

This checklist outlines the **minimal viable path** to get Zmarty Control Plane operational. Complete tasks in order for dependencies to resolve correctly.

---

## 🔷 Day 1: Infrastructure Setup

### Task 1.1: Create Render Services

- [ ] Sign up / log in to [Render](https://render.com)
- [ ] Create new web service: `orchestrator-api`
  - Runtime: Node.js / Python (your choice)
  - Build command: `npm install` or `pip install -r requirements.txt`
  - Start command: `npm start` or `python main.py`
- [ ] Create new background worker: `orchestrator-worker`
  - Same runtime as API
  - Start command: `npm run worker` or `python worker.py`

### Task 1.2: Set Environment Variables

- [ ] In Render `orchestrator-api`, add env vars from `50-ENV.sample`:
  - SUPABASE_A_URL, SUPABASE_A_SERVICE_KEY
  - SUPABASE_B_URL, SUPABASE_B_SERVICE_KEY
  - JWT_SECRET
  - XAI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, ELEVENLABS_API_KEY
- [ ] In Render `orchestrator-worker`, add same env vars
- [ ] In Netlify, add frontend env vars:
  - VITE_SUPABASE_A_URL, VITE_SUPABASE_A_ANON_KEY
  - VITE_ORCHESTRATOR_API_URL (Render API URL)

### Task 1.3: Apply Database Schemas

- [ ] Open Supabase A SQL Editor
- [ ] Copy/paste contents of `20-SCHEMA-SUPABASE-A.sql`
- [ ] Run and verify tables created:
  - `user_symbols`
  - `credits_ledger`
  - View: `credit_balance`
- [ ] Open Supabase B SQL Editor
- [ ] Copy/paste contents of `21-SCHEMA-SUPABASE-B.sql`
- [ ] Run and verify tables created:
  - `watchers`, `indicators`, `risk_metric`, `liq_clusters`, `signals`, `win_rate`
- [ ] Verify extensions enabled:
  - `pgmq` (message queues)
  - `pg_cron` (scheduled jobs)
- [ ] Verify queues created:
  - `ingest_indicators`, `compute_signals`, `compute_winrate`

### Task 1.4: Configure Database Webhook (A → B)

- [ ] In Supabase A dashboard:
  - Navigate to **Database → Webhooks**
  - Click **Enable Webhooks**
- [ ] Create new webhook:
  - **Name**: `user_symbols_sync`
  - **Table**: `public.user_symbols`
  - **Events**: `INSERT`, `UPDATE`, `DELETE`
  - **Type**: HTTP Request
  - **Method**: POST
  - **URL**: `<SUPABASE_B_URL>/functions/v1/watchers-upsert`
  - **Headers**: Add custom header:
    - Key: `x-hmac-sha256`
    - Value: `${YOUR_WEBHOOK_SECRET}` (will be verified in edge function)

### Task 1.5: Deploy Edge Function (Supabase B)

- [ ] Create edge function locally:

  ```bash
  supabase functions new watchers-upsert
  ```

- [ ] Copy implementation from `30-EDGE-FUNCTION-watchers-upsert.md`
- [ ] Deploy to Supabase B:

  ```bash
  supabase functions deploy watchers-upsert --project-ref <SUPABASE_B_REF>
  ```

- [ ] Set edge function env vars in Supabase B dashboard:
  - `SUPABASE_URL` = Supabase B URL
  - `SUPABASE_SERVICE_ROLE_KEY` = Supabase B service key
  - `WEBHOOK_SECRET` = Same secret used in webhook header

### Task 1.6: Enable pgmq Queues & pg_cron

- [ ] In Supabase B SQL Editor, verify queues exist:

  ```sql
  SELECT * FROM pgmq.list_queues();
  ```

  Should show: `ingest_indicators`, `compute_signals`, `compute_winrate`

- [ ] Create pg_cron job for win_rate recompute:

  ```sql
  SELECT cron.schedule(
    'recompute_winrate',
    '0 * * * *',  -- Every hour
    $$SELECT pgmq.send('compute_winrate', jsonb_build_object('symbol', symbol, 'timeframe', timeframe))
      FROM (SELECT DISTINCT symbol, timeframe FROM public.watchers WHERE active = true) AS active_watchers$$
  );
  ```

**✅ Day 1 Complete**: Infrastructure is ready for code deployment

---

## 🔷 Day 2: Core Implementation

### Task 2.1: Implement Orchestrator API Endpoints

- [ ] Create `/chat` endpoint (POST):
  - Verify JWT from Authorization header
  - Extract `user_id` from JWT
  - Fetch `user_symbols` from Supabase A
  - Fetch recent `signals` from Supabase B
  - Build context prompt
  - Route to LLM (Grok default)
  - Stream response to client
  - Calculate token usage
  - **Important**: Follow `40-ORCHESTRATOR-API.md` spec
- [ ] Create `/healthz` endpoint (GET):
  - Check Supabase A connectivity (simple SELECT 1)
  - Check Supabase B connectivity (simple SELECT 1)
  - Check Grok API reachability (test request)
  - Return 200 if all healthy, 503 if any fail

### Task 2.2: Implement Model Router

- [ ] Create model router logic:

  ```text
  IF user request mentions "tools" OR "analyze deeply":
    Try GPT first (better tool use)
  ELSE:
    Try Grok (default, faster, cheaper)

  IF any provider fails:
    Fallback to next: Grok → GPT → Claude

  IF all fail:
    Return error with retry suggestion
  ```

- [ ] Implement price caps per `60-CREDITS-PRICING.md`:
  - Fetch user's current credit balance from `A.credit_balance`
  - Calculate estimated cost before call
  - Reject if insufficient credits
  - Apply caps: max tokens per request based on user tier

### Task 2.3: Implement Credit Charging

- [ ] After every successful LLM call:

  ```sql
  INSERT INTO public.credits_ledger (user_id, delta, provider, units, reason)
  VALUES (
    $1,  -- user_id from JWT
    -$2,  -- negative delta (charge)
    $3,  -- 'grok' | 'gpt' | 'claude'
    jsonb_build_object('input_tokens', $4, 'output_tokens', $5),
    'chat_request'
  );
  ```

- [ ] Use formula from `60-CREDITS-PRICING.md`:

  ```javascript
  charge = ceil(
    (input_tokens / 1000) * input_per_1k +
    (output_tokens / 1000) * output_per_1k +
    min_call
  )
  ```

- [ ] Log credit transaction for audit trail

### Task 2.4: Implement Worker Consumers

- [ ] **Consumer 1**: `ingest_indicators`
  - Dequeue message from pgmq
  - Parse `{symbol, timeframe}` from message
  - Call Cryptometer API for indicators
  - Call KingFisher API for additional data
  - Write to `B.indicators` and `B.liq_clusters`
  - Enqueue `compute_signals` for same symbol
  - ACK message on success
- [ ] **Consumer 2**: `compute_signals`
  - Dequeue message from pgmq
  - Fetch latest indicators, risk_metric, liq_clusters
  - Apply trading strategy (combine 21 indicators)
  - Compute: direction (long/short/flat), score, entry, stop, targets
  - Check doubling guardrails (if applicable)
  - Write to `B.signals`
  - ACK message on success
- [ ] **Consumer 3**: `compute_winrate`
  - Dequeue message from pgmq
  - Fetch historical signals for symbol
  - Compare predicted direction vs actual price movement
  - Calculate win_rate % and sample_size
  - Write to `B.win_rate`
  - ACK message on success
- [ ] **Important**: Follow `41-ORCHESTRATOR-WORKER.md` spec

### Task 2.5: Frontend /chat Integration

- [ ] Create chat component in frontend:
  - Input field for user message
  - Send button
  - Chat history display
- [ ] Implement `/chat` API call:

  ```javascript
  const response = await fetch(`${ORCHESTRATOR_API_URL}/chat`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: userMessage, mode: 'text' })
  });

  // Handle streaming response
  const reader = response.body.getReader();
  // ... stream chunks to UI
  ```

- [ ] Optional: Add voice mode toggle:
  - If `mode: 'voice'`, expect `audioUrl` in response
  - Play audio using HTML5 `<audio>` element or Web Audio API

**✅ Day 2 Complete**: Core chat + signals flow operational

---

## 🔷 Day 3: Observability & Safety

### Task 3.1: Admin Dashboard

- [ ] Create admin page (protected route):
  - Show current queue depths:

    ```sql
    SELECT queue_name, COUNT(*) as depth
    FROM pgmq.q_<queue_name>
    GROUP BY queue_name;
    ```

  - Show pg_cron job status:

    ```sql
    SELECT * FROM cron.job_run_details
    ORDER BY start_time DESC LIMIT 10;
    ```

  - Show recent errors (from worker logs)
  - Show credits usage stats (top users, provider breakdown)

### Task 3.2: Add Request Caps

- [ ] Max rounds per request:
  - Track conversation turns
  - Limit to X turns per session (e.g., 10)
- [ ] Max tokens per request:
  - Set `max_tokens` param in LLM calls
  - Based on user tier: free=1024, pro=4096, enterprise=8192
- [ ] Price cap per request:
  - Calculate estimated cost before call
  - Reject if exceeds user's remaining credits
  - Reject if exceeds per-request limit (e.g., 100 credits max)

### Task 3.3: Risk Guardrails for Position Doubling

- [ ] Implement in `compute_signals` consumer:

  ```python
  # Check if doubling conditions met
  if new_score > previous_score + SCORE_DELTA_THRESHOLD:
      # Apply guardrails
      if current_position_size < MAX_POSITION_PCT * portfolio_value:
          if time_since_last_increase > COOLDOWN_SECONDS:
              volatility = fetch_risk_metric(symbol)
              if volatility < VOLATILITY_THRESHOLD:
                  # Safe to double
                  new_position_size = current_position_size * 2
              else:
                  # Too volatile, skip
                  pass
          else:
              # Cooldown active, skip
              pass
      else:
          # Max position reached, skip
          pass
  ```

- [ ] Make thresholds configurable via env vars:
  - `MAX_POSITION_PCT` (default: 0.1 = 10%)
  - `COOLDOWN_SECONDS` (default: 3600 = 1 hour)
  - `VOLATILITY_THRESHOLD` (default: 0.05 = 5%)
  - `SCORE_DELTA_THRESHOLD` (default: 0.1)

### Task 3.4: Logging & Monitoring

- [ ] Add structured logging to API:

  ```json
  {
    "timestamp": "2025-09-30T12:00:00Z",
    "level": "info",
    "service": "orchestrator-api",
    "endpoint": "/chat",
    "user_id": "abc123",
    "provider": "grok",
    "latency_ms": 523,
    "tokens": {"input": 150, "output": 300},
    "credits_charged": 5
  }
  ```

- [ ] Add structured logging to worker:

  ```json
  {
    "timestamp": "2025-09-30T12:00:00Z",
    "level": "info",
    "service": "orchestrator-worker",
    "queue": "compute_signals",
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "job_ms": 850,
    "queue_depth": 12
  }
  ```

- [ ] Set up alerts (via Render, Sentry, or similar):
  - Queue depth > 100
  - Error rate > 5%
  - `/healthz` failures

**✅ Day 3 Complete**: System is production-ready with observability & safety

---

## 📋 Post-Launch Tasks

### Performance Optimization

- [ ] Enable response caching for common queries
- [ ] Add rate limiting per user (e.g., 60 requests/min)
- [ ] Implement connection pooling for database clients
- [ ] Add CDN for static assets

### User Experience

- [ ] Add loading states in frontend
- [ ] Add error messages and retry buttons
- [ ] Show estimated credits cost before sending message
- [ ] Add voice mode with ElevenLabs integration

### Business Logic

- [ ] Create tier system (free, pro, enterprise)
- [ ] Implement credit top-up flow (Stripe integration)
- [ ] Add referral program (bonus credits)
- [ ] Implement usage analytics dashboard

### Advanced Features

- [ ] Multi-symbol analysis (compare BTC vs ETH)
- [ ] Portfolio management (track actual positions)
- [ ] Backtesting UI (simulate past trades)
- [ ] Email/SMS alerts for high-confidence signals

---

## ✅ Definition of Done

Each task is **complete** when:

1. Code is written and tested locally
2. Changes committed to git
3. Deployed to production (Render/Netlify)
4. Health check passing
5. Manual E2E test passed
6. No errors in logs for 5 minutes

---

## 🚨 Blockers & Dependencies

| Task | Depends On | Potential Blocker |
|------|------------|-------------------|
| 1.4 Webhook | 1.3 Schemas, 1.5 Edge Function | Webhook secret mismatch |
| 1.5 Edge Function | 1.3 Schemas | Missing env vars |
| 2.1 API /chat | 1.1 Services, 1.2 Env Vars | JWT verification failing |
| 2.4 Worker | 1.6 Queues, 2.1 API | Queue not created |
| 2.5 Frontend | 2.1 API /chat | CORS issues |

---

## 📞 Help & Resources

- **Architecture**: See `00-OVERVIEW.md`
- **API Spec**: See `40-ORCHESTRATOR-API.md`
- **Worker Spec**: See `41-ORCHESTRATOR-WORKER.md`
- **Schemas**: See `20-SCHEMA-SUPABASE-A.sql`, `21-SCHEMA-SUPABASE-B.sql`
- **Troubleshooting**: See `runbooks/ONCALL.md`

---

**Document Version**: 1.0.0
**Last Updated**: 2025-09-30
**Status**: Implementation Checklist Ready
