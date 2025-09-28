#!/usr/bin/env python3
"""
MCP and API Manager Integration
Connects MCP servers with ZmartBot API Keys Manager for unified credential management
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPAPIIntegration:
    """
    Integration layer between MCP servers and API Keys Manager
    """

    def __init__(self):
        self.api_manager_url = "http://localhost:8006"
        self.claude_config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        self.ccxt_config_path = Path("/Users/dansidanutz/Desktop/ZmartBot/ccxt-exchanges-config.json")
        self.supported_exchanges = [
            "binance", "bybit", "kucoin", "okx", "bitget", "kraken",
            "coinbase", "huobi", "bitfinex", "mexc"
        ]

    def fetch_api_keys_from_manager(self, service_name: str = None) -> Dict[str, Any]:
        """Fetch API keys from the API Keys Manager"""
        try:
            endpoint = f"{self.api_manager_url}/api/keys"
            if service_name:
                endpoint += f"?service_name={service_name}"

            response = requests.get(endpoint)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch API keys: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Error fetching API keys: {e}")
            return {}

    def store_api_key_in_manager(self, service_name: str, api_key: str, api_secret: str,
                                 passphrase: Optional[str] = None) -> bool:
        """Store API key in the API Keys Manager"""
        try:
            endpoint = f"{self.api_manager_url}/api/keys"
            data = {
                "service_name": service_name,
                "api_key": api_key,
                "api_secret": api_secret,
                "key_type": "exchange",
                "description": f"{service_name.upper()} Exchange API Key"
            }

            if passphrase:
                data["passphrase"] = passphrase

            response = requests.post(endpoint, json=data)
            return response.status_code == 201

        except Exception as e:
            logger.error(f"Error storing API key: {e}")
            return False

    def update_claude_config_with_keys(self) -> bool:
        """Update Claude Desktop config with API keys from API Manager"""
        try:
            # Load current Claude config
            with open(self.claude_config_path, 'r') as f:
                config = json.load(f)

            # Fetch keys from API Manager for each exchange
            for exchange in self.supported_exchanges:
                keys = self.fetch_api_keys_from_manager(exchange)
                if keys and keys.get('data'):
                    key_data = keys['data'][0] if isinstance(keys['data'], list) else keys['data']

                    # Update binance server
                    if exchange == 'binance' and 'binance' in config['mcpServers']:
                        config['mcpServers']['binance']['env']['BINANCE_API_KEY'] = key_data.get('api_key', '')
                        config['mcpServers']['binance']['env']['BINANCE_API_SECRET'] = key_data.get('api_secret', '')

                    # Update ccxt-multi server
                    if 'ccxt-multi' in config['mcpServers']:
                        env = config['mcpServers']['ccxt-multi']['env']
                        env[f"{exchange.upper()}_API_KEY"] = key_data.get('api_key', '')
                        env[f"{exchange.upper()}_SECRET"] = key_data.get('api_secret', '')

                        if key_data.get('passphrase'):
                            env[f"{exchange.upper()}_PASSPHRASE"] = key_data.get('passphrase', '')

            # Save updated config
            with open(self.claude_config_path, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info("Claude config updated with API keys from API Manager")
            return True

        except Exception as e:
            logger.error(f"Error updating Claude config: {e}")
            return False

    def update_ccxt_config_with_keys(self) -> bool:
        """Update CCXT config file with API keys from API Manager"""
        try:
            # Load or create CCXT config
            if self.ccxt_config_path.exists():
                with open(self.ccxt_config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {"accounts": []}

            # Update accounts for each exchange
            for exchange in self.supported_exchanges:
                keys = self.fetch_api_keys_from_manager(exchange)
                if keys and keys.get('data'):
                    key_data = keys['data'][0] if isinstance(keys['data'], list) else keys['data']

                    # Check if account exists
                    account_exists = False
                    for account in config['accounts']:
                        if account['exchangeId'] == exchange:
                            account['apiKey'] = key_data.get('api_key', '')
                            account['secret'] = key_data.get('api_secret', '')
                            if key_data.get('passphrase'):
                                account['passphrase'] = key_data.get('passphrase', '')
                            account_exists = True
                            break

                    # Add new account if doesn't exist
                    if not account_exists and key_data.get('api_key'):
                        new_account = {
                            "name": f"{exchange}_main",
                            "exchangeId": exchange,
                            "apiKey": key_data.get('api_key', ''),
                            "secret": key_data.get('api_secret', ''),
                            "defaultType": "spot"
                        }
                        if key_data.get('passphrase'):
                            new_account['passphrase'] = key_data.get('passphrase', '')
                        config['accounts'].append(new_account)

            # Save updated config
            with open(self.ccxt_config_path, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info("CCXT config updated with API keys from API Manager")
            return True

        except Exception as e:
            logger.error(f"Error updating CCXT config: {e}")
            return False

    def sync_all_keys(self) -> Dict[str, bool]:
        """Sync all API keys between API Manager and MCP configurations"""
        results = {
            "claude_config": False,
            "ccxt_config": False,
            "api_manager_healthy": False
        }

        # Check API Manager health
        try:
            response = requests.get(f"{self.api_manager_url}/health")
            results["api_manager_healthy"] = response.status_code == 200
        except:
            logger.error("API Manager is not running!")
            return results

        # Update configurations
        results["claude_config"] = self.update_claude_config_with_keys()
        results["ccxt_config"] = self.update_ccxt_config_with_keys()

        return results

    def add_exchange_credentials(self, exchange: str, api_key: str, api_secret: str,
                                passphrase: Optional[str] = None) -> bool:
        """Add exchange credentials to API Manager and sync to MCP configs"""
        # Store in API Manager
        if not self.store_api_key_in_manager(exchange, api_key, api_secret, passphrase):
            logger.error(f"Failed to store {exchange} credentials in API Manager")
            return False

        # Sync to configurations
        sync_results = self.sync_all_keys()

        if sync_results["claude_config"] and sync_results["ccxt_config"]:
            logger.info(f"Successfully added and synced {exchange} credentials")
            return True
        else:
            logger.warning(f"Credentials stored but sync incomplete: {sync_results}")
            return False

    def start_api_manager(self) -> bool:
        """Start the API Keys Manager service if not running"""
        try:
            # Check if already running
            response = requests.get(f"{self.api_manager_url}/health", timeout=2)
            if response.status_code == 200:
                logger.info("API Keys Manager is already running")
                return True
        except:
            pass

        # Start the service
        try:
            cmd = [
                "python3",
                "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/api_keys_manager/api_keys_manager_server.py",
                "--port", "8006"
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Started API Keys Manager service on port 8006")
            return True
        except Exception as e:
            logger.error(f"Failed to start API Keys Manager: {e}")
            return False

def main():
    """Main integration runner"""
    integration = MCPAPIIntegration()

    print("🔗 MCP and API Manager Integration")
    print("=" * 50)

    # Start API Manager if needed
    if not integration.start_api_manager():
        print("❌ Failed to start API Manager")
        return

    print("✅ API Manager is running")

    while True:
        print("\n📋 Options:")
        print("1. Sync all API keys from API Manager to MCP configs")
        print("2. Add new exchange credentials")
        print("3. View current exchange keys in API Manager")
        print("4. Test MCP server connections")
        print("5. Exit")

        choice = input("\nSelect option (1-5): ")

        if choice == "1":
            print("\n🔄 Syncing API keys...")
            results = integration.sync_all_keys()
            for key, value in results.items():
                status = "✅" if value else "❌"
                print(f"{status} {key}")

        elif choice == "2":
            print("\n📝 Add Exchange Credentials")
            print("Supported exchanges:", ", ".join(integration.supported_exchanges))
            exchange = input("Exchange name: ").lower()

            if exchange not in integration.supported_exchanges:
                print(f"❌ Exchange '{exchange}' not supported")
                continue

            api_key = input("API Key: ")
            api_secret = input("API Secret: ")
            passphrase = input("Passphrase (leave empty if not required): ") or None

            if integration.add_exchange_credentials(exchange, api_key, api_secret, passphrase):
                print(f"✅ {exchange} credentials added and synced")
            else:
                print(f"❌ Failed to add {exchange} credentials")

        elif choice == "3":
            print("\n🔍 Fetching keys from API Manager...")
            for exchange in integration.supported_exchanges:
                keys = integration.fetch_api_keys_from_manager(exchange)
                if keys and keys.get('data'):
                    print(f"✅ {exchange}: Keys found")
                else:
                    print(f"⚪ {exchange}: No keys configured")

        elif choice == "4":
            print("\n🧪 Testing MCP server connections...")
            print("Please restart Claude Desktop to test the connections")
            print("The servers should show green status if properly configured")

        elif choice == "5":
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()