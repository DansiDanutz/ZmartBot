# 🚀 Starting Fresh KingFisher Monitor

## ✅ Airtable Cleared
The Airtable has been successfully cleared of all data. We're ready to start fresh!

## 📱 Running the Telegram Watcher

Since the Telegram watcher requires interactive authentication on first run, you need to run it manually:

### Step 1: Navigate to the directory
```bash
cd /Users/dansidanutz/Desktop/ZmartBot/kingfisher-module/backend
```

### Step 2: Run the integrated monitor
```bash
python integrated_kingfisher_monitor.py
```

### Step 3: First-time authentication
When you run it for the first time, you'll be prompted for:

1. **Phone number**: Enter your phone with country code (e.g., +1234567890)
2. **Verification code**: Check your Telegram app for the code
3. **2FA password** (if enabled): Enter your 2FA password

### Step 4: Monitor will start
After authentication, the monitor will:
- ✅ Connect to Telegram
- ✅ Start watching @thekingfisher_liqmap_bot
- ✅ Backfill last 10 messages (if any have images)
- ✅ Monitor for new images continuously

## 📊 What Happens When Images Are Detected

When a KingFisher image is posted:

1. **Download**: Image is downloaded automatically
2. **Identify**: System identifies the type (liquidation map, heatmap, etc.)
3. **Extract**: Symbol is extracted (BTC, ETH, SOL, etc.)
4. **Store**: Data is stored in the correct Airtable field:
   - `Liquidation_Map` for liquidation maps
   - `Liquidation_Heatmap` for heatmaps
   - `RSI_Heatmap` for RSI analysis
   - `LiqRatios_long_term` for long-term ratios
   - `LiqRatios_short_term` for short-term ratios

## 🎯 Quick Start Commands

```bash
# Option 1: Integrated Monitor (RECOMMENDED)
python integrated_kingfisher_monitor.py

# Option 2: Service-based watcher
python start_telegram_watcher.py

# Option 3: Simple monitor
python universal_kingfisher_monitor.py
```

## 📋 Checking Airtable

After the monitor processes some images, you can verify in Airtable:
1. Go to your Airtable base
2. Check the KingFisher table
3. You'll see records with symbols and data in the appropriate fields

## 🔄 Keep Running

To keep the monitor running continuously:

### Using Screen (Recommended)
```bash
screen -S kingfisher
python integrated_kingfisher_monitor.py
# Press Ctrl+A, then D to detach
# To reattach: screen -r kingfisher
```

### Using tmux
```bash
tmux new -s kingfisher
python integrated_kingfisher_monitor.py
# Press Ctrl+B, then D to detach
# To reattach: tmux attach -t kingfisher
```

### Using nohup
```bash
nohup python integrated_kingfisher_monitor.py > kingfisher.log 2>&1 &
# Check logs: tail -f kingfisher.log
```

## 📝 Monitor Output

You'll see output like:
```
🚀 INTEGRATED KINGFISHER MONITOR
👀 Watching: ['@thekingfisher_liqmap_bot']
📊 Auto-detecting image types
🎯 Mapping to correct Airtable fields
✅ Connected to Telegram
📜 Backfilling last 10 messages...
✅ Monitor running. Press Ctrl+C to stop.

[When image detected:]
📥 Processing image from @thekingfisher_liqmap_bot
🎯 Identified: liquidation_map for ETH
📋 Mapping liquidation_map -> Liquidation_Map
✅ Updated Airtable: ETH -> Liquidation_Map
💾 Saved: downloads/kingfisher/ETH_liquidation_map_20250108_143022.jpg
```

## 🛑 To Stop

Press `Ctrl+C` to stop the monitor gracefully.

---

**Ready to start!** Run `python integrated_kingfisher_monitor.py` in your terminal.