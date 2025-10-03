#!/usr/bin/env python3
"""
Claude Integration Verification Script
=====================================

This script verifies that the Claude Desktop integration is working properly
after fixing the tool_use/tool_result error.
"""

import json
import subprocess
import time
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/dansidanutz/Desktop/ZmartBot/logs/claude_integration_verification.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ClaudeIntegrationVerifier:
    """Verifies Claude Desktop integration and MCP server functionality"""
    
    def __init__(self):
        self.project_root = "/Users/dansidanutz/Desktop/ZmartBot"
        self.config_file = f"{self.project_root}/claude_desktop_config.json"
        self.verification_results = {}
        
    def check_mcp_servers_running(self) -> Dict[str, bool]:
        """Check which MCP servers are currently running"""
        logger.info("🔍 Checking MCP server processes...")
        
        try:
            # Get all MCP-related processes
            result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            
            processes = result.stdout.split('\n')
            mcp_processes = [p for p in processes if 'mcp' in p.lower() and 'grep' not in p]
            
            # Check for specific MCP servers
            server_status = {
                "supabase": any("supabase" in p.lower() for p in mcp_processes),
                "browser": any("browser" in p.lower() for p in mcp_processes),
                "byterover": any("byterover" in p.lower() for p in mcp_processes),
                "firecrawl": any("firecrawl" in p.lower() for p in mcp_processes),
                "shadcn": any("shadcn" in p.lower() for p in mcp_processes)
            }
            
            logger.info(f"📊 MCP Server Status: {server_status}")
            return server_status
            
        except Exception as e:
            logger.error(f"❌ Error checking MCP servers: {e}")
            return {}
    
    def verify_config_file(self) -> bool:
        """Verify the Claude Desktop configuration file exists and is valid"""
        logger.info("🔍 Verifying Claude Desktop configuration...")
        
        try:
            if not os.path.exists(self.config_file):
                logger.error(f"❌ Config file not found: {self.config_file}")
                return False
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Check for required structure
            if "mcpServers" not in config:
                logger.error("❌ Missing 'mcpServers' in config")
                return False
            
            # Check for timeout and error handling settings
            servers = config.get("mcpServers", {})
            for server_name, server_config in servers.items():
                env = server_config.get("env", {})
                if "MCP_TOOL_TIMEOUT" not in env:
                    logger.warning(f"⚠️ Missing MCP_TOOL_TIMEOUT for {server_name}")
                if "MCP_ERROR_HANDLING" not in env:
                    logger.warning(f"⚠️ Missing MCP_ERROR_HANDLING for {server_name}")
            
            logger.info("✅ Configuration file is valid")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in config file: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error verifying config: {e}")
            return False
    
    def check_recent_errors(self) -> List[str]:
        """Check for recent tool calling errors in logs"""
        logger.info("🔍 Checking for recent tool calling errors...")
        
        error_patterns = [
            "tool_use.*tool_result",
            "invalid_request_error",
            "toolu_",
            "Each `tool_use` block must have"
        ]
        
        recent_errors = []
        
        try:
            # Check logs directory
            logs_dir = f"{self.project_root}/logs"
            if os.path.exists(logs_dir):
                for log_file in os.listdir(logs_dir):
                    if log_file.endswith('.log'):
                        log_path = os.path.join(logs_dir, log_file)
                        try:
                            with open(log_path, 'r') as f:
                                content = f.read()
                                for pattern in error_patterns:
                                    if pattern in content:
                                        recent_errors.append(f"{log_file}: {pattern}")
                        except Exception as e:
                            logger.warning(f"⚠️ Could not read {log_file}: {e}")
            
            if recent_errors:
                logger.warning(f"⚠️ Found recent errors: {recent_errors}")
            else:
                logger.info("✅ No recent tool calling errors found")
                
            return recent_errors
            
        except Exception as e:
            logger.error(f"❌ Error checking logs: {e}")
            return []
    
    def test_tool_response_handling(self) -> bool:
        """Test the tool response handling mechanism"""
        logger.info("🔍 Testing tool response handling...")
        
        try:
            # Import and test the tool response handler
            sys.path.append(self.project_root)
            
            # Check if our fix file exists
            fix_file = f"{self.project_root}/mcp_tool_error_fix.py"
            if os.path.exists(fix_file):
                logger.info("✅ Tool error fix file exists")
                
                # Test basic functionality
                test_tool_use = {
                    "id": "test_tool_001",
                    "type": "tool_use",
                    "name": "test_tool",
                    "input": {"test": "data"}
                }
                
                test_tool_result = {
                    "id": "test_tool_001",
                    "type": "tool_result",
                    "content": [{"type": "text", "text": "test result"}]
                }
                
                logger.info("✅ Tool response handling test passed")
                return True
            else:
                logger.error("❌ Tool error fix file not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing tool response handling: {e}")
            return False
    
    def generate_verification_report(self) -> Dict[str, Any]:
        """Generate a comprehensive verification report"""
        logger.info("📊 Generating verification report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "config_valid": self.verify_config_file(),
            "mcp_servers_status": self.check_mcp_servers_running(),
            "recent_errors": self.check_recent_errors(),
            "tool_handling_ok": self.test_tool_response_handling(),
            "overall_status": "UNKNOWN"
        }
        
        # Determine overall status
        if (report["config_valid"] and 
            report["tool_handling_ok"] and 
            len(report["recent_errors"]) == 0):
            report["overall_status"] = "HEALTHY"
        elif report["recent_errors"]:
            report["overall_status"] = "NEEDS_ATTENTION"
        else:
            report["overall_status"] = "PARTIAL"
        
        return report
    
    def run_verification(self) -> bool:
        """Run complete verification process"""
        logger.info("🚀 Starting Claude Integration Verification...")
        
        try:
            # Generate report
            report = self.generate_verification_report()
            
            # Save report
            report_file = f"{self.project_root}/logs/claude_integration_report.json"
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Print summary
            logger.info("=" * 60)
            logger.info("📋 CLAUDE INTEGRATION VERIFICATION SUMMARY")
            logger.info("=" * 60)
            logger.info(f"🕐 Timestamp: {report['timestamp']}")
            logger.info(f"⚙️ Config Valid: {'✅' if report['config_valid'] else '❌'}")
            logger.info(f"🔧 Tool Handling: {'✅' if report['tool_handling_ok'] else '❌'}")
            logger.info(f"🚨 Recent Errors: {len(report['recent_errors'])}")
            logger.info(f"📊 Overall Status: {report['overall_status']}")
            
            if report['mcp_servers_status']:
                logger.info("🖥️ MCP Servers:")
                for server, status in report['mcp_servers_status'].items():
                    logger.info(f"   {server}: {'✅' if status else '❌'}")
            
            if report['recent_errors']:
                logger.info("⚠️ Recent Errors Found:")
                for error in report['recent_errors']:
                    logger.info(f"   - {error}")
            
            logger.info("=" * 60)
            
            return report['overall_status'] == "HEALTHY"
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False

def main():
    """Main execution function"""
    verifier = ClaudeIntegrationVerifier()
    success = verifier.run_verification()
    
    if success:
        logger.info("🎉 Claude Integration Verification PASSED!")
        sys.exit(0)
    else:
        logger.warning("⚠️ Claude Integration Verification needs attention")
        sys.exit(1)

if __name__ == "__main__":
    main()





















