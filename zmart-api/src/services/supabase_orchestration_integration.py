"""
Supabase Orchestration Integration Service
Coordinates data flow and synchronization between ZmartyBrain and ZmartBot projects
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import uuid
from supabase import create_client, Client
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import schedule
import time
from threading import Thread

logger = logging.getLogger(__name__)

class SyncType(Enum):
    USER_PROFILE = "user_profile"
    TRADING_DATA = "trading_data"
    ANALYTICS = "analytics"
    ALERTS = "alerts"
    PERFORMANCE = "performance"

class SyncStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class SyncTask:
    id: str
    type: SyncType
    user_id: str
    data: Dict[str, Any]
    status: SyncStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class SupabaseOrchestrationIntegration:
    """
    Orchestrates data synchronization and coordination between ZmartyBrain and ZmartBot
    """
    
    def __init__(self):
        # ZmartyBrain configuration
        self.brain_url = "https://xhskmqsgtdhehzlvtuns.supabase.co"
        self.brain_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw"
        
        # ZmartBot configuration
        self.bot_url = "https://asjtxrmftmutcsnqgidy.supabase.co"
        self.bot_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM"
        
        # Initialize clients
        self.brain_client: Optional[Client] = None
        self.bot_client: Optional[Client] = None
        
        # Sync management
        self.sync_queue: List[SyncTask] = []
        self.active_syncs: Dict[str, SyncTask] = {}
        self.sync_history: List[SyncTask] = []
        
        # Configuration
        self.config = {
            "sync_interval": 300,  # 5 minutes
            "max_concurrent_syncs": 5,
            "retry_attempts": 3,
            "sync_timeout": 30
        }
        
        # Background sync thread
        self.sync_thread = None
        self.is_running = False
        
        self._initialize_clients()
        self._setup_sync_tables()
    
    def _initialize_clients(self):
        """Initialize Supabase clients for both projects"""
        try:
            self.brain_client = create_client(self.brain_url, self.brain_key)
            self.bot_client = create_client(self.bot_url, self.bot_key)
            logger.info("✅ Supabase Orchestration Integration initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase clients: {e}")
            raise
    
    async def _setup_sync_tables(self):
        """Set up sync tracking tables in both projects"""
        try:
            # Create sync_logs table in ZmartBot
            sync_table_sql = """
            CREATE TABLE IF NOT EXISTS sync_logs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                sync_type VARCHAR(50) NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                source_project VARCHAR(50) NOT NULL,
                target_project VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                data JSONB DEFAULT '{}',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                retry_count INTEGER DEFAULT 0
            );
            
            CREATE INDEX IF NOT EXISTS idx_sync_logs_user_id ON sync_logs(user_id);
            CREATE INDEX IF NOT EXISTS idx_sync_logs_status ON sync_logs(status);
            CREATE INDEX IF NOT EXISTS idx_sync_logs_created_at ON sync_logs(created_at);
            """
            
            # Execute in ZmartBot
            response = self.bot_client.rpc('exec_sql', {'sql': sync_table_sql}).execute()
            logger.info("✅ Sync tracking tables created")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create sync tables: {e}")
    
    async def start_orchestration(self):
        """Start the orchestration service"""
        if self.is_running:
            logger.warning("⚠️ Orchestration already running")
            return
        
        self.is_running = True
        self.sync_thread = Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()
        logger.info("🚀 Supabase Orchestration Integration started")
    
    async def stop_orchestration(self):
        """Stop the orchestration service"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        logger.info("🛑 Supabase Orchestration Integration stopped")
    
    def _sync_worker(self):
        """Background worker for processing sync tasks"""
        while self.is_running:
            try:
                # Process pending syncs
                self._process_sync_queue()
                
                # Schedule periodic syncs
                self._schedule_periodic_syncs()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Sync worker error: {e}")
                time.sleep(60)
    
    def _process_sync_queue(self):
        """Process pending sync tasks"""
        if len(self.active_syncs) >= self.config["max_concurrent_syncs"]:
            return
        
        # Get next pending task
        pending_tasks = [task for task in self.sync_queue if task.status == SyncStatus.PENDING]
        if not pending_tasks:
            return
        
        task = pending_tasks[0]
        self.sync_queue.remove(task)
        
        # Process task asynchronously
        asyncio.create_task(self._process_sync_task(task))
    
    async def _process_sync_task(self, task: SyncTask):
        """Process a single sync task"""
        task.status = SyncStatus.IN_PROGRESS
        self.active_syncs[task.id] = task
        
        try:
            # Execute sync based on type
            if task.type == SyncType.USER_PROFILE:
                await self._sync_user_profile(task)
            elif task.type == SyncType.TRADING_DATA:
                await self._sync_trading_data(task)
            elif task.type == SyncType.ANALYTICS:
                await self._sync_analytics(task)
            elif task.type == SyncType.ALERTS:
                await self._sync_alerts(task)
            elif task.type == SyncType.PERFORMANCE:
                await self._sync_performance(task)
            
            task.status = SyncStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # Log successful sync
            await self._log_sync_result(task)
            
        except Exception as e:
            task.status = SyncStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            
            logger.error(f"❌ Sync task {task.id} failed: {e}")
            await self._log_sync_result(task)
        
        finally:
            # Remove from active syncs and add to history
            if task.id in self.active_syncs:
                del self.active_syncs[task.id]
            self.sync_history.append(task)
    
    async def _sync_user_profile(self, task: SyncTask):
        """Sync user profile data between projects"""
        user_id = task.user_id
        data = task.data
        
        try:
            # Get user data from ZmartyBrain
            brain_user = await self._get_brain_user(user_id)
            if not brain_user:
                raise Exception("User not found in ZmartyBrain")
            
            # Update user profile in ZmartBot
            bot_profile = {
                "user_id": user_id,
                "email": brain_user.get("email"),
                "tier": brain_user.get("subscription_tier", "free"),
                "engagement_score": brain_user.get("engagement_score", 0.5),
                "credits_balance": brain_user.get("credits_balance", 0),
                "last_active": brain_user.get("last_active"),
                "updated_at": datetime.now().isoformat()
            }
            
            # Upsert profile in ZmartBot
            response = self.bot_client.table("user_profiles").upsert(bot_profile).execute()
            
            logger.info(f"✅ User profile synced for {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to sync user profile for {user_id}: {e}")
            raise
    
    async def _sync_trading_data(self, task: SyncTask):
        """Sync trading data and update user engagement"""
        user_id = task.user_id
        
        try:
            # Get recent trading activity from ZmartBot
            recent_trades = await self._get_recent_trades(user_id, days=7)
            
            if recent_trades:
                # Calculate trading engagement metrics
                trading_engagement = self._calculate_trading_engagement(recent_trades)
                
                # Update engagement score in ZmartyBrain
                await self._update_brain_engagement(user_id, trading_engagement)
                
                logger.info(f"✅ Trading data synced for {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to sync trading data for {user_id}: {e}")
            raise
    
    async def _sync_analytics(self, task: SyncTask):
        """Sync analytics data between projects"""
        user_id = task.user_id
        
        try:
            # Get analytics from both projects
            brain_analytics = await self._get_brain_analytics(user_id)
            bot_analytics = await self._get_bot_analytics(user_id)
            
            # Create unified analytics record
            unified_analytics = {
                "user_id": user_id,
                "brain_analytics": brain_analytics,
                "bot_analytics": bot_analytics,
                "unified_insights": self._generate_unified_insights(brain_analytics, bot_analytics),
                "generated_at": datetime.now().isoformat()
            }
            
            # Store in ZmartBot analytics table
            response = self.bot_client.table("unified_analytics").upsert(unified_analytics).execute()
            
            logger.info(f"✅ Analytics synced for {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to sync analytics for {user_id}: {e}")
            raise
    
    async def _sync_alerts(self, task: SyncTask):
        """Sync alerts between projects"""
        user_id = task.user_id
        
        try:
            # Get alerts from ZmartBot
            bot_alerts = await self._get_bot_alerts(user_id)
            
            # Create engagement alerts in ZmartyBrain
            for alert in bot_alerts:
                if alert.get("priority") == "high":
                    await self._create_brain_alert(user_id, alert)
            
            logger.info(f"✅ Alerts synced for {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to sync alerts for {user_id}: {e}")
            raise
    
    async def _sync_performance(self, task: SyncTask):
        """Sync performance metrics between projects"""
        user_id = task.user_id
        
        try:
            # Get performance data from ZmartBot
            performance_data = await self._get_bot_performance(user_id)
            
            # Update performance metrics in ZmartyBrain
            await self._update_brain_performance(user_id, performance_data)
            
            logger.info(f"✅ Performance synced for {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to sync performance for {user_id}: {e}")
            raise
    
    def _schedule_periodic_syncs(self):
        """Schedule periodic synchronization tasks"""
        # This would implement scheduled syncs for different data types
        # For now, it's a placeholder for future implementation
        pass
    
    async def queue_sync_task(self, sync_type: SyncType, user_id: str, data: Dict[str, Any] = None) -> str:
        """Queue a new sync task"""
        task_id = str(uuid.uuid4())
        task = SyncTask(
            id=task_id,
            type=sync_type,
            user_id=user_id,
            data=data or {},
            status=SyncStatus.PENDING,
            created_at=datetime.now()
        )
        
        self.sync_queue.append(task)
        logger.info(f"📋 Queued sync task {task_id} for user {user_id}")
        
        return task_id
    
    async def get_sync_status(self, task_id: str) -> Optional[SyncTask]:
        """Get status of a sync task"""
        # Check active syncs
        if task_id in self.active_syncs:
            return self.active_syncs[task_id]
        
        # Check history
        for task in self.sync_history:
            if task.id == task_id:
                return task
        
        return None
    
    async def get_user_sync_history(self, user_id: str, limit: int = 50) -> List[SyncTask]:
        """Get sync history for a user"""
        user_tasks = [task for task in self.sync_history if task.user_id == user_id]
        return sorted(user_tasks, key=lambda x: x.created_at, reverse=True)[:limit]
    
    # Helper methods for data retrieval and updates
    
    async def _get_brain_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data from ZmartyBrain"""
        try:
            response = self.brain_client.table("users").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"❌ Failed to get brain user: {e}")
            return None
    
    async def _get_recent_trades(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent trades from ZmartBot"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            response = self.bot_client.table("trades").select("*").eq("user_id", user_id).gte("timestamp", cutoff_date).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"❌ Failed to get recent trades: {e}")
            return []
    
    def _calculate_trading_engagement(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trading engagement metrics"""
        if not trades:
            return {"engagement_score": 0.0, "activity_level": "low"}
        
        # Calculate metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.get("pnl", 0) > 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Calculate engagement score (0-1)
        engagement_score = min(1.0, (total_trades / 10) * 0.5 + win_rate * 0.5)
        
        # Determine activity level
        if total_trades >= 10:
            activity_level = "high"
        elif total_trades >= 5:
            activity_level = "medium"
        else:
            activity_level = "low"
        
        return {
            "engagement_score": engagement_score,
            "activity_level": activity_level,
            "total_trades": total_trades,
            "win_rate": win_rate
        }
    
    async def _update_brain_engagement(self, user_id: str, engagement_data: Dict[str, Any]):
        """Update engagement data in ZmartyBrain"""
        try:
            update_data = {
                "engagement_score": engagement_data.get("engagement_score", 0.5),
                "last_active": datetime.now().isoformat()
            }
            
            response = self.brain_client.table("users").update(update_data).eq("id", user_id).execute()
            logger.info(f"✅ Updated brain engagement for {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update brain engagement: {e}")
            raise
    
    async def _get_brain_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics data from ZmartyBrain"""
        try:
            response = self.brain_client.table("users").select("*").eq("id", user_id).execute()
            user_data = response.data[0] if response.data else {}
            
            return {
                "engagement_score": user_data.get("engagement_score", 0.5),
                "credits_balance": user_data.get("credits_balance", 0),
                "subscription_tier": user_data.get("subscription_tier", "free"),
                "last_active": user_data.get("last_active")
            }
        except Exception as e:
            logger.error(f"❌ Failed to get brain analytics: {e}")
            return {}
    
    async def _get_bot_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics data from ZmartBot"""
        try:
            # Get trading performance
            trades = await self._get_recent_trades(user_id, days=30)
            performance = self._calculate_trading_engagement(trades)
            
            return {
                "trading_performance": performance,
                "total_trades": len(trades),
                "recent_activity": len(await self._get_recent_trades(user_id, days=7))
            }
        except Exception as e:
            logger.error(f"❌ Failed to get bot analytics: {e}")
            return {}
    
    def _generate_unified_insights(self, brain_analytics: Dict[str, Any], bot_analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate unified insights from both analytics"""
        brain_engagement = brain_analytics.get("engagement_score", 0.5)
        bot_engagement = bot_analytics.get("trading_performance", {}).get("engagement_score", 0.0)
        
        # Calculate correlation
        correlation = abs(brain_engagement - bot_engagement)
        
        return {
            "engagement_correlation": correlation,
            "overall_engagement": (brain_engagement + bot_engagement) / 2,
            "insights": [
                "User engagement correlates with trading activity",
                "Platform usage drives trading performance"
            ]
        }
    
    async def _get_bot_alerts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get alerts from ZmartBot"""
        try:
            response = self.bot_client.table("smart_alerts").select("*").eq("user_id", user_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"❌ Failed to get bot alerts: {e}")
            return []
    
    async def _create_brain_alert(self, user_id: str, alert_data: Dict[str, Any]):
        """Create alert in ZmartyBrain"""
        try:
            # This would create an alert in ZmartyBrain
            # For now, just log it
            logger.info(f"📢 High priority alert for {user_id}: {alert_data.get('message', 'Unknown')}")
        except Exception as e:
            logger.error(f"❌ Failed to create brain alert: {e}")
    
    async def _get_bot_performance(self, user_id: str) -> Dict[str, Any]:
        """Get performance data from ZmartBot"""
        try:
            trades = await self._get_recent_trades(user_id, days=30)
            return self._calculate_trading_engagement(trades)
        except Exception as e:
            logger.error(f"❌ Failed to get bot performance: {e}")
            return {}
    
    async def _update_brain_performance(self, user_id: str, performance_data: Dict[str, Any]):
        """Update performance data in ZmartyBrain"""
        try:
            # This would update performance metrics in ZmartyBrain
            # For now, just log it
            logger.info(f"📊 Updated performance for {user_id}: {performance_data}")
        except Exception as e:
            logger.error(f"❌ Failed to update brain performance: {e}")
    
    async def _log_sync_result(self, task: SyncTask):
        """Log sync result to database"""
        try:
            log_data = {
                "sync_type": task.type.value,
                "user_id": task.user_id,
                "source_project": "zmartbot",
                "target_project": "zmartybrain",
                "status": task.status.value,
                "data": task.data,
                "error_message": task.error_message,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "retry_count": 0
            }
            
            response = self.bot_client.table("sync_logs").insert(log_data).execute()
            
        except Exception as e:
            logger.error(f"❌ Failed to log sync result: {e}")

# FastAPI integration
app = FastAPI(title="Supabase Orchestration Integration", version="1.0.0")
orchestration_service = SupabaseOrchestrationIntegration()

@app.on_event("startup")
async def startup_event():
    """Start orchestration service on startup"""
    await orchestration_service.start_orchestration()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop orchestration service on shutdown"""
    await orchestration_service.stop_orchestration()

@app.post("/orchestration/sync/queue")
async def queue_sync(sync_type: str, user_id: str, data: dict = None):
    """Queue a new sync task"""
    try:
        sync_type_enum = SyncType(sync_type)
        task_id = await orchestration_service.queue_sync_task(sync_type_enum, user_id, data)
        return {"task_id": task_id, "status": "queued"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid sync type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orchestration/sync/status/{task_id}")
async def get_sync_status(task_id: str):
    """Get sync task status"""
    task = await orchestration_service.get_sync_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task.id,
        "type": task.type.value,
        "user_id": task.user_id,
        "status": task.status.value,
        "created_at": task.created_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "error_message": task.error_message
    }

@app.get("/orchestration/sync/history/{user_id}")
async def get_sync_history(user_id: str, limit: int = 50):
    """Get sync history for a user"""
    history = await orchestration_service.get_user_sync_history(user_id, limit)
    return {
        "user_id": user_id,
        "history": [
            {
                "task_id": task.id,
                "type": task.type.value,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            for task in history
        ]
    }

@app.get("/orchestration/status")
async def get_orchestration_status():
    """Get orchestration service status"""
    return {
        "is_running": orchestration_service.is_running,
        "queue_size": len(orchestration_service.sync_queue),
        "active_syncs": len(orchestration_service.active_syncs),
        "total_history": len(orchestration_service.sync_history)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8902)

