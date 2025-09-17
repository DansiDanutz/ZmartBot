#!/usr/bin/env python3
"""
ZmartBot Passport Assignment Script
Assigns Passport IDs to all registered services in the system
"""

import requests
import json
import time
from typing import Dict, List, Any

# Passport Service Configuration
PASSPORT_SERVICE_URL = "http://localhost:8620"
PASSPORT_API_BASE = f"{PASSPORT_SERVICE_URL}/api/passport"
PASSPORT_TOKEN = "zmartbot-passport-token"

# Services to register (from Master Orchestration Agent)
SERVICES_TO_REGISTER = [
    {"name": "system-protection-service", "type": "protection", "port": 8999, "description": "Critical system protection and security service"},
    {"name": "optimization-claude-service", "type": "optimization", "port": 8998, "description": "Advanced context optimization service"},
    {"name": "snapshot-service", "type": "critical_infrastructure", "port": 8085, "description": "Comprehensive disaster recovery and snapshot service"},
    {"name": "passport-service", "type": "backend", "port": 8620, "description": "Service registration and identity management"},
    {"name": "api-keys-manager-service", "type": "backend", "port": 8006, "description": "API key management and security service"},
    {"name": "binance", "type": "worker", "port": 8303, "description": "Binance exchange integration service"},
    {"name": "kingfisher-module", "type": "backend", "port": 8100, "description": "Advanced trading analysis and signal processing"},
    {"name": "kucoin", "type": "worker", "port": 8302, "description": "KuCoin exchange integration service"},
    {"name": "master-orchestration-agent", "type": "orchestration", "port": 8002, "description": "Central system orchestration controller"},
    {"name": "mdc-orchestration-agent", "type": "orchestration", "port": 8615, "description": "MDC documentation orchestration service"},
    {"name": "my-symbols-extended-service", "type": "backend", "port": 8005, "description": "Extended symbol management and analysis"},
    {"name": "mysymbols", "type": "internal_api", "port": 8201, "description": "Internal symbol management API"},
    {"name": "port-manager-service", "type": "orchestration", "port": 8610, "description": "Dynamic port allocation and management"},
    {"name": "test-analytics-service", "type": "backend", "port": 8003, "description": "Analytics testing and validation service"},
    {"name": "test-service", "type": "worker", "port": 8301, "description": "General testing and validation service"},
    {"name": "test-websocket-service", "type": "backend", "port": 8004, "description": "WebSocket testing and validation service"},
    {"name": "zmart-analytics", "type": "backend", "port": 8007, "description": "Advanced analytics and data processing"},
    {"name": "zmart-api", "type": "backend", "port": 8000, "description": "Main API server and trading platform core"},
    {"name": "zmart-dashboard", "type": "frontend", "port": 3400, "description": "Web dashboard and user interface"},
    {"name": "zmart-notification", "type": "backend", "port": 8008, "description": "Notification and alerting service"},
    {"name": "zmart-websocket", "type": "backend", "port": 8009, "description": "Real-time WebSocket communication service"},
    {"name": "zmart_alert_system", "type": "backend", "port": 8012, "description": "Alert system and notification management"},
    {"name": "zmart_backtesting", "type": "backend", "port": 8013, "description": "Trading strategy backtesting engine"},
    {"name": "zmart_data_warehouse", "type": "backend", "port": 8015, "description": "Data warehouse and storage management"},
    {"name": "zmart_machine_learning", "type": "backend", "port": 8014, "description": "Machine learning and AI processing"},
    {"name": "zmart_risk_management", "type": "backend", "port": 8010, "description": "Risk assessment and management system"},
    {"name": "zmart_technical_analysis", "type": "backend", "port": 8011, "description": "Technical analysis and indicator processing"}
]

