
"""
risk_coefficient.py
--------------------
Continuous rarity coefficient for risk bands.

Goal:
  - Map band frequency (common -> rare) to a coefficient in [coef_min, coef_max] (default [1.0, 1.6]).
  - Make the coefficient CONTINUOUS within bands (no flat steps).
  - Optionally boost values as you approach a rarer next band.

Steps:
  1) Compute per-band frequencies (days / LifeAge) OR provide them directly as percentages.
  2) Convert frequencies to per-band base coefficients C[0..9] using inverse linear mapping 
     (higher frequency -> lower coefficient).
  3) For any risk r in [0,1], interpolate between the adjacent band coefficients using a smooth curve:
       - Baseline: smoothstep s(x) = 3x^2 - 2x^3 (keeps midpoint as the average).
       - Optional: edge "boost" with x**gamma toward the rarer next band.

Exposed API:
  - compute_band_percentages(days)
  - map_percentages_to_coefficients(percentages, coef_min=1.0, coef_max=1.6)
  - continuous_coef(r, C, beta=0.3, gamma_up=0.7, gamma_down=1.2)
  - get_coefficient(r, days=None, percentages=None, coefs=None, ...)

Example (BTC data from user):
  days = [134, 721, 840, 1131, 1102, 943, 369, 135, 79, 19]
  C = map_percentages_to_coefficients(compute_band_percentages(days))
  coef_at_r = continuous_coef(0.572, C)  # sample call

Author: ChatGPT
"""
from __future__ import annotations
from typing import Iterable, List, Optional, Sequence, Tuple

def compute_band_percentages(days: Sequence[int]) -> List[float]:
    """Convert per-band days to percentages (fractions summing to ~1.0).

    Args:
        days: length-10 sequence of days per band for bands [0.0–0.1, 0.1–0.2, ..., 0.9–1.0].

    Returns:
        List of 10 floats (fractions), each equal to days[i] / sum(days).
    """
    if len(days) != 10:
        raise ValueError("Expected 10 bands of days for [0.0-0.1, ..., 0.9-1.0].")
    total = float(sum(days))
    if total <= 0:
        raise ValueError("Sum of days must be positive.")
    return [d / total for d in days]


def map_percentages_to_coefficients(
    percentages: Sequence[float],
    coef_min: float = 1.0,
    coef_max: float = 1.6
) -> List[float]:
    """Map band percentage (common->rare) to coefficients in [coef_min, coef_max] (inverse linear).

    Highest percentage -> coef_min (most common)
    Lowest percentage  -> coef_max (rarest)

    Args:
        percentages: length-10 floats (fractions), need not sum exactly to 1.
        coef_min: coefficient for most common band (default 1.0)
        coef_max: coefficient for rarest band (default 1.6)

    Returns:
        List[float] length-10 of mapped coefficients C[i].
    """
    if len(percentages) != 10:
        raise ValueError("Expected 10 percentages for [0.0-0.1, ..., 0.9-1.0].")
    if not (coef_max > coef_min):
        raise ValueError("coef_max must be greater than coef_min.")

    p_max = max(percentages)
    p_min = min(percentages)
    if p_max == p_min:
        # All equal => everyone gets the midpoint
        mid = (coef_min + coef_max) / 2.0
        return [mid for _ in percentages]

    span = p_max - p_min
    scale = (coef_max - coef_min)
    # Inverse linear mapping
    C = [coef_min + (p_max - p) / span * scale for p in percentages]
    return C


def _smoothstep(x: float) -> float:
    """Classic smoothstep s(x) = 3x^2 - 2x^3 for x in [0,1]."""
    if x <= 0.0: return 0.0
    if x >= 1.0: return 1.0
    return 3*x*x - 2*x*x*x


def _continuous_coef_float(r, C, beta=0.3, gamma_up=0.7, gamma_down=1.2):
    """Wrapper ensuring a clean float return from continuous_coef."""
    val = continuous_coef(r, C, beta=beta, gamma_up=gamma_up, gamma_down=gamma_down)
    try:
        return float(val)
    except Exception:
        return float(getattr(val, 'real', val))

