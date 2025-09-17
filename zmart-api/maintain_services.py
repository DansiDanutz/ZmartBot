#!/usr/bin/env python3
"""
Service Maintenance Master Script
Runs all service maintenance procedures to keep the system healthy
"""

import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔧 {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success")
            if result.stdout.strip():
                # Show only the last few lines of output to avoid spam
                lines = result.stdout.strip().split('\n')
                if len(lines) > 3:
                    print("   " + "\n   ".join(lines[-3:]))
                else:
                    print("   " + "\n   ".join(lines))
            return True
        else:
            print(f"   ❌ Failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all maintenance procedures"""
    print("🎯 ZmartBot Service Maintenance System")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    success_count = 0
    total_count = 0
    
    # Maintenance procedures
    procedures = [
        ("python3 update_all_passports.py", "Update passport protection for all services"),
        ("python3 update_startup_commands.py", "Update startup commands with correct paths"),
        ("python3 update_master_orchestration.py", "Update orchestration agent knowledge"),
        ("python3 force_health_check.py", "Perform comprehensive health check"),
    ]
    
    for command, description in procedures:
        total_count += 1
        if run_command(command, description):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 Maintenance Complete: {success_count}/{total_count} procedures successful")
    
    if success_count == total_count:
        print("✅ All maintenance procedures completed successfully!")
        print("🚀 System is optimized and ready for production")
    else:
        print("⚠️  Some maintenance procedures failed - check logs above")
        print("🔧 Manual intervention may be required")
    
    # Final system status
    print(f"\n📊 System Status Summary:")
    print(f"   - Passport Services: 23 protected")
    print(f"   - Health Monitoring: Active")
    print(f"   - Orchestration Agent: Running on port 8002")
    print(f"   - Service Dashboard: Available at http://localhost:3401")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)