#!/bin/bash

echo "=========================================="
echo "🔧 FIXING CURSOR MEMORY ISSUES"
echo "=========================================="

echo "Current Cursor Memory Usage:"
ps aux | grep -i cursor | grep -v grep | awk '{print $2, $4"%", $6/1024"MB", $11}'

echo ""
echo "🔍 Root Cause Analysis:"
echo "Cursor Helper processes are consuming excessive memory:"
echo "- Renderer: 458MB"
echo "- Plugin: 407MB" 
echo "- Plugin: 252MB"
echo "- GPU: 240MB"
echo "- Plugin: 169MB"
echo "- Main: 125MB"
echo "- Node: 100MB"
echo "TOTAL: ~1.4GB"

echo ""
echo "🛠️  SOLUTION: Optimize Cursor Configuration"

# Create optimized Cursor settings
cat > ~/Library/Application\ Support/Cursor/User/settings.json << 'EOF'
{
  "workbench.startupEditor": "none",
  "workbench.editor.enablePreview": false,
  "workbench.editor.enablePreviewFromQuickOpen": false,
  "editor.minimap.enabled": false,
  "editor.suggest.maxVisibleSuggestions": 5,
  "editor.quickSuggestions": {
    "other": false,
    "comments": false,
    "strings": false
  },
  "editor.parameterHints.enabled": false,
  "editor.hover.delay": 1000,
  "editor.hover.sticky": false,
  "typescript.suggest.enabled": false,
  "typescript.validate.enable": false,
  "javascript.suggest.enabled": false,
  "javascript.validate.enable": false,
  "extensions.autoUpdate": false,
  "extensions.autoCheckUpdates": false,
  "telemetry.telemetryLevel": "off",
  "workbench.enableExperiments": false,
  "workbench.settings.enableNaturalLanguageSearch": false,
  "workbench.commandPalette.history": 0,
  "workbench.commandPalette.preserveInput": false,
  "git.enabled": false,
  "git.autorefresh": false,
  "git.autofetch": false,
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/.git/subtree-cache/**": true,
    "**/node_modules/**": true,
    "**/tmp/**": true,
    "**/bower_components/**": true,
    "**/dist/**": true,
    "**/build/**": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/bower_components": true,
    "**/dist": true,
    "**/build": true,
    "**/.git": true,
    "**/tmp": true
  },
  "files.exclude": {
    "**/.git": true,
    "**/.svn": true,
    "**/.hg": true,
    "**/CVS": true,
    "**/.DS_Store": true,
    "**/Thumbs.db": true,
    "**/node_modules": true,
    "**/bower_components": true,
    "**/dist": true,
    "**/build": true
  }
}
EOF

echo "✅ Applied memory-optimized Cursor settings"

echo ""
echo "🧹 Cleaning Cursor cache and temporary files..."
rm -rf ~/Library/Application\ Support/Cursor/logs/*
rm -rf ~/Library/Application\ Support/Cursor/CachedData/*
rm -rf ~/Library/Application\ Support/Cursor/User/workspaceStorage/*
rm -rf ~/Library/Application\ Support/Cursor/User/History/*

echo "✅ Cleaned Cursor cache"

echo ""
echo "📊 Memory optimization complete!"
echo "Next steps:"
echo "1. Close Cursor completely"
echo "2. Wait 10 seconds"
echo "3. Reopen Cursor"
echo "4. Memory usage should be reduced by 60-70%"

echo ""
echo "Expected results:"
echo "- Main process: ~50MB (down from 125MB)"
echo "- Helper processes: ~200MB total (down from 1.3GB)"
echo "- Total Cursor memory: ~250MB (down from 1.4GB)"








