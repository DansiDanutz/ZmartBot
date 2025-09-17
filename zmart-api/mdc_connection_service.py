#!/usr/bin/env python3
"""
MDC Connection Service - Background Service
Runs the MDC Connection Agent as a continuous background service
Monitors .cursor/rules directory and maintains MDC connections automatically
"""

import os
import sys
import time
import signal
import logging
import asyncio
from pathlib import Path
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.mdc_connection_agent import MDCConnectionAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/mdc_service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MDCConnectionService:
    """
    Background service for MDC Connection Agent
    """
    
    def __init__(self):
        self.agent = None
        self.running = False
        self.pid_file = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/mdc_service.pid')
        self.status_file = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/mdc_service_status.json')
        self.mdc_directory = "/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules"
        
        # Configuration
        self.scan_interval = 3600  # 1 hour
        self.auto_connect_new_files = True
        self.use_llm = True  # Set to False for rule-based only
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}. Shutting down...")
        self.stop()
    
    def start(self):
        """Start the background service"""
        try:
            # Check if already running
            if self._is_already_running():
                logger.error("Service is already running!")
                return False
            
            # Write PID file
            self._write_pid_file()
            
            # Initialize agent
            openai_key = os.getenv('OPENAI_API_KEY') if self.use_llm else None
            self.agent = MDCConnectionAgent(self.mdc_directory, openai_key)
            
            # Start file watcher
            self.agent.start_watching()
            
            self.running = True
            logger.info("🚀 MDC Connection Service started successfully")
            
            # Update status
            self._update_status("running", "Service started successfully")
            
            # Run main service loop
            asyncio.run(self._service_loop())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start service: {e}")
            self._update_status("error", str(e))
            return False
    
    def stop(self):
        """Stop the background service"""
        try:
            self.running = False
            
            if self.agent:
                self.agent.stop_watching()
                logger.info("File watcher stopped")
            
            # Clean up PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            # Update status
            self._update_status("stopped", "Service stopped")
            
            logger.info("🛑 MDC Connection Service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping service: {e}")
    
    async def _service_loop(self):
        """Main service loop"""
        logger.info("Starting service loop...")
        
        # Initial full analysis
        await self._perform_initial_analysis()
        
        last_full_scan = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Periodic full scan
                if current_time - last_full_scan >= self.scan_interval:
                    logger.info("⏰ Performing scheduled full scan...")
                    await self._perform_full_scan()
                    last_full_scan = current_time
                
                # Update service status
                self._update_service_stats()
                
                # Sleep for a short interval
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in service loop: {e}")
                await asyncio.sleep(60)
    
    async def _perform_initial_analysis(self):
        """Perform initial analysis on startup"""
        try:
            logger.info("🔍 Performing initial analysis...")
            
            # Analyze all services first
            await self.agent.analyze_all_services()
            
            # Discover connections for all services
            connections = await self.agent.discover_all_connections()
            
            total_connections = sum(len(conns) for conns in connections.values())
            logger.info(f"✅ Initial analysis complete: {len(connections)} services, {total_connections} connections")
            
            # Update status
            self._update_status("running", f"Initial analysis complete: {total_connections} connections discovered")
            
        except Exception as e:
            logger.error(f"Error in initial analysis: {e}")
            self._update_status("error", f"Initial analysis failed: {str(e)}")
    
    async def _perform_full_scan(self):
        """Perform full scan of all MDC files"""
        try:
            logger.info("🔄 Starting full scan...")
            
            # Re-discover all connections
            connections = await self.agent.discover_all_connections()
            
            total_connections = sum(len(conns) for conns in connections.values())
            logger.info(f"✅ Full scan complete: {len(connections)} services, {total_connections} connections")
            
            # Update status
            self._update_status("running", f"Full scan complete: {total_connections} connections")
            
        except Exception as e:
            logger.error(f"Error in full scan: {e}")
    
    def _is_already_running(self):
        """Check if service is already running"""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            try:
                os.kill(pid, 0)  # Send signal 0 to check if process exists
                return True
            except OSError:
                # Process doesn't exist, clean up stale PID file
                self.pid_file.unlink()
                return False
                
        except Exception:
            return False
    
    def _write_pid_file(self):
        """Write PID to file"""
        pid = os.getpid()
        with open(self.pid_file, 'w') as f:
            f.write(str(pid))
        logger.info(f"PID {pid} written to {self.pid_file}")
    
    def _update_status(self, status: str, message: str = ""):
        """Update service status file"""
        try:
            status_data = {
                "status": status,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "pid": os.getpid() if self.running else None,
                "mdc_directory": self.mdc_directory,
                "scan_interval": self.scan_interval,
                "use_llm": self.use_llm
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    def _update_service_stats(self):
        """Update service statistics"""
        try:
            if self.agent:
                stats = self.agent.get_connection_stats()
                
                status_data = {
                    "status": "running",
                    "message": "Service healthy",
                    "timestamp": datetime.now().isoformat(),
                    "pid": os.getpid(),
                    "mdc_directory": self.mdc_directory,
                    "scan_interval": self.scan_interval,
                    "use_llm": self.use_llm,
                    "stats": stats
                }
                
                with open(self.status_file, 'w') as f:
                    json.dump(status_data, f, indent=2)
                    
        except Exception as e:
            logger.error(f"Error updating service stats: {e}")
    
    def get_status(self):
        """Get current service status"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    return json.load(f)
            return {"status": "unknown", "message": "Status file not found"}
        except Exception as e:
            return {"status": "error", "message": f"Error reading status: {e}"}

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MDC Connection Service')
    parser.add_argument('action', choices=['start', 'stop', 'status', 'restart'], 
                       help='Action to perform')
    parser.add_argument('--no-llm', action='store_true', 
                       help='Disable LLM analysis (rule-based only)')
    parser.add_argument('--scan-interval', type=int, default=3600,
                       help='Scan interval in seconds (default: 3600)')
    
    args = parser.parse_args()
    
    service = MDCConnectionService()
    
    # Apply configuration
    if args.no_llm:
        service.use_llm = False
        logger.info("LLM analysis disabled - using rule-based connections only")
    
    service.scan_interval = args.scan_interval
    logger.info(f"Scan interval set to {args.scan_interval} seconds")
    
    if args.action == 'start':
        logger.info("🚀 Starting MDC Connection Service...")
        success = service.start()
        sys.exit(0 if success else 1)
        
    elif args.action == 'stop':
        logger.info("🛑 Stopping MDC Connection Service...")
        # Find and kill running service
        pid_file = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/mdc_service.pid')
        if pid_file.exists():
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                os.kill(pid, signal.SIGTERM)
                logger.info(f"Sent SIGTERM to process {pid}")
                
                # Wait for graceful shutdown
                for i in range(10):
                    try:
                        os.kill(pid, 0)
                        time.sleep(1)
                    except OSError:
                        break
                
                # Force kill if still running
                try:
                    os.kill(pid, signal.SIGKILL)
                    logger.info(f"Force killed process {pid}")
                except OSError:
                    pass
                    
            except Exception as e:
                logger.error(f"Error stopping service: {e}")
                sys.exit(1)
        else:
            logger.info("Service is not running")
        
    elif args.action == 'status':
        status = service.get_status()
        print(json.dumps(status, indent=2))
        
    elif args.action == 'restart':
        logger.info("🔄 Restarting MDC Connection Service...")
        # Stop first
        pid_file = Path('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/mdc_service.pid')
        if pid_file.exists():
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
            except:
                pass
        
        # Start
        success = service.start()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()