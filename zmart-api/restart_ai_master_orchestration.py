#!/usr/bin/env python3
"""
Restart Master Orchestration Agent with AI Enhancements
Safely restarts the Master Orchestration Agent to enable AI features
"""

import os
import sys
import time
import signal
import requests
import subprocess
from pathlib import Path

def find_master_orchestration_process():
    """Find the current Master Orchestration Agent process"""
    try:
        result = subprocess.run(['pgrep', '-f', 'master_orchestration_agent'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pid = int(result.stdout.strip().split('\n')[0])
            print(f"📍 Found Master Orchestration Agent process: PID {pid}")
            return pid
    except:
        pass
    return None

def stop_current_agent(pid):
    """Stop the current Master Orchestration Agent"""
    try:
        print(f"🛑 Stopping Master Orchestration Agent (PID: {pid})...")
        os.kill(pid, signal.SIGTERM)
        
        # Wait for graceful shutdown
        for i in range(10):
            try:
                os.kill(pid, 0)  # Check if process still exists
                time.sleep(1)
                print(f"⏳ Waiting for shutdown... ({i+1}/10)")
            except ProcessLookupError:
                print("✅ Master Orchestration Agent stopped gracefully")
                return True
        
        # Force kill if needed
        try:
            os.kill(pid, signal.SIGKILL)
            print("⚡ Force stopped Master Orchestration Agent")
            return True
        except ProcessLookupError:
            print("✅ Master Orchestration Agent stopped")
            return True
            
    except Exception as e:
        print(f"❌ Error stopping agent: {e}")
        return False

def start_ai_enhanced_agent():
    """Start the AI-Enhanced Master Orchestration Agent"""
    try:
        print("🚀 Starting AI-Enhanced Master Orchestration Agent...")
        
        # Start as background process
        process = subprocess.Popen([
            sys.executable, 'master_orchestration_agent.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ AI-Enhanced Master Orchestration Agent started (PID: {process.pid})")
        
        # Wait a few seconds and check if it's responding
        time.sleep(5)
        
        try:
            response = requests.get('http://localhost:8002/health', timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                ai_active = health_data.get('ai_analytics_active', False)
                print(f"🌐 Master Orchestration Agent responding on port 8002")
                print(f"🧠 AI Analytics Active: {'✅' if ai_active else '❌'}")
                
                if ai_active:
                    print("🎉 AI-Enhanced Master Orchestration Agent successfully activated!")
                else:
                    print("⚠️ Master Orchestration Agent started but AI features may be initializing...")
                
                return True
            else:
                print(f"⚠️ Master Orchestration Agent responded with status: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"⚠️ Could not verify Master Orchestration Agent status: {e}")
            print("ℹ️ Agent may still be starting up...")
            return True
            
    except Exception as e:
        print(f"❌ Error starting AI-Enhanced Master Orchestration Agent: {e}")
        return False

def main():
    """Main restart process"""
    print("🔄 Restarting Master Orchestration Agent with AI Enhancements")
    print("="*60)
    
    # Find current process
    current_pid = find_master_orchestration_process()
    
    if current_pid:
        # Stop current agent
        if not stop_current_agent(current_pid):
            print("❌ Failed to stop current Master Orchestration Agent")
            return False
    else:
        print("ℹ️ No existing Master Orchestration Agent found")
    
    # Wait a moment for clean shutdown
    time.sleep(2)
    
    # Start AI-enhanced agent
    if start_ai_enhanced_agent():
        print("\n" + "="*60)
        print("🎉 AI-Enhanced Master Orchestration Agent is now running!")
        print("🧠 New AI Features Available:")
        print("   • Predictive analytics for service performance")
        print("   • ML-based failure prediction")
        print("   • Intelligent resource optimization") 
        print("   • Trading opportunity detection")
        print("\n🌐 New AI Endpoints:")
        print("   • http://localhost:8002/api/ai/intelligence")
        print("   • http://localhost:8002/api/ai/predictions")
        print("   • http://localhost:8002/api/ai/trading-opportunities")
        print("="*60)
        return True
    else:
        print("❌ Failed to start AI-Enhanced Master Orchestration Agent")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)