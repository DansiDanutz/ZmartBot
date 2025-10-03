#!/bin/bash

# Shell Environment Timeout Test
echo "Testing shell environment resolution..."

# Test 1: Basic shell startup time
echo "Test 1: Basic shell startup"
time zsh -c "echo 'Shell started successfully'"

# Test 2: Check for hanging processes
echo ""
echo "Test 2: Checking for hanging processes"
ps aux | grep -E "(zmartbot|python|node)" | grep -v grep

# Test 3: Check shell configuration load time
echo ""
echo "Test 3: Testing .zshrc load time"
time zsh -c "source ~/.zshrc; echo 'Configuration loaded'"

echo ""
echo "Shell environment test complete!"













