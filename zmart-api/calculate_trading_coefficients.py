#!/usr/bin/env python3
"""
Calculate Trading Coefficients Based on Rarity
Most common band = 1.00, Rarest band = 1.60
Inverse relationship: Rarer bands have higher coefficients
"""

import json
from pathlib import Path
from datetime import datetime

def calculate_band_coefficients(symbol_data):
    """
    Calculate coefficients for each risk band based on rarity.
    Most common = 1.00, Rarest = 1.60
    """

    # Extract days in each band
    risk_bands = symbol_data['risk_bands']

    # Find the most common and rarest bands
    days_list = list(risk_bands.values())
    max_days = max(days_list)  # Most common
    min_days = min(days_list)  # Rarest

    # Calculate coefficients with inverse relationship
    coefficients = {}

    for band, days in risk_bands.items():
        if days == max_days:
            # Most common gets 1.00
            coefficient = 1.00
        elif days == min_days:
            # Rarest gets 1.60
            coefficient = 1.60
        else:
            # Linear interpolation (inverse relationship)
            # The fewer days (rarer), the higher the coefficient
            # Formula: coefficient = 1.60 - (days - min_days) * (0.60 / (max_days - min_days))
            coefficient = 1.60 - ((days - min_days) * 0.60 / (max_days - min_days))

        coefficients[band] = {
            'days': days,
            'percentage': symbol_data.get(f"{band}_percentage", 0),
            'coefficient': round(coefficient, 3),
            'rarity_rank': sorted(days_list).index(days) + 1  # 1 = rarest
        }

    return coefficients

def apply_coefficient_to_current_risk(symbol, current_risk, coefficients):
    """
    Apply the coefficient based on current risk level
    """
    # Determine which band the current risk falls into
    current_band = None
    for band in coefficients.keys():
        lower, upper = band.split('-')
        lower = float(lower)
        upper = float(upper)
        if lower <= current_risk < upper:
            current_band = band
            break

    if current_band:
        band_info = coefficients[current_band]
        adjusted_risk = current_risk * band_info['coefficient']

        return {
            'symbol': symbol,
            'current_risk': current_risk,
            'current_band': current_band,
            'coefficient': band_info['coefficient'],
            'adjusted_risk': round(adjusted_risk, 3),
            'days_in_band': band_info['days'],
            'band_rarity': band_info['rarity_rank'],
            'trading_signal': get_trading_signal(current_risk, band_info['coefficient'])
        }

    return None

def get_trading_signal(risk, coefficient):
    """
    Generate trading signal based on risk and coefficient
    """
    if coefficient >= 1.5:  # Very rare band
        if risk < 0.2:
            return "🔥 STRONG BUY - Extremely rare low risk"
        elif risk > 0.8:
            return "⚠️ STRONG SELL - Extremely rare high risk"
        else:
            return "👀 WATCH - Rare zone, high volatility expected"
    elif coefficient >= 1.3:  # Rare band
        if risk < 0.3:
            return "✅ BUY - Rare accumulation zone"
        elif risk > 0.7:
            return "📉 SELL - Rare distribution zone"
        else:
            return "🔍 MONITOR - Uncommon zone"
    else:  # Common band
        if risk < 0.3:
            return "💰 ACCUMULATE - Common accumulation"
        elif risk > 0.7:
            return "💸 TAKE PROFIT - Common distribution"
        else:
            return "⏸️ HOLD - Normal zone"

