from ..db import SessionLocal, NotificationSub

async def subscribe_alerts(user_id: str, symbols: list[str], rules: list[str], channel: str, plan: str):
    async with SessionLocal() as s:
        for sym in symbols:
            for rule in rules:
                s.add(NotificationSub(user_id=user_id, symbol=sym, rule=rule, plan=plan, active=1))
        await s.commit()
    return True
