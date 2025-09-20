#!/usr/bin/env python3
"""
System Optimization Manager
Comprehensive management system for all ZmartBot optimizations
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout

class SystemOptimizationManager:
    """Manages all system optimization components"""
    
    def __init__(self):
        self.console = Console()
        self.config_file = Path("system_optimization_config.json")
        self.config = self.load_config()
        self.optimization_components = self.initialize_components()
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.component_threads = {}  # Initialize component threads dictionary
        self.stop_event = threading.Event()  # Initialize stop event
        
    def load_config(self):
        """Load system optimization configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        default_config = {
            "optimization_enabled": True,
            "monitoring_interval": 60,  # seconds
            "auto_optimization": True,
            "components": {
                "mdc_monitoring": {
                    "enabled": True,
                    "config_file": "mdc_monitoring_config.json"
                },
                "performance_dashboard": {
                    "enabled": True,
                    "refresh_interval": 5
                },
                "alert_handling": {
                    "enabled": True,
                    "config_file": "mdc_monitoring_config.json"
                },
                "api_key_monitoring": {
                    "enabled": True,
                    "config_file": "api_key_monitoring_config.json"
                },
                "performance_reporting": {
                    "enabled": True,
                    "config_file": "performance_reporting_config.json",
                    "report_frequency": "daily"
                },
                "expanded_monitoring": {
                    "enabled": True,
                    "config_file": "expanded_monitoring_config.json"
                }
            },
            "optimization_rules": {
                "auto_restart_unhealthy_services": True,
                "auto_scale_on_high_load": False,
                "auto_cleanup_old_logs": True,
                "auto_optimize_mdc_files": True
            }
        }
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config):
        """Save system optimization configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def initialize_components(self):
        """Initialize all optimization components"""
        components = {}
        
        try:
            # MDC Monitoring
            if self.config["components"]["mdc_monitoring"]["enabled"]:
                from enhanced_mdc_monitor import EnhancedMDCMonitor
                components["mdc_monitor"] = EnhancedMDCMonitor()
            
            # Performance Dashboard
            if self.config["components"]["performance_dashboard"]["enabled"]:
                from mdc_performance_dashboard import MDCPerformanceDashboard
                components["performance_dashboard"] = MDCPerformanceDashboard()
            
            # Alert Handler
            if self.config["components"]["alert_handling"]["enabled"]:
                from mdc_alert_handler import MDCAlertHandler
                components["alert_handler"] = MDCAlertHandler()
            
            # API Key Monitor
            if self.config["components"]["api_key_monitoring"]["enabled"]:
                from api_key_monitor import APIKeyMonitor
                components["api_key_monitor"] = APIKeyMonitor()
            
            # Performance Reporter
            if self.config["components"]["performance_reporting"]["enabled"]:
                from automated_performance_reporter import AutomatedPerformanceReporter
                components["performance_reporter"] = AutomatedPerformanceReporter()
            
            # Expanded Service Monitor
            if self.config["components"]["expanded_monitoring"]["enabled"]:
                from expanded_service_monitor import ExpandedServiceMonitor
                components["expanded_monitor"] = ExpandedServiceMonitor()
            
        except ImportError as e:
            self.console.print(f"[red]Warning: Could not import optimization component: {e}[/red]")
        
        return components
    
    def get_component_status(self) -> Dict[str, Dict]:
        """Get status of all optimization components"""
        status = {}
        
        for name, component in self.optimization_components.items():
            try:
                if hasattr(component, 'get_status'):
                    status[name] = component.get_status()
                elif hasattr(component, 'is_running'):
                    status[name] = {"is_running": component.is_running}
                else:
                    status[name] = {"status": "unknown"}
            except Exception as e:
                status[name] = {"error": str(e)}
        
        return status
    
    def start_optimization_monitoring(self):
        """Start continuous optimization monitoring"""
        if self.monitoring_active:
            self.console.print("[yellow]Optimization monitoring is already active[/yellow]")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.console.print("[green]System optimization monitoring started[/green]")
    
    def stop_optimization_monitoring(self):
        """Stop optimization monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.console.print("[yellow]System optimization monitoring stopped[/yellow]")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Check component health
                self.check_component_health()
                
                # Run auto-optimizations
                if self.config.get("auto_optimization", True):
                    self.run_auto_optimizations()
                
                # Generate performance report if needed
                self.check_performance_reporting()
                
                time.sleep(self.config.get("monitoring_interval", 60))
                
            except Exception as e:
                self.console.print(f"[red]Error in monitoring loop: {e}[/red]")
                time.sleep(10)  # Wait before retrying
    
    def check_component_health(self):
        """Check health of all optimization components"""
        for name, component in self.optimization_components.items():
            try:
                if hasattr(component, 'get_status'):
                    status = component.get_status()
                    if not status.get("is_running", True):
                        self.console.print(f"[yellow]Component {name} is not running, attempting restart[/yellow]")
                        self.restart_component(name)
            except Exception as e:
                self.console.print(f"[red]Error checking component {name}: {e}[/red]")
    
    def restart_component(self, component_name: str):
        """Restart a specific optimization component"""
        try:
            if component_name == "mdc_monitor":
                from enhanced_mdc_monitor import EnhancedMDCMonitor
                self.optimization_components["mdc_monitor"] = EnhancedMDCMonitor()
                self.optimization_components["mdc_monitor"].start_monitoring()
            elif component_name == "expanded_monitor":
                from expanded_service_monitor import ExpandedServiceMonitor
                self.optimization_components["expanded_monitor"] = ExpandedServiceMonitor()
                # Start monitoring in background
                threading.Thread(target=self.optimization_components["expanded_monitor"].start_monitoring, daemon=True).start()
            
            self.console.print(f"[green]Component {component_name} restarted successfully[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Failed to restart component {component_name}: {e}[/red]")
    
    def run_auto_optimizations(self):
        """Run automatic optimizations based on rules"""
        rules = self.config.get("optimization_rules", {})
        
        # Auto cleanup old logs
        if rules.get("auto_cleanup_old_logs", True):
            self.cleanup_old_logs()
        
        # Auto optimize MDC files
        if rules.get("auto_optimize_mdc_files", True):
            self.optimize_mdc_files()
    
    def cleanup_old_logs(self):
        """Clean up old log files"""
        log_dirs = ["logs", "performance_reports", "."]
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for log_dir in log_dirs:
            log_path = Path(log_dir)
            if log_path.exists():
                for log_file in log_path.glob("*.log"):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        try:
                            log_file.unlink()
                            self.console.print(f"[blue]Cleaned up old log: {log_file}[/blue]")
                        except Exception as e:
                            self.console.print(f"[red]Failed to clean up {log_file}: {e}[/red]")
    
    def optimize_mdc_files(self):
        """Optimize MDC files using smart context optimizer"""
        try:
            from smart_context_optimizer import SmartContextOptimizer
            optimizer = SmartContextOptimizer()
            optimizer.analyze_context()
            optimizer.generate_claude_md()
            self.console.print("[blue]MDC files optimized[/blue]")
        except Exception as e:
            self.console.print(f"[red]Failed to optimize MDC files: {e}[/red]")
    
    def check_performance_reporting(self):
        """Check if performance reporting is due"""
        try:
            reporter = self.optimization_components.get("performance_reporter")
            if reporter:
                # Check if it's time for a report (simplified logic)
                now = datetime.now()
                if now.hour == 9 and now.minute < 5:  # Around 9:00 AM
                    reporter.generate_and_distribute_report()
                    self.console.print("[blue]Performance report generated[/blue]")
        except Exception as e:
            self.console.print(f"[red]Error in performance reporting: {e}[/red]")
    
    def create_optimization_dashboard(self):
        """Create comprehensive optimization dashboard"""
        layout = Layout()
        
        layout.split_column(
            Layout(Panel.fit("[bold blue]ZmartBot System Optimization Manager[/bold blue]", border_style="blue")),
            Layout(name="main"),
            Layout(Panel.fit(f"[bold green]Status: {'ACTIVE' if self.monitoring_active else 'INACTIVE'}[/bold green]", border_style="green"))
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Component Status Table
        component_table = Table(title="Optimization Components")
        component_table.add_column("Component", style="cyan")
        component_table.add_column("Status", style="magenta")
        component_table.add_column("Details", style="green")
        
        component_status = self.get_component_status()
        for name, status in component_status.items():
            if "error" in status:
                status_text = f"[red]ERROR[/red]"
                details = status["error"]
            elif status.get("is_running", False):
                status_text = "[green]RUNNING[/green]"
                details = "Operational"
            else:
                status_text = "[yellow]STOPPED[/yellow]"
                details = "Not running"
            
            component_table.add_row(name, status_text, details)
        
        # System Metrics Table
        metrics_table = Table(title="System Metrics")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="magenta")
        metrics_table.add_column("Status", style="green")
        
        # Get system metrics
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            metrics_table.add_row("CPU Usage", f"{cpu_percent:.1f}%", "🟢" if cpu_percent < 80 else "🟡" if cpu_percent < 90 else "🔴")
            metrics_table.add_row("Memory Usage", f"{memory_percent:.1f}%", "🟢" if memory_percent < 80 else "🟡" if memory_percent < 90 else "🔴")
            metrics_table.add_row("Disk Usage", f"{disk_percent:.1f}%", "🟢" if disk_percent < 80 else "🟡" if disk_percent < 90 else "🔴")
            
        except Exception as e:
            metrics_table.add_row("System Metrics", "Error", f"[red]{e}[/red]")
        
        # Optimization Rules Table
        rules_table = Table(title="Optimization Rules")
        rules_table.add_column("Rule", style="cyan")
        rules_table.add_column("Enabled", style="magenta")
        
        rules = self.config.get("optimization_rules", {})
        for rule, enabled in rules.items():
            status = "✅" if enabled else "❌"
            rules_table.add_row(rule.replace("_", " ").title(), status)
        
        layout["left"].update(Panel(component_table, title="Component Status", border_style="blue"))
        layout["right"].split_column(
            Layout(Panel(metrics_table, title="System Metrics", border_style="green")),
            Layout(Panel(rules_table, title="Optimization Rules", border_style="yellow"))
        )
        
        return layout
    
    def run_optimization_dashboard(self):
        """Run the optimization dashboard"""
        with Live(self.create_optimization_dashboard(), refresh_per_second=1) as live:
            try:
                while True:
                    time.sleep(1)
                    live.update(self.create_optimization_dashboard())
            except KeyboardInterrupt:
                self.console.print("\n[bold red]Optimization dashboard stopped[/bold red]")
    
    def generate_optimization_report(self) -> Dict:
        """Generate comprehensive optimization report"""
        report = {
            "report_id": f"opt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "optimization_status": {
                "monitoring_active": self.monitoring_active,
                "components_initialized": len(self.optimization_components),
                "auto_optimization_enabled": self.config.get("auto_optimization", True)
            },
            "component_status": self.get_component_status(),
            "system_metrics": self.get_system_metrics(),
            "optimization_rules": self.config.get("optimization_rules", {}),
            "recommendations": self.generate_optimization_recommendations()
        }
        
        return report
    
    def get_system_metrics(self) -> Dict:
        """Get current system metrics"""
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Check component status
        component_status = self.get_component_status()
        for name, status in component_status.items():
            if "error" in status:
                recommendations.append(f"Fix error in {name}: {status['error']}")
            elif not status.get("is_running", True):
                recommendations.append(f"Restart {name} component")
        
        # Check system metrics
        system_metrics = self.get_system_metrics()
        if "error" not in system_metrics:
            if system_metrics.get("cpu_percent", 0) > 80:
                recommendations.append("High CPU usage detected - consider optimization")
            if system_metrics.get("memory_percent", 0) > 80:
                recommendations.append("High memory usage detected - consider scaling")
            if system_metrics.get("disk_percent", 0) > 80:
                recommendations.append("High disk usage detected - consider cleanup")
        
        if not recommendations:
            recommendations.append("System optimization is running smoothly")
        
        return recommendations
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all optimization components"""
        status = {
            "monitoring_active": self.monitoring_active,
            "components_initialized": len(self.optimization_components),
            "component_status": {},
            "threads_running": len([t for t in self.component_threads.values() if t.is_alive()]),
            "last_health_check": datetime.now().isoformat(),
            "config_loaded": bool(self.config),
            "stop_event_set": self.stop_event.is_set()
        }
        
        # Get status from each component
        for name, component in self.optimization_components.items():
            try:
                if hasattr(component, 'get_status'):
                    status["component_status"][name] = component.get_status()
                else:
                    status["component_status"][name] = {"status": "initialized", "details": "No status method available"}
            except Exception as e:
                status["component_status"][name] = {"status": "error", "details": str(e)}
        
        return status

# Global optimization manager instance
optimization_manager = SystemOptimizationManager()

if __name__ == "__main__":
    manager = SystemOptimizationManager()
    
    print("🚀 ZmartBot System Optimization Manager")
    print("=" * 50)
    
    # Start monitoring
    manager.start_optimization_monitoring()
    
    # Generate initial report
    report = manager.generate_optimization_report()
    print(f"\n📊 Optimization Report Generated:")
    print(f"   Report ID: {report['report_id']}")
    print(f"   Components: {report['optimization_status']['components_initialized']}")
    print(f"   Monitoring: {'Active' if report['optimization_status']['monitoring_active'] else 'Inactive'}")
    print(f"   Recommendations: {len(report['recommendations'])}")
    
    # Run dashboard
    try:
        manager.run_optimization_dashboard()
    except KeyboardInterrupt:
        manager.stop_optimization_monitoring()
        print("\n✅ System optimization manager stopped")
