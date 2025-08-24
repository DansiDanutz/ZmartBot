#!/usr/bin/env python3
"""
Telegram Watcher Service for KingFisher
Uses Telethon (MTProto) to monitor channels/chats as a user account
Watches for images, downloads them, and processes through KingFisher pipeline
"""

import os
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import re

from telethon import TelegramClient, events
from telethon.tl.types import Message
from dotenv import load_dotenv

from src.services.image_processing_service import ImageProcessingService
from src.services.airtable_service import AirtableService

load_dotenv()

logger = logging.getLogger(__name__)

class TelegramWatcherService:
    """Service for watching Telegram channels using user account (Telethon)"""
    
    def __init__(self):
        # Telegram credentials
        self.api_id = int(os.getenv("TELEGRAM_API_ID", "26706005"))
        self.api_hash = os.getenv("TELEGRAM_API_HASH", "bab8e720fd3b045785a5ec44d5e399fe")
        
        # Watch configuration
        watch_chats_raw = os.getenv("WATCH_CHATS", "@thekingfisher_liqmap_bot")
        self.watch_chats: List[str] = [c.strip() for c in watch_chats_raw.split(",") if c.strip()]
        
        # Download directory
        self.download_dir = Path(os.getenv("KINGFISHER_DOWNLOAD_DIR", "kingfisher-module/backend/downloads"))
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Services
        self.image_processor = ImageProcessingService()
        self.airtable_service = AirtableService()
        
        # Telethon client
        session_path = "kingfisher-module/backend/kingfisher_watcher.session"
        self.client = TelegramClient(session_path, self.api_id, self.api_hash)
        
        # State
        self.is_running = False
        self.processed_messages = set()  # Track processed message IDs
        
        # Backfill settings
        self.backfill_limit = int(os.getenv("BACKFILL_LIMIT", "10"))
        
        logger.info(f"Initialized TelegramWatcherService - Watching: {self.watch_chats}")
    
    def is_image_message(self, msg: Message) -> bool:
        """Check if message contains an image"""
        if msg.photo:
            return True
        if msg.document and msg.document.mime_type:
            mime_type = msg.document.mime_type.lower()
            return any(mime_type.startswith(mt) for mt in ["image/jpeg", "image/png", "image/webp", "image/jpg", "image/gif"])
        return False
    
    def extract_symbol_from_text(self, text: str) -> Optional[str]:
        """Extract cryptocurrency symbol from text"""
        if not text:
            return None
        
        # Common crypto symbols
        symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'DOT', 'PENGU', 
                  'AVAX', 'LINK', 'LTC', 'BNB', 'MATIC', 'UNI', 'ATOM', 'FIL']
        
        text_upper = text.upper()
        for symbol in symbols:
            if re.search(f"\\b{symbol}\\b", text_upper):
                return symbol
        
        return None
    
    def identify_image_type(self, text: str, ocr_text: str = "") -> str:
        """Identify the type of KingFisher image"""
        full_text = (text + " " + ocr_text).upper()
        
        # Check for specific image types
        if "LIQUIDATION MAP" in full_text or "LIQ MAP" in full_text:
            return "liquidation_map"
        elif "HEATMAP" in full_text or "HEAT MAP" in full_text:
            if "RSI" in full_text:
                return "rsi_heatmap"
            else:
                return "liquidation_heatmap"
        elif "LONG TERM" in full_text or "LONGTERM" in full_text:
            return "liqratio_longterm"
        elif "SHORT TERM" in full_text or "SHORTTERM" in full_text:
            return "liqratio_shortterm"
        elif "LIQUIDATION" in full_text and "RATIO" in full_text:
            return "liquidation_ratio"
        else:
            # Default to liquidation map
            return "liquidation_map"
    
    def get_airtable_field_for_image_type(self, image_type: str) -> str:
        """Map image type to correct Airtable field"""
        field_mapping = {
            "liquidation_map": "Liquidation_Map",
            "liquidation_heatmap": "Liquidation_Heatmap",
            "liqratio_longterm": "LiqRatios_long_term",
            "liqratio_shortterm": "LiqRatios_short_term",
            "rsi_heatmap": "RSI_Heatmap",
            "liquidation_ratio": "Liquidation_Ratio"
        }
        return field_mapping.get(image_type, "Liquidation_Map")
    
    async def download_and_process(self, event_msg: Message):
        """Download and process image from message"""
        try:
            # Skip if already processed
            if event_msg.id in self.processed_messages:
                return
            
            # Get chat info
            chat = await event_msg.get_chat()
            chat_label = getattr(chat, "username", None) or getattr(chat, "title", None) or str(getattr(chat, "id", "unknown"))
            
            # Create safe directory name
            safe_chat_name = "".join(c if c.isalnum() or c in ("-", "_", "@") else "_" for c in str(chat_label))
            chat_dir = self.download_dir / safe_chat_name
            chat_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            ts = datetime.fromtimestamp(event_msg.date.timestamp())
            ts_str = ts.strftime("%Y%m%d_%H%M%S")
            base_filename = f"{ts_str}_msg{event_msg.id}"
            
            # Download image
            logger.info(f"📥 Downloading image from {chat_label} - Message ID: {event_msg.id}")
            filepath = await event_msg.download_media(file=str(chat_dir / base_filename))
            
            if filepath:
                logger.info(f"✅ Downloaded: {filepath}")
                
                # Extract symbol from message text
                message_text = event_msg.text or ""
                symbol = self.extract_symbol_from_text(message_text)
                
                if not symbol:
                    # Try to extract from caption if it's a photo
                    if hasattr(event_msg, 'message') and event_msg.message:
                        symbol = self.extract_symbol_from_text(event_msg.message)
                    
                    # Default to ETH if no symbol found
                    if not symbol:
                        symbol = "ETH"
                        logger.info(f"⚠️ No symbol found in message, defaulting to {symbol}")
                else:
                    logger.info(f"📊 Detected symbol: {symbol}")
                
                # Identify image type
                image_type = self.identify_image_type(message_text)
                logger.info(f"🎯 Identified image type: {image_type}")
                
                # Process image through KingFisher pipeline
                analysis_result = await self.process_kingfisher_image(
                    filepath=filepath,
                    symbol=symbol,
                    image_type=image_type,
                    message_text=message_text
                )
                
                if analysis_result:
                    logger.info(f"✅ Successfully processed {symbol} {image_type}")
                    
                    # Store in Airtable with correct field mapping
                    await self.store_in_airtable(
                        symbol=symbol,
                        image_type=image_type,
                        analysis_result=analysis_result
                    )
                else:
                    logger.error(f"❌ Failed to process image")
                
                # Mark as processed
                self.processed_messages.add(event_msg.id)
                
                # Keep only last 1000 processed message IDs to prevent memory leak
                if len(self.processed_messages) > 1000:
                    self.processed_messages = set(list(self.processed_messages)[-1000:])
            
        except Exception as e:
            logger.error(f"Error downloading/processing message {event_msg.id}: {e}")
    
    async def process_kingfisher_image(self, filepath: str, symbol: str, image_type: str, message_text: str = "") -> Optional[Dict[str, Any]]:
        """Process KingFisher image through the analysis pipeline"""
        try:
            logger.info(f"🔍 Processing {image_type} for {symbol}")
            
            # Use existing image processing service
            analysis_result = await self.image_processor.process_image(filepath)
            
            # Enhance with our extracted data
            if analysis_result:
                analysis_result["symbol"] = symbol
                analysis_result["image_type"] = image_type
                analysis_result["message_text"] = message_text
                analysis_result["timestamp"] = datetime.now(timezone.utc).isoformat()
                
                # Add symbol-specific analysis
                if image_type == "liquidation_map":
                    analysis_result["liquidation_levels"] = self.extract_liquidation_levels(analysis_result)
                elif image_type in ["liqratio_longterm", "liqratio_shortterm"]:
                    analysis_result["ratio_analysis"] = self.analyze_ratios(analysis_result)
                
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error processing KingFisher image: {e}")
            return None
    
    def extract_liquidation_levels(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract liquidation levels from analysis"""
        # This would be enhanced with actual image analysis
        return {
            "major_levels": analysis_result.get("liquidation_clusters", []),
            "critical_zones": analysis_result.get("critical_zones", []),
            "risk_areas": analysis_result.get("risk_areas", [])
        }
    
    def analyze_ratios(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze long/short ratios"""
        return {
            "long_ratio": analysis_result.get("long_concentration", 0),
            "short_ratio": analysis_result.get("short_concentration", 0),
            "ratio_trend": analysis_result.get("ratio_trend", "neutral")
        }
    
    async def store_in_airtable(self, symbol: str, image_type: str, analysis_result: Dict[str, Any]) -> bool:
        """Store analysis in correct Airtable field"""
        try:
            # Get the correct field name for this image type
            field_name = self.get_airtable_field_for_image_type(image_type)
            
            # Prepare data for specific field
            field_data = {
                "timestamp": analysis_result.get("timestamp", ""),
                "symbol": symbol,
                "image_type": image_type,
                "significance_score": analysis_result.get("significance_score", 0),
                "confidence": analysis_result.get("confidence", 0),
                "sentiment": analysis_result.get("market_sentiment", "neutral")
            }
            
            # Add type-specific data
            if image_type == "liquidation_map":
                field_data["liquidation_levels"] = analysis_result.get("liquidation_levels", {})
                field_data["clusters"] = analysis_result.get("liquidation_clusters", [])
            elif image_type in ["liqratio_longterm", "liqratio_shortterm"]:
                field_data["ratio_analysis"] = analysis_result.get("ratio_analysis", {})
            elif image_type == "rsi_heatmap":
                field_data["rsi_levels"] = analysis_result.get("rsi_analysis", {})
            
            # Create Airtable record with correct field
            logger.info(f"📤 Storing in Airtable field: {field_name} for symbol: {symbol}")
            
            # Use the airtable service to store
            success = await self.airtable_service.store_image_analysis({
                "symbol": symbol,
                field_name: json.dumps(field_data),  # Store in the correct field
                "professional_report": analysis_result.get("professional_report", ""),
                "timestamp": analysis_result.get("timestamp", ""),
                "current_price": analysis_result.get("current_price", 0),
                "significance_score": analysis_result.get("significance_score", 0),
                "market_sentiment": analysis_result.get("market_sentiment", ""),
                "confidence": analysis_result.get("confidence", 0)
            })
            
            if success:
                logger.info(f"✅ Successfully stored {symbol} {image_type} in Airtable field: {field_name}")
            else:
                logger.error(f"❌ Failed to store in Airtable")
            
            return success
            
        except Exception as e:
            logger.error(f"Error storing in Airtable: {e}")
            return False
    
    @client.on(events.NewMessage())
    async def message_handler(self, event):
        """Handler for new messages"""
        msg = event.message
        
        # Check if message contains image
        if not self.is_image_message(msg):
            return
        
        # Check if message is from watched chats
        if self.watch_chats:
            try:
                chat = await event.get_chat()
                username = getattr(chat, "username", None)
                chat_id = getattr(chat, "id", None)
                title = getattr(chat, "title", None)
                
                # Create labels to match against
                labels = set([
                    str(chat_id) if chat_id is not None else "",
                    f"-100{abs(chat_id)}" if isinstance(chat_id, int) and chat_id < 0 else "",
                    username.lower() if username else "",
                    (title or "").lower(),
                ])
                
                # Check if this chat is in our watch list
                match = any(
                    watch.lower().lstrip("@") in labels or 
                    (username and watch.lower().lstrip("@") == username.lower())
                    for watch in self.watch_chats
                ) or any(str(watch) == str(chat_id) for watch in self.watch_chats)
                
                if not match:
                    return
                    
                logger.info(f"🎯 New image detected from {username or title or chat_id}")
                
            except Exception as e:
                logger.warning(f"Could not resolve chat for message {msg.id}: {e}")
                return
        
        # Process the image
        await self.download_and_process(msg)
    
    async def backfill_messages(self):
        """Backfill recent messages from watched chats"""
        if self.backfill_limit <= 0 or not self.watch_chats:
            return
        
        logger.info(f"📜 Backfilling last {self.backfill_limit} messages from: {self.watch_chats}")
        
        for target in self.watch_chats:
            try:
                logger.info(f"Fetching messages from {target}...")
                async for msg in self.client.iter_messages(entity=target, limit=self.backfill_limit):
                    if self.is_image_message(msg):
                        await self.download_and_process(msg)
                        
            except Exception as e:
                logger.error(f"Error backfilling from {target}: {e}")
    
    async def start(self):
        """Start the Telegram watcher"""
        try:
            logger.info("🚀 Starting Telegram Watcher Service...")
            
            # Start the client
            await self.client.start()
            logger.info("✅ Connected to Telegram")
            
            # Backfill recent messages
            if self.backfill_limit > 0:
                await self.backfill_messages()
            
            # Set running flag
            self.is_running = True
            
            logger.info(f"👀 Watching chats: {self.watch_chats}")
            logger.info("Press Ctrl+C to stop...")
            
            # Run until disconnected
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Error in Telegram watcher: {e}")
            self.is_running = False
            raise
    
    async def stop(self):
        """Stop the Telegram watcher"""
        logger.info("Stopping Telegram Watcher...")
        self.is_running = False
        await self.client.disconnect()
        logger.info("✅ Telegram Watcher stopped")
    
    def is_connected(self) -> bool:
        """Check if connected to Telegram"""
        return self.client.is_connected() if self.client else False


# Standalone runner
async def main():
    """Main function to run the watcher"""
    watcher = TelegramWatcherService()
    
    try:
        await watcher.start()
    except KeyboardInterrupt:
        logger.info("\n⏹️ Stopping watcher...")
        await watcher.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await watcher.stop()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the watcher
    asyncio.run(main())