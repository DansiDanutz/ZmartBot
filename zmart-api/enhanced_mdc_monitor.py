#!/usr/bin/env python3
"""
Enhanced MDC Monitor with Smart Context Optimization
Integrates with SmartContextOptimizer for performance-optimized context management
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import queue

from smart_context_optimizer import SmartContextOptimizer

class EnhancedMDCMonitor:
    """
    Enhanced MDC monitoring system with smart context optimization.
    Implements batching, relevance scoring, and performance monitoring.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.cursor_rules_dir = self.project_root / ".cursor" / "rules"
        self.claude_dir = self.project_root / ".claude"
        self.claude_main_file = self.project_root / "CLAUDE.md"
        
        # Performance settings
        self.batch_interval = 30  # seconds
        self.max_batch_size = 10
        self.update_threshold = 5  # minimum changes before batch update
        
        # Initialize smart context optimizer
        self.optimizer = SmartContextOptimizer(project_root)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Change tracking
        self.pending_changes = queue.Queue()
        self.last_update = datetime.now()
        self.change_count = 0
        self.is_running = False
        
        # Performance metrics
        self.metrics = {
            "total_updates": 0,
            "batch_updates": 0,
            "immediate_updates": 0,
            "average_update_time": 0,
            "last_performance_check": None
        }
    
    def start_monitoring(self):
        """Start the enhanced MDC monitoring system."""
        if self.is_running:
            self.logger.warning("Monitor is already running")
            return
        
        self.is_running = True
        self.logger.info("Starting Enhanced MDC Monitor...")
        
        # Start file system observer
        self.observer = Observer()
        event_handler = MDCFileHandler(self)
        self.observer.schedule(event_handler, str(self.cursor_rules_dir), recursive=True)
        self.observer.start()
        
        # Start batch processing thread
        self.batch_thread = threading.Thread(target=self._batch_processor, daemon=True)
        self.batch_thread.start()
        
        # Start performance monitoring thread
        self.performance_thread = threading.Thread(target=self._performance_monitor, daemon=True)
        self.performance_thread.start()
        
        self.logger.info("Enhanced MDC Monitor started successfully")
    
    def stop_monitoring(self):
        """Stop the enhanced MDC monitoring system."""
        if not self.is_running:
            return
        
        self.is_running = False
        self.observer.stop()
        self.observer.join()
        
        # Process any remaining changes
        self._process_pending_changes()
        
        self.logger.info("Enhanced MDC Monitor stopped")
    
    def add_change(self, file_path: str, change_type: str):
        """Add a file change to the pending queue."""
        change_info = {
            "file": file_path,
            "type": change_type,
            "timestamp": datetime.now().isoformat()
        }
        
        self.pending_changes.put(change_info)
        self.change_count += 1
        
        # Check if we should trigger immediate update
        if self.change_count >= self.update_threshold:
            self._trigger_update("threshold_reached")
    
    def _batch_processor(self):
        """Background thread for batch processing changes."""
        while self.is_running:
            try:
                # Wait for batch interval
                time.sleep(self.batch_interval)
                
                if not self.pending_changes.empty():
                    self._trigger_update("batch_interval")
                    
            except Exception as e:
                self.logger.error(f"Error in batch processor: {e}")
    
    def _performance_monitor(self):
        """Background thread for performance monitoring."""
        while self.is_running:
            try:
                time.sleep(300)  # Check every 5 minutes
                self._check_performance()
                
            except Exception as e:
                self.logger.error(f"Error in performance monitor: {e}")
    
    def _trigger_update(self, trigger_type: str):
        """Trigger a context update."""
        if self.pending_changes.empty():
            return
        
        start_time = time.time()
        
        try:
            # Collect all pending changes
            changes = []
            while not self.pending_changes.empty() and len(changes) < self.max_batch_size:
                try:
                    change = self.pending_changes.get_nowait()
                    changes.append(change)
                except queue.Empty:
                    break
            
            if not changes:
                return
            
            # Determine focus domain based on changes
            focus_domain = self._determine_focus_domain(changes)
            
            # Update context with smart optimization
            success = self.optimizer.update_claude_md_smart(focus_domain=focus_domain)
            
            if success:
                update_time = time.time() - start_time
                self.metrics["total_updates"] += 1
                self.metrics["batch_updates"] += 1
                self.metrics["average_update_time"] = (
                    (self.metrics["average_update_time"] * (self.metrics["total_updates"] - 1) + update_time) 
                    / self.metrics["total_updates"]
                )
                
                self.logger.info(
                    f"Batch update completed ({len(changes)} changes, {update_time:.2f}s, "
                    f"domain: {focus_domain}, trigger: {trigger_type})"
                )
            else:
                self.logger.error("Batch update failed")
                
        except Exception as e:
            self.logger.error(f"Error in batch update: {e}")
    
    def _determine_focus_domain(self, changes: List[Dict]) -> str:
        """Determine the focus domain based on changed files."""
        domain_counts = {}
        
        for change in changes:
            file_path = Path(change["file"])
            domain = self.optimizer.get_domain_for_file(file_path.stem)
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Return the most common domain, or "core" if no clear pattern
        if domain_counts:
            most_common = max(domain_counts.items(), key=lambda x: x[1])
            if most_common[1] > 1:  # At least 2 changes in same domain
                return most_common[0]
        
        return "core"
    
    def _check_performance(self):
        """Check and log performance metrics."""
        self.metrics["last_performance_check"] = datetime.now().isoformat()
        
        # Calculate performance indicators
        total_time = time.time() - self.last_update.timestamp()
        updates_per_minute = self.metrics["total_updates"] / (total_time / 60) if total_time > 0 else 0
        
        self.logger.info(f"Performance Check:")
        self.logger.info(f"  - Total Updates: {self.metrics['total_updates']}")
        self.logger.info(f"  - Batch Updates: {self.metrics['batch_updates']}")
        self.logger.info(f"  - Immediate Updates: {self.metrics['immediate_updates']}")
        self.logger.info(f"  - Average Update Time: {self.metrics['average_update_time']:.2f}s")
        self.logger.info(f"  - Updates per Minute: {updates_per_minute:.2f}")
        
        # Check for performance issues
        if self.metrics["average_update_time"] > 5.0:
            self.logger.warning("Slow update times detected - consider optimization")
        
        if updates_per_minute > 10:
            self.logger.warning("High update frequency detected - consider increasing batch interval")
    
    def _process_pending_changes(self):
        """Process any remaining changes when stopping."""
        if not self.pending_changes.empty():
            self._trigger_update("shutdown")
    
    def get_status(self) -> Dict:
        """Get current status of the monitor."""
        return {
            "is_running": self.is_running,
            "pending_changes": self.pending_changes.qsize(),
            "change_count": self.change_count,
            "last_update": self.last_update.isoformat(),
            "metrics": self.metrics.copy(),
            "batch_interval": self.batch_interval,
            "update_threshold": self.update_threshold
        }

