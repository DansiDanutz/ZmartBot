#!/usr/bin/env python3
"""
Background Optimization Agent
Continuous optimization service for ZmartBot system
Integrates with system startup and provides persistent optimization
"""

import os
import sys
import time
import signal
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import json
import subprocess
import psutil

class BackgroundOptimizationAgent:
    """Background agent for continuous system optimization"""
    
    def __init__(self, config_file: str = "background_optimization_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.pid_file = Path("background_optimization_agent.pid")
        self.log_file = Path("background_optimization_agent.log")
        self.running = False
        self.optimization_process: Optional[subprocess.Popen] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Setup logging
        self.setup_logging()
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def setup_logging(self):
        """Setup logging for the background agent"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('BackgroundOptimizationAgent')
        
    def load_config(self) -> Dict[str, Any]:
        """Load background optimization configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        # Create default configuration
        default_config = {
            "optimization_script": "comprehensive_optimization_integration.py",
            "restart_interval": 3600,  # 1 hour
            "health_check_interval": 60,  # 1 minute
            "max_restart_attempts": 3,
            "auto_start": True,
            "monitoring": {
                "enabled": True,
                "log_rotation": True,
                "max_log_size_mb": 100
            },
            "system_integration": {
                "create_launchd_plist": True,
                "create_systemd_service": False,  # macOS doesn't use systemd
                "startup_delay": 30  # seconds
            }
        }
        
        self.save_config(default_config)
        return default_config
        
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.stop()
        sys.exit(0)
        
    def write_pid_file(self):
        """Write PID file for process management"""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
            
    def remove_pid_file(self):
        """Remove PID file"""
        if self.pid_file.exists():
            self.pid_file.unlink()
            
    def is_optimization_running(self) -> bool:
        """Check if optimization process is running"""
        if self.optimization_process is None:
            return False
        return self.optimization_process.poll() is None
        
    def start_optimization_process(self) -> bool:
        """Start the comprehensive optimization integration process"""
        try:
            script_path = Path(self.config["optimization_script"])
            if not script_path.exists():
                self.logger.error(f"Optimization script not found: {script_path}")
                return False
                
            # Start the optimization process in daemon mode
            self.optimization_process = subprocess.Popen(
                [sys.executable, str(script_path), "--daemon"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            self.logger.info(f"Started optimization process with PID: {self.optimization_process.pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start optimization process: {e}")
            return False
            
    def stop_optimization_process(self):
        """Stop the optimization process"""
        if self.optimization_process and self.is_optimization_running():
            self.logger.info("Stopping optimization process...")
            self.optimization_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.optimization_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.logger.warning("Optimization process did not terminate gracefully, forcing kill...")
                self.optimization_process.kill()
                self.optimization_process.wait()
                
            self.logger.info("Optimization process stopped")
            
    def restart_optimization_process(self) -> bool:
        """Restart the optimization process"""
        self.logger.info("Restarting optimization process...")
        self.stop_optimization_process()
        time.sleep(5)  # Wait before restart
        return self.start_optimization_process()
        
    def monitor_optimization_process(self):
        """Monitor the optimization process and restart if needed"""
        restart_attempts = 0
        max_attempts = self.config.get("max_restart_attempts", 3)
        
        while not self.stop_event.is_set():
            try:
                if not self.is_optimization_running():
                    self.logger.warning("Optimization process is not running")
                    
                    if restart_attempts < max_attempts:
                        self.logger.info(f"Attempting to restart optimization process (attempt {restart_attempts + 1}/{max_attempts})")
                        if self.start_optimization_process():
                            restart_attempts = 0  # Reset on successful restart
                            self.logger.info("Optimization process restarted successfully")
                        else:
                            restart_attempts += 1
                            self.logger.error(f"Failed to restart optimization process (attempt {restart_attempts}/{max_attempts})")
                    else:
                        self.logger.error(f"Maximum restart attempts ({max_attempts}) reached. Stopping monitoring.")
                        break
                else:
                    # Process is running, reset restart attempts
                    restart_attempts = 0
                    
                # Wait for next health check
                time.sleep(self.config.get("health_check_interval", 60))
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait before retrying
                
    def create_launchd_plist(self) -> bool:
        """Create macOS LaunchAgent plist for system startup integration"""
        try:
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.zmartbot.background-optimization-agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{Path(__file__).absolute()}</string>
        <string>--daemon</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{Path.cwd()}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{self.log_file}</string>
    <key>StandardErrorPath</key>
    <string>{self.log_file}</string>
    <key>StartInterval</key>
    <integer>3600</integer>
</dict>
</plist>"""
            
            plist_path = Path.home() / "Library" / "LaunchAgents" / "com.zmartbot.background-optimization-agent.plist"
            plist_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(plist_path, 'w') as f:
                f.write(plist_content)
                
            self.logger.info(f"Created LaunchAgent plist: {plist_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create LaunchAgent plist: {e}")
            return False
            
    def install_launchd_service(self) -> bool:
        """Install the LaunchAgent service"""
        try:
            plist_path = Path.home() / "Library" / "LaunchAgents" / "com.zmartbot.background-optimization-agent.plist"
            
            # Load the service
            result = subprocess.run(
                ["launchctl", "load", str(plist_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("LaunchAgent service installed successfully")
                return True
            else:
                self.logger.error(f"Failed to install LaunchAgent service: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error installing LaunchAgent service: {e}")
            return False
            
    def uninstall_launchd_service(self) -> bool:
        """Uninstall the LaunchAgent service"""
        try:
            plist_path = Path.home() / "Library" / "LaunchAgents" / "com.zmartbot.background-optimization-agent.plist"
            
            # Unload the service
            result = subprocess.run(
                ["launchctl", "unload", str(plist_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("LaunchAgent service uninstalled successfully")
                # Remove the plist file
                if plist_path.exists():
                    plist_path.unlink()
                return True
            else:
                self.logger.error(f"Failed to uninstall LaunchAgent service: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error uninstalling LaunchAgent service: {e}")
            return False
            
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the background agent"""
        return {
            "running": self.running,
            "optimization_process_running": self.is_optimization_running(),
            "optimization_process_pid": self.optimization_process.pid if self.optimization_process else None,
            "monitoring_active": self.monitoring_thread and self.monitoring_thread.is_alive(),
            "config": self.config,
            "pid_file_exists": self.pid_file.exists(),
            "log_file_size": self.log_file.stat().st_size if self.log_file.exists() else 0
        }
        
    def start(self):
        """Start the background optimization agent"""
        if self.running:
            self.logger.warning("Background agent is already running")
            return
            
        self.logger.info("Starting Background Optimization Agent...")
        
        # Write PID file
        self.write_pid_file()
        
        # Create and install LaunchAgent plist if configured
        if self.config.get("system_integration", {}).get("create_launchd_plist", False):
            if self.create_launchd_plist():
                self.install_launchd_service()
            
        # Start optimization process
        if not self.start_optimization_process():
            self.logger.error("Failed to start optimization process")
            return
            
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitor_optimization_process)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.running = True
        self.logger.info("Background Optimization Agent started successfully")
        
        # Main loop
        try:
            while self.running and not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt, shutting down...")
        finally:
            self.stop()
            
    def stop(self):
        """Stop the background optimization agent"""
        if not self.running:
            return
            
        self.logger.info("Stopping Background Optimization Agent...")
        self.running = False
        self.stop_event.set()
        
        # Stop optimization process
        self.stop_optimization_process()
        
        # Wait for monitoring thread to finish
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=10)
            
        # Remove PID file
        self.remove_pid_file()
        
        self.logger.info("Background Optimization Agent stopped")
        
    def daemon_mode(self):
        """Run in daemon mode (background)"""
        # Fork the process
        try:
            pid = os.fork()
            if pid > 0:
                # Parent process
                sys.exit(0)
        except OSError as e:
            self.logger.error(f"Failed to fork process: {e}")
            sys.exit(1)
            
        # Child process continues
        os.setsid()
        os.umask(0)
        
        # Fork again to ensure we're not a session leader
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            self.logger.error(f"Failed to fork process (second time): {e}")
            sys.exit(1)
            
        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        
        # Start the agent
        self.start()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Background Optimization Agent for ZmartBot")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode")
    parser.add_argument("--install", action="store_true", help="Install as system service")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall system service")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--config", default="background_optimization_config.json", help="Configuration file")
    
    args = parser.parse_args()
    
    agent = BackgroundOptimizationAgent(args.config)
    
    if args.install:
        agent.install_launchd_service()
    elif args.uninstall:
        agent.uninstall_launchd_service()
    elif args.status:
        status = agent.get_status()
        print(json.dumps(status, indent=2))
    elif args.daemon:
        agent.daemon_mode()
    else:
        agent.start()

if __name__ == "__main__":
    main()