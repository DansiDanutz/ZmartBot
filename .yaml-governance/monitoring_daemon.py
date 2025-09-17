#!/usr/bin/env python3
"""
YAML Monitoring Daemon - Continuous YAML Governance Monitoring
Created: 2025-08-31
Purpose: Monitor YAML files for violations and send alerts
Level: 2 (Production Ready)
Port: 8899 (Monitoring Port)
Passport: YAML-MONITOR-8899-L2
Owner: zmartbot-system
Status: DAEMON
"""

import os
import time
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import threading
import schedule

from yaml_validator import YAMLGovernanceValidator

class YAMLMonitoringDaemon:
    """Continuous monitoring daemon for YAML governance"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.governance_dir = self.root_dir / ".yaml-governance"
        self.monitoring_db = self.governance_dir / "monitoring.db"
        self.alerts_log = self.governance_dir / "alerts.log"
        self.last_check = datetime.now()
        self.running = False
        
        self.setup_monitoring_db()
        
    def setup_monitoring_db(self):
        """Setup monitoring database"""
        self.governance_dir.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.monitoring_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                service_name TEXT,
                yaml_path TEXT,
                issue_description TEXT,
                resolved BOOLEAN DEFAULT FALSE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_yaml_files INTEGER,
                duplicates_count INTEGER,
                port_conflicts_count INTEGER,
                location_violations_count INTEGER,
                content_violations_count INTEGER,
                status TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
    def log_event(self, event_type: str, severity: str, service_name: str = None, 
                 yaml_path: str = None, description: str = ""):
        """Log monitoring event"""
        conn = sqlite3.connect(self.monitoring_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO monitoring_events 
            (timestamp, event_type, severity, service_name, yaml_path, issue_description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), event_type, severity, service_name, yaml_path, description))
        
        conn.commit()
        conn.close()
        
        # Also log to file
        with open(self.alerts_log, 'a') as f:
            f.write(f"{datetime.now().isoformat()} [{severity}] {event_type}: {description}\n")
            
        print(f"🚨 [{severity}] {event_type}: {description}")
        
    def log_monitoring_stats(self, validation_results: dict):
        """Log monitoring statistics"""
        conn = sqlite3.connect(self.monitoring_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO monitoring_stats 
            (timestamp, total_yaml_files, duplicates_count, port_conflicts_count, 
             location_violations_count, content_violations_count, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            validation_results.get("total_yaml_files", 0),
            len(validation_results.get("duplicates", {})),
            len(validation_results.get("port_conflicts", {})),
            len(validation_results.get("location_violations", [])),
            len(validation_results.get("content_violations", [])),
            validation_results.get("status", "UNKNOWN")
        ))
        
        conn.commit()
        conn.close()
        
    def check_yaml_governance(self):
        """Run YAML governance check"""
        try:
            validator = YAMLGovernanceValidator()
            results = validator.run_validation()
            
            # Log statistics
            self.log_monitoring_stats(results)
            
            if results["status"] == "FAILED":
                # Process duplicates
                if results["duplicates"]:
                    for service, paths in results["duplicates"].items():
                        self.log_event(
                            event_type="DUPLICATE_YAML",
                            severity="HIGH",
                            service_name=service,
                            description=f"Service '{service}' has {len(paths)} duplicate YAML files: {', '.join(paths)}"
                        )
                
                # Process port conflicts
                if results["port_conflicts"]:
                    for port, paths in results["port_conflicts"].items():
                        self.log_event(
                            event_type="PORT_CONFLICT",
                            severity="CRITICAL", 
                            description=f"Port {port} conflict between services: {', '.join(paths)}"
                        )
                
                # Process location violations
                for violation in results["location_violations"]:
                    self.log_event(
                        event_type="LOCATION_VIOLATION",
                        severity="MEDIUM",
                        yaml_path=violation["path"],
                        description=f"YAML in invalid location: {violation['error']}"
                    )
                
                # Process content violations
                for violation in results["content_violations"]:
                    self.log_event(
                        event_type="CONTENT_VIOLATION",
                        severity="MEDIUM",
                        yaml_path=violation["path"],
                        description=f"Content validation errors: {', '.join(violation['errors'])}"
                    )
                    
                return False
            else:
                print(f"✅ YAML governance check passed - {results['total_yaml_files']} files validated")
                return True
                
        except Exception as e:
            self.log_event(
                event_type="MONITORING_ERROR",
                severity="HIGH",
                description=f"Error during YAML governance check: {str(e)}"
            )
            return False
            
    def check_for_new_yaml_files(self):
        """Check for new YAML files that might need validation"""
        import glob
        
        current_yaml_files = set(glob.glob("**/service.yaml", recursive=True))
        
        # Load previous file list if exists
        state_file = self.governance_dir / "file_state.json"
        previous_files = set()
        
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
                previous_files = set(state.get("yaml_files", []))
        
        # Find new files
        new_files = current_yaml_files - previous_files
        if new_files:
            for new_file in new_files:
                self.log_event(
                    event_type="NEW_YAML_DETECTED",
                    severity="INFO",
                    yaml_path=new_file,
                    description=f"New YAML file detected: {new_file}"
                )
        
        # Save current state
        with open(state_file, 'w') as f:
            json.dump({"yaml_files": list(current_yaml_files), "last_check": datetime.now().isoformat()}, f)
            
        return len(new_files)
        
    def generate_daily_report(self):
        """Generate daily monitoring report"""
        conn = sqlite3.connect(self.monitoring_db)
        cursor = conn.cursor()
        
        # Get events from last 24 hours
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        
        cursor.execute("""
            SELECT event_type, severity, COUNT(*) as count
            FROM monitoring_events 
            WHERE timestamp > ? 
            GROUP BY event_type, severity
            ORDER BY severity DESC, count DESC
        """, (yesterday,))
        
        events = cursor.fetchall()
        
        cursor.execute("""
            SELECT * FROM monitoring_stats 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (yesterday,))
        
        latest_stats = cursor.fetchone()
        
        # Generate report
        report = f"""
YAML Governance Daily Report - {datetime.now().strftime('%Y-%m-%d')}
================================================================

Latest Statistics:
- Total YAML Files: {latest_stats[2] if latest_stats else 'N/A'}
- Duplicates: {latest_stats[3] if latest_stats else 'N/A'}
- Port Conflicts: {latest_stats[4] if latest_stats else 'N/A'}
- Location Violations: {latest_stats[5] if latest_stats else 'N/A'}
- Content Violations: {latest_stats[6] if latest_stats else 'N/A'}
- Overall Status: {latest_stats[7] if latest_stats else 'N/A'}

Events in Last 24 Hours:
"""
        
        if events:
            for event_type, severity, count in events:
                report += f"- {event_type} ({severity}): {count} occurrences\n"
        else:
            report += "- No events recorded\n"
        
        report += f"\nGenerated: {datetime.now().isoformat()}\n"
        
        # Save report
        report_file = self.governance_dir / f"daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
            
        print(f"📊 Daily report generated: {report_file}")
        
        conn.close()
        return report
        
    def cleanup_old_data(self):
        """Cleanup old monitoring data (keep last 30 days)"""
        conn = sqlite3.connect(self.monitoring_db)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
        
        cursor.execute("DELETE FROM monitoring_events WHERE timestamp < ?", (cutoff_date,))
        cursor.execute("DELETE FROM monitoring_stats WHERE timestamp < ?", (cutoff_date,))
        
        conn.commit()
        
        deleted_events = cursor.rowcount
        print(f"🧹 Cleaned up old monitoring data - removed {deleted_events} old records")
        
        conn.close()
        
    def start_monitoring(self, check_interval_minutes: int = 15):
        """Start continuous monitoring"""
        print(f"🔍 Starting YAML monitoring daemon (check interval: {check_interval_minutes}min)")
        
        # Schedule regular checks
        schedule.every(check_interval_minutes).minutes.do(self.check_yaml_governance)
        schedule.every(check_interval_minutes).minutes.do(self.check_for_new_yaml_files)
        schedule.every().day.at("09:00").do(self.generate_daily_report)
        schedule.every().week.do(self.cleanup_old_data)
        
        self.running = True
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            print(f"\n🛑 Monitoring daemon stopped")
            self.running = False
            
    def stop_monitoring(self):
        """Stop monitoring daemon"""
        self.running = False

def main():
    """Main monitoring daemon"""
    import argparse
    
    parser = argparse.ArgumentParser(description="YAML Monitoring Daemon")
    parser.add_argument('--interval', type=int, default=15, help='Check interval in minutes')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--report', action='store_true', help='Generate daily report and exit')
    
    args = parser.parse_args()
    
    daemon = YAMLMonitoringDaemon()
    
    if args.report:
        daemon.generate_daily_report()
    elif args.once:
        daemon.check_yaml_governance()
        daemon.check_for_new_yaml_files()
    else:
        daemon.start_monitoring(args.interval)

if __name__ == "__main__":
    main()