#!/usr/bin/env python3
"""
🔍 Comprehensive MDC System Diagnostic
Checks all MDC-related services, files, and orchestration health
"""

import os
import requests
import subprocess
import sqlite3
import json
from datetime import datetime
from pathlib import Path

def check_service_health(service_name, port, timeout=5):
    """Check if a service is responding to health checks"""
    try:
        url = f"http://localhost:{port}/health"
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)

def check_process_running(process_name):
    """Check if a process is running"""
    try:
        result = subprocess.run(['pgrep', '-f', process_name], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            return True, pids
        else:
            return False, []
    except Exception as e:
        return False, str(e)

def count_mdc_files():
    """Count MDC files in the system"""
    base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
    cursor_rules = os.path.join(base_path, ".cursor", "rules")
    
    if not os.path.exists(cursor_rules):
        return 0, []
    
    mdc_files = [f for f in os.listdir(cursor_rules) if f.endswith('.mdc')]
    return len(mdc_files), mdc_files

def check_database_services():
    """Check Level 3 services in database"""
    base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api"
    db_path = os.path.join(base_path, "src", "data", "service_registry.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT certification_level, COUNT(*) FROM service_registry GROUP BY certification_level")
        levels = dict(cursor.fetchall())
        
        cursor.execute("SELECT COUNT(*) FROM service_registry")
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_services': total,
            'level_1': levels.get(1, 0),
            'level_2': levels.get(2, 0),
            'level_3': levels.get(3, 0)
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    print("🔍 COMPREHENSIVE MDC SYSTEM DIAGNOSTIC")
    print("=" * 70)
    print(f"🕐 Diagnostic Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Check MDC-related processes
    print("1️⃣ PROCESS STATUS CHECK")
    print("-" * 40)
    
    mdc_processes = [
        'mdc_orchestration_agent.py',
        'background_mdc_agent.py', 
        'enhanced_mdc_monitor.py',
        'MDC-Dashboard'
    ]
    
    running_processes = []
    for process in mdc_processes:
        is_running, info = check_process_running(process)
        status = "✅ RUNNING" if is_running else "❌ STOPPED"
        pids = f"(PIDs: {', '.join(info)})" if is_running and isinstance(info, list) else ""
        print(f"   {process:<30} {status} {pids}")
        if is_running:
            running_processes.append(process)
    
    print(f"\n   📊 Running MDC Processes: {len(running_processes)}/{len(mdc_processes)}")
    print()
    
    # 2. Check MDC service health endpoints
    print("2️⃣ SERVICE HEALTH CHECK")
    print("-" * 40)
    
    mdc_services = [
        ('MDC Orchestration Agent', 8615),
        ('MDC Dashboard', 8090),
        ('Enhanced MDC Monitor', 8101),
        ('Background MDC Agent', 8091)
    ]
    
    healthy_services = 0
    for service_name, port in mdc_services:
        is_healthy, info = check_service_health(service_name.lower().replace(' ', '-'), port)
        status = "✅ HEALTHY" if is_healthy else "❌ UNHEALTHY"
        
        if is_healthy and isinstance(info, dict):
            details = f"({info.get('status', 'unknown')})"
        else:
            details = f"({info})" if not is_healthy else ""
            
        print(f"   {service_name:<25} Port {port} {status} {details}")
        if is_healthy:
            healthy_services += 1
    
    print(f"\n   📊 Healthy MDC Services: {healthy_services}/{len(mdc_services)}")
    print()
    
    # 3. Check MDC files
    print("3️⃣ MDC FILES ANALYSIS")
    print("-" * 40)
    
    mdc_count, mdc_files = count_mdc_files()
    print(f"   📁 Total MDC Files: {mdc_count}")
    
    if mdc_count > 0:
        # Check for recent modifications
        recent_files = []
        base_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/.cursor/rules"
        
        for mdc_file in mdc_files[:10]:  # Check first 10 files
            file_path = os.path.join(base_path, mdc_file)
            try:
                mod_time = os.path.getmtime(file_path)
                if (datetime.now().timestamp() - mod_time) < 3600:  # Modified within last hour
                    recent_files.append(mdc_file)
            except:
                pass
        
        print(f"   📝 Recently Modified (1hr): {len(recent_files)}")
        if recent_files:
            for rf in recent_files[:5]:
                print(f"      • {rf}")
    print()
    
    # 4. Check database services
    print("4️⃣ DATABASE SERVICES STATUS")
    print("-" * 40)
    
    db_status = check_database_services()
    if 'error' not in db_status:
        print(f"   📊 Total Services in Database: {db_status['total_services']}")
        print(f"   🔍 Level 1 (Discovery): {db_status['level_1']}")
        print(f"   🎫 Level 2 (Active): {db_status['level_2']}")
        print(f"   🏆 Level 3 (Certified): {db_status['level_3']}")
    else:
        print(f"   ❌ Database Error: {db_status['error']}")
    print()
    
    # 5. System Integration Check
    print("5️⃣ SYSTEM INTEGRATION STATUS")
    print("-" * 40)
    
    # Check if CLAUDE.md exists and is recent
    claude_md_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/CLAUDE.md"
    if os.path.exists(claude_md_path):
        mod_time = os.path.getmtime(claude_md_path)
        age = datetime.now().timestamp() - mod_time
        status = "✅ RECENT" if age < 300 else "⚠️ STALE" if age < 3600 else "❌ OLD"
        print(f"   CLAUDE.md Status: {status} (age: {age/60:.1f} minutes)")
    else:
        print("   CLAUDE.md Status: ❌ MISSING")
    
    # Check protection system
    protection_markers = len([f for f in os.listdir(".") if f.startswith(".protection_active_")])
    print(f"   Protection Markers: {protection_markers} active")
    
    print()
    
    # 6. Overall system health
    print("6️⃣ OVERALL MDC SYSTEM HEALTH")
    print("-" * 40)
    
    health_score = 0
    max_score = 4
    
    if len(running_processes) >= 3:
        health_score += 1
        print("   ✅ Process Health: Good (3+ processes running)")
    else:
        print("   ⚠️ Process Health: Degraded (some processes down)")
    
    if healthy_services >= 2:
        health_score += 1
        print("   ✅ Service Health: Good (2+ services responding)")
    else:
        print("   ❌ Service Health: Critical (services not responding)")
    
    if mdc_count >= 43:
        health_score += 1
        print("   ✅ File Health: Good (adequate MDC coverage)")
    else:
        print("   ⚠️ File Health: Degraded (insufficient MDC files)")
    
    if 'error' not in db_status and db_status['level_3'] >= 40:
        health_score += 1
        print("   ✅ Database Health: Good (40+ Level 3 services)")
    else:
        print("   ⚠️ Database Health: Needs attention")
    
    print()
    health_percentage = (health_score / max_score) * 100
    
    if health_percentage >= 90:
        overall_status = "🟢 EXCELLENT"
    elif health_percentage >= 70:
        overall_status = "🟡 GOOD"  
    elif health_percentage >= 50:
        overall_status = "🟠 DEGRADED"
    else:
        overall_status = "🔴 CRITICAL"
    
    print(f"   🎯 Overall MDC System Health: {overall_status} ({health_percentage:.0f}%)")
    
    # Recommendations
    print()
    print("💡 RECOMMENDATIONS")
    print("-" * 40)
    
    if len(running_processes) < 3:
        print("   • Restart failed MDC processes")
    if healthy_services < 2:
        print("   • Check network connectivity and service configurations")  
    if mdc_count < 43:
        print("   • Generate missing MDC files")
    if 'error' in db_status:
        print("   • Check database connectivity and integrity")
    
    if health_percentage == 100:
        print("   🏆 System is operating optimally!")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()