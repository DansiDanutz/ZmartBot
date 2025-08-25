#!/bin/bash

# CONTINUOUS MONITORING SCRIPT
# Runs all 5 steps every 5 minutes for maximum accuracy

echo "========================================"
echo "KINGFISHER CONTINUOUS MONITORING SYSTEM"
echo "========================================"
echo ""
echo "This will run every 5 minutes:"
echo "1. Download new Telegram images"
echo "2. Sort images into categories"  
echo "3. Remove duplicates"
echo "4. Analyze with ChatGPT (professional reports)"
echo "5. Extract liquidation clusters & update Airtable"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"

while true; do
    echo ""
    echo "========================================" 
    echo "Starting new cycle at $(date '+%H:%M:%S')"
    echo "========================================"
    
    # STEP 1: Download from Telegram
    echo ""
    echo "[STEP 1] Downloading new images from Telegram..."
    python STEP1-Monitoring-Images-And-download.py
    
    # STEP 2: Sort images
    echo ""
    echo "[STEP 2] Sorting images with AI..."
    python STEP2-Sort-Images-With-AI.py
    
    # STEP 3: Remove duplicates
    echo ""
    echo "[STEP 3] Removing duplicate images..."
    python STEP3-Remove-Duplicates.py
    
    # STEP 4: Analyze and create reports
    echo ""
    echo "[STEP 4] Analyzing images with ChatGPT..."
    python STEP4-Analyze-And-Create-Reports.py
    
    # STEP 5: Extract clusters and update Airtable
    echo ""
    echo "[STEP 5] Extracting liquidation clusters..."
    python STEP5-Extract-Liquidation-Clusters.py --once
    
    echo ""
    echo "========================================"
    echo "✅ Cycle complete at $(date '+%H:%M:%S')"
    echo "⏰ Next cycle in 5 minutes..."
    echo "========================================"
    
    # Wait 5 minutes
    sleep 300
done