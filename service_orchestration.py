#!/usr/bin/env python3
"""
ZmartBot Service Orchestration Manager with Supabase Integration
Manages integration between core foundation services and specialized services like engagement system
Now with centralized Supabase database management for comprehensive orchestration
"""

import asyncio
import aiohttp
import json
import subprocess
import signal
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging

# Import Supabase integration
try:
    from supabase_orchestration_integration import ZmartBotOrchestrationBridge
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase integration not available - running in local mode")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ZmartOrchestration')

@dataclass
class ServiceConfig:
    name: str
    port: int
    path: str
    startup_cmd: List[str]
    health_endpoint: str
    dependencies: List[str] = None
    auto_start: bool = True
    critical: bool = False

class ServiceOrchestrator:
    def __init__(self):
        self.services = {}
        self.running_processes = {}
        self.service_status = {}
        
        # Initialize Supabase bridge if available
        self.supabase_bridge = ZmartBotOrchestrationBridge() if SUPABASE_AVAILABLE else None
        self.supabase_initialized = False
        
        # Define service configurations
        self.service_configs = {
            "zmart-foundation": ServiceConfig(
                name="zmart-foundation",
                port=8000,
                path="/Users/dansidanutz/Desktop/ZmartBot/zmart-foundation",
                startup_cmd=["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
                health_endpoint="/v1/health",
                critical=True
            ),
            "engagement-system": ServiceConfig(
                name="engagement-system", 
                port=8350,
                path="/Users/dansidanutz/Desktop/ZmartBot/engagement-system",
                startup_cmd=["python3", "engagement_startup.py"],
                health_endpoint="/health",
                dependencies=["zmart-foundation"],
                auto_start=True,
                critical=False
            ),
            "health-scheduler": ServiceConfig(
                name="health-scheduler",
                port=0,  # No port, background process
                path="/Users/dansidanutz/Desktop/ZmartBot",
                startup_cmd=["python3", "automated_health_scheduler.py"],
                health_endpoint=None,
                dependencies=["zmart-foundation", "engagement-system"],
                auto_start=True,
                critical=False
            )
        }
        
    async def check_service_health(self, service_config: ServiceConfig, max_retries: int = 3) -> bool:
        """Check if service is healthy"""
        if not service_config.health_endpoint:
            # For services without health endpoints, check if process is running
            return service_config.name in self.running_processes and \
                   self.running_processes[service_config.name].poll() is None
        
        url = f"http://localhost:{service_config.port}{service_config.health_endpoint}"
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=5) as response:
                        if response.status == 200:
                            return True
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                else:
                    logger.warning(f"Health check failed for {service_config.name}: {e}")
        
        return False

    async def initialize_supabase(self):
        """Initialize Supabase integration"""
        if self.supabase_bridge and not self.supabase_initialized:
            try:
                await self.supabase_bridge.initialize()
                self.supabase_initialized = True
                logger.info("✅ Supabase orchestration bridge initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase bridge: {e}")

    async def sync_service_to_supabase(self, service_name: str, health_status: bool = True):
        """Sync service status to Supabase"""
        if self.supabase_bridge and self.supabase_initialized:
            try:
                # Get CPU and memory usage (simplified for demo)
                import psutil
                cpu_usage = psutil.cpu_percent()
                memory_usage = psutil.virtual_memory().percent
                
                # Calculate response time based on health check
                response_time = 50 if health_status else 5000
                error_count = 0 if health_status else 1
                
                await self.supabase_bridge.sync_service_health(
                    service_name, cpu_usage, memory_usage, response_time, error_count, 100
                )
            except Exception as e:
                logger.debug(f"Failed to sync {service_name} to Supabase: {e}")

    async def get_orchestration_dashboard(self) -> Dict:
        """Get comprehensive orchestration dashboard data"""
        dashboard_data = {
            'local_services': {},
            'supabase_services': {},
            'integration_status': self.supabase_initialized
        }
        
        # Local service status
        for name, config in self.service_configs.items():
            health = await self.check_service_health(config)
            dashboard_data['local_services'][name] = {
                'status': self.service_status.get(name, 'unknown'),
                'health': health,
                'port': config.port,
                'critical': config.critical
            }
        
        # Supabase service status
        if self.supabase_bridge and self.supabase_initialized:
            try:
                supabase_data = await self.supabase_bridge.get_service_status_dashboard()
                dashboard_data['supabase_services'] = supabase_data
            except Exception as e:
                logger.error(f"Failed to get Supabase dashboard: {e}")
        
        return dashboard_data

    async def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        if service_name not in self.service_configs:
            logger.error(f"Unknown service: {service_name}")
            return False
            
        config = self.service_configs[service_name]
        
        # Check dependencies first
        if config.dependencies:
            for dep in config.dependencies:
                if not await self.check_service_health(self.service_configs[dep]):
                    logger.error(f"Cannot start {service_name}: dependency {dep} not healthy")
                    return False
        
        try:
            logger.info(f"🚀 Starting {service_name}...")
            
            # Start the process
            process = subprocess.Popen(
                config.startup_cmd,
                cwd=config.path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.running_processes[service_name] = process
            self.service_status[service_name] = "starting"
            
            # Wait for service to be ready
            if config.health_endpoint:
                await asyncio.sleep(3)  # Initial wait
                if await self.check_service_health(config, max_retries=10):
                    self.service_status[service_name] = "healthy"
                    logger.info(f"✅ {service_name} started successfully (PID: {process.pid})")
                    
                    # Sync to Supabase
                    await self.sync_service_to_supabase(service_name, True)
                    return True
                else:
                    logger.error(f"❌ {service_name} failed health check after startup")
                    self.service_status[service_name] = "unhealthy"
                    
                    # Sync unhealthy status to Supabase
                    await self.sync_service_to_supabase(service_name, False)
                    return False
            else:
                # For services without health endpoints, assume success if process started
                await asyncio.sleep(2)
                if process.poll() is None:
                    self.service_status[service_name] = "running"
                    logger.info(f"✅ {service_name} process started (PID: {process.pid})")
                    return True
                else:
                    logger.error(f"❌ {service_name} process terminated immediately")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Failed to start {service_name}: {e}")
            self.service_status[service_name] = "failed"
            return False

    async def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        if service_name not in self.running_processes:
            logger.warning(f"Service {service_name} not running")
            return True
            
        try:
            process = self.running_processes[service_name]
            logger.info(f"🛑 Stopping {service_name}...")
            
            # Graceful shutdown
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
                logger.info(f"✅ {service_name} stopped gracefully")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ Force killing {service_name}")
                process.kill()
                process.wait()
            
            del self.running_processes[service_name]
            self.service_status[service_name] = "stopped"
            return True
            
        except Exception as e:
            logger.error(f"❌ Error stopping {service_name}: {e}")
            return False

    async def start_all_services(self) -> Dict[str, bool]:
        """Start all services in dependency order"""
        logger.info("🎯 Starting ZmartBot Service Orchestration")
        results = {}
        
        # Start critical services first
        critical_services = [name for name, config in self.service_configs.items() if config.critical]
        
        for service_name in critical_services:
            results[service_name] = await self.start_service(service_name)
            if not results[service_name]:
                logger.error(f"❌ Critical service {service_name} failed to start. Aborting.")
                return results
        
        # Start non-critical services
        non_critical = [name for name, config in self.service_configs.items() 
                       if not config.critical and config.auto_start]
        
        for service_name in non_critical:
            results[service_name] = await self.start_service(service_name)
            
        return results

    async def stop_all_services(self):
        """Stop all running services"""
        logger.info("🛑 Stopping all services...")
        
        # Stop in reverse order to respect dependencies
        service_names = list(self.running_processes.keys())
        service_names.reverse()
        
        for service_name in service_names:
            await self.stop_service(service_name)

    async def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        for service_name, config in self.service_configs.items():
            is_healthy = await self.check_service_health(config)
            status["services"][service_name] = {
                "name": service_name,
                "port": config.port if config.port > 0 else None,
                "status": self.service_status.get(service_name, "unknown"),
                "healthy": is_healthy,
                "critical": config.critical,
                "pid": self.running_processes[service_name].pid if service_name in self.running_processes else None
            }
            
        return status

    async def health_monitor(self, interval_seconds: int = 30):
        """Continuous health monitoring"""
        logger.info(f"🔍 Starting health monitoring (interval: {interval_seconds}s)")
        
        while True:
            try:
                status = await self.get_service_status()
                
                # Check for unhealthy critical services
                for service_name, service_status in status["services"].items():
                    config = self.service_configs[service_name]
                    
                    if config.critical and not service_status["healthy"]:
                        logger.error(f"🚨 CRITICAL SERVICE DOWN: {service_name}")
                        # Attempt restart
                        logger.info(f"🔄 Attempting to restart {service_name}")
                        await self.start_service(service_name)
                
                # Log overall status
                healthy_services = sum(1 for s in status["services"].values() if s["healthy"])
                total_services = len(status["services"])
                logger.info(f"📊 Service Health: {healthy_services}/{total_services} healthy")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"❌ Error in health monitoring: {e}")
                await asyncio.sleep(interval_seconds)

    def signal_handler(self, sig, frame):
        """Handle interrupt signals"""
        logger.info(f"📢 Received signal {sig}, shutting down...")
        asyncio.create_task(self.stop_all_services())
        sys.exit(0)

