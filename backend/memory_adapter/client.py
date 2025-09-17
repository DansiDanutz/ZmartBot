import os
import httpx
from typing import Any, Dict, List, Optional

BASE = os.getenv("MEMORY_GATEWAY_BASE", "http://127.0.0.1:8295")

class MemoryClient:
    def __init__(self, base: Optional[str] = None, timeout: float = 10.0):
        self.base = base or BASE
        self.timeout = timeout

    async def store(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Convert the payload to match our memory gateway format
        memory_payload = {
            "content": payload.get("body", ""),
            "tags": payload.get("tags", []),
            "metadata": {
                "kind": payload.get("kind", "concept"),
                "title": payload.get("title", ""),
                "timestamp": payload.get("timestamp", 0),
                "ttl_days": payload.get("ttl_days")
            }
        }
        url = f"{self.base}/memories"
        async with httpx.AsyncClient(timeout=self.timeout) as cx:
            r = await cx.post(url, json=memory_payload)
            r.raise_for_status()
            return r.json()

    async def search(self, q: str, tags: Optional[List[str]] = None, k: int = 8) -> List[Dict[str, Any]]:
        params = {"q": q, "k": k}
        if tags:
            params["tags"] = ",".join(tags)
        url = f"{self.base}/search"
        async with httpx.AsyncClient(timeout=self.timeout) as cx:
            r = await cx.get(url, params=params)
            r.raise_for_status()
            results = r.json()
            # Convert the results to match the expected format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.get("id", ""),
                    "title": result.get("metadata", {}).get("title", ""),
                    "snippet": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", ""),
                    "score": result.get("score", 0.0),
                    "tags": result.get("tags", [])
                })
            return formatted_results
