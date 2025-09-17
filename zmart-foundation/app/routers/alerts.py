from fastapi import APIRouter
from ..schemas import AlertSubscribeRequest
from ..services.notifications import subscribe_alerts

router = APIRouter()

@router.post("")
async def subscribe(req: AlertSubscribeRequest, user_id: str = "demo"):
    ok = await subscribe_alerts(user_id, req.symbols, req.rules, req.channel, req.plan)
    return {"ok": ok}
