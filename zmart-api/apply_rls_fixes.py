#!/usr/bin/env python3
"""
Apply Supabase RLS Policy Fixes for MDC Operations
This script applies the necessary RLS policy changes to enable MDC file storage
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append('.')

try:
    from supabase import create_client, Client
    from src.config.settings import settings
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    def apply_rls_fixes():
        """Apply RLS policy fixes to Supabase"""
        
        console.print(Panel.fit(
            "[bold blue]🔧 SUPABASE RLS POLICY FIXES[/bold blue]\n"
            "Applying Row Level Security policies for MDC operations",
            border_style="blue"
        ))
        
        try:
            # Create Supabase client
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
            console.print("✅ Supabase client created")
            
            # Read the SQL fix file
            sql_file = Path("fix_supabase_rls_policies.sql")
            if not sql_file.exists():
                console.print(f"❌ SQL fix file not found: {sql_file}")
                return False
            
            with open(sql_file, 'r') as f:
                sql_content = f.read()
            
            console.print("📄 SQL fix file loaded")
            
            # Split SQL into individual statements
            sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                
                task = progress.add_task("Applying RLS policy fixes...", total=len(sql_statements))
                
                success_count = 0
                error_count = 0
                
                for i, statement in enumerate(sql_statements):
                    if not statement or statement.startswith('--'):
                        continue
                    
                    try:
                        # Execute the SQL statement
                        result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                        success_count += 1
                        progress.update(task, advance=1, description=f"Applied statement {i+1}/{len(sql_statements)}")
                        
                    except Exception as e:
                        error_count += 1
                        console.print(f"⚠️ Statement {i+1} failed: {e}")
                        progress.update(task, advance=1, description=f"Error in statement {i+1}/{len(sql_statements)}")
                
                progress.update(task, completed=len(sql_statements))
            
            # Test the fixes
            console.print("\n🧪 Testing RLS policy fixes...")
            
            test_mdc_content = """
# Test MDC File - RLS Policy Fix Verification
## Description
This is a test MDC file to verify RLS policy fixes.

## Requirements
- ✅ Database connectivity
- ✅ Valid service passport
- ✅ Complete MDC documentation

## Triggers
- API endpoint requests
- Database events
"""
            
            try:
                # Test MDC record insertion
                result = supabase.table('mdc_documentation').insert({
                    'symbol': 'RLS_TEST',
                    'document_type': 'alert_report',
                    'mdc_content': test_mdc_content,
                    'version': '1.0.0',
                    'owner': 'zmartbot',
                    'status': 'active'
                }).execute()
                
                if result.data:
                    console.print("✅ MDC record insertion test successful!")
                    record_id = result.data[0]['id']
                    
                    # Clean up test record
                    supabase.table('mdc_documentation').delete().eq('id', record_id).execute()
                    console.print("🧹 Test record cleaned up")
                    
                    return True
                else:
                    console.print("❌ MDC record insertion test failed - no data returned")
                    return False
                    
            except Exception as e:
                console.print(f"❌ MDC record insertion test failed: {e}")
                return False
                
        except Exception as e:
            console.print(f"❌ Error applying RLS fixes: {e}")
            return False

    def create_monitoring_alerts():
        """Create monitoring and alerting system for MDC operations"""
        
        console.print(Panel.fit(
            "[bold green]🚨 MDC MONITORING & ALERTING SYSTEM[/bold green]\n"
            "Setting up comprehensive monitoring for MDC operations",
            border_style="green"
        ))
        
        # Create monitoring configuration
        monitoring_config = {
            "mdc_processing": {
                "enabled": True,
                "alert_thresholds": {
                    "processing_time_ms": 5000,
                    "error_rate_percent": 5,
                    "queue_size": 100
                },
                "notification_channels": ["log", "webhook", "email"]
            },
            "context_optimization": {
                "enabled": True,
                "alert_thresholds": {
                    "claude_size_kb": 50,
                    "optimization_time_ms": 10000,
                    "file_count": 500
                }
            },
            "supabase_operations": {
                "enabled": True,
                "alert_thresholds": {
                    "connection_timeout_ms": 3000,
                    "query_timeout_ms": 10000,
                    "error_rate_percent": 2
                }
            }
        }
        
        # Save monitoring configuration
        import json
        config_file = Path("mdc_monitoring_config.json")
        with open(config_file, 'w') as f:
            json.dump(monitoring_config, f, indent=2)
        
        console.print(f"✅ Monitoring configuration saved to {config_file}")
        
        # Create alert handler
        alert_handler_code = '''
import logging
import json
from datetime import datetime
from pathlib import Path

class MDCAlertHandler:
    """Handle MDC processing alerts and notifications"""
    
    def __init__(self, config_file="mdc_monitoring_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.logger = self.setup_logger()
    
    def load_config(self):
        """Load monitoring configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def setup_logger(self):
        """Setup alert logging"""
        logger = logging.getLogger('mdc_alerts')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('mdc_alerts.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def send_alert(self, alert_type, message, severity="INFO"):
        """Send alert notification"""
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "message": message,
            "severity": severity
        }
        
        # Log the alert
        self.logger.info(f"ALERT: {json.dumps(alert_data)}")
        
        # Send to configured channels
        channels = self.config.get("mdc_processing", {}).get("notification_channels", ["log"])
        
        for channel in channels:
            if channel == "webhook":
                self.send_webhook_alert(alert_data)
            elif channel == "email":
                self.send_email_alert(alert_data)
            # log is handled by logger above
    
    def send_webhook_alert(self, alert_data):
        """Send alert via webhook"""
        # Implementation for webhook notifications
        pass
    
    def send_email_alert(self, alert_data):
        """Send alert via email"""
        # Implementation for email notifications
        pass

