# 📚 Blueprint Index

**Complete Documentation Index for GPT-Claude-Cursor Blueprint System**

---

## 📖 Core Documentation (Read in Order)

| # | File | Purpose | Start Here |
|---|------|---------|------------|
| 1 | **[README.md](README.md)**| Overview + Getting Started | ⭐**YES** |
| 2 | **[QUICK-START.md](QUICK-START.md)**| 5-minute setup guide | ⭐**YES** |
| 3 | **[00-OVERVIEW.md](00-OVERVIEW.md)** | System architecture | Read 3rd |
| 4 | **[10-TASKLIST.md](10-TASKLIST.md)** | Implementation checklist | Read 4th |

---

## 🗄️ Database & Infrastructure

| # | File | Purpose | Size |
|---|------|---------|------|
| 5 | **[20-SCHEMA-SUPABASE-A.sql](20-SCHEMA-SUPABASE-A.sql)** | Chat/Auth database schema | ~9.5 KB |
| 6 | **[21-SCHEMA-SUPABASE-B.sql](21-SCHEMA-SUPABASE-B.sql)** | Trading database schema | ~13 KB |
| 7 | **[30-EDGE-FUNCTION-watchers-upsert.md](30-EDGE-FUNCTION-watchers-upsert.md)** | Database sync webhook | ~10 KB |

---

## ⚙️ Services Implementation

| # | File | Purpose | Size |
|---|------|---------|------|
| 8 | **[40-ORCHESTRATOR-API.md](40-ORCHESTRATOR-API.md)** | Web service spec | ~11 KB |
| 9 | **[41-ORCHESTRATOR-WORKER.md](41-ORCHESTRATOR-WORKER.md)** | Background worker spec | ~13 KB |

---

## 🔧 Configuration & Operations

| # | File | Purpose | Size |
|---|------|---------|------|
| 10 | **[50-ENV.sample](50-ENV.sample)** | Environment variables template | ~8 KB |
| 11 | **[60-CREDITS-PRICING.md](60-CREDITS-PRICING.md)** | Pricing model & formulas | ~9 KB |

---

## 📋 Specifications

| # | File | Purpose | Size |
|---|------|---------|------|
| 12 | **[specs/API-CONTRACTS.md](specs/API-CONTRACTS.md)** | API request/response formats | ~9.5 KB |

---

## 🛠️ Operations

| # | File | Purpose | Size |
|---|------|---------|------|
| 13 | **[runbooks/ONCALL.md](runbooks/ONCALL.md)** | Production troubleshooting | ~9.7 KB |

---

## 📂 Total Documentation

- **Total Files**: 13 documents
- **Total Size**: ~120 KB
- **Coverage**: Complete system specification
- **Status**: Production Ready

---

## 🎯 Read Order by Use Case

### For Developers (Implementing Features)

1. `README.md` - Understand the system
2. `QUICK-START.md` - Set up your environment
3. `00-OVERVIEW.md` - Learn architecture
4. `10-TASKLIST.md` - See what to build
5. `40-ORCHESTRATOR-API.md` or `41-ORCHESTRATOR-WORKER.md` - Implement
6. `specs/API-CONTRACTS.md` - Follow API formats

### For DevOps (Deploying)

1. `README.md` - Understand the system
2. `50-ENV.sample` - Set environment variables
3. `20-SCHEMA-SUPABASE-A.sql` - Apply to Supabase A
4. `21-SCHEMA-SUPABASE-B.sql` - Apply to Supabase B
5. `30-EDGE-FUNCTION-watchers-upsert.md` - Deploy edge function
6. `runbooks/ONCALL.md` - Bookmark for incidents

### For Product (Understanding Features)

1. `README.md` - System overview
2. `00-OVERVIEW.md` - Architecture
3. `60-CREDITS-PRICING.md` - Business model
4. `10-TASKLIST.md` - Implementation timeline

### For Support (Troubleshooting)

1. `runbooks/ONCALL.md` - Start here!
2. `00-OVERVIEW.md` - Understand data flow
3. `specs/API-CONTRACTS.md` - Check API formats
4. `40-ORCHESTRATOR-API.md` - Understand API behavior

---

## 🔍 Quick Lookup

### Finding Information

**Q: How do credits work?**
→ `60-CREDITS-PRICING.md`

