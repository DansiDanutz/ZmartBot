# Zmart Memory Gateway (ByteRover/Cipher)

This service runs a Cipher-compatible MCP memory server on **port 8295**.

## Start
```bash
docker compose -f services/memory-gateway/compose.memory.yml up -d
```

## Stop
```bash
docker compose -f services/memory-gateway/compose.memory.yml down
```

## Health
```bash
curl -fsS http://127.0.0.1:8295/health
```

## Data
Data persists under `services/memory-gateway/data/` which is mounted into the container at `/srv/cipher/.data`.
