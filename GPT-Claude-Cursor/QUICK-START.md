# 🚀 Quick Start Guide

## Get started with the GPT-Claude-Cursor Blueprint System in 5 minutes

---

## ✅ Prerequisites

You already have:

- ✅ Claude Code installed (v2.0.1 with Sonnet 4.5)
- ✅ Cursor IDE installed
- ✅ No authentication issues (using `./cursor-claude.sh`)
- ✅ Blueprint folder created (`GPT-Claude-Cursor/`)

---

## 🎯 Step 1: Test Claude Code

Verify everything works:

```bash
./cursor-claude.sh "Test the setup - read GPT-Claude-Cursor/README.md and summarize it"
```

**Expected**: Claude reads the README and gives you a summary without asking for passwords.

---

## 🎯 Step 2: Open Cursor with Blueprint Context

### Option A: Using Cursor IDE

1. **Open Cursor** in your ZmartBot project
2. **Open Chat Panel** (Cmd+L or Ctrl+L)
3. **Attach Blueprint Folder**:
   - Type `@GPT-Claude-Cursor`
   - Or click **+ Add Context** → Browse → Select `GPT-Claude-Cursor/` folder
4. **Paste House Rules** in first message:

```bash
Rules for you (Claude):
1. Only create/edit files you list first.
2. Work in small PR-sized steps (≤ 8 files). Always show a diff.
3. Use the GPT-Claude-Cursor docs as the authoritative spec.
4. Never push service keys to the client.
5. After each step, print a brief test plan (describing how to run and verify).
6. If you're not sure, ask before touching unrelated files.

Now read GPT-Claude-Cursor/00-OVERVIEW.md and 10-TASKLIST.md and tell me what we should build first.
```

### Option B: Using Command Line

```bash
./cursor-claude.sh "Read GPT-Claude-Cursor/00-OVERVIEW.md and GPT-Claude-Cursor/10-TASKLIST.md. List the Day 1 tasks and suggest which one to start with."
```

---

## 🎯 Step 3: Start Building (Example Workflow)

### Task: Create Database Migrations

```bash
./cursor-claude.sh "Create migration files for Supabase A and B using 20-SCHEMA-SUPABASE-A.sql and 21-SCHEMA-SUPABASE-B.sql. Put them in supabase/chat/migrations/ and supabase/trading/migrations/. Show me the file structure you'll create first."
```

**Claude will respond with**:

- List of files to create
- Ask for confirmation

**You say**: "Yes, proceed"

**Claude will**:

- Create the migration files
- Show you diffs
- Provide a test plan

---

### Task: Create Edge Function

```bash
./cursor-claude.sh "Create the watchers-upsert edge function following 30-EDGE-FUNCTION-watchers-upsert.md. Show me the code first before creating files."
```

---

### Task: Scaffold Orchestrator Services

```bash
./cursor-claude.sh "Scaffold orchestrator-api and orchestrator-worker services following 40-ORCHESTRATOR-API.md and 41-ORCHESTRATOR-WORKER.md. Use TypeScript with pnpm workspaces. List files you'll create first."
```

---

## 🎯 Step 4: Review & Accept Changes

### In Cursor IDE

1. Claude shows you a **diff view**
2. **Review each change** carefully
3. **Accept**✅ or**Reject** ❌ individual changes
4. **Commit** accepted changes to git

### Via Command Line

1. Claude creates files
2. **Review** using `git diff`
3. **Test** using Claude's test plan
4. **Commit** if all looks good

---

## 🎯 Step 5: Test Your Changes

Use Claude to create test plans:

```bash
./cursor-claude.sh "Create a test plan for the migrations I just applied. Include SQL queries to verify tables, indexes, and RLS policies."
```

Run the tests Claude suggests.

---

## 💡 Pro Tips

### Tip 1: Always Get a Plan First

```bash
# Good approach:
./cursor-claude.sh "Plan: How should I implement the /chat endpoint? List files to create/modify."

# Claude gives plan → You approve → Claude implements
```

