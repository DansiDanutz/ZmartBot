import os, httpx
from typing import Any
from pydantic import ValidationError
from schemas.cryptometer import TickerPayload, GenericPayload

BASE = os.getenv("CRYPTOMETER_BASE","")
KEY  = os.getenv("CRYPTOMETER_API_KEY","")

class CryptometerError(Exception): ...

async def _get(client: httpx.AsyncClient, path: str, params: dict[str,Any]|None=None):
    if not BASE or not KEY:
        raise CryptometerError("CRYPTOMETER_BASE or API key missing")
    headers = {"Authorization": f"Bearer {KEY}"}
    r = await client.get(f"{BASE.rstrip('/')}/{path.lstrip('/')}", params=params, headers=headers, timeout=20.0)
    r.raise_for_status()
    return r.json()

async def fetch_ticker(symbol: str) -> TickerPayload:
    async with httpx.AsyncClient() as client:
        data = await _get(client, f"ticker", params={"symbol":symbol})
        payload = TickerPayload(
            symbol=data.get("symbol",symbol).upper(),
            price=float(data.get("price") or data.get("last") or 0.0),
            funding=(float(data["funding"]) if data.get("funding") is not None else None),
            oi=(float(data["open_interest"]) if data.get("open_interest") is not None else None),
            volume_1h=(float(data["volume_1h"]) if data.get("volume_1h") is not None else None),
            momentum=data.get("momentum") or {},
            indicators=[
                {"name":"RSI_1h","value": (data.get("indicators") or {}).get("rsi_1h")},
                {"name":"MACD_1h","value": (data.get("indicators") or {}).get("macd_1h")},
                {"name":"EMA9_21_1h","value": (data.get("indicators") or {}).get("ema9_21_1h")},
            ]
        )
        return payload

async def fetch_generic(path: str, params: dict|None=None) -> GenericPayload:
    async with httpx.AsyncClient() as client:
        data = await _get(client, path, params=params or {})
        symbol = (params or {}).get("symbol","UNKNOWN").upper()
        return GenericPayload(symbol=symbol, data=data)
