"""
Zmart Trading Bot Platform - Locking Utilities
Resource locking system for concurrent access control
"""
import logging
import asyncio
import time
from typing import Dict, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class LockType(Enum):
    """Types of locks available"""
    READ = "read"
    WRITE = "write"
    EXCLUSIVE = "exclusive"

class LockStatus(Enum):
    """Lock status enumeration"""
    ACQUIRED = "acquired"
    WAITING = "waiting"
    TIMEOUT = "timeout"
    RELEASED = "released"

@dataclass
class Lock:
    """Lock information"""
    resource: str
    lock_type: LockType
    owner: str
    acquired_at: datetime
    expires_at: datetime
    status: LockStatus = LockStatus.ACQUIRED
    
    def is_expired(self) -> bool:
        """Check if lock has expired"""
        return datetime.utcnow() > self.expires_at
    
    def time_remaining(self) -> float:
        """Get time remaining until expiration in seconds"""
        return (self.expires_at - datetime.utcnow()).total_seconds()

class LockManager:
    """Manages resource locks for concurrent access control"""
    
    def __init__(self):
        self.locks: Dict[str, Lock] = {}
        self.waiting_locks: Dict[str, asyncio.Queue] = {}
        self.is_running = False
        self.lock_timeout = 30.0  # Default timeout in seconds
        self.cleanup_interval = 60.0  # Cleanup interval in seconds
        self.cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the lock manager"""
        if self.is_running:
            return
        
        self.is_running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_locks())
        logger.info("Lock manager started")
    
    async def stop(self):
        """Stop the lock manager"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Release all locks
        for resource in list(self.locks.keys()):
            await self.force_release_lock(resource)
        
        logger.info("Lock manager stopped")
    
    async def acquire_lock(self, resource: str, lock_type: LockType, owner: str, 
                          timeout: Optional[float] = None) -> bool:
        """Acquire a lock on a resource"""
        if not self.is_running:
            logger.warning("Lock manager not running")
            return False
        
        timeout = timeout or self.lock_timeout
        start_time = time.time()
        
        try:
            # Check if we can acquire the lock immediately
            if await self._can_acquire_lock(resource, lock_type, owner):
                return await self._acquire_lock_immediate(resource, lock_type, owner)
            
            # Wait for lock to become available
            return await self._wait_for_lock(resource, lock_type, owner, timeout, start_time)
            
        except asyncio.TimeoutError:
            logger.warning(f"Lock acquisition timeout for {resource} by {owner}")
            return False
        except Exception as e:
            logger.error(f"Error acquiring lock for {resource}: {e}")
            return False
    
    async def release_lock(self, resource: str, owner: str) -> bool:
        """Release a lock on a resource"""
        if resource not in self.locks:
            logger.warning(f"No lock found for resource: {resource}")
            return False
        
        lock = self.locks[resource]
        if lock.owner != owner:
            logger.warning(f"Lock {resource} not owned by {owner}")
            return False
        
        # Remove the lock
        del self.locks[resource]
        
        # Notify waiting locks
        if resource in self.waiting_locks:
            queue = self.waiting_locks[resource]
            if not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
        
        logger.debug(f"Lock released for {resource} by {owner}")
        return True
    
    async def force_release_lock(self, resource: str) -> bool:
        """Force release a lock regardless of owner"""
        if resource not in self.locks:
            return False
        
        del self.locks[resource]
        logger.warning(f"Lock force released for {resource}")
        return True
    
    def get_lock_info(self, resource: str) -> Optional[Lock]:
        """Get information about a lock"""
        return self.locks.get(resource)
    
    def get_all_locks(self) -> Dict[str, Lock]:
        """Get all active locks"""
        return self.locks.copy()
    
    def get_locks_by_owner(self, owner: str) -> Dict[str, Lock]:
        """Get all locks owned by a specific owner"""
        return {resource: lock for resource, lock in self.locks.items() 
                if lock.owner == owner}
    
    async def _can_acquire_lock(self, resource: str, lock_type: LockType, owner: str) -> bool:
        """Check if a lock can be acquired immediately"""
        if resource not in self.locks:
            return True
        
        existing_lock = self.locks[resource]
        
        # Check if lock has expired
        if existing_lock.is_expired():
            await self.force_release_lock(resource)
            return True
        
        # Same owner can re-acquire
        if existing_lock.owner == owner:
            return True
        
        # Read locks can be shared
        if lock_type == LockType.READ and existing_lock.lock_type == LockType.READ:
            return True
        
        return False
    
    async def _acquire_lock_immediate(self, resource: str, lock_type: LockType, owner: str) -> bool:
        """Acquire a lock immediately"""
        expires_at = datetime.utcnow() + timedelta(seconds=self.lock_timeout)
        
        lock = Lock(
            resource=resource,
            lock_type=lock_type,
            owner=owner,
            acquired_at=datetime.utcnow(),
            expires_at=expires_at
        )
        
        self.locks[resource] = lock
        logger.debug(f"Lock acquired for {resource} by {owner} ({lock_type.value})")
        return True
    
    async def _wait_for_lock(self, resource: str, lock_type: LockType, owner: str, 
                            timeout: float, start_time: float) -> bool:
        """Wait for a lock to become available"""
        if resource not in self.waiting_locks:
            self.waiting_locks[resource] = asyncio.Queue()
        
        queue = self.waiting_locks[resource]
        
        # Add ourselves to the waiting queue
        await queue.put((lock_type, owner))
        
        try:
            while time.time() - start_time < timeout:
                # Check if we can acquire the lock now
                if await self._can_acquire_lock(resource, lock_type, owner):
                    # Remove ourselves from queue
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                    
                    return await self._acquire_lock_immediate(resource, lock_type, owner)
                
                # Wait a bit before checking again
                await asyncio.sleep(0.1)
            
            # Timeout reached
            raise asyncio.TimeoutError()
            
        except asyncio.TimeoutError:
            # Remove ourselves from queue
            try:
                queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            raise
    
    async def _cleanup_expired_locks(self):
        """Periodically cleanup expired locks"""
        while self.is_running:
            try:
                expired_resources = []
                
                for resource, lock in self.locks.items():
                    if lock.is_expired():
                        expired_resources.append(resource)
                
                for resource in expired_resources:
                    await self.force_release_lock(resource)
                    logger.info(f"Expired lock cleaned up for {resource}")
                
                await asyncio.sleep(self.cleanup_interval)
                
            except Exception as e:
                logger.error(f"Error in lock cleanup: {e}")
                await asyncio.sleep(10)

