#!/usr/bin/env python3
import sqlite3
import numpy as np
import json

# EXACT XRP Polynomial coefficients (from your message)
xrp_coeffs = [17.5111, -25.0379, 13.5836, -0.5391, 0.8353]

# Generate 41 risk levels from 0.0 to 1.0
risk_levels = np.linspace(0, 1, 41)

# Calculate prices using the EXACT polynomial formula
xrp_prices = []
for risk in risk_levels:
    # XRP = 0.8353 - 0.5391*x + 13.5836*x^2 - 25.0379*x^3 + 17.5111*x^4
    price = (xrp_coeffs[0] * risk**4 + 
             xrp_coeffs[1] * risk**3 + 
             xrp_coeffs[2] * risk**2 + 
             xrp_coeffs[3] * risk + 
             xrp_coeffs[4])
    xrp_prices.append(round(price, 2))

# Connect to database
conn = sqlite3.connect('backend/zmart-api/data/riskmetric.db')
cursor = conn.cursor()

# Get XRP symbol_id
cursor.execute("SELECT id FROM symbols WHERE symbol = 'XRP'")
xrp_id = cursor.fetchone()[0]

# Clear existing XRP mapping
cursor.execute("DELETE FROM risk_price_mapping WHERE symbol_id = ?", (xrp_id,))

# Insert the EXACT polynomial mapping
for i, risk in enumerate(risk_levels):
    cursor.execute("""
        INSERT INTO risk_price_mapping (symbol_id, risk_level, price)
        VALUES (?, ?, ?)
    """, (xrp_id, round(risk, 3), xrp_prices[i]))

# Update the polynomial formula in symbols table
cursor.execute("""
    UPDATE symbols 
    SET polynomial_formula = ?
    WHERE symbol = 'XRP'
""", (json.dumps(xrp_coeffs),))

# Update the formula in symbol_formulas table
cursor.execute("""
    UPDATE symbol_formulas 
    SET formula_text = ?
    WHERE symbol_id = ? AND formula_type = 'risk_to_price_formula'
""", (
    f"XRP = {xrp_coeffs[0]:.4f}*x^4 + {xrp_coeffs[1]:.4f}*x^3 + {xrp_coeffs[2]:.4f}*x^2 + {xrp_coeffs[3]:.4f}*x + {xrp_coeffs[4]:.4f}",
    xrp_id
))

conn.commit()
conn.close()

print("✅ FIXED XRP with EXACT POLYNOMIAL:")
print("RISK\tXRP")
for i, risk in enumerate(risk_levels):
    print(f"{risk:.3f}\t${xrp_prices[i]:.2f}")

print(f"\nTotal: {len(risk_levels)} risk levels stored")
print(f"Min: ${xrp_prices[0]:.2f} (Risk 0.0)")
print(f"Max: ${xrp_prices[-1]:.2f} (Risk 1.0)")

print(f"\nEXACT Polynomial Formula:")
print(f"XRP = {xrp_coeffs[0]:.4f}*x^4 + {xrp_coeffs[1]:.4f}*x^3 + {xrp_coeffs[2]:.4f}*x^2 + {xrp_coeffs[3]:.4f}*x + {xrp_coeffs[4]:.4f}")

print(f"\nKey Values:")
print(f"Risk 0.0: ${xrp_prices[0]:.2f}")
print(f"Risk 0.5: ${xrp_prices[20]:.2f}")
print(f"Risk 1.0: ${xrp_prices[-1]:.2f}")

print(f"\nCOMPARISON:")
print(f"❌ OLD (Linear): Risk 0.5 = $1.91")
print(f"✅ NEW (Exact Polynomial): Risk 0.5 = ${xrp_prices[20]:.2f}")
print(f"Difference: ${abs(1.91 - xrp_prices[20]):.2f}") 