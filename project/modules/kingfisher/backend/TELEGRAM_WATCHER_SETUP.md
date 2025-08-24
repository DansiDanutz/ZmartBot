# KingFisher Telegram Watcher Setup Guide

## Overview
The Telegram Watcher monitors KingFisher channels/bots for liquidation images using your personal Telegram account (via Telethon/MTProto). It automatically downloads images, identifies their type, extracts the symbol, and stores the data in the correct Airtable field.

## Key Features
✅ **Automatic Image Detection** - Monitors multiple Telegram chats/channels
✅ **Smart Image Classification** - Identifies liquidation maps, heatmaps, ratios, etc.
✅ **Symbol Extraction** - Automatically detects cryptocurrency symbols (BTC, ETH, SOL, etc.)
✅ **Correct Field Mapping** - Stores data in the right Airtable field based on image type
✅ **Backfill Support** - Can process recent historical messages

## Image Type → Airtable Field Mapping

| Image Type | Airtable Field | Description |
|------------|----------------|-------------|
| Liquidation Map | `Liquidation_Map` | Main liquidation cluster map |
| Liquidation Heatmap | `Liquidation_Heatmap` | Heatmap visualization |
| RSI Heatmap | `RSI_Heatmap` | RSI indicator heatmap |
| Long-term Ratios | `LiqRatios_long_term` | Long-term liquidation ratios |
| Short-term Ratios | `LiqRatios_short_term` | Short-term liquidation ratios |

## Setup Instructions

### 1. Environment Variables
Create or update `.env` file in `kingfisher-module/backend/`:

```bash
# Telegram API Credentials (from my.telegram.org)
TELEGRAM_API_ID=26706005
TELEGRAM_API_HASH=bab8e720fd3b045785a5ec44d5e399fe

# Channels/Bots to Monitor (comma-separated)
WATCH_CHATS=@thekingfisher_liqmap_bot,kingfisher_automation

# Airtable Configuration
AIRTABLE_BASE_ID=appAs9sZH7OmtYaTJ
AIRTABLE_TABLE_ID=tblWxTJClUcLS2E0J
AIRTABLE_API_KEY=patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835

# Optional Settings
BACKFILL_LIMIT=10  # Number of recent messages to process on startup
KINGFISHER_DOWNLOAD_DIR=downloads/kingfisher  # Where to save images
```

### 2. Install Dependencies

```bash
cd kingfisher-module/backend
pip install telethon pytesseract pillow httpx python-dotenv
```

### 3. Test Connection

```bash
# Test your Telegram connection and chat access
python test_telegram_watcher.py
```

This will:
- Verify your Telegram credentials
- Check access to watched chats
- Show recent image counts

### 4. Run the Watcher

#### Option A: Integrated Monitor (Recommended)
```bash
# Complete solution with all features
python integrated_kingfisher_monitor.py
```

#### Option B: Service-based Watcher
```bash
# Uses the service architecture
python start_telegram_watcher.py
```

#### Option C: Simple Universal Monitor
```bash
# Basic monitoring
python universal_kingfisher_monitor.py
```

## First-Time Setup

When you run the watcher for the first time:

1. **Phone Number**: Enter your phone number (with country code)
2. **Verification Code**: Enter the code sent to your Telegram app
3. **2FA Password**: If enabled, enter your 2FA password

A session file will be created (`*.session`) to remember your login.

## How It Works

### 1. Message Detection
```python
# Monitors new messages from watched chats
@client.on(events.NewMessage())
async def handler(event):
    if is_image_message(event.message):
        await process_image(event.message)
```

### 2. Image Analysis
```python
# Identifies image type from OCR and text
image_type = identify_image_type(ocr_text + message_text)
# Examples: "liquidation_map", "rsi_heatmap", "liqratio_longterm"
```

### 3. Symbol Extraction
```python
# Extracts cryptocurrency symbol
symbol = extract_symbol(text)  # Returns: "BTC", "ETH", "SOL", etc.
```

### 4. Field Mapping
```python
# Maps to correct Airtable field
field = get_airtable_field_mapping(image_type)
# "liquidation_map" → "Liquidation_Map"
# "rsi_heatmap" → "RSI_Heatmap"
```

### 5. Airtable Update
```python
# Updates the specific field for the symbol
await update_airtable(
    symbol="ETH",
    field_name="Liquidation_Map",
    data={...analysis_results...}
)
```

## Monitoring Multiple Chats

Add multiple chats in `.env`:
```bash
WATCH_CHATS=@thekingfisher_liqmap_bot,@another_channel,groupname
```

Supported formats:
- `@username` - Public channels/bots
- `groupname` - Private groups you're in
- `-100xxxxx` - Chat IDs

## Troubleshooting

### "Chat not found"
- Make sure you've joined the channel/group
- For bots, start a conversation first
- Use the test script to verify access

### "No images detected"
- Check if the chat actually has images
- Verify image detection with test script
- Check OCR installation: `tesseract --version`

### "Airtable update failed"
- Verify API key and base/table IDs
- Check field names match exactly
- Ensure symbol exists in table

### Session Issues
- Delete `*.session` files to reset
- Re-authenticate with phone number
- Check for Telegram bans/restrictions

## Running as a Service

### Linux/Mac (systemd)
Create `/etc/systemd/system/kingfisher-watcher.service`:

```ini
[Unit]
Description=KingFisher Telegram Watcher
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/kingfisher-module/backend
ExecStart=/usr/bin/python3 integrated_kingfisher_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable kingfisher-watcher
sudo systemctl start kingfisher-watcher
```

### Using Screen/Tmux
```bash
# With screen
screen -S kingfisher
python integrated_kingfisher_monitor.py
# Detach: Ctrl+A, D

# With tmux
tmux new -s kingfisher
python integrated_kingfisher_monitor.py
# Detach: Ctrl+B, D
```

## Advanced Features

### Custom Analysis
Modify `analyze_image()` in the monitor to add custom analysis:

```python
async def analyze_image(self, image_bytes, symbol, image_type):
    # Add your custom analysis here
    if image_type == "liquidation_map":
        # Extract specific liquidation levels
        levels = extract_liquidation_levels(image_bytes)
        return {"levels": levels, ...}
```

### Multi-Symbol Detection
For images with multiple symbols (ratios):

```python
def extract_multiple_symbols(text):
    symbols = []
    for symbol in ALL_SYMBOLS:
        if symbol in text:
            symbols.append(symbol)
    return symbols
```

### Real-time Notifications
Add notifications when high-significance images are detected:

```python
if analysis["significance_score"] > 0.8:
    await send_alert(f"High significance {image_type} for {symbol}")
```

## Support

For issues or questions:
1. Check the test script output
2. Review logs for error messages
3. Verify all credentials and IDs
4. Ensure Telegram account is active

---

**Ready to Monitor!** 🚀

Run `python integrated_kingfisher_monitor.py` to start watching for KingFisher images!