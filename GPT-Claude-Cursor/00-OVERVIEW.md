# Zmarty Control Plane (High Level)

## System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Netlify)                       │
│                 React + Chat + Voice UI                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓ HTTPS + JWT
┌─────────────────────────────────────────────────────────────┐
│              Orchestrator API (Render)                       │
│   JWT Verify │ Model Router │ Credit Charging               │
└─────┬────────────────┬────────────────┬─────────────────────┘
      │                │                │
      ↓                ↓                ↓
┌──────────┐    ┌──────────┐    ┌────────────────────┐
│Supabase A│    │Supabase B│    │ LLM Providers      │
│  (Chat)  │    │ (Trading)│    │ • Grok (default)   │
│          │    │          │    │ • GPT (fallback)   │
│          │    │          │    │ • Claude (fallback)│
└──────────┘    └──────────┘    └────────────────────┘
      │                │
      │ Webhook        │ pgmq Queues
      │                │ pg_cron Jobs
      └────────┬───────┘
               ↓
    ┌────────────────────────┐
    │ Orchestrator Worker    │
    │      (Render)          │
    │ • Ingest Indicators    │
    │ • Compute Signals      │
    │ • Compute Win Rate     │
    └────────────────────────┘

```

---

## Component Breakdown

### **Frontend** (Netlify)

- **Technology**: React/Next.js
- **Features**:
  - User authentication (Supabase Auth)
  - Chat interface with Zmarty AI
  - Voice streaming (ElevenLabs)
  - Symbol management UI
  - Credits display
- **Communication**: Calls Orchestrator API via HTTPS with JWT tokens

---

### **Supabase A** (Chat Database)

- **Purpose**: Authentication, user management, credits tracking
- **Tables**:
  - `auth.users` - User accounts
  - `public.profiles` - User profiles and tier information
  - `public.user_symbols` - User's watched trading symbols
  - `public.credits_ledger` - All credit transactions
- **Views**:
  - `public.credit_balance` - Current credit balance per user
- **Features**:
  - Row Level Security (RLS) enabled
  - Database webhooks to Supabase B
  - JWT token generation

---

### **Supabase B** (Trading Database)

- **Purpose**: Trading data, signals, indicators, risk metrics
- **Tables**:
  - `public.watchers` - Active symbol watchers (synced from A)
  - `public.indicators` - Technical indicators data
  - `public.risk_metric` - Risk assessment data
  - `public.liq_clusters` - Liquidation cluster analysis
  - `public.signals` - Trading signals (long/short/flat)
  - `public.win_rate` - Historical win rate statistics
- **Extensions**:
  - `pgmq` - Message queues for async processing
  - `pg_cron` - Scheduled jobs for periodic recomputes
- **Queues**:
  - `ingest_indicators` - Data ingestion queue
  - `compute_signals` - Signal generation queue
  - `compute_winrate` - Win rate calculation queue

---

### **Database Webhook** (A → B)

- **Trigger**: INSERT/UPDATE/DELETE on `A.user_symbols`
- **Target**: Supabase B Edge Function `watchers-upsert`
- **Purpose**: Keep `B.watchers` in sync with user's symbol selections
- **Security**: HMAC signature verification (`x-hmac-sha256` header)
- **Response Time**: < 1 second

---

### **Orchestrator API** (Render Web Service)

- **Port**: 8080 (or assigned by Render)
- **Responsibilities**:
  1. **JWT Verification**: Validates tokens from Supabase A
  2. **Context Gathering**: Fetches user symbols from A, recent signals from B
  3. **Model Router**:
     - **Default**: Grok (XAI API) - fastest, cost-effective
     - **Fallback**: GPT (OpenAI) - when Grok unavailable or tool use needed
     - **Fallback**: Claude (Anthropic) - for complex reasoning or when others fail
  4. **Credit Charging**: Inserts transaction to `A.credits_ledger` after each call
  5. **Response Streaming**: Streams text responses to frontend
  6. **Voice Generation**: Optional ElevenLabs voice synthesis
- **Endpoints**:
  - `POST /chat` - Main chat endpoint
  - `GET /healthz` - Health check (A/B connectivity + provider status)
- **Environment Variables**: See `50-ENV.sample`

---

### **Orchestrator Worker** (Render Background Worker)

- **Type**: Long-running background process
- **Responsibilities**:
  1. **Ingest Indicators** (consumer: `ingest_indicators` queue):
     - Polls Cryptometer API for technical indicators
     - Polls KingFisher API for additional data
     - Writes to `B.indicators` and `B.liq_clusters`
  2. **Compute Signals** (consumer: `compute_signals` queue):
     - Combines 21 indicators + risk metrics + liquidation clusters
     - Applies trading strategy logic
     - Computes direction (long/short/flat), score, entry/exit prices
     - Writes to `B.signals`
  3. **Compute Win Rate** (consumer: `compute_winrate` queue):
     - Analyzes historical signals vs actual outcomes
     - Calculates win rate percentages
     - Writes rollups to `B.win_rate`
- **Features**:
  - Backoff & retry on API errors
  - Concise logging (symbol/timeframe/job_ms, queue_depth)
  - Observability metrics

---

### **Position "Doubling" with Guardrails**

- **Concept**: Increase position size when signal confidence improves
- **Guardrails**:
  1. **Max Position %**: Never exceed X% of portfolio (configurable)
  2. **Cooldown Period**: Minimum time between position increases
  3. **Volatility Filter**: Check `risk_metric.volatility` before doubling
  4. **Score Threshold**: Only double if new score > previous + delta
- **Implementation**: In `orchestrator-worker` signal computation logic

---

### **LLM Providers**

1. **Grok (XAI)** - Default
   - Fastest response time
   - Lower cost per token
   - Good for general chat
2. **GPT (OpenAI)** - Fallback/Tool Use
   - Better tool/function calling
   - Used when specific tools needed
   - Higher accuracy for complex queries
3. **Claude (Anthropic)** - Advanced Reasoning
   - Best for complex analysis
   - Used when Grok/GPT insufficient
   - Highest quality, highest cost

---

### **ElevenLabs Voice**

- **Purpose**: Voice synthesis for Zmarty responses
- **Flow**:
  1. User enables voice mode in frontend
  2. Orchestrator API generates text response
  3. Text sent to ElevenLabs API
  4. Returns audio stream URL
  5. Frontend plays audio
- **Caching**: Consider caching common responses

---

## Data Flow Examples

### **User Adds Symbol**

```text
1. User clicks "Add BTC/USDT" in Frontend
2. Frontend → POST to Supabase A.user_symbols (with JWT)
3. Supabase A RLS validates user_id = auth.uid()
4. Row inserted into A.user_symbols
5. Webhook fires → Supabase B Edge Function
6. Edge Function → Upserts B.watchers
7. pg_cron job (every 5min) → Enqueues ingest_indicators
8. Worker consumes queue → Fetches indicators → Writes B.indicators
9. Worker → Enqueues compute_signals
10. Worker consumes queue → Generates signal → Writes B.signals