class MDCFileHandler(FileSystemEventHandler):
    """File system event handler for MDC files."""
    
    def __init__(self, monitor: EnhancedMDCMonitor):
        self.monitor = monitor
        self.logger = logging.getLogger(__name__)
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.mdc'):
            self.monitor.add_change(event.src_path, "created")
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.mdc'):
            self.monitor.add_change(event.src_path, "modified")
    
    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith('.mdc'):
            self.monitor.add_change(event.src_path, "deleted")
    
    def on_moved(self, event):
        if not event.is_directory and event.src_path.endswith('.mdc'):
            self.monitor.add_change(event.src_path, "moved")

def main():
    """Main entry point for Enhanced MDC Monitor."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced MDC Monitor with Smart Context Optimization")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--stop", action="store_true", help="Stop monitoring")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--analyze", action="store_true", help="Analyze current context")
    parser.add_argument("--update", action="store_true", help="Force immediate update")
    parser.add_argument("--batch-interval", type=int, default=30, help="Batch interval in seconds")
    parser.add_argument("--update-threshold", type=int, default=5, help="Update threshold")
    
    args = parser.parse_args()
    
    monitor = EnhancedMDCMonitor(args.project_root)
    monitor.batch_interval = args.batch_interval
    monitor.update_threshold = args.update_threshold
    
    if args.start:
        monitor.start_monitoring()
        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
    
    elif args.stop:
        monitor.stop_monitoring()
    
    elif args.status:
        status = monitor.get_status()
        print(json.dumps(status, indent=2))
    
    elif args.analyze:
        monitor.optimizer.update_claude_md_smart(analyze=True)
    
    elif args.update:
        monitor.optimizer.update_claude_md_smart()
    
    else:
        print("No action specified. Use --help for options.")

if __name__ == "__main__":
    main()
