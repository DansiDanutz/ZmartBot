#!/usr/bin/env python3
"""
KingFisher Real Telegram Bot
Automatically processes images from @KingFisherAutomation channel
"""

import asyncio
import logging
import os
import sys
import json
import re
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from telegram import Update, Bot, Message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KingFisherRealTelegramBot:
    def __init__(self):
        # Telegram configuration
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '7995587461:AAELuQHeziFE4hZ1tlJ3d53-y5xQgeSoZHI')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '-1002891569616')
        self.channel_username = os.getenv('KINGFISHER_CHANNEL', '@KingFisherAutomation')
        
        # KingFisher API
        self.kingfisher_api_url = "http://localhost:8100"
        
        # Bot instance
        self.bot = None
        self.application = None
        
        # Message tracking
        self.last_processed_message_id = 0
        self.processed_messages = set()
        
        # Symbol detection patterns
        self.symbol_patterns = [
            r'([A-Z]{2,10}USDT)',  # BTCUSDT, ETHUSDT, etc.
            r'([A-Z]{2,10}/USDT)',  # BTC/USDT, ETH/USDT, etc.
            r'([A-Z]{2,10}-USDT)',  # BTC-USDT, ETH-USDT, etc.
        ]
        
        # Image type detection
        self.liquidation_patterns = [
            r'liquidation.*map',
            r'liquidation.*heatmap', 
            r'heatmap',
            r'cluster',
            r'toxic.*flow',
            r'order.*flow'
        ]
        
        logger.info("🚀 KingFisher Real Telegram Bot initialized")
        
    async def initialize_bot(self):
        """Initialize the Telegram bot"""
        try:
            self.bot = Bot(token=self.bot_token)
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("process", self.process_command))
            
            # Add message handlers
            self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
            self.application.add_handler(MessageHandler(filters.TEXT, self.handle_text))
            
            # Test bot connection
            bot_info = await self.bot.get_me()
            logger.info(f"✅ Bot connected: @{bot_info.username}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            return False
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🐟 **KingFisher Real Telegram Bot**\n\n"
            "I automatically process trading images from the KingFisher channel and generate professional analysis reports.\n\n"
            "**Commands:**\n"
            "• `/start` - Show this message\n"
            "• `/status` - Check system status\n"
            "• `/process` - Manually trigger processing\n\n"
            "**Features:**\n"
            "• Automatic image detection\n"
            "• Symbol extraction\n"
            "• Professional analysis reports\n"
            "• Airtable integration\n\n"
            "I'm monitoring the channel for new images! 📊"
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            # Check KingFisher API health
            response = requests.get(f"{self.kingfisher_api_url}/health", timeout=5)
            api_status = "✅ Online" if response.status_code == 200 else "❌ Offline"
            
            # Check Airtable connection
            airtable_response = requests.get(f"{self.kingfisher_api_url}/api/v1/airtable/status", timeout=5)
            airtable_status = "✅ Connected" if airtable_response.status_code == 200 else "❌ Disconnected"
            
            status_message = (
                f"🐟 **KingFisher Bot Status**\n\n"
                f"**API Health:** {api_status}\n"
                f"**Airtable:** {airtable_status}\n"
                f"**Channel:** {self.channel_username}\n"
                f"**Processed Messages:** {len(self.processed_messages)}\n"
                f"**Last Activity:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"Bot is ready to process images! 📊"
            )
            
            await update.message.reply_text(status_message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error checking status: {e}")
    
    async def process_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /process command - manually trigger processing"""
        await update.message.reply_text("🔄 Checking for new images in channel...")
        
        try:
            # Get recent messages from channel
            messages = await self.get_channel_messages(limit=10)
            
            if not messages:
                await update.message.reply_text("📭 No new messages found in channel")
                return
            
            processed_count = 0
            for message in messages:
                if await self.process_message(message):
                    processed_count += 1
            
            await update.message.reply_text(f"✅ Processed {processed_count} new messages")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error processing messages: {e}")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages"""
        try:
            message = update.message
            caption = message.caption or ""
            
            # Extract symbol from caption
            symbol = self.extract_symbol_from_text(caption)
            
            if not symbol:
                await message.reply_text("❌ No trading symbol detected in message")
                return
            
            # Download and process image
            await message.reply_text(f"🔄 Processing {symbol} image...")
            
            # Get the largest photo
            photo = message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            
            # Download image
            image_data = await file.download_as_bytearray()
            
            # Process with KingFisher API
            success = await self.process_image_with_api(symbol, image_data, caption)
            
            if success:
                await message.reply_text(f"✅ {symbol} analysis completed! Check Airtable for results.")
            else:
                await message.reply_text(f"❌ Failed to process {symbol} image")
                
        except Exception as e:
            logger.error(f"Error handling photo: {e}")
            await update.message.reply_text(f"❌ Error processing image: {e}")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        text = update.message.text
        
        # Check if it's a command
        if text.startswith('/'):
            return
        
        # Extract symbol from text
        symbol = self.extract_symbol_from_text(text)
        
        if symbol:
            await update.message.reply_text(f"📊 Detected symbol: {symbol}\nSend an image to analyze it!")
        else:
            await update.message.reply_text("💡 Send me trading images to analyze them automatically!")
    
    def extract_symbol_from_text(self, text: str) -> Optional[str]:
        """Extract trading symbol from text"""
        if not text:
            return None
        
        text_upper = text.upper()
        
        for pattern in self.symbol_patterns:
            matches = re.findall(pattern, text_upper)
            if matches:
                # Clean up the symbol
                symbol = matches[0].replace('/', '').replace('-', '')
                if len(symbol) >= 6:  # Minimum length for valid symbol
                    return symbol
        
        return None
    
    def is_liquidation_image(self, text: str) -> bool:
        """Check if text indicates liquidation analysis"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        for pattern in self.liquidation_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    async def get_channel_messages(self, limit: int = 20) -> List[Message]:
        """Get recent messages from the channel"""
        try:
            # Get updates from bot
            updates = await self.bot.get_updates(limit=limit)
            
            messages = []
            for update in updates:
                if update.message and update.message.chat.username == self.channel_username.replace('@', ''):
                    if update.message.message_id not in self.processed_messages:
                        messages.append(update.message)
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting channel messages: {e}")
            return []
    
    async def process_message(self, message: Message) -> bool:
        """Process a single message"""
        try:
            message_id = message.message_id
            
            # Skip if already processed
            if message_id in self.processed_messages:
                return False
            
            # Check if message has photo
            if not message.photo:
                return False
            
            # Extract symbol from caption
            caption = message.caption or ""
            symbol = self.extract_symbol_from_text(caption)
            
            if not symbol:
                logger.info(f"No symbol found in message {message_id}")
                return False
            
            # Download image
            photo = message.photo[-1]
            file = await self.bot.get_file(photo.file_id)
            image_data = await file.download_as_bytearray()
            
            # Process with API
            success = await self.process_image_with_api(symbol, image_data, caption)
            
            if success:
                self.processed_messages.add(message_id)
                self.last_processed_message_id = message_id
                logger.info(f"✅ Processed message {message_id} for {symbol}")
                return True
            else:
                logger.error(f"❌ Failed to process message {message_id} for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
    
    async def process_image_with_api(self, symbol: str, image_data: bytes, caption: str = "") -> bool:
        """Process image with KingFisher API"""
        try:
            # Prepare the API request
            files = {'image': ('image.jpg', image_data, 'image/jpeg')}
            data = {
                'symbol': symbol,
                'context': caption,
                'filename': f"{symbol}_liquidation_map.jpg"
            }
            
            # Call the complete workflow API
            response = requests.post(
                f"{self.kingfisher_api_url}/api/v1/complete-workflow/process-complete-workflow",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ API processed {symbol}: {result.get('status', 'success')}")
                return True
            else:
                logger.error(f"❌ API error for {symbol}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error calling API for {symbol}: {e}")
            return False
    
    async def monitor_channel_loop(self):
        """Continuous monitoring loop"""
        logger.info(f"🔍 Starting channel monitoring for {self.channel_username}")
        
        while True:
            try:
                # Get new messages
                messages = await self.get_channel_messages(limit=10)
                
                if messages:
                    logger.info(f"📥 Found {len(messages)} new messages")
                    
                    for message in messages:
                        await self.process_message(message)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def run(self):
        """Run the bot"""
        try:
            # Initialize bot
            if not await self.initialize_bot():
                logger.error("❌ Failed to initialize bot")
                return
            
            logger.info("🚀 Starting KingFisher Real Telegram Bot")
            
            # Start monitoring in background
            asyncio.create_task(self.monitor_channel_loop())
            
            # Start the bot
            await self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.error(f"Error running bot: {e}")

async def main():
    """Main function"""
    bot = KingFisherRealTelegramBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main()) 