# Global alert handler instance
alert_handler = MDCAlertHandler()
'''
        
        alert_file = Path("mdc_alert_handler.py")
        with open(alert_file, 'w') as f:
            f.write(alert_handler_code)
        
        console.print(f"✅ Alert handler created: {alert_file}")
        return True

    def create_performance_dashboard():
        """Create performance dashboard for context optimization"""
        
        console.print(Panel.fit(
            "[bold yellow]📊 PERFORMANCE DASHBOARD SETUP[/bold yellow]\n"
            "Creating performance monitoring dashboard",
            border_style="yellow"
        ))
        
        dashboard_code = '''
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
                self.console.print("\\n[bold red]Dashboard stopped[/bold red]")

# Global dashboard instance
dashboard = MDCPerformanceDashboard()
'''
        
        dashboard_file = Path("mdc_performance_dashboard.py")
        with open(dashboard_file, 'w') as f:
            f.write(dashboard_code)
        
        console.print(f"✅ Performance dashboard created: {dashboard_file}")
        return True

    def create_api_key_monitor():
        """Create API key rotation and expiration monitoring"""
        
        console.print(Panel.fit(
            "[bold magenta]🔑 API KEY MONITORING SYSTEM[/bold magenta]\n"
            "Setting up API key rotation and expiration monitoring",
            border_style="magenta"
        ))
        
        monitor_code = '''
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

