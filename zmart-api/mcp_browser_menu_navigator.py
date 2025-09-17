#!/usr/bin/env python3
"""
MCP Browser Menu Navigator for IntoTheCryptoverse
Navigates through the left menu to access all symbols
"""

import asyncio
import json
import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class CryptoverseMenuNavigator:
    """Navigate IntoTheCryptoverse using the left menu"""

    def __init__(self):
        self.base_url = "https://app.intothecryptoverse.com"
        self.current_symbol = None

    async def navigate_to_risk_page(self) -> bool:
        """Navigate to the main risk page"""
        try:
            logger.info("Navigating to main risk page...")

            # Navigate to the main page first
            url = f"{self.base_url}/assets/bitcoin/risk"

            # Use actual MCP browser navigation
            result = await self.call_mcp_tool(
                "mcp__browsermcp__browser_navigate",
                {"url": url}
            )

            # Wait for page load
            await self.call_mcp_tool(
                "mcp__browsermcp__browser_wait",
                {"time": 3}
            )

            return True

        except Exception as e:
            logger.error(f"Error navigating to risk page: {e}")
            return False

    async def open_symbol_menu(self) -> bool:
        """Open the left side symbol menu"""
        try:
            logger.info("Opening symbol menu...")

            # Take snapshot to find menu button
            snapshot = await self.call_mcp_tool(
                "mcp__browsermcp__browser_snapshot",
                {}
            )

            # Look for menu toggle or symbol selector
            # Common patterns: "menu", "symbols", "assets", dropdown icon
            menu_patterns = [
                r'ref="(menu-toggle[^"]*)"',
                r'ref="(symbol-selector[^"]*)"',
                r'ref="(asset-menu[^"]*)"',
                r'ref="(sidebar-toggle[^"]*)"'
            ]

            menu_ref = None
            for pattern in menu_patterns:
                match = re.search(pattern, snapshot)
                if match:
                    menu_ref = match.group(1)
                    break

            if menu_ref:
                # Click the menu
                await self.call_mcp_tool(
                    "mcp__browsermcp__browser_click",
                    {
                        "ref": menu_ref,
                        "element": "Symbol menu toggle"
                    }
                )

                # Wait for menu to open
                await self.call_mcp_tool(
                    "mcp__browsermcp__browser_wait",
                    {"time": 1}
                )

                logger.info("Symbol menu opened")
                return True
            else:
                logger.warning("Could not find menu toggle")
                return False

        except Exception as e:
            logger.error(f"Error opening menu: {e}")
            return False

    async def click_symbol_in_menu(self, symbol: str, symbol_name: str) -> bool:
        """Click on a specific symbol in the menu"""
        try:
            logger.info(f"Clicking on {symbol} in menu...")

            # Take snapshot to find symbol in menu
            snapshot = await self.call_mcp_tool(
                "mcp__browsermcp__browser_snapshot",
                {}
            )

            # Look for the symbol in the menu
            # Patterns to match: BTC, Bitcoin, bitcoin, etc.
            symbol_patterns = [
                rf'ref="([^"]*{symbol}[^"]*)"',
                rf'ref="([^"]*{symbol_name.lower()}[^"]*)"',
                rf'>{symbol}<.*?ref="([^"]*)"',
                rf'>{symbol_name}<.*?ref="([^"]*)"'
            ]

            symbol_ref = None
            for pattern in symbol_patterns:
                match = re.search(pattern, snapshot, re.IGNORECASE)
                if match:
                    symbol_ref = match.group(1)
                    break

            if symbol_ref:
                # Click the symbol
                await self.call_mcp_tool(
                    "mcp__browsermcp__browser_click",
                    {
                        "ref": symbol_ref,
                        "element": f"{symbol} menu item"
                    }
                )

                # Wait for page to load
                await self.call_mcp_tool(
                    "mcp__browsermcp__browser_wait",
                    {"time": 3}
                )

                logger.info(f"Successfully navigated to {symbol}")
                self.current_symbol = symbol
                return True
            else:
                logger.warning(f"Could not find {symbol} in menu")
                return False

        except Exception as e:
            logger.error(f"Error clicking symbol {symbol}: {e}")
            return False

    async def extract_risk_table_data(self) -> Dict:
        """Extract risk table data from current page"""
        try:
            logger.info(f"Extracting risk table for {self.current_symbol}...")

            # Take snapshot
            snapshot = await self.call_mcp_tool(
                "mcp__browsermcp__browser_snapshot",
                {}
            )

            risk_data = {
                "symbol": self.current_symbol,
                "timestamp": datetime.now().isoformat(),
                "fiat_risk_grid": [],
                "btc_risk_grid": [],
                "eth_risk_grid": []
            }

            # Look for table with risk data
            # Pattern: risk value followed by price
            # Example: "0.025" ... "$45,234.56"

            # Extract all risk rows (0.000 to 1.000 in 0.025 steps)
            for i in range(41):
                risk_value = round(i * 0.025, 3)
                risk_str = f"{risk_value:.3f}"

                # Find row with this risk value
                row_pattern = rf'{risk_str}[^$]*\$?([\d,]+\.?\d*)'
                match = re.search(row_pattern, snapshot)

                if match:
                    price_str = match.group(1).replace(',', '')
                    try:
                        price = float(price_str)
                        risk_data["fiat_risk_grid"].append({
                            "risk": risk_value,
                            "price": price
                        })
                    except ValueError:
                        logger.warning(f"Could not parse price for risk {risk_value}")

            # Check if we got all 41 points
            if len(risk_data["fiat_risk_grid"]) == 41:
                logger.info(f"✅ Extracted 41 risk points for {self.current_symbol}")
                return risk_data
            else:
                logger.warning(f"Only extracted {len(risk_data['fiat_risk_grid'])} points")
                return risk_data

        except Exception as e:
            logger.error(f"Error extracting risk table: {e}")
            return {}

    async def scrape_symbol_using_menu(self, symbol: str, symbol_name: str) -> Optional[Dict]:
        """Complete scraping process for one symbol using menu navigation"""
        try:
            logger.info(f"\nProcessing {symbol} ({symbol_name})...")

            # Step 1: Open menu if needed
            await self.open_symbol_menu()

            # Step 2: Click on symbol in menu
            if not await self.click_symbol_in_menu(symbol, symbol_name):
                logger.error(f"Failed to navigate to {symbol}")
                return None

            # Step 3: Extract risk table data
            risk_data = await self.extract_risk_table_data()

            if risk_data and len(risk_data.get("fiat_risk_grid", [])) == 41:
                return risk_data
            else:
                return None

        except Exception as e:
            logger.error(f"Error scraping {symbol}: {e}")
            return None

    async def scrape_all_symbols_via_menu(self) -> Dict[str, Dict]:
        """Scrape all symbols by navigating through the menu"""

        symbol_list = [
            ("BTC", "Bitcoin"),
            ("ETH", "Ethereum"),
            ("BNB", "Binance Coin"),
            ("ADA", "Cardano"),
            ("XRP", "Ripple"),
            ("SOL", "Solana"),
            ("AVAX", "Avalanche"),
            ("DOT", "Polkadot"),
            ("MATIC", "Polygon"),
            ("DOGE", "Dogecoin"),
            ("LINK", "Chainlink"),
            ("LTC", "Litecoin"),
            ("ATOM", "Cosmos"),
            ("XLM", "Stellar"),
            ("HBAR", "Hedera"),
            ("TRX", "Tron"),
            ("VET", "VeChain"),
            ("XMR", "Monero"),
            ("MKR", "Maker"),
            ("XTZ", "Tezos"),
            ("AAVE", "Aave"),
            ("RNDR", "Render"),
            ("SUI", "Sui"),
            ("STX", "Stacks"),
            ("SEI", "Sei")
        ]

        results = {}

        # Navigate to initial page
        if not await self.navigate_to_risk_page():
            logger.error("Failed to navigate to initial page")
            return results

        # Process each symbol
        for symbol, symbol_name in symbol_list:
            risk_data = await self.scrape_symbol_using_menu(symbol, symbol_name)

            if risk_data:
                results[symbol] = risk_data
                logger.info(f"✅ {symbol} scraped successfully")
            else:
                logger.error(f"❌ {symbol} failed")

            # Small delay between symbols
            await asyncio.sleep(2)

        # Summary
        success_count = len(results)
        total_count = len(symbol_list)
        logger.info(f"\nScraping complete: {success_count}/{total_count} successful")

        return results

    async def call_mcp_tool(self, tool_name: str, params: Dict) -> Any:
        """Call MCP tool - will be replaced with actual implementation"""
        logger.info(f"MCP Tool Call: {tool_name} with params: {params}")

        # This is where the actual MCP tool calls would happen
        # For now, returning mock data for testing

        if tool_name == "mcp__browsermcp__browser_snapshot":
            # Return a mock snapshot with risk data
            return self.generate_mock_snapshot()

        return {}

    def generate_mock_snapshot(self) -> str:
        """Generate mock snapshot for testing"""
        # This would be replaced with actual snapshot from MCP browser
        snapshot = """
        <div ref="menu-toggle">☰ Menu</div>
        <div ref="symbol-BTC">BTC - Bitcoin</div>
        <table>
            <tr><td>0.000</td><td>$30,000.00</td></tr>
            <tr><td>0.025</td><td>$32,500.00</td></tr>
            <!-- ... more rows ... -->
            <tr><td>1.000</td><td>$200,000.00</td></tr>
        </table>
        """
        return snapshot

async def test_menu_navigation():
    """Test the menu navigation"""
    navigator = CryptoverseMenuNavigator()

    # Test single symbol
    result = await navigator.scrape_symbol_using_menu("BTC", "Bitcoin")
    if result:
        logger.info("✅ Test successful")
    else:
        logger.error("❌ Test failed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_menu_navigation())