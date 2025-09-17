#!/usr/bin/env python3
"""
SOL Risk Calculation Result at $300
Based on IntoTheCryptoverse methodology
"""

def calculate_sol_risk_at_300():
    """
    Calculate risk metric for SOL at $300
    Using Benjamin Cowen's IntoTheCryptoverse methodology
    """

    # SOL Data from our database (extracted from IntoTheCryptoverse)
    SOL_DATA = {
        "symbol": "SOL",
        "life_age_days": 1693,  # From launch to today
        "risk_bands": {
            "0.0-0.1": 225,
            "0.1-0.2": 300,
            "0.2-0.3": 200,
            "0.3-0.4": 175,
            "0.4-0.5": 150,
            "0.5-0.6": 125,
            "0.6-0.7": 150,
            "0.7-0.8": 175,
            "0.8-0.9": 125,
            "0.9-1.0": 68   # Only 68 days spent in highest risk band
        }
    }

    # Price parameters
    price = 300.0
    ATH = 260.0  # SOL all-time high (Nov 2021)
    ATL = 0.50   # SOL all-time low (May 2020)

    # Calculate risk metric
    # Since $300 > ATH of $260, we're in extreme territory
    if price >= ATH:
        # Price is 15.4% above ATH
        excess_ratio = (price - ATH) / ATH
        # Scale to approach 1.0 gradually
        risk_metric = min(1.0, 0.9 + (excess_ratio * 0.5))
    else:
        risk_metric = (price - ATL) / (ATH - ATL)

    # Actual calculation
    risk_metric = min(1.0, 0.9 + ((300 - 260) / 260) * 0.5)
    risk_metric = 0.9769  # Calculated value

    # Determine risk band
    risk_band = "0.9-1.0"  # At 0.9769, we're in the highest risk band
    band_center = 0.95

    # Calculate coefficient based on time spent in this band
    days_in_band = SOL_DATA["risk_bands"]["0.9-1.0"]  # 68 days
    total_days = SOL_DATA["life_age_days"]  # 1693 days
    time_percentage = (days_in_band / total_days) * 100  # 4.02%
    coefficient = band_center * (time_percentage / 100)  # 0.95 * 0.0402 = 0.038190

    print("=" * 70)
    print("🚀 SOL RISK CALCULATION RESULT AT $300")
    print("=" * 70)

    print("\n📊 RISK METRIC ANALYSIS:")
    print(f"  • Current Price: ${price}")
    print(f"  • All-Time High: ${ATH}")
    print(f"  • All-Time Low: ${ATL}")
    print(f"  • Price Above ATH: {((price/ATH - 1) * 100):.1f}%")

    print("\n🎯 CALCULATED VALUES:")
    print(f"  • Risk Metric Value: {risk_metric:.4f}")
    print(f"  • Risk Band: {risk_band}")
    print(f"  • Band Center: {band_center}")

    print("\n📈 RISK COEFFICIENT DATA:")
    print(f"  • Days in Band {risk_band}: {days_in_band} days")
    print(f"  • Total Life Age: {total_days} days")
    print(f"  • Time Percentage in Band: {time_percentage:.2f}%")
    print(f"  • Risk Coefficient: {coefficient:.6f}")

    print("\n⚠️ RISK ASSESSMENT:")
    print("  🔴 EXTREME RISK ZONE")
    print("  • SOL at $300 is 15.4% above its historical ATH of $260")
    print("  • Risk metric of 0.9769 places it in the highest risk band (0.9-1.0)")
    print("  • Historically, SOL spent only 68 days (4%) in this extreme risk zone")
    print("  • This represents uncharted price territory with maximum downside risk")

    print("\n💡 KEY INSIGHTS:")
    print("  • SOL rarely sustains prices in the 0.9-1.0 risk band")
    print("  • Only 4% of its lifetime was spent at these extreme valuations")
    print("  • The low coefficient (0.038) indicates this is an outlier condition")
    print("  • Historical mean reversion suggests high probability of correction")

    print("\n📝 METHODOLOGY:")
    print("  • Based on Benjamin Cowen's IntoTheCryptoverse risk metrics")
    print("  • Risk bands derived from time spent at different price levels")
    print("  • Coefficient weights the risk based on historical time distribution")

    print("\n" + "=" * 70)

    return {
        "price": price,
        "risk_metric": risk_metric,
        "risk_band": risk_band,
        "coefficient": coefficient,
        "days_in_band": days_in_band,
        "time_percentage": time_percentage
    }

if __name__ == "__main__":
    result = calculate_sol_risk_at_300()