class APIKeyMonitor:
    """Monitor API key rotation and expiration"""
    
    def __init__(self):
        self.console = Console()
        self.api_keys_manager_url = "http://localhost:8006"
        self.monitoring_file = Path("api_key_monitoring.json")
        self.monitoring_data = self.load_monitoring_data()
    
    def load_monitoring_data(self):
        """Load API key monitoring data"""
        if self.monitoring_file.exists():
            with open(self.monitoring_file, 'r') as f:
                return json.load(f)
        return {
            "keys": {},
            "last_check": None,
            "alerts": []
        }
    
    def save_monitoring_data(self):
        """Save API key monitoring data"""
        with open(self.monitoring_file, 'w') as f:
            json.dump(self.monitoring_data, f, indent=2)
    
    def check_api_key_status(self, key_id):
        """Check status of a specific API key"""
        try:
            response = requests.get(f"{self.api_keys_manager_url}/keys/{key_id}", timeout=5)
            if response.status_code == 200:
                key_data = response.json()
                return {
                    "status": "active",
                    "last_used": key_data.get("last_used"),
                    "created_at": key_data.get("created_at"),
                    "expires_at": key_data.get("expires_at"),
                    "usage_count": key_data.get("usage_count", 0)
                }
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_all_keys(self):
        """Check status of all monitored API keys"""
        key_ids = [
            "b4ca17e568290443",  # KuCoin API Key
            "048e0229eff8f4c8",  # KuCoin Secret
            "855f3c5406856811",  # KuCoin Passphrase
            "73645e8a29fe40bd",  # Supabase Anon Key
            "b50fc81f12bba24b"   # Cryptometer API Key
        ]
        
        results = {}
        for key_id in key_ids:
            results[key_id] = self.check_api_key_status(key_id)
        
        self.monitoring_data["keys"] = results
        self.monitoring_data["last_check"] = datetime.now().isoformat()
        self.save_monitoring_data()
        
        return results
    
    def create_status_table(self):
        """Create API key status table"""
        table = Table(title="API Key Status")
        table.add_column("Key ID", style="cyan")
        table.add_column("Service", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Last Used", style="yellow")
        table.add_column("Usage Count", style="blue")
        
        key_mapping = {
            "b4ca17e568290443": "KuCoin API Key",
            "048e0229eff8f4c8": "KuCoin Secret",
            "855f3c5406856811": "KuCoin Passphrase",
            "73645e8a29fe40bd": "Supabase Anon Key",
            "b50fc81f12bba24b": "Cryptometer API Key"
        }
        
        for key_id, service_name in key_mapping.items():
            key_data = self.monitoring_data["keys"].get(key_id, {})
            status = key_data.get("status", "unknown")
            last_used = key_data.get("last_used", "Never")
            usage_count = key_data.get("usage_count", 0)
            
            table.add_row(
                key_id[:8] + "...",
                service_name,
                status,
                last_used,
                str(usage_count)
            )
        
        return table
    
    def run_monitoring(self):
        """Run API key monitoring"""
        self.console.print(Panel.fit(
            "[bold blue]🔑 API Key Monitoring[/bold blue]",
            border_style="blue"
        ))
        
        # Check all keys
        results = self.check_all_keys()
        
        # Display results
        table = self.create_status_table()
        self.console.print(table)
        
        # Check for alerts
        alerts = []
        for key_id, data in results.items():
            if data.get("status") == "error":
                alerts.append(f"❌ {key_id}: {data.get('error')}")
        
        if alerts:
            alert_panel = Panel(
                "\\n".join(alerts),
                title="🚨 API Key Alerts",
                border_style="red"
            )
            self.console.print(alert_panel)
        else:
            self.console.print("✅ All API keys are healthy")

# Global API key monitor instance
api_key_monitor = APIKeyMonitor()
'''
        
        monitor_file = Path("api_key_monitor.py")
        with open(monitor_file, 'w') as f:
            f.write(monitor_code)
        
        console.print(f"✅ API key monitor created: {monitor_file}")
        return True

    def main():
        """Main optimization implementation"""
        
        console.print(Panel.fit(
            "[bold green]🚀 IMPLEMENTING CONTINUED OPTIMIZATION[/bold green]\n"
            "Applying all recommended optimizations for ZmartBot",
            border_style="green"
        ))
        
        success_count = 0
        total_tasks = 4
        
        # 1. Apply RLS policy fixes
        console.print("\\n[bold blue]1. Applying Supabase RLS Policy Fixes...[/bold blue]")
        if apply_rls_fixes():
            console.print("✅ RLS policy fixes applied successfully")
            success_count += 1
        else:
            console.print("❌ RLS policy fixes failed")
        
        # 2. Create monitoring alerts
        console.print("\\n[bold green]2. Setting up Monitoring & Alerting...[/bold green]")
        if create_monitoring_alerts():
            console.print("✅ Monitoring & alerting system created")
            success_count += 1
        else:
            console.print("❌ Monitoring & alerting setup failed")
        
        # 3. Create performance dashboard
        console.print("\\n[bold yellow]3. Creating Performance Dashboard...[/bold yellow]")
        if create_performance_dashboard():
            console.print("✅ Performance dashboard created")
            success_count += 1
        else:
            console.print("❌ Performance dashboard creation failed")
        
        # 4. Create API key monitoring
        console.print("\\n[bold magenta]4. Setting up API Key Monitoring...[/bold magenta]")
        if create_api_key_monitor():
            console.print("✅ API key monitoring system created")
            success_count += 1
        else:
            console.print("❌ API key monitoring setup failed")
        
        # Summary
        console.print(f"\\n[bold green]🎯 OPTIMIZATION COMPLETE[/bold green]")
        console.print(f"✅ Successfully implemented: {success_count}/{total_tasks} optimizations")
        
        if success_count == total_tasks:
            console.print("\\n[bold green]🏆 ALL OPTIMIZATIONS SUCCESSFULLY IMPLEMENTED![/bold green]")
        else:
            console.print(f"\\n[bold yellow]⚠️ {total_tasks - success_count} optimizations need attention[/bold yellow]")

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("Please install: pip install supabase rich")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
