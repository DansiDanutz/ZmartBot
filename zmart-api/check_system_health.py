#!/usr/bin/env python3
"""
System Health Check for IntoTheCryptoverse Automation
Monitors all components and provides status report
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple
import psutil

class SystemHealthChecker:
    """Check health of the automation system"""

    def __init__(self):
        self.risk_grids_dir = Path("extracted_risk_grids")
        self.validation_dir = Path("risk_grid_validation")
        self.sync_logs_dir = Path("sync_logs")
        self.scheduler_state = Path("scheduler_state.json")
        self.scheduler_pid = Path("scheduler.pid")

    def check_scheduler_status(self) -> Tuple[str, Dict]:
        """Check if scheduler is running"""
        status = "❌ Not Running"
        details = {}

        # Check PID file
        if self.scheduler_pid.exists():
            with open(self.scheduler_pid, 'r') as f:
                pid = int(f.read().strip())

            # Check if process exists
            if psutil.pid_exists(pid):
                status = f"✅ Running (PID: {pid})"

                # Check process details
                try:
                    process = psutil.Process(pid)
                    details["cpu_percent"] = process.cpu_percent()
                    details["memory_mb"] = process.memory_info().rss / 1024 / 1024
                    details["uptime_hours"] = (datetime.now() - datetime.fromtimestamp(process.create_time())).total_seconds() / 3600
                except:
                    pass

        # Check scheduler state
        if self.scheduler_state.exists():
            with open(self.scheduler_state, 'r') as f:
                state = json.load(f)
                details["state"] = state

        return status, details

    def check_last_run(self) -> Tuple[str, Dict]:
        """Check last successful run"""
        if not self.scheduler_state.exists():
            return "⚠️ No runs recorded", {}

        with open(self.scheduler_state, 'r') as f:
            state = json.load(f)

        last_run = state.get("last_successful_run")
        if not last_run:
            return "⚠️ No successful runs", {}

        last_run_dt = datetime.fromisoformat(last_run)
        time_since = datetime.now() - last_run_dt
        hours_since = time_since.total_seconds() / 3600

        if hours_since < 72:
            status = f"✅ {last_run_dt.strftime('%Y-%m-%d %H:%M')}"
        elif hours_since < 96:
            status = f"⚠️ {last_run_dt.strftime('%Y-%m-%d %H:%M')} (overdue)"
        else:
            status = f"❌ {last_run_dt.strftime('%Y-%m-%d %H:%M')} (very overdue)"

        return status, {
            "hours_since": hours_since,
            "symbols_updated": state.get("symbols_updated", 0)
        }

    def check_next_run(self) -> str:
        """Check when next run is scheduled"""
        if not self.scheduler_state.exists():
            return "Unknown"

        with open(self.scheduler_state, 'r') as f:
            state = json.load(f)

        next_run = state.get("next_scheduled_run")
        if next_run:
            next_run_dt = datetime.fromisoformat(next_run)
            time_until = next_run_dt - datetime.now()
            hours = time_until.total_seconds() / 3600

            if hours > 0:
                return f"{next_run_dt.strftime('%Y-%m-%d %H:%M')} ({hours:.1f}h)"
            else:
                return f"{next_run_dt.strftime('%Y-%m-%d %H:%M')} (overdue)"

        return "Not scheduled"

    def check_risk_grids(self) -> Tuple[int, int, float]:
        """Check risk grid files"""
        if not self.risk_grids_dir.exists():
            return 0, 0, 0

        grid_files = list(self.risk_grids_dir.glob("*_risk_grid.json"))
        total = len(grid_files)

        # Check how many are up to date (< 72 hours old)
        up_to_date = 0
        for file in grid_files:
            age = datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)
            if age.total_seconds() < 72 * 3600:
                up_to_date += 1

        percentage = (up_to_date / total * 100) if total > 0 else 0

        return total, up_to_date, percentage

    def check_latest_reports(self) -> Dict:
        """Check latest scrape and sync reports"""
        reports = {}

        # Latest scrape report
        if self.validation_dir.exists():
            scrape_reports = list(self.validation_dir.glob("mcp_scrape_report_*.json"))
            if scrape_reports:
                latest_scrape = max(scrape_reports, key=lambda p: p.stat().st_mtime)
                with open(latest_scrape, 'r') as f:
                    data = json.load(f)
                    reports["scrape"] = {
                        "timestamp": data.get("timestamp"),
                        "success_rate": data.get("success_rate"),
                        "successful": data.get("successful_count"),
                        "failed": data.get("failed_count")
                    }

        # Latest sync report
        if self.sync_logs_dir.exists():
            sync_reports = list(self.sync_logs_dir.glob("sync_report_*.json"))
            if sync_reports:
                latest_sync = max(sync_reports, key=lambda p: p.stat().st_mtime)
                with open(latest_sync, 'r') as f:
                    data = json.load(f)
                    reports["sync"] = {
                        "timestamp": data.get("timestamp"),
                        "success_rate": data.get("success_rate"),
                        "successful": data.get("total_successful"),
                        "failed": data.get("total_failed")
                    }

        return reports

    def generate_health_report(self) -> str:
        """Generate complete health report"""
        report = []
        report.append("\n" + "🎯"*20)
        report.append("CRYPTOVERSE AUTOMATION HEALTH CHECK")
        report.append("="*60)
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*60)

        # Scheduler status
        scheduler_status, scheduler_details = self.check_scheduler_status()
        report.append(f"\n📅 SCHEDULER")
        report.append(f"Status: {scheduler_status}")

        if "uptime_hours" in scheduler_details:
            report.append(f"Uptime: {scheduler_details['uptime_hours']:.1f} hours")
            report.append(f"CPU: {scheduler_details['cpu_percent']:.1f}%")
            report.append(f"Memory: {scheduler_details['memory_mb']:.1f} MB")

        # Last run
        last_run_status, last_run_details = self.check_last_run()
        report.append(f"\n⏰ LAST RUN")
        report.append(f"Status: {last_run_status}")

        if "hours_since" in last_run_details:
            report.append(f"Hours ago: {last_run_details['hours_since']:.1f}")
            report.append(f"Symbols updated: {last_run_details['symbols_updated']}")

        # Next run
        next_run = self.check_next_run()
        report.append(f"\n⏭️ NEXT RUN")
        report.append(f"Scheduled: {next_run}")

        # Risk grids
        total_grids, up_to_date, percentage = self.check_risk_grids()
        report.append(f"\n📊 RISK GRIDS")
        report.append(f"Total files: {total_grids}")
        report.append(f"Up to date: {up_to_date}/{total_grids} ({percentage:.1f}%)")

        # Latest reports
        reports = self.check_latest_reports()
        if reports:
            report.append(f"\n📈 LATEST REPORTS")

            if "scrape" in reports:
                scrape = reports["scrape"]
                report.append(f"Scrape: {scrape['success_rate']} ({scrape['successful']}/{scrape['successful']+scrape['failed']})")

            if "sync" in reports:
                sync = reports["sync"]
                report.append(f"Sync: {sync['success_rate']} ({sync['successful']}/{sync['successful']+sync['failed']})")

        # Overall health
        report.append(f"\n🏥 OVERALL HEALTH")

        health_score = 0
        health_issues = []

        # Check scheduler
        if "Running" in scheduler_status:
            health_score += 25
        else:
            health_issues.append("Scheduler not running")

        # Check last run
        if "hours_since" in last_run_details:
            if last_run_details["hours_since"] < 96:
                health_score += 25
            else:
                health_issues.append("Last run overdue")

        # Check grid freshness
        if percentage > 90:
            health_score += 25
        elif percentage > 70:
            health_score += 15
            health_issues.append("Some grids outdated")
        else:
            health_issues.append("Many grids outdated")

        # Check reports
        if reports:
            if "scrape" in reports and "90%" in reports["scrape"]["success_rate"]:
                health_score += 25
            else:
                health_issues.append("Low scrape success rate")

        # Health verdict
        if health_score >= 90:
            verdict = "✅ EXCELLENT"
        elif health_score >= 70:
            verdict = "🟡 GOOD"
        elif health_score >= 50:
            verdict = "⚠️ NEEDS ATTENTION"
        else:
            verdict = "❌ CRITICAL"

        report.append(f"Score: {health_score}/100")
        report.append(f"Status: {verdict}")

        if health_issues:
            report.append(f"Issues: {', '.join(health_issues)}")

        # Recommendations
        if health_issues:
            report.append(f"\n💡 RECOMMENDATIONS")

            if "Scheduler not running" in health_issues:
                report.append("• Start scheduler: python3 cryptoverse_72h_scheduler.py --start")

            if "overdue" in " ".join(health_issues):
                report.append("• Force update: python3 cryptoverse_72h_scheduler.py --force")

            if "outdated" in " ".join(health_issues):
                report.append("• Run manual scrape: python3 cryptoverse_mcp_scraper.py --complete")

        report.append("\n" + "="*60)

        return "\n".join(report)

def main():
    """Main entry point"""
    checker = SystemHealthChecker()
    report = checker.generate_health_report()
    print(report)

    # Save report to file
    report_file = Path("health_report_latest.txt")
    with open(report_file, 'w') as f:
        f.write(report)

    print(f"\n📄 Report saved to {report_file}")

if __name__ == "__main__":
    main()