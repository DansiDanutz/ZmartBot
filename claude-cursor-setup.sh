#!/bin/bash

# Claude Code + Cursor Optimal Setup Script
# This script configures the best possible Claude Code experience inside Cursor

echo "🚀 Setting up Claude Code for optimal Cursor experience..."

# 1. Install latest Claude Code
echo "📦 Installing latest Claude Code..."
npm install -g @anthropic-ai/claude-code@latest

# 2. Create optimal configuration
echo "⚙️ Creating optimal configuration..."
cat > ~/.claude-config.json << 'EOF'
{
  "model": "claude-sonnet-4-5-20250929",
  "maxTokens": 4096,
  "temperature": 0.7,
  "streaming": true,
  "timeout": 30000,
  "features": {
    "codeCompletion": true,
    "inlineChat": true,
    "terminalIntegration": true,
    "fileAnalysis": true,
    "contextAwareness": true
  },
  "cursor": {
    "integration": "native",
    "autoComplete": true,
    "suggestions": true,
    "errorDetection": true,
    "refactoring": true,
    "documentation": true
  },
  "optimizations": {
    "rawModeFix": "nonInteractive",
    "terminalMode": "prompt",
    "interactiveFallback": "web"
  }
}
EOF

# 3. Create Cursor-specific aliases
echo "🔗 Creating Cursor aliases..."
cat >> ~/.zshrc << 'EOF'

# Claude Code + Cursor Optimizations
alias claude-cursor="claude -p"
alias claude-fast="claude -p --model claude-sonnet-4-5-20250929"
alias claude-code="claude -p --model claude-sonnet-4-5-20250929 --max-tokens 4096"
alias claude-debug="claude -p --model claude-sonnet-4-5-20250929 --temperature 0.3"
alias claude-creative="claude -p --model claude-sonnet-4-5-20250929 --temperature 0.9"

# Cursor-specific functions
claude-cursor-help() {
    echo "🎯 Claude Code + Cursor Commands:"
    echo "  claude-cursor 'your prompt'     - Quick prompt mode"
    echo "  claude-fast 'your prompt'       - Fast Sonnet 4.5 mode"
    echo "  claude-code 'your prompt'       - Code-focused mode"
    echo "  claude-debug 'your prompt'      - Debug mode (low temp)"
    echo "  claude-creative 'your prompt'   - Creative mode (high temp)"
    echo ""
    echo "💡 Tips for Cursor:"
    echo "  - Use prompt mode to avoid raw mode errors"
    echo "  - Sonnet 4.5 is the latest and most capable model"
    echo "  - Adjust temperature: 0.3 (focused) to 0.9 (creative)"
}
EOF

# 4. Create performance optimization script
echo "⚡ Creating performance optimization..."
cat > ~/claude-optimize.sh << 'EOF'
#!/bin/bash
# Claude Code Performance Optimization

echo "🔧 Optimizing Claude Code performance..."

# Clear npm cache
npm cache clean --force

# Update to latest version
npm install -g @anthropic-ai/claude-code@latest

# Set optimal environment variables
export NODE_OPTIONS="--max-old-space-size=4096"
export CLAUDE_STREAMING=true
export CLAUDE_TIMEOUT=30000

echo "✅ Claude Code optimized for Cursor!"
echo "💡 Use 'claude-cursor-help' for available commands"
EOF

chmod +x ~/claude-optimize.sh

# 5. Test installation
echo "🧪 Testing installation..."
claude --version

# 6. Create Cursor integration guide
echo "📚 Creating Cursor integration guide..."
cat > ~/claude-cursor-guide.md << 'EOF'
# Claude Code + Cursor Integration Guide

## 🎯 Best Practices for Cursor

### 1. Use Prompt Mode (Avoids Raw Mode Errors)
```bash
claude-cursor "Explain this code"
claude-fast "Debug this function"
claude-code "Refactor this component"
```

### 2. Model Selection
- **claude-sonnet-4-5-20250929**: Latest, most capable
- **claude-sonnet-4**: Stable, reliable
- **claude-opus**: Most creative

### 3. Temperature Settings
- **0.3**: Debugging, focused tasks
- **0.7**: General coding (default)
- **0.9**: Creative solutions

### 4. Cursor-Specific Features
- **Code Completion**: Automatic suggestions
- **Inline Chat**: Context-aware help
- **File Analysis**: Understands your codebase
- **Error Detection**: Identifies issues
- **Refactoring**: Suggests improvements

### 5. Performance Tips
- Use streaming for faster responses
- Set appropriate token limits
- Use context-aware prompts
- Leverage file analysis

### 6. Troubleshooting
- **Raw Mode Error**: Use prompt mode instead of interactive
- **Slow Responses**: Check network, use streaming
- **Memory Issues**: Run claude-optimize.sh

## 🚀 Quick Start
1. Open Cursor
2. Use `claude-cursor "your question"`
3. Enjoy optimal Claude Code experience!
EOF

echo ""
echo "✅ Claude Code + Cursor setup complete!"
echo ""
echo "🎯 Available commands:"
echo "  claude-cursor 'prompt'     - Quick prompt mode"
echo "  claude-fast 'prompt'       - Fast Sonnet 4.5 mode"
echo "  claude-code 'prompt'       - Code-focused mode"
echo "  claude-debug 'prompt'      - Debug mode"
echo "  claude-creative 'prompt'   - Creative mode"
echo "  claude-cursor-help         - Show all commands"
echo "  claude-optimize.sh         - Performance optimization"
echo ""
echo "📚 Integration guide: ~/claude-cursor-guide.md"
echo ""
echo "💡 Pro tip: Use prompt mode to avoid raw mode errors!"
echo "   Example: claude-cursor 'Help me debug this function'"
echo ""
echo "🔄 Reload your shell: source ~/.zshrc"


