#!/usr/bin/env python3
"""
Master Autonomous Controller for ZmartBot System
Orchestrates all autonomous systems and ensures complete self-management
"""

import os
import sys
import time
import json
import logging
import subprocess
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class MasterAutonomousController:
    """Master controller for complete system autonomy"""
    
    def __init__(self, config_path: str = "master_autonomous_config.json"):
        self.config_path = Path(config_path)
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.config = self.load_config()
        
        # System components
        self.components = {
            "background_optimization_agent": None,
            "autonomous_health_monitor": None,
            "log_rotation_manager": None
        }
        
        # Control flags
        self.running = False
        self.shutdown_requested = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.logger.info("Master Autonomous Controller initialized")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.logs_dir / "master_autonomous_controller.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default configuration
            default_config = {
                "system": {
                    "auto_start_all_services": True,
                    "check_interval_seconds": 60,
                    "max_restart_attempts": 5,
                    "graceful_shutdown_timeout": 30
                },
                "components": {
                    "background_optimization_agent": {
                        "enabled": True,
                        "script": "background_optimization_agent.py",
                        "args": ["--daemon"],
                        "auto_restart": True
                    },
                    "autonomous_health_monitor": {
                        "enabled": True,
                        "script": "autonomous_health_monitor.py",
                        "args": ["--daemon"],
                        "auto_restart": True
                    },
                    "log_rotation_manager": {
                        "enabled": True,
                        "script": "log_rotation_manager.py",
                        "args": ["--daemon"],
                        "auto_restart": True
                    }
                },
                "monitoring": {
                    "health_check_interval": 30,
                    "performance_check_interval": 300,
                    "auto_optimization_enabled": True
                }
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            self.logger.info(f"Created default configuration: {self.config_path}")
            return default_config
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
    
    def start_component(self, name: str, config: Dict) -> bool:
        """Start a system component"""
        try:
            if not config.get("enabled", False):
                self.logger.info(f"Component {name} is disabled, skipping...")
                return True
            
            script_path = Path(config["script"])
            if not script_path.exists():
                self.logger.error(f"Script not found: {script_path}")
                return False
            
            # Build command
            cmd = [sys.executable, str(script_path)] + config.get("args", [])
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            self.components[name] = process
            self.logger.info(f"Started {name} with PID: {process.pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start {name}: {e}")
            return False
    
    def stop_component(self, name: str) -> bool:
        """Stop a system component"""
        try:
            if name not in self.components or self.components[name] is None:
                return True
            
            process = self.components[name]
            if process.poll() is None:  # Process is still running
                self.logger.info(f"Stopping {name} (PID: {process.pid})...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"Force killing {name}...")
                    process.kill()
                    process.wait()
                
                self.logger.info(f"Stopped {name}")
            
            self.components[name] = None
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop {name}: {e}")
            return False
    
    def check_component_health(self, name: str) -> bool:
        """Check if a component is healthy"""
        if name not in self.components or self.components[name] is None:
            return False
        
        process = self.components[name]
        return process.poll() is None  # Process is still running
    
    def restart_component(self, name: str) -> bool:
        """Restart a system component"""
        self.logger.info(f"Restarting {name}...")
        self.stop_component(name)
        time.sleep(2)  # Brief pause
        
        config = self.config["components"].get(name, {})
        return self.start_component(name, config)
    
    def start_all_components(self) -> bool:
        """Start all configured components"""
        self.logger.info("Starting all autonomous system components...")
        
        success = True
        for name, config in self.config["components"].items():
            if not self.start_component(name, config):
                success = False
        
        return success
    
    def stop_all_components(self) -> bool:
        """Stop all components"""
        self.logger.info("Stopping all autonomous system components...")
        
        success = True
        for name in list(self.components.keys()):
            if not self.stop_component(name):
                success = False
        
        return success
    
    def monitor_components(self):
        """Monitor all components and restart if needed"""
        for name, config in self.config["components"].items():
            if not config.get("enabled", False):
                continue
            
            if not self.check_component_health(name):
                self.logger.warning(f"Component {name} is not healthy, restarting...")
                if config.get("auto_restart", False):
                    self.restart_component(name)
                else:
                    self.logger.error(f"Auto-restart disabled for {name}")
    
    def run(self):
        """Main execution loop"""
        self.logger.info("Starting Master Autonomous Controller...")
        self.running = True
        
        # Start all components
        if not self.start_all_components():
            self.logger.error("Failed to start some components")
            return False
        
        self.logger.info("All components started successfully")
        
        # Main monitoring loop
        try:
            while self.running and not self.shutdown_requested:
                # Monitor component health
                self.monitor_components()
                
                # Wait for next check
                time.sleep(self.config["system"]["check_interval_seconds"])
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.logger.info("Shutting down Master Autonomous Controller...")
            self.stop_all_components()
            self.running = False
        
        return True
    
    def run_daemon(self):
        """Run as daemon process"""
        self.logger.info("Starting Master Autonomous Controller in daemon mode...")
        
        # Fork to background
        try:
            pid = os.fork()
            if pid > 0:
                # Parent process
                sys.exit(0)
        except OSError as e:
            self.logger.error(f"Failed to fork: {e}")
            return False
        
        # Child process continues
        os.setsid()
        os.umask(0)
        
        # Fork again
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            self.logger.error(f"Failed to fork: {e}")
            return False
        
        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        
        # Run main loop
        return self.run()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Master Autonomous Controller")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--config", default="master_autonomous_config.json", help="Configuration file")
    
    args = parser.parse_args()
    
    controller = MasterAutonomousController(args.config)
    
    if args.daemon:
        success = controller.run_daemon()
    else:
        success = controller.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
