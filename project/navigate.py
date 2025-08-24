#!/usr/bin/env python3
"""
🧭 ZmartBot Project Navigator
Professional project navigation and search tool
"""

import os
import sys
from pathlib import Path

class ZmartBotNavigator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.structure = {
            "🏗️ Backend": {
                "path": "backend/",
                "description": "Backend services and APIs",
                "key_files": [
                    "api/main.py - Main API server",
                    "api/professional_dashboard_server.py - Dashboard server",
                    "api/run_dev.py - Development runner"
                ]
            },
            "🎨 Frontend": {
                "path": "frontend/",
                "description": "Frontend applications",
                "key_files": [
                    "dashboard/ - Professional React dashboard",
                    "components/ - Reusable UI components"
                ]
            },
            "🧩 Modules": {
                "path": "modules/",
                "description": "Specialized modules",
                "key_files": [
                    "kingfisher/ - Liquidation analysis",
                    "alerts/ - Alert system",
                    "grok-x/ - AI sentiment analysis"
                ]
            },
            "📚 Documentation": {
                "path": "documentation/",
                "description": "All documentation",
                "key_files": [
                    "user-guides/ - User guides and tutorials",
                    "technical/ - Technical documentation"
                ]
            },
            "🔧 Scripts": {
                "path": "scripts/",
                "description": "Automation scripts",
                "key_files": [
                    "start_zmartbot_official.sh - Start platform",
                    "stop_zmartbot_official.sh - Stop platform"
                ]
            }
        }
    
    def show_structure(self):
        """Display the project structure"""
        print("🚀 ZmartBot Professional Project Structure")
        print("=" * 50)
        
        for section, info in self.structure.items():
            print(f"\n{section}")
            print(f"📁 Path: {info['path']}")
            print(f"📋 {info['description']}")
            print("🔑 Key Files:")
            for file in info['key_files']:
                print(f"   • {file}")
    
    def find_file(self, filename):
        """Find a file in the project"""
        print(f"🔍 Searching for '{filename}'...")
        matches = []
        
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if filename.lower() in file.lower():
                    rel_path = os.path.relpath(os.path.join(root, file), self.project_root)
                    matches.append(rel_path)
        
        if matches:
            print(f"✅ Found {len(matches)} matches:")
            for match in matches:
                print(f"   📄 {match}")
        else:
            print("❌ No matches found")
    
    def quick_access(self):
        """Show quick access commands"""
        print("⚡ Quick Access Commands:")
        print("=" * 30)
        print("🚀 Start Platform:")
        print("   cd project/scripts/ && ./start_zmartbot_official.sh")
        print("\n🛑 Stop Platform:")  
        print("   cd project/scripts/ && ./stop_zmartbot_official.sh")
        print("\n🔧 Backend Development:")
        print("   cd project/backend/api/ && python run_dev.py")
        print("\n🎨 Frontend Development:")
        print("   cd project/frontend/dashboard/ && npm run dev")
        print("\n🌐 Access Points:")
        print("   Dashboard: http://localhost:3400")
        print("   API: http://localhost:8000")

if __name__ == "__main__":
    nav = ZmartBotNavigator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "structure":
            nav.show_structure()
        elif command == "find" and len(sys.argv) > 2:
            nav.find_file(sys.argv[2])
        elif command == "quick":
            nav.quick_access()
        else:
            print("Usage: python navigate.py [structure|find <filename>|quick]")
    else:
        nav.show_structure()
        print("\n")
        nav.quick_access()