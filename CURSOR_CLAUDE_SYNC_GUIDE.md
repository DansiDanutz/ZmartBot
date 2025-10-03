# Cursor-Claude Sync System Guide

## 🎯 Overview

This system optimizes the collaboration between Claude and Cursor IDE by providing intelligent context management, project analysis, and optimization suggestions. It works with your existing Claude-in-Cursor setup without requiring any changes.

## 🚀 Quick Start

### 1. Start the Context Optimizer

```bash
# Start the optimizer (runs in background)
./start_cursor_optimizer.sh

# Check status
python3 cursor_claude_context_optimizer.py --status

# Get optimized context for Claude
python3 cursor_claude_context_optimizer.py --context
```

### 2. Use the Integration Helper

```bash
# Get project context
python3 cursor_claude_integration.py --context

# Get Claude-specific instructions
python3 cursor_claude_integration.py --instructions

# Get session information
python3 cursor_claude_integration.py --session
```

## 🔧 Features

### Context Optimization
- **Intelligent File Selection**: Automatically identifies the most relevant files for Claude's context
- **Token Management**: Optimizes context to stay within Claude's token limits
- **Project Intelligence**: Analyzes project structure, technologies, and patterns
- **Real-time Monitoring**: Continuously monitors project changes and updates context

### Project Analysis
- **Technology Detection**: Automatically detects Python, Node.js, React, Vue, etc.
- **Architecture Patterns**: Identifies MVC, component-based, service-layer patterns
- **Code Quality Metrics**: Analyzes complexity, maintainability, and performance
- **Optimization Suggestions**: Provides actionable recommendations

### ZmartBot Integration
- **Trading System Awareness**: Specialized understanding of cryptocurrency trading systems
- **API Integration Focus**: Optimizes for exchange APIs (Binance, KuCoin)
- **Risk Management**: Emphasizes security and risk considerations
- **Real-time Processing**: Optimizes for low-latency trading decisions

## 📊 Configuration

### Main Configuration File: `.cursor_claude_optimizer.yaml`

Key settings:

```yaml
# Analysis intervals
context_analysis_interval: 30  # seconds

# File limits
max_context_files: 50
max_file_size_kb: 1000

# Claude context limits
claude_context_limits:
  max_tokens: 200000
  optimal_tokens: 150000
  min_tokens: 50000

# Project-specific settings
project_settings:
  zmartbot:
    trading_apis: true
    crypto_analysis: true
    portfolio_management: true
```

## 🎯 Usage Examples

### For Claude in Cursor

1. **Get Project Context**:

   ```python
   from cursor_claude_integration import get_project_context
   context = get_project_context()
   print(context['project_info'])
   ```

2. **Get Optimization Suggestions**:

   ```python
   from cursor_claude_context_optimizer import CursorClaudeContextOptimizer
   optimizer = CursorClaudeContextOptimizer()
   suggestions = optimizer.get_optimized_context_for_claude()
   ```

3. **Monitor Project Changes**:

   ```python
   optimizer = CursorClaudeContextOptimizer()
   optimizer.start_monitoring()
   # Context automatically updates as you work
   ```

### For Development Workflow

1. **Start Development Session**:

   ```bash
   # Start ZmartBot system
   ./START_ZMARTBOT.sh

   # Start context optimizer
   ./start_cursor_optimizer.sh
   ```

2. **Check System Status**:

   ```bash
   # Check ZmartBot services
   curl http://localhost:8000/health

   # Check context optimizer
   python3 cursor_claude_context_optimizer.py --status
   ```

3. **Get Optimized Context**:

   ```bash
   # Get context for Claude
   python3 cursor_claude_context_optimizer.py --context --max-tokens 150000
   ```

## 🔍 Monitoring and Analytics

### Status Reports

```bash
# Get comprehensive status
python3 cursor_claude_context_optimizer.py --status

# Output example:
{
  "is_running": true,
  "project_type": "zmartbot_trading_system",
  "technologies": ["Python", "FastAPI", "React", "Docker"],
  "last_snapshot": "2025-01-09T10:30:00",
  "active_files_count": 15,
  "optimization_score": 0.85,
  "suggestions_count": 3
}
```