# Global lock manager instance
lock_manager = LockManager()

# Convenience functions for common locking patterns
async def acquire_trading_lock(symbol: str, owner: str, timeout: float = 30) -> bool:
    """Acquire a trading lock for a symbol"""
    return await lock_manager.acquire_lock(f"trading:{symbol}", LockType.EXCLUSIVE, owner, timeout)

async def acquire_signal_lock(symbol: str, owner: str, timeout: float = 10) -> bool:
    """Acquire a signal processing lock for a symbol"""
    return await lock_manager.acquire_lock(f"signal:{symbol}", LockType.WRITE, owner, timeout)

async def acquire_portfolio_lock(owner: str, timeout: float = 30) -> bool:
    """Acquire a portfolio lock"""
    return await lock_manager.acquire_lock("portfolio", LockType.EXCLUSIVE, owner, timeout)

async def acquire_risk_lock(symbol: str, owner: str, timeout: float = 15) -> bool:
    """Acquire a risk management lock for a symbol"""
    return await lock_manager.acquire_lock(f"risk:{symbol}", LockType.WRITE, owner, timeout)

# Context manager for automatic lock release
class LockContext:
    """Context manager for automatic lock management"""
    
    def __init__(self, resource: str, lock_type: LockType, owner: str, timeout: Optional[float] = None):
        self.resource = resource
        self.lock_type = lock_type
        self.owner = owner
        self.timeout = timeout
        self.acquired = False
    
    async def __aenter__(self):
        """Acquire lock on enter"""
        self.acquired = await lock_manager.acquire_lock(
            self.resource, self.lock_type, self.owner, self.timeout
        )
        if not self.acquired:
            raise RuntimeError(f"Failed to acquire lock for {self.resource}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release lock on exit"""
        if self.acquired:
            await lock_manager.release_lock(self.resource, self.owner)

# Convenience context managers
def trading_lock(symbol: str, owner: str, timeout: float = 30):
    """Context manager for trading locks"""
    return LockContext(f"trading:{symbol}", LockType.EXCLUSIVE, owner, timeout)

def signal_lock(symbol: str, owner: str, timeout: float = 10):
    """Context manager for signal locks"""
    return LockContext(f"signal:{symbol}", LockType.WRITE, owner, timeout)

def portfolio_lock(owner: str, timeout: float = 30):
    """Context manager for portfolio locks"""
    return LockContext("portfolio", LockType.EXCLUSIVE, owner, timeout)

def risk_lock(symbol: str, owner: str, timeout: float = 15):
    """Context manager for risk locks"""
    return LockContext(f"risk:{symbol}", LockType.WRITE, owner, timeout) 