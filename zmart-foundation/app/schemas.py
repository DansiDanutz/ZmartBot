from pydantic import BaseModel
from typing import List, Literal

class EvidenceItem(BaseModel):
    source: Literal["Cryptometer","Binance","KuCoin","KingFisher","RiskMetric"]
    text: str

class SnapshotResponse(BaseModel):
    symbol: str
    long_prob: float
    short_prob: float
    stance: Literal["long","short","wait"]
    evidence: List[EvidenceItem]
    disclaimer: str = "This is educational content, not financial advice. Always do your own research."

class BestEntryResponse(BaseModel):
    symbol: str
    best_entry: float
    est_prob: float
    evidence: List[EvidenceItem]
    disclaimer: str = "This is educational content, not financial advice. Always do your own research."

class TargetsResponse(BaseModel):
    symbol: str
    tp: list[float]
    sr: list[float]
    trail_rule: str

class PlanBResponse(BaseModel):
    symbol: str
    invalidation: float
    notes: List[str]

class LadderStep(BaseModel):
    level_name: str
    price: float
    bankroll_pct: float
    leverage_cap: float

class LadderResponse(BaseModel):
    symbol: str
    steps: List[LadderStep]
    caps: dict
    alerts: List[str]

class CreditsBalance(BaseModel):
    user_id: str
    balance: int

class LedgerItem(BaseModel):
    delta: int
    reason: str
    meta: dict

class PoolCreate(BaseModel):
    topic: str
    goal_credits: int = 100
    contribute: int = 0

class PoolStatus(BaseModel):
    pool_id: int
    topic: str
    progress: int
    goal: int

class ContributeRequest(BaseModel):
    credits: int

class AlertSubscribeRequest(BaseModel):
    symbols: list[str]
    rules: list[str]
    channel: str
    plan: str
