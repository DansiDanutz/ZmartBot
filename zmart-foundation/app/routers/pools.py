from fastapi import APIRouter, HTTPException
from ..schemas import PoolCreate, PoolStatus, ContributeRequest
from ..services.pools import create_pool, contribute_to_pool, get_pool_status

router = APIRouter()

@router.post("", response_model=PoolStatus)
async def create(payload: PoolCreate, user_id: str = "demo"):
    return await create_pool(user_id, payload.topic, payload.goal_credits, payload.contribute)

@router.post("/{pool_id}/contribute", response_model=PoolStatus)
async def contribute(pool_id: int, payload: ContributeRequest, user_id: str = "demo"):
    ok, status = await contribute_to_pool(user_id, pool_id, payload.credits)
    if not ok:
        raise HTTPException(status_code=400, detail="Contribution failed")
    return status

@router.get("/{pool_id}", response_model=PoolStatus)
async def status(pool_id: int):
    st = await get_pool_status(pool_id)
    if not st:
        raise HTTPException(status_code=404, detail="Pool not found")
    return st
