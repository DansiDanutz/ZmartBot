#!/usr/bin/env python3
"""
Telegram Service for KingFisher Image Processing
Monitors KingFisher Telegram channel for automation images
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
import httpx

from src.config.settings import settings
from services.image_processing_service import ImageProcessingService

logger = logging.getLogger(__name__)

class TelegramService:
    """Service for monitoring Telegram channels and sending notifications"""
    
    def __init__(self):
        self.is_connected = False
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        # User's Telegram information
        self.user_telegram_id = 424184493  # Seme's Telegram ID
        self.user_username = "SemeCJ"
        self.user_first_name = "Seme"
        # KingFisher Bot information
        self.kingfisher_bot_id = "5646047866"  # TheKingfisherBot ID
        self.kingfisher_bot_username = "@thekingfisher_liqmap_bot"
        self.kingfisher_bot_name = "TheKingfisherBot"
        self.image_processor = ImageProcessingService()
        self.last_message_id = None
        self.monitoring_active = False
        self.automation_enabled = True  # New: Control automation
        self.last_update_id = 0  # For long polling
        self.polling_task = None
        
    async def initialize(self) -> bool:
        """Initialize Telegram service"""
        try:
            if not self.bot_token:
                logger.warning("No Telegram bot token provided")
                return False
                
            # Test bot connection
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.telegram.org/bot{self.bot_token}/getMe"
                )
                if response.status_code == 200:
                    bot_info = response.json()
                    logger.info(f"Connected to Telegram bot: {bot_info['result']['username']}")
                    self.is_connected = True
                    return True
                else:
                    logger.error(f"Failed to connect to Telegram bot: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error initializing Telegram service: {e}")
            return False
    
    def enable_automation(self):
        """Enable automation monitoring"""
        self.automation_enabled = True
        logger.info("✅ Automation enabled - KingFisher monitoring active")
        return True
    
    def disable_automation(self):
        """Disable automation monitoring"""
        self.automation_enabled = False
        logger.info("⏸️ Automation disabled - KingFisher monitoring paused")
        return True
    
    def is_automation_enabled(self) -> bool:
        """Check if automation is enabled"""
        return self.automation_enabled
    
    async def start_monitoring(self):
        """Start monitoring KingFisher bot messages using long polling"""
        if not self.is_connected:
            logger.error("Cannot start monitoring - Telegram service not connected")
            return False
            
        self.monitoring_active = True
        logger.info(f"Started monitoring KingFisher bot: {self.kingfisher_bot_username}")
        
        # Start long polling in background
        self.polling_task = asyncio.create_task(self._long_polling_loop())
        
        return True
    
    async def _long_polling_loop(self):
        """Long polling loop for getting updates"""
        while self.monitoring_active:
            try:
                # Only process updates if automation is enabled
                if self.automation_enabled:
                    await self._get_updates()
                else:
                    # Sleep longer when automation is disabled
                    await asyncio.sleep(5)
                    
                await asyncio.sleep(1)  # Small delay between polls
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def _get_updates(self):
        """Get updates from Telegram using long polling"""
        try:
            async with httpx.AsyncClient() as client:
                # Get updates with timeout
                response = await client.get(
                    f"https://api.telegram.org/bot{self.bot_token}/getUpdates",
                    params={
                        "offset": self.last_update_id + 1,
                        "timeout": 30,  # Long polling timeout
                        "limit": 100
                    },
                    timeout=35.0  # Slightly longer than Telegram timeout
                )
                
                if response.status_code == 200:
                    updates = response.json().get("result", [])
                    
                    for update in updates:
                        update_id = update.get("update_id", 0)
                        self.last_update_id = max(self.last_update_id, update_id)
                        
                        # Process different types of updates
                        if "message" in update:
                            await self._process_message(update["message"])
                        elif "channel_post" in update:
                            await self._process_channel_post(update["channel_post"])
                        elif "edited_message" in update:
                            await self._process_message(update["edited_message"])
                            
        except httpx.TimeoutException:
            # Timeout is expected in long polling
            pass
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
    
    async def _process_message(self, message: Dict[str, Any]):
        """Process incoming message"""
        try:
            # Check if message is from KingFisher bot
            from_user = message.get("from", {})
            if (from_user.get("id") == int(self.kingfisher_bot_id) or
                from_user.get("username") == "thekingfisher_liqmap_bot"):
                
                # Only process if automation is enabled
                if self.automation_enabled:
                    await self._process_kingfisher_message(message)
                else:
                    logger.info("⏸️ Automation disabled - skipping KingFisher message")
            else:
                # Handle messages from other users (manual forwarding)
                await self._process_user_message(message)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _process_channel_post(self, post: Dict[str, Any]):
        """Process channel post (for public channels)"""
        try:
            # Check if post is from KingFisher channel
            chat = post.get("chat", {})
            if (chat.get("username") == "kingfisher_automation" or
                "kingfisher" in chat.get("title", "").lower()):
                
                # Only process if automation is enabled
                if self.automation_enabled:
                    await self._process_kingfisher_message(post)
                else:
                    logger.info("⏸️ Automation disabled - skipping KingFisher channel post")
                
        except Exception as e:
            logger.error(f"Error processing channel post: {e}")
    
    async def _process_user_message(self, message: Dict[str, Any]):
        """Process message from user (manual forwarding)"""
        try:
            from_user = message.get("from", {})
            user_id = from_user.get("id")
            username = from_user.get("username")
            
            # Check if this is from the target user (Seme)
            if user_id == self.user_telegram_id:
                logger.info(f"✅ Message from target user: {self.user_first_name} ({self.user_username})")
                
                # Check if message has photo (forwarded image)
                if "photo" in message:
                    photos = message["photo"]
                    if photos:
                        largest_photo = max(photos, key=lambda x: x.get("file_size", 0))
                        file_id = largest_photo["file_id"]
                        
                        logger.info(f"Processing KingFisher image from {self.user_first_name} ({self.user_username})")
                        await self._download_and_process_image(file_id, f"user_{user_id}")
                        
                        # Send confirmation to user
                        await self.send_notification(
                            f"✅ <b>KingFisher Image Processed</b>\n\n"
                            f"📸 Your liquidation map has been analyzed\n"
                            f"👤 User: {self.user_first_name} ({self.user_username})\n"
                            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"🔍 Analysis: Liquidation patterns detected and stored in Airtable"
                        )
                else:
                    logger.info(f"Message from {self.user_first_name} but no image found")
            else:
                logger.info(f"Message from other user: {username} ({user_id}) - ignoring")
                    
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
    
    async def _process_kingfisher_message(self, message: Dict[str, Any]):
        """Process message from KingFisher bot"""
        try:
            message_id = message.get("message_id")
            
            # Skip if already processed
            if message_id == self.last_message_id:
                return
                
            # Check if message has photo
            if "photo" in message:
                photos = message["photo"]
                if photos:
                    # Get the largest photo
                    largest_photo = max(photos, key=lambda x: x.get("file_size", 0))
                    file_id = largest_photo["file_id"]
                    
                    # Download and process image
                    await self._download_and_process_image(file_id, message_id)
                    
            self.last_message_id = message_id
            
        except Exception as e:
            logger.error(f"Error processing KingFisher message: {e}")
    
    async def _download_and_process_image(self, file_id: str, message_id: Any):
        """Download and process image from Telegram"""
        try:
            async with httpx.AsyncClient() as client:
                # Get file path
                response = await client.get(
                    f"https://api.telegram.org/bot{self.bot_token}/getFile",
                    params={"file_id": file_id}
                )
                
                if response.status_code == 200:
                    file_info = response.json()["result"]
                    file_path = file_info["file_path"]
                    
                    # Download file
                    download_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
                    file_response = await client.get(download_url)
                    
                    if file_response.status_code == 200:
                        # Save image
                        downloads_dir = Path("downloads")
                        downloads_dir.mkdir(exist_ok=True)
                        
                        image_path = downloads_dir / f"kingfisher_{message_id}.jpg"
                        with open(image_path, "wb") as f:
                            f.write(file_response.content)
                        
                        logger.info(f"Downloaded image: {image_path}")
                        
                        # Process image
                        analysis_result = await self.image_processor.process_image(str(image_path))
                        
                        # Send analysis result
                        await self.send_analysis_result(analysis_result)
                        
                        # Send to ZmartBot if significant
                        if analysis_result.get("significance_score", 0) > 0.7:
                            await self._send_to_zmartbot(analysis_result)
                        
        except Exception as e:
            logger.error(f"Error downloading and processing image: {e}")
    
    async def process_manual_image(self, image_path: str, user_id: int = None, username: str = None):
        """Process manually uploaded image file"""
        try:
            logger.info(f"Processing manual image: {image_path}")
            
            # Validate file exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Process image
            analysis_result = await self.image_processor.process_image(image_path)
            
            # Send analysis result
            await self.send_analysis_result(analysis_result)
            
            # Send to ZmartBot if significant
            if analysis_result.get("significance_score", 0) > 0.7:
                await self._send_to_zmartbot(analysis_result)
            
            # Send confirmation if user info provided
            if user_id or username:
                await self.send_notification(
                    f"✅ <b>Manual Image Processed</b>\n\n"
                    f"📸 Your uploaded image has been analyzed\n"
                    f"👤 User: {username or user_id}\n"
                    f"📊 Significance: {analysis_result.get('significance_score', 0):.2%}\n"
                    f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error processing manual image: {e}")
            raise e
    
    async def setup_webhook(self, webhook_url: str):
        """Setup webhook for production (requires HTTPS)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.telegram.org/bot{self.bot_token}/setWebhook",
                    params={"url": webhook_url}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        logger.info(f"Webhook set successfully: {webhook_url}")
                        return True
                    else:
                        logger.error(f"Failed to set webhook: {result}")
                        return False
                else:
                    logger.error(f"Webhook setup failed: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error setting up webhook: {e}")
            return False
    
    async def delete_webhook(self):
        """Delete webhook (switch back to polling)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.telegram.org/bot{self.bot_token}/deleteWebhook"
                )
                
                if response.status_code == 200:
                    logger.info("Webhook deleted successfully")
                    return True
                else:
                    logger.error(f"Failed to delete webhook: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting webhook: {e}")
            return False
    
    async def process_forwarded_image(self, file_id: str, user_id: int, username: str = None):
        """Process manually forwarded image from user"""
        try:
            logger.info(f"Processing forwarded image from user {user_id} ({username})")
            
            # Download and process image
            await self._download_and_process_image(file_id, f"forwarded_{user_id}")
            
            # Send confirmation to user
            await self.send_notification(
                f"✅ <b>Image Processed</b>\n\n"
                f"📸 Your KingFisher image has been analyzed\n"
                f"👤 User: {username or user_id}\n"
                f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
        except Exception as e:
            logger.error(f"Error processing forwarded image: {e}")
            await self.send_notification(
                f"❌ <b>Processing Failed</b>\n\n"
                f"Error: {str(e)}\n"
                f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
    
    async def send_notification(self, message: str, image_path: Optional[str] = None) -> bool:
        """Send notification to Telegram chat"""
        try:
            if not self.is_connected:
                logger.warning("Telegram service not connected")
                return False
                
            async with httpx.AsyncClient() as client:
                if image_path and os.path.exists(image_path):
                    # Send photo with caption
                    with open(image_path, 'rb') as photo:
                        files = {'photo': photo}
                        data = {
                            'chat_id': self.chat_id,
                            'caption': message,
                            'parse_mode': 'HTML'
                        }
                        response = await client.post(
                            f"https://api.telegram.org/bot{self.bot_token}/sendPhoto",
                            files=files,
                            data=data
                        )
                else:
                    # Send text message
                    data = {
                        'chat_id': self.chat_id,
                        'text': message,
                        'parse_mode': 'HTML'
                    }
                    response = await client.post(
                        f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                        data=data
                    )
                
                if response.status_code == 200:
                    logger.info("Notification sent successfully")
                    return True
                else:
                    logger.error(f"Failed to send notification: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    async def send_analysis_result(self, analysis_result: Dict[str, Any]) -> bool:
        """Send analysis result to Telegram"""
        try:
            significance = analysis_result.get('significance_score', 0)
            sentiment = analysis_result.get('market_sentiment', 'neutral')
            confidence = analysis_result.get('confidence', 0)
            
            # Create message
            message = f"""
