# UI‑TARS Worker

Automates UI tasks like TradingView/KingFisher captures and FE smoke tests.

## Start
```bash
docker compose -f services/ui-tars/compose.ui-tars.yml up -d
```

## Tasks
- `tradingview_capture.ts`
- `kingfisher_capture.ts`
- `dashboard_smoke.ts`

Artifacts are saved under `services/ui-tars/data/` and should be forwarded to your backend/logging.
