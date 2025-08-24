#!/usr/bin/env python3
"""
Production Database Setup for ZmartBot
Sets up PostgreSQL database with all required tables and initial data
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'zmart_bot',
    'user': 'zmart_user',
    'password': 'zmart_secure_password_2025'
}

def check_postgres():
    """Check if PostgreSQL is installed and running"""
    try:
        result = subprocess.run(['pg_isready'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ PostgreSQL is running")
            return True
        else:
            logger.error("❌ PostgreSQL is not running")
            logger.info("Start PostgreSQL with: brew services start postgresql@14")
            return False
    except FileNotFoundError:
        logger.error("❌ PostgreSQL is not installed")
        logger.info("Install with: brew install postgresql@14")
        return False

def create_database():
    """Create the database and user"""
    try:
        # Connect to PostgreSQL as superuser
        conn = psycopg2.connect(
            host='localhost',
            database='postgres',
            user=os.environ.get('USER'),  # Use system user
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create user if not exists
        cursor.execute("SELECT 1 FROM pg_user WHERE usename = %s", (DB_CONFIG['user'],))
        if not cursor.fetchone():
            cursor.execute(f"CREATE USER {DB_CONFIG['user']} WITH PASSWORD '{DB_CONFIG['password']}'")
            logger.info(f"✅ Created user: {DB_CONFIG['user']}")
        else:
            cursor.execute(f"ALTER USER {DB_CONFIG['user']} WITH PASSWORD '{DB_CONFIG['password']}'")
            logger.info(f"✅ Updated password for user: {DB_CONFIG['user']}")
        
        # Create database if not exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['database'],))
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']} OWNER {DB_CONFIG['user']}")
            logger.info(f"✅ Created database: {DB_CONFIG['database']}")
        else:
            logger.info(f"✅ Database already exists: {DB_CONFIG['database']}")
        
        # Grant all privileges
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_CONFIG['database']} TO {DB_CONFIG['user']}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating database: {e}")
        return False

def create_tables():
    """Create all required tables"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create tables SQL
        tables = [
            # Positions table
            """
            CREATE TABLE IF NOT EXISTS positions (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                entry_price DECIMAL(20, 8) NOT NULL,
                quantity DECIMAL(20, 8) NOT NULL,
                leverage INTEGER DEFAULT 1,
                stop_loss DECIMAL(20, 8),
                take_profit DECIMAL(20, 8),
                status VARCHAR(20) DEFAULT 'OPEN',
                pnl DECIMAL(20, 8) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                metadata JSONB
            )
            """,
            
            # Trades table
            """
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                position_id INTEGER REFERENCES positions(id),
                symbol VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                price DECIMAL(20, 8) NOT NULL,
                quantity DECIMAL(20, 8) NOT NULL,
                fee DECIMAL(20, 8) DEFAULT 0,
                realized_pnl DECIMAL(20, 8) DEFAULT 0,
                order_id VARCHAR(100),
                exchange VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB
            )
            """,
            
            # Signals table
            """
            CREATE TABLE IF NOT EXISTS signals (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                signal_type VARCHAR(20) NOT NULL,
                strength DECIMAL(5, 2),
                source VARCHAR(50),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Market data table
            """
            CREATE TABLE IF NOT EXISTS market_data (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                price DECIMAL(20, 8) NOT NULL,
                volume DECIMAL(20, 8),
                bid DECIMAL(20, 8),
                ask DECIMAL(20, 8),
                high_24h DECIMAL(20, 8),
                low_24h DECIMAL(20, 8),
                change_24h DECIMAL(10, 4),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source VARCHAR(20)
            )
            """,
            
            # Risk metrics table
            """
            CREATE TABLE IF NOT EXISTS risk_metrics (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_exposure DECIMAL(20, 8),
                total_pnl DECIMAL(20, 8),
                win_rate DECIMAL(5, 2),
                sharpe_ratio DECIMAL(10, 4),
                max_drawdown DECIMAL(10, 4),
                var_95 DECIMAL(20, 8),
                metadata JSONB
            )
            """,
            
            # Alerts table
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                alert_type VARCHAR(50) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                message TEXT,
                metadata JSONB,
                acknowledged BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Performance metrics table
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL UNIQUE,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_pnl DECIMAL(20, 8) DEFAULT 0,
                best_trade DECIMAL(20, 8),
                worst_trade DECIMAL(20, 8),
                avg_win DECIMAL(20, 8),
                avg_loss DECIMAL(20, 8),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Learning patterns table
            """
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id SERIAL PRIMARY KEY,
                pattern_type VARCHAR(50) NOT NULL,
                symbol VARCHAR(20),
                conditions JSONB NOT NULL,
                outcome JSONB,
                confidence DECIMAL(5, 2),
                occurrences INTEGER DEFAULT 1,
                success_rate DECIMAL(5, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status)",
            "CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_trades_created ON trades(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_signals_created ON signals(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_performance_date ON performance_metrics(date)",
        ]
        
        # Execute table creation
        for table_sql in tables:
            cursor.execute(table_sql)
            
        # Execute index creation
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

