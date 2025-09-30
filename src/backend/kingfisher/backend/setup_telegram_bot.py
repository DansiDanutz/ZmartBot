#!/usr/bin/env python3
"""
KingFisher Telegram Bot Setup
Helps configure Telegram bot integration
"""

import os
import sys
import asyncio
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBotSetup:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID', '')
        
    def check_environment(self) -> bool:
        """Check if required environment variables are set"""
        missing_vars = []
        
        if not self.bot_token:
            missing_vars.append('TELEGRAM_BOT_TOKEN')
        if not self.channel_id:
            missing_vars.append('TELEGRAM_CHANNEL_ID')
            
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
            
        logger.info("✅ All environment variables are set")
        return True
    
    def create_env_file(self):
        """Create .env file template"""
        env_content = """# KingFisher Telegram Bot Configuration
# Get these values from @BotFather on Telegram

# Your bot token from @BotFather
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Your channel ID (can be found by forwarding a message to @userinfobot)
TELEGRAM_CHANNEL_ID=your_channel_id_here

# Optional: Set to 'true' for debug mode
DEBUG=false
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
            
        logger.info("✅ Created .env file template")
        logger.info("📝 Please edit .env file with your actual values")
    
    async def test_bot_connection(self) -> bool:
        """Test if bot token is valid"""
        try:
            from telegram import Bot
            
            bot = Bot(token=self.bot_token)
            me = await bot.get_me()
            
            logger.info(f"✅ Bot connected successfully!")
            logger.info(f"🤖 Bot name: {me.first_name}")
            logger.info(f"📝 Bot username: @{me.username}")
            logger.info(f"🆔 Bot ID: {me.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to bot: {e}")
            return False
    
    async def test_channel_access(self) -> bool:
        """Test if bot can access the channel"""
        try:
            from telegram import Bot
            
            bot = Bot(token=self.bot_token)
            
            # Try to get channel info
            chat = await bot.get_chat(self.channel_id)
            
            logger.info(f"✅ Channel access successful!")
            logger.info(f"📢 Channel name: {chat.title}")
            logger.info(f"🆔 Channel ID: {chat.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to access channel: {e}")
            return False
    
    def print_setup_instructions(self):
        """Print setup instructions"""
        print("\n" + "="*60)
        print("🐟 KingFisher Telegram Bot Setup")
        print("="*60)
        print("\n📋 Setup Instructions:")
        print("\n1. Create a Telegram Bot:")
        print("   - Open Telegram and search for @BotFather")
        print("   - Send /newbot command")
        print("   - Follow instructions to create your bot")
        print("   - Copy the bot token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)")
        print("\n2. Get Channel ID:")
        print("   - Add your bot to your channel as admin")
        print("   - Forward a message from your channel to @userinfobot")
        print("   - Copy the channel ID (looks like: -1001234567890)")
        print("\n3. Configure Environment:")
        print("   - Edit the .env file with your bot token and channel ID")
        print("   - Or set environment variables:")
        print("     export TELEGRAM_BOT_TOKEN=your_bot_token")
        print("     export TELEGRAM_CHANNEL_ID=your_channel_id")
        print("\n4. Test the Setup:")
        print("   - Run: python setup_telegram_bot.py --test")
        print("\n5. Start the Bot:")
        print("   - Run: python telegram_monitor.py")
        print("\n" + "="*60)

async def main():
    """Main setup function"""
    setup = TelegramBotSetup()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Test mode
        print("🧪 Testing Telegram bot configuration...")
        
        if not setup.check_environment():
            print("\n❌ Environment not configured properly")
            setup.print_setup_instructions()
            return
        
        # Test bot connection
        bot_ok = await setup.test_bot_connection()
        if not bot_ok:
            print("\n❌ Bot token is invalid")
            return
        
        # Test channel access
        channel_ok = await setup.test_channel_access()
        if not channel_ok:
            print("\n❌ Cannot access channel - make sure bot is admin")
            return
        
        print("\n✅ All tests passed! Bot is ready to use.")
        print("🚀 Start the bot with: python telegram_monitor.py")
        
    else:
        # Setup mode
        print("🔧 Setting up KingFisher Telegram Bot...")
        
        # Create .env file if it doesn't exist
        if not os.path.exists('.env'):
            setup.create_env_file()
        
        setup.print_setup_instructions()

if __name__ == "__main__":
    asyncio.run(main()) 