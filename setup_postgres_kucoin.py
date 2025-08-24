#!/usr/bin/env python3
"""
PostgreSQL Setup and KuCoin Configuration for ZmartBot
Sets up production database and configures KuCoin as default exchange
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'zmartbot_production',
    'user': 'zmartbot',
    'password': 'ZmartBot2025!Secure'
}

# KuCoin configuration
KUCOIN_CONFIG = {
    'exchange': 'kucoin',
    'default': True,
    'futures': True,
    'spot': False,
    'testnet': False,
    'base_url': 'https://api-futures.kucoin.com',
    'ws_url': 'wss://ws-api.kucoin.com'
}

def check_postgres():
    """Check if PostgreSQL is accessible"""
    try:
        # Use full path for PostgreSQL 15
        result = subprocess.run(['/opt/homebrew/opt/postgresql@15/bin/pg_isready'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ PostgreSQL is running")
            return True
        else:
            logger.error("❌ PostgreSQL is not running")
            return False
    except Exception as e:
        logger.error(f"❌ Error checking PostgreSQL: {e}")
        return False

def create_database():
    """Create the database and user"""
    try:
        # Connect to PostgreSQL as current user
        conn = psycopg2.connect(
            host='localhost',
            database='postgres',
            user=os.environ.get('USER')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create user if not exists
        cursor.execute("SELECT 1 FROM pg_user WHERE usename = %s", (DB_CONFIG['user'],))
        if not cursor.fetchone():
            cursor.execute(f"""
                CREATE USER {DB_CONFIG['user']} 
                WITH PASSWORD '{DB_CONFIG['password']}'
                CREATEDB
            """)
            logger.info(f"✅ Created user: {DB_CONFIG['user']}")
        else:
            cursor.execute(f"""
                ALTER USER {DB_CONFIG['user']} 
                WITH PASSWORD '{DB_CONFIG['password']}'
            """)
            logger.info(f"✅ Updated user: {DB_CONFIG['user']}")
        
        # Create database if not exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['database'],))
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']} OWNER {DB_CONFIG['user']}")
            logger.info(f"✅ Created database: {DB_CONFIG['database']}")
        else:
            logger.info(f"✅ Database exists: {DB_CONFIG['database']}")
        
        # Grant privileges
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_CONFIG['database']} TO {DB_CONFIG['user']}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating database: {e}")
        return False

def create_tables():
    """Create all required tables with KuCoin support"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Exchange configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exchange_config (
                id SERIAL PRIMARY KEY,
                exchange_name VARCHAR(50) UNIQUE NOT NULL,
                is_default BOOLEAN DEFAULT FALSE,
                api_key TEXT,
                api_secret TEXT,
                passphrase TEXT,
                testnet BOOLEAN DEFAULT FALSE,
                futures_enabled BOOLEAN DEFAULT TRUE,
                spot_enabled BOOLEAN DEFAULT FALSE,
                base_url TEXT,
                ws_url TEXT,
                config JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # KuCoin-specific positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kucoin_positions (
                id SERIAL PRIMARY KEY,
                position_id VARCHAR(100) UNIQUE,
                symbol VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                size DECIMAL(20, 8) NOT NULL,
                entry_price DECIMAL(20, 8) NOT NULL,
                mark_price DECIMAL(20, 8),
                liquidation_price DECIMAL(20, 8),
                leverage INTEGER DEFAULT 1,
                margin DECIMAL(20, 8),
                unrealized_pnl DECIMAL(20, 8),
                realized_pnl DECIMAL(20, 8),
                stop_loss DECIMAL(20, 8),
                take_profit DECIMAL(20, 8),
                status VARCHAR(20) DEFAULT 'OPEN',
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                metadata JSONB
            )
        """)
        
        # KuCoin orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kucoin_orders (
                id SERIAL PRIMARY KEY,
                order_id VARCHAR(100) UNIQUE NOT NULL,
                client_order_id VARCHAR(100),
                symbol VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                type VARCHAR(20) NOT NULL,
                size DECIMAL(20, 8) NOT NULL,
                price DECIMAL(20, 8),
                stop_price DECIMAL(20, 8),
                leverage INTEGER DEFAULT 1,
                status VARCHAR(20),
                filled_size DECIMAL(20, 8) DEFAULT 0,
                filled_value DECIMAL(20, 8) DEFAULT 0,
                fee DECIMAL(20, 8) DEFAULT 0,
                time_in_force VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB
            )
        """)
        
        # Trading signals table (enhanced)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_signals (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                exchange VARCHAR(20) DEFAULT 'kucoin',
                signal_type VARCHAR(20) NOT NULL,
                action VARCHAR(10) NOT NULL,
                strength DECIMAL(5, 2),
                price DECIMAL(20, 8),
                quantity DECIMAL(20, 8),
                source VARCHAR(50),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed BOOLEAN DEFAULT FALSE,
                executed_at TIMESTAMP,
                order_id VARCHAR(100)
            )
        """)
        
        # Market data table (KuCoin-specific)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kucoin_market_data (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                open DECIMAL(20, 8),
                high DECIMAL(20, 8),
                low DECIMAL(20, 8),
                close DECIMAL(20, 8) NOT NULL,
                volume DECIMAL(20, 8),
                quote_volume DECIMAL(20, 8),
                funding_rate DECIMAL(10, 8),
                mark_price DECIMAL(20, 8),
                index_price DECIMAL(20, 8),
                open_interest DECIMAL(20, 8),
                UNIQUE(symbol, timestamp)
            )
        """)
        
        # Account balance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_balance (
                id SERIAL PRIMARY KEY,
                exchange VARCHAR(20) DEFAULT 'kucoin',
                account_type VARCHAR(20) DEFAULT 'futures',
                currency VARCHAR(10) NOT NULL,
                total DECIMAL(20, 8),
                available DECIMAL(20, 8),
                frozen DECIMAL(20, 8),
                margin DECIMAL(20, 8),
                unrealized_pnl DECIMAL(20, 8),
                margin_ratio DECIMAL(10, 4),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Risk metrics table (enhanced for KuCoin)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_metrics (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                exchange VARCHAR(20) DEFAULT 'kucoin',
                total_exposure DECIMAL(20, 8),
                total_margin DECIMAL(20, 8),
                total_pnl DECIMAL(20, 8),
                unrealized_pnl DECIMAL(20, 8),
                realized_pnl DECIMAL(20, 8),
                margin_ratio DECIMAL(10, 4),
                liquidation_risk DECIMAL(5, 2),
                positions_count INTEGER,
                win_rate DECIMAL(5, 2),
                sharpe_ratio DECIMAL(10, 4),
                max_drawdown DECIMAL(10, 4),
                metadata JSONB
            )
        """)
        
        # Performance tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_history (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                exchange VARCHAR(20) DEFAULT 'kucoin',
                starting_balance DECIMAL(20, 8),
                ending_balance DECIMAL(20, 8),
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_volume DECIMAL(20, 8),
                total_fees DECIMAL(20, 8),
                net_pnl DECIMAL(20, 8),
                best_trade DECIMAL(20, 8),
                worst_trade DECIMAL(20, 8),
                metadata JSONB,
                UNIQUE(date, exchange)
            )
        """)
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_kucoin_positions_symbol ON kucoin_positions(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_kucoin_positions_status ON kucoin_positions(status)",
            "CREATE INDEX IF NOT EXISTS idx_kucoin_orders_symbol ON kucoin_orders(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_kucoin_orders_status ON kucoin_orders(status)",
            "CREATE INDEX IF NOT EXISTS idx_trading_signals_symbol ON trading_signals(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_trading_signals_created ON trading_signals(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_kucoin_market_symbol_time ON kucoin_market_data(symbol, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_risk_metrics_timestamp ON risk_metrics(timestamp)",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        logger.info("✅ All tables created successfully")
        
        # Get table count
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        logger.info(f"📊 Total tables in database: {table_count}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False

def insert_kucoin_config():
    """Insert KuCoin as default exchange"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if KuCoin config exists
        cursor.execute("SELECT id FROM exchange_config WHERE exchange_name = 'kucoin'")
        if cursor.fetchone():
            # Update existing config
            cursor.execute("""
                UPDATE exchange_config 
                SET is_default = TRUE,
                    futures_enabled = TRUE,
                    spot_enabled = FALSE,
                    base_url = %s,
                    ws_url = %s,
                    config = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE exchange_name = 'kucoin'
            """, (
                KUCOIN_CONFIG['base_url'],
                KUCOIN_CONFIG['ws_url'],
                json.dumps(KUCOIN_CONFIG)
            ))
            logger.info("✅ Updated KuCoin configuration")
        else:
            # Insert new config
            cursor.execute("""
                INSERT INTO exchange_config 
                (exchange_name, is_default, futures_enabled, spot_enabled, 
                 testnet, base_url, ws_url, config)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                'kucoin', True, True, False, False,
                KUCOIN_CONFIG['base_url'],
                KUCOIN_CONFIG['ws_url'],
                json.dumps(KUCOIN_CONFIG)
            ))
            logger.info("✅ Inserted KuCoin as default exchange")
        
        # Set all other exchanges as non-default
        cursor.execute("""
            UPDATE exchange_config 
            SET is_default = FALSE 
            WHERE exchange_name != 'kucoin'
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error configuring KuCoin: {e}")
        return False

def update_env_file():
    """Update .env file with PostgreSQL and KuCoin configuration"""
    env_file = Path("backend/zmart-api/.env")
    
    if not env_file.exists():
        logger.error("❌ .env file not found")
        return False
    
    # Read existing content
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Configuration to add/update
    config_updates = {
        'DATABASE_URL': f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}",
        'DB_HOST': DB_CONFIG['host'],
        'DB_PORT': str(DB_CONFIG['port']),
        'DB_NAME': DB_CONFIG['database'],
        'DB_USER': DB_CONFIG['user'],
        'DB_PASSWORD': DB_CONFIG['password'],
        'DEFAULT_EXCHANGE': 'kucoin',
        'KUCOIN_FUTURES_ENABLED': 'true',
        'KUCOIN_BASE_URL': KUCOIN_CONFIG['base_url'],
        'KUCOIN_WS_URL': KUCOIN_CONFIG['ws_url']
    }
    
    # Update or add configurations
    updated_keys = set()
    for i, line in enumerate(lines):
        for key, value in config_updates.items():
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                updated_keys.add(key)
                break
    
    # Add missing configurations
    for key, value in config_updates.items():
        if key not in updated_keys:
            lines.append(f"{key}={value}\n")
    
    # Write back
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    logger.info("✅ Updated .env file with PostgreSQL and KuCoin configuration")
    return True

def test_database_connection():
    """Test database connection and display info"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get PostgreSQL version
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        logger.info(f"✅ Connected to: {version}")
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        logger.info("\n📊 Database Tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            logger.info(f"  • {table[0]}: {count} records")
        
        # Check KuCoin configuration
        cursor.execute("SELECT * FROM exchange_config WHERE exchange_name = 'kucoin'")
        kucoin_config = cursor.fetchone()
        if kucoin_config:
            logger.info("\n🔧 KuCoin Configuration:")
            logger.info(f"  • Default Exchange: {'Yes' if kucoin_config[2] else 'No'}")
            logger.info(f"  • Futures Enabled: {'Yes' if kucoin_config[5] else 'No'}")
            logger.info(f"  • Base URL: {kucoin_config[8]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False

def create_kucoin_service():
    """Create KuCoin trading service"""
    service_code = '''#!/usr/bin/env python3
"""
KuCoin Trading Service for ZmartBot
Handles all KuCoin futures trading operations
"""

import ccxt
import os
from typing import Dict, List, Optional
import logging
import psycopg2
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KuCoinService:
    """KuCoin Futures trading service"""
    
    def __init__(self):
        self.exchange = None
        self.db_conn = None
        self.init_exchange()
        self.init_database()
    
    def init_exchange(self):
        """Initialize KuCoin exchange connection"""
        self.exchange = ccxt.kucoinfutures({
            'apiKey': os.getenv('KUCOIN_API_KEY'),
            'secret': os.getenv('KUCOIN_SECRET'),
            'password': os.getenv('KUCOIN_PASSPHRASE'),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True
            }
        })
        logger.info("✅ KuCoin Futures initialized")
    
    def init_database(self):
        """Initialize database connection"""
        self.db_conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432),
            database=os.getenv('DB_NAME', 'zmartbot_production'),
            user=os.getenv('DB_USER', 'zmartbot'),
            password=os.getenv('DB_PASSWORD')
        )
    
    def get_balance(self) -> Dict:
        """Get account balance"""
        try:
            balance = self.exchange.fetch_balance()
            
            # Store in database
            cursor = self.db_conn.cursor()
            for currency, info in balance['info'].items():
                if isinstance(info, dict) and 'available' in info:
                    cursor.execute("""
                        INSERT INTO account_balance 
                        (exchange, currency, total, available, frozen, updated_at)
                        VALUES ('kucoin', %s, %s, %s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (exchange, currency) 
                        DO UPDATE SET 
                            total = EXCLUDED.total,
                            available = EXCLUDED.available,
                            frozen = EXCLUDED.frozen,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        currency,
                        info.get('total', 0),
                        info.get('available', 0),
                        info.get('frozen', 0)
                    ))
            self.db_conn.commit()
            
            return balance
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {}
    
    def place_order(self, symbol: str, side: str, amount: float, 
                   price: Optional[float] = None, order_type: str = 'market') -> Dict:
        """Place an order on KuCoin"""
        try:
            if order_type == 'market':
                order = self.exchange.create_market_order(symbol, side, amount)
            else:
                order = self.exchange.create_limit_order(symbol, side, amount, price)
            
            # Store in database
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO kucoin_orders 
                (order_id, symbol, side, type, size, price, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                order['id'],
                symbol,
                side,
                order_type,
                amount,
                price,
                order['status']
            ))
            self.db_conn.commit()
            
            logger.info(f"✅ Order placed: {order['id']}")
            return order
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Get open positions"""
        try:
            positions = self.exchange.fetch_positions()
            
            # Update database
            cursor = self.db_conn.cursor()
            for pos in positions:
                if pos['contracts'] > 0:
                    cursor.execute("""
                        INSERT INTO kucoin_positions 
                        (symbol, side, size, entry_price, mark_price, 
                         unrealized_pnl, status, opened_at)
                        VALUES (%s, %s, %s, %s, %s, %s, 'OPEN', CURRENT_TIMESTAMP)
                        ON CONFLICT (symbol, side) 
                        DO UPDATE SET 
                            size = EXCLUDED.size,
                            mark_price = EXCLUDED.mark_price,
                            unrealized_pnl = EXCLUDED.unrealized_pnl
                    """, (
                        pos['symbol'],
                        pos['side'],
                        pos['contracts'],
                        pos['entryPrice'],
                        pos['markPrice'],
                        pos['unrealizedPnl']
                    ))
            self.db_conn.commit()
            
            return positions
            
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []
    
    def close_position(self, symbol: str) -> bool:
        """Close a position"""
        try:
            positions = self.get_positions()
            for pos in positions:
                if pos['symbol'] == symbol and pos['contracts'] > 0:
                    side = 'sell' if pos['side'] == 'long' else 'buy'
                    self.place_order(symbol, side, pos['contracts'])
                    
                    # Update database
                    cursor = self.db_conn.cursor()
                    cursor.execute("""
                        UPDATE kucoin_positions 
                        SET status = 'CLOSED', closed_at = CURRENT_TIMESTAMP
                        WHERE symbol = %s AND status = 'OPEN'
                    """, (symbol,))
                    self.db_conn.commit()
                    
                    logger.info(f"✅ Position closed: {symbol}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False

# Export service
kucoin_service = KuCoinService()
'''
    
    # Save KuCoin service file
    service_file = Path("backend/zmart-api/src/services/kucoin_futures_service.py")
    service_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(service_file, 'w') as f:
        f.write(service_code)
    
    logger.info(f"✅ Created KuCoin service at {service_file}")
    return True

def main():
    """Main setup function"""
    print("\n🔧 ZmartBot PostgreSQL & KuCoin Setup")
    print("=" * 60)
    
    # Step 1: Check PostgreSQL
    if not check_postgres():
        print("❌ PostgreSQL is not running. Please start it first:")
        print("   brew services start postgresql@15")
        return 1
    
    # Step 2: Create database
    print("\n📊 Creating database...")
    if not create_database():
        return 1
    
    # Step 3: Create tables
    print("\n📋 Creating tables...")
    if not create_tables():
        return 1
    
    # Step 4: Configure KuCoin
    print("\n🔧 Configuring KuCoin as default exchange...")
    if not insert_kucoin_config():
        return 1
    
    # Step 5: Update environment
    print("\n⚙️ Updating environment configuration...")
    if not update_env_file():
        return 1
    
    # Step 6: Create KuCoin service
    print("\n📝 Creating KuCoin trading service...")
    if not create_kucoin_service():
        return 1
    
    # Step 7: Test connection
    print("\n🔍 Testing database connection...")
    if not test_database_connection():
        return 1
    
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("\n📊 Database Configuration:")
    print(f"  • Host: {DB_CONFIG['host']}")
    print(f"  • Port: {DB_CONFIG['port']}")
    print(f"  • Database: {DB_CONFIG['database']}")
    print(f"  • User: {DB_CONFIG['user']}")
    
    print("\n🔧 KuCoin Configuration:")
    print(f"  • Default Exchange: Yes")
    print(f"  • Mode: Futures Trading")
    print(f"  • API URL: {KUCOIN_CONFIG['base_url']}")
    
    print("\n📝 Connection String:")
    print(f"  postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    print("\n🚀 Next Steps:")
    print("  1. Restart the backend server to use PostgreSQL")
    print("  2. Verify KuCoin API keys in .env file")
    print("  3. Test trading connection with KuCoin")
    
    print("\n💡 To connect to database:")
    print(f"  psql -h localhost -U {DB_CONFIG['user']} -d {DB_CONFIG['database']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())