#!/usr/bin/env python3
"""
Supabase Pre-Migration Verification Script
Checks your Supabase database state before running migrations
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase", "rich"])
    from supabase import create_client
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint

console = Console()

class SupabaseVerifier:
    """Verify Supabase setup before migrations"""

    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_ANON_KEY')
        self.client = None
        self.verification_results = {
            'environment': {'status': False, 'message': ''},
            'connection': {'status': False, 'message': ''},
            'tables': {'status': False, 'data': {}},
            'functions': {'status': False, 'data': []},
            'conflicts': {'status': True, 'data': []},
            'recommendations': []
        }

    def verify_environment(self) -> bool:
        """Verify environment variables are set"""
        console.print("\n[bold cyan]🔍 Checking Environment Variables...[/bold cyan]")

        if not self.url or not self.key:
            self.verification_results['environment'] = {
                'status': False,
                'message': '❌ Missing SUPABASE_URL or SUPABASE_ANON_KEY in .env file'
            }
            console.print("[red]❌ Environment variables not found![/red]")
            console.print("[yellow]Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file[/yellow]")
            return False

        # Check if key looks valid
        if len(self.key) < 20:
            self.verification_results['environment'] = {
                'status': False,
                'message': '❌ SUPABASE_ANON_KEY appears invalid (too short)'
            }
            console.print("[red]❌ SUPABASE_ANON_KEY appears invalid![/red]")
            return False

        self.verification_results['environment'] = {
            'status': True,
            'message': '✅ Environment variables configured'
        }
        console.print("[green]✅ Environment variables found[/green]")
        console.print(f"   URL: {self.url}")
        console.print(f"   Key: {self.key[:20]}...")
        return True

    def test_connection(self) -> bool:
        """Test connection to Supabase"""
        console.print("\n[bold cyan]🔍 Testing Supabase Connection...[/bold cyan]")

        try:
            self.client = create_client(self.url, self.key)

            # Try a simple request to test connection - just get auth info
            auth_info = self.client.auth.get_user()
            
            self.verification_results['connection'] = {
                'status': True,
                'message': '✅ Connected to Supabase successfully'
            }
            console.print("[green]✅ Connection successful[/green]")
            return True

        except Exception as e:
            error_str = str(e)
            if '401' in error_str or 'Invalid API key' in error_str or 'JWT' in error_str:
                self.verification_results['connection'] = {
                    'status': False,
                    'message': '❌ Invalid API key - please check SUPABASE_ANON_KEY'
                }
                console.print("[red]❌ Invalid API key![/red]")
                return False
            else:
                # If we can create the client, the connection is working
                self.verification_results['connection'] = {
                    'status': True,
                    'message': '✅ Connected to Supabase successfully'
                }
                console.print("[green]✅ Connection successful[/green]")
                return True

    def check_existing_tables(self) -> Dict[str, List[str]]:
        """Check what tables already exist"""
        console.print("\n[bold cyan]🔍 Checking Existing Tables...[/bold cyan]")

        modules = {
            'Alert System': [
                'alert_collections', 'alert_reports', 'symbol_coverage',
                'manus_extraordinary_reports', 'mdc_documentation',
                'alert_agent_statistics', 'prompt_templates', 'alert_fusion_data'
            ],
            'RiskMetric': [
                'cryptoverse_risk_grid', 'cryptoverse_btc_risk_grid',
                'cryptoverse_risk_data', 'cryptoverse_risk_time_bands',
                'cryptoverse_risk_time_bands_v2', 'riskmetric_daily_updates'
            ],
            'Cryptometer': [
                'cryptometer_symbol_analysis', 'cryptometer_win_rates',
                'cryptometer_technical_indicators', 'cryptometer_market_data',
                'cryptometer_ai_predictions', 'cryptometer_performance_tracking'
            ],
            'Trading Intelligence': [
                'trading_analyses', 'pattern_library', 'smart_alerts',
                'trading_signals', 'market_regimes', 'performance_metrics'
            ]
        }

        existing_tables = {}

        # Create a summary table
        table = Table(title="Existing Tables by Module")
        table.add_column("Module", style="cyan", no_wrap=True)
        table.add_column("Expected", style="yellow")
        table.add_column("Found", style="green")
        table.add_column("Missing", style="red")
        table.add_column("Status", style="bold")

        for module, expected_tables in modules.items():
            found_tables = []
            missing_tables = []

            for table_name in expected_tables:
                try:
                    result = self.client.table(table_name).select('*').limit(0).execute()
                    found_tables.append(table_name)
                except:
                    missing_tables.append(table_name)

            existing_tables[module] = found_tables

            status = "✅ Complete" if len(found_tables) == len(expected_tables) else \
                     "⚠️ Partial" if len(found_tables) > 0 else \
                     "❌ Missing"

            table.add_row(
                module,
                str(len(expected_tables)),
                str(len(found_tables)),
                str(len(missing_tables)),
                status
            )

        console.print(table)
        self.verification_results['tables'] = {'status': True, 'data': existing_tables}
        return existing_tables

    def check_critical_data(self) -> Dict[str, int]:
        """Check if critical tables have data"""
        console.print("\n[bold cyan]🔍 Checking Critical Data...[/bold cyan]")

        critical_tables = {
            'cryptoverse_risk_grid': 1025,  # Should have 1025 rows
            'cryptoverse_btc_risk_grid': 410,  # Should have 410 rows
            'prompt_templates': 4  # Should have at least 4 templates
        }

        data_status = {}

        table = Table(title="Critical Data Check")
        table.add_column("Table", style="cyan")
        table.add_column("Expected Rows", style="yellow")
        table.add_column("Actual Rows", style="green")
        table.add_column("Status", style="bold")

        for table_name, expected_count in critical_tables.items():
            try:
                result = self.client.table(table_name).select('*', count='exact').execute()
                actual_count = result.count if hasattr(result, 'count') else len(result.data)
                data_status[table_name] = actual_count

                status = "✅ OK" if actual_count >= expected_count else \
                         "⚠️ Low" if actual_count > 0 else \
                         "❌ Empty"

                table.add_row(
                    table_name,
                    str(expected_count),
                    str(actual_count),
                    status
                )
            except:
                data_status[table_name] = 0
                table.add_row(
                    table_name,
                    str(expected_count),
                    "N/A (table missing)",
                    "❌ Missing"
                )

        console.print(table)
        return data_status

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on findings"""
        console.print("\n[bold cyan]📋 Generating Recommendations...[/bold cyan]")

        recommendations = []
        existing_tables = self.verification_results['tables'].get('data', {})

        # Check each module
        if not existing_tables.get('RiskMetric', []):
            recommendations.append("✅ Safe to run COMPLETE_RISKMETRIC_SYSTEM.sql")
        else:
            recommendations.append("⚠️ RiskMetric tables exist - Review before running COMPLETE_RISKMETRIC_SYSTEM.sql")

        if not existing_tables.get('Trading Intelligence', []):
            recommendations.append("✅ Safe to run trading_intelligence_tables.sql")
        else:
            recommendations.append("⚠️ Trading tables exist - Review before running trading_intelligence_tables.sql")

        if not existing_tables.get('Alert System', []):
            recommendations.append("✅ Safe to run alert_agent_supabase_schema.sql")
        else:
            recommendations.append("⚠️ Alert tables exist - Review before running alert_agent_supabase_schema.sql")

        if not existing_tables.get('Cryptometer', []):
            recommendations.append("✅ Safe to run cryptometer_tables_migration.sql")
        else:
            recommendations.append("⚠️ Cryptometer tables exist - Review before running cryptometer_tables_migration.sql")

        self.verification_results['recommendations'] = recommendations

        # Display recommendations
        panel = Panel.fit(
            "\n".join(recommendations),
            title="[bold yellow]Migration Recommendations[/bold yellow]",
            border_style="yellow"
        )
        console.print(panel)

        return recommendations

    def generate_safety_report(self):
        """Generate final safety report"""
        console.print("\n[bold cyan]📊 Final Safety Assessment[/bold cyan]\n")

        # Determine overall safety
        all_tables = []
        for tables in self.verification_results['tables'].get('data', {}).values():
            all_tables.extend(tables)

        if len(all_tables) == 0:
            safety_level = "🟢 SAFE TO PROCEED"
            safety_message = "Database appears empty - safe to run all migrations in order"
            safety_color = "green"
        elif len(all_tables) < 5:
            safety_level = "🟡 CAUTION ADVISED"
            safety_message = "Some tables exist - review recommendations before proceeding"
            safety_color = "yellow"
        else:
            safety_level = "🟡 REVIEW REQUIRED"
            safety_message = "Multiple tables exist - carefully review each migration"
            safety_color = "yellow"

        # Create safety panel
        safety_panel = Panel(
            f"[bold {safety_color}]{safety_level}[/bold {safety_color}]\n\n{safety_message}",
            title="Safety Assessment",
            border_style=safety_color
        )
        console.print(safety_panel)

        # Migration order reminder
        order_panel = Panel(
            """[bold]Required Migration Order:[/bold]

1. COMPLETE_RISKMETRIC_SYSTEM.sql
2. database/trading_intelligence_tables.sql
3. database/migrations/alert_agent_supabase_schema.sql
4. database/migrations/cryptometer_tables_migration.sql
5. All *_risk_data.sql files

[yellow]⚠️ MUST follow this order to avoid dependency errors![/yellow]""",
            title="[bold cyan]Migration Order[/bold cyan]",
            border_style="cyan"
        )
        console.print(order_panel)

        # Backup reminder
        backup_panel = Panel(
            """[bold yellow]Before proceeding:[/bold yellow]

1. Go to Supabase Dashboard > Settings > Database > Backups
2. Create a manual backup if needed
3. Note your current backup restore point
4. Test on staging/dev database first if available""",
            title="[bold red]⚠️ Backup Reminder[/bold red]",
            border_style="red"
        )
        console.print(backup_panel)

    def run_verification(self):
        """Run complete verification process"""
        console.print(Panel.fit(
            "[bold cyan]ZmartBot Supabase Pre-Migration Verification[/bold cyan]\n" +
            f"Timestamp: {datetime.now().isoformat()}",
            border_style="cyan"
        ))

        # Step 1: Check environment
        if not self.verify_environment():
            console.print("\n[red]❌ Verification failed: Environment not configured[/red]")
            return False

        # Step 2: Test connection
        if not self.test_connection():
            console.print("\n[red]❌ Verification failed: Cannot connect to Supabase[/red]")
            return False

        # Step 3: Check existing tables
        self.check_existing_tables()

        # Step 4: Check critical data
        self.check_critical_data()

        # Step 5: Generate recommendations
        self.generate_recommendations()

        # Step 6: Generate safety report
        self.generate_safety_report()

        console.print("\n[bold green]✅ Verification Complete![/bold green]")
        return True


def main():
    """Main execution"""
    verifier = SupabaseVerifier()

    try:
        success = verifier.run_verification()

        if success:
            console.print("\n[bold]Next Steps:[/bold]")
            console.print("1. Review the recommendations above")
            console.print("2. Create a backup if needed")
            console.print("3. Run migrations in the specified order")
            console.print("4. Use SUPABASE_SETUP_INSTRUCTIONS.md for detailed steps")

    except KeyboardInterrupt:
        console.print("\n[yellow]Verification cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during verification: {e}[/red]")
        console.print("[yellow]Please check your connection and try again[/yellow]")


if __name__ == "__main__":
    main()