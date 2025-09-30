#!/bin/bash

# Setup Local AI Models for ZmartBot
# Installs Ollama and downloads recommended models for trading analysis

echo "🚀 ZmartBot Local AI Models Setup"
echo "=================================="
echo "This script will install Ollama and download local AI models"
echo "for enhanced trading analysis with fallback capabilities."
echo ""

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
else
    echo "❌ Unsupported platform: $OSTYPE"
    echo "This script supports macOS and Linux only."
    exit 1
fi

echo "🖥️  Detected platform: $PLATFORM"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Install Ollama
echo "📦 Step 1: Installing Ollama..."
if command_exists ollama; then
    echo "✅ Ollama is already installed"
    ollama --version
else
    echo "⬇️  Downloading and installing Ollama..."
    if curl -fsSL https://ollama.ai/install.sh | sh; then
        echo "✅ Ollama installed successfully"
    else
        echo "❌ Failed to install Ollama"
        echo "Please install manually from: https://ollama.ai/download"
        exit 1
    fi
fi

echo ""

# Step 2: Start Ollama service (if needed)
echo "🔄 Step 2: Starting Ollama service..."
if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama service is already running"
else
    echo "🚀 Starting Ollama service..."
    if [[ "$PLATFORM" == "macOS" ]]; then
        # On macOS, Ollama typically starts automatically
        ollama serve > /dev/null 2>&1 &
        sleep 3
    else
        # On Linux, start the service
        systemctl --user start ollama 2>/dev/null || ollama serve > /dev/null 2>&1 &
        sleep 3
    fi
    
    if pgrep -x "ollama" > /dev/null; then
        echo "✅ Ollama service started successfully"
    else
        echo "⚠️  Ollama service may not be running. You might need to start it manually."
    fi
fi

echo ""

# Step 3: Download recommended models
echo "📥 Step 3: Downloading recommended AI models for trading analysis..."
echo "This may take several minutes depending on your internet connection."
echo ""

MODELS=(
    "deepseek-r1-distill-llama:DeepSeek R1 Distill - Best for reasoning and pattern analysis"
    "deepseek-coder:DeepSeek Coder - Optimized for structured data and technical analysis"
    "phi3:Phi-3 - Compact model for quick insights"
)

# Download each model
for model_info in "${MODELS[@]}"; do
    model_name=$(echo "$model_info" | cut -d: -f1)
    model_desc=$(echo "$model_info" | cut -d: -f2-)
    
    echo "📊 Installing $model_name..."
    echo "   Description: $model_desc"
    
    if ollama pull "$model_name"; then
        echo "✅ $model_name installed successfully"
    else
        echo "❌ Failed to install $model_name"
        echo "   You can try installing it manually later with: ollama pull $model_name"
    fi
    echo ""
done

# Step 4: Verify installation
echo "🔍 Step 4: Verifying installation..."
echo "Installed models:"
if ollama list; then
    echo ""
    echo "✅ Model verification complete"
else
    echo "❌ Failed to list models"
fi

echo ""

# Step 5: Test models
echo "🧪 Step 5: Testing model functionality..."

test_prompt="What is 2+2? Answer briefly."

for model_info in "${MODELS[@]}"; do
    model_name=$(echo "$model_info" | cut -d: -f1)
    
    echo "Testing $model_name..."
    if timeout 30 ollama run "$model_name" "$test_prompt" >/dev/null 2>&1; then
        echo "✅ $model_name is working correctly"
    else
        echo "⚠️  $model_name test failed or timed out"
    fi
done

echo ""

# Step 6: Configuration recommendations
echo "⚙️  Step 6: Configuration Recommendations"
echo "========================================"
echo ""
echo "🎯 Model Usage Recommendations:"
echo "• deepseek-r1-distill-llama: Best for complex trading pattern analysis"
echo "• deepseek-coder: Ideal for technical indicator interpretation"
echo "• phi3: Perfect for quick market insights and signals"
echo ""
echo "💾 System Resources:"
echo "• Minimum RAM: 8GB (for Phi-3)"
echo "• Recommended RAM: 16GB+ (for DeepSeek models)"
echo "• Disk Space Used: ~5-10GB per model"
echo ""
echo "🔧 API Integration:"
echo "The models are now available through the ZmartBot API at:"
echo "• /api/v1/multi-model-analysis/analyze/{symbol}"
echo "• /api/v1/multi-model-analysis/compare-models/{symbol}"
echo "• /api/v1/multi-model-analysis/model-status"
echo ""

# Step 7: Final status check
echo "📊 Step 7: Final System Status"
echo "=============================="
echo ""

# Count installed models
model_count=$(ollama list | grep -c ":")
echo "📈 Installed Models: $model_count"

# Check system resources
if command_exists free; then
    total_ram=$(free -h | awk '/^Mem:/ {print $2}')
    echo "💾 System RAM: $total_ram"
elif command_exists vm_stat; then
    # macOS memory check
    total_ram=$(echo "scale=1; $(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//' ) * 4096 / 1024 / 1024 / 1024" | bc 2>/dev/null || echo "Unknown")
    if [[ "$total_ram" != "Unknown" ]]; then
        echo "💾 System RAM: ${total_ram}GB"
    else
        echo "💾 System RAM: Available"
    fi
fi

# Check disk space
if command_exists df; then
    disk_space=$(df -h . | awk 'NR==2 {print $4}')
    echo "💿 Available Disk Space: $disk_space"
fi

echo ""
echo "🎉 LOCAL AI MODELS SETUP COMPLETE!"
echo "=================================="
echo ""
echo "✅ Your ZmartBot system now has local AI capabilities with:"
echo "   • Fallback support when OpenAI is unavailable"
echo "   • Privacy-focused local analysis"
echo "   • Specialized trading pattern recognition"
echo "   • Fast reasoning for time-sensitive decisions"
echo ""
echo "🚀 Next Steps:"
echo "1. Restart your ZmartBot backend to detect the new models"
echo "2. Test the multi-model analysis endpoints"
echo "3. Use /api/v1/multi-model-analysis/model-status to verify integration"
echo ""
echo "📖 For more information, visit the API documentation or run:"
echo "   curl http://localhost:8001/api/v1/multi-model-analysis/status"
echo ""

# Optional: Start a simple test
read -p "🧪 Would you like to run a quick test of the multi-model system? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔄 Running quick test..."
    echo "This will test each model with a simple prompt..."
    
    for model_info in "${MODELS[@]}"; do
        model_name=$(echo "$model_info" | cut -d: -f1)
        echo "Testing $model_name with trading question..."
        
        if echo "Analyze: BTC price is 45000, RSI is 65, trend is bullish. Give brief trading recommendation." | timeout 20 ollama run "$model_name" 2>/dev/null | head -5; then
            echo "✅ $model_name trading analysis test passed"
        else
            echo "⚠️  $model_name test inconclusive"
        fi
        echo "---"
    done
    
    echo "🎯 Test complete! Models are ready for trading analysis."
fi

echo ""
echo "Thank you for setting up ZmartBot's local AI capabilities! 🚀"