#!/usr/bin/env python3
"""
Centralized Database Configuration
Defines the correct database paths for all services
"""

import os
from pathlib import Path

# Get the project root directory (4 levels up from this file to reach ZmartBot root)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
BACKEND_ROOT = Path(__file__).parent.parent.parent

# Database paths - According to PROJECT_INVENTORY.md, the ONLY official database is in backend/zmart-api/
MY_SYMBOLS_DB_PATH = str(BACKEND_ROOT / "my_symbols_v2.db")
PROJECT_ROOT_DB_PATH = str(PROJECT_ROOT / "my_symbols_v2.db")

# Use the backend database as the primary one (as specified in PROJECT_INVENTORY.md)
PRIMARY_DB_PATH = MY_SYMBOLS_DB_PATH

# Fallback paths in order of preference
DB_PATHS = [
    PRIMARY_DB_PATH,  # backend/zmart-api/my_symbols_v2.db (OFFICIAL)
    PROJECT_ROOT_DB_PATH,  # Project root fallback
    "my_symbols_v2.db",  # Current directory fallback
]

def get_database_path() -> str:
    """Get the correct database path, checking for file existence"""
    for db_path in DB_PATHS:
        if os.path.exists(db_path):
            return db_path
    
    # If none exist, return the primary path
    return PRIMARY_DB_PATH

def ensure_database_exists() -> str:
    """Ensure the database exists and return the path"""
    db_path = get_database_path()
    
    # If the primary database doesn't exist but project root one does, copy it
    if not os.path.exists(PRIMARY_DB_PATH) and os.path.exists(PROJECT_ROOT_DB_PATH):
        import shutil
        shutil.copy2(PROJECT_ROOT_DB_PATH, PRIMARY_DB_PATH)
        print(f"✅ Copied database from {PROJECT_ROOT_DB_PATH} to {PRIMARY_DB_PATH}")
    
    return db_path

# Export the primary database path for easy access
DATABASE_PATH = ensure_database_exists()
