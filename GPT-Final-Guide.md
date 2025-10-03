# 🚀 GPT-Final-Guide: Cursor + Claude Code Blueprint System

**ZmartBot Development Guide for AI-Assisted Development**
**Last Updated**: 2025-09-30
**Status**: Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Blueprint Architecture](#blueprint-architecture)
3. [Setup Instructions](#setup-instructions)
4. [Using Claude Code with Cursor](#using-claude-code-with-cursor)
5. [Development Workflow](#development-workflow)
6. [Blueprint File Structure](#blueprint-file-structure)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This guide establishes a **blueprint-driven development workflow** for ZmartBot using Cursor IDE and Claude Code. The system provides:

- ✅ **Single Source of Truth**: All architectural decisions in one place
- ✅ **AI-Friendly Context**: Claude can reliably reference and follow specs
- ✅ **Safe Code Generation**: Reviewable diffs and controlled changes
- ✅ **No Authentication Issues**: Pre-configured Claude Code setup
- ✅ **Professional Workflow**: Senior-level discipline with AI assistance

---

## 🏗️ Blueprint Architecture

### System Overview

**Zmarty Control Plane Architecture:**

```bash
Frontend (Netlify)
    ↓
Orchestrator API (Render)
    ↓ ↙ ↘
Supabase A    Supabase B    External APIs
(Chat/Auth)   (Trading)     (Grok/GPT/Claude)
```

**Key Components:**

- **Frontend**: Netlify-hosted, calls Orchestrator API for chat + voice
- **Supabase A (Chat)**: Auth, profiles, tiers, credits_ledger, user_symbols
- **Supabase B (Trading)**: Watchers, indicators, signals, win_rate, risk metrics
- **Database Webhook**: A.user_symbols → B Edge Function `watchers-upsert`
- **Queues**: pgmq for async processing (indicators, signals, win_rate)
- **Schedules**: pg_cron for periodic recomputes
- **Render Services**:
  - `orchestrator-api`: JWT verify, model routing, credit charging
  - `orchestrator-worker`: Consumes queues, ingests data, computes signals
- **ElevenLabs**: Voice streaming for Zmarty responses
- **Guardrails**: Position doubling caps with risk constraints

---

## 🛠️ Setup Instructions

### Step 1: Create Blueprint Folder Structure

From your repo root, create the blueprint folder:

```bash
mkdir -p docs/zmarty-blueprint/runbooks docs/zmarty-blueprint/specs
```

### Step 2: Blueprint File Structure

Create these files in `docs/zmarty-blueprint/`:

```bash
docs/
└─ zmarty-blueprint/
   ├─ 00-OVERVIEW.md
   ├─ 10-TASKLIST.md
   ├─ 20-SCHEMA-SUPABASE-A.sql
   ├─ 21-SCHEMA-SUPABASE-B.sql
   ├─ 30-EDGE-FUNCTION-watchers-upsert.md
   ├─ 40-ORCHESTRATOR-API.md
   ├─ 41-ORCHESTRATOR-WORKER.md
   ├─ 50-ENV.sample
   ├─ 60-CREDITS-PRICING.md
   ├─ specs/
   │  └─ API-CONTRACTS.md
   └─ runbooks/
      └─ ONCALL.md
```

### Step 3: Claude Code Setup (No Authentication Issues)

We've already configured Claude Code to work seamlessly without password prompts or typing issues. Use this command:

```bash

# Use the pre-configured script (no authentication issues)

./cursor-claude.sh "your prompt here"

# Or use the alias (after terminal restart)

claude-cursor "your prompt here"
```

**Why This Works:**

- ✅ Bypasses interactive authentication
- ✅ No typing delays or errors
- ✅ Uses Claude Sonnet 4.5 (latest model)
- ✅ Optimized for Cursor IDE integration

---

## 📝 Blueprint File Contents

### 00-OVERVIEW.md

```markdown

# Zmarty Control Plane (High Level)

- **Frontend**: Netlify, calls Orchestrator API (Render) for chat + voice.
- **Supabase A (Chat)**: auth, profiles, tiers, credits_ledger, user_symbols.
- **Supabase B (Trading)**: watchers, indicators, risk_metric, liq_clusters, signals, win_rate.
- **Database Webhook**: A.user_symbols → B Edge Function `watchers-upsert`.
- **Queues**: B uses pgmq (ingest_indicators, compute_signals, compute_winrate).
- **Schedules**: pg_cron in B for periodic recomputes.
- **Render**:
  - orchestrator-api (web service): JWT verify with Supabase A, model router (Grok default; GPT & Claude tool/fallback), charge credits.
  - orchestrator-worker (background): consumes pgmq; ingests data; computes signals; updates win_rate.
- **ElevenLabs**: voice streaming for Zmarty responses.
- **Guardrails**: position "doubling" capped with risk constraints in worker.

```

### 10-TASKLIST.md

```markdown

# Minimal Tasks to Wire Everything

## Day 1
- [ ] Create Render services: orchestrator-api (web), orchestrator-worker (background).
- [ ] Set env vars in Render & Netlify (see 50-ENV.sample).
- [ ] Apply SQL in 20- and 21- files to Supabase A and B.
- [ ] In Supabase A: turn on Database Webhook for table `public.user_symbols` → URL to Supabase B edge function.
- [ ] In Supabase B: deploy edge function `watchers-upsert` with HMAC check.
- [ ] Enable pgmq queues + pg_cron in B; create queues and schedule win_rate recompute.

## Day 2
- [ ] Implement orchestrator-api endpoints: `/chat`, `/healthz`.
- [ ] Implement basic model router (Grok default; GPT/Claude fallback/cap).
- [ ] Implement credit charge on each call: insert into A.credits_ledger.
- [ ] Worker: consumers for `ingest_indicators`, `compute_signals`, `compute_winrate`.
- [ ] Frontend: connect to `/chat`, stream text; optional ElevenLabs voice.

## Day 3 (obs & safety)
- [ ] Admin page for queue depth, cron status, recent errors.
- [ ] Add caps: max rounds, max tokens, price cap per request.
- [ ] Add risk guardrails in "doubling" logic: max position %, cool-down.

```

### 20-SCHEMA-SUPABASE-A.sql

```sql
-- Supabase A: Zmarty Chat (auth, credits, user_symbols)
create table if not exists public.user_symbols (
  id bigserial primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  symbol text not null check (length(symbol) > 0),
  timeframe text not null default '1h',
  strategy jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  unique(user_id, symbol, timeframe)
);

create table if not exists public.credits_ledger (
  id bigserial primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  delta integer not null,
  provider text not null,            -- grok|gpt|claude|data
  units jsonb default '{}'::jsonb,   -- {input_tokens:..., output_tokens:...}
  reason text,
  created_at timestamptz default now()
);

create or replace view public.credit_balance as
select user_id, coalesce(sum(delta),0) as balance
from public.credits_ledger
group by 1;

-- RLS
alter table public.user_symbols enable row level security;
create policy "users manage only their symbols"
  on public.user_symbols for all to authenticated
  using (auth.uid() = user_id) with check (auth.uid() = user_id);

alter table public.credits_ledger enable row level security;
create policy "users read own credits"
  on public.credits_ledger for select to authenticated
  using (auth.uid() = user_id);
-- inserts to credits_ledger are done by service role (orchestrator-api)
```

### 21-SCHEMA-SUPABASE-B.sql

```sql
-- Supabase B: Zmart Trading (watchers, indicators, signals, win_rate)
create table if not exists public.watchers (
  id bigserial primary key,
  user_id uuid not null,
  symbol text not null,
  timeframe text not null,
  strategy jsonb default '{}'::jsonb,
  active boolean default true,
  created_at timestamptz default now(),
  unique(user_id, symbol, timeframe)
);

create table if not exists public.indicators (
  id bigserial primary key,
  symbol text not null,
  timeframe text not null,
  at timestamptz not null default now(),
  data jsonb not null,
  source text default 'cryptometer',
  unique(symbol, timeframe, at)
);

create table if not exists public.risk_metric (
  id bigserial primary key,
  symbol text not null,
  at timestamptz not null,
  metrics jsonb not null,
  unique(symbol, at)
);

create table if not exists public.liq_clusters (
  id bigserial primary key,
  symbol text not null,
  at timestamptz not null,
  clusters jsonb not null
);

create table if not exists public.signals (
  id bigserial primary key,
  symbol text not null,
  timeframe text not null,
  at timestamptz not null default now(),
  direction text check (direction in ('long','short','flat')),
  score numeric not null,
  entry_price numeric,
  stop_loss numeric,
  take_profit numeric[],
  confidence numeric,
  reasons jsonb,
  user_id uuid,
  strategy_version text default 'v1',
  unique(symbol, timeframe, at, coalesce(user_id, '00000000-0000-0000-0000-000000000000'::uuid))
);

create table if not exists public.win_rate (
  id bigserial primary key,
  symbol text not null,
  timeframe text not null,
  lookback_days int not null,
  win_rate numeric not null,
  sample_size int not null,
  params jsonb default '{}'::jsonb,
  computed_at timestamptz default now(),
  unique(symbol, timeframe, lookback_days, coalesce(params->>'strategy_version','v1'))
);

-- Queues & Cron
create extension if not exists pgmq;
select pgmq.create('ingest_indicators');
select pgmq.create('compute_signals');
select pgmq.create('compute_winrate');

create extension if not exists pg_cron;
```

### 30-EDGE-FUNCTION-watchers-upsert.md

```markdown

## Supabase B Edge Function: `watchers-upsert`

**Purpose**: Receives webhook from Supabase A on INSERT/UPDATE/DELETE of `user_symbols`.

**Responsibilities**:

- Verify HMAC in header `x-hmac-sha256`
- Upsert or delete `watchers` accordingly
- Respond "ok" within < 1s

**Deliverables**:

- `/supabase/trading/functions/watchers-upsert/index.ts` (Deno)
- Env in Function: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, WEBHOOK_SECRET

**Implementation**:
```typescript

// Verify HMAC signature
// Parse webhook payload
// Execute upsert/delete on watchers table
// Return 200 OK within timeout

```bash
```

### 40-ORCHESTRATOR-API.md

```markdown

## Render Service: orchestrator-api

**Type**: Web Service

**Responsibilities**:

- `POST /chat`: Verify Supabase A JWT; fetch A.user_symbols and B.signals; route to LLM (Grok default, GPT/Claude as needed); charge credits.
- `GET /healthz`: Check A/B connectivity + provider reachability.

**Environment Variables**:

- SUPABASE_A_URL, SUPABASE_A_SERVICE_KEY
- SUPABASE_B_URL, SUPABASE_B_SERVICE_KEY
- JWT_SECRET (for session auth if needed)
- ELEVENLABS_API_KEY, XAI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY

**Implementation Notes**:

- Price map: see 60-CREDITS-PRICING.md
- Always bound tokens + rounds per request using user tier
- Never expose service keys to client
- Stream responses for better UX

```

### 41-ORCHESTRATOR-WORKER.md

```markdown

## Render Service: orchestrator-worker

**Type**: Background Worker

**Responsibilities**:

- Consume pgmq queues:
  - `ingest_indicators`: Pull Cryptometer + KingFisher; write indicators/liq_clusters
  - `compute_signals`: Combine 21 indicators + risk + liq; compute direction/score; write signals
  - `compute_winrate`: Rollups into win_rate
- "Doubling on better score" policy with guardrails:
  - Max position %
  - Min time between raises
  - Volatility filter from risk_metric

**Implementation Notes**:

- Backoff & retry on API errors
- Emit concise logs for observability (symbol/timeframe/job ms, queue depth)
- Monitor queue depth and scale accordingly

```

### 50-ENV.sample

```bash

# Shared

NODE_ENV=production

# Supabase A (Chat)

SUPABASE_A_URL=
SUPABASE_A_SERVICE_KEY=

# Supabase B (Trading)

SUPABASE_B_URL=
SUPABASE_B_SERVICE_KEY=

# Webhook HMAC

WEBHOOK_SECRET=

# Providers

XAI_API_KEY=      # Grok
OPENAI_API_KEY=   # GPT
ANTHROPIC_API_KEY=# Claude
ELEVENLABS_API_KEY=

# Optional

JWT_SECRET=
```

### 60-CREDITS-PRICING.md

```markdown

# Credits Map

**Pricing per 1K tokens** (adjust to your economics):

| Provider | Input/1K | Output/1K | Min Call |
|----------|----------|-----------|----------|
| grok     | 1        | 4         | 1        |
| gpt      | 3        | 10        | 2        |
| claude   | 3        | 10        | 2        |
| data     | 1        | 0         | 1        |

**Charge Formula**:

```text
total_credits = ceil((input_tokens/1000) * input_per_1k +
                     (output_tokens/1000) * output_per_1k +
                     min_call)
```

### specs/API-CONTRACTS.md

```markdown

# API Contracts

## POST /chat

**Request**:
```json

{
  "jwt": "string",
  "message": "string",
  "mode": "text" | "voice"
}

```

**Response**:

```json
{
  "provider": "grok" | "gpt" | "claude",
  "usage": {
    "input_tokens": number,
    "output_tokens": number
  },
  "text": "string",
  "audioUrl": "string?"
}
```

## Webhook Payload A→B

**Format**: JSON

```json
{
  "op": "INSERT" | "UPDATE" | "DELETE",
  "row": {
    "user_id": "uuid",
    "symbol": "string",
    "timeframe": "string",
    "strategy": {}
  },
  "old": {
    "user_id": "uuid",
    "symbol": "string",
    "timeframe": "string"
  }
}
```

### runbooks/ONCALL.md

```markdown

# On-Call Runbook

## Checks if users report "no updates"

1. **Health Check**: `/healthz` returns 200?
2. **Queue Depth**: Supabase B queue depth (pgmq) < 100?
3. **Recent Signals**: Latest signal row within the last 5-10 minutes?
4. **Backlog High**:
   - Scale worker up
   - Check API rate limits
   - Review error logs

## Common Issues

- **Queue Backlog**: Scale orchestrator-worker
- **Slow Responses**: Check provider API limits
- **Missing Signals**: Verify cron jobs running
- **Credit Issues**: Check credits_ledger inserts

```

---

## 🎮 Using Claude Code with Cursor

### A. Set Up Context (Once Per Workspace)

1. **Open Cursor** in your ZmartBot repo
2. **Open Blueprint Files**:
   - `docs/zmarty-blueprint/00-OVERVIEW.md`
   - `docs/zmarty-blueprint/10-TASKLIST.md`
3. **Attach Blueprint Folder** to Cursor chat context:
   - In Cursor, use `@` to attach files/folders
   - Attach entire `docs/zmarty-blueprint/` folder
4. **Set AI Rules** (paste this in first chat message):

```bash
Rules for you (Claude):

1. Only create/edit files you list first.
2. Work in small PR-sized steps (≤ 8 files). Always show a diff.
3. Use the blueprint docs as the authoritative spec.
4. Never push service keys to the client.
5. After each step, print a brief test plan (describing how to run and verify).
6. If you're not sure, ask before touching unrelated files.

```

### B. Generate Code in Safe, Reviewable Chunks

Use the pre-configured Claude Code command for each prompt:

#### Prompt 1: Migrations

```bash
./cursor-claude.sh "Create migration files that apply 20-SCHEMA-SUPABASE-A.sql and 21-SCHEMA-SUPABASE-B.sql. Put them under /supabase/chat/migrations/ and /supabase/trading/migrations/. Do not change other files. Show the exact SQL content taken from the blueprint."
```

#### Prompt 2: Edge Function

```bash
./cursor-claude.sh "Generate Supabase B Edge Function watchers-upsert per 30-EDGE-FUNCTION-watchers-upsert.md. Create /supabase/trading/functions/watchers-upsert/index.ts with HMAC verification, upsert/delete logic, and a 1-second timeout budget. Show the full file."
```

#### Prompt 3: Render Services Scaffolding

```bash
./cursor-claude.sh "Scaffold two Node/TypeScript services: /services/orchestrator-api and /services/orchestrator-worker following 40-ORCHESTRATOR-API.md and 41-ORCHESTRATOR-WORKER.md. Use pnpm workspaces and TypeScript. Add minimal endpoints: /chat and /healthz. In the worker, add consumers for ingest_indicators, compute_signals, and compute_winrate with placeholder handlers. Read env from 50-ENV.sample. Output a diff and a short README for each service."
```

#### Prompt 4: Model Router + Credits

```bash
./cursor-claude.sh "Implement a simple model router: Grok default; GPT/Claude fallback when asked, with a price cap. After each call, write a row to Supabase A credits_ledger using the formula in 60-CREDITS-PRICING.md. Avoid sending service keys to the browser."
```

#### Prompt 5: Frontend Hook-up

```bash
./cursor-claude.sh "Add a small client in the frontend that hits /chat with a user JWT, streams text, and optionally fetches ElevenLabs audio if audioUrl is returned."
```

### C. Keep the Agent on a Tight Leash

**Always include these guidelines in your prompts**:

1. ✅ List files you'll touch first
2. ✅ Show diffs for review
3. ✅ Reference blueprint docs
4. ✅ Include test plan
5. ✅ Ask before major changes

---

## 🚀 Development Workflow

### First Local Run Sequence

1. **Apply Migrations**:

   ```bash
   # In Supabase SQL editor or CLI
   # Apply 20-SCHEMA-SUPABASE-A.sql to Supabase A
   # Apply 21-SCHEMA-SUPABASE-B.sql to Supabase B
   ```

2. **Deploy Edge Function**:

   ```bash
   # In Supabase B: deploy watchers-upsert
   # Set WEBHOOK_SECRET in function environment
   ```

3. **Configure Webhook**:

   ```bash
   # In Supabase A: Database Webhook
   # Table: public.user_symbols
   # URL: Supabase B function URL
   # Include HMAC header
   ```

4. **Deploy to Render**:

   ```bash
   # Deploy orchestrator-api (web service)
   # Deploy orchestrator-worker (background worker)
   # Set all envs from 50-ENV.sample
   ```

5. **Test the Flow**:

   ```bash
   # 1. Log in to app
   # 2. Add a symbol
   # 3. Verify it appears in B.watchers
   # 4. Start worker and enqueue test job
   # 5. Verify indicators written
   # 6. Call /chat from frontend
   # 7. Verify credits_ledger row in A
   ```

### Daily Development Loop

```bash

# 1. Plan with Claude

./cursor-claude.sh "List files I need to modify for [feature]. Reference the blueprint."

# 2. Generate code

./cursor-claude.sh "Implement [feature] following the plan. Show diffs only."

# 3. Review diffs in Cursor
# Accept/reject changes using Cursor's diff UI

# 4. Test

./cursor-claude.sh "Create a test plan for [feature]"

# 5. Commit

git add .
git commit -m "feat: [feature] per blueprint"
```

---

## 🎯 Best Practices

### For Productive Sessions

1. **Pin the Blueprint**: Always attach `docs/zmarty-blueprint/` to new chats
2. **Plan First**: Ask "list files you'll touch and why", then accept
3. **Small Commits**: One subsystem at a time (migrations → edge fn → worker → API → UI)
4. **Test Each Step**: Run the test plan Claude proposes after each change
5. **Reference Verbatim**: If Claude wavers, paste relevant blueprint section

### Quality Gates

Before pushing code:

- ✅ All files listed in plan were modified
- ✅ Diffs reviewed and approved
- ✅ Test plan executed successfully
- ✅ No service keys exposed to client
- ✅ Blueprint docs still accurate

### When Things Go Wrong

```bash

# If Claude makes unwanted changes:

git checkout -- <file>

# If you need to reset context:
# 1. Close Cursor chat
# 2. Re-attach blueprint folder
# 3. Paste house rules again

# If authentication issues return:

./cursor-claude.sh "Test basic functionality"

# Should work without password prompts
```

---

## 🔧 Troubleshooting

### Claude Code Issues

**Problem**: Password prompts or typing slowness

**Solution**: Use the pre-configured script

```bash
./cursor-claude.sh "your prompt"
```

**Why it works**:

- Bypasses interactive authentication
- Uses non-interactive mode
- No raw mode errors
- Optimized for Cursor

### Blueprint Issues

**Problem**: Claude not following blueprint

**Solution**:

1. Re-attach blueprint folder to context
2. Say: "Follow docs/zmarty-blueprint/[specific-file].md verbatim"
3. Quote the exact section from blueprint

**Problem**: Can't find blueprint files

**Solution**:

```bash

# Verify structure

ls -la docs/zmarty-blueprint/

# Recreate if missing

mkdir -p docs/zmarty-blueprint/runbooks docs/zmarty-blueprint/specs
```

### Development Issues

**Problem**: Services not starting

**Solution**:

```bash

# Check health

curl http://localhost:PORT/healthz

# Check logs

./cursor-claude.sh "Analyze the error logs and suggest fixes"
```

**Problem**: Queue backlog building up

**Solution**:

```bash

# Scale worker

./cursor-claude.sh "How do I scale orchestrator-worker on Render?"
```

---

## 📚 Quick Reference

### Essential Commands

```bash

# Use Claude Code (no auth issues)

./cursor-claude.sh "your prompt"

# Or with alias (after terminal restart)

claude-cursor "your prompt"

# Check Claude version

claude --version

# Verify setup

./cursor-claude.sh "Test basic functionality"
```

### File Locations

- **Blueprint**: `docs/zmarty-blueprint/`
- **Claude Script**: `./cursor-claude.sh`
- **Alias**: `claude-cursor` (in `~/.zshrc`)
- **Config**: `.cursor-claude-config.json`

### Support Resources

- **Blueprint Docs**: `docs/zmarty-blueprint/00-OVERVIEW.md`
- **API Contracts**: `docs/zmarty-blueprint/specs/API-CONTRACTS.md`
- **Runbook**: `docs/zmarty-blueprint/runbooks/ONCALL.md`
- **This Guide**: `GPT-Final-Guide.md`

---

## 🎉 Conclusion

You now have a **professional, blueprint-driven development system** that combines:

- ✅ **Claude Sonnet 4.5**: Latest AI model for code generation
- ✅ **No Authentication Issues**: Pre-configured, optimized setup
- ✅ **Single Source of Truth**: Blueprint docs for all architectural decisions
- ✅ **Safe Code Generation**: Reviewable diffs and controlled changes
- ✅ **Senior-Level Discipline**: Plan → Diff → Test → Commit workflow

**Next Steps**:

1. Create the blueprint folder structure
2. Fill in the blueprint files
3. Start using `./cursor-claude.sh` for development
4. Follow the small-PR workflow
5. Keep commits clean and reviewable

**Happy Coding! 🚀**

---

**Document Version**: 1.0.0
**Last Updated**: 2025-09-30
**Author**: ZmartBot Development Team
**Status**: Production Ready


