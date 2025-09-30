# 🚀 Local AI Models Setup Guide for ZmartBot

This guide will help you install and configure DeepSeek-Coder, DeepSeek-R1-Distill, and Phi-3/Phi-4 models for enhanced trading analysis.

## 📋 Prerequisites

- macOS system
- Terminal access
- At least 8GB free disk space for models

## 🔧 Step 1: Install Ollama

### Option A: Manual Installation (Recommended)
1. **The Ollama.app is already downloaded to `/tmp/`**
2. **Install via Finder:**
   ```bash
   open /tmp/
   ```
   - Drag `Ollama.app` to your `Applications` folder

3. **Add Ollama to PATH:**
   ```bash
   echo 'export PATH="/Applications/Ollama.app/Contents/Resources:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

4. **Verify Installation:**
   ```bash
   ollama --version
   ```

### Option B: Homebrew Installation
```bash
brew install ollama
```

## 🤖 Step 2: Install AI Models

Once Ollama is installed, run our automated setup script:

```bash
cd /Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api
./setup_local_ai_models.sh
```

### Manual Model Installation (Alternative)

If the script doesn't work, install models manually:

```bash
# Start Ollama service
ollama serve &

# Install DeepSeek-Coder (6.7B parameters)
ollama pull deepseek-coder:6.7b

# Install DeepSeek-R1 (if available)
ollama pull deepseek-r1

# Install Phi-3 (3.8B parameters)
ollama pull phi3:3.8b

# Install Phi-3 14B (as Phi-4 alternative)
ollama pull phi3:14b

# List installed models
ollama list
```

## 🎯 Step 3: Model Capabilities

### DeepSeek-Coder
- **Purpose**: Structured data analysis and pattern recognition
- **Best for**: Technical indicator interpretation, time-series analysis
- **Size**: ~4GB
- **Speed**: Medium

### DeepSeek-R1-Distill
- **Purpose**: Fast reasoning and trend analysis
- **Best for**: Quick pattern detection, risk assessment
- **Size**: ~3GB
- **Speed**: Fast

### Phi-3 (3.8B)
- **Purpose**: Compact analysis and quick insights
- **Best for**: Trading signals, numeric pattern detection
- **Size**: ~2GB
- **Speed**: Very Fast

### Phi-3 14B (Phi-4 Alternative)
- **Purpose**: Enhanced reasoning and analysis
- **Best for**: Complex market analysis, better accuracy
- **Size**: ~8GB
- **Speed**: Medium

## 🧪 Step 4: Test Your Setup

Run the multi-model test to verify everything works:

```bash
python test_multi_model_system.py
```

Expected output should show all models as available:
```
Multi-Model AI Agent Status:
Available models: 5
  gpt-4o-mini: ✅ (cloud)
  deepseek-coder: ✅ (local)
  deepseek-r1-distill-llama: ✅ (local)
  phi-3: ✅ (local)
  phi-4: ✅ (local)
```

## 🔍 Step 5: Verify Integration

Test the complete system with a real analysis:

```bash
python -c "
import asyncio
from src.services.multi_model_ai_agent import MultiModelAIAgent

async def test():
    agent = MultiModelAIAgent()
    result = await agent.generate_comprehensive_analysis('ETH/USDT', use_all_models=True)
    print(f'Models used: {result[\"multi_model_analysis\"][\"models_used\"]}')
    print(f'Primary model: {result[\"multi_model_analysis\"][\"primary_model\"]}')

asyncio.run(test())
"
```

## ❗ Troubleshooting

### Ollama Not Found
```bash
# Check if Ollama is in Applications
ls /Applications/Ollama.app

# Add to PATH manually
export PATH="/Applications/Ollama.app/Contents/Resources:$PATH"
```

### Model Download Fails
```bash
# Check Ollama service is running
ps aux | grep ollama

# Restart Ollama service
pkill ollama
ollama serve &
```

### Permission Issues
```bash
# Fix permissions for Ollama
chmod +x /Applications/Ollama.app/Contents/Resources/ollama
```

### Disk Space Issues
```bash
# Check available space
df -h

# Remove unused models
ollama rm <model_name>
```

## 🚀 Performance Tips

1. **Model Selection Strategy:**
   - Use Phi-3 for quick analysis (< 30 seconds)
   - Use DeepSeek-Coder for detailed technical analysis
   - Use DeepSeek-R1 for fast trend detection
   - Use OpenAI GPT-4 Mini for comprehensive reports

2. **Resource Management:**
   - Local models use significant RAM (4-8GB per model)
   - Only load models when needed
   - Consider running one local model at a time

3. **Optimization:**
   - Keep Ollama service running for faster model loading
   - Use SSD storage for better performance
   - Close other applications when running multiple models

## 📊 Expected Benefits

After setup, your ZmartBot will have:

- **5 AI Models** instead of 1
- **Local Processing** for sensitive data
- **Faster Analysis** with model specialization
- **Redundancy** if cloud services fail
- **Cost Reduction** for high-volume analysis

## 🎉 Next Steps

Once all models are installed:

1. Test with different trading pairs
2. Compare analysis quality between models
3. Set up automated model selection based on analysis type
4. Monitor performance and resource usage

---

**Need Help?** 
- Check the logs: `tail -f ~/.ollama/logs/server.log`
- Verify models: `ollama list`
- Test connectivity: `ollama run phi3 "Hello"`