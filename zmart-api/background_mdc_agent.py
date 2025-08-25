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
from pathlib import Path
from datetime import datetime
import json

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
        
        # If CLAUDE.md is older than 24 hours, force update
        if age_hours > 24:
            self.log(f"CLAUDE.md is {age_hours:.1f} hours old, forcing update")
            return True
        
        return False
    
    def run_cycle(self):
        """Run one monitoring cycle"""
        try:
            # Get current MDC files info
            current_info = self.get_mdc_files_info()
            
            # Check for changes
            has_changes, current_info = self.check_for_changes(getattr(self, '_previous_info', None))
            self._previous_info = current_info
            
            # Check if CLAUDE.md is stale
            is_stale = self.check_claude_md_age()
            
            # Update if needed
            if has_changes or is_stale:
                self.log(f"Changes detected or CLAUDE.md stale. MDC files: {len(current_info)}")
                
                # Update CLAUDE.md
                if self.update_claude_md():
                    # Update Master Orchestration Agent
                    self.update_master_orchestration()
                else:
                    self.log("Failed to update CLAUDE.md, skipping Master Orchestration update")
            else:
                self.log(f"No changes detected. MDC files: {len(current_info)}")
                
        except Exception as e:
            self.log(f"Error in monitoring cycle: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.log("Received shutdown signal, stopping agent...")
        self.running = False
    
    def run(self):
        """Main run loop"""
        self.log("Background MDC Agent starting...")
        self.log(f"Monitoring directory: {self.mdc_dir}")
        self.log(f"Update interval: {self.update_interval} seconds")
        
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
