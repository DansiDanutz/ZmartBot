#!/bin/bash

# Claude Code without authentication issues
# This script bypasses the interactive authentication and typing problems

echo "🚀 Starting Claude Code without authentication issues..."

# Set environment variables to prevent interactive mode
export CLAUDE_NO_INTERACTIVE=1
export FORCE_COLOR=0
export TERM=xterm-256color

# Use non-interactive mode to avoid typing issues
if [ $# -eq 0 ]; then
    echo "Usage: $0 'your prompt here'"
    echo "Example: $0 'Help me with my ZmartBot project'"
    exit 1
fi

# Run Claude with the provided prompt
claude -p "$1"


