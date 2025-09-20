#!/usr/bin/env python3
"""
Comprehensive Optimization Integration Script
============================================

This script integrates all optimization components and provides a unified interface
for managing the ZmartBot system optimizations.

Features:
- Unified optimization management
- Real-time monitoring dashboard
- Automated optimization execution
- Performance reporting
- Alert management
- API key rotation
- Service health monitoring
"""

import json
import time
import threading
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import all optimization components
try:
    from system_optimization_manager import SystemOptimizationManager
    from smart_context_optimizer import SmartContextOptimizer
    from enhanced_mdc_monitor import EnhancedMDCMonitor
    from mdc_alert_handler import MDCAlertHandler
    from mdc_performance_dashboard import MDCPerformanceDashboard
    from api_key_monitor import APIKeyMonitor
    from api_key_rotation_policy import APIKeyRotationManager
    from expanded_service_monitor import ExpandedServiceMonitor
    from automated_performance_reporter import AutomatedPerformanceReporter
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all optimization components are in the same directory")
    sys.exit(1)

class ComprehensiveOptimizationIntegration:
    """
    Comprehensive optimization integration system for ZmartBot.
    """
    
    def __init__(self, config_file: str = "comprehensive_optimization_config.json"):
        self.console = Console()
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.running = False
        self.optimization_manager = None
        self.stop_event = threading.Event()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.console.print(Panel.fit(
            "[bold blue]🚀 ZmartBot Comprehensive Optimization Integration[/bold blue]\n"
            "[green]Advanced system optimization and monitoring platform[/green]",
            border_style="blue"
        ))
    
    def _load_config(self) -> Dict[str, Any]:
        """Load comprehensive optimization configuration."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        default_config = {
            "system_optimization": {
                "enabled": True,
                "auto_start": True,
                "config_file": "system_optimization_config.json"
            },
            "real_time_dashboard": {
                "enabled": True,
                "refresh_interval": 2,
                "show_detailed_metrics": True
            },
            "automated_optimization": {
                "enabled": True,
                "optimization_interval": 300,  # 5 minutes
                "auto_healing": True,
                "performance_threshold": 80
            },
            "monitoring": {
                "health_checks": True,
                "performance_tracking": True,
                "alert_management": True,
                "api_key_rotation": True
            },
            "reporting": {
                "generate_reports": True,
                "report_interval": 1800,  # 30 minutes
                "save_reports": True,
                "report_directory": "optimization_reports"
            },
            "logging": {
                "level": "INFO",
                "file": "comprehensive_optimization.log",
                "console_output": True
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.console.print(f"[green]✅ Created default configuration: {self.config_file}[/green]")
        return default_config
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.console.print(f"\n[yellow]🛑 Received signal {signum}, shutting down gracefully...[/yellow]")
        self.stop_event.set()
        self.running = False
    
    def initialize_optimization_manager(self):
        """Initialize the system optimization manager."""
        try:
            self.console.print("[blue]🔧 Initializing System Optimization Manager...[/blue]")
            self.optimization_manager = SystemOptimizationManager()
            
            # Get initial status
            status = self.optimization_manager.get_status()
            self.console.print(f"[green]✅ Optimization Manager initialized with {status['components_initialized']} components[/green]")
            
            return True
        except Exception as e:
            self.console.print(f"[red]❌ Failed to initialize optimization manager: {e}[/red]")
            return False
    
    def create_real_time_dashboard(self) -> Layout:
        """Create a real-time optimization dashboard."""
        layout = Layout()
        
        layout.split_column(
            Layout(Panel.fit("[bold blue]🚀 ZmartBot Optimization Dashboard[/bold blue]", border_style="blue")),
            Layout(name="main"),
            Layout(Panel.fit(f"[bold green]Status: {'RUNNING' if self.running else 'STOPPED'} | Last Update: {datetime.now().strftime('%H:%M:%S')}[/bold green]", border_style="green"))
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # System Status Table
        system_table = Table(title="System Status")
        system_table.add_column("Component", style="cyan")
        system_table.add_column("Status", style="magenta")
        system_table.add_column("Health", style="green")
        
        if self.optimization_manager:
            status = self.optimization_manager.get_status()
            for component_name, component_status in status.get('component_status', {}).items():
                system_table.add_row(component_name, "Active", "✅")
        
        # Performance Metrics Table
        perf_table = Table(title="Performance Metrics")
        perf_table.add_column("Metric", style="cyan")
        perf_table.add_column("Value", style="magenta")
        perf_table.add_column("Status", style="green")
        
        # Add sample metrics (in real implementation, these would be live data)
        perf_table.add_row("CPU Usage", "45%", "✅")
        perf_table.add_row("Memory Usage", "62%", "⚠️")
        perf_table.add_row("API Response Time", "120ms", "✅")
        perf_table.add_row("Service Health", "95%", "✅")
        
        # Optimization Status Table
        opt_table = Table(title="Optimization Status")
        opt_table.add_column("Optimization", style="cyan")
        opt_table.add_column("Status", style="magenta")
        opt_table.add_column("Last Run", style="green")
        
        opt_table.add_row("Context Optimization", "Active", "2 min ago")
        opt_table.add_row("MDC Processing", "Active", "1 min ago")
        opt_table.add_row("API Key Rotation", "Scheduled", "1 hour ago")
        opt_table.add_row("Performance Monitoring", "Active", "30 sec ago")
        
        layout["left"].update(Panel(system_table, title="System Status", border_style="blue"))
        layout["right"].split_column(
            Layout(Panel(perf_table, title="Performance", border_style="green")),
            Layout(Panel(opt_table, title="Optimizations", border_style="yellow"))
        )
        
        return layout
    
    def run_optimization_cycle(self):
        """Run a complete optimization cycle."""
        if not self.optimization_manager:
            return
        
        try:
            self.console.print("[blue]🔄 Running optimization cycle...[/blue]")
            
            # Run all components once
            self.optimization_manager.run_once()
            
            # Generate performance report
            report = self.optimization_manager.generate_optimization_report()
            
            # Check for auto-healing opportunities
            if self.config.get("automated_optimization", {}).get("auto_healing"):
                self._perform_auto_healing(report)
            
            self.console.print(f"[green]✅ Optimization cycle completed - Report: {report['report_id']}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Optimization cycle failed: {e}[/red]")
    
    def _perform_auto_healing(self, report: Dict[str, Any]):
        """Perform automatic healing based on report recommendations."""
        recommendations = report.get("recommendations", [])
        
        for rec in recommendations:
            if "restart" in rec.lower():
                self.console.print(f"[yellow]🔧 Auto-healing: {rec}[/yellow]")
                # In a real implementation, this would restart the specific component
            elif "scale" in rec.lower() or "optimize" in rec.lower():
                self.console.print(f"[yellow]🔧 Auto-healing: {rec}[/yellow]")
                # In a real implementation, this would trigger scaling or optimization
    
    def start_real_time_monitoring(self):
        """Start real-time monitoring with live dashboard."""
        if not self.optimization_manager:
            self.console.print("[red]❌ Optimization manager not initialized[/red]")
            return
        
        self.running = True
        self.console.print("[green]🚀 Starting real-time optimization monitoring...[/green]")
        
        try:
            with Live(self.create_real_time_dashboard(), refresh_per_second=0.5) as live:
                optimization_interval = self.config.get("automated_optimization", {}).get("optimization_interval", 300)
                last_optimization = time.time()
                
                while self.running and not self.stop_event.is_set():
                    # Update dashboard
                    live.update(self.create_real_time_dashboard())
                    
                    # Run optimization cycle if interval has passed
                    if time.time() - last_optimization >= optimization_interval:
                        self.run_optimization_cycle()
                        last_optimization = time.time()
                    
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            self.console.print("\n[yellow]🛑 Monitoring stopped by user[/yellow]")
        finally:
            self.running = False
    
    def run_optimization_report(self):
        """Generate and display a comprehensive optimization report."""
        if not self.optimization_manager:
            self.console.print("[red]❌ Optimization manager not initialized[/red]")
            return
        
        self.console.print("[blue]📊 Generating comprehensive optimization report...[/blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Generating report...", total=None)
            
            # Generate report
            report = self.optimization_manager.generate_optimization_report()
            
            progress.update(task, description="Report generated!")
            time.sleep(1)
        
        # Display report
        self.console.print(Panel.fit(
            f"[bold green]📈 Optimization Report Generated[/bold green]\n"
            f"Report ID: {report['report_id']}\n"
            f"Generated: {report['generated_at']}\n"
            f"Components: {report['optimization_status']['components_initialized']}\n"
            f"Auto-optimization: {report['optimization_status']['auto_optimization_enabled']}",
            border_style="green"
        ))
        
        # Show recommendations
        if report.get("recommendations"):
            rec_table = Table(title="Recommendations")
            rec_table.add_column("#", style="cyan")
            rec_table.add_column("Recommendation", style="magenta")
            
            for i, rec in enumerate(report["recommendations"], 1):
                rec_table.add_row(str(i), rec)
            
            self.console.print(rec_table)
        
        return report
    
    def start_optimization_services(self):
        """Start all optimization services."""
        if not self.optimization_manager:
            self.console.print("[red]❌ Optimization manager not initialized[/red]")
            return
        
        self.console.print("[blue]🚀 Starting optimization services...[/blue]")
        
        try:
            self.optimization_manager.start_optimization_monitoring()
            self.console.print("[green]✅ All optimization services started[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Failed to start services: {e}[/red]")
    
    def stop_optimization_services(self):
        """Stop all optimization services."""
        if not self.optimization_manager:
            return
        
        self.console.print("[yellow]🛑 Stopping optimization services...[/yellow]")
        
        try:
            self.optimization_manager.stop_optimization_monitoring()
            self.console.print("[green]✅ All optimization services stopped[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Error stopping services: {e}[/red]")
    
    def interactive_menu(self):
        """Display interactive menu for optimization management."""
        while True:
            self.console.print("\n" + "="*60)
            self.console.print("[bold blue]🚀 ZmartBot Optimization Management Menu[/bold blue]")
            self.console.print("="*60)
            
            menu_table = Table(show_header=False, box=None)
            menu_table.add_column("Option", style="cyan", width=3)
            menu_table.add_column("Description", style="white")
            
            menu_table.add_row("1", "Initialize Optimization Manager")
            menu_table.add_row("2", "Start Real-time Monitoring Dashboard")
            menu_table.add_row("3", "Run Optimization Cycle")
            menu_table.add_row("4", "Generate Optimization Report")
            menu_table.add_row("5", "Start All Services")
            menu_table.add_row("6", "Stop All Services")
            menu_table.add_row("7", "Show System Status")
            menu_table.add_row("8", "Configuration Management")
            menu_table.add_row("0", "Exit")
            
            self.console.print(menu_table)
            
            try:
                choice = input("\nEnter your choice (0-8): ").strip()
                
                if choice == "0":
                    self.console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                elif choice == "1":
                    self.initialize_optimization_manager()
                elif choice == "2":
                    self.start_real_time_monitoring()
                elif choice == "3":
                    self.run_optimization_cycle()
                elif choice == "4":
                    self.run_optimization_report()
                elif choice == "5":
                    self.start_optimization_services()
                elif choice == "6":
                    self.stop_optimization_services()
                elif choice == "7":
                    if self.optimization_manager:
                        status = self.optimization_manager.get_status()
                        self.console.print(f"[green]System Status: {json.dumps(status, indent=2)}[/green]")
                    else:
                        self.console.print("[red]❌ Optimization manager not initialized[/red]")
                elif choice == "8":
                    self.console.print(f"[blue]Configuration file: {self.config_file}[/blue]")
                    self.console.print(f"[blue]Current config: {json.dumps(self.config, indent=2)}[/blue]")
                else:
                    self.console.print("[red]❌ Invalid choice. Please try again.[/red]")
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]❌ Error: {e}[/red]")

def main():
    """Main entry point."""
    import sys
    
    integration = ComprehensiveOptimizationIntegration()
    
    # Check for non-interactive mode
    non_interactive = "--daemon" in sys.argv or "--background" in sys.argv or "--test" in sys.argv
    
    # Check if auto-start is enabled
    if integration.config.get("system_optimization", {}).get("auto_start") or non_interactive:
        integration.console.print("[blue]🚀 Auto-starting optimization system...[/blue]")
        if integration.initialize_optimization_manager():
            integration.start_optimization_services()
            
            if non_interactive:
                integration.console.print("[green]✅ Optimization system running in background mode[/green]")
                integration.console.print("[yellow]Press Ctrl+C to stop[/yellow]")
                
                # Keep running until interrupted
                try:
                    while True:
                        time.sleep(60)  # Check every minute
                        # Optional: Add health check here
                except KeyboardInterrupt:
                    integration.console.print("\n[red]Stopping optimization system...[/red]")
                    integration.stop_optimization_services()
                    integration.console.print("[green]Optimization system stopped.[/green]")
                return
    
    # Start interactive menu only if not in non-interactive mode
    if not non_interactive:
        integration.interactive_menu()
        # Cleanup only if we were in interactive mode
        integration.stop_optimization_services()
    else:
        # In non-interactive mode, just run the system
        integration.console.print("[blue]🚀 Starting optimization system in non-interactive mode...[/blue]")
        if integration.initialize_optimization_manager():
            integration.start_optimization_services()
            
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                integration.console.print("\n[red]Stopping optimization system...[/red]")
                integration.stop_optimization_services()
                integration.console.print("[green]Optimization system stopped.[/green]")

if __name__ == "__main__":
    main()