def continuous_coef(
    r: float,
    C: Sequence[float],
    beta: float = 0.3,
    gamma_up: float = 0.7,
    gamma_down: float = 1.2,
) -> float:
    """Continuous coefficient for arbitrary risk r in [0,1] from per-band coefficients C.

    Args:
        r: risk in [0, 1].
        C: length-10 per-band coefficients for [0.0-0.1, ..., 0.9-1.0].
        beta: blend factor in [0,1] for rarity "lean" near band edges (0 = pure smoothstep).
        gamma_up: exponent (<1) to accelerate toward next band if that next band is rarer (higher coef).
        gamma_down: exponent (>1) to decelerate toward next band if that next band is more common.

    Returns:
        Continuous coefficient value at r.
    """
    if len(C) != 10:
        raise ValueError("C must be length 10 for bands [0.0-0.1, ..., 0.9-1.0].")
    r = max(0.0, min(1.0, float(r)))
    if r == 1.0:
        return C[-1]
    # band index 0..9; for r in [0,1), cap at 8 so next band exists
    i = int(r * 10.0)
    if i > 8:
        i = 8
    # relative position inside band [0,1]
    x = (r - 0.1 * i) / 0.1

    c0 = float(C[i])
    c1 = float(C[i + 1])
    s = _smoothstep(x)  # baseline smooth interpolation

    # Boost toward the rarer side as we approach it
    if c1 > c0:
        t = (1.0 - beta) * s + beta * (x ** gamma_up)
    elif c1 < c0:
        t = (1.0 - beta) * s + beta * (x ** gamma_down)
    else:
        t = s

    return c0 + (c1 - c0) * t


def get_coefficient(
    r: float,
    days: Optional[Sequence[int]] = None,
    percentages: Optional[Sequence[float]] = None,
    coefs: Optional[Sequence[float]] = None,
    coef_min: float = 1.0,
    coef_max: float = 1.6,
    beta: float = 0.3,
    gamma_up: float = 0.7,
    gamma_down: float = 1.2,
) -> float:
    """Convenience wrapper to compute a coefficient at risk r from days/percentages/C.

    Priority: if `coefs` provided -> use it directly.
              elif `percentages` provided -> map to coefs.
              elif `days` provided -> compute percentages -> map to coefs.

    Args:
        r: risk in [0,1].
        days: length-10 list/tuple of per-band days.
        percentages: length-10 list/tuple of per-band fractions.
        coefs: length-10 list/tuple of per-band coefficients (skips mapping step).
        coef_min, coef_max: mapping bounds for the coefficients.
        beta, gamma_up, gamma_down: shaping parameters (see continuous_coef).

    Returns:
        Continuous coefficient at risk r.
    """
    if coefs is not None:
        C = list(coefs)
    else:
        if percentages is None:
            if days is None:
                raise ValueError("Provide one of: coefs, percentages, or days.")
            percentages = compute_band_percentages(days)
        C = map_percentages_to_coefficients(percentages, coef_min=coef_min, coef_max=coef_max)
    return _continuous_coef_float(r, C, beta=beta, gamma_up=gamma_up, gamma_down=gamma_down)


# ---- Example usage & self-test ----
if __name__ == "__main__":
    # BTC example from user
    btc_days = [134, 721, 840, 1131, 1102, 943, 369, 135, 79, 19]
    btc_percentages = compute_band_percentages(btc_days)
    btc_C = map_percentages_to_coefficients(btc_percentages, coef_min=1.0, coef_max=1.6)

    print("BTC Band Percentages (fractions):")
    print([round(p, 6) for p in btc_percentages])
    print("\nBTC Per-band Coefficients (C):")
    print([round(c, 6) for c in btc_C])

    # Sample risk points
    tests = [0.50, 0.55, 0.572, 0.59, 0.60, 0.68, 0.905]
    print("\nContinuous coef at sample risks (beta=0.3, gamma_up=0.7, gamma_down=1.2):")
    for r in tests:
        val = get_coefficient(r, coefs=btc_C, beta=0.3, gamma_up=0.7, gamma_down=1.2)
        print(f"r={r:>5}: coef={val:.6f}")
