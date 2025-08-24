#!/usr/bin/env python3
"""
Create Moving Average Convergence Table
Adds the ma_convergence_data table to the database for storing Moving Average Convergence analysis
"""

import sqlite3
import os
from datetime import datetime

def create_ma_convergence_table():
    """Create the ma_convergence_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create ma_convergence_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ma_convergence_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                sma_10 REAL NOT NULL,
                sma_20 REAL NOT NULL,
                sma_50 REAL NOT NULL,
                sma_200 REAL NOT NULL,
                ema_12 REAL NOT NULL,
                ema_26 REAL NOT NULL,
                convergence_status TEXT NOT NULL,
                convergence_strength REAL DEFAULT 0.0,
                ma_alignment TEXT NOT NULL,
                alignment_strength REAL DEFAULT 0.0,
                golden_cross_detected TEXT DEFAULT 'none',
                golden_cross_strength REAL DEFAULT 0.0,
                death_cross_detected TEXT DEFAULT 'none',
                death_cross_strength REAL DEFAULT 0.0,
                trend_direction TEXT NOT NULL,
                trend_strength REAL DEFAULT 0.0,
                support_resistance_levels TEXT,
                breakout_potential TEXT DEFAULT 'none',
                breakout_strength REAL DEFAULT 0.0,
                volume_confirmation TEXT DEFAULT 'none',
                volume_strength REAL DEFAULT 0.0,
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ma_convergence_data_symbol 
            ON ma_convergence_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ma_convergence_data_timeframe 
            ON ma_convergence_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ma_convergence_data_convergence 
            ON ma_convergence_data(convergence_status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ma_convergence_data_alignment 
            ON ma_convergence_data(ma_alignment)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ma_convergence_data_updated 
            ON ma_convergence_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Moving Average Convergence data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Moving Average Convergence table: {e}")
        return False

if __name__ == "__main__":
    create_ma_convergence_table()
