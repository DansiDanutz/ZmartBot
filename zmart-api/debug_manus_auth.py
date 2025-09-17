#!/usr/bin/env python3
"""
Debug Manus API Authentication
Test different authentication methods to find the correct format
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

def test_auth_methods():
    """Test different authentication methods with Manus API"""

    api_key = os.getenv('MANUS_API_KEY')
    if not api_key:
        print("❌ MANUS_API_KEY not found in .env")
        return

    print(f"🔑 Testing with API Key: {api_key[:10]}...{api_key[-10:]}")
    print("=" * 60)

    webhook_url = "http://localhost:8000/api/webhooks/manus"

    # Payload for webhook registration
    payload = {
        'webhook': {
            'url': webhook_url
        }
    }

    # Test 1: API_KEY header
    print("\n1️⃣ Testing with API_KEY header...")
    headers1 = {
        'API_KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            'https://api.manus.ai/v1/webhooks',
            headers=headers1,
            json=payload,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 2: Bearer token in Authorization header
    print("\n2️⃣ Testing with Bearer Authorization header...")
    headers2 = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            'https://api.manus.ai/v1/webhooks',
            headers=headers2,
            json=payload,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 3: X-API-Key header
    print("\n3️⃣ Testing with X-API-Key header...")
    headers3 = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            'https://api.manus.ai/v1/webhooks',
            headers=headers3,
            json=payload,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 4: api-key header (lowercase)
    print("\n4️⃣ Testing with api-key header (lowercase)...")
    headers4 = {
        'api-key': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            'https://api.manus.ai/v1/webhooks',
            headers=headers4,
            json=payload,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 5: Just the token without Bearer prefix
    print("\n5️⃣ Testing with Authorization header (no Bearer prefix)...")
    headers5 = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            'https://api.manus.ai/v1/webhooks',
            headers=headers5,
            json=payload,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "=" * 60)
    print("✅ Testing complete. Check which method returned a 200/201 status.")
    print("   Then update the register_manus_webhook.py script accordingly.")

if __name__ == '__main__':
    test_auth_methods()