🔍 <b>KingFisher Analysis Result</b>

📊 <b>Significance Score:</b> {significance:.2%}
📈 <b>Market Sentiment:</b> {sentiment.title()}
🎯 <b>Confidence:</b> {confidence:.2%}
⏰ <b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
            
            if significance > 0.7:
                message += "🚨 <b>HIGH SIGNIFICANCE DETECTED!</b>"
            elif significance > 0.5:
                message += "⚠️ <b>Medium significance detected</b>"
            else:
                message += "ℹ️ <b>Low significance</b>"
            
            return await self.send_notification(message)
            
        except Exception as e:
            logger.error(f"Error sending analysis result: {e}")
            return False
    
    async def send_alert(self, alert_type: str, details: str) -> bool:
        """Send alert to Telegram"""
        try:
            message = f"""
🚨 <b>KingFisher Alert</b>

📋 <b>Type:</b> {alert_type}
📝 <b>Details:</b> {details}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            return await self.send_notification(message)
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            return False
    
    async def _send_to_zmartbot(self, analysis_result: Dict[str, Any]):
        """Send analysis result to ZmartBot"""
        try:
            # TODO: Implement ZmartBot integration
            logger.info("Sending analysis to ZmartBot")
            
        except Exception as e:
            logger.error(f"Error sending to ZmartBot: {e}")
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self.is_connected
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        return self.monitoring_active
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        if self.polling_task:
            self.polling_task.cancel()
        logger.info("Stopped monitoring KingFisher bot")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Telegram connection"""
        try:
            success = await self.initialize()
            if success:
                # Send test message
                test_message = f"🧪 <b>KingFisher Test</b>\n\n✅ Connection successful!\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                message_sent = await self.send_notification(test_message)
                
                return {
                    "connected": True,
                    "bot_token_valid": True,
                    "chat_id_valid": message_sent,
                    "monitoring_ready": True,
                    "automation_enabled": self.automation_enabled,
                    "message": "Connection test successful"
                }
            else:
                return {
                    "connected": False,
                    "bot_token_valid": False,
                    "chat_id_valid": False,
                    "monitoring_ready": False,
                    "automation_enabled": self.automation_enabled,
                    "message": "Connection test failed"
                }
                
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "message": "Connection test failed"
            } 