from pydantic import BaseModel
from typing import Literal
from datetime import datetime

ClusterSize = Literal["small","medium","large","xlarge"]

class Cluster(BaseModel):
    symbol: str
    side: Literal["above","below"]
    price: float
    size: ClusterSize = "medium"
    notional: float | None = None
    ts: datetime
