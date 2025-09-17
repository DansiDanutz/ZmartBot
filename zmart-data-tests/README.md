# ZmartBot Data Test Harness — Cryptometer + KingFisher (Supabase) + NLG

Validate real endpoints, normalize JSON → **agent-friendly sentences**, and test Supabase storage for KingFisher clusters.

## Quick Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 1) Test Cryptometer
python tests/cryptometer_test.py --symbol ETH --endpoint ticker

# 2) Parse + NLG
python tests/nlg_agent_test.py --symbol ETH

# 3) KingFisher → Supabase
python tests/kingfisher_supabase_test.py --symbol ETH --json samples/kingfisher_eth_clusters.json

# 4) Risk Metric history CSV
python tests/riskmetric_history_test.py --symbol ETH --csv samples/risk_history_eth.csv
```