### Tip 2: Work in Small Chunks

```bash
# Day 1, Task 1.3a: Just create tables
./cursor-claude.sh "Apply only the table creation part of 20-SCHEMA-SUPABASE-A.sql. Skip RLS policies for now."

# Day 1, Task 1.3b: Add RLS policies
./cursor-claude.sh "Now add RLS policies from 20-SCHEMA-SUPABASE-A.sql."
```

### Tip 3: Reference Blueprint Files

```bash
# Always mention specific blueprint files:
./cursor-claude.sh "Follow GPT-Claude-Cursor/40-ORCHESTRATOR-API.md exactly to implement /chat endpoint."
```

### Tip 4: Ask for Test Plans

```bash
./cursor-claude.sh "Create a test plan for the edge function. Include curl commands and expected responses."
```

### Tip 5: Use Diffs for Review

In Cursor chat:

```bash
"Show me a diff of the changes you'll make to [file] before applying them."
```

---

## 🎨 Example Session

### Full Example: Implementing Day 1 Tasks

```bash
# Task 1.3: Apply schemas
./cursor-claude.sh "Read 20-SCHEMA-SUPABASE-A.sql. Create a migration file in supabase/chat/migrations/001_initial_schema.sql with this exact content. List the file you'll create first."

# Claude responds with plan → You approve

# Test the migration
./cursor-claude.sh "Create a test script to verify the migration applied correctly. Check for: tables exist, indexes exist, RLS enabled, triggers work."

# Task 1.5: Create edge function
./cursor-claude.sh "Create supabase/trading/functions/watchers-upsert/index.ts following 30-EDGE-FUNCTION-watchers-upsert.md. Show me the code first."

# Claude shows code → You review → Approve

# Test edge function
./cursor-claude.sh "Create a curl test for the edge function. Include HMAC signature generation."

# And so on...
```

---

## 🔄 Iterative Development

If Claude makes a mistake:

```bash
# Ask Claude to fix it:
./cursor-claude.sh "The edge function returned 401. Check the HMAC verification logic against 30-EDGE-FUNCTION-watchers-upsert.md and fix it."

# Or revert and try again:
git checkout -- supabase/trading/functions/watchers-upsert/index.ts

./cursor-claude.sh "Try again: create watchers-upsert following the spec exactly. Pay attention to HMAC signature verification."
```

---

## 📚 Useful Claude Prompts

### Planning

```bash
./cursor-claude.sh "Read 10-TASKLIST.md and suggest which tasks to do today based on priorities."
```

### Code Review

```bash
./cursor-claude.sh "Review my implementation of /chat endpoint against 40-ORCHESTRATOR-API.md. List any deviations."
```

### Documentation

```bash
./cursor-claude.sh "Read my code in services/orchestrator-api/ and check if it matches the blueprint. Update the blueprint if needed."
```

### Debugging

```bash
./cursor-claude.sh "The webhook is returning 401. Debug the HMAC signature verification in watchers-upsert edge function."
```

### Testing

```bash
./cursor-claude.sh "Create a comprehensive test suite for the orchestrator-api /chat endpoint. Include unit tests and integration tests."
```

---

## 🎓 Learning Path

### Week 1: Foundation

1. Day 1-2: Database schemas and migrations
2. Day 3-4: Edge functions and webhooks
3. Day 5: Queues and cron jobs

### Week 2: Services

1. Day 6-8: Orchestrator API
2. Day 9-10: Orchestrator Worker
3. Day 11-12: Frontend integration

### Week 3: Polish

1. Day 13-14: Testing and monitoring
2. Day 15-16: Guardrails and safety
3. Day 17-18: Documentation and deployment

---

## 🚀 You're Ready

Start with:

```bash
./cursor-claude.sh "I want to start implementing the Zmarty platform. Read all files in GPT-Claude-Cursor/ and suggest the best starting point for Day 1."
```

## Happy Building

---

**Document Version**: 1.0.0
**Last Updated**: 2025-09-30
**Status**: Quick Start Complete
