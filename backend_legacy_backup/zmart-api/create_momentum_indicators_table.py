#!/usr/bin/env python3
"""
Create Momentum Indicators Table
Adds the momentum_indicators_data table to the database for storing Rate of Change (ROC) and Momentum (MOM) analysis
"""

import sqlite3
import os
from datetime import datetime

def create_momentum_indicators_table():
    """Create the momentum_indicators_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create momentum_indicators_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS momentum_indicators_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                roc_value REAL NOT NULL,
                roc_signal TEXT NOT NULL,
                roc_strength REAL DEFAULT 0.0,
                roc_divergence TEXT DEFAULT 'none',
                roc_divergence_strength REAL DEFAULT 0.0,
                mom_value REAL NOT NULL,
                mom_signal TEXT NOT NULL,
                mom_strength REAL DEFAULT 0.0,
                mom_divergence TEXT DEFAULT 'none',
                mom_divergence_strength REAL DEFAULT 0.0,
                momentum_status TEXT NOT NULL,
                momentum_strength REAL DEFAULT 0.0,
                trend_alignment TEXT DEFAULT 'neutral',
                trend_strength REAL DEFAULT 0.0,
                overbought_oversold_status TEXT DEFAULT 'neutral',
                overbought_oversold_strength REAL DEFAULT 0.0,
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
            CREATE INDEX IF NOT EXISTS idx_momentum_indicators_data_symbol 
            ON momentum_indicators_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_momentum_indicators_data_timeframe 
            ON momentum_indicators_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_momentum_indicators_data_signal 
            ON momentum_indicators_data(roc_signal, mom_signal)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_momentum_indicators_data_status 
            ON momentum_indicators_data(momentum_status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_momentum_indicators_data_divergence 
            ON momentum_indicators_data(roc_divergence, mom_divergence)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_momentum_indicators_data_updated 
            ON momentum_indicators_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Momentum Indicators data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Momentum Indicators table: {e}")
        return False

if __name__ == "__main__":
    create_momentum_indicators_table()
