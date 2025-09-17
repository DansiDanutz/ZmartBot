#!/usr/bin/env python3
"""
🎯 Service Registration Automation System
========================================
Automatically updates orchestration startup when services are registered.
Integrates with port registry and orchestration startup script.
"""

import os
import sys
import sqlite3
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional
import json
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('service_registration_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ServiceRegistrationAutomation:
    """Automated service registration and orchestration management"""
    
    def __init__(self):
        self.project_root = Path("/Users/dansidanutz/Desktop/ZmartBot")
        self.port_registry_path = self.project_root / "zmart-api" / "port_registry.db"
        self.orchestration_script_path = self.project_root / "zmart-api" / "infra" / "orchestration" / "orchestrationstart.sh"
        self.backup_dir = self.project_root / "zmart-api" / "orchestration_backups"
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(exist_ok=True)
        
        # Service startup order template
        self.service_startup_order = [
            "system-protection-service",     # CRITICAL System Protection (Port 8999)
            "optimization-claude-service",   # HIGH Priority Optimization (Port 8998)
            "snapshot-service",              # CRITICAL Disaster Recovery (Port 8085)
            "passport-service",              # Service Registration & Identity Management (Port 8620)
            "doctor-service",                # AI-Powered System Diagnostics (Port 8700)
            "zmart_api",                    # Core API (Port 8000)
            "port-manager-service",          # Port management (Port 8610)
            "api_keys_manager_service",      # API keys (Port 8006)
            "mdc-orchestration-agent",       # MDC orchestration (Port 8615)
            "zmart_dashboard",              # Frontend (Port 3400)
            "zmart_analytics",              # Analytics (Port 8007)
            "zmart_backtesting",            # Backtesting (Port 8013)
            "zmart_data_warehouse",         # Data warehouse (Port 8015)
            "zmart_machine_learning",       # ML service (Port 8014)
            "zmart_notification",           # Notifications (Port 8008)
            "zmart_risk_management",        # Risk management (Port 8010)
            "zmart_technical_analysis",     # Technical analysis (Port 8011)
            "zmart_websocket",              # WebSocket (Port 8009)
            "zmart_alert_system",           # Alert system (Port 8012)
            "my_symbols_extended_service",  # Symbols extended (Port 8005)
            "mysymbols",                    # MySymbols internal API (Port 8201)
            "test-service",                 # Test service worker (Port 8301)
            "kucoin",                       # KuCoin worker (Port 8302)
            "binance-worker-service",       # Binance worker (Port 8303)
            "mdc-dashboard",                # MDC Dashboard System (Port 8090)
            "certification",                # Certification Service (Port 8901)
            "achievements",                 # Achievements Service (Port NULL)
        ]
    
    def get_registered_services(self) -> List[Dict]:
        """Get all services from port registry"""
        try:
            conn = sqlite3.connect(self.port_registry_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT service_name, port, status, pid, created_at, updated_at 
                FROM port_assignments 
                ORDER BY service_name
            """)
            
            services = []
            for row in cursor.fetchall():
                services.append({
                    'service_name': row[0],
                    'port': row[1],
                    'status': row[2],
                    'pid': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                })
            
            conn.close()
            return services
            
        except Exception as e:
            logger.error(f"Failed to get registered services: {e}")
            return []
    
    def backup_orchestration_script(self) -> str:
        """Create backup of orchestration script"""
        timestamp = subprocess.check_output(['date', '+%Y%m%d_%H%M%S']).decode().strip()
        backup_path = self.backup_dir / f"orchestrationstart_backup_{timestamp}.sh"
        
        try:
            with open(self.orchestration_script_path, 'r') as src:
                content = src.read()
            
            with open(backup_path, 'w') as dst:
                dst.write(content)
            
            logger.info(f"Backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return ""
    
    def update_orchestration_startup_order(self, new_services: List[str]) -> bool:
        """Update the service startup order in orchestration script"""
        try:
            # Read current script
            with open(self.orchestration_script_path, 'r') as f:
                content = f.read()
            
            # Create backup
            self.backup_orchestration_script()
            
            # Find existing startup order
            pattern = r'SERVICE_STARTUP_ORDER=\(\s*((?:[^)]*\n)*?)\s*\)'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            
            if not match:
                logger.error("Could not find SERVICE_STARTUP_ORDER in orchestration script")
                return False
            
            # Get current services
            current_services = []
            for line in match.group(1).split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract service name from line like '"service-name"'
                    service_match = re.search(r'"([^"]+)"', line)
                    if service_match:
                        current_services.append(service_match.group(1))
            
            # Add new services that aren't already in the list
            updated_services = current_services.copy()
            for service in new_services:
                if service not in updated_services:
                    updated_services.append(service)
                    logger.info(f"Added new service to startup order: {service}")
            
            # Create new startup order section
            new_startup_order = "SERVICE_STARTUP_ORDER=(\n"
            for service in updated_services:
                # Get port from registry
                port = self.get_service_port(service)
                comment = self.get_service_comment(service, port)
                new_startup_order += f'    "{service}"{comment}\n'
            new_startup_order += ")"
            
            # Replace in content
            new_content = re.sub(pattern, new_startup_order, content)
            
            # Write updated script
            with open(self.orchestration_script_path, 'w') as f:
                f.write(new_content)
            
            logger.info(f"Updated orchestration startup order with {len(new_services)} new services")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update orchestration startup order: {e}")
            return False
    
    def get_service_port(self, service_name: str) -> Optional[int]:
        """Get service port from registry"""
        try:
            conn = sqlite3.connect(self.port_registry_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT port FROM port_assignments WHERE service_name = ?", (service_name,))
            result = cursor.fetchone()
            
            conn.close()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Failed to get port for {service_name}: {e}")
            return None
    
    def get_service_comment(self, service_name: str, port: Optional[int]) -> str:
        """Get service comment for startup order"""
        comments = {
            "system-protection-service": "     # CRITICAL System Protection",
            "optimization-claude-service": "   # HIGH Priority Optimization",
            "snapshot-service": "              # CRITICAL Disaster Recovery",
            "passport-service": "              # Service Registration & Identity Management",
            "doctor-service": "                # AI-Powered System Diagnostics",
            "zmart_api": "                    # Core API",
            "port-manager-service": "          # Port management",
            "api_keys_manager_service": "      # API keys",
            "mdc-orchestration-agent": "       # MDC orchestration",
            "zmart_dashboard": "              # Frontend",
            "zmart_analytics": "              # Analytics",
            "zmart_backtesting": "            # Backtesting",
            "zmart_data_warehouse": "         # Data warehouse",
            "zmart_machine_learning": "       # ML service",
            "zmart_notification": "           # Notifications",
            "zmart_risk_management": "        # Risk management",
            "zmart_technical_analysis": "     # Technical analysis",
            "zmart_websocket": "              # WebSocket",
            "zmart_alert_system": "           # Alert system",
            "my_symbols_extended_service": "  # Symbols extended",
            "mysymbols": "                    # MySymbols internal API",
            "test-service": "                 # Test service worker",
            "kucoin": "                       # KuCoin worker",
            "binance-worker-service": "       # Binance worker",
        }
        
        base_comment = comments.get(service_name, "                    # Service")
        if port:
            return f"{base_comment} (Port {port})"
        return base_comment
    
    def update_service_directory_mapping(self, new_services: List[str]) -> bool:
        """Update service directory mapping in orchestration script"""
        try:
            # Read current script
            with open(self.orchestration_script_path, 'r') as f:
                content = f.read()
            
            # Find get_service_dir function
            pattern = r'get_service_dir\(\) \{\s*local service_name="\$1"\s*case "\$service_name" in\s*((?:[^}]*\n)*?)\s*esac\s*\}'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            
            if not match:
                logger.error("Could not find get_service_dir function in orchestration script")
                return False
            
            # Get current mappings
            current_mappings = match.group(1)
            
            # Add new service mappings
            new_mappings = []
            for service in new_services:
                directory = self.get_service_directory(service)
                if directory:
                    new_mappings.append(f'        "{service}") echo "{directory}" ;;')
            
            # Add new mappings to existing ones
            updated_mappings = current_mappings
            for mapping in new_mappings:
                if mapping not in updated_mappings:
                    updated_mappings += mapping + "\n"
            
            # Replace in content
            new_content = re.sub(pattern, f'get_service_dir() {{\n    local service_name="$1"\n    case "$service_name" in\n{updated_mappings}    esac\n}}', content)
            
            # Write updated script
            with open(self.orchestration_script_path, 'w') as f:
                f.write(new_content)
            
            logger.info(f"Updated service directory mappings for {len(new_services)} services")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update service directory mappings: {e}")
            return False
    
    def get_service_directory(self, service_name: str) -> Optional[str]:
        """Get service directory path"""
        directories = {
            "system-protection-service": "system_protection",
            "optimization-claude-service": "optimization_claude",
            "snapshot-service": "snapshot_service",
            "passport-service": "/Users/dansidanutz/Desktop/ZmartBot/services/passport-service",
            "doctor-service": "/Users/dansidanutz/Desktop/ZmartBot/services/doctor-service",
            "zmart_api": ".",
            "port-manager-service": "port_manager",
            "api_keys_manager_service": "api_keys_manager",
            "mdc-orchestration-agent": "mdc_orchestration",
            "zmart_dashboard": ".",
            "zmart_analytics": "analytics",
            "zmart_backtesting": "backtesting",
            "zmart_data_warehouse": "data_warehouse",
            "zmart_machine_learning": "machine_learning",
            "zmart_notification": "notification",
            "zmart_risk_management": "risk_management",
            "zmart_technical_analysis": "technical_analysis",
            "zmart_websocket": "websocket",
            "zmart_alert_system": "alert_system",
            "my_symbols_extended_service": "symbols_extended",
            "mysymbols": "mysymbols",
            "test-service": "test_service",
            "kucoin": "kucoin",
            "binance-worker-service": "binance_worker",
        }
        
        return directories.get(service_name)
    
    def update_service_commands(self, new_services: List[str]) -> bool:
        """Update service startup commands in orchestration script"""
        try:
            # Read current script
            with open(self.orchestration_script_path, 'r') as f:
                content = f.read()
            
            # Find get_service_command function
            pattern = r'get_service_command\(\) \{\s*local service_name="\$1"\s*case "\$service_name" in\s*((?:[^}]*\n)*?)\s*esac\s*\}'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            
            if not match:
                logger.error("Could not find get_service_command function in orchestration script")
                return False
            
            # Get current commands
            current_commands = match.group(1)
            
            # Add new service commands
            new_commands = []
            for service in new_services:
                command = self.get_service_command(service)
                if command:
                    new_commands.append(f'        "{service}") echo "{command}" ;;')
            
            # Add new commands to existing ones
            updated_commands = current_commands
            for command in new_commands:
                if command not in updated_commands:
                    updated_commands += command + "\n"
            
            # Replace in content
            new_content = re.sub(pattern, f'get_service_command() {{\n    local service_name="$1"\n    case "$service_name" in\n{updated_commands}    esac\n}}', content)
            
            # Write updated script
            with open(self.orchestration_script_path, 'w') as f:
                f.write(new_content)
            
            logger.info(f"Updated service commands for {len(new_services)} services")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update service commands: {e}")
            return False
    
    def get_service_command(self, service_name: str) -> Optional[str]:
        """Get service startup command"""
        commands = {
            "system-protection-service": "python3 system_protection_server.py --port 8999",
            "optimization-claude-service": "python3 optimization_claude_server.py --port 8998",
            "snapshot-service": "python3 snapshot_service_server.py --port 8085",
            "passport-service": "./start_passport_service.sh",
            "doctor-service": "./start_doctor_service.sh",
            "zmart_api": "python3 run_dev.py",
            "port-manager-service": "python3 port_manager_server.py --port 8610",
            "api_keys_manager_service": "python3 api_keys_manager_server.py --port 8006",
            "mdc-orchestration-agent": "python3 mdc_orchestration_agent.py --port 8615",
            "zmart_dashboard": "python3 professional_dashboard_server.py --port 3400",
            "zmart_analytics": "python3 analytics_server.py --port 8007",
            "zmart_backtesting": "python3 backtesting_server.py --port 8013",
            "zmart_data_warehouse": "python3 data_warehouse_server.py --port 8015",
            "zmart_machine_learning": "python3 machine_learning_server.py --port 8014",
            "zmart_notification": "python3 notification_server.py --port 8008",
            "zmart_risk_management": "python3 risk_management_server.py --port 8010",
            "zmart_technical_analysis": "python3 technical_analysis_server.py --port 8011",
            "zmart_websocket": "python3 websocket_server.py --port 8009",
            "zmart_alert_system": "python3 alert_system_server.py --port 8012",
            "my_symbols_extended_service": "python3 symbols_extended_server.py --port 8005",
            "mysymbols": "python3 mysymbols_server.py --port 8201",
            "test-service": "python3 test_service_server.py --port 8301",
            "kucoin": "python3 kucoin_server.py --port 8302",
            "binance-worker-service": "python3 binance_worker_server.py --port 8303",
        }
        
        return commands.get(service_name)
    
    def register_new_service(self, service_name: str, port: int, service_type: str = "service") -> bool:
        """Register a new service and update orchestration"""
        try:
            # Add to port registry
            conn = sqlite3.connect(self.port_registry_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO port_assignments 
                (service_name, port, status, service_type, created_at, updated_at)
                VALUES (?, ?, 'registered', ?, datetime('now'), datetime('now'))
            """, (service_name, port, service_type))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Registered new service: {service_name} (Port {port})")
            
            # Update orchestration startup
            self.update_orchestration_startup_order([service_name])
            self.update_service_directory_mapping([service_name])
            self.update_service_commands([service_name])
            
            # CRITICAL: Update Master Orchestration Agent
            self.update_master_orchestration_agent(service_name, port, service_type)
            
            logger.info(f"Updated orchestration startup for: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service_name}: {e}")
            return False
    
    def sync_all_services(self) -> bool:
        """Sync all registered services with orchestration startup"""
        try:
            registered_services = self.get_registered_services()
            service_names = [s['service_name'] for s in registered_services]
            
            logger.info(f"Syncing {len(service_names)} services with orchestration startup")
            
            # Update orchestration script
            success = (
                self.update_orchestration_startup_order(service_names) and
                self.update_service_directory_mapping(service_names) and
                self.update_service_commands(service_names)
            )
            
            if success:
                logger.info("Successfully synced all services with orchestration startup")
            else:
                logger.error("Failed to sync some services with orchestration startup")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to sync services: {e}")
            return False
    
    def get_orchestration_status(self) -> Dict:
        """Get current orchestration status"""
        try:
            registered_services = self.get_registered_services()
            
            # Check which services are in startup order
            with open(self.orchestration_script_path, 'r') as f:
                content = f.read()
            
            pattern = r'SERVICE_STARTUP_ORDER=\(\s*((?:[^)]*\n)*?)\s*\)'
            match = re.search(pattern, content)
            
            startup_services = []
            if match:
                for line in match.group(1).split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        service_match = re.search(r'"([^"]+)"', line)
                        if service_match:
                            startup_services.append(service_match.group(1))
            
            return {
                'registered_services': len(registered_services),
                'startup_services': len(startup_services),
                'registered_service_names': [s['service_name'] for s in registered_services],
                'startup_service_names': startup_services,
                'missing_from_startup': [s['service_name'] for s in registered_services if s['service_name'] not in startup_services],
                'orphaned_in_startup': [s for s in startup_services if s not in [rs['service_name'] for rs in registered_services]]
            }
            
        except Exception as e:
            logger.error(f"Failed to get orchestration status: {e}")
            return {}
    
    def update_master_orchestration_agent(self, service_name: str, port: int, service_type: str) -> bool:
        """Update Master Orchestration Agent with new service"""
        try:
            master_agent_path = self.project_root / ".cursor" / "rules" / "MasterOrchestrationAgent.mdc"
            
            if not master_agent_path.exists():
                logger.error("MasterOrchestrationAgent.mdc not found")
                return False
            
            # Read current content
            with open(master_agent_path, 'r') as f:
                content = f.read()
            
            # Get passport ID from passport registry
            passport_id = self.get_passport_id(service_name)
            
            # Find the next service number
            service_number = self.get_next_service_number(content)
            
            # Create new service entry
            port_display = str(port) if port else "NULL"
            new_service_entry = f"{service_number}. **{service_name}** ({service_type}) - Port {port_display} - Status: ACTIVE ✅ **PASSPORT: {passport_id}**"
            
            # Find where to insert (after the last numbered service)
            lines = content.split('\n')
            insert_index = -1
            
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{service_number-1}."):
                    insert_index = i + 1
                    break
            
            if insert_index == -1:
                # If not found, insert before "### Service Categories:"
                for i, line in enumerate(lines):
                    if "### Service Categories:" in line:
                        insert_index = i
                        break
            
            if insert_index == -1:
                insert_index = len(lines) - 1
            
            # Insert new service
            lines.insert(insert_index, new_service_entry)
            
            # Update service count
            content = '\n'.join(lines)
            content = self.update_service_count(content)
            
            # Write updated content
            with open(master_agent_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Updated Master Orchestration Agent with service: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Master Orchestration Agent: {e}")
            return False
    
    def get_passport_id(self, service_name: str) -> str:
        """Get passport ID for service from passport registry"""
        try:
            passport_db_path = self.project_root / "data" / "passport_registry.db"
            if not passport_db_path.exists():
                return "NO-PASSPORT"
            
            conn = sqlite3.connect(passport_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT passport_id FROM passport_registry WHERE service_name = ?", (service_name,))
            result = cursor.fetchone()
            
            conn.close()
            
            return result[0] if result else "NO-PASSPORT"
            
        except Exception as e:
            logger.error(f"Failed to get passport ID for {service_name}: {e}")
            return "NO-PASSPORT"
    
    def get_next_service_number(self, content: str) -> int:
        """Get the next service number for Master Orchestration Agent"""
        try:
            lines = content.split('\n')
            max_number = 0
            
            for line in lines:
                if line.strip().startswith(tuple(str(i) + '.' for i in range(1, 100))):
                    try:
                        number = int(line.split('.')[0])
                        max_number = max(max_number, number)
                    except ValueError:
                        continue
            
            return max_number + 1
            
        except Exception as e:
            logger.error(f"Failed to get next service number: {e}")
            return 1
    
    def update_service_count(self, content: str) -> str:
        """Update service count in Master Orchestration Agent"""
        try:
            # Count actual services in passport registry
            passport_db_path = self.project_root / "data" / "passport_registry.db"
            if passport_db_path.exists():
                conn = sqlite3.connect(passport_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM passport_registry WHERE status = 'ACTIVE'")
                actual_count = cursor.fetchone()[0]
                conn.close()
                
                # Update the count in the content
                import re
                pattern = r'(\d+) services registered'
                replacement = f'{actual_count} services registered'
                content = re.sub(pattern, replacement, content)
                
                logger.info(f"Updated service count to: {actual_count}")
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to update service count: {e}")
            return content
    
    def verify_master_agent_sync(self) -> Dict:
        """Verify Master Orchestration Agent synchronization"""
        try:
            # Get services from passport registry
            passport_db_path = self.project_root / "data" / "passport_registry.db"
            if not passport_db_path.exists():
                return {"error": "Passport registry not found"}
            
            conn = sqlite3.connect(passport_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT service_name FROM passport_registry WHERE status = 'ACTIVE'")
            passport_services = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Get services from Master Orchestration Agent
            master_agent_path = self.project_root / ".cursor" / "rules" / "MasterOrchestrationAgent.mdc"
            if not master_agent_path.exists():
                return {"error": "Master Orchestration Agent not found"}
            
            with open(master_agent_path, 'r') as f:
                content = f.read()
            
            # Extract service names from Master Orchestration Agent (only numbered services)
            import re
            pattern = r'^\s*\d+\.\s+\*\*([^*]+)\*\*'
            moa_services = re.findall(pattern, content, re.MULTILINE)
            
            # Compare
            missing_from_moa = [s for s in passport_services if s not in moa_services]
            extra_in_moa = [s for s in moa_services if s not in passport_services]
            
            return {
                "passport_services_count": len(passport_services),
                "moa_services_count": len(moa_services),
                "missing_from_moa": missing_from_moa,
                "extra_in_moa": extra_in_moa,
                "sync_status": "OK" if not missing_from_moa and not extra_in_moa else "OUT_OF_SYNC"
            }
            
        except Exception as e:
            logger.error(f"Failed to verify Master Orchestration Agent sync: {e}")
            return {"error": str(e)}
    
    def check_service_counts(self) -> Dict:
        """Check service count accuracy across all systems"""
        try:
            # Get counts from different sources
            passport_count = 0
            moa_count = 0
            port_registry_count = 0
            
            # Passport registry count
            passport_db_path = self.project_root / "data" / "passport_registry.db"
            if passport_db_path.exists():
                conn = sqlite3.connect(passport_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM passport_registry WHERE status = 'ACTIVE'")
                passport_count = cursor.fetchone()[0]
                conn.close()
            
            # Master Orchestration Agent count
            master_agent_path = self.project_root / ".cursor" / "rules" / "MasterOrchestrationAgent.mdc"
            if master_agent_path.exists():
                with open(master_agent_path, 'r') as f:
                    content = f.read()
                import re
                pattern = r'(\d+) services registered'
                match = re.search(pattern, content)
                if match:
                    moa_count = int(match.group(1))
            
            # Port registry count
            if self.port_registry_path.exists():
                conn = sqlite3.connect(self.port_registry_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM port_assignments")
                port_registry_count = cursor.fetchone()[0]
                conn.close()
            
            return {
                "passport_registry_count": passport_count,
                "master_orchestration_agent_count": moa_count,
                "port_registry_count": port_registry_count,
                "all_match": passport_count == moa_count == port_registry_count,
                "discrepancies": {
                    "passport_vs_moa": passport_count - moa_count,
                    "passport_vs_port": passport_count - port_registry_count,
                    "moa_vs_port": moa_count - port_registry_count
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to check service counts: {e}")
            return {"error": str(e)}

def main():
    """Main function for command line usage"""
    automation = ServiceRegistrationAutomation()
    
    if len(sys.argv) < 2:
        print("Usage: python3 service_registration_automation.py <command> [args...]")
        print("Commands:")
        print("  register <service_name> <port> [service_type] - Register new service")
        print("  sync - Sync all registered services with orchestration")
        print("  status - Show orchestration status")
        print("  list - List all registered services")
        print("  update_master_agent <service_name> <port> <service_type> - Update Master Orchestration Agent")
        print("  verify_master_agent - Verify Master Orchestration Agent sync")
        print("  check_counts - Check service count accuracy")
        return
    
    command = sys.argv[1]
    
    if command == "register":
        if len(sys.argv) < 4:
            print("Usage: python3 service_registration_automation.py register <service_name> <port> [service_type]")
            return
        
        service_name = sys.argv[2]
        port = int(sys.argv[3])
        service_type = sys.argv[4] if len(sys.argv) > 4 else "service"
        
        if automation.register_new_service(service_name, port, service_type):
            print(f"✅ Successfully registered service: {service_name}")
        else:
            print(f"❌ Failed to register service: {service_name}")
    
    elif command == "sync":
        if automation.sync_all_services():
            print("✅ Successfully synced all services with orchestration")
        else:
            print("❌ Failed to sync services with orchestration")
    
    elif command == "status":
        status = automation.get_orchestration_status()
        print("📊 Orchestration Status:")
        print(f"  Registered Services: {status.get('registered_services', 0)}")
        print(f"  Startup Services: {status.get('startup_services', 0)}")
        print(f"  Missing from Startup: {len(status.get('missing_from_startup', []))}")
        print(f"  Orphaned in Startup: {len(status.get('orphaned_in_startup', []))}")
        
        if status.get('missing_from_startup'):
            print(f"  Missing Services: {', '.join(status['missing_from_startup'])}")
        
        if status.get('orphaned_in_startup'):
            print(f"  Orphaned Services: {', '.join(status['orphaned_in_startup'])}")
    
    elif command == "list":
        services = automation.get_registered_services()
        print("📋 Registered Services:")
        for service in services:
            print(f"  {service['service_name']} (Port {service['port']}, Status: {service['status']})")
    
    elif command == "update_master_agent":
        if len(sys.argv) < 5:
            print("Usage: python3 service_registration_automation.py update_master_agent <service_name> <port> <service_type>")
            return
        
        service_name = sys.argv[2]
        port = int(sys.argv[3])
        service_type = sys.argv[4]
        
        if automation.update_master_orchestration_agent(service_name, port, service_type):
            print(f"✅ Successfully updated Master Orchestration Agent with: {service_name}")
        else:
            print(f"❌ Failed to update Master Orchestration Agent with: {service_name}")
    
    elif command == "verify_master_agent":
        sync_status = automation.verify_master_agent_sync()
        if "error" in sync_status:
            print(f"❌ Error: {sync_status['error']}")
        else:
            print("🔍 Master Orchestration Agent Sync Status:")
            print(f"  Passport Services: {sync_status['passport_services_count']}")
            print(f"  MOA Services: {sync_status['moa_services_count']}")
            print(f"  Sync Status: {sync_status['sync_status']}")
            
            if sync_status['missing_from_moa']:
                print(f"  Missing from MOA: {', '.join(sync_status['missing_from_moa'])}")
            
            if sync_status['extra_in_moa']:
                print(f"  Extra in MOA: {', '.join(sync_status['extra_in_moa'])}")
    
    elif command == "check_counts":
        counts = automation.check_service_counts()
        if "error" in counts:
            print(f"❌ Error: {counts['error']}")
        else:
            print("📊 Service Count Analysis:")
            print(f"  Passport Registry: {counts['passport_registry_count']}")
            print(f"  Master Orchestration Agent: {counts['master_orchestration_agent_count']}")
            print(f"  Port Registry: {counts['port_registry_count']}")
            print(f"  All Match: {'✅' if counts['all_match'] else '❌'}")
            
            if not counts['all_match']:
                print("  Discrepancies:")
                for key, value in counts['discrepancies'].items():
                    if value != 0:
                        print(f"    {key}: {value}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
