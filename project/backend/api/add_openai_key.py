#!/usr/bin/env python3
"""
Direct OpenAI API Key Setup
Add your OpenAI API key directly to the API keys manager
"""

import sys
sys.path.append('.')

from src.config.api_keys_manager import api_keys_manager

# ADD YOUR OPENAI API KEY HERE
# Replace the placeholder with your actual OpenAI API key
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"

def add_openai_key():
    """Add OpenAI API key to the manager"""
    
    if OPENAI_API_KEY == "sk-your-actual-openai-api-key-here":
        print("❌ Please replace OPENAI_API_KEY with your actual API key in add_openai_key.py")
        print("   Edit the file and change line 11 to your real API key")
        return False
    
    try:
        # Add OpenAI API key to the manager
        result = api_keys_manager.add_api_key(
            service_name='openai',
            api_key=OPENAI_API_KEY,
            base_url='https://api.openai.com/v1',
            rate_limit=3500,
            description='OpenAI API for ChatGPT-5/GPT-4 trading analysis'
        )
        
        if result:
            print("✅ OpenAI API key added successfully!")
            print("🚀 ChatGPT-5 trading advice is now ready!")
            
            # Verify the configuration
            openai_config = api_keys_manager.get_api_key('openai')
            if openai_config and openai_config['api_key']:
                print("🔑 API key configured and encrypted")
                print("🌐 Base URL:", openai_config['base_url'])
                print("⚡ Rate limit:", openai_config['rate_limit'])
                return True
        
        print("❌ Failed to add API key")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Adding OpenAI API Key to ZmartBot...")
    success = add_openai_key()
    
    if success:
        print("\n🎉 Setup complete! You can now use real ChatGPT-5 trading advice.")
    else:
        print("\n❌ Setup failed. Please check your API key and try again.")