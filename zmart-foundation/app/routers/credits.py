from fastapi import APIRouter, HTTPException, Header
from ..schemas import CreditsBalance, LedgerItem
from ..services.credits import get_balance, add_credits, spend_credits, get_ledger
from typing import Optional

router = APIRouter()

@router.get("", response_model=CreditsBalance)
async def balance(user_id: str):
    return await get_balance(user_id)

@router.post("/add", response_model=CreditsBalance)
async def add(user_id: str, amount: int):
    return await add_credits(user_id, amount, reason="topup", meta={})

@router.post("/spend", response_model=CreditsBalance)
async def spend(
    user_id: str, 
    amount: int, 
    reason: str, 
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID")
):
    ok, bal = await spend_credits(user_id, amount, reason, meta={}, request_id=x_request_id)
    if not ok:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    return bal

@router.get("/ledger", response_model=list[LedgerItem])
async def ledger(user_id: str):
    return await get_ledger(user_id)
