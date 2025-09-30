#!/usr/bin/env python3
"""
KingFisher Telegram Monitor
Real Telegram integration with python-telegram-bot
"""

import asyncio
import httpx
import logging
import time
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import settings

# Telegram bot imports
try:
    from telegram import Update, Bot
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️  python-telegram-bot not installed. Install with: pip install python-telegram-bot")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramImageMonitor:
    def __init__(self):
        self.base_url = "http://localhost:8100"
        self.last_message_id = 0
        self.processed_messages = set()
        self.monitoring_active = True
        
        # Telegram configuration
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID', '')
        self.bot = None
        self.application = None
        
        # Telegram channel patterns
        self.symbol_pattern = r'([A-Z]{2,10}USDT)'
        self.image_patterns = [
            r'liquidation.*map',
            r'liquidation.*heatmap',
            r'heatmap',
            r'cluster'
        ]
        
    async def initialize_telegram_bot(self):
        """Initialize Telegram bot if credentials are available"""
        if not TELEGRAM_AVAILABLE:
            logger.warning("⚠️  python-telegram-bot not available - using mock mode")
            return False
            
        if not self.bot_token:
            logger.warning("⚠️  TELEGRAM_BOT_TOKEN not set - using mock mode")
            return False
            
        try:
            self.bot = Bot(token=self.bot_token)
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
            self.application.add_handler(MessageHandler(filters.TEXT, self.handle_text))
            
            logger.info("✅ Telegram bot initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Telegram bot: {e}")
            return False
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🐟 KingFisher Image Processor Bot\n\n"
            "I automatically analyze trading images and generate professional reports.\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/status - Check system status\n\n"
            "Just send me trading images and I'll process them automatically!"
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        server_healthy = await self.check_server_health()
        airtable_connected = await self.check_airtable_connection()
        
        status_text = "🐟 KingFisher Status:\n\n"
        status_text += f"✅ Server: {'Healthy' if server_healthy else 'Unhealthy'}\n"
        status_text += f"📊 Airtable: {'Connected' if airtable_connected else 'Disconnected'}\n"
        status_text += f"🕒 Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        await update.message.reply_text(status_text)
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming photos"""
        try:
            message = update.message
            caption = message.caption or ""
            
            # Extract symbol from caption
            symbol = self.extract_symbol_from_text(caption)
            if not symbol:
                await message.reply_text("❌ No trading symbol found in message. Please include symbol (e.g., BTCUSDT)")
                return
            
            # Check if it's a liquidation image
            if not self.is_liquidation_image(caption):
                await message.reply_text("⚠️  Image doesn't appear to be a liquidation analysis. Processing anyway...")
            
            # Download and process image
            photo = message.photo[-1]  # Get highest quality
            file = await context.bot.get_file(photo.file_id)
            
            # Download image
            image_data = await file.download_as_bytearray()
            
            # Process with KingFisher
            success = await self.process_telegram_image(symbol, caption, image_data)
            
            if success:
                await message.reply_text(f"✅ Processed {symbol} successfully! Check Airtable for results.")
            else:
                await message.reply_text(f"❌ Failed to process {symbol}. Check server logs.")
                
        except Exception as e:
            logger.error(f"❌ Error processing photo: {e}")
            await update.message.reply_text(f"❌ Error processing image: {str(e)}")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        text = update.message.text
        symbol = self.extract_symbol_from_text(text)
        
        if symbol:
            await update.message.reply_text(f"📊 Found symbol: {symbol}\n\nSend me a liquidation image for {symbol} to process!")
        else:
            await update.message.reply_text("💡 Tip: Include trading symbols like BTCUSDT in your messages for better processing!")
    
    async def check_server_health(self) -> bool:
        """Check if KingFisher server is running"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Server healthy: {data.get('status', 'unknown')}")
                    return True
                else:
                    logger.error(f"❌ Server unhealthy: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to server: {e}")
            return False
    
    async def check_airtable_connection(self) -> bool:
        """Check Airtable connection status"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/v1/airtable/status")
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    logger.info(f"📊 Airtable status: {status}")
                    return status == 'connected'
                else:
                    logger.error(f"❌ Airtable connection failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Cannot check Airtable: {e}")
            return False
    
    def extract_symbol_from_text(self, text: str) -> Optional[str]:
        """Extract trading symbol from text"""
        if not text:
            return None
            
        # Look for XXXUSDT pattern
        match = re.search(self.symbol_pattern, text.upper())
        if match:
            return match.group(1)
        
        return None
    
    def is_liquidation_image(self, text: str) -> bool:
        """Check if text indicates liquidation image"""
        if not text:
            return False
            
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self.image_patterns)
    
    async def process_telegram_image(self, symbol: str, message_text: str = "", image_data: bytes = None) -> bool:
        """Process image from Telegram"""
        try:
            # Prepare data for KingFisher API
            data = {
                "symbol": symbol,
                "image_id": f"telegram_{symbol}_{int(time.time())}",
                "significance_score": 0.85,
                "market_sentiment": "neutral"
            }
            
            # Extract sentiment from message
            if "bullish" in message_text.lower():
                data["market_sentiment"] = "bullish"
            elif "bearish" in message_text.lower():
                data["market_sentiment"] = "bearish"
            
            # Send to KingFisher API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/enhanced-analysis/process-kingfisher-image",
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Processed {symbol}: {result.get('message', 'Success')}")
                    return True
                else:
                    logger.error(f"❌ Failed to process {symbol}: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error processing {symbol}: {e}")
            return False
    
    async def check_real_telegram_messages(self) -> List[Tuple[str, str]]:
        """Check for real Telegram messages (placeholder for polling)"""
        # This would implement actual Telegram API polling
        # For now, return empty list - no mock messages
        return []
    
    async def monitor_telegram_loop(self):
        """Main monitoring loop"""
        logger.info("🔄 Starting Telegram monitoring loop...")
        
        while self.monitoring_active:
            try:
                # Check server health
                if not await self.check_server_health():
                    logger.warning("⚠️  Server not healthy, waiting 30 seconds...")
                    await asyncio.sleep(30)
                    continue
                
                # Check Airtable connection
                if not await self.check_airtable_connection():
                    logger.warning("⚠️  Airtable not connected, waiting 30 seconds...")
                    await asyncio.sleep(30)
                    continue
                
                logger.info("✅ All systems healthy - monitoring active")
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def run_continuous_monitoring(self):
        """Run continuous monitoring with Telegram bot"""
        logger.info("🚀 Starting KingFisher Telegram Monitor")
        
        # Initialize Telegram bot
        bot_initialized = await self.initialize_telegram_bot()
        
        if bot_initialized:
            # Start bot polling
            logger.info("🤖 Starting Telegram bot polling...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            # Run monitoring loop
            await self.monitor_telegram_loop()
        else:
            # Fallback to basic monitoring
            logger.info("📡 Running in basic monitoring mode")
            await self.monitor_telegram_loop()

async def main():
    """Main function"""
    monitor = TelegramImageMonitor()
    await monitor.run_continuous_monitoring()

if __name__ == "__main__":
    asyncio.run(main()) 