#!/usr/bin/env python3
"""
ServiceLog Client Example
Demonstrates how to integrate with the ServiceLog system
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Any

class ServiceLogClient:
    """Client for interacting with ServiceLog system"""
    
    def __init__(self, base_url: str = "http://localhost:8750", service_name: str = "demo-service"):
        self.base_url = base_url.rstrip('/')
        self.service_name = service_name
        self.session = requests.Session()
        
    def register_service(self, service_config: Dict[str, Any]) -> bool:
        """Register this service with ServiceLog"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/services/register",
                json=service_config,
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Service registered: {result}")
                return result.get('success', False)
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
            
    def send_log(self, level: str, message: str, context: Dict = None, metadata: Dict = None) -> bool:
        """Send a single log entry"""
        return self.send_logs([{
            'service_name': self.service_name,
            'timestamp': datetime.now().isoformat() + 'Z',
            'level': level,
            'message': message,
            'context': context or {},
            'metadata': metadata or {}
        }])
        
    def send_logs(self, logs: List[Dict]) -> bool:
        """Send multiple log entries"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/logs/ingest",
                json={'logs': logs},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                return result.get('success', False)
            else:
                print(f"❌ Log ingestion failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Log sending error: {e}")
            return False
            
    def get_priority_advice(self, limit: int = 10) -> List[Dict]:
        """Get prioritized advice for issues"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/advice",
                params={'limit': limit},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                return result.get('advice', [])
            else:
                print(f"❌ Failed to get advice: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Advice retrieval error: {e}")
            return []
            
    def resolve_advice(self, advice_id: str) -> bool:
        """Mark advice as resolved"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/advice/{advice_id}/resolve",
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                return result.get('success', False)
            else:
                print(f"❌ Failed to resolve advice: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Advice resolution error: {e}")
            return False
            
    def get_dashboard_summary(self) -> Dict:
        """Get dashboard summary statistics"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/advice/dashboard",
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                return result.get('summary', {})
            else:
                print(f"❌ Failed to get dashboard: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Dashboard error: {e}")
            return {}

def demo_integration():
    """Demonstrate ServiceLog integration"""
    print("🚀 ServiceLog Client Demo")
    print("=" * 50)
    
    # Initialize client
    client = ServiceLogClient(service_name="demo-service")
    
    # 1. Register service
    print("\n1️⃣ Registering service...")
    service_config = {
        "service_name": "demo-service",
        "service_type": "demo",
        "port": 9999,
        "criticality_level": "MEDIUM",
        "log_sources": ["/var/log/demo.log"],
        "health_endpoints": ["http://localhost:9999/health"],
        "expected_patterns": ["normal_operation", "user_request"],
        "alert_contacts": ["demo@example.com"]
    }
    
    if client.register_service(service_config):
        print("✅ Service registration successful")
    else:
        print("❌ Service registration failed")
        return
        
    # 2. Send some normal logs
    print("\n2️⃣ Sending normal logs...")
    for i in range(3):
        client.send_log("INFO", f"Normal operation {i+1}", {"user_id": f"user_{i+1}"})
    print("✅ Normal logs sent")
    
    # 3. Send error logs to trigger pattern detection
    print("\n3️⃣ Sending error logs to trigger pattern detection...")
    error_logs = []
    for i in range(8):  # Send enough errors to trigger pattern (threshold is 5)
        error_logs.append({
            'service_name': 'demo-service',
            'timestamp': datetime.now().isoformat() + 'Z',
            'level': 'ERROR',
            'message': f'Database connection failed - attempt {i+1}',
            'context': {'error_code': 'DB_CONN_001', 'retry_count': i+1},
            'metadata': {'version': '1.0.0'}
        })
    
    if client.send_logs(error_logs):
        print("✅ Error logs sent")
    else:
        print("❌ Error logs failed")
        
    # 4. Wait a moment for processing
    print("\n4️⃣ Waiting for log processing...")
    import time
    time.sleep(8)  # Wait for background processing
    
    # 5. Get generated advice
    print("\n5️⃣ Retrieving generated advice...")
    advice_list = client.get_priority_advice()
    
    if advice_list:
        print(f"📋 Generated {len(advice_list)} advice items:")
        for advice in advice_list:
            print(f"\n🔹 Advice ID: {advice['advice_id']}")
            print(f"   Title: {advice['title']}")
            print(f"   Severity: {advice['severity']}")
            print(f"   Priority Score: {advice['priority_score']}")
            print(f"   Category: {advice['category']}")
            print(f"   Affected Services: {advice['affected_services']}")
            print(f"   Status: {advice['status']}")
            
            # Show some resolution steps
            if advice.get('resolution_steps'):
                print(f"   Resolution Steps:")
                for step in advice['resolution_steps'][:3]:  # First 3 steps
                    print(f"     • {step}")
                    
            # Resolve the advice
            print(f"\n   🔄 Resolving advice {advice['advice_id']}...")
            if client.resolve_advice(advice['advice_id']):
                print("   ✅ Advice marked as resolved")
            else:
                print("   ❌ Failed to resolve advice")
    else:
        print("📋 No advice generated yet (may need more time for processing)")
        
    # 6. Get dashboard summary
    print("\n6️⃣ Getting dashboard summary...")
    summary = client.get_dashboard_summary()
    if summary:
        print("📊 Dashboard Summary:")
        print(f"   Status Distribution: {summary.get('status_distribution', {})}")
        print(f"   Severity Distribution: {summary.get('severity_distribution', {})}")
        print(f"   Average Priority: {summary.get('average_priority', 0)}")
        print(f"   Total Services: {summary.get('total_services', 0)}")
        print(f"   Buffer Size: {summary.get('buffer_size', 0)}")
    else:
        print("📊 Dashboard summary not available")
        
    print("\n✨ Demo completed!")

if __name__ == '__main__':
    demo_integration()