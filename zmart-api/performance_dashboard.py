#!/usr/bin/env python3
"""
Performance Dashboard for Smart Context Optimization
Real-time monitoring and analytics for MDC management system
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import threading
import queue

class PerformanceDashboard:
    """
    Real-time performance dashboard for smart context optimization.
    Provides monitoring, analytics, and performance insights.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.claude_dir = self.project_root / ".claude"
        self.cursor_rules_dir = self.project_root / ".cursor" / "rules"
        self.claude_main_file = self.project_root / "CLAUDE.md"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Performance data storage
        self.performance_data = {
            "context_updates": [],
            "file_changes": [],
            "system_metrics": {},
            "domain_activity": {},
            "size_tracking": [],
            "error_log": []
        }
        
        # Real-time monitoring
        self.is_monitoring = False
        self.monitor_thread = None
        self.update_queue = queue.Queue()
        
        # Performance thresholds
        self.thresholds = {
            "max_update_time": 5.0,  # seconds
            "max_claude_size": 40000,  # characters
            "max_files_per_update": 20,
            "min_relevance_score": 30
        }
    
    def start_monitoring(self):
        """Start real-time performance monitoring."""
        if self.is_monitoring:
            self.logger.warning("Dashboard is already monitoring")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Performance Dashboard started")
    
    def stop_monitoring(self):
        """Stop real-time performance monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        self.logger.info("Performance Dashboard stopped")
    
    def record_context_update(self, update_info: Dict[str, Any]):
        """Record a context update for performance tracking."""
        update_info["timestamp"] = datetime.now().isoformat()
        self.performance_data["context_updates"].append(update_info)
        
        # Keep only last 100 updates
        if len(self.performance_data["context_updates"]) > 100:
            self.performance_data["context_updates"] = self.performance_data["context_updates"][-100:]
        
        # Update domain activity
        domain = update_info.get("focus_domain", "unknown")
        if domain not in self.performance_data["domain_activity"]:
            self.performance_data["domain_activity"][domain] = {
                "updates": 0,
                "total_time": 0,
                "last_update": None
            }
        
        self.performance_data["domain_activity"][domain]["updates"] += 1
        self.performance_data["domain_activity"][domain]["total_time"] += update_info.get("update_time", 0)
        self.performance_data["domain_activity"][domain]["last_update"] = update_info["timestamp"]
    
    def record_file_change(self, file_path: str, change_type: str, relevance_score: int = 0):
        """Record a file change for tracking."""
        change_info = {
            "file": file_path,
            "type": change_type,
            "relevance_score": relevance_score,
            "timestamp": datetime.now().isoformat()
        }
        
        self.performance_data["file_changes"].append(change_info)
        
        # Keep only last 200 changes
        if len(self.performance_data["file_changes"]) > 200:
            self.performance_data["file_changes"] = self.performance_data["file_changes"][-200:]
    
    def record_error(self, error_type: str, error_message: str, context: Dict = None):
        """Record an error for monitoring."""
        error_info = {
            "type": error_type,
            "message": error_message,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.performance_data["error_log"].append(error_info)
        
        # Keep only last 50 errors
        if len(self.performance_data["error_log"]) > 50:
            self.performance_data["error_log"] = self.performance_data["error_log"][-50:]
    
    def update_system_metrics(self):
        """Update current system metrics."""
        try:
            # File system metrics
            mdc_files = list(self.cursor_rules_dir.glob("**/*.mdc"))
            total_size = sum(f.stat().st_size for f in mdc_files if f.exists())
            
            # CLAUDE.md metrics
            claude_size = self.claude_main_file.stat().st_size if self.claude_main_file.exists() else 0
            
            # Recent activity
            recent_updates = len([u for u in self.performance_data["context_updates"] 
                                if datetime.fromisoformat(u["timestamp"]) > datetime.now() - timedelta(hours=1)])
            
            recent_changes = len([c for c in self.performance_data["file_changes"]
                                if datetime.fromisoformat(c["timestamp"]) > datetime.now() - timedelta(hours=1)])
            
            self.performance_data["system_metrics"] = {
                "total_mdc_files": len(mdc_files),
                "total_mdc_size": total_size,
                "claude_size": claude_size,
                "claude_size_percentage": (claude_size / self.thresholds["max_claude_size"]) * 100,
                "recent_updates_1h": recent_updates,
                "recent_changes_1h": recent_changes,
                "last_update": datetime.now().isoformat()
            }
            
            # Track size over time
            self.performance_data["size_tracking"].append({
                "timestamp": datetime.now().isoformat(),
                "claude_size": claude_size,
                "total_mdc_size": total_size
            })
            
            # Keep only last 100 size records
            if len(self.performance_data["size_tracking"]) > 100:
                self.performance_data["size_tracking"] = self.performance_data["size_tracking"][-100:]
                
        except Exception as e:
            self.record_error("system_metrics", str(e))
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.is_monitoring:
            try:
                # Update system metrics every 30 seconds
                self.update_system_metrics()
                
                # Check for performance issues
                self._check_performance_alerts()
                
                time.sleep(30)
                
            except Exception as e:
                self.record_error("monitor_loop", str(e))
                time.sleep(60)  # Wait longer on error
    
    def _check_performance_alerts(self):
        """Check for performance issues and generate alerts."""
        metrics = self.performance_data["system_metrics"]
        
        # Check CLAUDE.md size
        if metrics["claude_size_percentage"] > 90:
            self.logger.warning(f"CLAUDE.md size at {metrics['claude_size_percentage']:.1f}% of limit")
        
        # Check recent update frequency
        if metrics["recent_updates_1h"] > 20:
            self.logger.warning(f"High update frequency: {metrics['recent_updates_1h']} updates in last hour")
        
        # Check for errors
        recent_errors = [e for e in self.performance_data["error_log"]
                        if datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(hours=1)]
        
        if len(recent_errors) > 5:
            self.logger.error(f"High error rate: {len(recent_errors)} errors in last hour")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        self.update_system_metrics()
        
        # Calculate performance statistics
        if self.performance_data["context_updates"]:
            update_times = [u.get("update_time", 0) for u in self.performance_data["context_updates"]]
            avg_update_time = sum(update_times) / len(update_times)
            max_update_time = max(update_times)
            min_update_time = min(update_times)
        else:
            avg_update_time = max_update_time = min_update_time = 0
        
        # Domain statistics
        domain_stats = {}
        for domain, activity in self.performance_data["domain_activity"].items():
            if activity["updates"] > 0:
                domain_stats[domain] = {
                    "updates": activity["updates"],
                    "avg_time": activity["total_time"] / activity["updates"],
                    "last_update": activity["last_update"]
                }
        
        # Recent activity
        last_24h = datetime.now() - timedelta(hours=24)
        recent_updates = [u for u in self.performance_data["context_updates"]
                         if datetime.fromisoformat(u["timestamp"]) > last_24h]
        recent_changes = [c for c in self.performance_data["file_changes"]
                         if datetime.fromisoformat(c["timestamp"]) > last_24h]
        recent_errors = [e for e in self.performance_data["error_log"]
                        if datetime.fromisoformat(e["timestamp"]) > last_24h]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": self.performance_data["system_metrics"],
            "performance_stats": {
                "total_updates": len(self.performance_data["context_updates"]),
                "avg_update_time": avg_update_time,
                "max_update_time": max_update_time,
                "min_update_time": min_update_time,
                "recent_updates_24h": len(recent_updates),
                "recent_changes_24h": len(recent_changes),
                "recent_errors_24h": len(recent_errors)
            },
            "domain_activity": domain_stats,
            "performance_alerts": self._get_alerts(),
            "recommendations": self._get_recommendations()
        }
    
    def _get_alerts(self) -> List[Dict[str, Any]]:
        """Get current performance alerts."""
        alerts = []
        metrics = self.performance_data["system_metrics"]
        
        if metrics["claude_size_percentage"] > 90:
            alerts.append({
                "level": "warning",
                "message": f"CLAUDE.md size at {metrics['claude_size_percentage']:.1f}% of limit",
                "recommendation": "Consider optimizing context or increasing size limit"
            })
        
        if metrics["recent_updates_1h"] > 20:
            alerts.append({
                "level": "warning",
                "message": f"High update frequency: {metrics['recent_updates_1h']} updates/hour",
                "recommendation": "Consider increasing batch interval or update threshold"
            })
        
        recent_errors = [e for e in self.performance_data["error_log"]
                        if datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(hours=1)]
        
        if len(recent_errors) > 5:
            alerts.append({
                "level": "error",
                "message": f"High error rate: {len(recent_errors)} errors/hour",
                "recommendation": "Check system logs and fix underlying issues"
            })
        
        return alerts
    
    def _get_recommendations(self) -> List[str]:
        """Get performance optimization recommendations."""
        recommendations = []
        metrics = self.performance_data["system_metrics"]
        
        if metrics["claude_size_percentage"] > 80:
            recommendations.append("Consider implementing domain-specific context files")
        
        if metrics["recent_updates_1h"] > 15:
            recommendations.append("Increase batch interval to reduce update frequency")
        
        if len(self.performance_data["context_updates"]) > 0:
            avg_time = sum(u.get("update_time", 0) for u in self.performance_data["context_updates"]) / len(self.performance_data["context_updates"])
            if avg_time > 3.0:
                recommendations.append("Optimize context generation for faster updates")
        
        return recommendations
    
    def save_performance_data(self, file_path: str = None):
        """Save performance data to file."""
        if file_path is None:
            file_path = self.claude_dir / "performance_data.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.performance_data, f, indent=2)
            self.logger.info(f"Performance data saved to {file_path}")
        except Exception as e:
            self.record_error("save_data", str(e))
    
    def load_performance_data(self, file_path: str = None):
        """Load performance data from file."""
        if file_path is None:
            file_path = self.claude_dir / "performance_data.json"
        
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    self.performance_data = json.load(f)
                self.logger.info(f"Performance data loaded from {file_path}")
            except Exception as e:
                self.record_error("load_data", str(e))

def main():
    """Main entry point for Performance Dashboard."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Performance Dashboard for Smart Context Optimization")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--report", action="store_true", help="Generate performance report")
    parser.add_argument("--save", action="store_true", help="Save performance data")
    parser.add_argument("--load", action="store_true", help="Load performance data")
    parser.add_argument("--alerts", action="store_true", help="Show current alerts")
    
    args = parser.parse_args()
    
    dashboard = PerformanceDashboard(args.project_root)
    
    if args.load:
        dashboard.load_performance_data()
    
    if args.start:
        dashboard.start_monitoring()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            dashboard.stop_monitoring()
    
    elif args.report:
        report = dashboard.get_performance_report()
        print(json.dumps(report, indent=2))
    
    elif args.save:
        dashboard.save_performance_data()
    
    elif args.alerts:
        alerts = dashboard._get_alerts()
        for alert in alerts:
            print(f"[{alert['level'].upper()}] {alert['message']}")
            print(f"  Recommendation: {alert['recommendation']}")
    
    else:
        print("No action specified. Use --help for options.")

if __name__ == "__main__":
    main()
