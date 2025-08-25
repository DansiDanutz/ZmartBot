#!/bin/bash

echo "============================================================"
echo "🤖 STARTING ADVANCED KINGFISHER MONITOR"
echo "============================================================"
echo ""
echo "Image Type Handling:"
echo "✅ Liquidation Map → Updates ONE symbol"
echo "✅ Liq Heatmap → Updates ONE symbol"
echo "✅ LiqRatio Long Term → Updates ALL symbols in image"
echo "✅ LiqRatio Short Term → Updates ALL symbols in image"
echo ""
echo "Features:"
echo "• Precise liquidation clusters (not rounded)"
echo "• Automatic timestamp tracking"
echo "• Smart image type detection"
echo "• Multi-symbol batch updates"
echo ""
echo "Press Ctrl+C to stop"
echo "============================================================"
echo ""

# Activate virtual environment if it exists
if [ -d "../../backend/zmart-api/venv" ]; then
    source ../../backend/zmart-api/venv/bin/activate
fi

# Run the advanced monitor
python3 advanced_kingfisher_monitor.py