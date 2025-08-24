#!/usr/bin/env python3
"""
Update KingFisher Module Configuration
Adds the new API keys to the KingFisher module configuration
"""

import os
from pathlib import Path

def update_kingfisher_env():
    """Update the KingFisher .env file with new API keys"""
    
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        print("❌ .env file not found in KingFisher module")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Check if OpenAI key already exists
    if 'OPENAI_API_KEY=' in content:
        print("✅ OpenAI API key already configured in KingFisher module")
        return True
    
    # Add OpenAI configuration
    openai_config = """

# OpenAI Configuration for King-Image-Telegram Analysis
OPENAI_API_KEY=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
"""
    
    # Add to end of file
    with open(env_file, 'a') as f:
        f.write(openai_config)
    
    print("✅ Added OpenAI API key to KingFisher module configuration")
    return True

def update_kingfisher_scripts():
    """Update KingFisher scripts with the new API key"""
    
    scripts_dir = Path(__file__).parent / 'King-Scripts'
    
    # Files that need API key updates
    script_files = [
        'STEP4-Analyze-And-Create-Reports.py',
        'STEP5-Extract-Liquidation-Clusters-Enhanced.py'
    ]
    
    new_api_key = "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"
    
    for script_file in script_files:
        script_path = scripts_dir / script_file
        if script_path.exists():
            try:
                with open(script_path, 'r') as f:
                    content = f.read()
                
                # Replace the API key in the scripts
                if 'API_KEYS = [' in content:
                    # Update the API key array
                    import re
                    pattern = r'API_KEYS = \[[^\]]*\]'
                    replacement = f'API_KEYS = [\n    "{new_api_key}"\n]'
                    updated_content = re.sub(pattern, replacement, content)
                    
                    with open(script_path, 'w') as f:
                        f.write(updated_content)
                    
                    print(f"✅ Updated API key in {script_file}")
                else:
                    print(f"⚠️ No API_KEYS found in {script_file}")
                    
            except Exception as e:
                print(f"❌ Error updating {script_file}: {e}")
        else:
            print(f"⚠️ Script file not found: {script_file}")

def main():
    """Main function to update all KingFisher configurations"""
    print("🔧 Updating KingFisher Module Configuration...")
    print("=" * 50)
    
    # Update .env file
    print("\n1. Updating .env file...")
    update_kingfisher_env()
    
    # Update script files
    print("\n2. Updating script files...")
    update_kingfisher_scripts()
    
    print("\n✅ KingFisher configuration update complete!")
    print("\n📋 Summary:")
    print("   • OpenAI API key added to .env file")
    print("   • KingFisher scripts updated with new API key")
    print("   • Ready for King-Image-Telegram analysis")

if __name__ == "__main__":
    main()
