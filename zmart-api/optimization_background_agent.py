#!/usr/bin/env python3
"""
Optimization Background Agent
Simple background agent for running ZmartBot optimizations
"""

import json
import time
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Import optimization components
try:
    from system_optimization_manager import SystemOptimizationManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class OptimizationBackgroundAgent:
    """Simple background agent for optimization management"""
    
    def __init__(self):
        self.config_file = Path("optimization_background_config.json")
        self.config = self.load_config()
        self.optimization_manager = None
        self.running = False
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        # Create default config
        default_config = {
            "auto_start": True,
            "check_interval": 60,
            "log_file": "optimization_background_agent.log",
            "enable_components": {
                "mdc_monitoring": True,
                "performance_reporting": True,
                "api_key_monitoring": True,
                "expanded_service_monitoring": True
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def initialize(self) -> bool:
        """Initialize the optimization manager"""
        try:
            print("🔧 Initializing System Optimization Manager...")
            self.optimization_manager = SystemOptimizationManager()
            print("✅ System Optimization Manager initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize System Optimization Manager: {e}")
            return False
    
    def start(self):
        """Start the background agent"""
        if not self.initialize():
            return False
        
        print("🚀 Starting optimization services...")
        try:
            self.optimization_manager.start_all_monitors()
            self.running = True
            print("✅ All optimization services started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start optimization services: {e}")
            return False
    
    def stop(self):
        """Stop the background agent"""
        if self.optimization_manager and self.running:
            print("🛑 Stopping optimization services...")
            try:
                self.optimization_manager.stop_all_monitors()
                self.running = False
                print("✅ All optimization services stopped")
            except Exception as e:
                print(f"❌ Error stopping optimization services: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        if not self.optimization_manager:
            return {"status": "not_initialized"}
        
        try:
            return self.optimization_manager.get_status()
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def run(self):
        """Main run loop"""
        self.setup_signal_handlers()
        
        if not self.start():
            print("❌ Failed to start optimization agent")
            return
        
        print(f"🔄 Optimization agent running (checking every {self.config['check_interval']} seconds)")
        print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                time.sleep(self.config['check_interval'])
                
                # Optional: Add health checks here
                if self.optimization_manager:
                    try:
                        status = self.get_status()
                        if status.get("status") == "error":
                            print(f"⚠️ Warning: {status.get('error')}")
                    except Exception as e:
                        print(f"⚠️ Health check error: {e}")
                
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
        finally:
            self.stop()

def main():
    """Main entry point"""
    print("🚀 Starting ZmartBot Optimization Background Agent")
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    
    agent = OptimizationBackgroundAgent()
    agent.run()
    
    print("✅ Optimization Background Agent stopped")

if __name__ == "__main__":
    main()
