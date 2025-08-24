#!/usr/bin/env python3
"""
Create Symbol Alerts Table
Adds the symbol_alerts table to the database for dynamic alert management
"""

import sqlite3
import os
from datetime import datetime

def create_alerts_table():
    """Create the symbol_alerts table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create symbol_alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS symbol_alerts (
                id TEXT PRIMARY KEY,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                condition TEXT NOT NULL,
                threshold REAL NOT NULL,
                current_price REAL,
                price_change_24h REAL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                last_triggered TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id)
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_symbol_alerts_symbol 
            ON symbol_alerts(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_symbol_alerts_active 
            ON symbol_alerts(is_active)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Symbol alerts table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating alerts table: {e}")
        return False

if __name__ == "__main__":
    create_alerts_table()
