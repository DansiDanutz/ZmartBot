#!/usr/bin/env python3
"""
MCP Browser Live Data Extractor for IntoTheCryptoverse
Extracts risk data from actual MCP browser snapshots
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class MCPSnapshotParser:
    """Parse risk data from MCP browser snapshots"""

    def extract_risk_table_from_snapshot(self, snapshot: str, symbol: str) -> Dict:
        """
        Extract risk table data from an MCP browser snapshot
        The snapshot contains the risk table in a structured format
        """
        try:
            risk_data = {
                "symbol": symbol,
                "fiat_risk_grid": [],
                "current_price": None,
                "current_risk": None
            }

            # Extract the main risk table (Key Risks section)
            # Pattern: row "0.000 $30,000.00" or similar
            risk_price_pattern = r'row\s+"([\d.]+)\s+\$([0-9,]+(?:\.\d{2})?)"'

            matches = re.findall(risk_price_pattern, snapshot)

            for risk_str, price_str in matches:
                try:
                    risk_value = float(risk_str)
                    # Only process standard risk increments (0.025 steps)
                    if risk_value % 0.025 < 0.001 or (risk_value % 0.025 > 0.024 and risk_value <= 1.0):
                        price = float(price_str.replace(',', ''))
                        risk_data["fiat_risk_grid"].append({
                            "risk": round(risk_value, 3),
                            "price": price
                        })
                except ValueError:
                    continue

            # Also extract from cell content patterns
            # Pattern: cell "0.000" followed by cell "$30,000.00"
            cell_pattern = r'cell\s+"([\d.]+)"[^:]*:\s*[^c]*cell\s+"\$([0-9,]+(?:\.\d{2})?)"'
            cell_matches = re.findall(cell_pattern, snapshot)

            for risk_str, price_str in cell_matches:
                try:
                    risk_value = float(risk_str)
                    if risk_value % 0.025 < 0.001 or (risk_value % 0.025 > 0.024 and risk_value <= 1.0):
                        price = float(price_str.replace(',', ''))
                        # Check if not already added
                        if not any(item['risk'] == round(risk_value, 3) for item in risk_data["fiat_risk_grid"]):
                            risk_data["fiat_risk_grid"].append({
                                "risk": round(risk_value, 3),
                                "price": price
                            })
                except ValueError:
                    continue

            # Extract current price and risk
            # Pattern: "$116,782.00" and "0.552" for current values
            current_pattern = r'row\s+"([\d.]+)\s+\$([0-9,]+(?:\.\d{2})?)".*?cell\s+"\$\2".*?cell\s+"(\1)"'
            current_match = re.search(current_pattern, snapshot)
            if current_match:
                risk_data["current_price"] = float(current_match.group(2).replace(',', ''))
                risk_data["current_risk"] = float(current_match.group(1))

            # Alternative: Look for heading with price
            price_heading = re.search(r'heading\s+"\$([0-9,]+(?:\.\d{2})?)"', snapshot)
            if price_heading and not risk_data["current_price"]:
                risk_data["current_price"] = float(price_heading.group(1).replace(',', ''))

            # Sort risk grid by risk value
            risk_data["fiat_risk_grid"].sort(key=lambda x: x["risk"])

            # Ensure we have exactly 41 points (0.000 to 1.000 in 0.025 steps)
            expected_risks = [round(i * 0.025, 3) for i in range(41)]

            # Fill in any missing values by interpolation if needed
            complete_grid = []
            existing_dict = {item["risk"]: item["price"] for item in risk_data["fiat_risk_grid"]}

            for i, expected_risk in enumerate(expected_risks):
                if expected_risk in existing_dict:
                    complete_grid.append({
                        "risk": expected_risk,
                        "price": existing_dict[expected_risk]
                    })
                else:
                    # Interpolate if missing
                    if i > 0 and i < len(expected_risks) - 1:
                        # Find nearest existing values
                        lower_risk = None
                        upper_risk = None

                        for j in range(i-1, -1, -1):
                            if expected_risks[j] in existing_dict:
                                lower_risk = expected_risks[j]
                                break

                        for j in range(i+1, len(expected_risks)):
                            if expected_risks[j] in existing_dict:
                                upper_risk = expected_risks[j]
                                break

                        if lower_risk and upper_risk:
                            lower_price = existing_dict[lower_risk]
                            upper_price = existing_dict[upper_risk]
                            # Linear interpolation
                            ratio = (expected_risk - lower_risk) / (upper_risk - lower_risk)
                            interpolated_price = lower_price + ratio * (upper_price - lower_price)
                            complete_grid.append({
                                "risk": expected_risk,
                                "price": round(interpolated_price, 2)
                            })

            risk_data["fiat_risk_grid"] = complete_grid

            return risk_data

        except Exception as e:
            logger.error(f"Error extracting risk table: {e}")
            return {}

    def validate_extraction(self, risk_data: Dict) -> Tuple[bool, List[str]]:
        """Validate extracted risk data"""
        errors = []

        # Check we have data
        if not risk_data:
            errors.append("No data extracted")
            return False, errors

        # Check fiat grid
        fiat_grid = risk_data.get("fiat_risk_grid", [])

        if len(fiat_grid) != 41:
            errors.append(f"Expected 41 risk points, got {len(fiat_grid)}")

        # Check risk sequence
        expected_risks = [round(i * 0.025, 3) for i in range(41)]
        actual_risks = [item["risk"] for item in fiat_grid]

        if actual_risks != expected_risks:
            missing = set(expected_risks) - set(actual_risks)
            errors.append(f"Missing risk values: {missing}")

        # Check prices are positive
        for item in fiat_grid:
            if item.get("price", 0) <= 0:
                errors.append(f"Invalid price at risk {item['risk']}")
                break

        is_valid = len(errors) == 0
        return is_valid, errors

def extract_bitcoin_data_from_current_page():
    """Extract Bitcoin risk data from the current MCP browser page"""
    # This would be called after navigating to the page

    # The snapshot we received shows the complete risk table
    snapshot = """[The actual snapshot from MCP browser]"""

    parser = MCPSnapshotParser()
    risk_data = parser.extract_risk_table_from_snapshot(snapshot, "BTC")

    # Validate
    is_valid, errors = parser.validate_extraction(risk_data)

    if is_valid:
        logger.info(f"✅ Successfully extracted {len(risk_data['fiat_risk_grid'])} risk points for BTC")

        # Save to file
        output_dir = Path("extracted_risk_grids")
        output_dir.mkdir(exist_ok=True)

        with open(output_dir / "BTC_risk_grid.json", 'w') as f:
            json.dump(risk_data, f, indent=2)

        return risk_data
    else:
        logger.error(f"❌ Validation failed: {errors}")
        return None

if __name__ == "__main__":
    # Test with sample snapshot
    sample_snapshot = '''
    row "0.000 $30,000.00"
    row "0.025 $31,352.00"
    row "0.050 $32,704.00"
    '''

    parser = MCPSnapshotParser()
    data = parser.extract_risk_table_from_snapshot(sample_snapshot, "TEST")
    print(json.dumps(data, indent=2))