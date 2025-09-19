
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout

class MDCPerformanceDashboard:
    """Real-time performance dashboard for MDC operations"""
    
    def __init__(self):
        self.console = Console()
        self.metrics_file = Path("mdc_performance_metrics.json")
        self.metrics = self.load_metrics()
    
    def load_metrics(self):
        """Load performance metrics"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {
            "context_optimization": {
                "total_runs": 0,
                "average_time_ms": 0,
                "last_run": None,
                "success_rate": 100
            },
            "mdc_processing": {
                "files_processed": 0,
                "average_processing_time_ms": 0,
                "last_processed": None,
                "error_count": 0
            },
            "supabase_operations": {
                "total_queries": 0,
                "average_query_time_ms": 0,
                "last_query": None,
                "error_rate": 0
            }
        }
    
    def save_metrics(self):
        """Save performance metrics"""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def update_metric(self, category, metric, value):
        """Update a specific metric"""
        if category not in self.metrics:
            self.metrics[category] = {}
        
        self.metrics[category][metric] = value
        self.metrics[category]["last_updated"] = datetime.now().isoformat()
        self.save_metrics()
    
    def create_dashboard(self):
        """Create and display performance dashboard"""
        layout = Layout()
        
        layout.split_column(
            Layout(Panel.fit("[bold blue]MDC Performance Dashboard[/bold blue]", border_style="blue")),
            Layout(name="main"),
            Layout(Panel.fit("[bold green]System Status: OPERATIONAL[/bold green]", border_style="green"))
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Context Optimization Table
        context_table = Table(title="Context Optimization")
        context_table.add_column("Metric", style="cyan")
        context_table.add_column("Value", style="magenta")
        
        context_metrics = self.metrics.get("context_optimization", {})
        context_table.add_row("Total Runs", str(context_metrics.get("total_runs", 0)))
        context_table.add_row("Avg Time (ms)", str(context_metrics.get("average_time_ms", 0)))
        context_table.add_row("Success Rate", f"{context_metrics.get('success_rate', 100)}%")
        context_table.add_row("Last Run", context_metrics.get("last_run", "Never"))
        
        # MDC Processing Table
        mdc_table = Table(title="MDC Processing")
        mdc_table.add_column("Metric", style="cyan")
        mdc_table.add_column("Value", style="magenta")
        
        mdc_metrics = self.metrics.get("mdc_processing", {})
        mdc_table.add_row("Files Processed", str(mdc_metrics.get("files_processed", 0)))
        mdc_table.add_row("Avg Time (ms)", str(mdc_metrics.get("average_processing_time_ms", 0)))
        mdc_table.add_row("Error Count", str(mdc_metrics.get("error_count", 0)))
        mdc_table.add_row("Last Processed", mdc_metrics.get("last_processed", "Never"))
        
        # Supabase Operations Table
        supabase_table = Table(title="Supabase Operations")
        supabase_table.add_column("Metric", style="cyan")
        supabase_table.add_column("Value", style="magenta")
        
        supabase_metrics = self.metrics.get("supabase_operations", {})
        supabase_table.add_row("Total Queries", str(supabase_metrics.get("total_queries", 0)))
        supabase_table.add_row("Avg Time (ms)", str(supabase_metrics.get("average_query_time_ms", 0)))
        supabase_table.add_row("Error Rate", f"{supabase_metrics.get('error_rate', 0)}%")
        supabase_table.add_row("Last Query", supabase_metrics.get("last_query", "Never"))
        
        layout["left"].update(Panel(context_table, title="Context Optimization", border_style="blue"))
        layout["right"].split_column(
            Layout(Panel(mdc_table, title="MDC Processing", border_style="green")),
            Layout(Panel(supabase_table, title="Supabase Operations", border_style="yellow"))
        )
        
        return layout
    
    def run_dashboard(self):
        """Run the performance dashboard"""
        with Live(self.create_dashboard(), refresh_per_second=1) as live:
            try:
                while True:
                    time.sleep(1)
                    live.update(self.create_dashboard())
            except KeyboardInterrupt:
                self.console.print("\n[bold red]Dashboard stopped[/bold red]")

# Global dashboard instance
dashboard = MDCPerformanceDashboard()
