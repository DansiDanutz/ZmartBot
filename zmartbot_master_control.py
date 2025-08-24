#!/usr/bin/env python3
"""
ZmartBot Master Control System
Central control panel for all ZmartBot components
"""

import os
import sys
import subprocess
import time
import json
import signal
import threading
from datetime import datetime
from pathlib import Path

class ZmartBotMaster:
    """Master control system for ZmartBot"""
    
    def __init__(self):
        self.processes = {}
        self.running = True
        self.base_dir = Path("/Users/dansidanutz/Desktop/ZmartBot")
        self.backend_dir = self.base_dir / "backend" / "zmart-api"
        
    def display_banner(self):
        """Display ZmartBot banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗            ║
║     ╚══███╔╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝            ║
║       ███╔╝ ██╔████╔██║███████║██████╔╝   ██║               ║
║      ███╔╝  ██║╚██╔╝██║██╔══██║██╔══██╗   ██║               ║
║     ███████╗██║ ╚═╝ ██║██║  ██║██║  ██║   ██║               ║
║     ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝               ║
║                                                              ║
║           🤖 CRYPTOCURRENCY TRADING PLATFORM 🤖              ║
║                    Master Control System                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_server_status(self):
        """Check if the backend server is running"""
        try:
            import requests
            resp = requests.get("http://localhost:8000/health", timeout=2)
            return resp.status_code == 200
        except:
            return False
    
    def start_backend_server(self):
        """Start the backend FastAPI server"""
        if self.check_server_status():
            print("✅ Backend server is already running")
            return True
        
        print("🚀 Starting backend server...")
        os.chdir(self.backend_dir)
        
        # Activate virtual environment and start server
        cmd = f"source venv/bin/activate && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000"
        process = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
        self.processes['backend'] = process
        
        # Wait for server to start
        for _ in range(10):
            time.sleep(2)
            if self.check_server_status():
                print("✅ Backend server started successfully")
                return True
        
        print("❌ Failed to start backend server")
        return False
    
    def display_menu(self):
        """Display control menu"""
        print("\n" + "=" * 60)
        print("📋 ZMARTBOT CONTROL PANEL")
        print("=" * 60)
        print("1. 📊 View System Status")
        print("2. 🖥️  Start Monitoring Dashboard")
        print("3. 🤖 Start Trading Strategy (Paper)")
        print("4. 📈 Generate Portfolio Report")
        print("5. 🚨 Start Alert System")
        print("6. 🔍 Test Trading Signals")
        print("7. 📊 View Performance Metrics")
        print("8. ⚙️  System Configuration")
        print("9. 🛑 Stop All Services")
        print("0. 🚪 Exit")
        print("=" * 60)
    
    def view_system_status(self):
        """View current system status"""
        print("\n📊 SYSTEM STATUS")
        print("-" * 40)
        
        # Check backend server
        if self.check_server_status():
            print("✅ Backend Server: RUNNING")
            
            # Get server info
            try:
                import requests
                resp = requests.get("http://localhost:8000/health")
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"   • Uptime: {data.get('uptime', 'N/A')}")
                    print(f"   • Version: {data.get('version', 'N/A')}")
            except:
                pass
        else:
            print("❌ Backend Server: STOPPED")
        
        # Check processes
        for name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"✅ {name.title()}: RUNNING (PID: {process.pid})")
            else:
                print(f"❌ {name.title()}: STOPPED")
        
        # Check databases
        db_files = [
            "portfolio_analytics.db",
            "alerts.db",
            "trading_strategy_state.json"
        ]
        
        print("\n📁 Database Files:")
        for db_file in db_files:
            path = self.base_dir / db_file
            if path.exists():
                size = path.stat().st_size / 1024  # KB
                print(f"   • {db_file}: {size:.1f} KB")
            else:
                print(f"   • {db_file}: Not found")
    
    def start_monitoring_dashboard(self):
        """Start the monitoring dashboard"""
        print("\n🖥️  Starting Monitoring Dashboard...")
        cmd = f"cd {self.base_dir} && python monitor_dashboard.py"
        process = subprocess.Popen(cmd, shell=True)
        self.processes['dashboard'] = process
        print("✅ Dashboard started in new process")
    
    def start_trading_strategy(self):
        """Start the trading strategy"""
        print("\n🤖 Starting Trading Strategy (Paper Mode)...")
        cmd = f"cd {self.base_dir} && python trading_strategy_config.py"
        process = subprocess.Popen(cmd, shell=True)
        self.processes['trading'] = process
        print("✅ Trading strategy started in new process")
    
    def generate_portfolio_report(self):
        """Generate portfolio report"""
        print("\n📈 Generating Portfolio Report...")
        os.chdir(self.base_dir)
        subprocess.run(["python", "portfolio_analytics.py"])
        
        # Display the report
        report_file = self.base_dir / "portfolio_report.txt"
        if report_file.exists():
            with open(report_file, 'r') as f:
                print(f.read())
    
    def start_alert_system(self):
        """Start the alert system"""
        print("\n🚨 Starting Alert System...")
        cmd = f"cd {self.base_dir} && python alert_system.py"
        process = subprocess.Popen(cmd, shell=True)
        self.processes['alerts'] = process
        print("✅ Alert system started in new process")
    
    def test_signals(self):
        """Test trading signals"""
        print("\n🔍 Testing Trading Signals...")
        os.chdir(self.base_dir)
        subprocess.run(["python", "test_signals.py"])
    
    def view_performance_metrics(self):
        """View performance metrics"""
        print("\n📊 PERFORMANCE METRICS")
        print("-" * 40)
        
        # Load trading state if exists
        state_file = self.base_dir / "trading_strategy_state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
                
            perf = state.get('performance', {})
            print(f"Total Trades: {perf.get('total_trades', 0)}")
            print(f"Open Positions: {perf.get('open_positions', 0)}")
            print(f"Win Rate: {perf.get('win_rate', 0):.1f}%")
            print(f"Total P&L: ${perf.get('total_pnl_usd', 0):.2f}")
            print(f"Current Exposure: ${perf.get('current_exposure', 0):.2f}")
            
            if 'last_update' in state:
                print(f"\nLast Update: {state['last_update']}")
        else:
            print("No performance data available yet")
    
    def system_configuration(self):
        """System configuration menu"""
        print("\n⚙️  SYSTEM CONFIGURATION")
        print("-" * 40)
        print("1. View API Keys Status")
        print("2. Configure Trading Parameters")
        print("3. Set Alert Thresholds")
        print("4. Database Management")
        print("5. Back to Main Menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            self.view_api_keys_status()
        elif choice == '2':
            print("📝 Edit trading_strategy_config.py to modify parameters")
        elif choice == '3':
            print("📝 Edit alert_system.py to modify thresholds")
        elif choice == '4':
            self.database_management()
    
    def view_api_keys_status(self):
        """Check API keys configuration"""
        env_file = self.backend_dir / ".env"
        if env_file.exists():
            print("\n🔑 API Keys Status:")
            with open(env_file, 'r') as f:
                for line in f:
                    if 'API_KEY' in line or 'SECRET' in line:
                        key_name = line.split('=')[0]
                        has_value = len(line.split('=')[1].strip()) > 0
                        status = "✅ Configured" if has_value else "❌ Missing"
                        print(f"  • {key_name}: {status}")
        else:
            print("❌ .env file not found")
    
    def database_management(self):
        """Database management options"""
        print("\n💾 DATABASE MANAGEMENT")
        print("-" * 40)
        print("1. Clear Portfolio History")
        print("2. Clear Alert History")
        print("3. Backup Databases")
        print("4. Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            if input("Clear portfolio history? (y/n): ").lower() == 'y':
                (self.base_dir / "portfolio_analytics.db").unlink(missing_ok=True)
                print("✅ Portfolio history cleared")
        elif choice == '2':
            if input("Clear alert history? (y/n): ").lower() == 'y':
                (self.base_dir / "alerts.db").unlink(missing_ok=True)
                print("✅ Alert history cleared")
        elif choice == '3':
            self.backup_databases()
    
    def backup_databases(self):
        """Backup all databases"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.base_dir / f"backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        files_to_backup = [
            "portfolio_analytics.db",
            "alerts.db",
            "trading_strategy_state.json",
            "signal_test_results.json"
        ]
        
        for file_name in files_to_backup:
            src = self.base_dir / file_name
            if src.exists():
                dst = backup_dir / file_name
                import shutil
                shutil.copy2(src, dst)
                print(f"✅ Backed up {file_name}")
        
        print(f"\n✅ Backup completed to {backup_dir}")
    
    def stop_all_services(self):
        """Stop all running services"""
        print("\n🛑 Stopping all services...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                process.terminate()
                print(f"  • Stopped {name}")
        
        # Kill any remaining uvicorn processes
        subprocess.run(["pkill", "-f", "uvicorn"], capture_output=True)
        
        print("✅ All services stopped")
    
    def run(self):
        """Main control loop"""
        self.display_banner()
        
        # Ensure backend server is running
        if not self.check_server_status():
            print("\n⚠️  Backend server is not running")
            if input("Start backend server? (y/n): ").lower() == 'y':
                self.start_backend_server()
        
        while self.running:
            self.display_menu()
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.view_system_status()
            elif choice == '2':
                self.start_monitoring_dashboard()
            elif choice == '3':
                self.start_trading_strategy()
            elif choice == '4':
                self.generate_portfolio_report()
            elif choice == '5':
                self.start_alert_system()
            elif choice == '6':
                self.test_signals()
            elif choice == '7':
                self.view_performance_metrics()
            elif choice == '8':
                self.system_configuration()
            elif choice == '9':
                self.stop_all_services()
            elif choice == '0':
                print("\n👋 Exiting ZmartBot Master Control")
                self.stop_all_services()
                self.running = False
            else:
                print("❌ Invalid option")
            
            if self.running and choice != '0':
                input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    master = ZmartBotMaster()
    
    try:
        master.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        master.stop_all_services()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        master.stop_all_services()

if __name__ == "__main__":
    main()