def update_env_file():
    """Update .env file with database configuration"""
    env_file = Path("backend/zmart-api/.env")
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update database configuration
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('DB_HOST='):
                lines[i] = f"DB_HOST={DB_CONFIG['host']}\n"
                updated = True
            elif line.startswith('DB_PORT='):
                lines[i] = f"DB_PORT={DB_CONFIG['port']}\n"
                updated = True
            elif line.startswith('DB_NAME='):
                lines[i] = f"DB_NAME={DB_CONFIG['database']}\n"
                updated = True
            elif line.startswith('DB_USER='):
                lines[i] = f"DB_USER={DB_CONFIG['user']}\n"
                updated = True
            elif line.startswith('DB_PASSWORD='):
                lines[i] = f"DB_PASSWORD={DB_CONFIG['password']}\n"
                updated = True
        
        if updated:
            with open(env_file, 'w') as f:
                f.writelines(lines)
            logger.info("✅ Updated .env file with database configuration")
        
        # Also update .env.production
        env_prod = Path(".env.production")
        if env_prod.exists():
            with open(env_prod, 'r') as f:
                content = f.read()
            
            # Add database configuration if not present
            if 'POSTGRES_USER=' not in content:
                with open(env_prod, 'a') as f:
                    f.write(f"\n# PostgreSQL Production Configuration\n")
                    f.write(f"POSTGRES_USER={DB_CONFIG['user']}\n")
                    f.write(f"POSTGRES_PASSWORD={DB_CONFIG['password']}\n")
                    f.write(f"POSTGRES_DB={DB_CONFIG['database']}\n")
                logger.info("✅ Updated .env.production with database configuration")

def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        logger.info(f"✅ Connected to: {version}")
        
        # Get table list
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        logger.info("\n📊 Available tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            logger.info(f"  • {table[0]}: {count} records")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("\n🔧 ZmartBot Production Database Setup")
    print("=" * 50)
    
    # Check PostgreSQL
    if not check_postgres():
        print("\n❌ Please install and start PostgreSQL first")
        return 1
    
    # Create database and user
    if not create_database():
        print("\n❌ Failed to create database")
        return 1
    
    # Create tables
    if not create_tables():
        print("\n❌ Failed to create tables")
        return 1
    
    # Update environment files
    update_env_file()
    
    # Test connection
    if not test_connection():
        print("\n❌ Connection test failed")
        return 1
    
    print("\n" + "=" * 50)
    print("✅ Database setup complete!")
    print("\n📝 Database Configuration:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Port: {DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['database']}")
    print(f"  User: {DB_CONFIG['user']}")
    print("\n🚀 Next: Restart the server to use the new database:")
    print("  cd backend/zmart-api")
    print("  pkill -f uvicorn")
    print("  python -m uvicorn src.main:app --host 0.0.0.0 --port 8000")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())