### Performance Metrics
- **Context Size**: Tracks token usage and optimization
- **File Activity**: Monitors recently modified files
- **Project Health**: Calculates maintainability and performance scores
- **Optimization Impact**: Measures improvement over time

## 🛠️ Advanced Features

### Machine Learning Patterns
- **Pattern Recognition**: Learns from your coding patterns
- **Predictive Optimization**: Anticipates context needs
- **Adaptive Suggestions**: Improves recommendations over time

### Integration Points
- **Git Integration**: Tracks changes and commits
- **File System Monitoring**: Real-time file change detection
- **Cursor IDE Integration**: Works seamlessly with Cursor's features

### Customization
- **Project-Specific Rules**: Tailored optimization for different project types
- **Technology-Specific Hints**: Specialized guidance for Python, Node.js, React, etc.
- **Team Preferences**: Configurable optimization strategies

## 🚨 Troubleshooting

### Common Issues

1. **Optimizer Not Starting**:

   ```bash
   # Check dependencies
   pip3 install pyyaml psutil watchdog aiofiles aiohttp

   # Check permissions
   chmod +x start_cursor_optimizer.sh
   ```

2. **Context Too Large**:

   ```bash
   # Reduce max tokens
   python3 cursor_claude_context_optimizer.py --context --max-tokens 100000

   # Check configuration
   cat .cursor_claude_optimizer.yaml
   ```

3. **Performance Issues**:

   ```bash
   # Check system resources
   python3 cursor_claude_context_optimizer.py --status

   # Adjust intervals in config
   # context_analysis_interval: 60  # Increase to reduce CPU usage
   ```

### Logs and Debugging

```bash
# View optimizer logs
tail -f cursor_claude_optimizer.log

# Check database
sqlite3 .cursor_claude_context.db "SELECT * FROM context_snapshots ORDER BY timestamp DESC LIMIT 5;"
```

## 🔄 Integration with ZmartBot

### Automatic Integration

The system automatically detects ZmartBot projects and applies specialized optimizations:

- **Trading API Focus**: Prioritizes exchange integration files
- **Risk Management**: Emphasizes security and risk-related code
- **Real-time Processing**: Optimizes for low-latency operations
- **Portfolio Management**: Highlights portfolio and position management code

### Manual Integration

```python
# In your ZmartBot services
from cursor_claude_integration import update_claude_session

# Update session when making trading decisions
update_claude_session('trading_decision', {
    'symbol': 'BTCUSDT',
    'action': 'buy',
    'amount': 0.1
})
```

## 📈 Best Practices

### For Claude in Cursor

1. **Use Context Optimization**: Always get optimized context before complex tasks
2. **Follow Project Patterns**: Adhere to existing code patterns and architecture
3. **Consider Performance**: Think about real-time trading requirements
4. **Security First**: Always consider security implications for trading operations

### For Development

1. **Regular Monitoring**: Check optimization status regularly
2. **Incremental Improvements**: Apply optimization suggestions gradually
3. **Documentation**: Keep project documentation up to date
4. **Testing**: Test changes in development environment first

## 🎯 Future Enhancements

### Planned Features
- **AI-Powered Code Generation**: Generate code based on project patterns
- **Automated Testing**: Suggest and generate test cases
- **Performance Profiling**: Identify and fix performance bottlenecks
- **Security Scanning**: Automated security vulnerability detection

### Integration Roadmap
- **IDE Plugins**: Direct Cursor IDE integration
- **Team Collaboration**: Multi-developer context sharing
- **Cloud Sync**: Cross-device context synchronization
- **Analytics Dashboard**: Web-based monitoring interface

## 📞 Support

### Getting Help

1. **Check Logs**: Review `cursor_claude_optimizer.log` for errors
2. **Status Reports**: Use `--status` flag to diagnose issues
3. **Configuration**: Verify `.cursor_claude_optimizer.yaml` settings
4. **Dependencies**: Ensure all required packages are installed

### Contributing
- **Bug Reports**: Report issues with detailed logs
- **Feature Requests**: Suggest new optimization features
- **Code Contributions**: Submit improvements and optimizations

---

**🎯 This system is designed to work seamlessly with your existing Claude-in-Cursor setup, providing intelligent context optimization without requiring any changes to your current workflow.**
