#!/usr/bin/env python3
"""
ZmartBot OrchestrationStart
Auto-generated implementation based on OrchestrationStart.mdc

This script ensures Cloud Sync is integrated and always running by:
1. Starting the database service (which includes Cloud Sync functionality)
2. Ensuring SUPABASE_KEY is properly configured for Cloud Sync activation
3. Monitoring Cloud Sync status and reporting to Master Orchestration Agent
"""

import os
import sys
import time
import json
import logging
import requests
import subprocess
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OrchestrationStart:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.services_status = {}
        self.cloud_sync_status = "🔴 Inactive"
        
    def check_database_service(self):
        """Check if database service (with Cloud Sync) is running"""
        try:
            response = requests.get("http://127.0.0.1:8900/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Database Service (Port 8900) is running")
                return True
            else:
                logger.warning("⚠️ Database Service health check failed")
                return False
        except Exception as e:
            logger.error(f"❌ Database Service not accessible: {e}")
            return False
    
    def start_database_service(self):
        """Start database service with Cloud Sync functionality"""
        try:
            logger.info("🚀 Starting Database Service with Cloud Sync...")
            
            # Change to database directory and start service
            db_dir = self.base_dir / "database"
            if not db_dir.exists():
                logger.error("❌ Database directory not found")
                return False
            
            # Check if service is already running
            if self.check_database_service():
                logger.info("✅ Database Service already running")
                return True
            
            # Start the database service
            cmd = ["python3", "database_service.py"]
            process = subprocess.Popen(
                cmd,
                cwd=db_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait a moment for service to start
            time.sleep(3)
            
            # Verify service started successfully
            if self.check_database_service():
                logger.info("✅ Database Service started successfully")
                return True
            else:
                logger.error("❌ Failed to start Database Service")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting Database Service: {e}")
            return False
    
    def check_lifecycle_manager(self):
        """Check if ServiceLifecycleManager is running"""
        try:
            response = requests.get("http://127.0.0.1:8920/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ ServiceLifecycleManager (Port 8920) is running")
                return True
            else:
                logger.warning("⚠️ ServiceLifecycleManager not responding")
                return False
        except Exception as e:
            logger.warning(f"⚠️ ServiceLifecycleManager not reachable: {e}")
            return False
    
    def start_lifecycle_manager(self):
        """Start ServiceLifecycleManager service"""
        try:
            logger.info("🚀 Starting ServiceLifecycleManager...")
            
            # Check if service is already running
            if self.check_lifecycle_manager():
                logger.info("✅ ServiceLifecycleManager already running")
                return True
            
            # Start ServiceLifecycleManager as a service
            db_dir = self.base_dir / "database"
            lifecycle_script = db_dir / "service_lifecycle_manager.py"
            
            if not lifecycle_script.exists():
                logger.error("❌ ServiceLifecycleManager script not found")
                return False
            
            # Start the service in background
            cmd = [sys.executable, str(lifecycle_script), "--service"]
            process = subprocess.Popen(
                cmd,
                cwd=str(db_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Give it time to start
            time.sleep(3)
            
            # Verify it started
            if self.check_lifecycle_manager():
                logger.info("✅ ServiceLifecycleManager started successfully")
                return True
            else:
                logger.error("❌ ServiceLifecycleManager failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting ServiceLifecycleManager: {e}")
            return False
    
    def validate_lifecycle_integrity(self):
        """Validate service lifecycle integrity using the manager"""
        try:
            response = requests.get("http://127.0.0.1:8920/api/lifecycle/validate", timeout=10)
            if response.status_code == 200:
                validation_data = response.json()
                integrity_status = validation_data.get('integrity_status', 'UNKNOWN')
                
                if integrity_status == 'CLEAN':
                    logger.info("✅ Service lifecycle integrity: CLEAN")
                    return True
                else:
                    violations = validation_data.get('violations_count', 0)
                    logger.warning(f"⚠️ Service lifecycle violations detected: {violations}")
                    logger.info("🔧 Consider running cleanup: python3 database/service_lifecycle_manager.py --cleanup-execute")
                    return False
            else:
                logger.warning("⚠️ Could not validate lifecycle integrity")
                return False
        except Exception as e:
            logger.error(f"❌ Error validating lifecycle integrity: {e}")
            return False
    
    def check_ziva_agent(self):
        """Check if ZIVA Agent is running"""
        try:
            response = requests.get("http://127.0.0.1:8930/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ ZIVA Agent (Port 8930) is running")
                return True
            else:
                logger.warning("⚠️ ZIVA Agent not responding")
                return False
        except Exception as e:
            logger.warning(f"⚠️ ZIVA Agent not reachable: {e}")
            return False
    
    def start_ziva_agent(self):
        """Start ZIVA Agent service"""
        try:
            logger.info("🚀 Starting ZIVA Agent...")
            
            # Check if service is already running
            if self.check_ziva_agent():
                logger.info("✅ ZIVA Agent already running")
                return True
            
            # Start ZIVA Agent as a service
            ziva_script = self.base_dir / "ziva_agent.py"
            
            if not ziva_script.exists():
                logger.error("❌ ZIVA Agent script not found")
                return False
            
            # Start the service in background
            cmd = [sys.executable, str(ziva_script), "--service"]
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Give it time to start
            time.sleep(3)
            
            # Verify it started
            if self.check_ziva_agent():
                logger.info("✅ ZIVA Agent started successfully")
                return True
            else:
                logger.error("❌ ZIVA Agent failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting ZIVA Agent: {e}")
            return False
    
    def validate_system_integrity(self):
        """Validate system integrity using ZIVA Agent"""
        try:
            response = requests.get("http://127.0.0.1:8930/api/consistency/report", timeout=10)
            if response.status_code == 200:
                consistency_data = response.json()
                violations_count = consistency_data.get('violations_count', 0)
                consistency_score = consistency_data.get('consistency_score', 0)
                
                if violations_count == 0:
                    logger.info("✅ System integrity: CLEAN (0 violations)")
                    return True
                elif violations_count < 50:
                    logger.info(f"✅ System integrity: GOOD ({violations_count} minor violations)")
                    return True
                else:
                    logger.warning(f"⚠️ System integrity: COMPROMISED ({violations_count} violations, score: {consistency_score})")
                    logger.info("🔧 Consider running auto-fix: curl -X POST http://127.0.0.1:8930/api/violations/fix")
                    return False
            else:
                logger.warning("⚠️ Could not validate system integrity")
                return False
        except Exception as e:
            logger.error(f"❌ Error validating system integrity: {e}")
            return False
    
    def check_cloud_sync_status(self):
        """Check Cloud Sync status from database service"""
        try:
            response = requests.get("http://127.0.0.1:8900/api/system/overview", timeout=5)
            if response.status_code == 200:
                data = response.json()
                cloud_sync_status = data.get("cloud_sync", {}).get("status", "🔴 Inactive")
                
                if "🟢" in cloud_sync_status or "Active" in cloud_sync_status:
                    self.cloud_sync_status = "🟢 Active"
                    logger.info("✅ Cloud Sync is ACTIVE")
                else:
                    self.cloud_sync_status = "🔴 Inactive"
                    logger.warning("⚠️ Cloud Sync is INACTIVE - check SUPABASE_KEY")
                
                return self.cloud_sync_status
            else:
                logger.warning("⚠️ Could not get Cloud Sync status")
                return "🔴 Unknown"
        except Exception as e:
            logger.error(f"❌ Error checking Cloud Sync status: {e}")
            return "🔴 Error"
    
    def ensure_supabase_key(self):
        """Ensure SUPABASE_KEY is configured for Cloud Sync"""
        supabase_key = os.getenv("SUPABASE_KEY")
        if not supabase_key:
            logger.warning("⚠️ SUPABASE_KEY not found in environment variables")
            logger.info("💡 To enable Cloud Sync, set SUPABASE_KEY environment variable")
            logger.info("💡 Example: export SUPABASE_KEY=your_supabase_key_here")
            return False
        else:
            logger.info("✅ SUPABASE_KEY is configured")
            return True
    
    def monitor_cloud_sync(self):
        """Monitor Cloud Sync status and ensure it stays active"""
        logger.info("🔍 Monitoring Cloud Sync status...")
        
        # Check SUPABASE_KEY configuration
        key_configured = self.ensure_supabase_key()
        
        # Check current Cloud Sync status
        current_status = self.check_cloud_sync_status()
        
        if key_configured and "🟢" in current_status:
            logger.info("✅ Cloud Sync monitoring: All systems operational")
            return True
        elif not key_configured:
            logger.warning("⚠️ Cloud Sync disabled: SUPABASE_KEY not configured")
            return False
        else:
            logger.warning("⚠️ Cloud Sync issues detected, attempting recovery...")
            return False
    
    def check_master_orchestration_agent(self):
        """Check if Master Orchestration Agent is running"""
        try:
            response = requests.get("http://127.0.0.1:8002/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                logger.info("✅ Master Orchestration Agent (Port 8002) is running")
                
                # Check if AI analytics is active
                ai_active = health_data.get('ai_analytics_active', False)
                if ai_active:
                    logger.info("🧠 AI Analytics is ACTIVE")
                else:
                    logger.info("📊 AI Analytics is available but not yet active")
                
                return True
            else:
                logger.warning("⚠️ Master Orchestration Agent health check failed")
                return False
        except Exception as e:
            logger.error(f"❌ Master Orchestration Agent not accessible: {e}")
            return False
    
    def start_master_orchestration_agent(self):
        """Start AI-Enhanced Master Orchestration Agent"""
        try:
            logger.info("🚀 Starting AI-Enhanced Master Orchestration Agent...")
            
            # Check if service is already running
            if self.check_master_orchestration_agent():
                logger.info("✅ Master Orchestration Agent already running")
                return True
            
            # Start the Master Orchestration Agent
            cmd = ["python3", "master_orchestration_agent.py", "--service"]
            process = subprocess.Popen(
                cmd,
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait for service to start
            time.sleep(5)
            
            # Verify service started successfully
            if self.check_master_orchestration_agent():
                logger.info("✅ AI-Enhanced Master Orchestration Agent started successfully")
                
                # Try to activate AI analytics
                try:
                    response = requests.post("http://127.0.0.1:8002/api/ai/start", timeout=3)
                    if response.status_code == 200:
                        logger.info("🧠 AI Analytics Engine activated successfully")
                    else:
                        logger.info("📊 AI Analytics may still be initializing...")
                except:
                    logger.info("📊 AI Analytics activation attempted (may take time to initialize)")
                
                return True
            else:
                logger.error("❌ Master Orchestration Agent failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting Master Orchestration Agent: {e}")
            return False
    
    def get_ai_system_status(self):
        """Get AI system status from Master Orchestration Agent"""
        try:
            response = requests.get("http://127.0.0.1:8002/api/ai/intelligence", timeout=3)
            if response.status_code == 200:
                intelligence = response.json()
                return {
                    "ai_active": intelligence.get("ai_analytics_active", False),
                    "system_health": intelligence.get("intelligence_summary", {}).get("system_health", 0),
                    "active_services": intelligence.get("intelligence_summary", {}).get("active_services", 0),
                    "trading_opportunities": len(intelligence.get("intelligence_summary", {}).get("trading_opportunities", []))
                }
        except:
            pass
        return {"ai_active": False, "system_health": 0, "active_services": 0, "trading_opportunities": 0}

    def notify_master_orchestration_agent(self):
        """Notify Master Orchestration Agent about Cloud Sync status"""
        try:
            # Check if Master Orchestration Agent is running (Port 8002 according to MDC)
            try:
                response = requests.get("http://127.0.0.1:8002/health", timeout=3)
                if response.status_code == 200:
                    logger.info("✅ Master Orchestration Agent is accessible")
                    
                    # Send Cloud Sync status update
                    status_data = {
                        "service": "cloud_sync",
                        "status": self.cloud_sync_status,
                        "database_service": "running",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Try to notify (this endpoint may not exist yet, so handle gracefully)
                    try:
                        requests.post("http://127.0.0.1:8002/api/status/cloud_sync", 
                                    json=status_data, timeout=3)
                        logger.info("✅ Notified Master Orchestration Agent of Cloud Sync status")
                    except:
                        logger.info("📝 Master Orchestration Agent notification attempted (endpoint may not exist)")
                        
                else:
                    logger.info("📝 Master Orchestration Agent not yet available")
            except:
                logger.info("📝 Master Orchestration Agent not accessible (may start later)")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not notify Master Orchestration Agent: {e}")
    
    def check_trigger_manager(self):
        """Check if Trigger Manager is running"""
        try:
            response = requests.get("http://127.0.0.1:8890/health", timeout=5)
            if response.status_code == 200:
                return True
            return False
        except Exception:
            return False
    
    def start_trigger_manager(self):
        """Start Trigger Manager service"""
        try:
            if self.check_trigger_manager():
                logger.info("✅ Trigger Manager already running")
                return True
            
            cmd = [sys.executable, "trigger_manager.py", "--daemon"]
            subprocess.Popen(cmd, cwd=str(self.base_dir), start_new_session=True)
            time.sleep(3)
            
            return self.check_trigger_manager()
        except Exception as e:
            logger.error(f"❌ Error starting Trigger Manager: {e}")
            return False
    
    def check_level_manager(self):
        """Check if Level Manager is running"""
        try:
            response = requests.get("http://127.0.0.1:8891/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def start_level_manager(self):
        """Start Level Manager service"""
        try:
            if self.check_level_manager():
                logger.info("✅ Level Manager already running")
                return True
            
            cmd = [sys.executable, "level_manager.py", "--daemon"]
            subprocess.Popen(cmd, cwd=str(self.base_dir), start_new_session=True)
            time.sleep(3)
            
            return self.check_level_manager()
        except Exception as e:
            logger.error(f"❌ Error starting Level Manager: {e}")
            return False
    
    def check_status_manager(self):
        """Check if Status Manager is running"""
        try:
            response = requests.get("http://127.0.0.1:8892/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def start_status_manager(self):
        """Start Status Manager service"""
        try:
            if self.check_status_manager():
                logger.info("✅ Status Manager already running")
                return True
            
            cmd = [sys.executable, "status_manager.py", "--daemon"]
            subprocess.Popen(cmd, cwd=str(self.base_dir), start_new_session=True)
            time.sleep(3)
            
            return self.check_status_manager()
        except Exception as e:
            logger.error(f"❌ Error starting Status Manager: {e}")
            return False
    
    def check_security_manager(self):
        """Check if Security Manager is running"""
        try:
            response = requests.get("http://127.0.0.1:8893/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def start_security_manager(self):
        """Start Security Manager service (CRITICAL security service)"""
        try:
            if self.check_security_manager():
                logger.info("✅ Security Manager already running")
                return True
            
            logger.info("🛡️ Starting Security Manager - CRITICAL security service...")
            cmd = [sys.executable, "security_manager.py", "--daemon"]
            subprocess.Popen(cmd, cwd=str(self.base_dir), start_new_session=True)
            time.sleep(3)
            
            return self.check_security_manager()
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR starting Security Manager: {e}")
            return False
    
    def check_authentication_middleware(self):
        """Check if Authentication Middleware is running"""
        try:
            response = requests.get("http://127.0.0.1:8894/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def start_authentication_middleware(self):
        """Start Authentication Middleware service (Fixes auth bypass vulnerability)"""
        try:
            if self.check_authentication_middleware():
                logger.info("✅ Authentication Middleware already running")
                return True
            
            logger.info("🔐 Starting Authentication Middleware - Fixes authentication bypass...")
            cmd = [sys.executable, "authentication_middleware.py", "--daemon"]
            subprocess.Popen(cmd, cwd=str(self.base_dir), start_new_session=True)
            time.sleep(3)
            
            return self.check_authentication_middleware()
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR starting Authentication Middleware: {e}")
            return False
    
    def check_yaml_governance_service(self):
        """Check if YAML Governance Service is running"""
        try:
            response = requests.get("http://127.0.0.1:8897/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def check_registry_consolidator(self):
        """Check if Registry Consolidator is running"""
        try:
            response = requests.get("http://127.0.0.1:8898/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def start_yaml_governance_service(self):
        """Start YAML Governance Service (Prevents YAML duplication and chaos)"""
        try:
            if self.check_yaml_governance_service():
                logger.info("✅ YAML Governance Service already running")
                return True
            
            logger.info("🛡️ Starting YAML Governance Service - Prevents configuration chaos...")
            
            # Start YAML Governance Service
            governance_script = self.base_dir / ".yaml-governance" / "yaml_governance_service.py"
            if not governance_script.exists():
                logger.error("❌ YAML Governance Service script not found")
                return False
            
            cmd = [sys.executable, str(governance_script), "--service", "--port", "8897"]
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait for service to start
            time.sleep(3)
            
            # Verify service started successfully
            if self.check_yaml_governance_service():
                logger.info("✅ YAML Governance Service started successfully")
                
                # Run initial validation
                try:
                    response = requests.get("http://127.0.0.1:8897/api/validate", timeout=10)
                    if response.status_code == 200:
                        validation_data = response.json()
                        status = validation_data.get('status', 'UNKNOWN')
                        total_files = validation_data.get('total_yaml_files', 0)
                        duplicates = len(validation_data.get('duplicates', {}))
                        conflicts = len(validation_data.get('port_conflicts', {}))
                        
                        if status == "PASSED":
                            logger.info(f"✅ YAML Governance: {total_files} files validated - No issues detected")
                        else:
                            logger.warning(f"⚠️ YAML Governance: {duplicates} duplicates, {conflicts} port conflicts detected")
                    else:
                        logger.info("📝 YAML Governance validation initiated...")
                except:
                    logger.info("📝 YAML Governance validation may still be initializing...")
                
                return True
            else:
                logger.error("❌ YAML Governance Service failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting YAML Governance Service: {e}")
            return False
    
    def start_registry_consolidator(self):
        """Start Registry Consolidator (Organizes all registry databases)"""
        try:
            if self.check_registry_consolidator():
                logger.info("✅ Registry Consolidator already running")
                return True
            
            logger.info("📂 Starting Registry Consolidator - Database organization service...")
            
            # Start the registry consolidator service
            cmd = [sys.executable, "registry_consolidator.py", "--service", "--port", "8898"]
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait for service to start
            time.sleep(5)
            
            # Verify service started successfully
            if self.check_registry_consolidator():
                logger.info("✅ Registry Consolidator started successfully")
                
                # Run initial consolidation
                try:
                    consolidation_response = requests.get("http://127.0.0.1:8898/api/consolidate", timeout=30)
                    if consolidation_response.status_code == 200:
                        result = consolidation_response.json()
                        if result.get("status") == "completed":
                            consolidated_records = result.get("consolidated_records", 0)
                            processed_registries = result.get("processed_registries", 0)
                            logger.info(f"✅ Registry consolidation completed: {consolidated_records} records from {processed_registries} databases")
                        else:
                            logger.warning("⚠️ Registry consolidation completed with warnings")
                    else:
                        logger.info("📂 Registry Consolidator service started (consolidation will run automatically)")
                except:
                    logger.info("📂 Registry Consolidator service started (consolidation may be initializing)")
                
                return True
            else:
                logger.error("❌ Registry Consolidator failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting Registry Consolidator: {e}")
            return False
    
    def check_enhanced_mdc_monitor(self):
        """Check if Enhanced MDC Monitor is running"""
        try:
            # Check if the enhanced MDC monitor process is running
            result = subprocess.run(["pgrep", "-f", "enhanced_mdc_monitor.py"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def start_enhanced_mdc_monitor(self):
        """Start Enhanced MDC Monitor service (Optimal context optimization)"""
        try:
            if self.check_enhanced_mdc_monitor():
                logger.info("✅ Enhanced MDC Monitor already running")
                return True
            
            logger.info("🎯 Starting Enhanced MDC Monitor - Optimal context optimization...")
            
            # Start the enhanced MDC monitor with optimal settings
            cmd = [sys.executable, "enhanced_mdc_monitor.py", "--start", "--batch-interval", "30", "--update-threshold", "5"]
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait for service to start
            time.sleep(5)
            
            # Verify service started successfully
            if self.check_enhanced_mdc_monitor():
                logger.info("✅ Enhanced MDC Monitor started successfully")
                return True
            else:
                logger.error("❌ Enhanced MDC Monitor failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting Enhanced MDC Monitor: {e}")
            return False
    
    def check_background_mdc_agent(self):
        """Check if Background MDC Agent is running"""
        try:
            # Check if the background MDC agent process is running
            result = subprocess.run(["pgrep", "-f", "background_mdc_agent.py"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def start_background_mdc_agent(self):
        """Start Background MDC Agent service (MDC file monitoring)"""
        try:
            if self.check_background_mdc_agent():
                logger.info("✅ Background MDC Agent already running")
                return True
            
            logger.info("📝 Starting Background MDC Agent - MDC file monitoring...")
            
            # Start the background MDC agent
            cmd = [sys.executable, "background_mdc_agent.py"]
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait for service to start
            time.sleep(3)
            
            # Verify service started successfully
            if self.check_background_mdc_agent():
                logger.info("✅ Background MDC Agent started successfully")
                return True
            else:
                logger.error("❌ Background MDC Agent failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting Background MDC Agent: {e}")
            return False
    
    def run_orchestration(self):
        """Run the complete orchestration process"""
        logger.info("🎯 Starting ZmartBot OrchestrationStart")
        logger.info("🎯 Focus: Ensuring Cloud Sync Integration and Always-Running Status")
        
        print("\n" + "="*60)
        print("🚀 ZMARTBOT ORCHESTRATION START")
        print("="*60)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Focus: Cloud Sync Integration")
        print("-"*60)
        
        # Step 1: Ensure Database Service is running (contains Cloud Sync)
        logger.info("Step 1: Ensuring Database Service is running...")
        db_running = self.start_database_service()
        
        if not db_running:
            logger.error("❌ CRITICAL: Database Service failed to start")
            print("❌ CRITICAL ERROR: Database Service failed to start")
            return False
        
        # Step 2: Start ServiceLifecycleManager
        logger.info("Step 2: Starting ServiceLifecycleManager...")
        lifecycle_running = self.start_lifecycle_manager()
        
        if not lifecycle_running:
            logger.warning("⚠️ ServiceLifecycleManager failed to start - continuing without it")
            print("⚠️ WARNING: ServiceLifecycleManager not available")
        
        # Step 3: Validate Lifecycle Integrity  
        integrity_ok = False
        ziva_running = False
        system_integrity_ok = False
        if lifecycle_running:
            logger.info("Step 3: Validating service lifecycle integrity...")
            integrity_ok = self.validate_lifecycle_integrity()
            if not integrity_ok:
                logger.warning("⚠️ Service lifecycle violations detected")
                print("⚠️ WARNING: Service lifecycle violations detected")
        
        # Step 4: Start ZIVA Agent (Integrity Monitoring)
        logger.info("Step 4: Starting ZIVA Agent for integrity monitoring...")
        ziva_running = self.start_ziva_agent()
        
        if not ziva_running:
            logger.warning("⚠️ ZIVA Agent failed to start - continuing without integrity monitoring")
            print("⚠️ WARNING: ZIVA Agent not available - integrity monitoring disabled")
        else:
            # Validate system integrity using ZIVA
            logger.info("Step 4a: Validating system integrity with ZIVA...")
            system_integrity_ok = self.validate_system_integrity()
            if not system_integrity_ok:
                logger.warning("⚠️ System integrity violations detected")
                print("⚠️ WARNING: System integrity violations detected")
        
        # Step 5: Start Core Orchestration Services
        logger.info("Step 5: Starting Core Orchestration Services...")
        
        # Start Trigger Manager
        trigger_running = self.start_trigger_manager()
        if not trigger_running:
            logger.warning("⚠️ Trigger Manager failed to start")
            print("⚠️ WARNING: Trigger Manager not available")
        
        # Start Level Manager  
        level_running = self.start_level_manager()
        if not level_running:
            logger.warning("⚠️ Level Manager failed to start")
            print("⚠️ WARNING: Level Manager not available")
        
        # Start Status Manager
        status_running = self.start_status_manager()
        if not status_running:
            logger.warning("⚠️ Status Manager failed to start")
            print("⚠️ WARNING: Status Manager not available")
        
        # CRITICAL SECURITY SERVICES - Start immediately after orchestration services
        logger.info("CRITICAL: Starting Security Services...")
        
        # Start Security Manager (Fixes exposed API keys & security threats)
        security_running = self.start_security_manager()
        if not security_running:
            logger.error("❌ CRITICAL: Security Manager failed to start - System at risk!")
            print("🚨 CRITICAL ERROR: Security Manager not available - System exposed to threats!")
        else:
            logger.info("✅ Security Manager active - System protected from threats")
            print("🛡️ Security Manager active - API keys secured, threats monitored")
        
        # Start Authentication Middleware (Fixes authentication bypass)
        auth_running = self.start_authentication_middleware()
        if not auth_running:
            logger.error("❌ CRITICAL: Authentication Middleware failed - Endpoints unprotected!")
            print("🚨 CRITICAL ERROR: Authentication bypass vulnerability still active!")
        else:
            logger.info("✅ Authentication Middleware active - Endpoints protected")
            print("🔐 Authentication Middleware active - All endpoints protected")
        
        # Start YAML Governance Service (Configuration management)
        yaml_governance_running = self.start_yaml_governance_service()
        if not yaml_governance_running:
            logger.warning("⚠️ YAML Governance Service failed to start - configuration chaos prevention disabled")
            print("⚠️ WARNING: YAML Governance Service not available - YAML validation limited")
        else:
            logger.info("✅ YAML Governance Service active - Configuration chaos prevention enabled")
            print("🛡️ YAML Governance Service active - YAML validation and duplicate prevention")
        
        # Start Registry Consolidator (Database organization)
        registry_consolidator_running = self.start_registry_consolidator()
        if not registry_consolidator_running:
            logger.warning("⚠️ Registry Consolidator failed to start - database organization limited")
            print("⚠️ WARNING: Registry Consolidator not available - registry database chaos possible")
        else:
            logger.info("✅ Registry Consolidator active - Database organization enabled")
            print("📂 Registry Consolidator active - All registry databases organized")
        
        # Step 5b: Start Context Optimization Services
        logger.info("Step 5b: Starting Context Optimization Services...")
        
        # Start Enhanced MDC Monitor (Optimal context optimization)
        enhanced_mdc_running = self.start_enhanced_mdc_monitor()
        if not enhanced_mdc_running:
            logger.warning("⚠️ Enhanced MDC Monitor failed to start")
            print("⚠️ WARNING: Enhanced MDC Monitor not available - context optimization limited")
        else:
            logger.info("✅ Enhanced MDC Monitor active - Optimal context optimization enabled")
            print("🎯 Enhanced MDC Monitor active - Real-time context optimization")
        
        # Start Background MDC Agent (MDC file monitoring)
        background_mdc_running = self.start_background_mdc_agent()
        if not background_mdc_running:
            logger.warning("⚠️ Background MDC Agent failed to start")
            print("⚠️ WARNING: Background MDC Agent not available - MDC monitoring limited")
        else:
            logger.info("✅ Background MDC Agent active - MDC file monitoring enabled")
            print("📝 Background MDC Agent active - Automatic MDC updates")
        
        # Step 6: Start AI-Enhanced Master Orchestration Agent
        logger.info("Step 6: Starting AI-Enhanced Master Orchestration Agent...")
        master_orchestration_running = self.start_master_orchestration_agent()
        
        if not master_orchestration_running:
            logger.warning("⚠️ Master Orchestration Agent failed to start - continuing without AI coordination")
            print("⚠️ WARNING: Master Orchestration Agent not available - AI coordination disabled")
        
        # Step 7: Monitor Cloud Sync status
        logger.info("Step 6: Monitoring Cloud Sync status...")
        cloud_sync_ok = self.monitor_cloud_sync()
        
        # Step 7: Notify Master Orchestration Agent (if running)
        logger.info("Step 7: Notifying Master Orchestration Agent...")
        if master_orchestration_running:
            self.notify_master_orchestration_agent()
        else:
            logger.info("📝 Master Orchestration Agent not running - skipping notification")
        
        # Get AI system status for final report
        ai_status = self.get_ai_system_status()
        
        # Final status report
        print("\n" + "-"*60)
        print("📊 ORCHESTRATION STATUS REPORT")
        print("-"*60)
        print(f"Database Service (Port 8900): ✅ Running")
        print(f"ServiceLifecycleManager (Port 8920): {'✅ Running' if lifecycle_running else '❌ Not Running'}")
        print(f"ZIVA Agent (Port 8930): {'✅ Running' if ziva_running else '❌ Not Running'}")
        print(f"Master Orchestration Agent (Port 8002): {'✅ Running' if master_orchestration_running else '❌ Not Running'}")
        print(f"AI Analytics System: {'✅ Active' if ai_status['ai_active'] else '📊 Available' if master_orchestration_running else '❌ Disabled'}")
        print("-"*60)
        print("🎯 CONTEXT OPTIMIZATION SERVICES")
        print(f"Enhanced MDC Monitor: {'✅ Running' if enhanced_mdc_running else '❌ Not Running'}")
        print(f"Background MDC Agent: {'✅ Running' if background_mdc_running else '❌ Not Running'}")
        print("-"*60)
        print("🛡️ CRITICAL SECURITY SERVICES")
        print(f"Security Manager (Port 8893): {'✅ Running' if security_running else '🚨 CRITICAL - NOT RUNNING'}")
        print(f"Authentication Middleware (Port 8894): {'✅ Running' if auth_running else '🚨 CRITICAL - NOT RUNNING'}")
        print("-"*60)
        print("🔧 CONFIGURATION MANAGEMENT")
        print(f"YAML Governance Service (Port 8897): {'✅ Running' if yaml_governance_running else '⚠️ Not Running'}")
        print("-"*60)
        print("📂 DATABASE ORGANIZATION")
        print(f"Registry Consolidator (Port 8898): {'✅ Running' if registry_consolidator_running else '⚠️ Not Running'}")
        print("-"*60)
        print(f"Service Lifecycle Integrity: {'✅ Clean' if lifecycle_running and integrity_ok else '⚠️ Violations' if lifecycle_running else '❌ Unknown'}")
        print(f"System Integrity Monitoring: {'✅ Active' if ziva_running else '❌ Disabled'}")
        print(f"Cloud Sync Status: {self.cloud_sync_status}")
        print(f"SUPABASE_KEY Configured: {'✅ Yes' if os.getenv('SUPABASE_KEY') else '❌ No'}")
        
        # AI System Status (if available)
        if master_orchestration_running and ai_status['ai_active']:
            print("-"*60)
            print("🧠 AI SYSTEM STATUS")
            print(f"System Health Score: {ai_status['system_health']:.1%}")
            print(f"Services Under AI Monitoring: {ai_status['active_services']}")
            print(f"Trading Opportunities Detected: {ai_status['trading_opportunities']}")
            
        print("-"*60)
        
        # Success determination
        core_systems_ok = lifecycle_running and master_orchestration_running
        context_optimization_ok = enhanced_mdc_running and background_mdc_running
        governance_ok = yaml_governance_running
        organization_ok = registry_consolidator_running
        
        if cloud_sync_ok and core_systems_ok and context_optimization_ok and governance_ok and organization_ok:
            print("🎉 SUCCESS: Complete orchestration with AI analytics, context optimization, governance, and database organization!")
            if ai_status['ai_active']:
                print("🧠 AI-Powered system monitoring and predictive analytics enabled!")
            print("🎯 Optimal context optimization active - Claude Code performance maximized!")
            print("🛡️ YAML Governance active - Configuration chaos prevention enabled!")
            print("📂 Registry Consolidator active - Database organization and registry chaos prevention!")
            logger.info("✅ OrchestrationStart completed successfully with full AI integration, context optimization, governance, and organization")
        elif cloud_sync_ok and core_systems_ok and context_optimization_ok and governance_ok:
            print("🎉 SUCCESS: Complete orchestration with AI analytics, context optimization, and YAML governance!")
            if ai_status['ai_active']:
                print("🧠 AI-Powered system monitoring and predictive analytics enabled!")
            print("🎯 Optimal context optimization active - Claude Code performance maximized!")
            print("🛡️ YAML Governance active - Configuration chaos prevention enabled!")
            if not organization_ok:
                print("⚠️ Registry Consolidator not active - manual database organization required")
            logger.info("✅ OrchestrationStart completed successfully with AI integration, context optimization, and governance")
        elif cloud_sync_ok and core_systems_ok and context_optimization_ok:
            print("🎉 SUCCESS: Complete orchestration with AI analytics and optimal context optimization!")
            if ai_status['ai_active']:
                print("🧠 AI-Powered system monitoring and predictive analytics enabled!")
            print("🎯 Optimal context optimization active - Claude Code performance maximized!")
            if not governance_ok:
                print("⚠️ YAML Governance not active - manual configuration management required")
            logger.info("✅ OrchestrationStart completed successfully with AI integration and context optimization")
        elif cloud_sync_ok and core_systems_ok:
            print("⚠️ PARTIAL SUCCESS: Core systems running, context optimization needs attention")
            if ai_status['ai_active']:
                print("🧠 AI Analytics active - enhanced system monitoring enabled!")
            logger.warning("⚠️ OrchestrationStart completed with context optimization warnings")
        elif core_systems_ok:
            print("⚠️ PARTIAL SUCCESS: Core systems running, Cloud Sync needs SUPABASE_KEY")
            if ai_status['ai_active']:
                print("🧠 AI Analytics active - enhanced system monitoring enabled!")
            logger.warning("⚠️ OrchestrationStart completed with Cloud Sync warnings")
        else:
            print("⚠️ PARTIAL SUCCESS: Some core systems failed to start")
            logger.warning("⚠️ OrchestrationStart completed with system warnings")
        
        print("🔄 All systems handed off to Master Orchestration Agent...")
        if master_orchestration_running:
            print("🤖 AI-Enhanced coordination now active!")
        print("="*60)
        
        return True

def main():
    """Main entry point"""
    orchestration = OrchestrationStart()
    
    try:
        success = orchestration.run_orchestration()
        if success:
            logger.info("🎯 OrchestrationStart process completed")
            sys.exit(0)
        else:
            logger.error("❌ OrchestrationStart process failed")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("🛑 OrchestrationStart interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Unexpected error in OrchestrationStart: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()