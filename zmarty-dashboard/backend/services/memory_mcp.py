"""
Memory Adapter MCP Service for Zmarty Dashboard
Provides persistent conversation memory using MCP (Model Context Protocol)
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

import aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from ..models.database import ConversationMemory, User
from ..core.database import get_async_session
from ..core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class MemoryAdapter:
    """
    MCP-compatible memory adapter for persistent conversation storage
    Handles short-term (Redis) and long-term (PostgreSQL) memory
    """
    
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.memory_ttl = 3600  # 1 hour in seconds
        self.max_memory_entries = 100
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = await aioredis.from_url(
                settings.redis_url,
                encoding='utf-8',
                decode_responses=True
            )
            logger.info("Memory Adapter MCP initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Memory Adapter MCP: {e}")
            self.redis_client = None
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _get_memory_key(self, user_id: int, conversation_id: str) -> str:
        """Generate Redis key for conversation memory"""
        return f"memory:{user_id}:{conversation_id}"
    
    def _get_context_key(self, user_id: int) -> str:
        """Generate Redis key for user context"""
        return f"context:{user_id}"
    
    async def store_memory(
        self, 
        user_id: int, 
        conversation_id: str, 
        memory_type: str,
        content: Dict[str, Any],
        importance: int = 5
    ) -> str:
        """
        Store memory entry with MCP compatibility
        
        Args:
            user_id: User ID
            conversation_id: Conversation identifier
            memory_type: Type of memory (chat, preference, fact, etc.)
            content: Memory content as dict
            importance: Importance level (1-10)
            
        Returns:
            Memory entry ID
        """
        memory_id = str(uuid4())
        timestamp = datetime.utcnow()
        
        memory_entry = {
            "id": memory_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "type": memory_type,
            "content": content,
            "importance": importance,
            "timestamp": timestamp.isoformat(),
            "access_count": 0,
            "last_accessed": timestamp.isoformat()
        }
        
        # Store in Redis for short-term access
        if self.redis_client:
            try:
                memory_key = self._get_memory_key(user_id, conversation_id)
                await self.redis_client.hset(
                    memory_key, 
                    memory_id, 
                    json.dumps(memory_entry)
                )
                await self.redis_client.expire(memory_key, self.memory_ttl)
                
                # Add to conversation index
                index_key = f"memory_index:{user_id}"
                await self.redis_client.sadd(index_key, conversation_id)
                await self.redis_client.expire(index_key, self.memory_ttl * 24)  # 24 hours
                
                logger.debug(f"Stored memory {memory_id} in Redis")
            except Exception as e:
                logger.error(f"Failed to store memory in Redis: {e}")
        
        # Store in PostgreSQL for long-term persistence
        try:
            async with get_async_session() as session:
                db_memory = ConversationMemory(
                    id=memory_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    memory_type=memory_type,
                    content=content,
                    importance=importance,
                    created_at=timestamp
                )
                session.add(db_memory)
                await session.commit()
                logger.debug(f"Stored memory {memory_id} in PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to store memory in PostgreSQL: {e}")
        
        return memory_id
    
    async def retrieve_memories(
        self, 
        user_id: int, 
        conversation_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories with MCP compatibility
        
        Args:
            user_id: User ID
            conversation_id: Optional conversation filter
            memory_type: Optional type filter
            limit: Maximum number of memories to return
            
        Returns:
            List of memory entries
        """
        memories = []
        
        # Try Redis first for recent memories
        if self.redis_client and conversation_id:
            try:
                memory_key = self._get_memory_key(user_id, conversation_id)
                redis_memories = await self.redis_client.hgetall(memory_key)
                
                for memory_data in redis_memories.values():
                    memory_entry = json.loads(memory_data)
                    if not memory_type or memory_entry.get("type") == memory_type:
                        memories.append(memory_entry)
                        
                logger.debug(f"Retrieved {len(memories)} memories from Redis")
            except Exception as e:
                logger.error(f"Failed to retrieve memories from Redis: {e}")
        
        # Fallback to PostgreSQL or get additional memories
        if len(memories) < limit:
            try:
                async with get_async_session() as session:
                    query = select(ConversationMemory).where(
                        ConversationMemory.user_id == user_id
                    )
                    
                    if conversation_id:
                        query = query.where(
                            ConversationMemory.conversation_id == conversation_id
                        )
                    
                    if memory_type:
                        query = query.where(
                            ConversationMemory.memory_type == memory_type
                        )
                    
                    query = query.order_by(
                        ConversationMemory.importance.desc(),
                        ConversationMemory.created_at.desc()
                    ).limit(limit)
                    
                    result = await session.execute(query)
                    db_memories = result.scalars().all()
                    
                    # Convert to dict format
                    db_memory_dicts = []
                    for db_memory in db_memories:
                        memory_dict = {
                            "id": db_memory.id,
                            "user_id": db_memory.user_id,
                            "conversation_id": db_memory.conversation_id,
                            "type": db_memory.memory_type,
                            "content": db_memory.content,
                            "importance": db_memory.importance,
                            "timestamp": db_memory.created_at.isoformat(),
                            "access_count": db_memory.access_count,
                            "last_accessed": db_memory.last_accessed.isoformat() if db_memory.last_accessed else None
                        }
                        
                        # Avoid duplicates from Redis
                        if not any(m["id"] == memory_dict["id"] for m in memories):
                            db_memory_dicts.append(memory_dict)
                    
                    memories.extend(db_memory_dicts)
                    logger.debug(f"Retrieved {len(db_memory_dicts)} additional memories from PostgreSQL")
            except Exception as e:
                logger.error(f"Failed to retrieve memories from PostgreSQL: {e}")
        
        # Sort by importance and recency
        memories.sort(key=lambda x: (x["importance"], x["timestamp"]), reverse=True)
        return memories[:limit]
    
    async def update_memory(
        self, 
        memory_id: str, 
        user_id: int, 
        updates: Dict[str, Any]
    ) -> bool:
        """Update a memory entry"""
        try:
            # Update in PostgreSQL
            async with get_async_session() as session:
                query = update(ConversationMemory).where(
                    ConversationMemory.id == memory_id,
                    ConversationMemory.user_id == user_id
                ).values(**updates)
                
                await session.execute(query)
                await session.commit()
                
                # Update access tracking
                await self._update_access_stats(memory_id, user_id)
                
                logger.debug(f"Updated memory {memory_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            return False
    
    async def delete_memory(self, memory_id: str, user_id: int) -> bool:
        """Delete a memory entry"""
        try:
            # Delete from PostgreSQL
            async with get_async_session() as session:
                query = delete(ConversationMemory).where(
                    ConversationMemory.id == memory_id,
                    ConversationMemory.user_id == user_id
                )
                
                await session.execute(query)
                await session.commit()
                
                logger.debug(f"Deleted memory {memory_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
    async def get_conversation_context(
        self, 
        user_id: int, 
        conversation_id: str,
        context_window: int = 20
    ) -> Dict[str, Any]:
        """
        Get conversation context for MCP
        
        Returns relevant memories and conversation state
        """
        # Get recent memories
        memories = await self.retrieve_memories(
            user_id=user_id,
            conversation_id=conversation_id,
            limit=context_window
        )
        
        # Get user preferences
        preferences = await self.retrieve_memories(
            user_id=user_id,
            memory_type="preference",
            limit=10
        )
        
        # Get user facts/profile
        facts = await self.retrieve_memories(
            user_id=user_id,
            memory_type="fact",
            limit=20
        )
        
        # Build context
        context = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "memories": memories,
            "preferences": preferences,
            "facts": facts,
            "memory_count": len(memories),
            "context_window": context_window
        }
        
        # Cache context in Redis
        if self.redis_client:
            try:
                context_key = f"context:{user_id}:{conversation_id}"
                await self.redis_client.setex(
                    context_key,
                    300,  # 5 minutes
                    json.dumps(context, default=str)
                )
            except Exception as e:
                logger.error(f"Failed to cache context: {e}")
        
        return context
    
    async def store_conversation_turn(
        self,
        user_id: int,
        conversation_id: str,
        user_message: str,
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a complete conversation turn"""
        turn_content = {
            "user_message": user_message,
            "assistant_response": assistant_response,
            "metadata": metadata or {},
            "turn_timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.store_memory(
            user_id=user_id,
            conversation_id=conversation_id,
            memory_type="conversation_turn",
            content=turn_content,
            importance=7  # High importance for conversation turns
        )
    
    async def extract_and_store_facts(
        self,
        user_id: int,
        conversation_id: str,
        text: str,
        fact_type: str = "user_fact"
    ) -> List[str]:
        """
        Extract and store facts from conversation text
        This would typically use NLP/AI to extract facts
        """
        # Simplified fact extraction (in production, use NLP)
        facts = []
        
        # Look for explicit preferences
        if "I like" in text or "I prefer" in text:
            fact_content = {
                "extracted_text": text,
                "fact_type": "preference",
                "confidence": 0.8
            }
            
            fact_id = await self.store_memory(
                user_id=user_id,
                conversation_id=conversation_id,
                memory_type="fact",
                content=fact_content,
                importance=8
            )
            facts.append(fact_id)
        
        # Look for user information
        if "I am" in text or "My name is" in text:
            fact_content = {
                "extracted_text": text,
                "fact_type": "personal_info",
                "confidence": 0.9
            }
            
            fact_id = await self.store_memory(
                user_id=user_id,
                conversation_id=conversation_id,
                memory_type="fact",
                content=fact_content,
                importance=9
            )
            facts.append(fact_id)
        
        return facts
    
    async def cleanup_old_memories(self, days_old: int = 30) -> int:
        """Clean up old memories based on age and importance"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        cleaned_count = 0
        
        try:
            async with get_async_session() as session:
                # Delete low-importance old memories
                query = delete(ConversationMemory).where(
                    ConversationMemory.created_at < cutoff_date,
                    ConversationMemory.importance < 5
                )
                
                result = await session.execute(query)
                cleaned_count = result.rowcount
                await session.commit()
                
                logger.info(f"Cleaned up {cleaned_count} old memories")
        except Exception as e:
            logger.error(f"Failed to cleanup old memories: {e}")
        
        return cleaned_count
    
    async def _update_access_stats(self, memory_id: str, user_id: int):
        """Update memory access statistics"""
        try:
            async with get_async_session() as session:
                query = update(ConversationMemory).where(
                    ConversationMemory.id == memory_id,
                    ConversationMemory.user_id == user_id
                ).values(
                    access_count=ConversationMemory.access_count + 1,
                    last_accessed=datetime.utcnow()
                )
                
                await session.execute(query)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to update access stats for memory {memory_id}: {e}")
    
    async def get_memory_stats(self, user_id: int) -> Dict[str, Any]:
        """Get memory statistics for a user"""
        try:
            async with get_async_session() as session:
                # Get total memory count
                total_query = select(ConversationMemory).where(
                    ConversationMemory.user_id == user_id
                )
                total_result = await session.execute(total_query)
                total_memories = len(total_result.scalars().all())
                
                # Get memory by type
                type_stats = {}
                for memory_type in ["conversation_turn", "fact", "preference"]:
                    type_query = select(ConversationMemory).where(
                        ConversationMemory.user_id == user_id,
                        ConversationMemory.memory_type == memory_type
                    )
                    type_result = await session.execute(type_query)
                    type_stats[memory_type] = len(type_result.scalars().all())
                
                return {
                    "user_id": user_id,
                    "total_memories": total_memories,
                    "memory_types": type_stats,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Failed to get memory stats for user {user_id}: {e}")
            return {"error": str(e)}


# Global memory adapter instance
memory_adapter = MemoryAdapter()


async def get_memory_adapter() -> MemoryAdapter:
    """Get the global memory adapter instance"""
    if not memory_adapter.redis_client:
        await memory_adapter.initialize()
    return memory_adapter


# MCP-compatible interface functions
async def mcp_store_memory(
    user_id: int,
    conversation_id: str,
    memory_type: str,
    content: Dict[str, Any],
    importance: int = 5
) -> Dict[str, Any]:
    """MCP-compatible memory storage function"""
    adapter = await get_memory_adapter()
    memory_id = await adapter.store_memory(
        user_id, conversation_id, memory_type, content, importance
    )
    
    return {
        "memory_id": memory_id,
        "status": "stored",
        "timestamp": datetime.utcnow().isoformat()
    }


async def mcp_retrieve_memories(
    user_id: int,
    conversation_id: Optional[str] = None,
    memory_type: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """MCP-compatible memory retrieval function"""
    adapter = await get_memory_adapter()
    memories = await adapter.retrieve_memories(
        user_id, conversation_id, memory_type, limit
    )
    
    return {
        "memories": memories,
        "count": len(memories),
        "timestamp": datetime.utcnow().isoformat()
    }


async def mcp_get_context(
    user_id: int,
    conversation_id: str,
    context_window: int = 20
) -> Dict[str, Any]:
    """MCP-compatible context retrieval function"""
    adapter = await get_memory_adapter()
    context = await adapter.get_conversation_context(
        user_id, conversation_id, context_window
    )
    
    return context