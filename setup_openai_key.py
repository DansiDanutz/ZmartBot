#!/usr/bin/env python3
"""
Setup OpenAI API Key in API Keys Manager
Securely adds the provided OpenAI API key to the centralized manager
"""

import os
import sys
sys.path.append('/Users/dansidanutz/Desktop/ZmartBot/zmart-api')

def setup_openai_key():
    """Add OpenAI API key to the manager"""
    try:
        from src.config.api_keys_manager import APIKeysManager
        
        # Initialize the manager
        manager = APIKeysManager()
        
        # Your OpenAI API key
        openai_key = "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"
        
        # Add OpenAI API key to the manager
        success = manager.add_api_key(
            service_name="openai",
            api_key=openai_key,
            base_url="https://api.openai.com/v1",
            rate_limit=1000,
            description="OpenAI API for ChatGPT-5/GPT-4 trading analysis"
        )
        
        if success:
            print("✅ OpenAI API key successfully added to API Keys Manager!")
            print("🔐 Key is encrypted and stored securely")
            print("🤖 Ready for ChatGPT-5/GPT-4 trading analysis")
            
            # Test the configuration
            config = manager.get_api_config("openai")
            if config:
                print(f"✅ Configuration verified: {config.service_name}")
                print(f"🌐 Base URL: {config.base_url}")
                print(f"⚡ Rate limit: {config.rate_limit}")
            
            return True
        else:
            print("❌ Failed to add OpenAI API key")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure the API keys manager is properly installed")
        return False
    except Exception as e:
        print(f"❌ Error setting up OpenAI key: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Setting up OpenAI API Key in ZmartBot...")
    print("=" * 50)
    
    success = setup_openai_key()
    
    if success:
        print("\n🎉 OpenAI API Key Setup Complete!")
        print("📊 Your key is now available for all ZmartBot services")
        print("🚀 Restart your backend servers to use the new configuration")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
    
    print("=" * 50)