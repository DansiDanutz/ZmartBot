#!/bin/bash

# KingFisher Symbol Processing Script
# Usage: ./process_symbol.sh SYMBOL [SENTIMENT] [SIGNIFICANCE_SCORE]

if [ $# -lt 1 ]; then
    echo "❌ Usage: $0 SYMBOL [SENTIMENT] [SIGNIFICANCE_SCORE]"
    echo "📝 Examples:"
    echo "   $0 XRPUSDT"
    echo "   $0 BTCUSDT bullish"
    echo "   $0 ETHUSDT bearish 0.90"
    exit 1
fi

SYMBOL=$1
SENTIMENT=${2:-"neutral"}
SIGNIFICANCE_SCORE=${3:-"0.85"}

echo "🚀 Processing $SYMBOL..."
echo "📊 Sentiment: $SENTIMENT"
echo "⭐ Significance: $SIGNIFICANCE_SCORE"
echo ""

# Generate unique image ID
IMAGE_ID="real_${SYMBOL}_$(date +%s)"

# Process the symbol
curl -X POST http://localhost:8100/api/v1/enhanced-analysis/process-kingfisher-image \
  -F "symbol=$SYMBOL" \
  -F "image_id=$IMAGE_ID" \
  -F "significance_score=$SIGNIFICANCE_SCORE" \
  -F "market_sentiment=$SENTIMENT" \
  -F "total_clusters=6" \
  -F "total_flow_area=3500" \
  -F "liquidation_map_image=@/dev/null" \
  -F "liquidation_heatmap_image=@/dev/null"

echo ""
echo "✅ $SYMBOL processing complete!"
echo "📊 Check Airtable for results" 