async def main():
    """Main orchestration entry point"""
    orchestrator = ServiceOrchestrator()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, orchestrator.signal_handler)
    signal.signal(signal.SIGTERM, orchestrator.signal_handler)
    
    try:
        # Start all services
        results = await orchestrator.start_all_services()
        
        # Display results
        print("\n" + "="*60)
        print("🎯 ZMARTBOT SERVICE ORCHESTRATION RESULTS")
        print("="*60)
        
        for service_name, success in results.items():
            status_emoji = "✅" if success else "❌"
            config = orchestrator.service_configs[service_name]
            port_info = f":{config.port}" if config.port > 0 else ""
            print(f"{status_emoji} {service_name}{port_info} - {'SUCCESS' if success else 'FAILED'}")
        
        if all(results.values()):
            print("\n🎉 ALL SERVICES STARTED SUCCESSFULLY!")
            print("\n📋 Service Endpoints:")
            print("   • ZmartBot Foundation API: http://localhost:8000")
            print("   • Engagement System: http://localhost:8350")
            print("   • Health Dashboard: http://localhost:8080 (if available)")
            
            print("\n🔄 Starting continuous health monitoring...")
            
            # Start health monitoring
            await orchestrator.health_monitor(30)
        else:
            print("\n❌ Some services failed to start. Check logs above.")
            await orchestrator.stop_all_services()
            
    except Exception as e:
        logger.error(f"❌ Orchestration error: {e}")
        await orchestrator.stop_all_services()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Orchestration stopped.")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)