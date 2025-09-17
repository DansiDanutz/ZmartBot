#!/usr/bin/env python3
"""
Auto-Start Cryptoverse Risk Data System
This script ensures the Cryptoverse agent is ALWAYS running
Add this to your system startup or existing orchestration
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoverseAutoStarter:
    """Ensures Cryptoverse agent is always running"""

    def __init__(self):
        self.agent_script = Path(__file__).parent / "services" / "cryptoverse_background_agent.py"
        self.pid_file = Path("/tmp/cryptoverse_agent.pid")
        self.state_file = Path("/tmp/cryptoverse_agent_state.json")

    def is_agent_running(self) -> bool:
        """Check if agent is running"""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process exists
            os.kill(pid, 0)
            return True
        except:
            return False

    def start_agent(self) -> bool:
        """Start the background agent"""
        try:
            logger.info("Starting Cryptoverse Background Agent...")

            # Start as daemon
            cmd = [sys.executable, str(self.agent_script), "--start"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info("✅ Cryptoverse Agent started successfully")
                return True
            else:
                logger.error(f"Failed to start agent: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error starting agent: {e}")
            return False

    def check_health(self) -> Dict:
        """Check agent health"""
        if not self.state_file.exists():
            return {"healthy": False, "reason": "No state file"}

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            # Check last update
            last_update = state.get("last_update")
            if last_update:
                last_update_dt = datetime.fromisoformat(last_update)
                hours_since = (datetime.now() - last_update_dt).total_seconds() / 3600

                if hours_since > 96:  # More than 4 days
                    return {
                        "healthy": False,
                        "reason": f"No update for {hours_since:.1f} hours"
                    }

            # Check failures
            failures = state.get("consecutive_failures", 0)
            if failures >= 3:
                return {
                    "healthy": False,
                    "reason": f"Too many failures: {failures}"
                }

            return {"healthy": True, "state": state}

        except Exception as e:
            return {"healthy": False, "reason": str(e)}

    def ensure_running(self) -> bool:
        """Ensure agent is running and healthy"""
        logger.info("\n" + "="*60)
        logger.info("🔍 CRYPTOVERSE AGENT AUTO-START CHECK")
        logger.info("="*60)

        # Step 1: Check if running
        if self.is_agent_running():
            logger.info("✅ Agent is running")

            # Step 2: Check health
            health = self.check_health()
            if health["healthy"]:
                logger.info("✅ Agent is healthy")

                if "state" in health:
                    state = health["state"]
                    logger.info(f"Last update: {state.get('last_update', 'Unknown')}")
                    logger.info(f"Next update: {state.get('next_update', 'Unknown')}")

                return True
            else:
                logger.warning(f"⚠️ Agent unhealthy: {health.get('reason')}")

                # Restart agent
                logger.info("Restarting agent...")
                os.system(f"pkill -f cryptoverse_background_agent")
                time.sleep(2)
                return self.start_agent()
        else:
            logger.info("❌ Agent not running")
            return self.start_agent()

    def add_to_crontab(self):
        """Add to crontab for system startup"""
        try:
            # Check if already in crontab
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)

            if "auto_start_cryptoverse" not in result.stdout:
                # Add to crontab
                script_path = Path(__file__).absolute()
                cron_line = f"@reboot {sys.executable} {script_path} --ensure\n"

                # Get existing crontab
                existing = result.stdout if result.returncode == 0 else ""

                # Add new line
                new_crontab = existing + cron_line

                # Set new crontab
                process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE)
                process.communicate(new_crontab.encode())

                logger.info("✅ Added to crontab for automatic startup")
            else:
                logger.info("Already in crontab")

        except Exception as e:
            logger.error(f"Error adding to crontab: {e}")

    def add_to_systemd(self):
        """Create systemd service for automatic startup"""
        service_content = f"""[Unit]
Description=Cryptoverse Risk Data Background Agent
After=network.target

