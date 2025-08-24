#!/usr/bin/env python3
"""
Create RSI Table
Adds the rsi_data table to the database for storing RSI indicators
"""

import sqlite3
import os
from datetime import datetime

def create_rsi_table():
    """Create the rsi_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create rsi_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rsi_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                rsi_value REAL NOT NULL,
                signal_status TEXT NOT NULL,
                overbought_level REAL DEFAULT 70.0,
                oversold_level REAL DEFAULT 30.0,
                divergence_type TEXT DEFAULT 'none',
                divergence_strength REAL DEFAULT 0.0,
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rsi_data_symbol 
            ON rsi_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rsi_data_timeframe 
            ON rsi_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rsi_data_status 
            ON rsi_data(signal_status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rsi_data_updated 
            ON rsi_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ RSI data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating RSI table: {e}")
        return False

if __name__ == "__main__":
    create_rsi_table()