```

### **User Asks Chat Question**

```text
1. User types "What's the signal for BTC?" in chat
2. Frontend → POST /chat (with JWT + message)
3. Orchestrator API:

   a. Verifies JWT with Supabase A
   b. Fetches A.user_symbols (user's watched symbols)
   c. Fetches B.signals (recent signals for those symbols)
   d. Constructs prompt with context
   e. Routes to Grok (default)
   f. Streams response to frontend
   g. Calculates token usage
   h. Inserts A.credits_ledger (charge credits)

4. Frontend displays response (text or voice)

```

### **Periodic Win Rate Recompute**

```text
1. pg_cron job runs (e.g., hourly)
2. Enqueues compute_winrate for each active symbol
3. Worker consumes queue:

   a. Fetches historical B.signals
   b. Compares predicted direction vs actual price movement
   c. Calculates win rate %
   d. Writes to B.win_rate

4. Next chat query includes updated win rate in context

```

---

## Key Design Decisions

### **Why Two Supabase Instances?**

- **Supabase A (Chat)**: User-facing, auth, billing → needs RLS, user isolation
- **Supabase B (Trading)**: Service-facing, heavy data processing → needs pgmq, pg_cron
- **Separation of Concerns**: Auth/billing logic separate from trading logic

### **Why Grok Default?**

- **Cost-Effective**: Lower token costs for high-volume chat
- **Fast**: Responds quickly for better UX
- **Sufficient**: Handles 80% of queries adequately
- **Fallbacks**: GPT/Claude available when needed

### **Why Message Queues (pgmq)?**

- **Async Processing**: Don't block user requests
- **Reliability**: Retry failed jobs automatically
- **Scalability**: Can scale worker independently
- **Visibility**: Monitor queue depth for backlog alerts

### **Why pg_cron?**

- **Scheduled Jobs**: Periodic recomputes without external scheduler
- **Database-Native**: No need for separate cron service
- **Reliability**: Runs even if worker restarts

---

## Security Model

### **Authentication Flow**

```bash

1. User logs in → Supabase A generates JWT
2. Frontend stores JWT (localStorage/cookie)
3. Frontend sends JWT with every request
4. Orchestrator API verifies JWT signature
5. Extracts user_id from JWT
6. Uses service_role_key for A/B database queries

```text

### **API Key Management**

- **Never** expose service role keys to frontend
- **Always** verify JWT before processing
- **Always** use RLS policies in Supabase A
- **Rotate** API keys periodically

### **Webhook Security**

- **HMAC Verification**: Required for A→B webhooks
- **Secret Key**: Shared between A and B
- **Timeout**: Reject requests > 1 second old

---

## Scaling Considerations

### **High User Load**

- **Frontend**: Netlify CDN handles this automatically
- **Orchestrator API**: Scale horizontally on Render
- **Supabase**: Both A and B auto-scale

### **High Data Volume**

- **Orchestrator Worker**: Scale up instance size or add more workers
- **Queue Monitoring**: Alert if depth > 100
- **Batch Processing**: Process multiple symbols per job

### **Cost Optimization**

- **Cache**: Cache common queries and responses
- **Rate Limiting**: Limit requests per user per minute
- **Tier System**: Free tier (limited credits), paid tiers (more credits)

---

## Monitoring & Observability

### **Health Checks**

- `/healthz` endpoint checks:
  - Supabase A connectivity
  - Supabase B connectivity
  - Grok API reachability
  - Queue depth < threshold

### **Key Metrics**

- Request latency (p50, p95, p99)
- Error rate per endpoint
- Queue depth per queue
- Credits charged per provider
- Win rate accuracy

### **Alerts**

- Queue depth > 100
- Error rate > 5%
- Health check failures
- Provider API errors

---

## Next Steps

1. **Review** `10-TASKLIST.md` for implementation order
2. **Apply** schemas from `20-*.sql` files
3. **Implement** edge function per `30-*.md`
4. **Build** services per `40-*.md` and `41-*.md`
5. **Configure** environment per `50-ENV.sample`
6. **Test** end-to-end flow

---

**Document Version**: 1.0.0
**Last Updated**: 2025-09-30
**Status**: Architecture Definition Complete
