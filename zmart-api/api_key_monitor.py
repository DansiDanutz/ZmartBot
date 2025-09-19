
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
                "\n".join(alerts),
                title="🚨 API Key Alerts",
                border_style="red"
            )
            self.console.print(alert_panel)
        else:
            self.console.print("✅ All API keys are healthy")

# Global API key monitor instance
api_key_monitor = APIKeyMonitor()
