
Zmart Trading Bot Platform: Project Architecture Guide for Manus

---

### Scoring Agent Orchestration Flow

... [previous content remains unchanged] ...

---

### Smart Contract Vault Join Handler

... [previous section unchanged] ...

---

### Blog Auto-Publish for Monthly Summaries

... [previous section unchanged] ...

---

### Signal Debug Console for Rejected Signals

... [previous section remains unchanged] ...

---

### Vault Liquidity Tier Analytics

... [previous section remains unchanged] ...

---

### User Share Distribution Visualizer

... [previous section remains unchanged] ...

---

### Signal Confidence Heatmap UI

... [previous section remains unchanged] ...

---

### User Signal Subscription Controls

... [previous section remains unchanged] ...

---

### Main Dashboard & Card Design (Dark Theme UI)

... [previous section remains unchanged] ...

---

### Custom Token Branding Engine

... [previous section remains unchanged] ...

---

### Paper Trading & Live Trading Console

... [previous section remains unchanged] ...

---

### Trade Dispute & Conflict Resolution Engine

... [previous section remains unchanged] ...

---

### Dynamic Strategy Simulator

... [previous section remains unchanged] ...

---

### AI Signal Explainability Panel

... [previous section remains unchanged] ...

---

### Live Trade Tracker with Geo Map

... [previous section remains unchanged] ...

---

### Zmart Risk Guard (Circuit Breaker Agent)

... [previous section remains unchanged] ...

---

### Public Transparency Index

... [previous section remains unchanged] ...

---

### Dependency Lock Manager

Ensures consistency and compatibility between all service modules and external packages.

#### Features:
- Lock versions of APIs, packages, libraries per environment
- Detect outdated or breaking versions pre-deploy
- Auto-warn on incompatible changes during updates

#### Tools:
- Integrated with Cursor AI dependency tree
- Version lock config: `.zmart.lock.json`
- CI/CD hook validation step

---

### Orchestration Conflict Resolver

Ensures no two agents or signals create conflicting actions for a symbol or Vault.

#### Responsibilities:
- Detect simultaneous actions (e.g., update + trade trigger)
- Block execution and notify master admin
- Provide decision matrix: proceed / cancel / reroute

#### Integrated Modules:
- Orchestration Agent
- Vault Controller
- Trade & Score Agents

---

### Signal Throttle & Rate Limiter

Mitigates risk of API throttling or system overload from signal bursts.

#### Features:
- Max signals per symbol/hour
- Trade spacing rule: minimum X minutes between trades
- Alert system for signal overflow
- Emergency pause on abnormal activity

---

### Cross-Agent Locking Protocol

Prevents overlapping actions between agents acting on the same resource.

#### Logic:
- Temporary lock on vault/symbol during action
- Agents must request lock before execution
- Expiration + fallback if agent fails

#### Benefits:
- Avoids race conditions
- Ensures reliable state transitions
- Central coordination layer

---