def main():
    """
    Process all symbols and generate trading coefficients
    """
    print("📊 Calculating Trading Coefficients Based on Rarity...")
    print("=" * 60)

    # Load SOL data as example
    sol_file = Path("extracted_risk_time_bands/SOL_time_bands.json")

    if not sol_file.exists():
        print("❌ SOL time bands file not found!")
        return

    with open(sol_file, 'r') as f:
        sol_data = json.load(f)

    # Calculate coefficients for SOL
    coefficients = calculate_band_coefficients(sol_data)

    print(f"\n🪙 SOLANA (SOL) - Trading Coefficients")
    print(f"Total Life: {sol_data['total_days']} days")
    print(f"Birth Date: {sol_data['birth_date']}")
    print("\n" + "-" * 60)
    print(f"{'Band':<10} {'Days':<8} {'%':<8} {'Coef':<8} {'Rarity':<10}")
    print("-" * 60)

    # Sort by coefficient (highest first - rarest bands)
    sorted_bands = sorted(coefficients.items(), key=lambda x: x[1]['coefficient'], reverse=True)

    for band, info in sorted_bands:
        rarity = "RAREST" if info['rarity_rank'] == 1 else f"Rank {info['rarity_rank']}"
        if info['days'] == max(sol_data['risk_bands'].values()):
            rarity = "MOST COMMON"

        print(f"{band:<10} {info['days']:<8} {info['percentage']:<8.2f} {info['coefficient']:<8.3f} {rarity:<10}")

    # Example: Apply to current SOL risk
    print("\n" + "=" * 60)
    print("📍 CURRENT RISK APPLICATION")
    print("-" * 60)

    # SOL current risk from your data
    current_sol_risk = 0.715  # 71.5% risk

    result = apply_coefficient_to_current_risk('SOL', current_sol_risk, coefficients)

    if result:
        print(f"Symbol: {result['symbol']}")
        print(f"Current Risk: {result['current_risk']:.1%}")
        print(f"Current Band: {result['current_band']}")
        print(f"Days in Band: {result['days_in_band']} days")
        print(f"Coefficient: {result['coefficient']}")
        print(f"Adjusted Risk: {result['adjusted_risk']}")
        print(f"Trading Signal: {result['trading_signal']}")

    # Generate SQL for database
    print("\n" + "=" * 60)
    print("💾 SQL TO UPDATE DATABASE")
    print("-" * 60)

    sql = generate_sql_for_coefficients('SOL', coefficients)

    # Save to file
    output_file = "sol_trading_coefficients.sql"
    with open(output_file, 'w') as f:
        f.write(sql)

    print(f"✅ SQL saved to {output_file}")

    # Process all symbols
    print("\n" + "=" * 60)
    print("🔄 PROCESSING ALL SYMBOLS...")

    time_bands_dir = Path("extracted_risk_time_bands")
    all_coefficients = {}

    for json_file in sorted(time_bands_dir.glob("*_time_bands.json")):
        with open(json_file, 'r') as f:
            data = json.load(f)

        symbol = data['symbol']
        coeffs = calculate_band_coefficients(data)
        all_coefficients[symbol] = coeffs

        print(f"✅ {symbol}: Coefficients calculated")

    # Save all coefficients
    output_json = "trading_coefficients_all.json"
    with open(output_json, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'methodology': {
                'description': 'Inverse rarity-based coefficients',
                'most_common': 1.00,
                'rarest': 1.60,
                'formula': 'coefficient = 1.60 - ((days - min_days) * 0.60 / (max_days - min_days))'
            },
            'symbols': all_coefficients
        }, f, indent=2)

    print(f"\n✅ All coefficients saved to {output_json}")

def generate_sql_for_coefficients(symbol, coefficients):
    """
    Generate SQL to store coefficients in database
    """
    sql = f"""-- Trading Coefficients for {symbol}
-- Based on inverse rarity: Most common = 1.00, Rarest = 1.60

-- Create table if not exists
CREATE TABLE IF NOT EXISTS trading_coefficients (
    symbol VARCHAR(10) NOT NULL,
    risk_band VARCHAR(10) NOT NULL,
    days_in_band INTEGER,
    percentage DECIMAL(5,2),
    coefficient DECIMAL(4,3),
    rarity_rank INTEGER,
    PRIMARY KEY (symbol, risk_band)
);

-- Insert coefficients for {symbol}
"""

    for band, info in coefficients.items():
        sql += f"""
INSERT INTO trading_coefficients (symbol, risk_band, days_in_band, percentage, coefficient, rarity_rank)
VALUES ('{symbol}', '{band}', {info['days']}, {info['percentage']}, {info['coefficient']}, {info['rarity_rank']})
ON CONFLICT (symbol, risk_band) DO UPDATE SET
    days_in_band = EXCLUDED.days_in_band,
    percentage = EXCLUDED.percentage,
    coefficient = EXCLUDED.coefficient,
    rarity_rank = EXCLUDED.rarity_rank;
"""

    sql += f"""
-- Function to get trading signal
CREATE OR REPLACE FUNCTION get_trading_signal(p_symbol VARCHAR, p_current_risk DECIMAL)
RETURNS TABLE(
    symbol VARCHAR,
    current_risk DECIMAL,
    risk_band VARCHAR,
    coefficient DECIMAL,
    adjusted_risk DECIMAL,
    trading_signal TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p_symbol as symbol,
        p_current_risk as current_risk,
        tc.risk_band,
        tc.coefficient,
        p_current_risk * tc.coefficient as adjusted_risk,
        CASE
            WHEN tc.coefficient >= 1.5 AND p_current_risk < 0.2 THEN '🔥 STRONG BUY'
            WHEN tc.coefficient >= 1.5 AND p_current_risk > 0.8 THEN '⚠️ STRONG SELL'
            WHEN tc.coefficient >= 1.3 AND p_current_risk < 0.3 THEN '✅ BUY'
            WHEN tc.coefficient >= 1.3 AND p_current_risk > 0.7 THEN '📉 SELL'
            WHEN p_current_risk < 0.3 THEN '💰 ACCUMULATE'
            WHEN p_current_risk > 0.7 THEN '💸 TAKE PROFIT'
            ELSE '⏸️ HOLD'
        END as trading_signal
    FROM trading_coefficients tc
    WHERE tc.symbol = p_symbol
    AND p_current_risk >= CAST(SPLIT_PART(tc.risk_band, '-', 1) AS DECIMAL)
    AND p_current_risk < CAST(SPLIT_PART(tc.risk_band, '-', 2) AS DECIMAL);
END;
$$ LANGUAGE plpgsql;

-- Test with current SOL risk
SELECT * FROM get_trading_signal('SOL', 0.715);
"""

    return sql

if __name__ == "__main__":
    main()