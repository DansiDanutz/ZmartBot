# King-Scripts - KingFisher Image Processing Pipeline

## Overview
Complete pipeline for monitoring, downloading, and categorizing KingFisher trading images from Telegram.

## Scripts

### STEP 1: Monitor and Download
**File:** `STEP1-Monitoring-Images-And-download.py`
- Connects to your Telegram account (@SemeCJ)
- Monitors for images from @thekingfisher_liqmap_bot
- Downloads all images to `downloads/` folder
- Numbers them sequentially: 1.jpg, 2.jpg, etc.

### STEP 2: Sort Images with AI
**File:** `STEP2-Sort-Images-With-AI.py`
- Uses OCR and OpenAI to analyze each image
- Correctly identifies:
  - **LiquidationMap**: Single symbol price charts
  - **LiquidationHeatmap**: Images with "HEATMAP" text
  - **ShortTermRatio**: Images with "OPTICAL_OPTI" text
  - **LongTermRatio**: Images with many symbols and "ALL_LEVERAGE"
- Sorts images into appropriate folders

### STEP 3: Remove Duplicates
**File:** `STEP3-Remove-Duplicates.py`
- Scans all folders for duplicate images
- Removes duplicates, keeping only unique images
- Uses MD5 hash comparison

## Usage

```bash
# Step 1: Download images from Telegram
python STEP1-Monitoring-Images-And-download.py

# Step 2: Sort images into categories
python STEP2-Sort-Images-With-AI.py

# Step 3: Remove any duplicates
python STEP3-Remove-Duplicates.py
```

## Folder Structure

```
downloads/
├── LiquidationMap/      # Single symbol liquidation charts
├── LiquidationHeatmap/  # Heatmap visualizations
├── ShortTermRatio/      # OPTICAL_OPTI ratio charts
└── LongTermRatio/       # Multi-symbol ALL_LEVERAGE charts
```

## Results from Testing
- Processed 21 images
- Removed 4 duplicates
- Final: 17 unique images correctly categorized

## Requirements
- Python 3.9+
- Telegram API credentials
- OpenAI API key (for better accuracy)
- Tesseract OCR installed (`brew install tesseract`)

## Dependencies
```bash
pip install telethon pillow pytesseract openai requests
```