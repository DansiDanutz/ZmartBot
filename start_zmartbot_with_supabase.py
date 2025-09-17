#!/usr/bin/env python3
"""
ZmartBot Unified Startup with Supabase Orchestration
Complete integration of all ZmartBot services with Supabase centralized management
"""

import asyncio
import logging
import json
import sys
from datetime import datetime
from pathlib import Path

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zmartbot_supabase.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ZmartBotSupabase')

async def main():
    """Main startup routine with Supabase integration"""
    
    print("🚀 ZmartBot Supabase Orchestration Startup")
    print("=" * 60)
    
    try:
        # Import orchestration components
        from service_orchestration import ServiceOrchestrator
        from supabase_orchestration_integration import ZmartBotOrchestrationBridge
        
        # Initialize orchestrator
        orchestrator = ServiceOrchestrator()
        
        # Initialize Supabase integration
        logger.info("🔗 Initializing Supabase integration...")
        await orchestrator.initialize_supabase()
        
        # Get comprehensive dashboard before starting services
        dashboard_before = await orchestrator.get_orchestration_dashboard()
        logger.info(f"📊 Pre-startup Dashboard: {json.dumps(dashboard_before, indent=2, default=str)}")
        
        # Define startup sequence for critical services
        startup_sequence = [
            'zmart-foundation',      # Core API server
            'engagement-system',     # Engagement services  
            'health-scheduler'       # Health monitoring
        ]
        
        successful_starts = []
        failed_starts = []
        
        # Start services in sequence
        for service_name in startup_sequence:
            logger.info(f"🚀 Starting {service_name}...")
            try:
                success = await orchestrator.start_service(service_name)
                if success:
                    successful_starts.append(service_name)
                    logger.info(f"✅ {service_name} started successfully")
                else:
                    failed_starts.append(service_name)
                    logger.error(f"❌ {service_name} failed to start")
                    
                # Short delay between service starts
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error starting {service_name}: {e}")
                failed_starts.append(service_name)
        
        # Get post-startup dashboard
        dashboard_after = await orchestrator.get_orchestration_dashboard()
        
        # Print comprehensive status
        print("\n" + "=" * 60)
        print("🎯 ZmartBot Supabase Orchestration Status")
        print("=" * 60)
        
        print(f"✅ Successfully Started: {len(successful_starts)}")
        for service in successful_starts:
            print(f"   • {service}")
        
        if failed_starts:
            print(f"\n❌ Failed to Start: {len(failed_starts)}")
            for service in failed_starts:
                print(f"   • {service}")
        
        # Supabase Integration Status
        if orchestrator.supabase_initialized:
            print(f"\n🔗 Supabase Integration: ✅ Active")
            if 'supabase_services' in dashboard_after:
                supabase_data = dashboard_after['supabase_services']
                print(f"   • Total Services in DB: {supabase_data.get('total_services', 0)}")
                print(f"   • Active Services: {supabase_data.get('active_services', 0)}")
                print(f"   • Average Health Score: {supabase_data.get('avg_health_score', 0):.1f}%")
        else:
            print(f"\n🔗 Supabase Integration: ❌ Failed")
        
        # Service Types Summary
        if 'supabase_services' in dashboard_after and 'services_by_type' in dashboard_after['supabase_services']:
            print(f"\n📊 Services by Type:")
            for service_type, count in dashboard_after['supabase_services']['services_by_type'].items():
                print(f"   • {service_type}: {count}")
        
        print("\n" + "=" * 60)
        
        # Continuous monitoring loop
        if successful_starts:
            logger.info("🔄 Starting continuous monitoring...")
            await continuous_monitoring(orchestrator)
        else:
            logger.error("❌ No services started successfully - exiting")
            return False
            
    except KeyboardInterrupt:
        logger.info("👋 Graceful shutdown requested")
        return True
    except Exception as e:
        logger.error(f"💥 Critical error in main startup: {e}")
        return False

async def continuous_monitoring(orchestrator):
    """Continuous monitoring with Supabase sync"""
    monitoring_interval = 30  # seconds
    
    while True:
        try:
            # Get updated dashboard
            dashboard = await orchestrator.get_orchestration_dashboard()
            
            # Check health of all local services
            health_checks = {}
            for service_name in orchestrator.service_configs.keys():
                config = orchestrator.service_configs[service_name]
                health = await orchestrator.check_service_health(config)
                health_checks[service_name] = health
                
                # Sync to Supabase
                await orchestrator.sync_service_to_supabase(service_name, health)
            
            # Log health summary
            healthy_count = sum(1 for health in health_checks.values() if health)
            total_count = len(health_checks)
            
            logger.info(f"💓 Health Check: {healthy_count}/{total_count} services healthy")
            
            # Log Supabase sync status
            if orchestrator.supabase_initialized:
                logger.debug("🔄 Synced all service health to Supabase")
            
            await asyncio.sleep(monitoring_interval)
            
        except KeyboardInterrupt:
            logger.info("👋 Monitoring stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in monitoring loop: {e}")
            await asyncio.sleep(10)  # Short delay before retry

async def emergency_shutdown(orchestrator):
    """Emergency shutdown procedure"""
    logger.warning("🚨 Emergency shutdown initiated")
    
    # Stop all running processes
    for service_name, process in orchestrator.running_processes.items():
        try:
            logger.info(f"🛑 Stopping {service_name} (PID: {process.pid})")
            process.terminate()
            
            # Update status in Supabase
            await orchestrator.sync_service_to_supabase(service_name, False)
            
        except Exception as e:
            logger.error(f"Error stopping {service_name}: {e}")
    
    logger.info("🔄 Emergency shutdown complete")

if __name__ == "__main__":
    try:
        # Install required dependencies if missing
        try:
            import psutil
        except ImportError:
            logger.warning("Installing psutil for system monitoring...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
            import psutil
        
        # Run main startup
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)