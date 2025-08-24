#!/usr/bin/env python3
"""
Create Stochastic RSI Table
Adds the stoch_rsi_data table to the database for storing Stochastic RSI indicators
"""

import sqlite3
import os
from datetime import datetime

def create_stoch_rsi_table():
    """Create the stoch_rsi_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create stoch_rsi_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stoch_rsi_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                rsi_value REAL NOT NULL,
                stoch_k REAL NOT NULL,
                stoch_d REAL NOT NULL,
                stoch_rsi_value REAL NOT NULL,
                overbought_level REAL DEFAULT 80.0,
                oversold_level REAL DEFAULT 20.0,
                signal_status TEXT NOT NULL,
                signal_strength REAL DEFAULT 0.0,
                divergence_type TEXT DEFAULT 'none',
                divergence_strength REAL DEFAULT 0.0,
                momentum_trend TEXT DEFAULT 'neutral',
                momentum_strength REAL DEFAULT 0.0,
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stoch_rsi_data_symbol 
            ON stoch_rsi_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stoch_rsi_data_timeframe 
            ON stoch_rsi_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stoch_rsi_data_signal 
            ON stoch_rsi_data(signal_status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stoch_rsi_data_updated 
            ON stoch_rsi_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Stochastic RSI data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Stochastic RSI table: {e}")
        return False

if __name__ == "__main__":
    create_stoch_rsi_table()
