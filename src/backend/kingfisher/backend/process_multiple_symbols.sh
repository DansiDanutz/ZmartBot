#!/bin/bash

# KingFisher Batch Processing Script - LAMBORGHINI SPEED
# Process multiple symbols simultaneously for premium data sales

if [ $# -lt 1 ]; then
    echo "❌ Usage: $0 SYMBOL1 [SYMBOL2] [SYMBOL3] ..."
    echo "📝 Examples:"
    echo "   $0 BTCUSDT ETHUSDT XRPUSDT"
    echo "   $0 SOLUSDT INJUSDT ADAUSDT DOTUSDT"
    echo "   $0 AVAXUSDT BNBUSDT SUIUSDT ARBUSDT"
    exit 1
fi

echo "🚀 KingFisher Batch Processing - LAMBORGHINI SPEED"
echo "=================================================="
echo "🎯 Processing ${#} symbols simultaneously..."
echo "💎 Premium data for commercial sales"
echo ""

# Array to store background process IDs
pids=()

# Process each symbol in parallel
for symbol in "$@"; do
    echo "🔄 Starting $symbol processing..."
    
    # Generate unique image ID
    image_id="batch_${symbol}_$(date +%s)"
    
    # Determine sentiment based on symbol (for demo)
    case $symbol in
        BTC*|ETH*|SOL*)
            sentiment="bullish"
            significance="0.90"
            ;;
        XRP*|ADA*|DOT*)
            sentiment="neutral"
            significance="0.85"
            ;;
        *)
            sentiment="bullish"
            significance="0.88"
            ;;
    esac
    
    # Process symbol in background for parallel execution
    (
        start_time=$(date +%s)
        
        curl -s -X POST http://localhost:8100/api/v1/enhanced-analysis/process-kingfisher-image \
          -F "symbol=$symbol" \
          -F "image_id=$image_id" \
          -F "significance_score=$significance" \
          -F "market_sentiment=$sentiment" \
          -F "total_clusters=6" \
          -F "total_flow_area=3500" \
          -F "liquidation_map_image=@/dev/null" \
          -F "liquidation_heatmap_image=@/dev/null" > "/tmp/${symbol}_result.json"
        
        end_time=$(date +%s)
        processing_time=$((end_time - start_time))
        
        if [ $? -eq 0 ]; then
            echo "✅ $symbol processed in ${processing_time}s"
            
            # Extract key data for summary
            if command -v jq &> /dev/null; then
                price=$(jq -r '.analysis.current_price // "N/A"' "/tmp/${symbol}_result.json")
                record_id=$(jq -r '.storage.record_id // "N/A"' "/tmp/${symbol}_result.json")
                echo "   💰 Price: $price | 📊 Record: $record_id"
            fi
        else
            echo "❌ $symbol failed to process"
        fi
    ) &
    
    # Store the PID
    pids+=($!)
done

echo ""
echo "⏳ Waiting for all ${#pids[@]} symbols to complete..."
echo "🏎️  LAMBORGHINI SPEED PROCESSING IN PROGRESS..."

# Wait for all background processes
total_start=$(date +%s)
for pid in "${pids[@]}"; do
    wait $pid
done
total_end=$(date +%s)
total_time=$((total_end - total_start))

echo ""
echo "🎉 BATCH PROCESSING COMPLETE!"
echo "=================================================="
echo "⚡ Processed ${#} symbols in ${total_time} seconds"
echo "🚀 Average: $((total_time / ${#})) seconds per symbol"
echo "💎 Premium data ready for commercial sales"
echo ""

# Generate summary report
echo "📊 PROCESSING SUMMARY:"
echo "======================"
for symbol in "$@"; do
    if [ -f "/tmp/${symbol}_result.json" ]; then
        if command -v jq &> /dev/null; then
            success=$(jq -r '.success // false' "/tmp/${symbol}_result.json")
            if [ "$success" = "true" ]; then
                record_id=$(jq -r '.storage.record_id // "N/A"' "/tmp/${symbol}_result.json")
                price=$(jq -r '.analysis.current_price // "N/A"' "/tmp/${symbol}_result.json")
                sentiment=$(jq -r '.analysis.overall_sentiment // "N/A"' "/tmp/${symbol}_result.json")
                echo "✅ $symbol: Record $record_id | Price: $price | Sentiment: $sentiment"
            else
                echo "❌ $symbol: Processing failed"
            fi
        else
            echo "📝 $symbol: Result file created (install jq for detailed info)"
        fi
    else
        echo "❌ $symbol: No result file found"
    fi
done

echo ""
echo "📈 Check Airtable for all results!"
echo "💰 Premium trading intelligence ready for sales!"

# Cleanup temporary files
rm -f /tmp/*_result.json

echo ""
echo "🏁 Batch processing complete - LAMBORGHINI SPEED ACHIEVED!" 