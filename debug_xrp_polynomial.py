#!/usr/bin/env python3
import numpy as np

# XRP Polynomial coefficients
xrp_coeffs = [2.585207868394954, -0.7039830206293587, 2.4317658458661464, 1.269598958949238, 0.5933623292719191]

def calculate_xrp_polynomial(risk):
    """Calculate XRP price using polynomial formula"""
    return (xrp_coeffs[0] * risk**4 + 
            xrp_coeffs[1] * risk**3 + 
            xrp_coeffs[2] * risk**2 + 
            xrp_coeffs[3] * risk + 
            xrp_coeffs[4])

# Test different risk values
print("🔍 XRP POLYNOMIAL DEBUG:")
print("=" * 40)

test_risks = [0.0, 0.25, 0.5, 0.75, 1.0]
for risk in test_risks:
    price = calculate_xrp_polynomial(risk)
    print(f"Risk {risk:.2f}: ${price:.2f}")

print(f"\nPolynomial Formula:")
print(f"XRP = {xrp_coeffs[0]:.4f}*x^4 + {xrp_coeffs[1]:.4f}*x^3 + {xrp_coeffs[2]:.4f}*x^2 + {xrp_coeffs[3]:.4f}*x + {xrp_coeffs[4]:.4f}")

print(f"\nCoefficients:")
print(f"c4 (x^4): {xrp_coeffs[0]:.4f}")
print(f"c3 (x^3): {xrp_coeffs[1]:.4f}")
print(f"c2 (x^2): {xrp_coeffs[2]:.4f}")
print(f"c1 (x^1): {xrp_coeffs[3]:.4f}")
print(f"c0 (const): {xrp_coeffs[4]:.4f}")

# Check if this matches the original XRP polynomial you provided
print(f"\nORIGINAL XRP POLYNOMIAL:")
print(f"XRP = 0.8353 - 0.5391*x + 13.5836*x^2 - 25.0379*x^3 + 17.5111*x^4")

# Calculate using original coefficients
original_coeffs = [17.5111, -25.0379, 13.5836, -0.5391, 0.8353]

def calculate_original_xrp(risk):
    return (original_coeffs[0] * risk**4 + 
            original_coeffs[1] * risk**3 + 
            original_coeffs[2] * risk**2 + 
            original_coeffs[3] * risk + 
            original_coeffs[4])

print(f"\nORIGINAL XRP VALUES:")
for risk in test_risks:
    price = calculate_original_xrp(risk)
    print(f"Risk {risk:.2f}: ${price:.2f}") 