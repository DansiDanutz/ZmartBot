from pydantic import BaseModel
from typing import Optional, List, Any

class IndicatorPoint(BaseModel):
    name: str
    value: float | int | str | None = None

class TickerPayload(BaseModel):
    symbol: str
    price: float
    funding: float | None = None
    oi: float | None = None
    volume_1h: float | None = None
    momentum: dict | None = None
    indicators: list[IndicatorPoint] = []

class GenericPayload(BaseModel):
    symbol: str
    data: dict
