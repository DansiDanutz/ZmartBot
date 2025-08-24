#!/bin/bash

# My Symbols Database Protection Status Check
# ===========================================

echo "🔍 My Symbols Database Protection Status"
echo "========================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if protection is running
if [ -f "protection.pid" ]; then
    PROTECTION_PID=$(cat protection.pid)
    if ps -p $PROTECTION_PID > /dev/null; then
        echo "✅ Protection System: RUNNING (PID: $PROTECTION_PID)"
    else
        echo "❌ Protection System: NOT RUNNING (stale PID file)"
        rm -f protection.pid
    fi
else
    echo "❌ Protection System: NOT RUNNING"
fi

echo ""

# Check database file
if [ -f "my_symbols_v2.db" ]; then
    echo "✅ Database File: EXISTS"
    
    # Check file permissions
    PERMS=$(ls -la my_symbols_v2.db | awk '{print $1}')
    echo "📁 File Permissions: $PERMS"
    
    # Check if immutable flag is set
    if lsattr my_symbols_v2.db 2>/dev/null | grep -q "i"; then
        echo "🛡️ Immutable Flag: SET (file protected from deletion/modification)"
    else
        echo "⚠️ Immutable Flag: NOT SET"
    fi
    
    # Check file size
    SIZE=$(ls -lh my_symbols_v2.db | awk '{print $5}')
    echo "📊 File Size: $SIZE"
    
else
    echo "❌ Database File: MISSING"
fi

echo ""

# Check backups
BACKUP_COUNT=$(ls backups/my_symbols_v2_protected_*.db 2>/dev/null | wc -l)
if [ $BACKUP_COUNT -gt 0 ]; then
    echo "💾 Backups: $BACKUP_COUNT found"
    
    # Show most recent backup
    LATEST_BACKUP=$(ls -t backups/my_symbols_v2_protected_*.db 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        BACKUP_TIME=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$LATEST_BACKUP")
        echo "🕒 Latest Backup: $BACKUP_TIME"
    fi
else
    echo "❌ Backups: NONE FOUND"
fi

echo ""

# Check database integrity
echo "🔍 Database Integrity Check:"
if [ -f "my_symbols_v2.db" ]; then
    # Quick integrity check
    SYMBOL_COUNT=$(sqlite3 my_symbols_v2.db "SELECT COUNT(*) FROM portfolio_composition WHERE status = 'Active';" 2>/dev/null)
    if [ "$SYMBOL_COUNT" = "10" ]; then
        echo "✅ Active Symbols: $SYMBOL_COUNT (correct)"
    else
        echo "❌ Active Symbols: $SYMBOL_COUNT (should be 10)"
    fi
    
    # Check if all expected symbols are present
    EXPECTED_SYMBOLS="BTCUSDT ETHUSDT SOLUSDT BNBUSDT XRPUSDT ADAUSDT AVAXUSDT DOGEUSDT DOTUSDT LINKUSDT"
    MISSING_SYMBOLS=""
    
    for symbol in $EXPECTED_SYMBOLS; do
        if ! sqlite3 my_symbols_v2.db "SELECT 1 FROM portfolio_composition pc JOIN symbols s ON pc.symbol_id = s.id WHERE s.symbol = '$symbol' AND pc.status = 'Active';" 2>/dev/null | grep -q "1"; then
            MISSING_SYMBOLS="$MISSING_SYMBOLS $symbol"
        fi
    done
    
    if [ -z "$MISSING_SYMBOLS" ]; then
        echo "✅ All Expected Symbols: PRESENT"
    else
        echo "❌ Missing Symbols:$MISSING_SYMBOLS"
    fi
else
    echo "❌ Cannot check integrity - database file missing"
fi

echo ""

# Check protection log
if [ -f "database_protection.log" ]; then
    echo "📝 Protection Log: EXISTS"
    echo "🕒 Last Log Entry:"
    tail -1 database_protection.log 2>/dev/null || echo "No log entries found"
else
    echo "📝 Protection Log: NOT FOUND"
fi

echo ""
echo "========================================"
