#!/usr/bin/env python3
"""
ZmartBot Service Health Check Tool
Comprehensive health monitoring and diagnostics for all services
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime
from typing import Dict, List

# Colors for output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

async def check_service_health(name: str, port: int) -> Dict:
    """Check health of a single service"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            start_time = datetime.now()
            
            # Try common health endpoints
            endpoints = ['/health', '/status', '/ping', '/api/health', '/']
            for endpoint in endpoints:
                try:
                    response = await client.get(f"http://localhost:{port}{endpoint}")
                    response_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    if response.status_code == 200:
                        return {
                            "name": name,
                            "port": port,
                            "status": "healthy",
                            "endpoint": endpoint,
                            "response_time_ms": round(response_time, 2),
                            "status_code": response.status_code,
                            "last_check": datetime.now().isoformat()
                        }
                except Exception:
                    continue
            
            # If we get here, service is listening but no endpoint returned 200
            return {
                "name": name,
                "port": port,
                "status": "warning",
                "endpoint": "none_responding",
                "response_time_ms": round((datetime.now() - start_time).total_seconds() * 1000, 2),
                "status_code": None,
                "last_check": datetime.now().isoformat(),
                "message": "Service listening but no health endpoint responding with 200"
            }
            
    except Exception as e:
        return {
            "name": name,
            "port": port,
            "status": "error",
            "endpoint": None,
            "response_time_ms": None,
            "status_code": None,
            "last_check": datetime.now().isoformat(),
            "error": str(e)
        }

async def main():
    """Main health check function"""
    print(f"{Colors.BLUE}🏥 ZmartBot Service Health Check{Colors.NC}")
    print("=" * 50)
    
    # Get services from dashboard API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:3401/api/services")
            if response.status_code == 200:
                data = response.json()
                services = data.get("services", {})
                print(f"{Colors.GREEN}✅ Found {len(services)} configured services{Colors.NC}")
            else:
                print(f"{Colors.RED}❌ Could not fetch services from dashboard API{Colors.NC}")
                return
    except Exception as e:
        print(f"{Colors.RED}❌ Dashboard API not accessible: {e}{Colors.NC}")
        return
    
    print()
    
    # Check all services concurrently
    tasks = []
    for service_id, config in services.items():
        task = asyncio.create_task(
            check_service_health(config["name"], config["port"])
        )
        tasks.append(task)
    
    # Wait for all health checks
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process and display results
    healthy = []
    warning = []
    error = []
    
    print(f"{Colors.CYAN}📊 Service Health Results:{Colors.NC}")
    print("-" * 70)
    
    for result in results:
        if isinstance(result, Exception):
            error.append({"error": str(result)})
            continue
            
        status = result["status"]
        name = result["name"]
        port = result["port"]
        response_time = result.get("response_time_ms", "N/A")
        
        if status == "healthy":
            healthy.append(result)
            print(f"{Colors.GREEN}✅ {name:<25} Port {port:<5} {response_time}ms{Colors.NC}")
        elif status == "warning":
            warning.append(result)
            print(f"{Colors.YELLOW}⚠️  {name:<25} Port {port:<5} {result.get('message', 'Warning')}{Colors.NC}")
        else:
            error.append(result)
            print(f"{Colors.RED}❌ {name:<25} Port {port:<5} {result.get('error', 'Error')}{Colors.NC}")
    
    print()
    print(f"{Colors.CYAN}📈 Summary:{Colors.NC}")
    print(f"  {Colors.GREEN}Healthy: {len(healthy)}{Colors.NC}")
    print(f"  {Colors.YELLOW}Warning: {len(warning)}{Colors.NC}")
    print(f"  {Colors.RED}Error: {len(error)}{Colors.NC}")
    print(f"  {Colors.BLUE}Total: {len(results)}{Colors.NC}")
    
    health_percentage = (len(healthy) / len(results)) * 100 if results else 0
    print(f"  {Colors.PURPLE}Health: {health_percentage:.1f}%{Colors.NC}")
    
    # Show fastest and slowest services
    if healthy:
        fastest = min(healthy, key=lambda x: x["response_time_ms"])
        slowest = max(healthy, key=lambda x: x["response_time_ms"])
        print()
        print(f"{Colors.CYAN}⚡ Performance:{Colors.NC}")
        print(f"  Fastest: {fastest['name']} ({fastest['response_time_ms']}ms)")
        print(f"  Slowest: {slowest['name']} ({slowest['response_time_ms']}ms)")
    
    # Test dashboard API specifically
    print()
    print(f"{Colors.CYAN}🖥️  Dashboard API Test:{Colors.NC}")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Test main endpoints
            endpoints = [
                ("/health", "Health Check"),
                ("/api/services/status", "Services Status"),
                ("/api/system/stats", "System Stats")
            ]
            
            for endpoint, name in endpoints:
                try:
                    response = await client.get(f"http://localhost:3401{endpoint}")
                    if response.status_code == 200:
                        print(f"  {Colors.GREEN}✅ {name}{Colors.NC}")
                    else:
                        print(f"  {Colors.YELLOW}⚠️  {name} (HTTP {response.status_code}){Colors.NC}")
                except Exception as e:
                    print(f"  {Colors.RED}❌ {name} - {str(e)}{Colors.NC}")
                    
    except Exception as e:
        print(f"  {Colors.RED}❌ Dashboard API error: {e}{Colors.NC}")
    
    print()
    if health_percentage >= 90:
        print(f"{Colors.GREEN}🎉 System is healthy! All services operational.{Colors.NC}")
    elif health_percentage >= 70:
        print(f"{Colors.YELLOW}⚠️  System has some issues but is mostly operational.{Colors.NC}")
    else:
        print(f"{Colors.RED}🚨 System has significant health issues.{Colors.NC}")
    
    return health_percentage >= 70

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Health check interrupted.{Colors.NC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Health check failed: {e}{Colors.NC}")
        sys.exit(1)