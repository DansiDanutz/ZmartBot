#!/usr/bin/env python3

# BTC price mapping for $200,000
risk_0_8 = 0.8
price_0_8 = 191385.0
risk_0_825 = 0.825
price_0_825 = 201180.0
current_price = 200000

# Calculate exact position between 0.8 and 0.825
price_range = price_0_825 - price_0_8
position_in_range = (current_price - price_0_8) / price_range
exact_risk = risk_0_8 + (position_in_range * (risk_0_825 - risk_0_8))

print(f'Table Lookup for BTC $200,000:')
print(f'Risk 0.8 = ${price_0_8:,.2f}')
print(f'Risk 0.825 = ${price_0_825:,.2f}')
print(f'Current Price = ${current_price:,.2f}')
print(f'')
print(f'Position calculation:')
print(f'Price range = ${price_0_825:,.2f} - ${price_0_8:,.2f} = ${price_range:,.2f}')
print(f'Position in range = (${current_price:,.2f} - ${price_0_8:,.2f}) / ${price_range:,.2f}')
print(f'Position = ${current_price - price_0_8:,.2f} / ${price_range:,.2f} = {position_in_range:.4f}')
print(f'')
print(f'Exact Risk = {risk_0_8:.3f} + ({position_in_range:.4f} × {risk_0_825 - risk_0_8:.3f})')
print(f'Exact Risk = {risk_0_8:.3f} + ({position_in_range:.4f} × 0.025)')
print(f'Exact Risk = {exact_risk:.4f}') 