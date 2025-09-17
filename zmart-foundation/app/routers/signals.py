from fastapi import APIRouter, Query
from ..schemas import SnapshotResponse, BestEntryResponse, TargetsResponse, PlanBResponse, LadderResponse, LadderStep, EvidenceItem
from ..services.scoring import get_snapshot, get_best_entry, get_targets, get_plan_b, get_ladder

router = APIRouter()

@router.get("/snapshot", response_model=SnapshotResponse)
async def snapshot(symbol: str = Query(..., examples=["ETH","BTC"])):
    return await get_snapshot(symbol)

@router.post("/best-entry", response_model=BestEntryResponse)
async def best_entry(payload: dict):
    symbol = payload.get("symbol","ETH")
    return await get_best_entry(symbol)

@router.post("/targets", response_model=TargetsResponse)
async def targets(payload: dict):
    symbol = payload.get("symbol","ETH")
    return await get_targets(symbol)

@router.post("/plan-b", response_model=PlanBResponse)
async def plan_b(payload: dict):
    symbol = payload.get("symbol","ETH")
    return await get_plan_b(symbol)

@router.post("/ladder", response_model=LadderResponse)
async def ladder(payload: dict):
    symbol = payload.get("symbol","ETH")
    bankroll = float(payload.get("bankroll", 10000))
    return await get_ladder(symbol, bankroll)
