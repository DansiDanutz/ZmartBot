#!/bin/bash
# cleanup_zmartbot.sh - Automated cleanup script for ZmartBot project

set -e

PROJECT_ROOT="/Users/dansidanutz/Desktop/ZmartBot"
ARCHIVE_DIR="$PROJECT_ROOT/archive/$(date +%Y%m%d_%H%M%S)"

echo "🧹 ZmartBot Cleanup Script"
echo "========================="
echo ""

# Create archive directory
mkdir -p "$ARCHIVE_DIR/logs"
mkdir -p "$ARCHIVE_DIR/databases"

# Archive large log files (>10MB)
echo "📦 Archiving large log files (>10MB)..."
ARCHIVED_COUNT=0
while IFS= read -r -d '' file; do
    echo "  Archiving: $file"
    mv "$file" "$ARCHIVE_DIR/logs/"
    ((ARCHIVED_COUNT++))
done < <(find "$PROJECT_ROOT" -name "*.log" -type f -size +10M -print0 2>/dev/null)

if [ $ARCHIVED_COUNT -eq 0 ]; then
    echo "  No large log files found"
else
    echo "  ✅ Archived $ARCHIVED_COUNT log file(s)"
fi

# Compress archived logs
if [ "$(ls -A $ARCHIVE_DIR/logs 2>/dev/null)" ]; then
    echo ""
    echo "🗜️  Compressing archived logs..."
    cd "$ARCHIVE_DIR/logs"
    for log in *.log; do
        if [ -f "$log" ]; then
            gzip "$log"
            echo "  Compressed: $log"
        fi
    done
fi

# Clean Python cache (if any)
echo ""
echo "🐍 Cleaning Python cache..."
PYCACHE_COUNT=$(find "$PROJECT_ROOT" -type d -name "__pycache__" 2>/dev/null | wc -l)
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
PYC_COUNT=$(find "$PROJECT_ROOT" -type f -name "*.pyc" 2>/dev/null | wc -l)
find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyo" -delete 2>/dev/null || true
echo "  Removed $PYCACHE_COUNT __pycache__ directories and $PYC_COUNT .pyc files"

# Clean Node.js cache (if any)
echo ""
echo "📦 Cleaning Node.js cache..."
find "$PROJECT_ROOT" -type d -name "node_modules/.cache" -exec rm -rf {} + 2>/dev/null || true
echo "  ✅ Node.js cache cleaned"

# Remove temporary files
echo ""
echo "🗑️  Removing temporary files..."
TMP_COUNT=$(find "$PROJECT_ROOT" -type f -name "*.tmp" 2>/dev/null | wc -l)
find "$PROJECT_ROOT" -type f -name "*.tmp" -delete 2>/dev/null || true
DS_COUNT=$(find "$PROJECT_ROOT" -type f -name ".DS_Store" 2>/dev/null | wc -l)
find "$PROJECT_ROOT" -type f -name ".DS_Store" -delete 2>/dev/null || true
echo "  Removed $TMP_COUNT .tmp files and $DS_COUNT .DS_Store files"

# Summary
echo ""
echo "✅ Cleanup Complete!"
echo "===================="
echo ""
echo "Archive location: $ARCHIVE_DIR"
echo ""
echo "📊 Current disk usage:"
du -sh "$PROJECT_ROOT"

if [ "$(ls -A $ARCHIVE_DIR/logs 2>/dev/null)" ]; then
    echo ""
    echo "🔍 Archived files:"
    ls -lh "$ARCHIVE_DIR/logs/" 2>/dev/null
else
    echo ""
    echo "No files were archived during this run."
    rm -rf "$ARCHIVE_DIR"
fi

echo ""
echo "✨ Done!"

exit 0
