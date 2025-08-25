#!/usr/bin/env python3
"""
Create ATR Table
Adds the atr_data table to the database for storing ATR (Average True Range) indicators
"""

import sqlite3
import os
from datetime import datetime

def create_atr_table():
    """Create the atr_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create atr_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS atr_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                atr_value REAL NOT NULL,
                atr_percentage REAL NOT NULL,
                volatility_level TEXT NOT NULL,
                volatility_strength REAL DEFAULT 0.0,
                true_range REAL NOT NULL,
                high_low_range REAL NOT NULL,
                high_close_range REAL NOT NULL,
                low_close_range REAL NOT NULL,
                volatility_trend TEXT DEFAULT 'neutral',
                volatility_change REAL DEFAULT 0.0,
                breakout_potential TEXT DEFAULT 'none',
                breakout_strength REAL DEFAULT 0.0,
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_atr_data_symbol 
            ON atr_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_atr_data_timeframe 
            ON atr_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_atr_data_volatility 
            ON atr_data(volatility_level)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_atr_data_updated 
            ON atr_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ ATR data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating ATR table: {e}")
        return False

if __name__ == "__main__":
    create_atr_table()
