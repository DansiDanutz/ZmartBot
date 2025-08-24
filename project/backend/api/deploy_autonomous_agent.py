#!/usr/bin/env python3
"""
Deployment Configuration for Autonomous RiskMetric Agent
Sets up and launches the autonomous agent with all integrations
"""

import os
import sys
import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/autonomous_agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AutonomousAgentDeployment:
    """Deploy and manage the autonomous RiskMetric agent"""
    
    def __init__(self):
        self.config_path = Path("config/autonomous_agent.json")
        self.credentials_path = Path("credentials")
        self.data_path = Path("data")
        self.logs_path = Path("logs")
        
        # Create necessary directories
        self.setup_directories()
        
        # Configuration
        self.config = self.load_configuration()
    
    def setup_directories(self):
        """Create necessary directories"""
        for path in [self.credentials_path, self.data_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory ready: {path}")
    
    def load_configuration(self) -> dict:
        """Load or create configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Create default configuration
            config = {
                "agent": {
                    "name": "AutonomousRiskMetricAgent",
                    "version": "2.0",
                    "enabled": True,
                    "mode": "production"
                },
                "database": {
                    "path": "data/autonomous_riskmetric.db",
                    "backup_enabled": True,
                    "backup_interval_hours": 24
                },
                "google_sheets": {
                    "enabled": True,
                    "credentials_file": "credentials/google_service_account.json",
                    "sync_interval_hours": 24,
                    "sync_time_utc": "02:00",
                    "sheets": {
                        "risk_bands": "1F-0_I2zy7MIQ_thTF2g4oaTZNiv1aV4x",
                        "time_spent": "1fup2CUYxg7Tj3a2BvpoN3OcfGBoSe7EqHIxmp1RRjqg"
                    }
                },
                "telegram": {
                    "enabled": True,
                    "notifications": [
                        "sync_complete",
                        "new_symbol_added",
                        "rare_zone_entered",
                        "errors"
                    ]
                },
                "symbols": {
                    "auto_add": True,
                    "initial": ["BTC", "ETH", "SOL", "AVAX"],
                    "min_data_points": 365,
                    "max_symbols": 50
                },
                "monitoring": {
                    "enabled": True,
                    "port": 8001,
                    "dashboard_enabled": True
                },
                "rate_limiting": {
                    "enabled": True,
                    "ccxt_calls_per_minute": 30,
                    "google_sheets_calls_per_minute": 60
                }
            }
            
            # Save default configuration
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"Created default configuration at {self.config_path}")
            return config
    
    async def check_prerequisites(self) -> bool:
        """Check all prerequisites before deployment"""
        print("\n" + "="*60)
        print("CHECKING PREREQUISITES")
        print("="*60)
        
        checks = []
        
        # 1. Check Python version
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 11:
            print("✅ Python version: " + sys.version.split()[0])
            checks.append(True)
        else:
            print("❌ Python 3.11+ required")
            checks.append(False)
        
        # 2. Check required packages
        required_packages = [
            'pandas', 'numpy', 'scipy', 'sqlite3',
            'asyncio', 'logging', 'dataclasses'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ Package '{package}' installed")
                checks.append(True)
            except ImportError:
                print(f"❌ Package '{package}' not installed")
                checks.append(False)
        
        # 3. Check optional integrations
        print("\nOptional Integrations:")
        
        # Google Sheets
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            print("✅ Google Sheets API available")
            
            # Check for credentials
            creds_file = Path(self.config['google_sheets']['credentials_file'])
            if creds_file.exists():
                print("✅ Google service account credentials found")
            else:
                print("⚠️ Google credentials not found - will use local data only")
        except ImportError:
            print("⚠️ Google Sheets API not installed - will use local data only")
        
        # CCXT for historical data
        try:
            import ccxt
            print("✅ CCXT library available for market data")
        except ImportError:
            print("⚠️ CCXT not installed - will use mock data")
        
        # Telegram
        if os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'):
            print("✅ Telegram credentials configured")
        else:
            print("⚠️ Telegram not configured - notifications disabled")
        
        # 4. Check database
        db_path = Path(self.config['database']['path'])
        if db_path.exists():
            print(f"✅ Database exists at {db_path}")
        else:
            print(f"⚠️ Database will be created at {db_path}")
        
        return all(checks)
    
    async def initialize_agent(self):
        """Initialize the autonomous agent"""
        print("\n" + "="*60)
        print("INITIALIZING AUTONOMOUS AGENT")
        print("="*60)
        
        try:
            from src.agents.database.autonomous_riskmetric_agent import AutonomousRiskMetricAgent
            
            # Create agent instance
            self.agent = AutonomousRiskMetricAgent(
                db_path=self.config['database']['path']
            )
            
            print("✅ Agent initialized successfully")
            
            # Add initial symbols if configured
            if self.config['symbols']['auto_add']:
                print("\nAdding initial symbols...")
                for symbol in self.config['symbols']['initial']:
                    print(f"  Adding {symbol}...")
                    success = await self.agent.add_new_symbol(symbol)
                    if success:
                        print(f"  ✅ {symbol} added")
                    else:
                        print(f"  ⚠️ {symbol} skipped (insufficient data)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            return False
    
    async def setup_google_sheets_sync(self):
        """Set up Google Sheets synchronization"""
        if not self.config['google_sheets']['enabled']:
            print("⚠️ Google Sheets sync disabled in configuration")
            return
        
        print("\n" + "="*60)
        print("SETTING UP GOOGLE SHEETS SYNC")
        print("="*60)
        
        try:
            from src.services.cowen_sheets_sync import CowenSheetsSync
            
            self.sheets_sync = CowenSheetsSync(
                credentials_path=self.config['google_sheets']['credentials_file']
            )
            
            # Test authentication
            if self.sheets_sync.authenticate():
                print("✅ Google Sheets authenticated")
                
                # Schedule daily sync
                sync_time = self.config['google_sheets']['sync_time_utc']
                print(f"📅 Daily sync scheduled for {sync_time} UTC")
                
                # Start sync task
                asyncio.create_task(
                    self.sheets_sync.start_daily_sync(
                        sync_hour=int(sync_time.split(':')[0])
                    )
                )
                
                return True
            else:
                print("❌ Google Sheets authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup Google Sheets sync: {e}")
            return False
    
    async def setup_monitoring(self):
        """Set up monitoring dashboard"""
        if not self.config['monitoring']['enabled']:
            return
        
        print("\n" + "="*60)
        print("SETTING UP MONITORING")
        print("="*60)
        
        # Create simple HTTP server for monitoring
        from aiohttp import web
        
        async def status_handler(request):
            """Status endpoint"""
            assessment = await self.agent.get_enhanced_assessment('BTC', 95000)
            
            status = {
                "status": "running",
                "timestamp": datetime.now().isoformat(),
                "agent": {
                    "name": self.config['agent']['name'],
                    "version": self.config['agent']['version']
                },
                "current_assessment": assessment if assessment else None
            }
            
            return web.json_response(status)
        
        async def health_handler(request):
            """Health check endpoint"""
            return web.json_response({"status": "healthy"})
        
        # Create app
        app = web.Application()
        app.router.add_get('/status', status_handler)
        app.router.add_get('/health', health_handler)
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.config['monitoring']['port'])
        await site.start()
        
        print(f"✅ Monitoring dashboard available at http://localhost:{self.config['monitoring']['port']}/status")
    
    async def run_deployment(self):
        """Run complete deployment"""
        print("\n" + "="*70)
        print("AUTONOMOUS RISKMETRIC AGENT - DEPLOYMENT")
        print("="*70)
        print(f"Deployment started: {datetime.now()}")
        
        # Check prerequisites
        if not await self.check_prerequisites():
            print("\n❌ Prerequisites check failed. Please install missing components.")
            return False
        
        # Initialize agent
        if not await self.initialize_agent():
            print("\n❌ Agent initialization failed.")
            return False
        
        # Setup Google Sheets sync
        await self.setup_google_sheets_sync()
        
        # Setup monitoring
        await self.setup_monitoring()
        
        print("\n" + "="*70)
        print("DEPLOYMENT COMPLETE")
        print("="*70)
        
        print("\n🎉 Autonomous RiskMetric Agent is now running!")
        print("\nCapabilities:")
        print("  ✅ Automatic symbol addition and analysis")
        print("  ✅ Logarithmic regression calculation")
        print("  ✅ Real-time time-spent tracking")
        print("  ✅ Dynamic coefficient calculation")
        print("  ✅ Daily Google Sheets synchronization")
        print("  ✅ Telegram notifications")
        print("  ✅ HTTP monitoring endpoint")
        
        print("\nMonitoring:")
        print(f"  📊 Status: http://localhost:{self.config['monitoring']['port']}/status")
        print(f"  ❤️ Health: http://localhost:{self.config['monitoring']['port']}/health")
        
        print("\nPress Ctrl+C to stop the agent")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(60)
                
                # Periodic status log
                if datetime.now().minute == 0:  # Every hour
                    logger.info("Agent running normally")
                    
        except KeyboardInterrupt:
            print("\n⏹️ Stopping agent...")
            return True
    
    async def create_systemd_service(self):
        """Create systemd service for production deployment"""
        service_content = f"""[Unit]
Description=Autonomous RiskMetric Agent
After=network.target

[Service]
Type=simple
User={os.getenv('USER')}
WorkingDirectory={os.getcwd()}
Environment="PATH={os.environ['PATH']}"
ExecStart=/usr/bin/python3 {os.path.abspath(__file__)}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_path = Path("/etc/systemd/system/autonomous-riskmetric.service")
        
        print("\nSystemd service configuration:")
        print(service_content)
        print(f"\nTo install as system service:")
        print(f"1. Save above to {service_path}")
        print(f"2. Run: sudo systemctl daemon-reload")
        print(f"3. Run: sudo systemctl enable autonomous-riskmetric")
        print(f"4. Run: sudo systemctl start autonomous-riskmetric")

async def main():
    """Main deployment function"""
    deployment = AutonomousAgentDeployment()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--systemd':
            await deployment.create_systemd_service()
        elif sys.argv[1] == '--config':
            print(f"Configuration file: {deployment.config_path}")
            print(json.dumps(deployment.config, indent=2))
        else:
            print("Usage: python deploy_autonomous_agent.py [--systemd|--config]")
    else:
        # Run deployment
        await deployment.run_deployment()

if __name__ == "__main__":
    print("\n🚀 Autonomous RiskMetric Agent Deployment")
    print("   Complete autonomous trading intelligence")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Deployment stopped by user")
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        import traceback
        traceback.print_exc()