def check_passport_service_health() -> bool:
    """Check if Passport Service is running and healthy"""
    try:
        response = requests.get(f"{PASSPORT_SERVICE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def register_service(service: Dict[str, Any]) -> Dict[str, Any]:
    """Register a single service and get its Passport ID"""
    registration_data = {
        "service_name": service["name"],
        "service_type": service["type"],
        "port": service["port"],
        "description": service.get("description", f"{service['name']} service"),
        "metadata": {
            "category": service["type"],
            "owner": "zmartbot",
            "critical": service["type"] in ["protection", "orchestration", "critical_infrastructure"],
            "auto_assigned": True
        }
    }
    
    try:
        print(f"🔄 Registering {service['name']} (Port {service['port']})...")
        # Use public endpoint for service registration
        response = requests.post(
            f"{PASSPORT_API_BASE}/register-public",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            passport_id = result.get("passport_id")
            print(f"✅ {service['name']} → Passport ID: {passport_id}")
            return {"success": True, "passport_id": passport_id, "service": service["name"]}
        elif response.status_code == 409:
            print(f"⚠️  {service['name']} already registered")
            return {"success": True, "passport_id": "EXISTING", "service": service["name"]}
        else:
            print(f"❌ Failed to register {service['name']}: {response.status_code} - {response.text}")
            return {"success": False, "error": response.text, "service": service["name"]}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error registering {service['name']}: {str(e)}")
        return {"success": False, "error": str(e), "service": service["name"]}

def get_all_registered_services() -> List[Dict[str, Any]]:
    """Get all currently registered services"""
    try:
        # Use public endpoint for basic stats
        response = requests.get(f"{PASSPORT_API_BASE}/services-public", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            return [{"count": stats["total_services"], "active": stats["active_services"], "types": stats["service_types"]}]
        else:
            print(f"❌ Failed to fetch registered services: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching services: {str(e)}")
        return []

def get_detailed_services() -> List[Dict[str, Any]]:
    """Get detailed service list (authenticated)"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {PASSPORT_TOKEN}"
        }
        response = requests.get(f"{PASSPORT_API_BASE}/services", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("services", [])
        else:
            print(f"❌ Failed to fetch detailed services: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching detailed services: {str(e)}")
        return []

def main():
    """Main passport assignment process"""
    print("🛂 ZmartBot Passport Assignment Script")
    print("=" * 50)
    
    # Check if Passport Service is running
    print("🔍 Checking Passport Service health...")
    if not check_passport_service_health():
        print("❌ Passport Service is not running or unreachable!")
        print("💡 Please start the service: ./start_passport_service.sh")
        return
    
    print("✅ Passport Service is healthy")
    print(f"📊 Found {len(SERVICES_TO_REGISTER)} services to register")
    print("-" * 50)
    
    # Register all services
    results = []
    successful = 0
    failed = 0
    
    for service in SERVICES_TO_REGISTER:
        result = register_service(service)
        results.append(result)
        
        if result["success"]:
            successful += 1
        else:
            failed += 1
        
        # Small delay between registrations
        time.sleep(0.5)
    
    print("-" * 50)
    print(f"📊 Registration Summary:")
    print(f"✅ Successfully registered: {successful}")
    print(f"❌ Failed registrations: {failed}")
    print(f"📋 Total services: {len(SERVICES_TO_REGISTER)}")
    
    # Show final status
    print("\n🔍 Fetching final registration status...")
    stats = get_all_registered_services()
    if stats and len(stats) > 0:
        service_stats = stats[0]
        print(f"📊 Total registered services in system: {service_stats['count']}")
        print(f"📊 Active services: {service_stats['active']}")
        print(f"📊 Service types: {service_stats['types']}")
    
    # Get detailed services if possible
    detailed_services = get_detailed_services()
    if detailed_services:
        print(f"\n🛂 Currently Registered Services ({len(detailed_services)}):")
        for service in detailed_services:
            status = "✅ ACTIVE" if service.get("status") == "ACTIVE" else "⏸️ PENDING"
            print(f"  {service.get('passport_id')} - {service.get('service_name')} ({service.get('service_type')}) - {status}")
    else:
        print("\n🔒 Detailed service list requires authentication (check logs for passport assignments)")
    
    print("\n🎉 Passport assignment process complete!")

if __name__ == "__main__":
    main()