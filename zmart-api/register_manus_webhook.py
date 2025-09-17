#!/usr/bin/env python3
"""
Manus AI Webhook Registration Script
Registers webhook endpoints with Manus AI for event notifications
"""

import os
import sys
import json
import requests
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

def register_webhook(webhook_url=None):
    """
    Register webhook with Manus AI

    Args:
        webhook_url: The webhook URL to register (optional)
    """
    api_key = os.getenv('MANUS_API_KEY')

    if not api_key:
        print("❌ Error: MANUS_API_KEY not found in environment variables")
        return False

    # Default webhook URL if not provided
    if not webhook_url:
        host = os.getenv('HOST', 'localhost')
        port = os.getenv('PORT', '8000')

        # For production, use your public URL
        if os.getenv('ENVIRONMENT') == 'production':
            webhook_url = os.getenv('MANUS_WEBHOOK_URL', f'https://your-domain.com/api/webhooks/manus')
        else:
            webhook_url = f'http://{host}:{port}/api/webhooks/manus'

    print(f"📡 Registering webhook with Manus AI...")
    print(f"   Webhook URL: {webhook_url}")

    # Try different authentication methods
    headers = {
        'API_KEY': api_key,  # Based on OpenAPI spec, it might expect API_KEY header
        'Content-Type': 'application/json'
    }

    # Use the correct format as per Manus API specification
    payload = {
        'webhook': {
            'url': webhook_url
        }
    }

    try:
        response = requests.post(
            'https://api.manus.ai/v1/webhooks',
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code in [200, 201]:
            webhook_data = response.json()
            webhook_id = webhook_data.get('webhook_id', 'unknown')

            print(f"✅ Webhook registered successfully!")
            print(f"   Webhook ID: {webhook_id}")
            print(f"   Status: Active")

            # Save webhook configuration
            config_file = 'manus_webhook_config.json'
            with open(config_file, 'w') as f:
                json.dump({
                    'webhook_id': webhook_id,
                    'webhook_url': webhook_url,
                    'registered_at': datetime.now().isoformat(),
                    'response': webhook_data
                }, f, indent=2)

            print(f"📝 Configuration saved to {config_file}")
            return True

        else:
            print(f"❌ Failed to register webhook")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Manus API: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def list_webhooks():
    """List all registered webhooks"""
    api_key = os.getenv('MANUS_API_KEY')

    if not api_key:
        print("❌ Error: MANUS_API_KEY not found in environment variables")
        return

    # Try different authentication methods
    headers = {
        'API_KEY': api_key,  # Based on OpenAPI spec, it might expect API_KEY header
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(
            'https://api.manus.ai/v1/webhooks',
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            webhooks = response.json()

            if webhooks:
                print(f"📋 Registered Webhooks:")
                for webhook in webhooks:
                    print(f"\n   ID: {webhook.get('id')}")
                    print(f"   URL: {webhook.get('url')}")
                    print(f"   Events: {', '.join(webhook.get('events', []))}")
                    print(f"   Created: {webhook.get('created_at')}")
            else:
                print("📭 No webhooks registered")

        else:
            print(f"❌ Failed to list webhooks: {response.status_code}")

    except Exception as e:
        print(f"❌ Error listing webhooks: {e}")

def unregister_webhook(webhook_id):
    """Unregister a webhook"""
    api_key = os.getenv('MANUS_API_KEY')

    if not api_key:
        print("❌ Error: MANUS_API_KEY not found in environment variables")
        return False

    # Try different authentication methods
    headers = {
        'API_KEY': api_key,  # Based on OpenAPI spec, it might expect API_KEY header
        'Content-Type': 'application/json'
    }

    try:
        response = requests.delete(
            f'https://api.manus.ai/v1/webhooks/{webhook_id}',
            headers=headers,
            timeout=10
        )

        if response.status_code in [200, 204]:
            print(f"✅ Webhook {webhook_id} unregistered successfully")
            return True
        else:
            print(f"❌ Failed to unregister webhook: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error unregistering webhook: {e}")
        return False

def test_webhook():
    """Send a test event to verify webhook is working"""
    api_key = os.getenv('MANUS_API_KEY')

    if not api_key:
        print("❌ Error: MANUS_API_KEY not found in environment variables")
        return

    # Try different authentication methods
    headers = {
        'API_KEY': api_key,  # Based on OpenAPI spec, it might expect API_KEY header
        'Content-Type': 'application/json'
    }

    test_task = {
        'prompt': 'This is a test task from ZmartBot to verify webhook integration. Please acknowledge receipt.',
        'name': 'Webhook Test Task',
        'description': 'Testing ZmartBot webhook integration with Manus AI',
        'metadata': {
            'test_mode': True,
            'timestamp': datetime.now().isoformat(),
            'platform': 'zmartbot'
        }
    }

    print("🧪 Sending test task to trigger webhook...")

    try:
        response = requests.post(
            'https://api.manus.ai/v1/tasks',
            headers=headers,
            json=test_task,
            timeout=10
        )

        if response.status_code in [200, 201]:
            task_data = response.json()
            print(f"✅ Test task created successfully!")
            print(f"   Task ID: {task_data.get('id')}")
            print(f"   Status: {task_data.get('status')}")
            print(f"\n📨 Check your webhook endpoint for incoming events")
        else:
            print(f"❌ Failed to create test task: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ Error sending test task: {e}")

def main():
    parser = argparse.ArgumentParser(description='Manus AI Webhook Management')
    parser.add_argument('action', choices=['register', 'list', 'unregister', 'test'],
                      help='Action to perform')
    parser.add_argument('--webhook-url', help='Custom webhook URL')
    parser.add_argument('--webhook-id', help='Webhook ID for unregister action')

    args = parser.parse_args()

    print("🤖 Manus AI Webhook Manager for ZmartBot")
    print("=" * 50)

    if args.action == 'register':
        success = register_webhook(args.webhook_url)
        sys.exit(0 if success else 1)

    elif args.action == 'list':
        list_webhooks()

    elif args.action == 'unregister':
        if not args.webhook_id:
            # Try to load from config file
            try:
                with open('manus_webhook_config.json', 'r') as f:
                    config = json.load(f)
                    webhook_id = config.get('webhook_id')
            except:
                print("❌ Please provide --webhook-id or ensure manus_webhook_config.json exists")
                sys.exit(1)
        else:
            webhook_id = args.webhook_id

        success = unregister_webhook(webhook_id)
        sys.exit(0 if success else 1)

    elif args.action == 'test':
        test_webhook()

if __name__ == '__main__':
    main()