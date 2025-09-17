#!/usr/bin/env python3
"""
Background MDC Agent for Cursor
Automatically monitors and updates MDC files and CLAUDE.md
"""

import os
import time
import subprocess
import signal
import sys
import asyncio
from pathlib import Path
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import MDC Connection Agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.services.mdc_connection_agent import MDCConnectionAgent

class BackgroundMDCAgent:
    def __init__(self):
        self.project_root = Path("/Users/dansidanutz/Desktop/ZmartBot")
        self.agent_dir = self.project_root / "zmart-api"
        self.mdc_dir = self.project_root / ".cursor" / "rules"
        self.claude_file = self.project_root / "CLAUDE.md"
        self.running = True
        self.last_update = None
        self.update_interval = 300  # 5 minutes
        self.log_file = self.agent_dir / "background_mdc_agent.log"
        
        # Initialize MDC Connection Agent
        self.connection_agent = None
        self.connection_agent_enabled = True
        self.last_connection_scan = None
        self.connection_scan_interval = 3600  # 1 hour
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a') as f:
            f.write(log_message + '\n')
    
    def get_mdc_files_info(self):
        """Get information about MDC files"""
        mdc_files = list(self.mdc_dir.glob("*.mdc"))
        file_info = {}
        
        for mdc_file in mdc_files:
            stat = mdc_file.stat()
            file_info[mdc_file.name] = {
                'path': str(mdc_file),
                'modified': stat.st_mtime,
                'size': stat.st_size
            }
        
        return file_info
    
    def check_for_changes(self, previous_info):
        """Check if any MDC files have changed"""
        current_info = self.get_mdc_files_info()
        
        if not previous_info:
            return True, current_info
        
        # Check for new files, modified files, or deleted files
        current_files = set(current_info.keys())
        previous_files = set(previous_info.keys())
        
        # New files
        new_files = current_files - previous_files
        if new_files:
            self.log(f"New MDC files detected: {new_files}")
            return True, current_info
        
        # Modified files
        for filename in current_files & previous_files:
            if current_info[filename]['modified'] != previous_info[filename]['modified']:
                self.log(f"Modified MDC file detected: {filename}")
                return True, current_info
        
        # Deleted files
        deleted_files = previous_files - current_files
        if deleted_files:
            self.log(f"Deleted MDC files detected: {deleted_files}")
            return True, current_info
        
        return False, current_info
    
    def update_claude_md(self):
        """Update CLAUDE.md using smart context optimizer"""
        try:
            self.log("Updating CLAUDE.md...")
            
            # Run smart context optimizer
            cmd = [
                sys.executable, 
                str(self.agent_dir / "smart_context_optimizer.py"),
                "--update",
                "--project-root", str(self.project_root)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.agent_dir)
            
            if result.returncode == 0:
                self.log("CLAUDE.md updated successfully")
                self.last_update = datetime.now()
                return True
            else:
                self.log(f"Error updating CLAUDE.md: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"Exception updating CLAUDE.md: {e}")
            return False
    
    def update_master_orchestration(self):
        """Update Master Orchestration Agent"""
        try:
            self.log("Updating Master Orchestration Agent...")
            
            cmd = [
                sys.executable,
                str(self.agent_dir / "update_master_orchestration.py")
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.agent_dir)
            
            if result.returncode == 0:
                self.log("Master Orchestration Agent updated successfully")
                return True
            else:
                self.log(f"Error updating Master Orchestration Agent: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"Exception updating Master Orchestration Agent: {e}")
            return False
    
    def check_claude_md_age(self):
        """Check if CLAUDE.md is getting stale"""
        if not self.claude_file.exists():
            return True
        
        stat = self.claude_file.stat()
        age_hours = (time.time() - stat.st_mtime) / 3600
        
        # If CLAUDE.md is older than 1 hour, force update (high-activity system)
        if age_hours > 1:
            self.log(f"CLAUDE.md is {age_hours:.1f} hours old, forcing update")
            return True
        
        return False
    
    def initialize_connection_agent(self):
        """Initialize the MDC Connection Agent"""
        try:
            if self.connection_agent_enabled and not self.connection_agent:
                self.log("Initializing MDC Connection Agent...")
                
                # Get OpenAI API key if available
                openai_key = os.getenv('OPENAI_API_KEY')
                if not openai_key:
                    self.log("No OpenAI API key found, using rule-based connections only")
                
                # Initialize agent
                self.connection_agent = MDCConnectionAgent(str(self.mdc_dir), openai_key)
                self.connection_agent.start_watching()
                
                self.log("MDC Connection Agent initialized and file watching started")
                return True
                
        except Exception as e:
            self.log(f"Error initializing connection agent: {e}")
            self.connection_agent_enabled = False
            return False
    
    async def run_connection_analysis(self):
        """Run connection analysis on all MDC files"""
        try:
            if not self.connection_agent:
                return False
                
            self.log("Running MDC connection analysis...")
            
            # Discover connections for all services
            connections = await self.connection_agent.discover_all_connections()
            
            total_connections = sum(len(conns) for conns in connections.values())
            self.log(f"Connection analysis complete: {len(connections)} services, {total_connections} connections")
            
            self.last_connection_scan = time.time()
            return True
            
        except Exception as e:
            self.log(f"Error in connection analysis: {e}")
            return False
    
    def should_run_connection_scan(self):
        """Check if connection scan should be run"""
        if not self.connection_agent_enabled or not self.connection_agent:
            return False
            
        if not self.last_connection_scan:
            return True
            
        return (time.time() - self.last_connection_scan) > self.connection_scan_interval
    
    def run_cycle(self):
        """Run one monitoring cycle"""
        try:
            # Initialize connection agent if needed
            if not self.connection_agent and self.connection_agent_enabled:
                self.initialize_connection_agent()
            
            # Get current MDC files info
            current_info = self.get_mdc_files_info()
            
            # Check for changes
            has_changes, current_info = self.check_for_changes(getattr(self, '_previous_info', None))
            self._previous_info = current_info
            
            # Check if CLAUDE.md is stale
            is_stale = self.check_claude_md_age()
            
            # Check if connection scan should run
            should_scan_connections = self.should_run_connection_scan()
            
            # Update if needed
            if has_changes or is_stale:
                self.log(f"Changes detected or CLAUDE.md stale. MDC files: {len(current_info)}")
                
                # Run connection analysis if changes detected
                if has_changes and self.connection_agent:
                    try:
                        asyncio.run(self.run_connection_analysis())
                    except Exception as e:
                        self.log(f"Error in connection analysis: {e}")
                
                # Update CLAUDE.md
                if self.update_claude_md():
                    # Update Master Orchestration Agent
                    self.update_master_orchestration()
                else:
                    self.log("Failed to update CLAUDE.md, skipping Master Orchestration update")
            elif should_scan_connections:
                # Run periodic connection scan
                self.log("Running scheduled connection analysis...")
                try:
                    asyncio.run(self.run_connection_analysis())
                except Exception as e:
                    self.log(f"Error in scheduled connection analysis: {e}")
            else:
                self.log(f"No changes detected. MDC files: {len(current_info)}")
                
        except Exception as e:
            self.log(f"Error in monitoring cycle: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.log("Received shutdown signal, stopping agent...")
        
        # Stop connection agent
        if self.connection_agent:
            try:
                self.connection_agent.stop_watching()
                self.log("Connection agent file watcher stopped")
            except Exception as e:
                self.log(f"Error stopping connection agent: {e}")
        
        self.running = False
    
    def run(self):
        """Main run loop"""
        self.log("Background MDC Agent starting...")
        self.log(f"Monitoring directory: {self.mdc_dir}")
        self.log(f"Update interval: {self.update_interval} seconds")
        self.log(f"Connection agent enabled: {self.connection_agent_enabled}")
        self.log(f"Connection scan interval: {self.connection_scan_interval} seconds")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Initial update
        self.log("Performing initial update...")
        self.run_cycle()
        
        # Main loop
        while self.running:
            try:
                time.sleep(self.update_interval)
                self.run_cycle()
            except KeyboardInterrupt:
                self.log("Keyboard interrupt received, stopping...")
                break
            except Exception as e:
                self.log(f"Unexpected error in main loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
        
        self.log("Background MDC Agent stopped.")

def main():
    """Main entry point"""
    agent = BackgroundMDCAgent()
    agent.run()

if __name__ == "__main__":
    main()
