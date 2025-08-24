#!/usr/bin/env python3
"""
Create Bollinger Band Squeeze Table
Adds the bollinger_squeeze_data table to the database for storing Bollinger Band Squeeze analysis
"""

import sqlite3
import os
from datetime import datetime

def create_bollinger_squeeze_table():
    """Create the bollinger_squeeze_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create bollinger_squeeze_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bollinger_squeeze_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                squeeze_status TEXT NOT NULL,
                squeeze_strength REAL DEFAULT 0.0,
                band_width REAL NOT NULL,
                band_width_percentile REAL NOT NULL,
                upper_band REAL NOT NULL,
                middle_band REAL NOT NULL,
                lower_band REAL NOT NULL,
                current_price REAL NOT NULL,
                price_position REAL NOT NULL,
                volatility_ratio REAL DEFAULT 0.0,
                historical_volatility REAL DEFAULT 0.0,
                current_volatility REAL DEFAULT 0.0,
                squeeze_duration INTEGER DEFAULT 0,
                breakout_potential TEXT DEFAULT 'none',
                breakout_direction TEXT DEFAULT 'neutral',
                breakout_strength REAL DEFAULT 0.0,
                momentum_divergence TEXT DEFAULT 'none',
                momentum_strength REAL DEFAULT 0.0,
                volume_profile TEXT DEFAULT 'normal',
                volume_strength REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bollinger_squeeze_data_symbol 
            ON bollinger_squeeze_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bollinger_squeeze_data_timeframe 
            ON bollinger_squeeze_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bollinger_squeeze_data_squeeze 
            ON bollinger_squeeze_data(squeeze_status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bollinger_squeeze_data_breakout 
            ON bollinger_squeeze_data(breakout_potential)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bollinger_squeeze_data_updated 
            ON bollinger_squeeze_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Bollinger Band Squeeze data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Bollinger Band Squeeze table: {e}")
        return False

if __name__ == "__main__":
    create_bollinger_squeeze_table()
