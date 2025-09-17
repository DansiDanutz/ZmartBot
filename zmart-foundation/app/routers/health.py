from fastapi import APIRouter
import os

router = APIRouter()

@router.get("")
async def health():
    return {"status":"ok"}

@router.get("/full")
async def full():
    return {
        "status":"ok",
        "env": {
            "DATABASE_URL_set": bool(os.getenv("DATABASE_URL")),
            "CRYPTOMETER_BASE_set": bool(os.getenv("CRYPTOMETER_BASE")),
            "SUPABASE_URL_set": bool(os.getenv("SUPABASE_URL")),
            "RISK_HISTORY_CSV_set": bool(os.getenv("RISK_HISTORY_CSV")),
            "REDIS_URL_set": bool(os.getenv("REDIS_URL")),
            "OTEL_EXPORTER_OTLP_ENDPOINT_set": bool(os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"))
        }
    }
