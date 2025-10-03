#!/bin/bash

# Optimize Cursor & Claude Code Performance
# This script optimizes Cursor IDE and Claude integration

set -e

echo "🚀 Starting Cursor & Claude Optimization..."

# Clean cache directories
echo "📦 Cleaning cache directories..."
rm -rf ~/Library/Caches/Cursor/Cache/* 2>/dev/null || true
rm -rf ~/Library/Caches/Cursor/Code\ Cache/* 2>/dev/null || true
rm -rf ~/Library/Caches/Cursor/GPUCache/* 2>/dev/null || true
rm -rf ~/Library/Application\ Support/Cursor/CachedData/* 2>/dev/null || true
rm -rf ~/Library/Application\ Support/Cursor/logs/* 2>/dev/null || true

# Clean orphaned extensions
echo "🔧 Cleaning orphaned extensions..."
find ~/Library/Application\ Support/Cursor/extensions -type d -name ".obsolete" -exec rm -rf {} + 2>/dev/null || true

# Optimize SQLite databases
echo "💾 Optimizing SQLite databases..."
find ~/Library/Application\ Support/Cursor -name "*.db" -exec sqlite3 {} "VACUUM;" \; 2>/dev/null || true

# Set optimal memory limits
echo "⚙️  Setting optimal memory limits..."
defaults write com.todesktop.230313mzl4w4u92 JSCMemoryLimit -int 2048

# Enable GPU acceleration
echo "🎨 Enabling GPU acceleration..."
defaults write com.todesktop.230313mzl4w4u92 disableGPU -bool false

# Optimize file watchers
echo "👁  Optimizing file watchers..."
ulimit -n 10240 2>/dev/null || true

# Clean node_modules cache
echo "📦 Cleaning node_modules cache..."
find . -name "node_modules" -type d -prune -exec du -sh {} \; | sort -hr | head -5
echo "Consider cleaning large node_modules directories"

# Check and report memory usage
echo ""
echo "📊 Current System Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
top -l 1 | grep "PhysMem"
echo ""
ps aux | grep -E "(Cursor|claude)" | grep -v grep | awk '{printf "%-30s %6s %6s\n", $11, $3"%", $4"%"}' | head -10
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "✅ Optimization complete!"
echo ""
echo "💡 Additional recommendations:"
echo "   1. Restart Cursor for changes to take effect"
echo "   2. Limit open editor tabs to 10 or fewer"
echo "   3. Close unused terminal sessions"
echo "   4. Use workspace-specific settings when possible"
echo "   5. Monitor CPU/Memory usage with Activity Monitor"
echo ""
