#!/usr/bin/env python3
"""
Create Parabolic SAR Table
Adds the parabolic_sar_data table to the database for storing Parabolic SAR indicators
"""

import sqlite3
import os
from datetime import datetime

def create_parabolic_sar_table():
    """Create the parabolic_sar_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create parabolic_sar_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parabolic_sar_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                sar_value REAL NOT NULL,
                trend_direction TEXT NOT NULL,
                trend_strength REAL DEFAULT 0.0,
                acceleration_factor REAL NOT NULL,
                extreme_point REAL NOT NULL,
                stop_loss_level REAL NOT NULL,
                take_profit_level REAL NOT NULL,
                risk_reward_ratio REAL DEFAULT 0.0,
                trend_duration INTEGER DEFAULT 0,
                trend_quality TEXT DEFAULT 'neutral',
                reversal_signal TEXT DEFAULT 'none',
                reversal_strength REAL DEFAULT 0.0,
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_parabolic_sar_data_symbol 
            ON parabolic_sar_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_parabolic_sar_data_timeframe 
            ON parabolic_sar_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_parabolic_sar_data_trend 
            ON parabolic_sar_data(trend_direction)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_parabolic_sar_data_updated 
            ON parabolic_sar_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Parabolic SAR data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Parabolic SAR table: {e}")
        return False

if __name__ == "__main__":
    create_parabolic_sar_table()
