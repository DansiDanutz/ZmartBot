import os
import httpx
from typing import Any, Dict, List, Optional

BASE = os.getenv("MEMORY_GATEWAY_BASE", "http://127.0.0.1:8295")

class MemoryClient:
    def __init__(self, base: Optional[str] = None, timeout: float = 10.0):
        self.base = base or BASE
        self.timeout = timeout

    async def store(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base}/memories"
        async with httpx.AsyncClient(timeout=self.timeout) as cx:
            r = await cx.post(url, json=payload)
            r.raise_for_status()
            return r.json()

    async def search(self, q: str, tags: Optional[List[str]] = None, k: int = 8) -> Dict[str, Any]:
        params = {"q": q, "k": k}
        if tags:
            params["tags"] = ",".join(tags)
        url = f"{self.base}/search"
        async with httpx.AsyncClient(timeout=self.timeout) as cx:
            r = await cx.get(url, params=params)
            r.raise_for_status()
            return r.json()
