# ZmartBot Foundation (Server) — Conversation-First Backend

Run a single FastAPI app that exposes:
- `/v1/signals/*`  (snapshot, best-entry, targets, plan-b, ladder)
- `/v1/credits/*`  (balance, add, spend, ledger)
- `/v1/pools/*`    (create, contribute, status)
- `/v1/alerts`     (subscribe rules)
- `/v1/health`     (health & env flags)

## Quick Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
# http://127.0.0.1:8000/docs
```
