import time
import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from .models import MemoryIn, SearchOut
from .client import MemoryClient

app = FastAPI(title="Zmart Memory Adapter", version="0.1.0")
client = MemoryClient(base=os.getenv("MEMORY_GATEWAY_BASE", "http://127.0.0.1:8295"))

class HealthOut(BaseModel):
    status: str

@app.get("/health", response_model=HealthOut)
async def health():
    return HealthOut(status="ok")

@app.post("/memories")
async def create_memory(mem: MemoryIn):
    try:
        # Redaction policy (simple example): strip suspicious secrets patterns
        redacted = mem.model_copy()
        redacted.body = redacted.body.replace(os.getenv("API_KEY","***"), "***")
        payload = redacted.model_dump()
        return await client.store(payload)
    except Exception as e:
        # Fail-open: do not block callers
        raise HTTPException(status_code=502, detail=f"gateway_error: {e}")

@app.get("/search")
async def search(q: str = Query(..., min_length=1), tags: Optional[str] = None, k: int = Query(8, ge=1, le=32)):
    try:
        tag_list = tags.split(",") if tags else None
        return await client.search(q=q, tags=tag_list, k=k)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"gateway_error: {e}")
