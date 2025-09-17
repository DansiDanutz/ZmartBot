#!/usr/bin/env python3
"""
🎯 SINGLE SOURCE OF TRUTH - Database Configuration
MANDATORY configuration file that ALL services MUST import and use.
"""

import os
from pathlib import Path

# Project root - NEVER CHANGE THIS
PROJECT_ROOT = Path(__file__).parent.parent.parent

# THE ONE AND ONLY service registry database
MASTER_SERVICE_REGISTRY_DB = PROJECT_ROOT / "src" / "data" / "service_registry.db"
MASTER_SERVICE_REGISTRY_DB_STR = str(MASTER_SERVICE_REGISTRY_DB.absolute())

def get_master_database_path() -> str:
    """Get the master service registry database path."""
    return MASTER_SERVICE_REGISTRY_DB_STR

def get_master_database_connection():
    """Get a connection to the master service registry database."""
    import sqlite3
    return sqlite3.connect(MASTER_SERVICE_REGISTRY_DB_STR)

# FORBIDDEN PATHS - NEVER USE THESE
FORBIDDEN_PATHS = [
    "service_registry.db",
    "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/service_registry.db", 
    "passport_registry.db",
]

def check_for_violations():
    """Check for forbidden database files."""
    violations = []
    for forbidden_path in FORBIDDEN_PATHS:
        test_path = PROJECT_ROOT / forbidden_path
        if test_path.exists():
            violations.append(str(test_path))
        if os.path.isabs(forbidden_path) and os.path.exists(forbidden_path):
            violations.append(forbidden_path)
    return violations

def prevent_database_violations():
    """Remove forbidden database files."""
    violations = check_for_violations()
    if violations:
        print(f"🚨 Found {len(violations)} database violations!")
        for violation in violations:
            try:
                if os.path.exists(violation) and os.path.getsize(violation) == 0:
                    os.remove(violation)
                    print(f"✅ Removed: {violation}")
            except Exception as e:
                print(f"❌ Could not remove {violation}: {e}")

# Automatically prevent violations
prevent_database_violations()
