from sqlalchemy import select
from ..db import SessionLocal, Pool, PoolContribution, CreditLedger
from ..schemas import PoolStatus
from datetime import datetime, timedelta
from loguru import logger

async def create_pool(user_id: str, topic: str, goal_credits: int, contribute: int) -> PoolStatus:
    async with SessionLocal() as s:
        # Set expiry to 24 hours from now
        expires_at = datetime.utcnow() + timedelta(hours=24)
        pool = Pool(
            topic=topic, 
            goal_credits=goal_credits, 
            current_credits=0, 
            owner_user_id=user_id,
            expires_at=expires_at,
            status="active"
        )
        s.add(pool)
        await s.flush()
        if contribute > 0:
            s.add(PoolContribution(pool_id=pool.id, user_id=user_id, credits=contribute))
            pool.current_credits += contribute
        await s.commit()
        return PoolStatus(pool_id=pool.id, topic=pool.topic, progress=pool.current_credits, goal=pool.goal_credits)

async def contribute_to_pool(user_id: str, pool_id: int, credits: int):
    async with SessionLocal() as s:
        pool = (await s.execute(select(Pool).where(Pool.id==pool_id))).scalar_one_or_none()
        if not pool:
            return False, None
        s.add(PoolContribution(pool_id=pool_id, user_id=user_id, credits=credits))
        pool.current_credits += credits
        await s.commit()
        return True, PoolStatus(pool_id=pool.id, topic=pool.topic, progress=pool.current_credits, goal=pool.goal_credits)

async def get_pool_status(pool_id: int):
    async with SessionLocal() as s:
        pool = (await s.execute(select(Pool).where(Pool.id==pool_id))).scalar_one_or_none()
        if not pool:
            return None
        return PoolStatus(pool_id=pool.id, topic=pool.topic, progress=pool.current_credits, goal=pool.goal_credits)


async def process_expired_pools():
    """Background job to handle expired pools and refund contributors."""
    async with SessionLocal() as s:
        # Find expired pools that haven't been processed
        now = datetime.utcnow()
        expired_pools = await s.execute(
            select(Pool).where(
                Pool.expires_at <= now,
                Pool.status == "active",
                Pool.current_credits < Pool.goal_credits  # Not funded
            )
        )
        
        for pool in expired_pools.scalars():
            logger.info(f"Processing expired pool {pool.id}: {pool.topic}")
            
            # Get all contributions for this pool
            contributions = await s.execute(
                select(PoolContribution).where(PoolContribution.pool_id == pool.id)
            )
            
            # Refund each contribution
            for contrib in contributions.scalars():
                # Create refund ledger entry
                refund_entry = CreditLedger(
                    user_id=contrib.user_id,
                    delta=contrib.credits,
                    reason=f"pool_refund_{pool.id}",
                    meta=f"Pool expired: {pool.topic}"
                )
                s.add(refund_entry)
                logger.info(f"Refunding {contrib.credits} credits to user {contrib.user_id}")
            
            # Mark pool as expired
            pool.status = "expired"
            
        await s.commit()
        logger.info("Expired pools processing completed")
