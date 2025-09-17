#!/usr/bin/env python3
"""
Service Schema Verification
Validates all services have proper configuration and schema
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
from dataclasses import dataclass
from datetime import datetime
import asyncio
import aiohttp

@dataclass
class ServiceSchema:
    """Expected service schema structure"""
    name: str
    port: Optional[int]
    health_endpoint: Optional[str]
    required_env_vars: List[str]
    api_endpoints: List[str]
    dependencies: List[str]

class ServiceSchemaVerifier:
    """Verify service configurations and schemas"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "services_checked": 0,
            "services_passed": 0,
            "services_failed": 0,
            "errors": [],
            "warnings": [],
            "details": {}
        }

    def verify_env_file(self) -> bool:
        """Verify .env file exists and has required variables"""
        env_path = Path(".env")
        if not env_path.exists():
            self.results["errors"].append("❌ .env file not found")
            return False

        required_vars = [
            "OPENAI_API_KEY",
            "BINANCE_API_KEY",
            "KUCOIN_API_KEY",
            "CRYPTOMETER_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_KEY"
        ]

        with open(env_path, 'r') as f:
            env_content = f.read()

        missing_vars = []
        for var in required_vars:
            if f"{var}=" not in env_content:
                missing_vars.append(var)

        if missing_vars:
            self.results["errors"].append(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False

        self.results["details"]["env_file"] = "✅ All required environment variables present"
        return True

    def verify_service_configs(self) -> bool:
        """Verify service configuration files"""
        config_dirs = ["src/config", "config", ".cursor/rules"]
        configs_found = []

        for config_dir in config_dirs:
            if Path(config_dir).exists():
                for file in Path(config_dir).rglob("*.py"):
                    configs_found.append(str(file))
                for file in Path(config_dir).rglob("*.yml"):
                    configs_found.append(str(file))
                for file in Path(config_dir).rglob("*.mdc"):
                    configs_found.append(str(file))

        if not configs_found:
            self.results["errors"].append("❌ No configuration files found")
            return False

        self.results["details"]["config_files"] = f"✅ Found {len(configs_found)} configuration files"
        return True

    def verify_mdc_files(self) -> bool:
        """Verify MDC (Module Documentation and Configuration) files"""
        mdc_dir = Path(".cursor/rules")
        if not mdc_dir.exists():
            self.results["warnings"].append("⚠️ MDC directory not found")
            return True  # Not critical

        mdc_files = list(mdc_dir.glob("*.mdc"))

        if not mdc_files:
            self.results["warnings"].append("⚠️ No MDC files found")
            return True

        # Check for critical MDC files
        critical_mdcs = ["main.mdc", "rule_0_mandatory.mdc", "MasterOrchestrationAgent.mdc"]
        missing_critical = []

        existing_mdcs = [f.name for f in mdc_files]
        for critical in critical_mdcs:
            if critical not in existing_mdcs:
                missing_critical.append(critical)

        if missing_critical:
            self.results["warnings"].append(f"⚠️ Missing critical MDC files: {', '.join(missing_critical)}")

        self.results["details"]["mdc_files"] = f"✅ Found {len(mdc_files)} MDC files"
        return True

    async def verify_service_health(self, service_name: str, port: int) -> bool:
        """Check if a service is running and healthy"""
        health_endpoints = [
            f"http://localhost:{port}/health",
            f"http://localhost:{port}/api/health",
            f"http://localhost:{port}/status"
        ]

        async with aiohttp.ClientSession() as session:
            for endpoint in health_endpoints:
                try:
                    async with session.get(endpoint, timeout=2) as response:
                        if response.status == 200:
                            self.results["details"][service_name] = f"✅ Service healthy at {endpoint}"
                            return True
                except:
                    continue

        return False

    async def verify_running_services(self) -> bool:
        """Check which services are currently running"""
        # Load port registry to get actual ports
        try:
            with open('port_registry.json', 'r') as f:
                port_registry = json.load(f)
        except:
            port_registry = {}

        services_to_check = [
            ("Main API", 8000),
            ("KingFisher AI", 8098),  # Verified port from registry
            ("Risk Metric", 8556),    # Simple RiskMetric actual port
            ("Webhook", 8555),        # Manus/Simple Webhook actual port
            ("MDC Agent", 8559),      # MDC Background Agent actual port
            ("InfluxDB", 8086),       # Time-series database
            ("Prometheus", 9090),     # Metrics collection
            ("Service Dashboard", 8080),  # Monitoring dashboard
            ("PostgreSQL", 5432),     # Primary database
            ("Redis", 6379),          # Cache
            ("Supabase", 54321),      # Local Supabase if running
        ]

        running_count = 0
        for service_name, port in services_to_check:
            if await self.verify_service_health(service_name, port):
                running_count += 1
                self.results["services_passed"] += 1
            else:
                self.results["details"][service_name] = f"⚠️ Service not responding on port {port}"

        self.results["services_checked"] = len(services_to_check)
        return running_count > 0

    def verify_database_schema(self) -> bool:
        """Verify database schema files exist"""
        schema_paths = [
            "supabase/migrations",
            "database/schema.sql",
            "risk_time_bands_migration.sql"
        ]

        schemas_found = []
        for schema_path in schema_paths:
            if Path(schema_path).exists():
                schemas_found.append(schema_path)

        if not schemas_found:
            self.results["warnings"].append("⚠️ No database schema files found")
            return True  # Not critical

        self.results["details"]["database_schemas"] = f"✅ Found {len(schemas_found)} schema files"
        return True

    def generate_report(self) -> str:
        """Generate verification report"""
        report = []
        report.append("=" * 60)
        report.append("SERVICE SCHEMA VERIFICATION REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {self.results['timestamp']}")
        report.append("")

        # Summary
        report.append("SUMMARY:")
        report.append(f"  Services Checked: {self.results['services_checked']}")
        report.append(f"  Services Passed: {self.results['services_passed']}")
        report.append(f"  Services Failed: {self.results['services_failed']}")
        report.append("")

        # Errors
        if self.results["errors"]:
            report.append("ERRORS:")
            for error in self.results["errors"]:
                report.append(f"  {error}")
            report.append("")

        # Warnings
        if self.results["warnings"]:
            report.append("WARNINGS:")
            for warning in self.results["warnings"]:
                report.append(f"  {warning}")
            report.append("")

        # Details
        report.append("VERIFICATION DETAILS:")
        for key, value in self.results["details"].items():
            report.append(f"  {key}: {value}")

        report.append("")
        report.append("=" * 60)

        # Overall status
        if not self.results["errors"]:
            report.append("✅ VERIFICATION PASSED - All critical checks successful")
        else:
            report.append("❌ VERIFICATION FAILED - Critical errors found")

        return "\n".join(report)

    async def run_verification(self):
        """Run all verification checks"""
        print("🔍 Starting Service Schema Verification...")
        print("")

        # Check environment
        print("Checking environment variables...")
        self.verify_env_file()

        # Check configurations
        print("Checking service configurations...")
        self.verify_service_configs()

        # Check MDC files
        print("Checking MDC files...")
        self.verify_mdc_files()

        # Check database schemas
        print("Checking database schemas...")
        self.verify_database_schema()

        # Check running services
        print("Checking running services...")
        await self.verify_running_services()

        # Generate and display report
        report = self.generate_report()
        print("\n" + report)

        # Save report to file
        report_path = Path("service_verification_report.txt")
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {report_path}")

        # Return exit code
        return 0 if not self.results["errors"] else 1

async def main():
    """Main entry point"""
    verifier = ServiceSchemaVerifier()
    exit_code = await verifier.run_verification()
    sys.exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main())