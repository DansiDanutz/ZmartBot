#!/bin/bash

echo "🚀 ZmartBot Local AI Models Setup"
echo "=================================="

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed or not in PATH"
    echo "Please install Ollama first:"
    echo "1. Drag Ollama.app from /tmp/ to Applications folder"
    echo "2. Add to PATH: echo 'export PATH=\"/Applications/Ollama.app/Contents/Resources:\$PATH\"' >> ~/.zshrc"
    echo "3. Reload: source ~/.zshrc"
    exit 1
fi

echo "✅ Ollama found: $(which ollama)"

# Start Ollama service in background
echo "🔄 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!
sleep 5

# Install DeepSeek-Coder
echo "📥 Installing DeepSeek-Coder..."
ollama pull deepseek-coder:6.7b
if [ $? -eq 0 ]; then
    echo "✅ DeepSeek-Coder installed successfully"
else
    echo "❌ Failed to install DeepSeek-Coder"
fi

# Install DeepSeek-R1-Distill (Note: This might not be available, will try alternatives)
echo "📥 Installing DeepSeek-R1-Distill..."
ollama pull deepseek-r1-distill-llama || {
    echo "⚠️  DeepSeek-R1-Distill not available, trying deepseek-r1..."
    ollama pull deepseek-r1 || {
        echo "⚠️  DeepSeek-R1 not available, using deepseek-coder as fallback"
    }
}

# Install Phi-3
echo "📥 Installing Phi-3..."
ollama pull phi3:3.8b
if [ $? -eq 0 ]; then
    echo "✅ Phi-3 installed successfully"
else
    echo "❌ Failed to install Phi-3"
fi

# Install Phi-4 (Note: Phi-4 might not be available yet, will use latest)
echo "📥 Installing Phi-4..."
ollama pull phi3:14b || {
    echo "⚠️  Phi-4 not available, using Phi-3 14B as alternative"
}

# List installed models
echo ""
echo "📋 Installed Models:"
echo "==================="
ollama list

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Available models for ZmartBot:"
echo "- DeepSeek-Coder: For structured analysis and pattern recognition"
echo "- DeepSeek-R1: For fast reasoning and trend analysis"  
echo "- Phi-3: For compact analysis and quick insights"
echo "- Phi-3 14B: For enhanced reasoning (as Phi-4 alternative)"
echo ""
echo "Test your setup with:"
echo "  python test_multi_model_system.py"

# Kill the background Ollama service
kill $OLLAMA_PID 2>/dev/null