**Q: What's the database schema?**
→ `20-SCHEMA-SUPABASE-A.sql` (Chat) or `21-SCHEMA-SUPABASE-B.sql` (Trading)

**Q: How do I implement /chat endpoint?**
→ `40-ORCHESTRATOR-API.md` + `specs/API-CONTRACTS.md`

**Q: How do workers process data?**
→ `41-ORCHESTRATOR-WORKER.md`

**Q: What environment variables do I need?**
→ `50-ENV.sample`

**Q: How do I deploy the edge function?**
→ `30-EDGE-FUNCTION-watchers-upsert.md`

**Q: Users report stale signals, what do I do?**
→ `runbooks/ONCALL.md` → "No Updates" section

**Q: What are the API request/response formats?**
→ `specs/API-CONTRACTS.md`

**Q: What should I build first?**
→ `10-TASKLIST.md` → Day 1 tasks

**Q: How does the whole system fit together?**
→ `00-OVERVIEW.md` → Architecture diagrams

---

## 💻 Using with Claude Code

### Basic Usage

```bash

# Ask Claude to read a specific file

./cursor-claude.sh "Read GPT-Claude-Cursor/40-ORCHESTRATOR-API.md and implement the /chat endpoint"

# Ask Claude for implementation plan

./cursor-claude.sh "Read 10-TASKLIST.md and create a detailed plan for Day 1 tasks"

# Ask Claude to review code

./cursor-claude.sh "Review my /chat endpoint implementation against 40-ORCHESTRATOR-API.md"
```

### Advanced Usage

```bash

# Multi-file context

./cursor-claude.sh "Read 00-OVERVIEW.md, 40-ORCHESTRATOR-API.md, and 60-CREDITS-PRICING.md. Implement the credit charging logic with proper error handling."

# Architecture decisions

./cursor-claude.sh "Read 00-OVERVIEW.md and explain why we use two separate Supabase instances instead of one"

# Troubleshooting

./cursor-claude.sh "Read runbooks/ONCALL.md and help me debug why signals are stale"
```

---

## 🔄 Keeping Blueprint Updated

### When to Update

Update blueprint files when:

- ✅ Architecture changes (update `00-OVERVIEW.md`)
- ✅ New tables/columns added (update `20-*.sql` or `21-*.sql`)
- ✅ API contracts change (update `specs/API-CONTRACTS.md`)
- ✅ New environment variables (update `50-ENV.sample`)
- ✅ Pricing changes (update `60-CREDITS-PRICING.md`)
- ✅ New tasks/features (update `10-TASKLIST.md`)

### Update Process

1. **Make changes** to relevant blueprint file
2. **Document reason** in commit message
3. **Notify team** via Slack/PR
4. **Update version** in file footer (1.0.0 → 1.0.1)
5. **Regenerate if needed** (e.g., migrations from schema)

---

## 📊 Documentation Stats

### By Category

| Category | Files | Total Size | % of Total |
|----------|-------|------------|------------|
| **Core Docs** | 4 | ~38 KB | 32% |
| **Schemas** | 2 | ~23 KB | 19% |
| **Services** | 3 | ~35 KB | 29% |
| **Config** | 2 | ~17 KB | 14% |
| **Specs** | 1 | ~9.5 KB | 8% |
| **Runbooks** | 1 | ~9.7 KB | 8% |

### Completeness

- ✅ **Architecture**: 100% documented
- ✅ **Database**: 100% schema defined
- ✅ **APIs**: 100% contracts specified
- ✅ **Services**: 100% implementation guides
- ✅ **Operations**: 100% runbooks provided
- ✅ **Configuration**: 100% env vars templated

---

## 🎉 Ready to Build!

You have **everything you need** to build the Zmarty platform with AI assistance:

1. **Complete specifications** for all components
2. **Working Claude Code setup** (no auth issues!)
3. **Step-by-step guides** for implementation
4. **Operational runbooks** for production support
5. **API contracts** for frontend/backend integration

### Start Building Now

```bash
./cursor-claude.sh "I'm ready to start implementing Zmarty. Read 10-TASKLIST.md and let's begin with Day 1, Task 1.1: Create Render services. What do I need to do?"
```

**Happy Building! 🚀**

---

**Index Version**: 1.0.0
**Last Updated**: 2025-09-30
**Total Documentation**: 13 files, ~120 KB
**Status**: Complete & Ready



