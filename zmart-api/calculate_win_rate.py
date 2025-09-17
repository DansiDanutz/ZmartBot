#!/usr/bin/env python3
"""
Calculate WIN RATE based on band rarity
Win Rate = (Days in Target Band / Days in Current Band) * 100
"""

def calculate_win_rate(symbol_data, current_band, signal_type):
    """
    Calculate win rate based on historical band distribution

    For LONG signals: Compare to more common higher bands (where price will likely go)
    For SHORT signals: Compare to more common lower bands (where price will likely go)
    """

    bands = symbol_data['risk_bands']
    current_days = bands[current_band]

    if signal_type == 'LONG':
        # For LONG, we expect price to go UP (risk increases)
        # Compare to more common bands above current
        target_bands = {
            '0.0-0.1': ['0.3-0.4', '0.4-0.5', '0.5-0.6'],  # Will likely move to middle
            '0.1-0.2': ['0.3-0.4', '0.4-0.5', '0.5-0.6'],
            '0.2-0.3': ['0.4-0.5', '0.5-0.6'],
        }
    elif signal_type == 'SHORT':
        # For SHORT, we expect price to go DOWN (risk decreases)
        # Compare to more common bands below current
        target_bands = {
            '0.9-1.0': ['0.5-0.6', '0.4-0.5', '0.3-0.4'],  # Will likely move to middle
            '0.8-0.9': ['0.5-0.6', '0.4-0.5', '0.3-0.4'],
            '0.7-0.8': ['0.4-0.5', '0.3-0.4'],
            '0.6-0.7': ['0.4-0.5', '0.3-0.4'],
        }
    else:
        return 0  # No win rate for NEUTRAL

    if current_band not in target_bands:
        return 0

    # Calculate average days in target zones
    target_days = [bands[tb] for tb in target_bands[current_band] if tb in bands]
    avg_target_days = sum(target_days) / len(target_days) if target_days else 0

    # Win Rate = (Average Target Days / Current Days)
    # Higher ratio = Higher probability of mean reversion
    if current_days > 0:
        win_rate_ratio = (avg_target_days / current_days)
        # Convert to percentage and cap at 100%
        win_rate = min(win_rate_ratio * 100, 95)  # Cap at 95% max
    else:
        win_rate = 0

    return win_rate

# AVAX data
avax_data = {
    'symbol': 'AVAX',
    'risk_bands': {
        '0.0-0.1': 54,   # Rare (2.97%)
        '0.1-0.2': 181,  # Uncommon (9.95%)
        '0.2-0.3': 236,  # Common (12.97%)
        '0.3-0.4': 291,  # Common (16.0%)
        '0.4-0.5': 363,  # Very Common (19.96%)
        '0.5-0.6': 400,  # Most Common (21.99%)
        '0.6-0.7': 236,  # Common (12.97%)
        '0.7-0.8': 127,  # Uncommon (6.98%)
        '0.8-0.9': 72,   # Rare (3.96%)
        '0.9-1.0': 36    # Rarest (1.98%)
    }
}

print('=' * 60)
print('WIN RATE CALCULATION FOR AVAX')
print('=' * 60)
print()

# Current AVAX situation
current_risk = 0.482
current_band = '0.4-0.5'
current_days = avax_data['risk_bands'][current_band]

print(f'Current Risk: {current_risk}')
print(f'Current Band: {current_band}')
print(f'Days in Current Band: {current_days} (19.96% of life)')
print(f'Signal: NEUTRAL (no trade)')
print()

# Calculate win rates for all bands
print('WIN RATES BY BAND:')
print('-' * 40)

for band, days in avax_data['risk_bands'].items():
    risk_value = float(band.split('-')[0])

    # Determine signal type
    if risk_value <= 0.2:
        signal = 'LONG'
    elif risk_value >= 0.7:
        signal = 'SHORT'
    else:
        signal = 'NEUTRAL'

    win_rate = calculate_win_rate(avax_data, band, signal)

    if signal != 'NEUTRAL':
        print(f'{band}: {days:3d} days → {signal:6s} → Win Rate: {win_rate:.1f}%')
    else:
        print(f'{band}: {days:3d} days → {signal:6s} → No trade zone')

print()
print('=' * 60)
print('EXTREME EXAMPLES:')
print('=' * 60)

# Example 1: If AVAX was at 0.9-1.0 (rarest)
band_90_100 = '0.9-1.0'
days_90_100 = avax_data['risk_bands'][band_90_100]
days_50_60 = avax_data['risk_bands']['0.5-0.6']
win_rate_short = (days_50_60 / days_90_100) * 100

print(f'\n1. If AVAX reaches 0.9-1.0 band (SHORT signal):')
print(f'   Current days in 0.9-1.0: {days_90_100} (rarest)')
print(f'   Target days in 0.5-0.6: {days_50_60} (most common)')
print(f'   Win Rate = ({days_50_60}/{days_90_100}) = {win_rate_short:.1f}%')
print(f'   Interpretation: {win_rate_short:.0f}% chance of reverting to middle')

# Example 2: If AVAX was at 0.0-0.1 (rare)
band_00_10 = '0.0-0.1'
days_00_10 = avax_data['risk_bands'][band_00_10]
win_rate_long = (days_50_60 / days_00_10) * 100

print(f'\n2. If AVAX reaches 0.0-0.1 band (LONG signal):')
print(f'   Current days in 0.0-0.1: {days_00_10} (rare)')
print(f'   Target days in 0.5-0.6: {days_50_60} (most common)')
print(f'   Win Rate = ({days_50_60}/{days_00_10}) = {win_rate_long:.1f}%')
print(f'   Interpretation: {win_rate_long:.0f}% chance of reverting to middle')

print()
print('=' * 60)
print('FORMULA EXPLAINED:')
print('=' * 60)
print('Win Rate = (Days in Common Band / Days in Rare Band) × 100')
print()
print('Logic: The rarer the current position, the higher the')
print('       probability of reverting to more common zones.')
print()
print('• Rare zones (< 100 days) → HIGH win rate (> 200%)')
print('• Common zones (> 300 days) → LOW win rate (< 50%)')
print('• Most time spent in middle → Mean reversion likely')