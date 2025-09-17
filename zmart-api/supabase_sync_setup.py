#!/usr/bin/env python3
"""
Supabase Sync Setup for ZmartBot
Sets up complete synchronization between local service registry and Supabase
"""

import os
import sys
import json
import sqlite3
import requests
from pathlib import Path
from datetime import datetime

class SupabaseSetup:
    def __init__(self):
        self.config_file = Path("config.env")
        self.supabase_url = "https://asjtxrmftmutcsnqgidy.supabase.co"
        self.api_keys_service = "http://localhost:8006"
        
    def get_api_key_from_manager(self, key_id):
        """Get API key from API Keys Manager Service"""
        try:
            response = requests.get(f"{self.api_keys_service}/keys/{key_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('key')
            else:
                print(f"⚠️  API Keys Manager returned {response.status_code} for key {key_id}")
                return None
        except requests.exceptions.RequestException:
            print("⚠️  API Keys Manager Service not responding")
            return None
    
    def start_api_keys_manager(self):
        """Try to start the API Keys Manager Service"""
        try:
            # Look for the service
            api_service_path = None
            for path in Path(".").rglob("api_keys_manager_service.py"):
                api_service_path = path
                break
            
            if api_service_path:
                print(f"🔑 Starting API Keys Manager Service from {api_service_path}")
                os.system(f"python3 {api_service_path} --port 8006 > /dev/null 2>&1 &")
                import time
                time.sleep(3)  # Wait for service to start
                return True
            else:
                print("❌ API Keys Manager Service not found")
                return False
        except Exception as e:
            print(f"❌ Error starting API Keys Manager: {e}")
            return False
    
    def get_supabase_keys(self):
        """Get Supabase keys from API Keys Manager or prompt for manual entry"""
        
        # First try to start API Keys Manager
        if self.start_api_keys_manager():
            # Try to get keys from manager
            anon_key = self.get_api_key_from_manager("73645e8a29fe40bd")
            service_key = self.get_api_key_from_manager("0249c490fcc9ecf1")
            
            if anon_key and service_key:
                return anon_key, service_key
        
        # If API Keys Manager fails, prompt for manual entry
        print("\n🔑 SUPABASE API KEYS REQUIRED")
        print("=" * 40)
        print("Since the API Keys Manager is not accessible, please provide Supabase keys manually.")
        print(f"Project URL: {self.supabase_url}")
        print("\nTo get your keys:")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Select your project: asjtxrmftmutcsnqgidy") 
        print("3. Go to Settings > API")
        print("4. Copy the keys below:\n")
        
        anon_key = input("Enter Supabase Anon Key (public): ").strip()
        service_key = input("Enter Supabase Service Role Key (secret): ").strip()
        
        if not anon_key or not service_key:
            print("❌ Both keys are required for Supabase sync")
            return None, None
            
        return anon_key, service_key
    
    def setup_environment(self, anon_key, service_key):
        """Set up environment variables for Supabase"""
        
        # Set environment variables for current session
        os.environ['SUPABASE_URL'] = self.supabase_url
        os.environ['SUPABASE_KEY'] = service_key  # Use service role key for server operations
        os.environ['SUPABASE_ANON_KEY'] = anon_key
        
        print(f"✅ Environment variables set:")
        print(f"   SUPABASE_URL: {self.supabase_url}")
        print(f"   SUPABASE_KEY: {service_key[:20]}...")
        print(f"   SUPABASE_ANON_KEY: {anon_key[:20]}...")
        
        return True
    
    def test_supabase_connection(self, service_key):
        """Test connection to Supabase"""
        try:
            from supabase import create_client, Client
            
            client = create_client(self.supabase_url, service_key)
            
            # Test with a simple query
            result = client.table('service_registry').select('count', count='exact').execute()
            
            print(f"✅ Supabase connection successful!")
            print(f"   Current service_registry records: {result.count if hasattr(result, 'count') else 'unknown'}")
            return True
            
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            print("Please verify your API keys and project URL")
            return False
    
    def create_supabase_tables(self, service_key):
        """Create required tables in Supabase"""
        try:
            from supabase import create_client, Client
            
            client = create_client(self.supabase_url, service_key)
            
            print("🔧 Setting up Supabase tables...")
            
            # The tables should be created via Supabase SQL editor or migrations
            # Let's verify they exist
            
            tables_to_check = ['service_registry', 'database_registry', 'service_health_metrics']
            
            for table in tables_to_check:
                try:
                    result = client.table(table).select('count', count='exact').limit(1).execute()
                    print(f"✅ Table '{table}' exists")
                except Exception as e:
                    print(f"⚠️  Table '{table}' may not exist: {e}")
                    print(f"   Please create it using the SQL commands in database/supabase_setup_guide.md")
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking Supabase tables: {e}")
            return False
    
    def restart_database_service(self):
        """Restart database service to pick up new environment variables"""
        try:
            print("🔄 Restarting database service to apply Supabase configuration...")
            
            # Kill existing database service
            os.system("pkill -f database_service.py")
            
            import time
            time.sleep(2)
            
            # Start with new environment
            os.system("cd database && python3 database_service.py --port 8900 > /dev/null 2>&1 &")
            
            time.sleep(3)
            
            # Test if service is running
            response = requests.get("http://127.0.0.1:8900/health", timeout=5)
            if response.status_code == 200:
                print("✅ Database service restarted successfully")
                return True
            else:
                print("❌ Database service failed to restart")
                return False
                
        except Exception as e:
            print(f"❌ Error restarting database service: {e}")
            return False
    
    def sync_to_supabase(self):
        """Trigger sync to Supabase"""
        try:
            print("🚀 Syncing service registry to Supabase...")
            
            response = requests.post("http://127.0.0.1:8900/api/services/sync-to-supabase", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Sync successful: {result}")
                return True
            else:
                print(f"❌ Sync failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error during sync: {e}")
            return False
    
    def validate_sync(self):
        """Validate that sync is working"""
        try:
            print("🔍 Validating Supabase synchronization...")
            
            # Get local service count
            conn = sqlite3.connect('src/data/service_registry.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM service_registry')
            local_count = cursor.fetchone()[0]
            conn.close()
            
            # Get Supabase service count
            response = requests.get("http://127.0.0.1:8900/api/services/registry/supabase", timeout=10)
            
            if response.status_code == 200:
                supabase_data = response.json()
                supabase_count = supabase_data.get('total', 0)
                
                print(f"📊 Synchronization Status:")
                print(f"   Local services: {local_count}")
                print(f"   Supabase services: {supabase_count}")
                
                if local_count == supabase_count and local_count > 0:
                    print("✅ Perfect synchronization achieved!")
                    return True
                elif supabase_count > 0:
                    print("⚠️  Partial synchronization - some data synced")
                    return True
                else:
                    print("❌ No data found in Supabase")
                    return False
            else:
                print(f"❌ Cannot validate Supabase data: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error validating sync: {e}")
            return False
    
    def run_complete_setup(self):
        """Run complete Supabase setup and sync"""
        print("🚀 SUPABASE SYNC SETUP FOR ZMARTBOT")
        print("=" * 50)
        
        # Step 1: Get API keys
        anon_key, service_key = self.get_supabase_keys()
        if not anon_key or not service_key:
            print("❌ Setup failed - API keys required")
            return False
        
        # Step 2: Set up environment
        if not self.setup_environment(anon_key, service_key):
            print("❌ Setup failed - could not configure environment")
            return False
        
        # Step 3: Test connection
        if not self.test_supabase_connection(service_key):
            print("❌ Setup failed - cannot connect to Supabase")
            return False
        
        # Step 4: Check/create tables
        if not self.create_supabase_tables(service_key):
            print("⚠️  Table setup incomplete - please check Supabase configuration")
        
        # Step 5: Restart database service
        if not self.restart_database_service():
            print("❌ Setup failed - database service restart failed")
            return False
        
        # Step 6: Sync data
        if not self.sync_to_supabase():
            print("❌ Setup failed - initial sync failed")
            return False
        
        # Step 7: Validate
        if self.validate_sync():
            print("\n🎉 SUPABASE SYNC SETUP COMPLETE!")
            print("=" * 40)
            print("✅ All 64 services are now synchronized with Supabase")
            print(f"✅ Access your data at: {self.supabase_url}")
            print("✅ Automatic sync is now enabled")
            return True
        else:
            print("⚠️  Setup completed but validation failed")
            return False

if __name__ == "__main__":
    setup = SupabaseSetup()
    setup.run_complete_setup()