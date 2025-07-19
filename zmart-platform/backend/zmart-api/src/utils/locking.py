"""
Zmart Trading Bot Platform - Locking Utilities
Handles resource locking and concurrency control
"""
import asyncio
import logging
import time
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class LockType(Enum):
    """Types of locks available"""
    READ = "read"
    WRITE = "write"
    EXCLUSIVE = "exclusive"

@dataclass
class LockInfo:
    """Information about a lock"""
    resource_id: str
    lock_type: LockType
    owner: str
    acquired_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class LockManager:
    """Manages resource locking for concurrency control"""
    
    def __init__(self):
        self.locks: Dict[str, LockInfo] = {}
        self.lock_queue: Dict[str, asyncio.Queue] = {}
        self.default_timeout = 30  # seconds
        self.cleanup_interval = 60  # seconds
        self.is_running = False
        
        logger.info("Lock manager initialized")
    
    async def acquire_lock(self, resource_id: str, lock_type: LockType, owner: str, 
                          timeout: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Acquire a lock on a resource"""
        timeout = timeout or self.default_timeout
        metadata = metadata or {}
        
        # Check if lock already exists
        existing_lock = self.locks.get(resource_id)
        if existing_lock:
            # Check if lock is expired
            if existing_lock.expires_at and datetime.utcnow() > existing_lock.expires_at:
                logger.debug(f"Removing expired lock on {resource_id}")
                await self.release_lock(resource_id, existing_lock.owner)
                existing_lock = None
            
            # If lock still exists and is valid, check compatibility
            if existing_lock:
                if not self._can_acquire_lock(existing_lock, lock_type, owner):
                    logger.warning(f"Cannot acquire {lock_type.value} lock on {resource_id}, "
                                f"held by {existing_lock.owner} as {existing_lock.lock_type.value}")
                    return False
        
        # Create new lock
        lock_info = LockInfo(
            resource_id=resource_id,
            lock_type=lock_type,
            owner=owner,
            expires_at=datetime.utcnow() + timedelta(seconds=timeout),
            metadata=metadata
        )
        
        self.locks[resource_id] = lock_info
        
        logger.debug(f"Acquired {lock_type.value} lock on {resource_id} for {owner}")
        return True
    
    async def release_lock(self, resource_id: str, owner: str) -> bool:
        """Release a lock on a resource"""
        lock_info = self.locks.get(resource_id)
        
        if not lock_info:
            logger.debug(f"No lock found on {resource_id}")
            return True
        
        if lock_info.owner != owner:
            logger.warning(f"Cannot release lock on {resource_id}, owned by {lock_info.owner}, "
                         f"requested by {owner}")
            return False
        
        del self.locks[resource_id]
        logger.debug(f"Released lock on {resource_id} by {owner}")
        return True
    
    async def release_all_locks(self, owner: str) -> int:
        """Release all locks owned by a specific owner"""
        released_count = 0
        locks_to_remove = []
        
        for resource_id, lock_info in self.locks.items():
            if lock_info.owner == owner:
                locks_to_remove.append(resource_id)
        
        for resource_id in locks_to_remove:
            if await self.release_lock(resource_id, owner):
                released_count += 1
        
        logger.info(f"Released {released_count} locks for owner {owner}")
        return released_count
    
    def is_locked(self, resource_id: str) -> bool:
        """Check if a resource is currently locked"""
        lock_info = self.locks.get(resource_id)
        if not lock_info:
            return False
        
        # Check if lock is expired
        if lock_info.expires_at and datetime.utcnow() > lock_info.expires_at:
            logger.debug(f"Lock on {resource_id} is expired")
            return False
        
        return True
    
    def get_lock_info(self, resource_id: str) -> Optional[LockInfo]:
        """Get information about a lock"""
        lock_info = self.locks.get(resource_id)
        if lock_info and lock_info.expires_at and datetime.utcnow() > lock_info.expires_at:
            return None
        return lock_info
    
    def get_locks_by_owner(self, owner: str) -> Dict[str, LockInfo]:
        """Get all locks owned by a specific owner"""
        return {
            resource_id: lock_info
            for resource_id, lock_info in self.locks.items()
            if lock_info.owner == owner and (
                not lock_info.expires_at or datetime.utcnow() <= lock_info.expires_at
            )
        }
    
    def get_all_locks(self) -> Dict[str, LockInfo]:
        """Get all active locks"""
        return {
            resource_id: lock_info
            for resource_id, lock_info in self.locks.items()
            if not lock_info.expires_at or datetime.utcnow() <= lock_info.expires_at
        }
    
    def _can_acquire_lock(self, existing_lock: LockInfo, new_lock_type: LockType, new_owner: str) -> bool:
        """Check if a new lock can be acquired given an existing lock"""
        # Same owner can always acquire
        if existing_lock.owner == new_owner:
            return True
        
        # Read locks are compatible with other read locks
        if (existing_lock.lock_type == LockType.READ and 
            new_lock_type == LockType.READ):
            return True
        
        # Write and exclusive locks are not compatible with any other locks
        if existing_lock.lock_type in [LockType.WRITE, LockType.EXCLUSIVE]:
            return False
        
        if new_lock_type in [LockType.WRITE, LockType.EXCLUSIVE]:
            return False
        
        return True
    
    async def cleanup_expired_locks(self):
        """Remove expired locks"""
        current_time = datetime.utcnow()
        locks_to_remove = []
        
        for resource_id, lock_info in self.locks.items():
            if lock_info.expires_at and current_time > lock_info.expires_at:
                locks_to_remove.append(resource_id)
        
        for resource_id in locks_to_remove:
            del self.locks[resource_id]
            logger.debug(f"Cleaned up expired lock on {resource_id}")
        
        if locks_to_remove:
            logger.info(f"Cleaned up {len(locks_to_remove)} expired locks")
    
    async def start_cleanup_task(self):
        """Start the cleanup task for expired locks"""
        self.is_running = True
        
        while self.is_running:
            try:
                await self.cleanup_expired_locks()
                await asyncio.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"Error in lock cleanup task: {e}")
                await asyncio.sleep(self.cleanup_interval)
    
    def stop_cleanup_task(self):
        """Stop the cleanup task"""
        self.is_running = False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get lock manager statistics"""
        current_time = datetime.utcnow()
        active_locks = 0
        expired_locks = 0
        
        for lock_info in self.locks.values():
            if lock_info.expires_at and current_time > lock_info.expires_at:
                expired_locks += 1
            else:
                active_locks += 1
        
        lock_types = {}
        owners = {}
        
        for lock_info in self.locks.values():
            if lock_info.expires_at and current_time <= lock_info.expires_at:
                lock_types[lock_info.lock_type.value] = lock_types.get(lock_info.lock_type.value, 0) + 1
                owners[lock_info.owner] = owners.get(lock_info.owner, 0) + 1
        
        return {
            "total_locks": len(self.locks),
            "active_locks": active_locks,
            "expired_locks": expired_locks,
            "lock_types": lock_types,
            "owners": owners,
            "is_running": self.is_running
        }

# Global lock manager instance
lock_manager = LockManager()

def get_lock_manager() -> LockManager:
    """Get the global lock manager instance"""
    return lock_manager

# Convenience functions for common locking patterns
async def with_lock(resource_id: str, lock_type: LockType, owner: str, 
                   timeout: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None):
    """Context manager for automatic lock acquisition and release"""
    class LockContext:
        def __init__(self, manager: LockManager, resource_id: str, lock_type: LockType, 
                     owner: str, timeout: Optional[int], metadata: Optional[Dict[str, Any]]):
            self.manager = manager
            self.resource_id = resource_id
            self.lock_type = lock_type
            self.owner = owner
            self.timeout = timeout
            self.metadata = metadata
            self.acquired = False
        
        async def __aenter__(self):
            self.acquired = await self.manager.acquire_lock(
                self.resource_id, self.lock_type, self.owner, self.timeout, self.metadata
            )
            if not self.acquired:
                raise RuntimeError(f"Failed to acquire lock on {self.resource_id}")
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if self.acquired:
                await self.manager.release_lock(self.resource_id, self.owner)
    
    return LockContext(lock_manager, resource_id, lock_type, owner, timeout, metadata)

async def with_trading_lock(symbol: str, owner: str, timeout: Optional[int] = None):
    """Convenience function for trading locks"""
    return with_lock(f"trading:{symbol}", LockType.EXCLUSIVE, owner, timeout)

async def with_signal_lock(symbol: str, owner: str, timeout: Optional[int] = None):
    """Convenience function for signal processing locks"""
    return with_lock(f"signal:{symbol}", LockType.WRITE, owner, timeout)

async def with_position_lock(symbol: str, owner: str, timeout: Optional[int] = None):
    """Convenience function for position management locks"""
    return with_lock(f"position:{symbol}", LockType.WRITE, owner, timeout) 