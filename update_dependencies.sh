#!/bin/bash
# update_dependencies.sh - Safe dependency update script for ZmartBot

set -e

PROJECT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"
BACKUP_DIR="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$PROJECT_ROOT/update_log_$(date +%Y%m%d).txt"

echo "🔄 ZmartBot Dependency Update Script" | tee -a "$LOG_FILE"
echo "=====================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Check if venv exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "❌ Error: Virtual environment not found at $PROJECT_ROOT/venv" | tee -a "$LOG_FILE"
    echo "Please create it first with: python3.11 -m venv venv" | tee -a "$LOG_FILE"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..." | tee -a "$LOG_FILE"
source "$PROJECT_ROOT/venv/bin/activate"

# Create backup directory
echo "💾 Creating backup..." | tee -a "$LOG_FILE"
mkdir -p "$BACKUP_DIR"

# Backup current requirements
echo "  Backing up current requirements..." | tee -a "$LOG_FILE"
pip freeze > "$BACKUP_DIR/requirements_before.txt"
cp "$PROJECT_ROOT/requirements.txt" "$BACKUP_DIR/requirements_original.txt" 2>/dev/null || true

# Show current state
echo "" | tee -a "$LOG_FILE"
echo "📊 Current State:" | tee -a "$LOG_FILE"
python --version | tee -a "$LOG_FILE"
echo "Total packages: $(pip list | wc -l)" | tee -a "$LOG_FILE"

# Update pip, setuptools, wheel
echo "" | tee -a "$LOG_FILE"
echo "🔧 Updating pip, setuptools, wheel..." | tee -a "$LOG_FILE"
pip install --upgrade pip setuptools wheel >> "$LOG_FILE" 2>&1

# Phase 1: Security Updates
echo "" | tee -a "$LOG_FILE"
echo "🔒 Phase 1: Security Updates" | tee -a "$LOG_FILE"
echo "============================" | tee -a "$LOG_FILE"

SECURITY_PACKAGES=(
    "cryptography"
    "aiohttp"
    "bcrypt"
)

for pkg in "${SECURITY_PACKAGES[@]}"; do
    echo "  Updating $pkg..." | tee -a "$LOG_FILE"
    pip install --upgrade "$pkg" >> "$LOG_FILE" 2>&1 && \
        echo "    ✅ $pkg updated" | tee -a "$LOG_FILE" || \
        echo "    ⚠️  $pkg update failed" | tee -a "$LOG_FILE"
done

# Test imports after security updates
echo "" | tee -a "$LOG_FILE"
echo "🧪 Testing security package imports..." | tee -a "$LOG_FILE"
python -c "import cryptography, aiohttp, bcrypt; print('✅ Security packages OK')" | tee -a "$LOG_FILE"

# Phase 2: Core Framework (Optional - uncomment if ready)
echo "" | tee -a "$LOG_FILE"
echo "🚀 Phase 2: Core Framework Updates" | tee -a "$LOG_FILE"
echo "===================================" | tee -a "$LOG_FILE"
echo "⚠️  Skipping (uncomment in script to enable)" | tee -a "$LOG_FILE"

# Uncomment these when ready:
# CORE_PACKAGES=(
#     "fastapi"
#     "uvicorn"
#     "pydantic"
# )
#
# for pkg in "${CORE_PACKAGES[@]}"; do
#     echo "  Updating $pkg..." | tee -a "$LOG_FILE"
#     pip install --upgrade "$pkg" >> "$LOG_FILE" 2>&1 && \
#         echo "    ✅ $pkg updated" | tee -a "$LOG_FILE" || \
#         echo "    ⚠️  $pkg update failed" | tee -a "$LOG_FILE"
# done

# Phase 3: Database & Async
echo "" | tee -a "$LOG_FILE"
echo "🗄️  Phase 3: Database & Async Updates" | tee -a "$LOG_FILE"
echo "======================================" | tee -a "$LOG_FILE"

DB_PACKAGES=(
    "asyncpg"
    "alembic"
    "anyio"
    "async-timeout"
)

for pkg in "${DB_PACKAGES[@]}"; do
    echo "  Updating $pkg..." | tee -a "$LOG_FILE"
    pip install --upgrade "$pkg" >> "$LOG_FILE" 2>&1 && \
        echo "    ✅ $pkg updated" | tee -a "$LOG_FILE" || \
        echo "    ⚠️  $pkg update failed" | tee -a "$LOG_FILE"
done

# Phase 4: Development Tools
echo "" | tee -a "$LOG_FILE"
echo "🛠️  Phase 4: Development Tools" | tee -a "$LOG_FILE"
echo "==============================" | tee -a "$LOG_FILE"

DEV_PACKAGES=(
    "black"
    "isort"
    "coverage"
)

for pkg in "${DEV_PACKAGES[@]}"; do
    echo "  Updating $pkg..." | tee -a "$LOG_FILE"
    pip install --upgrade "$pkg" >> "$LOG_FILE" 2>&1 && \
        echo "    ✅ $pkg updated" | tee -a "$LOG_FILE" || \
        echo "    ⚠️  $pkg update failed" | tee -a "$LOG_FILE"
done

# Save new state
echo "" | tee -a "$LOG_FILE"
echo "💾 Saving new state..." | tee -a "$LOG_FILE"
pip freeze > "$BACKUP_DIR/requirements_after.txt"

# Show diff
echo "" | tee -a "$LOG_FILE"
echo "📊 Changes Summary:" | tee -a "$LOG_FILE"
echo "==================" | tee -a "$LOG_FILE"

if command -v diff &> /dev/null; then
    diff "$BACKUP_DIR/requirements_before.txt" "$BACKUP_DIR/requirements_after.txt" | grep "^[<>]" | head -20 | tee -a "$LOG_FILE"
else
    echo "  (diff command not available)" | tee -a "$LOG_FILE"
fi

# Final verification
echo "" | tee -a "$LOG_FILE"
echo "🧪 Final Verification:" | tee -a "$LOG_FILE"
echo "=====================" | tee -a "$LOG_FILE"

python -c "
import sys
try:
    import fastapi
    import uvicorn
    import aiohttp
    import asyncpg
    print('✅ Core imports successful')
    sys.exit(0)
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "✅ Update Complete!" | tee -a "$LOG_FILE"
    echo "==================" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "Backup location: $BACKUP_DIR" | tee -a "$LOG_FILE"
    echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "Next steps:" | tee -a "$LOG_FILE"
    echo "1. Test your application thoroughly" | tee -a "$LOG_FILE"
    echo "2. Run tests: pytest" | tee -a "$LOG_FILE"
    echo "3. Start dev server: uvicorn main:app --reload" | tee -a "$LOG_FILE"
    echo "4. If issues occur, rollback with:" | tee -a "$LOG_FILE"
    echo "   pip install -r $BACKUP_DIR/requirements_before.txt --force-reinstall" | tee -a "$LOG_FILE"
else
    echo "" | tee -a "$LOG_FILE"
    echo "⚠️  Update completed with warnings" | tee -a "$LOG_FILE"
    echo "==================================" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "Some packages may have import errors." | tee -a "$LOG_FILE"
    echo "Check log file: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "To rollback:" | tee -a "$LOG_FILE"
    echo "pip install -r $BACKUP_DIR/requirements_before.txt --force-reinstall" | tee -a "$LOG_FILE"
fi

exit 0
