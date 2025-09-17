#!/usr/bin/env python3
"""
ZmartBot Single Service Registration Script
Register one service at a time to avoid database locking
"""

import requests
import json
import sys

PASSPORT_SERVICE_URL = "http://localhost:8620"
PASSPORT_API_BASE = f"{PASSPORT_SERVICE_URL}/api/passport"

def register_single_service(name, type_name, port, description):
    """Register a single service"""
    registration_data = {
        "service_name": name,
        "service_type": type_name,
        "port": port,
        "description": description,
        "metadata": {
            "category": type_name,
            "owner": "zmartbot",
            "critical": type_name in ["protection", "orchestration", "critical_infrastructure"],
            "auto_assigned": True
        }
    }
    
    try:
        print(f"🔄 Registering {name} (Port {port})...")
        response = requests.post(
            f"{PASSPORT_API_BASE}/register-public",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            passport_id = result.get("passport_id")
            print(f"✅ {name} → Passport ID: {passport_id}")
            return True
        elif response.status_code == 409:
            print(f"⚠️  {name} already registered")
            return True
        else:
            print(f"❌ Failed to register {name}: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error registering {name}: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 assign_passports_single.py <service_name> <service_type> <port> <description>")
        sys.exit(1)
    
    name = sys.argv[1]
    type_name = sys.argv[2]
    port = int(sys.argv[3])
    description = sys.argv[4]
    
    success = register_single_service(name, type_name, port, description)
    sys.exit(0 if success else 1)