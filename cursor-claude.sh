#!/bin/bash

# Cursor-optimized Claude Code launcher
# This script provides the best Claude experience inside Cursor without authentication issues

# Set optimal environment for Cursor
export CLAUDE_NO_INTERACTIVE=1
export FORCE_COLOR=0
export TERM=xterm-256color
export NODE_NO_WARNINGS=1

# Function to run Claude with proper error handling
run_claude() {
    local prompt="$1"
    echo "🤖 Claude Code (Sonnet 4.5) - Ready to help with ZmartBot!"
    echo "📝 Processing: $prompt"
    echo "----------------------------------------"
    
    claude -p "$prompt" 2>/dev/null || {
        echo "⚠️  Fallback mode activated..."
        claude --model claude-sonnet-4-5-20250929 -p "$prompt"
    }
}

# Check if prompt is provided
if [ $# -eq 0 ]; then
    echo "🎯 Cursor Claude Code Helper"
    echo "Usage: $0 'your prompt here'"
    echo ""
    echo "Examples:"
    echo "  $0 'Help me optimize my trading algorithm'"
    echo "  $0 'Review my API endpoints for security'"
    echo "  $0 'Debug the authentication system'"
    echo "  $0 'Analyze the ZmartBot architecture'"
    exit 1
fi

# Run Claude with the provided prompt
run_claude "$1"