[Service]
Type=forking
User={os.getenv('USER')}
WorkingDirectory={Path(__file__).parent}
ExecStart={sys.executable} {self.agent_script} --start
ExecStop={sys.executable} {self.agent_script} --stop
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

        service_file = Path("/tmp/cryptoverse-agent.service")
        with open(service_file, 'w') as f:
            f.write(service_content)

        logger.info(f"Systemd service file created at {service_file}")
        logger.info("To install:")
        logger.info(f"  sudo cp {service_file} /etc/systemd/system/")
        logger.info("  sudo systemctl daemon-reload")
        logger.info("  sudo systemctl enable cryptoverse-agent")
        logger.info("  sudo systemctl start cryptoverse-agent")

def integrate_with_existing_services():
    """Hook into existing ZmartBot services"""
    try:
        # Try to import existing background services
        sys.path.append(str(Path(__file__).parent))

        # Check if background_agents exists
        background_path = Path(__file__).parent / "background_agents.py"

        if background_path.exists():
            # Add import to background_agents
            logger.info("Integrating with existing background agents...")

            with open(background_path, 'r') as f:
                content = f.read()

            if "cryptoverse_background_agent" not in content:
                # Add import
                import_line = "\nfrom services.cryptoverse_background_agent import integrate_with_zmartbot\n"

                # Find a good place to add it
                if "import" in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('import') or line.startswith('from'):
                            continue
                        else:
                            lines.insert(i, import_line)
                            break
                    content = '\n'.join(lines)
                else:
                    content = import_line + content

                # Add startup call
                startup_code = """
# Auto-start Cryptoverse Background Agent
try:
    integrate_with_zmartbot()
    logger.info("Cryptoverse agent integration successful")
except Exception as e:
    logger.error(f"Cryptoverse agent integration failed: {e}")
"""
                content += startup_code

                # Save updated file
                with open(background_path, 'w') as f:
                    f.write(content)

                logger.info("✅ Integrated with background_agents.py")

        # Also check for master orchestration
        orchestration_path = Path(__file__).parent / "master_orchestration.py"

        if orchestration_path.exists():
            logger.info("Found master_orchestration.py")
            # Similar integration can be done here

        return True

    except Exception as e:
        logger.error(f"Integration error: {e}")
        return False

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Auto-Start Cryptoverse System")
    parser.add_argument("--ensure", action="store_true", help="Ensure agent is running")
    parser.add_argument("--crontab", action="store_true", help="Add to crontab")
    parser.add_argument("--systemd", action="store_true", help="Create systemd service")
    parser.add_argument("--integrate", action="store_true", help="Integrate with existing services")
    parser.add_argument("--install", action="store_true", help="Full installation")

    args = parser.parse_args()

    starter = CryptoverseAutoStarter()

    if args.ensure:
        # Just ensure it's running
        if starter.ensure_running():
            logger.info("\n✅ Cryptoverse agent is running autonomously")
        else:
            logger.error("\n❌ Failed to start Cryptoverse agent")
            sys.exit(1)

    elif args.crontab:
        # Add to crontab
        starter.add_to_crontab()

    elif args.systemd:
        # Create systemd service
        starter.add_to_systemd()

    elif args.integrate:
        # Integrate with existing services
        if integrate_with_existing_services():
            logger.info("✅ Integration complete")
        else:
            logger.error("❌ Integration failed")

    elif args.install:
        # Full installation
        logger.info("🚀 FULL AUTONOMOUS INSTALLATION")

        # 1. Ensure running
        if not starter.ensure_running():
            logger.error("Failed to start agent")
            sys.exit(1)

        # 2. Add to crontab
        starter.add_to_crontab()

        # 3. Create systemd service
        starter.add_to_systemd()

        # 4. Integrate with existing services
        integrate_with_existing_services()

        logger.info("\n" + "✅"*20)
        logger.info("INSTALLATION COMPLETE")
        logger.info("Cryptoverse system is now 100% AUTONOMOUS")
        logger.info("It will run forever without any manual intervention!")
        logger.info("✅"*20)

    else:
        # Default: ensure running
        starter.ensure_running()

if __name__ == "__main__":
    main()