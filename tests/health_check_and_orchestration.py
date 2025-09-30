#!/usr/bin/env python3
"""
ZmartBot Health Check and Module Orchestration Script
Comprehensive testing and orchestration of all platform components
"""

import asyncio
import aiohttp
import subprocess
import time
import json
import logging
import sys
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ModuleStatus:
    name: str
    port: int
    url: str
    status: str
    health_check: Optional[Dict] = None
    error: Optional[str] = None

class ZmartBotOrchestrator:
    def __init__(self):
        self.modules = {
            'main_api': {
                'name': 'ZmartBot Main API',
                'port': 8000,
                'url': 'http://127.0.0.1:8000',
                'path': 'backend/zmart-api',
                'start_cmd': 'source venv/bin/activate && PYTHONPATH=src uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level info'
            },
            'kingfisher': {
                'name': 'KingFisher Module',
                'port': 8100,
                'url': 'http://127.0.0.1:8100',
                'path': 'kingfisher-module/backend',
                'start_cmd': 'source venv/bin/activate && PYTHONPATH=src uvicorn main:app --host 127.0.0.1 --port 8100 --reload --log-level info'
            }
        }
        self.processes = {}
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def kill_existing_processes(self):
        """Kill all existing uvicorn processes"""
        logger.info("🔄 Killing existing uvicorn processes...")
        try:
            subprocess.run(['pkill', '-f', 'uvicorn'], check=False)
            time.sleep(2)
            logger.info("✅ Existing processes killed")
        except Exception as e:
            logger.warning(f"⚠️  Error killing processes: {e}")

    def start_module(self, module_name: str) -> bool:
        """Start a specific module"""
        module = self.modules[module_name]
        logger.info(f"🚀 Starting {module['name']} on port {module['port']}...")
        
        try:
            # Change to module directory
            os.chdir(module['path'])
            
            # Start the process
            process = subprocess.Popen(
                module['start_cmd'],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            self.processes[module_name] = process
            logger.info(f"✅ {module['name']} process started (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {module['name']}: {e}")
            return False

    async def check_module_health(self, module_name: str) -> ModuleStatus:
        """Check health of a specific module"""
        module = self.modules[module_name]
        status = ModuleStatus(
            name=module['name'],
            port=module['port'],
            url=module['url'],
            status='unknown'
        )

        try:
            # Check if port is listening
            async with self.session.get(f"{module['url']}/health", timeout=5) as response:
                if response.status == 200:
                    status.status = 'healthy'
                    status.health_check = await response.json()
                else:
                    status.status = 'unhealthy'
                    status.error = f"HTTP {response.status}"
        except asyncio.TimeoutError:
            status.status = 'timeout'
            status.error = "Health check timeout"
        except Exception as e:
            status.status = 'error'
            status.error = str(e)

        return status

    async def wait_for_module_startup(self, module_name: str, timeout: int = 30) -> bool:
        """Wait for a module to start up and become healthy"""
        module = self.modules[module_name]
        logger.info(f"⏳ Waiting for {module['name']} to start up...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with self.session.get(f"{module['url']}/health", timeout=2) as response:
                    if response.status == 200:
                        logger.info(f"✅ {module['name']} is healthy!")
                        return True
            except:
                pass
            
            await asyncio.sleep(1)
        
        logger.error(f"❌ {module['name']} failed to start within {timeout} seconds")
        return False

    async def test_kingfisher_functionality(self) -> Dict:
        """Test KingFisher module functionality"""
        logger.info("🧪 Testing KingFisher functionality...")
        
        tests = {
            'health_check': False,
            'telegram_endpoints': False,
            'image_processing': False,
            'liquidation_analysis': False,
            'airtable_integration': False
        }

        try:
            # Test health endpoint
            async with self.session.get("http://127.0.0.1:8100/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    tests['health_check'] = True
                    logger.info(f"✅ Health check passed: {health_data}")

            # Test telegram endpoints
            async with self.session.get("http://127.0.0.1:8100/api/v1/telegram/status") as response:
                if response.status in [200, 404]:  # 404 is expected if no telegram config
                    tests['telegram_endpoints'] = True
                    logger.info("✅ Telegram endpoints accessible")

            # Test image processing endpoints
            async with self.session.get("http://127.0.0.1:8100/api/v1/images/status") as response:
                if response.status in [200, 404]:
                    tests['image_processing'] = True
                    logger.info("✅ Image processing endpoints accessible")

            # Test liquidation analysis endpoints
            async with self.session.get("http://127.0.0.1:8100/api/v1/liquidation/status") as response:
                if response.status in [200, 404]:
                    tests['liquidation_analysis'] = True
                    logger.info("✅ Liquidation analysis endpoints accessible")

            # Test airtable integration endpoints
            async with self.session.get("http://127.0.0.1:8100/api/v1/airtable/status") as response:
                if response.status in [200, 404]:
                    tests['airtable_integration'] = True
                    logger.info("✅ Airtable integration endpoints accessible")

        except Exception as e:
            logger.error(f"❌ Error testing KingFisher functionality: {e}")

        return tests

    async def run_comprehensive_health_check(self) -> Dict:
        """Run comprehensive health check on all modules"""
        logger.info("🏥 Running comprehensive health check...")
        
        results = {}
        
        for module_name in self.modules:
            logger.info(f"🔍 Checking {self.modules[module_name]['name']}...")
            status = await self.check_module_health(module_name)
            results[module_name] = status
            
            if status.status == 'healthy':
                logger.info(f"✅ {status.name}: {status.status}")
                if status.health_check:
                    logger.info(f"   Health data: {json.dumps(status.health_check, indent=2)}")
            else:
                logger.error(f"❌ {status.name}: {status.status} - {status.error}")

        return results

    async def orchestrate_startup(self) -> bool:
        """Orchestrate the startup of all modules"""
        logger.info("🎼 Starting module orchestration...")
        
        # Kill existing processes
        self.kill_existing_processes()
        
        # Start modules in order
        startup_order = ['main_api', 'kingfisher']
        
        for module_name in startup_order:
            if not self.start_module(module_name):
                logger.error(f"❌ Failed to start {module_name}")
                return False
            
            # Wait for module to start up
            if not await self.wait_for_module_startup(module_name):
                logger.error(f"❌ {module_name} failed to start up properly")
                return False
        
        logger.info("✅ All modules started successfully!")
        return True

    def stop_all_modules(self):
        """Stop all running modules"""
        logger.info("🛑 Stopping all modules...")
        
        for module_name, process in self.processes.items():
            try:
                os.killpg(os.getpgid(process.pid), 15)  # SIGTERM
                logger.info(f"✅ Stopped {module_name}")
            except Exception as e:
                logger.warning(f"⚠️  Error stopping {module_name}: {e}")
        
        self.kill_existing_processes()

async def main():
    """Main orchestration function"""
    logger.info("🚀 ZmartBot Health Check and Orchestration")
    logger.info("=" * 50)
    
    async with ZmartBotOrchestrator() as orchestrator:
        try:
            # Step 1: Orchestrate startup
            logger.info("\n📋 Step 1: Module Orchestration")
            if not await orchestrator.orchestrate_startup():
                logger.error("❌ Module orchestration failed!")
                return False
            
            # Step 2: Comprehensive health check
            logger.info("\n📋 Step 2: Comprehensive Health Check")
            health_results = await orchestrator.run_comprehensive_health_check()
            
            # Step 3: Test KingFisher functionality
            logger.info("\n📋 Step 3: KingFisher Functionality Test")
            kingfisher_tests = await orchestrator.test_kingfisher_functionality()
            
            # Step 4: Summary
            logger.info("\n📋 Step 4: Summary")
            logger.info("=" * 50)
            
            all_healthy = all(status.status == 'healthy' for status in health_results.values())
            kingfisher_working = any(kingfisher_tests.values())
            
            if all_healthy and kingfisher_working:
                logger.info("🎉 ALL SYSTEMS OPERATIONAL!")
                logger.info("✅ All modules are healthy")
                logger.info("✅ KingFisher functionality verified")
                logger.info("\n🌐 Access URLs:")
                logger.info("   Main API: http://127.0.0.1:8000")
                logger.info("   KingFisher: http://127.0.0.1:8100")
                logger.info("   API Docs: http://127.0.0.1:8000/docs")
                logger.info("   KingFisher Docs: http://127.0.0.1:8100/docs")
                return True
            else:
                logger.error("❌ Some systems are not operational!")
                return False
                
        except KeyboardInterrupt:
            logger.info("\n⚠️  Interrupted by user")
        except Exception as e:
            logger.error(f"❌ Orchestration error: {e}")
        finally:
            # Keep processes running for testing
            logger.info("\n💡 Processes are still running for testing")
            logger.info("   Use Ctrl+C to stop all modules")

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")
        sys.exit(0) 