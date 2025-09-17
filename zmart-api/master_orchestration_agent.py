#!/usr/bin/env python3
"""
ZmartBot Master Orchestration Agent
Auto-generated implementation based on MasterOrchestrationAgent.mdc

This agent ensures Cloud Sync integration and maintains continuous monitoring of:
1. Cloud Sync status through database service
2. Service health across the entire ZmartBot ecosystem
3. Orchestration coordination with OrchestrationStart
"""

import os
import sys
import time
import json
import logging
import requests
import threading
import sqlite3
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from intelligent_orchestrator import IntelligentOrchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MasterOrchestrationAgent:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.services_status = {}
        self.cloud_sync_status = "🔴 Inactive"
        self.monitoring_active = False
        self.app = None
        
        # Initialize AI-Powered Intelligent Orchestrator
        self.intelligent_orchestrator = IntelligentOrchestrator()
        self.ai_analytics_active = False
        
    def create_app(self) -> FastAPI:
        """Create FastAPI application for Master Orchestration Agent"""
        app = FastAPI(
            title="ZmartBot Master Orchestration Agent",
            description="Master coordination service for ZmartBot ecosystem with Cloud Sync integration",
            version="1.0.0"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": "master_orchestration_agent",
                "port": 8002,
                "cloud_sync_integrated": True,
                "monitoring_active": self.monitoring_active,
                "ai_analytics_active": self.ai_analytics_active,
                "intelligent_features": True,
                "timestamp": datetime.now().isoformat()
            }
        
        @app.get("/api/status/overview")
        async def get_status_overview():
            """Get comprehensive status overview including Cloud Sync and AI Intelligence"""
            # Get AI intelligence if available
            ai_summary = None
            try:
                if self.ai_analytics_active:
                    ai_summary = self.intelligent_orchestrator.get_system_intelligence_summary()
            except:
                ai_summary = None
            
            return {
                "agent_status": "active",
                "cloud_sync_status": self.cloud_sync_status,
                "services_monitored": len(self.services_status),
                "database_service_status": self.check_database_service_status(),
                "supabase_key_configured": bool(os.getenv("SUPABASE_KEY")),
                "monitoring_active": self.monitoring_active,
                "ai_analytics_active": self.ai_analytics_active,
                "ai_intelligence": ai_summary,
                "intelligent_orchestration": True,
                "last_updated": datetime.now().isoformat()
            }
        
        @app.post("/api/status/cloud_sync")
        async def receive_cloud_sync_status(status_data: dict):
            """Receive Cloud Sync status updates from OrchestrationStart"""
            try:
                self.cloud_sync_status = status_data.get("status", "🔴 Unknown")
                logger.info(f"📊 Received Cloud Sync status update: {self.cloud_sync_status}")
                return {"status": "received", "cloud_sync_status": self.cloud_sync_status}
            except Exception as e:
                logger.error(f"❌ Error processing Cloud Sync status: {e}")
                raise HTTPException(status_code=500, detail="Failed to process status")
        
        @app.get("/api/services/status")
        async def get_services_status():
            """Get status of all monitored services"""
            return {
                "services": self.services_status,
                "total_services": len(self.services_status),
                "timestamp": datetime.now().isoformat()
            }
        
        @app.get("/api/ai/intelligence")
        async def get_ai_intelligence():
            """Get AI intelligence summary and predictions"""
            try:
                intelligence_summary = self.intelligent_orchestrator.get_system_intelligence_summary()
                return {
                    "status": "success",
                    "ai_analytics_active": self.ai_analytics_active,
                    "intelligence_summary": intelligence_summary,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"❌ Error getting AI intelligence: {e}")
                raise HTTPException(status_code=500, detail="AI intelligence service error")
        
        @app.get("/api/ai/predictions")
        async def get_ai_predictions():
            """Get recent AI predictions"""
            try:
                predictions = self.intelligent_orchestrator.get_recent_predictions(limit=20)
                return {
                    "status": "success",
                    "predictions": predictions,
                    "total_predictions": len(predictions),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"❌ Error getting AI predictions: {e}")
                raise HTTPException(status_code=500, detail="AI predictions service error")
        
        @app.get("/api/ai/trading-opportunities")
        async def get_trading_opportunities():
            """Get AI-detected trading opportunities"""
            try:
                opportunities = self.intelligent_orchestrator.get_recent_trading_opportunities(limit=10)
                return {
                    "status": "success",
                    "trading_opportunities": opportunities,
                    "total_opportunities": len(opportunities),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"❌ Error getting trading opportunities: {e}")
                raise HTTPException(status_code=500, detail="Trading opportunities service error")
        
        @app.post("/api/ai/start")
        async def start_ai_analytics():
            """Start AI analytics engine"""
            try:
                if not self.ai_analytics_active:
                    self.intelligent_orchestrator.start_analytics_engine()
                    self.ai_analytics_active = True
                    logger.info("🤖 AI Analytics Engine started")
                    return {
                        "status": "success",
                        "message": "AI Analytics Engine started successfully",
                        "ai_active": True
                    }
                else:
                    return {
                        "status": "info",
                        "message": "AI Analytics Engine already running",
                        "ai_active": True
                    }
            except Exception as e:
                logger.error(f"❌ Error starting AI analytics: {e}")
                raise HTTPException(status_code=500, detail="Failed to start AI analytics")
        
        @app.post("/api/ai/stop")
        async def stop_ai_analytics():
            """Stop AI analytics engine"""
            try:
                if self.ai_analytics_active:
                    self.intelligent_orchestrator.stop_analytics_engine()
                    self.ai_analytics_active = False
                    logger.info("🛑 AI Analytics Engine stopped")
                    return {
                        "status": "success",
                        "message": "AI Analytics Engine stopped successfully",
                        "ai_active": False
                    }
                else:
                    return {
                        "status": "info",
                        "message": "AI Analytics Engine already stopped",
                        "ai_active": False
                    }
            except Exception as e:
                logger.error(f"❌ Error stopping AI analytics: {e}")
                raise HTTPException(status_code=500, detail="Failed to stop AI analytics")
        
        @app.get("/api/ziva/integrity")
        async def get_ziva_integrity_status():
            """Get system integrity status from ZIVA Agent"""
            try:
                response = requests.get("http://127.0.0.1:8930/api/consistency/report", timeout=5)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(status_code=503, detail="ZIVA Agent not accessible")
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"ZIVA Agent error: {str(e)}")
        
        @app.get("/api/ziva/violations")
        async def get_ziva_violations():
            """Get critical violations from ZIVA Agent"""
            try:
                response = requests.get("http://127.0.0.1:8930/api/violations/critical", timeout=5)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(status_code=503, detail="ZIVA Agent not accessible")
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"ZIVA Agent error: {str(e)}")
        
        @app.post("/api/ziva/fix")
        async def trigger_ziva_autofix():
            """Trigger ZIVA Agent auto-fix for violations"""
            try:
                response = requests.post("http://127.0.0.1:8930/api/violations/fix", timeout=10)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(status_code=503, detail="ZIVA Agent not accessible")
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"ZIVA Agent error: {str(e)}")
        
        @app.get("/api/lifecycle/status")
        async def get_lifecycle_status():
            """Get service lifecycle status from ServiceLifecycleManager"""
            try:
                response = requests.get("http://127.0.0.1:8920/api/lifecycle/validate", timeout=5)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(status_code=503, detail="ServiceLifecycleManager not accessible")
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"ServiceLifecycleManager error: {str(e)}")
        
        self.app = app
        return app
    
    def check_database_service_status(self):
        """Check if database service (with Cloud Sync) is healthy"""
        try:
            response = requests.get("http://127.0.0.1:8900/health", timeout=3)
            if response.status_code == 200:
                return "✅ Running"
            else:
                return "⚠️ Issues"
        except:
            return "❌ Not Accessible"
    
    def monitor_cloud_sync_status(self):
        """Continuously monitor Cloud Sync status"""
        try:
            response = requests.get("http://127.0.0.1:8900/api/system/overview", timeout=5)
            if response.status_code == 200:
                data = response.json()
                cloud_sync_info = data.get("cloud_sync", {})
                status = cloud_sync_info.get("status", "🔴 Inactive")
                
                if status != self.cloud_sync_status:
                    logger.info(f"🔄 Cloud Sync status changed: {self.cloud_sync_status} → {status}")
                    self.cloud_sync_status = status
                
                return status
        except Exception as e:
            logger.warning(f"⚠️ Could not check Cloud Sync status: {e}")
            return "🔴 Error"
    
    def get_level3_certified_services(self):
        """Get Level 3 CERTIFIED services from service_registry.db with their ports from passport_registry.db"""
        try:
            # Get certified services from service_registry.db
            from src.config.database_config import get_master_database_connection
            service_registry_conn = get_master_database_connection()
            service_cursor = service_registry_conn.cursor()
            
            service_cursor.execute("""
                SELECT service_name FROM services 
                WHERE certified = 1 AND status = 'REGISTERED'
            """)
            certified_services = [row[0] for row in service_cursor.fetchall()]
            service_registry_conn.close()
            
            # Get port information from passport_registry.db
            passport_conn = sqlite3.connect("data/passport_registry.db")
            passport_cursor = passport_conn.cursor()
            
            level3_services = {}
            for service_name in certified_services:
                passport_cursor.execute("""
                    SELECT port, service_type FROM passport_registry 
                    WHERE service_name = ? AND status = 'ACTIVE'
                """, (service_name,))
                passport_result = passport_cursor.fetchone()
                
                if passport_result:
                    # Service has active passport with port
                    port, service_type = passport_result
                    is_critical = service_type in ["security", "orchestration", "infrastructure"] or service_name in [
                        "database_service", "service_lifecycle_manager", "ziva_agent", "master_orchestration_agent"
                    ]
                    
                    level3_services[service_name] = {
                        "port": port, 
                        "critical": is_critical,
                        "service_type": service_type,
                        "status": "active_with_port"
                    }
                else:
                    # Level 3 service without active passport - still track for monitoring
                    level3_services[service_name] = {
                        "port": None, 
                        "critical": False,
                        "service_type": "certified_service",
                        "status": "certified_no_port"
                    }
            
            passport_conn.close()
            return level3_services
            
        except Exception as e:
            logger.error(f"❌ Error loading Level 3 certified services: {e}")
            # Fallback to essential services if database read fails
            return {
                "database_service": {"port": 8900, "critical": True, "service_type": "infrastructure"},
                "service_lifecycle_manager": {"port": 8920, "critical": True, "service_type": "infrastructure"},
                "ziva_agent": {"port": 8930, "critical": True, "service_type": "infrastructure"}
            }

    def monitor_core_services(self):
        """Monitor Level 3 CERTIFIED services only for Master Orchestration"""
        logger.info("🏆 Loading Level 3 CERTIFIED services for orchestration monitoring...")
        core_services = self.get_level3_certified_services()
        logger.info(f"📊 Monitoring {len(core_services)} Level 3 CERTIFIED services")
        
        for service_name, config in core_services.items():
            try:
                response = requests.get(f"http://127.0.0.1:{config['port']}/health", timeout=3)
                if response.status_code == 200:
                    self.services_status[service_name] = {
                        "status": "✅ Running",
                        "port": config['port'],
                        "last_checked": datetime.now().isoformat()
                    }
                else:
                    self.services_status[service_name] = {
                        "status": "⚠️ Issues",
                        "port": config['port'],
                        "last_checked": datetime.now().isoformat()
                    }
            except:
                self.services_status[service_name] = {
                    "status": "❌ Not Accessible",
                    "port": config['port'],
                    "last_checked": datetime.now().isoformat()
                }
    
    def background_monitoring(self):
        """Background monitoring thread"""
        logger.info("🔄 Starting background monitoring...")
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # Monitor Cloud Sync status every 30 seconds
                self.monitor_cloud_sync_status()
                
                # Monitor core services every minute
                self.monitor_core_services()
                
                # Check if OrchestrationStart needs to be notified about anything critical
                self.check_critical_status()
                
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in background monitoring: {e}")
                time.sleep(30)
    
    def check_critical_status(self):
        """Check for critical status changes that need attention"""
        # If Cloud Sync goes down, log it
        if "🔴" in self.cloud_sync_status:
            if not hasattr(self, '_cloud_sync_warning_logged'):
                logger.warning("⚠️ CRITICAL: Cloud Sync is inactive - check SUPABASE_KEY configuration")
                self._cloud_sync_warning_logged = True
        else:
            if hasattr(self, '_cloud_sync_warning_logged'):
                logger.info("✅ Cloud Sync restored to active status")
                delattr(self, '_cloud_sync_warning_logged')
        
        # Check if database service is down (critical for Cloud Sync)
        db_status = self.services_status.get("database_service", {}).get("status", "❌ Unknown")
        if "❌" in db_status:
            logger.error("🚨 CRITICAL: Database Service is down - Cloud Sync will be affected!")
        
        # Check if ZIVA Agent is down (critical for system integrity)
        ziva_status = self.services_status.get("ziva_agent", {}).get("status", "❌ Unknown")
        if "❌" in ziva_status:
            logger.error("🚨 CRITICAL: ZIVA Agent is down - System integrity monitoring disabled!")
            
        # Check if ServiceLifecycleManager is down (critical for service management)
        lifecycle_status = self.services_status.get("service_lifecycle_manager", {}).get("status", "❌ Unknown")
        if "❌" in lifecycle_status:
            logger.error("🚨 CRITICAL: ServiceLifecycleManager is down - Service lifecycle validation disabled!")
    
    def start_agent(self):
        """Start the Master Orchestration Agent with AI Intelligence"""
        logger.info("🎯 Starting Master Orchestration Agent")
        logger.info("🎯 Focus: Cloud Sync Integration and AI-Powered System Coordination")
        
        print("\n" + "="*70)
        print("🤖 MASTER ORCHESTRATION AGENT - AI ENHANCED")
        print("="*70)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Mission: Maintain Cloud Sync Integration + AI Intelligence")
        print("🔗 Integration: OrchestrationStart coordination")
        print("🧠 AI Features: Predictive Analytics, Performance Optimization")
        print("-"*70)
        
        # Start AI Analytics Engine
        try:
            self.intelligent_orchestrator.start_analytics_engine()
            self.ai_analytics_active = True
            print("🚀 AI Analytics Engine: STARTED")
        except Exception as e:
            logger.warning(f"⚠️ Could not start AI Analytics Engine: {e}")
            print("⚠️ AI Analytics Engine: FAILED TO START")
        
        # Start background monitoring
        monitoring_thread = threading.Thread(target=self.background_monitoring, daemon=True)
        monitoring_thread.start()
        
        # Initial status check
        self.monitor_cloud_sync_status()
        self.monitor_core_services()
        
        # Print initial status
        print(f"📊 Database Service: {self.check_database_service_status()}")
        print(f"📊 Cloud Sync Status: {self.cloud_sync_status}")
        print(f"📊 SUPABASE_KEY: {'✅ Configured' if os.getenv('SUPABASE_KEY') else '❌ Not Set'}")
        print(f"🧠 AI Analytics: {'✅ Active' if self.ai_analytics_active else '❌ Inactive'}")
        
        # Display initial AI intelligence if available
        if self.ai_analytics_active:
            try:
                ai_summary = self.intelligent_orchestrator.get_system_intelligence_summary()
                print(f"🎯 System Health: {ai_summary.get('system_health', 0):.2f}")
                print(f"📈 Active Predictions: {len(ai_summary.get('recent_predictions', []))}")
                print(f"💹 Trading Opportunities: {len(ai_summary.get('trading_opportunities', []))}")
            except:
                print("🧠 AI Intelligence: Initializing...")
        
        print("-"*70)
        print("✅ Master Orchestration Agent is active and monitoring")
        print("🔄 Background monitoring started (30-second intervals)")
        print("🧠 AI predictive analytics running (60-second cycles)")
        print("🌐 API available at http://127.0.0.1:8002")
        print("🎯 New AI Endpoints:")
        print("   • /api/ai/intelligence - AI intelligence summary")
        print("   • /api/ai/predictions - ML predictions")
        print("   • /api/ai/trading-opportunities - Trading insights")
        print("="*70)
        
        # Create and start FastAPI app
        app = self.create_app()
        
        # Start the server
        try:
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=8002,
                log_level="info",
                access_log=False
            )
        except Exception as e:
            logger.error(f"❌ Failed to start Master Orchestration Agent: {e}")
            self.monitoring_active = False
            return False
    
    def stop_agent(self):
        """Stop the agent gracefully"""
        logger.info("🛑 Stopping Master Orchestration Agent...")
        self.monitoring_active = False
        
        # Stop AI Analytics Engine
        if self.ai_analytics_active:
            try:
                self.intelligent_orchestrator.stop_analytics_engine()
                self.ai_analytics_active = False
                logger.info("🧠 AI Analytics Engine stopped")
            except Exception as e:
                logger.warning(f"⚠️ Error stopping AI Analytics Engine: {e}")
        
        print("🛑 Master Orchestration Agent stopped")
        print("🧠 AI Analytics Engine stopped")

def main():
    """Main entry point"""
    agent = MasterOrchestrationAgent()
    
    try:
        agent.start_agent()
    except KeyboardInterrupt:
        logger.info("🛑 Master Orchestration Agent interrupted by user")
        agent.stop_agent()
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error in Master Orchestration Agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()