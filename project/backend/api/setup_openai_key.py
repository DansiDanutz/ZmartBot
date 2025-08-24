#!/usr/bin/env python3
"""
Setup OpenAI API Key in the API Keys Manager
Run this script to add your OpenAI API key to the secure API keys manager
"""

import sys
import os
sys.path.append('.')

from src.config.api_keys_manager import api_keys_manager

def setup_openai_key():
    """Set up OpenAI API key in the API keys manager"""
    
    print("🔑 OpenAI API Key Setup")
    print("=" * 50)
    
    # Get API key from user input
    api_key = input("Enter your OpenAI API key (starts with sk-): ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return False
    
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: OpenAI API keys typically start with 'sk-'")
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            return False
    
    try:
        # Add OpenAI API key to the manager
        result = api_keys_manager.add_api_key(
            service_name='openai',
            api_key=api_key,
            base_url='https://api.openai.com/v1',
            rate_limit=3500,
            description='OpenAI API for ChatGPT-5/GPT-4 trading analysis'
        )
        
        if result:
            print("✅ OpenAI API key added successfully to the API keys manager!")
            print("🚀 ChatGPT-5 trading advice is now ready to use!")
            
            # Test the configuration
            openai_config = api_keys_manager.get_api_key('openai')
            if openai_config:
                print(f"📊 Service: {openai_config['service_name']}")
                print(f"🔒 Key configured: {'Yes' if openai_config['api_key'] else 'No'}")
                print(f"🌐 Base URL: {openai_config['base_url']}")
                print(f"⚡ Rate limit: {openai_config['rate_limit']} requests/hour")
            
            return True
        else:
            print("❌ Failed to add OpenAI API key")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up OpenAI API key: {e}")
        return False

def check_current_status():
    """Check current OpenAI configuration status"""
    print("\n📋 Current OpenAI Configuration Status")
    print("=" * 40)
    
    openai_config = api_keys_manager.get_api_key('openai')
    if openai_config:
        print("✅ OpenAI service found in API keys manager")
        print(f"   - Service active: {openai_config['is_active']}")
        print(f"   - Last used: {openai_config['last_used'] or 'Never'}")
        print(f"   - Usage count: {openai_config['usage_count']}")
        print(f"   - Base URL: {openai_config['base_url']}")
        
        # Check if key looks valid
        api_key = openai_config['api_key']
        if api_key and api_key != 'YOUR_API_KEY_HERE':
            print("   - API key: Configured ✅")
        else:
            print("   - API key: Not configured ❌")
    else:
        print("❌ OpenAI service not found in API keys manager")
        
    # List all services
    services = api_keys_manager.list_services()
    print(f"\n📊 Total services configured: {len(services)}")
    for service in services:
        status = "✅" if service['is_active'] else "❌"
        print(f"   {status} {service['service_name']}")

if __name__ == "__main__":
    print("🔐 ZmartBot OpenAI API Key Setup")
    print("=" * 50)
    
    # Check current status first
    check_current_status()
    
    print("\nOptions:")
    print("1. Add/Update OpenAI API key")
    print("2. Check status only")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        setup_openai_key()
    elif choice == '2':
        print("Status check complete.")
    elif choice == '3':
        print("Exiting.")
    else:
        print("Invalid choice. Exiting.")