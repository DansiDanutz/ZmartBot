from sqlalchemy import select, func
from ..db import SessionLocal, CreditLedger
from ..schemas import CreditsBalance, LedgerItem
import redis
import os
from loguru import logger
from typing import Optional

async def _sum_balance(session, user_id: str) -> int:
    q = await session.execute(select(func.coalesce(func.sum(CreditLedger.delta),0)).where(CreditLedger.user_id==user_id))
    return int(q.scalar_one())

async def get_balance(user_id: str) -> CreditsBalance:
    async with SessionLocal() as s:
        bal = await _sum_balance(s, user_id)
        
        # Auto-grant 10,000 welcome credits to new users
        if bal == 0:
            logger.info(f"New user {user_id} detected, granting 10,000 welcome credits")
            s.add(CreditLedger(user_id=user_id, delta=10000, reason="Welcome bonus - new user", meta="{}"))
            await s.commit()
            bal = 10000
            
        return CreditsBalance(user_id=user_id, balance=bal)

async def add_credits(user_id: str, amount: int, reason: str, meta: dict) -> CreditsBalance:
    async with SessionLocal() as s:
        s.add(CreditLedger(user_id=user_id, delta=amount, reason=reason, meta=str(meta)))
        await s.commit()
        bal = await _sum_balance(s, user_id)
        return CreditsBalance(user_id=user_id, balance=bal)

def _get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client with fallback."""
    try:
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            logger.warning("REDIS_URL not configured, idempotency disabled")
            return None
        
        client = redis.from_url(redis_url, decode_responses=True)
        # Test connection
        client.ping()
        return client
    except Exception as e:
        logger.warning(f"Redis not available: {e}, idempotency disabled")
        return None


async def spend_credits(user_id: str, amount: int, reason: str, meta: dict, request_id: Optional[str] = None):
    """Spend credits with optional idempotency via request_id."""
    
    # Check idempotency if request_id provided
    if request_id:
        redis_client = _get_redis_client()
        if redis_client:
            cache_key = f"credit_spend:{request_id}"
            
            # Check if this request was already processed
            if redis_client.exists(cache_key):
                logger.info(f"Duplicate spend request {request_id}, ignoring")
                # Return current balance without spending
                async with SessionLocal() as s:
                    bal = await _sum_balance(s, user_id)
                    return True, CreditsBalance(user_id=user_id, balance=bal)
            
            # Mark this request as processing (10 minutes TTL)
            redis_client.setex(cache_key, 600, f"{user_id}:{amount}:{reason}")
    
    async with SessionLocal() as s:
        bal = await _sum_balance(s, user_id)
        if bal < amount:
            return False, CreditsBalance(user_id=user_id, balance=bal)
        
        # Log the spend operation
        logger.info(f"Credit spend: user={user_id}, amount={amount}, reason={reason}, request_id={request_id}")
        
        s.add(CreditLedger(user_id=user_id, delta=-amount, reason=reason, meta=str(meta)))
        await s.commit()
        bal2 = await _sum_balance(s, user_id)
        return True, CreditsBalance(user_id=user_id, balance=bal2)

async def get_ledger(user_id: str) -> list[LedgerItem]:
    async with SessionLocal() as s:
        q = await s.execute(select(CreditLedger).where(CreditLedger.user_id==user_id).order_by(CreditLedger.created_at.desc()))
        rows = q.scalars().all()
        return [LedgerItem(delta=r.delta, reason=r.reason, meta={}) for r in rows]
