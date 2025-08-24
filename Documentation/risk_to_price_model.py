# risk_to_price_model.py

import numpy as np

# Define polynomial coefficients for supported coins
# Format: 'SYMBOL': [c0, c1, c2, c3, c4] for: c0 + c1*x + c2*x^2 + c3*x^3 + c4*x^4
coin_models = {
    "ETH": [459.09, 795.62, 6391.31, -7519.64, 10556.32],
    # Add more coins here using the same method
}

def estimate_price(symbol: str, risk: float) -> float:
    symbol = symbol.upper()
    if symbol not in coin_models:
        raise ValueError(f"Symbol '{symbol}' not found. Available: {list(coin_models.keys())}")
    if not (0 <= risk <= 1):
        raise ValueError("Risk must be between 0 and 1.")

    coeffs = coin_models[symbol]
    # Reverse coefficients to match np.poly1d format
    poly = np.poly1d(coeffs[::-1])
    return round(poly(risk), 2)

# Example usage
if __name__ == "__main__":
    sym = input("Enter symbol (e.g., ETH): ").strip()
    rsk = float(input("Enter risk (0 to 1): ").strip())
    est = estimate_price(sym, rsk)
    print(f"Estimated {sym.upper()} price at risk {rsk:.3f} is: ${est}")
